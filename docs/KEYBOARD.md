# English and Russian on a physical keyboard

[Русская инструкция](KEYBOARD.ru.md)

For a USB or Bluetooth keyboard connected to your Steam Deck:

1. Open **Deck AI → Settings → Physical keyboard**.
2. Press **Enable EN/RU**.
3. Save your game, switch to **Desktop Mode**, then return to **Gaming Mode**.
4. Press **Alt+Shift** to switch between English and Russian. A new Gaming Mode session starts in English.

The desktop companion offers the same setting in **Language and voice → Physical keyboard in Gaming Mode**. It takes effect on this Deck, including when your chat uses a remote Mac or PC. Use **Restore SteamOS layout**, then re-enter Gaming Mode, to undo the preset.

The setting is opt-in. Updating Deck AI does not replace anyone's keyboard layout automatically. A separately edited configuration is preserved and reported. No administrator password or SteamOS filesystem unlock is needed.

## Three different language settings

| Setting | What it changes |
| --- | --- |
| Interface language | Deck AI's menus and notification captions |
| Dictation language | Speech recognition |
| Physical keyboard | The characters typed with your connected keyboard in Gaming Mode |

The EN/RU preset applies to the Gamescope session, including Steam and games that use its keyboard layout. KDE Desktop Mode keeps its existing keyboard settings. A game's own raw-key bindings may behave differently; switch to English when entering commands or using English game bindings.

Steam's on-screen keyboard has its own active languages under **Steam → Settings → Keyboard**. It is separate from this physical-keyboard setting.

## Verification

The rc.20 check sent bounded Linux keyboard events through a temporary virtual keyboard on a physical Steam Deck. It typed `hello привет world` in the real Deck AI composer, switching EN → RU → EN with Alt+Shift. A Gaming Mode restart loaded the saved session setting. This is an end-to-end compositor/input check, not a claim that every USB or Bluetooth keyboard model was tested by a person.

The implementation uses only a user-owned Gamescope service override. It does not monitor or log keystrokes, change interface/dictation languages, or edit KDE's keyboard settings. The standard Gamescope session environment is the source of the active-state check; merely saving an X11 keymap does not count as active physical-keyboard support.
