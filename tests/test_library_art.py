import sys
import base64,fcntl,hashlib,importlib.util,json,os,struct,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'decky')]
spec=importlib.util.spec_from_file_location('library_art_tested',ROOT/'decky/library_art.py');art=importlib.util.module_from_spec(spec);spec.loader.exec_module(art)
PNG=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a7v8AAAAASUVORK5CYII=')
def vdf(values):
 result=b''
 for key,value in values.items():
  field=str(key).encode()+b'\0'
  if isinstance(value,dict):result+=b'\0'+field+vdf(value)
  elif isinstance(value,int):result+=b'\2'+field+struct.pack('<I',value)
  else:result+=b'\1'+field+str(value).encode()+b'\0'
 return result+b'\10'
class Adapter:
 def __init__(self,target,grid):self.target=target;self.grid=grid;self.calls=[];self.icons=[]
 def evaluate(self,expression):
  self.calls.append(expression)
  if 'appStore.allApps' in expression:return dict(self.target)
  data=json.loads(expression.split('})(',1)[1][:-1]);self.icons.append(data['icon']);appid=data['appid']
  for image in data['images']:
   suffix=art.KINDS[image['kind']][1];path=self.grid/(str(appid)+suffix+'.png')
   if image['data'] is None:path.unlink(missing_ok=True)
   else:path.write_bytes(base64.b64decode(image['data']))
  position=self.grid/(str(appid)+'.json')
  if data.get('position') is None:position.unlink(missing_ok=True)
  else:position.write_text(json.dumps({'nVersion':1,'logoPosition':data['position']}))
  return True
class LibraryArtworkTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.home=self.root/'home with spaces';self.plugin=self.root/'plugin';self.state=self.root/'state'
  app=self.home/'.local/share/deck-ai';app.mkdir(parents=True);(app/'app.py').write_text('');(app/'deck-ai.png').write_bytes(PNG)
  launcher=self.home/'.local/bin/deck-ai-steam';launcher.parent.mkdir(parents=True);launcher.write_text('launcher')
  folder=self.plugin/'artwork';folder.mkdir(parents=True);meta={'files':{}}
  for name in [*(v[0] for v in art.KINDS.values()),'icon']:
   path=folder/(name+'.png');path.write_bytes(PNG+name.encode());meta['files'][path.name]={'size':[1,1],'sha256':art.sha(path)}
  (folder/'manifest.json').write_text(json.dumps(meta));(self.plugin/'package.json').write_text('{"version":"1.0.0-rc.18"}')
  self.grid=self.home/'.local/share/Steam/userdata/123/config/grid';self.grid.mkdir(parents=True)
  self.fields={'appid':42,'AppName':'Deck AI','Exe':'"'+str(launcher)+'"','icon':'/previous/custom/icon.png'};self.save_shortcut()
  self.target={'appid':42,'account':str(art.STEAM_ID_BASE+123),'created':False};self.adapter=Adapter(self.target,self.grid)
 def save_shortcut(self):(self.grid.parent/'shortcuts.vdf').write_bytes(vdf({'shortcuts':{'0':self.fields}}))
 def apply(self,restore=False):return art.apply(self.plugin,self.home,self.state,restore,adapter=self.adapter)
 def test_apply_restore_is_idempotent_and_never_changes_another_game(self):
  position={'pinnedPosition':'CenterCenter','nWidthPct':30,'nHeightPct':40};(self.grid/'42.json').write_text(json.dumps({'nVersion':1,'logoPosition':position}))
  (self.grid/'42p.png').write_bytes(b'previous cover');other=self.grid/'999p.png';other.write_bytes(b'other game')
  result=self.apply();self.assertTrue(result['hasBackup']);record=art.read_json(self.state/'library-artwork/latest.json');self.assertEqual(len(record['installed']),4);self.assertEqual((self.grid/'42.png').read_bytes(),(self.plugin/'artwork/header.png').read_bytes())
  self.assertTrue(self.apply()['unchanged']);self.assertEqual(art.read_json(self.state/'library-artwork/latest.json')['id'],record['id'])
  self.assertTrue(self.apply(True)['restored']);self.assertEqual((self.grid/'42p.png').read_bytes(),b'previous cover');self.assertEqual(other.read_bytes(),b'other game');self.assertEqual(self.adapter.icons[-1],'/previous/custom/icon.png');self.assertEqual(art.read_json(self.grid/'42.json')['logoPosition'],position)
  self.assertFalse((self.grid/'42_hero.png').exists())
 def test_tampered_packaged_image_is_rejected_before_any_steam_call(self):
  (self.plugin/'artwork/hero.png').write_bytes(b'changed')
  with self.assertRaisesRegex(ValueError,'verification'):self.apply()
  self.assertFalse(self.adapter.calls);self.assertFalse(list(self.grid.glob('*.png')))
 def test_requested_setup_retries_then_completes_without_a_duplicate(self):
  art.request_setup(self.state);self.adapter.evaluate_original=self.adapter.evaluate
  with patch.object(self.adapter,'evaluate',side_effect=RuntimeError('Steam not ready')):result=art.attempt_setup(self.plugin,self.home,self.state,adapter=self.adapter)
  self.assertTrue(result['pending']);self.assertIn('Steam not ready',result['error'])
  result=art.attempt_setup(self.plugin,self.home,self.state,adapter=self.adapter);self.assertFalse(result['pending']);self.assertEqual(result['result']['appId'],42);before=len(self.adapter.calls)
  art.attempt_setup(self.plugin,self.home,self.state,adapter=self.adapter);self.assertEqual(len(self.adapter.calls),before)
 def test_automatic_setup_preserves_later_custom_artwork(self):
  self.apply();(self.grid/'42p.png').write_bytes(b'user changed the cover');art.request_setup(self.state)
  result=art.attempt_setup(self.plugin,self.home,self.state,adapter=self.adapter);self.assertFalse(result['pending']);self.assertTrue(result['result']['preservedCustomArtwork']);self.assertEqual((self.grid/'42p.png').read_bytes(),b'user changed the cover')
 def test_cancelled_setup_does_not_contact_steam(self):
  art.request_setup(self.state,False);result=art.attempt_setup(self.plugin,self.home,self.state,adapter=self.adapter);self.assertFalse(result['pending']);self.assertFalse(self.adapter.calls)
 def test_older_automatic_installation_schedules_library_after_update(self):
  self.state.mkdir(exist_ok=True)
  (self.state/'setup-choices.json').write_text('{"mode":"automatic","components":{"decky":true}}')
  with patch.object(art.threading,'Thread') as worker:art.start_setup_worker(self.plugin,self.home,self.state)
  self.assertTrue(art.read_json(self.state/'library-artwork/setup.json')['pending']);worker.return_value.start.assert_called_once();art._SETUP_WORKERS.discard(str(self.state.resolve()))
 def test_custom_or_opted_out_installation_does_not_add_library_on_update(self):
  self.state.mkdir(exist_ok=True)
  for choices in ({'mode':'custom','components':{}},{'mode':'automatic','components':{'steam':False}}):
   (self.state/'setup-choices.json').write_text(json.dumps(choices))
   with patch.object(art.threading,'Thread') as worker:art.start_setup_worker(self.plugin,self.home,self.state)
   worker.assert_not_called();self.assertFalse((self.state/'library-artwork/setup.json').exists())
 def test_restore_preserves_an_artwork_edit_made_after_application(self):
  self.apply();(self.grid/'42p.png').write_bytes(b'new custom picture')
  with self.assertRaisesRegex(ValueError,'preserved'):self.apply(True)
  self.assertEqual((self.grid/'42p.png').read_bytes(),b'new custom picture')
 def test_a_shortcut_name_collision_cannot_change_unrelated_artwork(self):
  self.fields['Exe']='"/games/different-app"';self.save_shortcut();(self.grid/'42p.png').write_bytes(b'unrelated')
  with self.assertRaisesRegex(ValueError,'unrelated'):self.apply()
  self.assertEqual((self.grid/'42p.png').read_bytes(),b'unrelated');self.assertEqual(len(self.adapter.calls),1)
  self.adapter.target['appid']=2**32
  with self.assertRaisesRegex(ValueError,'invalid'):self.apply()
 def test_linked_grid_and_a_parallel_operation_are_rejected(self):
  other=self.root/'outside';other.mkdir();self.grid.rmdir();self.grid.symlink_to(other,target_is_directory=True)
  with self.assertRaisesRegex(ValueError,'Linked'):self.apply()
  self.grid.unlink();self.grid.mkdir();lock=self.state/'library-artwork/operation.lock';fd=os.open(lock,os.O_RDWR);fcntl.flock(fd,fcntl.LOCK_EX)
  try:
   with self.assertRaisesRegex(ValueError,'already'):self.apply()
  finally:os.close(fd)
  shared=self.state/'updates/install.lock';shared.parent.mkdir(exist_ok=True);fd=os.open(shared,os.O_CREAT|os.O_RDWR,0o600);fcntl.flock(fd,fcntl.LOCK_EX);before=len(self.adapter.calls)
  try:
   with self.assertRaisesRegex(ValueError,'installation or update'):self.apply()
   self.assertEqual(len(self.adapter.calls),before)
  finally:os.close(fd)
 def test_native_target_guard_rejects_namesakes_duplicates_and_avoids_duplicate_creation(self):
  program='''const vm=require('node:vm');const code=CODE;
async function check(entries,create){let added=0;const apps={RegisterForAppDetails:(id,cb)=>{queueMicrotask(()=>cb({unAppID:id,strShortcutExe:entries.find(e=>e.appid===id).exe}));return {unregister(){}}},AddShortcut:async()=>{added++;return 99}};let result,error;try{result=await vm.runInNewContext(code.replace('CREATE',String(create)).replace('PAYLOAD',JSON.stringify({accounts:['76561197960265851'],launchers:['/managed/deck-ai-steam'],exe:'/managed/deck-ai-steam',directory:'/managed'})),{appStore:{allApps:entries},SteamClient:{Apps:apps},window:{friendStore:{currentUserSteamID:'76561197960265851'}},setTimeout,clearTimeout,queueMicrotask});}catch(e){error=e.message}return {result,error,added};}
(async()=>{const good={appid:42,app_type:1073741824,display_name:'Deck AI',exe:'"/managed/deck-ai-steam"'};const a=await check([good],true),b=await check([{...good,exe:'/other'}],true),c=await check([good,{...good,appid:43}],true),d=await check([],true),e=await check([],false);if(a.result.appid!==42||a.added||!b.error||!c.error||d.added!==1||!e.error||e.added)process.exit(2);console.log('guard passed')})();'''.replace('CODE',json.dumps(art.TARGET_JS))
  self.assertIn('guard passed',subprocess.check_output(['node','-e',program],text=True))
