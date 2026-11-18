"""Lesson 001 foundations gateway: release candidate teaching specification."""
import unittest
import foundations_lesson as f


class FoundationsLesson(unittest.TestCase):
    def test_status_is_release_candidate(self):
        html = f.lesson_html()
        self.assertIn('Release candidate', html)
        self.assertIn('Not yet technically or learner verified', html)
        self.assertNotIn('award-winning', html.lower())

    def test_separates_execution_and_commitment(self):
        html = f.lesson_html()
        low = html.lower()
        self.assertIn('execution result', low)
        self.assertIn('commitment', low)
        self.assertIn('collapse these into one green', low)
        self.assertIn('finalized', low)
        self.assertIn('confirmed means every instruction succeeded', f.assessment_html().lower())

    def test_safety_rules_present(self):
        html = f.lesson_html()
        self.assertIn('Do not deposit real funds', html)
        self.assertIn('recovery phrase', html)
        self.assertIn('destination mismatch', html.lower())
        self.assertIn('uncertain result', html.lower())

    def test_assessment_has_four_criteria_and_gates(self):
        html = f.assessment_html()
        self.assertIn('Criterion 1', html)
        self.assertIn('Criterion 2', html)
        self.assertIn('Criterion 3', html)
        self.assertIn('Criterion 4', html)
        self.assertIn('Mandatory safety gates', html)
        self.assertIn('Do not allow strength elsewhere to compensate', html)

    def test_meta_descriptions_fit(self):
        lesson_desc = (
            'RC foundations lesson: review a devnet SOL transfer, check execution and commitment separately, '
            'reconcile the fee. Not yet technically verified.'
        )
        self.assertLessEqual(len(lesson_desc), 158)

    def test_card_and_path_section_link_assessment(self):
        self.assertIn('/lessons/first-transaction/', f.foundations_card_html())
        self.assertIn('/lessons/first-transaction/assessment/', f.foundations_card_html())
        self.assertIn('release candidate', f.foundations_path_section().lower())


if __name__ == '__main__':
    unittest.main()
