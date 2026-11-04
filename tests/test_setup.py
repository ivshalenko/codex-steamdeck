"""Installer boundaries: explicit choices, language propagation and truthful success."""
import hashlib,importlib.util,io,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import setup_support as setup

def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
loader=load('setup_loader_test','install-loader.py');system=load('setup_system_test','setup-system.py');builder=load('setup_builder_test','build-release.py')
class SetupTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.home=Path(self.temp.name)/'user with spaces';self.home.mkdir();self.calls=[];self.events=[]
  for target,value in [('sys.platform','linux'),('shutil.which','/usr/bin/konsole')]:
   manager=patch(target,return_value=value) if target=='shutil.which' else patch(target,value);manager.start();self.addCleanup(manager.stop)
  manager=patch.object(setup.shutil,'disk_usage',return_value=type('Disk',(),{'free':2_000_000_000})());manager.start();self.addCleanup(manager.stop)
 def execute(self,command):
  self.calls.append(command)
  if '--receipt' in command:Path(command[command.index('--receipt')+1]).write_text('{"ok":true}')
 def progress(self,*event):self.events.append(event)
 def test_automatic_selects_required_components_without_enabling_remote_or_voice(self):
  options=setup.Options(voice=True,ssh=True,read_only=True,codex=False)
  self.assertTrue(options.codex and options.decky and options.loader);self.assertFalse(options.voice or options.ssh);self.assertIsNone(options.read_only)
  with patch.object(setup,'codex_installed',return_value=True):setup.run_install(options,ROOT,self.execute,self.progress,self.home)
  admin=next(c for c in self.calls if '--receipt' in c);self.assertIn('--decky',admin);self.assertIn('--allow-loader',admin);self.assertNotIn('--ssh',admin)
  self.assertEqual(self.events[-1],('ready',1.0));self.assertEqual((setup.resolve_state_dir(self.home)/'language').read_text(),'en\n')
 def test_english_and_russian_reach_legacy_app_state_without_touching_chats_or_credentials(self):
  state=self.home/'.local/state/deck-voice';state.mkdir(parents=True)
  for name,content in [('draft.txt','Мой текст'),('voice-language','de'),('runtime-preferences.json','{"autoApprove":false}'),('auth.json','personal fixture')]: (state/name).write_text(content)
  for language in ('ru','en'):
   options=setup.Options(language=language,mode='custom',decky=False,codex=False)
   setup.run_install(options,ROOT,self.execute,self.progress,self.home)
   self.assertEqual((state/'language').read_text().strip(),language)
   self.assertEqual(json.loads((state/'setup-choices.json').read_text())['language'],language)
  self.assertEqual((state/'draft.txt').read_text(),'Мой текст');self.assertEqual((state/'voice-language').read_text(),'de');self.assertEqual((state/'auth.json').read_text(),'personal fixture');self.assertEqual((state/'runtime-preferences.json').read_text(),'{"autoApprove":false}')
  self.assertEqual((state/'language').stat().st_mode&0o777,0o600)
 def test_custom_desktop_only_never_downloads_codex_or_launches_administrator_steps(self):
  setup.run_install(setup.Options(mode='custom',codex=False,decky=False),ROOT,self.execute,self.progress,self.home)
  self.assertEqual(len(self.calls),2);self.assertFalse(any('--receipt' in c for c in self.calls))
 def test_custom_voice_and_ssh_only_apply_when_explicitly_selected(self):
  setup.run_install(setup.Options(language='ru',mode='custom',codex=False,decky=False,voice=True,ssh=True),ROOT,self.execute,self.progress,self.home)
  voice=next(c for c in self.calls if any(str(x).endswith('setup-voice.py') for x in c));self.assertEqual(voice[-2:],['--language','ru'])
  admin=next(c for c in self.calls if '--receipt' in c);self.assertIn('--ssh',admin);self.assertNotIn('--decky',admin)
  self.assertEqual((setup.resolve_state_dir(self.home)/'voice-language').read_text().strip(),'ru')
 def test_unconfirmed_or_failed_terminal_cannot_show_ready_even_if_konsole_exits_zero(self):
  for receipt in (None,'not json','{"ok":false,"error":"password cancelled"}'):
   with self.subTest(receipt=receipt):
    self.events=[]
    def terminal(command):
     if '--receipt' in command and receipt is not None:Path(command[command.index('--receipt')+1]).write_text(receipt)
    with patch.object(setup,'codex_installed',return_value=True),self.assertRaises(RuntimeError):setup.run_install(setup.Options(),ROOT,terminal,self.progress,self.home)
    self.assertNotIn(('ready',1.0),self.events)
 def test_failed_required_step_stops_later_steps(self):
  def fail(command):raise RuntimeError('validation failed')
  with self.assertRaisesRegex(RuntimeError,'validation'):setup.run_install(setup.Options(),ROOT,fail,self.progress,self.home)
  self.assertFalse((setup.resolve_state_dir(self.home)/'language').exists());self.assertNotIn(('ready',1.0),self.events)
 def test_missing_loader_and_terminal_fail_before_mutating_an_installation(self):
  with patch.object(setup,'decky_installed',return_value=False),self.assertRaisesRegex(RuntimeError,'missing'):setup.run_install(setup.Options(mode='custom',loader=False),ROOT,self.execute,self.progress,self.home)
  self.assertEqual(self.calls,[])
  with patch.object(setup.shutil,'which',return_value=None),self.assertRaisesRegex(RuntimeError,'Konsole'):setup.run_install(setup.Options(),ROOT,self.execute,self.progress,self.home)
  self.assertEqual(self.calls,[])
 def test_missing_codex_is_installed_then_verified(self):
  with patch.object(setup,'codex_installed',side_effect=[False,True]):setup.run_install(setup.Options(mode='custom',decky=False),ROOT,self.execute,self.progress,self.home)
  self.assertTrue(any(any(str(x).endswith('install-codex.py') for x in c) for c in self.calls))
  self.events=[]
  with patch.object(setup,'codex_installed',return_value=False),self.assertRaisesRegex(RuntimeError,'not found'):setup.run_install(setup.Options(mode='custom',decky=False),ROOT,self.execute,self.progress,self.home)
  self.assertNotIn(('ready',1.0),self.events)
 def test_action_restrictions_are_preserved_until_custom_choice_changes_them(self):
  state=setup.resolve_state_dir(self.home);state.mkdir(parents=True);flag=state/'read-only';flag.write_text('on')
  setup.save_preferences(setup.Options(),self.home);self.assertTrue(flag.exists())
  setup.save_preferences(setup.Options(mode='custom',read_only=False),self.home);self.assertFalse(flag.exists())
  setup.save_preferences(setup.Options(mode='custom',read_only=True),self.home);self.assertTrue(flag.exists())
 def test_invalid_language_and_linked_preferences_are_rejected(self):
  with self.assertRaises(ValueError):setup.Options(language='ru;id')
  state=setup.resolve_state_dir(self.home);state.mkdir(parents=True);outside=self.home/'outside';outside.write_text('keep');(state/'language').symlink_to(outside)
  with self.assertRaises(ValueError):setup.save_preferences(setup.Options(),self.home)
  self.assertEqual(outside.read_text(),'keep')
 def test_existing_plugin_directory_is_reused_and_duplicates_are_preserved(self):
  parent=self.home/'homebrew/plugins';old=parent/'Codex';old.mkdir(parents=True);(old/'plugin.json').write_text('{"name":"Deck AI"}')
  self.assertEqual(setup.plugin_destination(self.home),old)
  second=parent/'Deck AI';second.mkdir();(second/'plugin.json').write_text('{"name":"Deck AI"}')
  with self.assertRaisesRegex(ValueError,'Two'):setup.plugin_destination(self.home)
  self.assertTrue(old.exists() and second.exists())
 def test_tampered_decky_installer_never_reaches_sudo(self):
  with patch.object(loader,'decky_installed',return_value=False),patch.object(loader.urllib.request,'urlopen',return_value=io.BytesIO(b'tampered')),patch.object(loader.subprocess,'run') as execute:
   with self.assertRaisesRegex(ValueError,'checksum'):loader.install()
   execute.assert_not_called()
 def test_existing_decky_is_not_reinstalled_or_downloaded(self):
  with patch.object(loader,'decky_installed',return_value=True),patch.object(loader.urllib.request,'urlopen') as fetch,patch.object(loader.subprocess,'run') as execute:
   loader.install();fetch.assert_not_called();execute.assert_not_called()
 def test_system_steps_do_not_enable_ssh_unless_selected(self):
  with patch.object(system,'decky_installed',return_value=True),patch.object(system.subprocess,'run') as execute:
   self.assertTrue(system.run_steps(decky=True)['ok']);self.assertFalse(any('sshd' in c.args[0] for c in execute.call_args_list));self.assertTrue(any(c.args[0]==['sudo','systemctl','enable','--now','plugin_loader'] for c in execute.call_args_list))
  with patch.object(system,'decky_installed',return_value=False),patch.object(system.subprocess,'run') as execute:
   with self.assertRaises(RuntimeError):system.run_steps(decky=True,loader=False)
   execute.assert_not_called()
 def test_unchecked_plugin_ignores_its_hidden_action_permission(self):
  state=setup.resolve_state_dir(self.home);state.mkdir(parents=True);flag=state/'read-only';flag.write_text('on')
  options=setup.Options(mode='custom',codex=False,decky=False,loader=True,read_only=False)
  setup.save_preferences(options,self.home);self.assertTrue(flag.exists());self.assertIsNone(options.read_only);self.assertFalse(options.loader)
 def test_repository_launcher_matches_release_and_embeds_graphical_brand(self):
  version=(ROOT/'VERSION').read_text().strip();text=(ROOT/'Install-Deck-AI.desktop').read_text()
  self.assertEqual(text,builder.launcher_text(version));self.assertIn('Terminal=false',text);self.assertIn('Name[ru]',text)

 def test_full_installer_cannot_race_an_active_one_click_transaction(self):
  import fcntl,os
  folder=setup.resolve_state_dir(self.home)/'updates';folder.mkdir(parents=True);fd=os.open(folder/'install.lock',os.O_CREAT|os.O_RDWR,0o600)
  try:
   fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
   with self.assertRaisesRegex(RuntimeError,'update is running'):setup.run_install(setup.Options(mode='custom',codex=False,decky=False),ROOT,self.execute,self.progress,self.home)
   self.assertEqual(self.calls,[])
  finally:os.close(fd)
