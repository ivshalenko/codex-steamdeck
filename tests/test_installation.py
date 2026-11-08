"""Install/update/uninstall in temporary homes, never in the real account."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('manage_install',ROOT/'scripts/manage-install.py');manager=importlib.util.module_from_spec(spec);spec.loader.exec_module(manager)
from runtime_paths import resolve_app_dir,resolve_state_dir,desktop_shortcut

class InstallationTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.home=Path(self.temp.name)/'user with spaces';self.home.mkdir()
 def test_fresh_install_has_every_runtime_file_but_no_dev_dependencies(self):
  app=manager.install(ROOT,self.home)
  self.assertEqual(app,self.home/'.local/share/deck-ai')
  for file in ('app.py','speech_accuracy.py','speech-languages.json','decky/runtime_paths.py','decky/dist/index.js','scripts/check-environment.py'):
   self.assertTrue((app/file).is_file(),file)
  self.assertFalse((app/'decky/node_modules').exists())
  self.assertTrue((self.home/'.local/bin/deck-ai').stat().st_mode&0o100)
  self.assertIn('"'+str(self.home), (self.home/'.local/share/applications/codex-steamdeck.desktop').read_text())
 def test_preflight_finds_native_cli_installations_without_path_entries(self):
  script=ROOT/'scripts/check-environment.py'
  check_spec=importlib.util.spec_from_file_location('check_environment',script)
  preflight=importlib.util.module_from_spec(check_spec);check_spec.loader.exec_module(preflight)
  bin_dir=self.home/'.local/bin';bin_dir.mkdir(parents=True)
  for name in ('codex','claude'):
   binary=bin_dir/name;binary.touch();binary.chmod(0o700)
  with patch.object(Path,'home',return_value=self.home), patch('shutil.which',return_value=None), patch('subprocess.run',side_effect=OSError):
   checks=preflight.check()['checks']
  self.assertTrue(checks['codex'])
  self.assertTrue(checks['claude'])
 def test_desktop_shortcut_is_executable_and_managed_without_duplicates(self):
  app=manager.install(ROOT,self.home);shortcut=self.home/'Desktop/Deck AI.desktop'
  self.assertTrue(shortcut.is_file());self.assertEqual(shortcut.stat().st_mode&0o777,0o755);self.assertIn('Exec="'+str(self.home/'.local/bin/deck-ai')+'"',shortcut.read_text());self.assertIn('Icon=deck-ai',shortcut.read_text())
  before=shortcut.read_bytes();manager.install(ROOT,self.home);self.assertEqual(shortcut.read_bytes(),before);self.assertEqual(list((self.home/'Desktop').glob('*.desktop')),[shortcut]);self.assertIn('Desktop/Deck AI.desktop',json.loads((app/'install-manifest.json').read_text())['files'])
  manager.uninstall(self.home);self.assertFalse(shortcut.exists())
 def test_localized_xdg_desktop_is_used(self):
  config=self.home/'.config';config.mkdir();(config/'user-dirs.dirs').write_text('XDG_DESKTOP_DIR="$HOME/Рабочий стол"\n')
  manager.install(ROOT,self.home);shortcut=self.home/'Рабочий стол/Deck AI.desktop';self.assertTrue(shortcut.is_file());self.assertFalse((self.home/'Desktop').exists());manager.uninstall(self.home);self.assertFalse(shortcut.exists())
 def test_disabled_or_external_desktop_never_receives_a_shortcut(self):
  config=self.home/'.config';config.mkdir()
  for value in ('$HOME','/tmp/deck-ai-unowned-desktop','$(touch /tmp/unwanted)'):
   (config/'user-dirs.dirs').write_text('XDG_DESKTOP_DIR="'+value+'"\n');self.assertIsNone(desktop_shortcut(self.home))
  manager.install(ROOT,self.home);self.assertFalse((self.home/'Desktop').exists())
 def test_existing_foreign_or_edited_desktop_file_is_preserved(self):
  folder=self.home/'Desktop';folder.mkdir();shortcut=folder/'Deck AI.desktop';shortcut.write_text('personal existing file')
  app=manager.install(ROOT,self.home);self.assertEqual(shortcut.read_text(),'personal existing file');self.assertNotIn('Desktop/Deck AI.desktop',json.loads((app/'install-manifest.json').read_text())['files'])
  shortcut.unlink();manager.install(ROOT,self.home);shortcut.write_text(shortcut.read_text()+'# my edit\n');manager.install(ROOT,self.home);manager.uninstall(self.home);self.assertTrue(shortcut.read_text().endswith('# my edit\n'))
 def test_legacy_update_reuses_location_and_preserves_models_and_data(self):
  for name in ('deck-voice','codex-steamdeck'):
   with self.subTest(name=name):
    home=self.home/name;old=home/'.local/share'/name;old.mkdir(parents=True);(old/'app.py').write_text('old version')
    models=old/'models/custom/model';models.parent.mkdir(parents=True);models.write_text('keep-model')
    state=home/'.local/state'/name;state.mkdir(parents=True);draft=state/'draft.txt';draft.write_text('keep-draft')
    self.assertEqual(manager.install(ROOT,home),old);self.assertEqual(models.read_text(),'keep-model');self.assertEqual(draft.read_text(),'keep-draft')
    self.assertEqual(resolve_state_dir(home),state)
 def test_uninstall_keeps_user_data_models_and_modified_files(self):
  app=manager.install(ROOT,self.home);state=resolve_state_dir(self.home);state.mkdir(parents=True);(state/'draft.txt').write_text('draft')
  models=app/'models/personal';models.parent.mkdir();models.write_text('model')
  edited=app/'themes.json';edited.write_text('my custom theme')
  manager.uninstall(self.home)
  self.assertFalse((app/'app.py').exists());self.assertFalse((self.home/'.local/bin/deck-ai').exists())
  self.assertEqual((state/'draft.txt').read_text(),'draft');self.assertEqual(models.read_text(),'model');self.assertEqual(edited.read_text(),'my custom theme')
 def test_reinstall_after_legacy_uninstall_finds_retained_models(self):
  app=self.home/'.local/share/deck-voice';app.mkdir(parents=True);(app/'app.py').touch()
  manager.install(ROOT,self.home);(app/'models').mkdir();(app/'models/keep').write_text('model')
  manager.uninstall(self.home)
  self.assertEqual(manager.install(ROOT,self.home),app)
  self.assertEqual((app/'models/keep').read_text(),'model')
 def test_manifest_path_escape_is_rejected_before_deleting_anything(self):
  app=manager.install(ROOT,self.home);manifest=app/'install-manifest.json';value=json.loads(manifest.read_text());value['files']['../../outside']='unused';manifest.write_text(json.dumps(value))
  with self.assertRaises(ValueError):manager.uninstall(self.home)
  self.assertTrue((app/'app.py').exists())
 def test_tampered_manifest_cannot_delete_models(self):
  app=manager.install(ROOT,self.home);model=app/'models/keep';model.parent.mkdir();model.write_text('KEEP')
  manifest=app/'install-manifest.json';data=json.loads(manifest.read_text());data['files'][str(model.relative_to(self.home))]=manager.digest(model);manifest.write_text(json.dumps(data))
  with self.assertRaises(ValueError):manager.uninstall(self.home)
  self.assertTrue(model.exists());self.assertTrue((app/'app.py').exists())
 def test_failed_update_rolls_back_previous_files(self):
  from unittest.mock import patch
  app=manager.install(ROOT,self.home);before=(app/'app.py').read_bytes();replace=manager.os.replace;count=0
  def fail_once(source,target):
   nonlocal count
   count+=1
   if count==3:raise OSError('simulated disk failure')
   return replace(source,target)
  with patch.object(manager.os,'replace',side_effect=fail_once):
   with self.assertRaises(OSError):manager.install(ROOT,self.home)
  self.assertEqual((app/'app.py').read_bytes(),before)
 def test_canonical_install_wins_when_present(self):
  for name in ('deck-ai','deck-voice'):
   folder=self.home/'.local/share'/name;folder.mkdir(parents=True);(folder/'app.py').touch()
  self.assertEqual(resolve_app_dir(self.home),self.home/'.local/share/deck-ai')
