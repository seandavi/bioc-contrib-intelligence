import { expect, test } from "bun:test";
import { rollup, type Turn } from "./usage";

const turn = (login: string, ms: number, logs: string[], ok = true): Turn => ({
  id: login + ms, at: "", login, issue: 1, skill: null, model: "m", steps: 1, finish: "stop", total_ms: ms,
  first_token_ms: 1, gateway_logs: logs, usage: { inputTokens: 10, outputTokens: 2, inputTokenDetails: { cacheReadTokens: 4 } },
  tools: [{ name: "read_file", ok, ms: 1 }],
});

test("rollup joins gateway cost and UI events per reviewer", () => {
  const rows = rollup([turn("a", 100, ["g1", "g2"]), turn("a", 300, ["g3"], false), turn("b", 50, [])],
    [{ type: "feedback", value: "up", login: "a", at: "" }, { type: "copy", login: "b", at: "" }],
    new Map([["g1", 0.01], ["g2", 0.02], ["g3", 0.5]]), "login");
  expect(rows[0]).toMatchObject({ key: "a", turns: 2, in: 20, cached: 8, out: 4, tool_errors: 1, up: 1, p50_ms: 300, p95_ms: 300 });
  expect(rows[0].cost).toBeCloseTo(0.53);
  expect(rows[1]).toMatchObject({ key: "b", turns: 1, cost: 0, copies: 1 });
});
