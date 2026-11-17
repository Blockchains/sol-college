"""Full listings for Solana Calendar events that mention Solana.

Host wording is quoted from the retrieval in events_host.json. A sentence on
the host page is not rewritten into a fact, and a month on the hackathon
archive is not given a day.
"""
from __future__ import annotations
import html, json, re
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOST = json.loads((HERE / 'events_host.json').read_text(encoding='utf-8'))
BY_SOURCE = {row['source_id']: row for row in HOST['events']}


def E(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def host_for(ev):
    return BY_SOURCE.get(ev.get('source_id') or '')


def retrieved_label():
    raw = HOST.get('retrieved_at') or ''
    try:
        dt = datetime.fromisoformat(raw.replace('Z', '+00:00'))
        return dt.strftime('%-d %b %Y, %H:%M UTC').replace(dt.strftime('%-d'), str(dt.day))
    except Exception:
        return raw or 'not recorded'


def lines_of(host):
    if not host:
        return []
    rows = []
    for block in host.get('blocks') or []:
        for line in block.split('\n'):
            line = ' '.join(line.split())
            if line:
                rows.append(line)
    return rows


def search_text(ev):
    host = host_for(ev)
    if not host:
        return ''
    return ' '.join(lines_of(host))


def _mentions(ev, host):
    title = 'solana' in (ev.get('title') or '').lower()
    body = '\n'.join((host or {}).get('blocks') or [])
    page = 'solana' in body.lower()
    bio = any('solana' in (b.get('bio') or '').lower() for b in (host or {}).get('bios') or [])
    archive = (ev.get('source_id') or '').startswith('solana-hackathon-archive')
    topic = 'Solana' in (ev.get('topics') or [])
    return title, page, bio, archive, topic


def in_scope(ev):
    title, page, bio, archive, topic = _mentions(ev, host_for(ev))
    return title or page or bio or archive or topic


def _minutes(ev):
    import events
    if not ev.get('start_utc') or not ev.get('end_utc'):
        return None
    start = events.parse_utc(ev['start_utc'])
    end = events.parse_utc(ev['end_utc'])
    return int((end - start).total_seconds() // 60)


def _facts(ev):
    import events
    when = events.when_label(ev)
    place = events.place_line(ev)
    orgs = events.organisers(ev)
    tz = events.tz_label(ev['timezone']) if ev.get('timezone') else 'Not stated'
    return when, place, orgs, tz


def _kind(line):
    low = line.lower()
    if any(w in low for w in ('photo', 'promotional', '撮影')):
        return 'photo'
    if re.search(r'\d', line) and any(w in low for w in ('guest', 'capacity', 'spot', 'worth', '$', '円', '人')):
        return 'number'
    if any(w in low for w in ('please', 'register', 'arrive', 'dress', 'follow', 'bring', 'sign up', 'ご案内', '参加')):
        return 'instruction'
    if any(w in low for w in ('venue', 'location', 'approval', 'campus', 'harbour', 'online', 'meet', '会場', '住所')):
        return 'place'
    if re.search(r'\b\d{1,2}:\d{2}\b|\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|am|pm)\b|時|日', low):
        return 'time'
    if 'solana' in low:
        return 'solana'
    if any(w in low for w in ('community', 'hosted', 'speaker', '講師', 'superteam')):
        return 'people'
    return 'other'


def _sentence(s):
    return ' '.join(str(s).split()).rstrip('.')


def _clip(line, n=90):
    line = ' '.join(line.split())
    if len(line) <= n:
        return line
    return line[:n].rsplit(' ', 1)[0] + '…'


def _frame(line, ev, when, place, orgs, tz):
    return (
        'The host page retrieved on %s contains this line for “%s”: “%s.” '
        'The calendar already stored a separate time, “%s,” in %s. Its place line is “%s.” Its organiser line is “%s.” '
        'Those stored lines are not rewritten to match the host sentence, and the host sentence is not dropped because the record is shorter. '
        'If the sentence names a room, a clock, or a person the record does not name, both stay on this page so the difference can be seen. '
        'Sol.College did not attend, did not count who came, and did not take photographs.'
        % (retrieved_label(), ev['title'], line, _sentence(when), tz, _sentence(place), _sentence(orgs))
    )


def _second(kind, line, ev, when, place, orgs):
    mins = _minutes(ev)
    length = ('The two stored instants are %s minutes apart. That figure is arithmetic on the record, not a claim that people stayed that long.'
              % mins) if mins is not None else 'This record has no pair of instants, so no duration is calculated.'
    price = ev.get('price') or 'not confirmed'
    if kind == 'photo':
        return (
            '“%s” is the host’s sentence about photographs or promotional use. It is not a photograph stored here, and it is not consent collected by Sol.College. '
            'The listing attaches no image from the event. A person who does not want to be photographed has to take that up with the host, on the host’s terms.'
            % _clip(line)
        )
    if kind == 'number':
        return (
            '“%s” contains a figure. A figure in the host’s wording can be a capacity, a suggested gift, or a date fragment. '
            'It is not a count of people who arrived, and it is not a fee Sol.College charged. Price on this record is “%s.” %s'
            % (_clip(line), price, length)
        )
    if kind == 'instruction':
        return (
            '“%s” tells a person to register, arrive, dress, bring something, or follow a link. The instruction is the host’s. '
            'This calendar does not enforce it, does not store who complied, and does not turn a registration link into proof that anyone registered. '
            'The registration URL on the record is the public page, not a private joining link copied from an email.'
            % _clip(line)
        )
    if kind == 'place':
        return (
            '“%s” is about where someone would go. The calendar’s place line remains “%s.” '
            'A phrase such as “upon approval,” “sign up to see the location,” or a campus named only in this sentence does not add a pin to the map. '
            'Guests-only coordinates are not stored. If the record already has a public street, that street is the one the calendar was allowed to keep, not a guess from the sentence.'
            % (_clip(line), _sentence(place))
        )
    if kind == 'time':
        return (
            '“%s” carries a clock, a weekday, or a date. The stored label is “%s.” %s '
            'A second date written in the host wording is not published as another event. The rule on this calendar is that a title is not turned into an extra occurrence. '
            'One Luma event remains one record, even when the description lists a series of meetings.'
            % (_clip(line), _sentence(when), length)
        )
    if kind == 'solana':
        return (
            '“%s” uses the word Solana. That mention is why this listing is expanded with the host’s wording. '
            'The word does not say the Solana Foundation is the host, unless the sentence itself says so. It does not make a lesson on Sol.College a prerequisite. '
            'The organiser line stays “%s.”'
            % (_clip(line), orgs)
        )
    if kind == 'people':
        return (
            '“%s” names a community, a host, or a speaker. The organiser field is “%s.” '
            'A name that appears only in the sentence is still the host’s wording. It is not an attendance list, and it is not a partnership with Sol.College. '
            'No guest list was copied.'
            % (_clip(line), orgs)
        )
    return (
        '“%s” stays a sentence from the host page. It is not recoded into the time, the place, or the price. '
        'The stored time remains “%s,” and the stored place remains “%s.”'
        % (_clip(line), _sentence(when), _sentence(place))
    )


def _basis(ev, host):
    title, page, bio, archive, topic = _mentions(ev, host)
    bits = []
    if title:
        bits.append('The title contains the word Solana.')
    if page:
        bits.append('The host page retrieved on %s contains the word Solana.' % retrieved_label())
    if bio:
        bits.append('A public host bio on the calendar contains the word Solana.')
    if archive:
        bits.append('The row comes from the Solana hackathon archive. The archive page is the mention, including when the event title does not repeat the word.')
    if topic and not (title or page or bio or archive):
        bits.append(
            'The topic label on this calendar is Solana because the event was on the Superteam calendar. '
            'The title and the host wording stored here do not contain the word. The topic is this calendar’s label, not a sentence the host wrote.'
        )
    elif topic:
        bits.append('The topic label Solana is also applied by this calendar. The label follows the source, and it is not a second piece of evidence.')
    if not bits:
        bits.append('This listing does not mention Solana in the title, the host wording, the bios, or the source name.')
    return ' '.join(bits)


def _questions(host):
    rows = (host or {}).get('questions') or []
    if not rows:
        return '<h2>Registration form</h2><p>No registration question was in the payload stored for this page. That absence is not a claim that the live form has no questions.</p>'
    items = []
    for row in rows:
        flag = 'Required' if row.get('required') else 'Not marked required'
        kind = row.get('question_type') or 'unspecified type'
        extra = ' The terms text on that checkbox is not copied here.' if row.get('has_terms') else ''
        items.append('<li>%s %s question: %s.%s</li>' % (E(flag), E(kind), E(row.get('label') or ''), extra))
    return (
        '<h2>Registration form</h2>'
        '<p>These are the question labels on the host form at the retrieval. No answer is stored. A label is not a description of who registered.</p>'
        '<ul>%s</ul>' % ''.join(items)
    )


def _bios(host):
    rows = (host or {}).get('bios') or []
    if not rows:
        return ''
    bits = ['<h2>Public host bios</h2>',
            '<p>A bio is the short public profile line on the calendar. It is not a Sol.College description of the event, and it is not checked against a company register.</p>']
    for row in rows:
        bits.append('<p><b>%s.</b> %s</p>' % (E(row.get('name') or ''), E(row.get('bio') or '')))
    return '\n'.join(bits)


def _copy(host):
    if not host or not host.get('blocks'):
        return (
            '<h2>Host wording</h2>'
            '<p>No host-page description was stored for this record. The calendar does not invent an agenda to fill the gap.</p>'
        )
    paras = []
    for block in host['blocks']:
        safe = '<br>'.join(E(line) for line in block.split('\n') if line.strip())
        paras.append('<p>%s</p>' % safe)
    note = ''
    if host.get('place_note'):
        note = '<p>Place note on the public address field: %s</p>' % E(host['place_note'])
    return (
        '<h2>What the host page says</h2>'
        '<p>Retrieved %s from the event’s public Luma page. The words below are the host’s. Sol.College did not write them and did not check them by attending. '
        'A later edit of the host page is not reflected until the snapshot is replaced.</p>'
        '<div class=ev-copy>%s</div>%s' % (E(retrieved_label()), ''.join(paras), note)
    )


def _reading(ev, host):
    lines = lines_of(host)
    if not lines:
        return ''
    when, place, orgs, tz = _facts(ev)
    paras = [
        '<h2>How to read those lines</h2>',
        '<p>Each line is quoted, then set beside the calendar record. The quote can be more specific than the record. The record can refuse a detail the quote only promises after approval. Neither side is silently corrected.</p>',
    ]
    for line in lines:
        kind = _kind(line)
        paras.append('<p>%s</p>' % E(_frame(line, ev, when, place, orgs, tz)))
        paras.append('<p>%s</p>' % E(_second(kind, line, ev, when, place, orgs)))
    return '\n'.join(paras)


def _fields(ev):
    import events
    when, place, orgs, tz = _facts(ev)
    mins = _minutes(ev)
    duration = ('%s minutes, the difference of the two stored instants.' % mins) if mins is not None else 'Not calculated. This record has no start and end instant.'
    topics = ', '.join(ev.get('topics') or []) or 'none'
    rows = [
        ('Time', 'The stored label is “%s.” Event timezone: %s. UTC start: %s. UTC end: %s. %s A clock in the host wording does not replace these fields.'
         % (_sentence(when), tz, ev.get('start_utc') or 'none', ev.get('end_utc') or 'none', duration)),
        ('Place', 'The place line is “%s.” Format: %s. A public street is present only when the source marked the address public. City: %s.'
         % (_sentence(place), ev.get('format') or '', ev.get('city') or 'not named')),
        ('Organiser', 'The organiser line is “%s.” An organiser named here is not a partner of Sol.College, and the name is not an attendance list.' % orgs),
        ('Price', 'Price on the ticket record: %s. %s Approval required: %s.'
         % (events.price_line(ev), events.wait_line(ev), 'yes' if ev.get('approval_required') else 'no')),
        ('Audience', 'Audience on the record: %s. Experience: %s. Language: %s. Age restriction: %s. “Not confirmed” means the field was not on the source used for the record. It does not mean the host has no preference.'
         % (ev.get('audience'), ev.get('experience'), ev.get('language'), ev.get('age'))),
        ('Topics', 'Topics stored for this listing: %s. %s' % (topics, _basis(ev, host_for(ev)))),
        ('Status', 'Status: %s. Precision: %s. Trust: %s. A scheduled listing can still be cancelled on the host page after this snapshot. A completed archive row is not a future competition.'
         % (ev.get('status'), ev.get('precision'), ev.get('trust'))),
        ('Source', 'Source name: %s. Source URL: %s. Registration URL: %s. Last check of the calendar fields: %s.'
         % (ev.get('source_name'), ev.get('source_url'), ev.get('registration_url') or 'none', ev.get('last_checked') or '')),
    ]
    body = ['<h2>The stored record</h2>',
            '<p>These paragraphs restate the fields the calendar already keeps for “%s,” in sentences, so a reader does not have to infer them from the table alone.</p>' % E(ev['title'])]
    for label, text in rows:
        body.append('<h3>%s</h3><p>%s</p>' % (E(label), E(text)))
    return '\n'.join(body)


def _siblings(ev):
    import events
    rows = []
    for other in events.EVENTS:
        if other['id'] == ev['id']:
            continue
        same_series = ev.get('series_id') and other.get('series_id') == ev['series_id']
        same_city = ev.get('city') and other.get('city') == ev['city'] and other.get('precision') == 'instant'
        same_org = False
        mine = set(ev.get('organisers') or [])
        theirs = set(other.get('organisers') or [])
        if mine and theirs and mine & theirs:
            same_org = True
        if same_series or same_city or same_org:
            rows.append(other)
    if not rows:
        return '<h2>Other listings in this snapshot</h2><p>No other published record shares this series, this city, or an organiser name. That is a fact about this snapshot, not a claim that no related gathering exists.</p>'
    items = []
    for other in rows:
        why = []
        if ev.get('series_id') and other.get('series_id') == ev['series_id']:
            why.append('same series')
        if ev.get('city') and other.get('city') == ev['city']:
            why.append('same city')
        if set(ev.get('organisers') or []) & set(other.get('organisers') or []):
            why.append('a shared organiser name')
        items.append(
            '<li><a href="/events/%s/">%s</a>. %s. Linked because of %s. The link does not merge the two records, and it does not copy one record’s venue onto the other.</li>'
            % (E(other['id']), E(other['title']), E(events.when_label(other)), E(', '.join(why)))
        )
    return (
        '<h2>Other listings in this snapshot</h2>'
        '<p>These are other rows already published on Solana Calendar. They are listed so “%s” can be read beside them. A shared title or a shared city is not a shared agenda.</p>'
        '<ul>%s</ul>' % (E(ev['title']), ''.join(items))
    )


def _archive(ev):
    import events
    if ev.get('precision') != 'month':
        return ''
    others = [row for row in events.archive() if row['id'] != ev['id']]
    paras = ['<h2>What the archive row can support</h2>']
    paras.append('<p>%s is stored as %s on the Solana hackathon archive. The archive states a month, not a start day and not a clock time. This page does not invent either. The series is described on the archive as online hackathons. That description is not a venue, and it is not a claim about who won.</p>'
                 % (E(ev['title']), E(ev.get('month_label') or 'an unstated month')))
    limits = [
        'No day of the month is printed, so no weekday is inferred.',
        'No timezone is printed, so UTC is not filled in.',
        'No organiser is named on this row. A hackathon can have had organisers. This record does not name them.',
        'No price is confirmed. Free is not assumed.',
        'No registration URL was stored. The archive page is the source link.',
        'Participant counts on the archive page were not copied.',
        'Winner names on the archive page were not copied.',
        'The row is marked completed because the month is in the past relative to the retrieval. It is not a result write-up.',
        'Sol.College did not host it and does not attach a recap.',
        'A lesson on this site is not a prerequisite the archive named.',
    ]
    for limit in limits:
        paras.append('<p>“%s,” %s. %s</p>' % (E(ev['title']), E(ev.get('month_label') or ''), E(limit)))
    paras.append('<h3>The other months on the same page</h3>')
    paras.append('<p>The archive snapshot holds %s other named months. Each is its own row. Naming them here does not import their winners or their headcounts.</p>' % len(others))
    for other in others:
        paras.append(
            '<p><a href="/events/archive/%s/">%s</a> is stored for %s. That month is not the month of “%s.” A reader who wants %s has to open that row. This page does not treat the two names as one hackathon.</p>'
            % (E(other['id'].removeprefix('archive-')), E(other['title']), E(other.get('month_label') or ''),
               E(ev['title']), E(other['title']))
        )
    return '\n'.join(paras)


def section(ev):
    if not in_scope(ev):
        return ''
    host = host_for(ev)
    return '\n'.join([
        '<h2>Solana on this listing</h2>',
        '<p>%s</p>' % E(_basis(ev, host)),
        _copy(host),
        _questions(host),
        _bios(host),
        _reading(ev, host),
        _fields(ev),
        _siblings(ev),
        _archive(ev),
    ])
