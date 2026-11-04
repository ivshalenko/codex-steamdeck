# rc.16: weekly checks and one-click updates

Version: **1.0.0-rc.16**. Device work: **4 November 2026**, one developer Steam Deck running SteamOS.

- 253 Python tests and 42 frontend logic tests passed, together with TypeScript, shell syntax and packaging checks.
- Regression coverage includes persisted seven-day scheduling, manual checks with automation off, preview/stable channels, ignored incomplete/draft releases, asset integrity, unsafe archives, active-work guards, packaged plugin runtime discovery, both-component rollback, process interruption, startup failures, concurrent file edits, bytecode invalidation and the shared graphical-installer lock.
- A controlled local development baseline reported rc.15 while containing the new updater. A real Steam toast opened the update card; one native pointer activation installed the rc.16 candidate into both components. The detached worker survived plugin unload. Installed files matched the candidate manifest, and the checked personal-state hashes were unchanged.
- With a real desktop window open, the worker entered its quiescing phase, the app saved an isolated English test draft and shut down before replacement. The draft marker survived.
- Gaming Mode regression checks passed in both English and Russian (14 checks per language), including layout, settings reachability and drafts across compact/fullscreen views. The device was returned to English.
- The loader's completed modal was closed through its own native callback, matched by project name, target version and package hash. Unrelated prompts are outside this path.

The local delivery trial used candidate files cached with their expected digests; it did not pretend that stock rc.15 already included an updater or that the candidate had been published at that time. Public release downloads and the device path are verified separately during publication.

Automatic checks run weekly, not hourly. Package installation requires the user's Update action. Steam/Decky must remain available during plugin installation. The updater preserves the selected language and shared state; raw conversation, file and command content is unchanged.

This remains a prerelease checked on one developer device. Independent clean hardware, a Stable/Beta matrix, suspend during an active task, Windows hardware and optional provider accounts retain their prior manual-check limits. Existing rc.14 conversation and rc.15 installer screenshots retain their recorded version labels.
