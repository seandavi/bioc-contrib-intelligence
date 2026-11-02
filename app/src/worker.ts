import { Hono } from "hono";
import { deleteCookie, getCookie, setCookie } from "hono/cookie";
import { allowed, canSeeIssue, type Data, resolveUser, scope, seal, unseal, type User } from "./auth";

type Env = {
  ASSETS: Fetcher;
  DATA: R2Bucket;
  REPO: string;
  DEADLINE: string;
  DEADLINE_LABEL: string;
  GITHUB_CLIENT_ID: string;
  GITHUB_CLIENT_SECRET: string;
  SESSION_SECRET: string;
  DEV_LOGIN?: string; // local `wrangler dev` only (.dev.vars); ignored over https
  DEV_ADMIN?: string;
  DEV_TOKEN?: string;
};
type Ctx = { Bindings: Env; Variables: { user: User } };

const app = new Hono<Ctx>();
const COOKIE = "session";
// Dev sign-in bypass only over plain http (local `wrangler dev`); deployed Workers are https-only.
const local = (url: string) => new URL(url).protocol === "http:";
const cache = () => (caches as unknown as { default: Cache }).default;

async function snapshot(env: Env, key: string) {
  const obj = await env.DATA.get(`snapshot/${key}`);
  return obj ? obj.text() : null;
}
const loadData = async (env: Env) => JSON.parse((await snapshot(env, "data.json")) ?? "null") as Data;

// ── Sign-in (GitHub OAuth) ────────────────────────────────────────────────────
app.get("/auth/login", (c) => {
  const state = crypto.randomUUID();
  setCookie(c, "oauth_state", state, { httpOnly: true, secure: true, sameSite: "Lax", path: "/", maxAge: 600 });
  const u = new URL("https://github.com/login/oauth/authorize");
  u.searchParams.set("client_id", c.env.GITHUB_CLIENT_ID);
  u.searchParams.set("redirect_uri", new URL("/auth/callback", c.req.url).toString());
  u.searchParams.set("state", state);
  // ponytail: no scope while v1 is read-only; writes (#8) add public_repo.
  return c.redirect(u.toString());
});

app.get("/auth/callback", async (c) => {
  const { code, state } = c.req.query();
  if (!code || !state || state !== getCookie(c, "oauth_state")) return c.text("Sign-in failed: bad state", 400);
  deleteCookie(c, "oauth_state", { path: "/" });
  const r = await fetch("https://github.com/login/oauth/access_token", {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({ client_id: c.env.GITHUB_CLIENT_ID, client_secret: c.env.GITHUB_CLIENT_SECRET, code }),
  });
  const { access_token } = (await r.json()) as { access_token?: string };
  const user = access_token && (await resolveUser(access_token, c.env.REPO));
  if (!user) return c.text("Sign-in failed: GitHub didn't return a user", 502);
  setCookie(c, COOKIE, await seal(user, c.env.SESSION_SECRET),
    { httpOnly: true, secure: true, sameSite: "Lax", path: "/", maxAge: 7 * 86400 });
  return c.redirect("/");
});

app.post("/auth/logout", (c) => {
  deleteCookie(c, COOKIE, { path: "/" });
  return c.json({ ok: true });
});

// ── Who is calling: session cookie, or a GitHub token as Bearer (API/MCP) ────
async function bearerUser(token: string, env: Env): Promise<User | null> {
  // Cache the GitHub lookups per token for 10 min, keyed by the token's hash.
  const h = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(token))),
    (b) => b.toString(16).padStart(2, "0")).join("");
  const k = new Request(`https://bioc-reviews.cache/auth/${h}`);
  const hit = await cache().match(k);
  if (hit) return { ...((await hit.json()) as Omit<User, "token">), token };
  const u = await resolveUser(token, env.REPO);
  if (u) {
    const { token: _, ...rest } = u;
    await cache().put(k, new Response(JSON.stringify(rest), { headers: { "Cache-Control": "max-age=600" } }));
  }
  return u;
}

app.use("/api/*", async (c, next) => {
  const env = c.env;
  let user: User | null = null;
  const auth = c.req.header("Authorization");
  if (auth?.startsWith("Bearer ")) user = await bearerUser(auth.slice(7), env);
  else if (env.DEV_LOGIN && local(c.req.url))
    user = { login: env.DEV_LOGIN, token: env.DEV_TOKEN ?? "", admin: env.DEV_ADMIN === "1", exp: Infinity };
  else {
    const s = getCookie(c, COOKIE);
    user = s ? await unseal(s, env.SESSION_SECRET) : null;
  }
  if (!user) return c.json({ error: "sign_in_required" }, 401);
  c.set("user", user);
  await next();
});

// ── Read API (the UI uses these; #9 documents them for other callers) ────────
app.get("/api/me", async (c) => {
  const u = c.get("user");
  const data = await loadData(c.env);
  return c.json({
    login: u.login, admin: u.admin, allowed: !!data && allowed(data, u), repo: c.env.REPO,
    deadline: c.env.DEADLINE, deadline_label: c.env.DEADLINE_LABEL,
  });
});

app.get("/api/data", async (c) => {
  const u = c.get("user");
  const data = await loadData(c.env);
  if (!data) return c.json({ error: "no_data" }, 503);
  if (!allowed(data, u)) return c.json({ error: "no_access" }, 403);
  return c.json(scope(data, u));
});

app.get("/api/issues/:n{[0-9]+}", async (c) => {
  const u = c.get("user");
  const n = Number(c.req.param("n"));
  const data = await loadData(c.env);
  if (!data) return c.json({ error: "no_data" }, 503);
  if (!canSeeIssue(data, u, n)) return c.json({ error: "no_access" }, 403);
  const thread = await snapshot(c.env, `i/${n}.json`);
  if (!thread) return c.json({ error: "not_found" }, 404);
  return c.json({ thread: JSON.parse(thread), review: await snapshot(c.env, `i/${n}.review.md`) });
});

app.all("/api/*", (c) => c.json({ error: "not_found" }, 404));

export default app;
