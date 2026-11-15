import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram, SYSVAR_RENT_PUBKEY } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;

const TOKEN_PROGRAM_ID = new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA');
const ASSOCIATED_TOKEN_PROGRAM_ID = new PublicKey('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL');

const pipeIdl = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const mockIdl = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const admin = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[4], 'utf8'))));
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[5], 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
const pipeId = new PublicKey(pipeIdl.address);
const mockId = new PublicKey(mockIdl.address);
const conn = new Connection(rpc, 'confirmed');
const adminPipe = new Program(pipeIdl, new AnchorProvider(conn, new Wallet(admin), { commitment: 'confirmed' }));
const payerPipe = new Program(pipeIdl, new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' }));
const adminMock = new Program(mockIdl, new AnchorProvider(conn, new Wallet(admin), { commitment: 'confirmed' }));
const payerMock = new Program(mockIdl, new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' }));
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

const IN = new PublicKey('BJMSdujxakjx7qypwfaFCnbkMTNPEYVWTTqnR9eJRL4D');
const OUT = new PublicKey('7xP1NAVvBMso44cQj6pLU86zJC159FAxsbAoPjbWh3jm');
const STAGING = new PublicKey('4uVMKC2maMbRyHcAroqv8TcgkiiDCHP9FMaRrDBuECZ9');
const POOL_OUT = new PublicKey('DswigQpL5wLpMu4jDfzLZfp1rT8rBvxWaq4s9thYr52t');
const POOL_IN = new PublicKey('3R1crAP6fC5MqHPs6J5drLv7EgV4tXPyxtYXY5nXEuFv');
const [poolAuth] = PublicKey.findProgramAddressSync([Buffer.from('pool_authority')], mockId);
const taskId = [...Buffer.alloc(32, 0xa5)];
const [commitment] = PublicKey.findProgramAddressSync([Buffer.from('commitment'), Buffer.from(taskId)], pipeId);
const escrowAta = ata(commitment, IN);
const outputAta = ata(commitment, OUT);
const payerIn = ata(payer.publicKey, IN);
const payerOut = ata(payer.publicKey, OUT);
const AMOUNT = new BN(1_000_000);

log({ step:'setup', pipe: pipeId.toBase58(), mock: mockId.toBase58(), commitment: commitment.toBase58(), escrowAta: escrowAta.toBase58(), outputAta: outputAta.toBase58(), staging: STAGING.toBase58(), poolAuth: poolAuth.toBase58() });

const slot = await conn.getSlot('confirmed');
log({ step:'slot', slot });

// seed mock pool
const s0 = await adminMock.methods.initializeMockPool(new BN(10_000_000))
  .accounts({
    payer: admin.publicKey,
    outputMint: OUT,
    mockPoolOutputVault: POOL_OUT,
    poolAuthority: poolAuth,
    tokenProgram: TOKEN_PROGRAM_ID,
  }).rpc();
log({ step:'initialize_mock_pool', ok:true, sig:s0 });
console.log('SIG initialize_mock_pool', s0);

const beforeIn = await tokenBal(payerIn);
const beforeOut = await tokenBal(payerOut);
log({ step:'balances_before', payerIn: beforeIn.toString(), payerOut: beforeOut.toString() });

const sig1 = await payerPipe.methods.createCommitment(
    taskId, payer.publicKey, AMOUNT, AMOUNT, new BN(slot + 100000), STAGING
  ).accounts({
    payer: payer.publicKey,
    executorAgent: payer.publicKey,
    inputToken: IN,
    outputToken: OUT,
    commitment,
    escrowAta,
    outputAta,
    payerInputAta: payerIn,
    systemProgram: SystemProgram.programId,
    tokenProgram: TOKEN_PROGRAM_ID,
    associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
  }).rpc();
log({ step:'create_commitment', ok:true, sig:sig1 });
console.log('SIG create_commitment', sig1);

const sig2 = await adminPipe.methods.withdrawForSwap()
  .accounts({
    settler: admin.publicKey,
    commitment,
    escrowAta,
    swapStagingAta: STAGING,
    tokenProgram: TOKEN_PROGRAM_ID,
  }).rpc();
log({ step:'withdraw_for_swap', ok:true, sig:sig2 });
console.log('SIG withdraw_for_swap', sig2);

const sig3 = await payerMock.methods.mockSwapExecute(AMOUNT)
  .accounts({
    swapStagingAta: STAGING,
    stagingAuthority: payer.publicKey,
    mockPoolInputVault: POOL_IN,
    mockPoolOutputVault: POOL_OUT,
    poolAuthority: poolAuth,
    outputAta,
    tokenProgram: TOKEN_PROGRAM_ID,
  }).rpc();
log({ step:'mock_swap_execute', ok:true, sig:sig3 });
console.log('SIG mock_swap_execute', sig3);

const outAmt = await tokenBal(outputAta);
log({ step:'output_ata_after_swap', amount: outAmt.toString() });

const sig4 = await payerPipe.methods.submitProof([...Buffer.alloc(64, 1)], new BN(slot), new BN(outAmt.toString()))
  .accounts({
    worker: payer.publicKey,
    commitment,
    outputAta,
  }).rpc();
log({ step:'submit_proof', ok:true, sig:sig4 });
console.log('SIG submit_proof', sig4);

const mid = await payerPipe.account.commitment.fetch(commitment);
log({ step:'after_proof', status: mid.status, verified: mid.verified });

const sig5 = await adminPipe.methods.release()
  .accounts({
    settler: admin.publicKey,
    commitment,
    payer: payer.publicKey,
    escrowAta,
    outputAta,
    payerOutputAta: payerOut,
    tokenProgram: TOKEN_PROGRAM_ID,
    payerInputAta: payerIn,
  }).rpc();
log({ step:'release', ok:true, sig:sig5 });
console.log('SIG release', sig5);

const afterIn = await tokenBal(payerIn);
const afterOut = await tokenBal(payerOut);
const acc = await payerPipe.account.commitment.fetch(commitment);
log({
  step:'fetch', ok:true, status: acc.status, verified: acc.verified,
  after: { payerIn: afterIn.toString(), payerOut: afterOut.toString() },
  deltas: { payerIn: (afterIn-beforeIn).toString(), payerOut: (afterOut-beforeOut).toString() },
});
if (!acc.status.released) throw new Error('expected released, got '+JSON.stringify(acc.status));
if ((afterOut-beforeOut) !== 1_000_000n) throw new Error('payer output expected +1000000, got '+(afterOut-beforeOut));

try {
  const s = await payerPipe.methods.createCommitment(
      taskId, payer.publicKey, new BN(0), AMOUNT, new BN(slot + 100000), STAGING
    ).accounts({
      payer: payer.publicKey,
      executorAgent: payer.publicKey,
      inputToken: IN,
      outputToken: OUT,
      commitment,
      escrowAta,
      outputAta,
      payerInputAta: payerIn,
      systemProgram: SystemProgram.programId,
      tokenProgram: TOKEN_PROGRAM_ID,
      associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
    }).rpc();
  log({ step:'negative_zero_or_reuse', ok:false, error:'UNEXPECTED SUCCESS', sig:s });
  throw new Error('unexpected success');
} catch (e) {
  if (String(e.message).includes('unexpected success')) throw e;
  log({ step:'negative_recreate_or_zero', expectedFailure:true, error: String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0,240) });
}

process.exit(0);
