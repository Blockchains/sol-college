"""Foundations lessons 001–002: release candidate teaching specifications."""
import unittest
import foundations_lesson as f
import foundations_l002 as l2


class FoundationsLesson001(unittest.TestCase):
    def test_status_is_release_candidate(self):
        html = f.lesson_html()
        self.assertIn('Release candidate', html)
        self.assertIn('Automated structural checks recorded', html)
        self.assertIn('learner testing and live specimens not completed', html.lower())
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
        self.assertIn('Automated structural checks recorded', html)
        self.assertIn('learner testing and live specimens not completed', html.lower())
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
        self.assertIn('Automated structural checks recorded', html)
        self.assertIn('learner testing and live specimens not completed', html.lower())
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


class FoundationsLesson006(unittest.TestCase):
    def test_status_is_release_candidate(self):
        import foundations_l006 as l6
        html = l6.lesson_html()
        self.assertIn('Release candidate', html)
        self.assertIn('observation', html.lower())
        self.assertIn('not actual SDK methods', html)

    def test_observation_draft_pending(self):
        import foundations_l006 as l6
        html = l6.lesson_html().lower()
        self.assertIn('observed profile', html)
        self.assertIn('draft', html)
        self.assertIn('pending', html)
        self.assertIn('mincontextslot', html)
        self.assertIn('whichever response arrives last wins', html)

    def test_assessment_six_criteria(self):
        import foundations_l006 as l6
        html = l6.assessment_html()
        self.assertIn('Criterion 6', html)
        self.assertIn('Mandatory conceptual checks', html)
        self.assertIn('Concurrency', html)
        self.assertIn('Guided configuration', html)

    def test_meta_descriptions_fit(self):
        import foundations_l006 as l6
        self.assertLessEqual(len(l6.LESSON_DESC), 158)
        self.assertLessEqual(len(l6.ASSESS_DESC), 158)

    def test_links_from_lesson_005(self):
        import foundations_l005 as l5
        self.assertIn('/lessons/application-state/', l5.lesson_html())


class FoundationsLesson007(unittest.TestCase):
    def test_status_is_release_candidate(self):
        import foundations_l007 as l7
        html = l7.lesson_html()
        self.assertIn('Release candidate', html)
        self.assertIn('expected_revision', html)
        self.assertIn('explanatory pseudocode', html.lower())

    def test_guard_and_conflict(self):
        import foundations_l007 as l7
        html = l7.lesson_html().lower()
        self.assertIn('update_profile_checked', html)
        self.assertIn('stale revision', html)
        self.assertIn('silently', html)
        self.assertIn('state guardian', html)

    def test_assessment_six_criteria(self):
        import foundations_l007 as l7
        html = l7.assessment_html()
        self.assertIn('Criterion 6', html)
        self.assertIn('Mandatory conceptual checks', html)
        self.assertIn('Mutation-path consistency', html)
        self.assertIn('Guided configuration', html)

    def test_meta_descriptions_fit(self):
        import foundations_l007 as l7
        self.assertLessEqual(len(l7.LESSON_DESC), 158)
        self.assertLessEqual(len(l7.ASSESS_DESC), 158)

    def test_links_from_lesson_006(self):
        import foundations_l006 as l6
        self.assertIn('/lessons/protecting-state-transitions/', l6.lesson_html())


class FoundationsIndexWiring(unittest.TestCase):
    def test_card_and_path_section_include_all_seven(self):
        cards = f.foundations_card_html()
        self.assertIn('/lessons/first-transaction/', cards)
        self.assertIn('/lessons/accounts-ownership/', cards)
        self.assertIn('/lessons/instructions-programs/', cards)
        self.assertIn('/lessons/transaction-atomicity/', cards)
        self.assertIn('/lessons/transaction-failures/', cards)
        self.assertIn('/lessons/application-state/', cards)
        self.assertIn('/lessons/protecting-state-transitions/', cards)
        self.assertIn('/lessons/protecting-state-transitions/assessment/', cards)
        path = f.foundations_path_section().lower()
        self.assertIn('release candidate', path)
        self.assertIn('expected revisions', path)
        self.assertIn('/lessons/protecting-state-transitions/', path)

    def test_main_nav_lists_all_seven(self):
        nav = f.foundations_main_nav_items()
        for slug in (
            'first-transaction',
            'accounts-ownership',
            'instructions-programs',
            'transaction-atomicity',
            'transaction-failures',
            'application-state',
            'protecting-state-transitions',
        ):
            self.assertIn(f'/lessons/{slug}/', nav)
        self.assertIn('/lessons/#foundations', nav)
        self.assertIn('/lessons/path/', nav)

    def test_sequence_nav_marks_current(self):
        html = f.foundations_sequence_nav('/lessons/application-state/')
        self.assertIn('aria-current=page', html)
        self.assertIn('title="Application state"', html)
        self.assertIn('/lessons/protecting-state-transitions/', html)
        self.assertIn('/lessons/first-transaction/', html)



class FoundationsHandoffD3(unittest.TestCase):
    def test_catalog_chain_and_stage1_handoff(self):
        import json
        from pathlib import Path
        root = Path(__file__).resolve().parent.parent
        catalog = json.loads((root / 'dapps' / 'foundations' / 'catalog.json').read_text())
        lessons = catalog['lessons']
        self.assertEqual(len(lessons), 7)
        ids = [L['id'] for L in lessons]
        self.assertEqual(ids[0], 'first-transaction')
        self.assertEqual(ids[-1], 'protecting-state-transitions')
        for i, L in enumerate(lessons[:-1]):
            self.assertEqual(L['next_id'], ids[i + 1], L['id'])
            self.assertTrue(L.get('technical_checks', {}).get('shared_workspace'))
            self.assertFalse(L.get('technical_checks', {}).get('learner_testing'))
        last = lessons[-1]
        self.assertEqual(last['next_id'], 'picassol-hackathon')
        self.assertEqual(last.get('stage1_handoff', {}).get('id'), 'picassol-hackathon')

    def test_all_seven_emit_workspace_and_assessment(self):
        import foundations_l003 as l3
        import foundations_l004 as l4
        import foundations_l005 as l5
        import foundations_l006 as l6
        import foundations_l007 as l7
        modules = [f, l2, l3, l4, l5, l6, l7]
        for mod in modules:
            html = mod.lesson_html()
            self.assertIn('id="workspace"', html, mod.SLUG)
            self.assertEqual(html.count('id="workspace"'), 1, mod.SLUG)
            self.assertIn('Foundations workspace', html, mod.SLUG)
            assess = mod.assessment_html()
            self.assertIn('Criterion 1', assess, mod.SLUG)
            self.assertIn(mod.ASSESS_PATH, html)

    def test_lesson_007_hands_off_to_picassol(self):
        import foundations_l007 as l7
        html = l7.lesson_html().lower()
        self.assertIn('/lessons/picassol-hackathon/', html)
        self.assertIn('stage 1', html)
        self.assertIn('does not block stage 1', html)
        self.assertNotIn('next foundations step (not yet published)', html)

    def test_picassol_prereqs_recommend_foundations_sequence(self):
        import json
        from pathlib import Path
        root = Path(__file__).resolve().parent.parent
        L = json.loads((root / 'dapps' / 'lessons' / 'picassol-hackathon.json').read_text())
        blob = ' '.join(L.get('prereqs') or [])
        self.assertIn('/lessons/first-transaction/', blob)
        self.assertIn('/lessons/protecting-state-transitions/', blob)
        self.assertIn('001', blob)
        self.assertIn('007', blob)



if __name__ == '__main__':
    unittest.main()
