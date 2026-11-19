"""Pre-launch consolidation safeguards."""
from __future__ import annotations

import json
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class PrelaunchIdentity(unittest.TestCase):
  def test_build_does_not_copy_legacy_spa(self):
    build = (ROOT / 'scripts' / 'build.py').read_text(encoding='utf-8')
    self.assertNotIn("shutil.copytree('legacy',OUT)", build)
    self.assertNotIn('Solar AI edge nodes programme', build)
    self.assertNotIn('Energy &amp; edge compute archive', build)
    self.assertNotIn('solar-powered AI', build)
    self.assertNotIn("OUT+'/edge-ai/", build)

  def test_landing_identity_and_ctas(self):
    html = (ROOT / 'scripts' / 'landing.html').read_text(encoding='utf-8')
    self.assertIn('Understand the code. Investigate the behaviour. Explain your work.', html)
    self.assertIn('Explore the learning path', html)
    self.assertIn('Browse lessons', html)
    self.assertIn('Register launch interest', html)
    self.assertNotIn('Join a cohort', html)
    self.assertNotIn('Enrol now', html)
    self.assertNotIn('Enroll now', html)
    self.assertNotIn('/edge-ai/', html)
    self.assertNotIn('solar-powered', html.lower())

  def test_prelaunch_pages_exist(self):
    import prelaunch_pages as pp
    learn = pp.learn_hub_html({'guided_lessons': 3, 'debug_challenges': 1, 'core_path_lessons': 2})
    self.assertIn('Learn Solana through application practice', learn)
    self.assertIn('generated from the curriculum registry', learn)
    teams = pp.for_teams_html('https://example.test/pilot')
    self.assertIn('Discuss a pilot', teams)
    self.assertIn('does not constitute enrolment', teams)

  def test_curriculum_registry_counts(self):
    import curriculum_registry as cr
    reg = cr.build_registry(ROOT)
    self.assertEqual(reg['schema'], 'sol.college.curriculum_registry/v1')
    self.assertIn('guided_lessons', reg['counts'])
    self.assertIn('debug_challenges', reg['counts'])
    self.assertTrue(reg['counting_rules']['previews_excluded_from_learning_totals'])
    self.assertGreater(reg['counts']['guided_lessons'], 0)

  def test_gifter_title_has_no_crash_suffix(self):
    L = json.loads((ROOT / 'dapps' / 'lessons' / 'gifter-escrow.json').read_text())
    self.assertNotIn('crashes', L.get('title', '').lower())
    self.assertIn('Gifter escrow', L.get('title', ''))

  def test_no_solar_phrases_in_active_scripts(self):
    banned = ('solar-powered AI', 'energy-to-compute', 'Sol Node Lab', 'Energy & edge')
    for rel in (
      'scripts/landing.html', 'scripts/landing.py', 'scripts/learning_layer.py',
      'scripts/prelaunch_pages.py', 'scripts/core_lessons.py',
    ):
      text = (ROOT / rel).read_text(encoding='utf-8')
      for phrase in banned:
        self.assertNotIn(phrase, text, rel)


if __name__ == '__main__':
  unittest.main()
