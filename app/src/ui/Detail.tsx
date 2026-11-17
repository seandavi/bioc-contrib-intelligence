import { useEffect, useState } from "react";
import { api, atRisk, band, type Check, type Data, days, type Entry, glyph, type Me, short } from "./lib";
import { CoReview, track } from "./CoReview";
import { Checks, Differs, Md, Wait } from "./parts";

// Review detail (spec §5.3, §7).
export function Detail({ n, data, me }: { n: number; data: Data; me: Me }) {
  const [issue, setIssue] = useState<{ thread: Entry[]; review: string | null } | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [showBots, setShowBots] = useState(false);
  // Co-review sidebar: open by default; open/closed is remembered per browser.
  const [ai, setAiState] = useState(() => localStorage.getItem("cr:open") !== "0");
  const setAi = (v: boolean) => { setAiState(v); localStorage.setItem("cr:open", v ? "1" : "0"); if (v) track("co_review_open", { issue: n }); };
  useEffect(() => {
    setIssue(null); setErr(null);
    api<{ thread: Entry[]; review: string | null }>(`/api/issues/${n}`).then(setIssue, (e) => setErr(e.message));
  }, [n]);

  const rows = data.queue.filter((r) => r.issue_number === n);
  const un = data.unassigned.find((u) => u.issue_number === n);
  const info = data.issues[n];
  const title = info?.package ?? rows[0]?.title ?? un?.title ?? `#${n}`;
  const submitter = rows[0]?.submitter ?? un?.submitter ?? "";
  const reviewers = rows.map((r) => r.reviewer);
  const mine = rows.find((r) => r.reviewer.toLowerCase() === me.login.toLowerCase()) ?? rows[0];
  const you = !!mine && mine.reviewer.toLowerCase() === me.login.toLowerCase();
  const gh = `https://github.com/${data.repo}/issues/${n}`;
  const b = info?.latest_build;
  const live = info?.live?.jobs.length ? info.live : null;

  if (!rows.length && !un) return <div className="banner err">Issue #{n} isn’t in your view.</div>;
  const d = mine ? days(mine.waiting_since) : days(un!.created_at);

  return (
    <div className={ai ? "cr-layout" : undefined}>
    <div className="cr-page">
      <div><a href="#/">← Back</a></div>
      <section className="card">
        <div className="head" style={{ alignItems: "flex-start" }}>
          <div>
            <h1 className="mono">{title}</h1>
            <a href={gh} target="_blank" rel="noreferrer" className="mono">#{n} on GitHub ↗</a>
          </div>
          <div className="checks">
            {mine ? (mine.reviewer_turn ? <span className="tag tag-you">{you ? "Your move" : "Reviewer’s move"}</span>
              : <span className="tag tag-them">Submitter’s move</span>) : <span className="tag tag-unassigned">Unassigned</span>}
            <Wait d={d} />
            {mine && atRisk(mine, me.deadline) && <span className="tag tag-risk">⚠ At risk for {me.deadline_label.replace(/^Bioconductor /, "")} · {short(me.deadline)}</span>}
          </div>
        </div>
        <div className="body">
          <dl className="meta">
            <div><dt>Submitter</dt><dd className="mono">{submitter}</dd></div>
            <div><dt>Reviewer</dt><dd className="mono">{reviewers.length ? reviewers.map((r) => r + (r.toLowerCase() === me.login.toLowerCase() ? " (you)" : "")).join(", ") : "—"}</dd></div>
            <div><dt>Stage</dt><dd>{mine?.stage ?? "—"}{mine?.stage_since && `, since ${short(mine.stage_since)}`}</dd></div>
          </dl>
        </div>
        {mine && (
          <div className="body">
            <details>
              <summary>Why {d} days?</summary>
              <ul className="why">
                {rows.length > 1 && <li>{reviewers.join(" and ")} share this review: a comment by either counts</li>}
                <li>{short(mine.first_assigned)} · first reviewer assigned{!mine.team_last && " → reviewer’s move starts"}</li>
                {rows.filter((r) => r.assigned_at !== mine.first_assigned).map((r) =>
                  <li key={r.reviewer}>{short(r.assigned_at)} · {r.reviewer} assigned</li>)}
                {mine.team_last
                  ? <li>{short(mine.team_last)} · last reviewer comment, by {mine.team_last_by}</li>
                  : <li>No reviewer comment since assignment</li>}
                {mine.team_last && mine.reviewer_turn &&
                  <li>{short(mine.waiting_since)} · submitter {mine.pushes_since && !mine.comments_since ? "pushed a new version" : "replied"} → reviewer’s move starts</li>}
                <li>Today · {d} days → band <Wait d={d} /> ({band(d)})</li>
                {atRisk(mine, me.deadline) && <li>Deadline {short(me.deadline)} is under 30 d away and the reviewer hasn’t moved → at risk</li>}
              </ul>
            </details>
          </div>
        )}
        <div className="filters">
          {!ai && <button className="btn primary" type="button" onClick={() => setAi(true)}>Co-review</button>}
          <a className="btn" href={`${gh}#new_comment_field`} target="_blank" rel="noreferrer">Comment on GitHub ↗</a>
        </div>
      </section>

      <div className="split">
        <div className="main">
          <section className="card" aria-label="Timeline">
            <div className="head">
              <h2>Timeline<span className="count">{issue?.thread.length ?? "…"}</span></h2>
              <label className="small"><input type="checkbox" checked={showBots} onChange={(e) => setShowBots(e.target.checked)} /> Show bot and label entries</label>
            </div>
            <div className="body">
              <div className="legend" style={{ marginBottom: 10 }}>
                <span><i style={{ background: "var(--role-reviewer)" }} />Reviewer</span>
                <span><i style={{ background: "var(--role-submitter)" }} />Submitter</span>
                <span><i style={{ background: "var(--role-core)" }} />Core / other</span>
                <span><i style={{ background: "var(--role-bot)" }} />Bot / event</span>
              </div>
              {err && <div className="banner err">Couldn’t load the thread: {err}</div>}
              {!issue && !err && <p className="muted">Loading…</p>}
              {issue && <Timeline thread={issue.thread} submitter={submitter} reviewers={reviewers} showBots={showBots} gh={gh} />}
            </div>
          </section>
        </div>
        <aside className="rail">
          <section className="card" aria-label="Current checks">
            <div className="head"><h2>Current checks{(live ?? b) && <span className="mono small muted">{live?.version ?? b!.version}</span>}</h2></div>
            <div className="body">
              {info?.live_differs && <p style={{ marginTop: 0 }}><Differs info={info} /></p>}
              <Checks info={info} />
              {live ? (
                <>
                  <CheckTable checks={live.jobs} />
                  <p className="note" style={{ marginTop: 8 }}>
                    Live from r-universe (commit {short(live.commit_time)}). r-universe re-runs checks without posting to the issue.
                  </p>
                  {b && (
                    <details>
                      <summary className="small">Bot’s report on the issue · {b.version} · {short(b.posted_at)}</summary>
                      <CheckTable checks={b.checks} />
                    </details>
                  )}
                </>
              ) : b ? (
                <>
                  <CheckTable checks={b.checks} />
                  <p className="note" style={{ marginTop: 8 }}>From the bot’s newest build report ({short(b.posted_at)}).</p>
                </>
              ) : <p className="muted">No build report on the issue yet.</p>}
              <div className="kv" style={{ marginTop: 10 }}>
                {b?.run_url && <><span className="muted">Build run</span><a href={b.run_url} target="_blank" rel="noreferrer">GitHub Actions ↗</a></>}
                {b?.runiverse_url && <><span className="muted">r-universe</span><a href={b.runiverse_url} target="_blank" rel="noreferrer">check page ↗</a></>}
                {b?.staging_url && <><span className="muted">Staging</span><a href={b.staging_url} target="_blank" rel="noreferrer">repository ↗</a></>}
                {info?.source_url && <><span className="muted">Source</span><a href={info.source_url} target="_blank" rel="noreferrer">repository ↗</a></>}
              </div>
            </div>
          </section>
          {mine && (
            <section className="card" aria-label="Since last comment">
              <div className="head"><h2>Since the last reviewer comment</h2></div>
              <div className="body">
                {!mine.team_last && <p style={{ marginTop: 0 }}>No reviewer has commented since assignment on {short(mine.first_assigned)}.</p>}
                {rows.filter((r) => !r.reviewer_last && mine.team_last).map((r) =>
                  <p key={r.reviewer} style={{ marginTop: 0 }} className="small muted">{r.reviewer} hasn’t commented; {mine.team_last_by} has.</p>)}
                <div className="kv"><span className="muted">Pushes</span><span>{mine.pushes_since}</span>
                  <span className="muted">Submitter comments</span><span>{mine.comments_since}</span></div>
              </div>
            </section>
          )}
          <section className="card" aria-label="Versions">
            <div className="head"><h2>Versions<span className="count">{info?.versions.length ?? 0}</span></h2></div>
            <div className="body">
              <ul className="why">
                {[...(info?.versions ?? [])].reverse().map((v, i) => (
                  <li key={i}><span className="mono">{v.version}</span> <span className="small muted">{short(v.posted_at)} · {
                    v.kind === "invalid_version" ? "invalid version bump, not built" : v.kind === "first" ? "first build" : "build"}</span>{" "}
                    {v.worst && <span className={`ck ck-${v.worst}`}>{v.worst === "OK" ? "✓" : glyph(v.worst)}</span>}</li>
                ))}
              </ul>
            </div>
          </section>
        </aside>
      </div>
    </div>
    {ai && <CoReview key={n} n={n} me={me} close={() => setAi(false)} />}
    </div>
  );
}

function CheckTable({ checks }: { checks: Check[] }) {
  return (
    <table style={{ minWidth: 0, marginTop: 8 }}>
      <thead><tr><th>Platform</th><th>R</th><th>Status</th><th>Log</th></tr></thead>
      <tbody>{checks.map((c) => (
        <tr key={c.platform}><td className="mono small">{c.platform}</td><td className="mono small">{c.r_version}</td>
          <td><span className={`ck ck-${c.status}`}>{c.status === "OK" ? "OK" : `${glyph(c.status)} ${c.status}`}</span></td>
          <td>{c.url ? <a href={c.url} target="_blank" rel="noreferrer">log</a> : <span className="muted">—</span>}</td></tr>
      ))}</tbody>
    </table>
  );
}

function Timeline({ thread, submitter, reviewers, showBots, gh }:
  { thread: Entry[]; submitter: string; reviewers: string[]; showBots: boolean; gh: string }) {
  const role = (e: Entry) => e.is_bot ? "bot" : e.who === submitter ? "submitter"
    : reviewers.includes(e.who) ? "reviewer" : "core";
  // Slash commands (/accept-policies) are bot instructions, not conversation.
  const human = (e: Entry) => e.kind === "comment" && !e.is_bot && !(e.body ?? "").trimStart().startsWith("/");
  const shown = thread.filter((e) => showBots || human(e) || e.kind === "assigned" || e.kind === "unassigned");
  const hidden = thread.length - shown.length;
  return (
    <>
      {hidden > 0 && !showBots && <p className="note" style={{ marginBottom: 8 }}>{hidden} bot and label entries hidden.</p>}
      <ol className="tl">
        {shown.map((e) => e.kind === "comment" ? (
          <li key={e.id} className={role(e)}>
            <div className="who-line"><b>{e.who}</b><span>{role(e)}</span>
              <a href={`${gh}#issuecomment-${e.id}`} target="_blank" rel="noreferrer">{new Date(e.created_at).toUTCString().slice(5, 22)} UTC ↗</a></div>
            {e.is_bot ? <details><summary className="small">Bot comment</summary><Md text={e.body ?? ""} /></details> : <Md text={e.body ?? ""} />}
          </li>
        ) : (
          <li key={e.id} className="ev">
            <span className="mono">{e.who}</span> {e.kind} <b>{e.body}</b> · <a href={`${gh}#event-${e.id}`} target="_blank" rel="noreferrer">{short(e.created_at)}</a>
          </li>
        ))}
      </ol>
    </>
  );
}
