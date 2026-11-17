"""Catalogue, evidence ledger, and articles that a chain read can support.
The numbered list is a publishing plan. A title gets a URL only when a record or this read can carry it.
Nothing here is a keyword page."""
import json, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
READ=os.path.join(ROOT,'dapps/articles/devnet-reads-2026-11-17.json')
LOG=os.path.join(ROOT,'tests/devnet/logs/gifter-escrow-2026-11-13-take-fix.jsonl')

def load_reads():
  d=json.loads(open(READ).read())
  if d.get('fetched')!='2026-11-17' or d.get('rpc')!='https://api.devnet.solana.com':
    raise SystemExit('articles: devnet read is not the 17 Nov 2026 snapshot')
  pixel, abort, take=d['txs']['pixel'], d['txs']['abort'], d['txs']['take']
  if pixel['fee']!=5000 or abort['fee']!=5000 or take['fee']!=5000:
    raise SystemExit('articles: expected fee 5000 on the three read transactions')
  if abort['preToken']!=abort['postToken']:
    raise SystemExit('articles: aborted take token balances are not unchanged')
  changed=[a for a in abort['accounts'] if a['pre']!=a['post']]
  if len(changed)!=1 or changed[0]['pre']-changed[0]['post']!=5000:
    raise SystemExit('articles: aborted take should move only the fee')
  pix={a['pubkey']:a for a in pixel['accounts']}
  if pix['EQhByMHgJxmhBmib6xWiqp36Unve5568A81fNJvmLMKA']['pre']!=0 or pix['EQhByMHgJxmhBmib6xWiqp36Unve5568A81fNJvmLMKA']['post']!=721360:
    raise SystemExit('articles: pixel account rent is not 721360')
  signer=pix['8WVmfKQ3D5QAzbg9cZvJtzPivLWtXqaKvHwJMTWRiNsa']
  if signer['pre']-signer['post']!=721360+5000:
    raise SystemExit('articles: pixel signer delta is not rent plus fee')
  closed=[a for a in take['accounts'] if a['post']==0 and a['pre']]
  got=take['accounts'][0]['post']-take['accounts'][0]['pre']
  if got!=sum(a['pre'] for a in closed)-5000:
    raise SystemExit('articles: completed take signer delta does not match closed rent minus fee')
  by={a['pubkey']:a for a in d['accounts']}
  expect={
    '368GPddGvhhbzwPRx5dwY78bVbHForatZvoCtovg2jGy':'10',
    '4aR3CewF1ZY2utnNxaifACknfifzihEEURaNTDB3PXcf':'5',
    '4RY5u7eRj1N1fVEyNWZF8wJP1YfsqDDNVL46dGXRCfbs':'995',
    '6Yf4zh1WHRv2yWJEBKuAXehcoq12Ftr5LG3mxjfypjpK':'990',
  }
  for pk, ui in expect.items():
    if not by[pk].get('exists') or by[pk].get('uiAmount')!=ui:
      raise SystemExit('articles: 17 Nov token balance drifted for '+pk[:6])
  for pk in ('v54wkHyoKHrJVzYFahztCScYhxz9BdypLvsJtvPC2G4','9aAYdmhB8fU5eyuRM7HaYbty4iC1DVxLZuqLEAJYLgSw'):
    if by[pk].get('exists'):
      raise SystemExit('articles: closed account still exists '+pk[:6])
  log=open(LOG).read()
  for mint in ('6yHzRTmukfp7DVAHNAb7hC5NxN6JDnPUSHWm22Exswpu','13WYoT3wv15uao4pu7kWffJZgbvLyKf8SkEivuLowwJ1'):
    if mint not in log:
      raise SystemExit('articles: mint missing from the 13 Nov log')
  return d

def acc(d, pk):
  for a in d['accounts']:
    if a['pubkey']==pk: return a
  raise SystemExit('articles: address missing from the read '+pk[:8])

def articles(E, tx, meta_block, credit, d):
  """Five pages. Numbers in the catalogue point here. Each one answers a different question."""
  C=lambda s: f'<code>{E(s)}</code>'
  pixel, abort, take=d['txs']['pixel'], d['txs']['abort'], d['txs']['take']
  wallet='8WVmfKQ3D5QAzbg9cZvJtzPivLWtXqaKvHwJMTWRiNsa'
  pixel_acct='EQhByMHgJxmhBmib6xWiqp36Unve5568A81fNJvmLMKA'
  program='GsFGX3pzdgzugAfjcxH9Lbbz2aPZgXyvBoXkNnmxXwuY'
  hosted='45C1bSkFCbjrqiQHqm8oS6J88jirW8rC46Qiu6TvoY6x'
  earlier='6Z5cvVUcJVFvkhmtJ4dYwgVqNn7jqN6TSisoYSihBA1r'
  mint_a='6yHzRTmukfp7DVAHNAb7hC5NxN6JDnPUSHWm22Exswpu'
  mint_b='13WYoT3wv15uao4pu7kWffJZgbvLyKf8SkEivuLowwJ1'
  maker_ata='6Yf4zh1WHRv2yWJEBKuAXehcoq12Ftr5LG3mxjfypjpK'
  taker_a='368GPddGvhhbzwPRx5dwY78bVbHForatZvoCtovg2jGy'
  maker_b='4aR3CewF1ZY2utnNxaifACknfifzihEEURaNTDB3PXcf'
  taker_b='4RY5u7eRj1N1fVEyNWZF8wJP1YfsqDDNVL46dGXRCfbs'
  escrow='v54wkHyoKHrJVzYFahztCScYhxz9BdypLvsJtvPC2G4'
  vault='9aAYdmhB8fU5eyuRM7HaYbty4iC1DVxLZuqLEAJYLgSw'
  maker='ExCmfnp2GQVRHb82wiZduqwdFgGbGxeJfXuypYk6pEJQ'
  taker='7v8vW5U5NWaRBAuS3ApFAQFHKKr176yjBcms4ZngSeY2'
  loader=acc(d, program)['programOwner']
  when='Chain read on 17 Nov 2026, confirmed, from api.devnet.solana.com. The transactions are the ones already in the deployment record.'
  # ---- 3 and 5
  rows=[
    (wallet,'Wallet','Signed the pixel create. The 17 Nov read shows a system-owned account, 0 bytes of data, not executable.', acc(d, wallet)),
    (pixel_acct,'Pixel account','Created by that transaction. The 17 Nov read shows 14 bytes, owned by the Picassol program, not executable, not a signer.', acc(d, pixel_acct)),
    (program,'Program','Picassol. Executable. Owned by the upgradeable loader. The account is 36 bytes. That is not the size of the program binary.', acc(d, program)),
    (hosted,'Program','Gifter, the hosted program. Same shape: executable, loader-owned, 36 bytes.', acc(d, hosted)),
    (earlier,'Program','Gifter, the earlier program whose take aborted. Still executable on this read. It is not the hosted program.', acc(d, earlier)),
    (mint_a,'Mint','Mint A. Owned by the Token program, parsed type mint, 82 bytes, 6 decimals.', acc(d, mint_a)),
    (mint_b,'Mint','Mint B. Same shape, 6 decimals.', acc(d, mint_b)),
    (maker_ata,'Token account','The maker’s mint A account. Owned by the Token program, 165 bytes. Its authority field is the maker address. That field is not the program owner.', acc(d, maker_ata)),
  ]
  body=''.join(
    '<tr><td>'+C(pk)+'</td><td>'+E(kind)+'</td><td>'+E(how)+'</td></tr>'
    for pk, kind, how, _row in rows)
  addr_title='A Solana address is not always a wallet'
  addr_desc='A sample of addresses from Picassol and Gifter, classified from the deployment logs and a devnet read on 17 Nov 2026.'
  addr=f'''<article class=lesson>
<p class=eyebrow>Fundamentals · Accounts</p>
<h1>{E(addr_title)}</h1>
<p class=lead>An address is a public key. It is not, by itself, a wallet. On these two recorded apps the same kind of string is a signer, a program, a mint, a token account, or an account a program owns. This page says which is which, and how that was decided.</p>
{meta_block([
  ('Who this is for','You can read a public key and you want to know what sort of thing it names before you treat it as a wallet.'),
  ('What you will learn','How a wallet, a program, a mint, a token account, and a program-owned account were told apart in this sample.'),
  ('Prerequisites','None. The chain read is already done.'),
  ('Record', when),
  ('Author','Sol.College, from that read and the deployment logs. No separate reviewer is named.'),
])}
<h2 id=sample>The sample</h2>
<table>
<thead><tr><th>Address</th><th>What it is</th><th>How it was identified</th></tr></thead>
<tbody>{body}</tbody>
</table>
<p>The program accounts are owned by {C(loader)}. A 36-byte program account is the address programs are called by. The Gifter build note, on a different commit, records a <code>.so</code> of 311,808 bytes. This read did not fetch that binary, and it did not fetch the program-data account.</p>
<h2 id=owner>Two different meanings of owner</h2>
<p>The pixel account’s owner is the Picassol program {C(program)}. That is the program allowed to change the account. The account did not sign the transaction that created it.</p>
<p>The token account {C(maker_ata)} has two different fields that are easy to mix up. The account’s program owner is the Token program {C('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA')}. The token balance’s authority, the field a parsed token account calls owner, is {C(maker)}. Only the Token program may change the account. The authority is who may approve a transfer of its tokens. Those are not the same control.</p>
<h2 id=gone>Addresses that are not accounts anymore</h2>
<p>The 13 Nov log names {C(escrow)} as escrow #1 and the completed take names {C(vault)} as the token account that closed. On 17 Nov both reads returned no account. In the transaction itself both went to 0 lamports.</p>
<p>The maker address {C(maker)} and the taker address {C(taker)} appear on that take, as the token authorities and, for the taker, as the fee payer. On 17 Nov neither address has an account. Their token accounts are still there, and those accounts still name these addresses as the authority. An authority pubkey does not imply a funded wallet account.</p>
<h2 id=limits>Limitations</h2>
<p>This is one confirmed read of these addresses on devnet. It is not a classifier for an arbitrary mainnet address. The read does not say where the maker and taker lamports went. The escrow address is identified from the run log and from the transaction, not by deriving the seeds again on this page.</p>
<h2 id=try>Continue</h2>
<ul class=continue-list>
<li><a href="/articles/where-picassol-stores-state/">Where the pixel account fits, and where the points counter does not</a></li>
<li><a href="/articles/what-is-a-solana-pda/">What the pixel account is for</a></li>
<li><a href="/articles/follow-one-token-balance/">Follow the token accounts through the completed take</a></li>
</ul>
{credit}</article>'''
  # ---- 4
  state_title='Where Picassol stores state, and the counter that does not'
  state_desc='A painted Picassol pixel is a 14-byte account created on devnet. The points counter is a separate API the static host does not run.'
  state=f'''<article class=lesson>
<p class=eyebrow>Fundamentals · Accounts</p>
<h1>{E(state_title)}</h1>
<p class=lead>Picassol’s canvas is not one account, and its points counter is not on the chain at all. A painted pixel is its own account. The counter stays at 0 because the static host does not run the author’s points API.</p>
{meta_block([
  ('Who this is for','You are looking at the canvas and trying to decide which number lives on Solana.'),
  ('What you will learn','Which account the recorded create made, and which displayed value is outside that transaction.'),
  ('Prerequisites','None. The <a href="/articles/what-is-a-solana-pda/">PDA article</a> is the seed explanation, if you want it next.'),
  ('Record','Deployment record verified 10 Nov 2026. Account read on 17 Nov 2026.'),
  ('Author','Sol.College. No separate reviewer is named.'),
])}
<h2 id=account>The account the click created</h2>
<p>The hosted click sent {tx(pixel['signature'])}. One account, {C(pixel_acct)}, went from 0 lamports to 721,360. The signer paid that rent plus the 5,000 lamport fee. On 17 Nov the account is 14 bytes and its program owner is {C(program)}.</p>
<p>The lesson file describes those 14 bytes as an 8-byte discriminator, then x, y, red, green, blue, and the bump. This chain read checked the length. It did not decode the fields again.</p>
<p>The canvas is 200 by 200. An unpainted cell has no account. The <a href="/articles/what-is-a-solana-pda/">PDA article</a> covers the seeds and the two recorded rejections, including <code>create_pixel</code> at x = 200.</p>
<h2 id=counter>The counter is not in the transaction</h2>
<p>The deployment record says the points and leaderboard call the author’s MongoDB route <code>/api/updateUserPoints</code>. The static host answers that POST with 501. The pixel transaction is unaffected, and the counter stays at 0. The create transaction above has no second instruction for a score. There is no points account in its account list.</p>
<h2 id=limits>Limitations</h2>
<p>This page traces one app. It does not say that every Solana interface splits state this way. The 501 and the counter are the 10 Nov record. They were not requested again on 17 Nov.</p>
<h2 id=try>Try it yourself</h2>
<p>Ready to paint one empty cell and read the account it creates? <a href="/lessons/picassol-hackathon/">Open the Picassol lesson</a>.</p>
<ul class=continue-list>
<li><a href="/articles/a-solana-address-is-not-a-wallet/">Which address is the wallet, the program, and the pixel</a></li>
<li><a href="/articles/read-a-solana-transaction/">Read the create transaction field by field</a></li>
</ul>
{credit}</article>'''
  # ---- 7
  read_title='Read a Solana transaction without guessing'
  read_desc='The Picassol create_pixel transaction, account by account: who signed, who was created, the fee, and the compute units the log and the meta agree on.'
  read=f'''<article class=lesson>
<p class=eyebrow>Transactions</p>
<h1>{E(read_title)}</h1>
<p class=lead>A signature is a pointer to a transaction. It does not tell you what happened until you read the accounts, the logs, the fee, and the balance changes. This page does that for one short transaction: the Picassol pixel create.</p>
{meta_block([
  ('Who this is for','You have an explorer tab open and you want a method, not a guess about which row matters.'),
  ('What you will learn','What each account on this transaction did, what the fee was, and which two compute figures agree.'),
  ('Prerequisites','None.'),
  ('Record', when+' Block time of this transaction: '+E(pixel['blockTimeUtc'])+' UTC.'),
  ('Author','Sol.College. No separate reviewer is named.'),
])}
<h2 id=fields>The fields, in order</h2>
<ol>
<li>Signature {tx(pixel['signature'])}. Slot {E(pixel['slot'])}. <code>err</code> is null, so the instructions completed.</li>
<li>Fee {E(pixel['fee'])} lamports, paid by the signer {C(wallet)}. The signer went from 179,081,200 lamports to 178,354,840. The difference is 726,360.</li>
<li>A new account {C(pixel_acct)} went from 0 to 721,360 lamports. 721,360 of rent plus the 5,000 fee is 726,360. The signer’s drop matches the new account plus the fee. Nothing else on this transaction changed lamports.</li>
<li>The log says <code>Instruction: CreatePixel</code>, then an inner call to the system program {C('11111111111111111111111111111111')}, then success. The program reports 9,740 compute units of a 200,000 budget. The transaction meta field <code>computeUnitsConsumed</code> is also 9,740.</li>
<li>There are no token balances. This instruction did not move a mint.</li>
</ol>
<p>Four accounts are listed. The signer is writable. The new pixel account is writable and is not a signer. The system program and the Picassol program are neither writable nor signers. They are there because the instruction calls them.</p>
<h2 id=not>What this read does not say</h2>
<p>It does not say the pixel’s colour. The account is 14 bytes on the later read; the lesson file describes the layout. It does not say the points counter moved. That counter is <a href="/articles/where-picassol-stores-state/">not in this transaction</a>.</p>
<h2 id=limits>Limitations</h2>
<p>One transaction, read on 17 Nov 2026 at commitment confirmed. The fee of 5,000 lamports is what this transaction reports. It is not a measurement of every Solana fee. A failed transaction can still charge a fee. The <a href="/articles/what-a-failed-transaction-changed/">next page</a> is the recorded abort, where that happened.</p>
<h2 id=try>Continue</h2>
<ul class=continue-list>
<li><a href="/articles/what-a-failed-transaction-changed/">What the aborted escrow take changed</a></li>
<li><a href="/lessons/picassol-hackathon/">Open the Picassol lesson and send your own create</a></li>
<li><a href="https://solana.com/docs/core/transactions">Solana’s transaction documentation</a></li>
</ul>
{credit}</article>'''
  # ---- 6
  fail_title='What changed when this transaction failed'
  fail_desc='On the aborted Gifter take, token balances stayed put and the fee payer lost 5,000 lamports. On the later completed take, tokens moved and two accounts closed.'
  pre=abort['preToken']
  def tokline(rows):
    return '; '.join(f"index {r['index']}: {r['ui']} of {r['mint'][:6]}…" for r in rows)
  changed_title='What changed when this transaction failed'
  changed=f'''<article class=lesson>
<p class=eyebrow>Troubleshooting · Transactions</p>
<h1>{E(changed_title)}</h1>
<p class=lead>A failed transaction is not a transaction that changed nothing. On the aborted Gifter take, the token balances were the same afterwards and the fee payer still lost 5,000 lamports. On the later take that completed, the same fee was charged and the tokens moved.</p>
{meta_block([
  ('Who this is for','You are comparing a red explorer row with a green one and you want the state change, not the root cause.'),
  ('What you will learn','Which balances moved on these two recorded takes, and which figures in the abort disagree.'),
  ('Prerequisites','You can open an explorer transaction. The cause of the abort is a <a href="/articles/why-this-escrow-take-failed/">separate article</a>.'),
  ('Record', when),
  ('Author','Sol.College. No separate reviewer is named.'),
])}
<h2 id=abort>The abort</h2>
<p>{tx(abort['signature'])} at {E(abort['blockTimeUtc'])} UTC. Program {C(earlier)}. <code>err</code> is <code>InstructionError</code> index 0, <code>ProgramFailedToComplete</code>. The log says <code>Instruction: TakeAndClose</code>, then an access violation reading 8 bytes at <code>0x10008</code>. There is no inner Token program call in the log.</p>
<p>One lamport balance changed. The fee payer {C(abort['accounts'][0]['pubkey'])} went from 120,000,000 to 119,995,000. That is the 5,000 lamport fee. The token rows are identical before and after: {E(tokline(pre))}.</p>
<p>The log says the program consumed 18,066 of 200,000 compute units. The meta field <code>computeUnitsConsumed</code> is 200,000. Both numbers are what the read returned. This page does not collapse them into one.</p>
<p>Those token mints, {C('7v8J9oDcLp2ErC8w3g1Z5qBtccNEVmqfibyTpfEaAad1')} and {C('8WZsMHBR6Nxw8xq4xwVzz2Na9EBY6gjJtWd29jjnxga6')}, belong to this earlier run. They are not mint A and mint B of the hosted program.</p>
<h2 id=done>The take that completed</h2>
<p>{tx(take['signature'])} at {E(take['blockTimeUtc'])} UTC, program {C(hosted)}. <code>err</code> is null. The fee is again 5,000 lamports. The log’s last compute line and the meta field agree: 55,673 of 200,000. The log includes inner Token program calls. The earlier abort does not.</p>
<p>Token balances, raw amounts at 6 decimals:</p>
<ul>
<li>Taker’s mint A account went from 0 to 10.</li>
<li>Maker’s mint B account went from 0 to 5.</li>
<li>Taker’s mint B account went from 1,000 to 995.</li>
<li>The vault held 10 of mint A beforehand and is absent afterwards.</li>
</ul>
<p>Two accounts went to 0 lamports: {C(vault)} from 1,488,440, and {C(escrow)} from 1,305,560. The fee payer {C(taker)} went from 120,000,000 to 122,789,000, a gain of 2,789,000. That is the two closed balances, 2,794,000, minus the 5,000 fee. The run log calls these the vault and the escrow state, and says both closed.</p>
<h2 id=limits>Limitations</h2>
<p>Two transactions, not a general rule about every failed Solana transaction. The 5,000 lamport fee is what these transactions report. The cause of the access violation is the other article. A substituted-mint take was not run.</p>
<h2 id=try>Continue</h2>
<ul class=continue-list>
<li><a href="/articles/why-this-escrow-take-failed/">Why the take aborted</a></li>
<li><a href="/articles/follow-one-token-balance/">The mint, the token accounts, and the wallets on the completed take</a></li>
<li><a href="/lessons/gifter-escrow/">Open the Gifter lesson</a></li>
</ul>
{credit}</article>'''
  # ---- 41
  bal_title='Follow one token balance through a completed escrow take'
  bal_desc='Mint A and mint B, the token accounts that held them, and the wallets named as authorities, from the 13 Nov take and a 17 Nov read.'
  sup=acc(d, mint_a).get('supply')
  bal=f'''<article class=lesson>
<p class=eyebrow>Tokens</p>
<h1>{E(bal_title)}</h1>
<p class=lead>A mint defines the token. A token account holds a balance of that mint. A wallet address can be the authority of a token account without being the account that stores the balance. The completed Gifter take moves 10 of mint A and 5 of mint B, and the 17 Nov read still shows those balances.</p>
{meta_block([
  ('Who this is for','You have heard “token” used for the mint, the balance, and the wallet, and you want one transfer where those are different addresses.'),
  ('What you will learn','Which address is the mint, which holds the balance, and which is only the authority, on this take.'),
  ('Prerequisites','None. The <a href="/articles/a-solana-address-is-not-a-wallet/#owner">two meanings of owner</a> are the shorter version.'),
  ('Record','Run log of 13 Nov 2026, transaction '+E(take['blockTimeUtc'])+' UTC, accounts reread 17 Nov 2026.'),
  ('Author','Sol.College. No separate reviewer is named.'),
])}
<h2 id=mints>The two mints</h2>
<p>The 13 Nov log creates mint A {C(mint_a)} and mint B {C(mint_b)}, each with 6 decimals. On 17 Nov both accounts are owned by the Token program, parsed type mint, 82 bytes. Mint A’s supply field is {E(sup)} raw units. At 6 decimals that is 1,050. The log records minting 1,000 to the maker and 50 to the UI wallet. The supply matches those two mints. This page does not claim it searched for every other mint instruction.</p>
<p>The amounts in the transaction are integers. 10 tokens of a 6-decimal mint are the raw amount 10000000. The parsed field <code>uiAmountString</code> is the decimal display. The transfer did not use a floating-point amount.</p>
<h2 id=move>What the take moved</h2>
<table>
<thead><tr><th>Token account</th><th>Mint</th><th>Authority</th><th>Before the take</th><th>After, and on 17 Nov</th></tr></thead>
<tbody>
<tr><td>{C(taker_a)}</td><td>A</td><td>{C(taker)}</td><td>0</td><td>10</td></tr>
<tr><td>{C(maker_b)}</td><td>B</td><td>{C(maker)}</td><td>0</td><td>5</td></tr>
<tr><td>{C(taker_b)}</td><td>B</td><td>{C(taker)}</td><td>1,000</td><td>995</td></tr>
<tr><td>{C(maker_ata)}</td><td>A</td><td>{C(maker)}</td><td>990 after the deposit, not moved by this take</td><td>990</td></tr>
<tr><td>{C(vault)}</td><td>A</td><td>{C(escrow)}</td><td>10</td><td>Account gone. The take set it to 0 lamports.</td></tr>
</tbody>
</table>
<p>The taker paid 5 of mint B and received the vault’s 10 of mint A. That is the swap the run log records. The vault’s authority was the escrow account, not the maker’s wallet. After the take, that escrow account is gone too.</p>
<p>On 17 Nov the maker and taker addresses themselves have no account. The token accounts above still name them as the authority, and the balances are still 10, 5, 995, and 990.</p>
<h2 id=limits>Limitations</h2>
<p>One completed take of these two mints. The aborted take used different mints, on the earlier program. A token with a transfer fee or a transfer hook was not part of this run. The hosted <code>Take</code> accounts constrain the maker. They do not, in the source excerpt, constrain the mint accounts to the stored mint keys, and a substituted mint was not run.</p>
<h2 id=try>Try it yourself</h2>
<p>The lesson is where you create and refund on the hosted app. <a href="/lessons/gifter-escrow/">Open the Gifter escrow lesson</a>. The completed take you are matching is {tx(take['signature'])}.</p>
<ul class=continue-list>
<li><a href="/articles/what-a-failed-transaction-changed/">What the aborted take changed instead</a></li>
<li><a href="/articles/tokens/">The token topic, including gree</a></li>
</ul>
{credit}</article>'''
  return [
    ('/articles/a-solana-address-is-not-a-wallet/', addr_title, addr_desc, addr, 'Fundamentals'),
    ('/articles/where-picassol-stores-state/', state_title, state_desc, state, 'Fundamentals'),
    ('/articles/read-a-solana-transaction/', read_title, read_desc, read, 'Practical guide'),
    ('/articles/what-a-failed-transaction-changed/', fail_title, fail_desc, changed, 'Troubleshooting'),
    ('/articles/follow-one-token-balance/', bal_title, bal_desc, bal, 'Practical guide'),
  ]

# Numbered plan. A slug means that proposal has a page. A related slug means a nearby page exists and is not this proposal.
PLAN=[
 ('A','Understand the system','Tell an address, an account, and a transaction apart before designing anything.',[
  (1,'Solana for backend developers: translate what you already know','',''),
  (2,'What actually happens when you click Approve in a Solana wallet?','',''),
  (3,'A Solana address is not always a wallet','a-solana-address-is-not-a-wallet',''),
  (4,'Where does a Solana application store its state?','where-picassol-stores-state',''),
  (5,'Program ownership versus wallet authority','a-solana-address-is-not-a-wallet#owner',''),
  (6,'What changes when a Solana transaction fails?','what-a-failed-transaction-changed',''),
  (7,'Read a Solana transaction without guessing','read-a-solana-transaction',''),
  (8,'From browser to program: draw the complete architecture of a small Solana app','',''),
 ]),
 ('B','A reproducible environment','A setup this repository has actually run, with versions and a failure written down.',[
  (9,'A reproducible Solana development environment from a clean machine','',''),
  (10,'Local validator, devnet, or mainnet? Choose the right test environment','',''),
  (11,'Diagnose a broken Solana toolchain without reinstalling everything','',''),
  (12,'Keep Rust, Anchor, and client dependencies compatible','',''),
  (13,'Manage program ids across local, test, and production environments','',''),
  (14,'Fund test wallets reliably without building around unlimited faucets','',''),
  (15,'Structure a Solana monorepo for programs, clients, tests, and documentation','',''),
  (16,'Make clone, install, test work for another developer','',''),
 ]),
 ('C','Accounts and state design','Schema, space, cost, growth, closing, and migration, on one evolving example.',[
  (17,'Design your first Solana account schema','',''),
  (18,'Calculate account space without hand-waving','',''),
  (19,'What does on-chain storage actually cost?','',''),
  (20,'One large account or many small accounts?','',''),
  (21,'Grow account data without breaking your application','',''),
  (22,'Close an account safely, and explain where its lamports go','',''),
  (23,'Version an account schema before you need a migration','',''),
  (24,'Design a state migration that can stop halfway','',''),
 ]),
 ('D','PDAs, instructions, and cross-program calls','From how an address is derived to who is allowed to act for it.',[
  (25,'PDAs explained by building a user profile registry','','what-is-a-solana-pda'),
  (26,'Choose PDA seeds that survive product changes','',''),
  (27,'Debug a PDA mismatch byte by byte','',''),
  (28,'What it means for a program to sign for a PDA','',''),
  (29,'Design instruction arguments and account lists together','',''),
  (30,'Your first CPI: trace a token transfer across programs','',''),
  (31,'Validate the program you are calling','',''),
  (32,'Trace privileges through a multi-step CPI flow','',''),
 ]),
 ('E','Transactions and reliable execution','What a signature authorises, and what to do when it expires, fails, or must be retried.',[
  (33,'Build a transaction from intent, not copy-pasted instructions','',''),
  (34,'What exactly does a Solana signature authorise?','',''),
  (35,'Safely collect signatures from multiple parties','',''),
  (36,'Submitted is not paid: build a transaction state machine','',''),
  (37,'Why transactions expire, and how to recover','',''),
  (38,'Retry a transaction without accidentally repeating the business action','',''),
  (39,'Estimate compute and set a fee budget transparently','',''),
  (40,'Why did this transaction fail? A structured debugging method','','why-this-escrow-take-failed'),
 ]),
 ('F','Tokens and token compatibility','A mint, a token account, and the ways a token can be more than a plain transfer.',[
  (41,'Mint account, token account, and wallet: follow one token balance','follow-one-token-balance',''),
  (42,'Create a token transfer that handles a missing destination account','',''),
  (43,'Convert token amounts without floating-point bugs','',''),
  (44,'Why a token’s name and symbol do not establish its identity','',''),
  (45,'Token program or Token Extensions? Build an explicit support policy','',''),
  (46,'Transfer fees: why sent and received amounts can differ','',''),
  (47,'Transfer hooks: what your integration must inspect and support','',''),
  (48,'Build a token compatibility test suite','',''),
 ]),
 ('G','Wallet and frontend engineering','The wallet as a product workflow.',[
  (49,'A wallet connection is not an application login','',''),
  (50,'Build a wallet flow that survives rejection and disconnects','',''),
  (51,'Prevent wrong-network actions before signing','',''),
  (52,'Make a transaction preview that explains what will change','',''),
  (53,'Stop stale balances from misleading users','',''),
  (54,'Build a read-only experience before requiring a wallet','',''),
  (55,'Passkeys and Solana wallets: evaluate the actual architecture','',''),
  (56,'Build accessible Solana interfaces','',''),
 ]),
 ('H','Testing that catches meaningful failures','Invariants, negative tests, and a bug that becomes a regression test.',[
  (57,'Test a Solana program by its invariants','',''),
  (58,'Happy-path tests are not a security strategy','',''),
  (59,'Build deterministic fixtures for multi-user programs','',''),
  (60,'Test deadline-based logic without waiting in real time','',''),
  (61,'Property-test token amounts and state transitions','',''),
  (62,'Test competing claims against the same funds','',''),
  (63,'Turn a bug report into a regression test','',''),
  (64,'Run Solana tests in CI without hiding flakiness','',''),
 ]),
 ('I','Security and authority boundaries','Teaching fixtures and reviews, kept separate from an undisclosed incident.',[
  (65,'Missing signer checks: reproduce the failure locally','',''),
  (66,'Validate account relationships, not just account types','',''),
  (67,'Reinitialisation: when create accidentally becomes overwrite','',''),
  (68,'Account aliasing: what if two inputs are the same account?','',''),
  (69,'Choose an arithmetic policy for fees, shares, and rounding','',''),
  (70,'Secure administrative instructions','',''),
  (71,'Threat-model a Solana escrow before writing it','',''),
  (72,'What a passing test suite does not prove','',''),
 ]),
 ('J','Payments and merchant systems','Invoice, verification, sponsorship, and refunds, with the costs named.',[
  (73,'Build a payment request that identifies the invoice','',''),
  (74,'Verify a payment without trusting the browser','',''),
  (75,'Accept a payment when the customer has no SOL','',''),
  (76,'Build a fee sponsor that cannot sign arbitrary transactions','',''),
  (77,'Prevent double fulfilment when payment notifications repeat','',''),
  (78,'Handle partial, excess, late, and wrong-asset payments','',''),
  (79,'Refund a payment without creating an uncontrolled withdrawal API','',''),
  (80,'Merchant settlement under uncertainty','',''),
 ]),
 ('K','RPC, indexing, and data correctness','What a provider response is evidence of, and what it is not.',[
  (81,'Build an RPC client that fails clearly','',''),
  (82,'Reconcile WebSocket events with authoritative reads','',''),
  (83,'Backfill missed activity without duplicating records','',''),
  (84,'Design a minimal Solana indexer','',''),
  (85,'Why two data sources may show different states','',''),
  (86,'Cache on-chain data without hiding important changes','',''),
  (87,'Reconcile your database with on-chain state','',''),
  (88,'Switch RPC providers without creating a second failure','',''),
 ]),
 ('L','Performance and operating cost','Measurements with versions and conditions, not a list of tips.',[
  (89,'Benchmark a Solana workflow without misleading yourself','',''),
  (90,'Find the bottleneck: browser, RPC, signing, or execution?','',''),
  (91,'Reduce compute only after establishing a baseline','',''),
  (92,'Measure contention from a shared writable account','',''),
  (93,'Smaller transactions: an instruction and account audit','',''),
  (94,'Evaluate address lookup tables for your actual workflow','',''),
  (95,'Batch operations without hiding failure semantics','',''),
  (96,'Build a cost model that includes more than network fees','',''),
 ]),
 ('M','Deployment and production operations','The gap between a devnet transaction and an application someone can operate.',[
  (97,'A production readiness review for a small Solana app','',''),
  (98,'Deploy with verifiable source and build provenance','',''),
  (99,'Design an upgrade authority policy','',''),
  (100,'Rotate authorities without losing control','',''),
  (101,'Monitor business invariants, not just server uptime','',''),
  (102,'Write an incident runbook before your first incident','',''),
  (103,'Recover from a broken client after a program upgrade','',''),
  (104,'Retire a Solana application responsibly','',''),
 ]),
 ('N','Complete application studies','A bounded app carried through specification, tests, failure, and operation.',[
  (105,'Build an escrow with explicit acceptance and refund rules','',''),
  (106,'Build a voting system and state exactly what one vote means','',''),
  (107,'Build a deadline-based claim system','',''),
  (108,'Build a credential registry with issuance and revocation','',''),
  (109,'Build milestone-based grant payments','',''),
  (110,'Build a spending-limit vault','',''),
  (111,'Build a crowdfunding campaign with refund conditions','',''),
  (112,'Build a merchant checkout from invoice to reconciliation','',''),
 ]),
 ('O','Investigations and contributions','A finding, a patch, and a published account that does not outrun the evidence.',[
  (113,'Give an AI agent transaction proposals, not unrestricted keys','',''),
  (114,'Build a policy layer for agent-initiated transfers','',''),
  (115,'Audit an agent’s claimed transaction outcome','',''),
  (116,'Keep secrets out of agent traces and debug logs','',''),
  (117,'Turn a practice-fork finding into a useful upstream issue','',''),
  (118,'Write a pull request another team can review','',''),
  (119,'Verify an AI-generated Solana patch','',''),
  (120,'Publish an engineering case study without overclaiming','from-failing-take-to-pull-request',''),
 ]),
]

def catalogue_tail(E):
  nav=''.join(f'<a href="#col-{cid}">{E(cid)}</a>' for cid,_n,_b,_i in PLAN)
  blocks=[]
  numbered=set()
  for cid, name, blurb, items in PLAN:
    lis=[]
    for n, title, slug, related in items:
      if slug:
        numbered.add(slug.split('#')[0])
        if '#' in slug:
          base, frag=slug.split('#', 1)
          href='/articles/'+base+'/#'+frag
        else:
          href='/articles/'+slug+'/'
        lis.append(f'<li><a href="{E(href)}">{n}. {E(title)}</a></li>')
      elif related:
        lis.append('<li class=proposal>'+str(n)+'. '+E(title)+'. No page yet. Nearby record: <a href="/articles/'+E(related)+'/">'+E(related.replace('-',' '))+'</a>.</li>')
      else:
        lis.append(f'<li class=proposal>{n}. {E(title)}. No page yet.</li>')
    note=''
    if cid=='B':
      note='<p>Recorded, and not one of those titles: <a href="/articles/what-we-could-build-for-this-escrow/">what the 13 Nov build produced</a>. The <a href="/how-to-build/setup/">setup guide</a> points at the current install docs. It is not a clean-machine manifest.</p>'
    elif cid=='D':
      note='<p>Recorded, and not title 25: <a href="/articles/what-is-a-solana-pda/">one pixel, one account</a>. A profile registry has not been built for title 25.</p>'
    elif cid=='H':
      note='<p><a href="/articles/from-failing-take-to-pull-request/">The case study</a> names a regression-test file and records no passing run. Title 63 has no page.</p>'
    elif cid=='I':
      note='<p>The <a href="/how-to-build/security-checklist/">security checklist</a> is a list of questions. This library does not add a local exploit fixture.</p>'
    elif cid=='N':
      note='<p>The Gifter and Picassol <a href="/lessons/">lessons</a> are practice on recorded apps. They are not titles 105 to 112.</p>'
    blocks.append(f'<h2 id="col-{cid}">{E(cid)}. {E(name)}</h2><p>{E(blurb)}</p>{note}<ol>{"".join(lis)}</ol>')
  return nav, ''.join(blocks), numbered

def evidence_page(E, tx, meta_block, credit, d):
  pixel, abort, take=d['txs']['pixel'], d['txs']['abort'], d['txs']['take']
  rows=[
    ('Pixel create fee and rent','getTransaction, confirmed, 17 Nov 2026', tx(pixel['signature']), 'Fee 5000. New account 0 to 721360. Signer drop equals the sum.', 'One transaction.'),
    ('Pixel compute units','Same read', 'log and meta', 'Both say 9740.', 'Not a budget recommendation.'),
    ('Aborted take fee and tokens','getTransaction, confirmed, 17 Nov 2026', tx(abort['signature']), 'Fee 5000. Token rows identical. One lamport change.', 'Log says 18066 compute units. Meta says 200000.'),
    ('Completed take','getTransaction plus the 13 Nov log', tx(take['signature']), 'Fee 5000. 10 of mint A to the taker, 5 of mint B to the maker. Two accounts to 0 lamports. Signer gain equals closed rent minus the fee.', 'Different mints from the abort.'),
    ('Balances still there on 17 Nov','getMultipleAccounts', 'four token accounts', '10, 5, 995, and 990.', 'Maker and taker wallet accounts were absent.'),
    ('Program account size','getMultipleAccounts', 'three program ids', '36 bytes, executable, upgradeable loader.', 'Not the .so size. The build note’s .so is a different commit.'),
    ('Gifter build','Lesson build note, 13 Nov 2026', 'commit a9c3a417', '.so of 311808 bytes, then an IDL failure. anchor test was not run.', 'Not the hosted commit fb2bbfd.'),
    ('Upstream pull request','dapps/patches/gifter-escrow/UPSTREAM_PR.md', 'berkaycirak/gifter-escrow#1', 'Recorded as opened.', 'No merge is recorded.'),
  ]
  body=''.join('<tr><td>'+E(a)+'</td><td>'+E(b)+'</td><td>'+c+'</td><td>'+E(e)+'</td><td>'+E(f)+'</td></tr>' for a,b,c,e,f in rows)
  title='Evidence for the articles'
  desc='The claims in the articles that depend on a version or a read, with the source, the result, and the limit.'
  html=f'''<article class=lesson>
<p class=eyebrow>Ledger</p>
<h1>{E(title)}</h1>
<p class=lead>A claim that depends on a particular run stays attached to that run. Changing a sentence on an article does not, by itself, mean the example was run again. This page is the list. No reviewer is named, because nobody separate from the record has signed it.</p>
{meta_block([
  ('Last chain read','17 Nov 2026, confirmed, api.devnet.solana.com.'),
  ('Deployment records','Picassol 10 Nov 2026. Gifter 13 Nov 2026.'),
  ('What is not here','A passing anchor test, a merged pull request, or a mainnet measurement.'),
])}
<table>
<thead><tr><th>Claim</th><th>Source</th><th>Where</th><th>Observed</th><th>Limit</th></tr></thead>
<tbody>{body}</tbody>
</table>
<p><a href="/articles/">Back to the catalogue</a></p>
{credit}</article>'''
  return title, desc, html

def path_page(E, meta, credit):
  title='Understand, reproduce, then build'
  desc='The published articles in workflow order. Stages with no recorded article are named and not linked.'
  html=f'''<article class=lesson>
<p class=eyebrow>Path</p>
<h1>{E(title)}</h1>
<p class=lead>This is the order for the articles that exist. Each one can be read on its own. The order is here so the questions stack: what an address is, where state lives, what a transaction shows, what a failure changes, and what was actually built.</p>
<h2 id=order>Published, in order</h2>
<ol>
<li><a href="/articles/a-solana-address-is-not-a-wallet/">A Solana address is not always a wallet</a></li>
<li><a href="/articles/where-picassol-stores-state/">Where Picassol stores state</a></li>
<li><a href="/articles/what-is-a-solana-pda/">What a PDA is, on one pixel</a></li>
<li><a href="/articles/read-a-solana-transaction/">Read one transaction</a></li>
<li><a href="/articles/what-a-failed-transaction-changed/">What a failed transaction changed</a></li>
<li><a href="/articles/why-this-escrow-take-failed/">Why that take aborted</a></li>
<li><a href="/articles/follow-one-token-balance/">Follow the token balances</a></li>
<li><a href="/articles/what-we-could-build-for-this-escrow/">What the recorded build produced</a></li>
<li><a href="/articles/from-failing-take-to-pull-request/">The case study of the opened pull request</a></li>
</ol>
<h2 id=gaps>Stages with no article</h2>
<ul>
<li>Design. No schema or seed-choice article beyond the accounts these apps already use.</li>
<li>Test. The case study names a test file. No passing run is recorded, so there is no testing article yet.</li>
<li>Secure. The <a href="/how-to-build/security-checklist/">checklist</a> is questions, not a fixture.</li>
<li>Deploy, observe, recover. The hosted apps are on devnet. There is no production-operations article.</li>
</ul>
<p>Lessons for the two apps are <a href="/lessons/picassol-hackathon/">Picassol</a> and <a href="/lessons/gifter-escrow/">Gifter</a>. They are the practice, not a missing chapter of these articles.</p>
<p><a href="/articles/">The catalogue</a> · <a href="/articles/evidence/">The evidence ledger</a></p>
{credit}</article>'''
  return title, desc, html
