import { expect, test } from "bun:test";
import { allowed, canSeeIssue, type Data, scope, seal, unseal, type User } from "./auth";

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
