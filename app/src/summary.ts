import { type Data, days } from "./ui/lib";

// Tracker-wide counts for the public landing page: no logins, no package names.
export function summary(data: Pick<Data, "generated_at" | "queue" | "unassigned" | "trend">, now: number) {
  const q = data.queue;
  // One per issue: co-reviewers share the move.
  const theirMove = [...new Map(q.filter((r) => r.reviewer_turn).map((r) => [r.issue_number, r])).values()].map((r) => days(r.waiting_since, now)).sort((a, b) => a - b);
  const open = new Set([...q.map((r) => r.issue_number), ...data.unassigned.map((u) => u.issue_number)]);
  return {
    generated_at: data.generated_at,
    open: open.size,
    assignments: q.length,
    reviewers: new Set(q.map((r) => r.reviewer.toLowerCase())).size,
    unassigned: data.unassigned.length,
    reviewer_move: theirMove.length,
    over_28d: theirMove.filter((d) => d > 28).length,
    median_wait: theirMove.length ? theirMove[theirMove.length >> 1] : null, // ponytail: upper median
    trend: data.trend ?? [], // weekly tracker-wide counts, no names
  };
}
