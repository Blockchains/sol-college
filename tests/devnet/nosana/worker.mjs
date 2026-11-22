// Sol.College campus worker: claims a job from the lab market, resolves its definition from the lab content store (hash-verified),
// executes it with the official Nosana executor (`@nosana/node run`, podman), stores the result and posts its CID with `finish`.
import { execFileSync } from 'child_process';
import fs from 'fs';
import { storeGet, storePut } from './lab.mjs';
export const NODE_REPO = process.env.NOSANA_NODE_REPO || '/workspace/sol-college/portfolio/src/nosana-ci_nosana-node';
export const PODMAN_SOCK = process.env.PODMAN_SOCK || '/tmp/lab-podman/podman.sock';
export function execute({ jobCid, job, run, node, walletFile }) {
  const def = JSON.parse(storeGet(jobCid).toString());
  const cfg = `/tmp/nosana-lab-cfg/${job}-${run}/`; fs.rmSync(cfg, { recursive: true, force: true }); fs.mkdirSync(cfg, { recursive: true });
  const defFile = `${cfg}job.json`; fs.writeFileSync(defFile, JSON.stringify(def));
  let execError = null;
  try {
    execFileSync('node', ['dist/src/index.js', 'run', defFile, '--podman', PODMAN_SOCK, '-w', walletFile, '-c', cfg], { cwd: NODE_REPO, env: { ...process.env, APP_ENV: 'development' }, stdio: ['ignore', 'pipe', 'pipe'], timeout: 300000 });
  } catch (e) { execError = String(e.message).slice(0, 400); }
  let flow = null;
  try { const db = JSON.parse(fs.readFileSync(`${cfg}nosana_db.json`)); flow = Object.values(db.flows || {})[0] || null; } catch {}
  const state = flow?.state ?? { status: 'monitoring-failed', note: 'executor produced no flow state', execError };
  const result = { schema: 'sol-college/nosana-lab-result@1', job, run, node, jobDefinitionCid: jobCid, executor: '@nosana/node run (nosana-ci/nosana-node 3f07617)', state };
  return { result, resultCid: storePut(result) };
}
export function diagnose(result) {
  const st = result.state || {};
  if (st.status === 'monitoring-failed') return { kind: 'monitoring failure', detail: st.note };
  const bad = (st.opStates || []).filter((o) => o.status !== 'success');
  if (!bad.length) return { kind: 'success', detail: `${(st.opStates || []).length} op(s) succeeded` };
  return bad.map((o) => {
    const r = o.diagnostics?.reason || {};
    const flagged = Object.entries(r).filter(([, v]) => v).map(([k]) => k);
    const stderr = (o.logs || []).filter((l) => l.type === 'stderr').map((l) => l.log.trim());
    return flagged.length ? { kind: 'host/monitoring failure', op: o.operationId, reasons: flagged }
      : { kind: 'execution failure', op: o.operationId, exitCode: o.exitCode, oomKilled: !!o.diagnostics?.state?.OOMKilled, stderr };
  });
}
