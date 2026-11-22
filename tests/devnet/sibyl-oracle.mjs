import fs from 'fs';
import { Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import { payer, conn, log, program, fund, expectFail, sendIx, BN } from './lib/labcommon.mjs';
const idl = JSON.parse(fs.readFileSync(new URL('../../dapps/static/sibyl-oracle/idl.json', import.meta.url), 'utf8'));
const pid = new PublicKey(idl.address);
const prog = program(idl);
const pda = (...s) => PublicKey.findProgramAddressSync(s.map(x => typeof x === 'string' ? Buffer.from(x) : x), pid)[0];
const le = (n) => new BN(n).toArrayLike(Buffer, 'le', 8);
const PHASE = process.env.PHASE || '1';
const oracle = pda('oracle');
const stranger = Keypair.generate();
await fund(stranger.publicKey, 3_000_000);
try {
const ps = program(idl, stranger);
if (PHASE === '1') {
  log({ step: 'setup', program: pid.toBase58(), oracle: oracle.toBase58(), authority: payer.publicKey.toBase58() });
  let sig;
  if (!(await conn.getAccountInfo(oracle))) { sig = await prog.methods.initialize().accountsPartial({ oracle, authority: payer.publicKey }).rpc(); log({ step: 'initialize', ok: true, sig }); }
  const next = async () => (await prog.account.oracle.fetch(oracle)).predictionCount.toNumber() + 1;
  await expectFail('create_confidence_over_100', async () => prog.methods.createPrediction('x', 101, 1).accountsPartial({ oracle, prediction: pda('prediction', le(await next())), authority: payer.publicKey }).rpc());
  await expectFail('create_zero_deadline', async () => prog.methods.createPrediction('x', 50, 0).accountsPartial({ oracle, prediction: pda('prediction', le(await next())), authority: payer.publicKey }).rpc());
  await expectFail('create_by_stranger', async () => ps.methods.createPrediction('x', 50, 1).accountsPartial({ oracle, prediction: pda('prediction', le(await next())), authority: stranger.publicKey }).signers([stranger]).rpc());
  for (const [t, c] of [['SOL closes above $150 on devnet lab day +1h (lab statement)', 72], ['Devnet slot height passes 600M within the hour (lab statement)', 35]]) {
    const n = await next(); const p = pda('prediction', le(n));
    sig = await prog.methods.createPrediction(t, c, 1).accountsPartial({ oracle, prediction: p, authority: payer.publicKey }).rpc();
    const a = await prog.account.prediction.fetch(p);
    log({ step: `create_prediction_${n}`, ok: true, sig, id: n, prediction: p.toBase58(), confidence: c, deadline: a.deadline.toNumber() });
  }
  const n = (await prog.account.oracle.fetch(oracle)).predictionCount.toNumber();
  await expectFail('resolve_before_deadline', () => prog.methods.resolvePrediction(new BN(n), true).accountsPartial({ oracle, prediction: pda('prediction', le(n)), authority: payer.publicKey }).rpc());
  await expectFail('transfer_authority_by_stranger', () => ps.methods.transferAuthority(stranger.publicKey).accountsPartial({ oracle, authority: stranger.publicKey }).signers([stranger]).rpc());
} else {
  const st = await prog.account.oracle.fetch(oracle); const n = st.predictionCount.toNumber();
  const ids = [n - 1, n];
  await expectFail('resolve_by_stranger', () => ps.methods.resolvePrediction(new BN(ids[0]), true).accountsPartial({ oracle, prediction: pda('prediction', le(ids[0])), authority: stranger.publicKey }).signers([stranger]).rpc());
  await expectFail('resolve_id_mismatch', () => prog.methods.resolvePrediction(new BN(ids[0]), true).accountsPartial({ oracle, prediction: pda('prediction', le(ids[1])), authority: payer.publicKey }).rpc());
  for (const [id, ok] of [[ids[0], true], [ids[1], false]]) {
    const sig = await prog.methods.resolvePrediction(new BN(id), ok).accountsPartial({ oracle, prediction: pda('prediction', le(id)), authority: payer.publicKey }).rpc();
    const o = await prog.account.oracle.fetch(oracle);
    log({ step: `resolve_prediction_${id}`, ok: true, sig, was_correct: ok, prediction_count: o.predictionCount.toString(), correct_predictions: o.correctPredictions.toString() });
  }
  await expectFail('resolve_twice', () => prog.methods.resolvePrediction(new BN(ids[0]), true).accountsPartial({ oracle, prediction: pda('prediction', le(ids[0])), authority: payer.publicKey }).rpc());
  const nk = Keypair.generate();
  let sig = await prog.methods.transferAuthority(nk.publicKey).accountsPartial({ oracle, authority: payer.publicKey }).rpc();
  log({ step: 'transfer_authority', ok: true, sig, new_authority: nk.publicKey.toBase58() });
  await fund(nk.publicKey, 2_000_000);
  sig = await program(idl, nk).methods.transferAuthority(payer.publicKey).accountsPartial({ oracle, authority: nk.publicKey }).signers([nk]).rpc();
  log({ step: 'transfer_authority_back', ok: true, sig });
  const l = await conn.getBalance(nk.publicKey); await sendIx([SystemProgram.transfer({ fromPubkey: nk.publicKey, toPubkey: payer.publicKey, lamports: l })], [payer, nk]);
}
} finally {
  const l = await conn.getBalance(stranger.publicKey); if (l > 0) await sendIx([SystemProgram.transfer({ fromPubkey: stranger.publicKey, toPubkey: payer.publicKey, lamports: l })], [payer, stranger]);
  log({ step: `cleanup_returned_lab_wallets_phase_${PHASE}` });
}
process.exit(0);
