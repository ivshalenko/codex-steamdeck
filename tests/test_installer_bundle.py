"""Exercise the exact launcher bytes and ZIP permissions used by new users."""
import base64,hashlib,importlib.util,io,json,sys,tarfile,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
builder=load('bundle_builder','build-release.py');site=load('download_site','build-site.py')
class InstallerBundleTests(unittest.TestCase):
 def setUp(self):
  self.temporary=tempfile.TemporaryDirectory();self.addCleanup(self.temporary.cleanup);self.root=Path(self.temporary.name);self.version=(ROOT/'VERSION').read_text().strip()
  self.package=self.root/f'deck-ai-{self.version}-steamdeck.tar.gz'
  with tarfile.open(self.package,'w:gz') as archive:
   info=tarfile.TarInfo('deck-ai-'+self.version+'/VERSION');data=self.version.encode();info.size=len(data);archive.addfile(info,io.BytesIO(data))
  self.bundle=builder.installer_bundle(self.root,self.version,self.package)
 def scope(self):
  with zipfile.ZipFile(self.bundle) as archive:launcher=archive.read('Deck AI Setup/Install Deck AI.desktop').decode()
  code=base64.b64decode(launcher.split("base64.b64decode('",1)[1].split("')",1)[0]).decode()
  scope={'__name__':'bundle_test'};exec(compile(code,'actual-bundle-launcher','exec'),scope);return scope,launcher
 def extracted(self):
  target=self.root/'Downloads with spaces';target.mkdir()
  with zipfile.ZipFile(self.bundle) as archive:archive.extractall(target)
  return target/'Deck AI Setup/Install Deck AI.desktop'
 def test_zip_has_executable_launcher_and_the_exact_app_archive(self):
  with zipfile.ZipFile(self.bundle) as archive:
   self.assertEqual(len(archive.namelist()),5);info=archive.getinfo('Deck AI Setup/Install Deck AI.desktop');self.assertEqual((info.external_attr>>16)&0o777,0o755);self.assertEqual(info.create_system,3)
   self.assertEqual(archive.read('Deck AI Setup/'+self.package.name),self.package.read_bytes())
  scope,launcher=self.scope();self.assertIn(' %k\n',launcher);self.assertEqual(scope['BUNDLED_ARCHIVE_SHA256'],hashlib.sha256(self.package.read_bytes()).hexdigest())
 def test_real_embedded_prepare_uses_bundle_without_network(self):
  launcher=self.extracted();scope,_=self.scope()
  for kind,location in [('path',str(launcher)),('uri',launcher.as_uri())]:
   output=self.root/kind;output.mkdir()
   with patch('urllib.request.urlopen',side_effect=AssertionError('Bundled app must not download')):
    source=scope['prepare'](output,location)
   self.assertEqual((source/'VERSION').read_text(),self.version)
 def test_changed_app_archive_is_rejected_before_extracting(self):
  launcher=self.extracted();scope,_=self.scope();launcher.with_name(self.package.name).write_bytes(b'tampered')
  output=self.root/'output';output.mkdir()
  with self.assertRaisesRegex(ValueError,'checksum'):scope['prepare'](output,launcher)
  self.assertEqual(list(output.iterdir()),[])
 def test_missing_archive_and_foreign_launcher_uri_explain_or_reject(self):
  scope,_=self.scope();output=self.root/'output';output.mkdir()
  for location in (self.root/'missing/Install Deck AI.desktop','https://other.example/launcher','file://other.example/launcher'):
   with self.subTest(location=location),self.assertRaises(ValueError):scope['prepare'](output,location)
 def test_download_page_serves_local_zip_with_download_filename_in_both_languages(self):
  output=self.root/'site';site.build(ROOT,output,self.bundle);page=(output/'install/index.html').read_text()
  self.assertIn('href="'+self.bundle.name+'" download="'+self.bundle.name+'"',page);self.assertIn('Скачать для Steam Deck',page);self.assertIn('id="ru"',page);self.assertIn("language('ru')",page)
  self.assertNotIn('raw.githubusercontent.com',page);self.assertNotIn('/releases/download/',page)
  self.assertEqual((output/'install'/self.bundle.name).read_bytes(),self.bundle.read_bytes());self.assertIn(hashlib.sha256(self.bundle.read_bytes()).hexdigest(),page)
 def test_site_cannot_be_published_without_matching_installer(self):
  with self.assertRaisesRegex(ValueError,'required'):site.build(ROOT,self.root/'no-installer')
  other=self.root/'Deck-AI-Setup-0.0.0.zip';other.write_bytes(b'old')
  with self.assertRaisesRegex(ValueError,'version'):site.build(ROOT,self.root/'wrong-version',other)
 def test_full_bundle_includes_codex_package_and_licenses(self):
  payload=self.root/'codex-package-x86_64-unknown-linux-musl.tar.gz';payload.write_bytes(b'pinned fixture')
  bundle=builder.installer_bundle(self.root,self.version,self.package,[payload])
  with zipfile.ZipFile(bundle) as archive:
   self.assertEqual(archive.read('Deck AI Setup/codex/'+payload.name),payload.read_bytes())
   self.assertIn('Deck AI Setup/codex/codex-LICENSE.md',archive.namelist());self.assertIn('Deck AI Setup/codex/codex-NOTICE.md',archive.namelist())
 def test_actual_bundled_entry_passes_local_codex_folder_into_setup(self):
  launcher=self.extracted();scope,text=self.scope();code=base64.b64decode(text.split("base64.b64decode('",1)[1].split("')",1)[0]).decode()
  calls=[]
  def execute(command,**options):
   calls.append(command);self.assertEqual(options['env']['DECK_AI_CODEX_BUNDLE_DIR'],str(launcher.parent.resolve()/'codex'));self.assertTrue(Path(command[1]).parent.parent.joinpath('VERSION').is_file())
  with patch.object(sys,'argv',[str(launcher),launcher.as_uri()]),patch.object(sys,'platform','linux'),patch('subprocess.run',side_effect=execute):exec(compile(code,'actual-zip-entry','exec'),{'__name__':'__main__'})
  self.assertEqual(len(calls),1)
