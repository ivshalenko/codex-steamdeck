"""Regression coverage for Decky snapshots and recovery, without network calls."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

spec=importlib.util.spec_from_file_location('decky_bridge_test',Path(__file__).resolve().parents[1]/'decky/bridge.py')
bridge=importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

class DeckyBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.state=patch.object(bridge,'STATE',Path(self.temp.name));self.state.start()
        self.addCleanup(self.state.stop);self.addCleanup(self.temp.cleanup)
        bridge.provider='codex';bridge.remote_host='';bridge.thread_id='';bridge.snapshot_cache={}
        bridge.outbox=[];bridge.active=False;bridge.bridge=None;bridge.cache=[];bridge.account_cache={'account':None}
        bridge.provider_chats={'claude':{},'deepseek':{},'tokenharbor':{}}
        bridge.provider_thread_ids={'claude':'','deepseek':'','tokenharbor':''}

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
        recorder=Mock();recorder.stdout.read.side_effect=[b'a',b'b',b'']
        vosk=SimpleNamespace(Model=Mock(),KaldiRecognizer=Mock(return_value=recognizer),SetLogLevel=Mock())
        with patch.dict(sys.modules,{'vosk':vosk}),patch('speech_accuracy.refine_dictation',side_effect=lambda pcm,lang,text,root:text),patch.object(bridge.subprocess,'check_output',return_value='microphone'),patch.object(bridge.subprocess,'Popen',return_value=recorder):
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
        bridge.snapshot_cache[('codex','')]={'messages':messages,'threadId':'saved'}
        with patch.object(bridge,'connected',side_effect=RuntimeError('offline')):
            result=bridge.get_snapshot()
        self.assertEqual(result['messages'],messages)
        self.assertEqual(result['threadId'],'saved')

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
