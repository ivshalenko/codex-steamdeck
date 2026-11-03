"""Scrollable language/voice settings, with preparation outside the GTK thread."""
from pathlib import Path
import threading
from gi.repository import Gtk,GLib,Pango
from ui_extras import translator,LAYOUTS,ScrollablePicker
import language_support as support

SAMPLES={'ru':'Проверка голоса. Всё готово.','en':'Voice check. Everything is ready.','de':'Stimmtest. Alles ist bereit.','fr':'Test de voix. Tout est prêt.','es':'Prueba de voz. Todo está listo.','ja':'音声のテストです。準備ができました。','zh':'这是语音测试。一切准备就绪。','uk':'Перевірка голосу. Усе готово.'}

class LanguageSettings:
    def __init__(self,panel):
        self.panel=panel;self.closed=False;self.busy=False;self.cancel=threading.Event()
        self.catalog=support.read_json(panel.state_directory()/'voice-catalog.json',{})
        if not isinstance(self.catalog,dict):self.catalog={}
        self.systems=support.system_voices()
        self.dialog,self.body=panel.request_dialog(translator.text('Язык и голос'))
        self.dialog.add_button(translator.text('Закрыть'),Gtk.ResponseType.CANCEL)
        self.apply_button=self.dialog.add_button(translator.text('Подготовить и применить'),Gtk.ResponseType.APPLY)
        self.label('Язык интерфейса')
        self.interface_language=ScrollablePicker()
        for code,name in sorted(support.LANGUAGES.items(),key=lambda item:support.NATIVE.get(item[0],item[1])):
            self.interface_language.append(code,support.NATIVE.get(code,name)+' ('+code+')',name)
        self.interface_language.set_active_id(translator.language)
        self.body.pack_start(self.interface_language,False,False,0)
        self.label('Язык распознавания речи')
        self.language=ScrollablePicker()
        for code,name in sorted(support.LANGUAGES.items(),key=lambda item:support.NATIVE.get(item[0],item[1])):
            self.language.append(code,support.NATIVE.get(code,name)+' ('+code+')',name)
        self.language.set_active_id(getattr(panel,'voice_language',translator.language))
        self.language.set_tooltip_text(translator.text('Нажмите один раз, затем листайте список или используйте поиск'))
        self.body.pack_start(self.language,False,False,0)
        self.model_label=self.label('Модель распознавания')
        self.label('Голос для чтения ответов')
        self.voice=ScrollablePicker();self.body.pack_start(self.voice,False,False,0)
        self.refresh=Gtk.Button(label=translator.text('Обновить каталог нейроголосов'))
        self.refresh.connect('clicked',lambda *_:self.load_catalog())
        self.body.pack_start(self.refresh,False,False,0)
        self.read_replies=Gtk.CheckButton(label=translator.text('Читать новые ответы вслух'))
        self.read_replies.set_active(bool(panel.runtime_preferences.get('readReplies',False)))
        self.body.pack_start(self.read_replies,False,False,0)
        self.sample=Gtk.Entry();self.body.pack_start(self.sample,False,False,0)
        row=Gtk.Box(spacing=8)
        preview=Gtk.Button(label=translator.text('Проверить голос'))
        preview.connect('clicked',lambda *_:panel.speak_text(self.sample.get_text(),self.voice.get_active_id()))
        stop=Gtk.Button(label=translator.text('Остановить озвучку'))
        stop.connect('clicked',lambda *_:panel.stop_speaking())
        row.pack_start(preview,True,True,0);row.pack_start(stop,True,True,0)
        self.body.pack_start(row,False,False,0)
        model=panel.model_picker.get_active_id() or panel.current_model or '—'
        self.label(translator.text('Модель перевода интерфейса')+': '+model)
        self.label('Русский и английский встроены. Другие переводы готовятся выбранной моделью один раз и сохраняются на устройстве. Для перевода передаются статические надписи интерфейса.')
        self.label('При подготовке загрузится только выбранный голос и недостающая модель распознавания. Общая модель Whisper используется для 99 языков. Нейроголоса доступны не для всех языков.')
        self.status=self.label('Готово к выбору языка')
        self.spinner=Gtk.Spinner();self.body.pack_start(self.spinner,False,False,0)
        self.language.connect('changed',lambda *_:self.changed())
        self.dialog.connect('response',self.response)
        self.dialog.connect('destroy',self.destroyed)
        self.changed();self.dialog.show_all();translator.bind_tree(self.dialog)
        if not self.catalog:self.load_catalog()

    def label(self,text):
        label=Gtk.Label(label=translator.text(text),xalign=0)
        label.set_line_wrap(True);label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        label.set_width_chars(1);label.set_max_width_chars(65)
        self.body.pack_start(label,False,False,0)
        return label

    def code(self):
        code=self.language.get_active_id()
        return code if code in support.LANGUAGES else None

    def post(self,callback,*args):
        def run():
            if not self.closed:callback(*args)
            return False
        GLib.idle_add(run)

    def changed(self):
        code=self.code()
        if not code:return
        current=self.voice.get_active_id()
        choices=support.voices_for(code,self.systems,self.catalog)
        self.voice.remove_all();self.voice.append('none',translator.text('Без озвучки'))
        for voice in choices:self.voice.append(voice['id'],voice['name'])
        saved=self.panel.runtime_preferences.get('languageVoices',{}).get(code)
        if not saved and code==getattr(self.panel,'voice_language',''):saved=self.panel.runtime_preferences.get('ttsVoice')
        ids={v['id'] for v in choices}
        self.voice.set_active_id(current if current in ids else saved if saved in ids else choices[0]['id'] if choices else 'none')
        self.sample.set_text(SAMPLES.get(code,support.NATIVE.get(code,support.LANGUAGES[code])))
        model=support.VOSK.get(code,'Whisper small · 99 языков')
        ready=support.recognition_ready(self.panel.install_directory(),code)
        self.model_label.set_text(translator.text('Модель распознавания')+': '+model+' · '+translator.text('Установлена' if ready else 'Требуется загрузка'))
        self.status.set_text(translator.text('Язык выбран. Нажмите «Подготовить и применить».'))

    def load_catalog(self):
        if self.closed:return
        self.refresh.set_sensitive(False)
        def worker():
            try:
                catalog=support.voice_catalog(self.panel.state_directory(),refresh=True)
                self.post(self.catalog_ready,catalog)
            except Exception:
                self.post(self.catalog_error)
        threading.Thread(target=worker,daemon=True).start()

    def catalog_ready(self,catalog):
        self.catalog=catalog;self.refresh.set_sensitive(True);self.changed()

    def catalog_error(self):
        self.refresh.set_sensitive(True)
        self.status.set_text(translator.text('Каталог недоступен. Системные и ранее загруженные голоса остаются доступны.'))

    def response(self,dialog,response):
        if response!=Gtk.ResponseType.APPLY:
            self.cancel.set();dialog.destroy();return
        if self.busy:return
        code=self.code()
        if not code:
            self.status.set_text(translator.text('Выберите поддерживаемый язык из списка'));return
        interface_code=self.interface_language.get_active_id() or translator.language
        voice=self.voice.get_active_id() or 'none'
        read=self.read_replies.get_active()
        model=self.panel.model_picker.get_active_id() or self.panel.current_model
        provider=self.panel.provider;host=self.panel.remote_host
        sources=translator.source_strings()
        self.busy=True;self.spinner.start();self.apply_button.set_sensitive(False)
        self.language.set_sensitive(False);self.interface_language.set_sensitive(False);self.voice.set_sensitive(False);self.refresh.set_sensitive(False)
        self.cancel=threading.Event()
        def progress(text):self.post(self.status.set_text,translator.text(text))
        def worker():
            try:
                support.prepare_recognition(self.panel.install_directory(),code,self.cancel,progress)
                if voice!='none':support.prepare_voice(self.panel.install_directory(),self.panel.state_directory(),voice,self.catalog,self.cancel,progress)
                request=support.model_translation_request(provider,model,host)
                support.translate_pack(interface_code,sources,request,self.panel.state_directory(),self.cancel,progress)
                support.check_cancel(self.cancel)
                self.post(self.finished,code,voice,read,interface_code)
            except support.Cancelled:self.post(self.failed,'Подготовка отменена')
            except Exception as error:self.post(self.failed,str(error)[:400])
        threading.Thread(target=worker,daemon=True).start()

    def finished(self,code,voice,read,interface_code):
        self.panel.runtime_preferences['ttsVoice']=voice
        self.panel.runtime_preferences['readReplies']=read and voice!='none'
        self.panel.runtime_preferences.setdefault('languageVoices',{})[code]=voice
        self.panel.save_runtime_preferences()
        self.panel.voice_language=code
        self.panel.fast_voice.set_sensitive(code in ('ru','en'))
        (self.panel.state_directory()/'voice-language').write_text(code)
        self.panel.voice_language_button.set_label('🎙 '+code.upper())
        self.panel.change_language(interface_code)
        if code.upper() in LAYOUTS:self.panel.app_keyboard.select_layout(code.upper())
        self.panel.message(translator.text('Язык и голос готовы'))
        self.dialog.destroy()

    def failed(self,message):
        self.busy=False;self.spinner.stop();self.apply_button.set_sensitive(True)
        self.language.set_sensitive(True);self.interface_language.set_sensitive(True);self.voice.set_sensitive(True);self.refresh.set_sensitive(True)
        self.status.set_text(translator.text(message))

    def destroyed(self,*_):
        self.closed=True;self.cancel.set()
