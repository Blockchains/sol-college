// Negative case: a job whose definition CID is not an allow-listed template (no memo) is never executed; the worker
// finishes it with a verified "refused" result. Usage: node campus-refusal-test.mjs
import { address } from '@solana/kit';
import { Connection, PublicKey } from '@solana/web3.js';
import { signer, labClient, loadState, cidV0, RPC } from './lab.mjs';
const log = (o) => console.log(JSON.stringify({ t: new Date().toISOString(), ...o }));
const S = loadState(); const C = labClient(await signer('nosana-client')); const conn = new Connection(RPC, 'confirmed');
const rogue = JSON.stringify({ version: '0.1', type: 'container', ops: [{ type: 'container/run', id: 'x', args: { image: 'docker.io/library/alpine:3', cmd: ['sh', '-c', 'cat /etc/passwd'] } }] });
const cid = cidV0(Buffer.from(rogue));
const ix = await C.jobs.list({ market: address(S.campusMarket), timeout: 300, ipfsHash: cid }); const job = ix.accounts[0].address;
log({ step: 'list non-allow-listed definition', cid, job: String(job), sig: await C.solana.buildSignAndSend(ix) });
for (let i = 0; i < 40; i++) {
  const j = await C.jobs.get(job, false);
  if (String(j.state) === '2') { const s = (await conn.getSignaturesForAddress(new PublicKey(String(job)))).find((x) => x.memo?.includes('nosana-result'));
    const body = s.memo.replace(/^\[\d+\] /, ''); const r = JSON.parse(body); const ok = cidV0(Buffer.from(body)) === j.ipfsResult && r.status === 'refused';
    log({ step: 'refused as expected', ok, status: r.status, reason: r.reason }); process.exit(ok ? 0 : 1); }
  await new Promise((r) => setTimeout(r, 3000));
}
process.exit(1);
