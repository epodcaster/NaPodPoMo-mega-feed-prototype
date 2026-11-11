# NaPodPoMo 2026 MEGA Feed launch

Authorized November 11, 2026. Publish the full aggregate as the NaPodPoMo 2026 MEGA Feed with an OPML import URL, while keeping existing beta RSS subscriptions valid.

- Official title: NaPodPoMo 2026 MEGA Feed.
- Description: Follow the voices of National Podcast Post Month. The NaPodPoMo 2026 MEGA Feed brings together November episodes from participating podcasters. Discover new shows, support creators, and follow the challenge throughout the month.
- OPML imports one combined RSS subscription, not 30 separate shows.
- All November participants remain configured; late additions are supported through configuration updates and the Substack bridge mapping when needed.
- Per-podcast main covers are selected where available. Feed-level cover remains the verified 2048-square RGB JPEG.
- Three-hour November schedule includes December 1–2 final collection; manual runs remain available.
- Website and original Feed Informer MEGA Feed remain unchanged.

Published November 11, 2026 in commit aee63f4d8c0a09306055e45d7a8e230067a90069. GitHub Actions run 43059113153 completed successfully, including all 17 automated tests and the Pages deployment.

Post-deployment verification: all 219 baseline episode GUIDs remain present. Original audio hosts and file paths are unchanged; six Audioboom URLs refreshed their host-provided `modified` query value during collection. There are no duplicate enclosure URLs. The published feed has the official title and description, and 25 active source podcasts have a consistent main cover. Three Substack sources still lack a mapped main cover and use the MEGA Feed cover as the app fallback. The public one-subscription OPML, landing page, and channel cover were checked after deployment.

Late joiners: add their public RSS URL to the configured sources and run the workflow. For Substack, update the Feed Informer bridge and source mapping as documented in README.md. Existing listeners stay subscribed to the same aggregate URL. November episodes still available in a new source feed can be collected; episodes already removed from that source cannot be recovered automatically.

See README.md for source addition instructions and listener URLs.
