# Скриншоты и видео Deck AI

Материалы сняты на настоящем Steam Deck. Записи 01–05 относятся к rc.5/rc.6, 06 — к rc.7, 08 — к rc.8. Игровые запросы показывают историю общения и не доказывают установку или запуск игры. Пример исправления — отдельный демонстрационный проект. Записи без голоса ведущего; исходный захват около 2–4 кадров/с, MP4 закодированы в 30 fps.

Bloodborne и Zelda используются как примеры запросов о настройке эмуляции. Для озвучки: «Показываю, как попросить помощника настроить эмулятор и разобраться с ошибкой. Игровые образы, ключи и прошивки плагин не предоставляет; необходимые права на используемые файлы пользователь обеспечивает сам». Эти кадры не подтверждают работоспособность эмуляции. Само слово «эмуляция» не определяет законность происхождения файлов или обхода защиты; для Nintendo действуют также [правила публикации видео, включая A11](https://www.nintendo.co.jp/networkservice_guideline/en/index.html#q11). Не обещайте зрителям гарантированную законность любого такого сценария.

**[Скачать все 7 видео и 21 скриншот](https://github.com/ivshalenko/codex-steamdeck/releases/download/v1.0.0-rc.8/deck-ai-1.0.0-rc.8-public-media.zip)** — распакуйте ZIP и откройте `index.html`. [Релиз и установка](https://github.com/ivshalenko/codex-steamdeck/releases/tag/v1.0.0-rc.8).

## Видео для сценария

| Сцена | Файл | Длительность |
|---|---|---|
| История реальных игровых запросов: Zelda и список чатов | [01-real-game-conversations.mp4](https://github.com/ivshalenko/codex-steamdeck/releases/download/v1.0.0-rc.8/01-real-game-conversations.mp4) | 16.23 с |
| Переключение тем в Decky | [02-appearance-controls.mp4](https://github.com/ivshalenko/codex-steamdeck/releases/download/v1.0.0-rc.8/02-appearance-controls.mp4) | 9.23 с |
| Настоящее уведомление при закрытой панели и переход в ответ | [03-real-background-notification.mp4](https://github.com/ivshalenko/codex-steamdeck/releases/download/v1.0.0-rc.8/03-real-background-notification.mp4) | 22.87 с |
| Продолжение чата с Mac; исполнение на Steam Deck | [04-mac-controls-deck.mp4](https://github.com/ivshalenko/codex-steamdeck/releases/download/v1.0.0-rc.8/04-mac-controls-deck.mp4) | 35.2 с |
| Настольный GTK: просмотр истории выполненной правки и теста | [05-real-bug-fix-history-gtk.mp4](https://github.com/ivshalenko/codex-steamdeck/releases/download/v1.0.0-rc.8/05-real-bug-fix-history-gtk.mp4) | 12.63 с |
| rc.7: живое выполнение нового демо-задания после включения экрана | [06-rc7-live-bug-fix.mp4](https://github.com/ivshalenko/codex-steamdeck/releases/download/v1.0.0-rc.8/06-rc7-live-bug-fix.mp4) | 80.27 с |
| rc.8: полный запрос, два подтверждения и настоящий результат | [08-rc8-live-confirmation.mp4](https://github.com/ivshalenko/codex-steamdeck/releases/download/v1.0.0-rc.8/08-rc8-live-confirmation.mp4) | 35.2 с |

События указателя и колёсика CDP проверены отдельно. В непрерывной записи 08 кнопки активированы обработчиками интерфейса; команда и результат Codex настоящие. Физические кнопки и тачскрин этим не проверены.

## Скриншоты

Путь в репозитории: `docs/media/screenshots/`. Ссылки ниже открывают исходные PNG.

- [01-bloodborne-request.png](media/screenshots/01-bloodborne-request.png) — Первый запрос Bloodborne и реальные ограничения в ответе.
- [02-bloodborne-error.png](media/screenshots/02-bloodborne-error.png) — Пользователь прислал ошибку запуска Bloodborne.
- [03-zelda-botw-request.png](media/screenshots/03-zelda-botw-request.png) — Историческая просьба настроить Zelda BOTW.
- [04-zelda-totk-request.png](media/screenshots/04-zelda-totk-request.png) — Историческая просьба настроить Zelda TOTK.
- [05-keyboard-error-request.png](media/screenshots/05-keyboard-error-request.png) — Исторический запрос об экранной клавиатуре.
- [06-empty-fullscreen.png](media/screenshots/06-empty-fullscreen.png) — Полноэкранный Decky: техническая проверка черновика.
- [07-appearance-settings.png](media/screenshots/07-appearance-settings.png) — Темы, плотность, компоновка и вид сообщений.
- [08-compact-panel.png](media/screenshots/08-compact-panel.png) — Компактная панель Decky.
- [09-installation-wizard.png](media/screenshots/09-installation-wizard.png) — Мастер установки на русском.
- [10-bloodborne-owned-files.png](media/screenshots/10-bloodborne-owned-files.png) — Уточнение о локальных файлах Bloodborne.
- [11-real-completion-notification.png](media/screenshots/11-real-completion-notification.png) — Настоящее уведомление Steam; исходный кадр системной записи.
- [12-notification-opens-result.png](media/screenshots/12-notification-opens-result.png) — Нажатие на уведомление открыло нужный результат.
- [14-mac-controls-deck-result.png](media/screenshots/14-mac-controls-deck-result.png) — Настоящая команда с Mac выполнена на Deck.
- [15-real-bug-fix-result.png](media/screenshots/15-real-bug-fix-result.png) — GTK: результат настоящего демонстрационного исправления.
- [16-real-failed-test-history.png](media/screenshots/16-real-failed-test-history.png) — GTK: история проверки демонстрационного проекта.
- [17-real-diff-history.png](media/screenshots/17-real-diff-history.png) — GTK: реальный diff и успешный тест.
- [18-rc7-bug-fix-request.png](media/screenshots/18-rc7-bug-fix-request.png) — rc.7: новый реальный запрос об исправлении демо-бага.
- [20-rc7-live-fix-result.png](media/screenshots/20-rc7-live-fix-result.png) — rc.7: результат нового исправления, diff и проверочный маркер.
- [25-rc8-visible-permission-buttons.png](media/screenshots/25-rc8-visible-permission-buttons.png) — rc.8: запрос и обе кнопки полностью в окне.
- [26-rc8-second-confirmation.png](media/screenshots/26-rc8-second-confirmation.png) — rc.8: отдельное второе подтверждение.
- [27-rc8-confirmed-result.png](media/screenshots/27-rc8-confirmed-result.png) — rc.8: настоящий результат разрешённой демо-команды.

## Как использовать материалы

Для демонстрации установки используйте скриншот 09, для уведомлений — видео 03 и скриншоты 11–12, для Mac → Deck — видео 04 и скриншот 14. Исправление на камеру — видео 06; подтверждение действия — видео 08 и скриншоты 25–27. Видео 05 показывает просмотр истории, а не новое выполнение.

Публичный пакет включает только перечисленные PNG/MP4, галерею и манифест. Локальная памятка SSH, исходный личный сценарий, внутренние журналы и материалы аккаунта в него не входят. Материалы проекта ivshalenko; при использовании сохраняйте ссылку на проект.
