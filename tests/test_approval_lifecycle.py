"""An approval answered on another device must disappear without another response."""
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import Mock, patch
from test_remote_speed import bridge


class ApprovalLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.backend=Mock(connected=True)
        p=patch.multiple(bridge,STATE=Path(self.temp.name),approvals={},notifications=[],
                         remote_host='',thread_id='chat',active=False,bridge=self.backend,
                         outbox=[],cache=[],history_cache_times={},watch_backends={})
        p.start();self.addCleanup(p.stop)

    def request(self,ident=77,host='',thread='chat',turn='turn',item='cmd'):
        msg={'id':ident,'method':'item/commandExecution/requestApproval',
             'params':{'threadId':thread,'turnId':turn,'itemId':item,'command':'cat brief.txt'}}
        (bridge.event if not host else bridge.watch_event(host))(msg)

    def test_resolution_from_other_client_clears_exact_request_without_answering(self):
        self.request();self.request(78)
        bridge.event({'method':'serverRequest/resolved','params':{'threadId':'chat','requestId':77}})
        self.assertNotIn('77',bridge.approvals);self.assertIn('78',bridge.approvals)
        self.backend.respond.assert_not_called()

    def test_same_request_id_on_other_host_or_thread_is_preserved(self):
        self.request();self.request(host='Mac');self.request(78,thread='different')
        bridge.event({'method':'serverRequest/resolved','params':{'threadId':'different','requestId':77}})
        self.assertEqual(set(bridge.approvals),{'77','Mac|77','78'})
        bridge.watch_event('Mac')({'method':'serverRequest/resolved','params':{'threadId':'chat','requestId':77}})
        self.assertEqual(set(bridge.approvals),{'77','78'})

    def test_string_request_id_and_duplicate_resolution_are_safe(self):
        self.request('server-1')
        event={'method':'serverRequest/resolved','params':{'threadId':'chat','requestId':'server-1'}}
        bridge.event(event);bridge.event(event)
        self.assertFalse(bridge.approvals)

    def test_item_completion_fallback_only_clears_that_item(self):
        self.request();self.request(78,item='other')
        bridge.event({'method':'item/completed','params':{'threadId':'chat','item':{'id':'cmd','type':'commandExecution','status':'completed'}}})
        self.assertEqual(set(bridge.approvals),{'78'})

    def test_old_turn_completion_cannot_clear_new_turn_approval(self):
        self.request(turn='new')
        bridge.event({'method':'turn/completed','params':{'threadId':'chat','turn':{'id':'old','status':'completed'}}})
        self.assertIn('77',bridge.approvals)
        bridge.event({'method':'turn/completed','params':{'threadId':'chat','turn':{'id':'new','status':'interrupted'}}})
        self.assertFalse(bridge.approvals)

    def test_legacy_approval_without_turn_id_clears_when_its_thread_ends(self):
        self.request(turn=None);self.request(78,thread='different',turn=None)
        bridge.event({'method':'turn/completed','params':{'threadId':'chat','turn':{'status':'completed'}}})
        self.assertEqual(set(bridge.approvals),{'78'})

    def test_watched_completion_clears_only_that_hosts_turn(self):
        self.request();self.request(host='Mac');self.request(78,host='Mac',turn='new')
        bridge.watch_event('Mac')({'method':'turn/completed','params':{'threadId':'chat','turn':{'id':'turn','status':'completed'}}})
        self.assertEqual(set(bridge.approvals),{'77','Mac|78'})

    def test_late_click_after_resolution_cannot_send_a_second_decision(self):
        self.request()
        bridge.event({'method':'serverRequest/resolved','params':{'threadId':'chat','requestId':77}})
        self.assertEqual(bridge.decide_approval('77','accept'),{'decided':False,'alreadyResolved':True})
        self.backend.respond.assert_not_called()

    def test_concurrent_clicks_send_only_one_decision(self):
        self.request()
        with ThreadPoolExecutor(max_workers=4) as pool:
            results=list(pool.map(lambda _:bridge.decide_approval('77','accept'),range(12)))
        self.assertEqual(sum(r['decided'] for r in results),1)
        self.backend.respond.assert_called_once_with(77,{'decision':'accept'})

