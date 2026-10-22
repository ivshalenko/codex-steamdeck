# Changelog

## Unreleased

- Show inline image attachments in Decky and desktop chat history, including image-only messages and assistant image links.
- Open thumbnails in a bounded image viewer; keep owned copies of sent images so temporary frame cleanup cannot remove them from history.
- Show unavailable images and file attachments by name without fetching external URLs.

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
