"""Comment signals: a Clef pass over human tracker comments.

Each human comment (bots and slash commands excluded, via the `activity` view)
is sent with its thread context and asked a role-specific set of typed
questions: is it a question, does it hand the turn over, what does a reviewer
ask for, does the submitter claim to be done, and so on. Answers feed the
dashboard (ball-in-court, unanswered questions, stuck submitters, outstanding
request categories) and a "what slows reviews down" analysis joined with
timing from SQL.

Runs are recorded under experiments/comments/ (config, predictions, LEDGER line).
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path

from . import clef, db
from .gate1 import record_run

EXP = Path("experiments/comments")

YN = str  # a bare string is a yes/no question


def choice(instructions: str, criteria: dict[str, str]) -> dict:
    return {"type": "choice", "instructions": instructions, "criteria": criteria}


def score(instructions: str, levels: list[str]) -> dict:
    return {"type": "score", "instructions": instructions, "criteria": levels}


COMMON = {
    "asks_question": "Does the COMMENT TO EVALUATE ask the other party a question that needs "
                     "an answer before the work can continue?",
    "question_kind": choice(
        "What kind of question, if any, does the COMMENT TO EVALUATE ask?",
        {"clarification": "asks what an earlier request means or how to satisfy it",
         "technical": "asks how to do something in R/Bioconductor, or about an error",
         "process": "asks about the submission or review process, policy, timing or next "
                    "steps",
         "scope": "asks whether the package or a feature is appropriate for Bioconductor",
         "negotiation": "asks whether a request can be waived, deferred or done differently",
         "none": "asks no question"}),
    "hands_off": "After the COMMENT TO EVALUATE, is it now the other party's turn to act: to "
                 "review, answer a question, make a decision or make changes? Answer no if "
                 "the author is only acknowledging, says they are still working, or the "
                 "conversation is finished.",
    "blocked": "Does the author of the COMMENT TO EVALUATE say they cannot make progress "
               "without someone else's help (e.g. an error they cannot resolve, missing "
               "access, a broken build system)? Asking permission or asking an ordinary "
               "question is not being blocked.",
    "pushback": "Does the author of the COMMENT TO EVALUATE disagree with or argue against a "
                "request or decision?",
    "tone": score("What is the tone of the COMMENT TO EVALUATE?",
                  ["curt or harsh", "neutral", "warm and encouraging"]),
    "delay_notice": "Does the COMMENT TO EVALUATE apologise for a delay, or say the author is "
                    "busy, forgot, or will respond later?",
    "urgency": "Does the COMMENT TO EVALUATE ask for faster action or mention a deadline "
               "(e.g. a release date, a paper or grant deadline)?",
    "about_build": "Does the COMMENT TO EVALUATE mainly discuss errors, warnings or results "
                   "reported by automated checks or builds (R CMD check, BiocCheck, the build "
                   "system), rather than the package's code, design or content?",
}

REVIEWER = {
    "review_kind": choice(
        "What kind of comment is the COMMENT TO EVALUATE, from the reviewer or Bioconductor "
        "team?",
        {"full_review": "a substantive review of the package, requesting changes or "
                        "approving it",
         "partial_review": "some review points, explicitly promising more later",
         "follow_up": "responds to the submitter's changes or replies on earlier points",
         "nudge": "reminds or chases the submitter for a response",
         "administrative": "a process note: assignment, labels, policy, triggering builds"}),
    "n_requests": score("How many distinct changes does the COMMENT TO EVALUATE ask the "
                        "submitter to make?",
                        ["none", "1-2", "3-5", "6-10", "more than 10"]),
    "req_checks": "Does the COMMENT TO EVALUATE ask the submitter to fix errors, warnings "
                  "or notes that it explicitly attributes to R CMD check, BiocCheck or the "
                  "build report?",
    "req_vignette": "Does the COMMENT TO EVALUATE ask for changes to the vignette?",
    "req_tests": "Does the COMMENT TO EVALUATE ask for unit tests to be added or improved?",
    "req_docs": "Does the COMMENT TO EVALUATE ask for changes to man pages, examples or the "
                "README?",
    "req_interop": "Does the COMMENT TO EVALUATE ask the submitter to use or support "
                   "Bioconductor classes such as SummarizedExperiment, GRanges or "
                   "SingleCellExperiment?",
    "req_code_style": "Does the COMMENT TO EVALUATE ask for changes to coding style or "
                      "practices (e.g. vapply instead of sapply, seq_along, avoiding T/F)?",
    "req_data": "Does the COMMENT TO EVALUATE raise data size, data provenance, or moving "
                "data to ExperimentHub/AnnotationHub?",
    "req_metadata": "Does the COMMENT TO EVALUATE ask for changes to DESCRIPTION fields, "
                    "version, biocViews, license or authors?",
    "req_scope": "Does the COMMENT TO EVALUATE question whether the package or parts of it "
                 "belong in Bioconductor?",
    "request_clarity": score("How concrete are the change requests in the COMMENT TO "
                             "EVALUATE?",
                             ["vague", "mixed", "concrete and checkable"]),
    "effort_implied": score("How much work do the requests in the COMMENT TO EVALUATE imply "
                            "for the submitter?",
                            ["none or trivial", "moderate changes", "major rework"]),
    "new_requests": "Compared with THIS AUTHOR'S PREVIOUS COMMENT, does the COMMENT TO "
                    "EVALUATE raise change requests that were not asked for before?",
    "decision_signal": choice(
        "Does the COMMENT TO EVALUATE signal a decision on the package?",
        {"none": "no decision signal", "lean_accept": "close to acceptance",
         "accept": "accepts the package", "lean_decline": "doubts the package will be "
         "accepted", "decline": "declines the package"}),
}

SUBMITTER = {
    "claims_all_addressed": "Does the COMMENT TO EVALUATE say that all requested changes "
                            "have been made?",
    "claims_partial": "Does the COMMENT TO EVALUATE say that only some requested changes "
                      "have been made so far?",
    "explains_not_doing": "Does the COMMENT TO EVALUATE explain why a requested change will "
                          "not be made?",
    "asks_for_help": "Does the COMMENT TO EVALUATE ask for help or guidance rather than just "
                     "a review?",
    "newcomer": "Does the author of the COMMENT TO EVALUATE say they are new to Bioconductor "
                "or R package development, or ask how basic Bioconductor processes work?",
}


def questions_for(role: str) -> dict:
    return COMMON | (SUBMITTER if role == "submitter" else REVIEWER)


THREAD = r"""
WITH a AS (
  SELECT a.repo, a.issue_number, a.occurred_at, a.who, a.role, a.body,
         lag(a.who) OVER w AS prev_who, lag(a.role) OVER w AS prev_role,
         lag(a.body) OVER w AS prev_body,
         lag(a.body) OVER (PARTITION BY a.repo, a.issue_number, a.who
                           ORDER BY a.occurred_at) AS own_prev_body
  FROM activity a WHERE a.kind = 'comment'
  WINDOW w AS (PARTITION BY a.repo, a.issue_number ORDER BY a.occurred_at)
)
SELECT a.*, p.package_name, i.author AS submitter, i.assignees,
       c.id AS comment_id
FROM a
JOIN issues i ON i.repo = a.repo AND i.number = a.issue_number
JOIN packages p ON p.repo = a.repo AND p.issue_number = a.issue_number
JOIN comments c ON c.repo = a.repo AND c.issue_number = a.issue_number
                AND c.created_at = a.occurred_at AND c.author = a.who
WHERE a.repo = $repo
ORDER BY c.id  -- stable order so seeded samples are reproducible
"""


def load(repo: str = "Bioconductor/Contributions") -> list[dict]:
    cur = db.connect().execute(THREAD, {"repo": repo})
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r, strict=True)) for r in cur.fetchall()]


def state(c: dict) -> str:
    """The text Clef sees: thread roles, context, then the comment itself."""
    def cut(t, n):
        t = t or ""
        return t if len(t) <= n else t[:n] + " […truncated]"
    parts = [f"Bioconductor package submission review thread, issue #{c['issue_number']} "
             f"(package: {c['package_name']}).",
             f"Roles: submitter = {c['submitter']}; assigned reviewer(s) = "
             f"{', '.join(c['assignees'] or []) or 'none'}; others are Bioconductor team.",
             "", f"PREVIOUS COMMENT (by {c['prev_who']}, {c['prev_role']}):"
             if c["prev_who"] else "PREVIOUS COMMENT: (none, this is the first)",
             cut(c["prev_body"], 800)]
    if c["role"] != "submitter":
        parts += ["", "THIS AUTHOR'S PREVIOUS COMMENT:", cut(c["own_prev_body"], 800) or "(none)"]
    parts += ["", f"COMMENT TO EVALUATE (by {c['who']}, {c['role']}):", cut(c["body"], 3000)]
    return "\n".join(parts)


def sample(rows: list[dict], per_role: dict[str, int], seed: int = 0) -> list[dict]:
    rng, out = random.Random(seed), []
    for role, k in per_role.items():
        pool = [r for r in rows if r["role"] == role]
        out += rng.sample(pool, k)
    return out


def run(rows: list[dict], tag: str, note: str = "", concurrency: int = 8,
        model: str = "clef") -> Path:
    started = datetime.now(timezone.utc)

    async def go():
        sem, tokens = asyncio.Semaphore(concurrency), 0
        async with clef.client() as c:
            async def one(r):
                nonlocal tokens
                async with sem:
                    a, usage = await clef.decide(c, state(r), questions_for(r["role"]), model)
                tokens += usage.get("input_tokens", 0)
                return {"comment_id": r["comment_id"], "issue": r["issue_number"],
                        "role": r["role"], "who": r["who"],
                        "at": r["occurred_at"].isoformat(), "answers": a}
            return list(await asyncio.gather(*(one(r) for r in rows))), tokens

    preds, tokens = asyncio.run(go())
    config = {"model": model, "n": len(preds), "common": COMMON, "reviewer": REVIEWER,
              "submitter": SUBMITTER, "input_tokens": tokens,
              "est_cost_usd": round(tokens * 0.24 / 1e6, 4), "note": note}
    return record_run(tag, config, {"n": len(preds)}, preds,
                      f"n={len(preds)} · ${config['est_cost_usd']}", exp=EXP, started=started)


LABELS = Path("data/comments/labels.jsonl")


def run_full(repo: str = "Bioconductor/Contributions", concurrency: int = 16,
             model: str = "clef", note: str = "") -> Path:
    """Label every human comment in `repo`, appending to data/comments/labels.jsonl as
    answers arrive. Resumable: comments already labelled with the current question set
    are skipped. Records config + counts as a run under experiments/comments/."""
    qhash = hashlib.sha256(json.dumps([COMMON, REVIEWER, SUBMITTER], sort_keys=True)
                           .encode()).hexdigest()[:12]
    started = datetime.now(timezone.utc)
    LABELS.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if LABELS.exists():
        for line in LABELS.read_text().splitlines():
            d = json.loads(line)
            if d.get("qhash") == qhash and "answers" in d:
                done.add(d["comment_id"])
    rows = [r for r in load(repo) if r["comment_id"] not in done]
    stats = {"todo": len(rows), "ok": 0, "error": 0, "tokens": 0}

    async def go():
        sem, lock = asyncio.Semaphore(concurrency), asyncio.Lock()
        async with clef.client() as c:
            with LABELS.open("a") as f:
                async def one(r):
                    rec = {"comment_id": r["comment_id"], "repo": repo,
                           "issue": r["issue_number"], "role": r["role"], "who": r["who"],
                           "at": r["occurred_at"].isoformat(), "qhash": qhash, "model": model}
                    try:
                        async with sem:
                            a, usage = await clef.decide(c, state(r), questions_for(r["role"]),
                                                         model)
                        rec["answers"] = a
                        stats["ok"] += 1
                        stats["tokens"] += usage.get("input_tokens", 0)
                    except Exception as e:  # keep going; errored rows are retried on resume
                        rec["error"] = repr(e)[:300]
                        stats["error"] += 1
                    async with lock:
                        f.write(json.dumps(rec) + "\n")
                        f.flush()
                await asyncio.gather(*(one(r) for r in rows))

    asyncio.run(go())
    config = {"kind": "full", "repo": repo, "model": model, "qhash": qhash,
              "common": COMMON, "reviewer": REVIEWER, "submitter": SUBMITTER,
              "labels_path": str(LABELS), **stats,
              "est_cost_usd": round(stats["tokens"] * 0.24 / 1e6, 2), "note": note}
    return record_run(f"full-{repo.split('/')[1]}", config, stats, [],
                      f"{repo} todo={stats['todo']} ok={stats['ok']} error={stats['error']} "
                      f"${config['est_cost_usd']} qhash={qhash}", exp=EXP, started=started)


def review_sheet(run_dir: Path, rows: list[dict], out: Path) -> Path:
    """Human-checkable sheet: each comment's text next to Clef's answers."""
    by_id = {r["comment_id"]: r for r in rows}
    lines = []
    for p in (json.loads(x) for x in (run_dir / "predictions.jsonl").read_text().splitlines()):
        r = by_id[p["comment_id"]]
        lines += [f"## #{p['issue']} c{p['comment_id']} · {p['who']} ({p['role']})", "",
                  "> " + (r["body"] or "")[:900].replace("\n", "\n> "), ""]
        for q, a in p["answers"].items():
            if isinstance(a, float):
                v = f"{a:.2f}" + ("  ◀" if a >= 0.5 else "")
            elif "choice" in a:
                v = f"{a['choice']} ({max(a['probabilities'].values()):.2f})"
            else:
                v = f"{a['score']:.2f}"
            lines.append(f"- {q}: {v}")
        lines.append("")
    out.write_text("\n".join(lines))
    return out
