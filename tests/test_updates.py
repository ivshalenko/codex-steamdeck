"""Published assets, weekly scheduling, failure recovery and personal-state isolation."""
import shlex
import hashlib,importlib.util,io,json,os,shutil,stat,sys,tarfile,tempfile,unittest,urllib.error,zipfile
from pathlib import Path
from unittest.mock import patch
import updates
ROOT=Path(__file__).resolve().parents[1]
def load(name,filename):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/filename);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
manager=load('update_install_manager','manage-install.py');packager=load('update_plugin_package','package-plugin.py');builder=load('update_release_builder','build-release.py')
TARGET=(ROOT/'VERSION').read_text().strip();OLD='1.0.0-rc.15'
class Response(io.BytesIO):
 def __init__(self,data,url):super().__init__(data);self.headers={'Content-Length':str(len(data))};self.url=url
 def geturl(self):return self.url
class Adapter:
 def __init__(self,home,fail=False):self.home=home;self.fail=fail;self.calls=[]
 def ready(self):pass
 def install(self,archive,value,sha):
  self.calls.append(value);assert updates.digest(archive)==sha
  current=updates.find_plugin(self.home)
  if current:shutil.rmtree(current)
  if self.fail and value==TARGET:raise RuntimeError('simulated failure after unloading the plugin')
  with zipfile.ZipFile(archive) as z:z.extractall(self.home/'homebrew/plugins')
 def health(self,value):
  assert updates.installed(self.home)['plugin']==value
class UpdateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.artifacts=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.artifacts.cleanup)
  with patch.object(builder.subprocess,'run'),patch.object(builder.package,'check',return_value=(TARGET,manager.source_files(ROOT))):builder.build(Path(cls.artifacts.name))
  cls.assets={p.name:p.read_bytes() for p in Path(cls.artifacts.name).iterdir()}
 @classmethod
 def release(cls,value=TARGET):
  names=updates.required_names(value)
  return {'id':123,'tag_name':'v'+value,'published_at':'2026-11-04T10:00:00Z','draft':False,'prerelease':'-' in value,'body':'New version','assets':[{'name':n,'size':len(cls.assets.get(n,b'x')),'browser_download_url':updates.WEB+'/releases/download/v'+value+'/'+n,'digest':'sha256:'+hashlib.sha256(cls.assets.get(n,b'x')).hexdigest()} for n in names]}
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.home=Path(self.temp.name)/'user with spaces';self.home.mkdir();self.state=updates.resolve_state_dir(self.home);self.state.mkdir(parents=True)
  self.app=manager.install(ROOT,self.home);(self.app/'VERSION').write_text(OLD+'\n')
  manifest=updates.read_json(self.app/'install-manifest.json');manifest['version']=OLD;manifest['files'][str((self.app/'VERSION').relative_to(self.home))]=updates.digest(self.app/'VERSION');updates.atomic_json(self.app/'install-manifest.json',manifest)
  self.plugin=self.home/'homebrew/plugins/Deck AI';self.plugin.mkdir(parents=True)
  for rel,file in packager.files(ROOT).items():
   dest=self.plugin/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(file,dest)
  meta=updates.read_json(self.plugin/'package.json');meta['version']=OLD;updates.atomic_json(self.plugin/'package.json',meta)
  for name in ('auth.json','draft.txt','voice-language','read-only','provider-chats.json'):(self.state/name).write_text('private fixture: '+name)
  (self.app/'models/keep').mkdir(parents=True);(self.app/'models/keep/model').write_text('voice model')
  python=self.app/'venv/bin/python';python.parent.mkdir(parents=True);python.write_text('#!/bin/sh\nexec '+shlex.quote(sys.executable)+' \"$@\"\n');python.chmod(0o755)
  self.controller=updates.Controller(self.home,self.plugin,self.state)
  self.candidate=updates.release_candidate([self.release()],{'plugin':OLD},'preview')
 def worker(self,adapter=None):
  ident='a'*32;folder=self.controller.root/'jobs'/ident;folder.mkdir(parents=True,exist_ok=True)
  job={'id':ident,'home':str(self.home),'state':str(self.state),'plugin':str(self.plugin),'version':TARGET,'candidate':self.candidate,'phase':'queued','changed':False,'pluginAttempted':False,'restartApp':False}
  updates.atomic_json(folder/'job.json',job);updates.atomic_json(self.controller.root/'job.json',job)
  return updates.Worker(folder,adapter or Adapter(self.home))
 def network(self,url,*args,**kwargs):
  url=url.full_url if hasattr(url,'full_url') else url;name=url.rsplit('/',1)[-1]
  return Response(self.assets[name],url)
 def assert_private(self):
  for name in ('auth.json','draft.txt','voice-language','read-only','provider-chats.json'):self.assertEqual((self.state/name).read_text(),'private fixture: '+name)
  self.assertEqual((self.app/'models/keep/model').read_text(),'voice model')
 def verify_files(self,worker):
  for rel,sha in worker.manifest['appFiles'].items():self.assertEqual(updates.digest(self.app/rel),sha,rel)
  for rel,sha in worker.manifest['pluginFiles'].items():self.assertEqual(updates.digest(updates.find_plugin(self.home)/rel),sha,rel)
  worker.adapter.health(TARGET)
 def test_versions_compare_numerically_and_stable_follows_release_candidates(self):
  self.assertLess(updates.version('1.0.0-rc.9'),updates.version('1.0.0-rc.10'));self.assertLess(updates.version('1.0.0-rc.99'),updates.version('1.0.0'))
  for invalid in ('v1.0.0','01.0.0','1.0.0;id','1.0.0-rc.-1','1.0.0+unsafe'):
   with self.assertRaises(ValueError):updates.version(invalid)
 def test_checks_are_weekly_and_the_timestamp_survives_a_restart(self):
  self.assertTrue(self.controller.due(1000))
  with patch.object(updates,'request_json',return_value=([self.release()],'tag')),patch.object(updates.time,'time',return_value=1000):self.controller.check()
  again=updates.Controller(self.home,self.plugin,self.state)
  self.assertFalse(again.due(1000+7*24*60*60-1));self.assertTrue(again.due(1000+7*24*60*60))
  again.configure(False,'automatic');self.assertFalse(again.due(1000+20*24*60*60))
  with patch.object(updates,'request_json',return_value=([self.release()],'tag')) as fetch:again.check()
  fetch.assert_called_once();self.assertIsNotNone(again.status()['available'])
 def test_failed_check_is_not_retried_hourly_and_preserves_the_last_valid_offer(self):
  with patch.object(updates,'request_json',return_value=([self.release()],'tag')):self.controller.check()
  with patch.object(updates,'request_json',side_effect=OSError('offline')),patch.object(updates.time,'time',return_value=2000):self.controller.check()
  self.assertFalse(self.controller.due(2000+3600));self.assertEqual(self.controller.status()['available']['version'],TARGET);self.assertTrue(self.controller.status()['checkError'])
 def test_channel_filters_drafts_incomplete_assets_and_untrusted_urls(self):
  valid=self.release();valid['prerelease']=True;bad=self.release();bad['draft']=True
  incomplete=self.release();incomplete['assets'].pop()
  untrusted=self.release();untrusted['assets'][0]['browser_download_url']='https://other.example/update'
  self.assertIsNone(updates.release_candidate([valid],{'plugin':OLD},'stable'))
  self.assertIsNone(updates.release_candidate([None,bad,incomplete,untrusted],{'plugin':OLD},'preview'))
  self.assertEqual(updates.release_candidate([valid],{'plugin':OLD},'preview')['version'],TARGET)
 def test_cached_current_release_can_still_update_an_older_component(self):
  (self.app/'VERSION').write_text(TARGET)
  with patch.object(updates,'request_json',return_value=([self.release()],'tag')):self.controller.check()
  self.assertEqual(self.controller.status()['available']['version'],TARGET)
  meta=updates.read_json(self.plugin/'package.json');meta['version']=TARGET;updates.atomic_json(self.plugin/'package.json',meta)
  self.assertIsNone(self.controller.status()['available'])
  meta['version']=OLD;updates.atomic_json(self.plugin/'package.json',meta)
  with patch.object(updates,'request_json',return_value=(None,'tag')):self.controller.check()
  self.assertIsNotNone(self.controller.status()['available'])
 def test_notification_acknowledgement_survives_restart(self):
  with patch.object(updates,'request_json',return_value=([self.release()],'tag')):self.controller.check()
  self.assertTrue(self.controller.status()['notificationPending']);self.controller.acknowledge(TARGET)
  self.assertFalse(updates.Controller(self.home,self.plugin,self.state).status()['notificationPending'])
 def test_busy_work_and_a_live_desktop_task_prevent_starting_an_update(self):
  with patch.object(updates,'request_json',return_value=([self.release()],'tag')):self.controller.check()
  with self.assertRaisesRegex(ValueError,'Finish'):self.controller.begin(TARGET,guard=lambda:True)
  lease=updates.Lease(self.state);lease.publish(True)
  try:
   with self.assertRaisesRegex(ValueError,'Finish'):self.controller.begin(TARGET)
  finally:lease.close()
  self.assertFalse((self.controller.root/'job.json').exists())
 def test_a_detached_worker_receives_the_cross_process_lock_and_copied_runtime(self):
  with patch.object(updates,'request_json',return_value=([self.release()],'tag')):self.controller.check()
  with patch.object(updates.subprocess,'Popen') as spawn:self.controller.begin(TARGET)
  args=spawn.call_args;self.assertTrue(args.kwargs['start_new_session']);self.assertTrue(args.kwargs['pass_fds'])
  job=updates.active_job(self.state);folder=self.controller.root/'jobs'/job['id'];self.assertTrue((folder/'worker.py').is_file());self.assertTrue((folder/'runtime_paths.py').is_file())
  with self.assertRaisesRegex(ValueError,'previous update'):self.controller.begin(TARGET)
 def test_packaged_plugin_can_copy_its_worker_runtime_without_the_desktop_source_tree(self):
  spec=importlib.util.spec_from_file_location('packaged_updater',self.plugin/'runtime/updates.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  controller=module.Controller(self.home,self.plugin,self.state)
  with patch.object(module,'request_json',return_value=([self.release()],'tag')):controller.check()
  with patch.object(module.subprocess,'Popen'):controller.begin(TARGET)
  job=module.active_job(self.state);folder=controller.root/'jobs'/job['id'];self.assertTrue((folder/'runtime_paths.py').is_file());self.assertTrue((folder/'websockets-15.0.1-py3-none-any.whl').is_file())
 def test_tampered_download_cannot_reach_any_installer(self):
  worker=self.worker();before=updates.digest(self.app/'app.py')
  def changed(url,*args,**kwargs):
   request=url.full_url if hasattr(url,'full_url') else url
   return Response(b'tampered' if request.endswith('decky.zip') else self.assets[request.rsplit('/',1)[-1]],request)
  with patch.object(updates.urllib.request,'urlopen',side_effect=changed),patch.object(updates.subprocess,'run',return_value=type('Result',(),{'returncode':0,'stdout':'15.0.1'})()),patch.object(worker,'apply_app') as install:worker.run()
  install.assert_not_called();self.assertEqual(worker.job['phase'],'failed');self.assertFalse(worker.job['changed']);self.assertEqual(updates.digest(self.app/'app.py'),before);self.assert_private()
 def test_archive_path_traversal_and_symlinks_are_rejected(self):
  for name,kind in [('deck-ai-'+TARGET+'/../../outside',tarfile.REGTYPE),('deck-ai-'+TARGET+'/link',tarfile.SYMTYPE)]:
   file=self.home/'bad.tar'
   with tarfile.open(file,'w') as archive:member=tarfile.TarInfo(name);member.type=kind;member.linkname='/outside';archive.addfile(member)
   with self.assertRaises(ValueError):updates.unpack_source(file,self.home/'extract',TARGET)
  file=self.home/'bad.zip'
  with zipfile.ZipFile(file,'w') as archive:archive.writestr('../outside','bad')
  with self.assertRaises(ValueError):updates.inspect_plugin(file,TARGET,{})
 def test_success_updates_both_components_and_preserves_personal_state(self):
  worker=self.worker()
  with patch.object(updates.urllib.request,'urlopen',side_effect=self.network),patch.object(worker,'verify',side_effect=lambda:self.verify_files(worker)):worker.run()
  self.assertEqual(worker.job['phase'],'completed',worker.job.get('error'));self.assertEqual(updates.installed(self.home),{'plugin':TARGET,'companion':TARGET});self.assert_private()
 def test_plugin_failure_restores_both_components_even_after_its_folder_was_removed(self):
  worker=self.worker(Adapter(self.home,fail=True));before={str(p.relative_to(self.app)):p.read_bytes() for p in (self.app/'app.py',self.app/'VERSION')}
  with patch.object(updates.urllib.request,'urlopen',side_effect=self.network):worker.run()
  self.assertEqual(worker.job['phase'],'failed');self.assertIn('restored',worker.job['error']);self.assertEqual(updates.installed(self.home),{'plugin':OLD,'companion':OLD})
  for name,data in before.items():self.assertEqual((self.app/name).read_bytes(),data)
  self.assertEqual(worker.adapter.calls,[TARGET,OLD]);self.assert_private()
 def test_startup_health_failure_also_rolls_back(self):
  worker=self.worker()
  with patch.object(updates.urllib.request,'urlopen',side_effect=self.network),patch.object(worker,'verify',side_effect=RuntimeError('startup failed')):worker.run()
  self.assertEqual(worker.job['phase'],'failed');self.assertIn('startup failed',worker.job['error']);self.assertEqual(worker.adapter.calls,[TARGET,OLD]);self.assertEqual(updates.installed(self.home),{'plugin':OLD,'companion':OLD});self.assert_private()
 def test_crash_recovery_restores_an_applied_companion_and_preserves_new_user_edits(self):
  worker=self.worker()
  with patch.object(updates.urllib.request,'urlopen',side_effect=self.network):worker.fetch()
  worker.quiesce();worker.snapshot();worker.write('installing');worker.apply_app()
  recovered=updates.Worker(worker.folder,worker.adapter);recovered.run(recover=True)
  self.assertEqual((self.app/'VERSION').read_text().strip(),OLD);self.assertEqual(recovered.job['phase'],'failed');self.assert_private()
  # Do not overwrite an edit made after a later update's file commit.
  worker=self.worker()
  with patch.object(updates.urllib.request,'urlopen',side_effect=self.network):worker.fetch()
  worker.snapshot();worker.write('installing');worker.apply_app();(self.app/'app.py').write_text('my concurrent edit')
  with self.assertRaisesRegex(RuntimeError,'preserved'):worker.rollback()
  self.assertEqual((self.app/'app.py').read_text(),'my concurrent edit')
 def test_manifest_cannot_target_credentials_models_or_external_files(self):
  for relative in ('.ssh/id_ed25519','../escape','.local/state/deck-ai/auth.json','.local/share/deck-ai/models/private','.local/share/deck-ai/auth.json'):
   with self.assertRaises(ValueError):updates.safe_managed(self.home,self.app,relative)
 def test_plugin_only_installation_does_not_create_a_desktop_companion(self):
  shutil.rmtree(self.app);worker=self.worker()
  with patch.object(updates.urllib.request,'urlopen',side_effect=self.network):worker.run()
  self.assertEqual(worker.job['phase'],'completed',worker.job.get('error'));self.assertFalse((self.app/'app.py').exists());self.assertEqual(updates.installed(self.home),{'plugin':TARGET})
 def test_managed_launchers_cannot_follow_symlinks_to_personal_files(self):
  launcher=self.home/'.local/bin/deck-ai';launcher.unlink();launcher.symlink_to(self.state/'auth.json')
  with self.assertRaises(ValueError):updates.safe_managed(self.home,self.app,'.local/bin/deck-ai')
  self.assertEqual((self.state/'auth.json').read_text(),'private fixture: auth.json')
 def test_update_clears_only_owned_python_bytecode_and_leaves_voice_cache_alone(self):
  cache=self.app/'__pycache__';cache.mkdir();(cache/'app.cpython-39.pyc').write_bytes(b'old compiled code')
  voice_cache=self.app/'models/__pycache__';voice_cache.mkdir();(voice_cache/'app.cpython-39.pyc').write_bytes(b'user model cache')
  updates.clear_bytecode(self.app,['app.py']);self.assertFalse((cache/'app.cpython-39.pyc').exists());self.assertTrue((voice_cache/'app.cpython-39.pyc').exists())

class BridgeUpdateGuardTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location('updater_bridge_guard',ROOT/'decky/bridge.py');cls.bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.bridge)
 def test_active_update_blocks_new_tasks_but_not_the_health_check(self):
  with tempfile.TemporaryDirectory() as root,patch.object(self.bridge,'STATE',Path(root)):
   updates.atomic_json(Path(root)/'updates/job.json',{'phase':'installing'})
   with self.assertRaisesRegex(ValueError,'updating'):self.bridge.call('send',{})
   self.assertEqual(self.bridge.call('update_health',{})['protocol'],1)
   self.assertEqual(self.bridge.maintenance_inflight,0)
 def test_action_failure_releases_its_update_guard(self):
  with patch.object(self.bridge,'call_view',side_effect=RuntimeError('failed action')):
   with self.assertRaises(RuntimeError):self.bridge.call('file_write',{})
  self.assertEqual(self.bridge.maintenance_inflight,0)
 def test_old_failed_queue_items_do_not_block_updates_but_pending_work_does(self):
  with patch.object(self.bridge,'active',False),patch.object(self.bridge,'provider_active',False),patch.object(self.bridge,'approvals',{}),patch.object(self.bridge,'voice_state','idle'),patch.object(self.bridge,'all_tasks',return_value=[]),patch.object(self.bridge,'outbox',[{'status':'error'}]):
   self.assertFalse(self.bridge.update_busy())
   self.bridge.outbox.append({'status':'queued'});self.assertTrue(self.bridge.update_busy())
 def test_manifest_compatibility_and_duplicate_checksums_fail_closed(self):
  with self.assertRaises(ValueError):updates.validate_manifest({'protocol':999,'version':TARGET},TARGET)
  with tempfile.TemporaryDirectory() as root:
   path=Path(root)/'SHA256SUMS.txt';path.write_text('0'*64+'  file.zip\n'+'1'*64+'  file.zip\n')
   with self.assertRaises(ValueError):updates.checksums(path)

class UpdateModalGuardTests(unittest.TestCase):
 def test_only_the_confirmed_package_modal_can_be_closed(self):
  sha='a'*64;page=[{'id':'ui','title':'Steam Big Picture Mode','url':'https://steamloopback.host/?browserType=4'}]
  adapter=updates.DeckyAdapter(Path('/nonexistent'))
  def evaluate(expression,**kwargs):
   program='''const vm=require('node:vm');const expression=EXPRESSION;
const results=[];
for(const props of [
 {artifact:'Deck AI',version:TARGET_VERSION,hash:'a'.repeat(64)},
 {artifact:'Another plugin',version:TARGET_VERSION,hash:'a'.repeat(64)},
 {artifact:'Deck AI',version:OLD_VERSION,hash:'a'.repeat(64)},
 {artifact:'Deck AI',version:TARGET_VERSION,hash:'b'.repeat(64)}]){
 let closed=0;props.closeModal=()=>closed++;
 const node={'__reactFiber$test':{memoizedProps:props,return:null}};
 vm.runInNewContext(expression,{document:{querySelectorAll:()=>[node]}});results.push(closed);
}
process.stdout.write(JSON.stringify(results));'''.replace('EXPRESSION',json.dumps(expression)).replace('TARGET_VERSION',json.dumps(TARGET)).replace('OLD_VERSION',json.dumps(OLD))
   result=__import__('subprocess').run(['node','-e',program],capture_output=True,text=True,check=True)
   self.assertEqual(json.loads(result.stdout),[1,0,0,0])
  with patch.object(updates.urllib.request,'urlopen',return_value=Response(json.dumps(page).encode(),'http://127.0.0.1:8080/json/list')),patch.object(adapter,'evaluate',side_effect=evaluate):adapter.dismiss(TARGET,sha)
