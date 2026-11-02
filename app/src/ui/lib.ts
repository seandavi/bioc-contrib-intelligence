// Types for the bcintel snapshot (src/bcintel/dashboard.py) and the rules the
// screens share: wait bands, check chips, deadline risk. Spec §3, design HANDOFF.

export type QueueRow = {
  issue_number: number; title: string; submitter: string; reviewer: string;
  reviewer_turn: boolean; waiting_since: string; assigned_at: string; reviewer_last: string | null;
  comments_since: number; pushes_since: number; build: string[]; stage: string | null;
  stage_since: string | null; last_comment: string | null;
};
export type Unassigned = { issue_number: number; title: string; submitter: string; created_at: string; labels: string[] };
export type Check = { platform: string; r_version: string; status: string; url: string };
export type Build = {
  comment_id: number; posted_at: string; kind: string; version: string; worst: string | null;
  run_url: string | null; staging_url: string | null; runiverse_url: string | null; checks: Check[];
};
export type IssueInfo = {
  package?: string; source_url?: string; latest_build: Build | null;
  versions: Array<{ version: string; posted_at: string; kind: string; worst: string | null }>;
};
export type Data = {
  repo: string; generated_at: string; queue: QueueRow[]; unassigned: Unassigned[];
  issues: Record<string, IssueInfo>;
};
export type Me = { login: string; admin: boolean; allowed: boolean; repo: string; deadline: string; deadline_label: string };
export type Entry = { id: number; created_at: string; kind: string; who: string; is_bot: boolean; body: string | null };

export const DAY = 864e5;
export const days = (t: string | null | undefined, now = Date.now()) =>
  t ? Math.floor((now - new Date(t).getTime()) / DAY) : 0;

export type Band = "fresh" | "due" | "stale" | "stalled";
export const band = (d: number): Band => (d <= 14 ? "fresh" : d <= 28 ? "due" : d <= 60 ? "stale" : "stalled");

// At risk (#12 default): reviewer's move, and either no reviewer comment yet or
// waiting > 14 d, with the release deadline under 30 d away.
export function atRisk(r: QueueRow, deadline: string, now = Date.now()) {
  const left = (new Date(deadline).getTime() - now) / DAY;
  return r.reviewer_turn && left >= 0 && left < 30 && (!r.reviewer_last || days(r.waiting_since, now) > 14);
}

// Platforms vary per run (linux/macos/windows × arm64/x86_64, wasm), so chips group
// them into families and show each family's worst status.
const FAMILIES: Array<[string, RegExp]> = [
  ["src", /^source$/], ["bioc", /^bioc-checks$/], ["lin", /^linux/], ["mac", /^macos/],
  ["win", /^windows/], ["wasm", /^wasm/],
];
const RANK: Record<string, number> = { OK: 0, UNKNOWN: 1, NOTE: 2, WARNING: 3, ERROR: 4, BUILD_FAILED: 5 };
export const worse = (a: string, b: string) => ((RANK[a] ?? 1) >= (RANK[b] ?? 1) ? a : b);

export function families(checks: Check[]) {
  return FAMILIES.map(([abbr, re]) => {
    const cs = checks.filter((c) => re.test(c.platform));
    return { abbr, status: cs.length ? cs.map((c) => c.status).reduce(worse) : "none", checks: cs };
  });
}

export const glyph = (s: string) =>
  ({ OK: "✓", NOTE: "N", WARNING: "W", ERROR: "E", BUILD_FAILED: "E", UNKNOWN: "?", none: "–" })[s] ?? "?";

const fmt = new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", timeZone: "UTC" });
export const short = (t: string | null | undefined) => (t ? fmt.format(new Date(t)) : "—");
export const ago = (t: string, now = Date.now()) => {
  const m = Math.round((now - new Date(t).getTime()) / 6e4);
  return m < 60 ? `${m} min ago` : m < 48 * 60 ? `${Math.round(m / 60)} h ago` : `${Math.round(m / 1440)} d ago`;
};

// One line under the wait chip: why the clock started.
export function explain(r: QueueRow, you: boolean) {
  const who = you ? "you" : r.reviewer;
  if (!r.reviewer_last) return `Assigned ${short(r.assigned_at)}, no comment from ${who} since`;
  if (!r.reviewer_turn) return `${you ? "You" : r.reviewer} commented ${short(r.reviewer_last)}`;
  return r.pushes_since && !r.comments_since
    ? `Submitter pushed ${short(r.waiting_since)}`
    : `Submitter replied ${short(r.waiting_since)}`;
}

export const sinceText = (r: QueueRow) =>
  [r.comments_since && `${r.comments_since} comment${r.comments_since > 1 ? "s" : ""}`,
   r.pushes_since && `${r.pushes_since} push${r.pushes_since > 1 ? "es" : ""}`].filter(Boolean).join(" · ") || "—";

export async function api<T>(path: string): Promise<T> {
  const r = await fetch(path, { credentials: "same-origin" });
  if (!r.ok) throw Object.assign(new Error(((await r.json().catch(() => ({}))) as { error?: string }).error ?? r.statusText),
    { status: r.status });
  return r.json() as Promise<T>;
}
