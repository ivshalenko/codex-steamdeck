# Deck AI for Steam Deck

A community-built multi-provider AI desktop app and Decky Loader plugin for Steam Deck Desktop Mode and Gaming Mode.

The project is designed for Steam Deck. Choose between your signed-in Codex account, Claude Code with a Claude Pro/Max subscription, and DeepSeek through OpenRouter. The desktop client provides a chat list, provider controls, dark and light themes, an integrated on-screen keyboard, and offline voice dictation. The Decky plugin puts a compact multi-provider chat panel in Steam's Quick Access menu.

## Features

- Browse and continue local Codex chats; select models, reasoning effort, and speed.
- Switch between your signed-in Codex account, Claude Code using a Claude Pro/Max subscription, and DeepSeek models through OpenRouter.
- Browse the current DeepSeek catalog from OpenRouter. Model prices are shown where the catalog provides them; OpenRouter requests require your own API key and may incur charges.
- Sign in, view the current account, or sign out through Codex.
- Use Russian or English for the interface. **English is the default on a fresh install.**
- Dictate offline with Russian/English live previews and an optional multilingual Whisper final pass (99 supported languages). Audio stays on the Deck.
- View image attachments directly in chat history; select a thumbnail to enlarge it. Sent images are kept in private app state, and unavailable files are labeled rather than silently hidden.
- Type with the integrated keyboard. It includes English, Russian, German, French, Spanish, Ukrainian, and Italian layouts.
- Switch between dark and light themes.
- Use the Decky Quick Access plugin for chats, model controls and dictation.
- Optionally connect to another computer running Codex over SSH. SSH access is configured on your own devices; this repository contains no connection keys or account data.

The interface is currently translated into English and Russian. Voice recognition supports English and Russian with the basic models, or 99 model-supported languages and automatic detection with the optional multilingual model. Keyboard layouts cover the seven languages listed above; other interface and speech languages are not included yet.

No software license has been selected yet. Reuse and redistribution permissions have not been granted. A public release has not been published.

## Requirements

- Steam Deck with SteamOS and Desktop Mode.
- Codex CLI installed and signed in on the Deck. The official Codex CLI installation guide is at <https://developers.openai.com/codex/cli/>.
- Python 3, GTK 3 Python bindings, FFmpeg, PulseAudio-compatible microphone input, and a working audio input device.
- Optional: Decky Loader for the Gaming Mode Quick Access plugin.
- Optional: Claude Code installed and signed in with your Claude Pro/Max subscription to use Claude in the desktop companion. Sign in with `claude auth login`; do not use `--console` for a Pro/Max subscription.
- Optional: an OpenRouter API key to use DeepSeek. The desktop app stores it in the system Secret Service (KWallet/libsecret), not in the repository or Codex config.
- Internet access during setup to install Python packages and download speech models.

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

## Gaming Mode controls

- Compact chat fills Decky's available height. Use **На весь экран** to expand it; settings open on a separate full-screen page.
- Adjust **Масштаб чата и кнопок** for smaller text and controls.
- The **Игра** checkbox adds only the running game's name. With it off, Deck AI sends your text without game metadata or instructions. Screenshots are attached only when selected.
- The recording button turns red. A separate line previews speech; **Стоп** moves recognized text into the draft. Russian/English use the streaming recognizer without a second pass in Decky. **Очистить** clears the unsent draft; chat history stays intact. Other languages need the multilingual model and may take several seconds after stopping.
- Select a message to reveal **Копировать**. When reading older messages, use **К последнему сообщению** to resume following the response.
- Queued messages and errors remain visible. A successful click shows **Запрос принят · в очереди**; queued requests wait for the current response to finish. After a backend restart, in-flight sends are checked against server turn IDs; an ambiguous send requires checking the chat before retrying.

## Install the Decky plugin

1. Install and start Decky Loader on Steam Deck.
2. Install the desktop companion above first. The plugin uses its private Python environment and the local Codex app-server.
3. Copy the `decky` folder from this repository to `~/homebrew/plugins/Codex` (replace an older copy if updating).
4. Restart Decky Loader or reboot the Deck. Open Steam's Quick Access menu and choose **Deck AI**.

The plugin reconnects to Codex after Decky starts. It needs no separate OpenAI API key. To make it available through the Decky plugin store, a maintainer can submit this repository to the Decky plugin index after review.

## Optional: connect another computer

Install Codex CLI on the other computer and sign in there. Configure SSH on the Deck using your own SSH host alias and key, then select that device in Codex. Use a trusted private network or VPN such as Tailscale; do not expose the Codex app-server port directly to the public internet. Never upload private SSH keys, `~/.codex/auth.json`, or account tokens.

Third-party dependency notices are included in `decky/THIRD_PARTY_NOTICES.txt`. These are separate from the still-pending license choice for Deck AI itself.

## Privacy and security

- Authentication is handled by the Codex CLI already installed on your machine.
- Claude authentication and subscription usage are handled by Claude Code. DeepSeek prompts and chat history are sent to OpenRouter using your key; OpenRouter usage and pricing are controlled by your OpenRouter account.
- Voice dictation uses local Vosk models and optionally a local multilingual Whisper model; microphone audio is not sent to a transcription service.
- Game screenshots and selected video frames are attached only when you choose to send a message containing them. Sent images are copied into private app state for chat previews and are preserved by uninstall. Image previews use local files or embedded image data; external image URLs are not fetched automatically.
- Do not commit personal SSH configuration, private keys, Codex state, logs, or local model files. The repository's ignore rules exclude common credential and machine-specific files.

## Languages

On a fresh install the interface and keyboard start in English. Choose **Interface: Русский** from the app menu to switch the interface to Russian. Use the voice-language menu to choose a supported language. The on-screen keyboard's language key cycles English and Russian; hold it to choose among the available layouts.

## Русский

Deck AI for Steam Deck — мультипровайдерная настольная оболочка и плагин Decky Loader для Steam Deck. Подключайте Codex, Claude через Claude Code или DeepSeek через OpenRouter.

Возможности: список чатов, выбор модели, глубины рассуждений и скорости, управление аккаунтом Codex, тёмная и светлая темы, встроенная экранная клавиатура, локальная голосовая диктовка и компактная панель в Quick Access меню Steam. Плагин повторно подключается к локальному Codex app-server после запуска системы.

При первой установке интерфейс и экранная клавиатура запускаются на английском языке. Переключение интерфейса на русский находится в меню приложения. Базовая диктовка поддерживает английский и русский языки: загрузите модели командой `./scripts/download-models.sh`. Для уточнения текста и выбора из 99 поддерживаемых языков используйте `./scripts/download-models.sh --accurate-ru`. Клавиатура содержит раскладки EN, RU, DE, FR, ES, UK и IT.

Установка: `./install.sh`. Для игрового режима нужен Decky Loader; после установки настольного приложения скопируйте папку `decky` в `~/homebrew/plugins/Codex` и перезапустите Decky Loader. Для подключения Mac или Windows используется SSH и отдельная настройка на компьютере пользователя.

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

Before a stable `1.0.0` tag: select a LICENSE; test the archives on another SteamOS installation; check controller-only navigation, suspend/resume, network loss, microphone language/quality and game performance; and test every advertised optional provider with its own account. The stable-package check refuses a release without a selected LICENSE. Publishing to the Decky store is a separate review from creating a GitHub release.

## Development

```bash
python3 -m py_compile app.py backend.py providers.py ui_extras.py decky/bridge.py decky/main.py
python3 -m unittest discover -s tests -v
cd decky && npm ci && npm exec tsc -- --noEmit && npm run build
```

See [`SECURITY.md`](SECURITY.md) to report a vulnerability. See [`CHANGELOG.md`](CHANGELOG.md) for releases.
