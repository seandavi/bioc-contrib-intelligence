import { expect, test } from "bun:test";
import { addSpend, turnCost, weekSpend } from "./spend";

test("turnCost prices uncached input, cache reads and output per model", () => {
  const u = { inputTokens: 1_000_000, outputTokens: 100_000, inputTokenDetails: { cacheReadTokens: 800_000 } };
  // Opus: 200k × $5 + 800k × $0.20 + 100k × $20 = 1 + 0.16 + 2
  expect(turnCost("claude-opus-5-5", u)).toBeCloseTo(3.16);
  expect(turnCost("claude-sonnet-5-5", u)).toBeCloseTo(1.58);
  expect(turnCost("unknown", u)).toBeCloseTo(3.16);
  expect(turnCost("claude-opus-5-5", {})).toBe(0);
});

test("weekSpend sums a rolling 7 days per login", async () => {
  const m = new Map<string, string>();
  const b = {
    get: async (k: string) => (m.has(k) ? { json: async () => JSON.parse(m.get(k)!) } : null),
    put: async (k: string, v: string) => { m.set(k, v); },
  } as never;
  const now = Date.parse("2026-11-24T12:00:00Z"), day = 864e5;
  await addSpend(b, "Rev", 10, now);
  await addSpend(b, "rev", 5, now);           // same day, login case-insensitive
  await addSpend(b, "rev", 7, now - 6 * day); // oldest day still in the window
  await addSpend(b, "rev", 100, now - 7 * day); // aged out
  await addSpend(b, "other", 50, now);
  expect(await weekSpend(b, "rev", now)).toBe(22);
});
