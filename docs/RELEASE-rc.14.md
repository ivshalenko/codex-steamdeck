# rc.14: English interface and media checks

Version: **1.0.0-rc.14**. Device checks and captures: **4 November 2026**, one developer Steam Deck running SteamOS.

- 210 Python regression tests and 37 frontend logic tests passed; TypeScript and release-package checks passed.
- All 14 automated Gaming Mode UI checks passed with English selected, then all 14 passed with Russian selected. The preference was returned to English.
- A fresh English Codex conversation repaired an isolated `free_space` demonstration project. The original unit test failed with `1250 != 750`, remained unchanged, and passed after the addition became subtraction.
- The native proposed patch was reviewed before approval. The first approval activation left the file unchanged and requested a second activation; the second allowed the reviewed change.
- A real `deck-remote new ... --wait` request from Mac received an English answer from Codex on Deck.
- A real Steam completion toast appeared with the plugin panel closed. Activating it opened the correct English conversation.
- English Steam menus, Decky controls, GTK history and the installer were captured directly. The [22-image gallery](MEDIA.en.md) uses new English conversation content. Capture checks rejected visible Cyrillic and blank frames.
- The original 24 Russian PNG assets (21 gallery images plus three guide copies) were checked against their original SHA-256 values and preserved byte for byte. Russian videos remain in their existing release archive.

The English game-setup and keyboard conversations are demonstration requests with real replies. The reported emulator and keyboard errors are simulated. They do not claim successful game installation or emulation. The code-fix example actually changed and tested only its separate demonstration project.

Automated pointer input and application handlers were used. Physical controller/trackpad testing, a second clean Steam Deck installation, a Stable/Beta matrix, suspend during a running task, a real Windows client, and all optional provider accounts remain separate manual checks. Earlier rc.13 timed runs are historical evidence and are not presented as new rc.14 soak tests.
