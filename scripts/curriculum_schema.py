"""Canonical curriculum record checks for live lessons.

Does not rewrite lesson JSON on every build. Validates inventory against the
fields Release A expects, and annotates /curriculum.json with schema status.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_ALWAYS = ('title',)
REQUIRED_GUIDED = ('summary', 'time', 'difficulty', 'objectives', 'prereqs')
RECOMMENDED = (
  'student_outcome',
  'content_version',
  'content_review',
  'content_owner',
  'track',
  'delivery',
  'not_covered',
)


def load_lesson(root: Path, slug: str) -> dict[str, Any]:
  fp = root / 'dapps' / 'lessons' / f'{slug}.json'
  if not fp.is_file():
    return {}
  try:
    return json.loads(fp.read_text(encoding='utf-8'))
  except Exception:
    return {}


def is_guided(live_row: dict, lesson: dict) -> bool:
  functional = str(live_row.get('functional') or lesson.get('functional') or '').lower()
  return functional in (
    '', 'full', 'fully working', 'fully_working', 'fully-functional', 'fully functional'
  )


def resource_type(live_row: dict, lesson: dict) -> str:
  if not is_guided(live_row, lesson):
    return 'challenge'
  if lesson.get('draft'):
    return 'preview'
  return 'lesson'


def normalize_record(live_row: dict, lesson: dict) -> dict[str, Any]:
  slug = live_row.get('slug') or ''
  guided = is_guided(live_row, lesson)
  missing_required = []
  missing_recommended = []
  for key in REQUIRED_ALWAYS:
    if not (lesson.get(key) or live_row.get('name')):
      missing_required.append(key)
  if guided and lesson and not lesson.get('draft'):
    for key in REQUIRED_GUIDED:
      val = lesson.get(key)
      if val is None or val == '' or val == []:
        missing_required.append(key)
    for key in RECOMMENDED:
      val = lesson.get(key)
      if val is None or val == '' or val == []:
        missing_recommended.append(key)
  status = 'ok'
  if missing_required:
    status = 'missing_required'
  elif missing_recommended:
    status = 'missing_recommended'
  elif not lesson:
    status = 'auto_draft'

  return {
    'id': slug,
    'title': lesson.get('title') or live_row.get('name') or slug,
    'resource_type': resource_type(live_row, lesson),
    'track': lesson.get('track') or '',
    'path_stage': lesson.get('path_stage'),
    'path_order': lesson.get('path_order'),
    'time': lesson.get('time') or '',
    'difficulty': lesson.get('difficulty') or '',
    'student_outcome': lesson.get('student_outcome') or '',
    'content_version': lesson.get('content_version') or lesson.get('version') or '',
    'content_review': lesson.get('content_review') or '',
    'content_owner': lesson.get('content_owner') or '',
    'prereqs': lesson.get('prereqs') or [],
    'objectives': lesson.get('objectives') or [],
    'verified': live_row.get('verified') or '',
    'functional': 'full' if guided else (live_row.get('functional') or 'partial'),
    'ui_check': live_row.get('ui_check') or '',
    'schema_status': status,
    'missing_required': missing_required,
    'missing_recommended': missing_recommended,
  }


def load_foundations_catalog(root: Path) -> list[dict[str, Any]]:
  fp = root / 'dapps' / 'foundations' / 'catalog.json'
  if not fp.is_file():
    return []
  try:
    data = json.loads(fp.read_text(encoding='utf-8'))
  except Exception:
    return []
  return list(data.get('lessons') or [])


def normalize_foundation(row: dict[str, Any]) -> dict[str, Any]:
  """Schema row for foundations (not live.json apps)."""
  missing_required = []
  missing_recommended = []
  for key in ('title', 'student_outcome', 'content_version', 'objectives', 'prereqs'):
    val = row.get(key)
    if val is None or val == '' or val == []:
      missing_required.append(key)
  for key in ('content_review', 'content_owner', 'delivery', 'verification_status'):
    val = row.get(key)
    if val is None or val == '' or val == []:
      missing_recommended.append(key)
  status = 'ok'
  if missing_required:
    status = 'missing_required'
  elif missing_recommended:
    status = 'missing_recommended'
  return {
    'id': row.get('id') or '',
    'title': row.get('title') or row.get('id') or '',
    'resource_type': row.get('resource_type') or 'lesson',
    'track': 'foundations',
    'path_stage': 0,
    'path_order': row.get('number'),
    'time': row.get('time') or '',
    'difficulty': row.get('difficulty') or '',
    'student_outcome': row.get('student_outcome') or '',
    'content_version': row.get('content_version') or '',
    'content_review': row.get('content_review') or '',
    'content_owner': row.get('content_owner') or '',
    'prereqs': row.get('prereqs') or [],
    'objectives': row.get('objectives') or [],
    'verified': row.get('verification_status') or 'release_candidate',
    'functional': 'foundations_rc',
    'ui_check': '',
    'schema_status': status,
    'missing_required': missing_required,
    'missing_recommended': missing_recommended,
    'assessment_available': bool(row.get('assessment_available')),
    'has_learning_loop': bool(row.get('learning_loop')),
  }


def audit_inventory(root: str | Path = '.') -> dict[str, Any]:
  root = Path(root)
  live = json.loads((root / 'dapps' / 'live.json').read_text(encoding='utf-8'))
  records = []
  missing_required_total = 0
  missing_recommended_total = 0
  for row in live:
    lesson = load_lesson(root, row['slug'])
    rec = normalize_record(row, lesson)
    records.append(rec)
    if rec['missing_required']:
      missing_required_total += 1
    if rec['missing_recommended']:
      missing_recommended_total += 1
  foundations = [normalize_foundation(r) for r in load_foundations_catalog(root)]
  foundations_missing_required = sum(1 for r in foundations if r['missing_required'])
  return {
    'lessons': records,
    'foundations': foundations,
    'summary': {
      'live_apps': len(live),
      'missing_required_lessons': missing_required_total,
      'missing_recommended_lessons': missing_recommended_total,
      'ok_lessons': sum(1 for r in records if r['schema_status'] == 'ok'),
      'foundations': len(foundations),
      'foundations_missing_required': foundations_missing_required,
      'foundations_with_learning_loop': sum(1 for r in foundations if r.get('has_learning_loop')),
    },
  }


def assert_picassol_contract(root: str | Path = '.') -> None:
  """Hard gate for the vertical-slice lesson used in Release B."""
  root = Path(root)
  live = {x['slug']: x for x in json.loads((root / 'dapps' / 'live.json').read_text(encoding='utf-8'))}
  row = live['picassol-hackathon']
  lesson = load_lesson(root, 'picassol-hackathon')
  rec = normalize_record(row, lesson)
  if rec['missing_required']:
    raise AssertionError(f'Picassol missing required fields: {rec["missing_required"]}')
  for key in ('student_outcome', 'content_version', 'learning_loop', 'track', 'delivery'):
    if key == 'learning_loop':
      if not lesson.get('learning_loop'):
        raise AssertionError('Picassol missing learning_loop')
    elif not lesson.get(key):
      raise AssertionError(f'Picassol missing {key}')
