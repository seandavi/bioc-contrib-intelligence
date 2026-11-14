"""Distil past Bioconductor package reviews into checklists, structure notes and examples.

    uv run python experiments/reviews/distil.py all --data ../bioc-contrib-intelligence/data

Stages (each cached under <data>/review-corpus/, so reruns only pay for what is missing):

    extract   Haiku, one call per review comment -> extract.jsonl
    cluster   Sonnet, one call per category: canonical checklist items -> items.json
    assign    Haiku, batches of points -> which item each point is an instance of -> assign.jsonl
    report    Sonnet writes the structure narrative; tables, counts and examples are computed
    cost      sum $ and tokens from AI Gateway logs for metadata.job == review-corpus

Corpus: comments by an issue assignee, not a bot, not the submitter, longer than 1500 chars,
on both trackers. Logins are anonymised in examples.md; package names are kept.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import subprocess
import sys
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from bcintel.db import connect

ACCOUNT = "55bf7202fe14474e57a300f56a652f64"
GATEWAY = f"https://gateway.ai.cloudflare.com/v1/{ACCOUNT}/default/compat/chat/completions"
LOGS = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/ai-gateway/gateways/default/logs"
JOB = "review-corpus"
HAIKU = "anthropic/claude-haiku-5-5"
SONNET = "anthropic/claude-sonnet-5-5"
WORKERS = 8
OUT = Path(__file__).parent / "out"
NEW, LEGACY = "Bioconductor/BiocContributions", "Bioconductor/Contributions"

CATEGORIES = {
    "DESCRIPTION": "DESCRIPTION file fields: Title, Description, Authors@R, biocViews, version, "
                   "License, URL/BugReports",
    "NAMESPACE": "NAMESPACE imports/exports, importFrom vs import, exporting too much",
    "vignette": "vignettes: content, installation chunk, eval=FALSE, sessionInfo, style",
    "man_pages_examples": "Rd/roxygen documentation, runnable examples, \\dontrun, @return",
    "unit_tests": "testthat/RUnit tests and coverage",
    "code_style": "indentation, line length, naming, formatting, commented-out code",
    "coding_practice": "vapply/sapply, seq_len/1:n, loops and vector growth, T/F, "
                       "message vs cat/print, set.seed, file paths, browser(), suppressWarnings",
    "S4_classes_reuse": "reuse of Bioconductor classes/methods (SummarizedExperiment, "
                        "GRanges...), S4 design, accessors, validity",
    "data_ExperimentHub": "package data size, inst/extdata, ExperimentHub/AnnotationHub, "
                          "downloads, data documentation, caching",
    "BiocCheck": "BiocCheck notes/warnings/errors as such",
    "build_check": "R CMD build/check errors, warnings, notes, timings, platforms",
    "dependencies": "Depends/Imports/Suggests choices, heavy or non-CRAN/Bioc deps, "
                    "system requirements",
    "performance": "speed, memory, parallelisation (BiocParallel)",
    "fit_overlap": "fit for Bioconductor, overlap with existing packages, scope, "
                   "interoperability",
    "process": "submission process: version bumps, pushing to git.bioconductor.org, webhooks, "
               "SSH keys, how to respond, timelines",
    "other": "anything else (README, NEWS, licensing of code, inst/ scripts, Shiny...)",
}

EXTRACT_SYSTEM = """You read one comment a Bioconductor reviewer posted on a package \
submission issue and extract what it asks of the submitter. Reply with one JSON object and \
nothing else:

{"review_kind": "first_full_review" | "follow_up" | "other",
  "findings": [{"category": <one of the keys below>,
                "point": "<short normalised imperative, e.g. 'Use vapply instead of sapply'>",
                "quote": "<verbatim excerpt from the comment, at most 200 chars>"}],
  "structure": {"sections": ["<section headings or labels as used, lowercased, short>"],
                "checkboxes": true|false, "numbered_items": true|false,
                "opening": "<first sentence verbatim, at most 120 chars>",
                "sign_off": "<closing sentence verbatim, at most 120 chars, or ''>"},
  "tone": "<at most 20 words on tone and stance>"}

review_kind: first_full_review = the reviewer's initial full review of the package; \
follow_up = response to the submitter's changes or replies, re-review of remaining items; \
other = not a review (process explanation, decline note, build help...).
One finding per distinct request or observation; keep the reviewer's specifics in quote. \
Points are generic enough to recur across packages (no package names in point).

Categories:
""" + "\n".join(f"- {k}: {v}" for k, v in CATEGORIES.items())

CLUSTER_SYSTEM = """You build a reviewer checklist for Bioconductor package submissions. \
Given review points extracted from many past reviews (one category, with how many reviews \
raised each), merge them into 8-25 canonical checklist items that cover the recurring points. \
Each item is one concrete, checkable request, written as an imperative. Reply with JSON only:
{"items": [{"id": 1, "item": "<imperative checklist item>"}, ...]}"""

ASSIGN_SYSTEM = """You map review points to checklist items. For each numbered point, give the \
id of the checklist item it is an instance of, or 0 if none fits. Reply with JSON only: \
{"<point number>": <item id>, ...} covering every point."""

STRUCTURE_SYSTEM = """You describe, for reviewers and an assistant that drafts reviews with \
them, how Bioconductor reviewers structure their written reviews. You get computed statistics \
and a sample of per-comment structure records (sections, checkbox use, opening, sign-off, \
tone). Write concise markdown (no top-level heading) with sections: \
'## First full reviews' and '## Follow-ups' (each: typical skeleton as an ordered outline, \
section names in use, how requests are marked required vs suggested, checkboxes, tone, \
opening and sign-off phrasing with short quoted examples), then '## New tracker vs legacy' \
(only differences supported by the statistics). Cite the statistics you rely on. \
Do not name reviewers or submitters."""


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def token():
    t = os.environ.get("CF_AIG_TOKEN")
    if not t:
        t = subprocess.run(
            ["gcloud", "secrets", "versions", "access", "latest", "--project", "cdsci-infra",
             "--secret", "cdsci-cloudflare-ai-gateway-token"],
            check=True, capture_output=True, text=True).stdout.strip()
        os.environ["CF_AIG_TOKEN"] = t
    return t


@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=2, max=60), reraise=True)
def chat(model, system, user, max_tokens):
    r = httpx.post(GATEWAY, timeout=300, headers={
        "cf-aig-authorization": f"Bearer {token()}", "cf-aig-metadata": json.dumps({"job": JOB})},
        json={"model": model, "max_tokens": max_tokens,
              "messages": [{"role": "system", "content": system},
                           {"role": "user", "content": user}]})
    r.raise_for_status()
    d = r.json()
    return d["choices"][0]["message"]["content"], d.get("usage", {})


def parse_json(text):
    return json.loads(text[text.index("{"): text.rindex("}") + 1])


def chat_json(model, system, user, max_tokens):
    """chat + parse; one re-ask on unparseable output. Returns (obj, usage summed)."""
    usage = Counter()
    for _ in range(2):
        text, u = chat(model, system, user, max_tokens)
        usage.update({k: v for k, v in u.items() if isinstance(v, int)})
        try:
            return parse_json(text), dict(usage)
        except ValueError:
            continue
    raise ValueError(f"unparseable JSON from {model}: {text[:200]!r}")


def read_jsonl(path):
    return [json.loads(x) for x in path.open()] if path.exists() else []


def log_stage(work, stage, started, t0, **extra):
    rec = {"stage": stage, "started_at": started, "finished_at": now(),
           "wall_seconds": round(time.time() - t0, 1), **extra}
    with (work / "runs.jsonl").open("a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec))


def run_pool(fn, items):
    """Apply fn over items with WORKERS threads; returns (ok, errors). fn writes its own cache."""
    ok = err = 0
    with ThreadPoolExecutor(WORKERS) as ex:
        for i, res in enumerate(ex.map(fn, items), 1):
            ok, err = ok + res, err + (not res)
            if i % 100 == 0:
                print(f"  {i}/{len(items)} ok={ok} err={err}", file=sys.stderr)
    return ok, err


# ── corpus ───────────────────────────────────────────────────────────────────

CORPUS_SQL = """
WITH c AS (
  SELECT c.repo, c.issue_number, c.id, c.author, c.created_at, c.body, i.author AS submitter,
         list_contains(i.assignees, c.author) AND NOT c.is_bot AND c.author <> i.author
           AS by_reviewer
  FROM comments c JOIN issues i ON i.repo = c.repo AND i.number = c.issue_number
), r AS (
  SELECT *, count(*) FILTER (WHERE by_reviewer) OVER w - 1 AS prior_reviewer_comments
  FROM c WINDOW w AS (PARTITION BY repo, issue_number ORDER BY created_at, id)
)
SELECT r.repo, r.issue_number, r.id, r.author, r.submitter, r.created_at::VARCHAR AS created_at,
       r.body, r.prior_reviewer_comments, p.package_name,
       row_number() OVER (PARTITION BY r.repo, r.issue_number ORDER BY r.created_at, r.id)
         AS long_ordinal
FROM r LEFT JOIN packages p ON p.repo = r.repo AND p.issue_number = r.issue_number
WHERE r.by_reviewer AND length(r.body) > 1500
ORDER BY r.id
"""


def corpus(data):
    con = connect(data)
    cur = con.execute(CORPUS_SQL)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row, strict=True)) for row in cur.fetchall()]


# ── stages ───────────────────────────────────────────────────────────────────

def extract(work, rows, limit=None):
    cache = work / "extract.jsonl"
    done = {r["id"] for r in read_jsonl(cache) if "result" in r}
    todo = [r for r in rows if r["id"] not in done][:limit]
    lock = threading.Lock()
    started, t0 = now(), time.time()

    def one(r):
        user = (f"Tracker: {r['repo']} ({'current' if r['repo'] == NEW else 'legacy'})\n"
                f"Earlier comments by this reviewer on this issue: "
                f"{r['prior_reviewer_comments']}\n\nComment:\n{r['body'][:24000]}")
        rec = {"id": r["id"], "repo": r["repo"], "issue_number": r["issue_number"],
               "model": HAIKU}
        try:
            rec["result"], rec["usage"] = chat_json(HAIKU, EXTRACT_SYSTEM, user, 12000)
        except Exception as e:  # recorded and retried on the next run
            rec["error"] = repr(e)[:300]
        with lock, cache.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        return "result" in rec

    ok, err = run_pool(one, todo)
    log_stage(work, "extract", started, t0, model=HAIKU, todo=len(todo), ok=ok, error=err)


def extracted(work, rows):
    """Latest successful extraction per corpus comment, joined to its corpus row."""
    by_id = {r["id"]: r for r in rows}
    out = {}
    for rec in read_jsonl(work / "extract.jsonl"):
        if "result" in rec and rec["id"] in by_id:
            out[rec["id"]] = {**by_id[rec["id"]], **rec["result"]}
    return out


def findings(ex):
    """Flat list of (comment_id, category, point, quote) for valid categories."""
    out = []
    for cid, e in sorted(ex.items()):
        for f in e.get("findings") or []:
            if isinstance(f, dict) and f.get("category") in CATEGORIES and f.get("point"):
                out.append((cid, f["category"], f["point"].strip(), (f.get("quote") or "")[:200]))
    return out


def cluster(work, rows):
    path = work / "items.json"
    items = json.loads(path.read_text()) if path.exists() else {}
    pts = defaultdict(Counter)
    for _, cat, point, _ in findings(extracted(work, rows)):
        pts[cat][point.lower().rstrip(".")] += 1
    started, t0, usage = now(), time.time(), Counter()
    for cat in CATEGORIES:
        if cat in items or not pts[cat]:
            continue
        # ponytail: cap at the 1500 most frequent distinct points; long tail is near-unique
        lines = [f"{n}x {p}" for p, n in pts[cat].most_common(1500)]
        obj, u = chat_json(SONNET, CLUSTER_SYSTEM,
                           f"Category: {cat} ({CATEGORIES[cat]})\n\n" + "\n".join(lines), 8000)
        usage.update(u)
        items[cat] = obj["items"]
        path.write_text(json.dumps(items, indent=1))
    log_stage(work, "cluster", started, t0, model=SONNET, usage=dict(usage))


def assign(work, rows):
    cache = work / "assign.jsonl"
    items = json.loads((work / "items.json").read_text())
    done = {(r["category"], r["batch"]) for r in read_jsonl(cache) if "map" in r}
    by_cat = defaultdict(list)
    for f in findings(extracted(work, rows)):
        by_cat[f[1]].append(f)
    batches = []
    for cat, fs in by_cat.items():
        for b in range(0, len(fs), 80):
            if (cat, b) not in done:
                batches.append((cat, b, fs[b:b + 80]))
    lock = threading.Lock()
    started, t0 = now(), time.time()

    def one(batch):
        cat, b, fs = batch
        menu = "\n".join(f"{it['id']}. {it['item']}" for it in items.get(cat, []))
        pts = "\n".join(f"{i}. {f[2]}" for i, f in enumerate(fs, 1))
        rec = {"category": cat, "batch": b, "keys": [[f[0], f[2]] for f in fs]}
        try:
            m, rec["usage"] = chat_json(HAIKU, ASSIGN_SYSTEM,
                                        f"Checklist items:\n{menu}\n\nPoints:\n{pts}", 8000)
            rec["map"] = {k: int(v) for k, v in m.items()}
        except Exception as e:
            rec["error"] = repr(e)[:300]
        with lock, cache.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        return "map" in rec

    ok, err = run_pool(one, batches)
    log_stage(work, "assign", started, t0, model=HAIKU, todo=len(batches), ok=ok, error=err)


# ── report ───────────────────────────────────────────────────────────────────

def pct(n, d):
    return f"{100 * n / d:.0f}%" if d else "–"


def report(work, rows):
    ex = extracted(work, rows)
    items = json.loads((work / "items.json").read_text())
    first = {cid for cid, e in ex.items() if e.get("review_kind") == "first_full_review"}
    n_first = {t: sum(ex[c]["repo"] == t for c in first) for t in (NEW, LEGACY)}
    # (comment_id, point) -> item id, from the latest successful batch
    item_of = {}
    for rec in read_jsonl(work / "assign.jsonl"):
        if "map" in rec:
            for i, (cid, point) in enumerate(rec["keys"], 1):
                item_of[(rec["category"], cid, point)] = rec["map"].get(str(i), 0)
    hits = defaultdict(set)      # (cat, item id) -> comment ids
    quotes = defaultdict(list)   # (cat, item id) -> (author, quote) from first reviews
    cat_hits = defaultdict(set)
    for cid, cat, point, quote in findings(ex):
        cat_hits[cat].add(cid)
        k = (cat, item_of.get((cat, cid, point), 0))
        hits[k].add(cid)
        if cid in first and 40 <= len(quote):
            quotes[k].append((ex[cid]["author"], quote))

    def first_pct(cids, tracker=None):
        sel = [c for c in cids if c in first and (tracker is None or ex[c]["repo"] == tracker)]
        den = len(first) if tracker is None else n_first[tracker]
        return pct(len(sel), den)

    rng = random.Random(34)
    n_issues = len({(e["repo"], e["issue_number"]) for e in ex.values()})
    lines = [
        "# Review checklist distilled from past reviews",
        "",
        f"Source: {len(ex):,} long reviewer comments on {n_issues:,} "
        f"submissions ({sum(e['repo'] == NEW for e in ex.values())} new tracker, "
        f"{sum(e['repo'] == LEGACY for e in ex.values()):,} legacy); "
        f"{len(first):,} classified as first full reviews ({n_first[NEW]} new, "
        f"{n_first[LEGACY]:,} legacy). Method and caveats: `experiments/reviews/LEDGER.md`.",
        "",
        "Columns: **reviews** = comments raising the item (any kind); **first** = share of "
        "first full reviews raising it, overall / new tracker / legacy. Items are ordered by "
        "reviews. Typical wording is quoted verbatim from first reviews (two different "
        "reviewers where possible). New-tracker shares rest on few reviews "
        f"({n_first[NEW]}), so treat differences under ~10 points as noise.",
        "",
        "| Category | reviews | first | first (new) | first (legacy) |",
        "|---|---|---|---|---|",
    ]
    for cat in sorted(CATEGORIES, key=lambda c: -len(cat_hits[c])):
        c = cat_hits[cat]
        lines.append(f"| [{cat}](#{cat.lower()}) | {len(c):,} | {first_pct(c)} | "
                     f"{first_pct(c, NEW)} | {first_pct(c, LEGACY)} |")
    for cat in sorted(CATEGORIES, key=lambda c: -len(cat_hits[c])):
        lines += ["", f"## {cat}", "", f"_{CATEGORIES[cat]}_", "",
                  "| # | Item | reviews | first | new | legacy |", "|---|---|---|---|---|---|"]
        its = sorted(items.get(cat, []), key=lambda it: -len(hits[(cat, it["id"])]))
        its = [it for it in its if hits[(cat, it["id"])]]
        for n, it in enumerate(its, 1):
            h = hits[(cat, it["id"])]
            lines.append(f"| {n} | {it['item']} | {len(h):,} | {first_pct(h)} | "
                         f"{first_pct(h, NEW)} | {first_pct(h, LEGACY)} |")
        if hits[(cat, 0)]:
            lines.append(f"| – | _unmatched points_ | {len(hits[(cat, 0)]):,} | | | |")
        lines += ["", "Typical wording:", ""]
        for n, it in enumerate(its, 1):
            qs, seen = quotes[(cat, it["id"])], set()
            rng.shuffle(qs)
            picked = [q for a, q in qs if not (a in seen or seen.add(a))][:2]
            for q in picked:
                q = " ".join(q.split()).replace("|", "\\|")
                lines.append(f"- {n}. “{q}”")
    (OUT / "checklist.md").write_text("\n".join(lines) + "\n")

    structure_report(work, ex, rng)
    examples_report(ex, rows)


def structure_report(work, ex, rng):
    kinds = ("first_full_review", "follow_up", "other")
    stats = {}
    for t in (NEW, LEGACY):
        for k in kinds:
            es = [e for e in ex.values() if e["repo"] == t and e.get("review_kind") == k]
            st = [e.get("structure") or {} for e in es]
            secs = Counter(s for x in st for s in set(x.get("sections") or []))
            stats[(t, k)] = {
                "n": len(es),
                "checkboxes": pct(sum(bool(x.get("checkboxes")) for x in st), len(es)),
                "numbered_items": pct(sum(bool(x.get("numbered_items")) for x in st), len(es)),
                "median_chars": sorted(len(e["body"]) for e in es)[len(es) // 2] if es else 0,
                "median_findings": sorted(len(e.get("findings") or []) for e in es)[len(es) // 2]
                if es else 0,
                "top_sections": [(s, pct(n, len(es))) for s, n in secs.most_common(15)],
            }
    sample = []
    for k in ("first_full_review", "follow_up"):
        for t, n in ((NEW, 60), (LEGACY, 140)):
            es = [e for e in ex.values() if e["repo"] == t and e.get("review_kind") == k]
            for e in rng.sample(es, min(n, len(es))):
                sample.append({"kind": k, "tracker": "new" if t == NEW else "legacy",
                               "structure": e.get("structure"), "tone": e.get("tone")})
    stat_txt = json.dumps({f"{'new' if t == NEW else 'legacy'}/{k}": v
                           for (t, k), v in stats.items()}, indent=1)
    started, t0 = now(), time.time()
    text, usage = chat(SONNET, STRUCTURE_SYSTEM,
                       f"Statistics:\n{stat_txt}\n\nSample records:\n"
                       + "\n".join(json.dumps(s) for s in sample), 6000)
    log_stage(work, "structure", started, t0, model=SONNET, usage=usage)
    lines = ["# How reviewers structure reviews", "",
             "Written by the synthesis model from the computed statistics below and a sample "
             f"of {len(sample)} per-comment structure records; the tables are computed "
             "directly. See `LEDGER.md` for method.", "", text.strip(), "",
             "## Statistics", "",
             "| Tracker | Kind | comments | checkboxes | numbered items | median chars | "
             "median findings |", "|---|---|---|---|---|---|---|"]
    for (t, k), v in stats.items():
        lines.append(f"| {'new' if t == NEW else 'legacy'} | {k} | {v['n']:,} | "
                     f"{v['checkboxes']} | {v['numbered_items']} | {v['median_chars']:,} | "
                     f"{v['median_findings']} |")
    for (t, k), v in stats.items():
        if k == "other" or not v["n"]:
            continue
        lines += ["", f"Most common section labels, {'new' if t == NEW else 'legacy'} "
                  f"tracker, {k} (share of comments):", "",
                  ", ".join(f"`{s}` {p}" for s, p in v["top_sections"])]
    (OUT / "structure.md").write_text("\n".join(lines) + "\n")


EXAMPLES = {  # (repo, issue_number): why it was picked; chosen by reading candidates
    ("Bioconductor/BiocContributions", 56):
        "New tracker; checkbox list grouped by file, 13 categories, one follow-up.",
    ("Bioconductor/BiocContributions", 75):
        "New tracker; uses the reviewer checklist template headings, quotes BiocCheck output.",
    ("Bioconductor/Contributions", 762):
        "Legacy tracker; leads with fit/interoperability, then build report and file sections; "
        "two follow-ups.",
}


def anonymise(text, logins):
    """Replace known logins and any @mention with stable role labels."""
    def sub(m):
        name = m.group(1)
        key = name.lower()
        if key not in logins:
            logins[key] = f"user-{sum(v.startswith('user-') for v in logins.values()) + 1}"
        return ("@" if m.group(0).startswith("@") else "") + logins[key]
    for login in sorted(logins, key=len, reverse=True):
        text = re.sub(rf"(?<![\w-]){re.escape(login)}(?![\w-])", logins[login], text, flags=re.I)
    return re.sub(r"@([A-Za-z0-9](?:[A-Za-z0-9-]{0,38}))\b", sub, text)


def examples_report(ex, rows):
    lines = ["# Example reviews", "",
             "Representative first full reviews and follow-ups, verbatim except that GitHub "
             "logins are replaced with role labels (reviewer-n, submitter-n, user-n). Package "
             "names are kept. Picked by reading candidates that cover many checklist "
             "categories, from different reviewers; see `LEDGER.md`."]
    reviewers, submitters = {}, {}
    for (repo, num), why in EXAMPLES.items():
        es = sorted((e for e in ex.values() if e["repo"] == repo and e["issue_number"] == num),
                    key=lambda e: e["created_at"])
        for e in es:
            if e.get("review_kind") not in ("first_full_review", "follow_up"):
                continue
            rv = reviewers.setdefault(e["author"].lower(), f"reviewer-{len(reviewers) + 1}")
            sb = submitters.setdefault(e["submitter"].lower(), f"submitter-{len(submitters) + 1}")
            logins = {e["author"].lower(): rv, e["submitter"].lower(): sb}
            body = anonymise(e["body"], logins)
            lines += ["", f"## {e['package_name']}: {e['review_kind'].replace('_', ' ')} "
                      f"({'new' if repo == NEW else 'legacy'} tracker, "
                      f"{e['created_at'][:7]})", "", f"_{why}_", "",
                      "````markdown", body.strip(), "````"]
    (OUT / "examples.md").write_text("\n".join(lines) + "\n")


# ── cost ─────────────────────────────────────────────────────────────────────

def cost(work):
    """Sum gateway-logged cost/tokens for this job since the first stage started."""
    runs = read_jsonl(work / "runs.jsonl")
    since = min(r["started_at"] for r in runs)
    tot = defaultdict(Counter)
    page = 1
    while True:
        r = httpx.get(LOGS, headers={"Authorization": f"Bearer {token()}"}, timeout=60,
                      params={"per_page": 50, "page": page, "order_by": "created_at",
                              "order_by_direction": "desc"})
        r.raise_for_status()
        logs = r.json()["result"]
        for g in logs:
            if g["created_at"] >= since and (g.get("metadata") or {}).get("job") == JOB:
                t = tot[g["model"]]
                t.update(calls=1, tokens_in=g["tokens_in"] or 0, tokens_out=g["tokens_out"] or 0,
                         failed=not g["success"])
                t["cost_usd"] += g["cost"] or 0
        if not logs or logs[-1]["created_at"] < since:
            break
        page += 1
    out = {"since": since, "until": now(), "by_model": {m: dict(t) for m, t in tot.items()}}
    (work / "cost.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("stage", choices=["extract", "cluster", "assign", "report", "cost", "all"])
    ap.add_argument("--data", default="data", help="bcintel data dir (gitignored)")
    ap.add_argument("--limit", type=int, help="extract at most N not-yet-cached comments")
    a = ap.parse_args()
    work = Path(a.data) / "review-corpus"
    work.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(exist_ok=True)
    rows = corpus(a.data)
    if a.stage in ("extract", "all"):
        extract(work, rows, a.limit)
    for name, fn in (("cluster", cluster), ("assign", assign), ("report", report)):
        if a.stage in (name, "all"):
            fn(work, rows)
    if a.stage in ("cost", "all"):
        cost(work)


if __name__ == "__main__":
    main()
