import { useEffect, useState } from "react";
import guide from "./guide.md?raw";
import { ago, api, short } from "./lib";
import { Md } from "./parts";

type Summary = {
  generated_at: string; open: number; assignments: number; reviewers: number; unassigned: number;
  reviewer_move: number; over_28d: number; median_wait: number | null; deadline: string; deadline_label: string;
};

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
      <main>
        <div>
          <h1>Package reviews on Bioconductor</h1>
          <p>Where each submission stands, and an AI co-reviewer to help draft your review.</p>
        </div>
        <div className="banner">
          <b>Sign in to use the app.</b> Your queue, the review pages and the co-reviewer need a GitHub sign-in, and
          they're open to reviewers with an assignment on BiocContributions and to the core team. This page and the
          numbers below are public.{" "}<a href="/auth/login">Sign in with GitHub →</a>
        </div>
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
        <Guide />
      </main>
    </>
  );
}
