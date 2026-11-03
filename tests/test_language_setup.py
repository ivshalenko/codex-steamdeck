"""Readiness checks stay read-only; dependencies install only after explicit preparation."""
import tempfile,threading,unittest
from pathlib import Path
from unittest.mock import patch
import language_support as languages
class LanguageSetupTests(unittest.TestCase):
 def test_opening_settings_never_installs_missing_voice_dependency(self):
  with tempfile.TemporaryDirectory() as root,patch.object(languages.importlib.util,'find_spec',return_value=None),patch.object(languages,'run_cancellable') as install:
   self.assertFalse(languages.recognition_ready(root,'ru'));install.assert_not_called()
 def test_ready_russian_pack_is_reused_without_network_or_package_changes(self):
  with tempfile.TemporaryDirectory() as root:
   model=Path(root)/'models'/languages.VOSK['ru']
   for name in ('am/final.mdl','conf/model.conf','graph/HCLr.fst'):
    path=model/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b'model fixture')
   with patch.object(languages.importlib.util,'find_spec',return_value=object()),patch.object(languages,'run_cancellable') as install,patch.object(languages,'download') as download:
    self.assertTrue(languages.recognition_ready(root,'ru'));languages.prepare_recognition(root,'ru',threading.Event(),lambda _:None);install.assert_not_called();download.assert_not_called()
