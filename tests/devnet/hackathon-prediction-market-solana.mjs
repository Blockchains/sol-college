// CS2 prediction market (hackathon-prediction-market-solana fork) on devnet: config, whitelist, market with YES/NO mints,
// liquidity, buys and a sell on the curve, admin resolution. Mirrors the app's calls (prediction-market-frontend/src/components).
// Usage (from prediction-market-frontend/, @coral-xyz/anchor 0.31): node hackathon-prediction-market-solana.mjs <idl.json> <rpc> <admin.json> <team-wallet pubkey>
// The admin keypair becomes the config authority and market creator (so the hosted app's test wallet can resolve);
// B (a whitelisted trader) and C (not whitelisted) are fresh keys it funds with a little devnet SOL.
import fs from 'fs';
import anchor from '@coral-xyz/anchor';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, LAMPORTS_PER_SOL, ComputeBudgetProgram, sendAndConfirmTransaction } from '@solana/web3.js';
import { createInitializeMintInstruction, getAssociatedTokenAddressSync, TOKEN_PROGRAM_ID } from '@solana/spl-token';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const [idlPath, rpc, kpPath, teamWalletArg] = process.argv.slice(2);
const rlFetch = async (url, opts) => { for (let i = 0; ; i++) { const r = await fetch(url, opts); if (r.status !== 429 || i >= 12) return r; await new Promise(z => setTimeout(z, 1500 * (i + 1))); } };
const conn = new Connection(rpc, { commitment: 'confirmed', fetch: rlFetch, disableRetryOnRateLimit: true });
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
conn.confirmTransaction = async (arg) => { const sig = typeof arg === 'string' ? arg : arg.signature;
  for (let i = 0; i < 90; i++) { const st = (await conn.getSignatureStatuses([sig])).value[0];
    if (st && (st.confirmationStatus === 'confirmed' || st.confirmationStatus === 'finalized')) {
      if (st.err) throw new Error('tx failed ' + JSON.stringify(st.err)); return { context: { slot: st.slot }, value: { err: st.err } }; }
    await sleep(1000); } throw new Error('confirm timeout ' + sig); };
const A = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(kpPath, 'utf8'))));
const TEAM = new PublicKey(teamWalletArg);
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8'));
const prog = (kp) => new Program(idl, new AnchorProvider(conn, new Wallet(kp), { commitment: 'confirmed' }));
const P = prog(A), pid = P.programId, SOL = LAMPORTS_PER_SOL;
const log = (o) => console.log(JSON.stringify(o));
const err = (e) => String(e.error?.errorCode?.code || e.logs?.find(l => /Error|failed|already in use/.test(l)) || e.message).split('\n')[0].slice(0, 200);
const expectFail = async (label, fn) => { try { const s = await fn(); log({ step: label, ok: false, error: 'UNEXPECTED SUCCESS', sig: s }); } catch (e) { log({ step: label, expectedFailure: true, error: err(e) }); } };
const pda = (...s) => PublicKey.findProgramAddressSync(s.map(x => typeof x === 'string' ? Buffer.from(x) : x), pid)[0];
const globalVault = pda('global'), whitelist = pda('wl-seed', A.publicKey.toBuffer());
const B = Keypair.generate(), C = Keypair.generate();
log({ step: 'setup', program: pid.toBase58(), admin: A.publicKey.toBase58(), team_wallet: TEAM.toBase58(), B: B.publicKey.toBase58(), C: C.publicKey.toBase58() });
log({ step: 'fund B (whitelisted trader) and C (not whitelisted)', sig: await sendAndConfirmTransaction(conn, new Transaction().add(
  SystemProgram.transfer({ fromPubkey: A.publicKey, toPubkey: B.publicKey, lamports: 0.06 * SOL }),
  SystemProgram.transfer({ fromPubkey: A.publicKey, toPubkey: C.publicKey, lamports: 0.02 * SOL })), [A], { commitment: 'confirmed' }) });

const cfg = (authority) => ({ authority, pendingAuthority: PublicKey.default, teamWallet: TEAM, steamOracle: PublicKey.default,
  platformBuyFee: new BN(100), platformSellFee: new BN(100), lpBuyFee: new BN(20), lpSellFee: new BN(20),
  tokenSupplyConfig: new BN(1_000_000_000_000), tokenDecimalsConfig: 6, initialRealTokenReservesConfig: new BN(1_000_000_000),
  minSolLiquidity: new BN(0.02 * SOL), initialized: true });
const configure = (kp) => prog(kp).methods.configure(cfg(A.publicKey)).accountsPartial({ payer: kp.publicKey }).rpc();
log({ step: 'configure: fees 1% platform + 0.2% LP each way, 1M-token supply per side, 1000-token initial reserves, min liquidity 0.02 SOL (the repo default is 5 SOL)', ok: true, sig: await configure(A) });
await expectFail('configure by a wallet that is not the config authority', () => configure(C));
if (!(await conn.getAccountInfo(whitelist))) log({ step: 'whitelist_init (creator is the first member)', ok: true, sig: await P.methods.whitelistInit().accountsPartial({ creator: A.publicKey }).rpc() });

// Market: the app's "Create Market" sends tx1 (two mints whose authority is the program's global vault) then create_market.
const yes = Keypair.generate(), no = Keypair.generate(); const rent = await conn.getMinimumBalanceForRentExemption(82);
const tx1 = new Transaction().add(
  SystemProgram.createAccount({ fromPubkey: A.publicKey, newAccountPubkey: no.publicKey, space: 82, lamports: rent, programId: TOKEN_PROGRAM_ID }),
  createInitializeMintInstruction(no.publicKey, 6, globalVault, globalVault, TOKEN_PROGRAM_ID),
  SystemProgram.createAccount({ fromPubkey: A.publicKey, newAccountPubkey: yes.publicKey, space: 82, lamports: rent, programId: TOKEN_PROGRAM_ID }),
  createInitializeMintInstruction(yes.publicKey, 6, globalVault, globalVault, TOKEN_PROGRAM_ID));
log({ step: 'create YES and NO mints (authority = global vault PDA)', ok: true, sig: await sendAndConfirmTransaction(conn, tx1, [A, no, yes], { commitment: 'confirmed' }), yes: yes.publicKey.toBase58(), no: no.publicKey.toBase58() });
const market = pda('market', yes.publicKey.toBuffer(), no.publicKey.toBuffer()), cs2 = pda('cs2-match', yes.publicKey.toBuffer(), no.publicKey.toBuffer());
const team = (n) => Array.from({ length: n }, (_, i) => ({ wallet: Keypair.generate().publicKey, steamid: 'S' + i }));  // short IDs: with 17-digit SteamID64s the create_market tx exceeds the 1232-byte limit (see limits)
const META = 'https://sol.college/dapps/hackathon-prediction-market-solana/meta/';
const params = (n) => ({ yesSymbol: 'SCYES', yesUri: META + 'yes.json', noSymbol: 'SCNO', noUri: META + 'no.json',
  startSlot: null, endingSlot: null, steamMatchIdHash: Array(32).fill(0), nextMatchCode: 'SC-1', teamMembers: team(n) });
const create = (n) => P.methods.createMarket(params(n)).accountsPartial({ creator: A.publicKey, yesToken: yes.publicKey, noToken: no.publicKey, market, whitelist, cs2Match: cs2, teamWallet: TEAM, globalVault })
  .preInstructions([ComputeBudgetProgram.setComputeUnitLimit({ units: 400_000 })]).rpc();
await expectFail('create_market with 4 team members (needs exactly 5)', () => create(4));
log({ step: 'create_market (5 team members, metadata for both mints, 1M of each minted to the vault)', ok: true, sig: await create(5), market: market.toBase58() });

const acc = (kp) => ({ teamWallet: TEAM, market, whitelist, globalVault, yesToken: yes.publicKey, noToken: no.publicKey, user: kp.publicKey });
const addLiq = (kp, sol) => prog(kp).methods.addLiquidity(new BN(Math.round(sol * SOL))).accountsPartial(acc(kp)).rpc();
await expectFail('add_liquidity below the 0.02 SOL minimum', () => addLiq(A, 0.01));
log({ step: 'add_liquidity 0.04 SOL (first LP: 0.02 SOL backs each side)', ok: true, sig: await addLiq(A, 0.04) });
const swap = (kp, amt, dir, tt, min = 0) => prog(kp).methods.swap(new BN(amt), dir, tt, new BN(min)).accountsPartial(acc(kp)).rpc();
await expectFail('swap by C, who is not on the market creator\'s whitelist', () => swap(C, 0.005 * SOL, 0, 1));
log({ step: 'whitelist_add_member B', ok: true, sig: await P.methods.whitelistAddMember(B.publicKey).accountsPartial({ authority: A.publicKey, whitelist }).rpc() });
const yesAta = getAssociatedTokenAddressSync(yes.publicKey, B.publicKey), noAta = getAssociatedTokenAddressSync(no.publicKey, B.publicKey);
const bal = async (a) => { try { return (await conn.getTokenAccountBalance(a)).value.uiAmount; } catch { return 0; } };
log({ step: 'B buys YES with 0.01 SOL', ok: true, sig: await swap(B, 0.01 * SOL, 0, 1), yes: await bal(yesAta) });
log({ step: 'B buys NO with 0.005 SOL', ok: true, sig: await swap(B, 0.005 * SOL, 0, 0), no: await bal(noAta) });
await expectFail('B buys YES with minimum_receive set impossibly high', () => swap(B, 0.001 * SOL, 0, 1, 1e15));
const halfYes = Math.floor(Number((await conn.getTokenAccountBalance(yesAta)).value.amount) / 2);
const bBefore = await conn.getBalance(B.publicKey);
log({ step: 'B sells half its YES', ok: true, sig: await swap(B, halfYes, 1, 1), yes: await bal(yesAta), sol_back: ((await conn.getBalance(B.publicKey)) - bBefore) / SOL });
const resolve = (kp, tt, done) => prog(kp).methods.resolution(new BN(0), new BN(0), tt, done).accountsPartial({ market, cs2Match: cs2, globalVault, yesToken: yes.publicKey, noToken: no.publicKey, user: kp.publicKey, authority: kp.publicKey }).rpc();
await expectFail('resolution by B (not admin or oracle)', () => resolve(B, 1, true));
log({ step: 'resolution by admin: match completed, YES (team A) wins', ok: true, sig: await resolve(A, 1, true) });
await expectFail('B swaps after the market is completed', () => swap(B, 0.001 * SOL, 0, 1));
await expectFail('resolve again', () => resolve(A, 0, true));
const vaultBefore = await conn.getBalance(globalVault);
log({ step: 'withdraw_liquidity 0.02 SOL by the LP', ok: true, sig: await prog(A).methods.withdrawLiquidity(new BN(0.02 * SOL)).accountsPartial(acc(A)).rpc(), vault_change_sol: ((await conn.getBalance(globalVault)) - vaultBefore) / SOL });
const m = await P.account.market.fetch(market), c = await P.account.cs2Match.fetch(cs2);
log({ step: 'final state', completed: m.isCompleted, winner: c.winnerTokenType, status: c.status, yes_sol_reserves: m.realYesSolReserves.toNumber() / SOL, no_sol_reserves: m.realNoSolReserves.toNumber() / SOL, volume_sol: m.totalVolume.toNumber() / SOL, B_yes: await bal(yesAta), B_no: await bal(noAta), vault_sol: (await conn.getBalance(globalVault)) / SOL });
