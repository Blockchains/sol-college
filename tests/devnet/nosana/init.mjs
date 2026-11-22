// Initialise an EMPTY devnet environment for the Nosana lab (idempotent): practice NOS mint, balances, staking settings,
// rewards reflection, node stake, and an open market. Writes lab-state.json. Usage: DEVNET_RPC=... node init.mjs
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, LAMPORTS_PER_SOL, sendAndConfirmTransaction } from '@solana/web3.js';
import { createMint, getOrCreateAssociatedTokenAccount, mintTo, getMint } from '@solana/spl-token';
import { address } from '@solana/kit';
import * as stakeProgram from '@nosana/stake-program';
import * as rewardsProgram from '@nosana/rewards-program';
import fs from 'fs';
import { LAB, RPC, FAUCET_NEVER, secret, signer, labClient, loadState, saveState } from './lab.mjs';
const log = (o) => console.log(JSON.stringify({ t: new Date().toISOString(), ...o }));
const conn = new Connection(RPC, 'confirmed');
const kp = (n) => Keypair.fromSecretKey(secret(n));
const deployer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.env.DEPLOYER || '/home/box/.config/solana/id.json'))));
if (deployer.publicKey.toBase58() === FAUCET_NEVER) throw new Error('refusing to use the faucet wallet');
const S = loadState();
async function fundSol(pk, sol, label) {
  if ((await conn.getBalance(pk)) >= sol * LAMPORTS_PER_SOL * 0.5) return;
  const sig = await sendAndConfirmTransaction(conn, new Transaction().add(SystemProgram.transfer({ fromPubkey: deployer.publicKey, toPubkey: pk, lamports: Math.round(sol * LAMPORTS_PER_SOL) })), [deployer]);
  log({ step: `fund ${label} ${sol} SOL`, ok: true, sig });
}
const authority = kp('nosana-authority'), node = kp('nosana-node-a'), client = kp('nosana-client'), outsider = kp('nosana-outsider');
await fundSol(authority.publicKey, 0.1, 'lab authority'); await fundSol(node.publicKey, 0.05, 'practice node'); await fundSol(client.publicKey, 0.05, 'practice client'); await fundSol(outsider.publicKey, 0.02, 'outsider');

// 1. practice NOS mint (6 decimals) at the lab mint address, mint authority = lab authority
const mintKp = kp('nosana-nos-mint');
if (!(await conn.getAccountInfo(mintKp.publicKey))) {
  await createMint(conn, deployer, authority.publicKey, null, 6, mintKp);
  log({ step: 'create practice NOS mint (6 decimals)', ok: true, mint: mintKp.publicKey.toBase58() });
}
const mint = await getMint(conn, mintKp.publicKey); if (!mint.mintAuthority.equals(authority.publicKey)) throw new Error('mint authority mismatch');
for (const [who, owner, amount] of [['lab authority (staking token account)', authority.publicKey, 0], ['practice node', node.publicKey, 1000], ['practice client', client.publicKey, 10000], ['outsider', outsider.publicKey, 10]]) {
  const ata = await getOrCreateAssociatedTokenAccount(conn, deployer, mintKp.publicKey, owner);
  if (amount && Number(ata.amount) < amount * 1e6 / 2) { const sig = await mintTo(conn, deployer, mintKp.publicKey, ata.address, authority, amount * 1e6); log({ step: `mint ${amount} practice NOS to ${who}`, ok: true, sig }); }
  if (who.startsWith('lab authority') && ata.address.toBase58() !== LAB.authorityAta) throw new Error('TOKEN_ACCOUNT mismatch');
}

const authSigner = await signer('nosana-authority');
const kit = labClient(authSigner);
const send = async (step, ixs, c = kit) => { const sig = await c.solana.buildSignAndSend(ixs); log({ step, ok: true, sig }); return sig; };
// 2. staking settings ["settings"] and rewards reflection ["reflection"] + vault [mint]
const settings = await kit.solana.pda(['settings'], address(LAB.stake));
if (!(await conn.getAccountInfo(new PublicKey(settings)))) await send('staking init (settings -> lab authority, lab token account)', stakeProgram.getInitInstruction({ settings, authority: authSigner }, { programAddress: address(LAB.stake) }));
const reflection = await kit.solana.pda(['reflection'], address(LAB.rewards)); const rvault = await kit.solana.pda([address(LAB.nos)], address(LAB.rewards));
if (!(await conn.getAccountInfo(new PublicKey(reflection)))) await send('rewards init (reflection + vault for practice NOS)', rewardsProgram.getInitInstruction({ mint: address(LAB.nos), reflection, vault: rvault, authority: authSigner }, { programAddress: address(LAB.rewards) }));

// 3. practice node stakes 100 practice NOS for 14 days
const nodeSigner = await signer('nosana-node-a'); const nodeKit = labClient(nodeSigner);
if (!(await nodeKit.stake.find(nodeSigner.address))) {
  // kit 2.24.5 stake() derives PDAs from config.stakeAddress but builds the instruction WITHOUT programAddress, so it targets
  // the official staking program. Build it with the generated client and the lab program address instead (see backlog).
  const mintA = address(LAB.nos), progA = address(LAB.stake);
  const [userAta, vault, stakePda] = await Promise.all([nodeKit.nos.getATA(nodeSigner.address), nodeKit.solana.pda(['vault', mintA, nodeSigner.address], progA), nodeKit.solana.pda(['stake', mintA, nodeSigner.address], progA)]);
  const ixs = stakeProgram.getStakeInstruction({ mint: mintA, user: userAta, vault, stake: stakePda, authority: nodeSigner, amount: 100_000_000n, duration: 14n * 86400n }, { programAddress: progA });
  await send('practice node stakes 100 practice NOS for 14 days', ixs, nodeKit);
}
const st = await nodeKit.stake.find(nodeSigner.address); log({ step: 'node stake', amount: String(st.amount), xnos: String(st.xnos), duration: String(st.duration) });

// 4. open market (authority = lab authority): price 1 base unit (0.000001 NOS) per second, 10 min timeout, no access key
if (!S.market) {
  const ix = await kit.jobs.open({ jobPrice: 1, jobTimeout: 600, jobExpiration: 86400, nodeStakeMinimum: 0 });
  const market = ix.accounts.find((a) => a.signer)?.address ?? ix.accounts[1].address;
  await send('jobs open market (practice NOS, price 1 base unit/s, timeout 600 s)', ix);
  S.market = String(market); saveState(S);
}
const m = await kit.jobs.market(address(S.market)); log({ step: 'market', market: S.market, jobPrice: String(m.jobPrice), jobTimeout: String(m.jobTimeout), queueType: m.queueType, authority: String(m.authority) });
process.exit(0);
