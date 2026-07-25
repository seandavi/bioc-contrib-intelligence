"""Advisory bot — dry-run mode.

Reads the fetched corpus and, for each OPEN issue in a state the bot serves,
writes a Markdown briefing to an output directory instead of posting a GitHub
comment. This is the poller's decide+act loop with `act` stubbed to disk, so it
carries zero risk while the review logic matures (see DESIGN.md "Operating the
bots"). The deterministic + precedent facts here are real; the LLM judgment
layer is not yet wired.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from . import db, llm
from .state import State

JUDGMENT_SYSTEM = (
    "You are assisting a Bioconductor package reviewer. Bioconductor expects packages "
    "to reuse core infrastructure classes (SummarizedExperiment, GRanges, Biostrings, "
    "SingleCellExperiment, BiocParallel, BiocFileCache, ExperimentHub/AnnotationHub) "
    "rather than reinvent them, to not duplicate existing packages, and to have clean "
    "S4 API design. You are given a package's DESCRIPTION and metadata but NOT its "
    "source code. Produce a SHORT markdown assessment for the human reviewer with "
    "sections: **Infrastructure reuse** (does the described functionality map onto "
    "existing Bioc classes it should use?), **Possible redundancy** (name existing "
    "Bioconductor/CRAN packages with overlapping functionality, if any), **Questions "
    "for the submitter** (2-3 targeted). Frame everything as items to verify, since "
    "you lack the source. Be concise. Do not restate the deterministic checklist."
)


def _judgment(pkg, src, desc_text):
    prompt = (f"Package: {pkg}\nSource: {src}\n\n"
              f"DESCRIPTION and submission notes:\n{desc_text[:2000]}")
    try:
        body = llm.generate(prompt, system=JUDGMENT_SYSTEM)
    except Exception as e:  # never let one API hiccup abort the run
        return f"## Judgment layer (LLM)\n\n_LLM call failed: {e}_"
    return f"## Judgment layer (Gemini)\n\n{body}"

# Map both label vocabularies (legacy Contributions + new BiocContributions) to
# canonical open stages. Terminal labels (3a/3b/3c, package accepted/declined)
# are deliberately absent -> the bot does not react to closed work.
CANON = {
    "1. awaiting moderation": "moderation",
    "awaiting policy acceptance": "moderation",
    "policies-accepted": "moderation",
    "pre-check passed": "pre_review",
    "precheck-passed": "pre_review",
    "pre-review": "pre_review",
    "assign reviewer": "pre_review",
    "2. review in progress": "review",
    "review in progress": "review",
    "3e. pending pre-review changes": "waiting_submitter",
    "3d. needs interop": "waiting_submitter",
    "inactive review": "waiting_submitter",
}
REACT = {
    "moderation": ("triage", "New submission — moderation triage"),
    "pre_review": ("pre-review", "Pre-review briefing"),
    "review": ("review", "Reviewer briefing"),
    "waiting_submitter": ("nudge", "Waiting on submitter"),
}
BLOCKING = {
    "moderation": "core team",
    "pre_review": "reviewer (assignment / review)",
    "review": "reviewer",
    "waiting_submitter": "submitter",
}
CHECKLIST = [
    "version is 0.99.x for a new package",
    "R CMD check clean on all platforms (see build report)",
    "BiocCheck ERROR / WARNING items cleared",
    ">=80% of exported functions have runnable examples",
    "unit tests present and actually exercise the code",
    "vignette is evaluated and explanatory (not copy-pasted output)",
    "reuses core Bioconductor classes (SummarizedExperiment / GRanges / ...)",
    "not redundant with an existing Bioconductor package",
]


def _dt(s):
    if not s:
        return None
    if isinstance(s, datetime):  # DuckDB may infer the column as TIMESTAMP
        return s if s.tzinfo else s.replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(str(s).replace("Z", "+00:00"))


def _age_days(s):
    d = _dt(s)
    return None if d is None else (datetime.now(timezone.utc) - d).days


def _briefing(repo, num, pkg, src, sub, created, label, stage, changed, action, desc,
              build, addl, hist, judgment=None):
    age = _age_days(created)
    dwell = _age_days(changed) if changed else None
    L = [f"# {desc} — {pkg} (#{num})", "",
         f"- **Repo:** {repo}#{num}",
         f"- **Package:** {pkg}  ·  **Source:** {src or '(none in body)'}",
         f"- **Submitter:** @{sub}",
         f"- **Current label:** {label or '(none yet)'}  ·  **Stage:** {stage}",
         f"- **Blocking:** {BLOCKING[stage]}",
         f"- **Age:** {age}d open" + (f"  ·  {dwell}d in stage" if dwell is not None else ""),
         "", "## Latest build"]
    if build and build[0]:
        L.append(f"`{build[0]}`" + (f" — [report]({build[1]})" if build[1] else ""))
    else:
        L.append("_No parsed SPB build report yet._")
    L.append("")
    if addl:
        L += ["## Bundled packages (`AdditionalPackage`)"] + [f"- {u}" for u in addl] + [""]
    others = [h for h in hist if h[1] != num]
    if others:
        L += ["## Submitter history"]
        L += [f"- {p} (#{n}) — {o}" for p, n, o in sorted(others, key=lambda x: x[1])] + [""]
    if action == "nudge":
        L += ["## Suggested nudge",
              f"Waiting on the submitter for ~{dwell}d in stage. Without a response this "
              "trends toward an inactive close — draft a polite check-in referencing the "
              "outstanding items.", ""]
    else:
        L += ["## Reviewer checklist (deterministic — verify vs SPB / BiocCheck)"]
        L += [f"- [ ] {c}" for c in CHECKLIST] + [""]
        if judgment:
            L += [judgment, ""]
        else:
            L += ["## Judgment layer (LLM — not enabled)",
                  "_Set GEMINI_API_KEY to add infrastructure-reuse, redundancy, and "
                  "API-design assessment._", ""]
    L += ["---", "_Generated by `bcintel bot` (dry-run: advisory only, not posted)._"]
    return "\n".join(L)


def run(repos, data_dir, out_dir, use_llm=True, limit=None, force=False):
    con = db.connect(str(data_dir))
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    state = State(out / "state.db")
    stage_keys = "', '".join(CANON)
    do_llm = use_llm and llm.available()
    log = []
    for repo in repos:
        slug = repo.split("/")[-1].lower()
        issues = con.execute(f"""
            WITH cur AS (
              SELECT issue_number, to_label AS label, changed_at,
                     row_number() OVER (PARTITION BY issue_number ORDER BY changed_at DESC) rn
              FROM label_transitions
              WHERE repo = ? AND to_label IN ('{stage_keys}'))
            SELECT p.issue_number, p.package_name, p.source_url, p.submitter,
                   i.created_at, c.label, c.changed_at, i.updated_at
            FROM packages p
            JOIN issues i ON i.repo = p.repo AND i.number = p.issue_number
            LEFT JOIN cur c ON c.issue_number = p.issue_number AND c.rn = 1
            WHERE p.repo = ? AND i.state = 'open'
            ORDER BY p.issue_number
        """, [repo, repo]).fetchall()

        # latest build sha per issue = this run's idempotency token (see state.py)
        shas = {r[0]: r[1] for r in con.execute("""
            SELECT issue_number, commit_sha FROM (
              SELECT issue_number, commit_sha,
                     row_number() OVER (PARTITION BY issue_number ORDER BY created_at DESC) rn
              FROM commits WHERE repo = ?) WHERE rn = 1
        """, [repo]).fetchall()}

        builds = {r[0]: (r[1], r[2]) for r in con.execute("""
            SELECT issue_number, state, report_url FROM (
              SELECT issue_number, state, report_url,
                     row_number() OVER (PARTITION BY issue_number ORDER BY created_at DESC) rn
              FROM builds WHERE repo = ?) WHERE rn = 1
        """, [repo]).fetchall()}

        addl: dict = {}
        for n, url in con.execute(
                "SELECT issue_number, source_url FROM additional_packages WHERE repo=?",
                [repo]).fetchall():
            addl.setdefault(n, []).append(url)

        hist: dict = {}
        for s, p, n, o in con.execute(
                "SELECT submitter, package_name, issue_number, outcome FROM packages WHERE repo=?",
                [repo]).fetchall():
            hist.setdefault(s, []).append((p, n, o))

        # earliest bot comment per issue = the ack that pastes the DESCRIPTION
        descs = {r[0]: r[1] for r in con.execute("""
            SELECT issue_number, body FROM (
              SELECT issue_number, body,
                     row_number() OVER (PARTITION BY issue_number ORDER BY created_at) rn
              FROM comments WHERE repo = ? AND is_bot) WHERE rn = 1
        """, [repo]).fetchall()}

        wrote = skipped = 0
        # limit caps issues *considered* so a repeat run re-visits (and skips) the same set
        for num, pkg, src, sub, created, label, changed, updated in issues[:limit]:
            token = shas.get(num) or f"updated:{updated}"  # no build yet -> issue mtime
            if not force and state.seen(repo, num, token):
                skipped += 1
                continue
            stage = CANON.get(label, "moderation")  # open but unlabeled -> treat as moderation
            action, desc = REACT[stage]
            judgment = None
            if do_llm and action != "nudge":
                judgment = _judgment(pkg, src, descs.get(num, "") or "")
            md = _briefing(repo, num, pkg, src, sub, created, label, stage, changed,
                           action, desc, builds.get(num), addl.get(num, []), hist.get(sub, []),
                           judgment)
            path = out / slug / f"issue-{num}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(md)
            state.record(repo, num, token, stage=stage, action=action,
                         briefing_path=str(path))
            log.append({"repo": repo, "issue": num, "stage": stage, "action": action,
                        "package": pkg, "path": str(path)})
            wrote += 1
        print(f"== {repo}: {wrote} written, {skipped} skipped -> {out / slug}")
    state.close()
    (out / "run-log.jsonl").write_text("".join(json.dumps(r) + "\n" for r in log))
    print(f"wrote {len(log)} briefings; log -> {out / 'run-log.jsonl'}")
