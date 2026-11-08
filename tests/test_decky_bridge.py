"""Regression coverage for Decky snapshots and recovery, without network calls."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import shutil,subprocess
from unittest.mock import Mock, patch

spec=importlib.util.spec_from_file_location('decky_bridge_test',Path(__file__).resolve().parents[1]/'decky/bridge.py')
bridge=importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

class DeckyBridgeTests(unittest.TestCase):
    def test_desktop_uuid_draft_opens_in_decky_without_requesting_a_rollout(self):
        import json,time,uuid
        ident=str(uuid.uuid4());draft={'id':ident,'name':'New chat','turns':[],'preview':''}
        (bridge.STATE/'empty-chats.json').write_text(json.dumps({ident:draft}));(bridge.STATE/'thread-id').write_text(ident)
        bridge.thread_id=ident;bridge.bridge=Mock(connected=True);bridge.model_cache_time=bridge.cache_media_time=time.time();bridge.history_caches={};bridge.history_cache_times={};bridge.model_catalog=[]
        with patch.object(bridge,'connected'),patch.object(bridge,'refresh_threads'),patch.object(bridge,'read_account',return_value={'account':None}),patch.object(bridge,'ssh_hosts',return_value=[]):result=bridge.get_snapshot()
        self.assertTrue(result['ready']);self.assertEqual(result['threadId'],ident);self.assertEqual(result['messages'],[]);bridge.bridge.request.assert_not_called();bridge.bridge.select_thread.assert_not_called()
    def test_first_decky_send_promotes_desktop_draft_before_queueing(self):
        import json,uuid
        ident=str(uuid.uuid4());draft={'id':ident,'turns':[],'preview':''};(bridge.STATE/'empty-chats.json').write_text(json.dumps({ident:draft}));bridge.thread_id=ident
        bridge.bridge=Mock(connected=True);bridge.bridge.request.return_value={'thread':{'id':'actual-server-thread','turns':[]}}
        with patch.object(bridge,'dispatch'),patch.object(bridge,'connected'):result=bridge.send_message('Hello from Gaming Mode',[],'test-model','','default')
        self.assertEqual(result['threadId'],'actual-server-thread');self.assertEqual(bridge.outbox[-1]['threadId'],'actual-server-thread');self.assertTrue(bridge.outbox[-1]['freshThread']);self.assertEqual(json.loads((bridge.STATE/'empty-chats.json').read_text())[ident],draft)
        self.assertEqual(bridge.bridge.request.call_args.args[0],'thread/start')
    def test_local_draft_marker_is_scoped_to_its_device(self):
        import json,uuid
        ident=str(uuid.uuid4());draft={'id':ident,'turns':[],'localDraft':True,'host':'workstation'};(bridge.STATE/'empty-chats.json').write_text(json.dumps({ident:draft}))
        self.assertIsNone(bridge.local_empty_thread(ident));bridge.remote_host='workstation';self.assertEqual(bridge.local_empty_thread(ident),draft)
    def test_stale_rollout_detaches_selection_but_keeps_drafts_and_queue(self):
        import time
        bridge.thread_id='missing';(bridge.STATE/'thread-id').write_text('missing');saved=bridge.STATE/'draft.txt';saved.write_text('Keep this draft');bridge.outbox=[{'id':'queued','threadId':'missing','status':'error'}]
        bridge.bridge=Mock(connected=True);bridge.bridge.select_thread.side_effect=RuntimeError('no rollout found for thread id missing');bridge.model_cache_time=bridge.cache_media_time=time.time();bridge.history_caches={};bridge.history_cache_times={};bridge.model_catalog=[]
        with patch.object(bridge,'connected'),patch.object(bridge,'refresh_threads'),patch.object(bridge,'read_account',return_value={'account':None}),patch.object(bridge,'ssh_hosts',return_value=[]):result=bridge.get_snapshot()
        self.assertTrue(result['ready']);self.assertEqual(result['threadId'],'');self.assertTrue(result['historyWarning']);self.assertEqual(saved.read_text(),'Keep this draft');self.assertEqual(bridge.outbox[0]['id'],'queued');self.assertEqual((bridge.STATE/'thread-id').read_text().strip(),'')
    def test_history_window_never_reads_attachments_outside_requested_tail(self):
        thread = {"turns": [{"items": [{"type": "userMessage", "id": str(i),
                  "content": [{"type": "text", "text": "Fixture"}]}]} for i in range(240)]}
        with patch.object(bridge, "attachments", return_value=[]) as preview:
            rows = bridge.extract_messages(thread, limit=41)
        self.assertEqual([str(i) for i in range(199, 240)], [row["id"] for row in rows])
        self.assertEqual([str(i) for i in range(239, 198, -1)], [call.args[0]["id"] for call in preview.call_args_list])

    def test_stale_composer_context_cannot_send_to_another_chat_or_host(self):
        with patch.multiple(bridge, provider="codex", remote_host="test-host", thread_id="active", read_only=False), \
                patch.object(bridge, "send_message", return_value={"queued": True}) as send:
            current = {"provider": "codex", "host": "test-host", "threadId": "active"}
            for field, old in (("provider", "claude"), ("host", ""), ("threadId", "old")):
                with self.subTest(field=field), self.assertRaisesRegex(ValueError, "Чат или устройство"):
                    bridge.call("send", {"expected": {**current, field: old}, "text": "fixture"})
            send.assert_not_called()
            self.assertEqual({"queued": True}, bridge.call("send", {"expected": current, "text": "fixture"}))
            send.assert_called_once()

    @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg required for media integration test')
    def test_short_and_long_recordings_produce_jpeg_frames(self):
        root=Path(self.temp.name)/'recordings';root.mkdir()
        for seconds,expected in [(5,1),(125,4)]:
            source=root/(str(seconds)+'.mp4')
            subprocess.run(['ffmpeg','-nostdin','-v','error','-f','lavfi','-i',f'color=c=red:s=320x180:r=2:d={seconds}',
                            '-c:v','mpeg4',str(source)],check=True,capture_output=True,timeout=15)
            with patch.object(bridge,'media_roots',return_value=[root]):frames=bridge.video_frames(str(source))
            self.assertEqual(len(frames),expected)
            for frame in frames:self.assertTrue(Path(frame['path']).read_bytes().startswith(b'\xff\xd8'))

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.state=patch.object(bridge,'STATE',Path(self.temp.name));self.state.start()
        self.addCleanup(self.state.stop);self.addCleanup(self.temp.cleanup)
        bridge.provider='codex';bridge.remote_host='';bridge.thread_id='';bridge.snapshot_cache={}
        bridge.outbox=[];bridge.active=False;bridge.bridge=None;bridge.cache=[];bridge.account_cache={'account':None}
        bridge.provider_chats={'claude':{},'deepseek':{},'tokenharbor':{}}
        bridge.provider_thread_ids={'claude':'','deepseek':'','tokenharbor':''}

    def test_selected_history_is_read_once_and_reused_by_snapshot(self):
        bridge.bridge=Mock(connected=True)
        thread={'turns':[{'status':'completed','items':[{'type':'agentMessage','text':'loaded once'}]}]}
        bridge.bridge.select_thread.return_value=({},thread)
        bridge.history_caches={};bridge.history_cache_times={}
        def snapshot():
            self.assertEqual(bridge.history_caches[('', 'chosen')],thread)
            return {'threadId':bridge.thread_id}
        with patch.object(bridge,'connected'),patch.object(bridge,'get_snapshot',side_effect=snapshot):
            result=bridge.call('select_thread',{'id':'chosen'})
        self.assertEqual(result['threadId'],'chosen');bridge.bridge.select_thread.assert_called_once_with('chosen')

    def test_offline_selection_never_shows_another_chats_messages(self):
        bridge.thread_id='old'
        old={'ready':True,'threadId':'old','messages':[{'text':'private old history'}]}
        with patch.object(bridge,'_get_snapshot',return_value=old):bridge.get_snapshot()
        bridge.thread_id='new'
        with patch.object(bridge,'_get_snapshot',side_effect=RuntimeError('offline')):result=bridge.get_snapshot()
        self.assertEqual(result['threadId'],'new');self.assertEqual(result['messages'],[])

    def test_external_selection_caches_history_under_its_actual_chat(self):
        bridge.thread_id='old'
        def external_selection():
            bridge.thread_id='new';return {'threadId':'new','messages':[{'text':'new history'}]}
        with patch.object(bridge,'_get_snapshot',side_effect=external_selection):bridge.get_snapshot()
        bridge.thread_id='old'
        with patch.object(bridge,'_get_snapshot',side_effect=RuntimeError('offline')):result=bridge.get_snapshot()
        self.assertEqual(result['messages'],[]);self.assertEqual(result['threadId'],'old')

    def test_new_task_notification_has_question_and_cancel_is_not_success(self):
        bridge.thread_id='demo';bridge.cache=[]
        bridge.outbox=[{'id':'job','threadId':'demo','text':'Check my disk','status':'sending','host':''}]
        with patch.object(bridge,'notify') as notify,patch.object(bridge.threading,'Thread'):
            self.assertEqual(bridge.thread_title('demo'),'Check my disk')
            bridge.event({'method':'turn/completed','params':{'threadId':'demo','turn':{'id':'turn','status':'interrupted'}}})
            notify.assert_called_once_with('cancelled','demo')

    def test_image_only_history_is_not_dropped(self):
        thread={'turns':[{'items':[{'id':'image','type':'userMessage','content':[{'type':'localImage','path':'/home/test/a.png'}]}]}]}
        with patch.object(bridge,'attachments',return_value=[{'name':'a.png','preview':'data:image/png;base64,AA=='}]):
            messages=bridge.extract_messages(thread)
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0]['text'],'')
        self.assertEqual(messages[0]['attachments'][0]['name'],'a.png')

    def test_completed_background_chat_releases_queue(self):
        bridge.thread_id='visible';job={'id':'j','threadId':'background','turnId':'turn','status':'sending'};bridge.outbox=[job]
        with patch.object(bridge.threading,'Thread'):
            bridge.event({'method':'turn/completed','params':{'threadId':'background','turn':{'id':'turn','status':'completed'}}})
        self.assertEqual(bridge.outbox,[])

    def test_unrelated_turn_cannot_complete_job(self):
        job={'id':'j','threadId':'chat','turnId':'owned','status':'sending'};bridge.outbox=[job]
        bridge.event({'method':'turn/completed','params':{'threadId':'chat','turn':{'id':'other','status':'completed'}}})
        self.assertEqual(bridge.outbox,[job])

    def test_recovery_retains_running_turn_without_resending(self):
        bridge.bridge=Mock(connected=True);job={'id':'j','threadId':'chat','turnId':'t','status':'recovering'};bridge.outbox=[job]
        bridge.bridge.request.return_value={'thread':{'turns':[{'id':'t','status':'inProgress'}]}}
        bridge.recover_outbox()
        self.assertEqual(job['status'],'sending')
        self.assertFalse(any(c.args[0]=='turn/start' for c in bridge.bridge.request.call_args_list))

    def test_recovery_completed_turn_clears_persisted_job(self):
        bridge.bridge=Mock(connected=True);bridge.outbox=[{'id':'j','threadId':'chat','turnId':'t','status':'recovering'}]
        bridge.bridge.request.return_value={'thread':{'turns':[{'id':'t','status':'completed'}]}}
        bridge.recover_outbox();self.assertEqual(bridge.outbox,[])

    def test_ambiguous_recovery_requires_manual_check(self):
        bridge.bridge=Mock(connected=True);job={'id':'j','threadId':'chat','status':'recovering'};bridge.outbox=[job]
        bridge.bridge.request.return_value={'thread':{'turns':[]}}
        bridge.recover_outbox();self.assertEqual(job['status'],'error')

    def test_offline_recovery_does_not_mark_send_failed(self):
        bridge.bridge=Mock(connected=True);job={'id':'j','threadId':'chat','turnId':'t','status':'recovering'};bridge.outbox=[job]
        bridge.bridge.request.side_effect=RuntimeError('offline')
        bridge.recover_outbox();self.assertEqual(job['status'],'recovering')

    def test_queued_message_waits_for_existing_turn(self):
        bridge.bridge=Mock(connected=True);bridge.thread_id='other'
        bridge.bridge.request.return_value={'thread':{'turns':[{'id':'busy','status':'inProgress'}]}}
        job={'id':'queued','threadId':'background','text':'question','images':[],'status':'sending'};bridge.outbox=[job]
        bridge.dispatch_job(job)
        self.assertEqual(job['status'],'queued')
        self.assertFalse(any(call.args[0]=='turn/start' for call in bridge.bridge.request.call_args_list))

    def test_first_send_does_not_read_unmaterialized_new_thread(self):
        bridge.bridge=Mock(connected=True);bridge.thread_id='new'
        bridge.bridge.request.return_value={'turn':{'id':'started'}}
        job={'id':'q','threadId':'new','text':'hello','images':[],'status':'sending','freshThread':True}
        bridge.outbox=[job];bridge.dispatch_job(job)
        bridge.bridge.request.assert_called_once()
        self.assertEqual(bridge.bridge.request.call_args.args[0],'turn/start')
        self.assertEqual(job['turnId'],'started')
        self.assertNotIn('freshThread',job)

    def test_completion_before_start_reply_does_not_reactivate_finished_job(self):
        bridge.thread_id='new';bridge.bridge=Mock(connected=True)
        job={'id':'q','threadId':'new','text':'hello','images':[],'status':'sending','freshThread':True}
        bridge.outbox=[job];bridge.active=True
        def fast_answer(*args,**kwargs):
            with patch.object(bridge.threading,'Thread'):
                bridge.event({'method':'turn/completed','params':{'threadId':'new','turn':{'id':'fast','status':'completed'}}})
            return {'turn':{'id':'fast'}}
        bridge.bridge.request.side_effect=fast_answer
        bridge.dispatch_job(job)
        self.assertFalse(bridge.active)
        self.assertEqual(bridge.outbox,[])

    def test_unique_legacy_send_recovers_by_exact_question(self):
        bridge.bridge=Mock(connected=True);job={'id':'legacy','threadId':'chat','text':'exact question','status':'recovering'};bridge.outbox=[job]
        turn={'id':'confirmed','status':'inProgress','items':[{'type':'userMessage','content':[{'type':'text','text':'exact question'}]}]}
        bridge.bridge.request.return_value={'thread':{'turns':[turn]}}
        bridge.recover_outbox();self.assertEqual(job['turnId'],'confirmed');self.assertEqual(job['status'],'sending')

    def test_repeated_question_is_ambiguous(self):
        bridge.bridge=Mock(connected=True);job={'id':'legacy','threadId':'chat','text':'repeat','status':'recovering'};bridge.outbox=[job]
        turn={'status':'completed','items':[{'type':'userMessage','content':[{'type':'text','text':'repeat'}]}]}
        bridge.bridge.request.return_value={'thread':{'turns':[{**turn,'id':'a'},{**turn,'id':'b'}]}}
        bridge.recover_outbox();self.assertEqual(job['status'],'error')

    def test_voice_publishes_partial_and_final_text(self):
        from types import SimpleNamespace
        import sys,threading
        bridge.voice_stop=threading.Event()
        recognizer=Mock()
        def waveform(block):
            if block==b'b':self.assertEqual(bridge.voice_text,'первая')
            return block==b'b'
        recognizer.AcceptWaveform.side_effect=waveform
        recognizer.PartialResult.return_value='{"partial":"первая"}'
        recognizer.Result.return_value='{"text":"первая фраза"}'
        recognizer.FinalResult.return_value='{"text":"готово"}'
        recorder=Mock()
        vosk=SimpleNamespace(Model=Mock(),KaldiRecognizer=Mock(return_value=recognizer),SetLogLevel=Mock())
        with patch.dict(sys.modules,{'vosk':vosk}),patch('speech_accuracy.refine_dictation',side_effect=lambda pcm,lang,text,root:text),patch.object(bridge.subprocess,'check_output',return_value='microphone'),patch.object(bridge.subprocess,'Popen',return_value=recorder),patch.object(bridge.select,'select',return_value=([recorder.stdout],[],[])),patch.object(bridge.os,'read',side_effect=[b'a',b'b',b'']):
            bridge.voice_capture('ru')
        self.assertEqual(bridge.voice_text,'первая фраза готово')
        self.assertEqual(bridge.voice_state,'done')
        bridge.voice_text='';bridge.voice_error='';bridge.voice_state='idle'

    def test_voice_stop_returns_current_transcript_without_second_recording(self):
        bridge.voice_state='recording';bridge.voice_id='v';bridge.voice_text='готовый текст'
        bridge.voice_error='';bridge.voice_language='ru-fast';bridge.voice_stop=Mock();bridge.voice_thread=Mock()
        with patch.object(bridge.threading,'Thread') as worker:
            result=bridge.start_voice('ru-fast')
        self.assertEqual(result['voiceText'],'готовый текст')
        self.assertEqual(result['voiceId'],'v')
        bridge.voice_thread.join.assert_called_once_with(timeout=.25)
        worker.assert_not_called()
        bridge.voice_state='idle';bridge.voice_thread=None;bridge.voice_stop=None

    def test_voice_processing_cannot_start_overlapping_recording(self):
        bridge.voice_state='processing';bridge.voice_id='busy';bridge.voice_text='слова'
        with patch.object(bridge.threading,'Thread') as worker:result=bridge.start_voice('en')
        self.assertEqual(result['voiceId'],'busy');worker.assert_not_called()
        bridge.voice_state='idle';bridge.voice_text=''

    def test_dictation_rejects_speaker_monitor(self):
        from types import SimpleNamespace
        import sys,threading
        bridge.voice_stop=threading.Event()
        vosk=SimpleNamespace(Model=Mock(),KaldiRecognizer=Mock(),SetLogLevel=Mock())
        with patch.dict(sys.modules,{'vosk':vosk}),patch.object(bridge.subprocess,'check_output',return_value='speaker.monitor'),patch.object(bridge.subprocess,'Popen') as capture:
            bridge.voice_capture('ru')
        capture.assert_not_called()
        self.assertIn('микрофон',bridge.voice_error)
        bridge.voice_text='';bridge.voice_error='';bridge.voice_state='idle'

    def test_shared_selection_is_plain_text(self):
        path=bridge.STATE/'thread-id'
        bridge.atomic_text(path,'chat-id\n')
        self.assertEqual(path.read_text(),'chat-id\n')
        self.assertEqual(bridge.read_text_state(path),'chat-id')

    def test_old_quoted_selection_is_readable(self):
        path=bridge.STATE/'thread-id'
        path.write_text('"chat-id\\n"')
        self.assertEqual(bridge.read_text_state(path),'chat-id')
        path.write_text('"\\n"')
        self.assertEqual(bridge.read_text_state(path),'')

    def test_offline_snapshot_keeps_ui_contract(self):
        with patch.object(bridge,'connected',side_effect=RuntimeError('server offline')):
            result=bridge.get_snapshot()
        self.assertFalse(result['ready'])
        self.assertEqual(result['status'],'server offline')
        self.assertEqual(result['messages'],[])
        self.assertIn('sshHosts',result)
        self.assertIn('models',result)

    def test_offline_retains_last_conversation(self):
        messages=[{'id':'1','role':'assistant','text':'Saved answer'}]
        bridge.thread_id='saved'
        bridge.snapshot_cache[('codex','','saved')]={'messages':messages,'threadId':'saved'}
        with patch.object(bridge,'connected',side_effect=RuntimeError('offline')):
            result=bridge.get_snapshot()
        self.assertEqual(result['messages'],messages)
        self.assertEqual(result['threadId'],'saved')

    def test_device_code_login_is_returned_for_game_mode(self):
        client=Mock(connected=True)
        client.request.return_value={'loginId':'login','verificationUrl':'https://auth.openai.com/codex/device','userCode':'ABCD-1234'}
        bridge.bridge=client;bridge.account_login_id=''
        with patch.object(bridge.subprocess,'Popen'):
            result=bridge.start_account_login()
        client.request.assert_called_once_with('account/login/start',{'type':'chatgptDeviceCode'},timeout=20)
        self.assertEqual(result['userCode'],'ABCD-1234')
        bridge.account_login_id=''

    def test_remote_first_send_skips_resume_of_unpersisted_chat(self):
        bridge.remote_host='desk';bridge.bridge=Mock(connected=True)
        bridge.bridge.request.return_value={'turn':{'id':'started'}}
        job={'id':'q','threadId':'new','host':'desk','text':'hello','images':[],'status':'sending','freshThread':True}
        bridge.outbox=[job];bridge.dispatch_job(job)
        bridge.bridge.request.assert_called_once()
        self.assertEqual(bridge.bridge.request.call_args.args[0],'turn/start')
        self.assertEqual(job['turnId'],'started')

    def test_recovery_does_not_read_jobs_from_another_device(self):
        bridge.bridge=Mock(connected=True);bridge.remote_host='desk'
        job={'id':'j','threadId':'chat','host':'other','turnId':'t','status':'recovering'}
        bridge.outbox=[job];bridge.recover_outbox()
        bridge.bridge.request.assert_not_called()
        self.assertEqual(job['status'],'recovering')

    def test_connect_does_not_resume_broken_thread(self):
        bridge.thread_id='broken-id';candidate=Mock(connected=True)
        with patch.object(bridge,'Backend',return_value=candidate):bridge.connected()
        candidate.connect.assert_called_once_with(None)

    def test_external_provider_status_does_not_crash(self):
        bridge.provider='claude';bridge.provider_status='Готов'
        with patch.object(bridge,'model_list_for_provider',return_value=[]),patch.object(bridge,'read_account',return_value={'account':None}),patch.object(bridge,'list_screenshots',return_value=[]),patch.object(bridge,'list_videos',return_value=[]):
            result=bridge.get_snapshot()
        self.assertTrue(result['ready'])
        self.assertEqual(result['status'],'Готов')

    def test_select_model_before_first_external_chat(self):
        bridge.provider='claude'
        bridge.save_settings('opus','','default')
        chat=bridge.provider_chats['claude'][bridge.provider_thread_ids['claude']]
        self.assertEqual(chat['model'],'opus')
        self.assertEqual(chat['messages'],[])

if __name__=='__main__':unittest.main()

class LongHistoryTests(unittest.TestCase):
    def test_old_game_request_is_available_without_truncating_default_view(self):
        thread={'turns':[{'items':[{'id':str(i),'type':'userMessage','content':[{'type':'text','text':'message '+str(i)}]} for i in range(100)]}]}
        self.assertEqual(len(bridge.extract_messages(thread)),40)
        full=bridge.extract_messages(thread,limit=None)
        self.assertEqual(len(full),100);self.assertEqual(full[0]['text'],'message 0')
