# Deck AI for Steam Deck

A community-built multi-provider AI desktop app and Decky Loader plugin for Steam Deck Desktop Mode and Gaming Mode.

The project is designed for Steam Deck. Choose between your signed-in Codex account, Claude Code with a Claude Pro/Max subscription, DeepSeek through OpenRouter, or DeepSeek V4.1 Flash through TokenHarbor. The desktop client provides a chat list, provider controls, dark and light themes, an integrated on-screen keyboard, and offline voice dictation. The Decky Loader plugin puts a compact multi-provider chat panel in Steam's Quick Access menu.

## Features

- Browse and continue local Codex chats; select models, reasoning effort, and speed.
- Switch between your signed-in Codex account, Claude Code using a Claude Pro/Max subscription, and DeepSeek models through OpenRouter.
- Browse the current DeepSeek catalog from OpenRouter. Model prices are shown where the catalog provides them; OpenRouter requests require your own API key and may incur charges.
- Use the fixed `deepseek-v4.1-flash:free` model through the OpenAI-compatible TokenHarbor endpoint (`https://tokenharbor.ai/v1`). The provider currently labels this model free; check TokenHarbor's terms and limits because provider availability and pricing can change.
- Connect **any other cloud AI** that has an OpenAI-compatible API (OpenAI, Gemini, Groq, Mistral, DeepSeek, xAI, OpenRouter, …): Decky Settings → «Свой облачный ИИ», or the **+** menu in the desktop app. Only https addresses of public cloud hosts are accepted (no local servers); the API key goes to the system secret store.
- Sign in, view the current account, or sign out through Codex.
- Open websites in an optional right-side browser panel with a persistent, app-local cookie profile.
- Use Russian or English for the interface. **English is the default on a fresh install.**
- Dictate offline with Russian/English live previews and an optional multilingual Whisper final pass (99 supported languages). Audio stays on the Deck.
- View image attachments directly in chat history; select a thumbnail to enlarge it. Sent images are kept in private app state, and unavailable files are labeled rather than silently hidden.
- Type with the integrated keyboard. It includes English, Russian, German, French, Spanish, Ukrainian, and Italian layouts.
- Switch between dark and light themes.
- Use the Decky Quick Access plugin for chats, model controls and dictation.
- Optionally connect to another computer running Codex over SSH. SSH access is configured on your own devices; this repository contains no connection keys or account data.

The interface is currently translated into English and Russian. Voice recognition supports English and Russian with the basic models, or 99 model-supported languages and automatic detection with the optional multilingual model. Keyboard layouts cover the seven languages listed above; other interface and speech languages are not included yet.

## License and attribution

Deck AI is licensed under the **Apache License 2.0** (see `LICENSE`). Anyone who copies, modifies or redistributes it must keep the copyright notice and the `NOTICE` file, which credit the author (ivshalenko), and must mark files they changed. A public release has not been published.

## Requirements

- Steam Deck with SteamOS and Desktop Mode.
- Codex CLI installed and signed in on the Deck (or on the selected SSH host). The official Codex CLI installation guide is at <https://developers.openai.com/codex/cli/>.
- Python 3, GTK 3 Python bindings, FFmpeg, PulseAudio-compatible microphone input, and a working audio input device.
- Optional: Decky Loader for the Gaming Mode Quick Access plugin. The plugin uses Decky API version 2 and the folder name `Codex` in the current manual install path.
- Optional: Claude Code installed and signed in with your Claude Pro/Max subscription to use Claude in the desktop companion. Sign in with `claude auth login`; do not use `--console` for a Pro/Max subscription.
- Optional: an OpenRouter API key to use DeepSeek. The desktop app stores it in the system Secret Service (KWallet/libsecret), not in the repository or Codex config.
- Optional: a TokenHarbor API key to use DeepSeek V4.1 Flash. It is stored in the system Secret Service (KWallet/libsecret), not in the repository. The API base is `https://tokenharbor.ai/v1`; the app calls its `/chat/completions` endpoint.
- Optional: WebKitGTK 4.1 or 4.0 with Python GObject bindings to enable the embedded browser panel. Without it, the app remains usable and explains that the browser component is missing. Browser cookies are stored locally under the app state directory and are not part of this repository.
- Internet access during setup to install Python packages and download speech models.

## Connect Codex on Steam Deck

In Desktop Mode, install Codex using the [official CLI guide](https://developers.openai.com/codex/cli/), then sign in:

```bash
codex --version
codex login --device-auth
codex login status
```

Open the displayed verification page on the Deck or another device and enter the code. If device authentication is disabled for your account, enable it in ChatGPT security settings or run `codex login` with a browser on the same machine. In Deck AI choose **Codex → Этот Steam Deck**. In the Decky panel, **Settings → Аккаунт ChatGPT → Войти в аккаунт** displays the verification URL and device code.

Deck AI connects to the local Codex control socket when available. It starts the shared daemon if supported and falls back to an owned stdio app-server for CLIs without daemon support. No public app-server listener is needed. A custom `CODEX_HOME` is respected.

## Install the desktop companion

Clone or download this repository, open a terminal in its directory, and run:

```bash
./install.sh --check
./install.sh
```

The launcher is `~/.local/bin/deck-ai`; `--version` prints the installed version and `--check` reports local dependencies without reading credentials. The `codex-steamdeck` launcher remains an alias for compatibility. Updates preserve the Python environment, downloaded models and chat/settings state. To uninstall managed app files while preserving data and models, run `~/.local/bin/deck-ai-uninstall`. The optional Python environment is retained so reinstalling can reuse it.

The installer creates an isolated Python environment, installs a new copy under `~/.local/share/deck-ai` (or updates an existing `deck-voice` / `codex-steamdeck` installation in place), and adds a **Deck AI** launcher to the application menu. It does not install provider CLIs, sign in to an account, or change existing credentials.

For offline voice dictation, download the English and Russian Vosk models:

```bash
./scripts/download-models.sh
```

The models are large downloads (about 150 MB together). Without them, chat and keyboard input still work; dictation will ask you to install the selected model.

For more accurate final text and multilingual dictation:

```bash
./scripts/download-models.sh --accurate-ru
```

The multilingual model also supports English. Choose a language or automatic detection in settings. Decky uses fast streaming recognition for Russian/English; the desktop app can also refine them. The final pass runs after recording stops and releases its model memory when finished.

## Project web page

The optional workflow builds a web page from this README, the changelog and the version (`.github/workflows/pages.yml`, `scripts/build-site.py`). To enable deployment, set Settings → Pages → Source to **GitHub Actions**, then set the repository Actions variable `ENABLE_GITHUB_PAGES=true`. Run the **Project web page** workflow or push to `main`. It is skipped until explicitly enabled. Build the page locally with `python3 scripts/build-site.py`.

## Notifications, remote tasks and files

- Steam toasts report finished, failed and approval-waiting tasks even with the panel closed. Under **Следить в фоне** you can watch several SSH machines at once.
- **История → Что произошло** lists recent events; **Задачи на всех устройствах** lists running chats of every device visited.
- Approval requests appear in the chat with **Разрешить / Отклонить**; allowing needs a second press. **Только чтение** disables all actions.
- **Файлы на устройстве** (История) opens text files from the home folder of the selected device for viewing and small edits.
- **Control the Deck from a Mac or PC.** On the Deck (Desktop Mode terminal) run `passwd`, then `sudo systemctl enable --now sshd` once. In Decky open Settings → «Доступ с другого компьютера», copy the shown `Host steamdeck` block into `~/.ssh/config` on the Mac, and paste the Mac's public key (`cat ~/.ssh/id_ed25519.pub`). For the Mac side there is a guided setup: `python3 scripts/deck-remote.py steamdeck setup DECK_ADDRESS` creates a key if needed, adds the `Host steamdeck` block to `~/.ssh/config` and prints the one command to run on the Deck. Then `python3 scripts/deck-remote.py steamdeck list` / `send THREAD "text" --wait` sends commands that appear in Deck AI. Use key login only and keep SSH reachable only on your home network or through Tailscale.
- **Appearance** (Decky Settings → «Оформление»): seven colour themes, message style (bubbles / lines / cards), density, and layout — tabs on top or at the bottom, or two columns (chat list + conversation) in full screen. The desktop app has the same colour themes in its menu.
- With a hardware keyboard, **Enter sends** the message (Shift+Enter inserts a new line in the desktop app). Dragging a finger over messages, history and settings scrolls them.
- X on the controller toggles dictation. Own words go in `vocabulary.txt` (project folder or `~/.config/deck-ai/`): one word per line, or `heard => written` to correct recognition.
- Faster final pass: `DECK_AI_WHISPER_SIZE=base ./scripts/download-models.sh --accurate-ru`.

## Gaming Mode controls

- Compact chat fills Decky's available height. Use **На весь экран** to expand it; settings open on a separate full-screen page.
- Adjust **Масштаб чата и кнопок** for smaller text and controls.
- The **Игра** checkbox adds only the running game's name. With it off, Deck AI sends your text without game metadata or instructions. Screenshots are attached only when selected.
- The recording button turns red. A separate line previews speech; **Стоп** moves recognized text into the draft. Russian/English use the streaming recognizer without a second pass in Decky. **Очистить** clears the unsent draft; chat history stays intact. Other languages need the multilingual model and may take several seconds after stopping.
- Select a message to reveal **Копировать**. When reading older messages, use **К последнему сообщению** to resume following the response.
- Queued messages and errors remain visible. A successful click shows **Запрос принят · в очереди**; queued requests wait for the current response to finish. **Очередь · посмотреть** shows saved requests, their status and originating chat; it separates waiting requests in the current chat from other chats. After a backend restart, in-flight sends are checked against server turn IDs; an ambiguous send requires checking the chat before retrying.

## Images, logos and app icons

The project artwork is included in this repository. `deck-ai.png` is the desktop icon and app logo; `scripts/manage-install.py` installs it into the user's hicolor icon directory. `icon.svg` is the editable vector artwork source. The Decky panel imports `decky/deck-ai.png`; the Rollup build copies it into `decky/dist/assets/` with a generated filename, and the bundle loads that local plugin asset at runtime. Keep the source PNG and generated `dist` asset together. After changing the artwork, rebuild the plugin with `npm ci && npm run build` from `decky/`; do not rename the generated asset by hand. The Decky `publish.image` URL in `decky/plugin.json` is only for a public plugin listing and needs a publicly accessible image URL if the plugin is submitted to a store. A private GitHub repository does not make that URL public. The legacy `decky/codex-official.png` is retained in the source tree; the current UI uses the Deck AI artwork.

The runtime copies of the logo are installed from the repository by `./install.sh`. No separate image download is required. Chat screenshots and user attachments are private runtime data under the app state directory and are deliberately not part of this repository.

## Install the Decky Loader plugin

**Quick way:** after `./install.sh`, run `./install.sh --decky` (or `scripts/install-decky.sh`). It copies the plugin to `~/homebrew/plugins/Codex`, asks for your password once because that folder belongs to root, and restarts Decky Loader. The manual steps below do the same thing by hand.

1. Install and start **Decky Loader** on the Steam Deck. Confirm it is running in Gaming Mode.
2. Install the desktop companion above first. The plugin bridge imports the desktop app's provider code from its installed Python environment; Codex itself must be installed and signed in on the Deck.
3. Copy the complete `decky/` directory from this repository to `~/homebrew/plugins/Codex/`, replacing the previous plugin directory when updating. Preserve the folder name `Codex`; Decky's displayed plugin name comes from `decky/plugin.json` and is **Deck AI**.
4. Ensure the copied directory contains `plugin.json`, `main.py`, `bridge.py`, `dist/index.js`, and `dist/assets/deck-ai-2f73c1d3.png`. The image filename is generated by the current build and can change if the source image changes; copy the whole `dist/` directory rather than selecting files manually.
5. Restart Decky Loader or reboot the Deck. Open Steam's Quick Access menu and choose **Deck AI**.

For a development build, install Node.js 24 or newer, then run `npm ci && npm test` in `decky/`. End users installing the checked-in build do not need Node.js. To create release archives, use `python3 scripts/build-release.py`; this writes a desktop/source archive and a self-contained Decky ZIP under `build/releases/`. It does not publish either archive or change GitHub access.

The plugin reconnects to Codex after Decky starts. It needs no separate OpenAI API key. To make it available through the Decky plugin store, a maintainer can submit this repository to the Decky plugin index after review.

## Optional: connect another computer

Install Codex CLI on the other computer and sign in there. Configure SSH on the Deck using your own SSH host alias and key. Before selecting that alias under **Устройство**, connect once from a Desktop Mode terminal to verify the host fingerprint and key login:

```bash
ssh YOUR_ALIAS true
ssh -o BatchMode=yes YOUR_ALIAS 'pwd'
```

Deck AI runs JSONL RPC through SSH. Current CLIs start the shared daemon and use a Python adapter to translate SSH JSONL into WebSocket messages on its Unix control socket. The adapter uses the installed companion Python environment, or system Python with `websockets`; installations without the required daemon or library use `app-server --listen stdio://`. Both desktop and Decky resume an existing thread before sending through the same RPC connection. A failed resume stays visible as an error instead of silently handing the message to another queue. For legacy CLIs, keep the client open while work is running; use `--wait` with `scripts/deck-remote.py`.

When launched by Decky Loader, the client removes inherited PyInstaller library paths from child-process environments. This prevents Decky libraries from breaking normal shell commands on SteamOS.

The SSH launcher also checks `~/.local/bin`, `~/.npm-global/bin`, Homebrew paths and the macOS Codex app binary when the SSH session has a minimal PATH. Remote account login uses a device code, so no browser callback needs to reach the other computer.

 Use a trusted private network or VPN such as Tailscale; do not expose the Codex app-server port directly to the public internet. Never upload private SSH keys, `~/.codex/auth.json`, or account tokens.

Third-party dependency notices are included in `decky/THIRD_PARTY_NOTICES.txt`. Deck AI itself is licensed under Apache-2.0 (`LICENSE`, `NOTICE`).

## Privacy and security

- Authentication is handled by the Codex CLI already installed on your machine.
- Claude authentication and subscription usage are handled by Claude Code. DeepSeek prompts and chat history are sent to OpenRouter using your key; OpenRouter usage and pricing are controlled by your OpenRouter account.
- Voice dictation uses local Vosk models and optionally a local multilingual Whisper model; microphone audio is not sent to a transcription service.
- Game screenshots and selected video frames are attached only when you choose to send a message containing them. Sent images are copied into private app state for chat previews and are preserved by uninstall. Image previews use local files or embedded image data; external image URLs are not fetched automatically.
- Do not commit personal SSH configuration, private keys, Codex state, logs, or local model files. The repository's ignore rules exclude common credential and machine-specific files.

## Languages

On a fresh install the interface and keyboard start in English. Choose **Interface: Русский** from the app menu to switch the interface to Russian. Use the voice-language menu to choose a supported language. The on-screen keyboard's language key cycles English and Russian; hold it to choose among the available layouts.

## Русский

Deck AI for Steam Deck — мультипровайдерное настольное приложение и плагин Decky Loader для Steam Deck. Доступны Codex, Claude через Claude Code, DeepSeek через OpenRouter и DeepSeek V4.1 Flash через TokenHarbor.

Возможности: список чатов, выбор модели, глубины рассуждений и скорости, управление аккаунтом Codex, тёмная и светлая темы, встроенная экранная клавиатура, локальная голосовая диктовка и компактная панель в Quick Access меню Steam. Плагин повторно подключается к локальному Codex app-server после запуска системы.

При первой установке интерфейс и экранная клавиатура запускаются на английском языке. Переключение интерфейса на русский находится в меню приложения. Базовая диктовка поддерживает английский и русский языки: загрузите модели командой `./scripts/download-models.sh`. Для уточнения текста и выбора из 99 поддерживаемых языков используйте `./scripts/download-models.sh --accurate-ru`. Клавиатура содержит раскладки EN, RU, DE, FR, ES, UK и IT.

Установка настольного приложения: `./install.sh`. Иконка `deck-ai.png` и все локальные изображения панели входят в репозиторий; отдельно скачивать их не нужно. Для игрового режима установите и запустите **Decky Loader**, затем после установки настольного приложения скопируйте всю папку `decky/` в `~/homebrew/plugins/Codex/` (имя папки сохраните `Codex`) и перезапустите Decky Loader. В Quick Access меню Steam появится плагин **Deck AI**. Папку `dist/` копируйте целиком: в ней находятся собранный интерфейс и сгенерированная ссылка на картинку.

Для сборки исходников плагина нужен Node.js 24 или новее: `cd decky && npm ci && npm test`. При обычной установке готового плагина Node.js не требуется. Для голосовой диктовки модели скачиваются отдельно командой `./scripts/download-models.sh`; в репозиторий они не включены, так как это большие файлы с отдельными лицензиями. TokenHarbor использует endpoint `https://tokenharbor.ai/v1` и модель `deepseek-v4.1-flash:free`; API-ключ хранится в системном хранилище секретов и не входит в проект.

Встроенная боковая панель браузера является дополнительной функцией. Для неё нужны WebKitGTK 4.1 или 4.0 и Python GObject bindings, доступные системе. Cookies браузера хранятся локально в каталоге данных приложения, а не в проекте. Если WebKitGTK не установлен, остальная оболочка продолжит работать, а браузер покажет сообщение о недостающей библиотеке.

Репозиторий не содержит паролей, ключей SSH, токенов, данных аккаунта, локальных чатов или установленных моделей речи. Не загружайте такие данные в публичный GitHub.

## Release verification

`VERSION`, `decky/package.json` and the package lock must agree. The current build is a release candidate, not a claim that all physical-device acceptance checks have passed.

```bash
python3 -m venv --system-site-packages .venv
.venv/bin/python -m pip install -r requirements.txt
npm --prefix decky ci --ignore-scripts
.venv/bin/python scripts/build-release.py
```

Optional live checks on the actual Deck (not run in CI):

```bash
.venv/bin/python scripts/check-decky-ui.py
DISPLAY=:1 .venv/bin/python scripts/check-gui.py
.venv/bin/python scripts/check-voice-send.py --live
```

The GUI and voice checks make one real Codex request each and use account quota. The voice check uses synthetic Russian audio rather than your microphone, uses isolated state and archives its test chat. Human speech accuracy and physical controller input still require manual acceptance.

The builder runs compilation, shell syntax checks, frontend tests, Python regression tests and package checks, then creates `build/releases/` with a desktop/source archive, a Decky runtime ZIP, `SHA256SUMS.txt` and `BUILD-REPORT.json`. Downloaded models, virtual environments, personal state and credentials are excluded. GitHub Actions runs the same builder and uploads artifacts; it does not publish a release automatically.

Before a stable `1.0.0` tag: test the archives on another SteamOS installation; check controller-only navigation, suspend/resume, network loss, microphone language/quality and game performance; and test every advertised optional provider with its own account. The stable-package check refuses a release without a LICENSE. Publishing to the Decky store is a separate review from creating a GitHub release.

## Development

```bash
python3 -m py_compile app.py backend.py providers.py ui_extras.py decky/bridge.py decky/main.py
python3 -m unittest discover -s tests -v
cd decky && npm ci && npm exec tsc -- --noEmit && npm run build
```

See [`SECURITY.md`](SECURITY.md) to report a vulnerability. See [`CHANGELOG.md`](CHANGELOG.md) for releases.
