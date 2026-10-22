#!/usr/bin/env python3
"""Real GTK and app-server integration check, using isolated local state."""
import os,sys,tempfile,time,json,traceback
from pathlib import Path
os.environ['DECK_AI_GAMING']='1'
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from decky.runtime_paths import resolve_app_dir
app_dir=resolve_app_dir()
sys.path.insert(0,str(app_dir))
import app as module
from gi.repository import GLib,Gdk
import ui_extras
state=tempfile.TemporaryDirectory(prefix='deck-ai-check-')
module.STATE_DIR=Path(state.name);module.DRAFT=Path(state.name)/'draft.txt';module.THREAD=Path(state.name)/'thread-id';module.THEME=Path(state.name)/'theme'
ui_extras.STATE=Path(state.name)/'language'
panel=module.Panel();panel.set_application_id('local.deck.DeckAIIntegrationTest')
checks=[];phase='boot';started=time.monotonic();deadline=started+100

def check(name,condition):
 if not condition:raise AssertionError(name)
 checks.append(name)
 print('PASS',name,flush=True)

def terminal(login):
 checks.append('recovery_terminal_invoked' if not login else 'offline_login_invoked')
 return True
panel.launch_codex_terminal=terminal

def tick():
 global phase
 try:
  if time.monotonic()>deadline:raise TimeoutError('phase '+phase)
  if phase=='boot':
   if not panel.history_ready or not panel.available_models:return True
   if not (panel.window.get_window().get_state() & Gdk.WindowState.FULLSCREEN) and time.monotonic()-started<8:return True
   check('connected_and_models_loaded',panel.backend.connected and bool(panel.available_models))
   monitor=Gdk.Display.get_default().get_monitor_at_window(panel.window.get_window()).get_geometry()
   size=panel.window.get_size()
   check('fullscreen_window',bool(panel.window.get_window().get_state() & Gdk.WindowState.FULLSCREEN) or (size.width>=monitor.width and size.height>=monitor.height))
   check('model_menu_hidden_at_start',not panel.model_menu_popover.get_visible())
   panel.model_menu_button.set_active(True);phase='model_open';return True
  if phase=='model_open':
   check('model_menu_opens_on_click',panel.model_menu_popover.get_visible())
   panel.model_menu_button.set_active(False);phase='model_closed';return True
  if phase=='model_closed':
   check('model_menu_closes',not panel.model_menu_popover.get_visible())
   panel.text.get_buffer().set_text('DECK_AI_DRAFT_TEST')
   first=panel.thread_id
   panel.new_chat()
   check('new_chat_has_separate_id',panel.thread_id!=first)
   panel.switch_thread(first)
   buf=panel.text.get_buffer()
   check('draft_restored_per_chat',buf.get_text(buf.get_start_iter(),buf.get_end_iter(),False)=='DECK_AI_DRAFT_TEST')
   panel.keyboard();check('onscreen_keyboard_opens',panel.app_keyboard.get_visible());panel.keyboard();check('onscreen_keyboard_closes',not panel.app_keyboard.get_visible())
   chosen=next((m.get('model') or m['id']) for m in panel.available_models if (m.get('model') or m['id'])!=panel.model_picker.get_active_id())
   panel.model_picker.set_active_id(chosen)
   check('model_selection_persisted',json.loads((Path(state.name)/'model-preferences.json').read_text()).get(panel.thread_id)==chosen)
   panel.backend.ws.close();phase='offline';return True
  if phase=='offline':
   if panel.backend.connected:return True
   check('disconnection_detected',not panel.backend.connected)
   check('draft_survives_disconnect',(Path(state.name)/'draft.txt').read_text()=='DECK_AI_DRAFT_TEST')
   panel.begin_account_login()
   check('login_available_without_backend','offline_login_invoked' in checks)
   panel.reconnect();phase='reconnected';return True
  if phase=='reconnected':
   if panel.connecting or not panel.backend.connected or not panel.history_ready:return True
   check('reconnect_restores_ready_state',panel.history_ready)
   original=panel.backend.request
   def isolated_request(method,params,**kwargs):
    if method=='thread/start':params={**params,'ephemeral':True}
    return original(method,params,**kwargs)
   panel.backend.request=isolated_request
   panel.new_chat()
   default=next((m for m in panel.available_models if m.get('isDefault')),panel.available_models[0])
   panel.model_picker.set_active_id(default.get('model') or default['id'])
   panel.text.get_buffer().set_text('Проверка клиента. Ответь ровно DECK_AI_OK без пояснений. Не выполняй команды и не изменяй файлы.')
   panel.send();phase='response';return True
  if phase=='response':
   text='\n'.join(str(m.get('text','')) for m in panel.messages.values() if m['frame'].get_style_context().has_class('assistant-message'))
   if 'DECK_AI_OK' not in text or panel.engine_active or panel.outbox:return True
   check('real_model_answer_received',text.strip()=='DECK_AI_OK')
   check('outbox_drained',not panel.outbox)
   phase='done'
   (Path(tempfile.gettempdir())/'deck-ai-gui-check.json').write_text(json.dumps({'passed':checks,'seconds':round(time.monotonic()-started,1)},ensure_ascii=False,indent=2))
   panel.close();return False
 except Exception:
  traceback.print_exc()
  (Path(tempfile.gettempdir())/'deck-ai-gui-check.json').write_text(json.dumps({'passed':checks,'error':traceback.format_exc(),'phase':phase},ensure_ascii=False,indent=2))
  panel.shutdown_app();return False
 return True
GLib.timeout_add(150,tick)
result=panel.run(None)
state.cleanup()
if phase!='done':sys.exit(1)
print('ALL GUI CHECKS PASSED',flush=True)
