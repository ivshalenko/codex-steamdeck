# Deck AI — standalone Decky source candidate

This branch places plugin.json, main.py, src/, runtime/ and vendor/ at the plugin root for review by Decky maintainers. Source release: 1.0.0-rc.8. Codex CLI 0.166.0 and your own ChatGPT sign-in are required. Desktop companion and voice are optional for text chat.

Build: `npm ci --ignore-scripts && npm test`; frontend tests: `node --test tests/*.test.mjs`. The bundled pure-Python WebSocket wheel is pinned and its BSD license is in vendor/. Main project and complete regression tests: https://github.com/ivshalenko/codex-steamdeck/tree/main. Installation: https://github.com/ivshalenko/codex-steamdeck/blob/main/docs/QUICKSTART.md.

This is a **review candidate**, not an approved store entry. Substantial code was developed with Claude/Codex assistance. The current store template's majority-non-AI confirmation cannot truthfully be checked. Stable/Beta, independent third-party and physical-control testing requirements remain open. Eligibility must be resolved with maintainers before a listing submission.

Apache-2.0; retain LICENSE, NOTICE and THIRD_PARTY_NOTICES.txt.
