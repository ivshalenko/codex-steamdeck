"""SSH multiplexing, live thread status and prewarmed dictation worker."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import sys, tempfile, unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import backend
spec = importlib.util.spec_from_file_location('speech_tested', ROOT/'speech_accuracy.py')
speech = importlib.util.module_from_spec(spec); spec.loader.exec_module(speech)
bridge_spec = importlib.util.spec_from_file_location('bridge_speed_tested', ROOT/'decky/bridge.py')
bridge = importlib.util.module_from_spec(bridge_spec); bridge_spec.loader.exec_module(bridge)


class SshTests(unittest.TestCase):
    def test_connection_is_shared_and_kept_alive(self):
        with tempfile.TemporaryDirectory() as home, patch.object(backend.Path, 'home', return_value=Path(home)):
            (Path(home)/'.ssh').mkdir()
            args = backend.ssh_command('desk', 'pwd')
            self.assertEqual(args[-2:], ['desk', 'pwd'])
            joined = ' '.join(args)
            for expected in ('ControlMaster=auto', 'ControlPersist=600', 'ServerAliveInterval=15', 'BatchMode=yes'):
                self.assertIn(expected, joined)
            self.assertIn(str(Path(home)/'.ssh'/'deck-ai-%C'), joined)

    def test_without_ssh_directory_no_control_socket(self):
        with tempfile.TemporaryDirectory() as home, patch.object(backend.Path, 'home', return_value=Path(home)):
            self.assertNotIn('ControlMaster', ' '.join(backend.ssh_command('desk', 'pwd')))


class ThreadStatusTests(unittest.TestCase):
    def test_running_detection(self):
        self.assertTrue(bridge.thread_running({'status': {'type': 'active'}}))
        self.assertTrue(bridge.thread_running({'status': 'inProgress'}))
        self.assertFalse(bridge.thread_running({'status': {'type': 'idle'}}))
        self.assertFalse(bridge.thread_running({}))
        self.assertTrue(bridge.thread_running({}, selected=True, selected_active=True))

    def test_event_invalidates_history_cache(self):
        bridge.remote_host = ''; bridge.history_cache_times[('', 't1')] = 123.0
        bridge.event({'method': 'item/agentMessage/delta', 'params': {'threadId': 't1'}})
        self.assertEqual(bridge.history_cache_times[('', 't1')], 0)


class PrewarmTests(unittest.TestCase):
    def worker(self, returncode=0, output='{"text":"Готово."}'):
        w = MagicMock(); w.communicate.return_value = (output, ''); w.returncode = returncode; w.poll.return_value = 0
        return w

    def model_dir(self, directory):
        model = Path(directory)/'models/faster-whisper-small'; model.mkdir(parents=True); (model/'model.bin').touch()

    def test_prewarmed_worker_gets_wav_path_and_result_used(self):
        with tempfile.TemporaryDirectory() as directory:
            self.model_dir(directory); w = self.worker()
            with patch.object(speech.subprocess, 'run') as run:
                self.assertEqual(speech.refine_dictation(b'\0\0'*100, 'ru', 'черновик', directory, w), 'Готово.')
                run.assert_not_called()
            self.assertTrue(w.communicate.call_args.kwargs['input'].endswith('.wav\n'))

    def test_worker_failure_keeps_draft(self):
        with tempfile.TemporaryDirectory() as directory:
            self.model_dir(directory)
            self.assertEqual(speech.refine_dictation(b'\0\0'*100, 'ru', 'черновик', directory, self.worker(1, '')), 'черновик')

    def test_unused_worker_is_released(self):
        w = MagicMock(); w.poll.return_value = None
        self.assertEqual(speech.refine_dictation(b'', 'ru', 'x', '/nonexistent', w), 'x')
        w.terminate.assert_called_once()

    def test_no_prewarm_for_fast_or_missing_model(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertIsNone(speech.prewarm_worker('ru-fast', directory))
            self.assertIsNone(speech.prewarm_worker('ru', directory))


if __name__ == '__main__':
    unittest.main()


class RemoteUploadTests(unittest.TestCase):
    def test_upload_returns_remote_path_and_rejects_non_images(self):
        b = backend.Backend(lambda m: None, lambda: None, 'desk')
        with tempfile.TemporaryDirectory() as d:
            image = Path(d)/'shot.png'; image.write_bytes(b'png')
            done = SimpleNamespace(returncode=0, stdout=b'/home/u/.cache/deck-ai-uploads/x.png', stderr=b'')
            with patch.object(backend.subprocess, 'run', return_value=done) as run:
                self.assertEqual(b.upload_file(str(image)), '/home/u/.cache/deck-ai-uploads/x.png')
                self.assertIn('desk', run.call_args.args[0])
            with self.assertRaises(backend.RpcError):
                b.upload_file(str(Path(d)/'notes.txt'))
            failed = SimpleNamespace(returncode=1, stdout=b'', stderr=b'denied')
            with patch.object(backend.subprocess, 'run', return_value=failed), self.assertRaisesRegex(backend.RpcError, 'denied'):
                b.upload_file(str(image))


class RemoteDispatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.saved = (bridge.bridge, bridge.remote_host, bridge.outbox, bridge.STATE, bridge.thread_id)
        bridge.STATE = Path(self.tmp.name); bridge.remote_host = 'desk'; bridge.thread_id = 't1'
        self.fake = MagicMock(); self.fake.connected = True
        bridge.bridge = self.fake
        self.job = {'id': 'j1', 'threadId': 't1', 'host': 'desk', 'text': 'привет', 'images': [], 'status': 'sending'}
        bridge.outbox = [self.job]

    def tearDown(self):
        bridge.bridge, bridge.remote_host, bridge.outbox, bridge.STATE, bridge.thread_id = self.saved
        self.tmp.cleanup()

    def calls(self):
        return [c.args[0] for c in self.fake.request.call_args_list]

    def test_text_goes_through_open_connection(self):
        self.fake.request.side_effect = lambda m, p, timeout=0: {'turn': {'id': 'turn9'}} if m == 'turn/start' else (
            {'thread': {'turns': []}} if m == 'thread/read' else {})
        bridge.dispatch_job(self.job)
        self.assertIn('turn/start', self.calls())
        self.fake.queue_message.assert_not_called()
        self.assertEqual((self.job['status'], self.job['turnId']), ('sending', 'turn9'))

    def test_dispatch_rejects_job_from_another_device(self):
        self.job['host']='other'
        bridge.dispatch_job(self.job)
        self.assertEqual(self.job['status'],'error')
        self.fake.request.assert_not_called()

    def test_dispatch_keeps_original_client_during_device_change(self):
        replacement=MagicMock(connected=True)
        def request(method, params, timeout=0):
            if method=='thread/resume':
                bridge.bridge=replacement;bridge.remote_host='other'
            return {'turn':{'id':'turn9'}} if method=='turn/start' else {'thread':{'turns':[]}}
        self.fake.request.side_effect=request
        bridge.dispatch_job(self.job)
        replacement.request.assert_not_called()
        self.assertIn('turn/start',self.calls())
        self.assertEqual(self.job['turnId'],'turn9')

    def test_resume_failure_keeps_error_without_sending_elsewhere(self):
        def request(method, params, timeout=0):
            if method == 'thread/resume':
                raise RuntimeError('boom')
            return {'thread': {'turns': []}}
        self.fake.request.side_effect = request
        bridge.dispatch_job(self.job)
        self.fake.queue_message.assert_not_called()
        self.assertEqual(self.job['status'], 'error')
        self.assertNotIn('turn/start', self.calls())

    def test_image_is_uploaded_and_sent_with_remote_path(self):
        shot = Path(self.tmp.name)/'game-frames'; shot.mkdir(); image = shot/'a.png'; image.write_bytes(b'x')
        self.job['images'] = [str(image)]
        self.fake.upload_file.return_value = '/home/u/.cache/deck-ai-uploads/a.png'
        sent = {}
        def request(method, params, timeout=0):
            if method == 'turn/start':
                sent.update(params); return {'turn': {'id': 'turn1'}}
            return {'thread': {'turns': []}}
        self.fake.request.side_effect = request
        bridge.dispatch_job(self.job)
        self.assertEqual(sent['input'][1], {'type': 'localImage', 'path': '/home/u/.cache/deck-ai-uploads/a.png'})


class NotificationTests(unittest.TestCase):
    def setUp(self):
        bridge.notifications.clear(); bridge.approvals.clear(); bridge.remote_host = ''; bridge.cache = [{'id': 't1', 'name': 'Сборка'}]

    def test_completion_and_failure_notifications(self):
        bridge.event({'method': 'turn/completed', 'params': {'threadId': 't1', 'turn': {'id': 'a', 'status': 'completed'}}})
        bridge.event({'method': 'turn/completed', 'params': {'threadId': 't1', 'turn': {'id': 'b', 'status': 'failed'}}})
        kinds = [n['kind'] for n in bridge.notifications]
        self.assertEqual(kinds, ['done', 'failed'])
        self.assertEqual(bridge.notifications[0]['title'], 'Сборка')

    def test_poll_returns_only_new_items_and_first_call_skips_backlog(self):
        bridge.event({'method': 'turn/completed', 'params': {'threadId': 't1', 'turn': {'id': 'a'}}})
        first = bridge.poll_events(None)
        self.assertEqual(first['notifications'], [])
        bridge.event({'method': 'turn/completed', 'params': {'threadId': 't1', 'turn': {'id': 'b'}}})
        later = bridge.poll_events(first['latest'])
        self.assertEqual(len(later['notifications']), 1)

    def test_approval_request_is_stored_and_answered(self):
        bridge.event({'id': 77, 'method': 'item/commandExecution/requestApproval', 'params': {'threadId': 't1', 'command': 'rm x'}})
        self.assertEqual(bridge.approvals['77']['summary'], 'rm x')
        fake = MagicMock(); fake.connected = True; saved = bridge.bridge; bridge.bridge = fake
        try:
            bridge.decide_approval(77, 'accept')
            fake.respond.assert_called_once_with(77, {'decision': 'accept'})
            self.assertNotIn('77', bridge.approvals)
            with self.assertRaises(ValueError):
                bridge.decide_approval(77, 'accept')
        finally:
            bridge.bridge = saved

    def test_tool_summaries_and_all_tasks(self):
        text = bridge.tool_text({'type': 'commandExecution', 'command': 'pytest', 'exitCode': 1, 'aggregatedOutput': 'FAILED'})
        self.assertIn('[код 1]', text); self.assertIn('FAILED', text)
        change = bridge.tool_text({'type': 'fileChange', 'changes': [{'path': 'a.py', 'diff': '+x'}]})
        self.assertIn('a.py', change); self.assertIn('+x', change)
        bridge.thread_caches = {'desk': [{'id': 'r1', 'name': 'Удалённая', 'status': {'type': 'active'}, 'updatedAt': 3}]}
        tasks = bridge.all_tasks()
        self.assertTrue(tasks[0]['running']); self.assertEqual(tasks[0]['host'], 'desk')
        bridge.thread_caches = {}


class SpeechOptionTests(unittest.TestCase):
    def test_model_size_and_vocabulary(self):
        with tempfile.TemporaryDirectory() as directory:
            models = Path(directory)/'models'; (models/'faster-whisper-base').mkdir(parents=True); (models/'faster-whisper-base'/'model.bin').touch()
            self.assertTrue(str(speech.whisper_dir(directory)).endswith('faster-whisper-small'))
            (models/'whisper-size').write_text('base\n')
            self.assertTrue(str(speech.whisper_dir(directory)).endswith('faster-whisper-base'))
            (models/'whisper-size').write_text('../evil\n')
            self.assertTrue(str(speech.whisper_dir(directory)).endswith('faster-whisper-small'))
            with patch.object(speech.Path, 'home', return_value=Path(directory)):
                (Path(directory)/'.config/deck-ai').mkdir(parents=True)
                (Path(directory)/'.config/deck-ai/vocabulary.txt').write_text('# моё\nKubernetes\n')
                self.assertIn('Kubernetes', speech.vocabulary_prompt())

    def test_timing_log_written_for_changed_text(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory)/'models/faster-whisper-small').mkdir(parents=True); (Path(directory)/'models/faster-whisper-small/model.bin').touch()
            w = MagicMock(); w.communicate.return_value = ('{"text":"Новый."}', ''); w.returncode = 0
            speech.refine_dictation(b'\0\0'*50, 'ru', 'старый', directory, w)
            self.assertIn('refineSeconds', (Path(directory)/'models/speech-timing.jsonl').read_text())


class ProtocolIntegrationTests(unittest.TestCase):
    """Real Backend + bridge code against the protocol stand-in server."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        fake = str(Path(__file__).with_name('fake_app_server.py'))
        def command(host, *remote, connect_timeout=8):
            if remote == ('pwd',):
                return ['pwd']
            if remote and remote[0] == backend._REMOTE_SERVER:
                return [sys.executable, '-u', fake]
            return ['true']
        self.patch = patch.object(backend, 'ssh_command', side_effect=command); self.patch.start()
        self.saved = (bridge.bridge, bridge.remote_host, bridge.outbox, bridge.STATE, bridge.thread_id, bridge.active)
        bridge.STATE = Path(self.tmp.name); bridge.remote_host = 'desk'; bridge.thread_id = 't1'; bridge.active = False
        bridge.notifications.clear(); bridge.approvals.clear()
        self.backend = backend.Backend(bridge.event, lambda: None, 'desk'); self.backend.connect(None)
        bridge.bridge = self.backend

    def tearDown(self):
        import shutil, time
        self.backend.close(); time.sleep(0.2)  # let the reader thread finish
        self.patch.stop()
        bridge.bridge, bridge.remote_host, bridge.outbox, bridge.STATE, bridge.thread_id, bridge.active = self.saved
        shutil.rmtree(self.tmp.name, ignore_errors=True)

    def wait(self, condition, seconds=5):
        import time
        end = time.time() + seconds
        while time.time() < end:
            if condition():
                return True
            time.sleep(0.05)
        return False

    def test_remote_send_completes_and_notifies(self):
        job = {'id': 'j1', 'threadId': 't1', 'host': 'desk', 'text': 'привет', 'images': [], 'status': 'sending'}
        bridge.outbox = [job]
        with patch.object(bridge, 'dispatch'):
            bridge.dispatch_job(job)
            self.assertTrue(self.wait(lambda: not bridge.outbox), 'turn/completed should clear the job')
        self.assertTrue(self.wait(lambda: any(n['kind'] == 'done' for n in bridge.notifications)))

    def test_approval_round_trip(self):
        job = {'id': 'j2', 'threadId': 't1', 'host': 'desk', 'text': 'please approve', 'images': [], 'status': 'sending'}
        bridge.outbox = [job]
        with patch.object(bridge, 'dispatch'):
            bridge.dispatch_job(job)
            self.assertTrue(self.wait(lambda: bridge.approvals), 'approval request should arrive')
            bridge.decide_approval('desk|srv1', 'accept')
            self.assertTrue(self.wait(lambda: not bridge.outbox), 'job should finish after approval')


import json, os, subprocess, importlib.util as _u
_bspec = _u.spec_from_file_location('backup_state_tested', ROOT/'scripts/backup-state.py')
backup_state = _u.module_from_spec(_bspec); _bspec.loader.exec_module(backup_state)


class DeviceFilesTests(unittest.TestCase):
    """The same shell scripts used over SSH are run locally here against a temporary HOME."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.home = Path(self.tmp.name).resolve()
        (self.home/'proj').mkdir(); (self.home/'proj/a.txt').write_text('привет\n')
        (self.home/'.ssh').mkdir(); (self.home/'.ssh/id_rsa').write_text('SECRET')
        def local_ssh(host, *remote, connect_timeout=8):
            return ['/bin/sh', '-c', remote[0]]
        self.patches = [patch.object(backend, 'ssh_command', side_effect=local_ssh),
                        patch.dict(os.environ, {'HOME': str(self.home)}),
                        patch.object(backend.Path, 'home', return_value=self.home)]
        for p in self.patches: p.start()

    def tearDown(self):
        for p in self.patches: p.stop()
        self.tmp.cleanup()

    def both(self, fn):
        """Run the operation on the remote (shell) and the local (pathlib) implementation."""
        return fn('desk'), fn('')

    def test_list_and_read(self):
        for host in ('desk', ''):
            folder, names = backend.list_files(host, '~')
            self.assertEqual(Path(folder), self.home); self.assertIn('proj/', names)
            self.assertEqual(backend.read_file(host, str(self.home/'proj/a.txt')), 'привет\n')

    def test_secrets_and_outside_home_are_blocked(self):
        for host in ('desk', ''):
            for path in (str(self.home/'.ssh/id_rsa'), '/etc/passwd', str(self.home/'.env'), str(self.home/'proj/../../etc/passwd')):
                with self.assertRaises(backend.RpcError, msg=(host, path)):
                    backend.read_file(host, path)
            with self.assertRaises(backend.RpcError):
                backend.list_files(host, str(self.home/'.ssh'))

    def test_write_requires_matching_hash_and_keeps_backup(self):
        import hashlib
        path = str(self.home/'proj/a.txt')
        for host in ('desk', ''):
            (self.home/'proj/a.txt').write_text('v1')
            good = hashlib.sha256(b'v1').hexdigest()
            with self.assertRaisesRegex(backend.RpcError, 'изменился'):
                backend.write_file(host, path, 'v2', 'wrong')
            backend.write_file(host, path, 'v2', good)
            self.assertEqual((self.home/'proj/a.txt').read_text(), 'v2')
            self.assertEqual((self.home/'proj/a.txt.deckai.bak').read_text(), 'v1')

    def test_binary_and_large_files_rejected(self):
        (self.home/'bin.dat').write_bytes(b'\0\1\2'); (self.home/'big.txt').write_text('x'*70000)
        for host in ('desk', ''):
            with self.assertRaises(backend.RpcError):
                backend.read_file(host, str(self.home/'bin.dat'))
            with self.assertRaises(backend.RpcError):
                backend.read_file(host, str(self.home/'big.txt'))

    def test_writes_preserve_mode_unicode_and_crlf(self):
        import hashlib, stat
        path = self.home/'proj'/r'скрипт с пробелами\версия.sh'
        for host in ('desk', ''):
            path.write_bytes(b'first\r\n');path.chmod(0o750)
            backend.write_file(host,str(path),'вторая\r\n',hashlib.sha256(b'first\r\n').hexdigest())
            self.assertEqual(path.read_bytes(),'вторая\r\n'.encode())
            self.assertEqual(stat.S_IMODE(path.stat().st_mode),0o750)
            self.assertEqual(Path(str(path)+'.deckai.bak').read_bytes(),b'first\r\n')

    def test_backup_and_legacy_temp_links_do_not_modify_another_file(self):
        import hashlib
        path = self.home/'proj/a.txt';other=self.home/'.env'
        other.write_text('fixture secret')
        good=hashlib.sha256(path.read_bytes()).hexdigest()
        for host in ('desk',''):
            backup=Path(str(path)+'.deckai.bak');backup.symlink_to(other)
            with self.assertRaises(backend.RpcError):backend.write_file(host,str(path),'new',good)
            self.assertEqual(other.read_text(),'fixture secret');backup.unlink()
            legacy=Path(str(path)+'.deckai.tmp');legacy.symlink_to(other)
            backend.write_file(host,str(path),'new',good)
            self.assertEqual(other.read_text(),'fixture secret');self.assertTrue(legacy.is_symlink())
            legacy.unlink();Path(str(path)+'.deckai.bak').unlink()
            path.write_text('привет\n')

    def test_local_and_remote_writers_respect_the_same_lock(self):
        import fcntl,hashlib
        path=self.home/'proj/a.txt';good=hashlib.sha256(path.read_bytes()).hexdigest()
        lock_path=path.with_name('.'+path.name+'.deckai.lock')
        with lock_path.open('w') as locked:
            fcntl.flock(locked,fcntl.LOCK_EX)
            for host in ('desk',''):
                with self.assertRaisesRegex(backend.RpcError,'сохраняется'):
                    backend.write_file(host,str(path),'new',good)
        backend.write_file('desk',str(path),'new',good)
        with self.assertRaisesRegex(backend.RpcError,'изменился'):
            backend.write_file('',str(path),'stale',good)
        self.assertEqual(path.read_text(),'new')

    def test_remote_save_rechecks_after_upload_before_replacing_the_file(self):
        import hashlib,time
        path=self.home/'proj/a.txt';good=hashlib.sha256(path.read_bytes()).hexdigest()
        uploaded=hashlib.sha256(b'new').hexdigest()
        process=subprocess.Popen(['/bin/sh','-c',backend._SH_WRITE,'sh',str(path),good,uploaded],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            process.stdin.write(b'new');process.stdin.flush()
            deadline=time.monotonic()+3
            while time.monotonic()<deadline:
                if any(file.read_bytes()==b'new' for file in path.parent.glob('.deckai-write.*')):break
                time.sleep(.01)
            else:self.fail('The staged upload did not start')
            path.write_text('manual edit')
            process.stdin.close();process.stdin=None
            process.communicate(timeout=5)
            self.assertEqual(process.returncode,8)
            self.assertEqual(path.read_text(),'manual edit')
            self.assertFalse(Path(str(path)+'.deckai.bak').exists())
            self.assertEqual(list(path.parent.glob('.deckai-*')),[])
        finally:
            if process.poll() is None:process.kill();process.communicate()

    def test_incomplete_remote_upload_keeps_the_original_and_backup(self):
        import hashlib
        path=self.home/'proj/a.txt';original=path.read_bytes()
        expected=hashlib.sha256(original).hexdigest()
        uploaded=hashlib.sha256(b'complete payload').hexdigest()
        result=subprocess.run(['/bin/sh','-c',backend._SH_WRITE,'sh',str(path),expected,uploaded],input=b'incomplete',capture_output=True,timeout=5)
        self.assertEqual(result.returncode,9)
        self.assertEqual(path.read_bytes(),original)
        self.assertFalse(Path(str(path)+'.deckai.bak').exists())
        self.assertEqual(list(path.parent.glob('.deckai-*')),[])


class WatchAndModeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.saved = (bridge.STATE, bridge.read_only, bridge.outbox, bridge.remote_host)
        bridge.STATE = Path(self.tmp.name); bridge.remote_host = ''; bridge.approvals.clear(); bridge.notifications.clear()

    def tearDown(self):
        bridge.STATE, bridge.read_only, bridge.outbox, bridge.remote_host = self.saved; self.tmp.cleanup()

    def test_watched_host_events_are_tagged_with_that_host(self):
        handler = bridge.watch_event('laptop')
        handler({'id': 'x1', 'method': 'item/fileChange/requestApproval', 'params': {'threadId': 'r1', 'reason': 'edit'}})
        handler({'method': 'turn/completed', 'params': {'threadId': 'r1', 'turn': {'status': 'completed'}}})
        self.assertIn('laptop|x1', bridge.approvals)
        self.assertEqual({n['host'] for n in bridge.notifications}, {'laptop'})
        fake = MagicMock(); fake.connected = True; bridge.watch_backends['laptop'] = fake
        bridge.decide_approval('laptop|x1', 'decline')
        fake.respond.assert_called_once_with('x1', {'decision': 'decline'})
        bridge.watch_backends.clear()

    def test_history_survives_restart(self):
        bridge.event({'method': 'turn/completed', 'params': {'threadId': 't', 'turn': {'id': 'a'}}})
        bridge.notifications.clear(); bridge.load_state()
        self.assertEqual(len(bridge.notifications), 1)

    def test_read_only_blocks_writes_but_not_reading(self):
        bridge.set_read_only(True)
        for method in ('send', 'approve', 'stop', 'file_write', 'queue_remove'):
            with self.assertRaisesRegex(ValueError, 'только чтения'):
                bridge.call(method, {})
        self.assertTrue((bridge.STATE/'read-only').exists())
        bridge.set_read_only(False)
        self.assertFalse((bridge.STATE/'read-only').exists())

    def test_queue_front_and_remove(self):
        bridge.outbox = [{'id': 'a', 'status': 'queued'}, {'id': 'b', 'status': 'queued'}, {'id': 'c', 'status': 'sending'}]
        bridge.queue_front('b'); self.assertEqual([j['id'] for j in bridge.outbox], ['b', 'a', 'c'])
        with self.assertRaises(ValueError): bridge.queue_remove('c')
        with self.assertRaises(ValueError): bridge.queue_front('c')
        bridge.queue_remove('a'); self.assertEqual([j['id'] for j in bridge.outbox], ['b', 'c'])


class CorrectionAndBackupTests(unittest.TestCase):
    def test_spoken_words_replaced_whole_word_only(self):
        with tempfile.TemporaryDirectory() as d, patch.object(speech.Path, 'home', return_value=Path(d)):
            (Path(d)/'.config/deck-ai').mkdir(parents=True)
            (Path(d)/'.config/deck-ai/vocabulary.txt').write_text('кубернетис => Kubernetes\nдекки => Decky\n')
            self.assertEqual(speech.apply_corrections('Запусти Кубернетис и декки лоадер'), 'Запусти Kubernetes и Decky лоадер')
            self.assertEqual(speech.apply_corrections('подекки'), 'подекки')
            self.assertIn('Kubernetes', speech.vocabulary_prompt())

    def test_backup_skips_big_dirs_and_rotates(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d); (state/'game-frames').mkdir(); (state/'game-frames/x.jpg').write_text('x'); (state/'thread-id').write_text('t1')
            for n in range(7): backup_state.backup(state, stamp=f'2026010{n}-000000')
            archives = sorted((state/'backups').glob('state-*.tar.gz'))
            self.assertEqual(len(archives), 5)
            import tarfile
            with tarfile.open(archives[-1]) as tar:
                self.assertEqual(tar.getnames(), ['thread-id'])


import deck_share
_rspec = _u.spec_from_file_location('deck_remote_tested', ROOT/'scripts/deck-remote.py')
deck_remote = _u.module_from_spec(_rspec); _rspec.loader.exec_module(deck_remote)
GOOD_KEY = 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl mac@laptop'


class DeckShareTests(unittest.TestCase):
    def test_add_key_validates_dedupes_and_sets_permissions(self):
        with tempfile.TemporaryDirectory() as home:
            self.assertTrue(deck_share.add_key(GOOD_KEY, home)['added'])
            self.assertFalse(deck_share.add_key(GOOD_KEY, home)['added'])
            path = Path(home)/'.ssh/authorized_keys'
            self.assertEqual(oct(path.stat().st_mode & 0o777), '0o600')
            self.assertEqual(oct(path.parent.stat().st_mode & 0o777), '0o700')
            self.assertEqual(deck_share.key_count(home), 1)
            bare = GOOD_KEY.rsplit(' ', 1)[0].replace('IOMq', 'IOMr')
            deck_share.add_key(bare, home)
            self.assertIn('deck-ai-share', path.read_text())

    def test_rejects_private_keys_options_and_multiple_lines(self):
        with tempfile.TemporaryDirectory() as home:
            for bad in ('-----BEGIN OPENSSH ' + 'PRIVATE KEY-----\nabc', 'command="rm -rf /" ' + GOOD_KEY, GOOD_KEY + '\n' + GOOD_KEY, 'ssh-ed25519 short', ''):
                with self.assertRaises(ValueError, msg=bad):
                    deck_share.add_key(bad, home)
            self.assertEqual(deck_share.key_count(home), 0)

    def test_status_and_snippet(self):
        with patch.object(deck_share, 'run', side_effect=lambda *c, **k: (0, 'active') if c[0] == 'systemctl' else (0, '2: wlan0 inet 192.168.1.50/24 brd x')):
            info = deck_share.status()
        self.assertTrue(info['sshActive']); self.assertIn('192.168.1.50', info['addresses'])
        self.assertIn('HostName 192.168.1.50', info['snippet']); self.assertIn('Host steamdeck', info['snippet'])


class DeckRemoteClientTests(unittest.TestCase):
    def setUp(self):
        fake = str(Path(__file__).with_name('fake_app_server.py'))
        def command(host, *remote, connect_timeout=8):
            if remote == ('pwd',): return ['pwd']
            return [sys.executable, '-u', fake] if remote and remote[0] == backend._REMOTE_SERVER else ['true']
        self.patch = patch.object(backend, 'ssh_command', side_effect=command); self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def run_cli(self, *args, answer='n'):
        lines = []
        with patch('builtins.input', return_value=answer):
            result = deck_remote.main(['desk', *args], out=lines.append)
        return result, '\n'.join(lines)

    def test_list_and_send_wait(self):
        result, text = self.run_cli('list')
        self.assertEqual(result, 0); self.assertIn('t1  Удалённая задача', text)
        result, text = self.run_cli('send', 't1', 'привет', '--wait')
        self.assertEqual(result, 0); self.assertIn('Готово (completed)', text)

    def test_new_thread_and_approval_prompt(self):
        result, text = self.run_cli('new', 'please approve', '--wait', answer='y')
        self.assertEqual(result, 0); self.assertIn('completed', text)
        result, text = self.run_cli('new', 'please approve', '--wait', answer='n')
        self.assertIn('failed', result)

    def test_completion_from_other_chat_does_not_finish_request(self):
        session = deck_remote.Session('desk')
        session.thread_id = 'own'; session.turn_id = 'turn1'
        session.on_event({'method':'turn/completed','params':{'threadId':'other','turn':{'id':'turn1','status':'completed'}}})
        self.assertFalse(session.done.is_set())
        session.on_event({'method':'turn/completed','params':{'threadId':'own','turn':{'id':'older','status':'completed'}}})
        self.assertFalse(session.done.is_set())

    def test_fast_completion_and_repeated_sends(self):
        session = deck_remote.Session('desk')
        session.backend = MagicMock()
        sequence = iter(('one','two'))
        def request(method, params, **kw):
            if method != 'turn/start':return {}
            ident = next(sequence)
            session.on_event({'method':'turn/completed','params':{'threadId':'own','turn':{'id':ident,'status':'completed'}}})
            return {'turn':{'id':ident}}
        session.backend.request.side_effect = request
        self.assertEqual(session.send('own','first',True,timeout=.1),'own')
        self.assertEqual(session.send('own','second',True,timeout=.1),'own')
        self.assertEqual(session.turn_id,'two')

    def test_disconnect_is_reported_as_failure(self):
        session = deck_remote.Session('desk'); session.backend = MagicMock()
        def request(method, params, **kw):
            if method=='turn/start':session.done.set(); return {'turn':{'id':'lost'}}
            return {}
        session.backend.request.side_effect=request
        with self.assertRaisesRegex(backend.RpcError,'соединение прервано'):
            session.send('own','text',True,timeout=.1)


import providers
_sspec = _u.spec_from_file_location('build_site_tested', ROOT/'scripts/build-site.py')
build_site = _u.module_from_spec(_sspec); _sspec.loader.exec_module(build_site)


class CustomProviderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.state = Path(self.tmp.name)
        self.secrets = {}
        def secret(*args, secret=None, account='openrouter'):
            if args[0] == 'store': self.secrets[account] = secret
            elif args[0] == 'clear': self.secrets.pop(account, None)
            else: return self.secrets.get(account, '')
        self.patch = patch.object(providers, '_secret_tool', side_effect=secret); self.patch.start()

    def tearDown(self):
        self.patch.stop(); self.tmp.cleanup()

    def test_url_validation(self):
        self.assertEqual(providers.normalize_base_url(' https://api.groq.com/openai/v1/ '), 'https://api.groq.com/openai/v1')
        self.assertEqual(providers.normalize_base_url('https://x.ai/v1/chat/completions'), 'https://x.ai/v1')
        for bad in ('', 'ftp://x/v1', 'https://user:pw@api.x.ai/v1', 'localhost:11434', 'file:///etc/passwd', 'http://api.openai.com/v1', 'https://localhost/v1', 'https://127.0.0.1/v1', 'https://192.168.1.10:11434/v1', 'https://10.0.0.5/v1', 'https://nas/v1', 'https://my-pc.local/v1', 'https://[::1]/v1'):
            with self.assertRaises(providers.ProviderError, msg=bad):
                providers.normalize_base_url(bad)

    def test_save_list_update_remove_and_key_goes_to_secret_store(self):
        ident = providers.save_custom(self.state, 'Мой Groq', 'https://api.groq.com/openai/v1', 'llama3, qwen', 'k-123')
        self.assertTrue(ident.startswith('custom:'))
        entries = providers.load_custom(self.state)
        self.assertEqual(entries[0]['models'], ['llama3', 'qwen'])
        self.assertNotIn('k-123', (self.state/'custom-providers.json').read_text())
        self.assertEqual(providers.read_custom_key(ident), 'k-123')
        providers.save_custom(self.state, 'Мой Groq', 'https://api.groq.com/openai/v1', 'llama3')
        self.assertEqual(len(providers.load_custom(self.state)), 1)
        with self.assertRaisesRegex(providers.ProviderError, 'ключ'):
            providers.save_custom(self.state, 'Другой', 'https://api.x.ai/v1', '', '')
        providers.remove_custom(self.state, ident)
        self.assertEqual(providers.load_custom(self.state), [])
        self.assertEqual(providers.read_custom_key(ident), '')

    def test_reply_sends_bearer_only_with_key_and_hides_error_bodies(self):
        entry = {'id': 'custom:x', 'name': 'Мой ИИ', 'baseUrl': 'https://api.example.com/v1', 'models': []}
        seen = {}
        class Reply:
            def __init__(self, data): self.data = data
            def read(self, *a): return self.data
            def __enter__(self): return self
            def __exit__(self, *a): return False
        def fake_open(request, timeout=0):
            seen['headers'] = dict(request.header_items()); seen['url'] = request.full_url; seen['body'] = json.loads(request.data)
            return Reply('{"choices":[{"message":{"content":" Привет! "}}]}'.encode())
        self.secrets['custom-x'] = 'sekret'
        with patch.object(providers.urllib.request, 'urlopen', fake_open):
            self.assertEqual(providers.custom_reply(entry, 'llama3', [{'role': 'user', 'content': 'a'}], 'b'), 'Привет!')
            self.assertEqual(seen['headers']['Authorization'], 'Bearer sekret'); self.assertEqual(seen['url'], 'https://api.example.com/v1/chat/completions')
            self.assertEqual(seen['body']['messages'][-1], {'role': 'user', 'content': 'b'})
        import io
        def failing(request, timeout=0):
            raise providers.urllib.error.HTTPError(request.full_url, 500, 'x', {}, io.BytesIO(b'SECRET echo'))
        with patch.object(providers.urllib.request, 'urlopen', failing), self.assertRaises(providers.ProviderError) as ctx:
            providers.custom_reply(entry, 'm', [], 'hi')
        self.assertNotIn('SECRET', str(ctx.exception))
        self.secrets.clear()
        with self.assertRaisesRegex(providers.ProviderError, 'ключ'):
            providers.custom_reply(entry, 'm', [], 'hi')

    def test_presets_are_all_cloud_and_old_local_entries_are_dropped(self):
        for name, url in providers.CUSTOM_PRESETS:
            self.assertEqual(providers.normalize_base_url(url), url, name)
        (self.state/'custom-providers.json').write_text(json.dumps([
            {'id': 'custom:old', 'name': 'Old', 'baseUrl': 'http://localhost:11434/v1', 'models': []},
            {'id': 'custom:ok', 'name': 'Ok', 'baseUrl': 'https://api.groq.com/openai/v1', 'models': []}]))
        self.assertEqual([e['id'] for e in providers.load_custom(self.state)], ['custom:ok'])

    def test_models_merge_typed_and_discovered(self):
        entry = {'id': 'custom:x', 'name': 'X', 'baseUrl': 'https://h.example.com/v1', 'models': ['mine']}
        class Reply:
            def read(self, *a): return b'{"data":[{"id":"found"},{"id":"mine"}]}'
            def __enter__(self): return self
            def __exit__(self, *a): return False
        with patch.object(providers.urllib.request, 'urlopen', lambda *a, **k: Reply()):
            self.assertEqual([m['id'] for m in providers.custom_models(entry)], ['mine', 'found'])
        with patch.object(providers.urllib.request, 'urlopen', side_effect=OSError):
            self.assertEqual([m['id'] for m in providers.custom_models(entry)], ['mine'])

    def test_bridge_adds_selects_and_answers_with_custom_ai(self):
        saved = (bridge.STATE, bridge.provider, bridge.provider_active, bridge.read_only)
        bridge.STATE = self.state; bridge.read_only = False
        try:
            ident = bridge.call('custom_save', {'name': 'Облако', 'baseUrl': 'https://api.groq.com/openai/v1', 'models': 'llama3', 'key': 'k'})['id']
            with patch.object(providers, 'custom_models', return_value=[{'id': 'llama3', 'name': 'llama3'}]):
                bridge.call('provider', {'provider': ident})
                self.assertEqual(bridge.provider, ident)
                with patch.object(providers, 'custom_reply', return_value='Ответ ИИ') as reply, patch.object(bridge.jobs, 'submit', side_effect=lambda fn, job: fn(job)):
                    bridge.send_message('вопрос', [], 'llama3', '', 'default')
                self.assertEqual(reply.call_args.args[1], 'llama3')
                chat = next(iter(bridge.provider_chats[ident].values()))
                self.assertEqual([m['text'] for m in chat['messages']], ['вопрос', 'Ответ ИИ'])
                self.assertIn('Облако', bridge.snapshot_extras()['customProviders'][0]['name'])
            with self.assertRaises(ValueError):
                bridge.call('provider', {'provider': 'custom:nope'})
            bridge.call('custom_remove', {'id': ident})
            self.assertEqual(bridge.provider, 'codex')
        finally:
            bridge.STATE, bridge.provider, bridge.provider_active, bridge.read_only = saved
            for key in [k for k in bridge.provider_chats if k.startswith('custom:')]: bridge.provider_chats.pop(key)
            bridge.custom_entries.clear()


class SiteAndInstallTests(unittest.TestCase):
    def test_site_is_generated_from_docs_and_is_valid_html(self):
        from html.parser import HTMLParser
        with tempfile.TemporaryDirectory() as out:
            page = build_site.build(ROOT, out)
            text = page.read_text()
            self.assertIn((ROOT/'VERSION').read_text().strip(), text)
            self.assertIn('id="quick-start"', text); self.assertIn('./install.sh --decky', text)
            self.assertIn('Notifications, remote tasks and files', text)
            self.assertTrue((Path(out)/'deck-ai.png').is_file() and (Path(out)/'.nojekyll').exists())
            class Check(HTMLParser):
                def __init__(self):
                    super().__init__(); self.stack = []
                def handle_starttag(self, tag, attrs):
                    if tag not in ('meta', 'link', 'img', 'br'): self.stack.append(tag)
                def handle_endtag(self, tag):
                    assert self.stack and self.stack.pop() == tag, tag
            checker = Check(); checker.feed(text); self.assertEqual(checker.stack, [])

    def test_markdown_subset_escapes_html_and_rewrites_relative_links(self):
        out = build_site.markdown('# T\n\nUse `a<b>` and **bold** [doc](decky/README.md) <script>\n\n- one\n- two\n\n```bash\nx && y\n```')
        self.assertIn('<code>a&lt;b&gt;</code>', out); self.assertIn('&lt;script&gt;', out)
        self.assertIn('blob/main/decky/README.md', out); self.assertIn('<ul><li>one</li><li>two</li></ul>', out)
        self.assertIn('x &amp;&amp; y', out)

    def test_setup_creates_key_config_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as home:
            lines = []
            with patch.object(deck_remote.subprocess, 'run') as run:
                def fake(cmd, **kw):
                    if cmd[0] == 'ssh-keygen':
                        Path(cmd[-1]).write_text('PRIV'); Path(cmd[-1] + '.pub').write_text(GOOD_KEY + '\n')
                        return SimpleNamespace(returncode=0, stdout='', stderr='')
                    return SimpleNamespace(returncode=0, stdout='ok\n', stderr='')
                run.side_effect = fake
                self.assertEqual(deck_remote.setup('steamdeck', '192.168.1.50', 'deck', True, home, out=lines.append), 0)
                self.assertEqual(deck_remote.setup('steamdeck', '192.168.1.50', 'deck', True, home, out=lines.append), 0)
            config = (Path(home)/'.ssh/config').read_text()
            self.assertEqual(config.count('Host steamdeck'), 1); self.assertIn('HostName 192.168.1.50', config)
            self.assertIn('add-key', '\n'.join(lines)); self.assertIn('Подключение работает', '\n'.join(lines))

    def test_decky_installer_copies_plugin_files(self):
        with tempfile.TemporaryDirectory() as dest:
            target = Path(dest)/'plugins/Codex'
            result = subprocess.run(['bash', str(ROOT/'scripts/install-decky.sh')], capture_output=True, text=True,
                                    env={**os.environ, 'DECKY_PLUGIN_DIR': str(target), 'DECK_AI_SKIP_RESTART': '1'})
            self.assertEqual(result.returncode, 0, result.stderr)
            for name in ('plugin.json', 'main.py', 'bridge.py', 'dist/index.js', 'LICENSE', 'NOTICE'):
                self.assertTrue((target/name).is_file(), name)
            self.assertFalse((target/'node_modules').exists())


class ThemeConsistencyTests(unittest.TestCase):
    def test_desktop_palettes_are_complete_and_menu_lists_every_theme(self):
        import re
        palettes = json.loads((ROOT/'themes.json').read_text())
        keys = set(palettes['dark'])
        for name, palette in palettes.items():
            self.assertEqual(set(palette), keys, name)
            for key, value in palette.items():
                self.assertRegex(value, r'^(#[0-9a-fA-F]{6}|rgba?\([^)]*\))$', f'{name}.{key}')
        titles = re.search(r'THEME_TITLES = \{(.*?)\}', (ROOT/'app.py').read_text()).group(1)
        self.assertEqual(set(re.findall(r"'(\w+)':", titles)), set(palettes))

    def test_decky_themes_have_css_tokens_and_node_list_matches(self):
        import re
        css = (ROOT/'decky/src/style.css').read_text()
        ids = re.findall(r'\{id:"(\w+)",name:"[^"]+",swatch', (ROOT/'decky/src/appearance.ts').read_text())
        self.assertGreaterEqual(len(ids), 6)
        for theme in ids:
            self.assertTrue(f'data-theme={theme}]' in css or theme == 'ocean', theme)
