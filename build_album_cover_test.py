#!/usr/bin/env python3
"""Build a small, separate RSS trial using each podcast's main cover only."""
import argparse
import json
from pathlib import Path
from urllib.parse import urljoin

from build import make_rss, save_atomic

TRIAL_SOURCES = (
    'https://podcasthottake.com/feed/podcast/',
    'https://feeds.blubrry.com/feeds/linuxstory.xml',
    'https://api.substack.com/feed/podcast/11679990.rss',
)


def make_trial(config, cached):
    entries = []
    for source in TRIAL_SOURCES:
        available = sorted((e for e in cached.values() if e['source'] == source),
                           key=lambda e: (e['date'], e['id']), reverse=True)
        cover = next((e.get('podcast_artwork') for e in available
                      if e.get('podcast_artwork')), '')
        # The same supplied cover is verified over HTTPS for this isolated trial.
        if source == TRIAL_SOURCES[0]:
            cover = cover.replace('http://podcasthottake.com/',
                                  'https://podcasthottake.com/', 1)
        if not available:
            raise ValueError('Album-cover trial source has no cached episodes: ' + source)
        for episode in available[:2]:
            copied = dict(episode)
            copied['id'] = 'album-cover-trial-' + episode['id']
            copied['title'] = episode['podcast'] + ': ' + episode['title']
            if cover:
                copied['podcast_artwork'] = cover
            entries.append(copied)
    trial_config = dict(config)
    trial_config.update(
        title='NaPodPoMo Podcast Album Cover Test',
        description='Separate six-episode beta test. Each podcast uses its own main cover on both episodes; the feed keeps the NaPodPoMo MEGA Feed cover. Audio stays on original hosts.',
        artwork_preference='podcast',
        feed_url=urljoin(config['feed_url'], 'album-cover-test.xml'),
    )
    return make_rss(trial_config, entries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--cache', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    cached = json.loads(Path(args.cache).read_text())
    payload = make_trial(config, cached)
    save_atomic(args.output, payload)
    print(json.dumps({'album_cover_test': args.output, 'bytes': len(payload)}))


if __name__ == '__main__':
    main()
