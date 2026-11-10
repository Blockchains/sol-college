// PulseFund (pulsefund-sol fork) on devnet: create a campaign, donate, admin-only withdraw down to the rent floor,
// and the program's rejections. Mirrors the app's calls (frontend/src/views/create, home/CampaignCard).
// Usage (from frontend/, @coral-xyz/anchor 0.29): node pulsefund-sol.mjs <idl.json> <rpc> <payer.json> [withdraw-own <keypair.json>]
// The payer funds two fresh keys (A = campaign admin, B = donor) and gets the unspent SOL back at the end.
// "withdraw-own" instead withdraws a keypair's own campaign balance above the rent floor (used to recover the app test's 0.2 SOL).
import fs from 'fs';
import anchor from '@coral-xyz/anchor';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, LAMPORTS_PER_SOL, sendAndConfirmTransaction } from '@solana/web3.js';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const [idlPath, rpc, payerPath, mode, ownPath] = process.argv.slice(2);
const rlFetch = async (url, opts) => { for (let i = 0; ; i++) { const r = await fetch(url, opts); if ((r.status !== 429 && r.status < 500) || i >= 12) return r; await new Promise(z => setTimeout(z, 1500 * (i + 1))); } };
const conn = new Connection(rpc, { commitment: 'confirmed', fetch: rlFetch, disableRetryOnRateLimit: true });
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
conn.confirmTransaction = async (arg) => { const sig = typeof arg === 'string' ? arg : arg.signature;
  for (let i = 0; i < 90; i++) { const st = (await conn.getSignatureStatuses([sig])).value[0];
    if (st && (st.confirmationStatus === 'confirmed' || st.confirmationStatus === 'finalized')) {
      if (st.err) throw new Error('tx failed ' + JSON.stringify(st.err)); return { context: { slot: st.slot }, value: { err: st.err } }; }
    await sleep(1000); } throw new Error('confirm timeout ' + sig); };
const kp = (p) => Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(p, 'utf8'))));
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8')); const pid = new PublicKey(idl.metadata.address);
const prog = (k) => new Program(idl, pid, new AnchorProvider(conn, new Wallet(k), { commitment: 'confirmed' }));
const log = (o) => console.log(JSON.stringify(o));
const err = (e) => String(e.error?.errorCode?.code || e.logs?.find(l => /Error|failed|already in use|insufficient/i.test(l)) || e.message).split('\n')[0].slice(0, 200);
const transient = (e) => /Backend error|StatusCode: 5|fetch failed|ECONNRESET|blockhash/i.test(String(e?.message || e));
const retry = async (fn) => { for (let i = 0; ; i++) { try { return await fn(); } catch (e) { if (!transient(e) || i >= 6) throw e; await sleep(4000 * (i + 1)); } } };
const expectFail = async (label, fn0) => { const fn = () => retry(fn0); try { const s = await fn(); log({ step: label, ok: false, error: 'UNEXPECTED SUCCESS', sig: s }); } catch (e) { log({ step: label, expectedFailure: true, error: err(e) }); } };
const campaignOf = (pk) => PublicKey.findProgramAddressSync([Buffer.from('CROWDFUND'), pk.toBuffer()], pid)[0];
const SOL = LAMPORTS_PER_SOL; const payer = kp(payerPath);
const floor = async (c) => conn.getMinimumBalanceForRentExemption((await conn.getAccountInfo(c)).data.length);
if (mode === 'withdraw-own') {
  const O = kp(ownPath), c = campaignOf(O.publicKey); const amt = (await conn.getBalance(c)) - await floor(c);
  log({ step: `withdraw-own: admin withdraws ${amt / SOL} SOL (everything above the rent floor) from its campaign`, campaign: c.toBase58(),
    sig: await prog(O).methods.withdraw(new BN(amt)).accounts({ campaign: c, user: O.publicKey }).rpc() });
  process.exit(0);
}
// role keys are saved next to the payer keypair (on the box, never committed) so SOL can be recovered after an interrupted run
const A = Keypair.generate(), B = Keypair.generate(); const keyDir = payerPath.replace(/[^/]*$/, '');
for (const [n, k] of [['A', A], ['B', B]]) try { fs.writeFileSync(`${process.env.ROLE_KEY_DIR || keyDir}pulsefund-${n}-${A.publicKey.toBase58().slice(0, 6)}.json`, JSON.stringify(Array.from(k.secretKey)), { mode: 0o600 }); } catch {} const cA = campaignOf(A.publicKey);
log({ step: 'setup', program: pid.toBase58(), A: A.publicKey.toBase58(), B: B.publicKey.toBase58(), campaignA: cA.toBase58() });
log({ step: 'fund A 0.08 and B 0.04 SOL', sig: await sendAndConfirmTransaction(conn, new Transaction().add(
  SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: A.publicKey, lamports: 0.08 * SOL }),
  SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: B.publicKey, lamports: 0.04 * SOL })), [payer], { commitment: 'confirmed' }) });
const create = (k, c) => prog(k).methods.create('sol.college devnet test', 'Campaign made by the sol.college test script', new BN(SOL),
  'https://sol.college/', '', '', 'Education').accounts({ campaign: c, user: k.publicKey, systemProgram: SystemProgram.programId }).rpc();
log({ step: 'A creates its campaign (target 1 SOL; the PDA is ["CROWDFUND", admin], 9000 bytes)', ok: true, sig: await retry(() => create(A, cA)), rent_sol: (await conn.getBalance(cA)) / SOL });
await expectFail('A creates a second campaign (one campaign PDA per wallet)', () => create(A, cA));
const donate = (k, c, amt) => prog(k).methods.donate(new BN(amt)).accounts({ campaign: c, user: k.publicKey, systemProgram: SystemProgram.programId }).rpc();
log({ step: 'B donates 0.02 SOL to A\'s campaign', ok: true, sig: await retry(() => donate(B, cA, 0.02 * SOL)) });
const withdraw = (k, c, amt) => prog(k).methods.withdraw(new BN(amt)).accounts({ campaign: c, user: k.publicKey }).rpc();
await expectFail('B withdraws from A\'s campaign (admin only)', () => withdraw(B, cA, 0.01 * SOL));
await expectFail('A withdraws 0.03 SOL, more than the 0.02 donated (cannot dip into the rent floor)', () => withdraw(A, cA, 0.03 * SOL));
log({ step: 'A withdraws 0.015 SOL', ok: true, sig: await retry(() => withdraw(A, cA, 0.015 * SOL)) });
await expectFail('B calls get_campaign on A\'s campaign (admin-only check)', () => prog(B).methods.getCampaign().accounts({ campaign: cA, user: B.publicKey }).rpc());
await expectFail('B donates to a campaign PDA that was never created', () => donate(B, campaignOf(B.publicKey), 0.001 * SOL));
const c = await retry(() => prog(A).account.campaign.fetch(cA));
log({ step: 'final state', amount_donated_sol: c.amountDonated.toNumber() / SOL, amount_withdrawn_sol: c.amountWithdrawn.toNumber() / SOL,
  campaign_balance_sol: (await conn.getBalance(cA)) / SOL, target_sol: c.targetAmount.toNumber() / SOL });
for (const k of [A, B]) { const bal = await conn.getBalance(k.publicKey); if (bal > 10000)
  log({ step: 'return unspent SOL to the payer', from: k.publicKey.toBase58(), sol: (bal - 5000) / SOL,
    sig: await sendAndConfirmTransaction(conn, new Transaction().add(SystemProgram.transfer({ fromPubkey: k.publicKey, toPubkey: payer.publicKey, lamports: bal - 5000 })), [k], { commitment: 'confirmed' }) }); }
