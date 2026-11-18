"""Picassol assessment rubric + resume-safety wiring."""
from __future__ import annotations
import json
import os
import tempfile
import unittest
from pathlib import Path

import learning_layer as ll


ROOT = Path(__file__).resolve().parent.parent


class LabAssessment(unittest.TestCase):
    def test_assessment_html_has_criteria_and_gates(self):
        L = json.loads((ROOT / 'dapps/lessons/picassol-hackathon.json').read_text())
        html = ll.assessment_html(L, 'picassol-hackathon')
        self.assertIn('Assessment rubric', html)
        self.assertIn('Criterion 1', html)
        self.assertIn('Mandatory honesty gates', html)
        self.assertIn('Observation ≠ practical mastery', html)
        self.assertIn('/lessons/picassol-hackathon/', html)

    def test_workspace_embeds_content_version_and_rubric_link(self):
        L = json.loads((ROOT / 'dapps/lessons/picassol-hackathon.json').read_text())
        html = ll.workspace_html(
            L['learning_loop'],
            '/dapps/picassol-hackathon/',
            [['create', 'abc']],
            content_version='2026-11-18.1',
            assess_href='/lessons/picassol-hackathon/assessment/',
        )
        self.assertIn('data-content-version="2026-11-18.1"', html)
        self.assertIn('/lessons/picassol-hackathon/assessment/', html)
        self.assertIn('lab-version-banner', html)
        self.assertIn('Live practical (my wallet)', html)
        self.assertIn('ev-route-tag', html)
        self.assertIn('attempt-sig', html)
        self.assertIn('inspect-stale', html)

    def test_lesson_js_restores_predict_lock_and_version(self):
        js = (ROOT / 'scripts/lesson.js').read_text()
        self.assertIn('data-content-version', js)
        self.assertIn('showPredictLockedUi', js)
        self.assertIn('lab-version-banner', js)
        self.assertIn('content_version', js)
        self.assertIn('observedAt', js)
        self.assertIn('routeTag', js)
        self.assertIn('My attempt (live)', js)

    def test_picassol_has_assessment_block(self):
        L = json.loads((ROOT / 'dapps/lessons/picassol-hackathon.json').read_text())
        self.assertIn('assessment', L)
        self.assertTrue(L['assessment'].get('purpose'))

    def test_namegen_has_learning_loop_and_assessment(self):
        L = json.loads((ROOT / 'dapps/lessons/c4-comets-todor-edward-andrei.json').read_text())
        self.assertIn('learning_loop', L)
        self.assertEqual(L['learning_loop'].get('predict_answer'), 'set')
        self.assertIn('assessment', L)
        html = ll.assessment_html(L, 'c4-comets-todor-edward-andrei')
        self.assertIn('NameGen', html)
        self.assertIn('Criterion 1', html)
        self.assertIn('init_user vs set_name', html)
        self.assertNotIn('Pixel account', html)

    def test_poe_has_learning_loop_and_lab_specific_criteria(self):
        L = json.loads((ROOT / 'dapps/lessons/poe-solana.json').read_text())
        self.assertIn('learning_loop', L)
        self.assertEqual(L['learning_loop'].get('predict_answer'), 'register_create')
        html = ll.assessment_html(L, 'poe-solana')
        self.assertIn('register_user then create_poll', html)
        self.assertNotIn('Pixel account', html)
        self.assertNotIn('update_pixel', html)

    def test_assessment_fallback_is_not_picassol_specific(self):
        html = ll.assessment_html({
            'title': 'Example Lab',
            'student_outcome': 'Explain a PDA seed',
            'learning_loop': {
                'explain_question': 'Why did seeds fail?',
                'transfer': 'Apply seeds on a fresh wallet.',
            },
            'assessment': {'purpose': 'Example purpose only.'},
        }, 'example-lab')
        self.assertIn('Example Lab', html)
        self.assertIn('Why did seeds fail?', html)
        self.assertNotIn('Pixel account', html)
        self.assertNotIn('update_pixel', html)

    def test_attempt_recovery_panel_and_js(self):
        html = ll.stuck_html()
        self.assertIn('attempt-recovery', html)
        self.assertIn('submitted_unknown', html)
        self.assertIn('wallet_rejected', html)
        self.assertIn('Do not send a second transaction', html)
        js = (ROOT / 'scripts/lesson.js').read_text()
        self.assertIn('ATTEMPT_GUIDE', js)
        self.assertIn('paintAttempt', js)
        self.assertIn('submitted_unknown', js)
        self.assertIn('attempt-recovery', js)


if __name__ == '__main__':
    unittest.main()
