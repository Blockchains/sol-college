"""Curriculum inventory and public-copy consistency checks."""
from __future__ import annotations
import json
import os
import unittest

import curriculum_copy as cc


class FormatHelpers(unittest.TestCase):
    def test_format_limit_flattens_lists(self):
        self.assertEqual(
            cc.format_limit_text(['Disputes', 'timeout reclaim']),
            'Disputes; timeout reclaim',
        )
        self.assertNotIn('[', cc.format_limit_text(['a', 'b']))
        self.assertEqual(
            cc.format_limit_text("[\"first\", \"second\"]"),
            'first; second',
        )

    def test_format_prereq_resolves_slug(self):
        def resolve(slug):
            return f'[Title](/lessons/{slug}/)' if slug == 'guild-protocol' else None
        self.assertEqual(
            cc.format_prereq('guild-protocol', resolve),
            '[Title](/lessons/guild-protocol/)',
        )
        self.assertEqual(
            cc.format_prereq('A wallet on Devnet.', resolve),
            'A wallet on Devnet.',
        )


class InventoryRecords(unittest.TestCase):
    def test_live_and_path_stage_split(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        live = json.load(open(os.path.join(root, 'dapps/live.json')))
        path = json.load(open(os.path.join(root, 'dapps/lessons/path.json')))
        staged_ids = {st['id'] for st in path.get('stages', [])}
        # Count lessons that declare a staged path_stage.
        guided_staged = 0
        guided_elective = 0
        for row in live:
            slug = row['slug']
            fp = os.path.join(root, 'dapps/lessons', f'{slug}.json')
            if not os.path.isfile(fp):
                continue
            L = json.load(open(fp))
            if L.get('functional') not in (None, '', 'full', 'fully working', 'fully_working', 'fully-functional', 'fully functional'):
                # Skip explicit non-full lesson docs when present.
                if str(L.get('functional')).lower() in ('partial', 'part', 'debug', 'incomplete'):
                    continue
            stage = L.get('path_stage')
            if stage in staged_ids:
                guided_staged += 1
            elif stage is not None:
                guided_elective += 1
        self.assertGreater(guided_staged, 0)
        self.assertGreaterEqual(guided_elective, 0)

    def test_picassol_claims_softened(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        L = json.load(open(os.path.join(root, 'dapps/lessons/picassol-hackathon.json')))
        blob = json.dumps(L)
        self.assertIn('fresh local deployment', blob)
        self.assertIn('scheduling opportunities still depend', blob)
        self.assertIn('Faucet availability', blob)
        self.assertNotIn('About 1 SOL arrives within a few seconds', blob)
        self.assertIn('Account count is the source of truth', blob)

    def test_list_not_covered_formats_for_proof(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        L = json.load(open(os.path.join(root, 'dapps/lessons/veedor.json')))
        raw = L.get('not_covered')
        self.assertIsInstance(raw, list)
        text = cc.format_limit_text(raw)
        self.assertTrue(text)
        self.assertNotIn('[', text)
        self.assertIn(';', text)


if __name__ == '__main__':
    unittest.main()
