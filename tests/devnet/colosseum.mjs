// Devnet end-to-end flow for the colosseum fork (Novengrid SOL staking), mirroring the app's calls in ui/components/Body.tsx
// and AdminBody.tsx. PDAs: vault = ["vault", admin], player = ["player", admin, player]. Anchor 0.31 resolves them from the IDL.
// Usage (from ui/, @coral-xyz/anchor 0.31): node colosseum.mjs <idl.json> <rpc> <admin.json>
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
const err = (e) => String(e.error?.errorCode?.code || e.logs?.find(l => /Error|failed|already in use/.test(l)) || e.message).split('\n')[0].slice(0, 200);
const expectFail = async (label, fn) => { try { await fn(); log({ step: label, ok: false, error: 'UNEXPECTED SUCCESS' }); } catch (e) { log({ step: label, expectedFailure: true, error: err(e) }); } };
const probe = async (label, fn) => { try { log({ step: label, probe: true, succeeded: true, sig: await fn() }); } catch (e) { log({ step: label, probe: true, succeeded: false, error: err(e) }); } };
const P = prog(A), pid = P.programId, SOL = LAMPORTS_PER_SOL, B = Keypair.generate();
const [vault] = PublicKey.findProgramAddressSync([Buffer.from('vault'), A.publicKey.toBuffer()], pid);
const [player] = PublicKey.findProgramAddressSync([Buffer.from('player'), A.publicKey.toBuffer(), B.publicKey.toBuffer()], pid);
const bal = (k) => conn.getBalance(k);
log({ step: 'fund B', sig: await sendAndConfirmTransaction(conn, new Transaction().add(SystemProgram.transfer({ fromPubkey: A.publicKey, toPubkey: B.publicKey, lamports: 0.3 * SOL })), [A], { commitment: 'confirmed' }) });
log({ step: 'setup', program: pid.toBase58(), admin: A.publicKey.toBase58(), B: B.publicKey.toBase58(), vault: vault.toBase58(), player });
if (!(await conn.getAccountInfo(vault))) log({ step: 'initialize apy_rate 100 (what the admin page sends)', ok: true, sig: await P.methods.initialize(new BN(100)).accounts({ authority: A.publicKey }).rpc() });
await expectFail('initialize_twice', () => P.methods.initialize(new BN(100)).accounts({ authority: A.publicKey }).rpc());
await expectFail('deposit_0', () => P.methods.deposit(new BN(0)).accounts({ authority: A.publicKey, player: A.publicKey }).rpc());
log({ step: 'admin deposits 0.2 SOL of rewards', ok: true, sig: await P.methods.deposit(new BN(0.2 * SOL)).accounts({ authority: A.publicKey, player: A.publicKey }).rpc(), vaultSol: (await bal(vault)) / SOL });
const PB = prog(B);
await expectFail('stake_0', () => PB.methods.solStake(new BN(0), new BN(20)).accounts({ authority: A.publicKey, player: B.publicKey }).rpc());
log({ step: 'B stakes 0.1 SOL for 20 s', ok: true, sig: await PB.methods.solStake(new BN(0.1 * SOL), new BN(20)).accounts({ authority: A.publicKey, player: B.publicKey }).rpc() });
await expectFail('unstake_before_duration', () => PB.methods.solUnstake().accounts({ authority: A.publicKey, player: B.publicKey }).rpc());
await expectFail('B_withdraws_admin_vault', () => PB.methods.withdraw().accountsPartial({ authority: B.publicKey, vaultData: vault }).rpc());
await sleep(8000);
let b0 = await bal(B.publicKey);
const sc = await PB.methods.claimRewards().accounts({ authority: A.publicKey, player: B.publicKey }).rpc();
let pd = await P.account.playerAccount.fetch(player);
log({ step: 'B claims rewards', ok: true, sig: sc, rewardLamports: pd.rewardAmount.toNumber(), Bdelta: (await bal(B.publicKey)) - b0, note: 'reward = staked * apy_rate * seconds / 31,536,000; apy_rate 100 is 100x the stake per year' });
const v = await P.account.vaultAccount.fetch(vault);
log({ step: 'vault accounting after claim', stakedAmount: v.stakedAmount.toNumber() / SOL, note: 'claim subtracts the reward from staked_amount' });
await sleep(15000);
b0 = await bal(B.publicKey);
log({ step: 'B unstakes after 20 s', ok: true, sig: await PB.methods.solUnstake().accounts({ authority: A.publicKey, player: B.publicKey }).rpc(), Bgain: ((await bal(B.publicKey)) - b0) / SOL });
await expectFail('claim_with_nothing_staked', () => PB.methods.claimRewards().accounts({ authority: A.publicKey, player: B.publicKey }).rpc());
await probe('B calls config (no admin check; it creates and sets B\'s own vault, not the admin\'s)', () => PB.methods.config(new BN(5)).accounts({ authority: B.publicKey }).rpc());
const before = await bal(vault);
await probe('admin withdraws the whole vault balance (rent included)', () => P.methods.withdraw().accounts({ authority: A.publicKey }).rpc());
log({ step: 'after withdraw', vaultLamportsBefore: before, vaultAccountExists: !!(await conn.getAccountInfo(vault)) });
