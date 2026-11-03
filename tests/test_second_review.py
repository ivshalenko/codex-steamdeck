"""User-visible failure cases found during the second release review."""
import asyncio,importlib.util,io,json,os,subprocess,sys,tempfile,threading,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
bridge=load('review_history','decky/bridge.py');pairing=load('review_pairing','scripts/connect-deck.py');worker=load('review_worker','decky/main.py')
class HistoryFailureTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  bridge.STATE=Path(self.temp.name);bridge.thread_id='selected';bridge.provider='codex';bridge.remote_host='';bridge.bridge=Mock(connected=True)
  bridge.cache=[{'id':'selected','name':'My chat'}];bridge.history_caches={};bridge.history_cache_times={};bridge.snapshot_cache={};bridge.outbox=[];bridge.model_cache_time=time.time();bridge.cache_media_time=time.time();bridge.model_catalog=[];bridge.active=False
  for name,value in [('connected',None),('refresh_threads',None),('read_account',{'account':None}),('ssh_hosts',[]),('multilingual_ready',False)]:
   p=patch.object(bridge,name,return_value=value);p.start();self.addCleanup(p.stop)
 def test_first_history_failure_is_not_an_empty_success(self):
  bridge.bridge.request.side_effect=TimeoutError('history timeout');snapshot=bridge.get_snapshot()
  self.assertFalse(snapshot['ready']);self.assertIn('history timeout',snapshot['status'])
 def test_cached_history_has_warning_and_recovers_without_losing_messages(self):
  thread={'turns':[{'items':[{'id':'answer','type':'agentMessage','text':'Saved answer'}]}]};bridge.history_caches[('', 'selected')]=thread
  bridge.bridge.request.side_effect=TimeoutError('history timeout');snapshot=bridge.get_snapshot()
  self.assertEqual(snapshot['messages'][0]['text'],'Saved answer');self.assertTrue(snapshot.get('historyWarning'))
  bridge.bridge.request.side_effect=None;bridge.bridge.request.return_value={'thread':thread};snapshot=bridge.get_snapshot();self.assertFalse(snapshot.get('historyWarning'))
 def test_older_selected_chat_reuses_cache_even_outside_first_list_page(self):
  bridge.cache=[];bridge.history_caches[('', 'selected')]={'turns':[]};bridge.history_cache_times[('', 'selected')]=time.time()
  bridge.get_snapshot();bridge.get_snapshot();bridge.bridge.select_thread.assert_not_called();bridge.bridge.request.assert_not_called()

class PairingUpdateTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.home=Path(self.temp.name);self.ssh=self.home/'.ssh';self.ssh.mkdir();self.key=self.ssh/'id_ed25519_deck_ai';self.key.write_text('existing private fixture');self.key.with_suffix('.pub').write_text('ssh-ed25519 PUBLIC_FIXTURE')
 def test_similar_ip_prefix_never_reuses_wrong_address(self):
  pairing.configure('192.0.2.154',self.home);pairing.configure('192.0.2.15',self.home)
  config=(self.ssh/'config').read_text();self.assertIn('HostName 192.0.2.15\n',config);self.assertNotIn('HostName 192.0.2.154\n',config)
 def test_managed_ip_update_preserves_other_hosts_and_private_key(self):
  original='Host work\n    HostName workstation\n';(self.ssh/'config').write_text(original)
  pairing.configure('192.0.2.15',self.home);pairing.configure('192.0.2.16',self.home)
  self.assertIn(original,(self.ssh/'config').read_text());self.assertEqual(self.key.read_text(),'existing private fixture');self.assertTrue(list(self.ssh.glob('config.before-deck-ai*')))
 def test_general_host_defaults_cannot_override_managed_deck_user(self):
  (self.ssh/'config').write_text('Host *\n    User somebody_else\n')
  pairing.configure('192.0.2.15',self.home);config=(self.ssh/'config').read_text();self.assertLess(config.index('Host deck-ai'),config.index('Host *'))
 @unittest.skipUnless(pairing.shutil.which('ssh'),'OpenSSH parser required')
 def test_global_options_keep_applying_to_other_hosts(self):
  (self.ssh/'config').write_text('ServerAliveInterval 37\nHost work\n    HostName workstation\n')
  pairing.configure('192.0.2.15',self.home)
  r=subprocess.run([pairing.shutil.which('ssh'),'-G','-F',str(self.ssh/'config'),'work'],capture_output=True,text=True,check=True)
  self.assertIn('serveraliveinterval 37',r.stdout)
  r=subprocess.run([pairing.shutil.which('ssh'),'-G','-F',str(self.ssh/'config'),'deck-ai'],capture_output=True,text=True,check=True)
  self.assertIn('user deck\n',r.stdout);self.assertIn('hostname 192.0.2.15\n',r.stdout)
 def test_custom_alias_is_preserved_without_rewriting(self):
  original='Host deck-ai\n    HostName my-custom-host\n    ProxyJump office\n';(self.ssh/'config').write_text(original)
  with self.assertRaises(ValueError):pairing.configure('192.0.2.15',self.home)
  self.assertEqual((self.ssh/'config').read_text(),original)
 def test_invalid_hostname_and_ipv6_zone_injection_are_rejected(self):
  for address in ['host..local','999.1.2.3','fe80::1%\nProxyCommand evil']:
   with self.subTest(address=address):self.assertFalse(pairing.valid_address(address))

class WorkerLifecycleTests(unittest.TestCase):
 def plugin(self):
  p=worker.Plugin();p.lock=threading.RLock();p.pending={};p.seq=0;return p
 def test_valid_json_noise_does_not_break_rpc_reader(self):
  p=self.plugin();child=SimpleNamespace(stdout=io.StringIO('null\n[]\n{"id": []}\n{"id": 1, "result": "ok"}\n'))
  future={'child':child,'event':threading.Event()};p.pending={1:future};p.read_bridge(child)
  self.assertEqual(future.get('response'),{'id':1,'result':'ok'})
 def test_send_timeout_does_not_recommend_duplicate_resubmission(self):
  p=self.plugin();p.child=SimpleNamespace(stdin=io.StringIO());p.start_bridge=Mock()
  with self.assertRaisesRegex(RuntimeError,'очеред'):p.rpc_sync('send',{},.001)
 def test_unload_reaps_own_worker_and_completes_waiters(self):
  p=self.plugin();p.child=subprocess.Popen([sys.executable,'-u','-c','import sys; sys.stdin.readline()'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  child=p.child
  def cleanup():
   if child.poll() is None:child.kill()
   child.wait(timeout=3)
   for stream in (child.stdin,child.stdout,child.stderr):stream.close()
  self.addCleanup(cleanup)
  future={'child':child,'event':threading.Event()};p.pending={1:future}
  asyncio.run(p._unload());self.assertIsNotNone(child.poll());self.assertTrue(future['event'].is_set())
