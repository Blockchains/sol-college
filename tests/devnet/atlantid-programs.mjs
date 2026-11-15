import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, TransactionInstruction, LAMPORTS_PER_SOL } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';

const { AnchorProvider, Program, Wallet, BN } = anchor;
const TOKEN_PROGRAM_ID = new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA');
const ASSOCIATED_TOKEN_PROGRAM_ID = new PublicKey('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL');
const MPL_CORE_PROGRAM_ID = new PublicKey('CoREENxT6tW1HoK8ypY1SxRMZTcVPm7R94rH4PZNhX7d');
const BPF_LOADER = new PublicKey('BPFLoaderUpgradeab1e11111111111111111111111');
const MINT = new PublicKey('BJMSdujxakjx7qypwfaFCnbkMTNPEYVWTTqnR9eJRL4D');
const REGISTRY_ID = new PublicKey('8oo4J9tBB3Hna1jRQ3rWvJjojqM5DYTDJo5cejUuJy3C');

const vaultIdl = JSON.parse(fs.readFileSync('/workspace/deai-work/proof/atlantid-vault.json', 'utf8'));
const escrowIdl = JSON.parse(fs.readFileSync('/workspace/deai-work/proof/atlantid-escrow.json', 'utf8'));
const registryIdl = JSON.parse(fs.readFileSync('/workspace/deai-work/proof/atlantid-8004.json', 'utf8'));
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.env.HOME + '/.config/solana/id.json', 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
const conn = new Connection(rpc, 'confirmed');
const provider = new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' });
const vaultProgram = new Program(vaultIdl, provider);
const escrowProgram = new Program(escrowIdl, provider);
const registryProgram = new Program(registryIdl, provider);
const vaultId = new PublicKey(vaultIdl.address);
const escrowId = new PublicKey(escrowIdl.address);
const log = (o) => { console.log(JSON.stringify(o)); if (process.env.PROOF_LOG) fs.appendFileSync(process.env.PROOF_LOG, JSON.stringify(o)+'\n'); };

function ata(owner, mint) {
  return PublicKey.findProgramAddressSync(
    [owner.toBuffer(), TOKEN_PROGRAM_ID.toBuffer(), mint.toBuffer()],
    ASSOCIATED_TOKEN_PROGRAM_ID
  )[0];
}
async function sendIx(ixs, signers) {
  const tx = new Transaction().add(...ixs);
  tx.feePayer = payer.publicKey;
  tx.recentBlockhash = (await conn.getLatestBlockhash()).blockhash;
  tx.sign(...signers);
  const sig = await conn.sendRawTransaction(tx.serialize());
  await conn.confirmTransaction(sig, 'confirmed');
  return sig;
}
async function ensureAta(owner) {
  const dest = ata(owner, MINT);
  if (await conn.getAccountInfo(dest)) return dest;
  const ix = new TransactionInstruction({
    programId: ASSOCIATED_TOKEN_PROGRAM_ID,
    keys: [
      { pubkey: payer.publicKey, isSigner: true, isWritable: true },
      { pubkey: dest, isSigner: false, isWritable: true },
      { pubkey: owner, isSigner: false, isWritable: false },
      { pubkey: MINT, isSigner: false, isWritable: false },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    ],
    data: Buffer.from([0]),
  });
  await sendIx([ix], [payer]);
  return dest;
}
async function mintTo(dest, amount) {
  const data = Buffer.alloc(9);
  data[0] = 7;
  data.writeBigUInt64LE(BigInt(amount), 1);
  const ix = new TransactionInstruction({
    programId: TOKEN_PROGRAM_ID,
    keys: [
      { pubkey: MINT, isSigner: false, isWritable: true },
      { pubkey: dest, isSigner: false, isWritable: true },
      { pubkey: payer.publicKey, isSigner: true, isWritable: false },
    ],
    data,
  });
  return sendIx([ix], [payer]);
}
async function tokenBal(pk) {
  return BigInt((await conn.getTokenAccountBalance(pk)).value.amount);
}

const owner = payer.publicKey;
const [regRoot] = PublicKey.findProgramAddressSync([Buffer.from('root_config')], REGISTRY_ID);
const rootConfig8004 = await registryProgram.account.rootConfig.fetch(regRoot);
const collection = rootConfig8004.baseCollection;
const [registryConfig] = PublicKey.findProgramAddressSync(
  [Buffer.from('registry_config'), collection.toBuffer()],
  REGISTRY_ID
);
log({ step:'8004_root', root: regRoot.toBase58(), collection: collection.toBase58(), registryConfig: registryConfig.toBase58(), authority: rootConfig8004.authority.toBase58() });

// 1. Register agent with ATOM
const asset = Keypair.generate();
const [agentPda] = PublicKey.findProgramAddressSync([Buffer.from('agent'), asset.publicKey.toBuffer()], REGISTRY_ID);
const uri = `https://sol.college/lab/atlantid/${Date.now()}`;
const sReg = await registryProgram.methods.registerWithOptions(uri, true)
  .accounts({
    rootConfig: regRoot,
    registryConfig,
    agentAccount: agentPda,
    asset: asset.publicKey,
    collection,
    owner,
    systemProgram: SystemProgram.programId,
    mplCoreProgram: MPL_CORE_PROGRAM_ID,
  })
  .signers([asset])
  .rpc();
const agent = await registryProgram.account.agentAccount.fetch(agentPda);
log({ step:'register_with_options', ok:true, sig:sReg, asset: asset.publicKey.toBase58(), agent: agentPda.toBase58(), atomEnabled: agent.atomEnabled, agentOwner: agent.owner.toBase58() });
console.log('SIG register_with_options', sReg);
if (!agent.atomEnabled) throw new Error('ATOM not enabled');

// 2. Initialize vault root config
const [vaultRoot] = PublicKey.findProgramAddressSync([Buffer.from('root_config')], vaultId);
const [vaultProgramData] = PublicKey.findProgramAddressSync([vaultId.toBuffer()], BPF_LOADER);
const treasury = payer.publicKey; // reuse deployer; fee is 0
if (!(await conn.getAccountInfo(vaultRoot))) {
  const sInit = await vaultProgram.methods.initializeRootConfig(new BN(0))
    .accounts({
      authority: owner,
      treasury,
      rootConfig: vaultRoot,
      programData: vaultProgramData,
      systemProgram: SystemProgram.programId,
    }).rpc();
  log({ step:'initialize_root_config', ok:true, sig:sInit, vaultRoot: vaultRoot.toBase58() });
  console.log('SIG initialize_root_config', sInit);
} else {
  log({ step:'initialize_root_config', skipped:true, vaultRoot: vaultRoot.toBase58() });
}

// 3. Create vault
const [vaultPda] = PublicKey.findProgramAddressSync(
  [Buffer.from('vault'), owner.toBuffer(), asset.publicKey.toBuffer()],
  vaultId
);
const [vaultAuth] = PublicKey.findProgramAddressSync(
  [Buffer.from('vault_authority'), vaultPda.toBuffer()],
  vaultId
);
const vaultAta = ata(vaultAuth, MINT);
const sCreate = await vaultProgram.methods.createVault()
  .accounts({
    owner,
    agentAsset: asset.publicKey,
    agent8004Account: agentPda,
    vaultAccount: vaultPda,
    vaultAuthority: vaultAuth,
    vaultTokenAccount: vaultAta,
    mint: MINT,
    rootConfig: vaultRoot,
    treasury,
    systemProgram: SystemProgram.programId,
    tokenProgram: TOKEN_PROGRAM_ID,
    associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
  }).rpc();
log({ step:'create_vault', ok:true, sig:sCreate, vault: vaultPda.toBase58(), vaultAta: vaultAta.toBase58(), vaultAuth: vaultAuth.toBase58() });
console.log('SIG create_vault', sCreate);

// 4. Fund vault + policy
const FUND = 5_000_000n;
await mintTo(vaultAta, FUND);
const ownerAta = await ensureAta(owner);
log({ step:'fund_vault', vaultBal: (await tokenBal(vaultAta)).toString() });

const sPol = await vaultProgram.methods.updatePolicy(new BN(4_000_000), new BN(2_000_000), false)
  .accounts({ owner, vaultAccount: vaultPda }).rpc();
log({ step:'update_policy', ok:true, sig:sPol });
console.log('SIG update_policy', sPol);

// 5. Spend as owner (bypass caps)
const recipient = Keypair.generate();
await sendIx([SystemProgram.transfer({ fromPubkey: owner, toPubkey: recipient.publicKey, lamports: 20_000_000 })], [payer]);
const recipAta = await ensureAta(recipient.publicKey);
const beforeRecip = await tokenBal(recipAta);
const SPEND = 3_000_000n; // exceeds per_tx 2M — owner bypass
const sSpend = await vaultProgram.methods.spend(new BN(SPEND.toString()))
  .accounts({
    authority: owner,
    vaultAccount: vaultPda,
    agent8004Account: agentPda,
    vaultAuthority: vaultAuth,
    vaultTokenAccount: vaultAta,
    recipientTokenAccount: recipAta,
    mint: MINT,
    tokenProgram: TOKEN_PROGRAM_ID,
  }).rpc();
const afterRecip = await tokenBal(recipAta);
log({ step:'spend_owner', ok:true, sig:sSpend, recipientDelta: (afterRecip-beforeRecip).toString() });
console.log('SIG spend_owner', sSpend);
if (afterRecip - beforeRecip !== SPEND) throw new Error('spend amount mismatch');

// 6. Withdraw remaining to owner
const remaining = await tokenBal(vaultAta);
const beforeOwner = await tokenBal(ownerAta);
const sW = await vaultProgram.methods.withdraw(new BN(remaining.toString()))
  .accounts({
    owner,
    vaultAccount: vaultPda,
    vaultAuthority: vaultAuth,
    vaultTokenAccount: vaultAta,
    ownerTokenAccount: ownerAta,
    mint: MINT,
    tokenProgram: TOKEN_PROGRAM_ID,
  }).rpc();
const afterOwner = await tokenBal(ownerAta);
log({ step:'withdraw', ok:true, sig:sW, ownerDelta: (afterOwner-beforeOwner).toString(), vaultLeft: (await tokenBal(vaultAta)).toString() });
console.log('SIG withdraw', sW);

// 7. Escrow config + job against this vault
const [escrowProgramData] = PublicKey.findProgramAddressSync([escrowId.toBuffer()], BPF_LOADER);
const [escrowConfig] = PublicKey.findProgramAddressSync([Buffer.from('escrow_config')], escrowId);
if (!(await conn.getAccountInfo(escrowConfig))) {
  const sEc = await escrowProgram.methods.initializeEscrowConfig(new BN(64), new BN(64), 100, 0)
    .accounts({
      authority: owner,
      treasury,
      mint: MINT,
      escrowConfig,
      programData: escrowProgramData,
      systemProgram: SystemProgram.programId,
    }).rpc();
  log({ step:'initialize_escrow_config', ok:true, sig:sEc, escrowConfig: escrowConfig.toBase58() });
  console.log('SIG initialize_escrow_config', sEc);
} else {
  log({ step:'initialize_escrow_config', skipped:true, escrowConfig: escrowConfig.toBase58() });
}

const jobId = Buffer.alloc(16); jobId.write('atl-job-1');
const [escrowRecord] = PublicKey.findProgramAddressSync([Buffer.from('escrow'), jobId], escrowId);
const [escrowAuth] = PublicKey.findProgramAddressSync([Buffer.from('escrow_authority'), escrowRecord.toBuffer()], escrowId);
const escrowAta = ata(escrowAuth, MINT);
const treasuryAta = await ensureAta(treasury);
const ESCROW_AMT = 1_000_000n;
await mintTo(ownerAta, ESCROW_AMT);
const beforeVaultAta = await tokenBal(vaultAta);
const sEs = await escrowProgram.methods.createEscrow(Array.from(jobId), new BN(ESCROW_AMT.toString()), new BN(10_000))
  .accounts({
    client: owner,
    workerVault: vaultPda,
    escrowConfig,
    escrowRecord,
    escrowAuthority: escrowAuth,
    escrowTokenAccount: escrowAta,
    clientTokenAccount: ownerAta,
    mint: MINT,
    systemProgram: SystemProgram.programId,
    tokenProgram: TOKEN_PROGRAM_ID,
    associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
  }).rpc();
log({ step:'create_escrow', ok:true, sig:sEs, escrow: escrowRecord.toBase58(), escrowAta: escrowAta.toBase58(), escrowBal: (await tokenBal(escrowAta)).toString() });
console.log('SIG create_escrow', sEs);

const sMk = await escrowProgram.methods.markCompleted(Array.from(jobId))
  .accounts({
    worker: owner,
    workerVault: vaultPda,
    agentAccount: agentPda,
    escrowRecord,
  }).rpc();
log({ step:'mark_completed', ok:true, sig:sMk });
console.log('SIG mark_completed', sMk);

const sAc = await escrowProgram.methods.acceptWork(Array.from(jobId))
  .accounts({
    client: owner,
    escrowConfig,
    escrowRecord,
    escrowAuthority: escrowAuth,
    escrowTokenAccount: escrowAta,
    workerVaultAta: vaultAta,
    treasuryAta,
    tokenProgram: TOKEN_PROGRAM_ID,
  }).rpc();
const afterVaultAta = await tokenBal(vaultAta);
log({ step:'accept_work', ok:true, sig:sAc, vaultDelta: (afterVaultAta-beforeVaultAta).toString(), escrowLeft: (await tokenBal(escrowAta)).toString() });
console.log('SIG accept_work', sAc);

log({ step:'DONE', ok:true, vault: vaultPda.toBase58(), escrow: escrowRecord.toBase58(), agent: agentPda.toBase58(), asset: asset.publicKey.toBase58() });
