import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram, SYSVAR_RENT_PUBKEY } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;

const TOKEN_PROGRAM_ID = new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA');
const ASSOCIATED_TOKEN_PROGRAM_ID = new PublicKey('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL');

const idl = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[3], 'utf8'))));
const providerKp = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[4], 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const program = new Program(idl, new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' }));
const log = (o) => { console.log(JSON.stringify(o)); if (process.env.PROOF_LOG) fs.appendFileSync(process.env.PROOF_LOG, JSON.stringify(o)+'\n'); };

function ata(owner, m) {
  return PublicKey.findProgramAddressSync(
    [owner.toBuffer(), TOKEN_PROGRAM_ID.toBuffer(), m.toBuffer()],
    ASSOCIATED_TOKEN_PROGRAM_ID
  )[0];
}
async function tokenBal(pk) {
  const info = await conn.getTokenAccountBalance(pk);
  return BigInt(info.value.amount);
}

const MINT = new PublicKey('BJMSdujxakjx7qypwfaFCnbkMTNPEYVWTTqnR9eJRL4D');
const TREASURY = new PublicKey('En7DGt8B4LtuH2cwBMRofhdhgAJv18uGaDZDqCthS3QU');
const AMOUNT = new BN(1_000_000);
const [escrow] = PublicKey.findProgramAddressSync([payer.publicKey.toBuffer(), Buffer.from('escrow')], programId);
const [vault] = PublicKey.findProgramAddressSync([escrow.toBuffer(), Buffer.from('vault')], programId);
const payerAta = ata(payer.publicKey, MINT);
const providerAta = ata(providerKp.publicKey, MINT);
const treasuryAta = ata(TREASURY, MINT);

const existing = await conn.getAccountInfo(escrow);
log({ step:'setup', program: programId.toBase58(), escrow: escrow.toBase58(), vault: vault.toBase58(), existing: !!existing, payerAta: payerAta.toBase58(), providerAta: providerAta.toBase58(), treasuryAta: treasuryAta.toBase58() });

const deadline = new BN(Math.floor(Date.now()/1000) + 86400);
const taskHash = [...Buffer.alloc(32, 7)];
const beforePayer = await tokenBal(payerAta);
const beforeProv = await tokenBal(providerAta);
const beforeTreas = await tokenBal(treasuryAta);
log({ step:'balances_before', payer: beforePayer.toString(), provider: beforeProv.toString(), treasury: beforeTreas.toString() });

if (!existing) {
  const sig1 = await program.methods.createEscrow(providerKp.publicKey, MINT, AMOUNT, deadline, taskHash)
    .accounts({
      payer: payer.publicKey,
      escrow,
      systemProgram: SystemProgram.programId,
      rent: SYSVAR_RENT_PUBKEY,
    }).rpc();
  log({ step:'create_escrow', ok:true, sig: sig1 });
  console.log('SIG create_escrow', sig1);
}

const sig2 = await program.methods.fundEscrow()
  .accounts({
    payer: payer.publicKey,
    escrow,
    payerTokenAccount: payerAta,
    vault,
    tokenMint: MINT,
    tokenProgram: TOKEN_PROGRAM_ID,
    systemProgram: SystemProgram.programId,
    rent: SYSVAR_RENT_PUBKEY,
  }).rpc();
log({ step:'fund_escrow', ok:true, sig: sig2 });
console.log('SIG fund_escrow', sig2);

const sig3 = await program.methods.startWork()
  .accounts({ provider: providerKp.publicKey, escrow })
  .signers([providerKp])
  .rpc();
log({ step:'start_work', ok:true, sig: sig3 });
console.log('SIG start_work', sig3);

const sig4 = await program.methods.submitWork()
  .accounts({ provider: providerKp.publicKey, escrow })
  .signers([providerKp])
  .rpc();
log({ step:'submit_work', ok:true, sig: sig4 });
console.log('SIG submit_work', sig4);

const sig5 = await program.methods.confirmCompletion()
  .accounts({
    payer: payer.publicKey,
    escrow,
    vault,
    providerTokenAccount: providerAta,
    treasuryTokenAccount: treasuryAta,
    tokenProgram: TOKEN_PROGRAM_ID,
  }).rpc();
log({ step:'confirm_completion', ok:true, sig: sig5 });
console.log('SIG confirm_completion', sig5);

const afterPayer = await tokenBal(payerAta);
const afterProv = await tokenBal(providerAta);
const afterTreas = await tokenBal(treasuryAta);
let vaultAmt = null;
try { vaultAmt = (await conn.getTokenAccountBalance(vault)).value.amount; } catch (e) { vaultAmt = 'err:' + String(e.message||e).slice(0,80); }
const acc = await program.account.escrow.fetch(escrow);
log({
  step:'fetch',
  ok:true,
  state: acc.state,
  amount: acc.amount.toString(),
  feeBps: acc.feeBps,
  providerSubmitted: acc.providerSubmitted,
  after: { payer: afterPayer.toString(), provider: afterProv.toString(), treasury: afterTreas.toString(), vault: vaultAmt },
  deltas: {
    payer: (afterPayer - beforePayer).toString(),
    provider: (afterProv - beforeProv).toString(),
    treasury: (afterTreas - beforeTreas).toString(),
  },
});
if (!acc.state.released) throw new Error('expected released, got ' + JSON.stringify(acc.state));
if ((afterProv - beforeProv) !== 995000n) throw new Error('provider payout expected 995000, got ' + (afterProv - beforeProv).toString());
if ((afterTreas - beforeTreas) !== 5000n) throw new Error('treasury fee expected 5000, got ' + (afterTreas - beforeTreas).toString());

try {
  const s = await program.methods.createEscrow(providerKp.publicKey, MINT, AMOUNT, deadline, taskHash)
    .accounts({
      payer: payer.publicKey,
      escrow,
      systemProgram: SystemProgram.programId,
      rent: SYSVAR_RENT_PUBKEY,
    }).rpc();
  log({ step:'negative_recreate', ok:false, error:'UNEXPECTED SUCCESS', sig:s });
  throw new Error('recreate unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  log({ step:'negative_recreate', expectedFailure:true, error: String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0,240) });
}

process.exit(0);
