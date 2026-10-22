"""Steam lifecycle, shortcuts and send availability regressions."""
from types import SimpleNamespace
from unittest.mock import Mock
import unittest
from test_connection_recovery import method

class GamingModeTests(unittest.TestCase):
    def test_steam_window_stays_fullscreen(self):
        panel=SimpleNamespace(gaming_mode=True,window=Mock())
        method('position')(panel)
        panel.window.fullscreen.assert_called_once()
        panel.window.unmaximize.assert_not_called()

    def test_steam_close_exits_process(self):
        panel=SimpleNamespace(gaming_mode=True,shutdown_app=Mock())
        self.assertTrue(method('close')(panel))
        panel.shutdown_app.assert_called_once()

    def test_desktop_close_keeps_background_app(self):
        panel=SimpleNamespace(gaming_mode=False,stop_event=Mock(),recorder=None,window=Mock())
        self.assertTrue(method('close')(panel))
        panel.window.hide.assert_called_once()

    def test_control_enter_sends(self):
        panel=SimpleNamespace(send=Mock())
        gdk=SimpleNamespace(ModifierType=SimpleNamespace(CONTROL_MASK=4),keyval_name=lambda value:value)
        self.assertTrue(method('application_key_pressed',Gdk=gdk)(panel,None,SimpleNamespace(state=4,keyval='Return')))
        panel.send.assert_called_once()

    def test_plain_enter_keeps_multiline_input(self):
        panel=SimpleNamespace(send=Mock())
        gdk=SimpleNamespace(ModifierType=SimpleNamespace(CONTROL_MASK=4),keyval_name=lambda value:value)
        self.assertFalse(method('application_key_pressed',Gdk=gdk)(panel,None,SimpleNamespace(state=0,keyval='Return')))
        panel.send.assert_not_called()

    def test_working_label_is_app_name_for_every_provider(self):
        for provider in ('codex','claude','deepseek','tokenharbor'):
            with self.subTest(provider=provider):
                panel=SimpleNamespace(provider=provider,stop_button=Mock(),turn_id=None,spinner=Mock(),activity=Mock(),busy=False,message=Mock())
                method('set_working')(panel,True)
                panel.activity.set_text.assert_called_once_with('Deck AI работает…')

    def test_external_provider_send_does_not_require_codex(self):
        panel=SimpleNamespace(placeholder=Mock(),provider='claude',external_threads={'claude':{}},history_ready=False,backend=None,send_button=Mock(),busy=False,sending=False)
        method('draft_changed')(panel,SimpleNamespace(get_char_count=lambda:10))
        panel.send_button.set_sensitive.assert_called_with(True)

if __name__=='__main__':unittest.main()
