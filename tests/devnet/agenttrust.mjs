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

const agent = payer.publicKey; // agent is just a referenced pubkey
const typ = 'campus-scout';
const [credential] = PublicKey.findProgramAddressSync(
  [Buffer.from('credential'), agent.toBuffer(), Buffer.from(typ)],
  programId
);
log({ step:'setup', program: programId.toBase58(), agent: agent.toBase58(), credential: credential.toBase58() });

const tooLong = 'x'.repeat(33);
try {
  const [c2] = PublicKey.findProgramAddressSync([Buffer.from('credential'), agent.toBuffer(), Buffer.from(tooLong)], programId);
  const s = await program.methods.issueCredential(tooLong).accounts({
    credential: c2, agent, issuer: payer.publicKey, systemProgram: SystemProgram.programId,
  }).rpc();
  log({ step:'issue_credential_too_long', ok:false, error:'UNEXPECTED SUCCESS', sig:s });
  throw new Error('too-long type unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  const msg = String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0, 240);
  log({ step:'issue_credential_too_long', expectedFailure:true, error: msg });
}

const sig = await program.methods.issueCredential(typ).accounts({
  credential, agent, issuer: payer.publicKey, systemProgram: SystemProgram.programId,
}).rpc();
log({ step:'issue_credential', ok:true, sig });
console.log('SIG issue_credential', sig);
const rec = await program.account.credential.fetch(credential);
log({ step:'fetch_credential', ok:true, agent: rec.agent.toBase58(), issuer: rec.issuer.toBase58(), credentialType: rec.credentialType, revoked: rec.revoked });
if (rec.credentialType !== typ) throw new Error('type mismatch');
if (rec.revoked) throw new Error('should not be revoked');

const sig2 = await program.methods.getCredential().accounts({ credential }).rpc();
log({ step:'get_credential', ok:true, sig: sig2 });
console.log('SIG get_credential', sig2);

const sig3 = await program.methods.revokeCredential().accounts({ credential, issuer: payer.publicKey }).rpc();
log({ step:'revoke_credential', ok:true, sig: sig3 });
console.log('SIG revoke_credential', sig3);
const rec2 = await program.account.credential.fetch(credential);
log({ step:'fetch_revoked', ok:true, revoked: rec2.revoked });
if (!rec2.revoked) throw new Error('expected revoked');

try {
  const s = await program.methods.getCredential().accounts({ credential }).rpc();
  log({ step:'get_credential_revoked', ok:false, error:'UNEXPECTED SUCCESS', sig:s });
  throw new Error('get revoked unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  const msg = String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0, 240);
  log({ step:'get_credential_revoked', expectedFailure:true, error: msg });
}

try {
  const s = await program.methods.revokeCredential().accounts({ credential, issuer: payer.publicKey }).rpc();
  log({ step:'revoke_twice', ok:false, error:'UNEXPECTED SUCCESS', sig:s });
  throw new Error('second revoke unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  const msg = String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0, 240);
  log({ step:'revoke_twice', expectedFailure:true, error: msg });
}

process.exit(0);
