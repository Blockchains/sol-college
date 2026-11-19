"""Single curriculum registry for published lessons, challenges and references.

Counts for homepage, directory and path pages must be derived from this registry
(or from the same audit that writes it). Do not hand-repeat catalogue totals.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_json(path: Path):
  if not path.exists():
    return None
  return json.loads(path.read_text(encoding='utf-8'))


def build_registry(root: Path | None = None) -> dict:
  root = Path(root or ROOT)
  live = _load_json(root / 'dapps' / 'live.json') or []
  foundations = (_load_json(root / 'dapps' / 'foundations' / 'catalog.json') or {}).get('lessons') or []
  try:
    import curriculum_schema as cs
    audit = cs.audit_inventory(str(root))
  except Exception:
    audit = {'lessons': [], 'foundations': []}

  by_slug = {r.get('slug'): r for r in (audit.get('lessons') or []) if r.get('slug')}
  entries = []

  for app in live:
    slug = app.get('slug')
    if not slug:
      continue
    lesson_path = root / 'dapps' / 'lessons' / f'{slug}.json'
    L = _load_json(lesson_path) or {}
    aud = by_slug.get(slug) or {}
    ready = aud.get('readiness') or ''
    track = L.get('track') or ''
    if track == 'debug-laboratory' or ready == 'challenge':
      ctype = 'debug_challenge'
      pub = 'published'
    elif ready == 'preview':
      ctype = 'preview'
      pub = 'preview'
    elif L or lesson_path.exists():
      ctype = 'guided_lesson'
      pub = 'published'
    else:
      ctype = 'preview'
      pub = 'draft'
    entries.append({
      'content_id': f'lesson:{slug}',
      'title': L.get('title') or app.get('name') or slug,
      'slug': slug,
      'content_type': ctype,
      'publication_status': pub,
      'level': L.get('difficulty') or '',
      'prerequisites': L.get('prereqs') or [],
      'learning_objectives': L.get('objectives') or [],
      'estimated_duration': L.get('time') or '',
      'path_stage': L.get('path_stage'),
      'path_order': L.get('path_order'),
      'associated_lab_version': {
        'program_id': app.get('program'),
        'fork_commit': app.get('commit'),
        'verified_date': app.get('verified'),
        'functional': app.get('functional'),
      },
      'reviewer': L.get('content_owner') or 'Sol.College curriculum',
      'last_review_date': L.get('content_review') or app.get('verified') or '',
      'content_version': L.get('content_version') or '',
    })

  for row in foundations:
    slug = row.get('id')
    entries.append({
      'content_id': f'foundation:{slug}',
      'title': row.get('title') or slug,
      'slug': slug,
      'content_type': 'guided_lesson',
      'publication_status': 'release_candidate',
      'level': row.get('difficulty') or 'Beginner',
      'prerequisites': row.get('prereqs') or [],
      'learning_objectives': row.get('objectives') or [],
      'estimated_duration': row.get('time') or '',
      'path_stage': 0,
      'path_order': row.get('number'),
      'associated_lab_version': None,
      'reviewer': row.get('content_owner') or 'Sol.College curriculum',
      'last_review_date': row.get('content_review') or '',
      'content_version': row.get('content_version') or '',
      'verification_status': row.get('verification_status') or 'release_candidate',
    })

  published_guided = [e for e in entries if e['content_type'] == 'guided_lesson' and e['publication_status'] == 'published']
  published_challenges = [e for e in entries if e['content_type'] == 'debug_challenge' and e['publication_status'] == 'published']
  previews = [e for e in entries if e['publication_status'] in ('preview', 'draft')]
  foundations_rc = [e for e in entries if e['content_id'].startswith('foundation:')]
  core_path = [e for e in published_guided if e.get('path_stage') in (1, 2, 3)]
  practice_envs = [a for a in live if (a.get('functional') or '') == 'full']

  return {
    'schema': 'sol.college.curriculum_registry/v1',
    'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'counting_rules': {
      'published_only_for_learning_totals': True,
      'guided_and_debug_counted_separately': True,
      'practice_environments_separate_from_content': True,
      'previews_excluded_from_learning_totals': True,
      'foundations_release_candidates_listed_separately': True,
    },
    'counts': {
      'guided_lessons': len(published_guided),
      'debug_challenges': len(published_challenges),
      'core_path_lessons': len(core_path),
      'previews': len(previews),
      'foundations_release_candidates': len(foundations_rc),
      'practice_environments_full': len(practice_envs),
      'live_apps': len(live),
    },
    'entries': entries,
  }


def write_registry(site_dir: str | Path, root: Path | None = None) -> dict:
  reg = build_registry(root)
  site = Path(site_dir)
  site.mkdir(parents=True, exist_ok=True)
  (site / 'curriculum-registry.json').write_text(json.dumps(reg, indent=2) + '\n', encoding='utf-8')
  # Also store under dapps for source-of-truth consumers
  out = (root or ROOT) / 'dapps' / 'curriculum_registry.json'
  out.write_text(json.dumps(reg, indent=2) + '\n', encoding='utf-8')
  return reg


def write_lab_manifests(root: Path | None = None) -> int:
  """Write per-lab manifests from live.json. Missing values stay null — never guessed."""
  root = Path(root or ROOT)
  live = _load_json(root / 'dapps' / 'live.json') or []
  labs_dir = root / 'dapps' / 'labs'
  labs_dir.mkdir(parents=True, exist_ok=True)
  n = 0
  for app in live:
    slug = app.get('slug')
    if not slug:
      continue
    functional = app.get('functional')
    if functional == 'full':
      test_status = 'passed_recorded_test'
    elif functional == 'partial':
      test_status = 'failed_recorded_test'
    else:
      test_status = 'not_tested'
    manifest = {
      'lab_id': slug,
      'lab_version': app.get('commit') or None,
      'upstream': {
        'repository': app.get('upstream') or app.get('original') or None,
        'commit': None,
      },
      'practice_fork': {
        'repository': app.get('fork') or None,
        'commit': app.get('commit') or None,
        'patch_set': None,
      },
      'deployment': {
        'network': 'devnet',
        'program_id': app.get('program') or None,
        'idl_hash': None,
        'frontend_build_id': None,
      },
      'verification': {
        'latest_run_id': app.get('log') or app.get('verified') or None,
        'test_status': test_status,
        'verified_date': app.get('verified') or None,
        'method': app.get('flow') or app.get('ui_check') or None,
        'evidence': {
          'steps': app.get('steps') or [],
          'functional_evidence': app.get('functional_evidence') or None,
          'ui_check': app.get('ui_check') or None,
          'log': app.get('log') or None,
        },
      },
      'limitations': [x for x in [app.get('limits')] if x],
      'standard_limitation': (
        'Practice-environment evidence records specified behaviour under stated conditions. '
        'It is not a security audit, a guarantee of current availability or an endorsement of production use.'
      ),
      'practice_boundary': (
        'This exercise applies only to the environment identified on this page. '
        'It does not authorise testing the original project or any production deployment.'
      ),
    }
    (labs_dir / f'{slug}.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    n += 1
  return n


if __name__ == '__main__':
  reg = write_registry(ROOT / 'site')
  n = write_lab_manifests()
  print('registry counts', reg['counts'], 'labs', n)
