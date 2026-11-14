// Input checks for the co-review routes: request shapes, the auto-resubmit loop cap,
// and the whitelist of UI events we store.
import type { UIMessage } from "ai";
import { z } from "zod";
import type { ChatBody } from "./agent";

const Chat = z.object({
  messages: z.array(z.object({ id: z.string(), role: z.enum(["user", "assistant", "system"]), parts: z.array(z.any()) })
    .passthrough()).min(1).max(200),
  draft: z.string().max(200_000).optional(),
  skill: z.string().max(64).optional(),
  model: z.string().max(64).optional(),
});

export function parseChat(raw: string): ChatBody | null {
  try {
    const r = Chat.safeParse(JSON.parse(raw));
    return r.success ? (r.data as unknown as ChatBody) : null;
  } catch { return null; }
}

// Client-tool calls since the last user message: each one triggers an automatic resubmit
// (the SDK keeps appending to the same assistant message), so this bounds the loop.
export function autoSteps(messages: Pick<UIMessage, "role" | "parts">[]) {
  let k = 0;
  for (let i = messages.length - 1; i >= 0 && messages[i].role !== "user"; i--)
    k += messages[i].parts.filter((p) => p.type === "tool-edit_draft" || p.type === "tool-write_draft").length;
  return k;
}

const EVENTS = new Set(["skill_start", "draft_edit", "draft_undo", "copy", "feedback", "co_review_open"]);
const FIELDS = ["type", "issue", "skill", "kind", "count", "chars", "turn", "value", "note"] as const;

export function cleanEvent(raw: string): Record<string, string | number> | null {
  let ev: Record<string, unknown>;
  try { ev = JSON.parse(raw); } catch { return null; }
  if (!ev || typeof ev.type !== "string" || !EVENTS.has(ev.type)) return null;
  const out: Record<string, string | number> = {};
  for (const f of FIELDS) {
    const v = ev[f];
    if (typeof v === "number" && Number.isFinite(v)) out[f] = v;
    else if (typeof v === "string") out[f] = v.slice(0, f === "note" ? 1000 : 80);
  }
  return out;
}
