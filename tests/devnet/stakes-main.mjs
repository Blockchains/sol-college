// Devnet end-to-end flow for the stakes-main fork (stakes.wtf: stake a token, get a gov token, bribes raise its price,
// unstaking vests linearly), mirroring app/src/services/instructions.ts. Built with the crate's `testing` feature,
// so one "day" in the program is one second. PDAs: pool = ["staking_pool", mint], vault = ["staking_vault", pool],
// vesting vault = ["vesting_vault", position]. Anchor 0.29 (the app's version).
// The app's IDL (app/src/types/program.ts) lists no fee_receiver for initializePool, but the program at this commit
// requires one; the script adds it (the app's own Create button cannot work, see the UI log).
// Usage (from app/): node stakes-main.mjs <idl.json> <rpc> <admin.json>
import fs from 'fs';
import anchor from '@coral-xyz/anchor';
import { createMint, getOrCreateAssociatedTokenAccount, mintTo, transfer, getAssociatedTokenAddressSync, getAccount, TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID } from '@solana/spl-token';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, LAMPORTS_PER_SOL, sendAndConfirmTransaction } from '@solana/web3.js';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const [idlPath, rpc, kpPath, uiWallet] = process.argv.slice(2);
const A = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(kpPath, 'utf8'))));
const conn = new Connection(rpc, 'confirmed');
conn.confirmTransaction = async (arg) => { const sig = typeof arg === 'string' ? arg : arg.signature;
  for (let i = 0; i < 90; i++) { const st = (await conn.getSignatureStatuses([sig])).value[0];
    if (st && (st.confirmationStatus === 'confirmed' || st.confirmationStatus === 'finalized')) {
      if (st.err) throw new Error('tx failed ' + JSON.stringify(st.err)); return { context: { slot: st.slot }, value: { err: st.err } }; }
    await new Promise(r => setTimeout(r, 1000)); } throw new Error('confirm timeout ' + sig); };
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8'));
const ip = idl.instructions.find(i => i.name === 'initializePool');
if (!ip.accounts.some(a => a.name === 'feeReceiver')) ip.accounts.splice(ip.accounts.findIndex(a => a.name === 'systemProgram'), 0, { name: 'feeReceiver', isMut: true, isSigner: false });
const programId = new PublicKey(process.env.PROGRAM_ID);
const prog = (kp) => new Program(idl, programId, new AnchorProvider(conn, new Wallet(kp), { commitment: 'confirmed' }));
const log = (o) => console.log(JSON.stringify(o)); const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const err = (e) => String(e.error?.errorCode?.code || e.logs?.find(l => /Error|failed|already in use/.test(l)) || e.message).split('\n')[0].slice(0, 200);
const expectFail = async (label, fn) => { try { await fn(); log({ step: label, ok: false, error: 'UNEXPECTED SUCCESS' }); } catch (e) { log({ step: label, expectedFailure: true, error: err(e) }); } };
const P = prog(A), B = Keypair.generate(), D = 1e6;
const pda = (seeds) => PublicKey.findProgramAddressSync(seeds, programId)[0];
log({ step: 'fund B', sig: await sendAndConfirmTransaction(conn, new Transaction().add(SystemProgram.transfer({ fromPubkey: A.publicKey, toPubkey: B.publicKey, lamports: 0.1 * LAMPORTS_PER_SOL })), [A], { commitment: 'confirmed' }) });
const mint = await createMint(conn, A, A.publicKey, null, 6);
const aTok = (await getOrCreateAssociatedTokenAccount(conn, A, mint, A.publicKey)).address;
const bTok = (await getOrCreateAssociatedTokenAccount(conn, A, mint, B.publicKey)).address;
log({ step: 'test mint, 1000 to A and 1000 to B', mint: mint.toBase58(), a: await mintTo(conn, A, mint, aTok, A, 1000 * D), b: await mintTo(conn, A, mint, bTok, A, 1000 * D) });
if (uiWallet) { const u = (await getOrCreateAssociatedTokenAccount(conn, A, mint, new PublicKey(uiWallet))).address; log({ step: 'mint 500 to the UI test wallet', sig: await mintTo(conn, A, mint, u, A, 500 * D) }); }
const pool = pda([Buffer.from('staking_pool'), mint.toBuffer()]), vault = pda([Buffer.from('staking_vault'), pool.toBuffer()]);
const initPool = (gov, fee) => P.methods.initializePool({}).accounts({ signer: A.publicKey, stakingPool: pool, mint, stakingVault: vault, govMint: gov.publicKey, feeReceiver: fee, systemProgram: SystemProgram.programId, tokenProgram: TOKEN_PROGRAM_ID }).signers([gov]).rpc();
await expectFail('initialize_pool_wrong_fee_receiver', () => initPool(Keypair.generate(), B.publicKey));
const gov = Keypair.generate();
log({ step: 'initialize_pool (2 SOL fee to the fee receiver, here the deployer itself)', ok: true, sig: await initPool(gov, A.publicKey), pool: pool.toBase58(), govMint: gov.publicKey.toBase58() });
await expectFail('initialize_pool_twice', () => initPool(Keypair.generate(), A.publicKey));
const stake = (kp, tok, amt, govMint = gov.publicKey) => prog(kp).methods.stake({ amount: new BN(amt) }).accounts({ signer: kp.publicKey, stakingPool: pool, govMint, stakingVault: vault, userToken: tok, userGovToken: getAssociatedTokenAddressSync(govMint, kp.publicKey), systemProgram: SystemProgram.programId, tokenProgram: TOKEN_PROGRAM_ID, associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID }).rpc();
await expectFail('stake_with_wrong_gov_mint', () => stake(B, bTok, 10 * D, mint));
log({ step: 'B stakes 100', ok: true, sig: await stake(B, bTok, 100 * D), govB: Number((await getAccount(conn, getAssociatedTokenAddressSync(gov.publicKey, B.publicKey))).amount) / D });
log({ step: 'A bribes 50 (plain token transfer into the vault, as the app does)', ok: true, sig: await transfer(conn, A, aTok, vault, A, 50 * D) });
await sleep(4000);
const sync = () => P.methods.syncBribes({}).accounts({ stakingPool: pool, govMint: gov.publicKey, stakingVault: vault }).rpc();
log({ step: 'sync_bribes', ok: true, sig: await sync(), pool: await P.account.stakingPool.fetch(pool).then(p => ({ activeBalance: p.activeBalance.toNumber() / D, govPrice: p.govPrice.toNumber() })) });
const pos = Keypair.generate(), vv = pda([Buffer.from('vesting_vault'), pos.publicKey.toBuffer()]);
const unstake = (kp, p, v) => prog(kp).methods.unstake({}).accounts({ signer: kp.publicKey, vestingPosition: p.publicKey, vestingVault: v, stakingPool: pool, mint, govMint: gov.publicKey, stakingVault: vault, userGovToken: getAssociatedTokenAddressSync(gov.publicKey, kp.publicKey), systemProgram: SystemProgram.programId, tokenProgram: TOKEN_PROGRAM_ID }).signers([p]).rpc();
const su = await unstake(B, pos, vv);
let vp = await P.account.vestingPosition.fetch(pos.publicKey);
log({ step: 'B unstakes all gov tokens (vesting position)', ok: true, sig: su, vested: Number((await getAccount(conn, vv)).amount) / D, claimPerDay: vp.claimPerDay.toNumber() / D });
const claim = (kp) => prog(kp).methods.claimVested({}).accounts({ owner: kp.publicKey, vestingPosition: pos.publicKey, vestingVault: vv, stakingPool: pool, mint, userToken: getAssociatedTokenAddressSync(mint, kp.publicKey), systemProgram: SystemProgram.programId, tokenProgram: TOKEN_PROGRAM_ID, associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID }).rpc();
await expectFail('A_claims_Bs_vesting', () => claim(A));
await sleep(5000);
let b0 = Number((await getAccount(conn, bTok)).amount);
log({ step: 'B claims after ~5 s (5 "days")', ok: true, sig: await claim(B), got: (Number((await getAccount(conn, bTok)).amount) - b0) / D });
await sleep(22000);
b0 = Number((await getAccount(conn, bTok)).amount);
log({ step: 'B claims after 20+ "days"', ok: true, sig: await claim(B), got: (Number((await getAccount(conn, bTok)).amount) - b0) / D, positionClosed: !(await conn.getAccountInfo(pos.publicKey)), Btotal: Number((await getAccount(conn, bTok)).amount) / D });
if (uiWallet) log({ step: 'for the UI run', mint: mint.toBase58(), pool: pool.toBase58() });
