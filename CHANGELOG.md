# Changelog

## Unreleased

- Design: seven colour themes (Ocean, Graphite, Violet, Forest, Amber, Rose, Light), three message styles (bubbles, lines, cards), three densities, and three layouts — tabs on top, tabs at the bottom (thumb-friendly), and two columns with a chat list beside the conversation in full screen. Settings → «Оформление». Pill-shaped tabs, card-style settings and composer, themed focus highlights.
- Chat toolbar with New chat, Files, Queue and Refresh, always one tap away; the main «Отправить» button no longer wraps in the narrow panel.
- Desktop app: the same colour themes in the menu (Colour theme).
- Any cloud AI: connect any cloud service with an OpenAI-compatible API (OpenAI, Gemini, Groq, Mistral, DeepSeek, xAI, Together, Fireworks, OpenRouter, …) with a name, https address, API key and optional models, in Decky settings and in the desktop app's + menu. Only public https hosts are accepted: localhost, LAN addresses and internal names (Ollama, LM Studio) are rejected. Models are discovered from the service's `/models` list; keys live in the system secret store; error bodies are never shown.
- Enter sends the message (Decky field and desktop app; Shift+Enter keeps a new line in the desktop app). Finger drag scrolls messages and lists in Decky (with momentum) and in the desktop app (kinetic scrolling).
- Install: `./install.sh --decky` installs the Decky plugin in one step; `scripts/deck-remote.py HOST setup ADDRESS` guides the Mac/PC side; an optional GitHub Pages workflow generates a project web page from the README when explicitly enabled.
- Control the Deck from a Mac or PC over SSH: «Доступ с другого компьютера» in Decky settings shows whether SSH is running, the Deck's addresses (including Tailscale), a ready `~/.ssh/config` block, and adds a pasted public key to `authorized_keys` (validated; private keys and key options are rejected). Enabling `sshd` stays a manual one-time step.
- `scripts/deck-remote.py` (Python 3 + ssh only): `list`, `read`, `send`, `new`, `--wait`, with y/N approval prompts in the terminal. The SSH client no longer needs the `websockets` package.
- License: Apache-2.0 with a `NOTICE` file. Redistribution and derivative works must keep the copyright notice and credit the author (ivshalenko).
- Background monitoring: pick up to 5 SSH machines under «Следить в фоне»; their results and approval requests arrive as notifications while another device is selected. Running chats are resumed automatically so their events are received.
- Approvals require a second press on «Разрешить». Read-only mode blocks sending, approving, stopping and file edits (also enforced in the backend).
- Queue: send a waiting request first, or remove it. «Что произошло» keeps the event history across restarts.
- Device files: browse the home folder of this Deck or the selected SSH machine, open and edit small UTF-8 text files (64 KB, a `.deckai.bak` copy is kept, edits are refused if the file changed meanwhile). Keys, `.ssh`, `.env` and other secrets are blocked.
- Speech: `heard => written` lines in `vocabulary.txt` correct any recognizer's output; hands-free end of phrase (2.5 s pause) when auto-send is enabled; editable ⚡ quick phrases; «🔊 Озвучить» for answers when the system provides speech synthesis.
- `scripts/backup-state.py` (run by `install.sh` before updates) archives chats and settings, keeping the last five.
- Decky: Steam toasts when a task finishes, fails or needs approval, even with the panel closed (can be turned off in settings). Approval requests show Allow/Decline buttons in the chat.
- Decky: «Задачи на всех устройствах» in History lists running and recent chats from every device visited; one tap switches device and opens the chat.
- Decky: command runs and file changes (with diff) appear as compact, expandable entries; ⚡ quick actions (Continue, Show diff, Run tests, Explain error).
- Decky: the X button toggles dictation; optional auto-send 3 s after stopping (cancellable); connection countdown with 5–30 s backoff; one-click diagnostics; button to unload speech models from memory.
- Remote devices: uploaded screenshots older than 7 days are removed on connect.
- Speech: custom vocabulary (`vocabulary.txt` next to the app or `~/.config/deck-ai/vocabulary.txt`, one word per line); `DECK_AI_WHISPER_SIZE=tiny|base ./scripts/download-models.sh --accurate-ru` for a faster final pass; timings are logged to `models/speech-timing.jsonl`.
- Tests: protocol-level stand-in for `codex app-server` covers send, completion, notifications and approvals end to end.
- Remote devices: screenshots and video frames can now be sent; images are copied over the shared SSH connection to `~/.cache/deck-ai-uploads` on the remote computer.
- Remote devices: text requests go through the open app-server connection (turn IDs, completion tracking, recovery after restart); a failed resume remains visible for retry without sending through a separate CLI queue.
- Remote devices: share one SSH connection per host (ControlMaster) with keepalives, so connecting, queueing and reconnecting no longer repeat the SSH handshake.
- Decky: live server events refresh the open chat immediately; idle chats are polled less often. Chats that are running show a pulsing dot and sort first, with a running count in the status bar.
- Decky: switch device and refresh remote tasks directly from the History tab; remote chats can be opened while another is running.
- Dictation: Vosk models stay loaded between recordings (released after 3 minutes idle), and the multilingual final-pass model loads while you speak instead of after you stop.
- Add an inspectable Decky queue with per-chat waiting counts, timestamps, full request text and navigation to the originating chat.
- Flag long-running work for review and clear transient connection errors after recovery.

- Show inline image attachments in Decky and desktop chat history, including image-only messages and assistant image links.
- Open thumbnails in a bounded image viewer; keep owned copies of sent images so temporary frame cleanup cannot remove them from history.
- Show unavailable images and file attachments by name without fetching external URLs.

## 1.0.0-rc.4 — Verified Steam Deck remote execution

- Add the JSONL-to-WebSocket adapter required to connect SSH clients to the shared Codex Unix socket; use the companion Python environment when available and stdio otherwise.
- Match remote completion events to their own chat and turn, retain fast replies and fail clearly on disconnection or an unsuccessful turn.
- Restore the original library search path when launching Codex or the Decky bridge from PyInstaller, preventing Decky libraries from causing `GLIBC_2.42 not found` on SteamOS.
- Account for both `deck-ai` and `deck-voice` installation folders during SSH setup.
- Add a real Unix WebSocket adapter round trip and regressions for event matching, reconnect failures and frozen-process environment cleanup.
- Verified actual SSH chat creation, continuation after reconnect/server restart, and shell execution on Steam Deck.

## 1.0.0-rc.3 — Connection fixes

- Make the optional Pages deployment opt-in with `ENABLE_GITHUB_PAGES=true`, so repositories without Pages can publish code and pass checks.
- Ensure the one-shot Rollup build exits after writing the bundle, so the release checker can continue on Node 24.
- Replace the unavailable `websockets==17.3` pin with the verified installable `15.0.1` version.
- Use the shared Codex daemon proxy over SSH when available, with stdio fallback for CLIs without daemon commands; resolve Codex in non-interactive SSH sessions.
- Resume existing local and remote chats before sending on the same RPC transport. Do not resume a fresh remote chat before its first turn.
- Use device-code login in Gaming Mode and on remote hosts, and show the code alongside the URL.
- Close child processes and pipes after failed initialization, shutdown or device changes. Ignore non-JSON banners and prevent UI callback errors from killing the response reader.
- Respect custom `CODEX_HOME`; reject SSH aliases that could become command options.
- Scope queue completion/recovery to its owning device. Refresh cached model catalogs after expiry.
- Block file-reader symlinks that point to credentials or paths outside the permitted home directory.
- Add strict protocol, connection lifecycle, first remote send, device-code login, minimal SSH PATH and secret-symlink regressions.

## 1.0.0-rc.2 — Release candidate

- Fix the first queued send in a new Codex chat before turn history is available.
- Avoid reactivating a queue job when completion arrives before the start RPC reply.
- Keep recordings attached to their original chat and persist consumed dictation across frontend reloads.
- Preserve edits and newly typed drafts while sends or recognition updates are in flight.
- Use streaming RU/EN dictation in Decky, show immediate stop results and clear drafts safely.
- Remove the redundant game/files action; keep the optional game-name checkbox.
- Add an opt-in real speech-to-Codex integration check using synthetic audio and isolated state.

## 1.0.0-rc.1 — Release candidate

- Add safe installation upgrades, rollback and data-preserving uninstall; unify legacy installation paths.
- Add deterministic release archives, checksums, package privacy checks and CI validation.
- Persist the desktop dictation language across restarts.
- Fill the Quick Access panel height and provide compact full-screen chat/settings with adjustable text and controls.
- Add message copy controls, return-to-latest navigation, visible queue state, and transient notices.
- Match queue completion by thread and turn, recover acknowledged sends after bridge restarts, and wait for existing turns before sending queued prompts.
- Prevent old bridge readers from clearing requests belonging to a replacement process.
- Add optional offline multilingual final-pass dictation, separate speech preview, and recording indicators.
- Make the game checkbox append only the game name; unchecked prompts contain no injected game instructions.
- Cover queue recovery, bridge lifecycle, dictation, and game context in regression tests; add a Gaming Mode UI smoke check.

- Add separate Claude Code (Claude Pro/Max) and DeepSeek via OpenRouter provider modes to desktop and Decky.
- Store OpenRouter credentials using the system Secret Service; fetch the DeepSeek model catalog and show published prices.
- Keep third-party provider chats isolated from Codex threads.

## Initial public preparation

- Steam Deck desktop chat companion with integrated keyboard and offline dictation.
- Decky Loader Quick Access plugin with chat, model, account, screenshot, and recording support.
- English default for fresh installations, with Russian interface and voice support.
- Optional SSH connection to Codex on another computer.
