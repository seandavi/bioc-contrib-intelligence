# Contributing

Thanks for helping. By participating you agree to the
[Code of Conduct](CODE_OF_CONDUCT.md). Contributions are accepted under the
[MIT License](LICENSE).

## Where things are discussed

- Bugs and features: [issues](https://github.com/seandavi/bioc-contrib-intelligence/issues).
  The plan is [#13](https://github.com/seandavi/bioc-contrib-intelligence/issues/13).
- Observations and suggestions about the Bioconductor contributions process
  itself go in [#20](https://github.com/seandavi/bioc-contrib-intelligence/issues/20),
  as factual, non-judgmental notes. Reviewers are volunteers: describe what the
  data shows, not who is behind it. Please don't open issues on Bioconductor
  repositories from here.

## Getting set up

```bash
# pipeline (Python, uv)
uv sync
uv run bcintel fetch --repo Bioconductor/BiocContributions   # needs a GitHub token
uv run ruff check src tests && uv run pytest -q

# app (Cloudflare Worker + React, bun)
cd app && bun install && bun test && bun run check
```

The tests build small synthetic trackers, so they don't need the fetched corpus.
App details, including local sign-in for `wrangler dev`: [`app/README.md`](app/README.md).

## What a good change looks like

- **Small**, and in the place every caller goes through.
- **Tested where the logic is real:** parsers, the whose-move rules, access
  scoping. Use real bot comment text in parser tests.
- **Data-backed.** Claims about the review process (in code comments, docs or
  #20) cite the query or the issue they come from.
- `ponytail:` comments mark a deliberate shortcut and name its limit.

Pull requests run CI (ruff, pytest, bun test, tsc).
