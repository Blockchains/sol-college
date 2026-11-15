import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
const BPF_LOADER_UPGRADEABLE_PROGRAM_ID = new PublicKey('BPFLoaderUpgradeab1e11111111111111111111111');
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const idl = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[3], 'utf8'))));
const second = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[4], 'utf8'))));
const third = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[5], 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const program = new Program(idl, new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' }));
const log = (o) => { console.log(JSON.stringify(o)); fs.appendFileSync(process.env.PROOF_LOG, JSON.stringify(o)+'\n'); };

const [config] = PublicKey.findProgramAddressSync([Buffer.from('protocol')], programId);
const [programData] = PublicKey.findProgramAddressSync([programId.toBuffer()], BPF_LOADER_UPGRADEABLE_PROGRAM_ID);
const owners = [payer.publicKey, second.publicKey, third.publicKey];
log({ step:'setup', program: programId.toBase58(), config: config.toBase58(), programData: programData.toBase58(), second: second.publicKey.toBase58(), third: third.publicKey.toBase58() });

const remaining = [{ pubkey: programData, isWritable: false, isSigner: false }];
const accs = {
  protocolConfig: config,
  treasury: payer.publicKey,
  authority: payer.publicKey,
  secondSigner: second.publicKey,
  systemProgram: SystemProgram.programId,
};

try {
  const s = await program.methods.initializeProtocol(0, 100, new BN(1_000_000), new BN(1_000), 2, owners)
    .accounts(accs).remainingAccounts(remaining).signers([second]).rpc();
  log({ step:'initialize_protocol_bad_threshold', ok:false, error:'UNEXPECTED SUCCESS', sig:s });
  throw new Error('threshold 0 unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  const msg = String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0, 300);
  log({ step:'initialize_protocol_bad_threshold', expectedFailure:true, error: msg });
}

if (!(await conn.getAccountInfo(config))) {
  const sig = await program.methods.initializeProtocol(51, 100, new BN(1_000_000), new BN(1_000), 2, owners)
    .accounts(accs).remainingAccounts(remaining).signers([second]).rpc();
  log({ step:'initialize_protocol', ok:true, sig });
  console.log('SIG initialize_protocol', sig);
} else {
  log({ step:'initialize_protocol', alreadyInitialized:true });
}
const info = await conn.getAccountInfo(config);
if (!info) throw new Error('protocol config missing');
log({ step:'fetch_protocol_config', ok:true, lamports: info.lamports, owner: info.owner.toBase58(), dataLen: info.data.length });
// authority is first 32 bytes after 8-byte discriminator
const auth = new PublicKey(info.data.slice(8, 40)).toBase58();
const treas = new PublicKey(info.data.slice(40, 72)).toBase58();
log({ step:'decode_head', authority: auth, treasury: treas });
if (auth !== payer.publicKey.toBase58()) throw new Error('authority mismatch');

process.exit(0);
