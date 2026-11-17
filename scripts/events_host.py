"""Public host wording for Solana Calendar listings.

The site build reads scripts/events_host.json and does not call Luma.
Guest lists, guest counts, answers, and guests-only coordinates are not stored.
A description is the host page's text. It is not a Sol.College recap.
"""
from __future__ import annotations
import json, re, urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'events_host.json'
API = 'https://api.lu.ma/calendar/get-items'
EVENT = 'https://api.lu.ma/event/get'
CALENDAR_ID = 'cal-cl57AMcV2gdbbau'


def _get(url):
    import time
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'sol-college-events/1.0', 'Accept': 'application/json',
            })
            with urllib.request.urlopen(req, timeout=30) as res:
                return json.loads(res.read().decode('utf-8'))
        except Exception as exc:
            last = exc
            time.sleep(1 + attempt)
    raise last


def _inline(node):
    if not isinstance(node, dict):
        return ''
    kind = node.get('type')
    if kind == 'text':
        return node.get('text') or ''
    if kind == 'hard_break':
        return '\n'
    return ''.join(_inline(child) for child in node.get('content') or [])


def scrub(text):
    """Drop a Google account id that share links sometimes carry."""
    return re.sub(r'([?&])ouid=[^&\s]+', r'\1', text)


def description_blocks(mirror):
    blocks = []
    for node in (mirror or {}).get('content') or []:
        text = scrub(_inline(node).replace('\u00a0', ' '))
        lines = [' '.join(line.split()) for line in text.split('\n')]
        lines = [line for line in lines if line]
        if lines:
            blocks.append('\n'.join(lines))
    return blocks


def questions(rows):
    kept = []
    for row in rows or []:
        label = ' '.join((row.get('label') or '').split())
        if not label:
            continue
        kept.append({
            'label': label,
            'required': bool(row.get('required')),
            'question_type': row.get('question_type') or '',
            'has_terms': bool(row.get('terms')),
        })
    return kept


def bios(hosts):
    kept = []
    for host in hosts or []:
        name = ' '.join((host.get('name') or '').split())
        bio = ' '.join((host.get('bio_short') or '').split())
        if name and bio:
            kept.append({'name': name, 'bio': bio})
    return kept


def copy_for(entry):
    ev = entry.get('event') or {}
    api = ev.get('api_id') or ''
    if not api:
        raise ValueError('event without api id')
    detail = _get(EVENT + '?event_api_id=' + api)
    geo = (detail.get('event') or {}).get('geo_address_info') or {}
    return {
        'source_id': api,
        'url': ev.get('url') or '',
        'title': (ev.get('name') or '').strip(),
        'blocks': description_blocks(detail.get('description_mirror')),
        'questions': questions(detail.get('registration_questions')),
        'bios': bios(detail.get('hosts')),
        'place_note': ' '.join((geo.get('description') or '').split()),
    }


def build():
    checked = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    payload = _get(API + '?calendar_api_id=' + CALENDAR_ID + '&period=future&pagination_limit=50')
    if payload.get('has_more'):
        raise SystemExit('events_host: more pages than this import reads')
    rows = []
    for entry in payload.get('entries') or []:
        rows.append(copy_for(entry))
    blob = json.dumps(rows)
    lowered = blob.lower()
    for banned in ('guest_count', 'guest_data', 'featured_guests', 'ticket_count'):
        if banned in lowered:
            raise SystemExit('events_host: guest field stored ' + banned)
    return {
        'retrieved_at': checked,
        'note': 'Host-page wording for events on the Superteam calendar. Question labels are the form, not anyone\'s answers. Guest lists are not stored.',
        'events': rows,
    }


def main():
    data = build()
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('events_host:', len(data['events']), 'descriptions, retrieved', data['retrieved_at'])


if __name__ == '__main__':
    main()
