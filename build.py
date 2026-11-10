#!/usr/bin/env python3
"""Generate a date-filtered podcast RSS feed from multiple source podcast feeds."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime, format_datetime
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
import json
import logging
import os
import sys
import tempfile
from urllib.parse import urlparse

from lxml import etree
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ITUNES = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
ATOM = 'http://www.w3.org/2005/Atom'
CONTENT = 'http://purl.org/rss/1.0/modules/content/'
PODCAST = 'https://podcastindex.org/namespace/1.0'
NS = {'itunes': ITUNES, 'atom': ATOM, 'content': CONTENT, 'podcast': PODCAST}
LOG = logging.getLogger('mega-feed')

class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)

def text_only(html: str, max_chars: int = 1400) -> str:
    p = TextOnly()
    try:
        p.feed(html or '')
        return ' '.join(''.join(p.parts).split())[:max_chars]
    except Exception:
        return (html or '')[:max_chars]

def val(parent, tag, default=''):
    if parent is None:
        return default
    node = parent.find(tag, namespaces=NS)
    return (node.text or '').strip() if node is not None and node.text else default

def parse_date(raw):
    if not raw:
        return None
    try:
        d = parsedate_to_datetime(raw)
    except (TypeError, ValueError, IndexError):
        try:
            d = datetime.fromisoformat(raw.replace('Z', '+00:00'))
        except (TypeError, ValueError):
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)

def normalized_url(url: str) -> str:
    p = urlparse(url)
    if p.scheme not in ('https', 'http') or not p.netloc:
        raise ValueError('Only public HTTP(S) feed URLs are supported')
    return url

def fetch(url, max_bytes, timeout=25):
    normalized_url(url)
    retry = Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=retry))
    session.mount('http://', HTTPAdapter(max_retries=retry))
    headers = {'User-Agent': 'NaPodPoMo-MEGA-Feed/0.1 (podcast aggregation; https://napodpomo.org)',
               'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml, */*'}
    try:
        with session.get(url, headers=headers, stream=True, timeout=(10, timeout)) as r:
            r.raise_for_status()
            chunks, length = [], 0
            for piece in r.iter_content(chunk_size=65536):
                if not piece:
                    continue
                length += len(piece)
                if length > max_bytes:
                    raise ValueError(f'Feed exceeded configured maximum of {max_bytes:,} bytes')
                chunks.append(piece)
            return b''.join(chunks)
    finally:
        session.close()

def extract_rss(xml_bytes, source_url, start, end, source_map=None):
    """Returns (selected episodes, totals). Reject malformed/XML entity expansion feeds."""
    parser = etree.XMLParser(resolve_entities=False, no_network=True, recover=False,
                             huge_tree=False, remove_comments=True)
    root = etree.fromstring(xml_bytes, parser)
    channel = root.find('channel')
    if root.tag != 'rss' or channel is None:
        raise ValueError('Expected RSS 2.0 podcast feed (not YouTube Atom)')
    podcast_title = val(channel, 'title', source_url)
    image = ''
    image_el = channel.find('itunes:image', namespaces=NS)
    if image_el is not None:
        image = image_el.get('href', '')
    if not image:
        image = val(channel.find('image'), 'url')
    items = channel.findall('item')
    selected = []
    missing_dates = no_audio = 0
    for item in items:
        date = parse_date(val(item, 'pubDate'))
        if date is None:
            missing_dates += 1
            continue
        if not (start <= date < end):
            continue
        enc = None
        for candidate in item.findall('enclosure'):
            if candidate.get('url') and (candidate.get('type','').lower().startswith('audio/') or
                                         candidate.get('type','').lower() in ('application/ogg', '')):
                enc = candidate
                break
        if enc is None:
            no_audio += 1
            continue
        identity_source = source_url
        episode_podcast = podcast_title
        if source_map is not None:
            origin = item.find('source')
            origin_url = origin.get('url', '') if origin is not None else ''
            if origin_url not in source_map:
                raise ValueError('Bridge item has missing or unrecognized source attribution')
            mapped = source_map[origin_url]
            identity_source = normalized_url(mapped['url'])
            episode_podcast = mapped.get('name') or val(item, 'source') or podcast_title
        guid = val(item, 'guid') or val(item, 'link') or enc.get('url')
        episode_id = sha256((identity_source + '\0' + guid).encode('utf8')).hexdigest()[:32]
        episode_art = item.find('itunes:image', namespaces=NS)
        episode_art_url = episode_art.get('href', '') if episode_art is not None else ''
        duration = val(item, 'itunes:duration')
        explicit = val(item, 'itunes:explicit') or val(channel, 'itunes:explicit')
        author = val(item, 'itunes:author') or episode_podcast
        selected.append({
            'id': episode_id, 'source': identity_source, 'podcast': episode_podcast,
            'title': val(item, 'title', 'Untitled episode'),
            'description': text_only(val(item, 'description') or val(item, 'content:encoded')),
            'link': val(item, 'link'), 'date': date.isoformat(),
            'audio_url': enc.get('url'), 'audio_type': enc.get('type') or 'audio/mpeg',
            'audio_length': enc.get('length') if (enc.get('length') or '').isdigit() else '0',
            'artwork': episode_art_url or image, 'duration': duration,
            'explicit': explicit, 'author': author,
        })
    return selected, {'total': len(items), 'selected': len(selected),
                      'missing_dates': missing_dates, 'selected_without_audio': no_audio}

def merge_episodes(merged, episodes):
    """Keep cached IDs when a show republishes the same enclosure with a new GUID."""
    by_audio = {(e['source'], e['audio_url']): key for key, e in merged.items()}
    seen = set()
    duplicates = 0
    for episode in sorted(episodes, key=lambda e: e['date'], reverse=True):
        key = (episode['source'], episode['audio_url'])
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        episode = dict(episode)
        episode['id'] = by_audio.get(key, episode['id'])
        merged[episode['id']] = episode
        by_audio[key] = episode['id']
    return duplicates

def append(parent, name, text, attrs=None):
    e = etree.SubElement(parent, name, **(attrs or {}))
    e.text = str(text)
    return e

def make_rss(config, entries):
    source_artwork = {mapped['url']: normalized_url(mapped['artwork_url'])
                      for source in config.get('sources', [])
                      for mapped in source.get('source_map', {}).values()
                      if mapped.get('artwork_url')}
    rss = etree.Element('rss', version='2.0', nsmap={'itunes': ITUNES, 'atom': ATOM})
    channel = etree.SubElement(rss, 'channel')
    append(channel, 'title', config['title'])
    append(channel, 'link', config['site_url'])
    append(channel, 'description', config['description'])
    append(channel, 'language', config.get('language', 'en-us'))
    append(channel, f'{{{ITUNES}}}author', config.get('author', 'National Podcast Post Month'))
    append(channel, f'{{{ITUNES}}}summary', config['description'])
    has_explicit = any(str(ep.get('explicit', '')).strip().lower() in ('yes', 'true', '1')
                       for ep in entries)
    append(channel, f'{{{ITUNES}}}explicit', 'true' if has_explicit else 'false')
    if config.get('feed_url'):
        append(channel, f'{{{ATOM}}}link', '', {'href': config['feed_url'], 'rel': 'self',
                                               'type': 'application/rss+xml'})
    if config.get('artwork_url'):
        normalized_url(config['artwork_url'])
        append(channel, f'{{{ITUNES}}}image', '', {'href': config['artwork_url']})
        image = etree.SubElement(channel, 'image')
        append(image, 'url', config['artwork_url'])
        append(image, 'title', config['title'])
        append(image, 'link', config['site_url'])
    for episode in sorted(entries, key=lambda x: (x['date'], x['id']), reverse=True):
        item = etree.SubElement(channel, 'item')
        append(item, 'title', episode['title'])
        if episode.get('link'):
            append(item, 'link', episode['link'])
        append(item, 'guid', 'napodpomo-mega:' + episode['id'], {'isPermaLink': 'false'})
        if episode.get('source'):
            append(item, 'source', episode['podcast'], {'url': episode['source']})
        date = datetime.fromisoformat(episode['date']).astimezone(timezone.utc)
        append(item, 'pubDate', format_datetime(date, usegmt=True))
        append(item, 'description', episode['description'])
        append(item, 'enclosure', '', {'url': episode['audio_url'],
                                      'type': episode['audio_type'],
                                      'length': str(episode.get('audio_length') or '0')})
        append(item, f'{{{ITUNES}}}author', episode.get('author') or episode['podcast'])
        if episode.get('duration'):
            append(item, f'{{{ITUNES}}}duration', episode['duration'])
        artwork = episode.get('artwork') or source_artwork.get(episode.get('source'))
        if artwork:
            append(item, f'{{{ITUNES}}}image', '', {'href': artwork})
        if episode.get('explicit'):
            append(item, f'{{{ITUNES}}}explicit', episode['explicit'])
    return etree.tostring(rss, encoding='utf-8', xml_declaration=True, pretty_print=True)

def save_atomic(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='._mega_')
    try:
        with os.fdopen(fd, 'wb') as fh:
            fh.write(payload)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.remove(name)

def run(cfg_path, output_path, cache_path, offline=False):
    config = json.loads(Path(cfg_path).read_text(encoding='utf8'))
    start = datetime.fromisoformat(config['start'].replace('Z', '+00:00')).astimezone(timezone.utc)
    end = datetime.fromisoformat(config['end'].replace('Z', '+00:00')).astimezone(timezone.utc)
    if not start < end:
        raise ValueError('start must be before end')
    cached = json.loads(Path(cache_path).read_text()) if Path(cache_path).exists() else {}
    merged = {key: x for key, x in cached.items()
              if start <= datetime.fromisoformat(x['date']).astimezone(timezone.utc) < end}
    successes = 0
    diagnostics = []
    for source in config['sources']:
        url = source['url']
        name = source.get('name', url)
        try:
            if offline:
                xml = Path(source['fixture']).read_bytes()
            else:
                xml = fetch(url, config.get('max_source_bytes', 40_000_000))
            episodes, counts = extract_rss(xml, url, start, end, source.get('source_map'))
            counts['duplicate_audio_entries'] = merge_episodes(merged, episodes)
            successes += 1
            diagnostics.append({'source': name, 'status': 'ok', **counts})
            LOG.info('%s: %s items, %s eligible', name, counts['total'], counts['selected'])
        except (requests.RequestException, OSError, ValueError, etree.XMLSyntaxError) as e:
            diagnostics.append({'source': name, 'status': 'error', 'message': str(e)})
            LOG.error('%s: %s', name, e)
    if not successes and not merged:
        raise RuntimeError('No sources succeeded and there is no cached data. Output not replaced.')
    max_items = config.get('max_output_episodes', 1500)
    selected = sorted(merged.values(), key=lambda x: (x['date'], x['id']), reverse=True)[:max_items]
    payload = make_rss(config, selected)
    # Refuse malformed output before replacing anything on disk.
    etree.fromstring(payload, etree.XMLParser(resolve_entities=False, no_network=True))
    save_atomic(output_path, payload)
    save_atomic(cache_path, json.dumps({e['id']: e for e in selected}, indent=2).encode('utf8'))
    print(json.dumps({'output': str(output_path), 'episodes': len(selected),
                      'bytes': len(payload), 'sources': diagnostics}, indent=2))
    return successes

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', default='config-2026.json')
    p.add_argument('--output', default='site/mega-feed.xml')
    p.add_argument('--cache', default='data/episodes-2026.json')
    p.add_argument('--offline', action='store_true', help='Read source fixture paths instead of network')
    p.add_argument('--verbose', action='store_true')
    args = p.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format='%(levelname)s: %(message)s')
    try:
        run(args.config, args.output, args.cache, args.offline)
    except Exception as exc:
        LOG.error('Build failed: %s', exc)
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
