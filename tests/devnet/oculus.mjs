import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { Connection, Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const idlPath = process.argv[2] || path.join(__dirname, '../../dapps/build/oculus/oculus_policy.json');
const payerPath = process.argv[3] || path.join(process.env.HOME, '.config/solana/id.json');
const yaml = fs.readFileSync(path.join(process.env.HOME, '.config/solana/cli/config.yml'), 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
if (!rpc) throw new Error('no rpc in solana config');

const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(payerPath, 'utf8'))));
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8'));
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const provider = new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' });
const program = new Program(idl, provider);
const log = (o) => { console.log(JSON.stringify(o)); fs.appendFileSync(process.env.PROOF_LOG || '/tmp/oculus-proof.jsonl', JSON.stringify(o)+'\n'); };

const agent = Keypair.generate();
const [policy] = PublicKey.findProgramAddressSync([Buffer.from('policy'), agent.publicKey.toBuffer()], programId);
log({ step: 'setup', program: programId.toBase58(), owner: payer.publicKey.toBase58(), agent: agent.publicKey.toBase58(), policy: policy.toBase58() });

try {
  const s = await program.methods.initPolicy(agent.publicKey, new BN(1_000_000), 30).accounts({
    policy, owner: payer.publicKey, systemProgram: SystemProgram.programId,
  }).rpc();
  log({ step: 'init_policy_invalid_window', ok: false, error: 'UNEXPECTED SUCCESS', sig: s });
  throw new Error('invalid window unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  const msg = String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0, 240);
  log({ step: 'init_policy_invalid_window', expectedFailure: true, error: msg });
}

const sig = await program.methods.initPolicy(agent.publicKey, new BN(1_000_000), 3600).accounts({
  policy, owner: payer.publicKey, systemProgram: SystemProgram.programId,
}).rpc();
log({ step: 'init_policy', ok: true, sig });
console.log('SIG init_policy', sig);

const p0 = await program.account.policy.fetch(policy);
log({ step: 'fetch_policy', ok: true, owner: p0.owner.toBase58(), agent: p0.agent.toBase58(), dailyLimitUsdc: p0.dailyLimitUsdc.toString(), windowSeconds: p0.windowSeconds, spentWindow: p0.spentWindow.toString(), paused: p0.paused });
if (p0.agent.toBase58() !== agent.publicKey.toBase58()) throw new Error('agent mismatch');

const memo = Array(32).fill(0);
const sig2 = await program.methods.checkSpend(new BN(100), memo).accounts({
  policy, agent: agent.publicKey,
}).signers([agent]).rpc();
log({ step: 'check_spend', ok: true, sig: sig2 });
console.log('SIG check_spend', sig2);
const p1 = await program.account.policy.fetch(policy);
log({ step: 'fetch_after_spend', ok: true, spentWindow: p1.spentWindow.toString() });
if (p1.spentWindow.toString() !== '100') throw new Error('spent_window mismatch');

try {
  const s = await program.methods.checkSpend(new BN(1_000_000), memo).accounts({
    policy, agent: agent.publicKey,
  }).signers([agent]).rpc();
  log({ step: 'check_spend_over_limit', ok: false, error: 'UNEXPECTED SUCCESS', sig: s });
  throw new Error('over-limit spend unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  const msg = String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0, 240);
  log({ step: 'check_spend_over_limit', expectedFailure: true, error: msg });
}

const sig3 = await program.methods.pauseAgent(1).accounts({ policy, owner: payer.publicKey }).rpc();
log({ step: 'pause_agent', ok: true, sig: sig3 });
console.log('SIG pause_agent', sig3);
const p2 = await program.account.policy.fetch(policy);
log({ step: 'fetch_after_pause', ok: true, paused: p2.paused, pauseReason: p2.pauseReason });
if (!p2.paused) throw new Error('not paused');

try {
  const s = await program.methods.checkSpend(new BN(10), memo).accounts({
    policy, agent: agent.publicKey,
  }).signers([agent]).rpc();
  log({ step: 'check_spend_paused', ok: false, error: 'UNEXPECTED SUCCESS', sig: s });
  throw new Error('paused spend unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  const msg = String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0, 240);
  log({ step: 'check_spend_paused', expectedFailure: true, error: msg });
}

const sig4 = await program.methods.closePolicy().accounts({ policy, owner: payer.publicKey }).rpc();
log({ step: 'close_policy', ok: true, sig: sig4 });
console.log('SIG close_policy', sig4);
const closed = await conn.getAccountInfo(policy);
log({ step: 'fetch_after_close', ok: true, closed: !closed });
if (closed) throw new Error('policy still exists after close');
process.exit(0);
