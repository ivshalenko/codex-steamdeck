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
    def test_ssh_helpers_cannot_read_or_change_the_parent_control_pipe(self):
        # OpenSSH makes inherited stdin nonblocking and can read ahead. Model
        # both effects in a real subprocess while a JSONL control line waits.
        harness=r'''
import json,os,sys
from pathlib import Path
import backend
root=Path(sys.argv[1]);operation=sys.argv[2]
probe="import os;os.set_blocking(0,False);os.read(0,65536);print(os.getcwd())"
def command(host,*remote,**kwargs):
    if remote==(backend._REMOTE_SERVER,):return [sys.executable,'-u',str(root/'tests/fake_app_server.py')]
    return [sys.executable,'-c',probe]
backend.ssh_command=command
client=backend.Backend(lambda e:None,lambda:None,'desk')
if operation=='connect':client.connect();client.close()
elif operation=='queue':client.queue_message('chat','fixture')
elif operation=='cleanup':client.cleanup_uploads()
else:backend._remote_sh('desk','printf fixture','~')
print(json.dumps({'blocking':os.get_blocking(0),'control':sys.stdin.readline()}))
'''
        for operation in ('connect','queue','cleanup','files'):
            with self.subTest(operation=operation):
                result=subprocess.run([sys.executable,'-c',harness,str(ROOT),operation],
                    input='CONTROL_SENTINEL\n',capture_output=True,text=True,timeout=12,
                    env={**os.environ,'PYTHONPATH':str(ROOT)})
                self.assertEqual(result.returncode,0,result.stderr)
                import json
                self.assertEqual(json.loads(result.stdout),{'blocking':True,'control':'CONTROL_SENTINEL\n'})

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
        with patch.object(backend,'CODEX',sys.executable), patch.dict(sys.modules, modules), patch.object(backend.subprocess, 'run', side_effect=subprocess.CalledProcessError(2, 'daemon')), patch.object(client, '_start_process', side_effect=fallback):
            client.connect()
        self.assertTrue(client.connected)
        self.assertIn('data', client.request('thread/list', {}))

    def test_missing_cli_has_installation_guidance_without_starting_process(self):
        client=self.open_backend();client.remote_host=''
        with patch.object(backend,'CODEX','/definitely/missing/codex'),patch.object(client,'_start_process') as start:
            with self.assertRaisesRegex(backend.RpcError,'Install Deck AI'):client.connect()
            start.assert_not_called()

    def test_ssh_option_and_shell_injection_are_rejected(self):
        for host in ('-oProxyCommand=touch-x', '-V', 'desk;id', 'desk\nwhoami', ''):
            with self.subTest(host=host), self.assertRaises(ValueError):
                backend.ssh_command(host, 'pwd')
        args = backend.ssh_command('deck@steamdeck.local', 'pwd')
        self.assertEqual(args[-3:], ['--','deck@steamdeck.local','pwd'])


class RemoteLauncherTests(unittest.TestCase):
    def test_remote_bootstrap_probes_cannot_consume_the_first_rpc_frame(self):
        with tempfile.TemporaryDirectory() as directory:
            home=Path(directory);binary=home/'.local/bin/codex';binary.parent.mkdir(parents=True)
            binary.write_text('#!/bin/sh\nread -r ignored || true\nexit 0\n');binary.chmod(0o755)
            python=home/'.local/share/deck-ai/venv/bin/python';python.parent.mkdir(parents=True)
            python.write_text('#!/bin/sh\nif [ "$1" = "-c" ]; then read -r ignored || true; exit 0; fi\ncat\n');python.chmod(0o755)
            frame='{"id":1,"method":"initialize","params":{}}\n'
            result=subprocess.run(['/bin/sh','-c',backend._REMOTE_SERVER],input=frame,
                capture_output=True,text=True,timeout=5,env={**os.environ,'HOME':str(home),'PATH':'/usr/bin:/bin'})
            self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stdout,frame)

    def test_noninteractive_path_and_shared_daemon_with_legacy_fallback(self):
        for shared in (True,False):
            with self.subTest(shared=shared), tempfile.TemporaryDirectory() as directory:
                home=Path(directory);binary=home/'.local/bin/codex';binary.parent.mkdir(parents=True)
                binary.write_text('#!/bin/sh\n'
                    'if [ "$1 $2 $3" = "app-server proxy --help" ]; then exit '+('0' if shared else '2')+'; fi\n'
                    'if [ "$1 $2 $3" = "app-server daemon start" ]; then exit 0; fi\n'
                    'printf "%s\\n" "$*"\n')
                binary.chmod(0o755)
                python = home/'.local/share/deck-ai/venv/bin/python'
                python.parent.mkdir(parents=True)
                python.write_text('#!/bin/sh\nif [ "$2" = "from websockets.sync.client import unix_connect" ]; then exit 0; fi\nprintf "JSONL adapter\\n"\n')
                python.chmod(0o755)
                result=subprocess.run(['/bin/sh','-c',backend._REMOTE_SERVER],capture_output=True,text=True,
                                      env={**os.environ,'HOME':str(home),'PATH':'/usr/bin:/bin'},timeout=5)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual(result.stdout.strip(),'JSONL adapter' if shared else 'app-server --listen stdio://')

    def test_stdio_fallback_accepts_shell_function_codex(self):
        # The macOS app-bundle fallback defines codex as a shell function.
        wrapper = 'codex() { if [ "$1 $2 $3" = "app-server proxy --help" ]; then return 2; fi; printf "%s\\n" "$*"; }\n'
        result=subprocess.run(['/bin/sh','-c',wrapper+backend._REMOTE_SERVER],capture_output=True,text=True,timeout=5)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.strip(),'app-server --listen stdio://')

    def test_jsonl_adapter_round_trip_to_real_websocket_socket(self):
        import json
        from websockets.sync.server import unix_serve
        with tempfile.TemporaryDirectory(prefix='deck-ws-',dir='/tmp') as home:
            folder=Path(home)/'app-server-control';folder.mkdir()
            def echo(ws):
                for raw in ws:
                    message=json.loads(raw)
                    ws.send(json.dumps({'id':message['id'],'result':{'echo':message['params']}}))
            with unix_serve(echo,str(folder/'app-server-control.sock')) as server:
                worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
                # Keep stdin open until the reply arrives: EOF deliberately closes the adapter.
                process=subprocess.Popen([sys.executable,'-u','-c',backend._REMOTE_JSONL_PROXY],
                    stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,
                    env={**os.environ,'CODEX_HOME':home})
                try:
                    process.stdin.write('{"id":2,"method":"check","params":{"text":"Привет"}}\n');process.stdin.flush()
                    import select
                    self.assertTrue(select.select([process.stdout],[],[],5)[0])
                    self.assertEqual(json.loads(process.stdout.readline()),{'id':2,'result':{'echo':{'text':'Привет'}}})
                    process.stdin.close();process.wait(timeout=5)
                    self.assertEqual(process.returncode,0)
                finally:
                    if process.poll() is None:process.kill();process.wait(timeout=3)
                    process.stdout.close();process.stderr.close()
                server.shutdown();worker.join(timeout=3)


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
