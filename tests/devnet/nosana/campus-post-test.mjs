// Script-side check of the browser market: post a template job (with the memo the browser app sends), wait for the campus
// worker, and verify the result memo hashes to the on-chain ipfsResult. Usage: node campus-post-test.mjs <template> [text]
import { address } from '@solana/kit';
import { Connection } from '@solana/web3.js';
import { signer, labClient, loadState, cidV0, RPC } from './lab.mjs';
import { definitionBytes, memoFor } from './campus-templates.mjs';
const [tpl = 'hash-text', text = 'hello from sol.college'] = process.argv.slice(2);
const log = (o) => console.log(JSON.stringify({ t: new Date().toISOString(), ...o }));
const S = loadState(); const C = labClient(await signer(process.env.POSTER || 'nosana-client')); const conn = new Connection(RPC, 'confirmed');
const params = { text }; const cid = cidV0(Buffer.from(definitionBytes(tpl, params)));
const ix = await C.jobs.list({ market: address(S.campusMarket), timeout: 300, ipfsHash: cid }); const job = ix.accounts[0].address;
const memo = { programAddress: address('MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr'), accounts: [], data: new TextEncoder().encode(memoFor(tpl, params)) };
log({ step: 'list', tpl, cid, job, sig: await C.solana.buildSignAndSend([ix, memo]) });
for (let i = 0; i < 60; i++) {
  const j = await C.jobs.get(job, false);
  if (String(j.state) === '2') {
    const sigs = await conn.getSignaturesForAddress(job.toString ? new (await import('@solana/web3.js')).PublicKey(String(job)) : job);
    const fin = sigs.find((s) => s.memo && s.memo.includes('nosana-result'));
    const body = fin.memo.replace(/^\[\d+\] /, ''); const ok = cidV0(Buffer.from(body)) === j.ipfsResult;
    log({ step: 'completed', ipfsResult: j.ipfsResult, memoVerified: ok, result: JSON.parse(body), finishSig: fin.signature }); process.exit(ok ? 0 : 1);
  }
  await new Promise((r) => setTimeout(r, 3000));
}
log({ step: 'TIMEOUT' }); process.exit(1);
