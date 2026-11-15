import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram, Ed25519Program, SYSVAR_INSTRUCTIONS_PUBKEY, Transaction, TransactionInstruction, LAMPORTS_PER_SOL } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
import { ed25519 } from '@noble/curves/ed25519';

const { AnchorProvider, Program, Wallet, BN } = anchor;
const TOKEN_PROGRAM_ID = new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA');
const ASSOCIATED_TOKEN_PROGRAM_ID = new PublicKey('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL');
const MINT = new PublicKey('BJMSdujxakjx7qypwfaFCnbkMTNPEYVWTTqnR9eJRL4D');

const idl = JSON.parse(fs.readFileSync('/workspace/deai-work/proof/veedor.json', 'utf8'));
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.env.HOME + '/.config/solana/id.json', 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const providerKp = Keypair.generate();
const verifier = Keypair.generate();
const arbiter = Keypair.generate();
const buyerProg = new Program(idl, new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' }));
const providerProg = new Program(idl, new AnchorProvider(conn, new Wallet(providerKp), { commitment: 'confirmed' }));
const log = (o) => { console.log(JSON.stringify(o)); if (process.env.PROOF_LOG) fs.appendFileSync(process.env.PROOF_LOG, JSON.stringify(o)+'\n'); };

function ata(owner, mint) {
  return PublicKey.findProgramAddressSync(
    [owner.toBuffer(), TOKEN_PROGRAM_ID.toBuffer(), mint.toBuffer()],
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
  const dest = ata(owner, MINT);
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
  const data = Buffer.alloc(9);
  data[0] = 7; // MintTo
  data.writeBigUInt64LE(BigInt(amount), 1);
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
  return BigInt((await conn.getTokenAccountBalance(pk)).value.amount);
}

const jobId = Buffer.alloc(32); jobId.write('veedor-lab-job-1');
const specHash = Buffer.alloc(32, 7);
const evidenceHash = Buffer.alloc(32, 9);
const AMOUNT = 1_000_000n;
const DOMAIN = Buffer.from('agentic-settlement/attestation/v1');
if (DOMAIN.length !== 33) throw new Error('domain length '+DOMAIN.length);
const [jobPda] = PublicKey.findProgramAddressSync([Buffer.from('job'), jobId], programId);
const escrowAta = ata(jobPda, MINT);

const now = Math.floor(Date.now()/1000);
const terms = {
  jobId: Array.from(jobId),
  specHash: Array.from(specHash),
  amount: new BN(AMOUNT.toString()),
  verifier: Array.from(verifier.publicKey.toBytes()),
  arbiter: Array.from(arbiter.publicKey.toBytes()),
  windows: {
    evidenceDeadline: new BN(now + 3600),
    review: new BN(3600),
    arbitration: new BN(3600),
  },
  provider: providerKp.publicKey,
};

log({ step:'setup', program: programId.toBase58(), job: jobPda.toBase58(), buyer: payer.publicKey.toBase58(), provider: providerKp.publicKey.toBase58(), verifier: verifier.publicKey.toBase58(), mint: MINT.toBase58() });

if ((await conn.getBalance(providerKp.publicKey)) < 50_000_000) {
  const sig = await sendIx([
    SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: providerKp.publicKey, lamports: 50_000_000 })
  ], [payer]);
  log({ step:'fund_provider', sig });
}

const buyerAta = await ensureAta(payer.publicKey);
const providerAta = await ensureAta(providerKp.publicKey);
const mintSig = await mintTo(buyerAta, AMOUNT * 2n);
log({ step:'mint_to_buyer', sig: mintSig, buyerAta: buyerAta.toBase58(), providerAta: providerAta.toBase58(), escrowAta: escrowAta.toBase58() });

const s1 = await buyerProg.methods.createJob(terms)
  .accounts({
    buyer: payer.publicKey,
    job: jobPda,
    mint: MINT,
    escrow: escrowAta,
    tokenProgram: TOKEN_PROGRAM_ID,
    associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
    systemProgram: SystemProgram.programId,
  }).rpc();
log({ step:'create_job', ok:true, sig:s1 });
console.log('SIG create_job', s1);

const job1 = await buyerProg.account.job.fetch(jobPda);
log({ step:'after_create', state: job1.state, amount: job1.amount.toString(), buyer: job1.buyer.toBase58() });

const s2 = await buyerProg.methods.fund()
  .accounts({
    buyer: payer.publicKey,
    job: jobPda,
    mint: MINT,
    buyerTokenAccount: buyerAta,
    escrow: escrowAta,
    tokenProgram: TOKEN_PROGRAM_ID,
  }).rpc();
log({ step:'fund', ok:true, sig:s2 });
console.log('SIG fund', s2);
log({ step:'after_fund', escrow: (await tokenBal(escrowAta)).toString() });

const s3 = await providerProg.methods.submitEvidence(Array.from(evidenceHash))
  .accounts({
    provider: providerKp.publicKey,
    job: jobPda,
  }).rpc();
log({ step:'submit_evidence', ok:true, sig:s3 });
console.log('SIG submit_evidence', s3);
log({ step:'after_evidence', state: (await buyerProg.account.job.fetch(jobPda)).state });

try {
  const bad = await buyerProg.methods.release({
    evidenceHash: Array.from(evidenceHash),
    verdict: { pass: {} },
    signature: Array(64).fill(0),
  }).accounts({
    job: jobPda,
    instructionsSysvar: SYSVAR_INSTRUCTIONS_PUBKEY,
    mint: MINT,
    escrow: escrowAta,
    providerTokenAccount: providerAta,
    buyerTokenAccount: buyerAta,
    tokenProgram: TOKEN_PROGRAM_ID,
  }).rpc();
  log({ step:'negative_no_ed25519', ok:false, error:'UNEXPECTED SUCCESS', sig:bad });
  throw new Error('release without ed25519 unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  log({ step:'negative_no_ed25519', expectedFailure:true, error: String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0,240) });
}

const message = Buffer.concat([DOMAIN, jobId, specHash, evidenceHash, Buffer.from([1])]);
if (message.length !== 130) throw new Error('message length '+message.length);
const signature = Buffer.from(ed25519.sign(message, verifier.secretKey.slice(0, 32)));
const edIx = Ed25519Program.createInstructionWithPublicKey({
  publicKey: verifier.publicKey.toBytes(),
  message,
  signature,
});

const beforeProvider = await tokenBal(providerAta);
const s4 = await buyerProg.methods.release({
  evidenceHash: Array.from(evidenceHash),
  verdict: { pass: {} },
  signature: Array.from(signature),
}).accounts({
  job: jobPda,
  instructionsSysvar: SYSVAR_INSTRUCTIONS_PUBKEY,
  mint: MINT,
  escrow: escrowAta,
  providerTokenAccount: providerAta,
  buyerTokenAccount: buyerAta,
  tokenProgram: TOKEN_PROGRAM_ID,
}).preInstructions([edIx]).rpc();
log({ step:'release', ok:true, sig:s4 });
console.log('SIG release', s4);

const afterProvider = await tokenBal(providerAta);
const afterEscrow = await tokenBal(escrowAta);
const job4 = await buyerProg.account.job.fetch(jobPda);
log({ step:'after_release', state: job4.state, providerDelta: (afterProvider - beforeProvider).toString(), escrow: afterEscrow.toString() });
if (afterProvider - beforeProvider !== AMOUNT) {
  throw new Error('provider did not receive amount, got '+(afterProvider-beforeProvider));
}
log({ step:'DONE', ok:true });
