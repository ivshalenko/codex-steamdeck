![Deck AI — Your AI. Right on Deck. Chat, fix and control your Steam Deck from Gaming Mode or your computer.](docs/brand/hero.svg)

[English](README.md) · [Russian](docs/README.ru.md)

[![Build](https://github.com/ivshalenko/codex-steamdeck/actions/workflows/checks.yml/badge.svg)](https://github.com/ivshalenko/codex-steamdeck/actions/workflows/checks.yml) [![Release candidate](https://img.shields.io/badge/release-1.0.0--rc.14-a8e1fa?style=flat-square&labelColor=17212d)](https://github.com/ivshalenko/codex-steamdeck/releases/tag/v1.0.0-rc.14) [![Steam Deck](https://img.shields.io/badge/made_for-Steam_Deck-c5d5e2?style=flat-square&labelColor=17212d)](docs/QUICKSTART.md) [![License](https://img.shields.io/badge/license-Apache_2.0-c5d5e2?style=flat-square&labelColor=17212d)](LICENSE)

**Ask for help, investigate a launch error, or send a task from your Mac.** Deck AI puts Codex in your Steam Deck's Quick Access menu, with full-screen chat, action confirmations, attachments and completion notifications. A desktop companion and SSH remote control are included.

[![Download Deck AI — open the rc.14 release and choose Install-Deck-AI.desktop.](docs/brand/install.svg)](https://github.com/ivshalenko/codex-steamdeck/releases/tag/v1.0.0-rc.14)

**[Installation](#install-on-your-steam-deck)** · **[See it in action](#see-it-in-action)** · **[Mac / PC connection](#your-computer-your-deck-one-conversation)** · **[Questions](#questions)** · **[All documentation](#find-your-next-step)**

Free, open source, and independently distributed. **Release candidate · manual installation.** You use your own provider account; its plan, usage limits and charges still apply. [Decky store status](docs/DECKY-SUBMISSION.md).

## One companion, three ways to use it

| In Gaming Mode | On the desktop | From your computer |
| --- | --- | --- |
| Open **(…) → Decky → Deck AI**. Ask a question, attach a screenshot, review an action, then return to your game. | Use the GTK app for longer conversations, local dictation, languages and account setup. | Pair Mac, Windows or Linux over SSH. Create a task on Deck and continue the same conversation. |

## See it in action

![Deck AI in English: a real code change and passing test on Steam Deck.](docs/media/en/screenshots/27-confirmed-result.png)

**A real fix, two-step approval, and an unchanged test that passes.** New English conversations and English Steam menus, captured on a real Deck with rc.14.

| Make it yours | Keep playing |
| --- | --- |
| ![English Deck AI appearance controls.](docs/media/en/screenshots/07-appearance-settings.png) | ![An actual English Steam completion toast.](docs/media/en/screenshots/11-completion-notification.png) |
| Themes, layout and text density. | A completion toast opens the correct conversation. |

**[Browse 22 English screenshots](docs/MEDIA.en.md)** · [Download the English gallery](https://github.com/ivshalenko/codex-steamdeck/releases/download/v1.0.0-rc.14/deck-ai-1.0.0-rc.14-english-media.zip)

These are actual interface captures with new English demonstration chats. Game setup requests and simulated error reports do not prove a successful game installation. The [Russian video archive](docs/MEDIA.md) remains available separately.

## Install on your Steam Deck

You need a Steam Deck running SteamOS, internet access and your own ChatGPT account for Codex. For the Quick Access plugin, install [Decky Loader](https://decky.xyz) first. Text chat does not need voice models, Node.js or a source build.

| Step | What to do |
| --- | --- |
| **01 · Download** | Switch to **Desktop Mode**. Open the [rc.14 release](https://github.com/ivshalenko/codex-steamdeck/releases/tag/v1.0.0-rc.14) and download **Install-Deck-AI.desktop** onto the Deck. |
| **02 · Install & sign in** | Open the file in Dolphin; allow execution/trust if asked. Follow the wizard, keep the Codex option selected if needed, and choose the Decky plugin if Decky is installed. Open Deck AI and sign into ChatGPT. Enter any sudo password only in the SteamOS terminal prompt. |
| **03 · Open & ask** | Return to **Gaming Mode → (…) → Decky → Deck AI → New chat**. Try: “Show the free space on my Steam Deck.” Review any requested action before approving it. |

**[Full illustrated setup →](docs/QUICKSTART.md)** · [Already have Decky? Manual ZIP instructions](docs/QUICKSTART.md#decky-zip-only)

![The actual Deck AI installation wizard running on Steam Deck.](docs/media/en/screenshots/09-installation-wizard.png)

## Your computer. Your Deck. One conversation.

![Mac, Windows or Linux sends a task over SSH; Codex runs on Steam Deck and returns the reply. Both devices stay awake.](docs/brand/remote.svg)

**Computer → Deck:** download the release's **remote-control.zip** on your computer and run the pairing wizard. Authorize its public key on Deck and compare the SSH fingerprint. The wizard creates a `deck-remote` launcher for your computer.

After pairing, on Mac or Linux:

```sh
~/.local/bin/deck-remote new "Show the free space on my Steam Deck" --wait
~/.local/bin/deck-remote list
~/.local/bin/deck-remote send THREAD_ID "Continue the check" --wait
```

**Deck → computer** is a separate setup: enable SSH and sign into Codex on your Mac/Linux host, then select that host in Deck AI. Windows hosts need WSL. The Windows client helper is available; a real Windows-device check remains outstanding.

Both devices must stay awake and reachable. Start on the same network; access away from home needs your own VPN. **[Pairing, Windows commands and troubleshooting →](docs/REMOTE-CONTROL.md)**

## More than a chat window

| You want to… | Deck AI helps you… |
| --- | --- |
| Understand why a game won't start | Inspect Steam launch settings and test a reversible launch-option reset. A paired browser can review or approve the repair. [Launch repair](docs/LAUNCH-REPAIR.md). |
| Show the problem | Attach Steam screenshots or up to four frames from a recording, within a five-image message limit. |
| Keep track of work | See pending tasks, review Codex confirmations and open the correct conversation from a completion notification. Keep Steam and Decky running. |
| Check or edit a file | Browse the selected device. The editor preserves unsaved changes across a device switch and checks the file version before saving. |
| Speak instead of type | Download an optional language pack in the desktop app. Dictation runs locally; the resulting prompt goes to your chosen provider. |
| Use another provider | Connect [Claude Code through its official CLI](docs/CLAUDE-AUTH.md), DeepSeek, OpenRouter or a compatible API. Use your own credentials. |

Codex actions have confirmations in Deck AI. Claude Code uses native CLI permissions; actions needing an interactive prompt must be handled in its terminal. API chat providers return chat replies. Features and account limits depend on the provider.

**Interface language:** Settings → Interface and voice → Interface language → English or Russian. Existing conversations keep their original text; choose **New chat** for a new English conversation. Speech recognition has its own language setting.

## Questions

### Is it free?

Deck AI is free under Apache-2.0. It does not include a cloud subscription, API credit, games or game files. Provider fees depend on your account.

### Where do my prompts and keys go?

Prompts and attachments go to the selected cloud provider. Dictation is local. Settings/history stay on your device, Codex manages its own credentials, and optional API keys use Secret Service/KWallet. A locked wallet can block an API provider. [Security and privacy](SECURITY.md).

### A chat is slow to reconnect. Should I send the task again?

Check the queue and the existing conversation first. After sleep or a network change, let the connection recover or choose **Reconnect**. Your draft and saved history remain available. [Troubleshooting](docs/QUICKSTART.md#troubleshooting).

### Is it in the official Decky store?

No. The store submission was declined on 3 November 2026 under its rules on LLM-access plugins and code written mostly by LLMs. This project used substantial Claude/Codex assistance and is distributed independently through GitHub. [Decision and status](docs/DECKY-SUBMISSION.md).

### How thoroughly has rc.14 been checked?

210 Python tests and 37 frontend logic tests passed. All 14 device UI checks passed in English and again in Russian. A real English Codex task fixed a small demonstration project, preserved its original test and passed it. Mac-to-Deck chat and completion-toast navigation were verified. [English release checks](docs/RELEASE-rc.14.md).

The earlier rc.13 build also completed timed queue, attachment and HTTP runs. Those durations are not claimed as new rc.14 runs. Physical controls, a second clean device, Stable/Beta coverage, suspend during a task, Windows and all optional providers still need separate checks.

## Find your next step

| Start using | Explore | Help improve |
| --- | --- | --- |
| [Installation](docs/QUICKSTART.md) | [English screenshot gallery](docs/MEDIA.en.md) | [Report a bug](https://github.com/ivshalenko/codex-steamdeck/issues/new?template=bug.yml) |
| [Mac / PC pairing](docs/REMOTE-CONTROL.md) | [Launch repair](docs/LAUNCH-REPAIR.md) | [Suggest a feature](https://github.com/ivshalenko/codex-steamdeck/issues/new?template=feature.yml) |
| [Claude Code sign-in](docs/CLAUDE-AUTH.md) | [Similar projects](docs/COMPARISON.md) | [Contributing](docs/CONTRIBUTING.md) |

## Build and attribution

```sh
python3 -m venv --system-site-packages venv
venv/bin/python -m pip install -r requirements.txt
npm --prefix decky ci --ignore-scripts
venv/bin/python scripts/build-release.py
```

Requirements: SteamOS x86-64 and Python 3.9+. The graphical app/installer needs GTK 3/PyGObject; media extraction needs FFmpeg. No SteamOS root-filesystem unlock is required. Updates retain user data; `~/.local/bin/deck-ai-uninstall` removes managed desktop files and retains user data. See the [setup guide](docs/QUICKSTART.md) for updates and plugin removal.

Created by **[ivshalenko](https://github.com/ivshalenko)**. [Apache-2.0](LICENSE) · [NOTICE](NOTICE) · [Third-party licenses](decky/THIRD_PARTY_NOTICES.txt). Releases include the corresponding LGPL source package. Preserve attribution and notices when redistributing. Community project; not affiliated with Valve, OpenAI or Anthropic.
