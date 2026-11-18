"""Curriculum schema audit and Picassol contract gate."""
from __future__ import annotations
import json
import unittest
from pathlib import Path

import curriculum_schema as cs


ROOT = Path(__file__).resolve().parent.parent


class CurriculumSchema(unittest.TestCase):
    def test_audit_runs_on_live_inventory(self):
        audit = cs.audit_inventory(ROOT)
        self.assertEqual(audit['summary']['live_apps'], 47)
        self.assertTrue(audit['lessons'])
        self.assertEqual(audit['summary']['missing_required_lessons'], 0)
        pic = next(r for r in audit['lessons'] if r['id'] == 'picassol-hackathon')
        self.assertEqual(pic['schema_status'], 'ok')
        self.assertEqual(pic['missing_required'], [])
        self.assertIn('content_version', pic)
        self.assertTrue(pic['content_version'])

    def test_former_gap_lessons_have_objectives_and_prereqs(self):
        for slug in (
            'agentescrow', 'pact-escrow', 'solagents-commerce', 'lattice-escrow',
            'trustrail-pipelines', 'veedor', 'atlantid-programs', 'allowance-solana',
            'escrowagent', 'agent-court', 'covenant', 'otomat',
        ):
            L = json.loads((ROOT / 'dapps' / 'lessons' / f'{slug}.json').read_text())
            self.assertTrue(L.get('objectives'), slug)
            self.assertTrue(L.get('prereqs'), slug)
            self.assertTrue(L.get('student_outcome'), slug)
            self.assertTrue(L.get('content_version'), slug)
            self.assertEqual(L.get('track'), 'elective', slug)

    def test_picassol_contract(self):
        cs.assert_picassol_contract(ROOT)

    def test_release_notice_script_exists(self):
        js = (ROOT / 'scripts' / 'release-notice.js').read_text(encoding='utf-8')
        self.assertIn('/release.json', js)
        self.assertIn('sc-release-seen', js)
        self.assertIn('Reload', js)

    def test_picassol_hosted_recolour_honesty(self):
        live = {x['slug']: x for x in json.loads((ROOT / 'dapps' / 'live.json').read_text())}
        ui = live['picassol-hackathon']['ui_check'].lower()
        self.assertIn('create', ui)
        self.assertIn('recolour', ui)
        self.assertIn('not yet', ui)
        L = json.loads((ROOT / 'dapps' / 'lessons' / 'picassol-hackathon.json').read_text())
        self.assertIn('Hosted-UI recolour is not yet recorded', L['not_covered'])


if __name__ == '__main__':
    unittest.main()
