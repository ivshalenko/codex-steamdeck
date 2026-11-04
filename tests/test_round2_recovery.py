"""Regression cases found while testing queued work, media and recovery."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'decky'))
spec = importlib.util.spec_from_file_location('round2_bridge', ROOT/'decky/bridge.py')
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
spec = importlib.util.spec_from_file_location('round2_backup', ROOT/'scripts/backup-state.py')
backup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup)


class RecoveryTests(unittest.TestCase):
    def test_file_operations_reject_the_previous_device_before_io(self):
        with patch.object(bridge,'remote_host','new-device'), patch.object(bridge.device,'write_file') as save, patch.object(bridge.device,'read_file') as read, patch.object(bridge.device,'list_files') as listing:
            for operation in ('list','read','write'):
                with self.assertRaisesRegex(ValueError,'Устройство изменилось'):
                    bridge.files_call(operation,{'expectedHost':'old-device','path':'/home/test/file.txt','text':'new'})
            save.assert_not_called();read.assert_not_called();listing.assert_not_called()

    def test_attachment_validation_is_complete_before_copies_are_created(self):
        with patch.object(bridge,'allowed_image',side_effect=[Path('first'),ValueError('missing')]), patch.object(bridge,'archive_image') as archive:
            with self.assertRaisesRegex(ValueError,'missing'):
                bridge.send_message('fixture',['a','b'],'model','','')
            archive.assert_not_called()
        with patch.object(bridge,'archive_image') as archive:
            with self.assertRaisesRegex(ValueError,'пяти'):
                bridge.send_message('fixture',['image']*6,'model','','')
            archive.assert_not_called()

    def test_recovering_request_cannot_be_submitted_again(self):
        job = {'id':'test', 'status':'recovering'}
        with patch.object(bridge,'outbox',[job]), patch.object(bridge,'dispatch') as dispatch:
            with self.assertRaisesRegex(ValueError,'проверяется'):
                bridge.call('retry',{'id':'test'})
            self.assertEqual(job['status'],'recovering')
            dispatch.assert_not_called()

    def test_every_failed_video_attempt_removes_its_frames(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            video = root/'sample.mp4'
            video.touch()
            state = root/'state'
            failures = [FileNotFoundError(), subprocess.TimeoutExpired('ffmpeg',90),
                        subprocess.CalledProcessError(1,'ffmpeg',stderr='broken recording'), None]
            for failure in failures:
                with self.subTest(failure=type(failure).__name__), patch.object(bridge,'STATE',state), patch.object(bridge,'media_roots',return_value=[root]):
                    def run(*args,**kwargs):
                        for target in (state/'game-frames').iterdir():
                            (target/'frame-01.jpg').write_bytes(b'incomplete')
                        if failure:raise failure
                        # A successful process with no actual frames is also a failure.
                        for target in (state/'game-frames').glob('*/frame-01.jpg'):
                            target.unlink()
                    with patch.object(bridge.subprocess,'run',side_effect=run), self.assertRaises(RuntimeError):
                        bridge.video_frames(str(video))
                    self.assertEqual(list((state/'game-frames').iterdir()),[])

    def test_stopped_microphone_does_not_wait_for_the_next_audio_block(self):
        reader,writer = os.pipe()
        stream = os.fdopen(reader,'rb',buffering=0)
        recorder = Mock(stdout=stream, stderr=Mock())
        recorder.poll.return_value = None
        recognizer = Mock()
        recognizer.FinalResult.return_value = '{"text":""}'
        vosk = SimpleNamespace(Model=Mock(),SetLogLevel=Mock(),KaldiRecognizer=Mock(return_value=recognizer))
        stop = threading.Event()
        timer = threading.Timer(.04,stop.set)
        started = time.monotonic()
        try:
            timer.start()
            with patch.dict(sys.modules,{'vosk':vosk}), patch.object(bridge,'voice_stop',stop), patch.object(bridge,'vosk_model',return_value=Mock()), patch.object(bridge.subprocess,'check_output',return_value='test-microphone'), patch.object(bridge.subprocess,'Popen',return_value=recorder):
                bridge.voice_capture('en-fast')
            self.assertLess(time.monotonic()-started,1.5)
            self.assertTrue(stream.closed)
            recorder.wait.assert_called()
        finally:
            stop.set();timer.join();stream.close();os.close(writer)

    def test_same_timestamp_backups_are_distinct_and_a_failure_keeps_both(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'thread-id').write_text('first')
            one = backup.backup(root,stamp='fixed')
            (root/'thread-id').write_text('second')
            two = backup.backup(root,stamp='fixed')
            self.assertNotEqual(one,two)
            before = {path.name:path.read_bytes() for path in (root/'backups').glob('state-*.tar.gz')}
            with patch.object(backup.tarfile,'open',side_effect=OSError('disk full')), self.assertRaises(OSError):
                backup.backup(root,stamp='fixed')
            self.assertEqual(before,{path.name:path.read_bytes() for path in (root/'backups').glob('state-*.tar.gz')})
            self.assertEqual(list((root/'backups').glob('*.part')),[])

    def test_backup_does_not_enter_skipped_media_directories(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'thread-id').write_text('selected')
            (root/'game-frames').mkdir()
            walked = []
            original = os.walk
            def observe(*args,**kwargs):
                for row in original(*args,**kwargs):
                    walked.append(Path(row[0]))
                    yield row
            with patch.object(backup.os,'walk',side_effect=observe):
                backup.backup(root)
            self.assertEqual(walked,[root])

class RemoteDisconnectTests(unittest.TestCase):
    def test_expected_disconnects_are_quiet_but_other_errors_are_reported(self):
        from http.server import ThreadingHTTPServer
        from repair_remote import LocalServer
        server = object.__new__(LocalServer)
        with patch.object(ThreadingHTTPServer,'handle_error') as report:
            for error in (BrokenPipeError(),ConnectionResetError()):
                try:raise error
                except OSError:server.handle_error(None,None)
            report.assert_not_called()
            try:raise ValueError('unexpected fixture failure')
            except ValueError:server.handle_error(None,None)
            report.assert_called_once()


if __name__ == '__main__':
    unittest.main()
