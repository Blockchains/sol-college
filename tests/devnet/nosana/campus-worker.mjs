// Sol.College Nosana campus worker daemon for the browser market. Devnet only.
// Chain side: @nosana/kit (work = join the node queue, runs, get, finish) against the lab programs.
// Execution: the official executor, `nosana-node run` (nosana-ci/nosana-node, podman), as in worker.mjs.
// It stands in for `nosana-node start`, which needs Nosana's private host-manager, FRP tunnel server and a GPU benchmark.
// Job definitions: only allow-listed templates (campus-templates.mjs). The definition is rebuilt from the template id and
// parameters in the poster's memo and must hash to the CID the job carries on-chain. Anything else is refused, never run.
// Results: a compact result JSON is written to the lab store and posted in a memo inside the same `finish` transaction; its
// CIDv0 is the on-chain ipfsResult, so the browser verifies the memo against the chain without any IPFS service.
import { execFileSync } from 'child_process';
import fs from 'fs';
import { address } from '@solana/kit';
import { Connection, PublicKey } from '@solana/web3.js';
import { RPC, KEYS, signer, labClient, loadState, storePut, cidV0 } from './lab.mjs';
import { TEMPLATES, definitionBytes, parseMemo, RESULT_SCHEMA } from './campus-templates.mjs';
import { NODE_REPO, PODMAN_SOCK } from './worker.mjs';
const MEMO = address('MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr');
const log = (o) => console.log(JSON.stringify({ t: new Date().toISOString(), ...o }));
const S = loadState(); if (!S.campusMarket) throw new Error('run campus-market.mjs first');
const market = address(S.campusMarket);
const nodeS = await signer('nosana-node-campus'); const N = labClient(nodeS); const conn = new Connection(RPC, 'confirmed');
const STATIC_CIDS = Object.fromEntries(Object.keys(TEMPLATES).filter((k) => !TEMPLATES[k].param).map((k) => [cidV0(Buffer.from(definitionBytes(k))), k]));
const done = new Set();
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function resolveDefinition(jobAddr, cid) {
  if (STATIC_CIDS[cid]) return { id: STATIC_CIDS[cid], bytes: definitionBytes(STATIC_CIDS[cid]) };
  const sigs = await conn.getSignaturesForAddress(new PublicKey(jobAddr), { limit: 20 });
  for (const s of sigs.reverse()) {
    const memo = s.memo && parseMemo(s.memo); if (!memo) continue;
    try { const bytes = definitionBytes(memo.id, memo.params); if (cidV0(Buffer.from(bytes)) === cid) return { id: memo.id, bytes, params: memo.params }; } catch (e) { return { refused: String(e.message) }; }
  }
  return { refused: 'job definition is not an allow-listed Sol.College template (no matching memo); the campus worker never runs arbitrary containers' };
}
function execute(defBytes, job, run) {
  const cfg = `/tmp/nosana-campus-cfg/${job}/`; fs.rmSync(cfg, { recursive: true, force: true }); fs.mkdirSync(cfg, { recursive: true });
  fs.writeFileSync(`${cfg}job.json`, defBytes); let execError = null;
  try { execFileSync('node', ['dist/src/index.js', 'run', `${cfg}job.json`, '--podman', PODMAN_SOCK, '-w', `${KEYS}/nosana-node-campus.json`, '-c', cfg], { cwd: NODE_REPO, env: { ...process.env, APP_ENV: 'development' }, stdio: ['ignore', 'pipe', 'pipe'], timeout: 240000 }); }
  catch (e) { execError = String(e.message).slice(0, 300); }
  let flow = null; try { flow = Object.values(JSON.parse(fs.readFileSync(`${cfg}nosana_db.json`)).flows || {})[0] || null; } catch {}
  return flow?.state ?? { status: 'monitoring-failed', execError };
}
const tail = (s, n) => (s.length > n ? '…' + s.slice(-n) : s);
function compact(base, state) {
  const op = (state.opStates || [])[0] || {};
  const pick = (t) => (op.logs || []).filter((l) => l.type === t).map((l) => l.log).join('').trim();
  const r = { ...base, status: state.status, exit: op.exitCode ?? null, results: op.results || {}, out: pick('stdout'), err: pick('stderr') };
  for (const n of [240, 160, 80, 0]) { r.out = tail(pick('stdout'), n); r.err = tail(pick('stderr'), n); const b = JSON.stringify(r); if (Buffer.byteLength(b) <= 560) return b; }
  r.results = {}; return JSON.stringify(r);
}
async function processRun(run) {
  const job = await N.jobs.get(run.job, false);
  if (String(job.market) !== String(market) || done.has(String(run.job))) return;
  const cid = job.ipfsJob; const def = await resolveDefinition(run.job, cid);
  const base = { s: RESULT_SCHEMA, job: String(run.job), tpl: def.id || null, def: cid, node: nodeS.address, executor: '@nosana/node run (nosana-node 3f07617)', at: new Date().toISOString() };
  let bytes;
  if (def.refused) { bytes = JSON.stringify({ ...base, status: 'refused', reason: def.refused.slice(0, 240) }); log({ step: 'refused job', job: String(run.job), cid }); }
  else { log({ step: 'run job', job: String(run.job), template: def.id }); bytes = compact(base, execute(def.bytes, String(run.job), String(run.address))); }
  const resultCid = storePut(bytes);
  const ixs = await N.jobs.finish({ job: run.job, ipfsResultsHash: resultCid });
  const memoIx = { programAddress: MEMO, accounts: [], data: new TextEncoder().encode(bytes) };
  const sig = await N.solana.buildSignAndSend([...(Array.isArray(ixs) ? ixs : [ixs]), memoIx]);
  done.add(String(run.job)); log({ step: 'finish', job: String(run.job), resultCid, sig, status: JSON.parse(bytes).status });
}
log({ step: 'campus worker up', node: nodeS.address, market: String(market), rpc: RPC.replace(/api-key=[^&]+/, 'api-key=***'), templates: Object.keys(TEMPLATES) });
let lastQueueLog = 0;
for (;;) {
  try {
    const runs = await N.jobs.runs({ node: nodeS.address });
    for (const r of runs) { try { await processRun(r); } catch (e) { log({ step: 'run error', job: String(r.job), error: String(e.message).slice(0, 300) }); } }
    if (!runs.length) {
      const m = await N.jobs.market(market);
      const queued = m.queueType === 1 && (m.queue || []).map(String).includes(nodeS.address);
      if (!queued) { const sig = await N.solana.buildSignAndSend(await N.jobs.work({ market })); log({ step: 'work: join queue / claim', sig }); }
      else if (Date.now() - lastQueueLog > 600000) { log({ step: 'waiting in node queue' }); lastQueueLog = Date.now(); }
    }
  } catch (e) { log({ step: 'loop error', error: String(e.message).slice(0, 300) }); await sleep(10000); }
  await sleep(3000);
}
