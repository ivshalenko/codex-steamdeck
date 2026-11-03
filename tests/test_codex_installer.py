import importlib.util,io,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
p=Path(__file__).resolve().parents[1]/'scripts/install-codex.py'
s=importlib.util.spec_from_file_location('codex_install_test',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class InstallerTests(unittest.TestCase):
 def test_tampered_official_download_is_rejected_before_execution(self):
  with tempfile.TemporaryDirectory() as d,patch.object(m.urllib.request,'urlopen',return_value=io.BytesIO(b'changed installer')),patch.object(m.subprocess,'run') as execute:
   with self.assertRaisesRegex(ValueError,'checksum'):m.install()
   execute.assert_not_called()
