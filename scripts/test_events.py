"""Calendar records stay inside what the sources actually said."""
import os, tempfile, unittest
from pathlib import Path

import events
import events_refresh as refresh


def guests_only():
    return {
        'event': {
            'api_id': 'evt-test-hidden', 'name': 'Closed Door Session',
            'start_at': '2026-12-01T15:00:00.000Z', 'end_at': '2026-12-01T17:00:00.000Z',
            'timezone': 'Asia/Dubai', 'location_type': 'offline', 'url': 'closed-door',
            'geo_address_visibility': 'guests-only',
            'geo_address_info': {
                'mode': 'obfuscated', 'city': 'Dubai', 'country': 'United Arab Emirates',
                'country_code': 'AE', 'address': 'Secret Hall', 'full_address': '1 Secret Street',
            },
            'coordinate': {'latitude': 25.1, 'longitude': 55.2},
        },
        'hosts': [{'name': 'Superteam Middle East'}],
        'ticket_info': {'is_free': True, 'require_approval': True, 'is_sold_out': False},
        'tags': [], 'waitlist_active': False,
    }


def public_venue():
    entry = guests_only()
    entry['event'] = dict(entry['event'])
    entry['event']['api_id'] = 'evt-test-public'
    entry['event']['name'] = 'Public Hall Session'
    entry['event']['url'] = 'public-hall'
    entry['event']['geo_address_visibility'] = 'public'
    entry['event']['geo_address_info'] = dict(entry['event']['geo_address_info'])
    entry['event']['geo_address_info']['mode'] = 'shown'
    return entry


class Refresh(unittest.TestCase):
    def test_guests_only_drops_the_venue(self):
        ev = refresh.normalise_superteam(guests_only(), '2026-11-17T10:40:00Z')
        self.assertEqual(ev['city'], 'Dubai')
        self.assertIsNone(ev['venue'])
        self.assertIsNone(ev['street'])
        self.assertIsNone(ev['lat'])
        self.assertEqual(ev['price'], 'free')
        self.assertTrue(ev['approval_required'])

    def test_public_venue_keeps_the_address(self):
        ev = refresh.normalise_superteam(public_venue(), '2026-11-17T10:40:00Z')
        self.assertEqual(ev['venue'], 'Secret Hall')
        self.assertEqual(ev['lat'], 25.1)

    def test_missing_price_is_not_free(self):
        entry = public_venue()
        entry['ticket_info'] = {'is_free': False, 'price': None}
        ev = refresh.normalise_superteam(entry, '2026-11-17T10:40:00Z')
        self.assertEqual(ev['price'], 'not confirmed')

    def test_online_has_no_city(self):
        entry = public_venue()
        entry['event']['location_type'] = 'zoom'
        ev = refresh.normalise_superteam(entry, '2026-11-17T10:40:00Z')
        self.assertEqual(ev['format'], 'online')
        self.assertEqual(ev['city'], '')
        self.assertIsNone(ev['lat'])

    def test_snapshot_has_no_hidden_coordinates(self):
        for ev in events.EVENTS:
            if ev.get('lat') is not None:
                self.assertTrue(ev.get('venue'), ev['id'])
            if ev['format'] == 'online':
                self.assertFalse(ev.get('city'))
                self.assertIsNone(ev.get('lat'))
            if ev['precision'] == 'month':
                self.assertIsNone(ev['start_utc'])
            if ev['listing'] != 'listed':
                self.fail(ev['id'])


class Pages(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.S = self.tmp.name
        css = Path(__file__).parent.joinpath('style.css').read_text(encoding='utf-8')
        events.write(self.S, events._standalone_page(css), '')

    def tearDown(self):
        self.tmp.cleanup()

    def read(self, path):
        return Path(self.S, path.lstrip('/')).read_text(encoding='utf-8')

    def test_home_lists_a_checked_event_and_the_limit(self):
        text = self.read('/events/index.html')
        self.assertIn('Solana Calendar', text)
        self.assertIn('Coworking Fridays Belgrade', text)
        self.assertIn('not every Solana event', text)
        self.assertIn('Source checked', text)
        self.assertNotIn('Verified event', text)
        self.assertIn('id=ev-q', text)
        self.assertNotIn('Solana Builder Epoch', text)

    def test_hidden_venue_is_absent_from_the_page_and_the_feed(self):
        # London co-working is guests-only. Belgrade publishes its hall.
        london = self.read('/events/london-nov-20/index.html')
        self.assertIn('street address is not public', london)
        self.assertNotIn('latitude', london.lower())
        ics = self.read('/events/london-nov-20/event.ics')
        self.assertIn('DTSTART:20261120T100000Z', ics)
        self.assertIn('UID:london-nov-20@sol.college', ics)
        self.assertNotIn('Secret', ics)
        self.assertIn('London', ics)
        belgrade = self.read('/events/coworking-fridays-belgrade/event.ics')
        self.assertIn('Savska', belgrade)

    def test_online_page_names_no_city(self):
        text = self.read('/events/aq7rqqmn/index.html')
        self.assertIn('names no city', text)
        self.assertIn('America/Toronto', text)
        spain = self.read('/events/4j37rbu1/index.html')
        self.assertIn('Etc/GMT', spain)
        self.assertIn('No city is given', spain)

    def test_archive_has_no_invented_day(self):
        text = self.read('/events/archive/solana-frontier/index.html')
        self.assertIn('April 2026', text)
        self.assertIn('not a start day', text)
        self.assertFalse(os.path.exists(os.path.join(self.S, 'events/archive/solana-frontier/event.ics')))
        self.assertNotIn('application/ld+json', text)

    def test_college_hosts_nothing(self):
        text = self.read('/events/college/index.html')
        self.assertIn('Hosted by Sol.College:</b> none.', text)

    def test_city_pages_exist_only_for_named_cities(self):
        self.assertTrue(os.path.exists(os.path.join(self.S, 'events/cities/london/index.html')))
        self.assertFalse(os.path.exists(os.path.join(self.S, 'events/cities/paris/index.html')))
        self.assertIn('Beograd', self.read('/events/cities/belgrade/index.html'))

    def test_queue_is_not_an_event(self):
        text = self.read('/events/queue/index.html')
        self.assertIn('Solana Builder Epoch', text)
        self.assertIn('not events', text)
        self.assertIn('Colosseum', text)

    def test_feed_keeps_a_stable_uid(self):
        text = self.read('/events/feeds/all.ics')
        self.assertEqual(text.count('UID:london-nov-20@sol.college'), 1)
        self.assertNotIn('DTSTART:202604', text)

    def test_solana_listing_quotes_the_host_and_keeps_a_hidden_venue_hidden(self):
        padel = self.read('/events/solanapadelmatchdxb/index.html')
        self.assertIn('upon approval', padel)
        self.assertIn('friendly competition', padel)
        self.assertIn('did not count who came', padel)
        self.assertNotIn('Sol.College attended', padel)
        london = self.read('/events/london-nov-20/index.html')
        self.assertIn('street address is not public', london)
        self.assertIn('Solana UK Telegram', london)
        self.assertNotIn('121 King', london)
        yacht = self.read('/events/solanayachtcruisesuperweek/index.html')
        self.assertIn('40', yacht)
        self.assertIn('not a count of people who arrived', yacht.lower())

    def test_archive_listing_does_not_grow_a_day(self):
        text = self.read('/events/archive/solana-frontier/index.html')
        self.assertIn('not a start day', text)
        self.assertIn('Winner names on the archive page were not copied.', text)
        self.assertNotIn('DTSTART', text)
        self.assertIn('Prediction Markets Hackathon', text)

    def test_a_host_series_is_not_split_into_extra_events(self):
        text = self.read('/events/lmy1gn6j/index.html')
        self.assertIn('not published as another event', text)
        self.assertIn('2026年11月27日', text)
        self.assertNotIn('ouid=', text)

    def test_topic_only_event_does_not_pretend_the_host_wrote_solana(self):
        text = self.read('/events/zupaxmas/index.html')
        self.assertIn('do not contain the word', text)
        self.assertIn('Al Hamra', text)

    def test_listings_are_an_order_of_magnitude_longer(self):
        # Detail pages before this expansion were 11,996 words.
        import re as _re
        total = 0
        for ev in events.EVENTS:
            html = events.detail(ev)
            html = _re.sub(r'<script[\s\S]*?</script>', ' ', html)
            html = _re.sub(r'<[^>]+>', ' ', html)
            total += len(_re.findall(r"[A-Za-z0-9''-]+", html))
        self.assertGreaterEqual(total, 11996 * 10)


if __name__ == '__main__':
    unittest.main()
