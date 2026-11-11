# NaPodPoMo RSS Aggregator Prototype v0.4

A separate expanded-source experiment. **Do not change napodpomo.org, its DNS, or the existing NaPodPoMo MEGA Feed.** Deploy only to a new repository named `napodpomo-mega-feed-prototype` (or another unused prototype name), using its default GitHub Pages URL. Do not add a custom domain.

## Expanded source trial

The configuration represents all 30 supplied shows through 26 direct feeds plus one separate Feed Informer digest for the four Substack shows. Kim Newlove uses the verified Libsyn feed; Modulations uses its public 3Speak alternative. The Substack digest contributes 27 unique November audio episodes after suppressing two duplicate audio listings, for a local total of 195. Fourteen automated tests pass. See `SOURCE_TEST_REPORT.md` for the trial history and current deployment status.

Source/code changes on main now start a build automatically; cache and documentation commits do not. Scheduled updates remain every three hours during November 2026.

## Initial three-source verification

On November 10, 2026: all five original tests passed; the expanded suite passes all eight. All three real sources loaded. The 2026 build selected 19 episodes; the separate 2023 build selected 25. One audio sample per podcast returned HTTP 206 and `audio/mpeg`. See `TEST_REPORT.md` and `test-results/` for evidence. GitHub-hosted execution and the first Pages deployment also succeeded. The live feed returns HTTP 200 with valid XML, 19 unique episode GUIDs, the correct Atom self URL, and dates inside the configured month. Podcast-app playback and a subsequent scheduled update remain unverified.

Live prototype: https://epodcaster.github.io/NaPodPoMo-mega-feed-prototype/mega-feed.xml

First successful workflow: https://github.com/epodcaster/NaPodPoMo-mega-feed-prototype/actions/runs/42773532032

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python build.py --config config-prototype.json --output site/mega-feed.xml --cache data/episodes-prototype-2026.json
```

`config-prototype.json` uses the expanded source list and the original November window, with a distinct prototype title and description. The workflow supplies the real Pages URLs at build time. Local output uses a placeholder website URL until deployment. The original configurations remain available for comparison.

Historical test (keep separate; it is not published by the workflow):

```bash
python build.py --config config-2023-test.json --output test-results/2023-test.xml --cache test-results/episodes-2023.json
```

## Publish the prototype

1. Connect GitHub to this ChatGPT session when offered. Use your intended GitHub account. Never paste passwords or access tokens into chat. A ChatGPT connection and the workflow's built-in GitHub token are separate authorizations.
2. Create a **new public repository** named `napodpomo-mega-feed-prototype`. Public repositories support Pages on GitHub Free. Confirm that this is a new repository, not the repository behind an existing site. If the GitHub connection offers repository selection, grant access only to the prototype where possible. Repository creation may need to be done in GitHub first.
3. Upload the contents of this project to its default branch, including `.github/workflows/build-feed.yml`, `tests/`, and `data/episodes-prototype-2026.json`. Upload extracted files, not this ZIP. The saved cache preserves episodes already discovered.
4. In repository **Settings > Pages**, select **GitHub Actions** under Build and deployment > Source. Leave Custom domain empty.
5. Ensure GitHub Actions is enabled and these official actions are allowed by repository/organization policy: checkout, setup-python, configure-pages, upload-pages-artifact, and deploy-pages. The workflow requests `contents: write` to save episode metadata; its deploy job requests `pages: write` and `id-token: write` to publish Pages. No personal access token or manually created repository secret is required. Existing organization policy or protected branches may prevent the cache commit; adjust only this new repository's settings if needed.
6. In **Actions**, select **Build and publish RSS prototype > Run workflow**, on the default branch. Review both build and deploy jobs. Approve the `github-pages` environment if GitHub explicitly requires it.
7. Visit the deployment URL, then its `mega-feed.xml` link. For a normal project repository, the feed URL is `https://OWNER.github.io/napodpomo-mega-feed-prototype/mega-feed.xml`. Use the URL actually returned by deployment.
8. Check the live feed returns XML over HTTPS, is titled as a prototype, contains unique GUIDs and original audio enclosures, and has its own URL in the Atom self link. Subscribe by direct RSS in a podcast app, play episodes from both 2026 sources, inspect artwork, and check that a second run preserves existing episodes without duplicates.

The workflow runs at 00:17, 03:17, 06:17, 09:17, 12:17, 15:17, 18:17, and 21:17 UTC during November 2026. Scheduled runs after 2026 skip build/deployment. Manual runs remain possible. GitHub scheduling is best effort, not exact. Scheduled workflows run from the default branch and may be disabled after 60 days of inactivity in a public repository. Disable this workflow in Actions to pause the prototype; this leaves the last published feed available.

## What changed in v0.2

- Added a distinct prototype configuration, landing page, and cache; no change to aggregation logic in `build.py`.
- Split build and deploy jobs, limiting Pages publication permissions to deployment.
- Resolve the feed's URLs from GitHub Pages metadata instead of guessing from repository names.
- Use the current documented `upload-pages-artifact@v4` action and explicit Bash failure handling.
- Keep scheduled processing within the 2026 experiment and add job timeouts.
- Added three regression tests: exact month boundaries, missing dates/audio, and total-source-failure output preservation.
- Included test results and the initially discovered episode cache.

## Behavior and remaining limits

- RSS 2.0 audio feeds only; YouTube Atom is not supported.
- Each source is limited to 40 MB. No audio files are downloaded or rehosted during aggregation.
- Date filtering is start-inclusive/end-exclusive and follows the offsets configured in the JSON. The November window uses US Eastern offsets, matching the original prototype.
- Metadata is cached to retain episodes removed by rolling source feeds. Episodes missing from a source before the first collection cannot be recovered automatically. The 1,500-item output cap also drops older cache entries beyond the cap.
- GUIDs use the canonical source feed URL plus the original GUID. Bridge source mappings keep the original podcast identity. Within a show, repeated exact audio URLs are collapsed and cached aggregate GUIDs are retained when upstream GUIDs change. Distinct shows are kept separate. The most recently dated duplicate entry supplies metadata.
- Descriptions become plain text truncated to 1,400 characters. Chapters, transcripts, and advanced Podcasting 2.0 metadata are not copied.
- A partial source failure uses cached metadata and still allows publication. If every source fails with no cache, the build fails and leaves local output untouched. With a cache, all-source failure can publish cached episodes; inspect Actions logs for source errors.
- Channel-level artwork uses the supplied NaPodPoMo 2026 MEGA Feed cover, served from this prototype's Pages assets. The replacement cover is a verified 2048 × 2048 RGB JPEG (325,625 bytes), within Apple's 1400–3000 pixel RSS cover range. It is served under the new mega-feed-cover-2026-v2.jpg filename; the original file is retained for older cached references. The RSS includes both itunes:image and the standard RSS image element. Episode artwork is copied with a show-art fallback. The combined channel declares explicit=true when any included episode is marked explicit; episode flags inherit their source channel flag when absent.
- Some source audio URLs use HTTP. The aggregator preserves them exactly. App compatibility still needs testing.
- Public prototype publishing is separate from participant onboarding or any launch of a replacement feed. Do not submit this prototype to podcast directories.

## Substack digest input

The separate input is https://feed.informer.com/digests/3IWM108UBD/feeder.rss. It replaces the four failing direct Substack requests in this prototype; the existing official MEGA Feed is not an input and remains unchanged. `source_map` maps each digest item's source page to the canonical public podcast feed and show name. Unknown or missing source attribution rejects the bridge input rather than silently mislabeling episodes; cached entries remain available. Output items include RSS source attribution and retain original media URLs.

The observed digest has 50 entries. A rolling window is safe only if collection runs before entries disappear. Set its output item limit to at least 200 if available for greater November headroom; the prototype retains discovered entries in its cache. The digest omits episode artwork, duration, and explicit flags. Those fields cannot be recovered from this input. Source media hosting and content-type issues remain separate from successful RSS collection.

## Public cover fallbacks for bridged shows

A mapped show can specify artwork_url in its source_map entry. This is applied when writing the feed, so cached episodes also receive the cover without changing their GUIDs or media URLs. Any existing episode artwork takes priority. Revivassance uses the supplied public 1400 × 1400 RGB PNG from Substack’s S3 image storage. The other three bridged shows still need confirmed cover-image URLs. Fifteen regression tests pass.
