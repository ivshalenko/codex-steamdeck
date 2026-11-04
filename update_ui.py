"""Native desktop update controls; the worker owns installation, not this window."""
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,GLib
import ui_extras

def text(en,ru):return ru if ui_extras.translator.language=='ru' else en

def show(parent,controller,begin):
 dialog=Gtk.Dialog(title=text('Deck AI updates','Обновления Deck AI'),transient_for=parent,modal=True);dialog._deck_ai_update_dialog=True
 dialog.set_default_size(650,460);dialog.add_button(text('Close','Закрыть'),Gtk.ResponseType.CLOSE)
 box=dialog.get_content_area();box.set_spacing(12);box.set_border_width(18)
 title=Gtk.Label(xalign=0);title.set_line_wrap(True);box.pack_start(title,False,False,0)
 info=Gtk.Label(xalign=0);info.set_line_wrap(True);box.pack_start(info,False,False,0)
 automatic=Gtk.CheckButton(label=text('Check GitHub automatically once a week','Проверять обновления на GitHub раз в неделю'));box.pack_start(automatic,False,False,0)
 channel=Gtk.ComboBoxText()
 for key,en,ru in [('automatic','Automatic channel (match installed release)','Канал автоматически по установленной версии'),('stable','Stable releases','Стабильные выпуски'),('preview','Stable and preview releases','Стабильные и предварительные выпуски')]:channel.append(key,text(en,ru))
 box.pack_start(channel,False,False,0)
 progress=Gtk.ProgressBar();box.pack_start(progress,False,False,0)
 details=Gtk.Label(xalign=0);details.set_line_wrap(True);details.set_selectable(True);scroll=Gtk.ScrolledWindow();scroll.add(details);box.pack_start(scroll,True,True,0)
 row=Gtk.Box(spacing=10);box.pack_start(row,False,False,0)
 check=Gtk.Button(label=text('Check now','Проверить сейчас'));row.pack_start(check,False,False,0)
 install=Gtk.Button(label=text('Update now','Обновить'));install.get_style_context().add_class('suggested-action');row.pack_start(install,True,True,0)
 state=[None];changing=[False];closed=[False]
 def refresh():
  if closed[0]:return False
  try:
   value=controller.status();state[0]=value;available=value.get('available');job=value.get('job') or {};phase=job.get('phase');active=phase in ('queued','downloading','quiescing','installing','verifying','rolling-back')
   title.set_text(text('Installed: ','Установлено: ')+', '.join(k+' '+v for k,v in value['installed'].items()))
   info.set_text(text('Updating… keep Steam and Decky running.','Обновление… оставьте Steam и Decky включёнными.') if active else text('Update available: ','Доступно обновление: ')+available['version'] if available else text('No newer compatible release is available.','Новой совместимой версии пока нет.'))
   changing[0]=True;automatic.set_active(value['preferences']['automatic']);channel.set_active_id(value['preferences']['channel']);changing[0]=False
   automatic.set_sensitive(not active);channel.set_sensitive(not active);check.set_sensitive(not active and not value['checking'])
   install.set_sensitive(bool(available) and not active and not value['busyDesktop'] and not value.get('requiresInstaller'))
   install.set_label(text('Update to ','Обновить до ')+available['version'] if available else text('Up to date','Актуальная версия'))
   progress.set_fraction(float(job.get('progress') or 0));progress.set_visible(active)
   details.set_text(job.get('error') or value.get('checkError') or text('The idle desktop app closes to apply the update, then reopens. Your draft and settings are kept.','Для обновления неработающее окно приложения закроется и откроется заново. Черновик и настройки сохранятся.'))
  except Exception as exc:details.set_text(str(exc))
  return True
 def configure(*_):
  if changing[0]:return
  try:controller.configure(automatic.get_active(),channel.get_active_id());refresh()
  except Exception as exc:details.set_text(str(exc))
 def update(*_):
  value=state[0]
  if not value or not value.get('available'):return
  try:begin(value['available']['version']);refresh()
  except Exception as exc:details.set_text(str(exc))
 automatic.connect('toggled',configure);channel.connect('changed',configure)
 check.connect('clicked',lambda *_:(controller.check_async(),refresh()));install.connect('clicked',update)
 def close(*_):closed[0]=True;dialog.destroy()
 dialog.connect('response',close);dialog.connect('destroy',lambda *_:closed.__setitem__(0,True));dialog.show_all();refresh();GLib.timeout_add(1000,refresh)
 return dialog
