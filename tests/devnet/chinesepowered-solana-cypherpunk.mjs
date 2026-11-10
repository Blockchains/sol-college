// UniProof (chinesepowered-solana-cypherpunk fork) on devnet: university, credential issue, registrar + dean signatures,
// verify, selective-disclosure proof, revoke, and the program's rejections. Mirrors src/lib/solana/uniproof-client.ts.
// Usage (from the fork root, @coral-xyz/anchor 0.31): node chinesepowered-solana-cypherpunk.mjs <idl.json> <rpc> <payer.json>
// The payer funds fresh keys U (university authority), R (an unrelated wallet), S (student), X; unspent SOL goes back at the end.
// Role keys are saved next to the payer keypair (on the box, never committed) so SOL can be recovered after an interruption.
import fs from 'fs';
import anchor from '@coral-xyz/anchor';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, LAMPORTS_PER_SOL, sendAndConfirmTransaction } from '@solana/web3.js';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const [idlPath, rpc, payerPath] = process.argv.slice(2);
const rlFetch = async (url, opts) => { for (let i = 0; ; i++) { const r = await fetch(url, opts); if ((r.status !== 429 && r.status < 500) || i >= 12) return r; await new Promise(z => setTimeout(z, 1500 * (i + 1))); } };
const conn = new Connection(rpc, { commitment: 'confirmed', fetch: rlFetch, disableRetryOnRateLimit: true });
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
conn.confirmTransaction = async (arg) => { const sig = typeof arg === 'string' ? arg : arg.signature;
  for (let i = 0; i < 90; i++) { const st = (await conn.getSignatureStatuses([sig])).value[0];
    if (st && (st.confirmationStatus === 'confirmed' || st.confirmationStatus === 'finalized')) {
      if (st.err) throw new Error('tx failed ' + JSON.stringify(st.err)); return { context: { slot: st.slot }, value: { err: st.err } }; }
    await sleep(1000); } throw new Error('confirm timeout ' + sig); };
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8'));
const prog = (k) => new Program(idl, new AnchorProvider(conn, new Wallet(k), { commitment: 'confirmed' }));
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(payerPath, 'utf8'))));
const P = prog(payer), pid = P.programId, SOL = LAMPORTS_PER_SOL;
const log = (o) => console.log(JSON.stringify(o));
const err = (e) => String(e.error?.errorCode?.code || e.logs?.find(l => /Error|failed|already in use/.test(l)) || e.message).split('\n')[0].slice(0, 200);
const transient = (e) => /Backend error|StatusCode: 5|fetch failed|ECONNRESET|blockhash/i.test(String(e?.message || e));
const retry = async (fn) => { for (let i = 0; ; i++) { try { return await fn(); } catch (e) { if (!transient(e) || i >= 6) throw e; await sleep(4000 * (i + 1)); } } };
const expectFail = async (label, fn) => { try { const s = await retry(fn); log({ step: label, ok: false, error: 'UNEXPECTED SUCCESS', sig: s }); } catch (e) { log({ step: label, expectedFailure: true, error: err(e) }); } };
const pda = (...s) => PublicKey.findProgramAddressSync(s, pid)[0];
const uniOf = (pk) => pda(Buffer.from('university'), pk.toBuffer());
const credOf = (uni, n) => pda(Buffer.from('credential'), uni.toBuffer(), new BN(n).toArrayLike(Buffer, 'le', 8));
const U = Keypair.generate(), R = Keypair.generate(), S = Keypair.generate(), X = Keypair.generate();
const keyDir = process.env.ROLE_KEY_DIR || payerPath.replace(/[^/]*$/, '');
for (const [n, k] of [['U', U], ['R', R], ['S', S], ['X', X]]) try { fs.writeFileSync(`${keyDir}uniproof-${n}-${U.publicKey.toBase58().slice(0, 6)}.json`, JSON.stringify(Array.from(k.secretKey)), { mode: 0o600 }); } catch {}
const uni = uniOf(U.publicKey);
log({ step: 'setup', program: pid.toBase58(), U: U.publicKey.toBase58(), R: R.publicKey.toBase58(), S: S.publicKey.toBase58(), X: X.publicKey.toBase58(), university: uni.toBase58() });
log({ step: 'fund U 0.05, R 0.01, S 0.02, X 0.02 SOL', sig: await retry(() => sendAndConfirmTransaction(conn, new Transaction().add(
  ...[[U, 0.05], [R, 0.01], [S, 0.02], [X, 0.02]].map(([k, a]) => SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: k.publicKey, lamports: a * SOL }))), [payer], { commitment: 'confirmed' })) });
const initUni = (k, name, auth) => prog(k).methods.initializeUniversity(name, auth).accountsPartial({ university: uniOf(k.publicKey), authority: k.publicKey }).rpc();
log({ step: 'U initializes its university (PDA ["university", U])', ok: true, sig: await retry(() => initUni(U, 'sol.college Test University', U.publicKey)) });
await expectFail('U initializes a second university (one per authority)', () => initUni(U, 'Again', U.publicKey));
const issue = (auth, issuer, uniPk, n, student) => prog(issuer).methods.issueCredential(student, 'Bachelor of Science', 'Computer Science', new BN(1767225600), 'https://sol.college/')
  .accountsPartial({ credential: credOf(uniPk, n), university: uniPk, authority: auth.publicKey, issuer: issuer.publicKey })
  .signers(auth === issuer ? [] : [auth]).rpc();
const cred = credOf(uni, 0);
log({ step: 'U issues credential #0 to student S (PDA ["credential", university, 0])', ok: true, sig: await retry(() => issue(U, U, uni, 0, S.publicKey)), issued_pda: cred.toBase58() });
await expectFail('R tries to issue a credential from U\'s university (has_one authority)', () => issue(R, R, uni, 1, S.publicKey));
const sign = (k, m) => prog(k).methods[m]().accountsPartial({ credential: cred, university: uni, signer: k.publicKey }).rpc();
log({ step: 'R, an unrelated wallet, signs as registrar: accepted (sign_as_registrar checks no role)', ok: true, sig: await retry(() => sign(R, 'signAsRegistrar')) });
const verify = () => prog(S).methods.verifyCredential().accountsPartial({ credential: cred }).view();
log({ step: 'verify_credential after only the registrar signature', ok: true, valid: await retry(verify) });
log({ step: 'U signs as dean', ok: true, sig: await retry(() => sign(U, 'signAsDean')) });
log({ step: 'verify_credential after both signatures', ok: true, valid: await retry(verify) });
const disclose = (n) => prog(S).methods.createDisclosureProof(cred, { degreeOnly: {} }, new BN(n)).accountsPartial({ student: S.publicKey }).rpc();
log({ step: 'S creates a degree-only disclosure proof (nonce 1)', ok: true, sig: await retry(() => disclose(1)) });
await expectFail('S reuses disclosure nonce 1', () => disclose(1));
const revoke = (k) => prog(k).methods.revokeCredential().accountsPartial({ credential: cred, university: uni, authority: k.publicKey }).rpc();
await expectFail('R tries to revoke U\'s credential', () => revoke(R));
log({ step: 'U revokes credential #0', ok: true, sig: await retry(() => revoke(U)) });
await expectFail('R signs as registrar after revocation', () => sign(R, 'signAsRegistrar'));
log({ step: 'verify_credential after revocation', ok: true, valid: await retry(verify) });
log({ step: 'X initializes a university naming U as its authority (the argument is stored, the PDA is seeded by X)', ok: true, sig: await retry(() => initUni(X, 'Mismatched authority', U.publicKey)) });
await expectFail('X tries to issue from the university it created (rejected by the seeds check: the stored authority U no longer matches the PDA seed X, so the account is unusable)', () => issue(X, X, uniOf(X.publicKey), 0, S.publicKey));
const c = await retry(() => P.account.credential.fetch(cred));
log({ step: 'final credential state', registrar_signed: c.registrarSigned, dean_signed: c.deanSigned, revoked: c.isRevoked, student: c.student.toBase58() });
for (const k of [U, R, S, X]) { const bal = await retry(() => conn.getBalance(k.publicKey)); if (bal > 10000)
  log({ step: 'return unspent SOL to the payer', from: k.publicKey.toBase58(), sol: (bal - 5000) / SOL,
    sig: await retry(() => sendAndConfirmTransaction(conn, new Transaction().add(SystemProgram.transfer({ fromPubkey: k.publicKey, toPubkey: payer.publicKey, lamports: bal - 5000 })), [k], { commitment: 'confirmed' })) }); }
