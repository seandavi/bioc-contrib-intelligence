"""Gate 1 v3: code-level features for "will this submission need rework?".

Label: rework = the issue was ever labelled 3b declined, 3d needs interop or
3e pending pre-review changes; clean = finally 3a accepted without any of those.
Everything else (inactive or unlabelled without rework) is excluded.

Input: the package source at the last commit before the issue was opened (one
rule for every package), fetched as a GitHub tarball and statically indexed
with scip-r (no R, nothing executed). Features come from the scip-r tables plus
the file listing; Clef gets DESCRIPTION plus a short evidence summary.

Pipeline (each step resumable; artifacts under data/gate1/, gitignored):
  fetch    -> data/gate1/src/<issue>/ + data/gate1/manifest.jsonl
  index    -> data/gate1/scip/issue=<issue>/*.parquet
  features -> data/gate1/features.jsonl
  eval     -> experiments/gate1/runs/<run_id>/ + LEDGER.md line
"""
from __future__ import annotations

import asyncio
import hashlib
import io
import json
import random
import re
import subprocess
import tarfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import duckdb
import httpx

from . import clef, db
from .fetch import token
from .gate1 import CORE, _git_sha, auc, record_run

DATA = Path("data/gate1")
SCIPR = "scip-r[export] @ git+https://github.com/seandavi/scip-r@4e5b8f5588c49079256f6454ce492cd0d0152e80"
KEEP = re.compile(r"^(DESCRIPTION|NAMESPACE|NEWS(\.md|\.Rd)?|R/.*|vignettes/.*|tests/.*"
                  r"|inst/NEWS.*)$")
MAX_TARBALL = 200 * 2**20  # ponytail: skip giant data-heavy repos; record as too_big

LABELS = r"""
WITH ever AS (
  SELECT issue_number,
         bool_or(to_label IN ('3b. declined', '3d. needs interop',
                              '3e. pending pre-review changes')) AS rework,
         arg_max(to_label, changed_at) FILTER (WHERE to_label IN (
           '3a. accepted', '3b. declined', '3c. inactive', '3d. needs interop',
           '3e. pending pre-review changes')) AS final
  FROM label_transitions WHERE repo = 'Bioconductor/Contributions' GROUP BY 1
)
SELECT e.issue_number, e.rework, p.source_url, i.created_at
FROM ever e
JOIN packages p ON p.repo = 'Bioconductor/Contributions' AND p.issue_number = e.issue_number
JOIN issues i ON i.repo = 'Bioconductor/Contributions' AND i.number = e.issue_number
WHERE p.source_url LIKE '%github.com%' AND (e.rework OR e.final = '3a. accepted')
ORDER BY 1
"""


def split_of(n: int) -> str:
    """v3 split, salted so it is independent of the v1/v2 split (whose test was seen)."""
    h = int(hashlib.sha256(f"v3:{n}".encode()).hexdigest(), 16)
    return "dev" if h % 10 < 3 else "test"


def sample(max_clean: int, seed: int = 0) -> list[dict]:
    rows = [dict(zip(("issue", "rework", "url", "created"), r, strict=True))
            for r in db.connect().execute(LABELS).fetchall()]
    rework = [r for r in rows if r["rework"]]
    clean = [r for r in rows if not r["rework"]]
    random.Random(seed).shuffle(clean)  # ponytail: subsample clean; ratio recorded per run
    return rework + clean[:max_clean]


# ── fetch ────────────────────────────────────────────────────────────────────

def _owner_repo(url: str) -> tuple[str, str] | None:
    m = re.search(r"github\.com[/:]([^/\s]+)/([^/\s#?]+?)(?:\.git)?/?$", url or "")
    return m.groups() if m else None


def _extract(blob: bytes, dest: Path) -> list[str]:
    """Extract only the files we analyse; tarfile's 'data' filter blocks path tricks."""
    kept = []
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
        for m in tf.getmembers():
            rel = m.name.split("/", 1)[1] if "/" in m.name else ""
            if m.isfile() and KEEP.match(rel):
                m.name = rel
                tf.extract(m, dest, filter="data")
                kept.append(rel)
    return kept


async def _fetch_one(c: httpx.AsyncClient, r: dict, sem: asyncio.Semaphore) -> dict:
    out = {"issue": r["issue"], "rework": r["rework"]}
    dest = DATA / "src" / str(r["issue"])
    orr = _owner_repo(r["url"])
    if not orr:
        return out | {"status": "not_github"}
    o, n = orr
    async with sem:
        cr = await c.get(f"https://api.github.com/repos/{o}/{n}/commits",
                         params={"until": r["created"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                                 "per_page": 1})
        if cr.status_code == 404:
            return out | {"status": "repo_gone"}
        if cr.status_code != 200 or not cr.json():
            return out | {"status": f"no_commit_before_submission:{cr.status_code}"}
        sha = cr.json()[0]["sha"]
        tr = await c.get(f"https://api.github.com/repos/{o}/{n}/tarball/{sha}",
                         follow_redirects=True)
    if tr.status_code != 200:
        return out | {"status": f"tarball_http_{tr.status_code}", "sha": sha}
    if len(tr.content) > MAX_TARBALL:
        return out | {"status": "too_big", "sha": sha}
    dest.mkdir(parents=True, exist_ok=True)
    files = await asyncio.to_thread(_extract, tr.content, dest)
    if "DESCRIPTION" not in files:
        return out | {"status": "no_description_at_root", "sha": sha}
    return out | {"status": "ok", "sha": sha, "repo": f"{o}/{n}", "files": files}


def fetch(rows: list[dict], concurrency: int = 10) -> Path:
    """Fetch sources for `rows` not already in the manifest. Resumable."""
    manifest = DATA / "manifest.jsonl"
    done = set()
    if manifest.exists():
        done = {json.loads(line)["issue"] for line in manifest.read_text().splitlines()}
    todo = [r for r in rows if r["issue"] not in done]

    async def go():
        sem = asyncio.Semaphore(concurrency)
        headers = {"Authorization": f"Bearer {token()}", "Accept": "application/vnd.github+json"}
        async with httpx.AsyncClient(headers=headers, timeout=180) as c:
            return await asyncio.gather(*(_fetch_one(c, r, sem) for r in todo))

    DATA.mkdir(parents=True, exist_ok=True)
    results = asyncio.run(go())
    with manifest.open("a") as f:
        f.writelines(json.dumps(x) + "\n" for x in results)
    return manifest


def manifest() -> list[dict]:
    return [json.loads(line) for line in (DATA / "manifest.jsonl").read_text().splitlines()]


# ── index ────────────────────────────────────────────────────────────────────

def _index_one(issue: int) -> tuple[int, str]:
    out = DATA / "scip" / f"issue={issue}"
    if out.exists():
        return issue, "cached"
    scip = DATA / "scip_raw" / f"{issue}.scip"
    scip.parent.mkdir(parents=True, exist_ok=True)
    base = ["uvx", "--quiet", "--from", SCIPR, "scip-r"]
    r = subprocess.run(base + ["index", str(DATA / "src" / str(issue)), "-o", str(scip)],
                       capture_output=True, text=True)
    if r.returncode:
        return issue, "index_failed: " + r.stderr.strip()[-200:]
    r = subprocess.run(base + ["export", str(scip), "--format", "parquet", "-o", str(out)],
                       capture_output=True, text=True)
    return issue, "ok" if not r.returncode else "export_failed: " + r.stderr.strip()[-200:]


def index(jobs: int = 8) -> dict[int, str]:
    ok = [m["issue"] for m in manifest() if m["status"] == "ok"]
    with ThreadPoolExecutor(jobs) as ex:
        return dict(ex.map(_index_one, ok))


# ── features ─────────────────────────────────────────────────────────────────

FEATURE_SQL = """
WITH occ AS (
  SELECT issue, package, index_package, is_definition
  FROM read_parquet('{root}/scip/*/occurrences.parquet', hive_partitioning = true)
), sym AS (
  SELECT issue, exported, is_function, is_class, is_local
  FROM read_parquet('{root}/scip/*/symbols.parquet', hive_partitioning = true)
), calls AS (
  SELECT issue,
         count(*) FILTER (WHERE package IS NOT NULL AND package <> index_package) AS ext_calls,
         count(*) FILTER (WHERE package IN ({core})) AS core_calls,
         count(*) FILTER (WHERE package = 'base') AS base_calls,
         count(DISTINCT package) FILTER (WHERE package NOT IN (index_package, 'base', '.'))
           AS n_dep_pkgs
  FROM occ WHERE NOT is_definition GROUP BY 1
), defs AS (
  SELECT issue,
         count(*) FILTER (WHERE exported AND is_function) AS n_exported_fns,
         count(*) FILTER (WHERE is_class) AS n_classes,
         count(*) FILTER (WHERE is_function AND NOT is_local) AS n_fns
  FROM sym GROUP BY 1
)
SELECT c.issue, c.ext_calls, c.core_calls, c.base_calls, c.n_dep_pkgs,
       d.n_exported_fns, d.n_classes, d.n_fns
FROM calls c JOIN defs d USING (issue)
"""


def features() -> list[dict]:
    core = ", ".join(f"'{p}'" for p in CORE)
    con = duckdb.connect()
    cur = con.execute(FEATURE_SQL.format(root=DATA, core=core))
    cols = [d[0] for d in cur.description]
    code = {int(r[0]): dict(zip(cols, r, strict=True)) for r in cur.fetchall()}
    out = []
    for m in manifest():
        if m["status"] != "ok" or m["issue"] not in code:
            continue
        f = code[m["issue"]]
        files = m["files"]
        ext = max(f["ext_calls"], 1)
        out.append({
            "issue": m["issue"], "label": 0 if m["rework"] else 1, "split": split_of(m["issue"]),
            # code-level (scip-r)
            "frac_core_bioc": f["core_calls"] / ext,
            "uses_core_bioc": float(f["core_calls"] > 0),
            "frac_base": f["base_calls"] / ext,
            "n_dep_pkgs": f["n_dep_pkgs"],
            "n_exported_fns": f["n_exported_fns"],
            "n_classes": f["n_classes"],
            "n_fns": f["n_fns"],
            # file listing
            "has_vignette": float(any(re.match(r"vignettes/.*\.(Rmd|Rnw|qmd|Rmarkdown)$", x,
                                               re.I) for x in files)),
            "has_tests": float(any(x.startswith("tests/") for x in files)),
            "n_test_files": sum(x.startswith("tests/") and x.endswith(".R") for x in files),
            "has_news": float(any("NEWS" in x for x in files)),
            "n_r_files": sum(x.startswith("R/") for x in files),
        })
    (DATA / "features.jsonl").write_text("".join(json.dumps(x) + "\n" for x in out))
    return out


FEATURES = ["frac_core_bioc", "uses_core_bioc", "frac_base", "n_dep_pkgs", "n_exported_fns",
            "n_classes", "n_fns", "has_vignette", "has_tests", "n_test_files", "has_news",
            "n_r_files"]


def _rank(xs: list[float]) -> list[float]:
    """Average ranks (ties share), scaled to 0..1."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 / max(len(xs) - 1, 1)
        i = j + 1
    return r


def eval_features(note: str = "") -> Path:
    """Per-feature AUC on dev and test. Each feature's direction is fixed on dev;
    the combined score (mean rank of dev-useful features) is built on dev and
    applied unchanged to test."""
    rows = [json.loads(x) for x in (DATA / "features.jsonl").read_text().splitlines()]
    dev = [r for r in rows if r["split"] == "dev"]
    test = [r for r in rows if r["split"] == "test"]
    sign = {f: (1 if (auc([r[f] for r in dev], [r["label"] for r in dev]) or 0.5) >= 0.5
                else -1) for f in FEATURES}
    useful = [f for f in FEATURES
              if abs((auc([r[f] for r in dev], [r["label"] for r in dev]) or 0.5) - 0.5) >= 0.05]

    def score(split_rows):
        ranks = {f: _rank([sign[f] * r[f] for r in split_rows]) for f in useful}
        return [sum(ranks[f][i] for f in useful) / max(len(useful), 1)
                for i in range(len(split_rows))]

    m = {}
    for name, part in (("dev", dev), ("test", test)):
        y = [r["label"] for r in part]
        m[name] = {"n": len(part), "n_pos": sum(y), "n_neg": len(y) - sum(y),
                   "auc": {f: auc([sign[f] * r[f] for r in part], y) for f in FEATURES}}
        m[name]["auc"]["combined_dev_selected"] = auc(score(part), y)
    config = {"kind": "features", "features": FEATURES, "sign": sign, "combined_uses": useful,
              "label": "clean accept (1) vs ever 3b/3d/3e (0)", "note": note}
    return record_run("features", config, m, rows,
                      f"test combined AUC={m['test']['auc']['combined_dev_selected']:.3f}")


# ── Clef with code evidence ──────────────────────────────────────────────────

QUESTIONS_V3 = {
    "bioc_fit": "Would an experienced Bioconductor package reviewer consider this package a "
                "good fit for Bioconductor as submitted?",
    "interop_gap": "Does this package work with expression or count matrices, genomic "
                   "ranges, sequences or single-cell data while NOT using the standard "
                   "Bioconductor containers for them (e.g. plain data.frames or matrices, "
                   "or Seurat objects, instead of SummarizedExperiment / SingleCellExperiment "
                   "/ GRanges)?",
    "ready_for_review": "Does this submission look ready for an in-depth review as is: a "
                        "vignette, unit tests, and code built on Bioconductor infrastructure, "
                        "with no obvious changes a moderator would request first?",
}
INVERTED_V3 = {"interop_gap"}


def evidence(issue: int, top: int = 12) -> str:
    """DESCRIPTION + a compact code summary for Clef (a few hundred tokens)."""
    src = DATA / "src" / str(issue)
    desc = (src / "DESCRIPTION").read_text(errors="replace")[:3000]
    con = duckdb.connect()
    base = DATA / "scip" / f"issue={issue}"
    deps = con.execute(f"""SELECT package, count(*) n
        FROM read_parquet('{base}/occurrences.parquet')
        WHERE NOT is_definition AND package IS NOT NULL AND package NOT IN (index_package, '.')
        GROUP BY 1 ORDER BY 2 DESC LIMIT {top}""").fetchall()
    exp = con.execute(f"""SELECT documentation[1] FROM read_parquet('{base}/symbols.parquet')
        WHERE exported AND is_function LIMIT 25""").fetchall()
    classes = con.execute(f"""SELECT name FROM read_parquet('{base}/symbols.parquet')
        WHERE is_class LIMIT 15""").fetchall()
    files = next(m["files"] for m in manifest() if m["issue"] == issue)
    vign = [f for f in files if f.startswith("vignettes/")]
    tests = [f for f in files if f.startswith("tests/")]
    return "\n".join([
        desc, "", "## Code summary (static analysis)",
        "Most-called packages: " + ", ".join(f"{p} ({n})" for p, n in deps),
        f"Exported functions ({len(exp)} shown):", *[f"  {e[0]}" for e in exp],
        "Classes defined: " + (", ".join(c[0] for c in classes) or "none"),
        "Vignette files: " + (", ".join(vign[:5]) or "none"),
        f"Test files: {len(tests)}",
    ])


def eval_clef(split: str = "dev", model: str = "clef", concurrency: int = 8,
              max_n: int | None = None, note: str = "") -> Path:
    if split == "test" and "+dirty" in _git_sha():
        raise SystemExit("Commit the frozen questions before scoring the test split.")
    rows = [json.loads(x) for x in (DATA / "features.jsonl").read_text().splitlines()]
    rows = [r for r in rows if r["split"] == split][:max_n]

    async def go():
        sem, tokens = asyncio.Semaphore(concurrency), 0
        async with clef.client() as c:
            async def one(r):
                nonlocal tokens
                async with sem:
                    p, usage = await clef.decide(c, evidence(r["issue"]), QUESTIONS_V3, model)
                tokens += usage.get("input_tokens", 0)
                return {"issue": r["issue"], "label": r["label"], "p": p}
            return list(await asyncio.gather(*(one(r) for r in rows))), tokens

    preds, tokens = asyncio.run(go())
    y = [p["label"] for p in preds]
    m = {"n": len(preds), "n_pos": sum(y), "n_neg": len(y) - sum(y), "auc": {
        q: auc([(1 - p["p"][q]) if q in INVERTED_V3 else p["p"][q] for p in preds], y)
        for q in QUESTIONS_V3}}
    config = {"kind": "clef+code", "split": split, "model": model, "questions": QUESTIONS_V3,
              "input_tokens": tokens, "est_cost_usd": round(tokens * 0.24 / 1e6, 4), "note": note}
    best = max(m["auc"], key=lambda q: m["auc"][q] or 0)
    return record_run(f"clef-{split}-{model}", config, m, preds,
                      f"{split} n={m['n']} best {best}={m['auc'][best]:.3f} "
                      f"${config['est_cost_usd']}")
