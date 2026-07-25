# bioc-contrib-intelligence

Database + bot toolkit for the Bioconductor package-submission review process.

## Data

Two trackers are ingested (both, because they overlap during a live migration):

| Repo | Role | Size |
|---|---|---|
| `Bioconductor/Contributions` | legacy tracker, historical corpus (2016–2025) | ~4,300 closed issues |
| `Bioconductor/BiocContributions` | new tracker (R-universe / GitHub Actions) | ~113 issues, live |

`fetch.sh` pulls **all** issues (open + closed), plus repo-wide comment and
event streams, to append-only JSONL under `data/<repo>/`. JSONL is the source
of truth; DuckDB reads it directly (no import step).

```bash
./fetch.sh                                   # backfill both repos -> data/*/*.jsonl
duckdb -init views.sql                        # interactive SQL over the JSONL
duckdb -init views.sql -c "SELECT state, count(*) FROM issues GROUP BY 1"
```

Views (`views.sql`): `issues`, `comments`, `events` — projected + deduped over
the raw `*_raw` views. `events` reconstructs the label/assignment/close history
that the plain issues endpoint drops.

Re-run `fetch.sh` to refresh (full refetch; dedup happens in the views). See
`fetch.sh` for the incremental-`since` upgrade path.

## Roadmap

Build order (see `DESIGN.md`): **DB** (this) → deterministic check harness →
retrieval over past reviews → multi-agent review → contribution-manager bot.
Downstream: dashboards, an advisory reviewer bot, a triage/manager bot.
