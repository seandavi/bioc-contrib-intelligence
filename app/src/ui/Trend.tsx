import type { TrendPoint } from "./lib";

type Line = { key: keyof TrendPoint; label: string; color: string; dash?: string };
const W = 640, H = 200, L = 36, R = 8, T = 8, B = 22;
const mon = new Intl.DateTimeFormat("en-GB", { month: "short", timeZone: "UTC" });
const day = new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", timeZone: "UTC" });

// ponytail: hand-rolled SVG lines, no chart lib; add one if we need zoom or many series.
function Chart({ pts, lines, unit, refLine }: { pts: TrendPoint[]; lines: Line[]; unit: string; refLine?: number }) {
  const val = (p: TrendPoint, k: keyof TrendPoint) => (typeof p[k] === "number" ? (p[k] as number) : null);
  const top = Math.max(refLine ?? 0, ...pts.flatMap((p) => lines.map((l) => val(p, l.key) ?? 0)));
  const step = [1, 2, 5, 10, 20, 25, 50, 100, 200, 500].find((s) => top / s <= 5) ?? 1000;
  const max = Math.ceil((top || 1) / step) * step;
  const x = (i: number) => L + (i * (W - L - R)) / Math.max(1, pts.length - 1);
  const y = (v: number) => T + (H - T - B) * (1 - v / max);
  const ticks = Array.from({ length: Math.floor(max / step) + 1 }, (_, i) => i * step);
  const months = pts.map((p, i) => [i, new Date(p.t)] as const)
    .filter(([i, d]) => i === 0 || d.getUTCMonth() !== new Date(pts[i - 1].t).getUTCMonth());
  const path = (k: keyof TrendPoint) => pts.map((p, i) => [i, val(p, k)] as const).filter(([, v]) => v != null)
    .map(([i, v], j) => `${j ? "L" : "M"}${x(i).toFixed(1)},${y(v!).toFixed(1)}`).join("");
  return (
    <figure className="trend">
      <figcaption className="legend small">
        {lines.map((l) => <span key={l.key}><i style={{ borderColor: l.color, borderTopStyle: l.dash ? "dashed" : "solid" }} />{l.label}</span>)}
      </figcaption>
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${lines.map((l) => l.label).join(", ")}, weekly`}>
        {ticks.map((v) => <g key={v}><line x1={L} x2={W - R} y1={y(v)} y2={y(v)} className="grid" />
          <text x={L - 6} y={y(v) + 4} textAnchor="end">{v}</text></g>)}
        {months.map(([i, d]) => <text key={i} x={x(i)} y={H - 6} textAnchor="middle">{mon.format(d)}</text>)}
        {refLine != null && <line x1={L} x2={W - R} y1={y(refLine)} y2={y(refLine)} className="ref" />}
        {lines.map((l) => <path key={l.key} d={path(l.key)} fill="none" stroke={l.color} strokeWidth={2} strokeDasharray={l.dash} />)}
        {pts.map((p, i) => (
          <rect key={i} x={x(i) - (W - L - R) / pts.length / 2} y={T} width={(W - L - R) / pts.length} height={H - T - B} className="hit">
            <title>{`Week to ${day.format(new Date(p.t))}\n${lines.map((l) => `${l.label}: ${val(p, l.key) == null ? "—" : `${Math.round(val(p, l.key)!)}${unit}`}`).join("\n")}`}</title>
          </rect>
        ))}
      </svg>
    </figure>
  );
}

export function Trends({ pts }: { pts: TrendPoint[] }) {
  if (pts.length < 2) return null;
  const sum = (k: "opened" | "closed") => pts.slice(-4).reduce((a, p) => a + p[k], 0);
  return (
    <section className="card" aria-label="Trends">
      <div className="head"><h2>Trends, weekly</h2>
        <span className="small muted">Last 4 weeks: {sum("opened")} opened · {sum("closed")} closed · hover for values</span></div>
      <div className="body trends">
        <div><h3>Backlog</h3>
          <Chart pts={pts} unit="" lines={[
            { key: "open", label: "Open", color: "var(--text)" },
            { key: "reviewer_move", label: "Reviewer’s move", color: "var(--role-reviewer)" },
            { key: "over28", label: "Reviewer’s move > 28 d", color: "var(--risk)" },
            { key: "unassigned", label: "Unassigned", color: "var(--admin)", dash: "4 3" },
          ]} /></div>
        <div><h3>Wait on reviewer’s move (days)</h3>
          <Chart pts={pts} unit=" d" refLine={28} lines={[
            { key: "median_wait", label: "Median", color: "var(--role-reviewer)" },
            { key: "p90_wait", label: "90th percentile", color: "var(--risk)", dash: "4 3" },
          ]} /></div>
      </div>
      <p className="note body">Replayed from the issue history with today’s whose-move rule; the last point is now. Reopened and unassigned events are ignored. Dotted line: 28 d.</p>
    </section>
  );
}
