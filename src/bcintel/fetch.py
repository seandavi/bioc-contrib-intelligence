"""Backfill Bioconductor submission-tracker data to JSONL (the source of truth).

Legacy tracker (Bioconductor/Contributions, ~4300 issues) + the new one
(Bioconductor/BiocContributions). Resumable: re-run to continue/refresh.

We fetch the per-issue TIMELINE, not the repo-wide comments/events streams,
because those are hard-capped by GitHub at 30k items (page 300 -> HTTP 422) and
the legacy repo has more than that. The timeline gives comments AND
label/assign/close/cross-reference events in one call per issue.

Architecture: async producers fetch issue timelines concurrently (bounded by a
semaphore); a SINGLE consumer owns every write to the JSONL file. One writer
means append boundaries can't interleave — the corruption mode a multi-process
`>>` backfill hits. tenacity handles transient network errors and rate limits.

Auth: GITHUB_TOKEN / GH_TOKEN env, falling back to `gh auth token`.
"""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

API = "https://api.github.com"
REPOS = ["Bioconductor/Contributions", "Bioconductor/BiocContributions"]
CONCURRENCY = 10


def token() -> str:
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not tok:
        try:
            tok = subprocess.run(
                ["gh", "auth", "token"], capture_output=True, text=True
            ).stdout.strip()
        except FileNotFoundError:
            tok = ""
    if not tok:
        raise SystemExit("No GitHub token: set GITHUB_TOKEN or run `gh auth login`.")
    return tok


def done_issues(timeline_path: Path) -> dict[int, str]:
    """Issue number -> the issue `updated_at` its stored timeline was fetched at.

    Rows written before `_fetched_at` existed map to "" so they count as stale.
    Tolerates partial/corrupt trailing lines.
    """
    done: dict[int, str] = {}
    if timeline_path.exists():
        for line in timeline_path.read_text().splitlines():
            try:
                row = json.loads(line)
                n = row["_issue"]
            except (json.JSONDecodeError, KeyError):
                continue
            done[n] = max(done.get(n, ""), row.get("_fetched_at", ""))
    return done


def since_cursor(issues_path: Path) -> str | None:
    """`since=` cursor for an incremental issues poll: the newest stored
    `updated_at` minus a small overlap (re-seeing a few issues is harmless).
    None -> no file yet, do a full listing."""
    newest = ""
    if issues_path.exists():
        for line in issues_path.read_text().splitlines():
            try:
                newest = max(newest, json.loads(line)["updated_at"])
            except (json.JSONDecodeError, KeyError):
                pass
    if not newest:
        return None
    t = datetime.fromisoformat(newest.replace("Z", "+00:00")) - timedelta(minutes=5)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def next_link(link_header: str) -> str | None:
    """Extract the rel="next" URL from a GitHub Link header, if present."""
    for part in link_header.split(","):
        if 'rel="next"' in part:
            return part[part.index("<") + 1 : part.index(">")]
    return None


def _rate_limited(r: httpx.Response) -> bool:
    return r.status_code in (403, 429) and (
        r.headers.get("x-ratelimit-remaining") == "0"
        or "retry-after" in r.headers
        or "secondary rate limit" in r.text.lower()
    )


def _retry_after(r: httpx.Response) -> float:
    if (ra := r.headers.get("retry-after")) and ra.isdigit():
        return float(ra)
    if reset := r.headers.get("x-ratelimit-reset"):
        return max(1.0, float(reset) - time.time())
    return 60.0


@retry(
    retry=retry_if_exception_type(httpx.TransportError),
    wait=wait_exponential(max=30),
    stop=stop_after_attempt(5),
    reraise=True,
)
async def _get(client: httpx.AsyncClient, url: str, params: dict | None) -> httpx.Response:
    while True:
        r = await client.get(url, params=params)
        if _rate_limited(r):
            await asyncio.sleep(_retry_after(r))
            continue
        r.raise_for_status()
        return r


async def _paginate(client: httpx.AsyncClient, url: str, params: dict) -> list[dict]:
    items: list[dict] = []
    while url:
        r = await _get(client, url, params)
        items.extend(r.json())
        url = next_link(r.headers.get("link", ""))
        params = None  # the next-link URL already carries the query
    return items


async def _fetch_issues(client: httpx.AsyncClient, repo: str, since: str | None) -> list[dict]:
    params = {"state": "all", "per_page": 100} | ({"since": since} if since else {})
    items = await _paginate(client, f"{API}/repos/{repo}/issues", params)
    return [i for i in items if "pull_request" not in i]  # drop PRs


async def _produce(client, repo, num, fetched_at, queue, sem):
    async with sem:
        items = await _paginate(
            client, f"{API}/repos/{repo}/issues/{num}/timeline", {"per_page": 100}
        )
    for it in items:
        await queue.put({**it, "_repo": repo, "_issue": num, "_fetched_at": fetched_at})


async def _writer(queue: asyncio.Queue, path: Path) -> None:
    """The sole writer. Drains the queue until it receives the None sentinel."""
    with path.open("a") as f:
        while (it := await queue.get()) is not None:
            f.write(json.dumps(it) + "\n")


async def _run(repos: list[str], data_dir: Path, limit: int | None, concurrency: int) -> None:
    headers = {
        "Authorization": f"Bearer {token()}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        for repo in repos:
            slug = repo.split("/")[-1].lower()
            d = data_dir / slug
            d.mkdir(parents=True, exist_ok=True)
            print(f"== {repo} ==")

            # Append-only: the issues view keeps the newest row per issue.
            ip = d / "issues.jsonl"
            since = since_cursor(ip)
            issues = await _fetch_issues(client, repo, since)
            with ip.open("a") as f:
                f.write("".join(json.dumps({**i, "_repo": repo}) + "\n" for i in issues))
            print(f"  issues: {len(issues)} updated since {since or 'the beginning'}")

            tl = d / "timeline.jsonl"
            done = done_issues(tl)
            # Refetch any issue updated since its timeline was stored. The whole
            # timeline is re-appended; db views dedupe by id.
            # ponytail: file grows per refetch; compact if it ever gets big.
            todo = [(i["number"], i["updated_at"]) for i in issues
                    if done.get(i["number"], "") < i["updated_at"]]
            if limit is not None:
                todo = todo[:limit]

            queue: asyncio.Queue = asyncio.Queue(maxsize=2000)
            writer = asyncio.create_task(_writer(queue, tl))
            sem = asyncio.Semaphore(concurrency)
            await asyncio.gather(*(_produce(client, repo, n, u, queue, sem) for n, u in todo))
            await queue.put(None)  # sentinel: tells the writer to stop
            await writer
            print(f"  timeline: +{len(todo)} issues")
    print("done.")


def fetch(
    repos: list[str], data_dir: Path, limit: int | None = None, concurrency: int = CONCURRENCY
) -> None:
    """Sync entry point; runs the async producer/consumer backfill."""
    asyncio.run(_run(repos, data_dir, limit, concurrency))
