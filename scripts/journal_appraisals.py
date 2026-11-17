"""Source appraisals for the Journal of Solana Studies.

Each note applies one instrument to one document the Solana Library retrieved
on 17 Nov 2026. The instrument records what that reading stored. It does not
review the file line by line, and it does not report a cluster observation.
"""
import html, re
import library_papers as papers

CHECKED = '17 Nov 2026'

def E(s):
    return html.escape(str(s if s is not None else ''), quote=True)

def _words(text):
    return re.findall(r"[A-Za-z0-9''-]+", text or '')

def status_of(row):
    if row['doc_type'] != 'SIMD':
        return None
    m = re.search(r'\(([^)]+)\)\.', row['desc'])
    if m:
        return m.group(1)
    m = re.search(r'\bstatus ([A-Za-z]+)', row['desc'])
    if m:
        return m.group(1)
    return None

STATUS_RULE = {
 'Activated': (
  'Activated is the file’s own front-matter label. A label inside a proposal is a claim about the proposal’s process, not a row this journal stored from a cluster. '
  'A study that wants to say the change is running has to name the record it would read — a feature gate, a program’s bytes, a slot — and store that read beside the label. '
  'This note does not have that read. Citing “Activated” as proof the network behaves as the summary describes is the inference the instrument forbids.'
 ),
 'Review': (
  'Review, on a SIMD file, means the proposal is in that process. It does not mean this journal reviewed it, and it does not mean a reviewer was assigned here. '
  'The journal’s own status panel says review has not started. Those two uses of the word have to stay apart. A file under review can still be quoted as a proposal. It cannot be quoted as a decision.'
 ),
 'Accepted': (
  'Accepted, in this file’s front matter, is a SIMD-process word. The journal’s status panel uses the same word to mean something else: that this journal accepted a paper. Nothing here has been accepted. '
  'A citation that slides from the file’s Accepted to “the journal accepted this design”, or to “the cluster runs it”, has changed the word. This note does not make that change.'
 ),
 'Idea': (
  'Idea is an early label. The file is allowed to be incomplete. A literature review that cites an Idea file as the network’s current design has treated a starting note as a specification. '
  'The instrument keeps the label in the sentence. The summary can be discussed as a proposal. It is not discussed as a behaviour that was observed.'
 ),
 'Draft': (
  'Draft means the authors have not presented the file as finished, on the label the catalogue recorded. Quoting a draft as if it were the activated rule is a mis-citation even before anyone asks whether a cluster matches it. '
  'This note quotes the summary as a draft summary.'
 ),
 'Withdrawn': (
  'Withdrawn is the file’s statement that the proposal is not being carried forward in that repository’s process. It is not a measurement that no validator ever ran related code, and it is not a reason to pretend the summary was never written. '
  'A citation of a withdrawn file has to carry the label. Otherwise the reader is handed a design the file itself has stepped away from.'
 ),
 'Implemented': (
  'Implemented, as a file label, says the authors consider the work implemented somewhere they have in mind. It does not name the bytes on a cluster this journal queried, because this journal queried none. '
  'A repository commit and a deployed program are different records. The catalogue stored the label. It did not store a deployment.'
 ),
 'Stagnant': (
  'Stagnant is the file’s description of its own pace. It is not a finding that the idea is absent from running systems, and it is not a finding that the idea is harmless to ignore. '
  'The summary can still be read. The label stops a citation from calling the proposal current.'
 ),
 'Living': (
  'Living means the file presents itself as a document that can change. A quotation from it needs the retrieval date, which for this series is 17 Nov 2026. '
  'A later edit of a living file does not rewrite this note. It would be a new retrieval.'
 ),
}

def _claim_sentence(scope):
    parts = [s.strip() for s in re.split(r'(?<=[.!?])\s+', scope or '') if s.strip()]
    if not parts:
        return ''
    frames = ('The title page', 'The file', 'The summary', 'The opening', 'This file', 'The catalogue', 'Reading the')
    for s in parts:
        if not s.startswith(frames):
            return s.rstrip('.')
    return parts[0].rstrip('.')

def bearing(row):
    blob = (row['title'] + ' ' + row['scope']).lower()
    def has(*keys):
        return any(re.search(r'\b' + re.escape(k) + r'\b', blob) for k in keys)
    rules = [
     (('transaction per second', 'transactions per second', '710,000', 'throughput', 'gbps', 'benchmark', 'millisecond'),
      'benchmarking-benchmarks', 'Benchmarking Benchmarks',
      'The journal’s benchmarking sketch refuses a performance number that arrives without the workload, the hardware, the client, and the failure rule. '
      'This file supplies a sentence a reader might repeat as a number. The sketch’s rule is that the sentence is not yet a measurement. '
      'Nothing on this page re-runs the analysis, times a client, or decides whether failed transactions would have counted.'),
     (('fee', 'rent', 'lamport', 'compute budget', 'priority'),
      'the-cost-of-a-payment', 'The Cost of a Payment',
      'The cost sketch says a displayed fee is an interpretation, and the observation would be the set of balance changes. '
      'This file may name a fee, a rent rule, or a compute charge. Naming it is not the same as walking a payment and listing every balance that moved. '
      'No workflow was costed for this note.'),
     (('blockhash', 'confirmation', 'commitment', 'receipt', 'nonce', 'pending'),
      'submitted-is-not-settled', 'Submitted Is Not Settled',
      'The first protocol separates submission, execution success, observed confirmation, expiry, and unresolved. '
      'A document that uses one of those words has not, by using it, shown that any application keeps them in different columns. '
      'This note does not store a client label beside a cluster response.'),
     (('retry', 'duplicate', 'idempoten', 'replay'),
      'retry-without-double-execution', 'Retry Without Double Execution',
      'The second protocol separates a signed message from the business act a second signature might repeat. '
      'A proposal about duplicates or replay can be prior reading for that protocol. It is not a fault-injection result, and no operation identifier was scored.'),
     (('upgrade', 'loader', 'immutable', 'authority'),
      'upgrade-authority', 'Upgrade Authority Disclosure',
      'The upgrade sketch compares an on-chain authority with a statement a user can open. '
      'This file is neither of those records. It does not show what a loader account currently names, and it does not show what a website tells a signer. '
      'No deployment was inspected.'),
     (('token', 'spl', 'mint', 'transfer', 'nft'),
      'one-token-api', 'One Token API, Different Behaviour',
      'The token protocol wants a matrix of named configurations, with expected and observed in different sentences, and “unsupported” left unsupported. '
      'A design note that describes a transfer does not fill a cell. The programmes under test are still not chosen, and no fixture was built for this note.'),
     (('rpc', 'indexer', 'ingest'),
      'indexer-recovery', 'Indexer Recovery After Interruption',
      'An indexer or an RPC history can be described in a file and still not be shown to recover a gap. '
      'The sketch’s observation would be the slots in a store compared with a source that is not the store. This note has no store and no gap.'),
     (('vote', 'consensus', 'tower', 'alpenglow', 'proof of history', 'votor', 'rotor', 'fork'),
      None, None,
      'This file’s stored sentences are about agreement: a vote, a fork, a consensus rule, or a named design such as Proof of History, Tower, or Alpenglow. '
      'None of the six founding protocols is a consensus study, and this appraisal does not invent one. '
      'A round count, a stake threshold, or a resilience figure in the file stays the file’s claim. It is not a finality measurement from a cluster, because no cluster was queried.'),
     (('wallet', 'signer', 'preview'),
      'wallet-preview', 'Wallet Preview Comprehension',
      'A file about what a signer sees is not a comprehension study. The wallet sketch needs a person’s answer, scored against bytes, after consent. '
      'No person was asked, and no preview was tested for this note.'),
     (('vulnerab', 'exploit', 'incident', 'security'),
      'evidence-quality', 'Evidence Quality in Security Claims',
      'The evidence-quality sketch keeps suspected, reproduced, fixed, and deployed in different sentences. '
      'A design note can mention an incident or a check without earning any of those four. This appraisal does not promote the file’s adjective into one of them.'),
    ]
    for keys, slug, title, text in rules:
        if has(*keys):
            return slug, title, text
    return None, None, (
     'This file does not, on the sentences the catalogue stored, fall under a single founding protocol tightly enough to pretend it is that protocol’s prior result. '
     'It remains a retrieved document. A later study may cite it for the summary below. The citation has to stay a citation of a document, not a report that the behaviour was observed.'
    )

def _terms(row):
    scope = row['scope']
    nums = []
    for n in re.findall(r'\b\d[\d,]*(?:\.\d+)?(?:\s*(?:%|gbps|tps|milliseconds?|ms|lamports?))?\b', scope, re.I):
        n = ' '.join(n.split())
        if re.fullmatch(r'\d', n):
            continue
        if n not in nums:
            nums.append(n)
    quotes = re.findall(r'[“"]([^”"]+)[”"]', scope)
    first = _claim_sentence(scope)
    parts = []
    if nums:
        parts.append(
         'The stored scope contains these quantities or version marks: %s. '
         'Each one is the file’s figure or the file’s label. None of them was remeasured for this note, and a figure does not become a baseline because a catalogue wrote it down.'
         % ', '.join(nums)
        )
    else:
        parts.append(
         'The stored scope states no quantity this note could mistake for a measurement. '
         'That absence is not a finding that the rest of the file contains no numbers. The rest of the file was not reviewed line by line.'
        )
    parts.append(
     'The estimand a later study could take from this stored sentence is documentary: what this retrieved file claims, in the words “%s.” '
     'The estimand is not the behaviour of a named cluster, a named signer, or a named pool of funds. Those would be different studies, and they would need records this page does not store.'
     % first
    )
    if quotes:
        shown = ', '.join('“%s”' % q for q in quotes[:4])
        parts.append('Marked phrases in the stored scope include %s. A marked phrase is the document’s wording. It is not this journal’s conclusion.' % shown)
    return ' '.join(parts)

_BOILER_HEADS = {
 'summary', 'motivation', 'alternatives considered', 'detailed design', 'impact',
 'security considerations', 'drawbacks', 'new terminology', 'references',
}

def _distinct_headings(row):
    heads = row.get('outline') or []
    distinct = [h for h in heads if h.strip().lower() not in _BOILER_HEADS]
    if not heads:
        return ''
    if not distinct:
        return (
         'The stored headings are the ordinary section names of this kind of file: %s. '
         'An ordinary heading is not evidence that the design is ordinary, and it is not evidence that the section under the heading succeeded. The section text was not reviewed line by line.'
         % '; '.join(heads[:8])
        )
    shown = '; '.join(distinct[:8])
    return (
     'Beyond the ordinary section names, the file’s own headings include: %s. '
     'Those names are specific to this file. They are still names. “%s” does not establish that the section did what the name suggests, because the text under the heading was not reviewed line by line and was not copied.'
     % (shown, distinct[0])
    )

_PROJECT = {
 'Solana': 'The catalogue files this under Solana. A path in a Solana repository is not a statement that a cluster runs the proposal.',
 'Wormhole': 'The catalogue files this under Wormhole. A Wormhole design is not a Solana protocol specification, including where the stored sentence mentions Solana. What a deployed bridge does is a different record from what the file proposes.',
 'Anza': 'The catalogue files this under Anza. An Anza paper is not, by that filing, the Solana white paper, and a retrieval that did not come from an anza.xyz URL is not recoded into one.',
 'Solayer': 'The catalogue files this under Solayer. Yield, conversion, or market figures in a Solayer document stay that document’s figures. This note did not inspect a reserve or an issuer.',
 'MagicBlock': 'The catalogue files this under MagicBlock. A game or an ephemeral-rollup document is not evidence a game is deployed, and an arXiv listing is not peer review.',
 'DoubleZero': 'The catalogue files this under DoubleZero. A throughput aim in a DoubleZero document was not benchmarked here.',
 'Pyth': 'The catalogue files this under Pyth. An example price in a Pyth paper is an illustration in the paper. This note did not call a Pyth feed, and the example is not a live price.',
 'UXD Protocol': 'The catalogue files this under UXD Protocol. Nothing in the stored record establishes a chain, a deployment, a reserve, or a redemption that was observed. The chain is not filled in from outside knowledge.',
 'Sonic': 'The catalogue files this under Sonic. A tick or a throughput figure in a Sonic document was not measured here, and a PDF that was not retrieved is not reviewed by mentioning it.',
 'Kamino': 'The catalogue files this under Kamino. Loan-to-value figures on a Kamino page were not checked, and the page was not copied.',
 'Mango': 'The catalogue files this under Mango. A draft’s volume ambition was not checked. No calendar date is printed where the catalogue says none is printed.',
}

def _project(row):
    return _PROJECT.get(row['project'], 'The catalogue’s project label is “%s”. The label places the file. It does not establish a deployment.' % row['project'])

def _misuse(row):
    sentence = _claim_sentence(row['scope'])
    return (
     'A careless citation of “%s” would lift this sentence out of the file and drop the limits: “%s.” '
     'That citation would sound like a finding about Solana. The record that was actually stored is narrower. It is a reading of a retrieved file, with the limits printed on the library page and repeated below. '
     'Putting the sentence in a result section of a journal paper would require the observations this note does not have.'
     % (row['title'], sentence)
    )

def _outline(row):
    heads = row.get('outline') or []
    if not heads:
        return (
         'No heading outline was stored for this record. The absence of an outline is not evidence the file has no sections. It means this series will not invent the section list.'
        )
    shown = heads[:12]
    more = ''
    if len(heads) > 12:
        more = ' %d further headings were stored and are not repeated here.' % (len(heads) - 12)
    return (
     'The file’s own headings, as stored, include: %s.%s '
     'A heading is the file’s name for a section. The text under the heading was not reviewed line by line for this note, and a heading is not a finding that the section succeeds at what its name suggests.'
     % ('; '.join(shown), more)
    )

def build(row):
    status = status_of(row)
    status_sentence = STATUS_RULE.get(status) if status else (
     'This record is not a SIMD front matter with one of the status labels the series codes. Its type is %s. '
     'The type is a description of the file that was retrieved. It is not a peer-review outcome, and it is not evidence the design runs on a cluster.'
     % row['doc_type']
    )
    slug, btitle, btext = bearing(row)
    authors = row['authors']
    version = row['version']
    date = row['date']
    kind = row['doc_type'] if row['doc_type'] == 'SIMD' else row['doc_type'].lower()
    nbytes = row['bytes']
    size = ('%s bytes were retrieved. ' % format(nbytes, ',')) if isinstance(nbytes, int) else 'A byte length was not stored. '
    paragraphs = [
     'This is a source appraisal of “%s”, a %s in the Solana Library. The library records version “%s”, date “%s”, and authors “%s”. %s'
     'The file was retrieved on %s. The retrieval note on the catalogue is the note this appraisal relies on. The journal did not open a second copy and did not collect observations of its own.'
     % (row['title'], kind, version, date, authors, size, CHECKED),
     _project(row),
     'What the reading stored as the document’s scope is this: %s' % row['scope'],
     _terms(row),
     'What the reading stored about Solana, specifically, is this: %s' % row['solana'],
     'What the reading stored as limits is this: %s Those limits bind this appraisal. A sentence that outruns them is not a reading of the record.' % row['limits'],
     status_sentence,
     _outline(row),
     *([_distinct_headings(row)] if _distinct_headings(row) else []),
     btext,
     _misuse(row),
     'No observations have been collected. No reviewer has been assigned. The page is not peer-reviewed research. '
     'The library page remains the catalogue record; this page is the journal’s statement of what that record can and cannot be cited for. '
     'A later study that uses the file has to say which sentence it used and which measurement it added. This note is not that measurement.',
    ]
    if slug:
        related = (slug, btitle)
    else:
        related = None
    desc = 'Appraisal of a retrieved %s. The file’s wording is not a cluster measurement, and no line-by-line review was done.' % kind
    if len(desc) > 158:
        raise SystemExit('appraisal desc ' + row['slug'])
    if not re.search(r'\b(not|no|never)\b', desc, re.I):
        raise SystemExit('appraisal desc limit ' + row['slug'])
    return dict(
     paper=row, status=status or 'No process label', paragraphs=paragraphs,
     related=related, desc=desc, words=len(_words('\n'.join(paragraphs))),
    )

def notes():
    rows = []
    seen_titles = set()
    for row in papers.papers():
        note = build(row)
        base = 'Appraisal: ' + row['title']
        extra = row['version']
        if extra in ('Not stated on the pages read', 'Not a numbered paper version'):
            extra = row['doc_type']
        title = base + ' — ' + extra
        if title in seen_titles:
            title = title + ' — ' + row['slug']
        seen_titles.add(title)
        note['title'] = title
        note['slug'] = row['slug']
        note['path'] = '/journal/notes/' + row['slug'] + '/'
        rows.append(note)
    return rows

def word_count():
    return sum(n['words'] for n in notes())

def index_html():
    import journal as j
    rows = notes()
    statuses = []
    types = []
    for n in rows:
        if n['status'] not in statuses:
            statuses.append(n['status'])
        t = n['paper']['doc_type']
        if t not in types:
            types.append(t)
    def opts(items):
        return ''.join('<option value="%s">%s</option>' % (E(i), E(i)) for i in items)
    cards = []
    for n in rows:
        blob = ' '.join([n['title'], n['paper']['scope'], n['paper']['solana'], n['status'], n['paper']['project']])
        cards.append(
         '<article data-paper="%s" data-status="%s" data-type="%s"><p class=eyebrow>%s · %s</p><h3><a href="%s">%s</a></h3><p>%s</p></article>'
         % (E(blob), E(n['status']), E(n['paper']['doc_type']), E(n['paper']['doc_type']), E(n['status']),
            n['path'], E(n['paper']['title']), E(n['paper']['scope']))
        )
    body = f'''{j.status_panel('Appraisal series. Not a completed study.')}
<p>This series applies one instrument to every document on the <a href="/library/papers/">white-paper shelf</a> that was retrieved on {CHECKED}. There are {len(rows)} records. The instrument asks what the catalogue stored, what a citation is allowed to do with it, and what would still have to be measured. It does not re-read the files line by line. No observations have been collected.</p>
<h2>The instrument</h2>
<p>The unit is one library record. The fields used are the title, the document type, the version, the date, the authors, the byte length when one was stored, the scope sentence, the Solana sentence, the limits sentence, and the heading outline when one was stored. Those fields were fixed when the library page was written. This series does not add a field because a conclusion would be more satisfying with it.</p>
<p>A status word such as Activated, Review, or Accepted is copied from the file’s label when the catalogue recorded one. It is not recoded into “true on a cluster” or “accepted by this journal”. A heading is the file’s name for a section. It is not a summary of the section, because the section was not reviewed line by line.</p>
<p>The series can support a description of what these retrieved files say, on the sentences that were stored. It cannot support a claim about the live network, a claim that a proposal is deployed, or a claim that a benchmark was reproduced. A note that sounds more specific than its record has left the instrument.</p>
<p>No research paper has been published. Nothing in the series is peer reviewed. Selecting one flattering file and ignoring the rest would be a different project, and it would have to say so.</p>
<form class=filters id=note-form role=search>
<label>Search <input id=note-q type=search placeholder="A title, a status, a claim"></label>
<label>Status <select id=note-status><option value="">Any</option>{opts(statuses)}</select></label>
<label>Type <select id=note-type><option value="">Any</option>{opts(types)}</select></label>
</form>
<p id=note-count>{len(rows)} appraisals</p>
<p id=note-empty hidden>No appraisal matches.</p>
<div class=hub-grid>{''.join(cards)}</div>
<p><a href="/journal/methods/">How to read a protocol</a> · <a href="/journal/programme/">The programme</a></p>
<script>
(function(){{
  var q=document.getElementById('note-q');
  var st=document.getElementById('note-status');
  var ty=document.getElementById('note-type');
  var items=[].slice.call(document.querySelectorAll('[data-paper]'));
  var count=document.getElementById('note-count');
  var empty=document.getElementById('note-empty');
  function apply(){{
    var words=(q.value||'').toLowerCase().split(/\\s+/).filter(Boolean);
    var shown=0;
    items.forEach(function(el){{
      var blob=(el.getAttribute('data-paper')||'').toLowerCase();
      var ok=!words.some(function(w){{return blob.indexOf(w)<0;}});
      if(st.value && el.getAttribute('data-status')!==st.value) ok=false;
      if(ty.value && el.getAttribute('data-type')!==ty.value) ok=false;
      el.hidden=!ok;
      if(ok) shown++;
    }});
    count.textContent=shown+' of '+items.length+' appraisals';
    empty.hidden=shown!==0;
  }}
  document.getElementById('note-form').addEventListener('submit', function(e){{e.preventDefault(); apply();}});
  q.addEventListener('input', apply);
  st.addEventListener('change', apply);
  ty.addEventListener('change', apply);
}})();
</script>'''
    return body

def pages():
    """(path, title, desc, main) for the series and each note. main is the article inner HTML."""
    import journal as j
    out = []
    index_title = 'Source appraisals'
    index_desc = 'Appraisals of every retrieved library document. A file’s wording is not a cluster measurement, and nothing is peer reviewed.'
    if len(index_desc) > 158:
        raise SystemExit('index desc %d' % len(index_desc))
    index_main = j.shell('Appraisal series · not a study', index_title,
     'What the retrieved documents can be cited for, and what they cannot establish.',
     index_html(), ['<span>Source appraisals</span>'])
    out.append(('/journal/notes/', index_title, index_desc, index_main))
    # Fix related links with the correct href now that we can classify.
    proto_slugs = {p['slug'] for p in j.PROTOCOLS}
    for note in notes():
        p = note['paper']
        paras = ''.join('<p>%s</p>' % E(x) for x in note['paragraphs'])
        rel = ''
        if note['related']:
            slug, title = note['related']
            href = ('/journal/protocols/' if slug in proto_slugs else '/journal/sketches/') + slug + '/'
            rel = '<h2>Where this could be cited later</h2><p>If a study is designed, the nearest open question on this site is <a href="%s">%s</a>. That page has not been run. This appraisal does not fill it in.</p>' % (E(href), E(title))
        main_body = f'''{j.status_panel('Source appraisal. Not a completed study.')}
<p><b>Instrument.</b> One retrieved library record, appraised with the rules on <a href="/journal/notes/">the series page</a>. The sentences below are the catalogue’s sentences.</p>
{paras}
{rel}
<h2>Record</h2>
<ul>
<li>Library page: <a href="{E(p['path'])}">{E(p['title'])}</a></li>
<li>Source file: <a href="{E(p['source'])}">{E(p['source'])}</a></li>
<li>Retrieved: {CHECKED}. This page did not repeat the fetch, and it did not collect a new observation.</li>
</ul>
<p><a href="/journal/notes/">All appraisals</a> · <a href="/journal/methods/">How to read a protocol</a></p>'''
        html_page = j.shell('Source appraisal · not a study', note['title'], E(note['desc']), main_body, ['<span>%s</span>' % E(p['title'])])
        out.append((note['path'], note['title'], note['desc'], html_page))
    return out
