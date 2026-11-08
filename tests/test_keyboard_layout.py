"""Gaming Mode layout ownership, rollback and restart detection."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import keyboard_layout as keyboard


class KeyboardLayoutTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.state = self.home/'state'
        self.original = {key: None for key in keyboard.ENVIRONMENT}
        self.support = patch.object(keyboard, 'supported', return_value=True)
        self.environment = patch.object(keyboard, 'running_environment', return_value=self.original)
        self.run = patch.object(keyboard.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0))
        for item in (self.support, self.environment, self.run):
            item.start(); self.addCleanup(item.stop)

    def test_enable_only_changes_owned_dropin_and_preference(self):
        desktop = self.home/'.config/kxkbrc'; desktop.parent.mkdir()
        desktop.write_text('Keep the desktop layouts')
        self.state.mkdir(); (self.state/'language').write_text('en')
        result = keyboard.configure(True, self.home, self.state)
        self.assertTrue(result['enabled']); self.assertTrue(result['restartRequired'])
        self.assertFalse(result['active'])
        self.assertEqual((self.home/keyboard.DROPIN).read_text(), keyboard.CONTENT)
        self.assertEqual(desktop.read_text(), 'Keep the desktop layouts')
        self.assertEqual((self.state/'language').read_text(), 'en')
        call = keyboard.subprocess.run.call_args
        self.assertEqual(call.args[0], ['systemctl', '--user', 'daemon-reload'])
        self.assertEqual(call.kwargs['stdin'], subprocess.DEVNULL)
        self.assertNotIn('restart', call.args[0])

    def test_running_session_must_actually_have_the_layout(self):
        keyboard.configure(True, self.home, self.state)
        with patch.object(keyboard, 'running_environment', return_value=keyboard.ENVIRONMENT):
            result = keyboard.status(self.home, self.state)
        self.assertTrue(result['active']); self.assertFalse(result['restartRequired'])

    def test_disable_restores_user_service_defaults_after_restart(self):
        keyboard.configure(True, self.home, self.state)
        with patch.object(keyboard, 'running_environment', return_value=keyboard.ENVIRONMENT):
            result = keyboard.configure(False, self.home, self.state)
        self.assertFalse((self.home/keyboard.DROPIN).exists())
        self.assertFalse(result['enabled']); self.assertTrue(result['restartRequired'])
        self.assertEqual(keyboard.read_state(self.state)['previousEnvironment'], self.original)

    def test_preexisting_custom_file_is_never_overwritten_or_deleted(self):
        target = self.home/keyboard.DROPIN; target.parent.mkdir(parents=True)
        target.write_text('[Service]\nEnvironment=XKB_DEFAULT_LAYOUT=fr\n')
        original = target.read_bytes()
        for enabled in (True, False):
            with self.assertRaisesRegex(ValueError, 'preserved'):
                keyboard.configure(enabled, self.home, self.state)
            self.assertEqual(target.read_bytes(), original)
        self.assertTrue(keyboard.status(self.home, self.state)['conflict'])
        keyboard.subprocess.run.assert_not_called()

    def test_failed_reload_rolls_back_the_dropin_and_keeps_preference(self):
        self.state.mkdir(); previous = {'enabled': False, 'custom': 'preserve'}
        (self.state/'hardware-keyboard.json').write_text(json.dumps(previous))
        with patch.object(keyboard.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, ['systemctl'])):
            with self.assertRaises(subprocess.CalledProcessError):
                keyboard.configure(True, self.home, self.state)
        self.assertFalse((self.home/keyboard.DROPIN).exists())
        self.assertEqual(keyboard.read_state(self.state), previous)

    def test_failed_disable_keeps_enabled_configuration(self):
        keyboard.configure(True, self.home, self.state)
        with patch.object(keyboard.subprocess, 'run', side_effect=OSError('unavailable')):
            with self.assertRaises(OSError): keyboard.configure(False, self.home, self.state)
        self.assertEqual((self.home/keyboard.DROPIN).read_text(), keyboard.CONTENT)
        self.assertTrue(keyboard.read_state(self.state)['enabled'])

    def test_unsupported_system_is_read_only(self):
        with patch.object(keyboard, 'supported', return_value=False):
            self.assertFalse(keyboard.status(self.home, self.state)['supported'])
            with self.assertRaises(ValueError): keyboard.configure(True, self.home, self.state)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_only_actual_booleans_are_accepted(self):
        for invalid in ('false', 'true', None, 0, 1, {}):
            with self.subTest(value=invalid), self.assertRaises(ValueError):
                keyboard.configure(invalid, self.home, self.state)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_symlink_to_another_file_is_not_followed(self):
        other = self.home/'do-not-change'; other.write_text('private')
        target = self.home/keyboard.DROPIN; target.parent.mkdir(parents=True)
        target.symlink_to(other)
        with self.assertRaises(ValueError): keyboard.configure(True, self.home, self.state)
        self.assertEqual(other.read_text(), 'private')

    def test_reenable_preserves_the_original_layout_for_restore(self):
        original = {**self.original, 'XKB_DEFAULT_LAYOUT': 'de'}
        with patch.object(keyboard, 'running_environment', return_value=original):
            keyboard.configure(True, self.home, self.state)
        with patch.object(keyboard, 'running_environment', return_value=keyboard.ENVIRONMENT):
            keyboard.configure(True, self.home, self.state)
        self.assertEqual(keyboard.read_state(self.state)['previousEnvironment'], original)

    def test_read_only_plugin_cannot_change_the_keyboard(self):
        from test_decky_bridge import bridge
        with patch.object(bridge, 'read_only', True), patch.object(bridge.keyboard_layout, 'configure') as apply:
            with self.assertRaises(ValueError): bridge.call('keyboard_configure', {'enabled': True})
        apply.assert_not_called()

    def test_toggle_off_on_before_restart_does_not_lose_the_restore_layout(self):
        original = {**self.original, 'XKB_DEFAULT_LAYOUT': 'de'}
        with patch.object(keyboard, 'running_environment', return_value=original):
            keyboard.configure(True, self.home, self.state)
        with patch.object(keyboard, 'running_environment', return_value=keyboard.ENVIRONMENT):
            keyboard.configure(False, self.home, self.state)
            keyboard.configure(True, self.home, self.state)
        self.assertEqual(keyboard.read_state(self.state)['previousEnvironment'], original)
