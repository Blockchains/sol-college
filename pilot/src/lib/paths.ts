import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
/** Repository root (pilot/src/lib -> repo). */
export const REPO_ROOT = resolve(here, "../../..");
export const CONFIG_DIR = resolve(REPO_ROOT, "config");
export const PUBLIC_RECORDS_DIR = resolve(REPO_ROOT, "records/public");

/** Private records never live in the public repository. */
export function privateRecordsDir(): string {
  const d = process.env["SC_PRIVATE_RECORDS_DIR"];
  if (!d) throw new Error("SC_PRIVATE_RECORDS_DIR is not set (private task/provisioning records must live outside the public repo)");
  const abs = resolve(d);
  if (abs === REPO_ROOT || abs.startsWith(REPO_ROOT + "/")) {
    throw new Error("SC_PRIVATE_RECORDS_DIR points inside the public repository; refusing");
  }
  return abs;
}
