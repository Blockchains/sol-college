"""Guardrails against known mobile horizontal-scroll causes."""
from __future__ import annotations
import os
import re
import unittest


HERE = os.path.dirname(os.path.abspath(__file__))


class MobileOverflowGuards(unittest.TestCase):
    def test_landing_marquee_avoids_100vw(self):
        with open(os.path.join(HERE, 'landing.css')) as f:
            css = f.read()
        # Full-bleed 100vw marquees cause horizontal scroll on mobile.
        self.assertNotRegex(css, r'\.marquee\s*\{[^}]*100vw')
        self.assertIn('overflow-x: clip', css)
        self.assertIn('.nav-fold > div {\n  display: none;', css)
        self.assertIn('.nav-fold[open] > div { display: flex; }', css)

    def test_lesson_css_clips_document(self):
        with open(os.path.join(HERE, 'lesson.css')) as f:
            css = f.read()
        self.assertIn('html{overflow-x:clip', css.replace(' ', ''))
        self.assertIn('overflow-x:auto', css)

    def test_top_css_wraps_on_small_screens(self):
        with open(os.path.join(HERE, 'core_lessons.py')) as f:
            src = f.read()
        self.assertIn('html,body{overflow-x:clip', src)
        self.assertIn('.top{flex-wrap:wrap', src)
        self.assertNotIn('.top{flex-wrap:nowrap', src)
        # Closed details menus must stay hidden when display:flex is used for open state.
        self.assertIn('.top nav details>div{display:none', src)
        self.assertIn('.top nav details[open]>div{display:flex}', src)

    def test_style_css_hides_closed_nav_menus(self):
        with open(os.path.join(HERE, 'style.css')) as f:
            css = f.read()
        self.assertIn('.top nav details>div{display:none', css)
        self.assertIn('.top nav details[open]>div{display:flex}', css)
        self.assertIn('.top{display:flex;flex-wrap:wrap', css)


if __name__ == '__main__':
    unittest.main()
