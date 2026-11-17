"""The white-paper shelf lists only documents that were retrieved."""
import html, json, os, shutil, tempfile, unittest
import library_papers as papers
import solana_library as lib

def page(body, title, desc, path):
  return ('<!doctype html><html><head><meta charset=utf-8><title>' + html.escape(title) +
    '</title><meta name=description content="' + html.escape(desc, quote=True) +
    '"></head><body><main id=main>' + body + '</main></body></html>')

class Papers(unittest.TestCase):
  def test_catalogue_is_retrieved_documents_only(self):
    rows = papers.papers()
    self.assertGreaterEqual(len(rows), 240)
    ids = [r['id'] for r in rows]
    self.assertEqual(len(ids), len(set(ids)))
    blob = json.dumps(rows)
    self.assertNotIn('helium', blob.lower())
    self.assertNotIn('audius', blob.lower())
    self.assertNotIn('peer-reviewed', blob.lower())
    self.assertNotIn("world's largest", blob.lower())
    uxd = next(r for r in rows if r['slug'].startswith('uxd-protocol'))
    self.assertFalse(uxd['names_solana'])
    self.assertIn('does not contain the word Solana', uxd['solana'])
    sol = next(r for r in rows if r['id'] == 'paper-solana-whitepaper')
    self.assertIn('v0.8.14', sol['version'])
    self.assertIn('Yakovenko', sol['authors'])
    self.assertIn('710,000', sol['scope'])
    self.assertIn('not a measurement', sol['limits'])
    silent = [r for r in rows if r['project'] == 'Wormhole' and not r['names_solana']]
    self.assertGreaterEqual(len(silent), 4)
    full = [r for r in rows if r['doc_type'] in papers.READING_TYPES]
    self.assertEqual(len(full), len(rows))
    self.assertGreaterEqual(len(full), 240)
    shelf = [r for r in rows if r['doc_type'] in ('White paper', 'Litepaper', 'Language edition')]
    self.assertEqual(len(shelf), 20)
    for r in shelf:
      reading = papers.load_reading(r['slug'])
      self.assertIsNotNone(reading)
      self.assertGreaterEqual(len(reading['sections']), 1)
      self.assertGreaterEqual(papers.reading_words(reading), 150)
    for r in full:
      reading = papers.load_reading(r['slug'])
      self.assertIsNotNone(reading, msg=r['slug'])
      self.assertGreaterEqual(len(reading['sections']), 1)
      self.assertGreaterEqual(papers.reading_words(reading), 120, msg=r['slug'])
      ret = r['retrieval'].lower()
      self.assertTrue(
        ('full text was read' in ret) or ('was read in full' in ret) or ('full markdown file was read' in ret)
        or ('full markdown' in ret) or ('full litepaper body' in ret) or ('full litepaper' in ret)
        or ('full french text was read' in ret) or ('full italian text was read' in ret)
        or ('full japanese text was read' in ret),
        msg=r['slug'] + ' retrieval does not say the file was fully read')
      self.assertTrue(
        ('verbatim' in r['limits'].lower()) or ('not a copy' in r['limits'].lower())
        or ('not a sentence-by-sentence' in r['limits'].lower()),
        msg=r['slug'] + ' limits do not say the reading is not a copy')
    for r in rows:
      self.assertLessEqual(len(r['desc']), 158)
      self.assertTrue(r['source'].startswith('http'))
      self.assertIn('17 Nov 2026', r['retrieval'])

  def test_pages_and_library_search(self):
    S = tempfile.mkdtemp(prefix='papers-')
    self.addCleanup(shutil.rmtree, S)
    os.makedirs(S + '/llms.txt' and S, exist_ok=True)
    open(S + '/llms.txt', 'w').write('# Sol.College\n\n## Library\nold\n\n## Other\nkeep\n')
    live = [
      dict(slug='picassol-hackathon', learn='pixel', program='GsFGX3pzdgzugAfjcxH9Lbbz2aPZgXyvBoXkNnmxXwuY', verified='2026-11-17'),
      dict(slug='gifter-escrow', learn='escrow', program='45C1bSkFCbjrqiQHqm8oS6J88jirW8rC46Qiu6TvoY6x', verified='2026-11-17'),
    ]
    def lesson_of(x):
      return dict(title=x['slug'], summary='A recorded lesson.', objectives=['Read the account.'])
    paths = lib.write(S, page, '', live, lesson_of, lambda x: True, lambda x: 'guided', lambda x: 'A recorded limit.', lambda s, n: s)
    self.assertIn('/library/papers/', paths)
    self.assertIn('/library/papers/solana-whitepaper/', paths)
    self.assertIn('/library/papers/guardian-signer/', paths)
    self.assertIn('/library/papers/solana-a-new-architecture-for-a-high-performance-blockchain/', paths)
    self.assertIn('/library/papers/relax-entry-constraints/', paths)
    index = open(S + '/library/papers/index.html').read()
    self.assertIn('Proof of History', index)
    self.assertIn('Helium white paper', index)
    self.assertIn('does not contain the word Solana', index)
    self.assertNotIn('peer-reviewed', index.lower())
    data = json.load(open(S + '/library/papers/catalogue.json'))
    self.assertEqual(len(data), len(papers.papers()))
    home = open(S + '/library/index.html').read()
    self.assertIn('id="r-paper-solana-whitepaper"', home)
    self.assertIn('data-search=', home)
    self.assertIn('Proof of History', home)
    self.assertIn('White papers and design notes', home)
    signer = open(S + '/library/papers/guardian-signer/index.html').read()
    self.assertIn('does not contain the word Solana', signer)
    self.assertIn('github.com/wormhole-foundation/wormhole', signer)
    self.assertIn('id="full-reading"', signer)
    self.assertIn('ScholarlyArticle', signer)
    self.assertIn('section-by-section reading', open(S + '/library/papers/index.html').read())
    sol_page = open(S + '/library/papers/solana-a-new-architecture-for-a-high-performance-blockchain/index.html').read()
    self.assertIn('id="full-reading"', sol_page)
    self.assertIn('Proof of History', sol_page)
    self.assertIn('710,000', sol_page)
    self.assertIn('not a verbatim copy', sol_page.lower())
    self.assertGreater(len(sol_page.split()), 7000)
    alp = open(S + '/library/papers/solana-alpenglow-consensus-v1-2/index.html').read()
    self.assertIn('id="full-reading"', alp)
    self.assertIn('Quantumglow', alp)
    self.assertIn('20+20', alp.replace('“', '"').replace('”', '"'))
    constel = open(S + '/library/papers/solana-constellation-fair-internet-capital-markets/index.html').read()
    self.assertIn('id="full-reading"', constel)
    self.assertIn('50', constel)
    self.assertIn('v0.9', constel)
    uxd = open(S + '/library/papers/uxd-protocol-an-algorithmic-stablecoin-100-backed-by-a-delta-neutral-position/index.html').read()
    self.assertIn('id="full-reading"', uxd)
    self.assertIn('does not contain the word Solana', uxd)
    moved = open(S + '/library/papers/wormhole-guardian-signer/index.html').read()
    self.assertIn('noindex', moved.lower())
    self.assertIn('/library/papers/guardian-signer/', moved)
    simd = open(S + '/library/papers/relax-entry-constraints/index.html').read()
    self.assertIn('SIMD-0083', simd)
    self.assertIn('Accepted', simd)
    self.assertIn('<h1>Relax Entry Constraints</h1>', simd)
    self.assertIn('was not copied', simd.lower())
    llms = open(S + '/llms.txt').read()
    self.assertIn('/library/papers/solana-a-new-architecture-for-a-high-performance-blockchain/', llms)
    self.assertIn('/library/papers/relax-entry-constraints/', llms)
    self.assertIn('## Other', llms)
    script = index.split('<script>\n', 1)[1].split('</script>', 1)[0]
    open('/tmp/paper-search.js', 'w').write(script)
    self.assertNotIn('{{', script)

if __name__ == '__main__':
  unittest.main()
