import DOMPurify from "dompurify";
import { marked } from "marked";
import { band, type Build, type Data, families, glyph } from "./lib";

export function Wait({ d }: { d: number }) {
  const b = band(d);
  return (
    <span className={`chip band-${b}`} title={`Waiting ${d} days: ${b}`}>
      <span className="d">{d} d</span>{b}
    </span>
  );
}

// Latest build, one chip per platform family. Never derived from issue labels:
// they pile up and don't show the current result.
export function Checks({ build }: { build: Build | null | undefined }) {
  if (!build) return <span className="muted small">No build report</span>;
  if (build.worst === "BUILD_FAILED")
    return (
      <div className="checks">
        <span className="ck ck-BUILD_FAILED" title="R-universe build failed">build failed</span>
        <span className="mono small muted">{build.version}</span>
      </div>
    );
  return (
    <div className="checks">
      {families(build.checks).map((f) => {
        const label = f.checks.length
          ? f.checks.map((c) => `${c.platform}: ${c.status}`).join(", ")
          : `${f.abbr}: not in this report`;
        return (
          <span key={f.abbr} className={`ck ck-${f.status}`} title={label} aria-label={label}>
            {f.abbr}{f.status !== "OK" && <span>{glyph(f.status)}</span>}
          </span>
        );
      })}
      <span className="mono small muted">{build.version}</span>
    </div>
  );
}

export const AXES: Array<[string, string]> = [
  ["C", "Code"], ["D", "Documentation"], ["F", "Bioconductor vs CRAN fit"],
  ["O", "Overlap with existing packages"], ["T", "Check triage"],
];

// ponytail: no review engine yet (#12), so every axis shows "not run".
export function AiChips() {
  return (
    <div className="checks" aria-label="AI review: not run">
      {AXES.map(([k, name]) => <span key={k} className="ax" title={`${name}: not run`}>{k}</span>)}
    </div>
  );
}

export function Md({ text }: { text: string }) {
  const html = DOMPurify.sanitize(marked.parse(text, { async: false, gfm: true, breaks: true }) as string);
  return <div className="md" dangerouslySetInnerHTML={{ __html: html }} />;
}

// Package name parsed from the issue body; titles are sometimes URLs or sentences.
export function Pkg({ n, name, sub, data }: { n: number; name: string; sub: string; data: Data }) {
  name = data.issues[n]?.package ?? name;
  return (
    <div className="pkg">
      <a href={`#/i/${n}`}>{name}</a>
      <span>#{n} · {sub}</span>
    </div>
  );
}
