"""Generate the pivoted Sol.College homepage from scripts/landing.html + dapps/live.json.

Usage: python3 scripts/landing.py [site_dir]

CI must call this after lesson pages are generated (end of core_lessons.py) so
this file replaces site/index.html and is not used as the lesson-page shell.

Honesty rules:
- Live environment cards list ONLY apps whose core flows completed on devnet.
  live.json has no `status` field today; when one is present ('fully working'
  and synonyms) it wins. Otherwise a documented exclusion list is used.
- Counts are computed, never invented. Fix-commit metrics are omitted until
  real suggested-commit patches exist (static-host build patches do not count).
- Practice environments are open-source dApps redeployed on devnet — not
  evidence that original teams are participating partners.
"""
from __future__ import annotations
import html, json, os, re, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SITE = 'https://sol.college'
E = lambda s: html.escape(str(s), quote=True)

WAITLIST = 'https://github.com/Blockchains/sol-college/issues/new?template=learner-waitlist.yml'
WAITLIST_DEV = WAITLIST + '&role=Developer'
WAITLIST_SEC = WAITLIST + '&role=Security+researcher'
WAITLIST_HUNT = WAITLIST + '&role=Bug+bounty+hunter'
PROJECT = 'https://github.com/Blockchains/sol-college/issues/new?template=project-partnership.yml'
COMMIT = 'https://github.com/Blockchains/sol-college/issues/new?template=commit-suggestion.yml'

TITLE = 'Sol.College — Learn on real Solana dApps. Help make them better.'
DESCRIPTION = (
    'Build your development and security skills inside live, hands-on environments '
    'based on participating Solana projects. Explore how real applications work, '
    'test their limits, discover issues and turn your findings into useful improvements.'
)

# Core-flow failures documented in dapps/live.json limits / negative (2026-11-13).
# These are excluded from the "fully working" list. Reasons are for operators;
# featured findings on the page are a subset, quoted from the same evidence.
CORE_BROKEN = {
    'gifter-escrow': 'take_and_close aborts with an access violation; a swap cannot complete',
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
        text='The program’s reject_grant_milestone entry point calls accept_milestone, so “rejecting” a milestone in review accepts it, and the sponsor can then be asked to pay it.',
    ),
    dict(
        slug='gifter-escrow',
        title='Gifter escrow: take_and_close aborts',
        text='take_and_close aborts with an access violation, so a taker can never complete the swap. The handler’s first statement is a println in the take path. Create and refund work.',
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
     'An interactive, isolated environment based on a participating project’s application or codebase—not simply a screenshot, video or static code example. The exact components, network, dependencies and available features are specified for each environment. A fork may differ from the production application, and findings may need further validation by the project team.'),
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


def lesson_functional(slug):
    """Read dapps/lessons/<slug>.json 'functional' if present."""
    fp = ROOT / 'dapps' / 'lessons' / f'{slug}.json'
    if not fp.exists():
        return None
    try:
        return json.loads(fp.read_text(encoding='utf-8')).get('functional')
    except Exception:
        return None


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


def first_sentence(text, n=150):
    t = ' '.join(str(text or '').split())
    if not t:
        return ''
    m = re.match(r'(.{1,' + str(n) + r'}?(?:\.(?=\s)|$))', t)
    s = (m.group(1) if m else t[:n]).strip()
    if len(t) > len(s):
        if not s.endswith('.'):
            s = s.rstrip('.,;:') + '…'
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


def live_cards(apps):
    out = []
    for x in apps:
        sl = E(x['slug'])
        name = E(display_name(x))
        learn = E(first_sentence(x.get('learn') or ''))
        verified = E(fmt_date(x.get('verified') or ''))
        out.append(
            f'<article class="glass card" data-slug="{sl}">'
            f'<p class="meta"><span class="live-dot" aria-hidden="true"></span>Verified on devnet {verified}</p>'
            f'<h3><a href="/dapps/{sl}/">{name}</a></h3>'
            f'<p>{learn}</p>'
            f'<p class="links"><a href="/dapps/{sl}/">Open the app</a>'
            f'<a href="/lessons/{sl}/">Take the lesson</a></p>'
            f'</article>'
        )
    return '\n'.join(out)


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


def write_home(site='site'):
    site = Path(site)
    site.mkdir(parents=True, exist_ok=True)
    apps = load_live()
    functional = [x for x in apps if is_fully_functional(x)]
    bugs = explicit_bugs(apps)
    fix_prs = opened_fix_prs(apps)
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
        'JSON_LD': json_ld(),  # raw JSON inside a script tag; no HTML escaping
        'LIVE_COUNT': str(len(functional)),
        'LESSON_COUNT': str(len(apps)),
        'BUG_COUNT': str(len(bugs)),
        'FIX_CARD': fix_card_html(fix_prs),
        'BUG_NOTE': E(bug_note).replace('“', '“').replace('”', '”'),  # keep unicode
        'LIVE_CARDS': live_cards(functional),
        'FINDINGS': findings_html(apps),
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
    }
    page = tpl
    # Replace longer tokens first so WAITLIST is not replaced inside WAITLIST_DEV, etc.
    for k in sorted(tokens, key=lambda s: -len(s)):
        page = page.replace('{{' + k + '}}', str(tokens[k]))
    leftover = re.findall(r'\{\{[A-Z0-9_]+\}\}', page)
    if leftover:
        raise SystemExit('unreplaced landing placeholders: ' + ', '.join(sorted(set(leftover))))
    (site / 'index.html').write_text(page, encoding='utf-8')
    assets = site / 'assets'
    assets.mkdir(exist_ok=True)
    shutil.copy(HERE / 'landing.css', assets / 'landing.css')
    shutil.copy(HERE / 'landing.js', assets / 'landing.js')
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
<p>Lessons and findings on this practice fork are meant to end in something the repository can take: a patch or pull request against the <a href="{fork}">practice fork</a>, with a regression test and the devnet transaction that proves it. Verified fixes are pushed to the working fork and opened as pull requests to the original project, for the team to accept or decline.</p>
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
