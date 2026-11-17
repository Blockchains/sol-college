"""Pull public Superteam calendar fields into scripts/events_data.json.

The site build reads that file and does not call Luma. Guest lists, profile
images, and venue coordinates marked guests-only are not stored. A title is
never turned into a future date. Re-running this replaces the Superteam
snapshot and keeps the hackathon archive and the unpublished queue.
"""
from __future__ import annotations
import json, re, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
OUT = HERE / 'events_data.json'
API = 'https://api.lu.ma/calendar/get-items'
CALENDAR_ID = 'cal-cl57AMcV2gdbbau'
CALENDAR_URL = 'https://luma.com/superteam'
SOURCE_NAME = 'Superteam calendar on Luma'
CHECKED_NOTE = 'Ticket flag, time, timezone, city, and public venue come from this response. Guest lists are not copied.'

CITY_EN = {'دبي': 'Dubai', 'أبو ظبي': 'Abu Dhabi', 'Beograd': 'Belgrade'}
TAG_COUNTRY = {
    'UK': 'United Kingdom', 'UAE': 'United Arab Emirates', 'Canada': 'Canada',
    'Germany': 'Germany', 'Australia': 'Australia', 'Japan': 'Japan',
}
RESERVED = {
    'submit', 'queue', 'coverage', 'sources', 'college', 'archive', 'cities',
    'countries', 'feeds', 'series', 'events', 'calendar',
}

ARCHIVE = [
    ('solana-frontier', 'Solana Frontier', '2026-04', '2026-04'),
    ('prediction-markets-hackathon', 'Prediction Markets Hackathon', '2026-03', '2026-03'),
    ('graveyard-hackathon', 'Graveyard Hackathon', '2026-02', '2026-02'),
    ('privacy-hack', 'Privacy Hack', '2026-01', '2026-02'),
    ('solana-cypherpunk', 'Solana Cypherpunk', '2025-09', '2025-09'),
    ('solana-breakout', 'Solana Breakout', '2025-04', '2025-04'),
    ('solana-radar', 'Solana Radar', '2024-09', '2024-09'),
    ('solana-renaissance', 'Solana Renaissance', '2024-03', '2024-03'),
    ('solana-hyperdrive', 'Solana Hyperdrive', '2023-09', '2023-09'),
    ('solana-grizzlython', 'Solana Grizzlython', '2023-02', '2023-02'),
    ('solana-summer-camp', 'Solana Summer Camp', '2022-07', '2022-07'),
    ('solana-riptide', 'Solana Riptide', '2022-02', '2022-02'),
    ('solana-ignition', 'Solana Ignition', '2021-08', '2021-08'),
    ('solana-season', 'Solana Season', '2021-05', '2021-05'),
    ('solana-defi', 'Solana DeFi', '2021-02', '2021-02'),
    ('solana-inaugural-hackathon', "Solana's Inaugural Hackathon", '2020-10', '2020-10'),
]
ARCHIVE_CHECKED = '2026-11-17T10:40:00Z'
ARCHIVE_URL = 'https://solana.com/hackathons'


def slugify(s):
    s = s.casefold()
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s or 'event'


def fetch_superteam():
    q = urllib.parse.urlencode({
        'calendar_api_id': CALENDAR_ID, 'period': 'future', 'pagination_limit': '50',
    })
    req = urllib.request.Request(API + '?' + q, headers={
        'User-Agent': 'sol-college-events/1.0', 'Accept': 'application/json',
    })
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.loads(res.read().decode('utf-8'))
    if data.get('has_more'):
        raise SystemExit('events: Superteam response has more pages than this import reads')
    return data.get('entries') or []


def _city(geo):
    raw = (geo.get('city') or '').strip()
    if not raw:
        return '', ''
    return CITY_EN.get(raw, raw), raw


def classify(title):
    t = title.casefold()
    if 'co-working' in t or 'coworking' in t:
        return 'coworking', 'build', ['Solana', 'Coworking']
    if 'bootcamp' in t:
        return 'bootcamp', 'learn', ['Solana', 'Students']
    if 'estudiantes' in t or 'for students' in t:
        return 'workshop', 'learn', ['Solana', 'Students']
    if 'rust' in t:
        return 'meetup', 'learn', ['Solana', 'Rust']
    if 'community call' in t:
        return 'call', 'participate', ['Solana', 'Community call']
    if 'demo' in t:
        return 'showcase', 'explore', ['Solana']
    if 'coffee' in t or 'mixer' in t:
        return 'meetup', 'meet', ['Solana']
    social = ('padel', 'pilates', 'muay', 'yoga', 'arcade', 'lunch', 'soir', 'yacht',
              'dunes', 'weihnacht', 'after party', 'pub crawl', 'equestrian', 'flow')
    if any(w in t for w in social):
        return 'social', 'enjoy', ['Solana']
    return 'meetup', 'meet', ['Solana']


def _times(start_at, end_at, tz_name):
    if not start_at or not tz_name:
        raise ValueError('missing start or timezone')
    tz = ZoneInfo(tz_name)
    start = datetime.fromisoformat(start_at.replace('Z', '+00:00')).astimezone(tz)
    end = datetime.fromisoformat(end_at.replace('Z', '+00:00')).astimezone(tz) if end_at else None
    return start, end


def normalise_superteam(entry, checked_at):
    ev = entry.get('event') or {}
    geo = ev.get('geo_address_info') or {}
    ticket = entry.get('ticket_info') or {}
    title = (ev.get('name') or '').strip()
    if not title:
        raise ValueError('event without a title')
    tz_name = ev.get('timezone') or ''
    start, end = _times(ev.get('start_at'), ev.get('end_at'), tz_name)
    loc_type = ev.get('location_type') or ''
    if loc_type in ('zoom', 'meet'):
        fmt = 'online'
    elif loc_type == 'offline':
        fmt = 'in-person'
    else:
        raise ValueError('unknown location type ' + loc_type + ' for ' + title)
    public = ev.get('geo_address_visibility') == 'public' and geo.get('mode') == 'shown' and geo.get('address')
    if fmt == 'online':
        public = False
    city, city_listed = ('', '') if fmt == 'online' else _city(geo)
    if fmt == 'online':
        country, country_code = '', ''
    else:
        country = (geo.get('country') or '').strip()
        country_code = (geo.get('country_code') or '').strip()
    tags = [t.get('name') for t in (entry.get('tags') or []) if t.get('name')]
    country_from_tag = False
    if fmt != 'online' and not country:
        tagged = [TAG_COUNTRY[t] for t in tags if t in TAG_COUNTRY]
        if len(set(tagged)) == 1:
            country = tagged[0]
            country_from_tag = True
    if fmt == 'online':
        tagged = [TAG_COUNTRY[t] for t in tags if t in TAG_COUNTRY]
        online_tag = tagged[0] if len(set(tagged)) == 1 else ''
    else:
        online_tag = ''
    hosts = []
    for host in entry.get('hosts') or []:
        name = (host.get('name') or '').strip()
        if name and name not in hosts:
            hosts.append(name)
    kind, intent, topics = classify(title)
    audience = 'Students, as the title states' if ('student' in title.casefold() or 'estudiantes' in title.casefold()) else 'not confirmed'
    is_free = ticket.get('is_free') is True
    price = 'free' if is_free else 'not confirmed'
    approval = ticket.get('require_approval') is True
    sold_out = ticket.get('is_sold_out') is True
    waitlist = (ev.get('waitlist_enabled') is True) or (entry.get('waitlist_active') is True)
    url_bit = ev.get('url') or ''
    if not url_bit:
        raise ValueError('no registration url for ' + title)
    slug = slugify(url_bit)
    if slug in RESERVED:
        slug = 'event-' + slug
    coord = ev.get('coordinate') if public else None
    lat = lng = None
    if isinstance(coord, dict) and coord.get('latitude') is not None and coord.get('longitude') is not None:
        lat = round(float(coord['latitude']), 5)
        lng = round(float(coord['longitude']), 5)
    venue = street = None
    if public:
        venue = geo.get('address')
        street = geo.get('full_address') or geo.get('short_address')
    access = ''
    desc = geo.get('description') or ''
    if 'bonfires.london' in desc:
        access = 'The public listing points to bonfires.london for the pub route.'
    related = ''
    if 'breakpoint' in title.casefold():
        related = 'The title refers to Breakpoint 2026. This calendar has no separate checked record for that conference.'
    return {
        'id': slug,
        'source_id': ev.get('api_id') or '',
        'title': title,
        'event_type': kind,
        'intent': intent,
        'topics': topics,
        'status': 'scheduled',
        'trust': 'source-checked',
        'listing': 'listed',
        'precision': 'instant',
        'precise_time': True,
        'all_day': False,
        'start_utc': start.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'end_utc': end.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') if end else None,
        'timezone': tz_name,
        'format': fmt,
        'country': country,
        'country_code': country_code,
        'country_from_tag': country_from_tag,
        'online_tag': online_tag,
        'city': city,
        'city_listed': city_listed if city_listed and city_listed != city else '',
        'venue': venue,
        'street': street,
        'lat': lat,
        'lng': lng,
        'organisers': hosts,
        'price': price,
        'approval_required': approval,
        'sold_out': sold_out,
        'waitlist': 'open' if waitlist else 'none',
        'language': 'not confirmed',
        'audience': audience,
        'experience': 'not confirmed',
        'age': 'not confirmed',
        'registration_url': 'https://luma.com/' + url_bit,
        'source_url': CALENDAR_URL,
        'source_name': SOURCE_NAME,
        'last_checked': checked_at,
        'access_note': access,
        'related_note': related,
        'series_id': '',
        'month_start': '',
        'month_end': '',
    }


def assign_series(events):
    groups = {}
    for ev in events:
        if ev['precision'] != 'instant':
            continue
        key = (re.sub(r'\s+', ' ', ev['title']).casefold(), ev['city'] or ('online' if ev['format'] == 'online' else ''))
        groups.setdefault(key, []).append(ev)
    for items in groups.values():
        if len(items) < 2:
            continue
        place = items[0]['city'] or ('online' if items[0]['format'] == 'online' else 'place-not-confirmed')
        sid = slugify(items[0]['title'] + '-' + place)
        if sid in RESERVED:
            sid = 'series-' + sid
        for ev in items:
            ev['series_id'] = sid


def archive_records():
    rows = []
    for slug, title, start, end in ARCHIVE:
        span = start == end
        when = _month_label(start) if span else _month_label(start) + '–' + _month_label(end)
        rows.append({
            'id': 'archive-' + slug,
            'source_id': 'solana-hackathon-archive:' + slug,
            'title': title,
            'event_type': 'hackathon',
            'intent': 'build',
            'topics': ['Solana', 'Hackathon'],
            'status': 'completed',
            'trust': 'source-checked',
            'listing': 'listed',
            'precision': 'month',
            'precise_time': False,
            'all_day': False,
            'start_utc': None,
            'end_utc': None,
            'timezone': '',
            'format': 'online',
            'country': '',
            'country_code': '',
            'country_from_tag': False,
            'online_tag': '',
            'city': '',
            'city_listed': '',
            'venue': None,
            'street': None,
            'lat': None,
            'lng': None,
            'organisers': [],
            'price': 'not confirmed',
            'approval_required': False,
            'sold_out': False,
            'waitlist': 'not confirmed',
            'language': 'not confirmed',
            'audience': 'not confirmed',
            'experience': 'not confirmed',
            'age': 'not confirmed',
            'registration_url': '',
            'source_url': ARCHIVE_URL,
            'source_name': 'Solana hackathon archive',
            'last_checked': ARCHIVE_CHECKED,
            'access_note': '',
            'related_note': '',
            'series_id': 'solana-hackathon-archive',
            'month_start': start,
            'month_end': end,
            'month_label': when,
        })
    return rows


def _month_label(ym):
    dt = datetime.strptime(ym, '%Y-%m')
    return dt.strftime('%B %Y')


def queue():
    return [
        {
            'id': 'solana-builder-epoch-01',
            'title': 'Solana Builder Epoch//01',
            'where_shown': 'San Francisco, on a secondary account of the Solana events directory',
            'source_url': 'https://solana.com/events',
            'reason': 'This build requested solana.com/events and received a Vercel security checkpoint, not the directory. The date, time, organiser, price, and status were not read. It is not published.',
        },
        {
            'id': 'solana-events-directory',
            'title': 'Solana events directory',
            'where_shown': 'https://solana.com/events',
            'source_url': 'https://solana.com/events',
            'reason': 'The directory distinguishes community events from events hosted by the Solana Foundation. This build could not read the page, so none of its listings are published from that source.',
        },
        {
            'id': 'colosseum-hackathon-hub',
            'title': 'Colosseum hackathon hub',
            'where_shown': 'https://colosseum.com/hackathon',
            'source_url': 'https://colosseum.com/hackathon',
            'reason': 'The page retrieved on 17 Nov 2026 describes two seasons a year, April to May and September to October, and an ongoing competition called Eternal. It does not give a start instant, an end instant, or a submission deadline for a named occurrence. Colosseum also says its hackathons are open across blockchain ecosystems, so a listing would need a documented Solana connection. Nothing from this page is published as an event.',
        },
    ]


def sources(checked_at, upcoming_count):
    return [
        {
            'id': 'superteam-luma',
            'name': SOURCE_NAME,
            'url': CALENDAR_URL,
            'status': 'checked',
            'last_checked': checked_at,
            'upcoming': upcoming_count,
            'permission': 'Public calendar fields: title, time, timezone, city, public venue, host names, ticket flags, and the registration URL. A separate snapshot stores host-page wording, public bios, and registration question labels, quoted as the host’s words. Guest lists, answers, attendee counts, and guests-only coordinates are not stored.',
            'refresh': 'This file is a snapshot. A site deploy does not call Luma. Run scripts/events_refresh.py to replace the Superteam records.',
        },
        {
            'id': 'solana-hackathon-archive',
            'name': 'Solana hackathon archive',
            'url': ARCHIVE_URL,
            'status': 'checked',
            'last_checked': ARCHIVE_CHECKED,
            'upcoming': 0,
            'permission': 'Month labels and event names from the archive page. Participant counts and winner names on that page are not copied into the calendar.',
            'refresh': 'The archive is typed from the page retrieved on 17 Nov 2026. It is not a schedule of a future hackathon.',
        },
        {
            'id': 'solana-events',
            'name': 'Solana events directory',
            'url': 'https://solana.com/events',
            'status': 'not read',
            'last_checked': '',
            'upcoming': 0,
            'permission': 'Not used. The request did not return the directory.',
            'refresh': 'Try again when the page can be read. Do not fill dates from memory.',
        },
        {
            'id': 'colosseum',
            'name': 'Colosseum hackathon hub',
            'url': 'https://colosseum.com/hackathon',
            'status': 'read, nothing scheduled',
            'last_checked': '2026-11-17T10:40:00Z',
            'upcoming': 0,
            'permission': 'The page was read. No occurrence had a start and end instant, so none was imported.',
            'refresh': 'A season name is not an event date.',
        },
    ]


def validate(events):
    ids = [e['id'] for e in events]
    if len(ids) != len(set(ids)):
        raise SystemExit('events: duplicate id')
    seen = set()
    for e in events:
        if e['price'] == 'free' and e['source_name'] != SOURCE_NAME:
            raise SystemExit('events: free without a ticket flag ' + e['id'])
        if e['format'] == 'online' and (e['city'] or e['venue'] or e['lat'] is not None):
            raise SystemExit('events: online event has a place ' + e['id'])
        if e['lat'] is not None and not e['venue']:
            raise SystemExit('events: coordinates without a public venue ' + e['id'])
        if e['precision'] == 'instant':
            if not e['start_utc'] or not e['timezone']:
                raise SystemExit('events: instant without time ' + e['id'])
            key = (e['title'], e['start_utc'])
            if key in seen:
                raise SystemExit('events: same title and start ' + e['id'])
            seen.add(key)
        if e['precision'] == 'month' and e['start_utc']:
            raise SystemExit('events: month record has an instant ' + e['id'])
        if e['listing'] == 'hosted':
            raise SystemExit('events: nothing in this snapshot is hosted by Sol.College')


def build(entries, checked_at):
    upcoming = [normalise_superteam(e, checked_at) for e in entries]
    assign_series(upcoming)
    upcoming.sort(key=lambda e: e['start_utc'])
    archive = archive_records()
    events = upcoming + archive
    validate(events)
    return {
        'checked_at': checked_at,
        'note': CHECKED_NOTE,
        'sources': sources(checked_at, len(upcoming)),
        'events': events,
        'queue': queue(),
    }


def main():
    checked_at = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    entries = fetch_superteam()
    data = build(entries, checked_at)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('events_refresh:', len(data['events']), 'records,', sum(1 for e in data['events'] if e['precision'] == 'instant'), 'dated')


if __name__ == '__main__':
    main()
