import { mkdirSync, readFileSync, writeFileSync, existsSync, openSync, closeSync, unlinkSync, renameSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { canonicalJson } from "./canonical.ts";

export interface Versioned<T> {
  version: number;
  data: T;
}

export class ConflictError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ConflictError";
  }
}

export class ImmutableRecordError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ImmutableRecordError";
  }
}

const KEY_RE = /^[a-z0-9][a-z0-9._-]*(\/[a-z0-9][a-z0-9._-]*)*$/;

/**
 * File-backed record store with optimistic concurrency (version check) and an exclusive lock
 * file per key so concurrent local processes serialise state transitions. This is the
 * persistence used for private task/provisioning records (outside the public repo) and for
 * immutable public records. It is not a distributed lock: GitHub Actions jobs must also use a
 * workflow `concurrency` group per project (see docs/operations.md).
 */
export class FileStore {
  readonly root: string;
  constructor(root: string) {
    this.root = resolve(root);
    mkdirSync(this.root, { recursive: true });
  }

  private path(key: string): string {
    if (!KEY_RE.test(key)) throw new Error(`invalid store key: ${key}`);
    return join(this.root, `${key}.json`);
  }

  read<T>(key: string): Versioned<T> | undefined {
    const p = this.path(key);
    if (!existsSync(p)) return undefined;
    return JSON.parse(readFileSync(p, "utf8")) as Versioned<T>;
  }

  /** Conditional write: expectedVersion 0 means "must not exist yet". */
  write<T>(key: string, data: T, expectedVersion: number): Versioned<T> {
    return this.withLock(key, () => {
      const cur = this.read<T>(key);
      const curVersion = cur?.version ?? 0;
      if (curVersion !== expectedVersion) {
        throw new ConflictError(`version conflict on ${key}: expected ${expectedVersion}, found ${curVersion}`);
      }
      const next: Versioned<T> = { version: curVersion + 1, data };
      this.atomicWrite(this.path(key), JSON.stringify(next, null, 2) + "\n");
      return next;
    });
  }

  /** Read-modify-write under the key lock. */
  update<T>(key: string, fn: (cur: Versioned<T> | undefined) => T): Versioned<T> {
    return this.withLock(key, () => {
      const cur = this.read<T>(key);
      const data = fn(cur);
      const next: Versioned<T> = { version: (cur?.version ?? 0) + 1, data };
      this.atomicWrite(this.path(key), JSON.stringify(next, null, 2) + "\n");
      return next;
    });
  }

  withLock<R>(key: string, fn: () => R): R {
    const lock = this.path(key) + ".lock";
    mkdirSync(dirname(lock), { recursive: true });
    let fd: number;
    try {
      fd = openSync(lock, "wx");
    } catch (e) {
      const err = e as NodeJS.ErrnoException;
      if (err.code === "EEXIST") {
        const age = Date.now() - statSync(lock).mtimeMs;
        throw new ConflictError(`record ${key} is locked by another operation (lock age ${Math.round(age / 1000)}s); not overriding`);
      }
      throw e;
    }
    try {
      return fn();
    } finally {
      closeSync(fd);
      unlinkSync(lock);
    }
  }

  /** Async variant: holds the key lock across awaited side effects (e.g. one send per task). */
  async withLockAsync<R>(key: string, fn: () => Promise<R>): Promise<R> {
    const lock = this.path(key) + ".oplock";
    mkdirSync(dirname(lock), { recursive: true });
    let fd: number;
    try {
      fd = openSync(lock, "wx");
    } catch (e) {
      if ((e as NodeJS.ErrnoException).code === "EEXIST") throw new ConflictError(`operation on ${key} already in progress; not starting a second one`);
      throw e;
    }
    try {
      return await fn();
    } finally {
      closeSync(fd);
      unlinkSync(lock);
    }
  }

  private atomicWrite(p: string, content: string): void {
    mkdirSync(dirname(p), { recursive: true });
    const tmp = `${p}.${process.pid}.tmp`;
    writeFileSync(tmp, content, { mode: 0o600 });
    renameSync(tmp, p);
  }
}

/** Immutable canonical-JSON files (public adoption manifests, acceptances, credentials). */
export function writeImmutableCanonical(path: string, value: unknown): { bytes: Buffer; created: boolean } {
  const content = canonicalJson(value);
  const bytes = Buffer.from(content, "utf8");
  mkdirSync(dirname(path), { recursive: true });
  try {
    const fd = openSync(path, "wx");
    try {
      writeFileSync(fd, bytes);
    } finally {
      closeSync(fd);
    }
    return { bytes, created: true };
  } catch (e) {
    if ((e as NodeJS.ErrnoException).code !== "EEXIST") throw e;
    const existing = readFileSync(path);
    if (existing.equals(bytes)) return { bytes: existing, created: false };
    throw new ImmutableRecordError(`refusing to overwrite immutable record ${path} with different content`);
  }
}
