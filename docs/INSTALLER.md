# An illustrated setup, in your language

[Open the download page](https://ivshalenko.github.io/codex-steamdeck/install/) · [Full installation guide](QUICKSTART.md) · [Russian guide](QUICKSTART.ru.md)

1. In Desktop Mode, open the download page and click **Download for Steam Deck**. It serves the versioned setup ZIP directly from GitHub Pages, without sending the browser to raw source or the GitHub release download gateway.
2. Open the ZIP in Ark, choose **Extract**, and keep all files together in **Deck AI Setup**.
3. Open **Install Deck AI** from the extracted folder in Dolphin. Confirm the SteamOS launch prompt, choose your language and **Automatic**.

The ZIP includes the checked app archive, official Codex package and an executable launcher. The app does not need to download again before the wizard opens. Internet is still needed for a missing Decky Loader and account sign-in. SteamOS launch trust and your own administrator password remain personal confirmations.

If you previously downloaded a standalone `.desktop` file and Dolphin offered Kate / KWrite, close that chooser and use the ZIP route above. The setup ZIP preserves execution permissions through extraction. Do not launch the file inside the archive preview: extract all files first.

The pinned official Codex installer recovers package downloads through the official OpenAI GitHub API after temporary 504 errors. Its original checksum and installation checks remain. Close an older failed setup and run this one; existing settings are retained.

## Automatic setup

English is the default, including on a fresh profile with a Russian system locale. Automatic setup installs the app, missing official Codex and the Gaming Mode plugin. If Decky Loader is missing, its official installer runs in a visible terminal. An existing Loader is reused; your chats, accounts and models remain.

Automatic setup also adds **Deck AI** to the Steam library with all five artwork assets. If Steam is still starting, the completion screen says the step is pending and Deck AI finishes it automatically when its app or Decky panel starts. Sign into Steam under the same Linux account. Custom setup can disable this option. Existing user edits to previously installed artwork are kept.

App installation and updates also create an executable **Deck AI** shortcut on the Desktop (including a localized desktop folder). Open it to launch the app in Desktop Mode. The application-menu entry remains available. Existing personal or edited desktop files are kept, and repeated updates do not create duplicate shortcuts.

![Actual automatic setup on Steam Deck.](media/en/branding/installer-automatic.png)

## Custom components and access

Choose which components to install. Local dictation downloads only the selected English or Russian pack. SSH is enabled only when selected; pairing still requires authorizing your own computer's public key. Decky can allow chat and confirmed actions or open saved history only. This is an application mode, not an operating-system sandbox. Desktop action permissions remain in the desktop app's own settings.

Automatic setup does not enable new SSH access or add voice packs. You can add these later. It does not turn off existing SSH or remove previously installed voice packs.

![Actual rc.17 custom setup on Steam Deck.](media/en/branding/installer-custom.png)

The two screenshots above show the rc.17 native installer, captured without starting installation in a temporary profile. The progress, completion and first-launch captures below document the earlier rc.15 installation test.

## Visible progress and a truthful result

The full ZIP includes the app's WebSocket wheel, official Codex package, pinned metadata and verified upstream installer. App and Codex installation need no network after extraction. A missing Decky Loader, optional downloads and account sign-in still need internet. Progress shows the current stage, with technical details underneath. Administrative tasks run in Konsole; enter the SteamOS password only there. A cancelled terminal, failed command or missing completion receipt does not display success. Return to the choices and retry.

![Actual installation running on Deck in a temporary profile.](media/en/installer/04-installing.png)

After installation, the completion page opens Deck AI for account sign-in and offers computer pairing. Account sign-in remains personal; the installer does not grant itself access to an AI account or collect passwords.

![Actual completion of the isolated desktop and Codex installation.](media/en/installer/05-ready.png)

## First launch uses your selection

Choose Russian in the installer and both the desktop companion and Decky use Russian. Choose English and they use English. Menu language does not translate existing chats, file contents or command output. A prior dictation language is kept unless you explicitly install a new selected-language pack.

![Actual first launch after choosing English.](media/en/installer/06-first-launch-en.png)

[Earlier English installer gallery (rc.15)](https://github.com/ivshalenko/codex-steamdeck/releases/download/v1.0.0-rc.15/deck-ai-1.0.0-rc.15-installer-media.zip) · [Capture manifest](media/en/installer/manifest.json)

These are real GTK captures on Steam Deck. The fresh-profile check installed the desktop app and pinned official Codex in a temporary HOME, then updated with Russian selected and checked both first launches. It did not replace the user's Decky Loader or enable SSH for that test. Missing-Loader installation and administrator failures have isolated regression coverage; a second clean physical Deck remains an independent check. [Verification details](RELEASE-rc.15.md).
