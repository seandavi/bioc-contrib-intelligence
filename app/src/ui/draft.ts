// The shared draft: the agent's edits are exact, unique find/replace operations on
// the reviewer's current text, applied all-or-nothing so a stale edit never lands
// half-way. lineDiff drives the "Changes" view after an agent edit.

export type Edit = { old_text: string; new_text: string };

export function applyEdits(text: string, edits: Edit[]): { text: string } | { error: string } {
  let out = text;
  for (const [i, e] of edits.entries()) {
    const at = out.indexOf(e.old_text);
    if (at < 0) return { error: `edit ${i + 1}: old_text not found in the current draft (it may have changed); re-read the draft and retry` };
    if (out.indexOf(e.old_text, at + 1) >= 0) return { error: `edit ${i + 1}: old_text occurs more than once; include more surrounding text` };
    out = out.slice(0, at) + e.new_text + out.slice(at + e.old_text.length);
  }
  return { text: out };
}

export type DiffLine = { op: " " | "+" | "-"; line: string };

// LCS line diff; drafts are short (≲ 500 lines), so O(n·m) is fine.
export function lineDiff(a: string, b: string): DiffLine[] {
  const x = a.split("\n"), y = b.split("\n");
  const L = Array.from({ length: x.length + 1 }, () => new Uint16Array(y.length + 1));
  for (let i = x.length - 1; i >= 0; i--)
    for (let j = y.length - 1; j >= 0; j--)
      L[i][j] = x[i] === y[j] ? L[i + 1][j + 1] + 1 : Math.max(L[i + 1][j], L[i][j + 1]);
  const out: DiffLine[] = [];
  let i = 0, j = 0;
  while (i < x.length || j < y.length) {
    if (i < x.length && j < y.length && x[i] === y[j]) { out.push({ op: " ", line: x[i] }); i++; j++; }
    else if (i < x.length && (j >= y.length || L[i + 1][j] >= L[i][j + 1])) out.push({ op: "-", line: x[i++] });
    else out.push({ op: "+", line: y[j++] });
  }
  return out;
}
