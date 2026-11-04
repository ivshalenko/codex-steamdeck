"""Release archives are deterministic and contain only distributable files."""
import hashlib,importlib.util,json,tarfile,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
package=load('package_tested','check-package.py');builder=load('builder_tested','build-release.py')

class ReleaseTests(unittest.TestCase):
 def test_source_allowlist_excludes_private_and_generated_files(self):
  files=package.source_files()
  self.assertTrue(all(not any(part in package.FORBIDDEN for part in p.parts) for p in files))
  self.assertFalse(any(p.parts[0]=='build' for p in files))
  self.assertFalse(any(p.parts[0]=='models' and str(p)!='models/README.md' for p in files))
  self.assertIn(Path('decky/runtime_paths.py'),files)
  self.assertIn(Path('docs/brand/hero.svg'),files)
  self.assertIn(Path('docs/README.ru.md'),files)
 def test_version_metadata_matches(self):
  version,_=package.check()
  self.assertEqual(json.loads((ROOT/'decky/package.json').read_text())['version'],version)
 def test_stable_release_without_license_is_rejected(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'decky').mkdir();(root/'VERSION').write_text('1.0.0')
   for name in ('package.json','package-lock.json'):(root/'decky'/name).write_text('{"version":"1.0.0"}')
   with self.assertRaisesRegex(ValueError,'LICENSE'):package.check(root)
 def test_archives_have_fixed_metadata_correct_checksums_and_repeatable_bytes(self):
  with tempfile.TemporaryDirectory() as directory,patch.object(builder.subprocess,'run'),patch.object(builder.package,'check',return_value=('1.0.0-rc.1',[Path('VERSION')])),patch.object(builder.plugin_package,'files',return_value={Path('plugin.json'):ROOT/'decky/plugin.json'}):
   output=builder.build(Path(directory));first={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()}
   builder.build(output);second={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()};self.assertEqual(first,second)
   with tarfile.open(output/'deck-ai-1.0.0-rc.1-steamdeck.tar.gz') as archive:
    member=archive.getmembers()[0];self.assertEqual(member.uid,0);self.assertEqual(member.mtime,0);self.assertTrue(member.name.endswith('/VERSION'))
   with zipfile.ZipFile(output/'deck-ai-1.0.0-rc.1-decky.zip') as archive:self.assertEqual(archive.namelist(),['Deck AI/plugin.json']);self.assertIsNone(archive.testzip())
   for line in (output/'SHA256SUMS.txt').read_text().splitlines():
    expected,name=line.split('  ');self.assertEqual(expected,hashlib.sha256((output/name).read_bytes()).hexdigest())
