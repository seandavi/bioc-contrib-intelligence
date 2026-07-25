import json

from bcintel import bot


def _write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))


def test_bot_reacts_to_open_stages_only(tmp_path):
    repo = "Bioconductor/Contributions"
    d = tmp_path / "data"
    _write(d / "contributions" / "issues.jsonl", [
        # open, in pre-review -> should get a briefing
        {"_repo": repo, "number": 1, "title": "pkgOpen", "state": "open",
         "state_reason": None, "user": {"login": "alice"},
         "created_at": "2024-01-01T00:00:00Z", "updated_at": "2024-02-01T00:00:00Z",
         "closed_at": None, "labels": [{"name": "pre-review"}], "assignees": [],
         "comments": 1, "body": "- Repository: https://github.com/alice/pkgOpen"},
        # closed, accepted -> terminal, no briefing
        {"_repo": repo, "number": 2, "title": "pkgDone", "state": "closed",
         "state_reason": "completed", "user": {"login": "bob"},
         "created_at": "2023-01-01T00:00:00Z", "updated_at": "2023-06-01T00:00:00Z",
         "closed_at": "2023-06-01T00:00:00Z", "labels": [{"name": "3a. accepted"}],
         "assignees": [], "comments": 1, "body": "- Repository: https://github.com/bob/pkgDone"},
    ])
    _write(d / "contributions" / "timeline.jsonl", [
        {"_repo": repo, "_issue": 1, "id": 10, "event": "labeled",
         "actor": {"login": "lshep"}, "label": {"name": "pre-review"},
         "created_at": "2024-01-15T00:00:00Z"},
        {"_repo": repo, "_issue": 1, "id": 11, "event": "assigned",
         "actor": {"login": "lshep"}, "assignee": {"login": "rev1"},
         "created_at": "2024-01-16T00:00:00Z"},
        {"_repo": repo, "_issue": 2, "id": 20, "event": "labeled",
         "actor": {"login": "lshep"}, "label": {"name": "3a. accepted"},
         "created_at": "2023-05-01T00:00:00Z"},
        {"_repo": repo, "_issue": 1, "id": 30, "event": "commented",
         "user": {"login": "bioc-issue-bot"}, "author_association": "MEMBER",
         "created_at": "2024-01-10T00:00:00Z", "updated_at": "2024-01-10T00:00:00Z",
         "body": 'the build results were: "OK". [1]\n[1]: http://x/pkgOpen_buildreport_1.html'},
    ])

    out = tmp_path / "out"
    bot.run([repo], d, out)

    assert (out / "contributions" / "issue-1.md").exists()
    assert not (out / "contributions" / "issue-2.md").exists()  # terminal -> skipped

    brief = (out / "contributions" / "issue-1.md").read_text()
    assert "Pre-review briefing" in brief
    assert "Stage:** pre_review" in brief
    assert "OK" in brief  # parsed build state surfaced
    assert "- [ ]" in brief  # deterministic checklist present

    log = [json.loads(x) for x in (out / "run-log.jsonl").read_text().splitlines()]
    assert log == [{"repo": repo, "issue": 1, "stage": "pre_review", "action": "pre-review",
                    "package": "pkgOpen", "path": str(out / "contributions" / "issue-1.md")}]
