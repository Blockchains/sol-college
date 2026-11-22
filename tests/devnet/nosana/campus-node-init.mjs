// Set up the campus browser-market node (idempotent): devnet SOL for fees, 200 practice NOS, 100 staked for 14 days in the lab staking program.
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, LAMPORTS_PER_SOL, sendAndConfirmTransaction } from '@solana/web3.js';
import { getOrCreateAssociatedTokenAccount, mintTo } from '@solana/spl-token';
import { address } from '@solana/kit';
import * as stakeProgram from '@nosana/stake-program';
import fs from 'fs';
import { LAB, RPC, FAUCET_NEVER, secret, signer, labClient } from './lab.mjs';
const log = (o) => console.log(JSON.stringify({ t: new Date().toISOString(), ...o }));
const conn = new Connection(RPC, 'confirmed');
const deployer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync('/home/box/.config/solana/id.json'))));
if (deployer.publicKey.toBase58() === FAUCET_NEVER) throw new Error('refusing to use the faucet wallet');
const node = Keypair.fromSecretKey(secret('nosana-node-campus')), authority = Keypair.fromSecretKey(secret('nosana-authority'));
if ((await conn.getBalance(node.publicKey)) < 0.03 * LAMPORTS_PER_SOL) log({ step: 'fund campus node 0.1 SOL', sig: await sendAndConfirmTransaction(conn, new Transaction().add(SystemProgram.transfer({ fromPubkey: deployer.publicKey, toPubkey: node.publicKey, lamports: 0.1 * LAMPORTS_PER_SOL })), [deployer]) });
const ata = await getOrCreateAssociatedTokenAccount(conn, node, new PublicKey(LAB.nos), node.publicKey);
if (Number(ata.amount) < 100e6) log({ step: 'mint 200 practice NOS to campus node', sig: await mintTo(conn, node, new PublicKey(LAB.nos), ata.address, authority, 200e6) });
const nodeSigner = await signer('nosana-node-campus'); const kit = labClient(nodeSigner);
if (!(await kit.stake.find(nodeSigner.address))) {
  const mintA = address(LAB.nos), progA = address(LAB.stake);
  const [userAta, vault, stakePda] = await Promise.all([kit.nos.getATA(nodeSigner.address), kit.solana.pda(['vault', mintA, nodeSigner.address], progA), kit.solana.pda(['stake', mintA, nodeSigner.address], progA)]);
  log({ step: 'campus node stakes 100 practice NOS for 14 days', sig: await kit.solana.buildSignAndSend(stakeProgram.getStakeInstruction({ mint: mintA, user: userAta, vault, stake: stakePda, authority: nodeSigner, amount: 100_000_000n, duration: 14n * 86400n }, { programAddress: progA })) });
}
log({ step: 'campus node ready', node: nodeSigner.address, stake: String((await kit.stake.find(nodeSigner.address)).amount) });
process.exit(0);
