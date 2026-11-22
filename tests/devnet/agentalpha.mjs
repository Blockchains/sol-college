import fs from 'fs';
import crypto from 'crypto';
import { Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import { payer, conn, log, program, fund, expectFail, sendIx, BN } from './lib/labcommon.mjs';
const idl = JSON.parse(fs.readFileSync(new URL('../../dapps/static/agentalpha/idl.json', import.meta.url), 'utf8'));
const pid = new PublicKey(idl.address);
const prog = program(idl);
const pda = (...s) => PublicKey.findProgramAddressSync(s.map(x => typeof x === 'string' ? Buffer.from(x) : x), pid)[0];
const H = (s) => [...crypto.createHash('sha256').update(s).digest()];
const provider = pda('provider', payer.publicKey.toBuffer());
const stranger = Keypair.generate();
await fund(stranger.publicKey, 20_000_000);
try {
  const ps = program(idl, stranger);
  log({ step: 'setup', program: pid.toBase58(), provider: provider.toBase58(), authority: payer.publicKey.toBase58() });
  await expectFail('register_name_too_long', () => prog.methods.registerProvider('n'.repeat(65), 'https://lab', Buffer.from([1]), new BN(0)).accountsPartial({ provider, authority: payer.publicKey }).rpc());
  let sig = await prog.methods.registerProvider('sol.college lab signal agent', 'https://sol.college/dapps/agentalpha/', Buffer.from([1, 2]), new BN(1000)).accountsPartial({ provider, authority: payer.publicKey }).rpc();
  log({ step: 'register_provider', ok: true, sig });
  sig = await prog.methods.updateProvider(null, null, new BN(5000)).accountsPartial({ provider, authority: payer.publicKey }).rpc();
  log({ step: 'update_provider', ok: true, sig, price_lamports: (await prog.account.provider.fetch(provider)).priceLamports.toString() });
  const sProv = pda('provider', stranger.publicKey.toBuffer());
  await expectFail('update_by_stranger', () => ps.methods.updateProvider('pwn', null, null).accountsPartial({ provider, authority: stranger.publicKey }).signers([stranger]).rpc());
  const sigs = [['SOL', 0, 15000, 16500, 14200, 24, 70], ['JUP', 1, 90, 75, 98, 12, 55]];
  const commits = [];
  for (const s of sigs) {
    const str = s.join(':'); const h = H(str); const c = pda('signal', provider.toBuffer(), Buffer.from(h));
    sig = await prog.methods.commitSignal(h).accountsPartial({ signalCommit: c, provider, authority: payer.publicKey }).rpc();
    log({ step: `commit_signal_${s[0]}`, ok: true, sig, preimage: str, hash: Buffer.from(h).toString('hex'), signal_commit: c.toBase58() });
    commits.push([s, c]);
  }
  const [s0, c0] = commits[0];
  await expectFail('record_before_reveal', () => prog.methods.recordOutcome(1, new BN(16500), 1000).accountsPartial({ signalCommit: c0, provider, oracle: payer.publicKey }).rpc());
  await expectFail('reveal_hash_mismatch', () => prog.methods.revealSignal('SOL', 0, new BN(15000), new BN(17000), new BN(14200), 24, 70).accountsPartial({ signalCommit: c0, provider, authority: payer.publicKey }).rpc());
  await expectFail('reveal_by_stranger', () => ps.methods.revealSignal(...[s0[0], s0[1], new BN(s0[2]), new BN(s0[3]), new BN(s0[4]), s0[5], s0[6]]).accountsPartial({ signalCommit: c0, provider: sProv, authority: stranger.publicKey }).signers([stranger]).rpc());
  for (const [s, c] of commits) {
    sig = await prog.methods.revealSignal(s[0], s[1], new BN(s[2]), new BN(s[3]), new BN(s[4]), s[5], s[6]).accountsPartial({ signalCommit: c, provider, authority: payer.publicKey }).rpc();
    log({ step: `reveal_signal_${s[0]}`, ok: true, sig });
  }
  await expectFail('reveal_twice', () => prog.methods.revealSignal(s0[0], s0[1], new BN(s0[2]), new BN(s0[3]), new BN(s0[4]), s0[5], s0[6]).accountsPartial({ signalCommit: c0, provider, authority: payer.publicKey }).rpc());
  await expectFail('record_invalid_outcome', () => prog.methods.recordOutcome(4, new BN(1), 0).accountsPartial({ signalCommit: c0, provider, oracle: payer.publicKey }).rpc());
  sig = await prog.methods.recordOutcome(1, new BN(16520), 1013).accountsPartial({ signalCommit: c0, provider, oracle: payer.publicKey }).rpc();
  let p = await prog.account.provider.fetch(provider);
  log({ step: 'record_outcome_tp_hit', ok: true, sig, total_signals: p.totalSignals.toString(), correct_signals: p.correctSignals.toString(), total_return_bps: p.totalReturnBps.toString() });
  await expectFail('record_twice', () => prog.methods.recordOutcome(2, new BN(1), -100).accountsPartial({ signalCommit: c0, provider, oracle: payer.publicKey }).rpc());
  // Upstream flaw: `oracle` is any Signer — a random stranger can write the outcome
  const c1 = commits[1][1];
  sig = await ps.methods.recordOutcome(2, new BN(98), -888).accountsPartial({ signalCommit: c1, provider, oracle: stranger.publicKey }).signers([stranger]).rpc();
  p = await prog.account.provider.fetch(provider);
  log({ step: 'flaw_stranger_records_outcome', ok: true, sig, note: 'UPSTREAM FLAW: record_outcome accepts any signer as oracle; a stranger wrote SL_HIT -888 bps into the provider reputation', total_signals: p.totalSignals.toString(), correct_signals: p.correctSignals.toString(), total_return_bps: p.totalReturnBps.toString() });
} finally {
  const l = await conn.getBalance(stranger.publicKey); if (l > 0) await sendIx([SystemProgram.transfer({ fromPubkey: stranger.publicKey, toPubkey: payer.publicKey, lamports: l })], [payer, stranger]);
  log({ step: 'cleanup_returned_lab_wallets' });
}
process.exit(0);
