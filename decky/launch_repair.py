"""Local Steam launch diagnostics and a journal for reversible launch-option changes."""
import base64
import json
import os
import re
import secrets
import shutil
import stat
import tempfile
import threading
import time
from pathlib import Path


STEAM_ID_BASE = 76561197960265728
LOG_SIGNALS = {
    b"no space left on device": "В журнале есть ошибка нехватки места.",
    b"permission denied": "В журнале есть ошибка доступа.",
    b"failed to initialize vulkan": "В журнале есть ошибка инициализации Vulkan.",
    b"could not load kernel32": "В журнале есть ошибка запуска Wine.",
}
STEAM_PROCESS = re.compile(
    rb"^\[([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\] "
    rb"AppID ([0-9]{1,20}) (adding|no longer tracking) PID [0-9]+"
    rb"(?:, exit code (-?[0-9]{1,12}))?(?: |$)"
)


def valid_account(account):
    return (isinstance(account, str) and re.fullmatch(r"[0-9]{17}", account)
            and 0 < int(account) - STEAM_ID_BASE <= 0xffffffff)


def clean_text(value, limit):
    if not isinstance(value, str):
        return ""
    return "".join(c if c.isprintable() else " " for c in value).strip()[:limit]


def read_regular(path, limit, *, tail=False):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
            raise ValueError("Ожидался обычный файл текущего пользователя.")
        if tail:
            stream.seek(max(0, info.st_size - limit))
        elif info.st_size > limit:
            raise ValueError("Скриншот превышает 4 МБ.")
        return stream.read(limit), info.st_mtime


def steam_ids(app_id, shortcut):
    # Steam identifies a non-Steam shortcut by both its 32-bit app ID and its
    # 64-bit game ID (type 2). Steam's process log uses the latter.
    if shortcut:
        return str(app_id), str((app_id << 32) | (2 << 24))
    return (str(app_id),)


def screenshot_dirs(steam, account, app_id, shortcut):
    base = steam / str(int(account) - STEAM_ID_BASE) / "760" / "remote"
    return [base / identifier / "screenshots" for identifier in steam_ids(app_id, shortcut)]


def steam_process_check(steam, app_id, shortcut):
    try:
        data, _ = read_regular(steam.parent / "logs" / "gameprocess_log.txt", 256 * 1024, tail=True)
    except (OSError, ValueError):
        return "Журнал процессов Steam недоступен."
    identifiers = {identifier.encode("ascii") for identifier in steam_ids(app_id, shortcut)}
    for line in reversed(data.splitlines()):
        event = STEAM_PROCESS.match(line)
        if not event or event[2] not in identifiers:
            continue
        timestamp = event[1].decode("ascii")
        if event[3] == b"adding":
            return f"Steam зарегистрировал процесс игры · {timestamp}."
        if event[4] is not None:
            code = event[4].decode("ascii")
            return f"Steam зарегистрировал завершение процесса · {timestamp} · код {code}."
        return f"Steam зарегистрировал завершение процесса · {timestamp}."
    return "В недавних событиях Steam процессы этой игры не найдены."


def collect_checks(home, steam, app_id, shortcut):
    checks = []
    try:
        gib = shutil.disk_usage(home).free / (1024 ** 3)
        checks.append(f"Свободно в домашнем разделе Steam Deck: {gib:.1f} ГБ.")
    except OSError:
        checks.append("Размер свободного места недоступен.")
    try:
        data, mtime = read_regular(home / f"steam-{app_id}.log", 128 * 1024, tail=True)
        age = max(0, int((time.time() - mtime) / 60))
        checks.append(f"Найден журнал Proton для игры. Возраст: {age} мин.")
        hits = [message for pattern, message in LOG_SIGNALS.items() if pattern in data.lower()]
        checks.extend(hits or ["В конце журнала не найдено известных ошибок из списка проверок."])
    except (OSError, ValueError):
        checks.append("Доступный журнал Proton для игры отсутствует.")
    checks.append(steam_process_check(steam, app_id, shortcut))
    return checks


def screenshot_preview(steam, account, app_id, shortcut, screenshot):
    path = Path(screenshot)
    directory = path.parent
    mime = {".jpg": "jpeg", ".jpeg": "jpeg", ".png": "png", ".webp": "webp"}.get(path.suffix.lower())
    if (not mime or directory not in screenshot_dirs(steam, account, app_id, shortcut)
            or path.resolve().parent != directory.resolve()
            or directory.resolve() != steam.resolve() / directory.relative_to(steam)):
        raise ValueError("Выберите скриншот этой игры из Steam.")
    try:
        data, _ = read_regular(path, 4_000_000)
    except OSError:
        raise ValueError("Скриншот Steam недоступен.") from None
    signature_ok = ((mime == "png" and data.startswith(b"\x89PNG\r\n\x1a\n"))
                    or (mime == "jpeg" and data.startswith(b"\xff\xd8\xff"))
                    or (mime == "webp" and data.startswith(b"RIFF") and data[8:12] == b"WEBP"))
    if not signature_ok:
        raise ValueError("Формат файла не совпадает с расширением скриншота.")
    return f"data:image/{mime};base64," + base64.b64encode(data).decode("ascii")


class LaunchRepair:
    def __init__(self, state, home, steam, can_write, clock=time.time):
        self.path = state / "launch-repair.json"
        self.home = home
        self.steam = steam
        self.can_write = can_write
        self.clock = clock
        self.lock = threading.RLock()
        self.case = None
        try:
            value = json.loads(self.path.read_text())
            if isinstance(value, dict) and value.get("schema") == 1:
                self.case = value
        except FileNotFoundError:
            pass
        # An interrupted write is reconciled from Steam. Old approvals cannot
        # cause a fresh write after the plugin has restarted.
        if self.case and self.case.get("action") and self.case["action"]["state"] != "running":
            self._update(action=None, detail="Срок предыдущего подтверждения истёк при перезапуске.")

    def _save(self, case):
        self.path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            try:
                json.dump(case, stream, ensure_ascii=False)
                stream.flush()
                os.fsync(stream.fileno())
                os.replace(temporary, self.path)
            finally:
                temporary.unlink(missing_ok=True)
        self.case = case

    def _update(self, **values):
        self._save({**self.case, **values})

    def _expire(self):
        action = self.case and self.case["action"]
        if action and action["state"] != "running" and action["until"] <= self.clock():
            self._update(action=None, detail="Подтверждение истекло. Запросите действие снова.")

    def _current(self, account, case_id):
        self._expire()
        if not self.case or self.case["account"] != account or self.case["id"] != case_id:
            raise ValueError("Диагностика устарела. Обновите экран.")
        return self.case

    def _public(self, case):
        keys = ("id", "appId", "name", "proton", "checks", "state", "detail", "launchResult", "note")
        result = {key: case[key] for key in keys}
        result["canReset"] = bool(case["original"].strip()) and case["state"] in ("inspected", "restored")
        result["action"] = ({key: case["action"][key] for key in ("id", "kind", "state")}
                            if case["action"] else None)
        result["readOnly"] = not self.can_write()
        return result

    def view(self, account, case_id=None):
        with self.lock:
            self._expire()
            case = self.case
            if not case or case["account"] != account or (case_id is not None and case["id"] != case_id):
                return None
            return self._public(case)

    def inspect(self, account, app, screenshot):
        if not valid_account(account) or not isinstance(app, dict):
            raise ValueError("Откройте библиотеку Steam под своим аккаунтом.")
        app_id, original = app.get("appId"), app.get("options")
        name, proton = clean_text(app.get("name"), 160), clean_text(app.get("proton"), 120)
        if (type(app_id) is not int or not 0 < app_id <= 0xffffffff or not name
                or not isinstance(original, str) or len(original) > 8192 or "\0" in original
                or type(app.get("shortcut")) is not bool or not isinstance(screenshot, str) or len(screenshot) > 4096):
            raise ValueError("Steam не предоставил данные о параметрах запуска игры.")
        checks = collect_checks(self.home, self.steam, app_id, app["shortcut"])
        preview = screenshot_preview(self.steam, account, app_id, app["shortcut"], screenshot) if screenshot else ""
        with self.lock:
            self._expire()
            if self.case and (self.case["action"] or self.case["state"] in ("applied", "conflict")):
                raise ValueError("Завершите предыдущую диагностику под тем же аккаунтом Steam.")
            self._save({
                "schema": 1, "id": secrets.token_hex(16), "account": account, "appId": app_id,
                "name": name, "proton": proton, "original": original, "shortcut": app["shortcut"],
                "checks": checks, "state": "inspected", "action": None, "detail": "",
                "launchResult": "", "note": "",
            })
            return {"case": self._public(self.case), "preview": preview}

    def command(self, account, case_id, verb, params):
        with self.lock:
            case = self._current(account, case_id)
            action = case["action"]
            if verb in ("request", "decide", "claim") and not self.can_write():
                raise ValueError("В Deck AI включён режим только чтения.")
            if verb == "request":
                kind = params.get("kind")
                allowed = ((kind == "reset" and case["state"] in ("inspected", "restored") and case["original"].strip())
                           or (kind == "restore" and case["state"] == "applied"))
                if action or not allowed:
                    raise ValueError("Действие сейчас недоступно.")
                self._update(action={"id": secrets.token_hex(16), "kind": kind, "state": "pending",
                                     "until": self.clock() + 180}, detail="")
            elif verb == "decide":
                decision = params.get("decision")
                if (not action or action["state"] != "pending" or params.get("actionId") != action["id"]
                        or type(decision) is not bool):
                    raise ValueError("Запрос подтверждения уже изменился.")
                self._update(action={**action, "state": "approved", "until": self.clock() + 45} if decision else None,
                             detail="" if decision else "Действие отклонено.")
            elif verb == "claim":
                if not action or action["state"] != "approved" or params.get("actionId") != action["id"]:
                    raise ValueError("Действие уже обработано или подтверждение истекло.")
                if params.get("shortcut") is not case["shortcut"]:
                    raise ValueError("Тип игры в Steam изменился.")
                expected = case["original"] if action["kind"] == "reset" else ""
                if params.get("options") != expected:
                    self._update(action=None, state="conflict", detail="Параметры изменились в Steam. Чужие изменения сохранены.")
                    return None
                self._update(action={**action, "state": "running", "until": self.clock() + 20})
                return {"options": "" if action["kind"] == "reset" else case["original"]}
            elif verb in ("observe", "abort"):
                if not action or action["state"] != "running" or params.get("actionId") != action["id"]:
                    raise ValueError("Действие уже обработано.")
                desired = "" if action["kind"] == "reset" else case["original"]
                previous = case["original"] if action["kind"] == "reset" else ""
                observed = params.get("options")
                if params.get("shortcut") is not case["shortcut"] or not isinstance(observed, str):
                    raise ValueError("Steam не подтвердил текущее значение.")
                if verb == "abort":
                    self._update(action=None, state="conflict",
                                 detail="Свойства игры изменились перед записью. Проверьте параметры в Steam.")
                elif observed == desired:
                    state = "applied" if action["kind"] == "reset" else "restored"
                    self._update(action=None, state=state, launchResult="", detail="Steam подтвердил значение параметров.")
                elif self.clock() >= action["until"]:
                    state = case["state"] if observed == previous else "conflict"
                    self._update(action=None, state=state, detail="Steam не подтвердил изменение. Проверьте свойства игры.")
            elif verb == "result":
                if action or case["state"] != "applied" or params.get("result") not in ("started", "failed"):
                    raise ValueError("Сначала дождитесь проверки сброса параметров.")
                self._update(launchResult=params["result"])
            elif verb == "recheck":
                checks = collect_checks(self.home, self.steam, case["appId"], case["shortcut"])
                self._update(checks=checks)
            elif verb == "note":
                note = clean_text(params.get("note"), 500)
                if not note:
                    raise ValueError("Введите короткое уточнение.")
                self._update(note=note)
            elif verb == "close":
                if action:
                    raise ValueError("Дождитесь завершения действия.")
                self._save(None)
                return None
            else:
                raise ValueError("Неизвестное действие диагностики.")
            return self._public(self.case)
