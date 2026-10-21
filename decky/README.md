# Decky Quick Access plugin

This folder contains the Codex panel for Steam's Gaming Mode Quick Access menu. Install the desktop companion first so the local bridge and Codex CLI are available; then copy this folder's contents to `~/homebrew/plugins/Codex` and restart Decky Loader.

See the repository [README](../README.md) for setup, supported languages, remote SSH connections, and privacy notes.

To build the frontend, use Node.js 20 or newer:

```bash
npm ci
npm run build
```
