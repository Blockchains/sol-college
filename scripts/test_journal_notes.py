"""The appraisal series is a tenfold expansion of journal prose, and it stays prospective."""
import re
import unittest
import journal
import journal_appraisals as appraisals
import library_papers as papers

# Words in string literals longer than 40 characters in journal.py and
# journal_depth.py on origin/main, before this series. Tenfold means the
# appraisal prose alone clears ten times that count.
BASELINE = 8555


def _blob(note):
    return '\n'.join(note['paragraphs'])


class JournalNotes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notes = appraisals.notes()
        cls.by_slug = {n['slug']: n for n in cls.notes}

    def test_word_count_is_tenfold(self):
        self.assertGreaterEqual(appraisals.word_count(), BASELINE * 10)

    def test_one_note_per_retrieved_document(self):
        library = papers.papers()
        self.assertEqual(len(self.notes), len(library))
        self.assertEqual({n['slug'] for n in self.notes}, {r['slug'] for r in library})
        self.assertEqual(len(self.by_slug), len(self.notes))

    def test_titles_and_descriptions_are_unique_and_short(self):
        titles = [n['title'] for n in self.notes]
        self.assertEqual(len(titles), len(set(titles)))
        for n in self.notes:
            self.assertLessEqual(len(n['desc']), 158, n['slug'])
            self.assertRegex(n['desc'], r'\b(not|no|never)\b')
            self.assertTrue(n['paper']['source'].startswith('https://'), n['slug'])

    def test_pages_stay_prospective(self):
        banned = ('impact factor', 'issn ', ' doi:', 'award-winning', 'award winning')
        for n in self.notes:
            text = _blob(n).lower()
            self.assertIn('no observations have been collected.', text, n['slug'])
            self.assertIn('not peer-reviewed research', text, n['slug'])
            for b in banned:
                self.assertNotIn(b, text, n['slug'] + ' ' + b)
            self.assertNotIn('the study found', text, n['slug'])
            self.assertNotIn('we measured', text, n['slug'])

    def test_white_paper_figure_is_not_rerun(self):
        note = self.by_slug['solana-a-new-architecture-for-a-high-performance-blockchain']
        text = _blob(note)
        self.assertIn('710,000', text)
        self.assertIn('did not rerun', text.lower())
        self.assertIn('not a measurement of the live network', text.lower())

    def test_alpenglow_review_is_not_activation(self):
        note = self.by_slug['simd-0326-alpenglow']
        text = _blob(note)
        self.assertEqual(note['status'], 'Review')
        self.assertIn('does not mean this journal reviewed it', text)
        self.assertIn('cannot be quoted as a decision', text)
        self.assertNotIn('is now active', text.lower())

    def test_activated_label_is_not_a_cluster_reading(self):
        activated = [n for n in self.notes if n['status'] == 'Activated']
        self.assertGreater(len(activated), 50)
        text = _blob(activated[0])
        self.assertIn('not a row this journal stored from a cluster', text)

    def test_homepage_still_has_no_paper(self):
        home = journal.home_page()
        self.assertIn('No research paper has been published.', home)
        self.assertIn('not peer reviewed', home.lower())
        self.assertIn('/journal/notes/', home)
        self.assertNotIn('award', home.lower())
