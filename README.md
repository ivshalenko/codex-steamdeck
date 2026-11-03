# Deck AI — standalone Decky source candidate

This branch places plugin.json, main.py, src/, runtime/ and vendor/ at the plugin root for review by Decky maintainers. Source release: 1.0.0-rc.9. Codex CLI 0.166.0 and your own ChatGPT sign-in are required. Desktop companion and voice are optional for text chat.

Build: `npm ci --ignore-scripts && npm test`; frontend tests: `node --test tests/*.test.mjs`. The bundled pure-Python WebSocket wheel is pinned and its BSD license is in vendor/. Main project and complete regression tests: https://github.com/ivshalenko/codex-steamdeck/tree/main. Installation: https://github.com/ivshalenko/codex-steamdeck/blob/main/docs/QUICKSTART.md.

This is standalone source for reference, **not an approved or pending store entry**. On 3 November 2026 a Decky maintainer [declined the submission](https://github.com/SteamDeckHomebrew/decky-plugin-database/issues/1178#issuecomment-6607400046), citing both the restriction on LLM-access shell plugins and the restriction on predominantly LLM-developed plugins. The project used substantial Claude/Codex assistance. Distribution is independent through GitHub; no store approval is claimed. Independent device and physical-control testing remain separate technical release checks.

Apache-2.0; retain LICENSE, NOTICE and THIRD_PARTY_NOTICES.txt.

Claude setup uses the unmodified official CLI and user-owned account/API/cloud access: [instructions](https://github.com/ivshalenko/codex-steamdeck/blob/main/docs/CLAUDE-AUTH.md). Complete LGPL library/application sources and rebuild instructions: [rc.9 source bundle](https://github.com/ivshalenko/codex-steamdeck/releases/download/v1.0.0-rc.9/deck-ai-1.0.0-rc.9-lgpl-sources.zip).
