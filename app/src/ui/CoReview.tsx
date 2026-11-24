// Co-review sidebar (#32): chat with the agent on top, the shared draft below.
// The agent edits the draft directly (edit_draft / write_draft run here, on the
// reviewer's current text); every agent edit is undoable and shown as a diff.
import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport, lastAssistantMessageIsCompleteWithToolCalls, type UIMessage } from "ai";
import { useEffect, useMemo, useRef, useState } from "react";
import { applyEdits, type Edit, lineDiff } from "./draft";
import type { Me } from "./lib";
import { Md } from "./parts";

type Skill = { id: string; label: string; description: string; when?: string; time?: string; model?: string };
type Meta = { turn?: string; model?: string; ms?: number; usage?: { inputTokens?: number; outputTokens?: number;
  inputTokenDetails?: { cacheReadTokens?: number } } };
type Msg = UIMessage<Meta>;
type Change = { before: string; after: string };

export const AI_FOOTER = (login: string) =>
  `\n\n---\n_Drafted with AI assistance in Bioconductor Reviews and edited by @${login}._`;
export const draftKey = (login: string, n: number) => `cr:draft:${login}:${n}`;
const chatKey = (login: string, n: number) => `cr:chat:${login}:${n}`;

export const track = (type: string, data: Record<string, unknown> = {}) =>
  fetch("/api/events", { method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type, ...data }) }).catch(() => {});

const load = <T,>(k: string, d: T): T => { try { return JSON.parse(localStorage.getItem(k) ?? "") as T; } catch { return d; } };
const save = (k: string, v: unknown) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* quota: keep going */ } };
// Saved chats drop tool outputs (logs, file contents): they're large and re-fetchable.
const slim = (ms: Msg[]) => ms.slice(-40).map((m) => ({ ...m, parts: m.parts.map((p) =>
  p.type.startsWith("tool-") && "output" in p && typeof p.output === "string" && p.output.length > 500
    ? { ...p, output: p.output.slice(0, 500) + " …(trimmed)" } : p) })) as Msg[];

export function CoReview({ n, me, close }: { n: number; me: Me; close: () => void }) {
  const [skills, setSkills] = useState<{ skills: Skill[]; models: string[] } | null>(null);
  const [skill, setSkill] = useState("");
  const [model, setModel] = useState(() => localStorage.getItem("cr:model") ?? "");
  const [draft, setDraftState] = useState(() => load(draftKey(me.login, n), ""));
  const [, bump] = useState(0);
  const [changes, setChanges] = useState<Record<string, Change>>({});
  const [shown, setShown] = useState<string | null>(null); // toolCallId whose diff is open
  const [view, setView] = useState<"edit" | "preview" | "split" | "changes">("edit");
  const [notice, setNotice] = useState<string | null>(null);
  const [status, setStatus] = useState(""); // screen-reader announcements
  const [input, setInput] = useState("");
  const [copied, setCopied] = useState(false);
  const draftRef = useRef(draft);
  const hist = useRef<{ past: string[]; future: string[]; lastAgent: string | null }>({ past: [], future: [], lastAgent: null });
  const editor = useRef<HTMLTextAreaElement>(null);
  const opts = useRef({ skill, model });
  opts.current = { skill, model };

  const setDraft = (t: string) => { draftRef.current = t; setDraftState(t); save(draftKey(me.login, n), t); };
  // Agent edits are checkpoints: undo goes back to the text before the edit.
  const agentEdit = (next: string, kind: string, count: number, callId: string) => {
    const before = draftRef.current;
    hist.current = { past: [...hist.current.past.slice(-49), before], future: [], lastAgent: next };
    setDraft(next);
    bump((x) => x + 1);
    setChanges((c) => ({ ...c, [callId]: { before, after: next } }));
    setStatus(`Draft updated by the co-reviewer: ${count} change${count === 1 ? "" : "s"}.`);
    // Don't pull the editor away from someone typing; otherwise show what changed.
    if (document.activeElement === editor.current) setNotice("The co-reviewer updated the draft.");
    else if (!before.trim()) setView("preview");
    else { setShown(callId); setView("changes"); }
    track("draft_edit", { issue: n, kind, count, chars: next.length - before.length });
  };

  useEffect(() => {
    fetch("/api/skills").then((r) => (r.ok ? (r.json() as Promise<{ skills: Skill[]; models: string[] }>) : null))
      .then(setSkills).catch(() => setSkills(null));
  }, []);

  const transport = useMemo(() => new DefaultChatTransport<Msg>({
    api: `/api/issues/${n}/chat`,
    body: () => ({ draft: draftRef.current, skill: opts.current.skill || undefined, model: opts.current.model || undefined }),
  }), [n]);

  const chat = useChat<Msg>({
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
        else { agentEdit(r.text, "edit", input.edits!.length, toolCall.toolCallId); output = `Applied ${input.edits!.length} edit(s).`; }
      } else if (toolCall.toolName === "write_draft") {
        agentEdit(input.text ?? "", "write", 1, toolCall.toolCallId);
        output = "Draft replaced.";
      } else return;
      chat.addToolOutput({ tool: toolCall.toolName as never, toolCallId: toolCall.toolCallId, output: output as never });
    },
    onFinish: () => setStatus("The co-reviewer finished replying."),
  });
  const { messages, sendMessage, status: chatStatus, stop, error, setMessages, regenerate } = chat;

  useEffect(() => { if (chatStatus === "ready") save(chatKey(me.login, n), slim(messages)); }, [messages, chatStatus, me.login, n]);

  const busy = chatStatus === "submitted" || chatStatus === "streaming";
  useEffect(() => { if (busy) setStatus("The co-reviewer is replying…"); }, [busy]);
  const send = (text: string) => { if (text.trim() && !busy) { sendMessage({ text }); setInput(""); } };
  const runSkill = (s: Skill) => { opts.current.skill = s.id; setSkill(s.id); track("skill_start", { issue: n, skill: s.id }); send(`Run the ${s.label} skill.`); };

  const undo = () => {
    const h = hist.current;
    if (!h.past.length) return;
    const cur = draftRef.current;
    if (h.lastAgent !== null && cur !== h.lastAgent &&
      !confirm("You've edited the draft since the co-reviewer's change. Undo anyway? Your later typing goes too (Redo brings it back)."))
      return;
    const prev = h.past[h.past.length - 1];
    hist.current = { past: h.past.slice(0, -1), future: [...h.future, cur], lastAgent: null };
    setDraft(prev); bump((x) => x + 1);
    if (view === "changes") setView("edit");
    setNotice(null);
    track("draft_undo", { issue: n });
  };
  const redo = () => {
    const h = hist.current;
    if (!h.future.length) return;
    const next = h.future[h.future.length - 1];
    hist.current = { past: [...h.past, draftRef.current], future: h.future.slice(0, -1), lastAgent: next };
    setDraft(next); bump((x) => x + 1);
  };
  const showChanges = (id: string) => { if (changes[id]) { setShown(id); setView("changes"); setNotice(null); } };

  // Follow the conversation only if the reader is already at the bottom.
  const log = useRef<HTMLDivElement>(null);
  const atBottom = useRef(true);
  useEffect(() => { if (atBottom.current && log.current) log.current.scrollTop = log.current.scrollHeight; }, [messages]);

  const full = draft + AI_FOOTER(me.login);
  const cur = shown ? changes[shown] : undefined;
  const active = skills?.skills.find((s) => s.id === skill);
  const copy = () => navigator.clipboard.writeText(full).then(() => {
    setCopied(true); track("copy", { issue: n, chars: full.length }); setTimeout(() => setCopied(false), 2000);
  });

  return (
    <aside className="cr card" aria-label="Co-review">
      <div className="sr-only" aria-live="polite">{status}</div>
      <div className="head">
        <h2>Co-review · #{n}</h2>
        <div className="checks">
          <select aria-label="Model" value={model} onChange={(e) => { setModel(e.target.value); localStorage.setItem("cr:model", e.target.value); }}>
            <option value="">Model: auto</option>
            {skills?.models.map((m) => <option key={m} value={m}>{m}</option>)}
          </select>
          <button className="btn" type="button" title="Clear the conversation (keeps the draft)" disabled={busy}
            onClick={() => { setMessages([]); setSkill(""); localStorage.removeItem(chatKey(me.login, n)); }}>New chat</button>
          <button className="btn" type="button" onClick={close} aria-label="Close co-review">✕</button>
        </div>
      </div>

      <div className="cr-skills" role="group" aria-label="Skills">
        {skills === null && <span className="note">Skills unavailable.</span>}
        {skills?.skills.map((s) => (
          <span key={s.id} className="tipwrap">
            <button type="button" className={`chipbtn${skill === s.id ? " on" : ""}`} aria-describedby={`tip-${s.id}`}
              aria-pressed={skill === s.id} disabled={busy} onClick={() => runSkill(s)}>{s.label}</button>
            <span role="tooltip" id={`tip-${s.id}`} className="tip"><SkillTip s={s} /></span>
          </span>
        ))}
        {active && <span className="note">{active.label} mode: your messages use this skill ·{" "}
          <button type="button" className="linkbtn small" onClick={() => setSkill("")}>turn off</button></span>}
      </div>

      <div className="cr-chat" role="log" aria-label="Conversation" ref={log}
        onScroll={(e) => { const el = e.currentTarget; atBottom.current = el.scrollHeight - el.scrollTop - el.clientHeight < 40; }}>
        {!messages.length && (
          <div className="cr-empty">
            <p className="note">Ask about this submission: the thread, the current checks and logs, or the package source at the
              built commit. The co-reviewer can edit the draft below; you decide what gets posted.</p>
            <ul className="cr-cards">
              {skills?.skills.map((s) => (
                <li key={s.id}><button type="button" disabled={busy} onClick={() => runSkill(s)}><b>{s.label}</b><span>{s.description}</span>
                  {s.when && <span><i>Use when:</i> {s.when}</span>}</button></li>
              ))}
            </ul>
          </div>
        )}
        {messages.map((m) => <Message key={m.id} m={m} n={n} admin={me.admin} changes={changes} showChanges={showChanges} />)}
        {chatStatus === "submitted" && <p className="note">Thinking…</p>}
        {error && <div className="banner err small">The co-reviewer hit an error: {friendly(error.message)}{" "}
          <button type="button" className="linkbtn small" onClick={() => regenerate()}>Retry</button></div>}
      </div>

      <form className="cr-input" onSubmit={(e) => { e.preventDefault(); send(input); }}>
        <textarea aria-label="Message the co-reviewer" placeholder="Ask, or tell it what to change in the draft…" value={input}
          onChange={(e) => setInput(e.target.value)} rows={2}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); send(input); } }} />
        {busy ? <button className="btn" type="button" onClick={stop}>Stop</button>
          : <button className="btn primary" type="submit" disabled={!input.trim()}>Send</button>}
      </form>

      <div className="cr-draft">
        <div className="cr-tabs">
          <b>Draft</b>
          {(["edit", "preview", "split"] as const).map((v) => (
            <button key={v} type="button" className={`tab${view === v ? " on" : ""}`} aria-pressed={view === v}
              onClick={() => setView(v)}>{v[0].toUpperCase() + v.slice(1)}</button>
          ))}
          {cur && <button type="button" className={`tab${view === "changes" ? " on" : ""}`} aria-pressed={view === "changes"}
            onClick={() => setView("changes")}>Changes</button>}
          <span className="sp" />
          <button type="button" className="tab" disabled={!hist.current.past.length} onClick={undo} title="Undo the co-reviewer's last edit">Undo</button>
          <button type="button" className="tab" disabled={!hist.current.future.length} onClick={redo}>Redo</button>
          <a className="tab" href={`#/preview/${n}`} target="_blank" rel="noreferrer" title="Open a live preview in a new tab">Pop out ↗</a>
          <button className="btn primary" type="button" disabled={!draft.trim()} onClick={copy}>{copied ? "Copied" : "Copy markdown"}</button>
        </div>
        {notice && (
          <div className="cr-notice" role="status">{notice}{" "}
            <button type="button" className="linkbtn small" onClick={() => { const ids = Object.keys(changes); showChanges(ids[ids.length - 1]); }}>View changes</button>{" · "}
            <button type="button" className="linkbtn small" onClick={undo}>Undo</button>{" · "}
            <button type="button" className="linkbtn small" onClick={() => setNotice(null)}>Dismiss</button>
          </div>
        )}
        <div className={`cr-pane cr-${view === "changes" && !cur ? "edit" : view}`}>
          {(view === "edit" || view === "split" || (view === "changes" && !cur)) && (
            <textarea ref={editor} className="editor" aria-label="Draft comment (markdown)" value={draft}
              placeholder="Your next comment on the issue. Type here, or ask the co-reviewer to draft it."
              onChange={(e) => { setDraft(e.target.value); if (hist.current.future.length) { hist.current.future = []; bump((x) => x + 1); } }} />
          )}
          {(view === "preview" || view === "split") && <div className="cr-preview"><Md text={full} /></div>}
          {view === "changes" && cur && <Changes {...cur} />}
        </div>
        <p className="note">
          Saved in this browser only ·{" "}
          <button type="button" className="linkbtn small" disabled={!draft} onClick={() => {
            if (confirm("Clear the draft? (Undo can bring it back.)")) {
              hist.current = { past: [...hist.current.past, draftRef.current], future: [], lastAgent: null }; setDraft("");
            } }}>Clear draft</button>
          {" "}· Every post ends with a fixed line: <i>Drafted with AI assistance in Bioconductor Reviews and edited by @{me.login}.</i>
        </p>
      </div>
    </aside>
  );
}

function SkillTip({ s }: { s: Skill }) {
  return (
    <>
      <b>{s.label}</b> — {s.description}
      {s.when && <><br /><i>Use when:</i> {s.when}</>}
      {(s.time || s.model) && <><br /><span className="muted">{[s.time && `Takes ${s.time}`, s.model].filter(Boolean).join(" · ")}</span></>}
    </>
  );
}

const friendly = (m: string) =>
  /weekly_cap/.test(m) ? (m.match(/"message":"([^"]+)"/)?.[1] ?? "you've used this week's co-review budget.")
    : /rate_limited|Too many/.test(m) ? "too many requests; wait a minute and retry."
    : /loop_limit/.test(m) ? "it took too many automatic steps for one message."
      : /sign_in|401/.test(m) ? "your session expired; reload the page to sign in again." : m.slice(0, 300);

function Changes({ before, after }: Change) {
  const d = lineDiff(before, after);
  const first = useRef<HTMLDivElement>(null);
  useEffect(() => { first.current?.scrollIntoView({ block: "nearest" }); }, [before, after]);
  let marked = false;
  return (
    <pre className="cr-diff" aria-label="Changes from the co-reviewer's edit">
      {d.map((l, i) => {
        const isFirst = l.op !== " " && !marked && (marked = true);
        return <div key={i} ref={isFirst ? first : undefined} className={l.op === "+" ? "add" : l.op === "-" ? "del" : ""}>{l.op} {l.line}</div>;
      })}
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

function Message({ m, n, admin, changes, showChanges }:
  { m: Msg; n: number; admin: boolean; changes: Record<string, Change>; showChanges: (id: string) => void }) {
  const [fb, setFb] = useState<"up" | "down" | "sent" | null>(null);
  const [note, setNote] = useState("");
  if (m.role === "user") {
    const text = m.parts.map((p) => (p.type === "text" ? p.text : "")).join("");
    return <div className="cr-msg user">{text}</div>;
  }
  const meta = m.metadata;
  return (
    <div className="cr-msg agent">
      {m.parts.map((p, i) => {
        if (p.type === "text") return <Md key={i} text={p.text} agent />;
        if (!p.type.startsWith("tool-")) return null;
        const t = p as unknown as { type: string; toolCallId: string; state: string; input?: unknown; output?: unknown; errorText?: string };
        const name = t.type.slice(5);
        const label = (TOOL_LABEL[name] ?? (() => name))(t.input);
        const draftTool = name === "edit_draft" || name === "write_draft";
        const failed = t.state === "output-error" || (typeof t.output === "string" && t.output.startsWith("Error"));
        return (
          <div key={i} className="cr-tool-row">
            <details className={`cr-tool${failed ? " retry" : ""}`}>
              <summary>{draftTool ? "✎" : "↳"} {label}{t.state.startsWith("input") ? " …" : failed ? " · didn’t apply, retried" : ""}</summary>
              <pre>{String(t.errorText ?? (typeof t.output === "string" ? t.output : JSON.stringify(t.output ?? t.input, null, 1))).slice(0, 6000)}</pre>
            </details>
            {draftTool && !failed && changes[t.toolCallId] &&
              <button type="button" className="linkbtn small" onClick={() => showChanges(t.toolCallId)}>view changes</button>}
          </div>
        );
      })}
      {meta?.usage && (
        <div className="cr-meta">
          {admin && <span title={`turn ${meta.turn}`}>{meta.model} · {((meta.usage.inputTokens ?? 0) / 1000).toFixed(1)}k in
            ({((meta.usage.inputTokenDetails?.cacheReadTokens ?? 0) / 1000).toFixed(1)}k cached) · {meta.usage.outputTokens} out · {((meta.ms ?? 0) / 1000).toFixed(1)} s</span>}
          {fb === "sent" ? <span>Thanks for the feedback.</span> : fb === "down" ? (
            <form className="cr-fb" onSubmit={(e) => { e.preventDefault(); track("feedback", { issue: n, turn: meta.turn, value: "down", note }); setFb("sent"); }}>
              <input aria-label="What was wrong? (optional)" placeholder="What was wrong? (optional)" value={note} onChange={(e) => setNote(e.target.value)} />
              <button className="linkbtn small" type="submit">Send</button>
            </form>
          ) : (
            <>
              <button type="button" className="linkbtn" aria-label="Helpful" title="Helpful"
                onClick={() => { setFb("sent"); track("feedback", { issue: n, turn: meta.turn, value: "up" }); }}>👍</button>
              <button type="button" className="linkbtn" aria-label="Not helpful" title="Not helpful" onClick={() => setFb("down")}>👎</button>
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
      <div className="head"><h2>Draft for #{n} · preview</h2>
        <div className="checks"><span className="note">Updates as the draft changes</span>
          <button className="btn" type="button" onClick={() => navigator.clipboard.writeText(text + AI_FOOTER(me.login))}>Copy markdown</button></div></div>
      <div className="body"><Md text={text + AI_FOOTER(me.login)} /></div>
    </section>
  );
}
