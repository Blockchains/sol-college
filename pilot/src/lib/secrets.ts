/**
 * Secret hygiene helpers. The Builder key is a JWT; we never print it. These helpers detect
 * accidental inclusion of the key (or any JWT-shaped token) in output that is about to be
 * published, logged, or committed.
 */
const JWT_RE = /eyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}/g;

export function findSecretLeaks(text: string, knownSecrets: readonly string[] = []): string[] {
  const hits: string[] = [];
  for (const s of knownSecrets) {
    if (s && s.length >= 16 && text.includes(s)) hits.push("known-secret");
  }
  if (JWT_RE.test(text)) hits.push("jwt-shaped-token");
  JWT_RE.lastIndex = 0;
  return hits;
}

export function assertNoSecrets(label: string, text: string, knownSecrets: readonly string[] = []): void {
  const hits = findSecretLeaks(text, knownSecrets);
  if (hits.length) throw new Error(`secret leak blocked in ${label}: ${hits.join(", ")}`);
}

export function redact(text: string, knownSecrets: readonly string[] = []): string {
  let out = text.replace(JWT_RE, "[REDACTED-JWT]");
  for (const s of knownSecrets) if (s && s.length >= 16) out = out.split(s).join("[REDACTED]");
  return out;
}

/** Short, non-reversible reference for private identifiers in logs (e.g. Mind IDs). */
export function shortRef(id: string): string {
  return id.length <= 6 ? "…" : `…${id.slice(-6)}`;
}
