import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { Connection, Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const idlPath = process.argv[2] || path.join(__dirname, 'mandatekey.json');
const payerPath = process.argv[3] || path.join(process.env.HOME, '.config/solana/id.json');
const rpcPath = path.join(process.env.HOME, '.config/solana/cli/config.yml');
const yaml = fs.readFileSync(rpcPath, 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
if (!rpc) throw new Error('no rpc in solana config');

const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(payerPath, 'utf8'))));
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8'));
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const provider = new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' });
const program = new Program(idl, provider);
const log = (o) => { console.log(JSON.stringify(o)); fs.appendFileSync(process.env.PROOF_LOG || '/tmp/mandatekey-proof.jsonl', JSON.stringify(o)+'\n'); };

const agent = Keypair.generate();
const mandateId = new BN(Date.now() % 1e9);
const now = Math.floor(Date.now()/1000);
const args = {
  agent: agent.publicKey,
  mandateId,
  cosigner: null,
  validFrom: new BN(now - 30),
  expiresAt: new BN(now + 30*24*3600),
  intentHash: Array(32).fill(0),
  tokenLimits: [],
  destinationAllowlist: [],
  allowAnyDestination: true,
};

const [mandatePda] = PublicKey.findProgramAddressSync(
  [Buffer.from('mandate'), payer.publicKey.toBuffer(), agent.publicKey.toBuffer(), mandateId.toArrayLike(Buffer, 'le', 8)],
  programId
);

log({ step: 'setup', program: programId.toBase58(), owner: payer.publicKey.toBase58(), agent: agent.publicKey.toBase58(), mandateId: mandateId.toString(), mandate: mandatePda.toBase58() });

// create_mandate
const sig = await program.methods.createMandate(args).accounts({
  owner: payer.publicKey,
  mandate: mandatePda,
  systemProgram: SystemProgram.programId,
}).rpc();
log({ step: 'create_mandate', ok: true, sig });
console.log('SIG create_mandate', sig);

const acc = await program.account.mandate.fetch(mandatePda);
log({ step: 'fetch_mandate', ok: true, owner: acc.owner.toBase58(), agent: acc.agent.toBase58(), revoked: acc.revoked, paymentCount: acc.paymentCount.toString() });

// negative: invalid window (expires_at <= valid_from)
const badId = mandateId.add(new BN(1));
const [badPda] = PublicKey.findProgramAddressSync(
  [Buffer.from('mandate'), payer.publicKey.toBuffer(), agent.publicKey.toBuffer(), badId.toArrayLike(Buffer, 'le', 8)],
  programId
);
try {
  const s = await program.methods.createMandate({
    ...args,
    mandateId: badId,
    validFrom: new BN(now + 1000),
    expiresAt: new BN(now),
  }).accounts({ owner: payer.publicKey, mandate: badPda, systemProgram: SystemProgram.programId }).rpc();
  log({ step: 'create_mandate_invalid_window', ok: false, error: 'UNEXPECTED SUCCESS', sig: s });
} catch (e) {
  const msg = String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0, 240);
  log({ step: 'create_mandate_invalid_window', expectedFailure: true, error: msg });
}

// revoke
const sig2 = await program.methods.revoke().accounts({
  owner: payer.publicKey,
  mandate: mandatePda,
}).rpc();
log({ step: 'revoke', ok: true, sig: sig2 });
console.log('SIG revoke', sig2);
const acc2 = await program.account.mandate.fetch(mandatePda);
log({ step: 'fetch_after_revoke', ok: true, revoked: acc2.revoked });
