import { expect, test } from "bun:test";
import { readFile, search, trimLog, untar } from "./sources";

// Build a tiny ustar archive in memory: one text file, one binary, one long name.
function tar(entries: Array<[string, Uint8Array | string, string?]>) {
  const enc = new TextEncoder();
  const blocks: Uint8Array[] = [];
  const header = (name: string, size: number, type: string) => {
    const h = new Uint8Array(512);
    h.set(enc.encode(name.slice(0, 99)), 0);
    h.set(enc.encode(size.toString(8).padStart(11, "0")), 124);
    h[156] = type.charCodeAt(0);
    return h;
  };
  const pad = (b: Uint8Array) => { const p = new Uint8Array(Math.ceil(b.length / 512) * 512); p.set(b); return p; };
  for (const [name, data, type = "0"] of entries) {
    const b = typeof data === "string" ? enc.encode(data) : data;
    blocks.push(header(name, b.length, type), pad(b));
  }
  blocks.push(new Uint8Array(1024));
  return new Uint8Array(blocks.flatMap((b) => [...b]));
}

const b = { pkg: "p", version: "0.99.1", staging: "BiocStaging/p", link: "me/p", sha: "abc", jobs: [], bioccheck: null };

test("untar keeps text, skips binary, handles GNU long names and strips the prefix", () => {
  const long = "p-abc/" + "d/".repeat(60) + "x.R";
  const t = untar(tar([["p-abc/R/a.R", "f <- function(x) {\n  sapply(x, g)\n}\n"],
    ["p-abc/data/x.rda", new Uint8Array([1, 0, 2])], ["././@LongLink", long, "L"], [long.slice(0, 99), "y <- 1"]]));
  expect(Object.keys(t.files).sort()).toEqual(["R/a.R", "d/".repeat(60) + "x.R"]);
  expect(t.skipped).toEqual([{ path: "data/x.rda", size: 3 }]);
  expect(readFile(t, b, "R/a.R")).toContain("https://github.com/me/p/blob/abc/R/a.R");
  expect(readFile(t, b, "R/a.R", 2, 2)).toContain("2|   sapply(x, g)");
  expect(search(t, b, "sapply")).toContain("R/a.R:2:");
  expect(readFile(t, b, "constructor")).toBe("constructor: no such file.");
  expect(readFile(t, b, "__proto__")).toBe("__proto__: no such file.");
});

test("trimLog keeps findings, drops timestamps, ANSI and noise", () => {
  const raw = ["2026-11-06T11:02:27.96Z setup", "2026-11-06T11:02:27.96Z _R_CHECK_FOO_NOTE_=true",
    "2026-11-06T11:04:03.40Z \x1b[34mNOTE: Avoid sapply(); use vapply()\x1b[39m", "2026-11-06T11:04:03.40Z   R/a.R line 2"].join("\n");
  const t = trimLog(raw);
  expect(t).toContain("NOTE: Avoid sapply(); use vapply()");
  expect(t).toContain("R/a.R line 2");
  expect(t).not.toContain("_R_CHECK");
  expect(t).not.toContain("2026-11-06");
});
