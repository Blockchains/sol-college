// Devnet flow for the gree fork, mirroring the re-enabled initNft code in web/src/app/gree/gree-data-access.tsx:
// fresh mint keypair, ATA, Metaplex metadata + master edition PDAs, one init_nft call. Negative: re-using an existing mint.
// Usage (from the fork root, anchor 0.29): node gree.mjs <legacy idl.json> <programId> <rpc> <tester.json>
import fs from 'fs';
import anchor from '@coral-xyz/anchor';
import { Connection, Keypair, PublicKey, SystemProgram, SYSVAR_RENT_PUBKEY } from '@solana/web3.js';
import { getAssociatedTokenAddressSync, TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID } from '@solana/spl-token';
const { AnchorProvider, Program, Wallet } = anchor;
const [idlPath, pidS, rpc, kpPath] = process.argv.slice(2);
const kp = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(kpPath, 'utf8'))));
const conn = new Connection(rpc, 'confirmed');
conn.confirmTransaction = async (arg) => { const sig = typeof arg === 'string' ? arg : arg.signature;
  for (let i = 0; i < 90; i++) { const st = (await conn.getSignatureStatuses([sig])).value[0];
    if (st && ['confirmed', 'finalized'].includes(st.confirmationStatus)) return { context: { slot: st.slot }, value: { err: st.err } };
    await new Promise(r => setTimeout(r, 1000)); } throw new Error('confirm timeout'); };
const program = new Program(JSON.parse(fs.readFileSync(idlPath, 'utf8')), new PublicKey(pidS), new AnchorProvider(conn, new Wallet(kp), { commitment: 'confirmed' }));
const MPL = new PublicKey('metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s');
const log = (o) => console.log(JSON.stringify(o));
const accs = (mint) => ({ signer: kp.publicKey, mint, associatedTokenAccount: getAssociatedTokenAddressSync(mint, kp.publicKey),
  metadataAccount: PublicKey.findProgramAddressSync([Buffer.from('metadata'), MPL.toBuffer(), mint.toBuffer()], MPL)[0],
  masterEditionAccount: PublicKey.findProgramAddressSync([Buffer.from('metadata'), MPL.toBuffer(), mint.toBuffer(), Buffer.from('edition')], MPL)[0],
  tokenProgram: TOKEN_PROGRAM_ID, associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID, tokenMetadataProgram: MPL, systemProgram: SystemProgram.programId, rent: SYSVAR_RENT_PUBKEY });
const mint = Keypair.generate();
const sig = await program.methods.initNft('GLC-20240317', 'GRLC', 'ipfs://bafkreidsv7qyevjbnsncrn7peogr6rp6bfclz3exx2vkunsd5egx7bd5wq').accounts(accs(mint.publicKey)).signers([mint]).rpc();
const sup = await conn.getTokenSupply(mint.publicKey); const md = await conn.getAccountInfo(accs(mint.publicKey).metadataAccount);
log({ step: 'init_nft', ok: true, sig, mint: mint.publicKey.toBase58(), supply: sup.value.amount, decimals: sup.value.decimals, metadataOwner: md?.owner.toBase58(), nameInMetadata: md ? md.data.toString('latin1').includes('GLC-20240317') : false });
try { await program.methods.initNft('X', 'X', 'ipfs://x').accounts(accs(mint.publicKey)).signers([mint]).rpc(); log({ step: 'init_nft_same_mint', ok: false, error: 'UNEXPECTED SUCCESS' }); }
catch (e) { log({ step: 'init_nft_same_mint', expectedFailure: true, error: String(e.message).split('\n')[0].slice(0, 160) }); }
