"""Fresh plugin install works without the desktop companion; upgrades are reversible."""
import importlib.util,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
def load(name,relative):
 s=importlib.util.spec_from_file_location(name,ROOT/relative);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
installer=load('plugin_installer_test','scripts/install-plugin.py')
class PluginInstallTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.home=Path(self.temp.name);self.target=self.home/'homebrew/plugins/Codex'
 def test_fresh_plugin_snapshot_without_companion_or_python_packages(self):
  installer.install(ROOT,self.target)
  code='''import runpy,sys,json
sys.path.insert(0,sys.argv[1])
b=runpy.run_path(sys.argv[1]+'/bridge.py',run_name='test_bridge')
b['_get_snapshot'].__globals__['device'].CODEX='/missing/codex'
b['_get_snapshot'].__globals__['CODEX']='/missing/codex'
result=b['get_snapshot']()
print(json.dumps({'ready':result['ready'],'provider':result['provider'],'messages':result['messages']}))
'''
  r=subprocess.run([sys.executable,'-S','-c',code,str(self.target)],capture_output=True,text=True,env={**os.environ,'HOME':str(self.home)},timeout=15)
  self.assertEqual(r.returncode,0,r.stderr);data=json.loads(r.stdout);self.assertFalse(data['ready']);self.assertEqual(data['provider'],'codex')
 def test_update_retains_old_plugin_for_rollback(self):
  installer.install(ROOT,self.target);(self.target/'local-marker').write_text('old-version')
  backup=Path(installer.install(ROOT,self.target));self.assertEqual((backup/'local-marker').read_text(),'old-version');self.assertFalse((self.target/'local-marker').exists())
 def test_failed_replacement_restores_previous_plugin(self):
  installer.install(ROOT,self.target);(self.target/'local-marker').write_text('keep')
  original=installer.os.replace
  def failure(source,target):
   if str(source).split('/')[-1].startswith('.deck-ai-staging-'):raise OSError('disk failure')
   return original(source,target)
  with patch.object(installer.os,'replace',side_effect=failure):
   with self.assertRaises(OSError):installer.install(ROOT,self.target)
  self.assertEqual((self.target/'local-marker').read_text(),'keep')
 def test_unrelated_destination_is_never_removed(self):
  self.target.mkdir(parents=True);(self.target/'plugin.json').write_text('{"name":"Other plugin"}')
  with self.assertRaises(ValueError):installer.install(ROOT,self.target)
  self.assertEqual(json.loads((self.target/'plugin.json').read_text())['name'],'Other plugin')
  with self.assertRaises(ValueError):installer.install(ROOT,self.home)
