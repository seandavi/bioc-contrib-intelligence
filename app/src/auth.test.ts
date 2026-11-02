import { expect, test } from "bun:test";
import { allowed, canSeeIssue, type Data, fresh, scope, seal, unseal, type User } from "./auth";

const u = (login: string, admin = false): User => ({ login, token: "t", admin, exp: Date.now() + 1e6 });

test("sealed session round-trips; tamper, wrong secret and expiry fail", async () => {
  const s = await seal(u("rev"), "secret");
  expect((await unseal(s, "secret"))?.login).toBe("rev");
  expect(await unseal(s, "other")).toBeNull();
  expect(await unseal(s.slice(0, -2) + (s.endsWith("A") ? "BB" : "AA"), "secret")).toBeNull();
  expect(await unseal(await seal({ ...u("rev"), exp: Date.now() - 1 }, "secret"), "secret")).toBeNull();
});

test("non-admins see only their own assignments", () => {
  const data: Data = {
    repo: "r", generated_at: "",
    queue: [{ issue_number: 1, reviewer: "Rev" }, { issue_number: 2, reviewer: "other" }],
    unassigned: [{ issue_number: 3 }],
    issues: { "1": {}, "2": {}, "3": {} },
  };
  const me = u("rev");
  expect(allowed(data, me)).toBe(true);
  expect(allowed(data, u("stranger"))).toBe(false);
  expect(allowed(data, u("stranger", true))).toBe(true);
  const s = scope(data, me);
  expect(s.queue.map((r) => r.issue_number)).toEqual([1]);
  expect(s.unassigned).toEqual([]);
  expect(Object.keys(s.issues)).toEqual(["1"]);
  expect(canSeeIssue(data, me, 2)).toBe(false);
  expect(canSeeIssue(data, u("x", true), 2)).toBe(true);
});

test("fresh: keeps live tokens, signs out expired ones without a refresh token", async () => {
  const live = { ...u("rev"), token_exp: Date.now() + 3600e3 };
  expect(await fresh(live, "id", "s")).toBe(live);
  expect(await fresh({ ...u("rev"), token_exp: Date.now() - 1 }, "id", "s")).toBeNull();
  const bearer = u("rev"); // no token_exp: not a GitHub App session token, nothing to renew
  expect(await fresh(bearer, "id", "s")).toBe(bearer);
});

test("fresh: renews an expiring token with the refresh token", async () => {
  const real = globalThis.fetch;
  let sent: Record<string, string> = {};
  globalThis.fetch = (async (_url: string, init: RequestInit) => {
    sent = JSON.parse(init.body as string);
    return new Response(JSON.stringify({ access_token: "new", expires_in: 28800, refresh_token: "r2" }));
  }) as typeof fetch;
  try {
    const out = await fresh({ ...u("rev"), refresh: "r1", token_exp: Date.now() + 30e3 }, "id", "s");
    expect(sent.grant_type).toBe("refresh_token");
    expect(sent.refresh_token).toBe("r1");
    expect(out?.token).toBe("new");
    expect(out?.refresh).toBe("r2");
    expect(out!.token_exp! > Date.now() + 28000e3).toBe(true);
  } finally {
    globalThis.fetch = real;
  }
});
