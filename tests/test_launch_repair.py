import concurrent.futures
import http.client
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlsplit


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "decky"))
from launch_repair import LaunchRepair, steam_ids
from repair_remote import RepairRemote


ACCOUNT = "76561197960265729"
ORIGIN = "https://deck.example.test:8443"
APP = {"appId": 42, "name": "Test game", "proton": "Proton Test", "shortcut": False, "options": "false %command%"}


class LaunchRepairTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.home = Path(temp.name)
        self.steam = self.home / "steam"
        self.write_allowed = True
        self.now = 100
        self.repair = self.open_journal()
        self.case_id = self.repair.inspect(ACCOUNT, APP, "")["case"]["id"]

    def open_journal(self):
        return LaunchRepair(self.home / "state", self.home, self.steam,
                            lambda: self.write_allowed, clock=lambda: self.now)

    def command(self, verb, **fields):
        return self.repair.command(ACCOUNT, self.case_id, verb, fields)

    def request(self, kind="reset"):
        return self.command("request", kind=kind)["action"]["id"]

    def test_apply_confirm_verify_result_and_restore(self):
        reset = self.request()
        with self.assertRaises(ValueError):
            self.command("claim", actionId=reset, options=APP["options"], shortcut=False)
        self.command("decide", actionId=reset, decision=True)
        self.assertEqual({"options": ""}, self.command("claim", actionId=reset, options=APP["options"], shortcut=False))
        self.assertEqual("running", self.command("observe", actionId=reset, options=APP["options"], shortcut=False)["action"]["state"])
        self.assertEqual("applied", self.command("observe", actionId=reset, options="", shortcut=False)["state"])
        self.assertEqual("started", self.command("result", result="started")["launchResult"])
        restore = self.request("restore")
        self.command("decide", actionId=restore, decision=True)
        self.assertEqual({"options": APP["options"]}, self.command("claim", actionId=restore, options="", shortcut=False))
        self.assertEqual("restored", self.command("observe", actionId=restore, options=APP["options"], shortcut=False)["state"])
        self.assertEqual(0o600, self.repair.path.stat().st_mode & 0o777)

    def test_stale_approval_and_concurrent_claim_cannot_reapply(self):
        previous = self.request()
        self.command("decide", actionId=previous, decision=False)
        current = self.request()
        with self.assertRaises(ValueError):
            self.command("decide", actionId=previous, decision=True)
        self.command("decide", actionId=current, decision=True)

        def claim():
            try:
                return self.command("claim", actionId=current, options=APP["options"], shortcut=False)
            except ValueError:
                return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            outcomes = list(pool.map(lambda _: claim(), range(8)))
        self.assertEqual(1, outcomes.count({"options": ""}))

    def test_restore_will_not_overwrite_a_new_manual_change(self):
        action = self.request()
        self.command("decide", actionId=action, decision=True)
        self.command("claim", actionId=action, options=APP["options"], shortcut=False)
        self.command("observe", actionId=action, options="", shortcut=False)
        restore = self.request("restore")
        self.command("decide", actionId=restore, decision=True)
        self.assertIsNone(self.command("claim", actionId=restore, options="PROTON_LOG=1 %command%", shortcut=False))
        self.assertEqual("conflict", self.repair.view(ACCOUNT)["state"])
        self.assertEqual(APP["options"], json.loads(self.repair.path.read_text())["original"])

    def test_recovery_rechecks_an_interrupted_change_without_new_write(self):
        pending = self.request()
        self.command("decide", actionId=pending, decision=True)
        self.repair = self.open_journal()
        self.assertIsNone(self.repair.view(ACCOUNT)["action"])
        running = self.request()
        self.command("decide", actionId=running, decision=True)
        self.command("claim", actionId=running, options=APP["options"], shortcut=False)
        self.repair = self.open_journal()
        self.assertEqual("running", self.repair.view(ACCOUNT)["action"]["state"])
        self.now += 21
        self.assertEqual("applied", self.command("observe", actionId=running, options="", shortcut=False)["state"])

    def test_read_only_and_account_scope_enforced_in_journal(self):
        action = self.request()
        self.command("decide", actionId=action, decision=True)
        self.write_allowed = False
        self.assertTrue(self.repair.view(ACCOUNT)["readOnly"])
        with self.assertRaises(ValueError):
            self.command("claim", actionId=action, options=APP["options"], shortcut=False)
        self.assertIsNone(self.repair.view("76561197960265730"))
        self.now += 46
        self.assertIsNone(self.repair.view(ACCOUNT)["action"])

    def test_only_matching_screenshots_and_redacted_log_signals(self):
        folder = self.steam / "1/760/remote/42/screenshots"
        folder.mkdir(parents=True)
        good = folder / "test.png"
        good.write_bytes(b"\x89PNG\r\n\x1a\n" + b"placeholder")
        outside = self.home / "other.png"
        outside.write_bytes(good.read_bytes())
        link = folder / "private.png"
        link.symlink_to(outside)
        fifo = folder / "pipe.png"
        os.mkfifo(fifo)
        for bad in (outside, link, fifo):
            with self.subTest(file=bad.name), self.assertRaises(ValueError):
                self.repair.inspect(ACCOUNT, APP, str(bad))
        (self.home / "steam-42.log").write_text("No space left on device\ncredential=local-fixture")
        result = self.repair.inspect(ACCOUNT, APP, str(good))
        self.assertTrue(result["preview"].startswith("data:image/png;base64,"))
        self.assertIn("В журнале есть ошибка нехватки места.", result["case"]["checks"])
        self.assertNotIn("local-fixture", json.dumps(result["case"]))
        self.assertNotIn(str(good), self.repair.path.read_text())

    def test_refresh_recognizes_shortcut_log_and_preserves_backup(self):
        shortcut = {**APP, "shortcut": True}
        self.case_id = self.repair.inspect(ACCOUNT, shortcut, "")["case"]["id"]
        reset = self.request()
        self.command("decide", actionId=reset, decision=True)
        self.command("claim", actionId=reset, options=APP["options"], shortcut=True)
        self.command("observe", actionId=reset, options="", shortcut=True)
        self.command("result", result="started")
        game_id = steam_ids(APP["appId"], True)[1]
        logs = self.steam.parent / "logs"
        logs.mkdir()
        (logs / "gameprocess_log.txt").write_text(
            f'[2026-11-04 02:27:33] AppID {game_id} adding PID 55 as a tracked process "private-path"\n'
            f"[2026-11-04 02:27:36] AppID {game_id} no longer tracking PID 55, exit code 0\n"
            "[2026-11-04 02:27:37] AppID 99 no longer tracking PID 66, exit code 12\n")
        result = self.command("recheck")
        self.assertIn("Steam зарегистрировал завершение процесса · 2026-11-04 02:27:36 · код 0.", result["checks"])
        self.assertNotIn("private-path", str(result))
        self.assertEqual("started", result["launchResult"])
        self.assertEqual("applied", result["state"])
        restore = self.request("restore")
        self.command("decide", actionId=restore, decision=True)
        self.assertEqual({"options": APP["options"]}, self.command("claim", actionId=restore, options="", shortcut=True))

    def test_real_http_pairing_scope_and_single_use_decision(self):
        remote = RepairRemote(self.repair, port=0, clock=lambda: self.now)
        url = remote.begin(ACCOUNT, self.case_id, ORIGIN)["url"]
        self.addCleanup(remote.stop, ACCOUNT)
        port = remote.server.server_port
        cookie = ""

        def request(path, data=None, origin=ORIGIN, host=urlsplit(ORIGIN).netloc):
            nonlocal cookie
            with_connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            try:
                body = json.dumps(data) if data is not None else None
                with_connection.request("POST" if body else "GET", path, body, {
                    "Host": host, "Origin": origin, "Content-Type": "application/json", "Cookie": cookie,
                })
                response = with_connection.getresponse()
                if response.getheader("Set-Cookie"):
                    header = response.getheader("Set-Cookie")
                    self.assertIn("Secure; HttpOnly; SameSite=Strict", header)
                    cookie = header.split(";", 1)[0]
                return response.status, json.loads(response.read())
            finally:
                with_connection.close()

        self.assertEqual(401, request("/api/status")[0])
        challenge = {"challenge": urlsplit(url).fragment}
        self.assertEqual(403, request("/api/pair", challenge, origin="https://untrusted.test")[0])
        self.assertEqual(403, request("/api/pair", challenge, host="untrusted.test")[0])
        code, pair = request("/api/pair", challenge)
        self.assertEqual(200, code)
        self.assertEqual(403, request("/api/pair", challenge)[0])
        action = self.request()
        decision = {"caseId": self.case_id, "actionId": action, "decision": True}
        self.assertEqual(403, request("/api/decision", decision)[0])
        remote.confirm(ACCOUNT, pair["code"])
        payload = request("/api/status")[1]
        self.assertNotIn("false %command%", json.dumps(payload))
        self.assertEqual(409, request("/api/decision", {**decision, "caseId": "other"})[0])
        self.assertEqual(200, request("/api/decision", decision)[0])
        self.assertEqual(409, request("/api/decision", decision)[0])
        self.now += 21
        self.assertEqual(503, request("/api/status")[0])
        remote.local_status("76561197960265730")
        self.assertEqual(401, request("/api/status")[0])
