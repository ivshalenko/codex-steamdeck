"""Receiving-side setup, available even without Decky Loader."""
import shutil,subprocess,threading
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,Gdk,GLib
import deck_share

def show(parent,language='ru'):
 def t(ru,en):return ru if language.startswith('ru') else en
 dialog=Gtk.Dialog(title=t('Доступ к этому Steam Deck','Access this Steam Deck'),transient_for=parent,modal=True)
 dialog.set_default_size(720,590);dialog.add_button(t('Закрыть','Close'),Gtk.ResponseType.CLOSE)
 body=dialog.get_content_area();body.set_spacing(10);body.set_border_width(18)
 intro=Gtk.Label(label=t('Mac/ПК → этот Steam Deck. Команды выполняются на Deck.\nНа компьютере распакуйте Remote Control из релиза и запустите connect-deck.py.','Mac/PC → this Steam Deck. Commands execute on Deck.\nOn the computer, unzip the release Remote Control package and run connect-deck.py.'));intro.set_line_wrap(True);body.pack_start(intro,False,False,0)
 info=Gtk.TextView(editable=False,monospace=True,wrap_mode=Gtk.WrapMode.WORD_CHAR);scroll=Gtk.ScrolledWindow();scroll.set_min_content_height(180);scroll.add(info);body.pack_start(scroll,True,True,0)
 note=Gtk.Label(label=t('Включение SSH может запросить пароль администратора в отдельном терминале.\nЕсли пароль ещё не задан: Desktop Mode → Konsole → passwd.','Enabling SSH may ask for your administrator password in a separate terminal.\nIf no password is set: Desktop Mode → Konsole → passwd.'));note.set_line_wrap(True);body.pack_start(note,False,False,0)
 row=Gtk.Box(spacing=8);body.pack_start(row,False,False,0)
 status=Gtk.Label();status.set_line_wrap(True);body.pack_end(status,False,False,0)
 alive=[True]
 def apply(value):
  if not alive[0]:return
  text=t('SSH работает: ','SSH running: ')+str(value['sshActive'])+'\n'+t('Пользователь: ','User: ')+value['user']+'\n'+t('Адрес: ','Address: ')+(', '.join(value['addresses']) or '—')+'\n\n'+t('Сверьте этот отпечаток при первом подключении:','Compare this fingerprint on your first connection:')+'\n'+'\n'.join(value.get('fingerprints',[]))
  info.get_buffer().set_text(text)
 def refresh(*_):
  info.get_buffer().set_text(t('Проверяю подключение…','Checking connection…'))
  threading.Thread(target=lambda:GLib.idle_add(apply,deck_share.status()),daemon=True).start()
 enable=Gtk.Button(label=t('Включить SSH','Enable SSH'))
 def enable_ssh(*_):
  terminal=shutil.which('konsole')
  if not terminal:status.set_text('Konsole: sudo systemctl enable --now sshd');return
  subprocess.Popen([terminal,'--separate','-e','bash','-c','sudo systemctl enable --now sshd; result=$?; read -r -p "Press Enter to close"; exit "$result"'],start_new_session=True)
  status.set_text(t('После завершения нажмите «Обновить».','After the terminal finishes, click Refresh.'))
 enable.connect('clicked',enable_ssh);row.pack_start(enable,False,False,0)
 update=Gtk.Button(label=t('Обновить','Refresh'));update.connect('clicked',refresh);row.pack_start(update,False,False,0)
 label=Gtk.Label(label=t('Вставьте публичный ключ из мастера на Mac/ПК:','Paste the public key from the computer wizard:'));body.pack_start(label,False,False,0)
 key=Gtk.Entry(placeholder_text='ssh-ed25519 AAAA…');body.pack_start(key,False,False,0)
 add=Gtk.Button(label=t('Разрешить этому компьютеру','Authorize this computer'));body.pack_start(add,False,False,0)
 def save(*_):
  try:
   result=deck_share.add_key(key.get_text());key.set_text('');status.set_text(t('Ключ добавлен. Вернитесь к мастеру на компьютере.','Key added. Continue the wizard on your computer.') if result['added'] else t('Этот ключ уже добавлен.','This key is already authorized.'))
  except (OSError,ValueError) as exc:status.set_text(str(exc))
 add.connect('clicked',save);dialog.show_all();refresh();dialog.run();alive[0]=False;dialog.destroy()
