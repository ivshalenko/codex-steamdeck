# Deck AI for Steam Deck

AI chat in Steam Deck's Quick Access menu, with an optional desktop app, local dictation and remote control over SSH. **Community project, release candidate 1.0.0-rc.7.** Not affiliated with Valve or OpenAI.

**[Download / Скачать](https://github.com/ivshalenko/codex-steamdeck/releases/tag/v1.0.0-rc.7)** · **[Установка по шагам / Quick start](docs/QUICKSTART.md)** · **[Steam Deck ↔ Mac / PC](docs/REMOTE-CONTROL.md)** · **[Report an issue](https://github.com/ivshalenko/codex-steamdeck/issues)**

## Quick start

On Steam Deck, switch to **Desktop Mode**, download **Install-Deck-AI.desktop** from Releases, and open it. In Dolphin, allow execution/trust if prompted. The wizard installs the app, offers the official Codex CLI if missing, and optionally adds the plugin to an existing Decky Loader installation. Open Deck AI, sign into your own ChatGPT account, then return to Gaming Mode: **(…) → Decky → Deck AI → New chat**.

На Steam Deck перейдите в **Desktop Mode**, скачайте **Install-Deck-AI.desktop** и запустите его. При необходимости разрешите выполнение файла в Dolphin. Мастер покажет ход установки; пароль sudo вводится в отдельном терминале SteamOS. Затем откройте Deck AI и войдите в свой ChatGPT. В Gaming Mode: **(…) → Decky → Deck AI → Новый чат**.

Users do **not** need Node.js, npm or a source build. The **decky.zip** asset includes the plugin's core Python runtime and a pinned WebSocket library. Codex CLI and sign-in are still required. The desktop companion and speech models are optional for text chat. See the [full guide](docs/QUICKSTART.md) for manual ZIP installation, voice setup, updates and troubleshooting.

For an unpacked desktop release, the terminal alternative is `python3 scripts/setup.py`. Advanced unattended app/plugin installation: `./install.sh --decky` (install/sign into Codex separately first).

## What you can do

- Continue local Codex chats and choose a model, reasoning effort and service tier available to your account.
- Send tasks, inspect requested confirmations, view the queue, and receive a notification when a task completes while the panel is closed.
- Attach Steam screenshots or up to four frames extracted from a recording. Video attachments are sampled frames, not full video analysis.
- Use full-screen chat, history, themes, local dictation, an on-screen keyboard and language settings in the desktop companion.
- Control Codex **on Deck from Mac/Windows/Linux**, or control a **Mac/Linux/WSL host from Deck** over SSH. [The guide separates both directions.](docs/REMOTE-CONTROL.md)
- Optional providers: Claude Code (requires its own installation and sign-in), DeepSeek/OpenRouter and custom compatible API endpoints (require their own credentials). Provider availability, limits and charges depend on those services. Only Codex's agent interface executes commands in this project; API chat providers produce chat replies.

## Notifications, remote tasks and files

Enable notifications in Settings. Keep Steam and Decky running. A completion toast opens the corresponding conversation/device. Use the Files view to inspect files on the selected device. Review changes before allowing an agent action. Start with automatic approval **off**. Device selection determines where commands and file actions execute.

For remote control, both devices must stay awake and be on the same reachable network. The pairing wizard creates a dedicated public/private key pair, keeps the private key on your computer and asks you to verify Deck's SSH host fingerprint. Internet access requires your own VPN; Deck AI does not configure one. Native Windows **clients** are supported by the helper but need testing on a real Windows machine; Windows **hosts** require WSL and are not claimed as native-host support.

## Privacy and requirements

SteamOS x86-64, Python 3.9+, and Codex CLI signed into your own account are required. GTK 3/PyGObject is needed for the desktop app and graphical installer. Decky Loader is needed for the Quick Access plugin. FFmpeg and a working microphone are needed only for relevant media/voice features. No SteamOS root filesystem unlock is required.

Dictation is local; prompts and attached content are sent to the selected cloud provider. The app stores local history/settings; Codex manages its own credentials. Optional API keys use Secret Service/KWallet. A locked wallet can prevent optional API providers from working. Never include tokens, private keys or account files in bug reports. See [SECURITY.md](SECURITY.md).

## Release status and Decky store

This release is distributed from GitHub. **Deck AI is not listed in the official Decky store.** Its current [submission template](https://github.com/SteamDeckHomebrew/decky-plugin-database/blob/main/.github/PULL_REQUEST_TEMPLATE/plugin_addition.md) requires confirming that a majority of submitted code was not written by generative AI. This project used substantial AI assistance; that confirmation cannot honestly be made. Store eligibility and any exception require an explicit maintainer decision. [Submission status](docs/DECKY-SUBMISSION.md).

Automated tests and checks on the developer's Deck do not replace an independent clean-device test. Physical controller behavior, SteamOS Stable/Beta coverage, suspend/resume during a running task and all optional providers still need the checks listed in the [release report](docs/RELEASE-CHECKLIST.md). Game installation or performance is not guaranteed; users must supply their own legally obtained games and files.

## Development

```sh
python3 -m venv --system-site-packages venv
venv/bin/python -m pip install -r requirements.txt
npm --prefix decky ci --ignore-scripts
venv/bin/python scripts/build-release.py
```

The build runs Python regression tests, TypeScript/Rollup, frontend logic checks, shell syntax and an explicit package allowlist. Release assets include desktop/source TAR, standalone Decky ZIP, remote-control ZIP, the desktop installer and SHA-256 checksums. Personal chats, keys, models, local state and development environments are excluded. `scripts/install-decky.sh` stages a complete installation and retains the prior plugin for rollback; it does not delete user data. `~/.local/bin/deck-ai-uninstall` removes managed app files and retains user data.

GitHub Pages is optional: the workflow runs only when repository variable `ENABLE_GITHUB_PAGES=true` is configured and Pages is enabled. It is not required for installation.

## License and attribution

Apache-2.0. Preserve [LICENSE](LICENSE), [NOTICE](NOTICE), author credit to **ivshalenko**, and third-party notices when redistributing. The plugin bundles Decky API components and a pure-Python websockets 15.0.1 wheel; their licenses are included. Codex, Decky Loader and optional voice models have their own upstream licenses and are downloaded separately where needed.
