"""Deep static review of a Bioconductor submission.

Clones the submitted GitHub repo, inspects it statically (read + grep — NO build
tools; build status comes from the SPB report already parsed off the issue), and
asks the LLM for the judgment layer + remediation, following the criteria in
.claude/skills/bioc-package-review.

First review vs re-review is decided by the state store. A re-review is
diff-aware: it feeds the code diff since the last reviewed sha, the prior review,
and the build-status trajectory, and uses a delta-focused comment format.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from . import db, llm
from .bot import CANON as _CANON
from .state import State

MAX_DIFF = 24000
MAX_SOURCE = 60000
REACT_STAGES = ("pre_review", "review")  # where reviewing the source pays off

# ── git ──────────────────────────────────────────────────────────────────────


def _git(args, cwd=None, timeout=240):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                          text=True, timeout=timeout)


def clone_or_update(source_url, dest) -> str | None:
    """Clone/refresh source_url at dest; leave the worktree at the default-branch
    tip and return its sha (full history, so re-review diffs resolve). None on failure."""
    url = (source_url or "").strip()
    if not url.startswith(("http://", "https://", "git@")):
        return None
    if not url.endswith(".git"):
        url += ".git"
    dest = Path(dest)
    try:
        if (dest / ".git").exists():
            _git(["remote", "set-url", "origin", url], cwd=dest)
            if _git(["fetch", "--quiet", "--tags", "origin"], cwd=dest).returncode:
                return None
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if _git(["clone", "--quiet", url, str(dest)]).returncode:
                return None
        head = ""
        for ref in ("origin/HEAD", "origin/main", "origin/master"):
            r = _git(["rev-parse", ref], cwd=dest)
            if r.returncode == 0:
                head = r.stdout.strip()
                break
        if not head:
            return None
        _git(["reset", "--hard", "--quiet", head], cwd=dest)
        return head
    except (subprocess.SubprocessError, OSError):
        return None


def code_diff(pkg, prev, head, budget=MAX_DIFF) -> str | None:
    stat = _git(["diff", "--stat", f"{prev}..{head}"], cwd=pkg)
    if stat.returncode:  # prev not in history (rewritten/force-push)
        return None
    patch = _git(["diff", f"{prev}..{head}", "--",
                  "*.R", "*.Rd", "DESCRIPTION", "NAMESPACE", "*.Rmd", "NEWS*"], cwd=pkg)
    body = (stat.stdout or "") + "\n" + (patch.stdout or "")
    return body[:budget] + "\n...[diff truncated]" if len(body) > budget else body


# ── static inspection ────────────────────────────────────────────────────────


def _read(p):
    try:
        return Path(p).read_text(errors="replace")
    except OSError:
        return ""


def static_checks(pkg) -> list[dict]:
    """Deterministic read/grep checks. Each: {severity, area, msg, fix}."""
    pkg = Path(pkg)
    out: list[dict] = []

    def add(sev, area, msg, fix=None):
        out.append({"severity": sev, "area": area, "msg": msg, "fix": fix})

    desc = _read(pkg / "DESCRIPTION")
    if not desc:
        add("ERROR", "DESCRIPTION", "No DESCRIPTION file found.", None)
    else:
        m = re.search(r"^Version:\s*(.+)$", desc, re.M)
        ver = m.group(1).strip() if m else None
        if ver and not ver.startswith("0.99."):
            add("ERROR", "DESCRIPTION", f"Version is {ver}; a new package must start 0.99.",
                "Set `Version: 0.99.0` in DESCRIPTION.")
        if re.search(r"^Remotes:", desc, re.M):
            add("ERROR", "DESCRIPTION", "`Remotes:` field present.",
                "Remove `Remotes:`; every dependency must be on CRAN or Bioconductor.")
        if not re.search(r"^biocViews:\s*\S", desc, re.M):
            add("ERROR", "DESCRIPTION", "`biocViews:` missing or empty.",
                "Add `biocViews:` with >=2 terms from one biocViews category.")
        if "Authors@R" not in desc:
            add("WARNING", "DESCRIPTION", "No `Authors@R` field.",
                "Use `Authors@R` with exactly one `cre` maintainer and an ORCID.")

    ns = _read(pkg / "NAMESPACE")
    if "exportPattern" in ns:
        add("WARNING", "NAMESPACE", "`exportPattern` in NAMESPACE (exports everything).",
            "Export objects explicitly with `@export` / `export()`.")

    if not (pkg / "vignettes").is_dir():
        add("ERROR", "vignettes", "No `vignettes/` directory.",
            "Add an R Markdown vignette under `vignettes/`.")
    if (pkg / "inst" / "doc").is_dir():
        add("WARNING", "vignettes", "`inst/doc/` present (pre-built vignette output?).",
            "Ship only vignette sources; remove pre-built products.")
    if not any((pkg / x).exists() for x in ("tests", "inst/unitTests")):
        add("NOTE", "tests", "No `tests/` directory found.",
            "Add unit tests (testthat or tinytest).")

    rdir = pkg / "R"
    src = "\n".join(_read(f) for f in rdir.glob("*.R")) if rdir.is_dir() else ""
    for pat, label, fix in (
        (r"\bsapply\s*\(", "sapply()", "Prefer `vapply()` for type-safe returns."),
        (r"\bset\.seed\s*\(", "set.seed() in package code",
         "Move seeding into examples/tests, not exported functions."),
        (r"\bbrowser\s*\(", "browser() left in code", "Remove `browser()` calls."),
        (r"<<-", "<<- superassignment", "Avoid `<<-`; thread state explicitly."),
        (r"(?<![\w.])[TF](?![\w.])", "T/F literal", "Use `TRUE`/`FALSE`, not `T`/`F`."),
    ):
        n = len(re.findall(pat, src))
        if n:
            add("NOTE", "R code", f"{n}x {label}", fix)

    for f in pkg.rglob("*"):
        try:
            if f.is_file() and f.stat().st_size > 5 * 1024 * 1024 and ".git/" not in str(f):
                add("ERROR", "size", f"{f.relative_to(pkg)} is "
                    f"{f.stat().st_size // (1024 * 1024)}MB (>5MB limit).",
                    "Host large data via ExperimentHub/AnnotationHub; keep files <=5MB.")
        except OSError:
            pass
    return out


def propose_patch(pkg_dir) -> tuple[list[str], str | None]:
    """Deterministic, SAFE metadata fixes only. Returns (change list, unified diff).

    Limited to unambiguous DESCRIPTION edits (version -> 0.99.0, strip Remotes) —
    things that can't change code behaviour. Risky code rewrites (sapply->vapply,
    T->TRUE, ...) stay as review suggestions, not auto-patches. Edits the working
    tree to produce the diff, then resets it. Requires pkg_dir to be a git repo.
    """
    pkg = Path(pkg_dir)
    desc = _read(pkg / "DESCRIPTION")
    if not desc:
        return [], None
    new = desc
    changes = []
    m = re.search(r"^(Version:\s*)(.+)$", new, re.M)
    if m and not m.group(2).strip().startswith("0.99."):
        new = new[:m.start()] + m.group(1) + "0.99.0" + new[m.end():]
        changes.append("DESCRIPTION: Version -> 0.99.0")
    if re.search(r"^Remotes:", new, re.M):
        new = re.sub(r"^Remotes:.*(?:\n[ \t].*)*\n?", "", new, flags=re.M)
        changes.append("DESCRIPTION: remove Remotes field (deps must be on CRAN/Bioconductor)")
    if new == desc:
        return [], None
    (pkg / "DESCRIPTION").write_text(new)
    patch = _git(["diff", "--", "DESCRIPTION"], cwd=pkg).stdout
    _git(["checkout", "--", "DESCRIPTION"], cwd=pkg)  # reset the working tree
    return changes, (patch or None)


def pr_markdown(pkg, num, changes, patch) -> str:
    return "\n".join([
        f"# Proposed PR — {pkg} (#{num})",
        "",
        "Safe, mechanical fixes for Bioconductor review items. **Review before "
        "filing** — this is a draft, not submitted.",
        "",
        "## Changes",
        *[f"- {c}" for c in changes],
        "",
        "## Patch",
        "```diff",
        (patch or "").rstrip(),
        "```",
        "",
        "---",
        "_Generated by `bcintel review --patch` (dry-run: not filed). Code-level "
        "fixes are left as suggestions in the review comment._",
    ])


def gather_source(pkg, budget=MAX_SOURCE) -> str:
    pkg = Path(pkg)
    parts = []

    def addfile(rel):
        p = pkg / rel
        if p.is_file():
            parts.append(f"===== {rel} =====\n{_read(p)}")

    addfile("DESCRIPTION")
    addfile("NAMESPACE")
    if (pkg / "R").is_dir():
        for f in sorted((pkg / "R").glob("*.R")):
            parts.append(f"===== R/{f.name} =====\n{_read(f)}")
    if (pkg / "vignettes").is_dir():
        vigs = sorted(list((pkg / "vignettes").glob("*.Rmd"))
                      + list((pkg / "vignettes").glob("*.Rnw")))
        if vigs:
            parts.append(f"===== vignettes/{vigs[0].name} =====\n{_read(vigs[0])}")
    text = "\n\n".join(parts)
    return text[:budget] + "\n...[source truncated]" if len(text) > budget else text


def _findings_md(findings) -> str:
    if not findings:
        return "_No blocking static issues found by inspection._"
    order = {"ERROR": 0, "WARNING": 1, "NOTE": 2}
    rows = sorted(findings, key=lambda f: order.get(f["severity"], 3))
    return "\n".join(f"- **[{f['severity']}]** ({f['area']}) {f['msg']}"
                     + (f" — _{f['fix']}_" if f["fix"] else "") for f in rows)


# ── LLM review ───────────────────────────────────────────────────────────────

_FIRST_SYSTEM = (
    "You are a Bioconductor package reviewer performing a FIRST review of a new "
    "submission, per the Bioconductor contribution guidelines. You are given "
    "authoritative deterministic static findings (do not contradict them), the "
    "package source, and the SPB build status. Write the body of a GitHub review "
    "comment with: a one-line summary; **Blockers**, **Warnings**, and **Notes** "
    "(only if present) where EACH item includes a concrete remediation the "
    "submitter can act on; a **Judgment** section (infrastructure reuse vs "
    "reinventing core classes, redundancy with existing packages, S4/API design, "
    "whether the vignette teaches); and **Questions for the submitter** (2-4). Be "
    "specific, cite files, and be constructive and kind. Do not restate the raw "
    "static list verbatim — synthesize and add remediation."
)
_REREVIEW_SYSTEM = (
    "You are performing a RE-REVIEW of a Bioconductor submission after the "
    "submitter pushed changes. You are given your PREVIOUS review, the code diff "
    "since then, the CURRENT static findings, and the build-status trajectory. "
    "Focus on the DELTA. Write a concise GitHub comment with: **Changes since "
    "last review** (what the diff did); **Resolved** (previously-raised items now "
    "fixed); **Still outstanding** (with remediation); **New concerns** "
    "introduced by the changes (with remediation). Do not repeat unchanged "
    "boilerplate or re-list everything — only what moved."
)


def _llm_section(pkg, source_url, findings, source, *, first, prior_review, diff, build_traj):
    if not llm.available():
        return ("## Judgment & remediation (LLM — not enabled)\n"
                "_Set GEMINI_API_KEY or ANTHROPIC_API_KEY to add judgment and remediation._")
    fparts = [f"[{f['severity']}] ({f['area']}) {f['msg']}" for f in findings]
    ctx = [f"Package source_url: {source_url}",
           "Static findings:\n" + ("\n".join(fparts) or "none"),
           f"SPB build trajectory: {build_traj or 'no report on the issue'}"]
    if first:
        ctx.append("PACKAGE SOURCE:\n" + source)
        system = _FIRST_SYSTEM
    else:
        ctx.append("YOUR PREVIOUS REVIEW:\n" + (prior_review or "(unavailable)"))
        ctx.append("CODE DIFF SINCE LAST REVIEW:\n"
                   + (diff or "(history unavailable — treat as a fresh look)"))
        system = _REREVIEW_SYSTEM
    try:
        body = llm.generate("\n\n".join(ctx), system=system)
    except Exception as e:
        return f"## Judgment & remediation (LLM)\n_LLM call failed: {e}_"
    return body


def build_comment(pkg, issue, source_url, head, findings, source, *, first,
                  prior_sha=None, prior_review=None, diff=None, build_traj=None):
    short = head[:8]
    title = f"# Package review — {pkg}" if first else f"# Package re-review — {pkg}"
    head_line = (f"Reviewed [{source_url}]({source_url}) @ `{short}`."
                 if first else
                 f"Re-reviewed @ `{short}` (previous: `{(prior_sha or '?')[:8]}`).")
    build_line = f"SPB build status: {build_traj[-1][1]}" if build_traj else \
        "SPB build status: no report on the issue yet."
    llm_md = _llm_section(pkg, source_url, findings, source, first=first,
                          prior_review=prior_review, diff=diff, build_traj=build_traj)
    L = [title, "", head_line, build_line, "",
         "## Static findings (by inspection — build/BiocCheck run on the SPB)",
         _findings_md(findings), "", llm_md, "",
         "---",
         "_Generated by `bcintel review` (dry-run: advisory, not posted). "
         "Static findings are mechanical; verify against the SPB report._"]
    return "\n".join(L)


# ── orchestration ────────────────────────────────────────────────────────────


def run(repos, data_dir, out_dir, *, stages=REACT_STAGES, limit=None, force=False,
        patch=False, only_issue=None):
    con = db.connect(str(data_dir))
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    state = State(out / "state.db")
    stage_keys = "', '".join(sorted({s for s in _CANON if _CANON[s] in stages}))
    log = []
    for repo in repos:
        slug = repo.split("/")[-1].lower()
        rows = con.execute(f"""
            WITH cur AS (
              SELECT issue_number, to_label AS label,
                     row_number() OVER (PARTITION BY issue_number ORDER BY changed_at DESC) rn
              FROM label_transitions
              WHERE repo = ? AND to_label IN ('{stage_keys}'))
            SELECT p.issue_number, p.package_name, p.source_url, c.label
            FROM packages p
            JOIN issues i ON i.repo = p.repo AND i.number = p.issue_number
            JOIN cur c ON c.issue_number = p.issue_number AND c.rn = 1
            WHERE p.repo = ? AND i.state = 'open'
            ORDER BY p.issue_number
        """, [repo, repo]).fetchall()
        if only_issue is not None:
            rows = [r for r in rows if r[0] == only_issue]

        traj = {}
        for n, created, st in con.execute(
                "SELECT issue_number, created_at, state FROM builds "
                "WHERE repo=? ORDER BY created_at", [repo]).fetchall():
            traj.setdefault(n, []).append((created, st))

        reviewed = skipped = failed = 0
        for num, pkg, src, label in rows:
            if limit is not None and reviewed >= limit:
                break
            stage = _CANON.get(label, "pre_review")
            if not src:
                failed += 1
                continue
            dest = out / "repos" / slug / f"{num}"
            head = clone_or_update(src, dest)
            if not head:
                print(f"  #{num} {pkg}: clone failed ({src})")
                failed += 1
                continue
            if state.seen(repo, num, head) and not force:
                skipped += 1
                continue
            prior = state.last_review(repo, num)
            first = prior is None
            findings = static_checks(dest)
            source = gather_source(dest) if first else ""
            diff = code_diff(dest, prior[0], head) if prior else None
            comment = build_comment(
                pkg, num, src, head, findings, source, first=first,
                prior_sha=prior[0] if prior else None,
                prior_review=prior[1] if prior else None,
                diff=diff, build_traj=traj.get(num))
            path = out / slug / f"issue-{num}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(comment)
            entry = {"repo": repo, "issue": num, "sha": head, "first": first,
                     "package": pkg, "path": str(path)}
            if patch:
                changes, diff_str = propose_patch(dest)
                if changes:
                    pr_path = out / slug / f"issue-{num}.pr.md"
                    pr_path.write_text(pr_markdown(pkg, num, changes, diff_str))
                    entry["pr_path"] = str(pr_path)
            state.record(repo, num, head, stage=stage, action="review",
                         briefing_path=str(path), review_md=comment)
            log.append(entry)
            reviewed += 1
        print(f"== {repo}: {reviewed} reviewed, {skipped} skipped, {failed} failed")
    (out / "review-log.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in log))
    state.close()
    print(f"reviewed {len(log)} packages; log -> {out / 'review-log.jsonl'}")
