import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, TransactionInstruction, SYSVAR_RENT_PUBKEY } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const TOKEN_PROGRAM_ID = new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA');
const ASSOCIATED_TOKEN_PROGRAM_ID = new PublicKey('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL');
const MINT = new PublicKey('BJMSdujxakjx7qypwfaFCnbkMTNPEYVWTTqnR9eJRL4D');
const BPF_LOADER = new PublicKey('BPFLoaderUpgradeab1e11111111111111111111111');

const idl = JSON.parse(fs.readFileSync(process.argv[2] || '/workspace/deai-work/proof/covenant.json', 'utf8'));
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.env.HOME + '/.config/solana/id.json', 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const taker = Keypair.generate();
const arb2 = Keypair.generate();
const arb3 = Keypair.generate();
const prog = new Program(idl, new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' }));
const takerProg = new Program(idl, new AnchorProvider(conn, new Wallet(taker), { commitment: 'confirmed' }));
const log = (o) => { console.log(JSON.stringify(o)); if (process.env.PROOF_LOG) fs.appendFileSync(process.env.PROOF_LOG, JSON.stringify(o)+'\n'); };

function ata(owner) {
  return PublicKey.findProgramAddressSync(
    [owner.toBuffer(), TOKEN_PROGRAM_ID.toBuffer(), MINT.toBuffer()],
    ASSOCIATED_TOKEN_PROGRAM_ID
  )[0];
}
async function sendIx(ixs, signers) {
  const tx = new Transaction().add(...ixs);
  tx.feePayer = payer.publicKey;
  tx.recentBlockhash = (await conn.getLatestBlockhash()).blockhash;
  tx.sign(...signers);
  const sig = await conn.sendRawTransaction(tx.serialize());
  await conn.confirmTransaction(sig, 'confirmed');
  return sig;
}
async function ensureAta(owner) {
  const dest = ata(owner);
  if (await conn.getAccountInfo(dest)) return dest;
  const ix = new TransactionInstruction({
    programId: ASSOCIATED_TOKEN_PROGRAM_ID,
    keys: [
      { pubkey: payer.publicKey, isSigner: true, isWritable: true },
      { pubkey: dest, isSigner: false, isWritable: true },
      { pubkey: owner, isSigner: false, isWritable: false },
      { pubkey: MINT, isSigner: false, isWritable: false },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    ],
    data: Buffer.from([0]),
  });
  await sendIx([ix], [payer]);
  return dest;
}
async function mintTo(dest, amount) {
  const data = Buffer.alloc(9); data[0]=7; data.writeBigUInt64LE(BigInt(amount),1);
  const ix = new TransactionInstruction({
    programId: TOKEN_PROGRAM_ID,
    keys: [
      { pubkey: MINT, isSigner: false, isWritable: true },
      { pubkey: dest, isSigner: false, isWritable: true },
      { pubkey: payer.publicKey, isSigner: true, isWritable: false },
    ],
    data,
  });
  return sendIx([ix], [payer]);
}
async function tokenBal(pk) {
  const i = await conn.getAccountInfo(pk);
  if (!i) return 0n;
  return BigInt((await conn.getTokenAccountBalance(pk)).value.amount);
}
function sleep(ms){ return new Promise(r=>setTimeout(r,ms)); }

const AMOUNT = 1_000_000;
const [config] = PublicKey.findProgramAddressSync([Buffer.from('config')], programId);
const [programData] = PublicKey.findProgramAddressSync([programId.toBuffer()], BPF_LOADER);
const specHash = Buffer.alloc(32, 7); specHash.write('cov-job-1');
const [job] = PublicKey.findProgramAddressSync(
  [Buffer.from('job'), payer.publicKey.toBuffer(), specHash],
  programId
);
const [escrowToken] = PublicKey.findProgramAddressSync(
  [Buffer.from('escrow_token'), job.toBuffer()],
  programId
);
const [reputation] = PublicKey.findProgramAddressSync(
  [Buffer.from('reputation'), taker.publicKey.toBuffer()],
  programId
);
const [claimListing] = PublicKey.findProgramAddressSync(
  [Buffer.from('claim'), job.toBuffer()],
  programId
);
const posterAta = await ensureAta(payer.publicKey);
const takerAta = await ensureAta(taker.publicKey);
await sendIx([SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: taker.publicKey, lamports: 20_000_000 })], [payer]);
await mintTo(posterAta, AMOUNT);
log({ step:'setup', program: programId.toBase58(), config: config.toBase58(), job: job.toBase58(), escrowToken: escrowToken.toBase58(), taker: taker.publicKey.toBase58(), programData: programData.toBase58() });

if (!(await conn.getAccountInfo(config))) {
  const s0 = await prog.methods.initConfig(
      [payer.publicKey, arb2.publicKey, arb3.publicKey],
      2,
      new BN(1),
      new BN(3600),
      0,
      new BN(0)
    ).accounts({
      admin: payer.publicKey,
      config,
      program: programId,
      programData,
      systemProgram: SystemProgram.programId,
    }).rpc();
  log({ step:'init_config', ok:true, sig:s0 });
  console.log('SIG init_config', s0);
} else {
  log({ step:'init_config', skipped:true });
}

const deadline = Math.floor(Date.now()/1000) + 3600;
const s1 = await prog.methods.createJob(new BN(AMOUNT), Array.from(specHash), new BN(deadline), new BN(1))
  .accounts({
    poster: payer.publicKey,
    config,
    jobEscrow: job,
    escrowTokenAccount: escrowToken,
    posterTokenAccount: posterAta,
    tokenMint: MINT,
    tokenProgram: TOKEN_PROGRAM_ID,
    systemProgram: SystemProgram.programId,
    rent: SYSVAR_RENT_PUBKEY,
  }).rpc();
log({ step:'create_job', ok:true, sig:s1, vaultBal: (await tokenBal(escrowToken)).toString() });
console.log('SIG create_job', s1);

const s2 = await takerProg.methods.acceptJob(Array.from(specHash))
  .accounts({
    taker: taker.publicKey,
    jobEscrow: job,
    poster: payer.publicKey,
  }).rpc();
log({ step:'accept_job', ok:true, sig:s2 });
console.log('SIG accept_job', s2);

const workHash = Buffer.alloc(32, 9); workHash.write('work-1');
const s3 = await takerProg.methods.submitWork(Array.from(workHash), 'ipfs://cov-work-1')
  .accounts({
    taker: taker.publicKey,
    jobEscrow: job,
    poster: payer.publicKey,
  }).rpc();
log({ step:'submit_work', ok:true, sig:s3 });
console.log('SIG submit_work', s3);

// challenge_period is 1 second
await sleep(2500);

const beforeTaker = await tokenBal(takerAta);
const s4 = await prog.methods.finalizePayment()
  .accounts({
    crank: payer.publicKey,
    jobEscrow: job,
    poster: payer.publicKey,
    escrowTokenAccount: escrowToken,
    takerTokenAccount: takerAta,
    taker: taker.publicKey,
    takerReputation: reputation,
    claimListing,
    tokenProgram: TOKEN_PROGRAM_ID,
    systemProgram: SystemProgram.programId,
  }).rpc();
const takerDelta = (await tokenBal(takerAta)) - beforeTaker;
const jobLeft = await conn.getAccountInfo(job);
log({ step:'finalize_payment', ok:true, sig:s4, takerDelta: takerDelta.toString(), jobClosed: !jobLeft });
console.log('SIG finalize_payment', s4);
if (takerDelta !== BigInt(AMOUNT)) throw new Error('taker did not receive '+AMOUNT+' got '+takerDelta);
log({ step:'DONE', ok:true });
process.exit(0);
