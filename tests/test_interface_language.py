"""Language preferences and tool captions must not rewrite user content."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('language_bridge',Path(__file__).resolve().parents[1]/'decky/bridge.py')
bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)

class InterfaceLanguageTests(unittest.TestCase):
 def test_language_is_persisted_separately_from_voice_and_history(self):
  with tempfile.TemporaryDirectory() as folder,patch.object(bridge,'STATE',Path(folder)):
   root=Path(folder);(root/'voice-language').write_text('ru');(root/'history.json').write_text('Русский диалог')
   self.assertEqual(bridge.interface_language(),'en')
   self.assertEqual(bridge.call('interface_language',{'language':'en'}),{'uiLanguage':'en'})
   self.assertEqual(bridge.interface_language(),'en')
   self.assertEqual((root/'voice-language').read_text(),'ru')
   self.assertEqual((root/'history.json').read_text(),'Русский диалог')
   for invalid in ('de','../../bad',None,False):
    with self.assertRaises(ValueError):bridge.set_interface_language(invalid)
   self.assertEqual(bridge.interface_language(),'en')
   bridge.set_interface_language('ru');self.assertEqual(bridge.interface_language(),'ru')

 def test_cached_or_failed_snapshot_uses_the_current_language(self):
  with tempfile.TemporaryDirectory() as folder,patch.object(bridge,'STATE',Path(folder)),patch.object(bridge,'_safe_snapshot',return_value={'ready':False,'uiLanguage':'ru'}):
   bridge.set_interface_language('en');self.assertEqual(bridge.get_snapshot()['uiLanguage'],'en')

 def test_tool_captions_are_localized_without_translating_commands_or_output(self):
  command={'type':'commandExecution','command':'cat "Мой файл"','exitCode':1,'aggregatedOutput':'Ошибка из самой программы'}
  self.assertEqual(bridge.tool_text(command,'en'),'$ cat "Мой файл"\n[exit code 1]\nОшибка из самой программы')
  self.assertIn('[код 1]',bridge.tool_text(command))
  change={'type':'fileChange','changes':[{'path':'Мой файл','diff':'+Привет'}]}
  self.assertEqual(bridge.tool_text(change,'en'),'Files changed: Мой файл\n+Привет')
  thread={'turns':[{'items':[command,{'type':'agentMessage','text':'Русский ответ'}]}]}
  rows=bridge.extract_messages(thread)
  self.assertEqual(rows[0]['textEn'],bridge.tool_text(command,'en'))
  self.assertEqual(rows[1]['text'],'Русский ответ');self.assertNotIn('textEn',rows[1])

 def test_generated_titles_follow_the_preference_but_existing_names_are_preserved(self):
  with tempfile.TemporaryDirectory() as folder,patch.object(bridge,'STATE',Path(folder)):
   bridge.set_interface_language('en');self.assertEqual(bridge.thread_summary({'id':'empty'})['name'],'New chat')
   self.assertEqual(bridge.thread_summary({'id':'named','name':'Мой разговор'})['name'],'Мой разговор')
   bridge.set_interface_language('ru');self.assertEqual(bridge.thread_summary({'id':'empty'})['name'],'Новый чат')

 def test_background_notifications_use_the_installer_language_before_a_panel_opens(self):
  with tempfile.TemporaryDirectory() as folder,patch.object(bridge,'STATE',Path(folder)):
   for language in ('ru','en'):
    bridge.set_interface_language(language)
    self.assertEqual(bridge.poll_events(None)['uiLanguage'],language)
    self.assertEqual(bridge.poll_events(0)['uiLanguage'],language)
