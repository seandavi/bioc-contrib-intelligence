// Co-review usage (#38): per-turn agent events and UI events (R2 obs/) joined with
// AI Gateway logs (authoritative $ per model call), rolled up for the admin view.

export type Turn = {
  id: string; at: string; login: string; issue: number; skill: string | null; model: string; steps: number;
  finish: string; total_ms: number; first_token_ms: number; gateway_logs: string[];
  usage: { inputTokens?: number; outputTokens?: number; inputTokenDetails?: { cacheReadTokens?: number } };
  tools: Array<{ name: string; ok: boolean; ms: number }>;
};
export type UiEvent = { type: string; login: string; at: string; value?: string; skill?: string };
export type Row = {
  key: string; turns: number; cost: number; in: number; cached: number; out: number; p50_ms: number; p95_ms: number;
  tool_errors: number; up: number; down: number; edits: number; undos: number; copies: number;
};

const pct = (xs: number[], p: number) => {
  if (!xs.length) return 0;
  const s = [...xs].sort((a, b) => a - b);
  return s[Math.min(s.length - 1, Math.floor(p * s.length))];
};

export function rollup(turns: Turn[], events: UiEvent[], cost: Map<string, number>, by: "login" | "skill" | "model"): Row[] {
  const groups = new Map<string, { t: Turn[]; e: UiEvent[] }>();
  const g = (k: string) => groups.get(k) ?? groups.set(k, { t: [], e: [] }).get(k)!;
  for (const t of turns) g(String(t[by] ?? "(chat)")).t.push(t);
  // UI events only carry login (and skill for skill_start); attribute by login, or by skill when grouping by skill.
  for (const e of events) if (by === "login") g(e.login).e.push(e); else if (by === "skill" && e.skill) g(e.skill).e.push(e);
  return [...groups].map(([key, { t, e }]) => ({
    key, turns: t.length,
    cost: t.reduce((s, x) => s + x.gateway_logs.reduce((a, id) => a + (cost.get(id) ?? 0), 0), 0),
    in: t.reduce((s, x) => s + (x.usage.inputTokens ?? 0), 0),
    cached: t.reduce((s, x) => s + (x.usage.inputTokenDetails?.cacheReadTokens ?? 0), 0),
    out: t.reduce((s, x) => s + (x.usage.outputTokens ?? 0), 0),
    p50_ms: pct(t.map((x) => x.total_ms), 0.5), p95_ms: pct(t.map((x) => x.total_ms), 0.95),
    tool_errors: t.reduce((s, x) => s + x.tools.filter((y) => !y.ok).length, 0),
    up: e.filter((x) => x.type === "feedback" && x.value === "up").length,
    down: e.filter((x) => x.type === "feedback" && x.value === "down").length,
    edits: e.filter((x) => x.type === "draft_edit").length,
    undos: e.filter((x) => x.type === "draft_undo").length,
    copies: e.filter((x) => x.type === "copy").length,
  })).sort((a, b) => b.cost - a.cost || b.turns - a.turns);
}
