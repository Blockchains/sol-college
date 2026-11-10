// Devnet end-to-end flow for the picassol-hackathon fork, mirroring frontend/components/Pixel.tsx:
// pixel PDA = ["pixel", [x, y]]; create_pixel then update_pixel; reads the account back. Negative: x=200 is out of range.
// Usage (from the fork's frontend/ dir, anchor 0.29): node picassol-hackathon.mjs <legacy idl.json> <programId> <rpc> <tester.json>
import fs from 'fs';
import anchor from '@coral-xyz/anchor';
import { Connection, Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
const { AnchorProvider, Program, Wallet } = anchor;
const [idlPath, pidS, rpc, kpPath] = process.argv.slice(2);
const kp = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(kpPath, 'utf8'))));
const provider = new AnchorProvider(new Connection(rpc, 'confirmed'), new Wallet(kp), { commitment: 'confirmed' });
const program = new Program(JSON.parse(fs.readFileSync(idlPath, 'utf8')), new PublicKey(pidS), provider);
const log = (o) => console.log(JSON.stringify(o));
const px = (x, y) => PublicKey.findProgramAddressSync([Buffer.from('pixel'), Buffer.from([x, y])], program.programId)[0];
let x, y;
for (let i = 0; i < 40; i++) { x = Math.floor(Math.random() * 200); y = Math.floor(Math.random() * 200); if (!(await provider.connection.getAccountInfo(px(x, y)))) break; }
log({ step: 'setup', program: pidS, tester: kp.publicKey.toBase58(), x, y, pixel: px(x, y).toBase58() });
try { await program.methods.createPixel(200, 5, 1, 2, 3).accounts({ pixel: px(200, 5), user: kp.publicKey, systemProgram: SystemProgram.programId }).rpc(); log({ step: 'create_pixel_out_of_range', ok: false, error: 'UNEXPECTED SUCCESS' }); }
catch (e) { log({ step: 'create_pixel_out_of_range', expectedFailure: true, error: String(e.error?.errorCode?.code || e.message).slice(0, 160) }); }
const s1 = await program.methods.createPixel(x, y, 153, 69, 255).accounts({ pixel: px(x, y), user: kp.publicKey, systemProgram: SystemProgram.programId }).rpc();
let a = await program.account.pixel.fetch(px(x, y)); log({ step: 'create_pixel', ok: true, sig: s1, color: [a.colR, a.colG, a.colB] });
try { await program.methods.createPixel(x, y, 0, 0, 0).accounts({ pixel: px(x, y), user: kp.publicKey, systemProgram: SystemProgram.programId }).rpc(); log({ step: 'create_pixel_twice', ok: false, error: 'UNEXPECTED SUCCESS' }); }
catch (e) { log({ step: 'create_pixel_twice', expectedFailure: true, error: String(e.message).split('\n')[0].slice(0, 160) }); }
const s2 = await program.methods.updatePixel(20, 241, 149).accounts({ pixel: px(x, y) }).rpc();
a = await program.account.pixel.fetch(px(x, y)); log({ step: 'update_pixel', ok: true, sig: s2, color: [a.colR, a.colG, a.colB] });
