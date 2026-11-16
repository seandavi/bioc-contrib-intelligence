import { type Context, Hono } from "hono";
import { deleteCookie, getCookie, setCookie } from "hono/cookie";
import { type AgentEnv, chat, MODELS } from "./agent";
import { allowed, canSeeIssue, type Data, exchange, fresh, resolveUser, scope, seal, unseal, type User,
  withTokens } from "./auth";
import { autoSteps, cleanEvent, parseChat } from "./guards";
import { SKILLS } from "./skills";
import { summary } from "./summary";
import { rollup, type Turn, type UiEvent } from "./usage";

type Env = AgentEnv & {
  CHAT_LIMIT?: RateLimit;
  ASSETS: Fetcher;
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
  // GitHub App: permissions come from the app's settings (Issues r/w, Metadata r), not scopes.
  return c.redirect(u.toString());
});

app.get("/auth/callback", async (c) => {
  const { code, state } = c.req.query();
  if (!code || !state || state !== getCookie(c, "oauth_state")) return c.text("Sign-in failed: bad state", 400);
  deleteCookie(c, "oauth_state", { path: "/" });
  const t = await exchange({ client_id: c.env.GITHUB_CLIENT_ID, client_secret: c.env.GITHUB_CLIENT_SECRET, code });
  const u = t && (await resolveUser(t.access_token, c.env.REPO));
  const user = u && withTokens(u, t);
  if (!user) return c.text("Sign-in failed: GitHub didn't return a user", 502);
  await setSession(c, user);
  // Who signs in, next to the co-review events (obs/ui); #/usage counts them by login.
  const rec = { event: "ui", type: "sign_in", login: user.login, admin: user.admin, at: new Date().toISOString(), id: crypto.randomUUID() };
  c.executionCtx.waitUntil(c.env.DATA.put(`obs/ui/${rec.at.slice(0, 10)}/${rec.id}.json`, JSON.stringify(rec)));
  return c.redirect("/");
});

async function setSession(c: Context<Ctx>, user: User) {
  setCookie(c, COOKIE, await seal(user, c.env.SESSION_SECRET),
    { httpOnly: true, secure: true, sameSite: "Lax", path: "/", maxAge: 7 * 86400 });
}

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
    const { token: _, refresh: __, ...rest } = u;
    await cache().put(k, new Response(JSON.stringify(rest), { headers: { "Cache-Control": "max-age=600" } }));
  }
  return u;
}

// Public: tracker-wide counts for the landing page. No logins or package names
// (per-reviewer numbers are sensitive, spec §9.3). Registered before the auth middleware.
app.get("/api/public/summary", async (c) => {
  const data = await loadData(c.env);
  if (!data) return c.json({ error: "no_data" }, 503);
  return c.json({ ...summary(data as unknown as Parameters<typeof summary>[0], Date.now()), deadline: c.env.DEADLINE, deadline_label: c.env.DEADLINE_LABEL });
});

app.use("/api/*", async (c, next) => {
  const env = c.env;
  let user: User | null = null;
  const auth = c.req.header("Authorization");
  if (auth?.startsWith("Bearer ")) user = await bearerUser(auth.slice(7), env);
  else if (env.DEV_LOGIN && local(c.req.url))
    user = { login: env.DEV_LOGIN, token: env.DEV_TOKEN ?? "", admin: env.DEV_ADMIN === "1", exp: Infinity };
  else {
    const s = getCookie(c, COOKIE);
    const old = s ? await unseal(s, env.SESSION_SECRET) : null;
    user = old && (await fresh(old, env.GITHUB_CLIENT_ID, env.GITHUB_CLIENT_SECRET));
    if (user && user !== old) await setSession(c, user); // token was renewed
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

// ── Co-review agent (#39) ─────────────────────────────────────────────────────
app.get("/api/skills", (c) => c.json({
  models: MODELS,
  skills: Object.values(SKILLS).map(({ id, label, description, when, time, model }) => ({ id, label, description, when, time, model })),
}));

app.post("/api/issues/:n{[0-9]+}/chat", async (c) => {
  const u = c.get("user");
  const n = Number(c.req.param("n"));
  const data = await loadData(c.env);
  if (!data) return c.json({ error: "no_data" }, 503);
  if (!canSeeIssue(data, u, n)) return c.json({ error: "no_access" }, 403);
  const raw = await c.req.text();
  if (raw.length > 2e6) return c.json({ error: "too_large" }, 413);
  const body = parseChat(raw);
  if (!body) return c.json({ error: "bad_request" }, 400);
  // Cost guards: per-reviewer rate limit, and a cap on automatic client-tool resubmits per user message.
  if (c.env.CHAT_LIMIT && !(await c.env.CHAT_LIMIT.limit({ key: u.login })).success)
    return c.json({ error: "rate_limited", message: "Too many co-review requests; wait a minute." }, 429);
  if (autoSteps(body.messages) > 12) return c.json({ error: "loop_limit", message: "Stopped: too many automatic steps for one message." }, 429);
  const thread = JSON.parse((await snapshot(c.env, `i/${n}.json`)) ?? "[]");
  return chat(c.env, u, data, n, thread, body, (p) => c.executionCtx.waitUntil(p), c.req.raw.signal);
});

// Product signals from the UI (#38): skill started, draft edit applied/undone, copy, feedback.
app.post("/api/events", async (c) => {
  const u = c.get("user");
  const data = await loadData(c.env);
  if (!data || !allowed(data, u)) return c.json({ error: "no_access" }, 403);
  const raw = await c.req.text();
  const ev = raw.length < 4096 ? cleanEvent(raw) : null;
  if (!ev) return c.json({ error: "bad_event" }, 400);
  const rec = { event: "ui", ...ev, login: u.login, at: new Date().toISOString(), id: crypto.randomUUID() };
  console.log(JSON.stringify(rec));
  c.executionCtx.waitUntil(c.env.DATA.put(`obs/ui/${rec.at.slice(0, 10)}/${rec.id}.json`, JSON.stringify(rec)));
  return c.json({ ok: true });
});

// Admin usage view (#38): last N days of turns + UI events from R2, $ from gateway logs.
app.get("/api/usage", async (c) => {
  if (!c.get("user").admin) return c.json({ error: "admin_only" }, 403);
  const days = Math.min(Number(c.req.query("days") ?? 7) || 7, 31);
  const since = new Date(Date.now() - days * 864e5);
  const read = async <T>(prefix: string) => {
    const keys: string[] = [];
    for (let d = 0; d <= days; d++) {
      const day = new Date(Date.now() - d * 864e5).toISOString().slice(0, 10);
      const l = await c.env.DATA.list({ prefix: `${prefix}/${day}/`, limit: 1000 });
      keys.push(...l.objects.map((o) => o.key));
    }
    // ponytail: one R2 get per event, capped; move to Analytics Engine when volume outgrows it.
    const objs = await Promise.all(keys.slice(0, 600).map((k) => c.env.DATA.get(k).then((o) => o?.json<T>())));
    return { items: objs.filter(Boolean) as T[], truncated: keys.length > 600 };
  };
  const [turns, events, cost] = await Promise.all([read<Turn>("obs/turns"), read<UiEvent>("obs/ui"), gatewayCost(c.env, since)]);
  const t = turns.items;
  return c.json({
    days, turns: t.length, truncated: turns.truncated || events.truncated, cost_complete: cost.complete,
    total_cost: rollup(t, [], cost.map, "model").reduce((s, r) => s + r.cost, 0),
    by_login: rollup(t, events.items, cost.map, "login"),
    by_skill: rollup(t, events.items, cost.map, "skill"),
    by_model: rollup(t, [], cost.map, "model"),
    recent: t.sort((a, b) => b.at.localeCompare(a.at)).slice(0, 50).map((x) => ({
      at: x.at, login: x.login, issue: x.issue, skill: x.skill, model: x.model, steps: x.steps, finish: x.finish,
      ms: x.total_ms, in: x.usage.inputTokens, out: x.usage.outputTokens,
      cost: x.gateway_logs.reduce((a, id) => a + (cost.map.get(id) ?? 0), 0),
      tool_errors: x.tools.filter((y) => !y.ok).length,
    })),
    feedback: events.items.filter((e) => e.type === "feedback").slice(-50),
  });
});

// Gateway log id → USD, paging back to `since` (max 40 pages of 50).
async function gatewayCost(env: Env, since: Date) {
  const map = new Map<string, number>();
  const base = env.AI_GATEWAY_URL.replace("https://gateway.ai.cloudflare.com/v1/", "https://api.cloudflare.com/client/v4/accounts/")
    .replace(/\/([^/]+)$/, "/ai-gateway/gateways/$1/logs");
  for (let page = 1; page <= 40; page++) {
    const r = await fetch(`${base}?per_page=50&page=${page}&order_by=created_at&order_by_direction=desc`,
      { headers: { Authorization: `Bearer ${env.AI_GATEWAY_TOKEN}` } });
    if (!r.ok) return { map, complete: false };
    const logs = ((await r.json()) as { result?: Array<{ id: string; cost?: number; created_at: string }> }).result ?? [];
    for (const l of logs) map.set(l.id, l.cost ?? 0);
    if (logs.length < 50 || new Date(logs[logs.length - 1].created_at) < since) return { map, complete: true };
  }
  return { map, complete: false };
}

app.all("/api/*", (c) => c.json({ error: "not_found" }, 404));

export default app;
