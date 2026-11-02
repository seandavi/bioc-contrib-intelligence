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


RUN = "https://github.com/r-universe/biocstaging/actions/runs/41"


def _report(pkg, version, rows, first=False):
    # Real r-universe bot format (BiocContributions #229, #170).
    head = ("✅ First" if first else "✅ New") + f" build detected for {pkg}, version {version}.\n"
    table = "".join(f"| {p} | {r} | {s} | [run]({RUN}/job/{i}) |\n"
                    for i, (p, r, s) in enumerate(rows))
    return (head + f"⚙️ Detailed run: {RUN}\n"
            f"📦 Bioconductor staging repository: https://github.com/BiocStaging/{pkg}\n"
            f"🌐 R-universe package page: https://biocstaging.r-universe.dev/{pkg}#checktable\n\n"
            f"📊 R-universe check results for `{pkg}`\n\n"
            "| Platform | R | Status | URL |\n|----------|---|--------|------|\n" + table)


def test_new_tracker_build_reports(tmp_path):
    repo = "Bioconductor/BiocContributions"

    def issue(n, state="open", labels=()):
        return {"_repo": repo, "number": n, "title": f"pkg{n}", "state": state,
                "state_reason": None, "closed_at": None, "user": {"login": "sub"},
                "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-03-01T00:00:00Z",
                "labels": [{"name": x} for x in labels], "assignees": [{"login": "rev"}],
                "comments": 0, "body": f"- Repository: https://github.com/sub/pkg{n}"}

    def bot(n, i, t, body):
        return {"_repo": repo, "_issue": n, "id": i, "event": "commented", "created_at": t,
                "updated_at": t, "author_association": "NONE",
                "user": {"login": "github-actions[bot]"}, "body": body}

    _write(tmp_path / "bioccontributions" / "issues.jsonl", [
        issue(1), issue(2, "closed", ["package accepted"]),
        issue(3, "closed", ["package declined"])])
    _write(tmp_path / "bioccontributions" / "timeline.jsonl", [
        {"_repo": repo, "_issue": 1, "id": 9, "event": "assigned",
         "created_at": "2026-01-02T00:00:00Z",
         "actor": {"login": "lshep"}, "assignee": {"login": "rev"}, "label": {"name": "x"},
         "user": {"login": "lshep"}},
        bot(1, 10, "2026-01-03T00:00:00Z", _report("pkg1", "0.99.0", [
            ("source", "4.6.1", "✅ OK"), ("bioc-checks", "4.6.1", "⚠️ WARNING"),
            ("linux-release-x86_64", "4.6.1", "✅ OK")], first=True)),
        bot(1, 11, "2026-01-09T00:00:00Z", "⚠️ Build detected for pkg1 with invalid version "
            "bump (0.99.0 -> 1.0.0). Only z should increase (x.99.z e.g. x.99.1, x.99.2); "
            "please correct version to see a new build report.\n"),
        bot(1, 12, "2026-01-10T00:00:00Z", _report("pkg1", "0.99.1", [
            ("source", "4.6.1", "✅ OK"), ("bioc-checks", "4.6.1", "ℹ️ NOTE"),
            ("windows-release-x86_64", "4.6.1", "❌ ERROR")])),
        bot(1, 13, "2026-01-11T00:00:00Z", "✅ New build detected for pkg1, version 0.99.2.\n"
            f"⚙️ Detailed run: {RUN}\n\n"
            "❌ Package `pkg1` not available in R-universe (likely build failure)"),
        bot(1, 14, "2026-01-12T00:00:00Z", "✅ New build detected for pkg1, version 0.99.3.\n"
            "🚨 R-universe build failed for `pkg1` (no check results available)\n\n"
            "| Platform | R | Status | URL |\n|----------|---|--------|------|\n"
            f"| ❌ build | — | ❌ BUILD FAILED | [run]({RUN}) |\n"),
    ])
    con = db.connect(str(tmp_path))

    reports = con.sql("SELECT version, kind, worst, run_url, staging_url, runiverse_url "
                      "FROM build_reports ORDER BY posted_at").fetchall()
    assert [r[:3] for r in reports] == [
        ("0.99.0", "first", "WARNING"), ("1.0.0", "invalid_version", None),
        ("0.99.1", "new", "ERROR"), ("0.99.2", "new", "BUILD_FAILED"),
        ("0.99.3", "new", "BUILD_FAILED")]
    assert reports[0][3:] == (RUN, "https://github.com/BiocStaging/pkg1",
                              "https://biocstaging.r-universe.dev/pkg1#checktable")

    checks = con.sql("SELECT platform, r_version, status, url FROM checks "
                     "WHERE version = '0.99.1' ORDER BY platform").fetchall()
    assert checks == [("bioc-checks", "4.6.1", "NOTE", f"{RUN}/job/1"),
                      ("source", "4.6.1", "OK", f"{RUN}/job/0"),
                      ("windows-release-x86_64", "4.6.1", "ERROR", f"{RUN}/job/2")]

    # First build is not a submitter push; the invalid bump and later builds are.
    assert con.sql("SELECT pushes_since FROM reviewer_queue").fetchone()[0] == 4

    outcomes = dict(con.sql("SELECT issue_number, outcome FROM packages").fetchall())
    assert outcomes == {1: "in_progress", 2: "accepted", 3: "declined"}


def test_dashboard_issue_info(tmp_path):
    from bcintel import dashboard
    test_new_tracker_build_reports(tmp_path)  # reuse its fixture data
    info = dashboard._issue_info(db.connect(str(tmp_path)))
    one = info[1]
    assert one["source_url"] == "https://github.com/sub/pkg1"
    assert [v["version"] for v in one["versions"]] == [
        "0.99.0", "1.0.0", "0.99.1", "0.99.2", "0.99.3"]
    assert one["latest_build"]["version"] == "0.99.3"  # the invalid bump isn't a build
    assert 2 not in info  # closed issues are left out


def test_dashboard_live_runiverse(tmp_path):
    from bcintel import dashboard
    test_new_tracker_build_reports(tmp_path)  # issue 1 = pkg1, latest report 0.99.3 (build failed)
    jobs = [{"config": "source", "r": "4.6.1", "check": "OK"},
            {"config": "macos-release-arm64", "r": "4.6.1", "check": "ERROR"},
            {"config": "pending"}]
    live = dashboard._live([{"Package": "PKG1", "Version": "0.99.3",
                             "_commit": {"time": 1789295583}, "_jobs": jobs}])
    one = dashboard._issue_info(db.connect(str(tmp_path)), live)[1]
    assert one["live"]["worst"] == "ERROR"
    assert [j["platform"] for j in one["live"]["jobs"]] == ["source", "macos-release-arm64"]
    assert one["live_differs"] is True  # report says BUILD_FAILED, r-universe says ERROR
    assert dashboard._issue_info(db.connect(str(tmp_path)))[1]["live"] is None  # no snapshot yet
