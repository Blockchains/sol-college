"""The Degen reading edition is sourced close reading, not a news report."""
import html, os, re, shutil, tempfile, unittest
import degen_edition as edition
import standard

def page(body, title, desc, path):
  return ('<!doctype html><html><head><meta charset=utf-8><title>' + html.escape(title) +
    '</title><meta name=description content="' + html.escape(desc, quote=True) +
    '"></head><body><main id=main>' + body + '</main></body></html>')

# Triple-quoted prose in standard.py and standard_depth.py on main at ed2beca.
CHARTER_WORDS = 4121

class Readings(unittest.TestCase):
  def test_ten_times_the_charter_and_the_empty_newsroom(self):
    rows = edition.readings()
    self.assertGreaterEqual(len(rows), 50)
    self.assertEqual(len(rows), len({r['slug'] for r in rows}))
    self.assertGreaterEqual(edition.word_count(), CHARTER_WORDS * 10)
    blob = '\n'.join(r['search'] for r in rows).lower()
    for phrase in ('award-winning', 'sources told', 'we interviewed', 'a student said', 'hot coin'):
      self.assertNotIn(phrase, blob)
    for needle in ('seed vault', '500', 'launchlab', 'metadao', 'jito', 'velocity', 'usdt'):
      self.assertIn(needle, blob)
    for r in rows:
      self.assertLessEqual(len(r['desc']), 158)
      self.assertRegex(r['desc'], re.compile(r'\b(not|no|never|without)\b', re.I))
      self.assertTrue(r['sources'])
      for src in r['sources']:
        self.assertTrue(src['url'].startswith('https://'))
      self.assertIn('17 Nov 2026', ' '.join(s['note'] for s in r['sources']))

  def test_pages_keep_the_unpublished_newsroom(self):
    S = tempfile.mkdtemp(prefix='degen-')
    self.addCleanup(shutil.rmtree, S)
    open(S + '/llms.txt', 'w').write('# Sol.College\n\n## The Degen\nold\n\n## Other\nkeep\n')
    paths = standard.write(S, page, '')
    self.assertIn('/degen/', paths)
    self.assertIn('/degen/readings/', paths)
    self.assertIn('/degen/readings/degen-mode-starts-the-slider-at-125-times/', paths)
    home = open(S + '/degen/index.html').read()
    self.assertIn('No report has been published.', home)
    self.assertIn('Seed Vault', home)
    self.assertIn('data-paper=', home)
    self.assertNotIn('award-winning', home.lower())
    desks = open(S + '/degen/desks/index.html').read()
    self.assertGreaterEqual(desks.count('No story is filed on this desk.'), 7)
    self.assertIn('No document reading is filed on this desk.', desks)
    board = open(S + '/degen/assignments/index.html').read()
    self.assertGreaterEqual(board.count('Assignment. Not reported. No finding.'), 10)
    index = open(S + '/degen/readings/index.html').read()
    self.assertIn('No report has been published.', index)
    self.assertIn('data-desk-filter', index)
    self.assertIn('500', index)
    one = open(S + '/degen/readings/the-fork-dropped-high-leverage-and-changed-the-dollar/index.html').read()
    self.assertIn('USDT', one)
    self.assertIn('No account was funded', one)
    self.assertIn('https://docs.velocity.exchange/developers/migrate-from-drift.md', one)
    llms = open(S + '/llms.txt').read()
    self.assertIn('/degen/readings/the-fork-dropped-high-leverage-and-changed-the-dollar/', llms)
    self.assertIn('## Other', llms)
    self.assertNotIn('\nold\n', llms)
    moved = open(S + '/standard/index.html').read()
    self.assertIn('noindex', moved.lower())
    self.assertFalse(os.path.exists(S + '/standard/readings/index.html'))

if __name__ == '__main__':
  unittest.main()
