// Weekly co-review spend cap per reviewer: estimated $ per turn from token usage,
// summed over a rolling 7 days from one small R2 file per (day, login).
// Estimate counts uncached input at the cache-write price: 2–8% above the AI
// Gateway's actual cost on Nov 2026 data, so it errs toward stopping early.

// $/MTok: [cache write (uncached input), cache read, output]. platform.claude.com pricing, Nov 2026.
// ponytail: Haiku at its ≤100k-prompt tier; it's a rounding error next to Opus/Sonnet.
const PRICES: Record<string, [number, number, number]> = {
  "claude-opus-5-5": [5, 0.2, 20],
  "claude-sonnet-5-5": [2.5, 0.1, 10],
  "claude-haiku-5-5": [0.125, 0.01, 0.5],
};

export type Usage = { inputTokens?: number; outputTokens?: number; inputTokenDetails?: { cacheReadTokens?: number } };

export function turnCost(model: string, u: Usage) {
  const [w, r, o] = PRICES[model] ?? PRICES["claude-opus-5-5"]; // unknown model: price as the dearest
  const cached = u.inputTokenDetails?.cacheReadTokens ?? 0;
  return (Math.max(0, (u.inputTokens ?? 0) - cached) * w + cached * r + (u.outputTokens ?? 0) * o) / 1e6;
}

type Bucket = Pick<R2Bucket, "get" | "put">;
const key = (day: string, login: string) => `obs/spend/${day}/${login.toLowerCase()}.json`;
const day = (t: number) => new Date(t).toISOString().slice(0, 10);
const read = async (b: Bucket, k: string) => ((await (await b.get(k))?.json<{ usd: number }>())?.usd ?? 0);

// Today and the 6 days before it.
export async function weekSpend(b: Bucket, login: string, now = Date.now()) {
  const days = Array.from({ length: 7 }, (_, i) => day(now - i * 864e5));
  return (await Promise.all(days.map((d) => read(b, key(d, login))))).reduce((a, x) => a + x, 0);
}

// ponytail: read-modify-write; two turns finishing at the same instant can drop one
// increment. A per-user Durable Object would fix it if that ever matters.
export async function addSpend(b: Bucket, login: string, usd: number, now = Date.now()) {
  if (!(usd > 0)) return;
  const k = key(day(now), login);
  await b.put(k, JSON.stringify({ usd: (await read(b, k)) + usd }));
}
