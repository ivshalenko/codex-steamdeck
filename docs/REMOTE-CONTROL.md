# Steam Deck ↔ Mac / PC

## С компьютера управлять Steam Deck / Computer → Deck

Оба устройства должны быть включены в одной сети. Codex работает и выполняет команды **на Steam Deck**. Компьютер служит пультом. Нужен ваш собственный вход в ChatGPT на Deck.

1. На Deck откройте **Decky → Deck AI → Настройки → Доступ с другого компьютера → Показать данные подключения**. Запишите IP. Без Decky: в настольном Deck AI нажмите **+ → Управлять этим Steam Deck с Mac / ПК** — там есть адрес, отпечатки SSH, кнопка включения сервера и поле ключа.
2. Если SSH выключен: Desktop Mode → Konsole → `passwd` (задайте пароль администратора), затем `sudo systemctl enable --now sshd`. Пароль вводите только на самом Deck. Не пересылайте его в чат.
3. На Mac/ПК скачайте и распакуйте **remote-control.zip** из [последнего релиза](https://github.com/ivshalenko/codex-steamdeck/releases/tag/v1.0.0-rc.9). Нужен Python 3.9+ ([python.org](https://www.python.org/downloads/)) и OpenSSH Client. На Windows OpenSSH включается в «Дополнительные компоненты» системы.
4. Mac: откройте Terminal в распакованной папке, выполните `python3 scripts/connect-deck.py`. Windows: дважды нажмите **Connect-Steam-Deck.cmd**. Linux: `python3 scripts/connect-deck.py`.
5. Введите IP Deck. Мастер создаст отдельный ключ. Если IP поменялся, запустите мастер снова: он обновит только собственный блок deck-ai и сохранит резервную копию SSH-конфигурации. Пользовательские изменения в этом блоке требуют ручной настройки. Скопируйте показанную **публичную** строку `ssh-ed25519 …` на Deck в поле публичного ключа → **Разрешить этому компьютеру**. Закрытый ключ остаётся на компьютере.
6. Вернитесь в мастер и нажмите Enter. Сверьте SSH-отпечаток с показанным на Deck. Подтвердите только совпадающий отпечаток. Пароль Deck для этого подключения не нужен.
7. Мастер покажет полный путь к команде. Mac/Linux:

```sh
~/.local/bin/deck-remote new "Проверь свободное место на Steam Deck" --wait
~/.local/bin/deck-remote list
~/.local/bin/deck-remote read THREAD_ID
~/.local/bin/deck-remote send THREAD_ID "Продолжи проверку" --wait
```

Windows PowerShell:

```powershell
& "$HOME/.local/bin/deck-remote.cmd" new "Проверь свободное место на Steam Deck" --wait
& "$HOME/.local/bin/deck-remote.cmd" list
```

Ответы и продолжение диалога сохраняются на Deck. Не закрывайте крышку ноутбука/не усыпляйте Deck во время проверки связи. Включённый SSH позволяет авторизованному пользователю выполнять команды от вашего имени: добавляйте только собственные публичные ключи. Чтобы отключить доступ: удалите добавленную строку из `~/.ssh/authorized_keys` на Deck. `sudo systemctl disable --now sshd` отключает весь SSH-сервер (также остальные SSH-подключения).

## Со Steam Deck управлять Mac / Linux / Windows WSL

Здесь **исполнитель — компьютер**, а Steam Deck — пульт. Это отдельное направление; оно не настраивается автоматически предыдущим мастером.

1. Установите [официальный Codex CLI](https://github.com/openai/codex#quickstart) на компьютере и выполните вход в ChatGPT.
2. Mac: System Settings → General → Sharing → Remote Login. Разрешите нужного пользователя. Linux: установите и включите OpenSSH Server средствами своего дистрибутива.
3. На Deck создайте ключ `ssh-keygen -t ed25519`, публичную строку из `~/.ssh/id_ed25519.pub` добавьте в `~/.ssh/authorized_keys` **на компьютере**. Приватный ключ не копируйте.
4. На Deck выполните `ssh USER@COMPUTER_IP`, сверьте отпечаток и убедитесь, что вход по ключу работает. `exit` возвращает на Deck.
5. В настольном Deck AI нажмите **+ → Подключить удалённый Codex**: адрес, имя SSH-пользователя, путь ключа. Либо создайте SSH-алиас в `~/.ssh/config` и выберите его в Decky → Настройки → Устройство.
6. Проверьте безобидным запросом: «Покажи ОС и текущую папку». Убедитесь, что это нужный компьютер, прежде чем поручать изменение файлов.

**Windows как исполнитель:** используйте Linux в WSL с Codex и SSH-сервером внутри WSL. Нативный Windows SSH-host этим релизом не проверен и не заявлен как поддерживаемый. **Windows как пульт → Steam Deck** поддержан мастером, но требует отдельной проверки на настоящем Windows.

## Вне дома и неполадки

Вне одной сети используйте собственный VPN (например, Tailscale) на обоих устройствах и VPN-адрес вместо домашнего IP. VPN не входит в Deck AI и не настраивается мастером. Не открывайте порт 22 роутера в интернет ради плагина.

- Timeout: Deck уснул, IP изменился или устройства в разных сетях. Посмотрите адрес снова; закрепите IP в настройках роутера при необходимости.
- Permission denied (publickey): ключ не сохранён на Deck, выбран другой пользователь или другой закрытый ключ.
- Host key changed: не отключайте проверку. Убедитесь, что это ваш Deck и что он переустанавливался; лишь затем обновляйте запись known_hosts.
- Codex not found: установите Codex и войдите на **устройстве-исполнителе**.
- Чат виден, команда не запускается: проверьте подтверждение в чате и режим «только чтение»; откройте Диагностику. Возобновите диалог после сна кнопкой «Переподключиться».

## English quick path

On Deck: Deck AI Settings → Remote access → show address. Enable `sshd` in Desktop Mode if needed (`passwd`, then `sudo systemctl enable --now sshd`). On your computer install Python 3.9+ and OpenSSH Client, unzip the release's remote-control ZIP, run `python3 scripts/connect-deck.py` (Windows: `Connect-Steam-Deck.cmd`). Paste its **public** key into Deck AI, save, then continue the wizard and compare the SSH host fingerprint with Deck's screen. Use the generated `deck-remote` launcher for `new`, `list`, `read`, and `send`. Tasks execute on Deck. For the reverse direction enable SSH + sign into Codex on your Mac/Linux computer, authorize Deck's public key there, and select that host in Deck AI. Windows hosts require WSL; native Windows hosting is unverified. Internet access needs your own VPN; devices must stay awake.
