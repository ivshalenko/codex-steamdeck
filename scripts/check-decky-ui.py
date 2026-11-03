#!/usr/bin/env python3
"""Manual Gaming Mode UI regression check against the installed Decky plugin.

Run with the companion's venv Python while Steam Gaming Mode is active.
Checks compact layout, full-screen settings, expansion/collapse and draft and
attachment preservation. Does not send messages or change model settings.
"""
import json,time,urllib.request,base64
from websockets.sync.client import connect

def pages():return json.load(urllib.request.urlopen('http://127.0.0.1:8080/json/list',timeout=3))
def command(title,method,params):
 page=next(p for p in pages() if p['title']==title)
 with connect(page['webSocketDebuggerUrl'],origin='http://localhost',max_size=12*1024*1024) as ws:
  ws.send(json.dumps({'id':1,'method':method,'params':params}))
  while True:
   r=json.loads(ws.recv(timeout=5))
   if r.get('id')==1:return r.get('result',r)
def evaluate(title,expression):
 r=command(title,'Runtime.evaluate',{'expression':expression,'returnByValue':True,'awaitPromise':True})
 if 'exceptionDetails' in r:raise RuntimeError(str(r['exceptionDetails']))
 return r.get('result',{}).get('value')
def wait(title,expression):
 deadline=time.monotonic()+8
 while time.monotonic()<deadline:
  if evaluate(title,expression):return
  time.sleep(.1)
 raise TimeoutError(expression)
SHARED='SharedJSContext'
QAM=next(p['title'] for p in pages() if p['title'].startswith('QuickAccess_'))
FULL=next(p['title'] for p in pages() if 'browserType=4' in p['url'] or p['title']=='Режим Big Picture')
def open_panel():
 evaluate(SHARED,"DeckyPluginLoader.deckyState.setActivePlugin('Deck AI');DFL.Navigation.OpenQuickAccessMenu(999)")
 wait(QAM,"!!document.querySelector('.dai-root')")
def fill(title,value):
 evaluate(title,"document.querySelector('.dai-composer input').focus();document.querySelector('.dai-composer input').select()")
 command(title,'Input.insertText',{'text':value})
 wait(title,"document.querySelector('.dai-composer input').value==="+json.dumps(value))
def click(title,expression):
 evaluate(title,expression+".click()")
old_draft=None;added_image=False
try:
 open_panel()
 assert evaluate(QAM,"!document.querySelector('.dai-fullscreen')")
 assert evaluate(QAM,"document.querySelector('.dai-root').scrollWidth<=document.querySelector('.dai-root').clientWidth")
 print('PASS compact panel has no overlap',flush=True)
 wait(QAM,"!!document.querySelector('.dai-status .dai-dot:not(.offline)')")
 old_draft=evaluate(QAM,"document.querySelector('.dai-composer input').value")
 test_draft=old_draft or 'DECK_AI_FULLSCREEN_CHECK'
 if not old_draft:
  fill(QAM,test_draft)
 # Check clearing without sending anything, then restore the test draft.
 assert evaluate(QAM,"![...document.querySelectorAll('.dai-compose-actions .dai-button')].some(e=>['Игра','Файлы'].includes(e.innerText))")
 click(QAM,"[...document.querySelectorAll('.dai-compose-actions .dai-button')].find(e=>e.innerText==='Очистить')")
 wait(QAM,"document.querySelector('.dai-composer input').value===''")
 fill(QAM,test_draft)
 print('PASS clear button clears input; redundant game button removed',flush=True)
 expected_images=evaluate(QAM,"document.querySelectorAll('.dai-attachments .dai-button').length")
 click(QAM,"document.querySelectorAll('.dai-tab')[2].querySelector('.dai-button')")
 wait(FULL,"!!document.querySelector('.dai-fullscreen .dai-settings-grid')")
 assert evaluate(FULL,"document.querySelector('.dai-tab[aria-selected=true]').innerText")=='Настройки'
 wait(FULL,"document.querySelector('.dai-fullscreen').getBoundingClientRect().width>=innerWidth-1")
 geometry=evaluate(FULL,"(()=>{const e=document.querySelector('.dai-fullscreen'),g=document.querySelector('.dai-settings-grid');return {root:e.getBoundingClientRect().toJSON(),viewport:[innerWidth,innerHeight],columns:getComputedStyle(g).gridTemplateColumns,overflow:e.scrollWidth>e.clientWidth};})()")
 print('Full-screen geometry:',geometry,flush=True)
 assert not geometry['overflow']
 assert geometry['root']['width']>=geometry['viewport'][0]-1
 assert geometry['root']['top']>=39
 assert len(geometry['columns'].split())==2,geometry
 print('PASS settings open full-width, in two columns, clear of Steam header/footer',flush=True)
 density=evaluate(FULL,"(()=>{const e=document.querySelector('.dai-settings');e.scrollTop=0;const r=e.getBoundingClientRect();return {fontSizes:[...e.querySelectorAll('button[role=combobox]')].map(b=>parseFloat(getComputedStyle(b).fontSize)),allCardsVisible:[...e.querySelectorAll('.dai-section')].every(c=>{const q=c.getBoundingClientRect();return q.top>=r.top-1&&q.bottom<=r.bottom+1;}),codex:!!document.querySelector('.dai-model-fields button[role=combobox]')?.innerText.includes('Codex')};})()")
 assert all(size<=13 for size in density['fontSizes']),density
 reachable=evaluate(FULL,"(()=>{const root=document.querySelector('.dai-settings');const cards=[...root.querySelectorAll('.dai-section')];const ok=cards.every(c=>{c.scrollIntoView({block:'nearest'});const r=root.getBoundingClientRect(),q=c.getBoundingClientRect();return q.bottom>r.top&&q.top<r.bottom;});root.scrollTop=0;return ok;})()")
 assert reachable,'A settings card is unreachable by scrolling'
 print('PASS compact fonts and every settings card reachable by scrolling',flush=True)
 shot=command(FULL,'Page.captureScreenshot',{'format':'png'})
 open('/tmp/deck-ai-settings-wide-final.png','wb').write(base64.b64decode(shot['data']))
 click(FULL,"document.querySelectorAll('.dai-tab')[0].querySelector('.dai-button')")
 wait(FULL,"!!document.querySelector('.dai-composer input')")
 assert evaluate(FULL,"document.querySelector('.dai-composer input').value")==test_draft
 assert evaluate(FULL,"document.querySelectorAll('.dai-attachments .dai-button').length")==expected_images
 print('PASS draft and attachments preserved in full-screen chat',flush=True)
 click(FULL,"[...document.querySelectorAll('.dai-full-header .dai-button')].find(e=>e.innerText.includes('В панель'))")
 wait(QAM,"!!document.querySelector('.dai-composer input')")
 assert evaluate(QAM,"document.querySelector('.dai-composer input').value")==test_draft
 assert evaluate(QAM,"document.querySelectorAll('.dai-attachments .dai-button').length")==expected_images
 print('PASS collapse restores draft and attachments in compact panel',flush=True)
 click(QAM,"document.querySelector('.dai-viewbar>.dai-button')")
 wait(FULL,"!!document.querySelector('.dai-fullscreen .dai-composer')")
 assert evaluate(FULL,"document.querySelector('.dai-tab[aria-selected=true]').innerText")=='Чат'
 assert evaluate(FULL,"document.querySelector('.dai-composer input').value")==test_draft
 print('PASS expand button opens full-screen chat directly',flush=True)
 if geometry['viewport'][1]>=500 and expected_images<=1:
  assert evaluate(FULL,"document.querySelector('.dai-messages').clientHeight>=230")
  assert evaluate(FULL,"document.querySelector('.dai-composer').clientHeight<=85")
 print('PASS full-screen chat gives most space to conversation',flush=True)
 # Opening QAM over an existing workspace must select Settings in that same
 # workspace, rather than push duplicate routes or leave Chat selected.
 open_panel()
 click(QAM,"document.querySelectorAll('.dai-tab')[2].querySelector('.dai-button')")
 wait(FULL,"!!document.querySelector('.dai-fullscreen .dai-settings-grid')")
 assert evaluate(FULL,"document.querySelector('.dai-tab[aria-selected=true]').innerText")=='Настройки'
 print('PASS reopening Settings over full-screen Chat selects the right tab',flush=True)
 click(FULL,"[...document.querySelectorAll('.dai-full-header .dai-button')].find(e=>e.innerText.includes('К игре'))")
 wait(FULL,"!document.querySelector('.dai-fullscreen')")
 print('PASS return-to-game closes full-screen view',flush=True)
 open_panel()
 assert evaluate(QAM,"document.querySelector('.dai-composer input').value")==test_draft
 print('PASS reopening panel retains draft',flush=True)
 # Keep the full-screen Panel mounted while typing in QAM. Previously the
 # shared storage changed but that existing Panel retained its old React state.
 click(QAM,"document.querySelector('.dai-viewbar>.dai-button')")
 wait(FULL,"!!document.querySelector('.dai-composer input')")
 open_panel();two_view_draft=test_draft+' · TWO_VIEW_CHECK'
 try:
  fill(QAM,two_view_draft)
  wait(FULL,"document.querySelector('.dai-composer input').value==="+json.dumps(two_view_draft))
  click(QAM,"document.querySelectorAll('.dai-tab')[2].querySelector('.dai-button')")
  wait(FULL,"!!document.querySelector('.dai-settings-grid')")
  click(FULL,"document.querySelectorAll('.dai-tab')[0].querySelector('.dai-button')")
  wait(FULL,"document.querySelector('.dai-composer input')?.value==="+json.dumps(two_view_draft))
  print('PASS compact edits survive reopening an already mounted full-screen workspace',flush=True)
 finally:
  if evaluate(FULL,"!!document.querySelector('.dai-composer input')"):fill(FULL,test_draft)

finally:
 try:
  # Leave the user's original draft and attachments unchanged.
  if evaluate(FULL,"!!document.querySelector('.dai-fullscreen')"):
   click(FULL,"[...document.querySelectorAll('.dai-full-header .dai-button')].find(e=>e.innerText.includes('В панель'))")
  open_panel()
  if old_draft is not None and not old_draft and evaluate(QAM,"document.querySelector('.dai-composer input').value")==test_draft:
   fill(QAM,old_draft)
  if added_image:click(QAM,"document.querySelector('.dai-attachments .dai-button')")
 except Exception as e:print('Cleanup:',str(e))
