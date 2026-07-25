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
