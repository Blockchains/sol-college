import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { Connection, Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const TOKEN_PROGRAM_ID = new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA');

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const idlPath = process.argv[2] || path.join(__dirname, '../../dapps/build/trust-protocol/trust_protocol.json');
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
const log = (o) => { console.log(JSON.stringify(o)); fs.appendFileSync(process.env.PROOF_LOG || '/tmp/trust-protocol-proof.jsonl', JSON.stringify(o)+'\n'); };

const mintStr = process.argv[4] || 'DwHZekzdhofMcQS6mtVWKwUMZaM2JQb72XtnoSt3MFBX';
const mint = new PublicKey(mintStr);
const [protocolConfig] = PublicKey.findProgramAddressSync([Buffer.from('protocol-config')], programId);
const [insurancePool] = PublicKey.findProgramAddressSync([Buffer.from('insurance-pool')], programId);
const [poolAuthority] = PublicKey.findProgramAddressSync([Buffer.from('pool-authority')], programId);
log({ step: 'setup', program: programId.toBase58(), admin: payer.publicKey.toBase58(), swornMint: mint.toBase58(), protocolConfig: protocolConfig.toBase58(), insurancePool: insurancePool.toBase58(), poolAuthority: poolAuthority.toBase58() });

const cfgInfo = await conn.getAccountInfo(protocolConfig);
if (!cfgInfo) {
  const sig = await program.methods.initialize({ minIdentityBond: new BN(3_000_000), maxIdentityBond: new BN(5_000_000) }).accounts({
    admin: payer.publicKey,
    swornMint: mint,
    protocolConfig,
    insurancePool,
    poolAuthority,
    systemProgram: SystemProgram.programId,
    tokenProgram: TOKEN_PROGRAM_ID,
  }).rpc();
  log({ step: 'initialize', ok: true, sig });
  console.log('SIG initialize', sig);
} else {
  log({ step: 'initialize', alreadyInitialized: true, protocolConfig: protocolConfig.toBase58() });
}

const cfg = await program.account.protocolConfig.fetch(protocolConfig);
log({
  step: 'fetch_config',
  ok: true,
  admin: cfg.admin.toBase58(),
  swornMint: cfg.swornMint.toBase58(),
  minIdentityBond: cfg.minIdentityBond.toString(),
  maxIdentityBond: cfg.maxIdentityBond.toString(),
  governancePhase: cfg.governancePhase,
});
if (cfg.admin.toBase58() !== payer.publicKey.toBase58()) throw new Error('admin mismatch');
if (cfg.swornMint.toBase58() !== mint.toBase58()) throw new Error('sworn mint mismatch');
if (cfg.minIdentityBond.toString() !== '3000000' || cfg.maxIdentityBond.toString() !== '5000000') throw new Error('bond bounds mismatch');

try {
  const s = await program.methods.initialize({ minIdentityBond: new BN(3_000_000), maxIdentityBond: new BN(5_000_000) }).accounts({
    admin: payer.publicKey, swornMint: mint, protocolConfig, insurancePool, poolAuthority,
    systemProgram: SystemProgram.programId, tokenProgram: TOKEN_PROGRAM_ID,
  }).rpc();
  log({ step: 'initialize_twice', ok: false, error: 'UNEXPECTED SUCCESS', sig: s });
  throw new Error('second initialize unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  const msg = String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0, 240);
  log({ step: 'initialize_twice', expectedFailure: true, error: msg });
}
