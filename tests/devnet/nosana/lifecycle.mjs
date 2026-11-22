// Sol.College Nosana lab: devnet job lifecycle with success, failure-diagnosis, recovery and rejection cases. Usage: DEVNET_RPC=... node lifecycle.mjs
import fs from 'fs';
import assert from 'assert';
import { address } from '@solana/kit';
import { Connection, PublicKey } from '@solana/web3.js';
import { getAssociatedTokenAddressSync } from '@solana/spl-token';
import { LAB, RPC, KEYS, signer, labClient, loadState, storePut, storeGet } from './lab.mjs';
import { execute, diagnose } from './worker.mjs';
const log = (o) => console.log(JSON.stringify({ t: new Date().toISOString(), ...o }));
const S = loadState(); assert(S.market, 'run init.mjs first'); const market = address(S.market);
const conn = new Connection(RPC, 'confirmed');
const clientS = await signer('nosana-client'), nodeS = await signer('nosana-node-a'), outS = await signer('nosana-outsider');
const C = labClient(clientS), N = labClient(nodeS), O = labClient(outS);
const send = async (step, kit, ixs) => { const sig = await kit.solana.buildSignAndSend(ixs); log({ step, ok: true, sig }); return sig; };
async function mustFail(step, p, expect) {
  try { const sig = await p; log({ step, unexpected_success: sig }); throw new Error('NEGATIVE CASE SUCCEEDED: ' + step); }
  catch (e) { if (String(e.message).startsWith('NEGATIVE')) throw e; const t = JSON.stringify({ m: e.message, logs: e.details?.context?.logs, code: e.details?.cause?.context }, (k, v) => typeof v === 'bigint' ? String(v) : v).slice(0, 4000);
    const hit = expect.find((x) => t.includes(x)); if (!hit) { log({ step, rejected: true, unexpected_error: t.slice(0, 700) }); throw new Error(step + ': wrong error'); } log({ step, rejected: true, error: hit }); }
}
const nosBal = async (owner) => { try { return BigInt((await conn.getTokenAccountBalance(getAssociatedTokenAddressSync(new PublicKey(LAB.nos), new PublicKey(owner)))).value.amount); } catch { return 0n; } };
const jobOf = (ix) => ix.accounts[0].address;
import crypto from 'crypto';
import { AccountRole } from '@solana/kit';
// `recover` exists in the program (refund a quit job's deposit to its poster) but not in @nosana/kit 2.24.5 or its generated
// client, so the lab builds it from the Anchor discriminator. See the improvement backlog.
async function recoverIx(job) {
  const j = await C.jobs.get(job, false); const m = await C.jobs.market(address(String(j.market)));
  const data = crypto.createHash('sha256').update('global:recover').digest().subarray(0, 8);
  return { programAddress: address(LAB.jobs), data: new Uint8Array(data), accounts: [
    { address: job, role: AccountRole.WRITABLE }, { address: address(String(j.market)), role: AccountRole.READONLY },
    { address: address(String(m.vault)), role: AccountRole.WRITABLE }, { address: await C.nos.getATA(clientS.address), role: AccountRole.WRITABLE },
    { address: address(String(j.payer)), role: AccountRole.WRITABLE }, { address: clientS.address, role: AccountRole.READONLY_SIGNER, signer: clientS },
    { address: address('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'), role: AccountRole.READONLY } ] };
}
async function post(defFile, label) {
  const def = JSON.parse(fs.readFileSync(defFile)); const cid = storePut(def);
  const ix = await C.jobs.list({ market, timeout: 600, ipfsHash: cid }); const job = jobOf(ix);
  await send(`list job "${label}" (definition ${cid})`, C, ix); return { job, cid };
}
async function claim(label, expectJob) {
  const ix = await N.jobs.work({ market }); const run = ix.accounts[0].address;
  await send(`work: practice node claims ${label}`, N, ix);
  const r = await N.jobs.run(run); if (expectJob) assert.equal(String(r.job), String(expectJob), 'claimed run must point at the expected job'); return run;
}
async function runAndFinish(job, run, label) {
  const j = await N.jobs.get(job); assert.equal(String(j.state), '1', 'job should be RUNNING'); assert.equal(String(j.node), nodeS.address);
  const { result, resultCid } = execute({ jobCid: j.ipfsJob, job: String(job), run: String(run), node: nodeS.address, walletFile: `${KEYS}/nosana-node-a.json` });
  log({ step: `executor ran ${label}`, status: result.state.status, resultCid, diagnosis: diagnose(result) });
  return { result, resultCid };
}

// --- 0. reset: the client delists any job still queued on the lab market (deposit refunded)
{ const m0 = await C.jobs.market(market);
  if (m0.queueType === 0) for (const qj of m0.queue || []) await send(`delist leftover queued job ${qj}`, C, await C.jobs.delist({ job: address(String(qj)) }));
  if (m0.queueType === 1 && (m0.queue || []).map(String).includes(nodeS.address)) await send('stop: node leaves the node queue', N, await N.jobs.stop({ market }));
  for (const sj of (await C.jobs.all({ state: 3, market })).filter((x) => String(x.project) === clientS.address)) await send(`recover deposit of leftover stopped job ${sj.address}`, C, await recoverIx(sj.address)); }

// --- A. happy path: deterministic container job, paid in practice NOS
const nodeBefore = await nosBal(nodeS.address), clientBefore = await nosBal(clientS.address);
const A = await post('../jobs/deterministic-sha256.json', 'deterministic sha256');
await mustFail('work by a wallet with no stake account is rejected', O.solana.buildSignAndSend(await O.jobs.work({ market })), ['AccountNotInitialized'] /* stake account */);
const runA = await claim('the deterministic job', A.job);
const ra = await runAndFinish(A.job, runA, 'deterministic job');
assert.equal(ra.result.state.status, 'success');
const digest = ra.result.state.opStates[0].results?.digest?.[0];
assert.equal(digest, 'digest=31eef93a35273a25a7dc165fbd7db8f6f5f58849035cad53996fbd59bdd4022a', 'deterministic output must match the fixture');
await mustFail('finish by a wallet that is not the assigned node is rejected', O.solana.buildSignAndSend(await O.jobs.finish({ job: A.job, ipfsResultsHash: ra.resultCid }).catch((e) => { throw e; })), ['Unauthorized', 'ConstraintHasOne', 'ConstraintSeeds', 'ConstraintRaw', 'InvalidAccount', 'no run', 'Run not found']);
await send('finish: node posts the result CID ' + ra.resultCid, N, await N.jobs.finish({ job: A.job, ipfsResultsHash: ra.resultCid }));
const jA = await C.jobs.get(A.job); log({ step: 'client reads job A', state: jA.state, ipfsResult: jA.ipfsResult, price: String(jA.price), timeStart: String(jA.timeStart), timeEnd: String(jA.timeEnd) });
assert.equal(String(jA.state), '2'); assert.equal(jA.ipfsResult, ra.resultCid);
const fetched = JSON.parse(storeGet(jA.ipfsResult).toString()); assert.equal(fetched.state.opStates[0].results.digest[0], digest);
await mustFail('finish a completed job again is rejected (kit guard: the run account was closed by finish)', (async () => N.solana.buildSignAndSend(await N.jobs.finish({ job: A.job, ipfsResultsHash: ra.resultCid })))(), ['No job run account found']);
{ // and on-chain: replay finish against the closed run account with the generated client
  const jobsClient = await import('@nosana/jobs-program'); const st = { rewardsProgram: address(LAB.rewards) };
  const deposit = await C.nos.getATA(clientS.address); const user = await N.nos.getATA(nodeS.address);
  const ixs = jobsClient.getFinishInstruction({ job: A.job, run: runA, market, vault: (await C.jobs.market(market)).vault, deposit, user, payerJob: clientS.address, payerRun: nodeS.address, authority: nodeS, ipfsResult: (await import('@nosana/ipfs')).ipfsHashToSolBytesArray(ra.resultCid) }, { programAddress: address(LAB.jobs) });
  await mustFail('finish replayed on-chain against the closed run account is rejected', N.solana.buildSignAndSend(ixs), ['AccountNotInitialized', 'AccountOwnedByWrongProgram', 'JobInWrongState']);
}
const nodeAfter = await nosBal(nodeS.address), clientAfter = await nosBal(clientS.address);
log({ step: 'practice NOS balances after job A', node_delta: String(nodeAfter - nodeBefore), client_delta: String(clientAfter - clientBefore) });

// --- B. failure diagnosis: the container exits 3
const B = await post('../jobs/failing-exit3.json', 'fails on purpose');
const runB = await claim('the failing job', B.job);
const rb = await runAndFinish(B.job, runB, 'failing job');
assert.equal(rb.result.state.status, 'failed'); const dB = diagnose(rb.result);
assert.equal(dB[0].kind, 'execution failure'); assert.equal(dB[0].exitCode, 3);
await send('finish: node posts the failed result CID ' + rb.resultCid, N, await N.jobs.finish({ job: B.job, ipfsResultsHash: rb.resultCid }));
const jB = await C.jobs.get(B.job); const rB = JSON.parse(storeGet(jB.ipfsResult).toString());
log({ step: 'client diagnoses job B from its on-chain result CID', state: jB.state, ipfsResult: jB.ipfsResult, diagnosis: diagnose(rB) });

// --- C. recovery: node quits a claimed job (job -> STOPPED), the client recovers the deposit, re-lists, and the node finishes it
const Cj = await post('../jobs/deterministic-sha256.json', 'deterministic sha256 (recovery)');
const runC1 = await claim('the recovery job', Cj.job);
await send('quit: node gives the job back before running it', N, await N.jobs.quit({ run: runC1 }));
const jC1 = await C.jobs.get(Cj.job, false); log({ step: 'job after quit', state: jC1.state }); assert.equal(String(jC1.state), '3');
await mustFail('recover by a wallet that did not post the job is rejected', (async () => { const ix = await recoverIx(Cj.job); ix.accounts[5] = { address: outS.address, role: AccountRole.READONLY_SIGNER, signer: outS }; ix.accounts[3] = { address: await O.nos.getATA(outS.address), role: AccountRole.WRITABLE }; return O.solana.buildSignAndSend(ix); })(), ['Unauthorized']);
const cBeforeRecover = await nosBal(clientS.address);
await send('recover: client takes back the stopped job deposit', C, await recoverIx(Cj.job));
log({ step: 'deposit refunded to client', delta: String((await nosBal(clientS.address)) - cBeforeRecover) });
const Cj2 = await post('../jobs/deterministic-sha256.json', 'deterministic sha256 (re-listed)');
const runC2 = await claim('the re-listed job', Cj2.job);
const rc = await runAndFinish(Cj2.job, runC2, 're-listed job'); assert.equal(rc.result.state.status, 'success');
await send('finish: re-listed job', N, await N.jobs.finish({ job: Cj2.job, ipfsResultsHash: rc.resultCid }));
assert.equal(String((await C.jobs.get(Cj2.job)).state), '2');

const m = await C.jobs.market(market); log({ step: 'market after run', queueType: m.queueType, queueLength: (m.queue || []).length });
S.lastRun = { A: A.job, B: B.job, C: Cj2.job, at: new Date().toISOString() }; fs.writeFileSync(new URL('./lab-state.json', import.meta.url), JSON.stringify(S, null, 2));
log({ step: 'DONE' }); process.exit(0);
