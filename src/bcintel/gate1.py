"""Gate 1 eval: can a decision model (Clef) tell, from a submission's DESCRIPTION
alone, which packages Bioconductor ends up accepting vs declining / sending back
for interoperability?

Labels: the legacy tracker's final outcome label (last of 3a accepted, 3b declined,
3d needs interop). 3c inactive is excluded: abandonment, not fit. So are 3b issues
closed for inactivity (the declined label was used for those too). Input: the
DESCRIPTION the bot posted at submission time, so nothing from the review leaks in.

Splits are a fixed hash of the issue number: iterate questions on `dev`, score
`test` once the questions are frozen. Each run writes
experiments/gate1/runs/<run_id>/{config.json,predictions.jsonl,metrics.json}
and appends a line to experiments/gate1/LEDGER.md.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import random
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from . import clef, db

EXP = Path("experiments/gate1")
NEG = {"3b. declined": "declined", "3d. needs interop": "interop"}

# Questions under evaluation (v1). Edit here, re-run on dev, compare in the ledger.
QUESTIONS = {
    "in_scope": "Is this R package's purpose the analysis, annotation, visualization or "
                "access of biological or biomedical data (genomics, transcriptomics, "
                "proteomics, imaging, etc.)?",
    "uses_bioc_classes": "Does the package build on standard Bioconductor data structures "
                         "(e.g. SummarizedExperiment, SingleCellExperiment, GRanges, "
                         "Biostrings, MultiAssayExperiment) according to its Imports/Depends?",
    "needs_bioc_classes": "Does this package work with data that Bioconductor already has "
                          "standard containers for (count or expression matrices with sample "
                          "metadata, genomic ranges, sequences, single-cell data)?",
    "general_tool": "Is this a reusable, general-purpose tool rather than code for a single "
                    "paper, dataset or lab pipeline?",
    "interop_gap": "Does this package work with expression or count matrices, genomic "
                   "ranges, sequences or single-cell data while NOT using the standard "
                   "Bioconductor containers for them (e.g. plain data.frames or matrices, "
                   "or Seurat objects, instead of SummarizedExperiment / SingleCellExperiment "
                   "/ GRanges)?",
    "bioc_fit": "Would an experienced Bioconductor package reviewer consider this package a "
                "good fit for Bioconductor as submitted?",
}

INVERTED = {"interop_gap"}

# Deterministic baseline: does Imports/Depends name a core Bioc infrastructure package?
CORE = ("SummarizedExperiment SingleCellExperiment SpatialExperiment MultiAssayExperiment "
        "GenomicRanges IRanges Biostrings S4Vectors BiocGenerics Biobase GenomicFeatures "
        "DelayedArray rtracklayer AnnotationDbi BiocParallel BiocFileCache ExperimentHub "
        "AnnotationHub TreeSummarizedExperiment VariantAnnotation").split()

DATASET = r"""
WITH outc AS (
  SELECT issue_number, arg_max(to_label, changed_at) AS final
  FROM label_transitions
  WHERE repo = 'Bioconductor/Contributions'
    AND to_label IN ('3a. accepted', '3b. declined', '3d. needs interop')
  GROUP BY 1
), d AS (
  SELECT issue_number,
         arg_min(regexp_extract(body, 'DESCRIPTION file for this package is:\s*```\s*(.*?)```',
                                1, 's'), created_at) AS descr
  FROM comments
  WHERE repo = 'Bioconductor/Contributions' AND is_bot AND body LIKE '%DESCRIPTION file%'
  GROUP BY 1
)
SELECT o.issue_number, o.final, d.descr FROM outc o JOIN d USING (issue_number)
WHERE coalesce(d.descr, '') <> ''
  AND NOT (o.final = '3b. declined' AND o.issue_number IN (
      SELECT issue_number FROM comments WHERE repo = 'Bioconductor/Contributions'
        AND (body ILIKE '%due to inactivity%' OR body ILIKE '%without activity%')))
ORDER BY 1
"""


def split_of(n: int) -> str:
    """Fixed 20/80 dev/test split by issue number."""
    return "dev" if int(hashlib.sha256(str(n).encode()).hexdigest(), 16) % 5 == 0 else "test"


def label_of(final: str) -> int:
    """1 = accepted (positive), 0 = declined or needs interop."""
    return 1 if final == "3a. accepted" else 0


def baseline(descr: str) -> float:
    deps = " ".join(re.findall(r"^(?:Imports|Depends):(.*(?:\n[ \t].*)*)", descr, re.M))
    return 1.0 if any(re.search(rf"\b{p}\b", deps) for p in CORE) else 0.0


def auc(scores: list[float], labels: list[int]) -> float | None:
    """ROC AUC via the Mann-Whitney U statistic (ties count half)."""
    pos = [s for s, y in zip(scores, labels, strict=True) if y == 1]
    neg = [s for s, y in zip(scores, labels, strict=True) if y == 0]
    if not pos or not neg:
        return None
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def load(split: str, max_accepted: int, seed: int = 0) -> list[dict]:
    rows = [dict(zip(("issue", "final", "descr"), r, strict=True))
            for r in db.connect().execute(DATASET).fetchall()]
    rows = [r for r in rows if split_of(r["issue"]) == split]
    neg = [r for r in rows if r["final"] in NEG]
    pos = [r for r in rows if r["final"] == "3a. accepted"]
    random.Random(seed).shuffle(pos)  # ponytail: subsample accepted; class ratio is not real-world
    return neg + pos[:max_accepted]


def _git_sha() -> str:
    out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    return out.stdout.strip() + ("+dirty" if dirty.stdout.strip() else "")


def metrics(preds: list[dict]) -> dict:
    labels = [p["label"] for p in preds]
    # Questions where "yes" signals a problem are scored as 1 - p, so AUC > 0.5 = useful.
    s = lambda p, q: 1 - p["p"][q] if q in INVERTED else p["p"][q]  # noqa: E731
    m = {"n": len(preds), "n_pos": sum(labels), "n_neg": len(labels) - sum(labels),
         "auc": {q: auc([s(p, q) for p in preds], labels) for q in QUESTIONS}}
    m["auc"]["baseline_core_imports"] = auc([p["baseline"] for p in preds], labels)
    # Interop question vs the interop label alone (accepted vs needs-interop).
    sub = [p for p in preds if p["final"] != "3b. declined"]
    m["auc_interop_only"] = {
        q: auc([s(p, q) for p in sub], [p["label"] for p in sub])
        for q in ("uses_bioc_classes", "needs_bioc_classes", "interop_gap")}
    m["auc_interop_only"]["baseline_core_imports"] = auc(
        [p["baseline"] for p in sub], [p["label"] for p in sub])
    return m


async def _score(rows: list[dict], model: str, concurrency: int) -> tuple[list[dict], int]:
    sem, tokens = asyncio.Semaphore(concurrency), 0
    async with clef.client() as c:
        async def one(r):
            nonlocal tokens
            async with sem:
                p, usage = await clef.decide(c, r["descr"], QUESTIONS, model=model)
            tokens += usage.get("input_tokens", 0)
            return {"issue": r["issue"], "final": r["final"], "label": label_of(r["final"]),
                    "baseline": baseline(r["descr"]), "p": p}
        return list(await asyncio.gather(*(one(r) for r in rows))), tokens


def run(split: str = "dev", max_accepted: int = 40, model: str = "clef",
        concurrency: int = 8, note: str = "") -> Path:
    if split == "test" and "+dirty" in _git_sha():
        raise SystemExit("Commit the frozen questions before scoring the test split.")
    started = datetime.now(timezone.utc)
    rows = load(split, max_accepted)
    preds, tokens = asyncio.run(_score(rows, model, concurrency))
    config = {"split": split, "model": model, "max_accepted": max_accepted,
              "questions": QUESTIONS, "note": note,
              "input_tokens": tokens, "est_cost_usd": round(tokens * 0.24 / 1e6, 4)}
    m = metrics(preds)
    best = max((q for q in m["auc"] if m["auc"][q] is not None), key=lambda q: m["auc"][q])
    return record_run(f"{split}-{model}", config, m, preds,
                      f"n={m['n']} ({m['n_pos']}+/{m['n_neg']}-) · best AUC {best}="
                      f"{m['auc'][best]:.3f} · baseline={m['auc']['baseline_core_imports']:.3f}"
                      f" · ${config['est_cost_usd']}", started=started)


def record_run(tag: str, config: dict, metrics_: dict, preds: list[dict], summary: str,
               exp: Path = EXP, started: datetime | None = None) -> Path:
    """Write <exp>/runs/<run_id>/{config,metrics,predictions} and append a LEDGER line.
    Pass `started` (UTC) to record wall-clock time alongside tokens and cost."""
    finished = datetime.now(timezone.utc)
    run_id = finished.strftime("%Y%m%dT%H%M%SZ") + f"-{tag}"
    if started is not None:
        config = {"started_at": started.isoformat(timespec="seconds"),
                  "finished_at": finished.isoformat(timespec="seconds"),
                  "wall_seconds": round((finished - started).total_seconds(), 1), **config}
        summary += f" · {config['wall_seconds']}s"
    out = exp / "runs" / run_id
    out.mkdir(parents=True)
    config = {"run_id": run_id, "git": _git_sha(), **config}
    (out / "config.json").write_text(json.dumps(config, indent=2))
    (out / "metrics.json").write_text(json.dumps(metrics_, indent=2))
    (out / "predictions.jsonl").write_text("".join(json.dumps(p) + "\n" for p in preds))
    ledger = exp / "LEDGER.md"
    if not ledger.exists():
        ledger.write_text(f"# {exp.name} ledger\n\nAppend-only. One line per run; details in "
                          "runs/<run_id>/.\n\n")
    note = config.get("note")
    with ledger.open("a") as f:
        f.write(f"- {run_id} · git {config['git']} · {summary}" + (f" · {note}" if note else "")
                + "\n")
    return out
