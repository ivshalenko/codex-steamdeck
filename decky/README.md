# Decky Quick Access plugin

This folder contains the Deck AI panel for Steam's Gaming Mode Quick Access menu. Install the desktop companion first so the local bridge and Codex CLI are available; then copy this folder's contents to `~/homebrew/plugins/Codex` and restart Decky Loader.

See the repository [README](../README.md) for setup, supported languages, remote SSH connections, and privacy notes.

To build the frontend, use Node.js 24 or newer:

```bash
npm ci
npm run build
```

Frontend logic tests (game-name checkbox and dictation draft handling):

```bash
node --test tests/*.test.mjs
```

Gaming Mode UI checks, with Steam running and its local debugging endpoint enabled:

```bash
~/.local/share/deck-voice/venv/bin/python ../scripts/check-decky-ui.py
```

This checks compact/full-screen geometry, navigation, drafts and attachments without sending prompts or changing model preferences.
