import { expect, test } from "bun:test";
import { summary } from "./summary";

// Issue 1 has two reviewers sharing one move: counted once.
test("public summary counts issues, without names", () => {
  const now = Date.parse("2026-11-16T00:00:00Z");
  const row = (n: number, reviewer: string, turn: boolean, since: string) => ({
    issue_number: n, reviewer, reviewer_turn: turn, waiting_since: since,
  }) as never;
  const s = summary({
    generated_at: "2026-11-16T00:00:00Z",
    queue: [row(1, "a", true, "2026-10-01T00:00:00Z"), row(1, "B", true, "2026-10-01T00:00:00Z"),
      row(2, "b", false, "2026-11-01T00:00:00Z")],
    unassigned: [{ issue_number: 3 } as never],
  }, now);
  expect(s).toMatchObject({ open: 3, assignments: 3, reviewers: 2, unassigned: 1, reviewer_move: 1, over_28d: 1, median_wait: 46 });
  expect(JSON.stringify(s)).not.toContain('"a"');
});
