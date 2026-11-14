// Co-review usage (#38), admins: cost, tokens, latency and feedback per reviewer, skill and model.
import { useEffect, useState } from "react";
import { api, short } from "./lib";

type Row = { key: string; turns: number; cost: number; in: number; cached: number; out: number; p50_ms: number;
  p95_ms: number; tool_errors: number; up: number; down: number; edits: number; undos: number; copies: number };
type U = { days: number; turns: number; total_cost: number; truncated: boolean; cost_complete: boolean;
  by_login: Row[]; by_skill: Row[]; by_model: Row[];
  recent: Array<{ at: string; login: string; issue: number; skill: string | null; model: string; steps: number; finish: string;
    ms: number; in: number; out: number; cost: number; tool_errors: number }>;
  feedback: Array<{ at: string; login: string; value: string; note?: string; issue?: number }> };

const usd = (x: number) => `$${x.toFixed(x < 1 ? 3 : 2)}`;
const k = (x: number) => `${(x / 1000).toFixed(1)}k`;
const s = (ms: number) => `${(ms / 1000).toFixed(1)} s`;

export function Usage() {
  const [days, setDays] = useState(7);
  const [u, setU] = useState<U | null>(null);
  const [err, setErr] = useState<string | null>(null);
  useEffect(() => { setU(null); api<U>(`/api/usage?days=${days}`).then(setU, (e) => setErr(e.message)); }, [days]);
  if (err) return <div className="banner err">{err}</div>;
  return (
    <>
      <section className="card">
        <div className="head"><h1>Co-review usage</h1>
          <select value={days} onChange={(e) => setDays(Number(e.target.value))} aria-label="Window">
            {[1, 7, 30].map((d) => <option key={d} value={d}>Last {d} d</option>)}</select></div>
        <div className="body">
          {!u ? <p className="muted">Loading…</p> : (
            <p style={{ margin: 0 }}><b className="mono">{u.turns}</b> agent turns · <b className="mono">{usd(u.total_cost)}</b> total
              {!u.cost_complete && " (cost partial: gateway logs not fully read)"}{u.truncated && " · event list truncated"}.
              Cost from AI Gateway logs; tokens and latency from the Worker's per-turn events.</p>)}
        </div>
      </section>
      {u && <Table title="By reviewer" rows={u.by_login} />}
      {u && <Table title="By skill" rows={u.by_skill} />}
      {u && <Table title="By model" rows={u.by_model} />}
      {u && (
        <section className="card"><div className="head"><h2>Recent turns</h2></div>
          <div className="scroll"><table>
            <thead><tr><th>When</th><th>Reviewer</th><th>Issue</th><th>Skill</th><th>Model</th><th>Steps</th><th>Tokens in/out</th><th>Time</th><th>Cost</th><th>Tool errors</th></tr></thead>
            <tbody>{u.recent.map((r, i) => (
              <tr key={i}><td className="small">{short(r.at)} {r.at.slice(11, 16)}</td><td className="mono">{r.login}</td>
                <td><a href={`#/i/${r.issue}`}>#{r.issue}</a></td><td>{r.skill ?? "chat"}</td><td className="mono small">{r.model}</td>
                <td>{r.steps}{r.finish !== "stop" && r.finish !== "tool-calls" ? ` (${r.finish})` : ""}</td>
                <td className="mono small">{k(r.in)} / {k(r.out)}</td><td>{s(r.ms)}</td><td className="mono">{usd(r.cost)}</td><td>{r.tool_errors || ""}</td></tr>))}
            </tbody></table></div></section>)}
      {u && !!u.feedback.length && (
        <section className="card"><div className="head"><h2>Feedback</h2></div><div className="body"><ul className="why">
          {u.feedback.map((f, i) => <li key={i}>{f.value === "up" ? "👍" : "👎"} <span className="mono">{f.login}</span> on #{f.issue} · {short(f.at)}{f.note && <> — “{f.note}”</>}</li>)}
        </ul></div></section>)}
    </>
  );
}

function Table({ title, rows }: { title: string; rows: Row[] }) {
  return (
    <section className="card"><div className="head"><h2>{title}</h2></div>
      <div className="scroll"><table>
        <thead><tr><th></th><th>Turns</th><th>Cost</th><th>Tokens in (cached)</th><th>Out</th><th>p50 / p95</th><th>Tool errors</th>
          <th>👍 / 👎</th><th>Draft edits / undos</th><th>Copies</th></tr></thead>
        <tbody>{rows.map((r) => (
          <tr key={r.key}><td className="mono">{r.key}</td><td>{r.turns}</td><td className="mono">{usd(r.cost)}</td>
            <td className="mono small">{k(r.in)} ({k(r.cached)})</td><td className="mono small">{k(r.out)}</td>
            <td>{s(r.p50_ms)} / {s(r.p95_ms)}</td><td>{r.tool_errors || ""}</td><td>{r.up} / {r.down}</td>
            <td>{r.edits} / {r.undos}</td><td>{r.copies}</td></tr>))}
        </tbody></table></div></section>
  );
}
