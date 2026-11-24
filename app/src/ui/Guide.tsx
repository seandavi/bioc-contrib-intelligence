import { useEffect, useState } from "react";
import guide from "./guide.md?raw";
import { ago, api, short, type TrendPoint } from "./lib";
import { Md } from "./parts";
import { Trends } from "./Trend";

type Summary = {
  generated_at: string; open: number; assignments: number; reviewers: number; unassigned: number;
  reviewer_move: number; over_28d: number; median_wait: number | null; deadline: string; deadline_label: string; trend: TrendPoint[];
};

const FEATURES: Array<[string, string, string]> = [
  ["⇄", "Whose move, at a glance", "Every open submission, sorted by who owes the next step and for how long, with what changed since the reviewer last commented."],
  ["✓", "Live checks", "Current R-universe results per platform, flagged when they are newer than the last build report on the issue."],
  ["✎", "An AI co-reviewer", "Drafts a first review from the source, check logs and thread, then follows up, triages checks and checks licensing. You edit; you post."],
  ["◎", "Read-only by design", "Reads the tracker and never posts, assigns or labels. Reviews still happen on GitHub, under your name."],
];

// The guide, for signed-in users (#/guide) and inside the public landing page.
export const Guide = () => <section className="card guide"><div className="body"><Md text={guide} prose /></div></section>;

// Signed out: what the app is, tracker-wide numbers, the guide. Sign-in is needed for everything else.
export function Landing() {
  const [s, setS] = useState<Summary | null>(null);
  useEffect(() => { api<Summary>("/api/public/summary").then(setS, () => {}); }, []);
  const left = s && Math.ceil((new Date(s.deadline).getTime() - Date.now()) / 864e5);
  return (
    <>
      <header className="bar">
        <div className="brand"><span className="logo" aria-hidden="true">BR</span><span>Bioconductor Reviews</span></div>
        <div className="right">
          {s && <span title={s.generated_at}>Data as of {short(s.generated_at)}, {s.generated_at.slice(11, 16)} UTC · {ago(s.generated_at)}</span>}
          <a className="btn primary" href="/auth/login">Sign in with GitHub</a>
        </div>
      </header>
      <section className="hero">
        <div className="hero-in">
          <p className="eyebrow">Bioconductor/BiocContributions</p>
          <h1>Package reviews on Bioconductor, out in the open</h1>
          <p className="lede">Where each submission stands, whose move it is, and an AI co-reviewer that drafts a
            first review in about a minute for the reviewer to edit and post.</p>
          <div className="cta">
            <a className="btn primary" href="/auth/login">Sign in with GitHub</a>
            <a className="btn ghost" href="#guide" onClick={(e) => { e.preventDefault(); document.getElementById("guide")?.scrollIntoView({ behavior: "smooth" }); }}>How it works ↓</a>
          </div>
          <p className="small hint">Open to reviewers with an assignment on BiocContributions and to the core team. The numbers on this page are public.</p>
        </div>
      </section>
      <main>
        {s && (
          <section className="stats" aria-label="Tracker summary">
            <div className="stat"><span className="label">Open submissions</span><span className="num">{s.open}</span>
              <span className="small muted">{s.assignments} assignments · {s.reviewers} reviewers</span></div>
            <div className="stat"><span className="label">Not yet assigned</span><span className="num">{s.unassigned}</span></div>
            <div className="stat"><span className="label">Reviewer’s move</span><span className="num">{s.reviewer_move}</span>
              <span className="small muted">{s.over_28d} waiting more than 28 days</span></div>
            <div className="stat"><span className="label">Median wait, reviewer’s move</span>
              <span className="num">{s.median_wait ?? "—"} d</span></div>
            {left !== null && left >= 0 && <div className="stat"><span className="label">{s.deadline_label}</span>
              <span className="num">{left} d</span><span className="small muted">{new Date(s.deadline).toUTCString().slice(0, 16)}</span></div>}
          </section>
        )}
        <section className="features" aria-label="What it does">
          {FEATURES.map(([icon, title, text]) => (
            <div className="feature" key={title}><span className="icon" aria-hidden="true">{icon}</span><h2>{title}</h2><p>{text}</p></div>
          ))}
        </section>
        {s && <Trends pts={s.trend} />}
        <div id="guide" />
        <Guide />
      </main>
    </>
  );
}
