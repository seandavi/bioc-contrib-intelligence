// What the co-review agent can read about a package, all pinned and cached:
// the source tree at the commit r-universe built, and the check logs of that build.
// One tarball fetch per commit, unpacked once into R2 (src/<repo>@<sha>.json);
// logs cached per job id (immutable). Everything here is submitter-controlled text.

const UA = { "User-Agent": "bioc-reviews" };
const MAX_FILE = 512 * 1024; // larger files are listed, not stored
const MAX_TAR = 60 * 1024 * 1024;

export type Build = {
  pkg: string;
  version: string | null;
  staging: string; // owner/repo the files come from (BiocStaging mirror)
  link: string; // owner/repo used in permalinks (submitter's repo when the commit exists there)
  sha: string;
  jobs: Array<{ platform: string; job: number; status: string; r: string }>;
  bioccheck: { error: number; warning: number; note: number } | null;
};
export type Tree = { files: Record<string, string>; skipped: Array<{ path: string; size: number }> };

const cached = async <T>(bucket: R2Bucket, key: string, make: () => Promise<T>): Promise<T> => {
  const hit = await bucket.get(key);
  if (hit) return hit.json<T>();
  const v = await make();
  await bucket.put(key, JSON.stringify(v));
  return v;
};

const ghRepo = (url: string | null | undefined) => url?.match(/github\.com\/([^/]+\/[^/#?]+?)(?:\.git)?\/?$/)?.[1];

// The build r-universe currently has for the package: commit, jobs, BiocCheck counts.
export async function build(pkg: string, sourceUrl: string | null, token: string): Promise<Build | null> {
  const r = await fetch(`https://biocstaging.r-universe.dev/api/packages/${encodeURIComponent(pkg)}`, { headers: UA });
  if (!r.ok) return null;
  const d = (await r.json()) as Record<string, any>;
  const staging = ghRepo(d.RemoteUrl) ?? `BiocStaging/${pkg}`;
  const sha = d.RemoteSha as string;
  let link = staging;
  const src = ghRepo(sourceUrl);
  if (src && src.toLowerCase() !== staging.toLowerCase()) {
    // ponytail: one HEAD-ish lookup per chat turn; cache it if it shows up in latency.
    const c = await fetch(`https://api.github.com/repos/${src}/commits/${sha}`, { method: "HEAD",
      headers: { ...UA, Accept: "application/vnd.github+json", ...(token ? { Authorization: `Bearer ${token}` } : {}) } });
    if (c.ok) link = src;
  }
  return {
    pkg, version: d.Version ?? null, staging, link, sha,
    jobs: ((d._jobs ?? []) as any[]).filter((j) => j.job).map((j) => ({ platform: j.config, job: j.job, status: j.check, r: j.r })),
    bioccheck: d._bioccheck ?? null,
  };
}

export const permalink = (b: Build, path: string, from?: number, to?: number) =>
  `https://github.com/${b.link}/blob/${b.sha}/${path}` + (from ? `#L${from}` + (to && to !== from ? `-L${to}` : "") : "");

// Source tree at the built commit. Text files only, each ≤ MAX_FILE.
export function tree(bucket: R2Bucket, b: Build): Promise<Tree> {
  return cached(bucket, `src/${b.staging}@${b.sha}.json`, async () => {
    const r = await fetch(`https://codeload.github.com/${b.staging}/tar.gz/${b.sha}`, { headers: UA });
    if (!r.ok || !r.body) throw new Error(`tarball ${r.status}`);
    const tar = new Uint8Array(await new Response(r.body.pipeThrough(new DecompressionStream("gzip"))).arrayBuffer());
    if (tar.length > MAX_TAR) throw new Error("source too large");
    return untar(tar);
  });
}

// Minimal ustar reader: regular files, GNU long names, pax path records.
export function untar(tar: Uint8Array): Tree {
  const dec = new TextDecoder();
  const str = (o: number, n: number) => dec.decode(tar.subarray(o, o + n)).replace(/\0.*$/s, "");
  const files: Record<string, string> = {};
  const skipped: Tree["skipped"] = [];
  let long: string | null = null;
  for (let o = 0; o + 512 <= tar.length;) {
    const name = str(o, 100);
    if (!name) break;
    const size = parseInt(str(o + 124, 12).trim() || "0", 8);
    const type = String.fromCharCode(tar[o + 156] || 48);
    const body = tar.subarray(o + 512, o + 512 + size);
    let path = long ?? ((str(o + 345, 155) ? str(o + 345, 155) + "/" : "") + name);
    long = null;
    if (type === "L") long = dec.decode(body).replace(/\0.*$/s, "");
    else if (type === "x") long = dec.decode(body).match(/\d+ path=([^\n]*)\n/)?.[1] ?? null;
    else if (type === "0" || type === "\0") {
      path = path.replace(/^[^/]+\//, ""); // drop the <repo>-<sha>/ prefix
      if (size > MAX_FILE || body.subarray(0, 8000).includes(0)) skipped.push({ path, size });
      else files[path] = dec.decode(body);
    }
    o += 512 + Math.ceil(size / 512) * 512;
  }
  return { files, skipped };
}

export function readFile(t: Tree, b: Build, path: string, from = 1, to?: number) {
  const text = t.files[path];
  if (text === undefined)
    return t.skipped.some((s) => s.path === path) ? `${path}: binary or larger than ${MAX_FILE} bytes; not readable.` : `${path}: no such file.`;
  const lines = text.split("\n");
  const end = Math.min(to ?? from + 399, lines.length, from + 799);
  const w = String(end).length;
  const body = lines.slice(from - 1, end).map((l, i) => `${String(from + i).padStart(w)}| ${l}`).join("\n");
  return `${path} (lines ${from}-${end} of ${lines.length}) ${permalink(b, path)}\n${body}` +
    (end < lines.length ? `\n… ${lines.length - end} more lines; call again with from=${end + 1}` : "");
}

export function search(t: Tree, b: Build, pattern: string, prefix = "") {
  let re: RegExp;
  try { re = new RegExp(pattern, "i"); } catch (e) { return `Bad regex: ${(e as Error).message}`; }
  const out: string[] = [];
  for (const [path, text] of Object.entries(t.files)) {
    if (!path.startsWith(prefix)) continue;
    text.split("\n").forEach((l, i) => {
      if (out.length < 150 && re.test(l)) out.push(`${path}:${i + 1}: ${l.trim().slice(0, 200)}`);
    });
  }
  return out.length ? `${out.length}${out.length === 150 ? "+ (truncated)" : ""} matches; permalink: ${permalink(b, "<path>", 1).replace("#L1", "#L<line>")}\n${out.join("\n")}`
    : `No matches for /${pattern}/ under '${prefix || "/"}'.`;
}

export function listing(t: Tree, prefix = "") {
  const rows = Object.entries(t.files).filter(([p]) => p.startsWith(prefix))
    .map(([p, s]) => `${p}  (${s.split("\n").length} lines)`);
  const big = t.skipped.filter((s) => s.path.startsWith(prefix)).map((s) => `${s.path}  (${s.size} bytes, not readable)`);
  return [...rows, ...big].sort().join("\n") || `No files under '${prefix}'.`;
}

// A check job's log, reduced to what a reviewer reads: status lines and the findings around them.
export async function checkLog(bucket: R2Bucket, job: number, token: string): Promise<string> {
  return cached(bucket, `logs/${job}.txt`, async () => {
    const r = await fetch(`https://api.github.com/repos/r-universe/biocstaging/actions/jobs/${job}/logs`,
      { headers: { ...UA, Accept: "application/vnd.github+json", Authorization: `Bearer ${token}` } });
    if (!r.ok) throw new Error(`log ${r.status}`);
    return trimLog(await r.text());
  });
}

export function trimLog(raw: string): string {
  const lines = raw.split("\n").map((l) =>
    l.replace(/^\d{4}-\d\d-\d\dT[\d:.]+Z ?/, "").replace(/\x1b\[[0-9;]*m/g, "").trimEnd());
  const hit = /\b(ERROR|WARNING|NOTE)\b|^\* checking .*\.\.\. (?!OK)|^##\[error\]|ERRORS? \| /;
  const keep = new Set<number>();
  lines.forEach((l, i) => {
    if (hit.test(l) && !/^_R_CHECK|Suppress/.test(l)) for (let k = i; k < Math.min(i + 8, lines.length); k++) keep.add(k);
  });
  const out: string[] = [];
  let prev = -2;
  for (const i of [...keep].sort((a, b) => a - b)) {
    if (i !== prev + 1) out.push("…");
    out.push(lines[i]);
    prev = i;
  }
  const s = out.join("\n");
  return s.length > 40000 ? s.slice(0, 40000) + "\n… (truncated)" : s || lines.slice(-60).join("\n");
}
