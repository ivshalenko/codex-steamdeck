# Deck AI for Decky Loader

This directory contains the Gaming Mode Quick Access plugin. Install Deck AI for Desktop Mode first; the plugin bridge uses the desktop app's private Python environment and installed provider modules. Codex CLI must also be installed and signed in on the Steam Deck.

## Install on Steam Deck

1. Install and start Decky Loader.
2. Install the desktop companion from the repository root with `./install.sh` and sign in to Codex there if you plan to use Codex.
3. Copy this complete `decky/` directory to `~/homebrew/plugins/Codex/`. Keep the destination folder name `Codex`; the displayed name is read from `plugin.json` and is **Deck AI**.
4. Keep `dist/` intact. It contains `index.js` and the bundled local image under `dist/assets/`; the image's generated filename may change when the source artwork changes.
5. Restart Decky Loader, then open Steam's Quick Access menu and select **Deck AI**.

The application logo is `decky/deck-ai.png`. The frontend build copies it to `dist/assets/` and rewrites the bundle to load that local plugin asset. No separate image download is required. The image URL under `publish.image` in `plugin.json` is for a public plugin listing only; a private GitHub repository cannot serve that URL to a public store.

## Build and check the plugin

For frontend development, use Node.js 24 or newer:

```bash
npm ci
npm test
```

`npm test` checks TypeScript and generates the distributable files in `dist/`. A normal install of the checked-in plugin does not require Node.js. The bridge imports `providers.py` and related files from the desktop installation; do not copy API keys, Codex state, local screenshots, or chat data into this directory.

See the root [README](../README.md) for desktop installation, provider setup, speech-model downloads, supported languages, and troubleshooting. The desktop companion also offers an optional embedded browser panel when WebKitGTK is available on the system; this is separate from the Decky plugin.
