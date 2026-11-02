import { useState } from "react";
import { atRisk, type Data, days, explain, type Me, type QueueRow, short, sinceText } from "./lib";
import { AiChips, Checks, Pkg, Wait } from "./parts";

// My queue (spec §5.2), and an admin's read-only view of another reviewer's queue.
export function Queue({ data, me, login }: { data: Data; me: Me; login: string }) {
  const you = login.toLowerCase() === me.login.toLowerCase();
  const rows = data.queue
    .filter((r) => r.reviewer.toLowerCase() === login.toLowerCase())
    .sort((a, b) => Number(b.reviewer_turn) - Number(a.reviewer_turn) || a.waiting_since.localeCompare(b.waiting_since));
  const mine = rows.filter((r) => r.reviewer_turn);
  const theirs = rows.filter((r) => !r.reviewer_turn);
  const oldest = mine[0];
  const risk = mine.filter((r) => atRisk(r, me.deadline)).length;

  return (
    <>
      <div>
        <h1>{you ? "My queue" : `${login}’s queue`}</h1>
        <p>{you ? "Your" : `${login}’s`} assignments on {data.repo}. {you ? "Your" : "Their"} move first, then the longest wait.</p>
      </div>
      <section className="stats" aria-label="Summary">
        <Stat label="Open assignments" value={rows.length} />
        <Stat label={you ? "Your move" : "Their move"} value={mine.length} />
        <div className="stat">
          <span className="label">Oldest wait</span>
          {oldest ? (
            <span className="value"><span className="num">{days(oldest.waiting_since)} d</span>
              <Wait d={days(oldest.waiting_since)} /><span className="mono small muted">#{oldest.issue_number}</span></span>
          ) : <span className="num">—</span>}
        </div>
        <div className="stat">
          <span className="label">At deadline risk</span>
          <span className="value"><span className={`num ${risk ? "risk" : ""}`}>{risk}</span>
            <span className="small muted">for {me.deadline_label.replace(/^Bioconductor /, "")}, {short(me.deadline)}</span></span>
        </div>
      </section>
      <ThreadNote />
      {rows.length === 0 ? (
        <div className="banner">Nothing assigned to {you ? "you" : login}.</div>
      ) : (
        <>
          <Section title={you ? "Your move" : "Their move"} rows={mine} data={data} me={me} you={you} open />
          <Section title="Submitter’s move" rows={theirs} data={data} me={me} you={you} open={false} />
        </>
      )}
    </>
  );
}

const Stat = ({ label, value }: { label: string; value: number }) => (
  <div className="stat"><span className="label">{label}</span><span className="num">{value}</span></div>
);

export const ThreadNote = () => (
  <p className="note">
    “Whose move” is worked out from the issue thread only. Review work done elsewhere (PR reviews on the
    package repo, email) isn’t visible. Each wait shows the events it came from.
  </p>
);

function Section({ title, rows, data, me, you, open: initial }:
  { title: string; rows: QueueRow[]; data: Data; me: Me; you: boolean; open: boolean }) {
  const [open, setOpen] = useState(initial);
  return (
    <section className="card" aria-label={title}>
      <div className="head">
        <h2>{title}<span className="count">{rows.length}</span></h2>
        <button className="btn" type="button" aria-expanded={open} onClick={() => setOpen(!open)}>
          {open ? "Hide" : "Show"}
        </button>
      </div>
      {open && (rows.length ? (
        <div className="scroll">
          <table>
            <thead><tr>
              <th>Package · submitter</th><th>Waiting</th><th>Since {you ? "your" : "their"} last comment</th>
              <th>Checks · latest build</th><th>Stage</th><th>Last comment</th><th>AI review</th>
            </tr></thead>
            <tbody>
              {rows.map((r) => {
                const d = days(r.waiting_since);
                return (
                  <tr key={r.issue_number}>
                    <td><Pkg n={r.issue_number} name={r.title} sub={r.submitter} data={data} /></td>
                    <td><div className="stack">
                      <Wait d={d} />
                      <span className="small muted">{explain(r, you)}</span>
                      {atRisk(r, me.deadline) && <span className="tag tag-risk">⚠ At risk for {me.deadline_label.replace(/^Bioconductor /, "")}</span>}
                    </div></td>
                    <td>{sinceText(r)}<div className="small muted">{r.reviewer_last ? `since ${short(r.reviewer_last)}` : "since assignment"}</div></td>
                    <td><Checks build={data.issues[r.issue_number]?.latest_build} /></td>
                    <td>{r.stage ?? "—"}<div className="small muted">{r.stage_since && `since ${short(r.stage_since)}`}</div></td>
                    <td><div className="clamp small">{r.last_comment ?? <span className="muted">No human comments yet</span>}</div></td>
                    <td><AiChips /></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : <div className="body muted">Nothing here.</div>)}
    </section>
  );
}
