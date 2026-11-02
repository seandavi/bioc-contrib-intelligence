import { expect, test } from "bun:test";
import { atRisk, band, families, type QueueRow } from "./lib";

test("wait bands", () => {
  expect([0, 14, 15, 28, 29, 60, 61].map(band)).toEqual(
    ["fresh", "fresh", "due", "due", "stale", "stale", "stalled"]);
});

test("check families take the worst status; missing families show none", () => {
  const f = families([
    { platform: "linux-release-x86_64", r_version: "", status: "OK", url: "" },
    { platform: "linux-release-arm64", r_version: "", status: "ERROR", url: "" },
    { platform: "bioc-checks", r_version: "", status: "NOTE", url: "" },
  ]);
  expect(Object.fromEntries(f.map((x) => [x.abbr, x.status]))).toEqual(
    { src: "none", bioc: "NOTE", lin: "ERROR", mac: "none", win: "none", wasm: "none" });
});

test("at risk: reviewer's move, silent or > 14 d, deadline < 30 d", () => {
  const now = Date.parse("2026-11-02T00:00:00Z");
  const row = (o: Partial<QueueRow>) => ({ reviewer_turn: true, reviewer_last: null,
    waiting_since: "2026-10-30T00:00:00Z", ...o }) as QueueRow;
  expect(atRisk(row({}), "2026-11-18", now)).toBe(true); // never commented
  expect(atRisk(row({ reviewer_last: "2026-10-29T00:00:00Z" }), "2026-11-18", now)).toBe(false); // 3 d wait
  expect(atRisk(row({ reviewer_turn: false }), "2026-11-18", now)).toBe(false);
  expect(atRisk(row({}), "2027-01-18", now)).toBe(false); // deadline far
  expect(atRisk(row({}), "2026-10-01", now)).toBe(false); // deadline passed
});
