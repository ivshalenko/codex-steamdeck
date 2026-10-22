"""Old subprocess readers must never cancel calls to a replacement bridge."""
import ast,io,json,threading,unittest
from pathlib import Path
from types import SimpleNamespace

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
