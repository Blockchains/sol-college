import { createHash } from "node:crypto";

/**
 * Deterministic canonical JSON: object keys sorted by UTF-16 code unit order, no insignificant
 * whitespace, UTF-8 output with a trailing newline. Rejects undefined, functions, NaN/Infinity,
 * so the exact stored bytes are reproducible and hashable.
 */
export function canonicalJson(value: unknown): string {
  return encode(value, "$") + "\n";
}

function encode(value: unknown, path: string): string {
  if (value === null) return "null";
  switch (typeof value) {
    case "string":
      return JSON.stringify(value);
    case "boolean":
      return value ? "true" : "false";
    case "number":
      if (!Number.isFinite(value)) throw new Error(`canonicalJson: non-finite number at ${path}`);
      return JSON.stringify(value);
    case "object": {
      if (Array.isArray(value)) return "[" + value.map((v, i) => encode(v, `${path}[${i}]`)).join(",") + "]";
      const obj = value as Record<string, unknown>;
      const keys = Object.keys(obj).sort();
      const parts: string[] = [];
      for (const k of keys) {
        const v = obj[k];
        if (v === undefined) throw new Error(`canonicalJson: undefined value at ${path}.${k}`);
        parts.push(JSON.stringify(k) + ":" + encode(v, `${path}.${k}`));
      }
      return "{" + parts.join(",") + "}";
    }
    default:
      throw new Error(`canonicalJson: unsupported ${typeof value} at ${path}`);
  }
}

export function canonicalBytes(value: unknown): Buffer {
  return Buffer.from(canonicalJson(value), "utf8");
}

export function sha256Hex(data: Buffer | string): string {
  return createHash("sha256").update(data).digest("hex");
}
