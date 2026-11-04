# Help make Deck AI better

The most useful contribution is a reproducible report from a real Steam Deck, especially a clean installation or a physical-control check.

| You can help with | Include |
| --- | --- |
| [A bug report](https://github.com/ivshalenko/codex-steamdeck/issues/new?template=bug.yml) | Deck AI, SteamOS and Decky versions; what you expected; what happened; exact reproduction steps. |
| [A feature suggestion](https://github.com/ivshalenko/codex-steamdeck/issues/new?template=feature.yml) | The task you want to accomplish and where the current flow gets in the way. |
| A device check | Device/OS version, installation method, input method and the result. See [RELEASE-CHECKLIST.md](RELEASE-CHECKLIST.md). |
| Documentation or translation | Update the English [README](../README.md) and [Russian version](README.ru.md) when the shared instructions change. |

For code, open a focused pull request describing the problem, resulting behavior and verification. Run the checks that cover your change; before a runtime release run `python3 scripts/build-release.py` with the dependencies from the README installed. Do not claim device checks that were only simulated. Describe any AI assistance honestly.

Do not attach credentials, private keys, account files or private conversations. Crop or redact identifying details in a copy before sharing a screenshot. For vulnerabilities, follow [SECURITY.md](../SECURITY.md).

**По-русски:** можно писать issues и предложения на русском. Для ошибки укажите версии Deck AI, SteamOS и Decky, шаги воспроизведения и ожидаемый результат. Особенно полезны проверки на другом устройстве и настоящими кнопками. Не отправляйте пароли, ключи и личные диалоги.
