# Deck AI for Steam Deck

A community-built multi-provider AI desktop app and Decky Loader plugin for Steam Deck Desktop Mode and Gaming Mode.

The project is designed for Steam Deck. Choose between your signed-in Codex account, Claude Code with a Claude Pro/Max subscription, and DeepSeek through OpenRouter. The desktop client provides a chat list, provider controls, dark and light themes, an integrated on-screen keyboard, and offline voice dictation. The Decky plugin puts a compact multi-provider chat panel in Steam's Quick Access menu.

## Features

- Browse and continue local Codex chats; select models, reasoning effort, and speed.
- Switch between your signed-in Codex account, Claude Code using a Claude Pro/Max subscription, and DeepSeek models through OpenRouter.
- Browse the current DeepSeek catalog from OpenRouter. Model prices are shown where the catalog provides them; OpenRouter requests require your own API key and may incur charges.
- Sign in, view the current account, or sign out through Codex.
- Use Russian or English for the interface. **English is the default on a fresh install.**
- Dictate offline in Russian or English using Vosk speech models; audio is processed on the Deck.
- Type with the integrated keyboard. It includes English, Russian, German, French, Spanish, Ukrainian, and Italian layouts.
- Switch between dark and light themes.
- Use the Decky Quick Access plugin for chats, model controls, dictation, screenshots, and recent game recordings.
- Optionally connect to another computer running Codex over SSH. SSH access is configured on your own devices; this repository contains no connection keys or account data.

The interface is currently translated into English and Russian. Voice recognition currently supports English and Russian. Keyboard layouts cover the seven languages listed above; other interface and speech languages are not included yet.

No software license has been selected yet. The repository is public to view and download, but reuse and redistribution permissions have not been granted.

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
./install.sh
```

The installer creates an isolated Python environment, installs the app under `~/.local/share/codex-steamdeck`, and adds a **Deck AI** launcher to the application menu. It does not install provider CLIs, sign in to an account, or change existing credentials.

For offline voice dictation, download the English and Russian Vosk models:

```bash
./scripts/download-models.sh
```

The models are large downloads (about 150 MB together). Without them, chat and keyboard input still work; dictation will ask you to install the selected model.

## Install the Decky plugin

1. Install and start Decky Loader on Steam Deck.
2. Install the desktop companion above first. The plugin uses its private Python environment and the local Codex app-server.
3. Copy the `decky` folder from this repository to `~/homebrew/plugins/Codex` (replace an older copy if updating).
4. Restart Decky Loader or reboot the Deck. Open Steam's Quick Access menu and choose **Codex**.

The plugin reconnects to Codex after Decky starts. It needs no separate OpenAI API key. To make it available through the Decky plugin store, a maintainer can submit this repository to the Decky plugin index after review.

## Optional: connect another computer

Install Codex CLI on the other computer and sign in there. Configure SSH on the Deck using your own SSH host alias and key, then select that device in Codex. Use a trusted private network or VPN such as Tailscale; do not expose the Codex app-server port directly to the public internet. Never upload private SSH keys, `~/.codex/auth.json`, or account tokens.

## Privacy and security

- Authentication is handled by the Codex CLI already installed on your machine.
- Claude authentication and subscription usage are handled by Claude Code. DeepSeek prompts and chat history are sent to OpenRouter using your key; OpenRouter usage and pricing are controlled by your OpenRouter account.
- Voice dictation uses local Vosk models; microphone audio is not sent to a transcription service.
- Game screenshots and selected video frames are attached only when you choose to send a message containing them.
- Do not commit personal SSH configuration, private keys, Codex state, logs, or local model files. The repository's ignore rules exclude common credential and machine-specific files.

## Languages

On a fresh install the interface and keyboard start in English. Choose **Interface: Русский** from the app menu to switch the interface to Russian. The voice button toggles between English and Russian speech recognition. The on-screen keyboard's language key cycles English and Russian; hold it to choose among the available layouts.

## Русский

Deck AI for Steam Deck — мультипровайдерная настольная оболочка и плагин Decky Loader для Steam Deck. Подключайте Codex, Claude через Claude Code или DeepSeek через OpenRouter.

Возможности: список чатов, выбор модели, глубины рассуждений и скорости, управление аккаунтом Codex, тёмная и светлая темы, встроенная экранная клавиатура, локальная голосовая диктовка и компактная панель в Quick Access меню Steam. Плагин повторно подключается к локальному Codex app-server после запуска системы.

При первой установке интерфейс и экранная клавиатура запускаются на английском языке. Переключение интерфейса на русский находится в меню приложения. Диктовка поддерживает английский и русский языки; для неё нужно загрузить локальные модели Vosk командой `./scripts/download-models.sh`. Клавиатура содержит раскладки EN, RU, DE, FR, ES, UK и IT.

Установка: `./install.sh`. Для игрового режима нужен Decky Loader; после установки настольного приложения скопируйте папку `decky` в `~/homebrew/plugins/Codex` и перезапустите Decky Loader. Для подключения Mac или Windows используется SSH и отдельная настройка на компьютере пользователя.

Репозиторий не содержит паролей, ключей SSH, токенов, данных аккаунта, локальных чатов или установленных моделей речи. Не загружайте такие данные в публичный GitHub.

## Development

```bash
python3 -m py_compile app.py backend.py providers.py ui_extras.py decky/bridge.py decky/main.py
python3 -m unittest discover -s tests -v
cd decky && npm ci && npm exec tsc -- --noEmit && npm run build
```

See [`SECURITY.md`](SECURITY.md) to report a vulnerability. See [`CHANGELOG.md`](CHANGELOG.md) for releases.
