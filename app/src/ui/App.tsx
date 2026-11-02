import { useEffect, useState } from "react";
import { Detail } from "./Detail";
import { ago, api, type Data, type Me, short } from "./lib";
import { Overview } from "./Overview";
import { Queue } from "./Queue";

const useHash = () => {
  const [h, setH] = useState(location.hash.slice(1) || "/");
  useEffect(() => {
    const f = () => { setH(location.hash.slice(1) || "/"); scrollTo(0, 0); };
    addEventListener("hashchange", f);
    return () => removeEventListener("hashchange", f);
  }, []);
  return h;
};

type State = { me?: Me; data?: Data; error?: string; status?: number };

export function App() {
  const [s, setS] = useState<State>({});
  const route = useHash();
  useEffect(() => {
    const load = () => api<Me>("/api/me")
      .then(async (me) => setS({ me, data: me.allowed ? await api<Data>("/api/data") : undefined }))
      .catch((e) => setS({ error: e.message, status: e.status }));
    load();
    const t = setInterval(load, 5 * 60e3); // the snapshot refreshes every 5 min
    return () => clearInterval(t);
  }, []);

  if (s.status === 401) return <SignIn />;
  if (s.error) return <Center><div className="banner err">Couldn’t load data: {s.error}</div></Center>;
  if (!s.me) return <Center><p className="muted">Loading…</p></Center>;
  const { me, data } = s;
  if (!me.allowed) return <Center><div><h1>No access</h1><p className="muted">Signed in as <b className="mono">{me.login}</b>. This app is for
    reviewers with open assignments on {me.repo} and for its triage team.</p><SignOut dark={false} /></div></Center>;
  if (!data) return <Center><p className="muted">Loading…</p></Center>;

  let page, nav = "queue";
  const m = route.match(/^\/(i|r)\/([^/]+)/);
  if (m?.[1] === "i") page = <Detail n={Number(m[2])} data={data} me={me} />;
  else if (m?.[1] === "r" && me.admin) { page = <Queue data={data} me={me} login={decodeURIComponent(m[2])} />; nav = ""; }
  else if (route === "/queue" || !me.admin) page = <Queue data={data} me={me} login={me.login} />;
  else { page = <Overview data={data} me={me} />; nav = "overview"; }

  const left = Math.ceil((new Date(me.deadline).getTime() - Date.now()) / 864e5);
  return (
    <>
      <header className="bar">
        <div className="brand"><span className="logo" aria-hidden="true">BR</span><span>Bioconductor Reviews</span></div>
        <nav aria-label="Main">
          {me.admin && <a href="#/" aria-current={nav === "overview" ? "page" : undefined}>Overview</a>}
          <a href={me.admin ? "#/queue" : "#/"} aria-current={nav === "queue" ? "page" : undefined}>My queue</a>
        </nav>
        <div className="right">
          <span title={data.generated_at}>Data as of {short(data.generated_at)}, {data.generated_at.slice(11, 16)} UTC · {ago(data.generated_at)} · refreshes every 5 min</span>
          <span className="who"><img className="avatar" alt="" src={`https://github.com/${me.login}.png?size=48`} />{me.login}
            {me.admin && <span className="tag tag-admin">Admin</span>}</span>
          <SignOut dark />
        </div>
      </header>
      {left >= 0 && (
        <div className="deadline"><b>{me.deadline_label} deadline</b>
          <span>{new Date(me.deadline).toUTCString().slice(0, 16)} · <span className="mono"><b>{left} d</b></span> away</span></div>
      )}
      <main>{page}</main>
    </>
  );
}

const Center = ({ children }: { children: React.ReactNode }) => <div className="center">{children}</div>;

function SignIn() {
  return (
    <Center>
      <div style={{ maxWidth: 420 }}>
        <div className="brand" style={{ justifyContent: "center", color: "var(--text)", marginBottom: 12 }}>
          <span className="logo" style={{ background: "var(--text)", color: "#fff" }}>BR</span><span>Bioconductor Reviews</span></div>
        <p className="muted">Pending reviews on Bioconductor/BiocContributions: whose move it is, how long it’s been
          waiting, and what changed since the last comment.</p>
        <a className="btn primary" href="/auth/login">Sign in with GitHub</a>
      </div>
    </Center>
  );
}

function SignOut({ dark }: { dark: boolean }) {
  const out = () => fetch("/auth/logout", { method: "POST" }).then(() => location.assign("/"));
  return <button type="button" className={dark ? "linkbtn" : "btn"} onClick={out}>Sign out</button>;
}
