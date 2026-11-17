"""Sitewide SEO pass. Runs after page generators, and again after the campus copy.

Honest limits: titles and descriptions already on the page are kept and only
shortened. Nothing here adds a partnership, a credential, a peer review, an
ISSN, a DOI, or a search box the site does not have. /dapps/ and /legacy/ are
left alone. Lesson copies under /explore/ stay noindex because their canonical
is the /lessons/ page. /auth, /standard/ and the 404 stay out of the sitemap.

Hydrated legacy pages (the solar-programme app) only get head tags. Inserting
links into their body breaks client hydration.
"""
from __future__ import annotations
import datetime, glob, html, json, os, re, sys

SITE = 'https://sol.college'
ORG = SITE + '/#org'
TODAY = datetime.date.today().isoformat()
MAP_DESC = 'Every public Sol.College page: lessons, the calendar, articles, the library, the journal, The Degen, and the source library.'
STYLE = '<style id=sc-seo>.seo-sections{margin:12px 0 0;font-size:14px;line-height:1.7}.seo-sections a{white-space:nowrap}nav.crumbs{font-size:13px;margin:0 0 12px}body:has(.dock-pin) footer{padding-bottom:96px}@media(max-width:700px){body:has(.dock-pin) footer{padding-bottom:220px}}</style>'
SKIP_DIRS = {'dapps', 'legacy', 'node_modules', '.git'}
LABELS = {
    'lessons': 'Lessons', 'events': 'Events', 'articles': 'Articles', 'library': 'Library', 'journal': 'Journal',
    'cities': 'Cities', 'countries': 'Countries', 'archive': 'Archive', 'submit': 'Submit',
    'queue': 'Queue', 'coverage': 'Coverage', 'sources': 'Sources', 'college': 'Sol.College',
    'series': 'Series', 'london': 'London', 'dubai': 'Dubai', 'belgrade': 'Belgrade',
    'melbourne': 'Melbourne', 'narashino': 'Narashino', 'abu-dhabi': 'Abu Dhabi',
    'berlin': 'Berlin', 'sharjah': 'Sharjah', 'united-kingdom': 'United Kingdom',
    'united-arab-emirates': 'United Arab Emirates', 'serbia': 'Serbia', 'australia': 'Australia',
    'japan': 'Japan', 'germany': 'Germany', 'canada': 'Canada',
    'degen': 'The Degen', 'campus': 'Campus', 'live': 'Live apps', 'how-to-build': 'How to build',
    'explore': 'Source library', 'findings': 'Findings', 'faq': 'FAQ', 'glossary': 'Glossary',
    'topics': 'Topics', 'learn-solana': 'Learn Solana', 'learn-by-example': 'Concept walkthroughs',
    'what-to-build': 'What to build', 'legal': 'Legal', 'new': 'New', 'edge-ai': 'Edge AI',
    'map': 'All pages', 'path': 'Learning path', 'guide': 'How to use a lesson', 'guides': 'Guides',
    'papers': 'White papers', 'readings': 'Readings',
    'methods': 'Methods', 'policy': 'Policy', 'protocols': 'Protocols', 'sketches': 'Sketches',
    'programme': 'Programme', 'policies': 'Policies', 'desks': 'Desks', 'assignments': 'Assignment board',
    'charter': 'Charter', 'editorial': 'Editorial', 'corrections': 'Corrections', 'letters': 'Letters',
    'tips': 'Tips', 'noticeboard': 'Noticeboard', 'templates': 'Templates', 'style': 'Style book',
    'terms': 'Terms', 'privacy': 'Privacy', 'about': 'About', 'contact': 'Contact', 'apply': 'Apply',
    'calculator': 'Calculator', 'learn': 'Learn', 'resources': 'Resources', 'network': 'Network',
    'for-teams': 'For teams',
}
SECTIONS = [
    ('/', 'Home'), ('/lessons/', 'Lessons'), ('/events/', 'Events'), ('/articles/', 'Articles'), ('/library/', 'Library'),
    ('/journal/', 'Journal'), ('/degen/', 'The Degen'), ('/campus/', 'Campus'), ('/live/', 'Live apps'),
    ('/how-to-build/', 'How to build'), ('/explore/', 'Source library'), ('/findings/', 'Findings'),
    ('/faq/', 'FAQ'), ('/map/', 'All pages'),
]
ORDER = ['Home', 'Lessons', 'Events', 'Articles', 'Library', 'Journal', 'The Degen', 'Campus', 'Live apps',
         'How to build', 'Findings', 'FAQ', 'Glossary', 'Topics', 'Learn Solana', 'Concept walkthroughs',
         'What to build', 'Legal', 'New', 'Edge AI', 'Source library', 'Other']
PAGE_TYPES = r'WebPage|Article|TechArticle|ScholarlyArticle|FAQPage|Course|CollectionPage|LearningResource|SoftwareSourceCode|DefinedTermSet'


def esc(s):
    return html.escape(str(s), quote=True)


def fit(s, n=158):
    """Shorten a meta description. Keep a closing sentence that states a limit.

    Whole sentences are dropped from the end of the lead until the line fits.
    A limit sentence is never sliced in half, and a one-word fragment is never
    glued to it. The returned string also fits after HTML-attribute escaping, so
    raw meta content never exceeds n characters in the file.
    """
    s = ' '.join((s or '').split())

    def ok(candidate):
        return len(candidate) <= n and len(esc(candidate)) <= n

    if ok(s):
        return s
    parts = re.split(r'(?<=[.!?])\s+', s)
    if len(parts) >= 2:
        tail = parts[-1]
        if re.search(r'\b(not|no|never|without)\b', tail, re.I) and ok(tail):
            head_parts = parts[:-1]
            while head_parts:
                head = ' '.join(head_parts)
                candidate = f'{head} {tail}'
                if ok(candidate):
                    return candidate
                head_parts.pop()
            return tail
    # Shrink until both plain and escaped forms fit.
    cut = s
    for _ in range(48):
        if ok(cut):
            return cut
        expansion = len(esc(cut)) - len(cut)
        budget = n - max(0, expansion) - 1
        if budget < 20:
            budget = 20
        nxt = cut[:budget].rsplit(' ', 1)[0].rstrip(',;:.')
        if not nxt or nxt == cut.rstrip('…'):
            nxt = cut[:budget].rstrip(',;:.…')
        cut = (nxt or cut[:20]).rstrip(',;:.') + '…'
    return cut[:n]


def short_title(title):
    t = re.sub(r'\s*\|.*$', '', title or '').strip()
    t = re.sub(r':\s*step-by-step Solana lesson, live on devnet$', '', t).strip()
    return t or 'Sol.College'


def _key_pat(key):
    return r'(?:name|property)=["\']?' + re.escape(key) + r'["\']?(?=[\s>/])'


def has_meta(text, key):
    return re.search(r'<meta\b[^>]*?' + _key_pat(key), text, re.I) is not None


def set_meta_content(text, key, value):
    pat = re.compile(r'(<meta\b[^>]*?' + _key_pat(key) + r'[^>]*?\bcontent=")([^"]*)"', re.I)
    def repl(m):
        if html.unescape(m.group(2)) == value:
            return m.group(0)
        return m.group(1) + esc(value) + '"'
    if pat.search(text):
        return pat.sub(repl, text, count=1)
    return text


def ensure_meta(text, kind, key, value):
    if has_meta(text, key):
        return set_meta_content(text, key, value)
    return text.replace('</head>', f'<meta {kind}="{key}" content="{esc(value)}"></head>', 1)


def extract_title(text):
    m = re.search(r'<title>(.*?)</title>', text, re.S | re.I)
    if not m:
        return ''
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).split())


def extract_desc(text):
    m = re.search(r'<meta\b[^>]*?' + _key_pat('description') + r'[^>]*?\bcontent="([^"]*)"', text, re.I)
    return html.unescape(m.group(1)) if m else ''


def extract_h1(text):
    m = re.search(r'<h1\b[^>]*>(.*?)</h1>', text, re.S | re.I)
    if not m:
        return ''
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).split())


def set_titles(text, title):
    text = re.sub(r'<title>.*?</title>', lambda _: f'<title>{esc(title)}</title>', text, count=1, flags=re.S)
    for key in ('og:title', 'twitter:title'):
        text = set_meta_content(text, key, title)
    return text


def canonical_of(text):
    m = re.search(r'<link\b[^>]*rel=["\']?canonical["\']?[^>]*>', text, re.I)
    if not m:
        return ''
    h = re.search(r'href=["\']([^"\']+)["\']', m.group(0), re.I)
    return h.group(1) if h else ''


def norm_url(u):
    u = (u or '').split('#')[0].split('?')[0].strip()
    u = u.replace('http://sol.college', SITE)
    if u == SITE:
        return SITE + '/'
    if u.startswith(SITE + '/') and not u.endswith('/') and not re.search(r'\.[a-z0-9]{1,5}$', u, re.I):
        u += '/'
    return u


def has_noindex(text):
    for m in re.finditer(r'<meta\b[^>]*>', text, re.I):
        tag = m.group(0)
        if re.search(r'\brobots\b', tag, re.I) and re.search(r'noindex', tag, re.I):
            return True
    return False


def has_robots(text):
    return re.search(r'<meta\b[^>]*\brobots\b', text, re.I) is not None


def is_spa(text):
    return '$_TSR' in text or 'data-precedence=' in text or '__TSR' in text


def is_mirror(path, text):
    m = re.fullmatch(r'/explore/([^/]+)/', path or '')
    if not m:
        return False
    return f'/lessons/{m.group(1)}/' in (canonical_of(text) or '')


def url_path(site, fp):
    rel = os.path.relpath(fp, site).replace(os.sep, '/')
    if rel == 'index.html':
        return '/', rel
    if rel.endswith('/index.html'):
        return '/' + rel[:-len('index.html')], rel
    return None, rel


def force_noindex(text):
    def repl(m):
        tag = m.group(0)
        if re.search(r'\brobots\b', tag, re.I) and not re.search(r'noindex', tag, re.I):
            return ''
        return tag
    text = re.sub(r'<meta\b[^>]*>', repl, text, flags=re.I)
    if not has_noindex(text) and '</head>' in text:
        text = text.replace('</head>', '<meta name=robots content="noindex,follow"></head>', 1)
    return text


def fit_descriptions(text):
    keys = ('description', 'og:description', 'twitter:description')
    trimmed = False
    for key in keys:
        pat = re.compile(r'(<meta\b[^>]*?' + _key_pat(key) + r'[^>]*?\bcontent=")([^"]*)"', re.I)
        def repl(m, _key=key):
            nonlocal trimmed
            raw = html.unescape(m.group(2))
            fitted = fit(raw, 158)
            if fitted == raw:
                return m.group(0)
            trimmed = True
            return m.group(1) + esc(fitted) + '"'
        text = pat.sub(repl, text)
    return text, trimmed


def breadcrumb_items(path, name):
    parts = [p for p in path.strip('/').split('/') if p]
    items = [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'}]
    acc = ''
    for i, part in enumerate(parts):
        acc += '/' + part
        url = SITE + acc + '/'
        label = name if i == len(parts) - 1 else (LABELS.get(part) or part.replace('-', ' '))
        items.append({'@type': 'ListItem', 'position': len(items) + 1, 'name': label, 'item': url})
    return items


def visible_crumbs(path, title):
    parts = [p for p in path.strip('/').split('/') if p]
    bits = ['<a href="/">Home</a>']
    acc = ''
    for i, part in enumerate(parts):
        acc += '/' + part + '/'
        if i == len(parts) - 1:
            bits.append(f'<span>{esc(short_title(title))}</span>')
        else:
            bits.append(f'<a href="{esc(acc)}">{esc(LABELS.get(part) or part.replace("-", " "))}</a>')
    return '<!--sc-seo-crumbs--><nav class=crumbs aria-label=Breadcrumb>' + ' / '.join(bits) + '</nav><!--/sc-seo-crumbs-->'


def ld_block(text, path, title, desc, url):
    if path == '/':
        return text
    outside = re.sub(r'<!--sc-seo-->.*?<!--/sc-seo-->', '', text, flags=re.S)
    if 'BreadcrumbList' in outside and '<!--sc-seo-->' not in text:
        return text
    name = short_title(title)
    nodes = []
    has_type = re.search(r'"@type"\s*:\s*"(?:' + PAGE_TYPES + r')"', outside) is not None
    if not has_type:
        nodes.append({
            '@type': 'WebPage', '@id': url + '#webpage', 'url': url, 'name': name,
            'description': desc, 'isPartOf': {'@id': SITE + '/#website'},
            'publisher': {'@id': ORG}, 'inLanguage': 'en-GB',
            'breadcrumb': {'@id': url + '#breadcrumb'},
        })
    nodes.append({'@type': 'BreadcrumbList', '@id': url + '#breadcrumb', 'itemListElement': breadcrumb_items(path, name)})
    lesson = path.startswith('/lessons/') and path.count('/') >= 3 and path not in (
        '/lessons/', '/lessons/path/', '/lessons/glossary/', '/lessons/guide/')
    if lesson and 'LearningResource' not in outside:
        nodes.append({
            '@type': 'LearningResource', '@id': url + '#lesson', 'url': url, 'name': name,
            'description': desc, 'isAccessibleForFree': True, 'inLanguage': 'en-GB',
            'learningResourceType': 'lesson', 'provider': {'@id': ORG},
        })
    blob = json.dumps({'@context': 'https://schema.org', '@graph': nodes}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    block = '<!--sc-seo--><script type="application/ld+json">' + blob + '</script><!--/sc-seo-->'
    if '<!--sc-seo-->' in text:
        return re.sub(r'<!--sc-seo-->.*?<!--/sc-seo-->', lambda _: block, text, count=1, flags=re.S)
    return text.replace('</head>', block + '</head>', 1)


def sections_html(links=None):
    parts = ' · '.join(f'<a href="{h}">{esc(n)}</a>' for h, n in (links or SECTIONS))
    return '<!--sc-seo-nav--><nav class=seo-sections aria-label=Sections>' + parts + '</nav><!--/sc-seo-nav-->'


def ensure_nav(text, nav_html):
    if '<!--sc-seo-nav-->' in text:
        return re.sub(r'<!--sc-seo-nav-->.*?<!--/sc-seo-nav-->', lambda _: nav_html, text, count=1, flags=re.S)
    fm = re.search(r'<footer\b.*?</footer>', text, re.S | re.I)
    footer = fm.group(0) if fm else ''
    # Only the footer's own links count. The header already links to these sections.
    if 'href="/journal/"' in footer and 'href="/lessons/"' in footer:
        if 'href="/map/"' not in footer:
            new_footer = re.sub(
                r'(<nav\b[^>]*>)(.*?)(</nav>)',
                lambda m: m.group(1) + m.group(2) + '<a href="/map/">All pages</a>' + m.group(3),
                footer, count=1, flags=re.S)
            if new_footer == footer:
                new_footer = footer.replace('</footer>', '<p><a href="/map/">All pages</a></p></footer>', 1)
            return text.replace(footer, new_footer, 1)
        return text
    if footer:
        return text.replace(footer, footer.replace('</footer>', nav_html + '</footer>', 1), 1)
    if '</body>' in text:
        return text.replace('</body>', '<footer>' + nav_html + '</footer></body>', 1)
    return text


def ensure_style(text):
    if 'id=sc-seo' in text or 'id="sc-seo"' in text:
        return re.sub(r'<style id=["\']?sc-seo["\']?>.*?</style>', STYLE, text, count=1, flags=re.S)
    return text.replace('</head>', STYLE + '</head>', 1)


def fix_alt(text, title):
    def repl(m):
        cur = html.unescape(m.group(2))
        if 'Sol.College: Sol.College' in cur or 'learn Solana development from real code' in cur:
            return m.group(1) + esc(fit(title, 120)) + '"'
        return m.group(0)
    return re.sub(r'(<meta\b[^>]*?property=["\']?og:image:alt["\']?[^>]*?\bcontent=")([^"]*)"', repl, text, count=1, flags=re.I)


def clear_noindex(text):
    def repl(m):
        tag = m.group(0)
        if re.search(r'\brobots\b', tag, re.I) and re.search(r'noindex', tag, re.I):
            return ''
        return tag
    return re.sub(r'<meta\b[^>]*>', repl, text, flags=re.I)


def should_hide(path, rel, title, desc, text):
    if path is None or rel == '404.html':
        return True
    if path.startswith('/standard') or path.startswith('/auth'):
        return True
    if title.strip().lower() == 'shell' or (desc or '').strip().lower() == 'shell':
        return True
    if is_mirror(path, text):
        return True
    # A noindex tag counts when this file is already its own canonical URL.
    # A noindex copied from another page, beside that page's canonical, is stale.
    canon = canonical_of(text)
    url = norm_url(SITE + path) if path else ''
    if has_noindex(text) and (not canon or norm_url(canon) == url):
        return True
    return False


def patch(text, path, rel, nav_html=None, title_override=None, desc_override=None):
    """Return (html, info). info['indexable'] is true only for sitemap URLs."""
    info = {'indexable': False, 'title': '', 'trimmed': False, 'path': path}
    if '</head>' not in text or '</body>' not in text:
        return text, info
    nav_html = nav_html or sections_html()
    if title_override:
        text = set_titles(text, title_override)
    if desc_override:
        for key, kind in (('description', 'name'), ('og:description', 'property'), ('twitter:description', 'name')):
            text = ensure_meta(text, kind, key, desc_override)
    title = extract_title(text)
    if path == '/explore/':
        h1 = extract_h1(text)
        if h1.lower().startswith('source library') and not title.lower().startswith('source library'):
            title = 'Source library (not yet live) | Sol.College'
            text = set_titles(text, title)
    desc = extract_desc(text)
    info['title'] = title
    if should_hide(path, rel, title, desc, text):
        return force_noindex(text), info
    if has_noindex(text):
        text = clear_noindex(text)
    text, info['trimmed'] = fit_descriptions(text)
    desc = extract_desc(text) or desc
    if not desc and title:
        desc = fit(short_title(title) + ' on Sol.College.', 158)
        text = ensure_meta(text, 'name', 'description', desc)
    url = SITE + path
    canon = canonical_of(text)
    if canon and norm_url(canon) != url:
        text = re.sub(r'(<link\b[^>]*rel=["\']?canonical["\']?[^>]*href=")[^"]*"',
                      lambda m: m.group(1) + esc(url) + '"', text, count=1, flags=re.I)
    elif not canon:
        text = text.replace('</head>', f'<link rel=canonical href="{esc(url)}"></head>', 1)
    text = ensure_meta(text, 'property', 'og:url', url)
    if not has_robots(text):
        text = text.replace('</head>', '<meta name=robots content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"></head>', 1)
    if not has_meta(text, 'og:type'):
        kind = 'article' if path.count('/') > 2 else 'website'
        text = ensure_meta(text, 'property', 'og:type', kind)
    if not has_meta(text, 'og:title'):
        text = ensure_meta(text, 'property', 'og:title', title or 'Sol.College')
    if not has_meta(text, 'og:description'):
        text = ensure_meta(text, 'property', 'og:description', desc or title or 'Sol.College')
    if not has_meta(text, 'og:site_name'):
        text = ensure_meta(text, 'property', 'og:site_name', 'Sol.College')
    if not has_meta(text, 'og:locale'):
        text = ensure_meta(text, 'property', 'og:locale', 'en_GB')
    if not has_meta(text, 'og:image'):
        text = text.replace('</head>', f'<meta property="og:image" content="{SITE}/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"></head>', 1)
    if not has_meta(text, 'og:image:alt'):
        text = ensure_meta(text, 'property', 'og:image:alt', fit(title or 'Sol.College', 120))
    else:
        text = fix_alt(text, title or 'Sol.College')
    if not has_meta(text, 'twitter:card'):
        text = ensure_meta(text, 'name', 'twitter:card', 'summary_large_image')
    if not has_meta(text, 'twitter:title'):
        text = ensure_meta(text, 'name', 'twitter:title', title or 'Sol.College')
    if not has_meta(text, 'twitter:description'):
        text = ensure_meta(text, 'name', 'twitter:description', desc or title or 'Sol.College')
    if not has_meta(text, 'twitter:image'):
        image = SITE + '/og.png'
        m = re.search(r'<meta\b[^>]*?' + _key_pat('og:image') + r'[^>]*?\bcontent="([^"]+)"', text, re.I)
        if m:
            image = m.group(1)
        text = ensure_meta(text, 'name', 'twitter:image', image)
    if 'llms.txt' not in text:
        text = text.replace('</head>', '<link rel=alternate type=text/plain href="/llms.txt" title="llms.txt"></head>', 1)
    text = ld_block(text, path, title, desc, url)
    if not is_spa(text):
        if path != '/':
            if not re.search(r'<h1\b', text, re.I) and title.strip().lower() != 'shell':
                text = re.sub(r'(<main\b[^>]*>)', lambda m: m.group(1) + f'<h1>{esc(short_title(title))}</h1>', text, count=1, flags=re.I)
            crumbs = visible_crumbs(path, title)
            if '<!--sc-seo-crumbs-->' in text:
                text = re.sub(r'<!--sc-seo-crumbs-->.*?<!--/sc-seo-crumbs-->', lambda _: crumbs, text, count=1, flags=re.S)
            elif not re.search(r'aria-label=["\']?Breadcrumb', text, re.I):
                text = re.sub(r'(<main\b[^>]*>)', lambda m: m.group(1) + crumbs, text, count=1, flags=re.I)
        text = ensure_nav(text, nav_html)
        if 'seo-sections' in text or 'sc-seo-crumbs' in text:
            text = ensure_style(text)
    info['indexable'] = True
    info['title'] = extract_title(text) or title
    return text, info


def html_files(site):
    out = []
    for dirpath, dirnames, filenames in os.walk(site):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith('.html'):
                out.append(os.path.join(dirpath, name))
    return out


def section_of(path):
    if path == '/':
        return 'Home'
    seg = path.strip('/').split('/')[0]
    return {
        'lessons': 'Lessons', 'events': 'Events', 'articles': 'Articles', 'library': 'Library', 'journal': 'Journal',
        'degen': 'The Degen', 'campus': 'Campus', 'live': 'Live apps', 'how-to-build': 'How to build',
        'explore': 'Source library', 'findings': 'Findings', 'faq': 'FAQ', 'glossary': 'Glossary',
        'topics': 'Topics', 'learn-solana': 'Learn Solana', 'learn-by-example': 'Concept walkthroughs',
        'what-to-build': 'What to build', 'legal': 'Legal', 'new': 'New', 'edge-ai': 'Edge AI',
    }.get(seg, 'Other')


def write_map(site, entries, nav_html):
    groups = {}
    for path, title in entries:
        if path == '/map/':
            continue
        groups.setdefault(section_of(path), []).append((path, short_title(title) or path))
    body = ['<h1>All pages</h1><p class=lead>Every public page on Sol.College. The same addresses are in the <a href="/sitemap.xml">XML sitemap</a>.</p>']
    keys = [k for k in ORDER if k in groups] + [k for k in groups if k not in ORDER]
    for key in keys:
        items = sorted(groups[key], key=lambda x: x[0])
        body.append(f'<h2>{esc(key)}</h2>')
        if key == 'Source library':
            body.append('<p>These are code walkthroughs. A page marked not yet live has not been deployed or run, so it is not a lesson. Live lessons are listed under Lessons.</p>')
        body.append('<ul>')
        for path, label in items:
            body.append(f'<li><a href="{esc(path)}">{esc(label)}</a></li>')
        body.append('</ul>')
    header = '<header class=top><a class=brand href="/">Sol.College</a></header>'
    styles = ''
    shell_fp = os.path.join(site, 'lessons', 'index.html')
    if os.path.isfile(shell_fp):
        shell = open(shell_fp, encoding='utf-8', errors='replace').read()
        hm = re.search(r'<header\b[^>]*class=["\']?top["\']?[^>]*>.*?</header>', shell, re.S | re.I)
        if hm:
            header = hm.group(0)
        styles = ''.join(re.findall(r'<style\b[^>]*>.*?</style>', shell, flags=re.S)[:2])
    doc = f'''<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>All pages | Sol.College</title>
<meta name=description content="{esc(MAP_DESC)}">
<link rel=canonical href="{SITE}/map/">
{styles}</head><body>
<a class=skip href="#main">Skip to content</a>{header}
<main id=main>{''.join(body)}</main>
<footer><p>Sol.College</p></footer></body></html>'''
    patched, info = patch(doc, '/map/', 'map/index.html', nav_html=nav_html, title_override='All pages | Sol.College', desc_override=MAP_DESC)
    dest = os.path.join(site, 'map')
    os.makedirs(dest, exist_ok=True)
    open(os.path.join(dest, 'index.html'), 'w', encoding='utf-8').write(patched)
    info['path'] = '/map/'
    info['title'] = 'All pages | Sol.College'
    return info


def write_sitemap(site, paths):
    urls = sorted(set(paths))
    rows = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path in urls:
        rows.append(f'<url><loc>{esc(SITE + path)}</loc><lastmod>{TODAY}</lastmod></url>')
    rows.append('</urlset>')
    xml = '\n'.join(rows) + '\n'
    open(os.path.join(site, 'sitemap.xml'), 'w', encoding='utf-8').write(xml)
    open(os.path.join(site, 'sitemap-index.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'<sitemap><loc>{SITE}/sitemap.xml</loc><lastmod>{TODAY}</lastmod></sitemap>'
        '</sitemapindex>\n')
    open(os.path.join(site, 'robots.txt'), 'w', encoding='utf-8').write(
        'User-agent: *\nAllow: /\nDisallow: /auth\nDisallow: /standard/\nDisallow: /404.html\n\n'
        f'Sitemap: {SITE}/sitemap.xml\n')
    return xml


def append_llms(site):
    fp = os.path.join(site, 'llms.txt')
    if not os.path.isfile(fp):
        return
    text = open(fp, encoding='utf-8', errors='replace').read()
    text = re.sub(r'\n## Site map\n.*?(?=\n## |\Z)', '\n', text, flags=re.S)
    block = f'\n## Site map\n- [All pages]({SITE}/map/)\n- [XML sitemap]({SITE}/sitemap.xml)\n'
    open(fp, 'w', encoding='utf-8').write(text.rstrip() + '\n' + block)


def _check(site, sitemap):
    if f'<loc>{SITE}/</loc>' not in sitemap:
        raise SystemExit('seo: homepage missing from sitemap')
    if f'<loc>{SITE}/map/</loc>' not in sitemap:
        raise SystemExit('seo: map missing from sitemap')
    for banned in (f'<loc>{SITE}/auth/</loc>', f'<loc>{SITE}/auth</loc>', f'<loc>{SITE}/standard/'):
        if banned in sitemap:
            raise SystemExit('seo: noindex path listed in sitemap: ' + banned)
    lessons = os.path.join(site, 'lessons')
    explore = os.path.join(site, 'explore')
    if os.path.isdir(lessons) and os.path.isdir(explore):
        for slug in sorted(os.listdir(lessons)):
            ep = os.path.join(explore, slug, 'index.html')
            if not os.path.isfile(ep):
                continue
            t = open(ep, encoding='utf-8', errors='replace').read()
            if f'/lessons/{slug}/' not in (canonical_of(t) or ''):
                continue
            if not has_noindex(t):
                raise SystemExit('seo: lesson mirror is indexable ' + slug)
            if f'<loc>{SITE}/explore/{slug}/</loc>' in sitemap:
                raise SystemExit('seo: lesson mirror in sitemap ' + slug)
            break
    home = os.path.join(site, 'index.html')
    if os.path.isfile(home):
        ht = open(home, encoding='utf-8', errors='replace').read()
        if 'data-landing="sol-college-v2"' in ht and 'not a claim that the original team is a partner' not in ht:
            raise SystemExit('seo: homepage lost the partnership disclaimer')
        if ht.count('EducationalOrganization') > 1:
            raise SystemExit('seo: duplicate EducationalOrganization')
    journal = os.path.join(site, 'journal', 'index.html')
    if os.path.isfile(journal):
        jt = open(journal, encoding='utf-8', errors='replace').read()
        if 'peer reviewed' not in jt and 'peer-reviewed' not in jt:
            raise SystemExit('seo: journal lost the peer-review limit')
        if 'ISSN' in jt or 'doi:' in jt.lower():
            raise SystemExit('seo: journal gained a serial identifier')
    degen = os.path.join(site, 'degen', 'index.html')
    if os.path.isfile(degen):
        dt = open(degen, encoding='utf-8', errors='replace').read()
        if 'No report has been published' not in dt:
            raise SystemExit('seo: The Degen lost its empty-newsroom line')


def apply(site='site'):
    site = os.path.abspath(site)
    if not os.path.isdir(site):
        raise SystemExit('seo: missing site directory ' + site)
    links = list(SECTIONS)
    faq_fp = os.path.join(site, 'faq', 'index.html')
    if os.path.isfile(faq_fp) and extract_title(open(faq_fp, encoding='utf-8', errors='replace').read()).strip().lower() == 'shell':
        links = [item for item in links if item[0] != '/faq/']
    if not os.path.isfile(os.path.join(site, 'findings', 'index.html')):
        links = [item for item in links if item[0] != '/findings/']
    nav = sections_html(links)
    pages = []
    seen = hidden = trimmed = 0
    samples = []
    for fp in html_files(site):
        rel_dir = os.path.relpath(fp, site).replace(os.sep, '/')
        if rel_dir.startswith('dapps/') or rel_dir.startswith('legacy/'):
            continue
        seen += 1
        path, rel = url_path(site, fp)
        text = open(fp, encoding='utf-8', errors='replace').read()
        new, info = patch(text, path, rel, nav_html=nav)
        if new != text:
            open(fp, 'w', encoding='utf-8').write(new)
        if info.get('trimmed') and len(samples) < 30:
            samples.append((path or rel, extract_desc(new)[:180]))
        if info.get('trimmed'):
            trimmed += 1
        if info.get('indexable') and path and path != '/map/':
            pages.append((path, info.get('title') or path))
        else:
            hidden += 1
    mapped = write_map(site, pages, nav)
    if mapped.get('indexable'):
        pages.append(('/map/', mapped.get('title') or 'All pages'))
    sitemap = write_sitemap(site, [p for p, _ in pages])
    append_llms(site)
    _check(site, sitemap)
    from collections import Counter
    dups = [t for t, n in Counter(title for _, title in pages).items() if n > 1 and t]
    print(f'seo: html={seen} indexable={len(pages)} hidden={hidden} trimmed={trimmed} sitemap={sitemap.count("<loc>")} duplicate_titles={len(dups)}')
    for title in dups[:8]:
        print('seo duplicate title:', title)
    for path, desc in samples:
        print('seo trim:', path, '→', desc)
    return pages


if __name__ == '__main__':
    apply(sys.argv[1] if len(sys.argv) > 1 else 'site')
