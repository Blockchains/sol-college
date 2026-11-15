import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;

const idl = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[3], 'utf8'))));
const payee = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[4], 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const program = new Program(idl, new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' }));
const logp = process.env.PROOF_LOG;
const log = (o) => { console.log(JSON.stringify(o)); fs.appendFileSync(logp, JSON.stringify(o)+'\n'); };

const INCINERATOR = new PublicKey('1nc1nerator11111111111111111111111111111111');
const [agent] = PublicKey.findProgramAddressSync([Buffer.from('agent'), payer.publicKey.toBuffer()], programId);
const nonce = Uint8Array.from({ length: 16 }, (_, i) => i + 1);
const [escrow] = PublicKey.findProgramAddressSync([Buffer.from('escrow'), payer.publicKey.toBuffer(), nonce], programId);

log({ step:'setup', program: programId.toBase58(), agent: agent.toBase58(), escrow: escrow.toBase58(),
      payee: payee.publicKey.toBase58() });

const sig = async (ix, step) => {
  const s = await ix.rpc();
  log({ step, ok:true, sig:s });
  console.log('SIG', step, s);
  return s;
};

try {
  await program.methods.registerAgent({ primary: {} }, 'x'.repeat(65), new BN(1_000_000), 0)
    .accounts({ agent, owner: payer.publicKey, feeCollector: INCINERATOR, systemProgram: SystemProgram.programId })
    .rpc();
  log({ step:'register_agent_model_too_long', expectedFailure:true, error:'unexpected success' });
} catch (e) {
  log({ step:'register_agent_model_too_long', expectedFailure:true, error: e.error?.errorCode?.code || e.message || String(e) });
}

await sig(program.methods.registerAgent({ primary: {} }, 'campus-scout', new BN(1_000_000), 0)
  .accounts({ agent, owner: payer.publicKey, feeCollector: INCINERATOR, systemProgram: SystemProgram.programId }),
  'register_agent');

try {
  await program.methods.lockEscrow(new BN(0), Array.from(nonce))
    .accounts({ escrow, payer: payer.publicKey, payee: payee.publicKey, systemProgram: SystemProgram.programId })
    .rpc();
  log({ step:'lock_escrow_zero', expectedFailure:true, error:'unexpected success' });
} catch (e) {
  log({ step:'lock_escrow_zero', expectedFailure:true, error: e.error?.errorCode?.code || e.message || String(e) });
}

const payeeBefore = await conn.getBalance(payee.publicKey);
await sig(program.methods.lockEscrow(new BN(1_000_000), Array.from(nonce))
  .accounts({ escrow, payer: payer.publicKey, payee: payee.publicKey, systemProgram: SystemProgram.programId }),
  'lock_escrow');

await sig(program.methods.releaseEscrow()
  .accounts({ escrow, payer: payer.publicKey, payee: payee.publicKey, systemProgram: SystemProgram.programId }),
  'release_escrow');

const ag = await program.account.agentAccount.fetch(agent);
const payeeAfter = await conn.getBalance(payee.publicKey);
const escrowAfter = await conn.getAccountInfo(escrow);
log({ step:'fetch', ok:true, model: ag.model, active: ag.active, rate: ag.rateLamports.toString(),
      agentType: ag.agentType, payeeDelta: payeeAfter - payeeBefore, escrowClosed: escrowAfter === null });
process.exit(0);
