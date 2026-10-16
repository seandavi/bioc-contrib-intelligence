import json

from bcintel import db


def _write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))


def test_views_derive_issues_comments_events(tmp_path):
    repo = "Bioconductor/Contributions"
    _write(tmp_path / "contributions" / "issues.jsonl", [
        {"_repo": repo, "number": 1, "title": "pkgA", "state": "closed",
         "state_reason": "completed", "user": {"login": "alice"},
         "created_at": "2024-01-01T00:00:00Z", "updated_at": "2024-02-01T00:00:00Z",
         "closed_at": "2024-02-01T00:00:00Z",
         "labels": [{"name": "3a. accepted"}], "assignees": [{"login": "lshep"}],
         "comments": 2, "body": "- Repository: https://github.com/alice/pkgA"},
    ])
    _write(tmp_path / "contributions" / "timeline.jsonl", [
        {"_repo": repo, "_issue": 1, "id": 100, "event": "commented",
         "user": {"login": "bioc-issue-bot"}, "author_association": "MEMBER",
         "created_at": "2024-01-02T00:00:00Z", "updated_at": "2024-01-02T00:00:00Z",
         "body": "The DESCRIPTION file..."},
        {"_repo": repo, "_issue": 1, "id": 101, "event": "labeled",
         "actor": {"login": "lshep"}, "label": {"name": "3a. accepted"},
         "created_at": "2024-01-20T00:00:00Z"},
        {"_repo": repo, "_issue": 1, "id": 102, "event": "assigned",
         "actor": {"login": "lshep"}, "assignee": {"login": "reviewer1"},
         "created_at": "2024-01-21T00:00:00Z"},
        {"_repo": repo, "_issue": 1, "id": 103, "event": "commented",
         "user": {"login": "bioc-issue-bot"}, "author_association": "MEMBER",
         "created_at": "2024-01-10T00:00:00Z", "updated_at": "2024-01-10T00:00:00Z",
         "body": 'build results were: "OK". [1]\n'
                 "[1]: http://bioconductor.org/spb_reports/pkgA_buildreport_20240110.html"},
        {"_repo": repo, "_issue": 1, "id": 104, "event": "commented",
         "user": {"login": "alice"}, "author_association": "NONE",
         "created_at": "2024-01-11T00:00:00Z", "updated_at": "2024-01-11T00:00:00Z",
         "body": "AdditionalPackage: https://github.com/alice/pkgB"},
    ])

    con = db.connect(str(tmp_path))
    assert con.sql("SELECT count(*) FROM issues").fetchone()[0] == 1
    assert con.sql("SELECT labels[1] FROM issues").fetchone()[0] == "3a. accepted"

    # comments = 'commented' timeline events, with bot detection
    author, is_bot = con.sql("SELECT author, is_bot FROM comments WHERE id=100").fetchone()
    assert author == "bioc-issue-bot" and is_bot is True

    # events include the label event with actor coalesced from .actor
    ev = con.sql("SELECT event, actor, label FROM events WHERE event='labeled'").fetchone()
    assert ev == ("labeled", "lshep", "3a. accepted")

    # assigned event carries the reviewer
    assignee = con.sql("SELECT assignee FROM events WHERE event='assigned'").fetchone()[0]
    assert assignee == "reviewer1"

    # label_transitions: single label event -> from_label NULL, to_label set
    tr = con.sql("SELECT from_label, to_label FROM label_transitions").fetchone()
    assert tr == (None, "3a. accepted")


def test_derived_views(tmp_path):
    repo = "Bioconductor/Contributions"
    _write(tmp_path / "contributions" / "issues.jsonl", [
        {"_repo": repo, "number": 1, "title": "(inactive) pkgA", "state": "closed",
         "state_reason": "completed", "user": {"login": "alice"},
         "created_at": "2024-01-01T00:00:00Z",
         "updated_at": "2024-02-01T00:00:00Z", "closed_at": "2024-02-01T00:00:00Z",
         "labels": [{"name": "3a. accepted"}], "assignees": [],
         "comments": 2, "body": "- Repository: https://github.com/alice/pkgA.git"},
    ])
    _write(tmp_path / "contributions" / "timeline.jsonl", [
        {"_repo": repo, "_issue": 1, "id": 1, "event": "commented",
         "user": {"login": "bioc-issue-bot"}, "author_association": "MEMBER",
         "created_at": "2024-01-05T00:00:00Z", "updated_at": "2024-01-05T00:00:00Z",
         "body": 'the build results were: "skipped, ERROR". [1]\n'
                 "[1]: http://bioconductor.org/spb_reports/pkgA_buildreport_20240105.html"},
        {"_repo": repo, "_issue": 1, "id": 2, "event": "commented",
         "user": {"login": "alice"}, "author_association": "NONE",
         "created_at": "2024-01-06T00:00:00Z", "updated_at": "2024-01-06T00:00:00Z",
         "body": "AdditionalPackage: https://github.com/alice/pkgB"},
        # label/assign events so the `events` view's columns are inferable
        {"_repo": repo, "_issue": 1, "id": 3, "event": "labeled",
         "actor": {"login": "lshep"}, "label": {"name": "3a. accepted"},
         "created_at": "2024-01-07T00:00:00Z"},
        {"_repo": repo, "_issue": 1, "id": 4, "event": "assigned",
         "actor": {"login": "lshep"}, "assignee": {"login": "rev1"},
         "created_at": "2024-01-08T00:00:00Z"},
    ])
    con = db.connect(str(tmp_path))

    # packages: name from the repo URL (.git stripped, prefix stripped), outcome from label
    name, outcome = con.sql("SELECT package_name, outcome FROM packages").fetchone()
    assert name == "pkgA" and outcome == "accepted"

    # builds: cross-platform state string + report URL
    state, url = con.sql("SELECT state, report_url FROM builds").fetchone()
    assert state == "skipped, ERROR"
    assert url.endswith("pkgA_buildreport_20240105.html")

    # additional_packages: the 1-issue -> N-package bundling
    extra = con.sql("SELECT source_url FROM additional_packages").fetchone()[0]
    assert extra == "https://github.com/alice/pkgB"


def test_reviewer_queue_ball_in_court(tmp_path):
    repo = "Bioconductor/BiocContributions"
    def issue(n):
        return {"_repo": repo, "number": n, "title": f"pkg{n}", "state": "open",
                "state_reason": None, "closed_at": None, "user": {"login": "sub"},
                "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-03-01T00:00:00Z",
                "labels": [{"name": "review in progress"}, {"name": "Build OK"}],
                "assignees": [{"login": "rev"}], "comments": 0, "body": ""}

    def ev(n, i, who, t, **kw):
        return {"_repo": repo, "_issue": n, "id": i, "created_at": t, "updated_at": t,
                "author_association": "NONE", **kw,
                "user": {"login": who}, "actor": {"login": who}}

    def say(n, i, who, t, body="x"):
        return ev(n, i, who, t, event="commented", body=body)

    def assign(n, i, t):
        return ev(n, i, "lshep", t, event="assigned", assignee={"login": "rev"},
                  label={"name": "review in progress"})

    _write(tmp_path / "bioccontributions" / "issues.jsonl", [issue(1), issue(2), issue(3)])
    _write(tmp_path / "bioccontributions" / "timeline.jsonl", [
        # 1: reviewer commented, then submitter pushed -> reviewer's move since push
        assign(1, 10, "2026-01-02T00:00:00Z"),
        say(1, 11, "rev", "2026-01-05T00:00:00Z"),
        say(1, 12, "github-actions[bot]", "2026-01-09T00:00:00Z",
            "✅ New build detected for pkg1, version 0.99.2."),
        # 2: submitter pinged, reviewer replied after -> submitter's move
        assign(2, 20, "2026-01-02T00:00:00Z"),
        say(2, 21, "sub", "2026-01-04T00:00:00Z"),
        say(2, 22, "rev", "2026-01-06T00:00:00Z"),
        # 3: reviewer never commented; submitter pings -> reviewer's move since assignment
        assign(3, 30, "2026-01-03T00:00:00Z"),
        say(3, 31, "sub", "2026-01-10T00:00:00Z", "any news?"),
    ])
    rows = {r[0]: r[1:] for r in db.connect(str(tmp_path)).sql(
        "SELECT issue_number, reviewer_turn, waiting_since::VARCHAR, pushes_since, "
        "comments_since FROM reviewer_queue ORDER BY 1").fetchall()}
    assert rows[1] == (True, "2026-01-09 00:00:00", 1, 0)
    assert rows[2] == (False, "2026-01-06 00:00:00", 0, 0)
    assert rows[3] == (True, "2026-01-03 00:00:00", 0, 1)
