#!/usr/bin/env python3
"""Visible first-install wizard; no root filesystem modifications."""
import os,shutil,subprocess,sys,tempfile,threading,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'decky'))
from runtime_paths import resolve_app_dir
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,GLib
RU=os.environ.get('LANG','').startswith('ru')
def text(en,ru):return ru if RU else en
class Setup(Gtk.Window):
 def __init__(self):
  super().__init__(title='Deck AI · Setup');self.set_default_size(760,620);self.set_border_width(24);self.connect('delete-event',self.close)
  box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=12);self.add(box)
  title=Gtk.Label();title.set_markup('<span size="xx-large" weight="bold">Deck AI</span>');box.pack_start(title,False,False,0)
  self.language=Gtk.Button(label='Русский / English');self.language.connect('clicked',self.change_language);box.pack_start(self.language,False,False,0)
  subtitle=Gtk.Label(label=text('1. Install → 2. Sign in → 3. Ask your first question','1. Установите → 2. Войдите → 3. Задайте первый вопрос'));box.pack_start(subtitle,False,False,0)
  self.decky=Gtk.CheckButton(label=text('Add to Decky Loader (requires Decky; may ask for sudo password)','Добавить в Decky Loader (нужен Decky; возможен запрос пароля sudo)'));self.decky.set_active((Path.home()/'homebrew').is_dir());box.pack_start(self.decky,False,False,0)
  self.codex=Gtk.CheckButton(label=text('Install official Codex CLI if it is missing (OpenAI download)','Установить официальный Codex CLI, если его нет (загрузка OpenAI)'));self.codex.set_active(True);box.pack_start(self.codex,False,False,0)
  note=Gtk.Label(label=text('Uses your ChatGPT account. Requests go to your selected provider.\nVoice models are optional; add them later in Settings → Languages.\nChats, models and keys are preserved when updating.','Использует ваш ChatGPT-аккаунт. Запросы отправляются выбранному провайдеру.\nГолосовые модели необязательны: Настройки → Языки.\nПри обновлении чаты, модели и ключи сохраняются.'));note.set_line_wrap(True);box.pack_start(note,False,False,0)
  self.log=Gtk.TextView(editable=False,monospace=True,wrap_mode=Gtk.WrapMode.WORD_CHAR);scroll=Gtk.ScrolledWindow();scroll.add(self.log);box.pack_start(scroll,True,True,0)
  self.button=Gtk.Button(label=text('Install / update','Установить / обновить'));self.button.connect('clicked',self.start);box.pack_start(self.button,False,False,0)
  self.open=Gtk.Button(label=text('Open Deck AI and sign in','Открыть Deck AI и войти'));self.open.connect('clicked',lambda *_:subprocess.Popen([str(Path.home()/'.local/bin/deck-ai')]));self.open.set_sensitive(False);box.pack_start(self.open,False,False,0)
  guide=Gtk.LinkButton.new_with_label('https://github.com/ivshalenko/codex-steamdeck/blob/main/docs/QUICKSTART.md',text('Installation & remote control guide','Инструкция: установка и удалённое управление'));box.pack_start(guide,False,False,0)
  self.running=False;self.show_all()
 def change_language(self,*_):
  global RU
  if self.running:return
  RU=not RU;self.destroy();Setup()
 def close(self,*_):
  if self.running:self.line(text('Installation is running. Please wait.','Установка идёт. Дождитесь завершения.'));return True
  Gtk.main_quit();return False
 def line(self,value):
  def append():
   b=self.log.get_buffer();b.insert(b.get_end_iter(),value+'\n');self.log.scroll_to_iter(b.get_end_iter(),0,False,0,0)
  GLib.idle_add(append)
 def run(self,command):
  p=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,env={**os.environ,'PYTHONUNBUFFERED':'1'})
  for line in p.stdout:self.line(line.rstrip())
  if p.wait():raise RuntimeError(text('This step failed. See the message above; click Install to retry.','Этап не выполнен. Причина выше; нажмите «Установить», чтобы повторить.'))
 def start(self,*_):
  self.running=True;self.language.set_sensitive(False);self.button.set_sensitive(False);self.decky.set_sensitive(False);self.codex.set_sensitive(False)
  with_decky=self.decky.get_active();with_codex=self.codex.get_active()
  threading.Thread(target=self.work,args=(with_decky,with_codex),daemon=True).start()
 def work(self,with_decky,with_codex):
  try:
   if shutil.disk_usage(Path.home()).free<800_000_000:raise RuntimeError(text('Free at least 800 MB before installing.','Освободите хотя бы 800 МБ перед установкой.'))
   self.line(text('Checking packaged files…','Проверяю файлы…'));self.run([sys.executable,str(ROOT/'scripts/manage-install.py'),'validate',str(ROOT)])
   self.line(text('Installing application and Python dependencies…','Устанавливаю приложение и Python-компоненты…'));self.run(['bash',str(ROOT/'install.sh')])
   from importlib.util import spec_from_file_location,module_from_spec
   spec=spec_from_file_location('backend',ROOT/'backend.py');backend=module_from_spec(spec);spec.loader.exec_module(backend)
   if with_codex and not os.access(backend.find_codex(),os.X_OK):
    self.line(text('Downloading the official OpenAI Codex installer…','Загружаю официальный установщик OpenAI Codex…'))
    self.run([sys.executable,str(ROOT/'scripts/install-codex.py')])
   if with_decky:
    self.line(text('Installing Decky plugin. A terminal may ask for your sudo password.','Устанавливаю плагин Decky. В терминале может появиться запрос пароля sudo.'))
    # Konsole supplies an actual TTY for sudo instead of hiding its prompt.
    terminal=shutil.which('konsole')
    if terminal:self.run([terminal,'--separate','--nofork','-e','bash',str(ROOT/'scripts/install-decky.sh')])
    else:self.run(['bash',str(ROOT/'scripts/install-decky.sh')])
   self.line(text('Ready. Open Deck AI → sign in with ChatGPT → New chat.\nGaming Mode: (…) → Decky → Deck AI.','Готово. Откройте Deck AI → войдите в ChatGPT → Новый чат.\nGaming Mode: (…) → Decky → Deck AI.'));GLib.idle_add(self.open.set_sensitive,True)
  except Exception as exc:self.line(str(exc))
  finally:
   self.running=False
   for w in (self.button,self.decky,self.codex,self.language):GLib.idle_add(w.set_sensitive,True)
if __name__=='__main__':Setup();Gtk.main()
