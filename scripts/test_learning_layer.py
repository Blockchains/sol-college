"""Learning-layer vertical slice: front door, preflight, Picassol loop."""
from __future__ import annotations
import json
import os
import unittest

import learning_layer as ll


class LearningLayerHtml(unittest.TestCase):
    def test_start_section_has_three_routes_and_quiz(self):
        html = ll.start_section_html()
        self.assertIn('id="start"', html)
        self.assertIn('New to Solana', html)
        self.assertIn('Already a developer', html)
        self.assertIn('Here to investigate', html)
        self.assertIn('/lessons/first-transaction/', html)
        self.assertIn('/lessons/picassol-hackathon/', html)
        self.assertIn('id="start-form"', html)
        self.assertIn('id="start-resume"', html)
        self.assertIn('not proof of mastery', html)
        self.assertIn('/lessons/path/', html)

    def test_landing_js_wires_homepage_resume(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        js = open(os.path.join(root, 'scripts/landing.js'), encoding='utf-8').read()
        self.assertIn("getElementById('start-resume')", js)
        self.assertIn('sc-lesson-last', js)
        self.assertIn('start-resume-go', js)

    def test_preflight_offers_observation_and_practical(self):
        html = ll.preflight_html('/dapps/picassol-hackathon/', 'Picassol')
        self.assertIn('data-mode="observe"', html)
        self.assertIn('data-mode="practical"', html)
        self.assertIn('not graded', html.lower())
        self.assertIn('Devnet', html)

    def test_workspace_has_predict_act_inspect(self):
        loop = {
            'objective': 'Test objective',
            'predict_question': 'Will it update?',
            'predict_options': [{'id': 'update', 'label': 'Update'}],
            'predict_answer': 'update',
            'predict_why': 'Because PDA exists',
            'act': 'Do the thing',
            'inspect': [{'id': 'coord', 'label': 'Coordinate', 'placeholder': 'x,y'}],
            'explain_question': 'Why?',
            'transfer': 'Try another coordinate',
        }
        html = ll.workspace_html(loop, '/dapps/picassol-hackathon/', [('create', 'abc123')])
        self.assertIn('data-learning="workspace"', html)
        self.assertIn('data-loop-step="predict"', html)
        self.assertIn('Platform historical', html)
        self.assertIn('data-predict-answer="update"', html)

    def test_picassol_json_has_learning_loop(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        L = json.load(open(os.path.join(root, 'dapps/lessons/picassol-hackathon.json')))
        self.assertIn('learning_loop', L)
        self.assertEqual(L['learning_loop']['predict_answer'], 'update')
        self.assertIn('student_outcome', L)

    def test_landing_template_wires_start_section(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        html = open(os.path.join(root, 'scripts/landing.html')).read()
        self.assertIn('{{START_SECTION}}', html)
        self.assertIn('href="#start"', html)
        self.assertIn('Start learning', html)

    def test_path_progress_wiring_in_sources(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        core = open(os.path.join(root, 'scripts/core_lessons.py'), encoding='utf-8').read()
        js = open(os.path.join(root, 'scripts/lesson.js'), encoding='utf-8').read()
        self.assertIn('def path_progress_html', core)
        self.assertIn('id="path-progress"', core)
        self.assertIn('path-progress-data', core)
        self.assertIn('path-progress-clear', core)
        self.assertIn('path-progress-export', core)
        self.assertIn("not</b> proof of mastery", core)
        self.assertIn("getElementById('path-progress')", js)
        self.assertIn('path-progress-clear', js)
        self.assertIn('path-progress-export', js)
        self.assertIn('sol-college-local-progress.json', js)
        self.assertIn('Not mastery or assessment completion', js)
        self.assertIn('sc-lesson-loop', js)
        self.assertIn('touched on this device', js)
        # Used on both catalogue and path pages
        self.assertGreaterEqual(core.count('path_progress_html()'), 2)

    def test_card_touch_marks_from_loop(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        js = open(os.path.join(root, 'scripts/lesson.js'), encoding='utf-8').read()
        css = open(os.path.join(root, 'scripts/lesson.css'), encoding='utf-8').read()
        core = open(os.path.join(root, 'scripts/core_lessons.py'), encoding='utf-8').read()
        self.assertIn("load('sc-lesson-loop')", js)
        self.assertIn('Touched on this device', js)
        self.assertIn('is-touched', js)
        self.assertIn('card-touch', js)
        self.assertIn('.card.is-touched', css)
        self.assertIn('.card .card-touch', css)
        self.assertIn('finder-touch', core)
        self.assertIn('data-touch=touched', core)
        self.assertIn("c.classList.contains('is-touched')", js)

    def test_picassol_recolour_harness_steps(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        harness = open(os.path.join(root, 'tests/devnet/wallet_click.py'), encoding='utf-8').read()
        self.assertIn("elif app == 'picassol':", harness)
        self.assertIn('click_pixel_create', harness)
        self.assertIn('click_pixel_recolour', harness)
        self.assertIn('lastClickTime', harness)


if __name__ == '__main__':
    unittest.main()
