"""Connection regressions, with real JSONL pipes and no account/network access."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch

import backend
from test_connection_recovery import method
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


class TransportTests(unittest.TestCase):
    def open_backend(self, *flags, event=None):
        fake = str(ROOT/'tests/fake_app_server.py')
        def command(host, *remote, **kwargs):
            if remote == ('pwd',):
                return [sys.executable, '-c', 'import os;print(os.getcwd())']
            if remote == (backend._REMOTE_SERVER,):
                return [sys.executable, '-u', fake, *flags]
            return [sys.executable, '-c', 'pass']
        patched = patch.object(backend, 'ssh_command', side_effect=command)
        patched.start(); self.addCleanup(patched.stop)
        client = backend.Backend(event or (lambda message: None), Mock(), 'desk')
        self.addCleanup(client.close)
        return client

    def test_remote_handshake_resume_and_round_trip(self):
        client = self.open_backend('--noise')
        client.connect()
        client.select_thread('t1')
        result = client.request('turn/start', {'threadId':'t1', 'input':[{'type':'text','text':'hello'}]})
        self.assertEqual(result['turn']['id'], 'turn1')
        client.close()
        self.assertFalse(client.connected)
        self.assertIsNotNone(client.process.poll())
        self.assertTrue(client.process.stdout.closed)

    def test_failed_initialize_cannot_leave_false_ready_state(self):
        client = self.open_backend('--reject-init')
        with self.assertRaisesRegex(backend.RpcError, 'initialization rejected'):
            client.connect()
        self.assertFalse(client.connected)
        self.assertIsNotNone(client.process.poll())
        self.assertEqual(client.pending, {})

    def test_callback_exception_does_not_break_responses(self):
        received = threading.Event()
        def event(message):
            received.set()
            raise ValueError('UI callback failed')
        client = self.open_backend(event=event)
        client.connect('t1')
        client.request('turn/start', {'threadId':'t1','input':[{'type':'text','text':'hello'}]})
        self.assertTrue(received.wait(2))
        self.assertIn('data', client.request('thread/list', {}))
        self.assertTrue(client.connected)

    def test_request_after_close_fails_immediately(self):
        client = self.open_backend()
        client.connect(); client.close()
        with self.assertRaisesRegex(backend.RpcError, 'Нет соединения'):
            client.request('thread/list', {})

    def test_local_cli_without_daemon_uses_stdio(self):
        client = self.open_backend()
        client.remote_host = ''
        start = client._start_process
        def fallback(command):
            self.assertEqual(command, [backend.CODEX, 'app-server', '--listen', 'stdio://'])
            start([sys.executable, '-u', str(ROOT/'tests/fake_app_server.py')])
        modules = {'websockets.sync.client': SimpleNamespace(unix_connect=Mock(side_effect=OSError('no socket')))}
        with patch.dict(sys.modules, modules), patch.object(backend.subprocess, 'run', side_effect=subprocess.CalledProcessError(2, 'daemon')), patch.object(client, '_start_process', side_effect=fallback):
            client.connect()
        self.assertTrue(client.connected)
        self.assertIn('data', client.request('thread/list', {}))

    def test_ssh_option_and_shell_injection_are_rejected(self):
        for host in ('-oProxyCommand=touch-x', '-V', 'desk;id', 'desk\nwhoami', ''):
            with self.subTest(host=host), self.assertRaises(ValueError):
                backend.ssh_command(host, 'pwd')
        args = backend.ssh_command('deck@steamdeck.local', 'pwd')
        self.assertEqual(args[-3:], ['--','deck@steamdeck.local','pwd'])


class RemoteLauncherTests(unittest.TestCase):
    def test_noninteractive_path_and_shared_daemon_with_legacy_fallback(self):
        for shared in (True,False):
            with self.subTest(shared=shared), tempfile.TemporaryDirectory() as directory:
                home=Path(directory);binary=home/'.local/bin/codex';binary.parent.mkdir(parents=True)
                binary.write_text('#!/bin/sh\n'
                    'if [ "$1 $2 $3" = "app-server proxy --help" ]; then exit '+('0' if shared else '2')+'; fi\n'
                    'if [ "$1 $2 $3" = "app-server daemon start" ]; then exit 0; fi\n'
                    'printf "%s\\n" "$*"\n')
                binary.chmod(0o755)
                result=subprocess.run(['/bin/sh','-c',backend._REMOTE_SERVER],capture_output=True,text=True,
                                      env={**os.environ,'HOME':str(home),'PATH':'/usr/bin:/bin'},timeout=5)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual(result.stdout.strip(),'app-server proxy' if shared else 'app-server --listen stdio://')


class DesktopDeliveryTests(unittest.TestCase):
    def test_existing_remote_chat_uses_resumed_rpc_connection(self):
        client = Mock(connected=True)
        client.select_thread.return_value = ({}, {'turns': []})
        panel = SimpleNamespace(backend=client, remote_host='desk', empty_threads={}, thread_activity={},
                                job_finished=Mock(), job_waiting=Mock(), is_thread_busy=lambda exc:False)
        glib = SimpleNamespace(idle_add=lambda fn,*args:fn(*args))
        job = {'id':'j','threadId':'t1','text':'hello'}
        method('deliver_job', GLib=glib)(panel, job)
        client.select_thread.assert_called_once_with('t1')
        client.queue_message.assert_not_called()
        self.assertEqual(client.request.call_args.args[0], 'turn/start')
        panel.job_finished.assert_called_once_with(job, None)


class SecretSymlinkTests(unittest.TestCase):
    def test_local_and_remote_file_reader_reject_secret_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory).resolve()
            (home/'.env').write_text('SECRET')
            (home/'innocent.txt').symlink_to(home/'.env')
            def command(host,*remote,**kwargs):return ['/bin/sh','-c',remote[0]]
            with patch.object(backend.Path,'home',return_value=home), patch.dict(os.environ,{'HOME':str(home)}), patch.object(backend,'ssh_command',side_effect=command):
                for host in ('','desk'):
                    with self.subTest(host=host), self.assertRaises(backend.RpcError):
                        backend.read_file(host, str(home/'innocent.txt'))


if __name__ == '__main__':
    unittest.main()
