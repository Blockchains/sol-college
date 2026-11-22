import fs from 'fs';
import crypto from 'crypto';
import { Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import { keccak_256 } from '@noble/hashes/sha3';
import { payer, conn, log, program, ata, ensureAta, mintTo, tokenBal, fund, expectFail, BN, MINT, BPF_LOADER, TOKEN_PROGRAM_ID } from './lib/labcommon.mjs';
const idl = JSON.parse(fs.readFileSync(new URL('../../dapps/static/prize-escrow/idl.json', import.meta.url),'utf8'));
const prog = program(idl); const pid = new PublicKey(idl.address); const me = payer.publicKey;
const regrader = Keypair.generate(), winner1 = Keypair.generate(), winner2 = Keypair.generate(), guardian = Keypair.generate(), complianceKp = Keypair.generate();
const [config] = PublicKey.findProgramAddressSync([Buffer.from('config')], pid);
const [programData] = PublicKey.findProgramAddressSync([pid.toBuffer()], BPF_LOADER);
process.on('unhandledRejection', e => { console.log('FAIL', JSON.stringify(e.logs || e.transactionLogs || String(e))); process.exit(1); });
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const CLOCK = new PublicKey('SysvarC1ock11111111111111111111111111111111');
const chainNow = async () => Number((await conn.getAccountInfo(CLOCK)).data.readBigInt64LE(32));
log({ step:'setup', program: pid.toBase58(), config: config.toBase58(), winner1: winner1.publicKey.toBase58(), winner2: winner2.publicKey.toBase58(), regrader: regrader.publicKey.toBase58() });
if (!(await conn.getAccountInfo(config))) {
  const init = { admin: me, guardian: guardian.publicKey, arbiter: me,
    limits: { escrowCap: new BN(100_000_000), globalCap: new BN(1_000_000_000), flowCapacity: new BN(100_000_000), flowPeriod: new BN(3600), minBond: new BN(0), maxHouseRegraders: 1 },
    floors: { minChallengeWindow: new BN(60), minAttestWindow: new BN(60), minHoldWindow: new BN(60), minClaimWindow: new BN(90), revealGrace: new BN(20) },
    mints: [MINT], sponsors: [me], regraders: [{ key: regrader.publicKey, house: false }] };
  log({ step:'initialize_config', sig: await prog.methods.initializeConfig(init).accountsPartial({ authority: me, config, programData }).rpc() });
} else {
  log({ step:'set_allowed_regrader', sig: await prog.methods.setAllowed({ regrader: {} }, regrader.publicKey, true, false).accountsPartial({ admin: me, config }).rpc(), regrader: regrader.publicKey.toBase58() });
}
const cid = crypto.randomBytes(16);
const [escrow] = PublicKey.findProgramAddressSync([Buffer.from('escrow'), me.toBuffer(), cid], pid);
const vault = ata(escrow);
const sponsorAta = await ensureAta(me); await mintTo(sponsorAta, 1_000_000);
let now = await chainNow();
const terms = (over = {}) => ({ total: new BN(1_000_000), rulesSha256: Array.from(crypto.createHash('sha256').update('sol-college lab prize rules').digest()), resolver: me, compliance: complianceKp.publicKey, arbiter: me, refundTo: me,
  regraders: [regrader.publicKey], k: 1, bondLamports: new BN(10_000_000), entriesDeadline: new BN(now + 45), finalEnd: new BN(now + 45), resolveDeadline: new BN(now + 3600),
  challengeWindow: new BN(60), attestWindow: new BN(60), holdWindow: new BN(60), claimWindow: new BN(600), hardDeadline: new BN(now + 3600 + 60 + 60 + 60 + 600 + 7*24*3600 + 60), ...over });
const openAcc = { sponsor: me, escrow, mint: MINT, sponsorTokenAccount: sponsorAta, vault, config };
await expectFail('open_escrow_window_below_floor', () => prog.methods.openEscrow(Array.from(cid), terms({ challengeWindow: new BN(10) })).accountsPartial(openAcc).rpc());
let so; try { so = await prog.methods.openEscrow(Array.from(cid), terms()).accountsPartial(openAcc).rpc(); } catch (e) { console.log('OPENLOGS', JSON.stringify(e.logs || e.transactionLogs || String(e))); process.exit(1); }
log({ step:'open_escrow', sig: so, escrow: escrow.toBase58(), vault: vault.toBase58(), vault_balance: String(await tokenBal(vault)) });
const entriesRoot = Array.from(crypto.createHash('sha256').update('entries:' + winner1.publicKey.toBase58() + winner2.publicKey.toBase58()).digest());
log({ step:'commit_entries', sig: await prog.methods.commitEntries(entriesRoot, 2).accountsPartial({ resolver: me, escrow, config }).rpc() });
// payout tree: winner1 700_000, winner2 300_000
const leaf = (who, amt) => { const b = Buffer.alloc(8); b.writeBigUInt64LE(BigInt(amt)); const inner = keccak_256(Buffer.concat([escrow.toBuffer(), who.toBuffer(), b])); return Buffer.from(keccak_256(Buffer.concat([Buffer.from([0]), Buffer.from(inner)]))); };
const l1 = leaf(winner1.publicKey, 700_000), l2 = leaf(winner2.publicKey, 300_000);
const pair = (a, b) => Buffer.from(keccak_256(Buffer.compare(a, b) < 0 ? Buffer.concat([a, b]) : Buffer.concat([b, a])));
const root = pair(l1, l2);
while ((await chainNow()) < now + 46) await sleep(3000);
await expectFail('post_result_total_exceeds_vault', () => prog.methods.postResult(Array.from(root), Array(32).fill(9), Array(32).fill(8), new BN(1_000_001)).accountsPartial({ resolver: me, escrow, mint: MINT, vault, config }).rpc());
log({ step:'post_result', sig: await prog.methods.postResult(Array.from(root), Array(32).fill(9), Array(32).fill(8), new BN(1_000_000)).accountsPartial({ resolver: me, escrow, mint: MINT, vault, config }).rpc(), payout_root: root.toString('hex') });
await expectFail('settle_before_challenge_deadline', () => prog.methods.settle().accountsPartial({ escrow, mint: MINT, vault, resolver: me, challenger: null, config }).rpc());
const e1 = await prog.account.escrow.fetch(escrow);
while ((await chainNow()) < Number(e1.challengeDeadline) + 1) await sleep(4000);
log({ step:'settle', sig: await prog.methods.settle().accountsPartial({ escrow, mint: MINT, vault, resolver: me, challenger: null, config }).rpc(), status: Object.keys((await prog.account.escrow.fetch(escrow)).status)[0] });
await fund(winner1.publicKey, 10_000_000);
const w1 = program(idl, winner1);
const claimAcc = (w) => ({ claimant: w.publicKey, payer: w.publicKey, compliance: complianceKp.publicKey, escrow, mint: MINT, vault, config });
await expectFail('claim_with_wrong_amount_proof', () => w1.methods.claim(new BN(900_000), new BN(900_000), [Array.from(l2)]).accountsPartial(claimAcc(winner1)).signers([complianceKp]).rpc());
log({ step:'claim_winner1', sig: await w1.methods.claim(new BN(700_000), new BN(700_000), [Array.from(l2)]).accountsPartial(claimAcc(winner1)).signers([complianceKp]).rpc(), winner1_received: String(await tokenBal(ata(winner1.publicKey))) });
await fund(winner2.publicKey, 10_000_000);
const w2 = program(idl, winner2);
log({ step:'claim_winner2', sig: await w2.methods.claim(new BN(300_000), new BN(300_000), [Array.from(l1)]).accountsPartial(claimAcc(winner2)).signers([complianceKp]).rpc(), winner2_received: String(await tokenBal(ata(winner2.publicKey))), vault_left: String(await tokenBal(vault)) });
await expectFail('claim_twice', () => w1.methods.claim(new BN(700_000), new BN(1), [Array.from(l2)]).accountsPartial(claimAcc(winner1)).signers([complianceKp]).rpc());
process.exit(0);
