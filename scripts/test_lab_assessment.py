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

    def test_gree_has_learning_loop_and_metaplex_criteria(self):
        L = json.loads((ROOT / 'dapps/lessons/gree.json').read_text())
        self.assertIn('learning_loop', L)
        self.assertEqual(L['learning_loop'].get('predict_answer'), 'new_mint')
        html = ll.assessment_html(L, 'gree')
        self.assertIn('Metaplex', html)
        self.assertIn('fresh mint keypair', html)
        self.assertNotIn('Pixel account', html)
        self.assertNotIn('update_pixel', html)

    def test_trustlock_has_learning_loop_and_deadline_criteria(self):
        L = json.loads((ROOT / 'dapps/lessons/trustlock.json').read_text())
        self.assertIn('learning_loop', L)
        self.assertEqual(L['learning_loop'].get('predict_answer'), 'reject')
        html = ll.assessment_html(L, 'trustlock')
        self.assertIn('DeadlineExceeded', html)
        self.assertIn('Clock', html)
        self.assertNotIn('Pixel account', html)
        self.assertNotIn('update_pixel', html)

    def test_gifter_has_learning_loop_and_vault_criteria(self):
        L = json.loads((ROOT / 'dapps/lessons/gifter-escrow.json').read_text())
        self.assertIn('learning_loop', L)
        self.assertEqual(L['learning_loop'].get('predict_answer'), 'maker_only')
        html = ll.assessment_html(L, 'gifter-escrow')
        self.assertIn('maker', html.lower())
        self.assertIn('PDA', html)
        self.assertIn('45C1bSkF', html)
        self.assertNotIn('Pixel account', html)
        self.assertNotIn('update_pixel', html)

    def test_all_stage1_path_labs_have_learning_loop(self):
        stage1 = [
            'picassol-hackathon',
            'c4-comets-todor-edward-andrei',
            'poe-solana',
            'gree',
            'trustlock',
            'gifter-escrow',
        ]
        for slug in stage1:
            L = json.loads((ROOT / f'dapps/lessons/{slug}.json').read_text())
            self.assertIn('learning_loop', L, slug)
            self.assertIn('assessment', L, slug)
            self.assertTrue(L['assessment'].get('criteria'), slug)

    def test_ciphervault_has_learning_loop_and_threshold_criteria(self):
        L = json.loads((ROOT / 'dapps/lessons/ciphervault.json').read_text())
        self.assertEqual(L.get('path_stage'), 2)
        self.assertIn('learning_loop', L)
        self.assertEqual(L['learning_loop'].get('predict_answer'), 'wait')
        html = ll.assessment_html(L, 'ciphervault')
        self.assertIn('threshold', html.lower())
        self.assertIn('leftover', html.lower())
        self.assertNotIn('Pixel account', html)
        self.assertNotIn('update_pixel', html)

    def test_mandatekey_has_learning_loop_and_revoke_criteria(self):
        L = json.loads((ROOT / 'dapps/lessons/mandatekey.json').read_text())
        self.assertEqual(L.get('path_stage'), 2)
        self.assertIn('learning_loop', L)
        self.assertEqual(L['learning_loop'].get('predict_answer'), 'blocked')
        html = ll.assessment_html(L, 'mandatekey')
        self.assertIn('revoked', html.lower())
        self.assertIn('pay', html.lower())
        self.assertNotIn('Pixel account', html)
        self.assertNotIn('update_pixel', html)

    def test_trust_protocol_has_learning_loop_and_init_criteria(self):
        L = json.loads((ROOT / 'dapps/lessons/trust-protocol.json').read_text())
        self.assertEqual(L.get('path_stage'), 2)
        self.assertIn('learning_loop', L)
        self.assertEqual(L['learning_loop'].get('predict_answer'), 'fail_exists')
        html = ll.assessment_html(L, 'trust-protocol')
        self.assertIn('protocol-config', html)
        self.assertIn('bond-vault-v2', html)
        self.assertNotIn('Pixel account', html)
        self.assertNotIn('update_pixel', html)

    def test_zeroai_has_learning_loop_and_stale_pyth_criteria(self):
        L = json.loads((ROOT / 'dapps/lessons/zeroai.json').read_text())
        self.assertEqual(L.get('path_stage'), 2)
        self.assertIn('learning_loop', L)
        self.assertEqual(L['learning_loop'].get('predict_answer'), 'zeros_ok')
        html = ll.assessment_html(L, 'zeroai')
        self.assertIn('closeprice', html.lower())
        self.assertIn('60', html)
        self.assertNotIn('Pixel account', html)
        self.assertNotIn('update_pixel', html)

    def test_oculus_has_learning_loop_and_pause_criteria(self):
        L = json.loads((ROOT / 'dapps/lessons/oculus.json').read_text())
        self.assertEqual(L.get('path_stage'), 2)
        self.assertIn('learning_loop', L)
        self.assertEqual(L['learning_loop'].get('predict_answer'), 'paused')
        html = ll.assessment_html(L, 'oculus')
        self.assertIn('paused', html.lower())
        self.assertIn('LimitBreached', html)
        self.assertNotIn('Pixel account', html)
        self.assertNotIn('update_pixel', html)

    def test_agentx_has_learning_loop_and_active_oracle_criteria(self):
        L = json.loads((ROOT / 'dapps/lessons/agentx.json').read_text())
        self.assertEqual(L.get('path_stage'), 2)
        self.assertIn('learning_loop', L)
        self.assertEqual(L['learning_loop'].get('predict_answer'), 'need_active')
        html = ll.assessment_html(L, 'agentx')
        self.assertIn('Active', html)
        self.assertIn('registry.authority', html)
        self.assertNotIn('Pixel account', html)
        self.assertNotIn('update_pixel', html)

    def test_naim_has_learning_loop_and_token_config_criteria(self):
        L = json.loads((ROOT / 'dapps/lessons/naim.json').read_text())
        self.assertEqual(L.get('path_stage'), 2)
        self.assertIn('learning_loop', L)
        self.assertEqual(L['learning_loop'].get('predict_answer'), 'need_token_cfg')
        html = ll.assessment_html(L, 'naim')
        self.assertIn('init_token_config', html)
        self.assertIn('registration_period', html)
        self.assertNotIn('Pixel account', html)
        self.assertNotIn('update_pixel', html)

    def test_all_stage2_path_labs_have_learning_loop(self):
        stage2 = [
            'ciphervault',
            'mandatekey',
            'trust-protocol',
            'zeroai',
            'oculus',
            'agentx',
            'naim',
        ]
        for slug in stage2:
            L = json.loads((ROOT / f'dapps/lessons/{slug}.json').read_text())
            self.assertEqual(L.get('path_stage'), 2, slug)
            self.assertIn('learning_loop', L, slug)
            self.assertIn('assessment', L, slug)
            self.assertTrue(L['assessment'].get('criteria'), slug)

    def test_sentient_send_has_learning_loop_and_payout_criteria(self):
        L = json.loads((ROOT / 'dapps/lessons/sentient-send.json').read_text())
        self.assertEqual(L.get('path_stage'), 3)
        self.assertIn('learning_loop', L)
        self.assertEqual(L['learning_loop'].get('predict_answer'), 'yes_wins')
        html = ll.assessment_html(L, 'sentient-send')
        self.assertIn('winner-takes-all', html.lower().replace(' ', '-').replace('—', '-'))
        # also accept spaced form
        self.assertTrue('winner' in html.lower() and 'pool' in html.lower())
        self.assertIn('32', html)
        self.assertNotIn('Pixel account', html)
        self.assertNotIn('update_pixel', html)

    def test_colosseum_has_learning_loop_and_lock_criteria(self):
        L = json.loads((ROOT / 'dapps/lessons/colosseum.json').read_text())
        self.assertEqual(L.get('path_stage'), 3)
        self.assertIn('learning_loop', L)
        self.assertEqual(L['learning_loop'].get('predict_answer'), 'refuse')
        html = ll.assessment_html(L, 'colosseum')
        self.assertIn('lock', html.lower())
        self.assertIn('31,536,000', html)
        self.assertNotIn('Pixel account', html)
        self.assertNotIn('update_pixel', html)

    def test_orboracle_has_learning_loop_and_weight_lock_criteria(self):
        L = json.loads((ROOT / 'dapps/lessons/orboracle-solana.json').read_text())
        self.assertEqual(L.get('path_stage'), 3)
        self.assertIn('learning_loop', L)
        self.assertEqual(L['learning_loop'].get('predict_answer'), 'after_lock')
        html = ll.assessment_html(L, 'orboracle-solana')
        self.assertIn('half-life', html.lower())
        self.assertIn('lock', html.lower())
        self.assertNotIn('Pixel account', html)
        self.assertNotIn('update_pixel', html)

    def test_all_stage3_path_labs_have_learning_loop(self):
        stage3 = ['sentient-send', 'colosseum', 'orboracle-solana']
        for slug in stage3:
            L = json.loads((ROOT / f'dapps/lessons/{slug}.json').read_text())
            self.assertEqual(L.get('path_stage'), 3, slug)
            self.assertIn('learning_loop', L, slug)
            self.assertIn('assessment', L, slug)
            self.assertTrue(L['assessment'].get('criteria'), slug)

    def test_elective_batch1_learning_loops(self):
        batch = {
            'guild-protocol': 'fee_high',
            'qvac-marketplace': 'provider_pda',
            'agenttrust': 'revoked_flag',
            'agenc-protocol': 'config_only',
            'forge-agent-bounty': 'init_only',
        }
        for slug, answer in batch.items():
            L = json.loads((ROOT / f'dapps/lessons/{slug}.json').read_text())
            self.assertEqual(L.get('track'), 'elective', slug)
            self.assertIn('learning_loop', L, slug)
            self.assertEqual(L['learning_loop'].get('predict_answer'), answer, slug)
            ids = {o['id'] for o in L['learning_loop'].get('predict_options') or []}
            self.assertIn(answer, ids, slug)
            self.assertTrue(L.get('assessment', {}).get('criteria'), slug)
            self.assertTrue(L.get('student_outcome'), slug)
            html = ll.assessment_html(L, slug)
            self.assertNotIn('Pixel account', html, slug)
            self.assertNotIn('update_pixel', html, slug)
            # criterion titles should appear
            self.assertIn(L['assessment']['criteria'][0]['title'].split()[0], html)

    def test_elective_batch2_learning_loops(self):
        batch = {
            'hydra': 'reject',
            'agent-bazaar': 'invalid',
            'agentvault': 'explain_reject',
            'orrery': 'bad',
            'reddi-escrow': 'payee',
        }
        for slug, answer in batch.items():
            L = json.loads((ROOT / f'dapps/lessons/{slug}.json').read_text())
            self.assertEqual(L.get('track'), 'elective', slug)
            self.assertEqual(L.get('path_stage'), 'apply', slug)
            self.assertIn('learning_loop', L, slug)
            self.assertEqual(L['learning_loop'].get('predict_answer'), answer, slug)
            ids = {o['id'] for o in L['learning_loop'].get('predict_options') or []}
            self.assertIn(answer, ids, slug)
            self.assertTrue(L.get('assessment', {}).get('criteria'), slug)
            html = ll.assessment_html(L, slug)
            self.assertNotIn('Pixel account', html, slug)
            self.assertNotIn('update_pixel', html, slug)

    def test_elective_batch3_learning_loops(self):
        batch = {
            'agentescrow': 'vault_bump',
            'pact-escrow': 'fail',
            'lattice-escrow': 'fail',
            'escrowagent': 'rejected',
            'agent-court': 'status',
            'allowance-solana': 'over',
        }
        for slug, answer in batch.items():
            L = json.loads((ROOT / f'dapps/lessons/{slug}.json').read_text())
            self.assertEqual(L.get('track'), 'elective', slug)
            self.assertIn('learning_loop', L, slug)
            self.assertEqual(L['learning_loop'].get('predict_answer'), answer, slug)
            ids = {o['id'] for o in L['learning_loop'].get('predict_options') or []}
            self.assertIn(answer, ids, slug)
            self.assertTrue(L.get('assessment', {}).get('criteria'), slug)
            html = ll.assessment_html(L, slug)
            self.assertNotIn('Pixel account', html, slug)
            self.assertNotIn('update_pixel', html, slug)

    def test_elective_batch4_learning_loops(self):
        batch = {
            'atlantid-programs': 'owner_ok',
            'covenant': 'need_signer',
            'otomat': 'err',
            'solagents-commerce': 'job_pda',
            'trustrail-pipelines': 'need_delegate',
            'veedor': 'missing',
        }
        for slug, answer in batch.items():
            L = json.loads((ROOT / f'dapps/lessons/{slug}.json').read_text())
            self.assertEqual(L.get('track'), 'elective', slug)
            self.assertIn('learning_loop', L, slug)
            self.assertEqual(L['learning_loop'].get('predict_answer'), answer, slug)
            ids = {o['id'] for o in L['learning_loop'].get('predict_options') or []}
            self.assertIn(answer, ids, slug)
            self.assertTrue(L.get('assessment', {}).get('criteria'), slug)
            html = ll.assessment_html(L, slug)
            self.assertNotIn('Pixel account', html, slug)
            self.assertNotIn('update_pixel', html, slug)

    def test_all_track_elective_lessons_have_learning_loop(self):
        for path in (ROOT / 'dapps' / 'lessons').glob('*.json'):
            L = json.loads(path.read_text())
            if L.get('track') != 'elective':
                continue
            self.assertIn('learning_loop', L, path.stem)
            self.assertTrue(L.get('assessment', {}).get('criteria'), path.stem)
            self.assertTrue(L.get('student_outcome'), path.stem)

    def test_elective_batch5_debug_catalogue_loops(self):
        batch = {
            'barn': 'accepted',
            'chinesepowered-solana-cypherpunk': 'succeeds',
            'friendstake': 'pays_x',
            'hackathon-prediction-market-solana': 'stuck',
            'web3-splitter': 'seeds',
        }
        for slug, answer in batch.items():
            L = json.loads((ROOT / f'dapps/lessons/{slug}.json').read_text())
            self.assertEqual(L.get('track'), 'elective', slug)
            self.assertEqual(L['learning_loop'].get('predict_answer'), answer, slug)
            ids = {o['id'] for o in L['learning_loop'].get('predict_options') or []}
            self.assertIn(answer, ids, slug)
            html = ll.assessment_html(L, slug)
            self.assertNotIn('Pixel account', html, slug)
            self.assertNotIn('update_pixel', html, slug)

    def test_elective_batch6_final_catalogue_loops(self):
        batch = {
            'pulsefund-sol': 'connected',
            'stakes-main': 'stale',
            'votara': 'reject_quorum',
            'devos-decentralized-voting': 'reopen',
        }
        for slug, answer in batch.items():
            L = json.loads((ROOT / f'dapps/lessons/{slug}.json').read_text())
            self.assertEqual(L.get('track'), 'elective', slug)
            self.assertEqual(L['learning_loop'].get('predict_answer'), answer, slug)
            ids = {o['id'] for o in L['learning_loop'].get('predict_options') or []}
            self.assertIn(answer, ids, slug)
            html = ll.assessment_html(L, slug)
            self.assertNotIn('Pixel account', html, slug)

    def test_all_guided_live_lessons_have_learning_loop(self):
        skip = {'excerpts', 'glossary', 'path'}
        live = {row['slug'] for row in json.loads((ROOT / 'dapps' / 'live.json').read_text())}
        missing = []
        for slug in sorted(live):
            if slug in skip:
                continue
            path = ROOT / 'dapps' / 'lessons' / f'{slug}.json'
            if not path.is_file():
                continue
            L = json.loads(path.read_text())
            if not (L.get('title') or L.get('summary')):
                continue
            if not L.get('learning_loop'):
                missing.append(slug)
        self.assertEqual(missing, [], f'live lessons missing learning_loop: {missing}')

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
