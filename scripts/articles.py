"""Articles: explanations of recorded Sol.College work. A lesson is the practice; an article answers a question.
Run from core_lessons.py. Nothing here is a keyword page, and no claim is added that the deployment record does not already make."""
import html, json, os, re
import article_library as library
SITE='https://sol.college'
PUBLISHED='2026-11-17'
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def E(s):
  return html.escape(str(s if s is not None else ''), quote=True)
def tx(sig):
  return f'<a href="https://explorer.solana.com/tx/{sig}?cluster=devnet"><code>{E(sig[:8])}…</code></a>'
def one(text, n=180):
  t=' '.join(str(text or '').split())
  if len(t)<=n: return t
  return t[:n].rsplit(' ',1)[0]+'…'
def load():
  live={x['slug']:x for x in json.load(open(os.path.join(ROOT,'dapps/live.json')))}
  def lesson(slug):
    return json.load(open(os.path.join(ROOT,'dapps/lessons',slug+'.json')))
  return live, lesson
def lim(x):
  v=x.get('limits')
  if isinstance(v, list): v=v[0] if v else ''
  return one(v, 220)
def learn(x):
  return one(x.get('learn') or '', 220)
def meta_block(rows):
  body=''.join(f'<dt>{E(k)}</dt><dd>{v}</dd>' for k,v in rows)
  return f'<dl class=article-meta>{body}</dl>'
def shell(crumbs, kicker, title, lead, body):
  crumb='<nav class=crumbs aria-label=Breadcrumb>'+' / '.join(crumbs)+'</nav>'
  return f'{crumb}<article class=lesson><p class=eyebrow>{E(kicker)}</p><h1>{E(title)}</h1><p class=lead>{lead}</p>{body}</article>'
def ld(title, desc, path, kind='Article'):
  return {'@context':'https://schema.org','@type':kind,'headline':title,'description':desc,
    'datePublished':PUBLISHED,'dateModified':PUBLISHED,
    'author':{'@type':'Organization','name':'Sol.College','url':SITE+'/'},
    'publisher':{'@type':'Organization','name':'Sol.College','url':SITE+'/'},
    'mainEntityOfPage':SITE+path}
def write_page(S, page, css, path, title, desc, main, data):
  html_page=page(css+main, title+' | Sol.College', desc, path)
  blob=json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
  html_page=html_page.replace('</head>', f'<script type="application/ld+json">{blob}</script></head>', 1)
  os.makedirs(os.path.dirname(f'{S}{path}index.html'), exist_ok=True)
  open(f'{S}{path}index.html','w').write(html_page)
RELATED={
  'picassol-hackathon':[
    ('a-solana-address-is-not-a-wallet','Read which address on this canvas is a wallet, which is the program, and which is the pixel account.'),
    ('where-picassol-stores-state','Read where a painted pixel is stored, and why the points counter stays at 0.'),
    ('what-is-a-solana-pda','Read the explanation of this pixel account before you paint one.'),
  ],
  'gifter-escrow':[
    ('what-a-failed-transaction-changed','Read what the aborted take changed, and what the completed take changed.'),
    ('follow-one-token-balance','Read the mint, the token accounts, and the wallets on the completed take.'),
    ('why-this-escrow-take-failed','Read why an earlier take aborted, and which program this hosted app uses now.'),
    ('from-failing-take-to-pull-request','Read the case study of the pull request that was opened for that failure.'),
  ],
}
def attach(S):
  for slug, links in RELATED.items():
    fp=f'{S}/lessons/{slug}/index.html'
    if not os.path.exists(fp): continue
    items=''.join(f'<li><a href="/articles/{E(a)}/">{E(text)}</a></li>' for a,text in links)
    box=f'<aside class=goals><h2>Read the explanation</h2><ul>{items}</ul></aside>'
    t=open(fp).read().replace('<!--sc-article-->', box, 1)
    open(fp,'w').write(t)
def write(S, page, CSS):
  live, lesson=load()
  pic=live['picassol-hackathon']; gif=live['gifter-escrow']
  trust=live['trustlock']; gree=live['gree']; poe=live['poe-solana']
  for need, sig in (
    (pic,'2yj2GAqcniqCBFkL2yekqVRtJk4fjKopQNvVRgY1bGCGJjZioTd9gFwMGU7fgy8CedBt6QEwy4oaxXVqy6EUhtGb'),
    (gif,'33yMgZzAaH3mMcHgSmQBRVb4FeRmu5gX6nkAMfJU2T8F8sAwqMDTVfgsVcg7MXPM28GoAo7RPC7E35NhkNSrLXZd'),
    (gif,'ck53TqoU8UfpBav2V3bE1oy4Wm2qvxeU6bgibkXqzCsbP4YbBxDGK98bJxoowGpKNwkkPotBtCxVfUQMEm2zZu7'),
  ):
    if not any(sig in str(step) for step in need.get('steps', [])) and sig.startswith('ck53') is False:
      raise SystemExit('articles: missing recorded signature '+sig[:8])
  # ck53 is the earlier program, cited in limits rather than steps
  if 'ck53TqoU' not in json.dumps(gif):
    raise SystemExit('articles: gifter record no longer cites the earlier failing take')
  diagram=lesson('picassol-hackathon').get('diagram') or ''
  home=f'<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <span>Articles</span></nav>'
  hub=f'<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/articles/">Articles</a> / <span>{{}}</span></nav>'
  art=lambda name: f'<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/articles/">Articles</a> / <span>{E(name)}</span></nav>'
  credit='<p class=note>Drawn from the Sol.College deployment record and the lesson file. No separate reviewer is named on this page. Published '+PUBLISHED+'.</p>'
  # ---- article: PDA
  pda_title='What is a Solana PDA? One pixel, one account'
  pda_desc='A PDA is an address a program derives from seeds. Picassol stores each painted pixel at seeds ["pixel", x, y]. Recorded on devnet 10 Nov 2026.'
  pda=art('What is a Solana PDA?')+f'''<article class=lesson>
<p class=eyebrow>Fundamentals · Accounts</p>
<h1>{E(pda_title)}</h1>
<p class=lead>A program derived address is an address a program computes from its program id and a list of seeds. It is chosen so that it has no private key. In Picassol, each painted pixel is one such account. Anyone can recompute the address from the coordinates. Only that program can create it.</p>
{meta_block([
  ('Who this is for','You have seen the word PDA and want one account you can point at.'),
  ('What you will learn','What seeds and a bump are for, what this pixel account holds, and which recorded transaction created one.'),
  ('Prerequisites','None to read this. A devnet wallet is needed only if you paint a pixel in the lesson.'),
  ('Record','Devnet, verified '+E(pic['verified'])+'. Program <code>'+E(pic['program'])+'</code>. Commit <code>'+E(pic['commit'][:7])+'</code>.'),
  ('Author','Sol.College, from that deployment record.'),
])}
<h2 id=concept>The address is computed</h2>
<p>A wallet address comes from a keypair, so someone can sign for it. A PDA is derived so that it falls off the ed25519 curve. No one holds a private key for it. The program that derived it can be treated as the signer for that address, for one instruction, by passing the same seeds. Clients recompute the address from the seeds, so the address does not have to be stored anywhere else.</p>
<p>The extra byte that pushes the address off the curve is the bump. The <a href="/lessons/glossary/#pda">glossary entry for PDA</a> is the short definition. This page is the working example.</p>
<h2 id=example>Picassol: one account per coordinate</h2>
<p>{E(pic['learn'])}</p>
<pre class=diagram>{E(diagram)}</pre>
<p>The account is 14 bytes: an 8-byte discriminator, then x, y, red, green, blue, and the bump. The canvas is 200 by 200, so 40,000 addresses are possible. Only a pixel that has been painted has an account. An empty cell is the absence of that account, not a white account.</p>
<p>The lesson records two rejections. <code>create_pixel</code> at x = 200 returns <code>InvalidXCoordinate</code>. Creating the same pixel again fails because the account is already initialised. The colour comparisons in the program are against a <code>u8</code>, which is already between 0 and 255, so those comparisons cannot fail.</p>
<h2 id=reproduce>The recorded create</h2>
<p>On {E(pic['verified'])} a click on an empty cell of the hosted canvas sent <code>create_pixel</code>. The signature is {tx('2yj2GAqcniqCBFkL2yekqVRtJk4fjKopQNvVRgY1bGCGJjZioTd9gFwMGU7fgy8CedBt6QEwy4oaxXVqy6EUhtGb')}. Recolouring the same pixel was run from the test script ({tx('37Ri7VJHRydxi4uqHRJ57TmSSAWgmiDEdFGeMhnzVk4yo6teQpYiB29538g4fLToSh27brHxzKm7q8dubAXGnrYa')}), not from a second click in that UI pass. The program was written for Anchor 0.26.0. This page does not claim a fresh build.</p>
<h2 id=mistakes>Common mistakes</h2>
<ul>
<li>Treating the pixel address as a wallet you can import. There is no private key.</li>
<li>Expecting all 40,000 pixels to exist before anyone paints. Only painted pixels are accounts.</li>
<li>Reading the points counter as part of the pixel. It stays at 0 on this host.</li>
</ul>
<h2 id=limits>Limitations</h2>
<p>{E(lim(pic))} The source for the seeds is <a href="{E(pic['source'][1][1])}">lib.rs at the pinned commit</a>.</p>
<h2 id=try>Try it yourself</h2>
<p>Ready to paint one empty pixel and read the account it creates? <a href="/lessons/picassol-hackathon/">Open the Picassol lesson</a>. The lesson is the practice. This page is the explanation.</p>
<h2 id=next>Continue</h2>
<ul class=continue-list>
<li><a href="/articles/accounts/">Accounts, ownership, signers, and PDAs</a></li>
<li><a href="/articles/why-this-escrow-take-failed/">A PDA that holds tokens: why one escrow take aborted</a></li>
<li><a href="/lessons/glossary/#seeds">Seeds in the glossary</a></li>
</ul>
{credit}</article>'''
  # ---- article: failure
  fail_title='Why this escrow take failed'
  fail_desc='On program 6Z5cvVUc the Gifter take aborted with an access violation. The hosted app recorded on 13 Nov 2026 is a later program, and its take completed.'
  fail=art('Why this escrow take failed')+f'''<article class=lesson>
<p class=eyebrow>Troubleshooting · Tokens</p>
<h1>{E(fail_title)}</h1>
<p class=lead>The take that aborted was not a rejected Anchor constraint, and it was not the refund. On an earlier devnet program the <code>take_and_close</code> instruction finalized as a failed transaction: an access violation at <code>0x10008</code>. The program this site hosts now is a later deployment. On that program the same swap completed.</p>
{meta_block([
  ('Who this is for','You are looking at a failed escrow transaction and need to know which program it was, and whether the hosted app still does that.'),
  ('What you will learn','How this failure showed up, the two causes recorded for it, and which signature is the later successful take.'),
  ('Prerequisites','You can read an explorer transaction. You do not need a wallet to read this page.'),
  ('Record','Hosted program <code>'+E(gif['program'])+'</code>, verified '+E(gif['verified'])+'. Earlier failing program cited in that record as 6Z5cvVUc….'),
  ('Author','Sol.College, from the deployment record and the opened pull request note.'),
])}
<h2 id=problem>What failed, and where</h2>
<p>Signature {tx('ck53TqoU8UfpBav2V3bE1oy4Wm2qvxeU6bgibkXqzCsbP4YbBxDGK98bJxoowGpKNwkkPotBtCxVfUQMEm2zZu7')} is <code>ProgramFailedToComplete</code> on program <code>6Z5cvVUc…</code>. The recorded log is <code>Instruction: TakeAndClose</code>, then an access violation reading 8 bytes at <code>0x10008</code>. No inner cross-program invocation is recorded on that failure. Mint B did not move, and the vault still held mint A, so the maker could refund.</p>
<p>That is a program abort. It is not <code>ConstraintSeeds</code>, not an insufficient-funds error, and not a wallet the learner rejected. On the hosted app of that earlier build, pressing Accept simulated the instruction, the simulation failed, and no transaction was sent from the page.</p>
<h2 id=causes>The two causes in the pull-request note</h2>
<p>The note at <a href="https://github.com/Blockchains/sol-college/blob/main/dapps/patches/gifter-escrow/UPSTREAM_PR.md">dapps/patches/gifter-escrow/UPSTREAM_PR.md</a> records two causes, in order:</p>
<ol>
<li><code>send_to_maker</code> started with <code>println!("Hello")</code>. That is not a supported log on the BPF virtual machine. <code>msg!</code> is the log macro that is.</li>
<li>After that line was removed, take still aborted during account validation. The <code>seeds</code> attribute used <code>escrow_id.to_le_bytes().as_ref()</code>, and that reference did not live long enough. The note calls it a dangling pointer.</li>
</ol>
<p>The hosted commit <code>fb2bbfd</code> is the later one. In <code>take.rs</code> at that commit, <code>send_to_maker</code> has no <code>println!</code>. The account constraint checks the maker against the stored key. The handler copies the seed bytes into owned locals and still calls <code>create_program_address</code>. A comment above the account says not to put <code>to_le_bytes()</code> in <code>seeds = []</code>, and not to call <code>create_program_address</code> there because it can exhaust the heap. The source at this commit does call it. The recorded take on this program completed anyway. This page does not add a theory for why the heap limit was not hit.</p>
<h2 id=later>The hosted program on 13 Nov 2026</h2>
<p>Program <code>{E(gif['program'])}</code> is the app at <a href="{E(gif['app'])}">{E(gif['app'])}</a>. Signature {tx('33yMgZzAaH3mMcHgSmQBRVb4FeRmu5gX6nkAMfJU2T8F8sAwqMDTVfgsVcg7MXPM28GoAo7RPC7E35NhkNSrLXZd')} completed: the taker paid 5 of mint B, received 10 of mint A, and the vault and the state account closed. The upgrade that landed the seed-byte fix is {tx('4HaARQTeA2dbGcQ73QuD3GDyrtd5xvZJHcDKZRKARioDdHNEjnYziDauM8d2Pi3tVZSZVhEunxkHvC872aafvs9n')}.</p>
<p>The click-through that day created and refunded from the form. It did not press Accept, because no escrow opened by someone else was left. Do not describe that click-through as a clicked take.</p>
<h2 id=investigate>How the record was read</h2>
<ol>
<li>Confirm the program id on the transaction. <code>6Z5cvVUc…</code> and <code>45C1bSkF…</code> are different deployments.</li>
<li>Read the program log before the error name. <code>Instruction: TakeAndClose</code> followed by an access violation is an abort inside the program. A constraint failure names the constraint.</li>
<li>Check whether tokens moved. On the failing take they did not, which is why refund could still return the deposit.</li>
<li>Separate a simulation that never sent a transaction from a transaction that landed and failed.</li>
</ol>
<h2 id=mistakes>Common mistakes</h2>
<ul>
<li>Calling this a refund bug. The recorded refunds succeeded, on both programs.</li>
<li>Treating the earlier abort as the behavior of the hosted app. The deployment record says <code>6Z5cvVUc…</code> is still on devnet and is not the hosted program.</li>
<li>Expecting a substituted mint B to fail a constraint. That case was not run. The hosted <code>Take</code> accounts constrain the maker. The excerpt does not constrain <code>mint_a</code> or <code>mint_b</code> to the stored mints.</li>
</ul>
<h2 id=limits>Limitations</h2>
<p>The card still promises a GFT reward. The program has no reward-mint instruction. The escrow list is fetched once when the wallet connects and does not refresh until reload. The upstream pull request is recorded as opened, not as merged. This is a finding on a practice fork, published in that pull request. It is not a write-up of an undisclosed upstream incident.</p>
<h2 id=try>Try it yourself</h2>
<p>To create and refund on the hosted app, and to read the completed take next to the earlier failure, <a href="/lessons/gifter-escrow/">open the Gifter escrow lesson</a>.</p>
<h2 id=next>Continue</h2>
<ul class=continue-list>
<li><a href="/articles/from-failing-take-to-pull-request/">From the failing take to the opened pull request</a></li>
<li><a href="/articles/what-we-could-build-for-this-escrow/">What the recorded build of an earlier commit produced</a></li>
<li><a href="/articles/tokens/">Token accounts, transfers, and escrow</a></li>
</ul>
{credit}</article>'''
  # ---- article: build
  build_title='What the recorded build of this escrow produced'
  build_desc='On 13 Nov 2026 an Anchor 0.30.1 build of an earlier Gifter commit produced a .so, then failed while building the IDL. anchor test was not run.'
  build=art('What the recorded build produced')+f'''<article class=lesson>
<p class=eyebrow>Practical guide · Testing</p>
<h1>{E(build_title)}</h1>
<p class=lead>One build of this escrow program was recorded. Cargo finished and wrote a valid <code>.so</code>. Anchor then failed while building the IDL. <code>anchor test</code> was not run. That build checked out an earlier commit than the program the site hosts.</p>
{meta_block([
  ('Who this is for','You want to know what “we built it” means for this escrow, before you spend an afternoon on the toolchain.'),
  ('What you will learn','The commit, the Anchor version, the toolchain pin, the artifact, and the step that failed.'),
  ('Prerequisites','None. The toolchain install itself is the existing <a href="/how-to-build/setup/">setup guide</a>, which follows the current Solana docs rather than a copied command.'),
  ('Record','13 Nov 2026, Europe/London. Commit <code>a9c3a417d2d78294f58975b1461859ffb20df05a</code>. Anchor 0.30.1. <code>RUSTUP_TOOLCHAIN=1.89.0</code>.'),
  ('Author','Sol.College, from the lesson’s build note.'),
])}
<h2 id=command>What was run</h2>
<p>In <code>contract/</code>, after <code>git checkout a9c3a417d2d78294f58975b1461859ffb20df05a</code>, the command was <code>/home/box/.avm/bin/anchor-0.30.1 build</code> with <code>RUSTUP_TOOLCHAIN=1.89.0</code>. Cargo finished a release build in 1 minute 13 seconds and wrote <code>target/deploy/gifter_escrow.so</code>, 311,808 bytes, a valid ELF.</p>
<h2 id=failed>What failed</h2>
<p>Anchor then stopped at “Building IDL failed” with a <code>proc-macro-error</code> Span trait error. The note calls this the same host-toolchain issue seen on another lesson, not a defect in the program’s logic. The default host rustc was 1.99, which was too new for that Anchor. The pin used was 1.89.</p>
<p><code>anchor test</code> was not run on that commit. A later pull request adds <code>contract/tests/take-and-close.ts</code> and describes what the test asserts. This build record does not say that file passed.</p>
<h2 id=which>Which commit this was</h2>
<p>The hosted program recorded on the same day is <code>{E(gif['program'])}</code> at commit <code>{E(gif['commit'])}</code>. The build above is <code>a9c3a417…</code>, not that commit. The fork’s <code>declare_id!</code> is still <code>9HP45DvS…</code>. A local build targets the declared id unless you change it. Do not treat the <code>.so</code> from <code>a9c3a417…</code> as the binary behind the hosted app.</p>
<h2 id=limits>Limitations</h2>
<p>There is no recorded successful <code>anchor test</code>, and no recorded IDL for this build. The workspace path and the Anchor version are what the lesson file states. Commands for installing Rust and Anchor change; use the setup guide’s link to the current docs.</p>
<h2 id=try>Try it yourself</h2>
<p>The practice is the hosted app, not a local rebuild. <a href="/lessons/gifter-escrow/">Open the Gifter escrow lesson</a> for the accounts and the recorded transactions. <a href="/how-to-build/anchor-workflow/">The Anchor workflow guide</a> is the general sequence of init, build, and keys.</p>
<h2 id=next>Continue</h2>
<ul class=continue-list>
<li><a href="/articles/from-failing-take-to-pull-request/">The pull request opened from the failing take</a></li>
<li><a href="/articles/testing/">Tests, failures, and contributions</a></li>
<li><a href="/how-to-build/testing/">Testing Solana programs</a></li>
</ul>
{credit}</article>'''
  # ---- article: case study
  case_title='From a failing escrow take to an opened pull request'
  case_desc='A practice-fork finding on Gifter escrow: the take aborted, a patch and a regression test were proposed, and pull request 1 was opened. No merge is recorded.'
  case=art('From a failing take to an opened pull request')+f'''<article class=lesson>
<p class=eyebrow>Case study · Testing</p>
<h1>{E(case_title)}</h1>
<p class=lead>The take on an earlier Gifter deployment aborted. A patch on a practice fork removed the illegal log, stopped the seeds attribute from holding a temporary pointer, and fixed an empty token dropdown. Pull request 1 was opened on the original repository. This record does not say the original maintainers merged it.</p>
{meta_block([
  ('Who this is for','You want the status of this finding: what changed, what was tested, and what was left with the original project.'),
  ('What you will learn','Which repository, commits, and transactions the note cites, and how an opened pull request differs from an accepted one.'),
  ('Prerequisites','The short version of the failure is <a href="/articles/why-this-escrow-take-failed/">why this escrow take failed</a>.'),
  ('Record','Upstream <a href="https://github.com/berkaycirak/gifter-escrow">berkaycirak/gifter-escrow</a>. Pull request <a href="https://github.com/berkaycirak/gifter-escrow/pull/1">#1</a>. Fork commit <code>{E(gif["commit"][:7])}</code>.'),
  ('Author','Sol.College. The note is <code>dapps/patches/gifter-escrow/UPSTREAM_PR.md</code>.'),
])}
<h2 id=problem>The problem that was investigated</h2>
<p><code>take_and_close</code> on program <code>6Z5cvVUc…</code> never completed. Signature {tx('ck53TqoU8UfpBav2V3bE1oy4Wm2qvxeU6bgibkXqzCsbP4YbBxDGK98bJxoowGpKNwkkPotBtCxVfUQMEm2zZu7')} aborted with an access violation. Create and refund on that program did complete. A second, separate defect: the Create form’s token dropdown stayed empty because the query key stored <code>toBase58</code> without calling it.</p>
<p>This is a practice fork Sol.College deployed for lessons. The pull request is how that finding was offered to the original repository. It is not a claim that the original project’s maintainers confirmed the diagnosis.</p>
<h2 id=patch>What the note says was changed</h2>
<p>Branch <a href="https://github.com/Blockchains/gifter-escrow/tree/fix/take-and-close-pda-seeds"><code>fix/take-and-close-pda-seeds</code></a>, based on upstream <code>main</code>, without the Sol.College program id. The note names three commits on that branch: <code>db240db</code> removes <code>println!</code>, <code>a9967c0</code> binds the PDA seed bytes, and <code>5628bfc</code> uses the wallet string as the token-list query key and reads the DAS URL from <code>NEXT_PUBLIC_HELIUS_DAS_URL</code>.</p>
<p>The hosted app is commit <code>{E(gif['commit'])}</code> of <a href="{E(gif['fork'])}">the working fork</a>, program <code>{E(gif['program'])}</code>. On that program the script’s take completed ({tx('33yMgZzAaH3mMcHgSmQBRVb4FeRmu5gX6nkAMfJU2T8F8sAwqMDTVfgsVcg7MXPM28GoAo7RPC7E35NhkNSrLXZd')}) and the form’s dropdown listed 18 tokens before a create ({tx('2c6QNtYzCDr2McZcXG9dsyD6e951w8EvA5QBAgwxCYG9uDjYD2a3B4xf9UV7QGk3rdJ7oDNNfex9bBHZTiMzujCk')}).</p>
<h2 id=test>The test the note describes</h2>
<p><code>contract/tests/take-and-close.ts</code> is described as a localnet test that creates two mints, opens an escrow, runs <code>take_and_close</code>, and checks both token balances and that the vault and the state account are closed. The lesson’s build note, on a different commit, says <code>anchor test</code> was not run. This page does not report a passing test run.</p>
<h2 id=status>Status of the contribution</h2>
<ul>
<li>Local change: the three commits named above, on the fork branch.</li>
<li>Tests: a regression test file is in the pull request. No passing run is recorded on the lesson’s build commit.</li>
<li>Pull request prepared and submitted: <a href="https://github.com/berkaycirak/gifter-escrow/pull/1">berkaycirak/gifter-escrow#1</a>, recorded as opened.</li>
<li>Pull request accepted: not recorded. An opened request is not a merged one. The original maintainers decide.</li>
</ul>
<h2 id=limits>Limitations</h2>
<p>{E(lim(gif))} A take that substitutes a different mint was not run. The hosted source still calls <code>create_program_address</code> from the take handler even though a comment warns about the heap. Do not use this page as an exploit procedure. The failing inputs and the patch are already in the public pull request.</p>
<h2 id=try>Try it yourself</h2>
<p>The lesson is where you inspect the accounts and the two signatures. <a href="/lessons/gifter-escrow/">Open the Gifter escrow lesson</a>.</p>
<h2 id=next>Continue</h2>
<ul class=continue-list>
<li><a href="/articles/why-this-escrow-take-failed/">Why the take failed</a></li>
<li><a href="/articles/what-we-could-build-for-this-escrow/">The recorded build</a></li>
<li><a href="/articles/testing/">Tests, failures, and contributions</a></li>
</ul>
{credit}</article>'''
  pages=[
    ('/articles/what-is-a-solana-pda/', pda_title, pda_desc, pda, 'Fundamentals'),
    ('/articles/why-this-escrow-take-failed/', fail_title, fail_desc, fail, 'Troubleshooting'),
    ('/articles/what-we-could-build-for-this-escrow/', build_title, build_desc, build, 'Practical guide'),
    ('/articles/from-failing-take-to-pull-request/', case_title, case_desc, case, 'Case study'),
  ]
  reads=library.load_reads()
  pages.extend((p, t, d, art(t)+b, a) for p, t, d, b, a in library.articles(E, tx, meta_block, credit, reads))
  def card(path, title, area, desc):
    return f'<a class=card href="{path}"><p class=eyebrow>{E(area)}</p><h3>{E(title)}</h3><p>{E(desc)}</p></a>'
  nav, plan_html, _numbered=library.catalogue_tail(E)
  linked=sum(1 for _c,_n,_b,items in library.PLAN for _n,_t,slug,_r in items if slug)
  index=home+f'''<article class=lesson>
<p class=eyebrow>Solana development, from working examples</p>
<h1>Articles</h1>
<p class=lead>Understand the system. Reproduce the behaviour. Build something that survives failure. An article answers one question from a recorded run. A lesson is where you practise. These are not two copies of one page.</p>
<p>There are {len(pages)} articles. {linked} of the 120 planned titles link to a page. Titles 3 and 5 share one page. A title with no link has no URL. Reading a published page does not require a wallet. A study with a research question and a method belongs in the <a href="/journal/">Journal of Solana Studies</a>, not in this list.</p>
<ol class=workflow>
<li>Understand</li><li>Design</li><li>Build</li><li>Test</li><li>Secure</li><li>Deploy</li><li>Observe</li><li>Recover</li><li>Improve</li>
</ol>
<p>The published pages start at Understand. One recorded build and one case study are included. There is no article yet for a passing test suite, a security fixture, or production operations.</p>
<p><a href="/articles/paths/understand-reproduce-build/">Read the published pages in order</a> · <a href="/articles/evidence/">The evidence ledger</a></p>
<h2 id=hubs>Start with a topic</h2>
<div class=hub-grid>
<a class=card href="/articles/accounts/"><h3>Accounts, ownership, signers, and PDAs</h3><p>Where state lives, and how a program picks an address.</p></a>
<a class=card href="/articles/tokens/"><h3>Token accounts, transfers, and escrow</h3><p>A mint, a token account, and a vault a PDA controls.</p></a>
<a class=card href="/articles/transactions/"><h3>Signing, confirmation, and a failed transaction</h3><p>What a signature proves, and what an abort looks like.</p></a>
<a class=card href="/articles/testing/"><h3>Tests, failures, and contributions</h3><p>A recorded build, a regression test, and an opened pull request.</p></a>
</div>
<h2 id=library>Published</h2>
<div class=hub-grid>{''.join(card(p,t,a,d) for p,t,d,_,a in pages)}</div>
<h2 id=plan>The 120-title plan</h2>
<p class=cat-nav>{nav}</p>
{plan_html}
<p class=note>The <a href="/lessons/">lessons</a> are the practice. The <a href="/lessons/glossary/">glossary</a> is the short definition. The <a href="/explore/">source library</a> is generated from code that has not been deployed, so it is not part of this set.</p>
</article>'''
  def lesson_link(slug, note):
    x=live[slug]
    return f'<li><a href="/lessons/{E(slug)}/"><b>{E(x["name"])}</b></a> — {E(note)} <span class=meta>Verified {E(x["verified"])}.</span></li>'
  hubs=[]
  accounts=hub.format('Accounts')+f'''<article class=lesson>
<p class=eyebrow>Topic</p>
<h1>Accounts, ownership, signers, and PDAs</h1>
<p class=lead>A Solana program keeps state in accounts. The owner is the program allowed to change an account. A signer is a key that approved the transaction. A PDA is an address the program derives, so the account can be found again from the seeds.</p>
{meta_block([('Prerequisites','None to read. The first practice lesson asks for a devnet wallet.'),
  ('Reading order','The explanation, then one pixel account, then a poll, a SOL lock, and a token vault.')])}
<h2 id=order>Read, then practise</h2>
<ol>
<li><a href="/articles/a-solana-address-is-not-a-wallet/">A Solana address is not always a wallet</a> Which of these addresses signs, which is a program, and which holds state.</li>
<li><a href="/articles/where-picassol-stores-state/">Where Picassol stores state</a> The pixel account, and the counter that is not one.</li>
<li><a href="/articles/what-is-a-solana-pda/">What is a Solana PDA?</a> The pixel account, with the recorded create.</li>
{lesson_link('picassol-hackathon', learn(pic))}
{lesson_link('poe-solana', learn(poe))}
{lesson_link('trustlock', learn(trust)+' '+lim(trust))}
{lesson_link('gifter-escrow', learn(gif))}
</ol>
<p>Beginner material is Picassol and the PDA article. TrustLock and Gifter add a deadline and a token vault. Debug challenges are listed on the <a href="/lessons/#debug-challenges">lessons index</a> and are not repeated here as finished environments.</p>
<p><a href="/lessons/glossary/#pda">PDA</a> · <a href="/lessons/glossary/#seeds">seeds</a> · <a href="/lessons/glossary/#signer">signer</a> · <a href="/articles/">All articles</a></p>
</article>'''
  tokens=hub.format('Tokens')+f'''<article class=lesson>
<p class=eyebrow>Topic</p>
<h1>Token accounts, transfers, and escrow</h1>
<p class=lead>A mint defines a token. A token account holds a balance of that mint. An escrow in Gifter puts the deposited tokens in a token account whose authority is a PDA, and moves them with <code>transfer_checked</code>.</p>
{meta_block([('Prerequisites','The <a href="/articles/accounts/">accounts</a> page, or the PDA article.'),
  ('Reading order','The failure and the later successful take, then the lesson, then a mint that creates one token.')])}
<h2 id=order>Read, then practise</h2>
<ol>
<li><a href="/articles/follow-one-token-balance/">Follow one token balance</a> Mint, token account, and authority on the completed take.</li>
<li><a href="/articles/why-this-escrow-take-failed/">Why this escrow take failed</a></li>
<li><a href="/articles/from-failing-take-to-pull-request/">From the failing take to the opened pull request</a></li>
{lesson_link('gifter-escrow', 'Create, the completed take, and refund. The earlier abort is kept beside them.')}
{lesson_link('gree', learn(gree))}
</ol>
<p>Gifter is the worked escrow. gree is a different shape: one instruction mints a token and attaches metadata. Both are guided lessons whose core flow is recorded as working, with the limits on each lesson page.</p>
<p><a href="/lessons/glossary/#ata">Associated token account</a> · <a href="/lessons/glossary/#mint">mint</a> · <a href="/articles/">All articles</a></p>
</article>'''
  txhub=hub.format('Transactions')+f'''<article class=lesson>
<p class=eyebrow>Topic</p>
<h1>Signing, confirmation, and a failed transaction</h1>
<p class=lead>A transaction is the signed list of instructions that was submitted. A successful signature shows that those instructions were processed. It does not, by itself, show that you can explain the accounts. A failed signature is still evidence: it shows the program id, the instruction, and the error.</p>
{meta_block([('Prerequisites','None.'),
  ('Reading order','One click that landed, then one instruction that aborted, then the lesson that holds both Gifter signatures.')])}
<h2 id=order>Read, then practise</h2>
<ol>
<li><a href="/articles/read-a-solana-transaction/">Read the pixel create field by field</a></li>
<li><a href="/articles/what-a-failed-transaction-changed/">What the aborted take changed, and what the completed take changed</a></li>
<li><a href="/articles/why-this-escrow-take-failed/">Why the take aborted</a></li>
{lesson_link('picassol-hackathon', 'The click is the practice. The article is the account.')}
{lesson_link('gifter-escrow', 'Proof lists the completed take and the refunds. The article keeps the earlier abort next to them.')}
</ol>
<p>When a simulation fails before anything is sent, there is no signature to open. The Gifter article separates that case from a transaction that landed and failed. Wallet approval, an empty practice balance, and a program abort are different stops.</p>
<p><a href="/articles/">All articles</a> · <a href="/lessons/guide/">How to use a lesson</a></p>
</article>'''
  testing=hub.format('Testing')+f'''<article class=lesson>
<p class=eyebrow>Topic</p>
<h1>Tests, failures, and contributions</h1>
<p class=lead>A completed devnet transaction shows that an operation occurred. A test is a checked expectation: balances, closed accounts, or a specific error. A pull request is a proposal to the original repository. Those are three different results, and this set keeps them separate.</p>
{meta_block([('Prerequisites','The Gifter failure, or a willingness to read the build note as a log rather than as a tutorial.'),
  ('Reading order','The recorded build, the case study, then the lesson exercises and the general testing guide.')])}
<h2 id=order>Read, then practise</h2>
<ol>
<li><a href="/articles/what-we-could-build-for-this-escrow/">What the recorded build produced</a> — a <code>.so</code>, then an IDL failure. <code>anchor test</code> was not run.</li>
<li><a href="/articles/from-failing-take-to-pull-request/">The opened pull request</a> — commits, a described regression test, no recorded merge.</li>
{lesson_link('gifter-escrow', 'The exercises ask you to tell the two takes apart, and they say which check was not run.')}
<li><a href="/how-to-build/testing/">Testing Solana programs</a> — the general guide, with links to the current tools.</li>
</ol>
<p>Finishing the lesson’s steps is not the same as the pull request being accepted. The case study lists local change, the test file, the submitted request, and the missing merge as separate lines.</p>
<p><a href="/articles/">All articles</a> · <a href="/how-to-build/security-checklist/">Security checklist</a></p>
</article>'''
  hubs=[
    ('/articles/accounts/','Accounts, ownership, signers, and PDAs','Where a Solana program keeps state, and how Picassol, TrustLock, and Gifter pick addresses.', accounts),
    ('/articles/tokens/','Token accounts, transfers, and escrow','A mint, a token account, and the Gifter vault, with the recorded take and the earlier abort.', tokens),
    ('/articles/transactions/','Signing, confirmation, and a failed transaction','What a devnet signature shows, using a landed pixel create and an aborted escrow take.', txhub),
    ('/articles/testing/','Tests, failures, and contributions','A recorded Anchor build, a regression test in an opened pull request, and no recorded merge.', testing),
  ]
  paths=['/articles/']
  desc='Recorded Solana articles, plus the 120-title plan. A title has a page only when a recorded run or a chain read can carry it.'
  write_page(S, page, CSS, '/articles/', 'Articles', desc, index, ld('Articles', desc, '/articles/', 'WebPage'))
  for path, title, description, body in ((p,t,d,b) for p,t,d,b,_ in pages):
    write_page(S, page, CSS, path, title, description, body, ld(title, description, path))
    paths.append(path)
  for path, title, description, body in hubs:
    write_page(S, page, CSS, path, title, description, body, ld(title, description, path, 'WebPage'))
    paths.append(path)
  ev_title, ev_desc, ev_html=library.evidence_page(E, tx, meta_block, credit, reads)
  write_page(S, page, CSS, '/articles/evidence/', ev_title, ev_desc, art(ev_title)+ev_html, ld(ev_title, ev_desc, '/articles/evidence/', 'WebPage'))
  paths.append('/articles/evidence/')
  path_title, path_desc, path_html=library.path_page(E, meta_block, credit)
  write_page(S, page, CSS, '/articles/paths/understand-reproduce-build/', path_title, path_desc, art(path_title)+path_html, ld(path_title, path_desc, '/articles/paths/understand-reproduce-build/', 'WebPage'))
  paths.append('/articles/paths/understand-reproduce-build/')
  attach(S)
  llms=f'{S}/llms.txt'
  if os.path.exists(llms):
    block='\n## Articles\n'+''.join(f'- [{t}]({SITE}{p}): {d}\n' for p,t,d,_,_ in pages)
    block+=f'- [Evidence for the articles]({SITE}/articles/evidence/): The reads and records behind the claims.\n'
    block+=f'- [Understand, reproduce, then build]({SITE}/articles/paths/understand-reproduce-build/): The published articles in order.\n'
    block+='\n## Article topics\n'+''.join(f'- [{t}]({SITE}{p}): {d}\n' for p,t,d,_ in hubs)
    text=open(llms).read()
    text=re.sub(r'\n## Articles\n.*?(?=\n## |\Z)','',text,flags=re.S)
    text=re.sub(r'\n## Article topics\n.*?(?=\n## |\Z)','',text,flags=re.S)
    open(llms,'w').write(text.rstrip()+'\n'+block)
  print('articles:', len(paths), 'pages')
  return paths
