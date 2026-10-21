# Security policy

Please do not publish credentials or exploit details in an issue. Report security problems privately to the repository maintainer through GitHub's private vulnerability reporting, if enabled.

Never share Codex auth files, API tokens, SSH private keys, SSH configuration containing private host details, or unredacted application logs.

The app uses the local Codex CLI/app-server and does not include credentials in this repository. Remote computers are reached only through SSH configured by the user. Keep SSH restricted to trusted devices and do not expose the Codex app-server directly to the internet.

The optional OpenRouter API key is stored through the desktop Secret Service interface and is never written into application state or project files. Do not paste API keys into issue reports or commit them. Claude Pro/Max authentication is owned by Claude Code; use its subscription login (`claude auth login`), not Anthropic Console API credentials, when using a Pro/Max plan.
