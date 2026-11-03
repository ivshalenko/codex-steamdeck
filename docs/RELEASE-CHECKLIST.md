# Release candidate verification

## Automated

- Python regression tests: backend transport, reconnects, queue recovery, media, installation and rollback, standalone plugin without companion/site-packages.
- TypeScript, production Rollup build, frontend logic tests.
- Shell syntax, package allowlist and credential-pattern checks.
- Deterministic archive metadata and SHA-256 manifest.

The exact counts and device results are recorded in the GitHub release and release-kit report. Passing code tests does not prove physical-button or microphone quality.

## Before calling this stable

- Independent fresh Steam Deck installation using the public desktop installer and ZIP path.
- SteamOS Stable and Beta; compatible Decky Stable and prerelease if required by its submission policy.
- Physical controls, QAM over a running game, touch keyboard, real microphone in a game.
- Suspend/resume during a running task; safe recovery after network loss.
- Optional providers with valid accounts and an unlocked system wallet.
- Real Windows client pairing; Mac/Linux host pairing on another machine.
- Keep the official-store status accurate: the request was declined; do not advertise a pending or approved listing.

Do not mark these boxes complete merely because unit tests or Steam Desktop Big Picture passed.
