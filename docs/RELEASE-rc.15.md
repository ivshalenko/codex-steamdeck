# rc.15: illustrated installer and language defaults

Version: **1.0.0-rc.15**. Device work: **4 November 2026**, one Steam Deck running SteamOS.

## Automated checks

228 Python regression tests, 38 frontend logic tests, TypeScript, shell syntax and package checks passed. Installer regressions cover automatic/custom selection, skipped components, language persistence in canonical and legacy state locations, preserved drafts/credentials/preferences, failed administrator receipts, missing Loader/terminal, failed Codex discovery, unchanged duplicate plugin folders, tampered upstream installer downloads and the repository launcher's exact release content.

A fresh Decky view defaults to English and honors an explicit Russian selection. Background notification polling also reads the shared language, so installer language selection applies before opening a panel. Generated empty-chat names use the preference; existing user names and conversation text remain unchanged.

## Real native checks on Steam Deck

- A real installation in a separate temporary HOME created the app environment and installed the checksum-pinned official Codex. The user's application and account state were outside this profile.
- The installer defaulted to English even with a Russian system locale. Switching its language preserved manual component choices.
- The first desktop launch used English, including generated empty-chat labels. Reinstalling/updating that profile with Russian selected produced a Russian first launch.
- Automatic, custom, live installation progress, completion and first launch were captured from actual GTK windows. The [installer gallery](INSTALLER.md) identifies the test scope.
- All 14 automated Gaming Mode UI checks passed in English and again in Russian on the updated plugin.

The fresh-profile installation selected desktop + Codex. It did **not** replace the user's system Decky Loader or enable SSH. The missing-Loader installer is fetched from an explicit upstream commit and checksum-checked before sudo; the upstream script downloads its stable Loader. Administrative steps use a visible terminal and must produce a successful completion receipt. These paths have regression tests, but a full privileged automatic installation on a second clean physical Deck remains outstanding.

SteamOS executable trust, an administrator password and AI-account sign-in cannot be silently granted by this installer. No password or account token is collected by the wizard. Physical controller checks, suspend during an active task, Windows client hardware and optional provider accounts retain the limitations documented in previous release reports.

The [22 English rc.14 conversation captures](MEDIA.en.md) and original Russian video archive retain their original version labels and files.
