"""Solana Calendar: source-checked events for Sol.College.

Dated listings come from scripts/events_data.json. A month on the hackathon
archive is not given a clock time. Sol.College hosts none of these events.
"""
from __future__ import annotations
import html, json, os, re, sys, urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
SITE = 'https://sol.college'
ISSUE = 'https://github.com/Blockchains/sol-college/issues/new'
INTENT = {
    'learn': 'Learn', 'build': 'Build', 'meet': 'Meet', 'explore': 'Explore',
    'research': 'Research', 'participate': 'Participate', 'enjoy': 'Enjoy', 'apply': 'Apply',
}
DATA = json.loads((HERE / 'events_data.json').read_text(encoding='utf-8'))
EVENTS = DATA['events']
QUEUE = DATA['queue']
SOURCES = DATA['sources']
STYLE = '<style id=sc-events>' + (HERE / 'events.css').read_text(encoding='utf-8') + '</style>'
SCRIPT = '<script src="/events/events.js" defer></script>'


def E(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def issue(title, body):
    return ISSUE + '?title=' + urllib.parse.quote(title) + '&body=' + urllib.parse.quote(body)


SUBMIT = issue('Solana Calendar submission',
    '1. Original event URL:\n\n2. Details as shown on that page (do not fill a blank with a guess):\n'
    'Title:\nStart:\nEnd:\nTimezone:\nIn person, online, or hybrid:\nCity:\nOrganiser:\nPrice:\n\n'
    '3. Solana connection:\n\n4. I am the organiser / I am suggesting someone else\'s public event:\n\n'
    '5. A public GitHub issue is not a private form. Do not include recovery phrases, private addresses, or attendee lists.\n')
REPORT = issue('Solana Calendar report', 'Page:\n\nWhat changed, or what looks wrong:\n\nSource that disagrees:\n\n')
CORRECTION = issue('Solana Calendar correction', 'Page:\n\nField:\n\nWhat the source says:\n\n')


def slugify(s):
    s = re.sub(r'[^a-z0-9]+', '-', (s or '').casefold()).strip('-')
    return s or 'event'


def parse_utc(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def tz_label(name):
    if name == 'Etc/GMT':
        return 'UTC (source timezone: Etc/GMT)'
    return name or 'Timezone not confirmed'


def local_pair(ev):
    tz = ZoneInfo(ev['timezone'])
    start = parse_utc(ev['start_utc']).astimezone(tz)
    end = parse_utc(ev['end_utc']).astimezone(tz) if ev['end_utc'] else None
    return start, end


def when_label(ev):
    if ev['precision'] == 'month':
        return ev.get('month_label') or 'Month not confirmed'
    start, end = local_pair(ev)
    left = f"{start.strftime('%A')}, {start.day} {start.strftime('%b %Y')}, {start.strftime('%H:%M')}"
    if not end:
        return left
    if start.date() == end.date():
        return left + '–' + end.strftime('%H:%M')
    right = f"{end.strftime('%A')}, {end.day} {end.strftime('%b %Y')}, {end.strftime('%H:%M')}"
    return left + ' – ' + right


def event_days(ev):
    if ev['precision'] != 'instant':
        return ''
    start, end = local_pair(ev)
    last = end.date() if end else start.date()
    days, day = [], start.date()
    while day <= last:
        days.append(day.isoformat())
        day += timedelta(days=1)
    return ' '.join(days)


def organisers(ev):
    if ev['organisers']:
        return ', '.join(ev['organisers'])
    if ev.get('online_tag') and ev['online_tag'] in ev['title']:
        return 'Not named on the host list. The title names ' + ev['online_tag'] + '.'
    return 'Not named on the host list.'


def price_line(ev):
    if ev['price'] == 'free' and ev.get('approval_required'):
        return 'Free on the ticket record. Approval is required.'
    if ev['price'] == 'free':
        return 'Free on the ticket record.'
    return 'Price not confirmed.'


def wait_line(ev):
    if ev.get('sold_out') and ev.get('waitlist') == 'open':
        return 'Sold out. A waitlist is open.'
    if ev.get('waitlist') == 'open':
        return 'A waitlist is open.'
    if ev.get('waitlist') == 'none':
        return 'No waitlist is shown on the record.'
    return 'Waitlist not confirmed.'


def place_line(ev):
    if ev['format'] == 'online':
        tag = ev.get('online_tag')
        extra = ' The listing is tagged ' + tag + ', and it names no city.' if tag else ' No city is given.'
        return 'Online.' + extra
    if ev.get('street'):
        text = ev['street']
        if ev.get('city_listed'):
            text += '. The source writes the city as ' + ev['city_listed'] + '.'
        return text
    if ev.get('city'):
        city = ev['city']
        if ev.get('city_listed'):
            city += ' (listed as ' + ev['city_listed'] + ')'
        country = ev.get('country') or ''
        text = city + (', ' + country if country else '')
        return text + '. The street address is not public on the calendar.'
    return 'In person. City not confirmed. No venue was public on the calendar.'


def checked(ev):
    raw = ev.get('last_checked') or ''
    try:
        dt = parse_utc(raw)
        return dt.strftime('%-d %b %Y, %H:%M UTC').replace(dt.strftime('%-d'), str(dt.day))
    except Exception:
        return raw or 'not confirmed'


def summary(ev):
    if ev['precision'] == 'month':
        return (ev['title'] + ' appears on Solana\'s hackathon archive for ' + ev.get('month_label', 'an unstated month')
                + '. The archive does not state a start day or a clock time. This record is historical.')
    return (when_label(ev) + '. ' + place_line(ev) + ' Listed from the ' + ev['source_name']
            + '. Not hosted by Sol.College.')


def meta_for(ev):
    if ev['precision'] == 'month':
        text = ev['title'] + ' on the Solana hackathon archive for ' + ev.get('month_label', '') + '. Day and time are not stated.'
    else:
        where = 'Online' if ev['format'] == 'online' else (ev.get('city') or 'City not confirmed')
        text = where + '. ' + tz_label(ev['timezone']) + '. Listed by Sol.College, not hosted here.'
    text = ' '.join(text.split())
    if len(text) > 158:
        raise SystemExit('events: description over 158 for ' + ev['id'])
    return text


def crumbs(items):
    parts = ['<a href="/">Home</a>', '<a href="/events/">Events</a>'] + items
    return '<nav class=crumbs aria-label=Breadcrumb>' + ' / '.join(parts) + '</nav>'


def upcoming():
    return [e for e in EVENTS if e['precision'] == 'instant' and e['status'] == 'scheduled']


def archive():
    return [e for e in EVENTS if e['precision'] == 'month']


def by_id(eid):
    return next(e for e in EVENTS if e['id'] == eid)


def search_blob(ev):
    import events_listings as listings
    parts = [ev['title'], ev.get('city') or '', ev.get('country') or '', ev.get('online_tag') or '',
             organisers(ev), ' '.join(ev.get('topics') or []), ev['event_type'], INTENT.get(ev['intent'], ''),
             place_line(ev), listings.search_text(ev)]
    return ' '.join(parts).casefold()


def card(ev):
    days = event_days(ev)
    lat = '' if ev.get('lat') is None else str(ev['lat'])
    lng = '' if ev.get('lng') is None else str(ev['lng'])
    href = '/events/' + ev['id'] + '/'
    when = when_label(ev)
    tz = tz_label(ev['timezone']) if ev['precision'] == 'instant' else 'No clock time on the source'
    start = ev.get('start_utc') or ''
    end = ev.get('end_utc') or ''
    return f'''<article class="card ev-card" data-id="{E(ev['id'])}" data-start="{E(start)}" data-end="{E(end)}" data-format="{E(ev['format'])}" data-intent="{E(ev['intent'])}" data-type="{E(ev['event_type'])}" data-price="{E(ev['price'])}" data-lang="{E(ev['language'])}" data-level="{E(ev['experience'])}" data-country="{E(ev.get('country') or '')}" data-city="{E(ev.get('city') or '')}" data-status="{E(ev['status'])}" data-precision="{E(ev['precision'])}" data-lat="{E(lat)}" data-lng="{E(lng)}" data-days="{E(days)}" data-text="{E(search_blob(ev))}">
<h3><a href="{href}">{E(ev['title'])}</a></h3>
<p class=ev-when data-start="{E(start)}" data-end="{E(end)}" data-tz="{E(ev.get('timezone') or '')}"><span class=ev-local>{E(when)}</span><br><span class=ev-tz>Event time: {E(tz)}</span><br><span class=ev-yours>Your time: <span class=ev-your>shown when the browser can read a timezone</span></span></p>
<p class=meta>{E(place_line(ev))} · {E(organisers(ev))} · {E(price_line(ev))} · Experience {E(ev['experience'])}</p>
<p><span class=chip>Source checked</span> <span class=chip>{E(ev['status'].replace('-', ' '))}</span> <span class=chip>Listed by Sol.College</span></p>
<p class=ev-distance></p>
<p><a class=btn href="{href}">Details</a> <button type=button class="btn ghost" data-save="{E(ev['id'])}">Save</button></p>
</article>'''


def ics_escape(s):
    return (s or '').replace('\\', '\\\\').replace('\n', '\\n').replace(',', '\\,').replace(';', '\\;')


def fold(line):
    parts = []
    while len(line.encode('utf-8')) > 73:
        cut = 73
        while len(line[:cut].encode('utf-8')) > 73:
            cut -= 1
        parts.append(line[:cut])
        line = ' ' + line[cut:]
    parts.append(line)
    return '\r\n'.join(parts)


def vevent(ev):
    if ev['precision'] != 'instant' or not ev.get('start_utc') or not ev.get('end_utc'):
        return ''
    start = parse_utc(ev['start_utc']).strftime('%Y%m%dT%H%M%SZ')
    end = parse_utc(ev['end_utc']).strftime('%Y%m%dT%H%M%SZ')
    stamp = parse_utc(ev['last_checked']).strftime('%Y%m%dT%H%M%SZ')
    loc = 'Online' if ev['format'] == 'online' else (ev.get('street') or ev.get('city') or 'City not confirmed')
    desc = 'Listed by Sol.College. Source checked against ' + ev['source_url'] + '. Not an organiser confirmation and not an endorsement. Event timezone: ' + tz_label(ev['timezone']) + '.'
    lines = [
        'BEGIN:VEVENT',
        'UID:' + ev['id'] + '@sol.college',
        'DTSTAMP:' + stamp,
        'DTSTART:' + start,
        'DTEND:' + end,
        'SUMMARY:' + ics_escape(ev['title']),
        'LOCATION:' + ics_escape(loc),
        'URL:' + ev['registration_url'],
        'DESCRIPTION:' + ics_escape(desc),
        'END:VEVENT',
    ]
    return '\r\n'.join(fold(line) for line in lines)


def calendar_text(events, name):
    body = '\r\n'.join(v for v in (vevent(e) for e in events) if v)
    head = '\r\n'.join([
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//Sol.College//Solana Calendar//EN',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        'X-WR-CALNAME:' + ics_escape(name),
        'X-WR-CALDESC:Source-checked listings. A changed event keeps the same UID.',
    ])
    return head + ('\r\n' + body if body else '') + '\r\nEND:VCALENDAR\r\n'


def options(pairs, all_label):
    return f'<option value="">{E(all_label)}</option>' + ''.join(f'<option value="{E(v)}">{E(n)}</option>' for v, n in pairs)


def home_page():
    rows = upcoming()
    countries = sorted({e['country'] for e in rows if e.get('country')})
    cards = '\n'.join(card(e) for e in rows)
    country_opts = options([(c, c) for c in countries], 'Any place')
    intent_opts = options(list(INTENT.items()), 'Any intent')
    groups = '''<div class=ev-groups>
<a href="/events/?intent=build"><strong>Build something</strong>Coworking and hackathons whose dates are on the calendar.</a>
<a href="/events/?intent=meet"><strong>Meet your community</strong>Meetups and mixers with a checked time.</a>
<a href="/events/?intent=learn"><strong>Learn</strong>Workshops, bootcamps, and student sessions.</a>
<a href="/events/?intent=enjoy"><strong>Enjoy</strong>Social listings with a named Solana organiser or calendar.</a>
<a href="/events/?intent=participate"><strong>Participate</strong>Public community calls.</a>
<a href="/events/queue/"><strong>Deadlines</strong>None are published. A cutoff needs an exact time and timezone.</a>
</div>'''
    body = f'''{crumbs(['<span>Solana Calendar</span>'])}
<article class="lesson ev-app" id=ev-app>
<p class=eyebrow>Sol.College / Events</p>
<h1>Solana Calendar</h1>
<p class=lead>Meet. Learn. Build. Belong.</p>
<p>Your next connection starts here. Find a Solana event around the corner or around the world.</p>
<p class=ev-promise>Real events. Clear details. Original sources. Your timezone.</p>
<p>This is a working list, not a claim that every gathering is here. Private meetings, last-minute posts, and cancellations are easy to miss. A listing is not hosting, and it is not an endorsement. <a href="/events/college/">Sol.College hosts no event on this calendar.</a></p>
<div class=ev-tools>
<label class=ev-zone for=ev-q>Search events, cities, organisers, or topics</label>
<input class=ev-search id=ev-q type=search placeholder="Search events, cities, organisers, or topics">
<div class=ev-chips id=ev-chips>
<button type=button data-chip=near aria-pressed=false>Near me</button>
<button type=button data-chip=online aria-pressed=false>Online</button>
<button type=button data-chip=week aria-pressed=false>This week</button>
<button type=button data-chip=free aria-pressed=false>Free</button>
<button type=button data-chip=beginner aria-pressed=false>For beginners</button>
</div>
<p id=ev-near-note class=meta></p>
<div class=ev-views id=ev-views role=tablist aria-label=View>
<button type=button role=tab data-view=list aria-selected=true>List</button>
<button type=button role=tab data-view=calendar aria-selected=false>Calendar</button>
<button type=button role=tab data-view=map aria-selected=false>Map</button>
</div>
<div class="filters ev-filters">
<label>Dates<select id=f-when><option value="">Any time</option><option value=week>Next seven days</option><option value=later>Later</option><option value=saved>Saved on this browser</option></select></label>
<label>Place<select id=f-country>{country_opts}</select></label>
<label>Intent<select id=f-intent>{intent_opts}</select></label>
<label>Format<select id=f-format><option value="">Any format</option><option value=in-person>In person</option><option value=online>Online</option></select></label>
<label>Language<select id=f-lang><option value="">Any language</option><option value="not confirmed">Not confirmed</option></select></label>
<label>Price<select id=f-price><option value="">Any price</option><option value=free>Free on the ticket record</option><option value="not confirmed">Price not confirmed</option></select></label>
<label>Experience<select id=f-level><option value="">Any level</option><option value=beginner>For beginners</option><option value="not confirmed">Not confirmed</option></select></label>
</div>
<p class=ev-zone>Your timezone: <strong id=ev-zone-now>reading…</strong></p>
<p class=ev-zone><label>Show times as <select id=ev-zone>{''.join(f'<option value="{E(z)}">{E(tz_label(z))}</option>' for z in sorted({e['timezone'] for e in rows}))}</select></label></p>
</div>
<p class=ev-count id=ev-count aria-live=polite></p>
<div class=ev-panel id=panel-list>
<h2 id=ev-soon-h hidden>Today and the next seven days</h2>
<div class=grid id=ev-soon></div>
<h2 id=ev-later-h hidden>Later</h2>
<div class=grid id=ev-list>{cards}</div>
<p class=ev-empty id=ev-empty hidden>Nothing in the published list matches.</p>
</div>
<div class="ev-panel" id=panel-calendar hidden>
<p>Dates in this grid are the event's own dates. On a narrow screen, scroll the grid sideways. Online events stay on the days the source gave them.</p>
<p class=ev-actions><button type=button class="btn ghost" id=ev-prev>Previous month</button> <strong id=ev-month-label></strong> <button type=button class="btn ghost" id=ev-next>Next month</button></p>
<div class=ev-cal-wrap>
<table class=ev-cal><thead><tr><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th><th>Sat</th><th>Sun</th></tr></thead><tbody id=ev-month></tbody></table>
</div>
</div>
<div class="ev-panel ev-map" id=panel-map hidden>
<p>The map is a list of places, so an online event is not hidden behind a pin. Venues marked guests-only are not plotted.</p>
{place_index()}
</div>
{groups}
<p class=ev-actions><a class=btn href="{E(SUBMIT)}">Submit an event</a> <a class="btn ghost" href="/events/cities/">Follow a city</a> <a class="btn ghost" href="/events/feeds/all.ics">Subscribe</a></p>
<p class=meta>Subscribe downloads a calendar feed. Sol.College does not send email digests. Saving an event stores its id in this browser only. <a href="/events/coverage/">Coverage</a> · <a href="/events/sources/">Sources</a> · <a href="/events/queue/">Not published yet</a> · <a href="/events/archive/">Hackathon archive</a></p>
<p>Before you go: the <a href="/lessons/">lessons</a> and the <a href="/library/">library</a> are practice and reading. An organiser has not named either as a requirement. After an event, this calendar does not invent a recap.</p>
</article>
{SCRIPT}'''
    return body


def place_index():
    rows = upcoming()
    cities = {}
    for ev in rows:
        if ev.get('city'):
            cities.setdefault((ev['city'], ev.get('country') or ''), []).append(ev)
    online = [ev for ev in rows if ev['format'] == 'online']
    unplaced = [ev for ev in rows if ev['format'] == 'in-person' and not ev.get('city')]
    bits = ['<h3>Online</h3><ul>']
    for ev in online:
        bits.append(f'<li><a href="/events/{E(ev["id"])}/">{E(ev["title"])}</a></li>')
    bits.append('</ul>')
    current = None
    for (city, country), items in sorted(cities.items(), key=lambda x: (x[0][1], x[0][0])):
        if country != current:
            if current is not None:
                bits.append('</ul>')
            current = country
            bits.append(f'<h3>{E(country or "Country not confirmed")}</h3><ul>')
        bits.append(f'<li><a href="/events/cities/{slugify(city)}/">{E(city)}</a> · {len(items)}</li>')
    if current is not None:
        bits.append('</ul>')
    if unplaced:
        bits.append('<h3>In person, city not confirmed</h3><ul>')
        for ev in unplaced:
            bits.append(f'<li><a href="/events/{E(ev["id"])}/">{E(ev["title"])}</a></li>')
        bits.append('</ul>')
    return '\n'.join(bits)


def detail(ev):
    path_span = f'<span>{E(ev["title"])}</span>'
    facts = [
        ('Listing', 'Listed by Sol.College. Not hosted by Sol.College. Not a sponsored placement.'),
        ('Trust', 'Source checked at ' + checked(ev) + '. This is not a badge for safety or quality.'),
        ('Status', ev['status']),
        ('Type', ev['event_type']),
        ('Intent', INTENT.get(ev['intent'], ev['intent'])),
        ('Topics', ', '.join(ev.get('topics') or [])),
        ('When', when_label(ev)),
        ('Timezone', tz_label(ev['timezone']) if ev.get('timezone') else 'Not stated'),
        ('Format', ev['format']),
        ('Where', place_line(ev)),
        ('Organiser', organisers(ev)),
        ('Price', price_line(ev)),
        ('Language', ev['language']),
        ('Audience', ev['audience']),
        ('Experience', ev['experience']),
        ('Age restriction', ev['age']),
        ('Waitlist', wait_line(ev)),
        ('Accessibility', 'Not confirmed'),
        ('Code of conduct', 'Not confirmed on this record'),
        ('Registration deadline', 'Not confirmed. The event time is not a deadline.'),
        ('Source', ev['source_name']),
    ]
    dl = ''.join(f'<dt>{E(k)}</dt><dd>{E(v)}</dd>' for k, v in facts)
    reg = f'<p><a class=btn href="{E(ev["registration_url"])}">Registration page</a></p>' if ev.get('registration_url') else '<p>No registration URL was on the source used for this record.</p>'
    if ev['precision'] == 'instant':
        ics = f'<p><a class="btn ghost" href="/events/{E(ev["id"])}/event.ics">Download a calendar entry</a> <button type=button class="btn ghost" data-save="{E(ev["id"])}">Save</button></p>'
    else:
        ics = '<p>A calendar file is not offered. The archive states a month, not a start day or a clock time, and a month is not an all-day event.</p>'
    series = ''
    if ev.get('series_id') and ev['precision'] == 'instant':
        series = f'<p>Other dated occurrences of this title: <a href="/events/series/{E(ev["series_id"])}/">the series</a>. A shared title did not create any date that the source did not list.</p>'
    related = f'<p>{E(ev["related_note"])}</p>' if ev.get('related_note') else ''
    access = f'<p>{E(ev["access_note"])}</p>' if ev.get('access_note') else ''
    import events_listings as listings
    full = listings.section(ev)
    learn = '''<h2>Before you go</h2>
<p>The organiser did not name a prerequisite, a lesson, or a reading list on the fields kept here. Sol.College lessons are optional practice: <a href="/lessons/">Lessons</a>. Sources for reading sit in the <a href="/library/">library</a>.</p>
<h2>After the event</h2>
<p>No recording, slides, or recap is attached. A summary is not written from the listing, and nobody at Sol.College is recorded as having attended.</p>'''
    body = f'''{crumbs([path_span])}
<article class="lesson ev-detail">
<p class=eyebrow>{E(INTENT.get(ev['intent'], 'Event'))} · {E(ev['event_type'])}</p>
<h1>{E(ev['title'])}</h1>
<p class="lead ev-when" data-start="{E(ev.get('start_utc') or '')}" data-end="{E(ev.get('end_utc') or '')}" data-tz="{E(ev.get('timezone') or '')}"><span class=ev-local>{E(when_label(ev))}</span><br><span class=ev-tz>Event time: {E(tz_label(ev['timezone']) if ev.get('timezone') else 'Not stated')}</span><br><span class=ev-yours>Your time: <span class=ev-your>shown when the browser can read a timezone</span></span></p>
<p>{E(summary(ev))}</p>
{related}{access}
<dl class=facts>{dl}</dl>
{reg}{ics}{series}
<p>Original source: <a href="{E(ev['source_url'])}">{E(ev['source_name'])}</a></p>
{full}
{learn}
<p><a href="{E(CORRECTION)}">Something here disagrees with the source</a> · <a href="{E(REPORT)}">Report a suspicious change</a></p>
</article>
{SCRIPT}'''
    return body


def event_ld(ev, path):
    mode = 'https://schema.org/OnlineEventAttendanceMode' if ev['format'] == 'online' else 'https://schema.org/OfflineEventAttendanceMode'
    data = {
        '@context': 'https://schema.org', '@type': 'Event', 'name': ev['title'],
        'description': meta_for(ev), 'url': SITE + path,
        'eventStatus': 'https://schema.org/EventScheduled', 'eventAttendanceMode': mode,
        'startDate': ev['start_utc'], 'endDate': ev['end_utc'],
        'isAccessibleForFree': ev['price'] == 'free',
        'organizer': [{'@type': 'Organization', 'name': n} for n in ev['organisers']] or {'@type': 'Organization', 'name': 'Not named on the host list'},
    }
    if ev['format'] == 'online':
        data['location'] = {'@type': 'VirtualLocation', 'url': ev.get('registration_url') or ev['source_url']}
    elif ev.get('venue'):
        data['location'] = {'@type': 'Place', 'name': ev['venue'], 'address': ev.get('street') or ev.get('city') or ''}
        if ev.get('lat') is not None:
            data['location']['geo'] = {'@type': 'GeoCoordinates', 'latitude': ev['lat'], 'longitude': ev['lng']}
    elif ev.get('city'):
        data['location'] = {'@type': 'Place', 'name': ev['city'], 'address': {'@type': 'PostalAddress', 'addressLocality': ev['city'], 'addressCountry': ev.get('country') or ''}}
    else:
        data['location'] = {'@type': 'Place', 'name': 'City not confirmed'}
    return data


def simple(kicker, title, lead, inner, trail):
    return f'''{crumbs(trail)}<article class=lesson><p class=eyebrow>{E(kicker)}</p><h1>{E(title)}</h1><p class=lead>{E(lead)}</p>{inner}</article>{SCRIPT}'''


def college_page():
    inner = '''<p><b>Hosted by Sol.College:</b> none.</p>
<p><b>Listed by Sol.College:</b> the events on <a href="/events/">the calendar</a>, each with a source.</p>
<p><b>Sponsored placement:</b> none.</p>
<p>Lessons on this site are pages you open when you want them. They are not scheduled classes. No research seminar, journal discussion, newspaper debate, project demonstration, office hour, or club meeting has a published time.</p>
<p>If the college hosts something later, the page will say hosted, and it will carry a start time. A lesson link is not that time.</p>'''
    return simple('Sol.College calendar', 'Hosted by Sol.College',
                  'Nothing on this calendar is a Sol.College class.', inner, ['<span>Sol.College</span>'])


def submit_page():
    inner = f'''<ol>
<li>Paste the original event URL in the public issue.</li>
<li>Copy the details the page actually shows. Leave a blank as not confirmed.</li>
<li>Say what the Solana connection is.</li>
<li>Say whether you are the organiser or you are suggesting someone else's public event.</li>
<li>Submit the issue. A person reads it before anything is published.</li>
</ol>
<p>There is no extractor running on this form. A missing date stays missing. Sol.College will not invent the next session of a series.</p>
<p>Suggesting an event does not make you the organiser. An organiser who wants to claim a listing can say so in the issue. Changes to a registration link, a payment link, or an online joining link need a check against the organiser's own page.</p>
<p>The issue is public. Do not include recovery phrases, private venues, or a list of attendees.</p>
<p><a class=btn href="{E(SUBMIT)}">Open the submission issue</a></p>
<p><a href="{E(REPORT)}">Report a suspicious change</a></p>'''
    return simple('Submission', 'Submit a Solana event',
                  'A public GitHub issue is the queue. It is not an automatic listing.', inner, ['<span>Submit</span>'])


def queue_page():
    items = []
    for row in QUEUE:
        items.append(f'<h2>{E(row["title"])}</h2><p>{E(row["reason"])}</p><p>Shown as: {E(row["where_shown"])}. <a href="{E(row["source_url"])}">Source</a></p>')
    inner = '\n'.join(items) + '<p>These rows are not events. They have no start time on Solana Calendar.</p>'
    return simple('Editorial queue', 'Not published yet',
                  'A name without a checked time stays here.', inner, ['<span>Queue</span>'])


def listings_retrieved():
    import events_listings as listings
    return listings.retrieved_label()


def coverage_page():
    rows = upcoming()
    countries = sorted({e['country'] for e in rows if e.get('country')})
    cities = sorted({e['city'] for e in rows if e.get('city')})
    instant = [e for e in rows if e['series_id']]
    series = sorted({e['series_id'] for e in instant})
    inner = f'''<table class=tbl><tbody>
<tr><th>Active checked sources</th><td>{sum(1 for s in SOURCES if s['status'] == 'checked')}</td></tr>
<tr><th>Sources not producing listings</th><td>{sum(1 for s in SOURCES if s['status'] != 'checked')}</td></tr>
<tr><th>Upcoming published events</th><td>{len(rows)}</td></tr>
<tr><th>Countries with an in-person listing</th><td>{len(countries)}</td></tr>
<tr><th>Cities with a listing</th><td>{len(cities)}</td></tr>
<tr><th>Records in the unpublished queue</th><td>{len(QUEUE)}</td></tr>
<tr><th>Confirmed cancellations</th><td>0</td></tr>
<tr><th>Historical archive rows</th><td>{len(archive())}</td></tr>
<tr><th>Last Superteam refresh</th><td>{E(DATA.get('checked_at') or '')} UTC</td></tr>
</tbody></table>
<p>Countries: {E(', '.join(countries) or 'none')}.</p>
<p>Cities: {E(', '.join(cities) or 'none')}.</p>
<p>Series kept as separate occurrences: {E(', '.join(series) or 'none')}. Nothing was merged on the title alone.</p>
<p>Two in-person listings name an organiser and do not name a city: Solana Demo &amp; Dine, Solana Yacht Cruise.</p>
<p>A deploy of the website does not refresh Luma. Stale times stay until <code>scripts/events_refresh.py</code> is run and the data file is published.</p>
<p>Registration clicks are not attendance. An organiser named here is not a partner.</p>
<p>Host-page wording was retrieved separately on {E(listings_retrieved())} for the Superteam events. It is quoted on those listings. Guest lists and answers are not in that file. The hackathon archive still has no day and no winner list.</p>'''
    return simple('Coverage', 'What this calendar actually holds',
                  'Counts from the current snapshot. Not a claim of global completeness.', inner, ['<span>Coverage</span>'])


def sources_page():
    blocks = []
    for src in SOURCES:
        blocks.append(f'''<h2>{E(src['name'])}</h2>
<p>Status: {E(src['status'])}. Last checked: {E(src['last_checked'] or 'not checked')}.</p>
<p>{E(src['permission'])}</p>
<p>{E(src['refresh'])} <a href="{E(src['url'])}">Source page</a></p>''')
    inner = '\n'.join(blocks) + '<p>The public label on a listing is "Source checked". There is no general verified badge.</p>'
    return simple('Source registry', 'Where listings come from',
                  'A source is either checked, unread, or read without a datable occurrence.', inner, ['<span>Sources</span>'])


def city_index():
    rows = upcoming()
    cities = {}
    for ev in rows:
        if ev.get('city'):
            cities.setdefault(ev['city'], []).append(ev)
    items = []
    for city, group in sorted(cities.items()):
        items.append(f'<li><a href="/events/cities/{slugify(city)}/">{E(city)}</a> · {len(group)} · {E(group[0].get("country") or "")}</li>')
    inner = '<ul>' + '\n'.join(items) + '</ul><p>Follow a city by opening its page and downloading its calendar feed. That feed is not an email list.</p>'
    return simple('Cities', 'Cities with a listing',
                  'A city page exists only where a published event names the city.', inner, ['<span>Cities</span>'])


def city_page(city, group):
    country = group[0].get('country') or ''
    cards = '\n'.join(card(e) for e in group)
    feed = f'/events/feeds/cities/{slugify(city)}.ics'
    inner = f'''<p>Listed by Sol.College. Not hosted here. <a href="{feed}">City calendar feed</a></p>
<div class=grid>{cards}</div>'''
    return simple(country or 'City', 'Solana events in ' + city,
                  'Only occurrences whose source named this city and a start time.', inner,
                  [f'<a href="/events/cities/">Cities</a>', f'<span>{E(city)}</span>'])


def country_index():
    rows = upcoming()
    names = sorted({e['country'] for e in rows if e.get('country')} | {e['online_tag'] for e in rows if e.get('online_tag')})
    items = []
    for name in names:
        items.append(f'<li><a href="/events/countries/{slugify(name)}/">{E(name)}</a></li>')
    inner = '<ul>' + '\n'.join(items) + '</ul>'
    return simple('Countries', 'Countries and tags',
                  'In-person listings use the country on the source. An online tag is labelled as a tag.', inner,
                  ['<span>Countries</span>'])


def country_page(name, group, tagged):
    cards = '\n'.join(card(e) for e in group)
    note = 'These online listings carry this tag. They do not name a city, and the tag is not a venue.' if tagged else 'In-person listings whose source names this country.'
    inner = f'<p>{note}</p><p><a href="/events/feeds/countries/{slugify(name)}.ics">Calendar feed</a></p><div class=grid>{cards}</div>'
    return simple('Country', name, note, inner, [f'<a href="/events/countries/">Countries</a>', f'<span>{E(name)}</span>'])


def series_page(sid, group):
    cards = '\n'.join(card(e) for e in group)
    inner = f'''<p>These are the occurrences on the source at the last check. No further date is generated from the title.</p>
<p><a href="/events/feeds/series/{E(sid)}.ics">Calendar feed for these occurrences</a></p>
<div class=grid>{cards}</div>'''
    return simple('Series', group[0]['title'],
                  'Same title, separate records, each with its own start.', inner,
                  [f'<span>{E(group[0]["title"])}</span>'])


def archive_index():
    items = []
    for ev in archive():
        items.append(f'<li><a href="/events/archive/{E(ev["id"].removeprefix("archive-"))}/">{E(ev["title"])}</a> · {E(ev.get("month_label") or "")}</li>')
    inner = '''<p>The archive describes the series as online hackathons. This calendar does not add a venue, a winner, or a participant count. None of these rows is a future competition.</p>
<ul>''' + '\n'.join(items) + '</ul>'
    return simple('Archive', 'Solana hackathon archive',
                  'Month labels from solana.com/hackathons. Not a schedule.', inner, ['<span>Archive</span>'])


def write_text(S, path, text):
    dest = Path(S) / path.lstrip('/')
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding='utf-8')


def write_page(S, page, path, title, desc, main, data=None):
    doc = page(STYLE + main, title, desc, path)
    if data is not None:
        blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
        doc = doc.replace('</head>', '<script type="application/ld+json">' + blob + '</script></head>', 1)
    if path == '/events/':
        doc = doc.replace('</head>', '<link rel=alternate type=text/calendar href="/events/feeds/all.ics" title="Solana Calendar"></head>', 1)
    if '<h1>' not in doc:
        raise SystemExit('events: missing h1 ' + path)
    write_text(S, path + 'index.html', doc)


def write(S, page, css):
    del css
    pages = []
    desc = 'Solana Calendar: source-checked events with original timezones. A listing is not hosting, and this is not every Solana event.'
    if len(desc) > 158:
        raise SystemExit('events: home description')
    write_page(S, page, '/events/', 'Solana Calendar | Sol.College', desc, home_page())
    pages.append(('/events/', 'Solana Calendar', desc))
    write_text(S, '/events/events.js', (HERE / 'events.js').read_text(encoding='utf-8'))
    write_text(S, '/events/feeds/all.ics', calendar_text(upcoming(), 'Solana Calendar'))
    intents = {}
    for ev in upcoming():
        intents.setdefault(ev['intent'], []).append(ev)
        write_text(S, f'/events/{ev["id"]}/event.ics', calendar_text([ev], ev['title']))
        path = f'/events/{ev["id"]}/'
        d = meta_for(ev)
        write_page(S, page, path, ev['title'] + ' | Solana Calendar', d, detail(ev), event_ld(ev, path))
        pages.append((path, ev['title'], d))
    for intent, group in intents.items():
        write_text(S, f'/events/feeds/intent-{intent}.ics', calendar_text(group, INTENT.get(intent, intent)))
    online = [e for e in upcoming() if e['format'] == 'online']
    write_text(S, '/events/feeds/online.ics', calendar_text(online, 'Solana Calendar online'))

    specs = [
        ('/events/college/', 'Sol.College calendar', 'No Sol.College-hosted event is scheduled. Lessons are pages, not class times.', college_page()),
        ('/events/submit/', 'Submit a Solana event', 'Suggest a public event with its original URL. A person checks it before it is listed.', submit_page()),
        ('/events/queue/', 'Not published yet', 'Listings without a checked time stay off the calendar, including sources this build could not read.', queue_page()),
        ('/events/coverage/', 'Calendar coverage', 'Counts of checked sources, cities, and unpublished rows. Not a claim that every event is listed.', coverage_page()),
        ('/events/sources/', 'Calendar sources', 'Superteam on Luma is the dated source. The Solana events directory was not read in this snapshot.', sources_page()),
        ('/events/cities/', 'Cities with a Solana event', 'City pages exist only where a published listing names the city.', city_index()),
        ('/events/countries/', 'Countries on the calendar', 'Country pages follow the country or tag on a published listing.', country_index()),
        ('/events/archive/', 'Solana hackathon archive', 'Past Solana hackathons by the month the archive states. No day or clock time is added.', archive_index()),
    ]
    for path, title, d, main in specs:
        if len(d) > 158:
            raise SystemExit('events: description over 158 ' + path)
        write_page(S, page, path, title + ' | Solana Calendar', d, main)
        pages.append((path, title, d))

    cities = {}
    for ev in upcoming():
        if ev.get('city'):
            cities.setdefault(ev['city'], []).append(ev)
    for city, group in cities.items():
        path = f'/events/cities/{slugify(city)}/'
        d = f'Solana events in {city} with a checked start time. Listed by Sol.College, not hosted here.'
        if len(d) > 158:
            raise SystemExit('events: city description ' + city)
        write_page(S, page, path, f'Solana events in {city} | Solana Calendar', d, city_page(city, group))
        pages.append((path, city, d))
        write_text(S, f'/events/feeds/cities/{slugify(city)}.ics', calendar_text(group, 'Solana events in ' + city))

    countries = {}
    tagged = {}
    for ev in upcoming():
        if ev.get('country'):
            countries.setdefault(ev['country'], []).append(ev)
        elif ev.get('online_tag'):
            tagged.setdefault(ev['online_tag'], []).append(ev)
    for name, group in list(countries.items()) + list(tagged.items()):
        path = f'/events/countries/{slugify(name)}/'
        d = f'Solana listings for {name}. A tag on an online event is not a venue.'
        if len(d) > 158:
            raise SystemExit('events: country description ' + name)
        write_page(S, page, path, f'{name} | Solana Calendar', d, country_page(name, group, name in tagged))
        pages.append((path, name, d))
        write_text(S, f'/events/feeds/countries/{slugify(name)}.ics', calendar_text(group, 'Solana Calendar ' + name))

    series = {}
    for ev in upcoming():
        if ev.get('series_id'):
            series.setdefault(ev['series_id'], []).append(ev)
    for sid, group in series.items():
        path = f'/events/series/{sid}/'
        d = 'Dated occurrences only. The series title is not a future date.'
        write_page(S, page, path, group[0]['title'] + ' | Solana Calendar', d, series_page(sid, group))
        pages.append((path, group[0]['title'], d))
        write_text(S, f'/events/feeds/series/{sid}.ics', calendar_text(group, group[0]['title']))

    for ev in archive():
        slug = ev['id'].removeprefix('archive-')
        path = f'/events/archive/{slug}/'
        d = meta_for(ev)
        write_page(S, page, path, ev['title'] + ' | Solana Calendar', d, detail(ev))
        pages.append((path, ev['title'], d))

    for path, _t, _d in pages:
        text = Path(S, path.lstrip('/'), 'index.html').read_text(encoding='utf-8')
        if 'Sol.College hosts' in text and 'none' not in text.lower() and path != '/events/college/':
            pass
        if re.search(r'Verified event', text):
            raise SystemExit('events: verified badge ' + path)
    college = Path(S, 'events/college/index.html').read_text(encoding='utf-8')
    if 'Hosted by Sol.College:</b> none.' not in college and 'Hosted by Sol.College:</b> none' not in college:
        if '<b>Hosted by Sol.College:</b> none.' not in college:
            raise SystemExit('events: college page overclaims')
    llms = Path(S) / 'llms.txt'
    if llms.exists():
        block = '\n## Events\n' + ''.join(f'- [{t}]({SITE}{p}): {d}\n' for p, t, d in pages)
        text = re.sub(r'\n## Events\n.*?(?=\n## |\Z)', '', llms.read_text(encoding='utf-8'), flags=re.S)
        llms.write_text(text.rstrip() + '\n' + block, encoding='utf-8')
    print('events:', len(pages), 'pages')
    return [p for p, _t, _d in pages]


def _standalone_page(css_text):
    def page(main, title, desc, path):
        return f'''<!doctype html><html lang=en-GB><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name=description content="{E(desc)}">
<link rel=canonical href="{SITE}{path}">
<style>{css_text}</style></head><body>
<a class=skip href="#main">Skip to content</a>
<header class=top><a class=brand href="/"><span class=logo></span>Sol.College</a>
<nav aria-label=Main><a href="/lessons/">Lessons</a><a href="/events/">Events</a><a href="/articles/">Articles</a></nav></header>
<main id=main>{main}</main></body></html>'''
    return page


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'site'
    css_text = (HERE / 'style.css').read_text(encoding='utf-8')
    write(out, _standalone_page(css_text), '')
