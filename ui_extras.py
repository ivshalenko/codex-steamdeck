"""App-local multilingual input; never injects keys into other applications."""
import json
import weakref
from decky.runtime_paths import resolve_state_dir
from pathlib import Path
from gi.repository import Gtk, Gdk

STATE=resolve_state_dir()/'language'
EN={
'Без рассуждений':'No reasoning','Минимальная':'Minimal','Низкая · быстрее':'Low · faster','Средняя · баланс':'Medium · balanced','Очень высокая':'Very high','Максимальная':'Maximum',
'Модель':'Model','Чаты':'Chats','В работе':'Working','Готов':'Ready','Не удалось сохранить черновик на диск.':'Could not save your draft.',
'Личный помощник':'Personal assistant','Готов к работе':'Ready','Светлая':'Light','Тёмная':'Dark','Клавиатура':'Keyboard',
'Новый чат':'New chat','Найти чат':'Search chats','СОХРАНЁННЫЕ ЧАТЫ':'SAVED CHATS','Ещё чаты':'More chats','Модель для новых сообщений':'Model for new messages',
'Глубина обработки':'Reasoning effort','Скорость':'Speed','Текущий разговор':'Current conversation','Подключаюсь к вашему диалогу…':'Connecting to your conversation…',
'Остановить':'Stop','Подключиться':'Connect','Что сделаем сегодня? Напишите или продиктуйте…':'What shall we do? Type or dictate…','Говорить':'Dictate','Закончить':'Finish',
'Отправить':'Send','Распознавание на устройстве':'On-device speech recognition','Проверьте текст перед отправкой':'Review your text before sending','Очистить':'Clear',
'Загружаю историю разговора…':'Loading conversation history…','Открываю чат…':'Opening chat…','Deck AI работает…':'Deck AI is working…',
'Продолжите разговор голосом или текстом':'Continue by voice or text','Выполняю действие на устройстве…':'Working on your device…','Сохраняю изменения…':'Saving changes…',
'Не удалось подключиться. Нажмите «Подключиться».':'Could not connect. Press Connect.','Черновик сохранён. Нажмите «Подключиться».':'Draft saved. Press Connect.',
'Распознаю…':'Transcribing…','Подготовка микрофона…':'Preparing microphone…','● Слушаю · нажмите «Закончить»':'● Listening · press Finish',
'Проверьте текст и нажмите «Отправить»':'Review your text and press Send','Речь не распознана. Попробуйте ещё раз.':'No speech recognized. Try again.',
'Сообщение уже отправляется…':'Message is already being sent…','Сначала закончите запись.':'Finish recording first.',
'Сначала подключитесь к Codex. Черновик сохранён.':'Connect to Codex first. Your draft is saved.','Отправляю…':'Sending…',
'Обычная':'Standard','Низкая':'Low','Средняя':'Medium','Высокая':'High','Повторить':'Retry','Вставить':'Paste','Пробел':'Space','Скрыть':'Hide',
'Скрыть окно':'Hide window','Свернуть':'Minimize','Завершить приложение':'Quit application',
'Аккаунт':'Account','Аккаунт: проверка…':'Account: checking…','Вход не выполнен':'Not signed in','Войти или сменить аккаунт':'Sign in or switch account','Выйти из аккаунта':'Sign out','Войти через ChatGPT':'Sign in with ChatGPT','Страница входа открыта в браузере.':'The sign-in page opened in your browser.','Вы вышли из аккаунта Codex.':'You signed out of Codex.','Не удалось открыть браузер.':'Could not open the browser.',
'Подключить ИИ-провайдера или устройство':'Connect an AI provider or device','Подключить Codex на другом компьютере':'Connect Codex on another computer','Подключить Claude Pro / Max':'Connect Claude Pro / Max','Подключить DeepSeek через OpenRouter':'Connect DeepSeek via OpenRouter',
'Подключить DeepSeek через TokenHarbor':'Connect DeepSeek via TokenHarbor','DeepSeek · TokenHarbor':'DeepSeek · TokenHarbor','Настроить TokenHarbor':'Set up TokenHarbor',
'Источник моделей':'Model provider','Выбрать ИИ-провайдера':'Choose AI provider','Codex · ChatGPT':'Codex · ChatGPT','Claude · Pro / Max':'Claude · Pro / Max','DeepSeek · OpenRouter':'DeepSeek · OpenRouter','Настроить DeepSeek / OpenRouter':'Set up DeepSeek / OpenRouter','Войти в Claude Code':'Sign in to Claude Code','Отправляю запрос…':'Sending request…','Ответ Claude готов':'Claude replied','Ответ DeepSeek готов':'DeepSeek replied',
'УСТРОЙСТВО CODEX':'CODEX DEVICE','Этот Steam Deck · локальные чаты':'This Steam Deck · local chats','Подключить компьютер':'Connect a computer','Список Mac и Windows берётся из SSH-конфигурации Steam Deck.':'Mac and Windows devices are listed from the Steam Deck SSH configuration.','Выберите компьютер из SSH-конфигурации. На нём нужен Codex с активным входом.':'Choose a computer from SSH configuration. Codex must be installed and signed in there.','Других устройств пока нет. Добавьте SSH-хост кнопкой «Подключить компьютер».':'No other devices yet. Add an SSH host with “Connect a computer”.','Подключить удалённый Codex':'Connect remote Codex','Добавьте устройство или выберите готовый SSH-алиас.':'Add a device or choose an existing SSH alias.','Имя в Codex':'Codex device name','например, macbook':'for example, macbook','Адрес компьютера':'Computer address','IP или имя в сети':'IP address or network name','Пользователь SSH':'SSH user','учётная запись Mac/Windows':'Mac/Windows account','Путь к SSH-ключу':'SSH key path','Для нового подключения укажите адрес и пользователя. На втором компьютере включите SSH и разрешите вход по вашему публичному ключу; Codex CLI должен быть установлен и авторизован.':'For a new connection, enter the address and user. Enable SSH on the other computer and authorize your public key; Codex CLI must be installed and signed in.','Отмена':'Cancel','Подключить':'Connect','Проверьте адрес и имя пользователя SSH.':'Check the SSH address and username.','Укажите короткое имя устройства латиницей.':'Enter a short device name using Latin characters.','Проверьте путь к SSH-ключу.':'Check the SSH key path.','Обновить список SSH-устройств из ~/.ssh/config':'Refresh SSH devices from ~/.ssh/config',
}
class Translator:
    def __init__(self):
        self.language=STATE.read_text().strip() if STATE.exists() else 'en'
        self.widgets=weakref.WeakSet()
    def text(self,value):return EN.get(value,value) if self.language=='en' else value
    def set_language(self,code):
        self.language=code if code in ('ru','en') else 'ru'
        STATE.parent.mkdir(parents=True,exist_ok=True)
        STATE.write_text(self.language)
        for widget in list(self.widgets):widget.refresh_translation()
translator=Translator()
class UILabel(Gtk.Label):
    def __init__(self,label=None,**kwargs):
        super().__init__(**kwargs)
        translator.widgets.add(self)
        self.source=label or ''
        self.refresh_translation()
    def set_text(self,text):
        self.source=text
        Gtk.Label.set_text(self,translator.text(text))
    def refresh_translation(self):Gtk.Label.set_text(self,translator.text(self.source))

LAYOUTS={
'RU':['ёйцукенгшщзхъ','фывапролджэ','ячсмитьбю'],
'EN':['qwertyuiop','asdfghjkl','zxcvbnm'],
'DE':['qwertzuiopü','asdfghjklöä','yxcvbnmß'],
'FR':['azertyuiop','qsdfghjklm','wxcvbnçéèà'],
'ES':['qwertyuiop','asdfghjklñ','zxcvbnmáéíóú'],
'UK':['йцукенгшщзхї','фівапролджє','ячсмитьбюґ'],
'IT':['qwertyuiopè','asdfghjklòà','zxcvbnmùì'],
}
class AppKeyboard(Gtk.Box):
    def __init__(self,editor,toggle,root):
        super().__init__(orientation=Gtk.Orientation.VERTICAL,spacing=4)
        self.editor=editor;self.toggle=toggle;self.shift=False;self.symbols=False
        self.path=STATE.parent/'keyboard-layout'
        self.layout=self.path.read_text().strip() if self.path.exists() else 'EN'
        if self.layout not in LAYOUTS:self.layout='EN'
        self.get_style_context().add_class('keyboard')
        self.refresh()
    def key(self,label,callback,expand=True):
        button=Gtk.Button(label=label);button.set_focus_on_click(False)
        button.connect('clicked',lambda *_:callback())
        button.set_hexpand(expand)
        return button
    def insert(self,value):
        buf=self.editor.get_buffer();buf.delete_selection(True,True)
        buf.insert_at_cursor(value)
        self.editor.grab_focus();self.editor.scroll_mark_onscreen(buf.get_insert())
    def backspace(self):
        buf=self.editor.get_buffer()
        if not buf.delete_selection(True,True):buf.backspace(buf.get_iter_at_mark(buf.get_insert()),True,True)
        self.editor.grab_focus()
    def paste(self):
        Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).request_text(lambda _,text,*args:self.insert(text) if text else None)
    def select_layout(self,code):
        self.layout=code;self.path.write_text(code);self.refresh()
    def cycle(self):self.select_layout('EN' if self.layout=='RU' else 'RU')
    def flip(self,attribute):setattr(self,attribute,not getattr(self,attribute));self.refresh()
    def move_cursor(self, delta):
        buf=self.editor.get_buffer()
        cursor=buf.get_iter_at_mark(buf.get_insert())
        if delta<0:cursor.backward_cursor_position()
        else:cursor.forward_cursor_position()
        buf.place_cursor(cursor);self.editor.grab_focus()

    def language_menu(self, button):
        popover=Gtk.Popover.new(button)
        popover.get_style_context().add_class('selection-popover')
        options=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=3,margin=6)
        for code in LAYOUTS:
            key=self.key(code,lambda c=code:(popover.popdown(),self.select_layout(c)))
            options.pack_start(key,False,False,0)
        popover.add(options);popover.show_all();popover.popup()

    def refresh(self):
        for child in self.get_children():child.destroy()
        self.set_spacing(7)
        rows=['1234567890','@#$%&*()[]','.,?!:;/_+-='] if self.symbols else LAYOUTS[self.layout]
        columns=max(28,len(rows[0])*2+4,len(rows[1])*2+4,len(rows[2])*2+8)
        grid=Gtk.Grid(column_spacing=6,row_spacing=7,column_homogeneous=True)
        self.pack_start(grid,False,False,0)
        def add(label,callback,x,y,width=2,tool=False):
            key=self.key(label,callback)
            key.set_size_request(-1,60)
            if tool:key.get_style_context().add_class('key-tool')
            grid.attach(key,x,y,width,1)
            return key
        for row,chars in enumerate(rows):
            offset=0 if row==0 else (1 if row==1 else 4)
            for index,ch in enumerate(chars):
                value=ch.upper() if self.shift else ch
                add(value,lambda v=value:self.insert(v),offset+index*2,row)
            end=offset+len(chars)*2
            if row==0:add('⌫',self.backspace,end,row,columns-end,True)
            elif row==1:add('↵',lambda:self.insert('\n'),end,row,columns-end,True)
            else:
                shift=add('⇧',lambda:self.flip('shift'),0,row,4,True)
                if self.shift:shift.get_style_context().add_class('selected')
                add(',',lambda:self.insert(','),end,row,2)
                add('.',lambda:self.insert('.'),end+2,row,columns-end-2)
        add('ABC' if self.symbols else '?123',lambda:self.flip('symbols'),0,3,4,True)
        language=add('RU / EN' if self.layout in ('RU','EN') else self.layout,self.cycle,4,3,4,True)
        language.set_tooltip_text('RU ↔ EN · удерживайте для других языков' if translator.language=='ru' else 'RU ↔ EN · hold for other languages')
        gesture=Gtk.GestureLongPress.new(language)
        gesture.connect('pressed',lambda *_:self.language_menu(language))
        language._long_press=gesture
        add(translator.text('Вставить'),self.paste,8,3,4,True)
        add(self.layout+' · '+translator.text('Пробел'),lambda:self.insert(' '),12,3,columns-20,True)
        add('←',lambda:self.move_cursor(-1),columns-8,3,2,True)
        add('→',lambda:self.move_cursor(1),columns-6,3,2,True)
        add('⌄',self.toggle,columns-4,3,4,True)
        if self.get_visible():
            previous=self.get_no_show_all();self.set_no_show_all(False);self.show_all();self.set_no_show_all(previous)

class CompactPicker(Gtk.MenuButton):
    """Bounded selection popover, with the ComboBoxText interface used by Panel."""
    from gi.repository import GObject
    __gsignals__={'changed':(GObject.SignalFlags.RUN_FIRST,None,())}
    def __init__(self):
        super().__init__()
        from gi.repository import Pango
        self.items={};self.active_id=None
        self.get_style_context().add_class('compact-picker')
        content=Gtk.Box(spacing=8)
        self.value_label=Gtk.Label(xalign=0)
        self.value_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.value_label.set_width_chars(1)
        content.pack_start(self.value_label,True,True,0)
        content.pack_end(Gtk.Image.new_from_icon_name('pan-down-symbolic',Gtk.IconSize.MENU),False,False,0)
        self.add(content)
        self.popup=Gtk.Popover.new(self)
        self.popup.get_style_context().add_class('selection-popover')
        self.popup.set_position(Gtk.PositionType.RIGHT)
        self.scroller=Gtk.ScrolledWindow()
        self.scroller.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC)
        self.scroller.set_overlay_scrolling(False)
        self.scroller.set_min_content_width(254)
        self.scroller.set_max_content_height(288)
        self.scroller.set_propagate_natural_height(True)
        self.options=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=3,margin=6)
        self.scroller.add(self.options);self.popup.add(self.scroller)
        self.scroller.set_size_request(254,-1)
        self.scroller.show_all()
        self.set_popover(self.popup)
    def get_cells(self):return []
    def append(self,ident,title):
        button=Gtk.Button();button.set_relief(Gtk.ReliefStyle.NONE)
        box=Gtk.Box(spacing=10)
        label=Gtk.Label(label=title,xalign=0)
        label.set_line_wrap(True);label.set_max_width_chars(29)
        check=Gtk.Label(label='✓' if ident==self.active_id else '')
        check.set_size_request(18,-1)
        box.pack_start(label,True,True,0);box.pack_end(check,False,False,0)
        button.add(box);button.connect('clicked',lambda *_:self.choose(ident))
        self.items[ident]=(title,button,check)
        self.options.pack_start(button,False,False,0);button.show_all()
    def remove_all(self):
        for child in self.options.get_children():child.destroy()
        self.items={};self.active_id=None;self.value_label.set_text('')
    def set_active_id(self,ident):
        if ident not in self.items:return False
        changed=self.active_id!=ident;self.active_id=ident
        self.value_label.set_text(self.items[ident][0])
        self.set_tooltip_text(self.items[ident][0])
        for key,(_,button,check) in self.items.items():
            check.set_text('✓' if key==ident else '')
            ctx=button.get_style_context()
            if key==ident:ctx.add_class('selected-option')
            else:ctx.remove_class('selected-option')
        if changed:self.emit('changed')
        return True
    def get_active_id(self):return self.active_id
    def choose(self,ident):
        self.set_active_id(ident);self.popup.popdown();self.set_active(False)
