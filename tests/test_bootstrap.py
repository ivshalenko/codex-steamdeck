import importlib.util,io,tarfile,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
p=Path(__file__).resolve().parents[1]/'scripts/bootstrap.py';s=importlib.util.spec_from_file_location('bootstrap_test',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class BootstrapTests(unittest.TestCase):
 def test_archive_traversal_and_links_are_rejected_before_extraction(self):
  for name,kind in [('deck-ai-'+m.VERSION+'/../../escape',tarfile.REGTYPE),('deck-ai-'+m.VERSION+'/link',tarfile.SYMTYPE)]:
   with self.subTest(name=name),tempfile.TemporaryDirectory() as folder:
    root=Path(folder);archive=root/'input.tar.gz';output=root/'output';output.mkdir()
    with tarfile.open(archive,'w:gz') as tar:
     member=tarfile.TarInfo(name);member.type=kind;member.linkname='/outside';tar.addfile(member)
    with self.assertRaisesRegex(ValueError,'Unsafe'):m.unpack(archive,output)
    self.assertEqual(list(output.iterdir()),[])
 def test_checksum_failure_never_extracts_or_launches_code(self):
  with tempfile.TemporaryDirectory() as folder,patch.object(m,'unpack') as unpack:
   def fake(name,path,limit):Path(path).write_bytes(b'0'*64+b'  deck-ai-'+m.VERSION.encode()+b'-steamdeck.tar.gz\n' if name=='SHA256SUMS.txt' else b'corrupt archive')
   with patch.object(m,'download',side_effect=fake):
    with self.assertRaisesRegex(ValueError,'checksum'):m.prepare(folder)
   unpack.assert_not_called()
