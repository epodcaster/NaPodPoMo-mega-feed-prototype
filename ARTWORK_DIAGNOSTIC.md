# Temporary artwork diagnostic

RSS: https://epodcaster.github.io/NaPodPoMo-mega-feed-prototype/assets/artwork-diagnostic.xml

This separate two-episode feed uses fresh diagnostic GUIDs to test a fresh RSS import in Apple Podcasts. Main prototype episode GUIDs are unchanged. No original audio files are modified.

The diagnostic show cover uses The Pharmacist’s Voice latest pronunciation-episode image as a visual control, not as the branding of a new public show. Episode 1 uses Revivassance’s 1400 × 1400 RGB PNG; episode 2 uses a different pronunciation-episode image. Both episode images differ from the diagnostic show cover. All three image files were decoded and verified to be square, RGB, PNG/JPEG, within 1400–3000 pixels, and HTTP HEAD 200.

Follow this diagnostic RSS URL in Apple Podcasts and play Artwork test 1. If Revivassance artwork appears, a fresh feed import changes the result, supporting an existing-library metadata/cache explanation. If the control show cover persists, this still does not prove a general Apple limitation; compare the same diagnostic feed in another app with RSS episode-art support, or escalate a reproducible case to Apple.

Documentation is not conclusive about this exact unlisted direct-RSS case. Do not claim the cause is proven. App playback/display remains unverified until the user tests. The diagnostic is not submitted to a podcast directory.

## User-observed result, November 10, 2026

The user followed the separate diagnostic feed in Apple Podcasts and reported that The Pharmacist’s Voice control image appeared both as the diagnostic show cover and while the Revivassance episode played. This fresh-import test did not show the Revivassance episode-level image. The original prototype likewise displayed its MEGA Feed channel cover in Now Playing on iPhone, and episode images were not observed on Mac.

The original-subscription-only cache explanation is therefore less likely. This observation does not prove that every Apple Podcasts client or every direct RSS feed behaves identically. Episode artwork is present and image delivery was validated, but per-episode display in this direct-RSS Apple Podcasts setup remains unsupported by our observed results. Playback of the test episode was possible. Do not describe adding RSS image tags as confirmed end-to-end artwork display in Apple Podcasts.

No feed or audio changes were made in response to this observation. Keep the episode image metadata for apps that use it. Additional app tests or a reproducible support report would be needed to establish the exact cause.
