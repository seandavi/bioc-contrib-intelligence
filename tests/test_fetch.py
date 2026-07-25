import asyncio
import json

from bcintel.fetch import _writer, done_issues, next_link


def test_next_link_extracts_rel_next():
    hdr = ('<https://api.github.com/x?page=2>; rel="next", '
           '<https://api.github.com/x?page=5>; rel="last"')
    assert next_link(hdr) == "https://api.github.com/x?page=2"
    assert next_link('<https://api.github.com/x?page=5>; rel="last"') is None
    assert next_link("") is None


def test_done_issues_skips_corrupt_lines(tmp_path):
    p = tmp_path / "timeline.jsonl"
    p.write_text(
        json.dumps({"_issue": 1, "event": "commented"}) + "\n"
        + json.dumps({"_issue": 2, "event": "labeled"}) + "\n"
        + '{"_issue": 3}{"_issue": 4}\n'   # concatenated garbage -> skipped
        + '{"no_issue_key": true}\n'        # missing _issue -> skipped
        + '{partial'                        # truncated tail -> skipped
    )
    assert done_issues(p) == {1, 2}


def test_writer_is_single_and_line_framed(tmp_path):
    # The sole-writer invariant: records in, one JSON object per line out.
    p = tmp_path / "timeline.jsonl"

    async def drive():
        q: asyncio.Queue = asyncio.Queue()
        w = asyncio.create_task(_writer(q, p))
        for i in range(3):
            await q.put({"_issue": i})
        await q.put(None)
        await w

    asyncio.run(drive())
    lines = p.read_text().splitlines()
    assert [json.loads(x)["_issue"] for x in lines] == [0, 1, 2]
