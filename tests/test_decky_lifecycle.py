"""Old subprocess readers must never cancel calls to a replacement bridge."""
import ast,io,json,threading,unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch

class DeckyLifecycleTests(unittest.TestCase):
 def test_old_reader_only_finishes_its_own_requests(self):
  path=Path(__file__).resolve().parents[1]/'decky/main.py'
  tree=ast.parse(path.read_text());node=next(n for n in tree.body if isinstance(n,ast.ClassDef))
  scope={'threading':threading,'json':json}
  exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),scope)
  plugin=scope['Plugin']();plugin.lock=threading.RLock()
  old=SimpleNamespace(stdout=io.StringIO('{"id":2,"result":"obsolete"}\n'))
  new=object();gone={'child':old,'event':threading.Event()};fresh={'child':new,'event':threading.Event()}
  plugin.pending={1:gone,2:fresh};plugin.read_bridge(old)
  self.assertTrue(gone['event'].is_set());self.assertFalse(fresh['event'].is_set())
  self.assertEqual(plugin.pending,{2:fresh});self.assertNotIn('response',fresh)

 def test_eof_waits_for_snapshot_without_submitting_during_shutdown(self):
  from test_remote_speed import bridge
  entered=threading.Event();closing=threading.Event();watch_stop=threading.Event()
  client=Mock(connected=True);client.request.return_value={'data':[]}
  def request(method,params):
   entered.set()
   self.assertTrue(closing.wait(2),'stdin EOF should begin orderly shutdown')
   bridge.refresh_threads(force=True)
   return {'ready':True}
  def stdin():
   yield json.dumps({'id':1,'method':'snapshot'})+'\n'
   self.assertTrue(entered.wait(2),'snapshot must be in progress before EOF')
  output=io.StringIO()
  with ThreadPoolExecutor(max_workers=2) as pool, \
       patch.multiple(bridge,jobs=pool,stopping=closing,bridge=client,cache=[],
                      thread_caches={},thread_cache_times={},remote_host='',
                      watch_stops={'Mac':watch_stop},watch_backends={}), \
       patch.object(bridge,'load_state'),patch.object(bridge,'reconcile_watchers'), \
       patch.object(bridge,'get_updater'),patch.object(bridge,'pump'), \
       patch.object(bridge,'_call',side_effect=request), \
       patch.object(bridge,'subscribe_running') as subscribe, \
       patch.object(bridge.sys,'stdin',stdin()),patch.object(bridge.sys,'stdout',output):
   bridge.main()
   self.assertEqual(json.loads(output.getvalue()),{'id':1,'result':{'ready':True}})
   self.assertTrue(watch_stop.is_set());subscribe.assert_not_called()
   client.close.assert_called_once()
   with self.assertRaisesRegex(RuntimeError,'Deck AI перезапускается'):
    bridge.submit_job(lambda:None)
