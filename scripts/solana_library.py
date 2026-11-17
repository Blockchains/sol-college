"""The Solana Library: one catalogue of records that point at pages we can substantiate.

A record is not a second copy of an article or a lesson. External records are links
plus the note from the page that was read. A URL that was not retrieved is omitted.
"""
import html, json, os, re, urllib.parse
REVIEW = '2026-11-17'
SITE = 'https://sol.college'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ISSUE = 'https://github.com/Blockchains/sol-college/issues/new'
SOL_DISC = ('Named in the collection plan. The page was read on 17 Nov 2026. A direct client on the build machine received HTTP 429 from solana.com that day, so this check is the retrieved page, not that client.')
OK_DISC = 'Named in the collection plan. The build machine received HTTP 200 on 17 Nov 2026, and the page was read.'
SUBJECTS = [
 ('orientation', 'Orientation', 'What Solana is, the words, and where to start.'),
 ('prerequisites', 'Programming prerequisites', 'Toolchains and framework docs a program build depends on.'),
 ('accounts', 'Accounts and state', 'Ownership, addresses, and where state is stored.'),
 ('programs', 'Programs and instructions', 'Program structure and instruction design.'),
 ('pdas', 'PDAs and CPIs', 'Derived addresses and cross-program calls.'),
 ('transactions', 'Transactions', 'Signatures, messages, fees, confirmation, and expiry.'),
 ('tokens', 'Tokens', 'Mints, token accounts, transfers, and authorities.'),
 ('token-extensions', 'Token Extensions', 'Optional behaviour on mints and token accounts.'),
 ('wallets', 'Wallets and identity', 'Connection, signing, and custody.'),
 ('frontend', 'Frontend development', 'Transaction UX in an application.'),
 ('backend', 'Backend development', 'Verification, queues, and reconciliation.'),
 ('testing', 'Testing and debugging', 'Builds, failures, and regression tests.'),
 ('security', 'Security', 'Questions to ask before treating an example as safe.'),
 ('rpc', 'RPC and indexing', 'Endpoints, providers, and reading chain data.'),
 ('deployment', 'Deployment and operations', 'Install, deploy, and what this site has not re-run.'),
 ('payments', 'Payments and commerce', 'Invoices, settlement, and reconciliation.'),
 ('defi', 'DeFi engineering', 'Exchange, lending, and oracle integration.'),
 ('nfts', 'NFTs and digital assets', 'Metadata and asset lifecycle.'),
 ('games', 'Games and consumer apps', 'Application state for games.'),
 ('depin', 'DePIN and hardware', 'Device identity and telemetry.'),
 ('ai', 'AI and agents', 'Tool use, approvals, and auditability.'),
 ('validators', 'Validators and networking', 'Operating or inspecting validators.'),
 ('research', 'Protocol research', 'Proposals and implementation discussions.'),
 ('history', 'History and case studies', 'Earlier behaviour, kept separate from current guidance.'),
]
SUBJECT_NAME = dict((i, n) for i, n, _c in SUBJECTS)
NEEDS = [('explain', 'Understand a concept'), ('build', 'Build something'), ('fix', 'Fix a problem'), ('evidence', 'Find documentation'), ('practise', 'Let me practise')]
NEED_NAME = dict(NEEDS)
COLLECTIONS = [
 ('foundations', 'Foundations', ['orientation', 'accounts', 'prerequisites']),
 ('programs', 'Programs', ['programs', 'pdas']),
 ('tokens', 'Tokens', ['tokens', 'token-extensions']),
 ('transactions', 'Transactions', ['transactions']),
 ('security', 'Security', ['security']),
 ('wallets', 'Wallets', ['wallets', 'frontend']),
 ('payments', 'Payments', ['payments']),
 ('infrastructure', 'Infrastructure', ['rpc', 'validators']),
 ('research', 'Research', ['research']),
 ('applications', 'Applications', ['frontend', 'defi', 'nfts', 'games', 'depin', 'ai']),
 ('operations', 'Operations', ['deployment', 'backend', 'testing']),
 ('history', 'History', ['history']),
]
LABEL_NAME = {
 'source-checked': 'Source checked',
 'technically-reproduced': 'Technically reproduced',
}
STOP = set('a an the to of on in for and or versus vs my your why did how what does can is it with from this that me do you about into than understand explain show find help let something anything'.split())
def E(s):
  return html.escape(str(s if s is not None else ''), quote=True)
def plain(s):
  s = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', str(s or ''))
  return ' '.join(s.replace('`', '').split())
def issue(title, body):
  return ISSUE + '?title=' + urllib.parse.quote(title) + '&body=' + urllib.parse.quote(body)
def show(v):
  return 'Not established' if v in (None, '') else str(v)
def has_word(text, words):
  return any(re.search(r'\b' + re.escape(w) + r'\b', text) for w in words)
def base(**kw):
  row = dict(difficulty='Not established', prereqs='Not established', language='English', time=None,
    publisher='Sol.College', origin='original', standing='Sol.College original', published=None, updated=None,
    reviewed=REVIEW, environment=None, licence='Sol.College page.', learn='', why='', limits='', labels=[],
    keywords='', relationships=[], replacement=None, historical=False, discovery='Sol.College site.',
    verification='Catalogued on 17 Nov 2026. Not a new execution for this page.')
  row.update(kw)
  return row
def external(id, title, purpose, kind, subjects, needs, href, why, limits, learn, keywords, publisher, standing, discovery):
  return base(id=id, title=title, purpose=purpose, type=kind, subjects=subjects, needs=needs, href=href,
    publisher=publisher, standing=standing, origin='external',
    licence='Link only. The destination licence was not copied into this catalogue.',
    language='English, as read on 17 Nov 2026', learn=learn, why=why, limits=limits, keywords=keywords,
    labels=['source-checked'], discovery=discovery,
    environment='Not established. Examples on the destination were not run.',
    verification='Destination read on 17 Nov 2026. Examples were not run.')
def hand_records():
  s = SOL_DISC
  rows = [
    external('ext-docs', 'Solana documentation', 'Primary entry to the official docs, including a browser quickstart and the concept path.',
      'Official reference', ['orientation'], ['explain', 'build'], 'https://solana.com/docs',
      'It is the front door the collection plan names. The page offers a browser quickstart, an agent-setup path, and a link into the concepts.',
      'The quickstart was not opened or run. This record is the index, not a review of every child page.',
      'Where the official docs send a new reader.', 'quickstart concepts documentation start', 'Solana', 'Official Solana documentation', s),
    external('ext-core', 'Solana core concepts', 'The official concept index: accounts, programs, instructions, transactions, fees, PDAs, and CPIs.',
      'Official reference', ['accounts', 'programs', 'pdas', 'transactions'], ['explain', 'evidence'], 'https://solana.com/docs/core',
      'The page names those seven topics as the foundation and states a base fee of 5,000 lamports per signature. It also mentions SIMD-0268 in a note about CPI depth.',
      'Sol.College did not remeasure the fee schedule. A SIMD number on this page is not evidence the change is active. Child pages were not each reviewed.',
      'The official map of the core terms.', 'fee lamports PDA CPI instruction account program', 'Solana', 'Official Solana documentation', s),
    external('ext-tools', 'Solana developer resources', 'The official directory of RPC references, SDKs, CLI notes, recipes, courses, and tools.',
      'Tools directory', ['rpc', 'prerequisites'], ['build', 'evidence'], 'https://solana.com/docs/tools',
      'One page lists the kinds of tool the collection plan asked for. The AI-tools heading is on this directory.',
      'Child tools, courses, and the AI pages were not opened. A directory entry is not a recommendation of each product.',
      'Where the official docs list tools.', 'RPC SDK CLI cookbook course AI tools', 'Solana', 'Official Solana documentation', s),
    external('ext-cookbook', 'Solana Cookbook', 'Official recipe index for common development tasks.',
      'Recipe collection', ['programs', 'transactions', 'tokens'], ['build'], 'https://solana.com/developers/cookbook',
      'The index describes focused examples for validators, wallets, transactions, accounts, and token instructions.',
      'Individual recipes were not opened and were not run. Do not treat this record as a review of a recipe.',
      'That an official recipe index exists, and what sections the index names.', 'recipe cookbook keypair send token', 'Solana', 'Official Solana documentation', s),
    external('ext-tokens', 'Solana token documentation', 'Official explanation of token programs, mint accounts, token accounts, and associated token accounts.',
      'Official reference', ['tokens', 'accounts', 'wallets'], ['explain', 'evidence'], 'https://solana.com/docs/tokens',
      'The page distinguishes a mint, a token account, and the wallet that is the token account authority. It also distinguishes that authority from the program that owns the account.',
      'The examples were not run. This matches the distinction in the Sol.College token article, which is a separate, measured record.',
      'The official mint, token-account, and wallet-authority model.', 'token account wallet mint authority ATA owner', 'Solana', 'Official Solana documentation', s),
    external('ext-extensions', 'Token Extensions documentation', 'Official page on optional extensions added to mints and token accounts.',
      'Official reference', ['token-extensions', 'tokens'], ['explain', 'evidence'], 'https://solana.com/docs/tokens/extensions',
      'The page says extensions are optional, that most cannot be added after initialisation, and that some cannot be combined.',
      'Sol.College has not executed an extension transfer. Compatibility for a given mint is not established here.',
      'The official scope of Token Extensions.', 'Token-2022 extension NonTransferable transfer fee', 'Solana', 'Official Solana documentation', s),
    external('ext-transactions', 'Transaction documentation', 'Official page on signatures, messages, instructions, and atomic execution.',
      'Official reference', ['transactions'], ['explain', 'evidence'], 'https://solana.com/docs/core/transactions',
      'The page says a transaction’s instructions succeed or fail together, and that a recent blockhash is valid for 150 slots. It states a base fee of 5,000 lamports per signature. A limits table cites SIMD-0596 for one v1 figure.',
      'The 150-slot lifetime and the fee line are the page’s statements. They were not remeasured for this record. SIMD-0596 activation is not established. Sol.College measured a 5,000 lamport fee only on the transactions named in the articles.',
      'The official transaction model, including what the page says about expiry.', 'transaction expire expired blockhash signature atomic fee', 'Solana', 'Official Solana documentation', s),
    external('ext-landing', 'Transaction landing guidance', 'Official notes on getting a transaction included: blockhash expiry, retries, and fees.',
      'Official reference', ['transactions', 'rpc'], ['fix', 'build'], 'https://solana.com/docs/tools/transaction-landing',
      'The page discusses a fresh blockhash, lastValidBlockHeight, retries, priority fees, and public RPC limits. It is the page to open for “why did my transaction expire?”',
      'The sample clients were not run. Dollar figures and timings on that page were not checked. This is not a payments integration guide.',
      'How the official docs talk about expiry and retries.', 'transaction expire expired blockhash retry lastValidBlockHeight priority fee', 'Solana', 'Official Solana documentation', s),
    external('ext-network', 'Solana network hub', 'Where the official site points for validator operation, RPC options, explorers, status, and reports.',
      'Official reference', ['validators', 'rpc', 'orientation'], ['explain', 'evidence'], 'https://solana.com/network',
      'Selected for validator operation. The page routes to validator docs, RPC providers, explorers, status, and reports.',
      'Sol.College has not operated a validator. Child pages were not opened. A link on this hub is not a reviewed provider.',
      'The official map of network operations.', 'validator operation RPC explorer status', 'Solana', 'Official Solana documentation', s),
    external('ext-learn', 'Solana learning hub', 'Official beginner orientation, including non-developer introductions, plus links to the docs and the cookbook.',
      'Official orientation', ['orientation', 'wallets'], ['explain'], 'https://solana.com/learn',
      'The page is a set of short introductions (wallet, fees, tokens, and others) and points at the docs, cookbook, and courses.',
      'Those introductions were not opened one by one. This is not the developer concept index.',
      'That a beginner orientation exists beside the docs.', 'learn wallet beginner course', 'Solana', 'Official Solana documentation', s),
    external('ext-install', 'Solana local installation', 'The official install page. It describes an installer and says version numbers change.',
      'Official reference', ['prerequisites', 'deployment'], ['build'], 'https://solana.com/docs/intro/installation',
      'The how-to-build setup guide points here instead of copying a command.',
      'The installer was not run for this catalogue. Do not treat the guide’s commands as a clean-machine result.',
      'Where the current install instructions live.', 'install Rust Anchor CLI version', 'Solana', 'Official Solana documentation', s),
    external('ext-simd', 'Solana Improvement Documents', 'The repository of proposed and accepted changes to the Solana protocol.',
      'Research archive', ['research'], ['evidence', 'explain'], 'https://github.com/solana-foundation/solana-improvement-documents',
      'The repository description says SIMDs describe proposed and accepted changes. That is the research collection’s primary source.',
      'SIMD-0326 has its own page because that file cites the Alpenglow white paper. The other proposals are not each catalogued. Discussion status, acceptance, implementation, and activation are not established for the repository as a whole. A proposal is not proof a feature is active.',
      'Where protocol proposals are tracked, and what this record does not establish.', 'SIMD proposal accepted research', 'solana-foundation', 'Solana Foundation repository', OK_DISC),
    external('ext-anchor', 'Anchor documentation', 'The Anchor docs home. The page title read on 17 Nov 2026 was Introduction.',
      'Framework reference', ['programs', 'prerequisites'], ['build'], 'https://www.anchor-lang.com/docs',
      'The Sol.College Anchor guide links here. The check confirmed the docs home, not a version matrix.',
      'The docs were not inventoried. The Anchor workflow guide was not re-run. Version compatibility is not established.',
      'Where the Anchor project’s own docs start.', 'Anchor framework Rust program', 'Anchor', 'Anchor project documentation', OK_DISC),
  ]
  art = 'Written from the deployment record and, where cited, the 17 Nov 2026 devnet read.'
  rows += [
    base(id='art-index', title='Articles', purpose='The list of published Sol.College articles and the 120 titles that have no page.',
      type='Catalogue', subjects=['orientation'], needs=['explain'], href='/articles/',
      learn='Which questions have a page, and which titles are only a plan.',
      why='Articles are one collection inside the library. A title with no link has no URL.',
      limits='113 of the 120 titles have no page. Titles 3 and 5 share one page.',
      keywords='articles catalogue plan', published=REVIEW, discovery='scripts/articles.py'),
    base(id='art-pda', title='What is a Solana PDA? One pixel, one account',
      purpose='A PDA explained from one Picassol pixel account: seeds, size, and the recorded diagram.',
      type='Explanation', subjects=['pdas', 'accounts', 'programs'], needs=['explain'], href='/articles/what-is-a-solana-pda/',
      learn='How one pixel address is derived, and what the account stores.',
      why='The pixel account was part of the 17 Nov 2026 read. This is not a general PDA textbook.',
      limits='It does not describe a profile registry. Colour checks that compare a byte with 0 and 255 cannot fail.',
      labels=['technically-reproduced'], keywords='PDA seeds bump pixel create_pixel GsFGX3pzdgzugAfjcxH9Lbbz2aPZgXyvBoXkNnmxXwuY',
      published=REVIEW, discovery=art, verification='The pixel account from the recorded create was read on 17 Nov 2026.',
      relationships=[('Related lesson', 'lesson-picassol-hackathon'), ('Prerequisite of', 'lesson-gifter-escrow')]),
    base(id='art-address', title='A Solana address is not a wallet',
      purpose='Which addresses in the recorded sample are wallets, programs, token accounts, or closed accounts.',
      type='Explanation', subjects=['accounts', 'wallets', 'tokens'], needs=['explain'], href='/articles/a-solana-address-is-not-a-wallet/',
      learn='Program owner, token-account authority, and a wallet are different fields.',
      why='The classification uses the 17 Nov 2026 account read, including accounts that were absent.',
      limits='A 36-byte program account is not the compiled .so. Maker and taker wallet accounts were absent; the record does not say where that SOL went.',
      labels=['technically-reproduced'], keywords='address wallet owner authority token account program',
      published=REVIEW, discovery=art, verification='Account owners and lengths were read on 17 Nov 2026.',
      relationships=[('Prerequisite of', 'lesson-picassol-hackathon'), ('Prerequisite of', 'lesson-gifter-escrow')]),
    base(id='art-state', title='Where Picassol stores state',
      purpose='The pixel account holds the colour. The points counter is a different system and stayed at 0.',
      type='Explanation', subjects=['accounts', 'programs'], needs=['explain'], href='/articles/where-picassol-stores-state/',
      learn='Which state is on the pixel account and which state the static host does not update.',
      why='The account read and the deployment limit are both recorded.',
      limits='The points API returning 501 is the 10 Nov record, not a 17 Nov request.',
      labels=['technically-reproduced'], keywords='state pixel points leaderboard account',
      published=REVIEW, discovery=art, verification='The pixel account was still present on 17 Nov 2026.',
      relationships=[('Related lesson', 'lesson-picassol-hackathon')]),
    base(id='art-read-tx', title='Read a Solana transaction',
      purpose='One pixel-create transaction, field by field, from the 17 Nov 2026 read.',
      type='Explanation', subjects=['transactions'], needs=['explain', 'evidence'], href='/articles/read-a-solana-transaction/',
      learn='What fee, accounts, and compute the recorded pixel create showed.',
      why='It is a single transaction, not a fee schedule and not an expiry guide.',
      limits='The 5,000 lamport fee is this transaction. Compute was 9740 in both the log and the meta.',
      labels=['technically-reproduced'], keywords='transaction signature fee compute create_pixel 2yj2GAqcniqCBFkL2yekqVRtJk4fjKopQNvVRgY1bGCGJjZioTd9gFwMGU7fgy8CedBt6QEwy4oaxXVqy6EUhtGb',
      published=REVIEW, discovery=art, verification='getTransaction of the pixel create, confirmed, 17 Nov 2026.',
      relationships=[('Related lesson', 'lesson-picassol-hackathon')]),
    base(id='art-failed-change', title='What a failed transaction changed',
      purpose='What the aborted escrow take changed, and what the later completed take changed.',
      type='Explanation', subjects=['transactions', 'tokens'], needs=['explain', 'fix', 'evidence'], href='/articles/what-a-failed-transaction-changed/',
      learn='An abort can still charge a fee and move no tokens. A later success is a different transaction.',
      why='Both transactions were read on 17 Nov 2026. They do not share mints.',
      limits='The abort log says 18066 compute units and the meta says 200000. Those figures are not collapsed.',
      labels=['technically-reproduced'], keywords='failed abort take fee token ProgramFailedToComplete ck53TqoU8UfpBav2V3bE1oy4Wm2qvxeU6bgibkXqzCsbP4YbBxDGK98bJxoowGpKNwkkPotBtCxVfUQMEm2zZu7',
      published=REVIEW, discovery=art, verification='getTransaction of the abort and the completed take, 17 Nov 2026.',
      relationships=[('Related lesson', 'lesson-gifter-escrow')]),
    base(id='art-balance', title='Follow one token balance',
      purpose='Mint, token account, and authority on the completed Gifter take, re-read on 17 Nov 2026.',
      type='Explanation', subjects=['tokens', 'accounts', 'wallets'], needs=['explain', 'evidence'], href='/articles/follow-one-token-balance/',
      learn='A wallet can be the authority of a token account that holds the balance.',
      why='The balances were still 10, 5, 995, and 990 on 17 Nov 2026.',
      limits='Token Extensions were not part of this transfer. The maker and taker wallet accounts were absent.',
      labels=['technically-reproduced'], keywords='token account wallet mint balance authority ATA escrow',
      published=REVIEW, discovery=art, verification='getMultipleAccounts of the four token accounts, 17 Nov 2026.',
      relationships=[('Prerequisite of', 'lesson-gifter-escrow')]),
    base(id='art-take-failed', title='Why this escrow take failed',
      purpose='An earlier Gifter take aborted inside the program. The refund was a different instruction. The hosted program later completed a take.',
      type='Troubleshooting', subjects=['tokens', 'programs', 'testing'], needs=['fix', 'explain'], href='/articles/why-this-escrow-take-failed/',
      learn='How to tell the aborted take, the refund, and the later success apart.',
      why='The abort signature was read again on 17 Nov 2026. The headline is the take, not a failed refund.',
      limits='The hosted source still calls create_program_address. A substituted-mint take was not run. This is not an exploit procedure.',
      labels=['technically-reproduced'], keywords='escrow take refund abort 6Z5cvVUcJVFvkhmtJ4dYwgVqNn7jqN6TSisoYSihBA1r 45C1bSkFCbjrqiQHqm8oS6J88jirW8rC46Qiu6TvoY6x ProgramFailedToComplete TakeAndClose',
      published=REVIEW, discovery=art, verification='The abort transaction was re-read on 17 Nov 2026. The earlier program account was still present.',
      relationships=[('Related lesson', 'lesson-gifter-escrow')]),
    base(id='art-build', title='What the recorded build of this escrow produced',
      purpose='What one local Anchor build of the Gifter escrow produced on 13 Nov 2026, including the IDL failure.',
      type='Build record', subjects=['testing', 'programs', 'deployment'], needs=['build', 'evidence'], href='/articles/what-we-could-build-for-this-escrow/',
      learn='Which commit was built, the .so size, and the step that failed.',
      why='It is the build log for this escrow. It is not a tutorial that was re-run, and it is not the hosted commit.',
      limits='anchor test was not run. The IDL step failed. The .so is not the hosted binary. The setup guide was not a clean-machine install.',
      keywords='build escrow anchor IDL so compile', published=REVIEW, discovery=art,
      verification='The lesson build note. Not re-run for this catalogue.'),
    base(id='art-case', title='From a failing escrow take to an opened pull request',
      purpose='The pull request opened for the failing take. The test file is named. No passing run is recorded. No merge is recorded.',
      type='Case study', subjects=['testing', 'programs', 'history'], needs=['evidence', 'build'], href='/articles/from-failing-take-to-pull-request/',
      learn='What the note claims was changed, and which outcomes are not recorded.',
      why='Title 120 of the article plan. The status words stay inside the evidence.',
      limits='Local commit names come from the note and were not re-checked on GitHub for this catalogue. The pull request is recorded as opened.',
      keywords='escrow pull request test case study', published=REVIEW, discovery=art,
      verification='dapps/patches/gifter-escrow/UPSTREAM_PR.md. No test run was added.',
      relationships=[('Related lesson', 'lesson-gifter-escrow')]),
    base(id='art-evidence', title='Evidence for the articles',
      purpose='The claim ledger: each measured claim, the read, the result, and the limit.',
      type='Evidence ledger', subjects=['transactions', 'testing'], needs=['evidence'], href='/articles/evidence/',
      learn='Which sentences depend on a version or a read.',
      why='The library’s original evidence lives here and in the articles, not in an unsourced summary.',
      limits='No separate reviewer is named. A row is not a security review.',
      keywords='evidence ledger fee rent compute', published=REVIEW, discovery=art),
    base(id='art-path', title='Understand, reproduce, then build',
      purpose='The published articles in order, and the stages that still have no article.',
      type='Reading path', subjects=['orientation'], needs=['explain', 'build'], href='/articles/paths/understand-reproduce-build/',
      learn='Which of the nine articles to read first, and which stages are empty.',
      why='A path through the original writing. It is not the whole library.',
      limits='There is no article yet for a passing test suite, a security fixture, or production operations.',
      keywords='reading path articles', published=REVIEW, discovery=art),
    base(id='art-hub-accounts', title='Accounts, ownership, signers, and PDAs',
      purpose='The article hub for addresses, state, and the pixel PDA.',
      type='Collection', subjects=['accounts', 'pdas'], needs=['explain'], href='/articles/accounts/',
      learn='Which account articles exist.', why='A hub, not an extra article.',
      limits='Not counted as an original article.', keywords='accounts hub', published=REVIEW),
    base(id='art-hub-tokens', title='Token accounts, transfers, and escrow',
      purpose='The article hub for the token balance, the failure, and the case study.',
      type='Collection', subjects=['tokens'], needs=['explain'], href='/articles/tokens/',
      learn='Which token articles exist.', why='A hub, not an extra article.',
      limits='Not counted as an original article.', keywords='tokens hub escrow', published=REVIEW),
    base(id='art-hub-transactions', title='Signing, confirmation, and a failed transaction',
      purpose='The article hub for the pixel create, the abort, and the failure write-up.',
      type='Collection', subjects=['transactions'], needs=['explain', 'fix'], href='/articles/transactions/',
      learn='Which transaction articles exist.', why='A hub, not an extra article.',
      limits='Not counted as an original article.', keywords='transactions hub', published=REVIEW),
    base(id='art-hub-testing', title='Tests, failures, and contributions',
      purpose='The article hub for the recorded build, the case study, and the testing guide.',
      type='Collection', subjects=['testing'], needs=['build', 'fix'], href='/articles/testing/',
      learn='Which testing records exist.', why='A hub, not an extra article.',
      limits='Not counted as an original article. No passing test run is recorded.', keywords='testing hub', published=REVIEW),
  ]
  return rows
GUIDE_NOTES = {
 'setup': ('Points at the current official installer. This guide was not re-run as a clean-machine install.',
   ['prerequisites', 'deployment'], ['build'],
   'Commands in the guide were not run for this catalogue. Version compatibility is not established. The public devnet airdrop is described as closed.'),
 'anchor-workflow': ('The Anchor steps the site documents, with links to the Anchor docs.',
   ['programs', 'prerequisites'], ['build'],
   'Not re-run. Version compatibility is not established.'),
 'testing': ('How the site talks about anchor test and failure-path tests.',
   ['testing'], ['build', 'fix'],
   'No passing suite was run for this catalogue. Naming a harness is not a review of that harness.'),
 'deploy': ('Devnet deploy notes, then a mainnet warning.',
   ['deployment'], ['build'],
   'Not re-run. It is not a production operations article.'),
 'security-checklist': ('A list of security questions. It is not a finding and not a local exploit.',
   ['security', 'testing'], ['fix', 'explain'],
   'The course and attack repository linked from the guide were not opened in this pass. Nothing here is marked technically reproduced.'),
 'build-a-dapp': ('An end-to-end outline that points at the official generator and the live lessons.',
   ['programs', 'frontend', 'deployment'], ['build'],
   'create-solana-dapp was not run for this catalogue. The outline is not a recorded build.'),
}
def guide_records():
  import content, hubs
  guides = list(content.GUIDES) + [hubs.BUILD_DAPP]
  rows = []
  for g in guides:
    if g['slug'] not in GUIDE_NOTES:
      raise SystemExit('library: guide has no catalogue note: ' + g['slug'])
    purpose, subjects, needs, limits = GUIDE_NOTES[g['slug']]
    rows.append(base(id='guide-' + g['slug'], title=g['title'], purpose=purpose, type='Guide',
      subjects=subjects, needs=needs, href='/how-to-build/' + g['slug'] + '/',
      learn=purpose, why='Original Sol.College guidance. It defers to the current official docs for commands.',
      limits=limits, keywords=g['slug'].replace('-', ' '),
      discovery='scripts/content.py and scripts/hubs.py',
      verification='Not re-run for this catalogue.'))
  return rows, [g['slug'] for g in guides]
def ownership(slug):
  path = os.path.join(ROOT, 'config', 'projects', slug + '.json')
  if not os.path.exists(path):
    return 'Sol.College lesson. No ownership file for this slug.'
  own = json.load(open(path)).get('ownership')
  if own == 'sol-college-demonstration':
    return 'Sol.College original. Independent practice fork.'
  if own == 'participating-project':
    return 'Sol.College original. Recorded as an official project participant.'
  return 'Sol.College original. Ownership value: ' + str(own or 'missing')
def lesson_subjects(text):
  t = text.lower()
  out = ['programs']
  if has_word(t, ['account', 'pda', 'owner']): out.append('accounts')
  if has_word(t, ['pda', 'seed', 'seeds']): out.append('pdas')
  if has_word(t, ['token', 'mint', 'escrow', 'nft']): out.append('tokens')
  if has_word(t, ['nft']): out.append('nfts')
  if has_word(t, ['transaction', 'signature', 'blockhash']): out.append('transactions')
  if has_word(t, ['wallet', 'phantom']): out.append('wallets')
  if has_word(t, ['test', 'debug', 'fail']): out.append('testing')
  if has_word(t, ['defi', 'swap', 'lend', 'amm', 'oracle']): out.append('defi')
  if has_word(t, ['game']): out.append('games')
  if has_word(t, ['payment', 'checkout', 'invoice']): out.append('payments')
  return list(dict.fromkeys(out))
def lesson_records(live, lesson_of, functional_of, readiness, limit_of, one_line):
  extra = {
    'picassol-hackathon': dict(
      labels=['technically-reproduced'],
      keywords='create_pixel update_pixel PixelChanged GsFGX3pzdgzugAfjcxH9Lbbz2aPZgXyvBoXkNnmxXwuY',
      why='The recorded create_pixel was read back on 17 Nov 2026. Recolour was run from the script. The points counter is a separate limit.',
      verification='getTransaction of the UI create_pixel, confirmed, 17 Nov 2026. The lesson’s other steps were not all re-run.'),
    'gifter-escrow': dict(
      labels=['technically-reproduced'],
      keywords='escrow build TakeAndClose refund ProgramFailedToComplete 45C1bSkFCbjrqiQHqm8oS6J88jirW8rC46Qiu6TvoY6x 6Z5cvVUcJVFvkhmtJ4dYwgVqNn7jqN6TSisoYSihBA1r',
      why='Practice for the hosted escrow. A separate article records one local build. The completed take was read back on 17 Nov 2026. An earlier program’s take aborted.',
      verification='getTransaction of the hosted take, confirmed, 17 Nov 2026. Accept was not clicked. The lesson was not re-run as a whole.'),
  }
  rows = []
  counts = {'guided': 0, 'challenge': 0, 'preview': 0}
  for x in live:
    L = lesson_of(x)
    ready = readiness(x)
    counts[ready] += 1
    slug = x['slug']
    ex = extra.get(slug, {})
    lim = plain(one_line(limit_of(x) if not isinstance(limit_of(x), list) else ' '.join(map(str, limit_of(x))), 500))
    if not lim:
      lim = 'None recorded on the lesson.'
    text = ' '.join([L.get('title') or '', L.get('summary') or '', x.get('learn') or '', slug])
    prereqs = L.get('prereqs') or []
    pre = ' '.join(plain(p) for p in prereqs[:3]) if prereqs else 'Not established'
    if ready == 'challenge':
      needs, why = ['fix', 'practise'], 'A core flow does not complete. The lesson is practice for finding that gap. It is not a successful reproduction.'
    elif ready == 'preview':
      needs, why = ['explain'], 'The teaching sequence is not written yet. The page is the deployment record.'
    else:
      needs, why = ['practise', 'explain'], 'The deployment record marks the core flow as working. This catalogue entry is not a new run.'
    why = ex.get('why', why)
    program = x.get('program') or ''
    obj = (L.get('objectives') or [None])[0]
    rows.append(base(
      id='lesson-' + slug, title=L.get('title') or x.get('name') or slug,
      purpose=plain(L.get('summary') or x.get('learn') or L.get('title') or slug),
      type={'guided': 'Guided lesson', 'challenge': 'Debug challenge', 'preview': 'Project preview'}[ready],
      subjects=lesson_subjects(text), needs=needs, href='/lessons/' + slug + '/',
      difficulty=L.get('difficulty') or 'Not established', prereqs=pre,
      time=('Lesson file says ' + L['time'] + '. That figure is the file’s own estimate.') if L.get('time') else None,
      standing=ownership(slug), learn=plain(obj or L.get('summary') or ''),
      why=why, limits=lim, labels=ex.get('labels', []),
      keywords=' '.join(filter(None, [program, slug, ex.get('keywords', ''), ' '.join(L.get('concepts') or [])])),
      discovery='dapps/live.json and the lesson file.',
      verification=ex.get('verification', 'Deployment record verified ' + str(x.get('verified') or 'on an unstated date') + '. Not re-run for this catalogue.'),
      environment='Solana devnet. Deployment record verified ' + str(x.get('verified') or 'not established') + ('. Program ' + program if program else '.'),
      published=None))
  return rows, counts
def site_records():
  return [
    base(id='gloss', title='Glossary', purpose='Short definitions used by the lessons.',
      type='Glossary', subjects=['orientation'], needs=['explain'], href='/lessons/glossary/',
      learn='The meaning of a term, with the lessons that use it.',
      why='Definitions stay here. They are not each catalogued as a separate work.',
      limits='A glossary entry is not counted as an original article.', keywords='glossary definition'),
    base(id='lessons-index', title='Lessons', purpose='The catalogue of guided lessons, debug challenges, and the project preview.',
      type='Catalogue', subjects=['orientation', 'programs'], needs=['practise', 'explain', 'fix'], href='/lessons/',
      learn='Which apps have a written walkthrough and which do not.',
      why='Practice lives here. The library links to it.',
      limits='A debug challenge is not a completed core flow. Counts come from the same records as the lesson pages.',
      keywords='guided lesson debug challenge preview'),
    base(id='lessons-path', title='Learning path', purpose='The guided lessons in path order. Debug challenges stay off this path.',
      type='Reading path', subjects=['orientation', 'programs'], needs=['practise'], href='/lessons/path/',
      learn='A practice order for the apps recorded as working.',
      why='The maintained route for someone who wants to practise.',
      limits='Only guided lessons are on the path. Progress ticks are stored in the browser and are not a measure of comprehension.',
      keywords='learning path practise'),
    base(id='lessons-guide', title='How to use a lesson', purpose='How to open a lesson, use a devnet wallet, and read a recorded signature.',
      type='Guide', subjects=['wallets', 'frontend', 'orientation'], needs=['practise'], href='/lessons/guide/',
      learn='What a tick, a signature, and a debug challenge mean on this site.',
      why='The wallet steps for the lessons. No account on Sol.College is required to read.',
      limits='A wallet is needed only when a step sends a transaction. This page does not custody keys.',
      keywords='wallet phantom devnet lesson'),
    base(id='explore-index', title='Source library', purpose='Code walkthroughs generated from forks that have not been deployed.',
      type='Generated index', subjects=['programs'], needs=['explain'], href='/explore/',
      learn='That these pages exist and that they are not lessons.',
      why='One record for the whole generated set.',
      limits='Not deployed and not run. Each walkthrough is not a curated library record. Do not count them in the holdings.',
      keywords='source library walkthrough undeployed'),
    base(id='campus', title='Campus', purpose='The public room list of practice projects.',
      type='Catalogue', subjects=['orientation'], needs=['explain'], href='/campus/',
      learn='Which projects have a public room.',
      why='A room list. It is not a prerequisite for the library or the lessons.',
      limits='The homepage states the environment count and the room count separately. Paused means that project’s CTO agent is not producing work.',
      keywords='campus room'),
    base(id='live-index', title='Live apps', purpose='The deployment records for the hosted devnet apps.',
      type='Evidence ledger', subjects=['deployment', 'programs'], needs=['evidence'], href='/live/',
      learn='What was recorded for each hosted app.',
      why='The evidence behind the lesson status.',
      limits='A functional mark is the deployment record. It is not a security review and not a fresh run for this catalogue.',
      keywords='live devnet deployment record'),
  ]
ROOMS = [
 ('first-week', 'First week with Solana', 'Where do I start?',
  'Start with the official orientation, the glossary, and one measured article, then a guided lesson. This is not the only entrance.',
  ['ext-learn', 'gloss', 'art-address', 'ext-core', 'lessons-path', 'lesson-picassol-hackathon']),
 ('backend', 'Backend developer’s room', 'How does existing knowledge translate?',
  'There is no catalogue record yet for queues, databases, or idempotent workers. The closest records are how a transaction is read, the evidence ledger, and the testing and deploy guides.',
  ['art-read-tx', 'art-evidence', 'guide-testing', 'guide-deploy', 'ext-transactions']),
 ('rust', 'Rust and program development', 'How do I write and test programs?',
  'The pixel PDA, the hosted escrow, the one recorded build, and the Anchor docs. The build was not re-run, and the Anchor docs were not inventoried.',
  ['art-pda', 'lesson-picassol-hackathon', 'lesson-gifter-escrow', 'art-build', 'guide-anchor-workflow', 'ext-anchor', 'ext-install']),
 ('frontend', 'Frontend and wallet UX', 'How do I make an understandable application?',
  'No separate wallet-UX article is catalogued. The lesson guide says when a wallet is required. Picassol is a recorded UI transaction.',
  ['lessons-guide', 'gloss', 'ext-learn', 'lesson-picassol-hackathon']),
 ('payments', 'Payments and commerce', 'How do I verify and reconcile money movement?',
  'The payments pages named in the collection plan were not retrieved, so they are not catalogued. The landing guide is about inclusion and expiry, not an invoice flow.',
  ['ext-landing', 'ext-transactions', 'art-read-tx', 'art-balance']),
 ('security', 'Security and review', 'What can go wrong, and what evidence can I gather?',
  'The checklist is questions. The escrow article is one recorded failure, not an exploit write-up. A reproduced example is not a security review.',
  ['guide-security-checklist', 'art-take-failed', 'art-case', 'art-hub-testing']),
 ('validator', 'Validator and infrastructure', 'How do I operate or investigate network infrastructure?',
  'The network hub is the official map. Sol.College has not operated a validator, and the child links were not opened.',
  ['ext-network', 'ext-tools']),
 ('research', 'Research and protocol', 'What is proposed, implemented, or still debated?',
  'The SIMD repository holds proposed and accepted documents. SIMD-0326 is catalogued on its own because it cites the Alpenglow paper. White papers that were retrieved have their own pages. A mention of a SIMD number is not activation evidence.',
  ['ext-simd', 'paper-solana-whitepaper', 'paper-alpenglow-v1-1', 'ext-core']),
 ('agents', 'AI and agents', 'How do I control permissions and verify outcomes?',
  'The developer-resources page has an AI-tools heading. Those child pages were not opened. Article titles 113 to 116 have no page.',
  ['ext-tools', 'art-index']),
 ('educator', 'Educator’s room', 'How do I teach and assess this material?',
  'Lesson ticks are stored in the browser. They record that a step was checked, not that a learner can explain the accounts.',
  ['lessons-guide', 'lessons-path', 'art-path', 'gloss', 'lessons-index']),
]
SELECTION = ['art-address', 'art-read-tx', 'art-balance', 'lesson-picassol-hackathon', 'lesson-gifter-escrow', 'ext-core', 'ext-tokens', 'art-evidence', 'lessons-path', 'ext-simd']
ORIGINAL_ARTICLES = ['art-pda', 'art-address', 'art-state', 'art-read-tx', 'art-failed-change', 'art-balance', 'art-take-failed', 'art-build', 'art-case']
def card(r, by_id):
  labels = ''.join(f'<li>{E(LABEL_NAME[l])}</li>' for l in r['labels'])
  rels = []
  for name, tid in r['relationships']:
    other = by_id.get(tid)
    if not other:
      raise SystemExit('library: missing relationship ' + tid)
    rels.append(f'<li>{E(name)}: <a href="{E(other["href"])}">{E(other["title"])}</a></li>')
  rel_html = '<ul>' + ''.join(rels) + '</ul>' if rels else '<p>None recorded.</p>'
  subs = ', '.join(E(SUBJECT_NAME[s]) for s in r['subjects'])
  exact = ' '.join([r['keywords'], r['title'], r.get('environment') or ''])
  search = ' '.join([r['title'], r['purpose'], r['why'], r['limits'], r['learn'], r['keywords'], subs, r['type'], r['standing']]).lower()
  report = issue('Library correction: ' + r['title'], 'Record: ' + r['id'] + '\n\nWhat is wrong:\n\nWhat the source says:\n\nDo not include private keys or recovery phrases.\n')
  kind = 'Open the record' if str(r['href']).startswith('/') else ('Open original' if r['origin'] == 'external' else 'Open')
  label_attr = ' '.join(r['labels'])
  return f'''<article class="card lib-item" id="r-{E(r['id'])}" data-needs="{E(' '.join(r['needs']))}" data-subjects="{E(' '.join(r['subjects']))}" data-origin="{E(r['origin'])}" data-labels="{E(label_attr)}" data-historical="{'1' if r['historical'] else '0'}" data-href="{E(r['href'])}" data-exact="{E(exact)}" data-search="{E(search)}">
<h3>{E(r['title'])}</h3>
<p>{E(r['purpose'])}</p>
<p class=meta>{E(r['type'])} · {subs} · {E(show(r['difficulty']))}</p>
<ul class=labels>{labels}</ul>
<p><b>Why this result. </b>{E(r['why'])}</p>
<p class=limit><b>Known limitations. </b>{E(r['limits'])}</p>
<p><a href="{E(r['href'])}">{kind}</a> · <button type=button class="btn ghost" data-save="{E(r['id'])}">Save</button> · <a href="{E(report)}">Report a problem</a></p>
<details><summary>Catalogue record</summary>
<dl class=article-meta>
<dt>What you will learn</dt><dd>{E(r['learn'] or r['purpose'])}</dd>
<dt>Prerequisites</dt><dd>{E(show(r['prereqs']))}</dd>
<dt>Language</dt><dd>{E(r['language'])}</dd>
<dt>Estimated time</dt><dd>{E(show(r['time']))}</dd>
<dt>Publisher</dt><dd>{E(r['publisher'])}</dd>
<dt>Standing</dt><dd>{E(r['standing'])}</dd>
<dt>Published</dt><dd>{E(show(r['published']))}</dd>
<dt>Last substantive update</dt><dd>{E(show(r['updated']))}</dd>
<dt>Last library review</dt><dd>{E(r['reviewed'])}</dd>
<dt>Environment</dt><dd>{E(show(r['environment']))}</dd>
<dt>Licence or access</dt><dd>{E(r['licence'])}</dd>
<dt>Stable id</dt><dd><code>{E(r['id'])}</code></dd>
<dt>Canonical URL</dt><dd><a href="{E(r['href'])}">{E(r['href'])}</a></dd>
<dt>Discovery</dt><dd>{E(r['discovery'])}</dd>
<dt>Technical verification</dt><dd>{E(r['verification'])}</dd>
<dt>Replacement</dt><dd>{E(r['replacement'] or 'None recorded.')}</dd>
<dt>Relationships</dt><dd>{rel_html}</dd>
</dl></details></article>'''
def inventory(records, counts):
  def n(pred):
    return sum(1 for r in records if pred(r))
  active = [s for s, _name, _c in SUBJECTS if any(s in r['subjects'] for r in records)]
  empty = [SUBJECT_NAME[s] for s, _n, _c in SUBJECTS if s not in active]
  lines = [
    ('Unique catalogued resources', str(len(records)), 'One row each. A lesson is also counted below as a lesson. That is a second view of the same row, not a second holding.'),
    ('Original articles', str(len(ORIGINAL_ARTICLES)), 'The nine pages that answer a question. Hubs, the plan, and this catalogue are not articles.'),
    ('Technically reproduced', str(n(lambda r: 'technically-reproduced' in r['labels'])), 'A named example was run in a documented environment. Not a security review.'),
    ('Complete lessons', str(counts['guided']), 'Guided lessons: a written walkthrough of an app recorded as working.'),
    ('Debug challenges', str(counts['challenge']), 'Deployed, and a core flow does not complete. Not counted as complete lessons.'),
    ('Project previews', str(counts['preview']), 'Teaching sequence not written.'),
    ('Research records', str(n(lambda r: 'research' in r['subjects'])), 'Includes the white-paper shelf and SIMD-0326. The SIMD repository remains one record. Other individual proposals were not catalogued.'),
    ('White papers and design notes', str(n(lambda r: r['id'].startswith('paper-'))), 'One retrieved document each. A French, Italian, or Japanese edition is a separate URL and not a second design. A docs homepage is not in this count.'),
    ('Historical records', str(n(lambda r: r['historical'])), 'None in this release. Past failures that still matter are inside current articles.'),
    ('Languages', str(len({r['language'] for r in records if r['id'].startswith('paper-')} | {'English'})), 'English, plus any language edition whose file was read. Those editions were not compared line by line. No other translation is catalogued.'),
    ('Active subject collections', str(len(active)) + ' of 24', 'A subject is active when at least one record names it. Active is not complete.'),
    ('Source checked', str(n(lambda r: 'source-checked' in r['labels'])), 'Destination read on 17 Nov 2026. Examples on those pages were not run.'),
    ('Editorially reviewed', '0', 'No reviewer is named, so the label is not used.'),
    ('Maintainer-confirmed', '0', 'No maintainer confirmation is recorded.'),
    ('Needs review', '0', 'Nothing has been marked invalid. A zero here is the state of this list, not a promise that every page is current.'),
    ('Replaced', '0', 'No replacement resource is recorded.'),
    ('Broken destinations', 'None recorded', 'A page that was read can still describe a workflow that fails. This number is not a link check from the build machine to solana.com, which returned HTTP 429.'),
    ('Review dates', '17 Nov 2026', 'Every review date in this release is that day. A median age is not meaningful until reviews happen on more than one date.'),
    ('Corrections resolved', 'No log in the site', 'GitHub issues are the log. Nothing is marked resolved inside this catalogue.'),
    ('Subjects with no record', ', '.join(empty) if empty else 'None', 'A gap in the coverage map. Not a claim that the subject is unimportant.'),
  ]
  body = ''.join(f'<tr><td>{E(a)}</td><td>{E(b)}</td><td>{E(c)}</td></tr>' for a, b, c in lines)
  return f'<table><thead><tr><th>Count</th><th>Value</th><th>What it includes</th></tr></thead><tbody>{body}</tbody></table>', empty
SCRIPT = r'''<script>
(function(){
  var form = document.getElementById('lib-form');
  var q = document.getElementById('lib-q');
  var items = [].slice.call(document.querySelectorAll('.lib-item'));
  var count = document.getElementById('lib-count');
  var empty = document.getElementById('lib-empty');
  var origin = document.getElementById('lib-origin');
  var subject = document.getElementById('lib-subject');
  var label = document.getElementById('lib-label');
  var historical = document.getElementById('lib-hist');
  var need = '', collection = '';
  var collections = COLLECTION_JSON;
  var stop = STOP_JSON;
  function words(s){
    var raw = (s.toLowerCase().match(/[a-z0-9_'-]+/g) || []);
    return raw.filter(function(w){ return w.length >= 3 && stop.indexOf(w) < 0; });
  }
  function apply(){
    var query = (q.value || '').trim();
    var exactMode = query.length >= 6 && query.indexOf(' ') < 0;
    var ws = exactMode ? [] : words(query);
    var shown = 0;
    items.forEach(function(el){
      var ok = true;
      if (need && el.getAttribute('data-needs').split(' ').indexOf(need) < 0) ok = false;
      if (subject.value && el.getAttribute('data-subjects').split(' ').indexOf(subject.value) < 0) ok = false;
      if (origin.value && el.getAttribute('data-origin') !== origin.value) ok = false;
      if (label.value && el.getAttribute('data-labels').split(' ').indexOf(label.value) < 0) ok = false;
      if (collection){
        var subs = el.getAttribute('data-subjects').split(' ');
        var want = collections[collection] || [];
        if (!want.some(function(s){ return subs.indexOf(s) >= 0; })) ok = false;
      }
      if (el.getAttribute('data-historical') === '1' && !historical.checked) ok = false;
      if (query && ok){
        if (exactMode){
          var raw = el.getAttribute('data-exact') || '';
          var hay = (el.getAttribute('data-search') || '');
          if (raw.indexOf(query) < 0 && hay.indexOf(query.toLowerCase()) < 0) ok = false;
        } else if (ws.length){
          var blob = el.getAttribute('data-search') || '';
          if (!ws.every(function(w){ return blob.indexOf(w) >= 0; })) ok = false;
        } else if ((el.getAttribute('data-search') || '').indexOf(query.toLowerCase()) < 0) ok = false;
      }
      el.hidden = !ok;
      if (ok) shown++;
    });
    count.textContent = shown + ' of ' + items.length + ' records';
    empty.hidden = shown !== 0;
  }
  function press(group, value, attr){
    document.querySelectorAll(group).forEach(function(b){
      b.setAttribute('aria-pressed', b.getAttribute(attr) === value ? 'true' : 'false');
    });
  }
  form.addEventListener('submit', function(e){ e.preventDefault(); apply(); document.getElementById('catalogue').scrollIntoView(); });
  q.addEventListener('input', apply);
  origin.addEventListener('change', apply);
  subject.addEventListener('change', function(){ collection = ''; press('[data-collection]', '', 'data-collection'); apply(); });
  label.addEventListener('change', apply);
  historical.addEventListener('change', apply);
  document.querySelectorAll('[data-try]').forEach(function(b){
    b.addEventListener('click', function(){ q.value = b.getAttribute('data-try'); q.focus(); apply(); document.getElementById('catalogue').scrollIntoView(); });
  });
  document.querySelectorAll('[data-need]').forEach(function(b){
    b.addEventListener('click', function(){
      need = b.getAttribute('data-need');
      press('[data-need]', need, 'data-need');
      apply();
      document.getElementById('catalogue').scrollIntoView();
    });
  });
  document.querySelectorAll('[data-collection]').forEach(function(b){
    b.addEventListener('click', function(){
      collection = b.getAttribute('data-collection');
      subject.value = '';
      press('[data-collection]', collection, 'data-collection');
      apply();
      document.getElementById('catalogue').scrollIntoView();
    });
  });
  var KEY = 'sc-library-saved';
  function load(){ try { var v = JSON.parse(localStorage.getItem(KEY) || '[]'); return Array.isArray(v) ? v : []; } catch (e) { return []; } }
  function persist(list){ localStorage.setItem(KEY, JSON.stringify(list)); }
  function renderSaved(){
    var list = load();
    document.querySelectorAll('[data-save]').forEach(function(b){
      var on = list.indexOf(b.getAttribute('data-save')) >= 0;
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.textContent = on ? 'Saved in this browser' : 'Save';
    });
    var box = document.getElementById('saved-list');
    box.replaceChildren();
    if (!list.length){
      var p = document.createElement('p');
      p.textContent = 'Nothing is saved in this browser.';
      box.appendChild(p);
      return;
    }
    var ul = document.createElement('ul');
    list.forEach(function(id){
      var el = document.getElementById('r-' + id);
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = el ? el.getAttribute('data-href') : '/library/';
      a.textContent = el && el.querySelector('h3') ? el.querySelector('h3').textContent : id;
      li.appendChild(a);
      ul.appendChild(li);
    });
    box.appendChild(ul);
  }
  document.querySelectorAll('[data-save]').forEach(function(b){
    b.addEventListener('click', function(){
      var id = b.getAttribute('data-save');
      var list = load();
      var i = list.indexOf(id);
      if (i >= 0) list.splice(i, 1); else list.push(id);
      persist(list);
      renderSaved();
    });
  });
  var lastBox = document.getElementById('continue-lesson');
  try {
    var last = JSON.parse(localStorage.getItem('sc-lesson-last') || 'null');
    if (last && typeof last.href === 'string' && last.href.charAt(0) === '/'){
      var a = document.createElement('a');
      a.href = last.href;
      a.textContent = last.title || last.href;
      lastBox.replaceChildren(a, document.createTextNode(' Stored in this browser. This is the last lesson page opened here, not a measured path.'));
    }
  } catch (e) {}
  renderSaved();
  apply();
})();
</script>'''
def page_html(records, counts):
  by_id = dict((r['id'], r) for r in records)
  table, _empty = inventory(records, counts)
  cards = ''.join(card(r, by_id) for r in records)
  needs = ''.join(f'<button type=button data-need="{i}">{E(n)}</button>' for i, n in NEEDS)
  collections = ''.join(f'<button type=button data-collection="{i}">{E(n)}</button>' for i, n, _s in COLLECTIONS)
  subject_opts = ''.join(f'<option value="{E(i)}">{E(n)}</option>' for i, n, _c in SUBJECTS)
  selection = ''.join(f'<li><a href="#r-{E(i)}">{E(by_id[i]["title"])}</a> — {E(by_id[i]["purpose"])}</li>' for i in SELECTION)
  checked = [r for r in records if r['labels']]
  recent = ''.join(f'<li><a href="#r-{E(r["id"])}">{E(r["title"])}</a> — {E(", ".join(LABEL_NAME[l] for l in r["labels"]))}, {E(r["reviewed"])}</li>' for r in checked)
  rooms = []
  for rid, name, question, intro, ids in ROOMS:
    lis = ''.join(f'<li><a href="{E(by_id[i]["href"])}">{E(by_id[i]["title"])}</a></li>' for i in ids)
    rooms.append(f'<section class=room id="room-{rid}"><h3>{E(name)}</h3><p><b>{E(question)}</b></p><p>{E(intro)}</p><p><a href="/library/guides/{rid}/">Read the guide</a>. The guide teaches only what these records support. It does not add a measurement.</p><ol>{lis}</ol></section>')
  subject_map = []
  for sid, name, coverage in SUBJECTS:
    rows = [r for r in records if sid in r['subjects']]
    if not rows:
      subject_map.append(f'<p id="subject-{sid}"><b>{E(name)}.</b> {E(coverage)} No record yet.</p>')
    else:
      links = ', '.join(f'<a href="#r-{E(r["id"])}">{E(r["title"])}</a>' for r in rows[:3])
      more = f' and {len(rows) - 3} more in the catalogue' if len(rows) > 3 else ''
      subject_map.append(f'<p id="subject-{sid}"><b>{E(name)}.</b> {len(rows)} catalogued. {E(coverage)} {links}{more}.</p>')
  suggest = issue('Library suggestion', 'Resource URL:\n\nWhy it should be in the library:\n\nWhat it does not cover:\n\n')
  report = issue('Library error', 'Page or record:\n\nWhat is wrong:\n\nWhat the source says:\n\n')
  repro = issue('Library reproduction', 'Record:\n\nEnvironment (commit, cluster, tool versions):\n\nWhat you ran:\n\nWhat you observed:\n\nDo not include private keys or recovery phrases.\n')
  maintain = issue('Library maintenance', 'Collection:\n\nWhat you can check:\n\n')
  coll_json = json.dumps(dict((i, s) for i, _n, s in COLLECTIONS))
  stop_json = json.dumps(sorted(STOP))
  script = SCRIPT.replace('COLLECTION_JSON', coll_json).replace('STOP_JSON', stop_json)
  return f'''<article class="lesson lib-page">
<p class=eyebrow>At Sol.College</p>
<h1>The Solana Library</h1>
<p class=lead>Understand it. Build it. Find the evidence.</p>
<p>Anything you need to understand, build, or investigate on Solana—find the right starting point here. The reference desk for your next question. The workshop for your next idea.</p>
<p>This is the founding catalogue. It is not a claim that every subject is covered, and it does not use a size ranking. A later stage aims at about 150 to 250 reviewed records. This page does not claim that count.</p>
<p>White papers and design notes that were retrieved, each with its own page, are in the <a href="/library/papers/">white paper catalogue</a>. A project’s docs homepage is not listed there unless a paper file was read.</p>
<form id=lib-form class=finder role=search>
<label>Search concepts, errors, code, tools, and research
<input id=lib-q type=search placeholder="A question, an error, or a program id" autocomplete=off>
</label>
<div class="finder-row lib-try">
<button type=button data-try="Why did my transaction expire?">Why did my transaction expire?</button>
<button type=button data-try="Token account versus wallet">Token account versus wallet</button>
<button type=button data-try="Build an escrow">Build an escrow</button>
<button type=button data-try="Understand validator operation">Understand validator operation</button>
<button type=button data-try="Proof of History">Proof of History</button>
</div>
<div class=finder-row>
<label>Subject <select id=lib-subject><option value="">Any subject</option>{subject_opts}</select></label>
<label>Origin <select id=lib-origin><option value="">Any origin</option><option value=original>Sol.College original</option><option value=external>External</option></select></label>
<label>Label <select id=lib-label><option value="">Any label</option><option value=source-checked>Source checked</option><option value=technically-reproduced>Technically reproduced</option></select></label>
</div>
<p><label><input id=lib-hist type=checkbox> Include historical records</label></p>
<p class=meta id=lib-count></p>
</form>
<p>A query with no spaces matches that string, including a program id or an instruction name. A question matches records that contain each remaining word. Semantic search is not part of this release. An AI librarian is not part of this release. The catalogue stays readable if that layer is never added. Results are not dropped for disagreeing with each other. Historical records stay hidden until you include them. None are marked historical yet.</p>
<p id=lib-empty hidden>No catalogue record contains every word of that query. That is a gap in this collection. Try one term, or a program id.</p>
<h2 id=continue>Continue learning</h2>
<p id=continue-lesson>No lesson page is stored in this browser.</p>
<p>Saved in this browser. There is no account.</p>
<div id=saved-list><p>Nothing is saved in this browser.</p></div>
<noscript><p>Saving and the last-lesson reminder need JavaScript. The records below are in the page without it.</p></noscript>
<h2 id=need>What do you need?</h2>
<div class="finder-row" role=group aria-label=Need>
<button type=button data-need="" aria-pressed=true>All</button>
{needs}
</div>
<h2 id=collections>Explore the collections</h2>
<div class="finder-row" role=group aria-label=Collections>{collections}</div>
<p>These buttons filter the catalogue. They do not create a separate URL, so an empty combination is not a page.</p>
<h2 id=catalogue>Catalogue</h2>
<p>Original pages and external links are mixed here on purpose, and the standing field says which is which. A record that stays on Sol.College opens the research page. A link that leaves the site is the publisher’s own page. A search or a button scrolls here.</p>
{cards}
<h2 id=selection>Librarian’s selection</h2>
<p>A small list chosen for this release. It is not ranked by visits, and it is not a complete set.</p>
<ol>{selection}</ol>
<h2 id=checked>Records checked on 17 Nov 2026</h2>
<p>Each line names the label that was earned. Source checked means the destination was read. Technically reproduced means a named example was run. Neither means editorially reviewed, and neither means safe.</p>
<ul>{recent}</ul>
<h2 id=replaced>Updated or replaced</h2>
<p>No replacement is recorded. Nothing in this catalogue is marked Replaced. The earlier Gifter program is described on the current failure article because that program account was still on devnet. It is not filed as a retired document.</p>
<h2 id=rooms>Reading rooms</h2>
<p>Ten routes through records that exist. A room with a thin shelf says so. There is no separate URL for an empty room.</p>
{''.join(rooms)}
<h2 id=escrow>Example: escrow</h2>
<p>Start at any of these. They stay different kinds of page.</p>
<ul>
<li>Prerequisite: <a href="/articles/follow-one-token-balance/">mint, token account, and authority</a></li>
<li>Prerequisite: <a href="/articles/what-is-a-solana-pda/">PDAs, from one pixel account</a></li>
<li>Prerequisite: <a href="/articles/a-solana-address-is-not-a-wallet/">an address is not a wallet</a></li>
<li>Explanation: <a href="/articles/why-this-escrow-take-failed/">why an earlier take aborted</a></li>
<li>Reference: <a href="https://solana.com/docs/tokens">official token documentation</a></li>
<li>Practice: <a href="/lessons/gifter-escrow/">the Gifter lesson</a></li>
<li>Investigation: <a href="/articles/what-a-failed-transaction-changed/">what the abort changed, and what the completed take changed</a></li>
<li>Case study: <a href="/articles/from-failing-take-to-pull-request/">an opened pull request, with no recorded passing test and no recorded merge</a></li>
</ul>
<p>There is no page yet for an acceptance-and-refund test suite. The case study names a test file and records no passing run.</p>
<h2 id=inventory>Inventory</h2>
<p>These numbers are this catalogue. The counting rules are on the <a href="/library/policy/">maintenance policy</a>.</p>
{table}
<h2 id=subjects>Subject catalogue</h2>
<p>A record can sit in more than one subject. It is still one page. This is a coverage map, not a claim that a subject is complete.</p>
{''.join(subject_map)}
<h2 id=contribute>Contribute</h2>
<p>Suggestions and corrections are GitHub issues. This page does not submit them for you. Do not send a private key or a recovery phrase.</p>
<ul>
<li><a href="{E(suggest)}">Suggest a resource</a></li>
<li><a href="{E(report)}">Report an error</a></li>
<li><a href="{E(repro)}">Submit a reproduction</a></li>
<li><a href="{E(maintain)}">Help maintain a collection</a></li>
<li><a href="/library/policy/">Maintenance policy</a></li>
</ul>
</article>''' + script
def policy_html():
  suggest = issue('Library suggestion', 'Resource URL:\n\nWhy it should be in the library:\n\nWhat it does not cover:\n\n')
  report = issue('Library error', 'Page or record:\n\nWhat is wrong:\n\nWhat the source says:\n\n')
  repro = issue('Library reproduction', 'Record:\n\nEnvironment (commit, cluster, tool versions):\n\nWhat you ran:\n\nWhat you observed:\n\nDo not include private keys or recovery phrases.\n')
  maintain = issue('Library maintenance', 'Collection:\n\nWhat you can check:\n\n')
  return f'''<article class="lesson lib-page">
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/library/">Library</a> / <span>Policy</span></nav>
<p class=eyebrow>Maintenance</p>
<h1>How the library is counted and corrected</h1>
<p class=lead>The catalogue has to stay usable if no assistant is available. Labels say only what was done.</p>
<h2 id=labels>Labels</h2>
<table>
<thead><tr><th>Label</th><th>Meaning</th><th>Used in this release</th></tr></thead>
<tbody>
<tr><td>Source checked</td><td>The publisher and the destination were confirmed by reading the page on the review date. Examples were not run.</td><td>The external records, dated 17 Nov 2026.</td></tr>
<tr><td>Editorially reviewed</td><td>A named reviewer assessed relevance, clarity, and scope.</td><td>No. No reviewer is named.</td></tr>
<tr><td>Technically reproduced</td><td>A stated example was run in a documented environment. This is not a security review.</td><td>The articles and two lessons that cite the 17 Nov 2026 devnet read.</td></tr>
<tr><td>Maintainer-confirmed</td><td>The original maintainer confirmed a specific fact.</td><td>No.</td></tr>
<tr><td>Historical</td><td>Preserved for context, not current guidance.</td><td>No record uses it yet.</td></tr>
<tr><td>Needs review</td><td>A change or a report has removed confidence.</td><td>No. The label is not used as a synonym for “we have not finished the subject”.</td></tr>
<tr><td>Replaced</td><td>A newer recommended resource exists.</td><td>No.</td></tr>
</tbody>
</table>
<p>An official page is not automatically a complete teaching resource. A technically reproduced tutorial is not automatically secure.</p>
<h2 id=history>Historical material</h2>
<p>When a record is historical, the page should show this notice, with the blanks filled from the record rather than from a guess:</p>
<aside class=note>
<p><b>Historical resource</b></p>
<p>This material describes an earlier toolchain or interface. Do not assume the examples work with current dependencies.</p>
<p>Why it is preserved: no record in this release uses this notice.</p>
<p>Current starting point: not established. Nothing is marked Replaced.</p>
</aside>
<p>A working link is not evidence the workflow still works.</p>
<h2 id=proposals>Proposals</h2>
<p>The SIMD repository contains proposed and accepted changes. SIMD-0326 is catalogued because the file cites the Alpenglow white paper, and its front matter says Review. For every other proposal this catalogue does not establish discussion status, acceptance, implementation, activation, or the client and network. The same rule applies to announcements and roadmaps.</p>
<h2 id=papers>White papers</h2>
<p>A white paper page exists only when the file was retrieved. The page records the title, the version, the date if the file states one, and what the opening says the document is for. It does not copy the paper. A figure in a paper is the paper’s figure. A translation is its own URL and is not counted as a second design. A docs page with no link to a paper is named on the <a href="/library/papers/">white paper catalogue</a> as a page that was checked, not as a holding.</p>
<h2 id=not-checked>Pages named in the plan that are not records</h2>
<ul>
<li>https://solana.com/developers — the fetch timed out.</li>
<li>https://solana.com/docs/payments/how-payments-work — not retrieved.</li>
<li>https://solana.com/docs/payments/interacting-with-solana — not retrieved.</li>
<li>https://solana.com/llms.txt — the build machine received HTTP 429, and the file was not read another way.</li>
</ul>
<p>A URL from the plan is not a curated record until the destination has been read. Older concept pages under /learn-by-example/ were not reviewed for this catalogue. The generated source walkthroughs under /explore/ are one index record, not one holding each.</p>
<h2 id=counting>Counting rules</h2>
<p>If a size claim is ever made, these are the counts that would have to be shown separately: unique catalogued resources, original articles, technically reproduced examples, complete lessons, research records, historical records, languages, and active subject collections.</p>
<p>Do not count every section of one document as a book, a repeated URL as a second resource, a translation as a new original, an unreviewed crawl as a holding, or a dead link as a current resource. Glossary entries are one glossary. Article hubs are not articles. The 120-title plan is not 120 holdings.</p>
<p>This release does not publish a size ranking. The stage target of about 150 to 250 reviewed records is a programme target, not the current inventory.</p>
<h2 id=search>Search and the assistant that is not here</h2>
<p>Search matches words and exact identifiers in this catalogue. It does not answer from outside the catalogue. There is no semantic index and no assistant. If one is added later, a technical sentence needs a citation, an inference needs to be named as an inference, unrun code needs to stay labelled as a draft, and the assistant must not ask for a private key or a recovery phrase or send a transaction because someone asked a question.</p>
<h2 id=access>Access</h2>
<p>Reading and searching do not require a wallet or an account. Saving a list uses this browser only. The key is <code>sc-library-saved</code>. The last lesson page, if you opened one, is <code>sc-lesson-last</code>. There is no Sol.College account behind either key.</p>
<p>This release is English. A translation would have to say whether it was machine-generated or human-reviewed, and which revision it follows. None is catalogued. The records are text, so the essential claims are not locked in a screenshot.</p>
<h2 id=roles>Who can change a record</h2>
<p>Contributor, collection editor, technical reviewer, translator, archivist, and administrator are roles a larger library would need. They are not assigned in this release. Adding the most records is not the thing this catalogue rewards. A useful correction is one that names the source.</p>
<h2 id=suggest>Corrections</h2>
<p>Each link opens a GitHub issue on Blockchains/sol-college. It does not submit from this page.</p>
<ul>
<li><a href="{E(suggest)}">Suggest a resource</a></li>
<li><a href="{E(report)}">Report an error</a></li>
<li><a href="{E(repro)}">Submit a reproduction</a></li>
<li><a href="{E(maintain)}">Help maintain a collection</a></li>
</ul>
<p><a href="/library/">Back to the library</a></p>
</article>'''
def validate(records, counts, guide_slugs):
  ids = [r['id'] for r in records]
  if len(ids) != len(set(ids)):
    raise SystemExit('library: duplicate id')
  hrefs = [r['href'] for r in records]
  if len(hrefs) != len(set(hrefs)):
    raise SystemExit('library: duplicate href')
  by = dict((r['id'], r) for r in records)
  for i in SELECTION + [i for _r in ROOMS for i in _r[4]]:
    if i not in by:
      raise SystemExit('library: missing id ' + i)
  for r in records:
    if not re.fullmatch(r'[a-z0-9-]+', r['id']):
      raise SystemExit('library: bad id ' + r['id'])
    for s in r['subjects']:
      if s not in SUBJECT_NAME:
        raise SystemExit('library: bad subject ' + s)
    if r['origin'] == 'external' and 'source-checked' not in r['labels']:
      raise SystemExit('library: external without source check ' + r['id'])
    if r['origin'] != 'external' and 'source-checked' in r['labels']:
      raise SystemExit('library: original marked source-checked ' + r['id'])
    for banned in ('editorially-reviewed', 'maintainer-confirmed', 'needs-review', 'replaced'):
      if banned in r['labels']:
        raise SystemExit('library: label not earned ' + r['id'])
    if 'technically-reproduced' in r['labels'] and 'not run' in r['verification'].lower():
      raise SystemExit('library: reproduced label without a run ' + r['id'])
  if set(ORIGINAL_ARTICLES) - set(ids):
    raise SystemExit('library: missing article')
  if counts['guided'] + counts['challenge'] + counts['preview'] != counts['lessons']:
    raise SystemExit('library: lesson counts do not add up')
  if set(guide_slugs) != set(GUIDE_NOTES):
    raise SystemExit('library: guide notes drifted')
  blob = json.dumps(records)
  for token in ('45C1bSkFCbjrqiQHqm8oS6J88jirW8rC46Qiu6TvoY6x', 'GsFGX3pzdgzugAfjcxH9Lbbz2aPZgXyvBoXkNnmxXwuY', '6Z5cvVUcJVFvkhmtJ4dYwgVqNn7jqN6TSisoYSihBA1r'):
    if token not in blob:
      raise SystemExit('library: missing identifier ' + token[:8])
def ld(title, desc, path):
  return {'@context': 'https://schema.org', '@type': 'WebPage', 'headline': title, 'description': desc,
    'dateModified': REVIEW, 'isPartOf': {'@type': 'WebSite', 'name': 'Sol.College', 'url': SITE + '/'},
    'mainEntityOfPage': SITE + path}
def write_page(S, page, css, path, title, desc, main, data):
  html_page = page(css + main, title + ' | Sol.College', desc, path)
  blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
  html_page = html_page.replace('</head>', '<script type="application/ld+json">' + blob + '</script></head>', 1)
  os.makedirs(os.path.dirname(f'{S}{path}index.html'), exist_ok=True)
  open(f'{S}{path}index.html', 'w').write(html_page)
  if '<h1>' not in html_page:
    raise SystemExit('library: page has no h1 ' + path)
  if 'world’s largest' in html_page or "world's largest" in html_page:
    raise SystemExit('library: size claim slipped into ' + path)
def guide_html(g, by_id):
  paras = ''.join(f'<p>{E(p)}</p>' for p in g['paras'])
  items = []
  for i, label in g['next']:
    if i not in by_id:
      raise SystemExit('library: guide link missing ' + i)
    r = by_id[i]
    items.append(f'<li><a href="/library/#r-{E(i)}">{E(label)}</a>. Catalogue title: <a href="{E(r["href"])}">{E(r["title"])}</a>.</li>')
  return f'''<article class="lesson lib-page">
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/library/">Library</a> / <span>{E(g["title"])}</span></nav>
<p class=eyebrow>Reading guide</p>
<h1>{E(g["title"])}</h1>
<p class=lead>{E(g["question"])}</p>
{paras}
<h2>Records this guide uses</h2>
<ul>{''.join(items)}</ul>
<p>A guide is not an extra holding. The counts on the <a href="/library/#inventory">inventory</a> do not include it. Nothing in this guide was executed for the guide itself. Where a figure appears, it is attributed to the page that states it.</p>
<p><a href="/library/#rooms">All reading rooms</a> · <a href="/library/policy/">Maintenance policy</a></p>
</article>'''
def write(S, page, css, live, lesson_of, functional_of, readiness, limit_of, one_line):
  records = hand_records()
  guides, guide_slugs = guide_records()
  records.extend(guides)
  records.extend(site_records())
  lessons, counts = lesson_records(live, lesson_of, functional_of, readiness, limit_of, one_line)
  counts['lessons'] = len(live)
  records.extend(lessons)
  import library_papers as _papers
  records.extend(_papers.records())
  validate(records, counts, guide_slugs)
  import library_guides as guides
  by_id = dict((r['id'], r) for r in records)
  guide_paths = []
  for g in guides.GUIDES:
    path = f'/library/guides/{g["slug"]}/'
    limit = ' It is not an additional holding and it reports no new measurement.'
    gdesc = g['question'].strip() + limit
    if len(gdesc) > 158:
      raise SystemExit('library: guide description is over 158 characters ' + g['slug'])
    write_page(S, page, css, path, g['title'], gdesc, guide_html(g, by_id), ld(g['title'], gdesc, path))
    guide_paths.append(path)
  paper_paths = _papers.write_pages(S, page, css)
  desc = 'A catalogue of Solana explanations, lessons, and official references. Search does not require a wallet. Holdings are counted in public.'
  write_page(S, page, css, '/library/', 'The Solana Library', desc, page_html(records, counts), ld('The Solana Library', desc, '/library/'))
  policy = 'Labels, counting rules, and the GitHub issues used to suggest a resource or report an error.'
  write_page(S, page, css, '/library/policy/', 'Library maintenance policy', policy, policy_html(), ld('Library maintenance policy', policy, '/library/policy/'))
  llms = f'{S}/llms.txt'
  if os.path.exists(llms):
    guide_lines = ''.join(f'- [{g["title"]}]({SITE}/library/guides/{g["slug"]}/): {g["question"]}\n' for g in guides.GUIDES)
    paper_lines = ''.join(f'- [{p["title"]}]({SITE}{p["path"]}): {p["project"]} {p["doc_type"]}.\n' for p in _papers.papers())
    block = '\n## Library\n- [The Solana Library](' + SITE + '/library/): Catalogue of original pages and source-checked references.\n- [Library maintenance](' + SITE + '/library/policy/): Labels, counting rules, and corrections.\n- [White papers](' + SITE + '/library/papers/): Retrieved project papers, one page each.\n' + guide_lines + paper_lines
    text = re.sub(r'\n## Library\n.*?(?=\n## |\Z)', '', open(llms).read(), flags=re.S)
    open(llms, 'w').write(text.rstrip() + '\n' + block)
  print('library:', len(records), 'records;', len(guide_paths), 'guides;', counts)
  return ['/library/', '/library/policy/'] + guide_paths + paper_paths
