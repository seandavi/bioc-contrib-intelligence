// Sessions and access. A session is the GitHub user, their token and whether
// they're an admin, AES-GCM sealed into a cookie: no session store. The token
// stays server-side (HttpOnly cookie, never sent to the UI) and is what write
// actions use, so GitHub enforces permissions and actions show under their name.

export type User = { login: string; token: string; admin: boolean; exp: number };
export type Data = {
  repo: string;
  generated_at: string;
  queue: Array<{ issue_number: number; reviewer: string } & Record<string, unknown>>;
  unassigned: Array<{ issue_number: number } & Record<string, unknown>>;
  issues: Record<string, unknown>;
};

const enc = new TextEncoder();

async function key(secret: string) {
  const raw = await crypto.subtle.digest("SHA-256", enc.encode(secret));
  return crypto.subtle.importKey("raw", raw, "AES-GCM", false, ["encrypt", "decrypt"]);
}

const b64 = (b: Uint8Array) =>
  btoa(String.fromCharCode(...b)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const unb64 = (s: string) =>
  Uint8Array.from(atob(s.replace(/-/g, "+").replace(/_/g, "/")), (c) => c.charCodeAt(0));

export async function seal(user: User, secret: string): Promise<string> {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ct = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, await key(secret),
    enc.encode(JSON.stringify(user)));
  return b64(iv) + "." + b64(new Uint8Array(ct));
}

export async function unseal(sealed: string, secret: string): Promise<User | null> {
  try {
    const [iv, ct] = sealed.split(".").map(unb64);
    const pt = await crypto.subtle.decrypt({ name: "AES-GCM", iv }, await key(secret), ct);
    const user = JSON.parse(new TextDecoder().decode(pt)) as User;
    return user.exp > Date.now() ? user : null;
  } catch {
    return null; // tampered, wrong secret or malformed
  }
}

export async function gh(path: string, token: string, init: RequestInit = {}) {
  return fetch(`https://api.github.com${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "bioc-reviews",
      ...init.headers,
    },
  });
}

// Who the token belongs to, and whether they can triage the tracker (= admin, #12).
export async function resolveUser(token: string, repo: string): Promise<User | null> {
  const me = await gh("/user", token);
  if (!me.ok) return null;
  const { login } = (await me.json()) as { login: string };
  const r = await gh(`/repos/${repo}`, token);
  const perms = r.ok ? ((await r.json()) as { permissions?: { triage?: boolean } }).permissions : undefined;
  return { login, token, admin: !!perms?.triage, exp: Date.now() + 7 * 864e5 };
}

// Viewers: admins, and anyone assigned to an open review (decision default, #12).
export const allowed = (data: Data, u: User) =>
  u.admin || data.queue.some((r) => r.reviewer.toLowerCase() === u.login.toLowerCase());

// Non-admins see only their own assignments.
export function scope(data: Data, u: User): Data {
  if (u.admin) return data;
  const me = u.login.toLowerCase();
  const queue = data.queue.filter((r) => r.reviewer.toLowerCase() === me);
  const mine = new Set(queue.map((r) => String(r.issue_number)));
  const issues = Object.fromEntries(Object.entries(data.issues).filter(([n]) => mine.has(n)));
  return { ...data, queue, unassigned: [], issues };
}

export const canSeeIssue = (data: Data, u: User, n: number) =>
  u.admin || scope(data, u).queue.some((r) => r.issue_number === n);
