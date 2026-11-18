"""Trust and catalogue consistency: status language, path order, lesson metadata."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TrustConsistency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.live = {x['slug']: x for x in json.loads((ROOT / 'dapps' / 'live.json').read_text())}
        cls.lessons = {}
        for p in (ROOT / 'dapps' / 'lessons').glob('*.json'):
            if p.name in ('path.json', 'excerpts.json', 'glossary.json'):
                continue
            cls.lessons[p.stem] = json.loads(p.read_text())
        cls.path = json.loads((ROOT / 'dapps' / 'lessons' / 'path.json').read_text())

    def test_path_orders_are_contiguous_within_stages(self):
        for st in self.path['stages']:
            items = sorted(
                (d['path_order'], slug)
                for slug, d in self.lessons.items()
                if d.get('path_stage') == st['id'] and d.get('path_order') is not None
            )
            self.assertTrue(items, st['id'])
            orders = [o for o, _ in items]
            self.assertEqual(orders, list(range(orders[0], orders[0] + len(orders))), st['id'])
            self.assertEqual(len(orders), len(set(orders)), 'duplicate path_order in stage %s' % st['id'])

    def test_stages_do_not_interleave_path_orders(self):
        ranges = []
        for st in self.path['stages']:
            orders = [
                d['path_order']
                for d in self.lessons.values()
                if d.get('path_stage') == st['id'] and d.get('path_order') is not None
            ]
            self.assertTrue(orders)
            ranges.append((min(orders), max(orders), st['id']))
        ranges.sort()
        for i in range(1, len(ranges)):
            self.assertEqual(ranges[i][0], ranges[i - 1][1] + 1, ranges)

    def test_guided_full_lessons_have_difficulty_and_time(self):
        for slug, row in self.live.items():
            if row.get('functional') != 'full':
                continue
            d = self.lessons.get(slug)
            if not d or d.get('draft'):
                continue
            self.assertTrue(d.get('difficulty'), slug)
            self.assertTrue(d.get('time'), slug)
            self.assertRegex(str(d['difficulty']), r'^(Beginner|Intermediate|Advanced)$', slug)

    def test_lesson_functional_matches_live_when_set(self):
        for slug, d in self.lessons.items():
            if slug not in self.live or not d.get('functional'):
                continue
            self.assertEqual(d['functional'], self.live[slug].get('functional'), slug)

    def test_gifter_is_full_and_findings_are_past_tense(self):
        self.assertEqual(self.live['gifter-escrow']['functional'], 'full')
        self.assertEqual(self.lessons['gifter-escrow']['functional'], 'full')
        import landing
        gifter = next(f for f in landing.FEATURED_FINDINGS if f['slug'] == 'gifter-escrow')
        self.assertIn('was broken', gifter['title'].lower())
        self.assertIn('now completes', gifter['text'].lower())
        self.assertNotIn('can never complete', gifter['text'].lower())

    def test_homepage_proof_copy_avoids_fully_working(self):
        html = (ROOT / 'scripts' / 'landing.html').read_text()
        self.assertNotIn('fully working environments', html)
        self.assertIn('environments with recorded core flows', html)

    def test_campus_lead_does_not_call_all_projects_participating(self):
        text = (ROOT / 'campus' / 'index.html').read_text()
        self.assertNotIn('Each participating project has its own CTO agent', text)
        self.assertIn('independent demonstration forks', text)


if __name__ == '__main__':
    unittest.main()
