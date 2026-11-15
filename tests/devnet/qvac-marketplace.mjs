import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet } = anchor;
const idl = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[3], 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const program = new Program(idl, new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' }));
const log = (o) => { console.log(JSON.stringify(o)); fs.appendFileSync(process.env.PROOF_LOG, JSON.stringify(o)+'\n'); };

const [providerPda] = PublicKey.findProgramAddressSync([Buffer.from('provider'), payer.publicKey.toBuffer()], programId);
const peer = Array.from({length:32}, (_,i)=> i+1);
log({ step:'setup', program: programId.toBase58(), authority: payer.publicKey.toBase58(), provider: providerPda.toBase58() });

try {
  const s = await program.methods.registerProvider('x', 1, peer).accounts({
    provider: providerPda, authority: payer.publicKey, systemProgram: SystemProgram.programId,
  }).rpc();
  log({ step:'register_provider_name_short', ok:false, error:'UNEXPECTED SUCCESS', sig:s });
  throw new Error('short name unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  const msg = String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0, 240);
  log({ step:'register_provider_name_short', expectedFailure:true, error: msg });
}

const sig = await program.methods.registerProvider('campus-scout', 1, peer).accounts({
  provider: providerPda, authority: payer.publicKey, systemProgram: SystemProgram.programId,
}).rpc();
log({ step:'register_provider', ok:true, sig });
console.log('SIG register_provider', sig);
const p = await program.account.provider.fetch(providerPda);
log({ step:'fetch_provider', ok:true, authority: p.authority.toBase58(), name: p.name, taskTypes: p.taskTypes, jobsCompleted: p.jobsCompleted.toString() });
if (p.name !== 'campus-scout') throw new Error('name mismatch');

const sig2 = await program.methods.updateProvider('campus-scout-v2', 3).accounts({
  provider: providerPda, authority: payer.publicKey,
}).rpc();
log({ step:'update_provider', ok:true, sig: sig2 });
console.log('SIG update_provider', sig2);
const p2 = await program.account.provider.fetch(providerPda);
log({ step:'fetch_after_update', ok:true, name: p2.name, taskTypes: p2.taskTypes });
if (p2.name !== 'campus-scout-v2') throw new Error('update name mismatch');

try {
  const s = await program.methods.registerProvider('campus-scout', 1, peer).accounts({
    provider: providerPda, authority: payer.publicKey, systemProgram: SystemProgram.programId,
  }).rpc();
  log({ step:'register_provider_twice', ok:false, error:'UNEXPECTED SUCCESS', sig:s });
  throw new Error('second register unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  const msg = String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0, 240);
  log({ step:'register_provider_twice', expectedFailure:true, error: msg });
}

process.exit(0);
