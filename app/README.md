# Bioconductor Reviews (reviewer app)

One Cloudflare Worker: Hono serves `/api`, `/auth` (and later `/mcp`); the React
SPA in `src/ui/` is static assets. Data is the bcintel snapshot that
`scripts/run-cycle.sh` syncs to R2 (`data-bioc-reviews/snapshot/`) every 5 min.
No database. Spec: `../docs/specs/reviewer-app.md`. Design comps (reference
only, not shipped): `design/`.

```bash
bun install
bun test                 # auth + shared-rule tests
bun run check            # tsc
bun run dev              # build UI, wrangler dev (reads the real bucket)
bun run deploy
```

Local dev signs you in from `.dev.vars` (gitignored), over plain http only:

```
DEV_LOGIN=<github login>
DEV_ADMIN=1
SESSION_SECRET=dev-only
```

## Auth

Sign-in is a **GitHub App** (user authorization), not an OAuth app: permissions
are Issues read/write + Metadata read, user tokens expire after 8 h and are
renewed with the refresh token kept in the sealed session cookie. Writes only
work where the app is installed (Bioconductor/BiocContributions); read-only
sign-in works without the installation.

App settings: callbacks `https://reviewer.bioconductor.org/auth/callback` and
`https://bioc-reviews.seandavi.workers.dev/auth/callback` (the redirect uses the host signed in from),
"Expire user authorization tokens" on, webhook off (#11 adds it).

Secrets live in GCP Secret Manager (`cdsci-infra`) and are copied to the Worker:

```bash
bun run secrets   # bioc-reviews-github-client-id / -client-secret / -session-secret
```

Admin = triage permission on the tracker, as GitHub reports it for the user's
token. API callers can send `Authorization: Bearer <GitHub token>` instead of the
session cookie.

## API

| Route | Returns |
|---|---|
| `GET /api/me` | login, admin, allowed, deadline |
| `GET /api/data` | the snapshot, scoped to the caller (non-admins: own assignments) |
| `GET /api/issues/:n` | timeline + AI review body for one issue |
| `POST /api/issues/:n/chat` | co-review agent turn (AI SDK UI message stream); body `{messages, draft, skill?, model?}` |
| `GET /api/skills` | skills and models for the co-review sidebar |
| `POST /api/events` | UI product signals (skill start, draft edit/undo, copy, feedback) |
| `GET /api/usage?days=7` | admins: co-review turns, cost, tokens, latency, feedback |

## Co-review agent (#39)

The Review detail page has a sidebar: chat with an agent on top, the reviewer's
draft comment below. The agent edits the draft directly (exact find/replace,
applied in the browser to the reviewer's current text; every edit is undoable
and shown as a diff). Nothing is posted by the agent.

- **Model access:** Cloudflare AI Gateway `bioc-reviews` (unified billing, no
  provider keys). `AI_GATEWAY_URL` is a var; `AI_GATEWAY_TOKEN` is a secret
  (`cdsci-cloudflare-ai-gateway-token` in Secret Manager). Models: Sonnet 5.5
  default, per-skill override in the skill's front-matter, picker in the UI.
- **What it reads:** the issue thread and queue state (snapshot), the build
  r-universe has now (`RemoteSha`, jobs, BiocCheck counts), the package source at
  that commit (one tarball per commit, unpacked into R2 `src/`), and check logs
  (GitHub Actions job logs trimmed to findings, cached in R2 `logs/`). Code is
  cited with permalinks to the submitter's repo at the built commit.
- **Skills:** `skills/*.md`, front-matter `label`, `description`, optional `model`.
  Add one by adding the file and listing it in `src/skills.ts`.
- **Observability:** Workers Logs + traces on; one `agent_turn` JSON event per turn
  (tokens, cache, steps, per-tool timing, gateway log ids) and `ui` events, both
  also written to R2 `obs/`. Gateway logs carry `cf-aig-metadata` {login, issue,
  skill, turn}. `#/usage` (admins) joins them with gateway cost.
- **Prompt injection:** thread, logs and code are submitter-controlled. The agent
  has no GitHub write tool and its only side effect is the draft the reviewer sees.

Local dev needs `AI_GATEWAY_TOKEN` and `DEV_TOKEN` (a GitHub token for logs) in
`.dev.vars`.
