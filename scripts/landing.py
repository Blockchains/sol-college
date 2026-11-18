"""Generate the pivoted Sol.College homepage from scripts/landing.html + dapps/live.json.

Usage: python3 scripts/landing.py [site_dir]

CI must call this after lesson pages are generated (end of core_lessons.py) so
this file replaces site/index.html and is not used as the lesson-page shell.

Honesty rules:
- Live environment cards list ONLY apps whose recorded core flows completed
  on devnet (live.json `functional` == full). Partial apps are debug challenges.
- Counts are computed, never invented. Fix-commit metrics are omitted until
  real suggested-commit patches exist (static-host build patches do not count).
- Practice environments are open-source dApps redeployed on devnet — not
  evidence that original teams are participating partners.
- Finding cards must not contradict current functional status (past-tense a fixed bug).
"""
from __future__ import annotations
import html, json, os, re, shutil, sys
from pathlib import Path
import findings as _findings  # records/public/findings -> landing card, proof stat, /findings/ pages
import learning_layer as _learning_layer
import release_identity as _release

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SITE = 'https://sol.college'
E = lambda s: html.escape(str(s), quote=True)


def _learning_layer_start():
  return _learning_layer.start_section_html()

# Overwritten by core_lessons with the first guided path lesson before write_home.
START_LESSON = '/lessons/'
WAITLIST = 'https://github.com/Blockchains/sol-college/issues/new?template=learner-waitlist.yml'
WAITLIST_DEV = WAITLIST + '&role=Developer'
WAITLIST_SEC = WAITLIST + '&role=Security+researcher'
WAITLIST_HUNT = WAITLIST + '&role=Bug+bounty+hunter'
PROJECT = 'https://github.com/Blockchains/sol-college/issues/new?template=project-partnership.yml'
COMMIT = 'https://github.com/Blockchains/sol-college/issues/new?template=commit-suggestion.yml'

TITLE = 'Sol.College — Learn, Test and Improve Real Solana dApps'
DESCRIPTION = (
    'Learn on Solana apps and offer patches back. Practice environments are independent '
    'forks we ran on devnet, not a claim that the original team is a partner.'
)

# Core-flow failures documented in dapps/live.json limits / negative (2026-11-13).
# These are excluded from the "fully working" list. Reasons are for operators;
# featured findings on the page are a subset, quoted from the same evidence.
# Historical operator notes for apps once excluded from the live list.
# live.json `functional` is the source of truth now; this map is only a fallback
# when a row has no functional field. Do not treat entries here as current status.
CORE_BROKEN = {
    'hackathon-prediction-market-solana': 'withdraw_liquidity moves 0 SOL; there is no claim or redeem, so winnings cannot be cashed out',
    'web3-splitter': 'claim pays the whole balance to the authority; a multi-recipient payout does not work',
    'pulsefund-sol': 'Contribute always donates to the connected wallet’s own campaign, not the selected one',
    'votara': 'stake_tokens and buy_tokens move no tokens and no SOL',
    'barn': 'reject_grant_milestone calls accept_milestone, so a reject accepts the milestone',
    'friendstake': 'cancel, decline and settle_bet do not bind the accounts, so funds can be sent to the wrong wallet',
    'devos-decentralized-voting': 'the hosted UI cannot open the election, add voters or vote; after get_winner the election can be reopened and the stored winner goes stale',
}
STATUS_WORKING = {
    'fully working', 'fully_working', 'fully-functional', 'fully functional',
    'working', 'ok', 'complete',
}

# Featured findings (must match live.json evidence; do not invent).
FEATURED_FINDINGS = [
    dict(
        slug='barn',
        title='Barn: reject calls accept',
        text='The program’s reject_grant_milestone entry point calls accept_milestone, so “rejecting” a milestone in review accepts it, and the sponsor can then be asked to pay it. Still recorded as a debug challenge until a verified fix lands.',
    ),
    dict(
        slug='gifter-escrow',
        title='Gifter escrow: take was broken, then fixed',
        text='An earlier program aborted take_and_close with an access violation (println in the take path). Create and refund already worked. The hosted program now completes take; the opened upstream PR records the patch. This card is the finding history, not a claim that take is still broken.',
    ),
    dict(
        slug='hackathon-prediction-market-solana',
        title='Prediction market: withdraw moves 0 SOL',
        text='withdraw_liquidity succeeds but moves nothing — the handler only runs checks. A 0.02 SOL withdrawal changed the vault by 0, so LP SOL is locked. There is also no claim or redeem instruction.',
    ),
]

BUG_RE = re.compile(r'(?i)(?:^\s*bugs?\s*:|^\s*BUG\b|\bBUG:)')

ICO = {
    'CONTEXT': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19V5m0 14h16"/><path d="M8 15l3-4 3 3 4-6"/></svg>',
    'TEST': '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6"/><path d="M20 20l-4-4"/><path d="M9 11h4M11 9v4"/></svg>',
    'INVESTIGATE': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l8 4v5c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V7l8-4z"/><path d="M9 12l2 2 4-4"/></svg>',
    'CONTRIBUTE': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 3H6a2 2 0 00-2 2v14a2 2 0 002 2h12a2 2 0 002-2V9z"/><path d="M14 3v6h6"/><path d="M9 13h6M12 10v6"/></svg>',
    'DEV': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 8l-5 4 5 4M16 8l5 4-5 4M13 4l-2 16"/></svg>',
    'SEC': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l8 4v5c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V7l8-4z"/><circle cx="12" cy="12" r="2.5"/><path d="M12 14.5V17"/></svg>',
    'HUNT': '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/></svg>',
    'FORK': '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="6" cy="6" r="2.5"/><circle cx="6" cy="18" r="2.5"/><circle cx="18" cy="12" r="2.5"/><path d="M8.5 6H12a4 4 0 014 4v2M8.5 18H12a4 4 0 004-4"/></svg>',
    'SCOPE': '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M8 9h8M8 12h8M8 15h5"/></svg>',
    'COMMIT': '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="M12 3v6M12 15v6"/></svg>',
    'LOOP': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 12a8 8 0 11-2.3-5.6"/><path d="M20 4v6h-6"/></svg>',
    'X': '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 8l8 8M16 8l-8 8"/></svg>',
}

FAQ = [
    ('What do you mean by a live fork?',
     'An interactive, isolated environment: an open-source Solana application redeployed on devnet, not a screenshot or a static code sample. Unless a project is recorded as an official participant, the fork is an independent practice environment. It is not an endorsement, and it is not evidence of a partnership. A fork may differ from the production application.'),
    ('Do I need to be an experienced Solana developer?',
     'The pathway should match your starting point. Some challenges focus on understanding application flows and testing user journeys; others require programming knowledge or security research experience. Each challenge states its prerequisites so you can choose work that is appropriate for you.'),
    ('Am I testing the project’s production application?',
     'Not unless a separate programme explicitly authorises it. The default learning environment is the provided fork. Permission to use that environment does not extend to production systems, real user accounts or third-party infrastructure.'),
    ('Will I earn a bug bounty?',
     'Only where a participating programme explicitly offers one and your submission meets its published terms. Course participation, challenge completion and submission of a potential issue do not automatically qualify for payment.'),
    ('What happens to a finding?',
     'You submit it through the designated process with the evidence needed to assess it. The project can then determine whether it is reproducible, relevant to its production system, already known or in need of further investigation. A submission is not a confirmed vulnerability until it has been appropriately validated.'),
    ('Can I share my work publicly?',
     'Only within the relevant permissions and disclosure rules. Some learning outputs may be suitable for a public portfolio; security findings and confidential project information may need to remain private.'),
    ('Does this replace a security audit?',
     'No. Educational testing and community research can contribute useful findings, but they are not a guarantee of security or a substitute for appropriately scoped professional review.'),
    ('How can my project participate?',
     'Start by proposing an application, feature or challenge. Together, we define the environment, learning objectives, testing scope, deliverables and review process before opening it to participants.'),
]


def load_live():
    p = ROOT / 'dapps' / 'live.json'
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding='utf-8'))


def lesson_doc(slug):
    fp = ROOT / 'dapps' / 'lessons' / f'{slug}.json'
    if not fp.exists():
        return {}
    try:
        return json.loads(fp.read_text(encoding='utf-8'))
    except Exception:
        return {}


def lesson_functional(slug):
    """Read dapps/lessons/<slug>.json 'functional' if present."""
    return lesson_doc(slug).get('functional')


def ownership_by_slug(root=None):
    root = Path(root) if root else ROOT
    out = {}
    for f in (root / 'config' / 'projects').glob('*.json'):
        try:
            c = json.loads(f.read_text(encoding='utf-8'))
        except Exception:
            continue
        if c.get('slug'):
            out[str(c['slug'])] = str(c.get('ownership') or '')
    return out


def pr_slugs(prs):
    """Slugs whose evidence records an opened upstream pull request."""
    found = set()
    for p in prs:
        src = str(p.get('source') or '').replace('\\', '/')
        if src.startswith('live.json:'):
            found.add(src.split(':', 1)[1])
            continue
        parts = src.split('/')
        if 'patches' in parts:
            i = parts.index('patches')
            if i + 1 < len(parts):
                found.add(parts[i + 1])
    return found


def is_fully_functional(x):
    """Match scripts/core_lessons.py functional_of: live.json field wins, then lesson JSON.

    'partial' / 'debug' / 'incomplete' are debug challenges and are excluded from
    the fully-working list. Unset defaults to 'full', matching the lessons path.
    A live.json 'status' of fully-working synonyms is also honoured.
    """
    raw = x.get('functional') if x.get('functional') not in (None, '') else None
    if raw is None:
        raw = x.get('status') or x.get('working')
    if raw is None:
        raw = lesson_functional(x.get('slug'))
    v = str(raw or 'full').strip().lower()
    if v in ('partial', 'part', 'debug', 'incomplete'):
        return False
    if v in STATUS_WORKING or v == 'full':
        return True
    return x.get('slug') not in CORE_BROKEN


def first_sentence(text, n=112):
    t = ' '.join(str(text or '').split())
    if not t:
        return ''
    m = re.match(r'(.{1,' + str(n) + r'}?(?:\.(?=\s)|$))', t)
    s = (m.group(1) if m else t[:n]).strip()
    if len(t) > len(s) and not s.endswith('.'):
        if ' ' in s:
            s = s.rsplit(' ', 1)[0]
        s = s.rstrip('.,;:—-') + '…'
    return s


def display_name(x):
    n = re.sub(r'\s+[—–]\s+.*$', '', x.get('name') or x['slug']).strip()
    sl = x.get('slug') or ''
    if sl:
        n = re.sub(r'\s*\(' + re.escape(sl) + r'\)\s*$', '', n, flags=re.I)
    return n


def fmt_date(s):
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', str(s or ''))
    if not m:
        return s or ''
    months = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
    return f'{int(m.group(3))} {months[int(m.group(2))-1]} {m.group(1)}'


def _limit_texts(x):
    items = []
    lim = x.get('limits')
    if isinstance(lim, list):
        items.extend(lim)
    elif lim:
        items.append(lim)
    for n in x.get('negative') or []:
        if isinstance(n, (list, tuple)):
            items.append(' '.join(str(p) for p in n))
        else:
            items.append(n)
    return [str(t) for t in items]


def explicit_bugs(apps):
    """Unique explicit BUG records in live.json limits / negative. Conservative."""
    named = (
        'take_and_close', 'reject_grant_milestone', 'withdraw_liquidity',
        'sign_as_registrar', 'sign_as_dean', 'signcredential',
        'initialize_university', 'settle_bet', 'approve_sponsor',
    )
    seen = set()
    found = []
    for x in apps:
        for t in _limit_texts(x):
            if not BUG_RE.search(t):
                continue
            norm = re.sub(r'\s+', ' ', t).lower()
            # Prefer a named instruction so the same bug recorded in both
            # limits and negative is counted once (e.g. take_and_close).
            instr = next((w for w in named if w in norm), None)
            stem = (x['slug'], instr or norm[:80])
            if stem in seen:
                continue
            seen.add(stem)
            found.append((x['slug'], t))
    return found


def orbit_html(apps):
    """Six real practice-app names placed around the hero ring. Short names read at a glance."""
    picked = []
    for x in apps:
        name = display_name(x)
        if 3 <= len(name) <= 18 and name not in picked:
            picked.append(name)
        if len(picked) == 6:
            break
    if len(picked) < 6:
        for x in apps:
            name = display_name(x)
            if name not in picked:
                picked.append(name if len(name) <= 18 else name[:17].rstrip() + '…')
            if len(picked) == 6:
                break
    return ''.join(f'<span class="sat sat-{i}">{E(name)}</span>' for i, name in enumerate(picked, 1))


def marquee_html(apps):
    names = [display_name(x) for x in apps]
    if not names:
        return ''
    chips = ''.join(f'<span>{E(n)}</span>' for n in names)
    # Decorative ticker only: the duplicated chip stream stays out of the
    # accessibility tree. Sighted users see motion; assistive tech gets the label.
    return (
        '<div class="marquee" role="presentation">'
        f'<p class="marquee-label">Practice environments on devnet '
        f'<span class="visually-hidden">({len(names)} named; decorative ticker)</span></p>'
        f'<div class="marquee-mask" aria-hidden="true"><div class="marquee-track">{chips}{chips}</div></div>'
        '</div>'
    )


def plain_pitch(x):
    """A short newcomer pitch. Prefer the lesson summary; do not cut mid-clause when a full sentence fits."""
    doc = lesson_doc(x.get('slug'))
    raw = ' '.join(str(doc.get('summary') or x.get('learn') or '').split())
    if not raw:
        return ''
    if len(raw) <= 180:
        return raw
    # Prefer ending on a sentence boundary inside the budget.
    cut = raw[:180]
    dot = cut.rfind('. ')
    if dot >= 80:
        return cut[:dot + 1]
    return cut.rsplit(' ', 1)[0].rstrip('.,;:—-') + '…'


def relation_html(slug, ownership, submitted):
    if ownership.get(slug) == 'participating-project':
        kind = 'Official project participant'
    else:
        kind = 'Independent practice fork'
    bits = [f'<span class="rel">{E(kind)}</span>']
    if slug in submitted:
        bits.append('<span class="rel pr">Upstream PR submitted</span>')
    return f'<p class="rels">{"".join(bits)}</p>'


def card_article(x, ownership, submitted, marks):
    sl = E(x['slug'])
    name = E(display_name(x))
    pitch = E(plain_pitch(x))
    verified = E(fmt_date(x.get('verified') or ''))
    level = str(lesson_doc(x['slug']).get('difficulty') or '').strip()
    level_html = f'<span class="level">{E(level)}</span>' if level else ''
    mark = ''
    if (marks / f'{x["slug"]}.jpg').is_file():
        mark = (
            f'<a class="mark-stage" href="/dapps/{sl}/" tabindex="-1" aria-hidden="true">'
            f'<img class="mark" src="/assets/marks/{sl}.jpg" alt="" width="640" height="640">'
            f'</a>'
        )
    return (
        f'<article class="glass card" data-slug="{sl}">'
        f'{mark}'
        f'<div class="card-body">'
        f'<p class="meta">{level_html}<span class="live-dot" aria-hidden="true"></span>Devnet verification {verified}</p>'
        f'{relation_html(x["slug"], ownership, submitted)}'
        f'<h3><a href="/dapps/{sl}/">{name}</a></h3>'
        f'<p class="pitch">{pitch}</p>'
        f'<p class="links"><a class="app" href="/dapps/{sl}/">Open the environment</a>'
        f'<a class="lesson" href="/lessons/{sl}/">Start the lesson</a>'
        f'<a class="evidence" href="/live/#{sl}">View evidence</a></p>'
        f'</div>'
        f'</article>'
    )


def live_cards(apps, ownership=None, submitted=None):
    marks = HERE / 'marks'
    ownership = ownership if ownership is not None else ownership_by_slug()
    submitted = submitted if submitted is not None else set()
    return '\n'.join(card_article(x, ownership, submitted, marks) for x in apps)


FEATURED = ('poe-solana', 'mandatekey', 'sentient-send')


def featured_html(apps, ownership, submitted):
    by = {x['slug']: x for x in apps}
    marks = HERE / 'marks'
    cards = []
    for slug in FEATURED:
        x = by.get(slug)
        if not x or not is_fully_functional(x):
            continue
        cards.append(card_article(x, ownership, submitted, marks))
    if not cards:
        return ''
    return '\n'.join(cards)


def results_html(bugs, prs, sec_findings):
    sec_prs = _findings.total_prs(sec_findings)
    sec_merged = sum(_findings.stats(d)['merged'] for d in sec_findings)
    rows = (
        ('Functional bugs in the practice forks', len(bugs), len(prs), 0),
        ('Security remediation', len(sec_findings), sec_prs, sec_merged),
    )
    body = ''.join(
        f'<tr><th scope="row">{E(name)}</th>'
        f'<td data-label="Findings">{found}</td>'
        f'<td data-label="PRs submitted">{submitted}</td>'
        f'<td data-label="Recorded as merged">{merged}</td></tr>'
        for name, found, submitted, merged in rows
    )
    return (
        '<div class="results">'
        '<table class="results-table">'
        '<thead><tr><th scope="col">Work</th><th scope="col">Findings</th>'
        '<th scope="col">PRs submitted</th><th scope="col">Recorded as merged</th></tr></thead>'
        f'<tbody>{body}</tbody>'
        '</table>'
        '<p class="results-more"><a href="/live/#counts">How these counts are recorded</a></p>'
        '</div>'
    )


def counts_note_html():
    """The counting rules live on the evidence page, not under the homepage table."""
    return (
        '<h2 id="counts" style="scroll-margin-top:88px">How the homepage counts are recorded</h2>'
        '<p>The homepage table is filled from the evidence files, not from a separate headline.</p>'
        '<p>Functional findings are explicit Bug records in the devnet notes. '
        'Security remediation is the public finding record: one review, with a pull request counted only when that record links one. '
        '“Recorded as merged” counts only pull requests whose stored state is merged. '
        'An opened pull request with no recorded decision stays in submitted. The original team accepts or declines.</p>'
    )


def example_html(prs):
    hit = next((p for p in prs if p.get('url') == 'https://github.com/berkaycirak/gifter-escrow/pull/1'), None)
    if not hit:
        return ''
    url = E(hit['url'])
    return (
        '<section class="band" id="example"><div class="inner">'
        '<p class="eyebrow">One complete pass</p>'
        '<h2>A finding, a fix, an opened pull request.</h2>'
        '<p class="lead">Gifter escrow is an independent practice fork. This is the recorded path for one finding. It is not a claim that the original team has accepted the change, and it is not a claim that every listed environment still has a broken core flow.</p>'
        '<ol class="example-steps">'
        '<li><strong>Finding.</strong> <span>On an earlier program, take_and_close aborted with an access violation, so a taker could not finish the swap. Create and refund already completed.</span></li>'
        '<li><strong>Regression test.</strong> <span>The patch records a test that opens an escrow, runs take_and_close, and checks both token balances and that the accounts close.</span></li>'
        '<li><strong>Fork patch.</strong> <span>The fix removes an invalid println and binds the PDA seed bytes in the handler. The hosted program now completes take.</span></li>'
        f'<li><strong>Upstream PR.</strong> <span><a href="{url}">Opened upstream</a>. Recorded as submitted, not as reviewed or merged.</span></li>'
        '</ol>'
        '<p class="links-inline"><a href="/live/#gifter-escrow">View the evidence</a> · <a href="/lessons/gifter-escrow/">Read the lesson</a></p>'
        '</div></section>'
    )


def findings_html(apps):
    by = {x['slug']: x for x in apps}
    out = []
    for f in FEATURED_FINDINGS:
        x = by.get(f['slug'])
        sl = E(f['slug'])
        lesson = f'/lessons/{sl}/'
        app = E((x or {}).get('app') or f'/dapps/{f["slug"]}/')
        out.append(
            f'<article class="glass find-card">'
            f'<p class="tag">Found in the fork</p>'
            f'<h3>{E(f["title"])}</h3>'
            f'<p>{E(f["text"])}</p>'
            f'<p><a href="{lesson}">Read the lesson</a> · <a href="{app}">Open the app</a> · '
            f'<a href="{COMMIT}&amp;slug={sl}">Submit a commit suggestion</a></p>'
            f'</article>'
        )
    return '\n'.join(out)


def json_ld():
    org_id = SITE + '/#org'
    data = {
        '@context': 'https://schema.org',
        '@graph': [
            {
                '@type': 'EducationalOrganization',
                '@id': org_id,
                'name': 'Sol.College',
                'url': SITE + '/',
                'description': DESCRIPTION,
                'sameAs': ['https://github.com/Blockchains/sol-college'],
            },
            {
                '@type': 'WebSite',
                '@id': SITE + '/#website',
                'name': 'Sol.College',
                'url': SITE + '/',
                'description': DESCRIPTION,
                'publisher': {'@id': org_id},
                'inLanguage': 'en-GB',
            },
            {
                '@type': 'FAQPage',
                '@id': SITE + '/#faq',
                'url': SITE + '/#faq',
                'isPartOf': {'@id': SITE + '/#website'},
                'mainEntity': [
                    {
                        '@type': 'Question',
                        'name': q,
                        'acceptedAnswer': {'@type': 'Answer', 'text': a},
                    }
                    for q, a in FAQ
                ],
            },
        ],
    }
    return json.dumps(data, ensure_ascii=False, separators=(',', ':'))


PR_URL_RE = re.compile(
    r'https?://(?:www\.)?github\.com/([^/\s)#]+)/([^/\s)#]+)/pull/(\d+)',
    re.I,
)

def _normalise_pr(url):
    m = PR_URL_RE.search(url or '')
    if not m:
        return None
    owner, repo, num = m.group(1), m.group(2).rstrip('.git'), m.group(3)
    return f'https://github.com/{owner}/{repo}/pull/{num}', (owner.lower(), repo.lower(), num)


def _walk_pr_urls(val, into, src):
    """Collect every GitHub pull-request URL in a string, list or dict."""
    if isinstance(val, str):
        for m in PR_URL_RE.finditer(val):
            n = _normalise_pr(m.group(0))
            if n:
                into.append((n[0], n[1], src))
    elif isinstance(val, (list, tuple)):
        for i in val:
            _walk_pr_urls(i, into, src)
    elif isinstance(val, dict):
        for v in val.values():
            _walk_pr_urls(v, into, src)


def opened_fix_prs(apps=None, root=None):
    """Unique opened upstream PR URLs, computed — never invented.

    Sources (the only ones this count uses):
    - GitHub pull-request URLs inside dapps/patches/*/UPSTREAM_PR.md
    - GitHub pull-request URLs in live.json (dedicated fields, or any /pull/N URL)

    A draft UPSTREAM_PR.md with no opened PR URL does not count. Hidden when 0.
    """
    root = Path(root) if root else ROOT
    found = []
    for fp in sorted((root / 'dapps' / 'patches').glob('*/UPSTREAM_PR.md')):
        try:
            text = fp.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        rel = str(fp.relative_to(root)) if root in fp.parents or fp.is_relative_to(root) else str(fp)
        _walk_pr_urls(text, found, rel)
    for x in (apps if apps is not None else load_live()):
        _walk_pr_urls(x, found, 'live.json:' + str(x.get('slug') or ''))
    seen = set()
    out = []
    for url, key, src in found:
        if key in seen:
            continue
        seen.add(key)
        out.append({'url': url, 'source': src})
    return out


def fix_card_html(prs):
    if not prs:
        return ''
    n = len(prs)
    href = prs[0]['url'] if n == 1 else '#loop'
    label = 'verified fix opened as an upstream pull request' if n == 1 else 'verified fixes opened as upstream pull requests'
    return (
        f'<a class="glass proof-card" href="{E(href)}"><b>{n}</b>'
        f'<span>{E(label)}</span>'
        f'<small>Counted from recorded GitHub PR URLs in our evidence. The original team accepts or declines.</small></a>'
    )



# ---------- live campus hero (first section of the landing page) ----------
# Public, allowlisted view of config/projects/*.json, mirroring pilot/src/campus/projection.ts
# (a pilot test checks the two agree). Only projects approved for listing with authorised research are shown;
# examples/placeholders are excluded. The full projection is /campus/data.json, built later in CI.
CAMPUS_SECTORS = [
    ('DeFi', 'escrows, swaps, lending, payments'),
    ('DePIN', 'physical-infrastructure networks'),
    ('DeAI', 'decentralised AI'),
]
_PLACEHOLDER_RE = re.compile(r'(example|placeholder|todo|changeme|xxx|00000000-0000)', re.I)


def _is_placeholder(c: dict) -> bool:
    if c.get('placeholder') is True:
        return True
    vals = [c.get('projectId'), c.get('slug'), c.get('displayName'),
            (c.get('upstream') or {}).get('repo'), (c.get('lab') or {}).get('repo')]
    return any(isinstance(v, str) and _PLACEHOLDER_RE.search(v) for v in vals)


def _cto_live(root, c) -> str:
    """'' unless the project's CTO Mind is mapped and its autonomy status was updated in the last 6 hours (UTC ISO time)."""
    if (c.get('mind') or {}).get('mappingStatus') != 'approved':
        return ''
    f = Path(root) / 'records' / 'public' / 'status' / f"{c.get('slug')}.json"
    try:
        at = json.loads(f.read_text(encoding='utf-8')).get('updatedAt') or ''
        from datetime import datetime, timezone
        age = datetime.now(timezone.utc) - datetime.fromisoformat(at.replace('Z', '+00:00'))
        return at[:16].replace('T', ' ') + ' UTC' if age.total_seconds() < 6 * 3600 else ''
    except Exception:
        return ''


def _agent_state(root, c) -> dict:
    """CTO agent display state; mirrors pilot/src/campus/agent-state.ts (tested for agreement).
    Source of truth: config/autonomy.json, maintained by the autonomy worker (paused map/list, enabled flags)."""
    slug = c.get('slug')
    if (c.get('mind') or {}).get('mappingStatus') != 'approved':
        return {'state': 'none', 'label': '', 'note': 'No CTO agent provisioned'}
    st = _config_agent_state(root, slug)
    if st['state'] != 'active':
        return st
    # operations snapshot published by the autonomy loop: paused / not enabled / no credits => cannot produce work
    try:
        ops = json.loads((Path(root) / 'records' / 'public' / 'minds' / f'{slug}.json').read_text(encoding='utf-8'))
    except Exception:
        ops = None
    if isinstance(ops, dict):
        bal = ops.get('cognitionBalance')
        at = str(ops.get('balanceCheckedAt') or ops.get('at') or '')[:16].replace('T', ' ')
        if ops.get('paused') is True or ops.get('isEnabled') is False:
            pr = ops.get('pausedReason')
            return {'state': 'paused', 'label': 'Paused', 'note': (pr[:240] if isinstance(pr, str) and pr else '') or f"Paused ({str(ops.get('status') or '')[:60] or 'Mind not enabled'})"}
        if isinstance(bal, (int, float)) and not isinstance(bal, bool) and bal <= 0:
            return {'state': 'paused', 'label': 'No credits', 'note': f'Out of credits: HelloMinds cognition balance {bal:.2f}' + (f' (checked {at} UTC)' if at else '') + '. This agent cannot produce work until its credits are topped up.'}
    return st


def _config_agent_state(root, slug) -> dict:
    try:
        auto = json.loads((Path(root) / 'config' / 'autonomy.json').read_text(encoding='utf-8'))
    except Exception:
        auto = {}

    def s(v, n=240):
        return v[:n] if isinstance(v, str) else ''
    projects = auto.get('projects') if isinstance(auto.get('projects'), list) else []
    listed, flag, reason = False, None, ''
    for e in projects:
        if e == slug:
            listed = True
        elif isinstance(e, dict):
            if (e.get('slug') or e.get('project') or e.get('id')) != slug:
                continue
            listed = True
            if e.get('paused') is True or e.get('enabled') is False:
                flag = False
            elif e.get('enabled') is True or e.get('paused') is False:
                flag = True
            reason = s(e.get('pausedReason') or e.get('reason') or e.get('note'))
    en, pz, dz = auto.get('enabled'), auto.get('paused'), auto.get('disabled')
    if flag is None and isinstance(en, dict) and isinstance(en.get(slug), bool):
        flag = en[slug]
    if flag is None and ((isinstance(pz, list) and slug in pz) or (isinstance(dz, list) and slug in dz)):
        flag = False
    if flag is None and isinstance(pz, dict) and slug in pz:
        flag = False
        v = pz[slug]
        if not reason and isinstance(v, dict):
            st, rs = s(v.get('status'), 60), s(v.get('reason'))
            reason = s((st[:1].upper() + st[1:] + (': ' + rs if rs else '')) if st else rs)
        elif not reason:
            reason = s(v)
    if flag is False:
        return {'state': 'paused', 'label': 'Paused', 'note': reason or 'Paused in config/autonomy.json'}
    if flag is True:
        return {'state': 'active', 'label': 'Active', 'note': 'Active: scheduled autonomy runs'}
    if not listed:
        return {'state': 'paused', 'label': 'Paused', 'note': 'Paused: not in the autonomy schedule'}
    return {'state': 'active', 'label': 'Active', 'note': 'Active: scheduled autonomy runs'}

def campus_projects(root=None) -> list[dict]:
    root = Path(root) if root else ROOT
    out = []
    for f in sorted((root / 'config' / 'projects').glob('*.json')):
        try:
            c = json.loads(f.read_text(encoding='utf-8'))
        except Exception as e:  # a broken config must not break the homepage; CI config validation reports it
            print('landing: skipping unreadable project config', f.name, e)
            continue
        if _is_placeholder(c) or not (c.get('publicListing') or {}).get('approved') or not (c.get('research') or {}).get('authorised'):
            continue
        if c.get('sector') not in {s for s, _ in CAMPUS_SECTORS}:
            continue
        out.append({
            'slug': str(c['slug']),
            'displayName': str(c['displayName']),
            'sector': str(c['sector']),
            'description': str(c.get('description', '')),
            'demonstration': c.get('ownership') == 'sol-college-demonstration',
            'demonstrationNotice': str(c.get('demonstrationNotice') or ''),
            'agent': (ag := _agent_state(root, c)),
            'ctoLive': _cto_live(root, c) if ag['state'] == 'active' else '',
        })
    return out


def campus_hero_html(projects: list[dict]) -> str:
    rooms = []
    for sid, blurb in CAMPUS_SECTORS:
        # active CTO agents first; paused agents are listed dimmed with an explicit 'Paused' state
        ps = sorted((p for p in projects if p['sector'] == sid), key=lambda p: (p.get('agent') or {}).get('state') == 'paused')
        items = ''.join(
            f'<li><button type="button" class="ch-avatar{" is-paused" if (p.get("agent") or {}).get("state") == "paused" else ""}" data-slug="{E(p["slug"])}" aria-haspopup="dialog">'
            f'<span class="ch-dot" aria-hidden="true"></span><span class="ch-name">{E(re.sub(r"\s*\(.*\)$", "", p["displayName"]))}</span>'
            + (('<span class="ch-state" title="' + E(p['agent']['note']) + '">' + E(p['agent'].get('label') or 'Paused') + '</span>') if (p.get('agent') or {}).get('state') == 'paused'
               else ('<span class="ch-demo" title="CTO Mind live: last autonomous pass ' + E(p['ctoLive']) + ' (Sol.College demonstration lab)">CTO live</span>') if p.get('ctoLive')
               else ('<span class="ch-demo">Demo</span>' if p['demonstration'] else '')) +
            '</button></li>' for p in ps)
        body = f'<ul class="ch-list">{items}</ul>' if ps else '<p class="ch-empty">No projects yet</p>'
        rooms.append(
            f'<li class="ch-room ch-{sid.lower()}"><h3>{E(sid)} room</h3><p class="ch-blurb">{E(blurb)}</p>{body}</li>')
    n_act = sum(1 for p in projects if (p.get('agent') or {}).get('state') == 'active')
    n_pau = sum(1 for p in projects if (p.get('agent') or {}).get('state') == 'paused')
    n_demo = sum(1 for p in projects if p.get('demonstration'))
    active_line = (
        f'{len(projects)} campus projects · {n_act} active CTO agent{"" if n_act == 1 else "s"}'
        + (f' · {n_pau} paused' if n_pau else '')
        + (f' · {n_demo} demonstration forks' if n_demo else '')
    )
    data = json.dumps(projects, ensure_ascii=False).replace('<', '\\u003c')
    return (
        '<section class="campus-hero" id="campus-hero" aria-labelledby="ch-title">\n'
        '  <div class="ch-head">\n'
        f'    <div><p class="eyebrow ch-live"><span class="live-dot" aria-hidden="true"></span><span class="ch-live-pre">Campus · </span>{E(active_line)}</p>'
        '<p class="ch-blurb">Campus projects are mostly independent demonstration forks with optional CTO automation. '
        '“Active” and “Paused” describe the agent, not whether the practice app can be opened. '
        'Practice environments on the homepage are a separate count from this campus roster.</p>'
        f'<h2 id="ch-title">Sol.College campus</h2></div>\n'
        '    <a class="btn ghost ch-explore" href="/campus/">Explore campus</a>\n'
        '  </div>\n'
        '  <div class="ch-stage" id="ch-stage" data-mode="2d">\n'
        '    <div class="ch-poster" aria-hidden="true"><span class="ch-shelf"></span><span class="ch-table"></span><span class="ch-load">Loading the live 3D campus…</span></div>\n'
        f'    <ul class="ch-rooms" aria-label="Campus rooms">{"".join(rooms)}</ul>\n'
        '  </div>\n'
        '  <dialog class="ch-dialog" id="ch-dialog" aria-labelledby="ch-dialog-title"><div id="ch-dialog-body"></div>'
        '<form method="dialog"><button class="btn ch-close" value="close">Close</button></form></dialog>\n'
        f'  <script type="application/json" id="ch-data">{data}</script>\n'
        '</section>'
    )


def write_home(site='site'):
    site = Path(site)
    site.mkdir(parents=True, exist_ok=True)
    apps = load_live()
    functional = [x for x in apps if is_fully_functional(x)]
    bugs = explicit_bugs(apps)
    fix_prs = opened_fix_prs(apps)
    ownership = ownership_by_slug()
    submitted = pr_slugs(fix_prs)
    try:
        sec_findings = _findings.load()
    except SystemExit:
        raise
    except Exception as e:  # a broken record must not take the homepage down
        print('landing: findings unavailable', type(e).__name__, e)
        sec_findings = []
    tpl = (HERE / 'landing.html').read_text(encoding='utf-8')
    bug_note = (
        f'{len(bugs)} issues are labelled as bugs in our devnet evidence for the practice forks '
        f'(explicit “Bug:” / “BUG:” records in the deployment notes, counted uniquely). '
        f'This is not a formal audit and not a claim about any project’s production system. '
    )
    if fix_prs:
        bug_note += (
            f'{len(fix_prs)} verified fix{"es" if len(fix_prs) != 1 else ""} '
            f'{"have" if len(fix_prs) != 1 else "has"} been opened as upstream pull requests, '
            f'counted from recorded GitHub PR URLs.'
        )
    else:
        bug_note += (
            'A count of verified fixes opened as upstream pull requests appears when recorded '
            'GitHub PR URLs exist. Static-host build patches are not counted.'
        )
    tokens = {
        'TITLE': E(TITLE),
        'DESCRIPTION': E(DESCRIPTION),
        'CAMPUS_HERO': campus_hero_html(campus_projects()),
        'JSON_LD': json_ld(),  # raw JSON inside a script tag; no HTML escaping
        'LIVE_COUNT': str(len(functional)),
        'LESSON_COUNT': str(len(apps)),
        'LESSON_BREAKDOWN': (
            f'{len(functional)} guided-ready environments and '
            f'{len(apps) - len(functional)} debug or preview activities in the live inventory'
        ),
        'BUG_COUNT': str(len(bugs)),
        'FIX_CARD': fix_card_html(fix_prs) + _findings.proof_card(sec_findings),
        'BUG_NOTE': E(bug_note).replace('“', '“').replace('”', '”'),  # keep unicode
        'RESULTS': results_html(bugs, fix_prs, sec_findings),
        'FEATURED': featured_html(functional, ownership, submitted),
        'EXAMPLE': example_html(fix_prs),
        'LIVE_CARDS': live_cards(functional, ownership, submitted),
        'ORBIT': orbit_html(functional),
        'MARQUEE': marquee_html(functional),
        'FINDINGS': _findings.landing_cards(sec_findings) + findings_html(apps),
        'START_LESSON': START_LESSON,
        'START_SECTION': _learning_layer_start(),
        'WAITLIST': WAITLIST,
        'WAITLIST_DEV': WAITLIST_DEV,
        'WAITLIST_SEC': WAITLIST_SEC,
        'WAITLIST_HUNT': WAITLIST_HUNT,
        'PROJECT': PROJECT,
        'COMMIT': COMMIT,
        'ICO_CONTEXT': ICO['CONTEXT'],
        'ICO_TEST': ICO['TEST'],
        'ICO_INVESTIGATE': ICO['INVESTIGATE'],
        'ICO_CONTRIBUTE': ICO['CONTRIBUTE'],
        'ICO_DEV': ICO['DEV'],
        'ICO_SEC': ICO['SEC'],
        'ICO_HUNT': ICO['HUNT'],
        'ICO_FORK': ICO['FORK'],
        'ICO_SCOPE': ICO['SCOPE'],
        'ICO_COMMIT': ICO['COMMIT'],
        'ICO_LOOP': ICO['LOOP'],
        'ICO_X': ICO['X'],
        'RELEASE_FOOTER': '',  # filled after release artifacts are written
    }
    rel = _release.write_artifacts(site, ROOT)
    tokens['RELEASE_FOOTER'] = _release.footer_html(rel)
    page = tpl
    # Replace longer tokens first so WAITLIST is not replaced inside WAITLIST_DEV, etc.
    for k in sorted(tokens, key=lambda s: -len(s)):
        page = page.replace('{{' + k + '}}', str(tokens[k]))
    leftover = re.findall(r'\{\{[A-Z0-9_]+\}\}', page)
    if leftover:
        raise SystemExit('unreplaced landing placeholders: ' + ', '.join(sorted(set(leftover))))
    page = _release.inject_into_html(page, rel)
    (site / 'index.html').write_text(page, encoding='utf-8')
    assets = site / 'assets'
    assets.mkdir(exist_ok=True)
    shutil.copy(HERE / 'landing.css', assets / 'landing.css')
    shutil.copy(HERE / 'landing.js', assets / 'landing.js')
    shutil.copy(HERE / 'landing-campus.js', assets / 'landing-campus.js')
    shutil.copy(HERE / 'landing-bg.js', assets / 'landing-bg.js')
    shutil.copy(HERE / 'landing-film.js', assets / 'landing-film.js')
    shutil.copy(HERE / 'hero-wide.jpg', assets / 'hero-wide.jpg')
    shutil.copy(HERE / 'hero-tall.jpg', assets / 'hero-tall.jpg')
    for name in (
        'hero-talk-wide-a.jpg', 'hero-talk-wide-b.jpg', 'hero-talk-wide-c.jpg',
        'hero-talk-tall-a.jpg', 'hero-talk-tall-b.jpg', 'hero-talk-tall-c.jpg',
    ):
        shutil.copy(HERE / name, assets / name)
    marks = HERE / 'marks'
    if marks.is_dir():
        dest = assets / 'marks'
        dest.mkdir(exist_ok=True)
        for img in marks.glob('*.jpg'):
            shutil.copy(img, dest / img.name)
    _findings.write_pages(site, page_shell(site), sec_findings)
    print(
        'landing: wrote', site / 'index.html',
        'functional=', len(functional),
        'deployed=', len(apps),
        'bugs=', len(bugs),
        'fix_prs=', len(fix_prs),
        'excluded=', [x['slug'] for x in apps if not is_fully_functional(x)],
    )
    return site / 'index.html'


COMMIT_BLOCK = '''<!--sc-commit-->
<section class="note" id="commit-suggestion">
<h2>Turn a finding into a commit suggestion</h2>
<p>Every lesson should produce evidence of understanding. Suitable investigations can develop into tests, patches, or a pull request against the <a href="{fork}">practice fork</a>, with a regression test and the devnet transaction that proves it. Verified fixes may be opened as pull requests to the original project, for the team to accept or decline.</p>
<p><a class="btn" href="{url}">Submit a commit suggestion</a></p>
</section>
<!--/sc-commit-->'''


def enrich_lessons(site='site'):
    """Idempotently add a commit-suggestion CTA to each live-app lesson page."""
    site = Path(site)
    apps = {x['slug']: x for x in load_live()}
    n = 0
    for sl, x in apps.items():
        for folder in ('lessons', 'explore'):
            fp = site / folder / sl / 'index.html'
            if not fp.exists():
                continue
            t = fp.read_text(encoding='utf-8', errors='replace')
            block = COMMIT_BLOCK.format(
                fork=E(x.get('fork') or 'https://github.com/Blockchains/' + sl),
                url=E(COMMIT + '&slug=' + sl),
            )
            if 'template=commit-suggestion.yml' in t and '<!--sc-commit-->' not in t:
                # Lesson already has a commit-suggestion CTA (e.g. a worked example).
                n += 1
                continue
            if '<!--sc-commit-->' in t:
                t = re.sub(r'<!--sc-commit-->.*?<!--/sc-commit-->', block, t, count=1, flags=re.S)
            elif '</article>' in t:
                t = t.replace('</article>', block + '</article>', 1)
            else:
                t = t.replace('</main>', block + '</main>', 1)
            fp.write_text(t, encoding='utf-8')
            n += 1
    print('landing: enriched', n, 'lesson pages with commit-suggestion CTA')
    return n


def is_landing(text: str) -> bool:
    return 'data-landing="sol-college-v2"' in text


def page_shell(site='site') -> str:
    """Return an inner-page HTML shell that is NOT the pivoted landing.

    Lesson pages and /live/ wrap their body in this chrome. After the first
    deploy, site/index.html is the new landing and must not be used as a shell.
    """
    site = Path(site)
    cands = [
        site / 'index.html',
        site / 'live' / 'index.html',
        site / 'lessons' / 'index.html',
        site / 'lessons' / 'path' / 'index.html',
        site / 'how-to-build' / 'index.html',
        site / 'explore' / 'index.html',
        site / 'faq' / 'index.html',
    ]
    for p in cands:
        if not p.exists():
            continue
        text = p.read_text(encoding='utf-8', errors='replace')
        if is_landing(text):
            continue
        if '<main id=main>' in text or '<main id="main">' in text:
            return text
    return ''


if __name__ == '__main__':
    dest = sys.argv[1] if len(sys.argv) > 1 else 'site'
    write_home(dest)
