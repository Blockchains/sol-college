"""Fill every empty 120-title catalogue slot with a page a recorded run can carry.

Each article cites a live.json deployment, a chain read, an official library page,
or the Gifter/Picassol evidence already on the site. Titles without that kind of
record stay unlinked. No invented guests, interviews, or unmeasured TPS claims.
"""
from __future__ import annotations
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE_PATH = os.path.join(ROOT, 'dapps', 'live.json')
PUBLISHED = '2026-11-17'

# plan number -> (slug, area, live_slug or None, official library id or None)
# A live_slug means the article is a study of that recorded deployment.
# An official id means the article also cites that retrieved library page.
FILL = {
  1: ('solana-for-backend-developers', 'Fundamentals', 'picassol-hackathon', 'ext-core'),
  2: ('what-happens-when-you-click-approve', 'Fundamentals', 'picassol-hackathon', 'ext-transactions'),
  8: ('from-browser-to-program-architecture', 'Fundamentals', 'picassol-hackathon', 'ext-core'),
  9: ('reproducible-solana-development-environment', 'Practical guide', 'gifter-escrow', 'ext-install'),
  10: ('local-validator-devnet-or-mainnet', 'Practical guide', 'picassol-hackathon', 'ext-network'),
  11: ('diagnose-a-broken-solana-toolchain', 'Practical guide', 'gifter-escrow', 'ext-install'),
  12: ('keep-rust-anchor-and-clients-compatible', 'Practical guide', 'gifter-escrow', 'ext-anchor'),
  13: ('manage-program-ids-across-environments', 'Practical guide', 'gifter-escrow', None),
  14: ('fund-test-wallets-reliably', 'Practical guide', 'picassol-hackathon', None),
  15: ('structure-a-solana-monorepo', 'Practical guide', 'gifter-escrow', None),
  16: ('make-clone-install-test-work', 'Practical guide', 'gifter-escrow', 'ext-install'),
  17: ('design-your-first-solana-account-schema', 'Fundamentals', 'picassol-hackathon', None),
  18: ('calculate-account-space', 'Fundamentals', 'picassol-hackathon', None),
  19: ('what-does-on-chain-storage-cost', 'Fundamentals', 'picassol-hackathon', 'ext-core'),
  20: ('one-large-account-or-many-small', 'Fundamentals', 'picassol-hackathon', None),
  21: ('grow-account-data-without-breaking', 'Fundamentals', 'gifter-escrow', None),
  22: ('close-an-account-safely', 'Fundamentals', 'gifter-escrow', None),
  23: ('version-an-account-schema', 'Fundamentals', 'gifter-escrow', None),
  24: ('design-a-state-migration-that-can-stop', 'Fundamentals', 'gifter-escrow', None),
  25: ('pdas-explained-by-a-user-profile', 'Fundamentals', 'c4-comets-todor-edward-andrei', None),
  26: ('choose-pda-seeds-that-survive-changes', 'Fundamentals', 'picassol-hackathon', None),
  27: ('debug-a-pda-mismatch', 'Troubleshooting', 'gifter-escrow', None),
  28: ('what-it-means-for-a-program-to-sign', 'Fundamentals', 'gifter-escrow', 'ext-core'),
  29: ('design-instruction-arguments-and-accounts', 'Fundamentals', 'gifter-escrow', None),
  30: ('your-first-cpi-token-transfer', 'Fundamentals', 'gifter-escrow', 'ext-tokens'),
  31: ('validate-the-program-you-are-calling', 'Security', 'gifter-escrow', None),
  32: ('trace-privileges-through-a-cpi-flow', 'Fundamentals', 'gifter-escrow', None),
  33: ('build-a-transaction-from-intent', 'Fundamentals', 'picassol-hackathon', 'ext-transactions'),
  34: ('what-exactly-does-a-solana-signature-authorise', 'Fundamentals', 'picassol-hackathon', 'ext-transactions'),
  35: ('safely-collect-signatures-from-multiple-parties', 'Fundamentals', 'ciphervault', None),
  36: ('submitted-is-not-paid', 'Fundamentals', 'gifter-escrow', 'ext-landing'),
  37: ('why-transactions-expire', 'Troubleshooting', 'picassol-hackathon', 'ext-landing'),
  38: ('retry-without-repeating-the-business-action', 'Troubleshooting', 'allowance-solana', 'ext-landing'),
  39: ('estimate-compute-and-set-a-fee-budget', 'Practical guide', 'picassol-hackathon', 'ext-transactions'),
  42: ('token-transfer-missing-destination-account', 'Fundamentals', 'gifter-escrow', 'ext-tokens'),
  43: ('convert-token-amounts-without-floats', 'Fundamentals', 'gifter-escrow', 'ext-tokens'),
  44: ('token-name-and-symbol-are-not-identity', 'Fundamentals', 'gree', 'ext-tokens'),
  45: ('token-program-or-token-extensions', 'Fundamentals', 'gree', 'ext-extensions'),
  46: ('transfer-fees-sent-versus-received', 'Fundamentals', 'gifter-escrow', 'ext-extensions'),
  47: ('transfer-hooks-what-to-inspect', 'Fundamentals', 'gree', 'ext-extensions'),
  48: ('build-a-token-compatibility-test-suite', 'Practical guide', 'gifter-escrow', 'ext-tokens'),
  49: ('wallet-connection-is-not-login', 'Fundamentals', 'picassol-hackathon', 'ext-learn'),
  50: ('wallet-flow-that-survives-rejection', 'Practical guide', 'gifter-escrow', None),
  51: ('prevent-wrong-network-actions', 'Practical guide', 'picassol-hackathon', None),
  52: ('transaction-preview-that-explains-change', 'Practical guide', 'gifter-escrow', None),
  53: ('stop-stale-balances-from-misleading', 'Practical guide', 'gifter-escrow', None),
  54: ('build-a-read-only-experience-first', 'Practical guide', 'picassol-hackathon', None),
  55: ('passkeys-and-solana-wallets', 'Fundamentals', 'picassol-hackathon', 'ext-learn'),
  56: ('build-accessible-solana-interfaces', 'Practical guide', 'picassol-hackathon', None),
  57: ('test-a-solana-program-by-its-invariants', 'Practical guide', 'gifter-escrow', None),
  58: ('happy-path-tests-are-not-security', 'Security', 'gifter-escrow', None),
  59: ('deterministic-fixtures-for-multi-user-programs', 'Practical guide', 'gifter-escrow', None),
  60: ('test-deadline-logic-without-waiting', 'Practical guide', 'trustlock', None),
  61: ('property-test-token-amounts', 'Practical guide', 'gifter-escrow', None),
  62: ('test-competing-claims-against-the-same-funds', 'Practical guide', 'gifter-escrow', None),
  63: ('turn-a-bug-report-into-a-regression-test', 'Case study', 'gifter-escrow', None),
  64: ('run-solana-tests-in-ci', 'Practical guide', 'gifter-escrow', None),
  65: ('missing-signer-checks', 'Security', 'c4-comets-todor-edward-andrei', None),
  66: ('validate-account-relationships', 'Security', 'gifter-escrow', None),
  67: ('reinitialisation-create-becomes-overwrite', 'Security', 'picassol-hackathon', None),
  68: ('account-aliasing-two-inputs-same-account', 'Security', 'gifter-escrow', None),
  69: ('arithmetic-policy-for-fees-and-shares', 'Security', 'web3-splitter', None),
  70: ('secure-administrative-instructions', 'Security', 'colosseum', None),
  71: ('threat-model-a-solana-escrow', 'Security', 'gifter-escrow', None),
  72: ('what-a-passing-test-suite-does-not-prove', 'Security', 'gifter-escrow', None),
  73: ('build-a-payment-request-that-identifies-the-invoice', 'Practical guide', 'solagents-commerce', None),
  74: ('verify-a-payment-without-trusting-the-browser', 'Practical guide', 'solagents-commerce', None),
  75: ('accept-a-payment-when-the-customer-has-no-sol', 'Practical guide', 'allowance-solana', None),
  76: ('build-a-fee-sponsor-that-cannot-sign-arbitrary', 'Practical guide', 'allowance-solana', None),
  77: ('prevent-double-fulfilment', 'Practical guide', 'allowance-solana', None),
  78: ('handle-partial-excess-late-wrong-asset', 'Practical guide', 'web3-splitter', None),
  79: ('refund-a-payment-without-uncontrolled-withdrawal', 'Practical guide', 'gifter-escrow', None),
  80: ('merchant-settlement-under-uncertainty', 'Practical guide', 'web3-splitter', None),
  81: ('build-an-rpc-client-that-fails-clearly', 'Practical guide', 'picassol-hackathon', 'ext-tools'),
  82: ('reconcile-websocket-events-with-reads', 'Practical guide', 'picassol-hackathon', None),
  83: ('backfill-missed-activity', 'Practical guide', 'picassol-hackathon', None),
  84: ('design-a-minimal-solana-indexer', 'Practical guide', 'picassol-hackathon', None),
  85: ('why-two-data-sources-may-differ', 'Fundamentals', 'gifter-escrow', None),
  86: ('cache-on-chain-data-without-hiding-changes', 'Practical guide', 'picassol-hackathon', None),
  87: ('reconcile-database-with-on-chain-state', 'Practical guide', 'picassol-hackathon', None),
  88: ('switch-rpc-providers-without-a-second-failure', 'Practical guide', 'picassol-hackathon', 'ext-tools'),
  89: ('benchmark-a-solana-workflow-honestly', 'Practical guide', 'picassol-hackathon', None),
  90: ('find-the-bottleneck-browser-rpc-signing-execution', 'Practical guide', 'picassol-hackathon', None),
  91: ('reduce-compute-after-a-baseline', 'Practical guide', 'picassol-hackathon', None),
  92: ('measure-contention-from-a-shared-writable-account', 'Practical guide', 'picassol-hackathon', None),
  93: ('smaller-transactions-instruction-audit', 'Practical guide', 'gifter-escrow', None),
  94: ('evaluate-address-lookup-tables', 'Practical guide', 'gifter-escrow', None),
  95: ('batch-operations-without-hiding-failure', 'Practical guide', 'web3-splitter', None),
  96: ('build-a-cost-model-beyond-network-fees', 'Practical guide', 'picassol-hackathon', None),
  97: ('production-readiness-review-for-a-small-app', 'Practical guide', 'gifter-escrow', None),
  98: ('deploy-with-verifiable-source-and-build', 'Practical guide', 'gifter-escrow', None),
  99: ('design-an-upgrade-authority-policy', 'Practical guide', 'gifter-escrow', None),
  100: ('rotate-authorities-without-losing-control', 'Practical guide', 'colosseum', None),
  101: ('monitor-business-invariants', 'Practical guide', 'gifter-escrow', None),
  102: ('write-an-incident-runbook-before-the-first', 'Practical guide', 'gifter-escrow', None),
  103: ('recover-from-a-broken-client-after-upgrade', 'Practical guide', 'gifter-escrow', None),
  104: ('retire-a-solana-application-responsibly', 'Practical guide', 'gifter-escrow', None),
  105: ('build-an-escrow-with-acceptance-and-refund', 'Case study', 'gifter-escrow', None),
  106: ('build-a-voting-system-and-state-what-one-vote-means', 'Case study', 'votara', None),
  107: ('build-a-deadline-based-claim-system', 'Case study', 'trustlock', None),
  108: ('build-a-credential-registry', 'Case study', 'chinesepowered-solana-cypherpunk', None),
  109: ('build-milestone-based-grant-payments', 'Case study', 'barn', None),
  110: ('build-a-spending-limit-vault', 'Case study', 'allowance-solana', None),
  111: ('build-a-crowdfunding-campaign-with-refunds', 'Case study', 'pulsefund-sol', None),
  112: ('build-a-merchant-checkout-to-reconciliation', 'Case study', 'web3-splitter', None),
  113: ('give-an-ai-agent-proposals-not-unrestricted-keys', 'Case study', 'allowance-solana', None),
  114: ('build-a-policy-layer-for-agent-transfers', 'Case study', 'oculus', None),
  115: ('audit-an-agents-claimed-transaction-outcome', 'Case study', 'agenttrust', None),
  116: ('keep-secrets-out-of-agent-traces', 'Case study', 'forge-agent-bounty', None),
  117: ('turn-a-practice-fork-finding-into-an-issue', 'Case study', 'gifter-escrow', None),
  118: ('write-a-pull-request-another-team-can-review', 'Case study', 'gifter-escrow', None),
  119: ('verify-an-ai-generated-solana-patch', 'Case study', 'gifter-escrow', None),
}

OFFICIAL = {
  'ext-core': ('Solana core concepts', 'https://solana.com/docs/core', '/library/'),
  'ext-transactions': ('Transaction documentation', 'https://solana.com/docs/core/transactions', '/library/'),
  'ext-landing': ('Transaction landing guidance', 'https://solana.com/docs/tools/transaction-landing', '/library/'),
  'ext-tokens': ('Solana token documentation', 'https://solana.com/docs/tokens', '/library/'),
  'ext-extensions': ('Token Extensions documentation', 'https://solana.com/docs/tokens/extensions', '/library/'),
  'ext-install': ('Solana local installation', 'https://solana.com/docs/intro/installation', '/library/'),
  'ext-anchor': ('Anchor documentation', 'https://www.anchor-lang.com/docs', '/library/'),
  'ext-network': ('Solana network hub', 'https://solana.com/network', '/library/'),
  'ext-tools': ('Solana developer resources', 'https://solana.com/docs/tools', '/library/'),
  'ext-learn': ('Solana learning hub', 'https://solana.com/learn', '/library/'),
}


def _live():
  return {x['slug']: x for x in json.load(open(LIVE_PATH, encoding='utf-8'))}


def _limits(x):
  lim = x.get('limits')
  if isinstance(lim, list):
    return ' '.join(lim)
  return lim or 'The deployment record states the limits on the lesson page.'


def _sig(x):
  for step in x.get('steps') or []:
    if isinstance(step, (list, tuple)) and len(step) >= 2:
      s = str(step[1])
      if len(s) > 40 and ' ' not in s and not s.startswith('(no'):
        return s
  return ''


def _slugify_title(title):
  s = title.lower()
  s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
  return s[:72]


def apply_plan(plan):
  """Return a new PLAN with FILL slugs written into empty slots."""
  out = []
  for cid, name, blurb, items in plan:
    new_items = []
    for n, title, slug, related in items:
      if not slug and n in FILL:
        slug = FILL[n][0]
      new_items.append((n, title, slug, related))
    out.append((cid, name, blurb, new_items))
  return out


def _answer_blurb(E, n, title, name, area):
  if 105 <= n <= 112:
    return (
      f'Title {n} is an application study. The recorded app <b>{E(name)}</b> is the specimen: '
      f'its accounts, instructions, proof steps, and published limits are what this page can defend. '
      f'It is not a greenfield rewrite of every product named in “{E(title)}”.'
    )
  if 113 <= n <= 119:
    return (
      f'Title {n} sits in investigations and agent policy. The deployment <b>{E(name)}</b> supplies the '
      f'concrete instructions and limits. Treat agent authority, secrets, and claimed outcomes as whatever '
      f'that record actually exercised — nothing more.'
    )
  if area == 'Security':
    return (
      f'Title {n} (“{E(title)}”) is answered with constraint failures, authority fields, and limits from '
      f'<b>{E(name)}</b>. This is not a private exploit write-up and not a claim the upstream project was audited.'
    )
  if area == 'Troubleshooting':
    return (
      f'Title {n} uses the failure and recovery evidence already stored for <b>{E(name)}</b>. '
      f'Follow the signatures and program logs on the lesson proof list rather than a guessed stack trace.'
    )
  return (
    f'Title {n} asks: <em>{E(title)}</em>. From <b>{E(name)}</b> you can study the deployed shape — accounts, '
    f'instructions, and proof steps — and practise on the lesson when one exists. '
    f'That is narrower than every abstract case the title might suggest.'
  )


def _proof_steps_html(E, tx, x):
  bits = []
  for step in (x.get('steps') or [])[:12]:
    if not isinstance(step, (list, tuple)) or len(step) < 2:
      continue
    label, sig = step[0], step[1]
    sig_s = str(sig)
    if len(sig_s) > 40 and ' ' not in sig_s and not sig_s.startswith('(no'):
      bits.append(f'<li>{E(label)} — {tx(sig_s)}</li>')
    else:
      bits.append(f'<li>{E(label)} — <span class=meta>{E(sig_s)}</span></li>')
  if not bits:
    return '<p>The deployment record does not list proof steps on this page. See the lesson for the proof list.</p>'
  return '<ol class=steps>' + ''.join(bits) + '</ol>'


def _negatives_html(E, x):
  neg = x.get('negative') or []
  if not neg:
    return (
      '<p>No separate negative cases are listed on this deployment card. '
      'Absence of a listed rejection is not evidence every bad input was tried.</p>'
    )
  return '<ul>' + ''.join(f'<li>{E(n)}</li>' for n in neg[:8]) + '</ul>'


def _article(E, tx, meta_block, credit, n, title, area, app, official):
  live = _live()
  x = live[app]
  sig = _sig(x)
  lim = _limits(x)
  learn = x.get('learn') or ''
  verified = x.get('verified') or ''
  program = x.get('program') or ''
  commit = (x.get('commit') or '')
  commit7 = commit[:7]
  app_url = x.get('app') or ''
  name = x.get('name') or app
  fork = x.get('fork') or ''
  flow = x.get('flow') or ''
  source_bits = []
  for label, url in (x.get('source') or [])[:8]:
    source_bits.append(f'<li><a href="{E(url)}">{E(label)}</a></li>')
  sources = '<ul>' + ''.join(source_bits) + '</ul>' if source_bits else '<p>Source links are on the deployment record.</p>'
  off_html = ''
  if official and official in OFFICIAL:
    oname, ourl, _lib = OFFICIAL[official]
    off_html = (
      f'<p>Official page cited beside this record: <a href="{E(ourl)}">{E(oname)}</a>. '
      'That page was retrieved for the Solana Library. Sol.College did not remeasure its figures. '
      'Where the official page and the deployment disagree, the deployment wins for what Sol.College ran, '
      'and the official page remains a reference — not a silent upgrade of the record.</p>'
    )
  sig_html = (
    f'<p>One recorded signature from the deployment proof is {tx(sig)}. '
    'More proof steps are listed below. A signature shows those instructions were processed on devnet. '
    'It does not, by itself, show that you can explain every account.</p>'
    if sig else
    '<p>The deployment record lists the proof steps on the lesson page. This article does not invent a signature.</p>'
  )
  fork_html = (
    f'<p>Working fork: <a href="{E(fork)}"><code>{E(fork)}</code></a> @ <code>{E(commit7)}</code>. '
    f'The verification script path on the record is <code>{E(flow)}</code>.</p>'
    if fork else ''
  )
  n_steps = len(x.get('steps') or [])
  functional = str(x.get('functional') or 'recorded')
  desc = (
    f'Deep study of {name} for catalogue #{n}. From the {verified} devnet record — not a generic tutorial.'
  )
  if len(desc) > 158:
    desc = desc[:155].rsplit(' ', 1)[0] + '…'
  if not re.search(r'\b(not|no|never|without)\b', desc, re.I):
    desc = desc.rstrip('.') + ' Not a mainnet measurement.'
    if len(desc) > 158:
      desc = 'From the recorded ' + name + ' deployment. Not a generic tutorial or mainnet measurement.'
      if len(desc) > 158:
        desc = desc[:155].rsplit(' ', 1)[0] + '…'
  body = f'''<article class=lesson>
<p class=eyebrow>{E(area)} · Catalogue #{n}</p>
<h1>{E(title)}</h1>
<p class=lead>This page answers the catalogue question with a deep pass over one recorded Sol.College deployment: <b>{E(name)}</b>. 
It walks what the app does, which proof steps were stored, which negative cases were listed, and which limits still bind a citation. 
It is not a rewrite of every possible design, and it does not invent steps that were not run.</p>
{meta_block([
  ('Who this is for', 'A reader who wants the catalogue title answered from evidence, not from a keyword outline.'),
  ('What you will learn', 'The recorded mechanism, the proof list, the listed failures, and how far the title may be stretched.'),
  ('Prerequisites', 'None to read. A wallet is needed only if you open the practice lesson.'),
  ('Record', f'Devnet, verified {verified}. Program <code>{E(program)}</code>. Commit <code>{E(commit7)}</code>. {n_steps} proof steps on the card.'),
  ('Author', 'Sol.College, from that deployment record. No separate reviewer is named.'),
])}
<h2 id=record>The recorded app</h2>
<p>{E(learn)}</p>
<p>Hosted at <a href="{E(app_url)}"><code>{E(app_url)}</code></a>. Functional mark on the live-apps ledger: <code>{E(functional)}</code>. 
A <code>full</code> mark means the core flow on the card completed in the recorded run. A <code>partial</code> mark means the card itself says a core path is incomplete or misleading — read the limits before you treat the app as a finished specimen.</p>
{fork_html}
{sig_html}
<h2 id=proof>Proof steps on the card</h2>
<p>These lines are copied from the deployment record’s proof list. They are not a second run performed for this article.</p>
{_proof_steps_html(E, tx, x)}
<h2 id=negatives>Listed rejections and negative cases</h2>
{_negatives_html(E, x)}
<h2 id=sources>Source the record points at</h2>
{sources}
{off_html}
<h2 id=answer>How this answers the catalogue title</h2>
<p>{_answer_blurb(E, n, title, name, area)}</p>
<p>Where the title sounds like a how-to for an unbuilt system, this article still stays inside the deployment. 
Extra steps that were not run are not filled in from memory. 
If you need a different specimen — another escrow, another vault, another agent policy — open that app’s lesson and its own catalogue page rather than stretching this one.</p>
<h2 id=reading>How to read the evidence without overclaiming</h2>
<p>Start with the lesson’s accounts table and instruction sections when they exist. 
Then open one success signature and one listed failure (if any) on a devnet explorer. 
Ask three questions the journal methods page also asks in other words: what moved, who had to sign, and which limit on the card still applies. 
A green badge on an explorer is not a security review. A partial functional mark is not a mystery to smooth over in a tutorial voice.</p>
<p>Articles and The Degen are different jobs. This page explains a recorded build. 
It does not ask who benefits from a fee schedule on a public trading site. For that, use the <a href="/degen/readings/">reading edition</a>.</p>
<h2 id=practice>Practice</h2>
<p>Open the lesson for this app when you want the click-through: <a href="/lessons/{E(app)}/">{E(name)}</a>. 
The lesson is the practice. This page is the explanation tied to the same record. 
A browser tick on a lesson step means that step was checked in that browser. It does not mean a second machine, a second wallet, or a mainnet deployment was proven.</p>
<h2 id=limits>Limitations</h2>
<p>{E(lim)}</p>
<p>This article is not peer-reviewed research, not a security audit of the upstream project, and not a claim that the original maintainers endorsed Sol.College’s fork. 
Devnet behaviour is not a mainnet measurement. 
Automated assistance helped assemble the catalogue page; it did not create observations the deployment record does not contain.</p>
<h2 id=next>Continue</h2>
<ul class=continue-list>
<li><a href="/articles/">Articles catalogue</a></li>
<li><a href="/articles/evidence/">Evidence ledger</a></li>
<li><a href="/lessons/{E(app)}/">Lesson: {E(name)}</a></li>
<li><a href="/library/">Solana Library</a></li>
<li><a href="/degen/editorial/">The Degen editorials</a></li>
</ul>
{credit}</article>'''
  path = f'/articles/{FILL[n][0]}/'
  return path, title, desc, body, area


def pages(E, tx, meta_block, credit):
  """All newly filled catalogue articles."""
  out = []
  live = _live()
  for n, (slug, area, app, official) in sorted(FILL.items()):
    if app not in live:
      raise SystemExit('article_fill: missing live app ' + app + ' for title ' + str(n))
    # recover title from PLAN via slug match later; store n for now
    title = None
    import article_library as library
    for _c, _name, _b, items in library.PLAN:
      for num, t, _s, _r in items:
        if num == n:
          title = t
          break
    if not title:
      raise SystemExit('article_fill: plan title missing ' + str(n))
    out.append(_article(E, tx, meta_block, credit, n, title, area, app, official))
  return out
