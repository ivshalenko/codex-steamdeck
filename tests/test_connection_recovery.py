"""Exercise recovery paths without requiring a GTK display or real login."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

SOURCE = Path(__file__).resolve().parents[1] / 'app.py'

def method(name, **scope):
    tree = ast.parse(SOURCE.read_text())
    panel = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Panel')
    node = next(n for n in panel.body if isinstance(n, ast.FunctionDef) and n.name == name)
    namespace = dict(scope)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), str(SOURCE), 'exec'), namespace)
    return namespace[name]

class RecoveryTests(unittest.TestCase):
    def test_empty_history_creates_chat(self):
        panel = SimpleNamespace(connecting=True, new_chat=Mock())
        self.assertFalse(method('load_history')(panel, {}, {}))
        self.assertFalse(panel.connecting)
        panel.new_chat.assert_called_once()

    def test_offline_login_does_not_need_backend(self):
        panel = SimpleNamespace(backend=None, launch_codex_login=Mock())
        method('begin_account_login')(panel)
        panel.launch_codex_login.assert_called_once()

    def test_automatic_terminal_only_once(self):
        panel = SimpleNamespace(recovery_terminal_opened=False, launch_codex_terminal=Mock(return_value=True))
        recover = method('open_recovery_terminal')
        recover(panel)
        recover(panel)
        panel.launch_codex_terminal.assert_called_once_with(False)

    def test_failed_terminal_can_retry(self):
        panel = SimpleNamespace(recovery_terminal_opened=False, launch_codex_terminal=Mock(return_value=False))
        method('open_recovery_terminal')(panel)
        self.assertFalse(panel.recovery_terminal_opened)

if __name__ == '__main__':unittest.main()
