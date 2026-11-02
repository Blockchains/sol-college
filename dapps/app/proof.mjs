// Server-side proof run (NOT the browser dapp): sends real instructions through a deployed program with a throwaway keypair,
// using the same IDL-driven Anchor client as the dapp. Prints "SIG <ix> <signature>" lines. Never prints keys or RPC URLs with secrets.
import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram, SYSVAR_RENT_PUBKEY } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const [idlPath, programId, rpc, payerPath] = process.argv.slice(2);
const idl = { ...JSON.parse(fs.readFileSync(idlPath)), address: programId };
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(payerPath))));
const conn = new Connection(rpc, 'confirmed'), provider = new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' });
const program = new Program(idl, provider);
const camel = (s) => s.replace(/_([a-z0-9])/g, (_, c) => c.toUpperCase());
const WK = { systemProgram: SystemProgram.programId, rent: SYSVAR_RENT_PUBKEY, tokenProgram: new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'), associatedTokenProgram: new PublicKey('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL'), tokenMetadataProgram: new PublicKey('metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s'), metadataProgram: new PublicKey('metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s') };
const flat = (a) => a.flatMap((x) => (x.accounts ? flat(x.accounts) : [x]));
const sample = (t, name) => {
  if (typeof t === 'string') {
    if (/^[ui](64|128)$/.test(t)) return /id$/i.test(name) ? (globalThis.__id ??= new BN(Date.now() % 1e9)) : new BN(1); if (/^[uif]\d+$/.test(t)) return 1; if (t === 'bool') return true;
    if (t === 'string') return /symbol/i.test(name) ? 'SOLC' : /uri|url|link/i.test(name) ? 'https://sol.college/' : 'solcollege'; if (t === 'pubkey' || t === 'publicKey') return payer.publicKey; if (t === 'bytes') return Buffer.from([1]);
  }
  if (t.option) return null; if (t.array) return Array.from({ length: t.array[1] }, () => sample(t.array[0], name)); if (t.vec) return [];
  throw new Error('complex arg ' + JSON.stringify(t));
};
const only = process.env.IXS ? process.env.IXS.split(',') : null; let n = 0;
for (const ix of idl.instructions) {
  if (only && !only.includes(ix.name)) continue;
  try {
    const accs = {}, extra = [];
    for (const a of flat(ix.accounts)) {
      const k = camel(a.name);
      if (a.address || a.pda) continue;
      if (WK[k]) accs[k] = WK[k];
      else if (a.signer) { if (/payer|authority|user|owner|signer|admin|creator|initializer|maker|seller|buyer|player|fee/i.test(a.name) || !accs.__p) { accs[k] = payer.publicKey; accs.__p = 1; } else { const kp = Keypair.generate(); extra.push(kp); accs[k] = kp.publicKey; } }
      else extra.__d = [...(extra.__d || []), a];
    }
    // Derived accounts that follow common conventions: the payer's ATA for the instruction's mint, and Metaplex metadata/edition PDAs.
    const MD = WK.tokenMetadataProgram, mint = accs.mint;
    for (const a of extra.__d || []) {
      const k = camel(a.name);
      if (mint && /associated_token|token_account|^ata$|_ata$/i.test(a.name)) accs[k] = PublicKey.findProgramAddressSync([payer.publicKey.toBuffer(), WK.tokenProgram.toBuffer(), mint.toBuffer()], WK.associatedTokenProgram)[0];
      else if (mint && /master_edition|edition/i.test(a.name)) accs[k] = PublicKey.findProgramAddressSync([Buffer.from('metadata'), MD.toBuffer(), mint.toBuffer(), Buffer.from('edition')], MD)[0];
      else if (mint && /metadata/i.test(a.name)) accs[k] = PublicKey.findProgramAddressSync([Buffer.from('metadata'), MD.toBuffer(), mint.toBuffer()], MD)[0];
      else throw new Error('needs account ' + a.name);
    }
    delete extra.__d;
    delete accs.__p;
    const args = ix.args.map((a) => sample(a.type, a.name));
    const sig = await program.methods[camel(ix.name)](...args).accountsPartial(accs).signers(extra).rpc();
    console.log(`SIG ${ix.name} ${sig}`); n++;
  } catch (e) { console.log(`SKIP ${ix.name}: ${String(e.message || e).split('\n')[0].slice(0, 160)}`); if (process.env.DEBUG) console.log(e.logs || e); }
}
console.log(`DONE ${n} instruction(s) sent`);
