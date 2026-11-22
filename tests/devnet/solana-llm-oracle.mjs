import fs from 'fs';
import { Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import { payer, conn, log, program, fund, expectFail, sendIx, BN } from './lib/labcommon.mjs';
const idl = JSON.parse(fs.readFileSync(new URL('../../dapps/static/solana-llm-oracle/idl.json', import.meta.url), 'utf8'));
const pid = new PublicKey(idl.address);
const prog = program(idl);
const pda = (...s) => PublicKey.findProgramAddressSync(s.map(x => typeof x === 'string' ? Buffer.from(x) : x), pid)[0];
const user = Keypair.generate(), stranger = Keypair.generate();
await fund(user.publicKey, 12_000_000); await fund(stranger.publicKey, 3_000_000);
try {
const pu = program(idl, user), ps = program(idl, stranger);
const config = pda('config');
log({ step: 'setup', program: pid.toBase58(), config: config.toBase58(), user: user.publicKey.toBase58(), oracle: payer.publicKey.toBase58() });
await expectFail('initialize_by_non_admin', () => ps.methods.initialize().accountsPartial({ admin: stranger.publicKey, config }).signers([stranger]).rpc());
let sig;
if (!(await conn.getAccountInfo(config))) { sig = await prog.methods.initialize().accountsPartial({ admin: payer.publicKey, config }).rpc(); log({ step: 'initialize', ok: true, sig }); }
const seed = 1, chat = pda('chat_context', user.publicKey.toBuffer(), Buffer.from([seed]));
sig = await pu.methods.createChat('You are a Solana devnet tutor. Answer in one sentence.', seed).accountsPartial({ user: user.publicKey, chatContext: chat }).signers([user]).rpc();
log({ step: 'create_chat', ok: true, sig, chat_context: chat.toBase58() });
const inference = pda('inference', user.publicKey.toBuffer(), chat.toBuffer());
const disc = idl.instructions.find(i => i.name === 'callback_test').discriminator;
sig = await pu.methods.createLlmInference('What is a PDA?', pid, disc, null).accountsPartial({ user: user.publicKey, chatContext: chat, inference }).signers([user]).rpc();
let inf = await prog.account.inference.fetch(inference);
log({ step: 'create_llm_inference', ok: true, sig, inference: inference.toBase58(), text: inf.text, is_processed: inf.isProcessed });
const answer = 'A PDA is an address derived from seeds and a program id that has no private key, so only that program can sign for it.';
await expectFail('callback_by_non_oracle', () => ps.methods.callbackFromLlm(answer).accountsPartial({ payer: stranger.publicKey, config, inference, program: pid }).signers([stranger]).rpc());
await expectFail('callback_test_without_config_signature', () => prog.methods.callbackTest('forged answer').accountsPartial({ config }).rpc());
sig = await prog.methods.callbackFromLlm(answer).accountsPartial({ payer: payer.publicKey, config, inference, program: pid }).rpc();
inf = await prog.account.inference.fetch(inference);
const tx = await conn.getTransaction(sig, { maxSupportedTransactionVersion: 0, commitment: 'confirmed' });
log({ step: 'callback_from_llm', ok: true, sig, is_processed: inf.isProcessed, callback_log: (tx.meta.logMessages || []).find(l => l.includes('Callback response')) });
sig = await pu.methods.createLlmInference('And what is a CPI? Please answer in more detail than before.', pid, disc, null).accountsPartial({ user: user.publicKey, chatContext: chat, inference }).signers([user]).rpc();
inf = await prog.account.inference.fetch(inference);
log({ step: 'create_llm_inference_reuse_resize', ok: true, sig, text: inf.text, is_processed: inf.isProcessed, data_len: (await conn.getAccountInfo(inference)).data.length });
await expectFail('create_chat_same_seed', () => pu.methods.createChat('again', seed).accountsPartial({ user: user.publicKey, chatContext: chat }).signers([user]).rpc());
} finally {
  for (const k of [user, stranger]) { const l = await conn.getBalance(k.publicKey); if (l > 0) await sendIx([SystemProgram.transfer({ fromPubkey: k.publicKey, toPubkey: payer.publicKey, lamports: l })], [payer, k]); }
  log({ step: 'cleanup_returned_lab_wallets' });
}
process.exit(0);
