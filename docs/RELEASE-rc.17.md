# rc.17: one consistent visual identity

The approved Steam Deck illustration is the shared source for the English/Russian covers, installer banner, remote-control diagrams and social cover. Application and plugin icons use the same midnight-blue, ice-blue and silver palette. The installer colors and generated project page follow it too.

Validation: 253 Python tests, 42 frontend logic tests, TypeScript, shell and package checks. All generated page images load locally; desktop and 390 px mobile previews have no horizontal page overflow. The native installer was opened on the developer Steam Deck in a temporary profile: automatic/custom choices and English/Russian switching were checked and captured, without starting installation or changing real user preferences.

The complete installer and update-engine checks from [rc.15](RELEASE-rc.15.md) and [rc.16](RELEASE-rc.16.md) remain separate evidence. Historical screenshots keep their original pixels and recorded versions. The [brand guide](BRAND.md) links the new assets and native captures.

This release retains the seven-day update interval. The published packages and actual rc.16 → rc.17 device update are verified during publication. It remains a prerelease tested on one developer Steam Deck; the previously documented independent-hardware and optional-provider limits still apply.
