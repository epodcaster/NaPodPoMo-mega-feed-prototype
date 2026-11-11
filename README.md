# NaPodPoMo 2026 MEGA Feed

The live NaPodPoMo 2026 aggregate collects November audio episodes from participating podcasts. Participation is open throughout November, and maintainers can add feeds at any time. Audio stays on the creators' original hosts.

## Listener links

- Combined RSS: https://epodcaster.github.io/NaPodPoMo-mega-feed-prototype/mega-feed.xml
- OPML import: https://epodcaster.github.io/NaPodPoMo-mega-feed-prototype/napodpomo-2026-mega-feed.opml
- Subscription page: https://epodcaster.github.io/NaPodPoMo-mega-feed-prototype/

The OPML contains one RSS subscription: the combined MEGA Feed. It does not subscribe listeners individually to all participant podcasts. New shows and episodes are delivered through the same combined RSS URL; no repeat OPML import is needed. Existing beta subscribers keep the same RSS URL and episode GUIDs.

## Current configuration

The authoritative live configuration is `config-prototype.json` (legacy filename retained for continuity). It represents 30 shows through 26 direct feeds and one separate Feed Informer digest for four Substack shows. The 2023 configuration and initial three-source configuration remain historical examples, not the live source list.

The published title and description identify the NaPodPoMo 2026 MEGA Feed. `artwork_preference: podcast` uses each podcast's main cover on its episodes. The MEGA Feed retains its own 2048 × 2048 RGB JPEG cover under `assets/mega-feed-cover-2026-v2.jpg`. The supplied file was validated, and 2048 square is within Apple's accepted 1400–3000 RSS cover range.

Per-podcast covers and the feed's cover have been confirmed together in Pocket Casts with Use episode artwork enabled. Apple Podcasts displayed the MEGA Feed cover but not item-level images in our direct-RSS tests. Three bridged Substack shows still need confirmed public cover URLs: Outrage Science Bites, The Lessons Learned Series, and A3Day Expanded Podcast. Apps can use the MEGA Feed cover where individual covers are unavailable.

## Add a late participant

1. Obtain the show name and complete public podcast RSS URL. Do not commit private subscriber tokens.
2. Check that the URL returns RSS 2.0, publication dates, and original audio enclosures.
3. For a regular feed, add `{"name": "Podcast name", "url": "https://example.com/podcast.rss"}` to the live configuration's sources array. Keep existing source URLs stable so identities remain consistent.
4. For a Substack show, add its public podcast RSS to the separate Feed Informer digest, then add a source_map entry mapping the exact source page URL in the digest to that podcast's name and canonical public RSS URL. Configure artwork_url there if its public cover is known. Complete both changes together: an unrecognized bridge source rejects that bridge input while retaining previously cached episodes.
5. Commit the configuration change to main. This automatically runs tests, collects feeds, preserves episode metadata, and publishes. Inspect per-source counts and confirm the new show's episodes in the public XML.

The first collection backfills only eligible November episodes still present in the source's current RSS. Previously removed episodes require an archive or separate import. Existing cached discoveries are retained. Only November episodes fit the configured date window, regardless of the date a participant is added.

The Substack-only digest is https://feed.informer.com/digests/3IWM108UBD/feeder.rss. Maintain sufficient output headroom (at least 200 items if available) so new entries remain visible between collections. Its original 50-item window has been observed. The bridge preserves dates, audio URLs, show names, and source links but omits artwork, duration, and explicit flags unless supplied separately. Within a show, repeated exact audio URLs are collapsed and cached aggregate GUIDs remain stable when upstream GUIDs change.

## Automation and retention

GitHub Actions runs at minute 17 every three hours UTC throughout November, plus December 1–2 for final collection of late-November entries. Scheduled processing is limited to 2026. Manual runs remain available. GitHub scheduling is best effort. Changes to configuration, build code, tests, workflow, or assets trigger a build; cache-only commits and documentation commits do not loop.

The month window is November 1, 2026 00:00 Eastern through December 1, 2026 00:00 Eastern, end-exclusive. Each source is capped at 40 MB and the output/cache at 1,500 episodes. Oldest entries beyond the cap are dropped. Descriptions are plain text truncated to 1,400 characters. Transcripts, chapters, and advanced Podcasting 2.0 metadata are not copied in this implementation.

A source failure uses cached discoveries when available. A complete failure with no cache fails without replacing the local output. Inspect logs even when publication succeeds. Image/media server compatibility and podcast app caching are separate from XML validity.

## Maintenance commands

```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v
python build.py --config config-prototype.json --output site/mega-feed.xml --cache data/episodes-prototype-2026.json
```

The workflow supplies actual Pages URLs when publishing. Local runs use the configuration's URLs; it currently retains a placeholder site_url that the workflow replaces.

## Historical tests

See SOURCE_TEST_REPORT.md, ARTWORK_DIAGNOSTIC.md, and ALBUM_COVER_TEST.md for the trial history. The two diagnostic RSS feeds and their test OPML remain separate from the live subscription. Seventeen automated tests passed before launch; live deployment checks are recorded in LIVE_FEED.md.

Promotion changes the hosted feed's metadata, cover selection, and import links. It does not change napodpomo.org, the existing Feed Informer MEGA Feed, or any participant's source feed.
