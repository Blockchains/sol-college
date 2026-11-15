import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram, SYSVAR_RENT_PUBKEY } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;

const TOKEN_PROGRAM_ID = new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA');
const ASSOCIATED_TOKEN_PROGRAM_ID = new PublicKey('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL');

const idl = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const admin = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[3], 'utf8'))));
const client = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[4], 'utf8'))));
const providerKp = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[5], 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const program = new Program(idl, new AnchorProvider(conn, new Wallet(admin), { commitment: 'confirmed' }));
const clientProg = new Program(idl, new AnchorProvider(conn, new Wallet(client), { commitment: 'confirmed' }));
const log = (o) => { console.log(JSON.stringify(o)); if (process.env.PROOF_LOG) fs.appendFileSync(process.env.PROOF_LOG, JSON.stringify(o)+'\n'); };

function ata(owner, mint) {
  return PublicKey.findProgramAddressSync(
    [owner.toBuffer(), TOKEN_PROGRAM_ID.toBuffer(), mint.toBuffer()],
    ASSOCIATED_TOKEN_PROGRAM_ID
  )[0];
}
async function tokenBal(pk) {
  return BigInt((await conn.getTokenAccountBalance(pk)).value.amount);
}

const MINT = new PublicKey('BJMSdujxakjx7qypwfaFCnbkMTNPEYVWTTqnR9eJRL4D');
const TREASURY = new PublicKey('En7DGt8B4LtuH2cwBMRofhdhgAJv18uGaDZDqCthS3QU');
const AMOUNT = new BN(1_000_000);
const [config] = PublicKey.findProgramAddressSync([Buffer.from('config')], programId);
const clientAta = ata(client.publicKey, MINT);
const providerAta = ata(providerKp.publicKey, MINT);
const treasuryAta = ata(TREASURY, MINT);

log({ step:'setup', program: programId.toBase58(), config: config.toBase58(), client: client.publicKey.toBase58(), provider: providerKp.publicKey.toBase58(), evaluator: admin.publicKey.toBase58() });

const existingCfg = await conn.getAccountInfo(config);
if (!existingCfg) {
  const s = await program.methods.initialize(50)
    .accounts({
      admin: admin.publicKey,
      config,
      paymentMint: MINT,
      treasury: TREASURY,
      systemProgram: SystemProgram.programId,
    }).rpc();
  log({ step:'initialize', ok:true, sig:s });
  console.log('SIG initialize', s);
} else {
  log({ step:'initialize', skipped:true });
}

const cfg = await program.account.platformConfig.fetch(config);
const jobIdBuf = cfg.jobCounter.toArrayLike(Buffer, 'le', 8);
const [job] = PublicKey.findProgramAddressSync([Buffer.from('job'), config.toBuffer(), jobIdBuf], programId);
const [vault] = PublicKey.findProgramAddressSync([Buffer.from('vault'), job.toBuffer()], programId);
log({ step:'pdas', jobId: cfg.jobCounter.toString(), job: job.toBase58(), vault: vault.toBase58(), feeBps: cfg.feeBps });

const beforeClient = await tokenBal(clientAta);
const beforeProv = await tokenBal(providerAta);
const beforeTreas = await tokenBal(treasuryAta);
log({ step:'balances_before', client: beforeClient.toString(), provider: beforeProv.toString(), treasury: beforeTreas.toString() });

const expiredAt = new BN(Math.floor(Date.now()/1000) + 86400);
const sig1 = await clientProg.methods.createJob(providerKp.publicKey, admin.publicKey, expiredAt, 'campus-scout job', PublicKey.default)
  .accounts({
    client: client.publicKey,
    config,
    job,
    vault,
    paymentMint: MINT,
    tokenProgram: TOKEN_PROGRAM_ID,
    systemProgram: SystemProgram.programId,
    rent: SYSVAR_RENT_PUBKEY,
  }).rpc();
log({ step:'create_job', ok:true, sig:sig1 });
console.log('SIG create_job', sig1);

const sig2 = await clientProg.methods.setBudget(AMOUNT, Buffer.from([]))
  .accounts({ caller: client.publicKey, job }).rpc();
log({ step:'set_budget', ok:true, sig:sig2 });
console.log('SIG set_budget', sig2);

const sig3 = await clientProg.methods.fund(AMOUNT, Buffer.from([]))
  .accounts({
    client: client.publicKey,
    job,
    clientToken: clientAta,
    vault,
    tokenProgram: TOKEN_PROGRAM_ID,
  }).rpc();
log({ step:'fund', ok:true, sig:sig3 });
console.log('SIG fund', sig3);

const sig4 = await new Program(idl, new AnchorProvider(conn, new Wallet(providerKp), { commitment: 'confirmed' }))
  .methods.submit([...Buffer.alloc(32, 9)], Buffer.from([]))
  .accounts({ provider: providerKp.publicKey, job }).rpc();
log({ step:'submit', ok:true, sig:sig4 });
console.log('SIG submit', sig4);

const sig5 = await program.methods.complete([...Buffer.alloc(32, 11)], Buffer.from([]))
  .accounts({
    evaluator: admin.publicKey,
    job,
    config,
    paymentMint: MINT,
    vault,
    providerToken: providerAta,
    provider: providerKp.publicKey,
    treasuryToken: treasuryAta,
    treasury: TREASURY,
    tokenProgram: TOKEN_PROGRAM_ID,
    associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
    systemProgram: SystemProgram.programId,
  }).rpc();
log({ step:'complete', ok:true, sig:sig5 });
console.log('SIG complete', sig5);

const afterClient = await tokenBal(clientAta);
const afterProv = await tokenBal(providerAta);
const afterTreas = await tokenBal(treasuryAta);
let vaultAmt;
try { vaultAmt = (await conn.getTokenAccountBalance(vault)).value.amount; } catch (e) { vaultAmt = 'err'; }
const jobAcc = await program.account.job.fetch(job);
log({
  step:'fetch', ok:true, status: jobAcc.status, jobId: jobAcc.jobId.toString(), budget: jobAcc.budget.toString(),
  description: jobAcc.description,
  after: { client: afterClient.toString(), provider: afterProv.toString(), treasury: afterTreas.toString(), vault: vaultAmt },
  deltas: {
    client: (afterClient-beforeClient).toString(),
    provider: (afterProv-beforeProv).toString(),
    treasury: (afterTreas-beforeTreas).toString(),
  },
});
if (!jobAcc.status.completed) throw new Error('expected completed, got '+JSON.stringify(jobAcc.status));
if ((afterProv-beforeProv) !== 995000n) throw new Error('provider payout expected 995000, got '+(afterProv-beforeProv));
if ((afterTreas-beforeTreas) !== 5000n) throw new Error('treasury fee expected 5000, got '+(afterTreas-beforeTreas));

// negative: set_budget 0 while Open is already Completed — use initialize FeeTooHigh instead, or create_job with empty evaluator
try {
  const s = await program.methods.initialize(2000)
    .accounts({
      admin: admin.publicKey,
      config,
      paymentMint: MINT,
      treasury: TREASURY,
      systemProgram: SystemProgram.programId,
    }).rpc();
  log({ step:'negative_reinit', ok:false, error:'UNEXPECTED SUCCESS', sig:s });
  throw new Error('reinit unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  log({ step:'negative_reinit', expectedFailure:true, error: String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0,240) });
}

process.exit(0);
