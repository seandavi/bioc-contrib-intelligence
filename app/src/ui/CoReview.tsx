// Co-review sidebar (#32): chat with the agent on top, the shared draft below.
// The agent edits the draft directly (edit_draft / write_draft run here, on the
// reviewer's current text); every agent edit is undoable and shown as a diff.
import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport, lastAssistantMessageIsCompleteWithToolCalls, type UIMessage } from "ai";
import { useEffect, useMemo, useRef, useState } from "react";
import { applyEdits, type Edit, lineDiff } from "./draft";
import type { Me } from "./lib";
import { Md } from "./parts";

type Skill = { id: string; label: string; description: string; model?: string };
type Meta = { turn?: string; model?: string; ms?: number; usage?: { inputTokens?: number; outputTokens?: number;
  inputTokenDetails?: { cacheReadTokens?: number } } };
type Msg = UIMessage<Meta>;

export const AI_FOOTER = (login: string) =>
  `\n\n---\n_Drafted with AI assistance in Bioconductor Reviews and edited by @${login}._`;
export const draftKey = (login: string, n: number) => `cr:draft:${login}:${n}`;
const chatKey = (login: string, n: number) => `cr:chat:${login}:${n}`;

export const track = (type: string, data: Record<string, unknown> = {}) =>
  fetch("/api/events", { method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type, ...data }) }).catch(() => {});

const load = <T,>(k: string, d: T): T => { try { return JSON.parse(localStorage.getItem(k) ?? "") as T; } catch { return d; } };

export function CoReview({ n, me, close }: { n: number; me: Me; close: () => void }) {
  const [skills, setSkills] = useState<{ skills: Skill[]; models: string[] }>({ skills: [], models: [] });
  const [skill, setSkill] = useState("");
  const [model, setModel] = useState(() => localStorage.getItem("cr:model") ?? "");
  const [draft, setDraftState] = useState(() => load(draftKey(me.login, n), ""));
  const [hist, setHist] = useState<{ past: string[]; future: string[] }>({ past: [], future: [] });
  const [changes, setChanges] = useState<{ before: string; after: string } | null>(null);
  const [view, setView] = useState<"edit" | "preview" | "split" | "changes">("edit");
  const [input, setInput] = useState("");
  const [copied, setCopied] = useState(false);
  const draftRef = useRef(draft);
  const opts = useRef({ skill, model });
  opts.current = { skill, model };

  const setDraft = (t: string) => { draftRef.current = t; setDraftState(t); localStorage.setItem(draftKey(me.login, n), JSON.stringify(t)); };
  // Agent edits are checkpoints: undo goes back to the text before the edit.
  const agentEdit = (next: string, kind: string, count: number) => {
    const before = draftRef.current;
    setHist((h) => ({ past: [...h.past.slice(-49), before], future: [] }));
    setDraft(next);
    setChanges({ before, after: next });
    setView("changes");
    track("draft_edit", { issue: n, kind, count, chars: next.length - before.length });
  };

  useEffect(() => { fetch("/api/skills").then((r) => r.json() as Promise<{ skills: Skill[]; models: string[] }>).then(setSkills).catch(() => {}); }, []);

  const transport = useMemo(() => new DefaultChatTransport<Msg>({
    api: `/api/issues/${n}/chat`,
    body: () => ({ draft: draftRef.current, skill: opts.current.skill || undefined, model: opts.current.model || undefined }),
  }), [n]);

  const { messages, sendMessage, status, stop, error, setMessages, addToolOutput } = useChat<Msg>({
    id: `${n}`,
    messages: load<Msg[]>(chatKey(me.login, n), []),
    transport,
    sendAutomaticallyWhen: lastAssistantMessageIsCompleteWithToolCalls,
    onToolCall({ toolCall }) {
      if (toolCall.dynamic) return;
      const input = toolCall.input as { edits?: Edit[]; text?: string };
      let output: string;
      if (toolCall.toolName === "edit_draft") {
        const r = applyEdits(draftRef.current, input.edits ?? []);
        if ("error" in r) output = `Error: ${r.error}`;
        else { agentEdit(r.text, "edit", input.edits!.length); output = `Applied ${input.edits!.length} edit(s).`; }
      } else if (toolCall.toolName === "write_draft") {
        agentEdit(input.text ?? "", "write", 1);
        output = "Draft replaced.";
      } else return;
      addToolOutput({ tool: toolCall.toolName as never, toolCallId: toolCall.toolCallId, output: output as never });
    },
  });

  useEffect(() => {
    if (status === "ready") localStorage.setItem(chatKey(me.login, n), JSON.stringify(messages.slice(-60)));
  }, [messages, status, me.login, n]);

  const busy = status === "submitted" || status === "streaming";
  const send = (text: string) => { if (text.trim() && !busy) { sendMessage({ text }); setInput(""); } };
  const runSkill = (s: Skill) => { opts.current.skill = s.id; setSkill(s.id); track("skill_start", { issue: n, skill: s.id }); send(`Run the ${s.label} skill.`); };
  const undo = () => setHist((h) => {
    if (!h.past.length) return h;
    const prev = h.past[h.past.length - 1];
    const cur = draftRef.current;
    setDraft(prev); setChanges(null); track("draft_undo", { issue: n });
    return { past: h.past.slice(0, -1), future: [...h.future, cur] };
  });
  const redo = () => setHist((h) => {
    if (!h.future.length) return h;
    const next = h.future[h.future.length - 1];
    const cur = draftRef.current;
    setDraft(next);
    return { past: [...h.past, cur], future: h.future.slice(0, -1) };
  });

  const bottom = useRef<HTMLDivElement>(null);
  useEffect(() => { bottom.current?.scrollIntoView({ block: "end" }); }, [messages]);
  const full = draft + AI_FOOTER(me.login);

  return (
    <aside className="cr card" aria-label="Co-review">
      <div className="head">
        <h2>Co-review · #{n}</h2>
        <div className="checks">
          <select aria-label="Model" value={model} onChange={(e) => { setModel(e.target.value); localStorage.setItem("cr:model", e.target.value); }}>
            <option value="">Model: auto</option>
            {skills.models.map((m) => <option key={m} value={m}>{m}</option>)}
          </select>
          <button className="btn" type="button" title="Clear the conversation (keeps the draft)" disabled={busy}
            onClick={() => { setMessages([]); setSkill(""); localStorage.removeItem(chatKey(me.login, n)); }}>New chat</button>
          <button className="btn" type="button" onClick={close} aria-label="Close co-review">✕</button>
        </div>
      </div>

      <div className="cr-skills" role="group" aria-label="Skills">
        {skills.skills.map((s) => (
          <button key={s.id} type="button" className={`chipbtn${skill === s.id ? " on" : ""}`} title={s.description}
            disabled={busy} onClick={() => runSkill(s)}>{s.label}</button>
        ))}
        {skill && <button type="button" className="linkbtn small" onClick={() => setSkill("")}>clear skill</button>}
      </div>

      <div className="cr-chat" aria-live="polite">
        {!messages.length && (
          <div className="note cr-empty">
            <p>Ask about this submission: the thread, the current checks and logs, or the package source at the built commit.
              Pick a skill to start a standard review. The agent can edit the draft below; you post it.</p>
          </div>
        )}
        {messages.map((m) => <Message key={m.id} m={m} n={n} showChanges={() => setView("changes")} />)}
        {status === "submitted" && <p className="note">Thinking…</p>}
        {error && <div className="banner err small">{error.message}</div>}
        <div ref={bottom} />
      </div>

      <form className="cr-input" onSubmit={(e) => { e.preventDefault(); send(input); }}>
        <textarea aria-label="Message the co-reviewer" placeholder="Ask, or tell it what to change in the draft…" value={input}
          onChange={(e) => setInput(e.target.value)} rows={2}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(input); } }} />
        {busy ? <button className="btn" type="button" onClick={stop}>Stop</button>
          : <button className="btn primary" type="submit" disabled={!input.trim()}>Send</button>}
      </form>

      <div className="cr-draft">
        <div className="cr-tabs">
          <b>Draft</b>
          {(["edit", "preview", "split"] as const).map((v) => (
            <button key={v} type="button" className={`tab${view === v ? " on" : ""}`} onClick={() => setView(v)}>{v[0].toUpperCase() + v.slice(1)}</button>
          ))}
          {changes && <button type="button" className={`tab${view === "changes" ? " on" : ""}`} onClick={() => setView("changes")}>Changes</button>}
          <span className="sp" />
          <button type="button" className="linkbtn small" disabled={!hist.past.length} onClick={undo} title="Undo the agent's last edit">Undo</button>
          <button type="button" className="linkbtn small" disabled={!hist.future.length} onClick={redo}>Redo</button>
          <a className="small" href={`#/preview/${n}`} target="_blank" rel="noreferrer" title="Open a live preview in a new tab">Pop out ↗</a>
        </div>
        <div className={`cr-pane ${view}`}>
          {(view === "edit" || view === "split") && (
            <textarea className="editor" aria-label="Draft comment (markdown)" value={draft}
              placeholder="Your next comment on the issue. Type here, or ask the co-reviewer to draft it."
              onChange={(e) => { setDraft(e.target.value); setHist((h) => (h.future.length ? { ...h, future: [] } : h)); }} />
          )}
          {(view === "preview" || view === "split") && <div className="cr-preview"><Md text={full} /></div>}
          {view === "changes" && changes && <Changes {...changes} />}
        </div>
        <p className="note">Added to every post · can’t be edited: <i>Drafted with AI assistance in Bioconductor Reviews and edited by @{me.login}.</i></p>
        <div className="cr-actions">
          <button className="btn" type="button" disabled={!draft.trim()}
            onClick={() => navigator.clipboard.writeText(full).then(() => { setCopied(true); track("copy", { issue: n, chars: full.length }); setTimeout(() => setCopied(false), 2000); })}>
            {copied ? "Copied" : "Copy markdown"}</button>
          <button className="btn primary" type="button" disabled title="Posting from the app comes with #8">Post to #{n}…</button>
        </div>
      </div>
    </aside>
  );
}

function Changes({ before, after }: { before: string; after: string }) {
  const d = lineDiff(before, after);
  return (
    <pre className="cr-diff" aria-label="Changes from the agent's last edit">
      {d.map((l, i) => <div key={i} className={l.op === "+" ? "add" : l.op === "-" ? "del" : ""}>{l.op} {l.line}</div>)}
    </pre>
  );
}

const TOOL_LABEL: Record<string, (i: any) => string> = {
  list_files: (i) => `Listed files ${i?.prefix || "/"}`,
  read_file: (i) => `Read ${i?.path ?? ""}${i?.from > 1 || i?.to ? ` L${i.from ?? 1}–${i.to ?? ""}` : ""}`,
  search_code: (i) => `Searched /${i?.pattern ?? ""}/${i?.prefix ? ` in ${i.prefix}` : ""}`,
  get_check_log: (i) => `Read ${i?.platform ?? ""} check log`,
  edit_draft: (i) => `Edited the draft (${i?.edits?.length ?? 0} change${i?.edits?.length === 1 ? "" : "s"})`,
  write_draft: () => "Wrote the draft",
};

function Message({ m, n, showChanges }: { m: Msg; n: number; showChanges: () => void }) {
  const [fb, setFb] = useState<string | null>(null);
  if (m.role === "user") {
    const text = m.parts.map((p) => (p.type === "text" ? p.text : "")).join("");
    return <div className="cr-msg user">{text}</div>;
  }
  const meta = m.metadata;
  return (
    <div className="cr-msg agent">
      {m.parts.map((p, i) => {
        if (p.type === "text") return <Md key={i} text={p.text} />;
        if (!p.type.startsWith("tool-")) return null;
        const t = p as unknown as { type: string; state: string; input?: unknown; output?: unknown; errorText?: string };
        const name = t.type.slice(5);
        const label = (TOOL_LABEL[name] ?? (() => name))(t.input);
        const draftTool = name === "edit_draft" || name === "write_draft";
        const failed = t.state === "output-error" || (typeof t.output === "string" && t.output.startsWith("Error"));
        return (
          <details key={i} className={`cr-tool${failed ? " err" : ""}`}>
            <summary>{draftTool ? "✎" : "↳"} {label}{t.state.startsWith("input") ? " …" : failed ? " · failed" : ""}
              {draftTool && !failed && t.state === "output-available" &&
                <>{" · "}<button type="button" className="linkbtn small" onClick={(e) => { e.preventDefault(); showChanges(); }}>view changes</button></>}</summary>
            <pre>{String(t.errorText ?? (typeof t.output === "string" ? t.output : JSON.stringify(t.output ?? t.input, null, 1))).slice(0, 6000)}</pre>
          </details>
        );
      })}
      {meta?.usage && (
        <div className="cr-meta">
          <span title={`turn ${meta.turn}`}>{meta.model} · {((meta.usage.inputTokens ?? 0) / 1000).toFixed(1)}k in
            ({((meta.usage.inputTokenDetails?.cacheReadTokens ?? 0) / 1000).toFixed(1)}k cached) · {meta.usage.outputTokens} out · {((meta.ms ?? 0) / 1000).toFixed(1)} s</span>
          {fb ? <span>thanks</span> : (
            <>
              <button type="button" className="linkbtn" aria-label="Helpful" onClick={() => { setFb("up"); track("feedback", { issue: n, turn: meta.turn, value: "up" }); }}>👍</button>
              <button type="button" className="linkbtn" aria-label="Not helpful" onClick={() => {
                const note = prompt("What was wrong? (optional)") ?? "";
                setFb("down"); track("feedback", { issue: n, turn: meta.turn, value: "down", note });
              }}>👎</button>
            </>
          )}
        </div>
      )}
    </div>
  );
}

// Pop-out preview (#/preview/<n>): the draft rendered as it will be posted; follows edits live.
export function Preview({ n, me }: { n: number; me: Me }) {
  const [text, setText] = useState(() => load(draftKey(me.login, n), ""));
  useEffect(() => {
    const f = (e: StorageEvent) => { if (e.key === draftKey(me.login, n)) setText(load(draftKey(me.login, n), "")); };
    addEventListener("storage", f);
    return () => removeEventListener("storage", f);
  }, [me.login, n]);
  return (
    <section className="card" style={{ maxWidth: 900, margin: "0 auto" }}>
      <div className="head"><h2>Draft for #{n} · preview</h2><span className="note">Updates as the draft changes</span></div>
      <div className="body"><Md text={text + AI_FOOTER(me.login)} /></div>
    </section>
  );
}
