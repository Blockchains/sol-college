import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { Connection, Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const idlPath = process.argv[2] || path.join(__dirname, '../../dapps/build/agentx/agentx.json');
const payerPath = process.argv[3] || path.join(process.env.HOME, '.config/solana/id.json');
const yaml = fs.readFileSync(path.join(process.env.HOME, '.config/solana/cli/config.yml'), 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
if (!rpc) throw new Error('no rpc in solana config');
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(payerPath, 'utf8'))));
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8'));
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const program = new Program(idl, new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' }));
const log = (o) => { console.log(JSON.stringify(o)); fs.appendFileSync(process.env.PROOF_LOG || '/tmp/agentx-proof.jsonl', JSON.stringify(o)+'\n'); };

const [registry] = PublicKey.findProgramAddressSync([Buffer.from('registry')], programId);
const agentId = Array.from(Buffer.from(('id'+Date.now()).slice(-8)));
const [agentAccount] = PublicKey.findProgramAddressSync([Buffer.from('agent'), payer.publicKey.toBuffer(), Buffer.from(agentId)], programId);
log({ step:'setup', program: programId.toBase58(), registry: registry.toBase58(), agentAccount: agentAccount.toBase58() });

if (!(await conn.getAccountInfo(registry))) {
  const sig = await program.methods.initializeRegistry().accounts({
    registry, agxMint: payer.publicKey, authority: payer.publicKey, systemProgram: SystemProgram.programId,
  }).rpc();
  log({ step:'initialize_registry', ok:true, sig });
} else {
  log({ step:'initialize_registry', alreadyInitialized:true });
}
const sig2 = await program.methods.registerAgent(agentId, 'campus-scout', 'grok-bot').accounts({
  agentAccount, registry, owner: payer.publicKey, systemProgram: SystemProgram.programId,
}).rpc();
log({ step:'register_agent', ok:true, sig: sig2 });
const a0 = await program.account.agentAccount.fetch(agentAccount);
log({ step:'fetch_agent', ok:true, name: a0.name, status: a0.status });
if (a0.name !== 'campus-scout') throw new Error('name mismatch');

const nonce = new BN(1);
const [taskPda] = PublicKey.findProgramAddressSync([Buffer.from('task'), agentAccount.toBuffer(), nonce.toArrayLike(Buffer,'le',8)], programId);
try {
  const s = await program.methods.executeTask(nonce, Array(32).fill(1), 'should fail', new BN(0), true).accounts({
    taskAccount: taskPda, agentAccount, registry, oracle: payer.publicKey, systemProgram: SystemProgram.programId,
  }).rpc();
  log({ step:'execute_task_inactive', ok:false, error:'UNEXPECTED SUCCESS', sig:s });
  throw new Error('inactive execute unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  const msg = String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0,240);
  log({ step:'execute_task_inactive', expectedFailure:true, error: msg });
}

const sig3 = await program.methods.updateState({ active: {} }).accounts({ agentAccount, owner: payer.publicKey }).rpc();
log({ step:'update_state_active', ok:true, sig: sig3 });
const sig4 = await program.methods.executeTask(nonce, Array(32).fill(7), 'devnet proof task', new BN(42), true).accounts({
  taskAccount: taskPda, agentAccount, registry, oracle: payer.publicKey, systemProgram: SystemProgram.programId,
}).rpc();
log({ step:'execute_task', ok:true, sig: sig4 });
const a2 = await program.account.agentAccount.fetch(agentAccount);
log({ step:'fetch_after_task', ok:true, tasksCompleted: a2.tasksCompleted.toString(), totalRewards: a2.totalRewards.toString() });
if (a2.tasksCompleted.toString() !== '1') throw new Error('tasks_completed mismatch');
const sig5 = await program.methods.deactivateAgent().accounts({ agentAccount, owner: payer.publicKey }).rpc();
log({ step:'deactivate_agent', ok:true, sig: sig5 });
try {
  const s = await program.methods.updateState({ active: {} }).accounts({ agentAccount, owner: payer.publicKey }).rpc();
  log({ step:'update_state_after_deactivate', ok:false, error:'UNEXPECTED SUCCESS', sig:s });
  throw new Error('reactivate unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  const msg = String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0,240);
  log({ step:'update_state_after_deactivate', expectedFailure:true, error: msg });
}
process.exit(0);
