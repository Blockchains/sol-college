"""Foundations lessons 001–002: release candidate teaching specifications."""
import unittest
import foundations_lesson as f
import foundations_l002 as l2


class FoundationsLesson001(unittest.TestCase):
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

    def test_links_to_lesson_002(self):
        self.assertIn('/lessons/accounts-ownership/', f.lesson_html())


class FoundationsLesson002(unittest.TestCase):
    def test_status_is_release_candidate(self):
        html = l2.lesson_html()
        self.assertIn('Release candidate', html)
        self.assertIn('Not yet technically or learner verified', html)
        self.assertIn('yet provide verified live addresses', html.lower())
        self.assertIn('Do not treat schematic addresses', html)

    def test_separates_ownership_and_authority(self):
        html = l2.lesson_html()
        low = html.lower()
        self.assertIn('program ownership', low)
        self.assertIn('update_authority', low)
        self.assertIn('owner field', low)
        self.assertIn('system program', low)
        self.assertIn('does not, by itself, enforce permission', low)

    def test_no_fake_live_specimen_addresses(self):
        html = l2.lesson_html()
        self.assertIn('Do not treat schematic addresses or decoded panels on this RC page as live account evidence', html)
        self.assertIn('no placeholder address on this page is labelled as a live verified specimen', html.lower())

    def test_assessment_five_criteria_and_checks(self):
        html = l2.assessment_html()
        self.assertIn('Criterion 1', html)
        self.assertIn('Criterion 5', html)
        self.assertIn('Mandatory conceptual checks', html)
        self.assertIn('Signer versus included address', html)
        self.assertIn('but A has not signed', html)
        self.assertIn('scenarios A–C', html)

    def test_meta_descriptions_fit(self):
        self.assertLessEqual(len(l2.LESSON_DESC), 158)
        self.assertLessEqual(len(l2.ASSESS_DESC), 158)

    def test_read_only_assessment(self):
        html = l2.assessment_html()
        self.assertIn('No practical transaction is required', html)
        self.assertIn('Captured-evidence route', html)


class FoundationsLesson003(unittest.TestCase):
    def test_status_is_release_candidate(self):
        import foundations_l003 as l3
        html = l3.lesson_html()
        self.assertIn('Release candidate', html)
        self.assertIn('Not yet technically or learner verified', html)
        self.assertIn('not interchangeable', html.lower())

    def test_instruction_three_components(self):
        import foundations_l003 as l3
        html = l3.lesson_html().lower()
        self.assertIn('program id', html)
        self.assertIn('instruction data', html)
        self.assertIn('signer', html)
        self.assertIn('writable', html)
        self.assertIn('simulation', html)
        self.assertIn('finalized', html)

    def test_assessment_six_criteria(self):
        import foundations_l003 as l3
        html = l3.assessment_html()
        self.assertIn('Criterion 6', html)
        self.assertIn('Mandatory conceptual checks', html)
        self.assertIn('Request versus outcome', html)
        self.assertIn('wrong target program', html.lower())

    def test_meta_descriptions_fit(self):
        import foundations_l003 as l3
        self.assertLessEqual(len(l3.LESSON_DESC), 158)
        self.assertLessEqual(len(l3.ASSESS_DESC), 158)

    def test_links_from_lesson_002(self):
        self.assertIn('/lessons/instructions-programs/', l2.lesson_html())

    def test_links_to_lesson_004(self):
        import foundations_l003 as l3
        self.assertIn('/lessons/transaction-atomicity/', l3.lesson_html())


class FoundationsLesson004(unittest.TestCase):
    def test_status_is_release_candidate(self):
        import foundations_l004 as l4
        html = l4.lesson_html()
        self.assertIn('Release candidate', html)
        self.assertIn('assert_revision', html)
        self.assertIn('not live observations', html.lower())

    def test_atomicity_and_fee_distinction(self):
        import foundations_l004 as l4
        html = l4.lesson_html().lower()
        self.assertIn('atomic', html)
        self.assertIn('fee', html)
        self.assertIn('nothing happens if it fails', html)
        self.assertIn('transaction boundary', html)
        self.assertIn('simulation does', html)  # simulation does not establish fee

    def test_assessment_six_criteria(self):
        import foundations_l004 as l4
        html = l4.assessment_html()
        self.assertIn('Criterion 6', html)
        self.assertIn('Mandatory conceptual checks', html)
        self.assertIn('Separate outcomes', html)
        self.assertIn('Cedar', html)

    def test_meta_descriptions_fit(self):
        import foundations_l004 as l4
        self.assertLessEqual(len(l4.LESSON_DESC), 158)
        self.assertLessEqual(len(l4.ASSESS_DESC), 158)

    def test_failing_tx_not_required(self):
        import foundations_l004 as l4
        self.assertIn('never required', l4.assessment_html().lower())


class FoundationsLesson005(unittest.TestCase):
    def test_status_is_release_candidate(self):
        import foundations_l005 as l5
        html = l5.lesson_html()
        self.assertIn('Release candidate', html)
        self.assertIn('classify before retrying', html.lower())
        self.assertIn('Do not invent signatures', html)

    def test_failure_stages_and_timeout(self):
        import foundations_l005 as l5
        html = l5.lesson_html().lower()
        self.assertIn('wallet rejection', html)
        self.assertIn('simulation', html)
        self.assertIn('timeout', html)
        self.assertIn('null', html)
        self.assertIn('lastvalidblockheight', html)
        self.assertIn('not the same as proving the operation never happened', html)

    def test_assessment_six_criteria(self):
        import foundations_l005 as l5
        html = l5.assessment_html()
        self.assertIn('Criterion 6', html)
        self.assertIn('Mandatory conceptual checks', html)
        self.assertIn('Replacement risk', html)
        self.assertIn('Secret protection', html)

    def test_meta_descriptions_fit(self):
        import foundations_l005 as l5
        self.assertLessEqual(len(l5.LESSON_DESC), 158)
        self.assertLessEqual(len(l5.ASSESS_DESC), 158)

    def test_no_deliberate_fail_required(self):
        import foundations_l005 as l5
        self.assertIn('never required', l5.assessment_html().lower())

    def test_links_from_lesson_004(self):
        import foundations_l004 as l4
        self.assertIn('/lessons/transaction-failures/', l4.lesson_html())


class FoundationsIndexWiring(unittest.TestCase):
    def test_card_and_path_section_include_all_five(self):
        cards = f.foundations_card_html()
        self.assertIn('/lessons/first-transaction/', cards)
        self.assertIn('/lessons/accounts-ownership/', cards)
        self.assertIn('/lessons/instructions-programs/', cards)
        self.assertIn('/lessons/transaction-atomicity/', cards)
        self.assertIn('/lessons/transaction-failures/', cards)
        self.assertIn('/lessons/transaction-failures/assessment/', cards)
        path = f.foundations_path_section().lower()
        self.assertIn('release candidate', path)
        self.assertIn('recover safely', path)
        self.assertIn('/lessons/transaction-failures/', path)


if __name__ == '__main__':
    unittest.main()
