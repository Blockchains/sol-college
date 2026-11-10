// Devnet end-to-end flow for the sentient-send fork (sentiment market: the side with the most SOL wins), mirroring the
// app's calls (frontend/src/app/create/page.tsx, market/[id]/page.tsx). PDAs: treasury = ["treasury"],
// market = ["market", creator, question], position = ["position", market, user]. Anchor 0.32 resolves them.
// Usage (from frontend/, @coral-xyz/anchor 0.32): node sentient-send.mjs <idl.json> <rpc> <creator.json>
import fs from 'fs';
import anchor from '@coral-xyz/anchor';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, LAMPORTS_PER_SOL, sendAndConfirmTransaction } from '@solana/web3.js';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const [idlPath, rpc, kpPath] = process.argv.slice(2);
const A = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(kpPath, 'utf8'))));
const conn = new Connection(rpc, 'confirmed');
conn.confirmTransaction = async (arg) => { const sig = typeof arg === 'string' ? arg : arg.signature;
  for (let i = 0; i < 90; i++) { const st = (await conn.getSignatureStatuses([sig])).value[0];
    if (st && (st.confirmationStatus === 'confirmed' || st.confirmationStatus === 'finalized')) {
      if (st.err) throw new Error('tx failed ' + JSON.stringify(st.err)); return { context: { slot: st.slot }, value: { err: st.err } }; }
    await new Promise(r => setTimeout(r, 1000)); } throw new Error('confirm timeout ' + sig); };
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8'));
const prog = (kp) => new Program(idl, new AnchorProvider(conn, new Wallet(kp), { commitment: 'confirmed' }));
const log = (o) => console.log(JSON.stringify(o)); const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const err = (e) => String(e.error?.errorCode?.code || e.logs?.find(l => /Error|failed/.test(l)) || e.message).split('\n')[0].slice(0, 200);
const expectFail = async (label, fn) => { try { await fn(); log({ step: label, ok: false, error: 'UNEXPECTED SUCCESS' }); } catch (e) { log({ step: label, expectedFailure: true, error: err(e) }); } };
const P = prog(A), pid = P.programId, SOL = LAMPORTS_PER_SOL;
const [treasury] = PublicKey.findProgramAddressSync([Buffer.from('treasury')], pid);
const B = Keypair.generate(), C = Keypair.generate();
log({ step: 'fund B and C', sig: await sendAndConfirmTransaction(conn, new Transaction().add(
  SystemProgram.transfer({ fromPubkey: A.publicKey, toPubkey: B.publicKey, lamports: 0.4 * SOL }),
  SystemProgram.transfer({ fromPubkey: A.publicKey, toPubkey: C.publicKey, lamports: 0.2 * SOL })), [A], { commitment: 'confirmed' }) });
if (!(await conn.getAccountInfo(treasury))) log({ step: 'initialize_treasury', ok: true, sig: await P.methods.initializeTreasury().accounts({ authority: A.publicKey }).rpc() });
const now = async () => conn.getBlockTime(await conn.getSlot('confirmed'));
const q = 'Devnet run ' + Date.now().toString(36); // the question is a PDA seed, so it must fit in 32 bytes
const [market] = PublicKey.findProgramAddressSync([Buffer.from('market'), A.publicKey.toBuffer(), Buffer.from(q)], pid);
log({ step: 'setup', program: pid.toBase58(), creator: A.publicKey.toBase58(), B: B.publicKey.toBase58(), C: C.publicKey.toBase58(), treasury: treasury.toBase58(), market: market.toBase58(), question: q });
const create = (o) => P.methods.createMarket(o.q ?? q, 'sol.college devnet run', new BN(o.end), o.sides ?? ['Yes', 'No'], new BN(o.amt ?? SOL)).accounts({ creator: A.publicKey }).rpc();
const t0 = await now();
await expectFail('create_one_side', () => create({ end: t0 + 600, sides: ['Yes'], q: q + 'a' }));
await expectFail('create_duplicate_sides', () => create({ end: t0 + 600, sides: ['Yes', 'yes'], q: q + 'b' }));
await expectFail('create_below_1_SOL', () => create({ end: t0 + 600, amt: 0.5 * SOL, q: q + 'c' }));
await expectFail('create_end_in_past', () => create({ end: t0 - 10, q: q + 'd' }));
const s1 = await create({ end: (await now()) + 75 });
let m = await P.account.market.fetch(market);
log({ step: 'create_market 1 SOL, Yes/No, ends in 75 s', ok: true, sig: s1, sides: m.sides.slice(0, 2).map(s => s.totalAmount.toNumber() / SOL), feePool: m.feePool.toNumber() / SOL });
const bet = (kp, side, amt) => prog(kp).methods.placeBet(side, new BN(amt)).accounts({ market, user: kp.publicKey }).rpc();
log({ step: 'B bets 0.2 SOL on Yes', ok: true, sig: await bet(B, 0, 0.2 * SOL) });
log({ step: 'C bets 0.05 SOL on No', ok: true, sig: await bet(C, 1, 0.05 * SOL) });
await expectFail('bet_below_min_0.001', () => bet(B, 0, 0.001 * SOL));
await expectFail('bet_above_max_1.5', () => bet(B, 0, 1.5 * SOL));
await expectFail('bet_invalid_side_5', () => bet(B, 5, 0.02 * SOL));
await expectFail('claim_before_end', () => prog(B).methods.claimWinnings().accounts({ market, user: B.publicKey }).rpc());
m = await P.account.market.fetch(market);
while ((await now()) < m.endTimestamp.toNumber() + 2) await sleep(5000);
await expectFail('bet_after_end', () => bet(C, 1, 0.02 * SOL));
const bal = (k) => conn.getBalance(k);
let b0 = await bal(B.publicKey);
const s2 = await prog(B).methods.claimWinnings().accounts({ market, user: B.publicKey }).rpc();
m = await P.account.market.fetch(market);
log({ step: 'B claims (Yes had the most SOL)', ok: true, sig: s2, Bgain: ((await bal(B.publicKey)) - b0) / SOL, winning: m.winningSides.slice(0, 2), resolved: m.resolved });
await expectFail('B_claims_twice', () => prog(B).methods.claimWinnings().accounts({ market, user: B.publicKey }).rpc());
await expectFail('C_claims_losing_side', () => prog(C).methods.claimWinnings().accounts({ market, user: C.publicKey }).rpc());
b0 = await bal(A.publicKey);
const s3 = await P.methods.claimWinnings().accounts({ market, user: A.publicKey }).rpc();
log({ step: 'creator claims its Yes share', ok: true, sig: s3, creatorGainApprox: ((await bal(A.publicKey)) - b0) / SOL });
await expectFail('claim_fees_by_non_creator', () => prog(B).methods.claimCreatorFees().accounts({ market, creator: B.publicKey, protocolAuthority: A.publicKey }).rpc());
await expectFail('claim_fees_wrong_protocol_authority', () => P.methods.claimCreatorFees().accounts({ market, creator: A.publicKey, protocolAuthority: C.publicKey }).rpc());
const s4 = await P.methods.claimCreatorFees().accounts({ market, creator: A.publicKey, protocolAuthority: A.publicKey }).rpc();
log({ step: 'claim_creator_fees (creator + protocol halves)', ok: true, sig: s4, marketLamportsLeft: (await bal(market)) / SOL });
