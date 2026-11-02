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

GitHub OAuth app, callback `https://<host>/auth/callback`. Secrets:
`wrangler secret put GITHUB_CLIENT_ID | GITHUB_CLIENT_SECRET | SESSION_SECRET`.
Admin = triage permission on the tracker, as GitHub reports it for the user's
token. API callers can send `Authorization: Bearer <GitHub token>` instead of the
session cookie.

## API

| Route | Returns |
|---|---|
| `GET /api/me` | login, admin, allowed, deadline |
| `GET /api/data` | the snapshot, scoped to the caller (non-admins: own assignments) |
| `GET /api/issues/:n` | timeline + AI review body for one issue |
