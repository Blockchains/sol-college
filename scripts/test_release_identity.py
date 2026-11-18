"""Release identity and public curriculum summary."""
from __future__ import annotations
import json
import os
import tempfile
import unittest
from pathlib import Path

import release_identity as ri


ROOT = Path(__file__).resolve().parent.parent


class ReleaseIdentity(unittest.TestCase):
    def test_build_release_separates_app_and_curriculum(self):
        rel = ri.build_release(ROOT)
        self.assertEqual(rel['schema'], 'sol.college.release/v1')
        self.assertTrue(rel['app_release'])
        self.assertTrue(rel['curriculum_version'])
        self.assertNotEqual(rel['app_release'], rel['curriculum_version'])
        self.assertTrue(rel['built_at'].endswith('Z'))
        self.assertFalse(rel['sensitive'])
        self.assertIn('guided_lessons', rel['counts'])
        self.assertGreater(rel['counts']['live_apps'], 0)

    def test_write_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            rel = ri.write_artifacts(td, ROOT)
            site = Path(td)
            self.assertTrue((site / 'release.json').is_file())
            self.assertTrue((site / 'curriculum.json').is_file())
            self.assertTrue((site / 'releases' / 'index.html').is_file())
            data = json.loads((site / 'release.json').read_text())
            self.assertEqual(data['app_release'], rel['app_release'])
            cur = json.loads((site / 'curriculum.json').read_text())
            self.assertEqual(cur['curriculum_version'], rel['curriculum_version'])
            self.assertEqual(cur['counts']['live_apps'], rel['counts']['live_apps'])
            self.assertTrue(cur['lessons'])
            page = (site / 'releases' / 'index.html').read_text()
            self.assertIn(rel['app_release'], page)
            self.assertIn('curriculum', page.lower())

    def test_inject_footer_and_meta(self):
        rel = ri.build_release(ROOT)
        html = '<html><head><title>x</title></head><body><footer><p>hi</p></footer></body></html>'
        out = ri.inject_into_html(html, rel)
        self.assertIn('sc-app-release', out)
        self.assertIn('id="sc-release"', out)
        self.assertIn(rel['git_sha_short'], out)
        # idempotent
        out2 = ri.inject_into_html(out, rel)
        self.assertEqual(out2.count('id="sc-release"'), 1)

    def test_curriculum_counts_match_live_inventory(self):
        live = json.loads((ROOT / 'dapps' / 'live.json').read_text())
        snap = ri.curriculum_snapshot(ROOT)
        self.assertEqual(snap['live_apps'], len(live))
        self.assertEqual(
            snap['guided_lessons'] + snap['debug_challenges'],
            len(live),
        )


class EnvironmentStatusCopy(unittest.TestCase):
    def test_environment_panel_separates_dimensions(self):
        import learning_layer as ll
        html = ll.environment_panel_html('2026-04-01', 'Clicked create on hosted UI; recolour via script')
        self.assertIn('Program flow', html)
        self.assertIn('Hosted UI', html)
        self.assertIn('Frontend / RPC', html)
        self.assertIn('not live uptime', html.lower())


if __name__ == '__main__':
    unittest.main()
