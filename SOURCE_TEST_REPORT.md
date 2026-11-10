# Current prototype status

The configuration now covers the supplied 30 shows using 26 direct feeds and one separate Feed Informer digest for the four Substack shows. See the latest bridge trial below; earlier sections document the preceding tests.

# Expanded source trial, November 10, 2026

30 entries were supplied. All 30 public URLs are now configured, including the five supplied 3Speak URLs. Modulations uses its public 3Speak feed; no private subscription URL is included. The original 2023 archive remains available in the historical test configuration and is no longer an active 2026 source.

## Local results

All 10 automated tests passed. 26 sources returned RSS; four Substack endpoints returned a 195-byte HTML Site Unavailable page in this environment. They remain configured for an independent GitHub-hosted check. With Kim Newlove’s canonical Libsyn feed substituted for her website feed, the local combined output contains 168 unique episodes and audio URLs, is 274,530 bytes, and parses as XML.

| Source | Local status | November episodes |
| --- | --- | ---: |
| Computer Freedom | RSS OK | 5 |
| Revivassance Podcast | HTML unavailable page | Pending |
| Simple Joe | RSS OK | 10 |
| Hidden In Plain Sight | RSS OK | 9 |
| Oh That's A Fact | RSS OK | 9 |
| Mike Dell's World | RSS OK | 0 |
| This Podcast Is... Uncalled For | RSS OK | 2 |
| Outrage Science Bites | HTML unavailable page | Pending |
| Stories of Change: Helping You Navigate What's Next | RSS OK | 9 |
| A Second First Look | RSS OK | 5 |
| Jordan's Knowledge | RSS OK | 6 |
| Matcha Moments — NaPodPoMo 2026 | RSS OK | 1 |
| sm2n on Anchor | RSS OK | 10 |
| Podcast Hot Take | RSS OK | 9 |
| NaPodPoMo 2026 (stand) | RSS OK | 9 |
| Kim Newlove (The Pharmacist's Voice) | RSS OK | 10 |
| From Cork With Love - by Paul O'Mahony @omaniblog | RSS OK | 9 |
| Connecting Body, Environments and Systems in Holistic Women's Health \| Perfect CARE Play-versations | RSS OK | 0 |
| Automating By Design: Your Business, Life, and Legacy | RSS OK | 1 |
| Micless | RSS OK | 10 |
| The Lessons Learned Series | HTML unavailable page | Pending |
| Black Girls Consult TOO! | RSS OK | 8 |
| A3Day Expanded Podcast | HTML unavailable page | Pending |
| Elsie, As Is | RSS OK | 9 |
| Nomadic Diaries | RSS OK | 7 |

| Kagok Talk Podcast | RSS OK | 6 |
| NaPodPoMo 2026 (Shaine) | RSS OK | 7 |
| NaPodPoMo 2026 (Steve Clark) | RSS OK | 9 |
| Official NaPodPoMo 2026 | RSS OK | 6 |
| Modulations (public feed) | RSS OK | 2 |

## Source corrections and findings

- Kim Newlove: the supplied website feed contained 10 eligible dated items but no audio enclosures. The verified Libsyn feed at https://feeds.libsyn.com/228308/rss contains 10 November audio episodes, is 6,756,866 bytes, and is within the prototype’s 40 MB limit. The original source URL is retained for these episodes so their GUIDs do not change.
- Mike Dell’s World: the supplied feed’s latest item is May 29, 2026; zero episodes fit November. This is a source date result, not a download failure.
- Perfect CARE: the supplied feed contains one trailer dated February 9, 2026; zero episodes fit November.
- Explicit content: item flags now inherit the source channel flag when absent. The combined channel is marked explicit if any included item is explicitly flagged. Episode-specific false flags override their source channel default. Two regression tests cover this.
- Configuration/code changes now trigger a build on main. Cache-only commits and documentation changes do not trigger a new build, avoiding a cache commit loop. The November 2026 three-hour schedule is unchanged.

## 3Speak checks

All five feeds parsed as RSS with audio/mpeg enclosures. Each contributed only November 2026 episodes. One audio URL from each feed returned HTTP 206, audio/mpeg, and a 1,024-byte sample. This verifies reachability, not podcast-app playback. The newly added 30 episodes introduce no duplicate GUIDs or audio URLs in the 168-item combined feed.

## Initial 25-source GitHub-hosted check

Automatic push-triggered run 42774668017 completed both build and deployment successfully. All 10 tests passed on GitHub. 21 feeds parsed successfully; Revivassance Podcast, Outrage Science Bites, The Lessons Learned Series, and A3Day Expanded Podcast each returned HTTP 403 from their supplied api.substack.com URLs. They are configured but currently contribute no episodes. An attempted public-publication lookup did not establish usable replacement feeds.

The published prototype was independently fetched and validated: HTTP 200, 138 episodes, 138 unique GUIDs, 138 unique audio URLs, correct Atom self URL, all dates within the configured November window, and aggregate explicit=true. Published size: 230,301 bytes. Mike Dell’s World and Perfect CARE remain at zero November episodes.

Live feed: https://epodcaster.github.io/NaPodPoMo-mega-feed-prototype/mega-feed.xml

Workflow: https://github.com/epodcaster/NaPodPoMo-mega-feed-prototype/actions/runs/42774668017

The three-hour November 2026 schedule remains configured; its first scheduled execution and podcast-app playback are still outstanding checks. No changes were made to napodpomo.org or the existing MEGA Feed.

## Current 30-source deployment

Run 42775680500 completed build and deployment successfully. All 10 tests passed, 26 of 30 sources loaded successfully, and the same four Substack endpoints returned HTTP 403. All five new 3Speak feeds loaded on GitHub.

The public RSS feed was fetched after deployment: HTTP 200, 168 episodes, 168 unique GUIDs, 168 unique audio URLs, all dates within the configured November window, correct Atom self URL, and 274,681 bytes. Podcast-app playback and the first scheduled run remain unverified.

Workflow: https://github.com/epodcaster/NaPodPoMo-mega-feed-prototype/actions/runs/42775680500

The original website and existing NaPodPoMo MEGA Feed remain unchanged.

## Substack digest trial

Input: https://feed.informer.com/digests/3IWM108UBD/feeder.rss

The digest fetched successfully, is 126,093 bytes, and contains 50 RSS items. 29 items fit November 2026 and all have audio enclosures and source attribution. Two exact repeated audio URLs within The Lessons Learned Series are duplicate listings under changed titles. They are collapsed, retaining the latest dated metadata.

| Show | November input listings | Unique audio episodes |
| --- | ---: | ---: |
| Revivassance Podcast | 6 | 6 |
| Outrage Science Bites | 9 | 9 |
| The Lessons Learned Series | 9 | 7 |
| A3Day Expanded Podcast | 5 | 5 |
| Total | 29 | 27 |

The local merged feed contains 195 episodes, 195 unique GUIDs, 195 unique enclosure URLs, and 330,920 bytes. Fourteen automated tests pass. New tests cover mapped source identity, missing/unrecognized bridge sources, duplicate audio and cached GUID retention, and preserving separate shows sharing an audio URL.

The bridge preserves titles, descriptions, dates, links, source names, GUIDs, and enclosure URL/type/length. It does not provide artwork, duration, or explicit flags. No private subscription URLs are used. Output includes canonical source feed attribution rather than labeling all four shows as the digest.

The observed input window is 50 entries. Raising the digest's output item limit to at least 200 would give more room for November episodes if available. The prototype cache preserves already discovered episodes.

GitHub-hosted bridge retrieval and deployment are pending the following configuration commit. Podcast-app playback remains an acceptance check; successful RSS retrieval does not resolve the original audio server content-type issue reported by the validator.
