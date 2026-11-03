# Claude Code: собственный доступ пользователя

Deck AI запускает установленный официальный Claude Code. Пароли, одноразовые коды, OAuth-токены и API-ключи Claude не вводятся в Deck AI и не сохраняются в его настройках. Для этой интеграции нужен Claude Code **2.1.259 или новее**: используется документированный режим отказа в запросах разрешения, на которые некому ответить.

## Настройка на Steam Deck

1. Перейдите в Desktop Mode и установите Claude Code по [официальной инструкции Anthropic](https://code.claude.com/docs/en/setup).
2. Откройте Deck AI → **+ → Подключить Claude Code**. Либо выберите Claude Code и нажмите **Настроить Claude Code** в меню модели.
3. Откроется **официальный терминальный интерфейс Claude Code**. Выберите доступ, который принадлежит вам: аккаунт Claude, Console/API или поддерживаемую облачную платформу. Для смены существующего входа используйте `/login` в самом Claude Code.
4. Для Anthropic Console есть отдельный путь: Deck AI → **+ → Войти через Anthropic Console (API)**. Он запускает `claude auth login --console`. API-расходы оплачиваются по выбранному доступу пользователя; бесплатность Deck AI не делает использование модели бесплатным.
5. После завершения входа вернитесь в Deck AI и отправьте короткий проверочный вопрос. Проверить доступ отдельно можно командой `claude auth status` — она сама выводит JSON; флаг `--json` не нужен.

В Gaming Mode настройки Decky напоминают этот путь. Подготовка доступа выполняется в Desktop Mode. Deck AI ищет CLI в `PATH` и стандартном каталоге нативной установки `~/.local/bin`.

## API-ключи и облачные платформы

Если вы уже настроили API-ключ, `apiKeyHelper`, Bedrock, Vertex, Foundry или другой доступ, поддерживаемый официальным CLI, Deck AI сохраняет его окружение и принимает готовность, сообщённую самим CLI. Принудительного переключения на Pro/Max нет. Настраивайте секреты средствами Claude Code/провайдера; не вставляйте их в чат или issue.

Учтите окружение рабочего стола: переменная, заданная только в одной вкладке Konsole, не появляется автоматически в уже запущенном приложении/Decky. Используйте предусмотренную вашим провайдером постоянную настройку и перезапускайте приложение после изменения окружения. Не копируйте учётные данные между чужими аккаунтами.

## Разрешения действий

Текстовый клиент использует стандартный режим разрешений Claude Code без автоматического `acceptEdits`. Запросы, требующие интерактивного подтверждения, отклоняются: Deck AI не изображает собственное подтверждение за Claude Code. Для таких действий откройте нативный Claude Code и подтвердите их там. Интерактивные подтверждения Codex в плагине работают отдельно.

## Условия и границы проверки

Официальный CLI остаётся немодифицированным. Способы авторизации не отключаются; аккаунт, API и биллинг принадлежат конечному пользователю. Deck AI не перепродаёт доступ и не выдаёт собственный вход Claude.ai. Это описание реализации, а не заявление об официальном одобрении Anthropic. Издателям и операторам нужно соблюдать применимые Commercial Terms и прочие условия Anthropic; прохождение входа не заменяет эти обязанности.

- [Legal and compliance](https://code.claude.com/docs/en/legal-and-compliance)
- [Authentication](https://code.claude.com/docs/en/authentication)
- [CLI reference](https://code.claude.com/docs/en/cli-reference)

Account/API/cloud-ветви проверяются как контракт CLI. Настоящий ответ модели и конкретная облачная платформа требуют соответствующего доступа пользователя; не отмечайте их проверенными только по unit-тестам.

## English

Install the unmodified official Claude Code 2.1.259+. In Desktop Mode open Deck AI → **+ → Connect Claude Code**, then complete Anthropic's own UI. Use `/login` to change access. **Sign in with Anthropic Console (API)** opens `claude auth login --console`. Your account, API/helper or supported cloud environment remains intact, with billing under your access. Deck AI does not collect Claude credentials. Check readiness with `claude auth status` (JSON by default). Tool actions requiring approval must be handled in the native CLI; the text client denies unanswered permission requests.
