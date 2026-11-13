// Gifter escrow on devnet: create an A-for-B escrow, take it, refund a second one, and the program's rejections.
// Mirrors the app's calls (gifter-escrow-frontend/contract/methods/{create,refund,take}.ts). The app lists tokens
// through Helius DAS (getAssetsByOwner); this script talks to the program directly and also mints two 6-decimal
// tokens (the app multiplies amounts by 1e6).
// Usage (from gifter-escrow-frontend/, @coral-xyz/anchor 0.30): node gifter-escrow.mjs <idl.json> <rpc> <payer.json>
// The payer funds two fresh keys (M = maker, T = taker, X = outsider) and gets the unspent SOL back at the end.
import fs from 'fs';
import anchor from '@coral-xyz/anchor';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, LAMPORTS_PER_SOL, sendAndConfirmTransaction } from '@solana/web3.js';
import { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID, createMint, getOrCreateAssociatedTokenAccount, mintTo, getAccount, getAssociatedTokenAddressSync, createAssociatedTokenAccountInstruction, createMintToInstruction, createInitializeMint2Instruction, MINT_SIZE, getMinimumBalanceForRentExemptMint } from '@solana/spl-token';
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
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8')); const pid = new PublicKey(idl.address || idl.metadata.address);
const prog = (k) => new Program(idl, new AnchorProvider(conn, new Wallet(k), { commitment: 'confirmed' }));
const log = (o) => console.log(JSON.stringify(o));
const err = (e) => String(e.error?.errorCode?.code || e.logs?.find(l => /Error|failed|already in use|insufficient/i.test(l)) || e.message).split('\n')[0].slice(0, 240);
const transient = (e) => /Backend error|StatusCode: 5|fetch failed|ECONNRESET|blockhash|timed out|429/i.test(String(e?.message || e));
const retry = async (fn) => { for (let i = 0; ; i++) { try { return await fn(); } catch (e) { if (!transient(e) || i >= 6) throw e; await sleep(4000 * (i + 1)); } } };
const expectFail = async (label, fn0) => { try { const s = await retry(fn0); log({ step: label, ok: false, error: 'UNEXPECTED SUCCESS', sig: s }); } catch (e) { log({ step: label, expectedFailure: true, error: err(e), sig: e.signature || undefined }); } };
const SOL = LAMPORTS_PER_SOL; const payer = kp(payerPath);
const M = Keypair.generate(), T = Keypair.generate(), X = Keypair.generate(); const keyDir = payerPath.replace(/[^/]*$/, '');
const tag = M.publicKey.toBase58().slice(0, 6);
for (const [n, k] of [['M', M], ['T', T], ['X', X]]) try { fs.writeFileSync(`${process.env.ROLE_KEY_DIR || keyDir}gifter-${n}-${tag}.json`, JSON.stringify(Array.from(k.secretKey)), { mode: 0o600 }); } catch {}
const DEC = 6, UNIT = 10 ** DEC;
const escrowOf = (maker, id) => PublicKey.findProgramAddressSync([Buffer.from('gifter_escrow'), maker.toBuffer(), new BN(id).toArrayLike(Buffer, 'le', 8)], pid)[0];
const vaultOf = (state, mint) => getAssociatedTokenAddressSync(mint, state, true, TOKEN_PROGRAM_ID);
const ata = (owner, mint) => getAssociatedTokenAddressSync(mint, owner, false, TOKEN_PROGRAM_ID);
log({ step: 'setup', program: pid.toBase58(), M: M.publicKey.toBase58(), T: T.publicKey.toBase58(), X: X.publicKey.toBase58() });
log({ step: 'fund M 0.12, T 0.12, X 0.03 SOL (enough for mint ATAs and escrow rent)', sig: await sendAndConfirmTransaction(conn, new Transaction().add(
  SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: M.publicKey, lamports: 0.12 * SOL }),
  SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: T.publicKey, lamports: 0.12 * SOL }),
  SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: X.publicKey, lamports: 0.03 * SOL })), [payer], { commitment: 'confirmed' }) });
const newMint = async (label) => {
  const mint = Keypair.generate();
  const lamports = await conn.getMinimumBalanceForRentExemption(MINT_SIZE);
  const tx = new Transaction().add(
    SystemProgram.createAccount({ fromPubkey: payer.publicKey, newAccountPubkey: mint.publicKey, space: MINT_SIZE, lamports, programId: TOKEN_PROGRAM_ID }),
    createInitializeMint2Instruction(mint.publicKey, DEC, payer.publicKey, null, TOKEN_PROGRAM_ID),
  );
  const sig = await retry(() => sendAndConfirmTransaction(conn, tx, [payer, mint], { commitment: 'confirmed' }));
  log({ step: `create ${label} (6 decimals, payer is mint authority)`, mint: mint.publicKey.toBase58(), sig });
  return mint.publicKey;
};
const mintA = await newMint('mint A (the deposited token)');
const mintB = await newMint('mint B (what the maker wants in return)');
const ensureAta = async (ownerKp, mint, label) => {
  const dest = ata(ownerKp.publicKey, mint);
  if (!(await conn.getAccountInfo(dest))) {
    const tx = new Transaction().add(createAssociatedTokenAccountInstruction(payer.publicKey, dest, ownerKp.publicKey, mint, TOKEN_PROGRAM_ID));
    const sig = await retry(() => sendAndConfirmTransaction(conn, tx, [payer], { commitment: 'confirmed' }));
    log({ step: `create ATA ${label}`, account: dest.toBase58(), sig });
  }
  return dest;
};
const mintUnits = async (dest, mint, units, label) => {
  const tx = new Transaction().add(createMintToInstruction(mint, dest, payer.publicKey, units, [], TOKEN_PROGRAM_ID));
  const sig = await retry(() => sendAndConfirmTransaction(conn, tx, [payer], { commitment: 'confirmed' }));
  log({ step: `mint ${units / UNIT} of ${label}`, to: dest.toBase58(), sig });
};
const ataMA = await ensureAta(M, mintA, 'M / mint A');
const ataMB = await ensureAta(M, mintB, 'M / mint B');
const ataTA = await ensureAta(T, mintA, 'T / mint A');
const ataTB = await ensureAta(T, mintB, 'T / mint B');
const ataXA = await ensureAta(X, mintA, 'X / mint A');
await mintUnits(ataMA, mintA, 1000 * UNIT, 'mint A to M');
await mintUnits(ataTB, mintB, 1000 * UNIT, 'mint B to T');
const tok = async (a) => Number((await getAccount(conn, a)).amount);
const create = (k, id, dep, want) => {
  const state = escrowOf(k.publicKey, id);
  return prog(k).methods.createEscrow(new BN(id), new BN(dep * UNIT), new BN(want * UNIT)).accounts({
    maker: k.publicKey, mintA, mintB, makerTokenAccountA: ata(k.publicKey, mintA),
    gifterEscrowState: state, escrowVault: vaultOf(state, mintA),
    systemProgram: SystemProgram.programId, associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID, tokenProgram: TOKEN_PROGRAM_ID,
  }).rpc();
};
const refund = (k, id) => {
  const state = escrowOf(k.publicKey, id);
  return prog(k).methods.refund().accounts({
    maker: k.publicKey, mintA, makerTokenAccountA: ata(k.publicKey, mintA),
    gifterEscrowState: state, escrowVault: vaultOf(state, mintA),
    systemProgram: SystemProgram.programId, associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID, tokenProgram: TOKEN_PROGRAM_ID,
  }).rpc();
};
const take = (taker, maker, id) => {
  const state = escrowOf(maker, id);
  return prog(taker).methods.takeAndClose().accounts({
    maker, taker: taker.publicKey, mintA, mintB,
    makerTokenAccountB: ata(maker, mintB), takerTokenAccountA: ata(taker.publicKey, mintA), takerTokenAccountB: ata(taker.publicKey, mintB),
    gifterEscrowState: state, escrowVault: vaultOf(state, mintA),
    systemProgram: SystemProgram.programId, associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID, tokenProgram: TOKEN_PROGRAM_ID,
  }) .rpc({ skipPreflight: true });
};
log({ step: 'M creates escrow #1: deposits 10 of mint A, wants 5 of mint B', ok: true, sig: await retry(() => create(M, 1, 10, 5)), escrow: escrowOf(M.publicKey, 1).toBase58(), M_A: (await tok(ataMA)) / UNIT });
await expectFail('M creates escrow #1 again (same PDA)', () => create(M, 1, 10, 5));
await expectFail("X refunds M's open escrow (PDA is seeded by the signer, so X's seeds miss)", () => refund(X, 1));
await expectFail("BUG: T takes escrow #1 — take_and_close aborts with an access violation (the handler starts with println(\"Hello\") in take.rs)", () => take(T, M.publicKey, 1));
const mA0 = await tok(ataMA);
log({ step: 'M refunds escrow #1 (the take never ran, so the 10 of mint A is still in the vault)', ok: true, sig: await retry(() => refund(M, 1)), M_A_gain: ((await tok(ataMA)) - mA0) / UNIT });
log({ step: 'M creates escrow #2 asking for 10_000 of mint B (more than T holds) — take is the same crashing instruction, so this is about create with a large want', ok: true, sig: await retry(() => create(M, 2, 1, 10000)) });
log({ step: 'M refunds escrow #2', ok: true, sig: await retry(() => refund(M, 2)) });
// fund the hosted-app test wallet so the DAS-backed token dropdown can see the two mints
const testerPk = new PublicKey('m4AcRjHcQzpvejFnU9KBEgf9z7pwni84CrGpARCoJpr');
for (const [mint, label] of [[mintA, 'A'], [mintB, 'B']]) {
  const dest = getAssociatedTokenAddressSync(mint, testerPk, false, TOKEN_PROGRAM_ID);
  const ixs = [];
  if (!(await conn.getAccountInfo(dest))) ixs.push(createAssociatedTokenAccountInstruction(payer.publicKey, dest, testerPk, mint, TOKEN_PROGRAM_ID));
  ixs.push(createMintToInstruction(mint, dest, payer.publicKey, 50 * UNIT, [], TOKEN_PROGRAM_ID));
  const sig = await retry(() => sendAndConfirmTransaction(conn, new Transaction().add(...ixs), [payer], { commitment: 'confirmed' }));
  log({ step: `mint 50 of mint ${label} to the UI test wallet for the DAS token list`, mint: mint.toBase58(), ata: dest.toBase58(), sig });
}
for (const k of [M, T, X]) { const b = await conn.getBalance(k.publicKey); if (b > 10000)
  log({ step: 'return unspent SOL to the payer', from: k.publicKey.toBase58(), sol: (b - 5000) / SOL,
    sig: await retry(() => sendAndConfirmTransaction(conn, new Transaction().add(SystemProgram.transfer({ fromPubkey: k.publicKey, toPubkey: payer.publicKey, lamports: b - 5000 })), [k], { commitment: 'confirmed' })) }); }
