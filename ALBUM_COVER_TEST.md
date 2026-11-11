# Per-podcast album cover trial, November 11, 2026

Goal: the MEGA Feed has its own cover; each podcast uses its main cover consistently on all its episodes. Unique episode images are not the target of this trial.

The beta main feed keeps its existing artwork selection (episode art, then podcast cover, then mapped fallback). A separate six-item feed uses podcast covers only. Sources are Podcast Hot Take, Computer Freedom, and Revivassance, with two recent episodes from each. The three supplied main covers were fetched and decoded as 1400 × 1400 RGB JPG/PNG. Podcast Hot Take's equivalent HTTPS image URL was also verified.

`extract_rss` now stores a separate podcast_artwork field from each original channel. `make_rss` defaults to its previous episode-image behavior, and an explicit artwork_preference=podcast opts into main-cover selection. A cover found on a current episode also applies to older cached episodes from the same source. Mapped bridge covers take precedence as explicit source configuration. A missing main cover does not substitute an unrelated episode image in podcast mode.

The test uses separate diagnostic GUIDs and a separate URL. Original audio URLs remain unchanged. Main beta GUIDs and title remain unchanged, and no website or original official feed is modified.

Trial RSS: https://epodcaster.github.io/NaPodPoMo-mega-feed-prototype/album-cover-test.xml

Application caveat: even though these are each podcast's album covers, the aggregate attaches them to individual RSS items. Apps call that episode artwork. Changing which image is selected does not guarantee Apple Podcasts will start displaying item images. Earlier tests with direct URL following in Apple Podcasts showed the feed-level cover even with correctly formed item image tags; the cause remains unconfirmed.

Pocket Casts explicitly documents support for RSS item artwork on iOS and Android with Profile → Settings → Appearance → Use episode artwork enabled, and automatic display in its web/desktop apps. This provides a different app test instead of repeating only the prior Apple test.

Reference: https://support.pocketcasts.com/knowledge-base/episode-artwork/

Local automated tests: 17 passed. GitHub build and live feed validation pending deployment. Actual app display requires a user test and must not be described as confirmed until observed.
