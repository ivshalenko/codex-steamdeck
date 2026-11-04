# rc.18: Gaming Mode and Steam library artwork

The default Ocean palette now matches the approved cover. The plugin heading, empty chat, controls and completion/update notifications use the shared identity. A Steam library card adds or refreshes only the managed Deck AI shortcut, with a verified set of capsule/header/hero/logo images and a separate shortcut icon. Existing art and logo placement can be restored; newer independent edits are protected.

The vertical cover has one title and a CHAT / FIX / CONTROL footer. The hero is composed for the crop observed in Steam's actual details page. This is a non-Steam shortcut, not a Steam store listing.

Validation: 259 Python tests and 44 frontend tests, TypeScript/shell/package checks, and Gaming Mode navigation/layout checks in English and Russian. New tests cover namesake shortcuts, duplicate prevention, artwork integrity, backup/restore, newer edits, linked folders, concurrent operations and requested-tab delivery across mounted views/module reloads.

On one developer Steam Deck, actual native buttons applied, restored and reapplied the library images. The empty chat, compact view, settings card, Steam details page and branded completion toast were captured. A real no-tools Codex reply produced the toast; clicking it returned to the correct chat. The existing-shortcut path was exercised on hardware; fresh-shortcut creation was covered by the native-target simulation and still needs a separate clean-device check.

The seven-day update interval is retained. Public package delivery is checked during publication. Independent hardware, optional providers and the earlier documented manual-check limits remain outstanding. See [the artwork guide](GAMING-ART.md) and earlier [rc.16 update checks](RELEASE-rc.16.md).
