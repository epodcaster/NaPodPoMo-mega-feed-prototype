# Initial three-source prototype test report

Tested November 10, 2026, using Python 3.12. Original ZIP retained unchanged; this package is a separate v0.2 copy.

## Automated tests

Original project: **5/5 passed** after installing requirements. Updated package: **8/8 passed**. Coverage includes large XML input above 5,242,880 bytes, date filtering and exact month boundaries, XML generation, stable deduplication/cache retention, invalid dates/missing enclosures, and failure without overwriting an existing feed.

Logs: `test-results/unit-tests.log` and `test-results/unit-tests-v02.log`. Error messages for deliberately missing fixture files are expected test scenarios.

## Live source tests

| Source | Items read | November 2026 selected | November 2023 selected |
| --- | ---: | ---: | ---: |
| Podcast Hot Take | 9 | 9 | 0 |
| NaPodPoMo 2023 archive | 31 | 0 | 21 |
| The Pharmacist's Voice | 386 | 10 | 4 |
| Total | 426 | 19 | 25 |

Every source parsed successfully. Neither date window reported missing publication dates or eligible items without audio. The 31-item archive contributes 21 items within the configured November 2023 window, not all 31 feed items.

The original 2026 build was 34,280 bytes; the historical build was 27,412 bytes. These sizes are for the original configuration titles/descriptions. Both generated RSS documents parsed successfully. All selected dates are inside their respective windows; each output has unique GUIDs and audio URLs. The prototype configuration was also built live using the same sources.

## Audio spot checks

One selected episode from each of the three podcasts returned HTTP 206, content type `audio/mpeg`, and a 1,024-byte sample. This verifies basic audio URL reachability, not full playback. Redirects were followed; the aggregator itself retains original enclosure URLs.

## Deployment status

Deployed successfully on November 10, 2026. Run 42773532032 passed all eight tests, fetched all three sources, built 19 episodes, uploaded the Pages artifact, and completed deployment. The cache-preservation step succeeded with no changed entries, so a new cache commit/push was not exercised.

Live feed: https://epodcaster.github.io/NaPodPoMo-mega-feed-prototype/mega-feed.xml

The published feed returned HTTP 200 with application/xml content, parsed successfully, and contained 19 unique GUIDs and 19 audio enclosures. All dates are inside the November 2026 window, and the Atom self URL matches the published URL. Output size: 34,433 bytes.

Only the new prototype repository and its GitHub Pages publication were changed. No changes were made to napodpomo.org, DNS, or the existing MEGA Feed.

## Acceptance checks still needed

- A second cache-preserving run and a cache commit when new metadata is discovered.
- Direct RSS subscription in a podcast app.
- Podcast-app playback and artwork display.
- Observe a later automatic update before considering any production use.

Channel artwork remains unset; advanced podcast metadata is not preserved. The initial version marked the aggregate channel non-explicit even if an individual entry was explicit. The expanded-source version corrects this and adds regression tests; see SOURCE_TEST_REPORT.md. Advanced metadata and app playback remain acceptance checks.
