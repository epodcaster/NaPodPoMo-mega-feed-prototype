import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from lxml import etree
from build import extract_rss, make_rss, run, parse_date, merge_episodes


def fixture(n, year, prefix, padding=''):
    episodes = []
    for i in range(n):
        episodes.append(f'''<item><title>{prefix} episode {i}</title>
          <guid>{prefix}-{i}</guid><link>https://example.com/{prefix}/{i}</link>
          <pubDate>{i%28+1:02d} Nov {year} 09:00:00 GMT</pubDate>
          <description><![CDATA[<p>Episode {i} {padding}</p>]]></description>
          <enclosure url="https://media.example.org/{prefix}/{i}.mp3" length="123456" type="audio/mpeg"/>
          <itunes:image href="https://images.example.org/{prefix}/{i}.jpg"/>
          </item>''')
    return (f'''<?xml version="1.0" encoding="UTF-8"?>
      <rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
      <channel><title>{prefix}</title><itunes:image href="https://example.com/{prefix}.jpg"/>
      {''.join(episodes)}</channel></rss>''').encode()

class BuildTests(unittest.TestCase):
    def test_small_medium_oversized(self):
        start = datetime(2026, 11, 1, tzinfo=timezone.utc)
        end = datetime(2026, 12, 1, tzinfo=timezone.utc)
        for n, padding in [(3, ''), (31, ''), (500, 'X'*12000)]:
            xml = fixture(n, 2026, 'show', padding)
            if n == 500:
                self.assertGreater(len(xml), 5_242_880)
            episodes, stats = extract_rss(xml, 'https://example.com/feed', start, end)
            self.assertEqual(n, stats['total'])
            self.assertEqual(n, len(episodes))
            self.assertEqual(episodes[0]['artwork'], 'https://images.example.org/show/0.jpg')
            self.assertLess(len(episodes[0]['description']), 1500)
    def test_archive_date_filter(self):
        start = datetime(2026, 11, 1, tzinfo=timezone.utc)
        end = datetime(2026, 12, 1, tzinfo=timezone.utc)
        self.assertEqual(extract_rss(fixture(31, 2023, 'archive'), 'https://example.com/feed', start, end)[0], [])
        start23 = datetime(2023, 11, 1, tzinfo=timezone.utc)
        end23 = datetime(2023, 12, 1, tzinfo=timezone.utc)
        self.assertEqual(len(extract_rss(fixture(31, 2023, 'archive'), 'https://example.com/feed', start23, end23)[0]),31)
    def test_feed_xml_and_guids(self):
        start = datetime(2026, 11, 1, tzinfo=timezone.utc)
        end = datetime(2026, 12, 1, tzinfo=timezone.utc)
        episodes, _ = extract_rss(fixture(3, 2026, 'show'), 'https://example.com/feed', start, end)
        conf = {'title':'Test MEGA','site_url':'https://napodpomo.org/','description':'Test feed','artwork_url':'https://example.com/cover.jpg'}
        doc = etree.fromstring(make_rss(conf, episodes))
        self.assertEqual(len(doc.findall('./channel/item')),3)
        self.assertEqual(doc.find('./channel/{http://www.itunes.com/dtds/podcast-1.0.dtd}image').get('href'), conf['artwork_url'])
        self.assertEqual(len(set(item.findtext('guid') for item in doc.findall('./channel/item'))),3)
    def test_failure_keeps_cached_data_and_deduplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            xml = folder/'small.xml'
            xml.write_bytes(fixture(3, 2026, 'small'))
            config = {'title':'Test','site_url':'https://napodpomo.org/',
                     'description':'test','start':'2026-11-01T00:00:00+00:00',
                     'end':'2026-12-01T00:00:00+00:00',
                     'sources':[{'url':'https://example.com/test','fixture':str(xml)}]}
            c=folder/'cfg.json'; c.write_text(json.dumps(config))
            out=folder/'rss.xml'; cache=folder/'cache.json'
            run(c,out,cache,offline=True)
            run(c,out,cache,offline=True)
            self.assertEqual(len(etree.fromstring(out.read_bytes()).findall('./channel/item')),3)
            xml.unlink()
            run(c,out,cache,offline=True)
            self.assertEqual(len(etree.fromstring(out.read_bytes()).findall('./channel/item')),3)
    def test_date_parsing(self):
        self.assertIsNotNone(parse_date('Wed, 04 Nov 2026 12:04:33 +0000'))
        self.assertIsNone(parse_date('not a date'))

    def test_bridge_preserves_identity_and_show_attribution(self):
        start = datetime(2026, 11, 1, tzinfo=timezone.utc)
        end = datetime(2026, 12, 1, tzinfo=timezone.utc)
        direct_url = 'https://example.com/original.rss'
        direct, _ = extract_rss(fixture(1, 2026, 'show'), direct_url, start, end)
        root = etree.fromstring(fixture(1, 2026, 'show'))
        root.find('./channel/title').text = 'Combined bridge'
        etree.SubElement(root.find('./channel/item'), 'source', url='https://example.com/podcast').text = 'Original show'
        mapping = {'https://example.com/podcast': {'url': direct_url, 'name': 'Original show'}}
        bridged, _ = extract_rss(etree.tostring(root), 'https://bridge.example/feed', start, end, mapping)
        self.assertEqual(bridged[0]['id'], direct[0]['id'])
        self.assertEqual(bridged[0]['source'], direct_url)
        self.assertEqual(bridged[0]['podcast'], 'Original show')
        self.assertEqual(bridged[0]['author'], 'Original show')
        self.assertEqual(bridged[0]['audio_url'], direct[0]['audio_url'])
        self.assertEqual(bridged[0]['date'], direct[0]['date'])
        doc = etree.fromstring(make_rss({'title':'Test','site_url':'https://example.com','description':'Test'}, bridged))
        self.assertEqual(doc.find('./channel/item/source').get('url'), direct_url)
        self.assertEqual(doc.findtext('./channel/item/source'), 'Original show')

    def test_bridge_rejects_missing_or_unknown_source(self):
        root = etree.fromstring(fixture(1, 2026, 'show'))
        for source_url in [None, 'https://unexpected.example/podcast']:
            with self.subTest(source=source_url):
                if source_url:
                    etree.SubElement(root.find('./channel/item'), 'source', url=source_url).text = 'Unexpected'
                with self.assertRaisesRegex(ValueError, 'source attribution'):
                    extract_rss(etree.tostring(root), 'https://bridge.example/feed',
                                datetime(2026, 11, 1, tzinfo=timezone.utc),
                                datetime(2026, 12, 1, tzinfo=timezone.utc), {})

    def test_duplicate_audio_keeps_latest_title_and_cached_identity(self):
        episodes, _ = extract_rss(fixture(2, 2026, 'show'), 'https://example.com/feed',
                                 datetime(2026, 11, 1, tzinfo=timezone.utc),
                                 datetime(2026, 12, 1, tzinfo=timezone.utc))
        episodes[1]['audio_url'] = episodes[0]['audio_url']
        merged = {}
        self.assertEqual(merge_episodes(merged, episodes), 1)
        self.assertEqual(len(merged), 1)
        cached_id = next(iter(merged))
        self.assertEqual(merged[cached_id]['title'], 'show episode 1')
        updated = dict(episodes[1], id='new-upstream-guid', title='Updated title')
        merge_episodes(merged, [updated])
        self.assertEqual(list(merged), [cached_id])
        self.assertEqual(merged[cached_id]['title'], 'Updated title')

    def test_same_audio_on_different_shows_is_not_collapsed(self):
        episodes, _ = extract_rss(fixture(2, 2026, 'show'), 'https://example.com/feed',
                                 datetime(2026, 11, 1, tzinfo=timezone.utc),
                                 datetime(2026, 12, 1, tzinfo=timezone.utc))
        episodes[1]['audio_url'] = episodes[0]['audio_url']
        episodes[1]['source'] = 'https://other.example/feed'
        merged = {}
        self.assertEqual(merge_episodes(merged, episodes), 0)
        self.assertEqual(len(merged), 2)

    def test_combined_feed_explicit_flag(self):
        episodes, _ = extract_rss(fixture(2, 2026, 'show'), 'https://example.com/feed',
                                 datetime(2026, 11, 1, tzinfo=timezone.utc),
                                 datetime(2026, 12, 1, tzinfo=timezone.utc))
        conf = {'title': 'Test', 'site_url': 'https://example.com', 'description': 'Test'}
        for flag in ['true', 'yes', '1', ' TRUE ']:
            episodes[1]['explicit'] = flag
            doc = etree.fromstring(make_rss(conf, episodes))
            self.assertEqual(doc.findtext('./channel/{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit'), 'true')
        episodes[1]['explicit'] = 'false'
        doc = etree.fromstring(make_rss(conf, episodes))
        self.assertEqual(doc.findtext('./channel/{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit'), 'false')

    def test_episode_inherits_explicit_flag_unless_overridden(self):
        root = etree.fromstring(fixture(2, 2026, 'show'))
        tag = '{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit'
        etree.SubElement(root.find('channel'), tag).text = 'true'
        etree.SubElement(root.findall('./channel/item')[1], tag).text = 'false'
        episodes, _ = extract_rss(etree.tostring(root), 'https://example.com/feed',
                                 datetime(2026, 11, 1, tzinfo=timezone.utc),
                                 datetime(2026, 12, 1, tzinfo=timezone.utc))
        self.assertEqual([ep['explicit'] for ep in episodes], ['true', 'false'])

    def test_exact_month_boundaries(self):
        start = datetime.fromisoformat('2026-11-01T00:00:00-04:00')
        end = datetime.fromisoformat('2026-12-01T00:00:00-05:00')
        root = etree.fromstring(fixture(4, 2026, 'boundary'))
        dates = ['01 Nov 2026 03:59:59 GMT', '01 Nov 2026 04:00:00 GMT',
                 '01 Dec 2026 04:59:59 GMT', '01 Dec 2026 05:00:00 GMT']
        for item, date in zip(root.findall('./channel/item'), dates):
            item.find('pubDate').text = date
        episodes, _ = extract_rss(etree.tostring(root), 'https://example.com/feed', start, end)
        self.assertEqual([ep['title'] for ep in episodes],
                         ['boundary episode 1', 'boundary episode 2'])

    def test_missing_date_and_audio_are_reported(self):
        root = etree.fromstring(fixture(3, 2026, 'invalid'))
        items = root.findall('./channel/item')
        items[0].find('pubDate').text = 'invalid'
        items[1].remove(items[1].find('enclosure'))
        episodes, counts = extract_rss(etree.tostring(root), 'https://example.com/feed',
                                      datetime(2026, 11, 1, tzinfo=timezone.utc),
                                      datetime(2026, 12, 1, tzinfo=timezone.utc))
        self.assertEqual(len(episodes), 1)
        self.assertEqual(counts['missing_dates'], 1)
        self.assertEqual(counts['selected_without_audio'], 1)

    def test_total_failure_preserves_previous_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            cfg = folder / 'config.json'
            cfg.write_text(json.dumps({
                'start': '2026-11-01T00:00:00+00:00',
                'end': '2026-12-01T00:00:00+00:00',
                'sources': [{'url': 'https://example.com/feed',
                             'fixture': str(folder / 'missing.xml')}]}))
            out = folder / 'rss.xml'
            out.write_bytes(b'previous feed')
            with self.assertRaises(RuntimeError):
                run(cfg, out, folder / 'cache.json', offline=True)
            self.assertEqual(out.read_bytes(), b'previous feed')
            self.assertFalse((folder / 'cache.json').exists())

if __name__=='__main__':
    unittest.main()
