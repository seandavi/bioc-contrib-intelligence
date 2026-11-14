// Skills: app/skills/<id>.md, front-matter (label, description, model?) + instructions.
// Bundled as text (wrangler `rules`); listed by /api/skills, applied per chat turn.
import checkTriage from "../skills/check-triage.md";
import firstReview from "../skills/first-review.md";
import fitOverlap from "../skills/fit-overlap.md";
import followUp from "../skills/follow-up.md";
import nudge from "../skills/nudge.md";

export type Skill = { id: string; label: string; description: string; model?: string; body: string };

export function parseSkill(id: string, src: string): Skill {
  const m = src.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  const meta = Object.fromEntries((m?.[1] ?? "").split("\n").map((l) => l.split(/:\s*(.*)/s).slice(0, 2).map((s) => s.trim())));
  return { id, label: meta.label ?? id, description: meta.description ?? "", model: meta.model || undefined, body: (m?.[2] ?? src).trim() };
}

// Order = chip order in the UI.
export const SKILLS: Record<string, Skill> = Object.fromEntries(
  ([["follow-up", followUp], ["check-triage", checkTriage], ["first-review", firstReview], ["fit-overlap", fitOverlap],
    ["nudge", nudge]] as const).map(([id, src]) => [id, parseSkill(id, src)]));
