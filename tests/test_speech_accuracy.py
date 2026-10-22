import importlib.util
from pathlib import Path
from types import SimpleNamespace
import tempfile,unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('speech_accuracy_tested',Path(__file__).resolve().parents[1]/'speech_accuracy.py')
speech=importlib.util.module_from_spec(spec);spec.loader.exec_module(speech)
class SpeechAccuracyTests(unittest.TestCase):
 def test_missing_model_and_economy_keep_original(self):
  with tempfile.TemporaryDirectory() as directory,patch.object(speech.subprocess,'run') as worker:
   self.assertEqual(speech.refine_dictation(b'aa','ru','исходный',directory),'исходный')
   self.assertEqual(speech.refine_dictation(b'aa','ru-fast','исходный',directory),'исходный')
   worker.assert_not_called()
 def test_worker_result_and_failure_preserve_original(self):
  with tempfile.TemporaryDirectory() as directory:
   model=Path(directory)/'models/faster-whisper-small';model.mkdir(parents=True);(model/'model.bin').touch()
   with patch.object(speech.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout='{"text":"Точная фраза."}')) as worker:
    self.assertEqual(speech.refine_dictation(b'aa','ru','черновой',directory),'Точная фраза.')
    self.assertEqual(worker.call_args.kwargs['env']['HF_HUB_OFFLINE'],'1')
   with patch.object(speech.subprocess,'run',return_value=SimpleNamespace(returncode=1,stdout='')):
    self.assertEqual(speech.refine_dictation(b'aa','ru','черновой',directory),'черновой')
