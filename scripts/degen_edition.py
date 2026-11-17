"""Reading edition of The Degen.

Each page is a close reading of a public document retrieved on 17 Nov 2026.
It is not a report. No interview, site visit, or transaction is claimed.
"""
import html, os, re, unicodedata

SITE = 'https://sol.college'
RETRIEVED = '17 Nov 2026'
BANNED = (
    'sources told', 'a student said', 'we interviewed', 'our reporter', 'hot coin',
    'price ticker', 'editorially independent', 'an independent newsroom', 'award-winning',
    'issn', 'doi:',
)

def E(s):
    return html.escape(str(s if s is not None else ''), quote=True)

def slugify(title):
    s = unicodedata.normalize('NFKD', str(title))
    s = s.encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return re.sub(r'-{2,}', '-', s)[:90].strip('-')

def _words(text):
    return re.findall(r"[A-Za-z0-9''-]+", text or '')

def load():
    import degen_copy
    import degen_depth
    rows = []
    seen = set()
    for raw in degen_copy.READINGS:
        row = dict(raw)
        row['slug'] = slugify(row['title'])
        if not re.fullmatch(r'[a-z0-9-]+', row['slug']):
            raise SystemExit('degen: bad slug ' + row['title'])
        if row['slug'] in seen:
            raise SystemExit('degen: duplicate slug ' + row['slug'])
        seen.add(row['slug'])
        row['path'] = '/degen/readings/' + row['slug'] + '/'
        desc = ' '.join(row['desc'].split())
        if len(desc) > 158:
            raise SystemExit('degen: description too long (%d) %s' % (len(desc), row['slug']))
        if not re.search(r'\b(not|no|never|without)\b', desc, re.I):
            raise SystemExit('degen: description has no limit word ' + row['slug'])
        row['desc'] = desc
        # Depth pass triples analytical prose from fields the reading already stored.
        row['paragraphs'] = list(row['paragraphs']) + degen_depth.deepen(row)
        blob = '\n'.join([
            row['title'], row['question'], row['desc'],
            '\n'.join(row['paragraphs']),
            '\n'.join(row['says']),
            '\n'.join(row['paid']),
            '\n'.join(row['decides']),
            '\n'.join(row['limits']),
        ])
        low = blob.lower()
        for phrase in BANNED:
            if phrase in low:
                raise SystemExit('degen: banned phrase %s in %s' % (phrase, row['slug']))
        if not row['sources']:
            raise SystemExit('degen: no source ' + row['slug'])
        for src in row['sources']:
            if not str(src['url']).startswith('https://'):
                raise SystemExit('degen: bad source ' + row['slug'])
        row['words'] = len(_words(blob))
        row['search'] = ' '.join(blob.split())
        rows.append(row)
    return rows

def readings():
    return load()

def word_count():
    return sum(r['words'] for r in readings())

def for_desk(desk):
    return [r for r in readings() if r['desk'] == desk]

def _sources(r):
    items = ''.join(
        '<li><a href="%s">%s</a>. %s</li>' % (E(s['url']), E(s['label']), E(s['note']))
        for s in r['sources'])
    return '<ul>' + items + '</ul>'

def _list(title, items):
    return '<h2>%s</h2><ul>%s</ul>' % (E(title), ''.join('<li>%s</li>' % E(x) for x in items))

def article(r, mast, foot, crumbs):
    paras = ''.join('<p>%s</p>' % E(p) for p in r['paragraphs'])
    related = ''
    if r.get('related'):
        by = {x['slug']: x for x in readings()}
        links = []
        for slug in r['related']:
            other = by.get(slug)
            if other:
                links.append('<a href="%s">%s</a>' % (other['path'], E(other['title'])))
        if links:
            related = '<h2>Related readings</h2><p>' + ' · '.join(links) + '</p>'
    return f'''<article class=tds>
{crumbs('Reading')}
{mast(False)}
<p class=label>{E(r['feature'])} · Document reading · not a report</p>
<h1>{E(r['title'])}</h1>
<p class=deck>{E(r['deck'])}</p>
<p class=byline>By Sol.College · {RETRIEVED} · {E(r['desk_name'])}</p>
<aside class=box>
<p class=label>Status</p>
<dl class=facts>
<dt>Type</dt><dd>A reading of a public page. Not a report of an event.</dd>
<dt>Question</dt><dd>{E(r['question'])}</dd>
<dt>Reporting</dt><dd>None. No interview, no site visit, and no transaction sent by the paper.</dd>
<dt>Author</dt><dd>Sol.College, the publisher. No person is named as the writer.</dd>
<dt>Retrieved</dt><dd>{RETRIEVED}. The dateline is the day the pages were fetched, not a day a reporter went somewhere.</dd>
<dt>Disclosure</dt><dd>No writer is named, so no holding is on file. That is not a claim that nobody at Sol.College holds a token.</dd>
<dt>Corrections</dt><dd><a href="/degen/corrections/">The log</a>. None has been issued.</dd>
</dl>
</aside>
{paras}
{_list('What the retrieved page says', r['says'])}
{_list('Who gets paid, as the page describes it', r['paid'])}
{_list('Who can decide, as the page describes it', r['decides'])}
{_list('What this reading does not establish', r['limits'])}
<h2>Pages retrieved</h2>
{_sources(r)}
{related}
<p><a href="/degen/readings/">All readings</a> · <a href="/degen/">The Degen</a></p>
{foot()}
</article>'''

def index_page(mast, foot, crumbs):
    rows = readings()
    desks = []
    seen = []
    for r in rows:
        if r['desk'] not in seen:
            seen.append(r['desk'])
            desks.append((r['desk'], r['desk_name']))
    options = ''.join('<option value="%s">%s</option>' % (E(i), E(n)) for i, n in desks)
    cards = []
    for r in rows:
        cards.append(
            '<article data-paper="%s" data-desk="%s"><p class=kind>%s · %s</p><h3><a href="%s">%s</a></h3><p>%s</p></article>'
            % (E(r['search']), E(r['desk']), E(r['feature']), E(r['desk_name']), r['path'], E(r['title']), E(r['deck'])))
    return f'''<article class=tds>
{crumbs('Readings')}
{mast(False)}
<p class=label>Reading edition · not a news edition</p>
<h1>Readings</h1>
<p class=deck>{len(rows)} close readings of public pages about hardware custody, perpetual futures, meme-launch curves, and the markets around them. No report has been published.</p>
<p>Search matches the words on these readings. It does not answer from outside the pages, and it does not decide which document is right when two of them disagree. A screen the paper did not open is not in the index.</p>
<form class="filters papersearch" role=search>
<label>Search the readings <input type=search data-standard-search placeholder="Seed Vault, 500x, bonding curve, futarchy" enterkeyhint=search></label>
<label>Desk <select data-desk-filter><option value="">Any desk</option>{options}</select></label>
</form>
<p id=paper-count>{len(rows)} readings</p>
<p id=paper-empty hidden>No reading matches.</p>
<div class=edition>{''.join(cards)}</div>
{foot()}
<script>
(function(){{
  var q=document.querySelector('[data-standard-search]');
  var desk=document.querySelector('[data-desk-filter]');
  var items=[].slice.call(document.querySelectorAll('[data-paper]'));
  var count=document.getElementById('paper-count');
  var empty=document.getElementById('paper-empty');
  function apply(){{
    var words=(q.value||'').toLowerCase().split(/\\s+/).filter(Boolean);
    var d=desk?desk.value:'';
    var shown=0;
    items.forEach(function(el){{
      var t=((el.getAttribute('data-paper')||'')+' '+(el.textContent||'')).toLowerCase();
      var ok=!words.some(function(w){{return t.indexOf(w)<0;}});
      if(d && el.getAttribute('data-desk')!==d) ok=false;
      el.hidden=!ok;
      if(ok) shown++;
    }});
    if(count) count.textContent=shown+' of '+items.length+' readings';
    if(empty) empty.hidden=shown!==0;
  }}
  q.form.addEventListener('submit', function(e){{e.preventDefault(); apply();}});
  q.addEventListener('input', apply);
  if(desk) desk.addEventListener('change', apply);
}})();
</script>
</article>'''

def pages(mast, foot, crumbs):
    out = [('/degen/readings/', 'Readings',
            'Close readings of public pages on hardware custody, perpetual futures, and meme launches. No report has been published.',
            index_page(mast, foot, crumbs))]
    for r in readings():
        out.append((r['path'], r['title'], r['desc'], article(r, mast, foot, crumbs)))
    return out
