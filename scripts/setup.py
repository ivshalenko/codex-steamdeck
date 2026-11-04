#!/usr/bin/env python3
"""Illustrated first-run installer. System authorization stays in a real terminal."""
import argparse,os,subprocess,sys,threading
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from setup_support import Options,run_install
from decky.runtime_paths import resolve_state_dir
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,GLib,Gdk,GdkPixbuf

STAGES={
 'validate':('Checking packaged files','Проверка файлов установщика'),
 'application':('Installing Deck AI','Установка Deck AI'),
 'codex':('Preparing official Codex CLI','Подготовка официального Codex CLI'),
 'voice':('Preparing local dictation','Подготовка локальной диктовки'),
 'system':('Waiting for SteamOS authorization','Ожидание разрешения SteamOS'),
 'ready':('Installation complete','Установка завершена')}

class Setup(Gtk.Window):
 def __init__(self,language=None):
  super().__init__(title='Deck AI · Setup')
  candidate=language or os.environ.get('DECK_AI_SETUP_LANGUAGE','en');self.language_code=candidate if candidate in ('en','ru') else 'en'
  self.running=False;self.installed=None;self.choices={'mode':'automatic','codex':True,'decky':True,'loader':True,'voice':False,'ssh':False,'read_only':(resolve_state_dir()/'read-only').exists()}
  self.set_default_size(900,720);self.set_position(Gtk.WindowPosition.CENTER);self.set_name('deck-ai-setup');self.connect('delete-event',self.close)
  css=Gtk.CssProvider();css.load_from_data(b'#deck-ai-setup { background: #101a26; color: #edf5fc; } #deck-ai-setup label { color: #edf5fc; } #deck-ai-setup .muted { color: #b2c6d7; } #deck-ai-setup .heading { font-size: 23px; font-weight: bold; } #deck-ai-setup .card { background: #1b2a3b; border-radius: 12px; padding: 12px; } #deck-ai-setup .suggested-action { background: #287cac; color: white; border-radius: 8px; padding: 9px 20px; } #deck-ai-setup .error { color: #ffbf9e; }')
  Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
  self.build();self.show_all();self.details.set_reveal_child(False)
 def t(self,en,ru):return ru if self.language_code=='ru' else en
 def label(self,en,ru=None,style=None):
  label=Gtk.Label(label=self.t(en,ru or en),xalign=0);label.set_line_wrap(True);label.set_max_width_chars(90)
  if style:label.get_style_context().add_class(style)
  return label
 def box(self,spacing=9):return Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=spacing)
 def button(self,en,ru,callback,primary=False):
  button=Gtk.Button(label=self.t(en,ru));button.connect('clicked',callback)
  if primary:button.get_style_context().add_class('suggested-action')
  return button
 def snapshot_choices(self):
  self.choices.update(mode='custom' if self.custom.get_active() else 'automatic',read_only=self.actions.get_active_id()=='history')
  for key,widget in self.components.items():self.choices[key]=widget.get_active()
 def build(self):
  self.set_title(self.t('Deck AI · Setup','Deck AI · Установка'))
  old=self.get_child()
  if old:self.remove(old);old.destroy()
  outer=self.box(12);outer.set_border_width(18);self.add(outer)
  try:
   banner=GdkPixbuf.Pixbuf.new_from_file_at_scale(str(ROOT/'docs/brand/installer.svg'),840,147,True)
   outer.pack_start(Gtk.Image.new_from_pixbuf(banner),False,False,0)
  except GLib.Error:outer.pack_start(self.label('Deck AI',style='heading'),False,False,0)
  row=Gtk.Box(spacing=12);outer.pack_start(row,False,False,0)
  row.pack_start(self.label('Make your Deck ready.','Подготовим ваш Steam Deck.',style='heading'),True,True,0)
  row.pack_start(self.label('Language','Язык'),False,False,0)
  self.language=Gtk.ComboBoxText();self.language.append('en','English');self.language.append('ru','Русский');self.language.set_active_id(self.language_code);self.language.connect('changed',self.change_language);row.pack_start(self.language,False,False,0)
  outer.pack_start(self.label('1  Choose     →     2  Install     →     3  Sign in & play','1  Выбор     →     2  Установка     →     3  Вход и запуск','muted'),False,False,0)
  self.stack=Gtk.Stack();self.stack.set_homogeneous(False);outer.pack_start(self.stack,True,True,0)
  self.build_choices();self.build_progress();self.build_ready();self.stack.set_visible_child_name('choose')
  footer=Gtk.Box(spacing=12);outer.pack_end(footer,False,False,0)
  version=(ROOT/'VERSION').read_text().strip();footer.pack_start(self.label(version+' · ivshalenko',style='muted'),True,True,0)
  guide='QUICKSTART.ru.md' if self.language_code=='ru' else 'QUICKSTART.md'
  footer.pack_start(Gtk.LinkButton.new_with_label('https://github.com/ivshalenko/codex-steamdeck/blob/main/docs/'+guide,self.t('Installation & remote control guide','Установка и связь с компьютером')),False,False,0)
 def build_choices(self):
  page=self.box(10);scroll=Gtk.ScrolledWindow();scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC);scroll.add(page)
  self.stack.add_named(scroll,'choose')
  card=self.box(7);card.get_style_context().add_class('card');page.pack_start(card,False,False,0)
  self.auto=Gtk.RadioButton.new_with_label_from_widget(None,self.t('Automatic · recommended','Автоматически · рекомендуется'))
  self.custom=Gtk.RadioButton.new_with_label_from_widget(self.auto,self.t('Custom · choose components and access','Вручную · компоненты и доступ'))
  self.auto.set_active(self.choices['mode']=='automatic');self.custom.set_active(self.choices['mode']=='custom')
  card.pack_start(self.auto,False,False,0)
  card.pack_start(self.label('Installs Deck AI, official Codex and the Decky plugin. Installs Decky Loader if missing. Keeps your chats, models and accounts.','Установит Deck AI, официальный Codex и плагин Decky. Если Decky Loader отсутствует — установит его. Сохранит чаты, модели и аккаунты.','muted'),False,False,0)
  card.pack_start(self.custom,False,False,0)
  self.details=Gtk.Revealer();self.details.set_transition_type(Gtk.RevealerTransitionType.NONE);page.pack_start(self.details,False,False,0)
  detail=self.box(8);detail.get_style_context().add_class('card');self.details.add(detail);self.components={}
  values=[('codex','Install Codex if missing','Установить Codex, если отсутствует'),('decky','Add the Gaming Mode plugin','Добавить плагин Gaming Mode'),('loader','Install Decky Loader if missing','Установить Decky Loader, если отсутствует'),('voice','Download local dictation for the selected language (optional)','Загрузить локальную диктовку для выбранного языка (необязательно)'),('ssh','Enable SSH for Mac / PC remote control (optional)','Включить SSH для управления с Mac / ПК (необязательно)')]
  for key,en,ru in values:
   widget=Gtk.CheckButton(label=self.t(en,ru));widget.set_active(self.choices[key]);detail.pack_start(widget,False,False,0);self.components[key]=widget
  actionrow=Gtk.Box(spacing=10);detail.pack_start(actionrow,False,False,0);actionrow.pack_start(self.label('Decky access','Доступ в Decky'),True,True,0)
  self.actions=Gtk.ComboBoxText();self.actions.append('confirm',self.t('Chat & confirmed actions','Чат и действия с подтверждением'));self.actions.append('history',self.t('History only · no sending or edits','Только история · без отправки и правок'));self.actions.set_active_id('history' if self.choices['read_only'] else 'confirm');actionrow.pack_start(self.actions,False,False,0)
  self.note=self.label('Automatic setup does not enable SSH or add voice packs. You can add them later. Actions ask for confirmation in the app; existing action preferences are kept on updates.','Автоматическая установка не включает SSH и голосовые пакеты. Их можно добавить позже. Действия подтверждаются в приложении; при обновлении настройки действий сохраняются.','muted');page.pack_start(self.note,False,False,0)
  page.pack_start(self.label('SteamOS may ask for your administrator password in a separate terminal. ChatGPT sign-in happens after installation. Deck AI never asks you to paste a password or token here.','SteamOS может запросить пароль администратора в отдельном терминале. Вход в ChatGPT — после установки. Deck AI не просит вставлять сюда пароль или токен.','muted'),False,False,0)
  access=Gtk.Expander(label=self.t('What access does this use?','Какой доступ используется?'));page.pack_start(access,False,False,0)
  access.add(self.label('Network: downloads and your chosen AI provider. Files and commands: your account, with in-app confirmations. Microphone: only when you press Dictate. SSH: only if selected; authorize your computer separately. No account sign-in is automatic.','Сеть: загрузки и выбранный ИИ-провайдер. Файлы и команды: от вашего пользователя, с подтверждениями в приложении. Микрофон: при нажатии «Говорить». SSH: только если выбран; компьютер нужно разрешить отдельно. Вход в аккаунт не выполняется автоматически.','muted'))
  self.install_button=self.button('Install automatically','Установить автоматически',self.start,True);page.pack_start(self.install_button,False,False,0)
  self.custom.connect('toggled',self.mode_changed);self.components['decky'].connect('toggled',self.component_access);self.mode_changed();self.component_access()
 def component_access(self,*_):
  enabled=self.components['decky'].get_active();self.components['loader'].set_sensitive(enabled);self.actions.set_sensitive(enabled)
 def mode_changed(self,*_):
  custom=self.custom.get_active();self.details.set_reveal_child(custom)
  self.install_button.set_label(self.t('Install selected components' if custom else 'Install automatically','Установить выбранное' if custom else 'Установить автоматически'))
  self.note.set_visible(not custom)
 def change_language(self,*_):
  code=self.language.get_active_id()
  if self.running or not code or code==self.language_code:return
  self.snapshot_choices();self.language_code=code;self.build();self.show_all();self.mode_changed()
 def build_progress(self):
  page=self.box(14);self.stack.add_named(page,'progress')
  self.status=self.label('Preparing installation…','Подготовка установки…',style='heading');page.pack_start(self.status,False,False,0)
  self.progress=Gtk.ProgressBar();self.progress.set_show_text(True);page.pack_start(self.progress,False,False,0)
  self.progress_note=self.label('Keep this window open. If a SteamOS terminal appears, complete its password prompt there.','Не закрывайте окно. Если открылся терминал SteamOS, подтвердите запрос пароля в нём.','muted');page.pack_start(self.progress_note,False,False,0)
  self.log=Gtk.TextView(editable=False,monospace=True,wrap_mode=Gtk.WrapMode.WORD_CHAR);self.log.set_cursor_visible(False);scroll=Gtk.ScrolledWindow();scroll.set_min_content_height(140);scroll.add(self.log);page.pack_start(scroll,True,True,0)
  self.retry=self.button('Back to choices / retry','Вернуться к выбору / повторить',self.retry_install);page.pack_start(self.retry,False,False,0)
 def build_ready(self):
  page=self.box(15);self.stack.add_named(page,'ready')
  page.pack_start(self.label('Your Deck is ready.','Steam Deck готов.',style='heading'),False,False,0)
  self.ready_note=self.label('1. Open Deck AI and sign into ChatGPT.\n2. Return to Gaming Mode → (…) → Decky → Deck AI.\n3. Choose New chat and ask your first question.','1. Откройте Deck AI и войдите в ChatGPT.\n2. Вернитесь в Gaming Mode → (…) → Decky → Deck AI.\n3. Выберите «Новый чат» и задайте вопрос.');page.pack_start(self.ready_note,False,False,0)
  page.pack_start(self.label('Interface language: English','Язык интерфейса: русский','muted'),False,False,0)
  self.open=self.button('Open Deck AI and sign in','Открыть Deck AI и войти',self.open_app,True);page.pack_start(self.open,False,False,0)
  page.pack_start(self.button('Connect a Mac / PC','Подключить Mac / ПК',self.open_remote),False,False,0)
  page.pack_start(self.button('Close installer','Закрыть установщик',lambda *_:self.close()),False,False,0)
 def line(self,value):
  def append():
   buf=self.log.get_buffer();buf.insert(buf.get_end_iter(),value+'\n');self.log.scroll_to_iter(buf.get_end_iter(),0,False,0,0);return False
  GLib.idle_add(append)
 def set_progress(self,stage,fraction):
  def update():self.status.set_text(self.t(*STAGES[stage]));self.progress.set_fraction(fraction);self.progress.set_text(str(round(fraction*100))+'%');return False
  GLib.idle_add(update)
 def run(self,command):
  env={**os.environ,'PYTHONUNBUFFERED':'1','DECK_AI_SETUP_LANGUAGE':self.language_code}
  process=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,env=env)
  for line in process.stdout:self.line(line.rstrip())
  if process.wait():raise RuntimeError(self.t('This step failed. Review the details and choose Retry.','Этап не выполнен. Посмотрите подробности и повторите установку.'))
 def start(self,*_):
  if self.running:return
  self.snapshot_choices();options=Options(language=self.language_code,**self.choices)
  self.running=True;self.language.set_sensitive(False);self.open.set_sensitive(False);self.retry.hide();self.log.get_buffer().set_text('');self.stack.set_visible_child_name('progress')
  threading.Thread(target=self.work,args=(options,),daemon=True).start()
 def work(self,options):
  try:installed=run_install(options,ROOT,self.run,self.set_progress)
  except Exception as exc:GLib.idle_add(self.finish_error,str(exc));return
  GLib.idle_add(self.finish_success,installed,options)
 def finish_error(self,message):
  self.running=False;self.language.set_sensitive(True);self.status.set_text(self.t('Setup needs your attention','Нужно ваше внимание'));self.status.get_style_context().add_class('error');self.line(message);self.retry.show();return False
 def finish_success(self,installed,options):
  self.running=False;self.installed=installed;self.open.set_sensitive(True)
  if not options.decky:self.ready_note.set_text(self.t('Open Deck AI and sign into ChatGPT.\nChoose New chat to begin. You can add the Gaming Mode plugin later.','Откройте Deck AI и войдите в ChatGPT.\nВыберите «Новый чат». Плагин Gaming Mode можно добавить позже.'))
  if not options.codex:
   from setup_support import codex_installed
   if not codex_installed():self.ready_note.set_text(self.t('Deck AI is installed. Codex was not selected. Install Codex or choose another provider in the app settings before starting a task.','Deck AI установлен. Установка Codex не выбрана. Установите Codex или выберите другого провайдера в настройках, прежде чем начинать задачу.'))
  self.stack.set_visible_child_name('ready');return False
 def retry_install(self,*_):
  if self.running:return
  self.language.set_sensitive(True);self.status.get_style_context().remove_class('error');self.stack.set_visible_child_name('choose')
 def open_app(self,*_):
  if self.installed:subprocess.Popen([str(Path.home()/'.local/bin/deck-ai')],start_new_session=True)
 def open_remote(self,*_):
  if not self.installed:return
  code='import remote_access;remote_access.show(None,'+repr(self.language_code)+')'
  subprocess.Popen([str(self.installed/'venv/bin/python'),'-c',code],cwd=self.installed,start_new_session=True)
 def close(self,*_):
  if self.running:self.progress_note.set_text(self.t('Installation is running. Wait until this step finishes.','Установка идёт. Дождитесь завершения этапа.'));return True
  self.destroy();Gtk.main_quit();return False
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--language',choices=('en','ru'),default=os.environ.get('DECK_AI_SETUP_LANGUAGE','en'));args=parser.parse_args();Setup(args.language);Gtk.main()
