import { useMemo, useState } from "react";
import { atRisk, band, type Data, days, explain, type Me, type QueueRow, short, sinceText } from "./lib";
import { AiChips, Checks, Pkg, Wait } from "./parts";
import { ThreadNote } from "./Queue";

const median = (a: number[]) => {
  if (!a.length) return null;
  const s = [...a].sort((x, y) => x - y), m = s.length >> 1;
  return s.length % 2 ? s[m] : Math.round((s[m - 1] + s[m]) / 2);
};

// Admin home (spec §5.4).
export function Overview({ data, me }: { data: Data; me: Me }) {
  const q = data.queue;
  const theirMove = q.filter((r) => r.reviewer_turn);
  const over28 = theirMove.filter((r) => days(r.waiting_since) > 28);
  const silent = over28.filter((r) => !r.reviewer_last);
  const risk = theirMove.filter((r) => atRisk(r, me.deadline));
  const reviewers = new Set(q.map((r) => r.reviewer));
  const open = new Set([...q.map((r) => r.issue_number), ...data.unassigned.map((u) => u.issue_number)]);
  const oldestUn = [...data.unassigned].sort((a, b) => a.created_at.localeCompare(b.created_at))[0];
  const left = Math.ceil((new Date(me.deadline).getTime() - Date.now()) / 864e5);

  return (
    <>
      <div>
        <h1>Overview</h1>
        <p>All open submissions on {data.repo}.</p>
      </div>
      <section className="stats" aria-label="Summary">
        <div className="stat"><span className="label">Open submissions</span><span className="num">{open.size}</span>
          <span className="small muted">{q.length} assignments · {reviewers.size} reviewers</span></div>
        <div className="stat"><span className="label">Unassigned</span><span className="num">{data.unassigned.length}</span>
          <span className="small muted">{oldestUn ? `oldest ${days(oldestUn.created_at)} d (#${oldestUn.issue_number})` : "none"}</span></div>
        <div className="stat"><span className="label">Reviewer’s move &gt; 28 d</span><span className="num">{over28.length}</span>
          <span className="small muted">{silent.length} with no reviewer comment since assignment</span></div>
        <div className="stat"><span className="label">At risk for {me.deadline_label.replace(/^Bioconductor /, "")}</span>
          <span className="num risk">{risk.length}</span>
          <span className="small muted">reviewer’s move, deadline in {left} d</span></div>
        <div className="stat"><span className="label">Median wait, reviewer’s move</span>
          <span className="num">{median(theirMove.map((r) => days(r.waiting_since))) ?? "—"} d</span></div>
      </section>
      <p className="note">
        “Whose move” and “no reviewer comment” count only comments by the assignee in the issue thread.
        Reviews done by someone else, or outside the thread, aren’t visible.
      </p>
      <Attention data={data} me={me} />
      <Load q={q} />
      <All data={data} me={me} />
    </>
  );
}

// Each submission once, under its most urgent reason.
function Attention({ data, me }: { data: Data; me: Me }) {
  const seen = new Set<number>();
  const take = (rows: QueueRow[]) => rows.filter((r) => !seen.has(r.issue_number) && seen.add(r.issue_number));
  const byWait = [...data.queue].filter((r) => r.reviewer_turn)
    .sort((a, b) => a.waiting_since.localeCompare(b.waiting_since));
  data.unassigned.forEach((u) => seen.add(u.issue_number));
  const groups = [
    { title: "Stalled, no reviewer comment", desc: "Over 60 d since assignment with no comment from the reviewer. Candidates for reassignment.",
      rows: take(byWait.filter((r) => !r.reviewer_last && days(r.waiting_since) > 60)) },
    { title: `At risk for ${me.deadline_label.replace(/^Bioconductor /, "")}`, desc: "Reviewer’s move, deadline close.",
      rows: take(byWait.filter((r) => atRisk(r, me.deadline))) },
    { title: "Stale", desc: "Reviewer’s move for 29–60 d.", rows: take(byWait.filter((r) => band(days(r.waiting_since)) === "stale")) },
  ];
  return (
    <section className="card" aria-label="Needs attention">
      <div className="head"><h2>Needs attention</h2><span className="small muted">Each submission appears once, under its most urgent reason</span></div>
      <div className="body">
        <h2>Unassigned<span className="count">{data.unassigned.length}</span></h2>
        <ul className="why">
          {data.unassigned.map((u) => (
            <li key={u.issue_number}>
              <a href={`#/i/${u.issue_number}`} className="mono">{data.issues[u.issue_number]?.package ?? u.title}</a> <span className="mono muted">#{u.issue_number} · {u.submitter}</span>{" "}
              <Wait d={days(u.created_at)} /> <span className="small muted">opened {short(u.created_at)}</span>{" "}
              <Checks info={data.issues[u.issue_number]} />
            </li>
          ))}
        </ul>
      </div>
      {groups.map((g) => (
        <div className="body" key={g.title}>
          <h2>{g.title}<span className="count">{g.rows.length}</span></h2>
          <p className="note">{g.desc}</p>
          <ul className="why">
            {g.rows.map((r) => (
              <li key={r.issue_number}>
                <a href={`#/i/${r.issue_number}`} className="mono">{data.issues[r.issue_number]?.package ?? r.title}</a> <span className="mono muted">#{r.issue_number}</span>{" "}
                <a href={`#/r/${encodeURIComponent(r.reviewer)}`} className="mono">{r.reviewer}</a>{" "}
                <Wait d={days(r.waiting_since)} /> <span className="small muted">{explain(r, false)}</span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </section>
  );
}

function Load({ q }: { q: QueueRow[] }) {
  const by = new Map<string, QueueRow[]>();
  for (const r of q) by.set(r.reviewer, [...(by.get(r.reviewer) ?? []), r]);
  const rows = [...by].map(([login, rs]) => {
    const w = rs.filter((r) => r.reviewer_turn).map((r) => days(r.waiting_since));
    return { login, open: rs.length, move: w.length, oldest: w.length ? Math.max(...w) : null, median: median(w) };
  }).sort((a, b) => (b.oldest ?? -1) - (a.oldest ?? -1));
  return (
    <section className="card" aria-label="Reviewer load">
      <div className="head"><h2>Reviewer load<span className="count">{rows.length}</span></h2></div>
      <div className="scroll">
        <table>
          <thead><tr><th>Reviewer</th><th className="num">Open</th><th className="num">Their move</th>
            <th>Oldest wait</th><th className="num">Median wait</th><th /></tr></thead>
          <tbody>
            {rows.map((v) => (
              <tr key={v.login}>
                <td className="mono">{v.login}</td><td className="num">{v.open}</td><td className="num">{v.move}</td>
                <td>{v.oldest == null ? "—" : <Wait d={v.oldest} />}</td>
                <td className="num">{v.median == null ? "—" : `${v.median} d`}</td>
                <td><a href={`#/r/${encodeURIComponent(v.login)}`}>View queue</a></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function All({ data, me }: { data: Data; me: Me }) {
  const [f, setF] = useState({ text: "", stage: "", band: "", reviewer: "", check: "", risk: false });
  const set = (k: keyof typeof f) => (e: { target: { value: string; checked?: boolean } }) =>
    setF({ ...f, [k]: k === "risk" ? !!e.target.checked : e.target.value });
  const stages = useMemo(() => [...new Set(data.queue.map((r) => r.stage ?? ""))].filter(Boolean).sort(), [data]);
  const reviewers = useMemo(() => [...new Set(data.queue.map((r) => r.reviewer))].sort(), [data]);
  const rows = data.queue.filter((r) => {
    const d = days(r.waiting_since), it = data.issues[r.issue_number];
    const worst = (it?.live?.jobs.length ? it.live.worst : it?.latest_build?.worst) ?? "none";
    return (!f.text || `${r.title} ${r.issue_number} ${r.submitter}`.toLowerCase().includes(f.text.toLowerCase()))
      && (!f.stage || r.stage === f.stage) && (!f.band || band(d) === f.band)
      && (!f.reviewer || r.reviewer === f.reviewer) && (!f.check || worst === f.check)
      && (!f.risk || atRisk(r, me.deadline));
  }).sort((a, b) => a.waiting_since.localeCompare(b.waiting_since));
  return (
    <section className="card" aria-label="All submissions">
      <div className="head"><h2>All assignments<span className="count">{data.queue.length}</span></h2>
        <span className="small muted">{rows.length} shown · sorted by waiting, longest first</span></div>
      <div className="filters">
        <input placeholder="Search package, #, submitter" value={f.text} onChange={set("text")} aria-label="Search" />
        <select value={f.stage} onChange={set("stage")} aria-label="Stage"><option value="">Any stage</option>
          {stages.map((s) => <option key={s}>{s}</option>)}</select>
        <select value={f.band} onChange={set("band")} aria-label="Wait band"><option value="">Any band</option>
          {["fresh", "due", "stale", "stalled"].map((s) => <option key={s}>{s}</option>)}</select>
        <select value={f.reviewer} onChange={set("reviewer")} aria-label="Reviewer"><option value="">Anyone</option>
          {reviewers.map((s) => <option key={s}>{s}</option>)}</select>
        <select value={f.check} onChange={set("check")} aria-label="Checks"><option value="">Any result</option>
          {["OK", "NOTE", "WARNING", "ERROR", "BUILD_FAILED"].map((s) => <option key={s}>{s}</option>)}</select>
        <label className="small"><input type="checkbox" checked={f.risk} onChange={set("risk")} /> At risk only</label>
      </div>
      <div className="scroll">
        <table>
          <thead><tr><th>Package · submitter</th><th>Reviewer</th><th>Whose move</th><th>Stage</th><th>Waiting</th>
            <th>Pushes · comments</th><th>Checks · latest build</th><th>AI review</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={`${r.issue_number}-${r.reviewer}`}>
                <td><Pkg n={r.issue_number} name={r.title} sub={r.submitter} data={data} /></td>
                <td><a className="mono" href={`#/r/${encodeURIComponent(r.reviewer)}`}>{r.reviewer}</a></td>
                <td>{r.reviewer_turn ? <span className="tag tag-you">Reviewer</span> : <span className="tag tag-them">Submitter</span>}</td>
                <td>{r.stage ?? "—"}</td>
                <td><div className="stack"><Wait d={days(r.waiting_since)} />
                  {atRisk(r, me.deadline) && <span className="tag tag-risk">⚠ At risk</span>}</div></td>
                <td>{sinceText(r)}</td>
                <td><Checks info={data.issues[r.issue_number]} /></td>
                <td><AiChips /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
