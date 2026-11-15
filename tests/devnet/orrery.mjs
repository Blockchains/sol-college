import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
const TOKEN_PROGRAM_ID = new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA');
const ASSOCIATED_TOKEN_PROGRAM_ID = new PublicKey('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL');
const ata = (mint, owner, allowOwnerOffCurve=false) => PublicKey.findProgramAddressSync(
  [owner.toBuffer(), TOKEN_PROGRAM_ID.toBuffer(), mint.toBuffer()],
  ASSOCIATED_TOKEN_PROGRAM_ID
)[0];

import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const BPF_LOADER_UPGRADEABLE_PROGRAM_ID = new PublicKey('BPFLoaderUpgradeab1e11111111111111111111111');

const idl = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[3], 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const program = new Program(idl, new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' }));
const logp = process.env.PROOF_LOG;
const log = (o) => { console.log(JSON.stringify(o)); fs.appendFileSync(logp, JSON.stringify(o)+'\n'); };

const mint = new PublicKey(process.argv[4] || 'BJMSdujxakjx7qypwfaFCnbkMTNPEYVWTTqnR9eJRL4D');
const [config] = PublicKey.findProgramAddressSync([Buffer.from('config')], programId);
const [programData] = PublicKey.findProgramAddressSync([programId.toBuffer()], BPF_LOADER_UPGRADEABLE_PROGRAM_ID);
const [providerPda] = PublicKey.findProgramAddressSync([Buffer.from('provider'), payer.publicKey.toBuffer()], programId);
const channelId = 1n;
const idBuf = Buffer.alloc(8); idBuf.writeBigUInt64LE(channelId);
const [channel] = PublicKey.findProgramAddressSync([Buffer.from('channel'), payer.publicKey.toBuffer(), providerPda.toBuffer(), idBuf], programId);
const payerTokens = ata(mint, payer.publicKey);
const vault = ata(mint, channel, true);
const session = Keypair.generate();

log({ step:'setup', program: programId.toBase58(), config: config.toBase58(), programData: programData.toBase58(),
      provider: providerPda.toBase58(), channel: channel.toBase58(), vault: vault.toBase58(),
      payerTokens: payerTokens.toBase58(), mint: mint.toBase58(), sessionKey: session.publicKey.toBase58() });

const sig = async (ix, step) => {
  const s = await ix.rpc();
  log({ step, ok:true, sig:s });
  console.log('SIG', step, s);
  return s;
};

const goodParams = { closeGraceSecs: new BN(600), unbondSecs: new BN(3600), minDeposit: new BN(1_000_000) };

try {
  await program.methods.initialize({ closeGraceSecs: new BN(600), unbondSecs: new BN(3600), minDeposit: new BN(0) })
    .accounts({ admin: payer.publicKey, program: programId, programData, config, settleMint: mint, systemProgram: SystemProgram.programId })
    .rpc();
  log({ step:'initialize_zero_deposit', expectedFailure:true, error:'unexpected success' });
} catch (e) {
  log({ step:'initialize_zero_deposit', expectedFailure:true, error: e.error?.errorCode?.code || e.message || String(e) });
}

await sig(program.methods.initialize(goodParams)
  .accounts({ admin: payer.publicKey, program: programId, programData, config, settleMint: mint, systemProgram: SystemProgram.programId }),
  'initialize');

try {
  await program.methods.registerProvider(payer.publicKey, 'ftp://bad.example', new Array(32).fill(1))
    .accounts({ authority: payer.publicKey, config, provider: providerPda, systemProgram: SystemProgram.programId })
    .rpc();
  log({ step:'register_provider_bad_endpoint', expectedFailure:true, error:'unexpected success' });
} catch (e) {
  log({ step:'register_provider_bad_endpoint', expectedFailure:true, error: e.error?.errorCode?.code || e.message || String(e) });
}

const manifest = Array.from({ length: 32 }, (_, i) => i + 1);
await sig(program.methods.registerProvider(payer.publicKey, 'https://sol.college/dapps/orrery/', manifest)
  .accounts({ authority: payer.publicKey, config, provider: providerPda, systemProgram: SystemProgram.programId }),
  'register_provider');

await sig(program.methods.openChannel(new BN(1), new BN(1_000_000), session.publicKey)
  .accounts({
    payer: payer.publicKey, config, provider: providerPda, channel, mint,
    payerTokens, vault,
    tokenProgram: TOKEN_PROGRAM_ID,
    associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
    systemProgram: SystemProgram.programId,
  }), 'open_channel');

const cfg = await program.account.config.fetch(config);
const prov = await program.account.provider.fetch(providerPda);
const ch = await program.account.channel.fetch(channel);
log({ step:'fetch', ok:true, providers: cfg.providers.toString(), channels: cfg.channels.toString(),
      minDeposit: cfg.minDeposit.toString(), settleMint: cfg.settleMint.toBase58(),
      endpoint: prov.endpoint, active: prov.active, deposit: ch.deposit.toString(), redeemed: ch.redeemed.toString() });
process.exit(0);
