"""An opt-in browser remote for one repair. HTTPS terminates at a private proxy."""
import hmac
import json
import re
import secrets
import threading
import time
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


PORT = 18754
WEB = Path(__file__).with_name("repair-web")
COOKIE = "__Host-deck-ai-repair"
FILES = {"/": ("index.html", "text/html; charset=utf-8"),
         "/app.js": ("app.js", "text/javascript; charset=utf-8"),
         "/style.css": ("style.css", "text/css; charset=utf-8")}


def https_origin(value):
    if not isinstance(value, str) or len(value) > 200:
        raise ValueError("Укажите HTTPS-адрес пульта.")
    try:
        url = urlsplit(value.strip())
        hostname, port = url.hostname, url.port
    except ValueError:
        raise ValueError("Проверьте HTTPS-адрес пульта.") from None
    if (url.scheme != "https" or not hostname or not re.fullmatch(r"[a-z0-9-]+(?:\.[a-z0-9-]+)+", hostname)
            or url.username is not None or url.password is not None or url.path not in ("", "/")
            or url.query or url.fragment or port == 0):
        raise ValueError("Нужен HTTPS-адрес с именем хоста, без пути и параметров.")
    return f"https://{hostname}" + (f":{port}" if port and port != 443 else "")


class RemoteError(ValueError):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, remote):
        self.remote = remote
        self.slots = threading.BoundedSemaphore(12)
        super().__init__(address, Handler)

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()


class RepairRemote:
    def __init__(self, repair, port=PORT, clock=time.monotonic):
        self.repair = repair
        self.port = port
        self.clock = clock
        self.lock = threading.RLock()
        self.server = None
        self.pair = None
        self.seen = ("", 0)

    def _expire(self):
        if self.pair and (self.pair["until"] <= self.clock() or self.pair["account"] != self.seen[0]):
            self.pair = None

    def local_status(self, account):
        with self.lock:
            self.seen = (account, self.clock())
            self._expire()
            if not self.pair:
                return {"state": "off"}
            if self.pair["authorized"]:
                return {"state": "connected"}
            if self.pair["session"]:
                return {"state": "pending", "code": self.pair["code"]}
            return {"state": "pairing", "url": self.pair["origin"] + "/#" + self.pair["challenge"]}

    def begin(self, account, case_id, address):
        origin = https_origin(address)
        with self.lock:
            if not self.repair.view(account, case_id):
                raise ValueError("Сначала проверьте выбранную игру.")
            if self.server is None:
                try:
                    self.server = LocalServer(("127.0.0.1", self.port), self)
                except OSError:
                    raise ValueError("Локальный порт пульта занят. Закройте прежнее подключение.") from None
                threading.Thread(target=self.server.serve_forever, daemon=True).start()
            self.pair = {"account": account, "case": case_id, "origin": origin,
                         "challenge": secrets.token_urlsafe(24), "until": self.clock() + 180,
                         "session": "", "authorized": False, "code": ""}
            return self.local_status(account)

    def confirm(self, account, code):
        with self.lock:
            self._expire()
            pair = self.pair
            if not pair or pair["account"] != account or not pair["session"] or pair["authorized"] or code != pair["code"]:
                raise ValueError("Запрос сопряжения изменился. Откройте новый QR.")
            pair["authorized"] = True
            pair["until"] = self.clock() + 8 * 3600
            return self.local_status(account)

    def stop(self, account):
        with self.lock:
            if self.pair and self.pair["account"] != account:
                raise ValueError("Откройте пульт под исходным аккаунтом Steam.")
            self.pair = None
            server, self.server = self.server, None
            if server:
                server.shutdown()
                server.server_close()
            return {"state": "off"}

    def request(self, path, host, origin, token, body):
        with self.lock:
            self._expire()
            pair = self.pair
            if not pair:
                raise RemoteError(401, "Откройте новый QR на Steam Deck.")
            authority = urlsplit(pair["origin"]).netloc
            local_host = f"127.0.0.1:{self.server.server_port}"
            if host not in (authority, local_host) or (body is not None and origin != pair["origin"]):
                raise RemoteError(403, "Адрес пульта изменился.")
            if self.clock() - self.seen[1] > 20:
                raise RemoteError(503, "Steam Deck сейчас недоступен.")
            if path == "/api/pair":
                challenge = body.get("challenge")
                if (pair["session"] or not isinstance(challenge, str) or not challenge.isascii()
                        or not hmac.compare_digest(challenge, pair["challenge"])):
                    raise RemoteError(403, "QR уже использован или истёк. Откройте новый QR на Deck.")
                pair["challenge"] = ""
                pair["session"] = secrets.token_urlsafe(32)
                pair["code"] = f"{secrets.randbelow(1_000_000):06d}"
                return {"state": "pending", "code": pair["code"]}, pair["session"]
            if not token or not token.isascii() or not hmac.compare_digest(token, pair["session"]):
                raise RemoteError(401, "Сопрягите браузер с Deck через QR.")
            if not pair["authorized"]:
                if path != "/api/status":
                    raise RemoteError(403, "Подтвердите код на Steam Deck.")
                return {"state": "pending", "code": pair["code"]}, ""
            case = self.repair.view(pair["account"], pair["case"])
            if not case:
                raise RemoteError(410, "Диагностика закрыта. Откройте новый QR на Deck.")
            if body is not None:
                if body.get("caseId") != case["id"]:
                    raise RemoteError(409, "Обновите статус диагностики.")
                verb = {"/api/decision": "decide", "/api/result": "result", "/api/note": "note"}[path]
                case = self.repair.command(pair["account"], case["id"], verb, body)
            return {"state": "connected", "case": case}, ""


class Handler(BaseHTTPRequestHandler):
    timeout = 4

    def log_message(self, *args):
        # Pairing secrets and user input stay out of server logs.
        pass

    def respond(self, status, body, mime, token=""):
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy",
                         "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; "
                         "frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        if token:
            self.send_header("Set-Cookie", f"{COOKIE}={token}; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=28800")
        self.end_headers()
        self.wfile.write(body)

    def api(self, body=None):
        try:
            cookies = SimpleCookie(self.headers.get("Cookie", ""))
            token = cookies[COOKIE].value if COOKIE in cookies else ""
            payload, session = self.server.remote.request(
                self.path, self.headers.get("Host"), self.headers.get("Origin"), token, body)
            status = 200
        except RemoteError as exc:
            status, payload, session = exc.status, {"error": str(exc)}, ""
        except ValueError as exc:
            status, payload, session = 409, {"error": str(exc)}, ""
        except Exception:
            status, payload, session = 500, {"error": "Пульт временно недоступен."}, ""
        self.respond(status, json.dumps(payload, ensure_ascii=False).encode(), "application/json; charset=utf-8", session)

    def do_GET(self):
        if self.path == "/api/status":
            self.api()
        elif self.path in FILES:
            filename, mime = FILES[self.path]
            self.respond(200, (WEB / filename).read_bytes(), mime)
        else:
            self.respond(404, b"Not found", "text/plain")

    def do_POST(self):
        if self.path not in ("/api/pair", "/api/decision", "/api/result", "/api/note"):
            self.respond(404, b"Not found", "text/plain")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 4096 or self.headers.get_content_type() != "application/json":
                raise ValueError()
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError()
        except (ValueError, OSError):
            self.respond(400, b"Invalid request", "text/plain")
            return
        self.api(body)
