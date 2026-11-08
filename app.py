#!/usr/bin/env python3
"""Standalone Codex client with offline dictation for Steam Deck."""
import json
import base64
import math
from array import array
import os
import re
from pathlib import Path
import signal
import shlex
import subprocess
import shutil
from decky.runtime_paths import resolve_state_dir
import threading
import time
import uuid
from datetime import datetime
# Use GTK’s local input context: Steam’s IM module opens its own keyboard
# on editor focus, while this standalone app already provides AppKeyboard.
os.environ["GTK_IM_MODULE"] = "gtk-im-context-simple"
# Apply the saved interface preference before GTK loads its native dialogs.
try:_interface_language=(resolve_state_dir()/'language').read_text().strip()
except OSError:_interface_language='en'
if _interface_language in ('en','ru'):os.environ['LANGUAGE']=_interface_language
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Gio, Pango, GdkPixbuf
from backend import Backend, RpcError, CODEX
import providers
import updates
from chat_media import attachments,display_text
from message_blocks import split_message
from ui_extras import UILabel, translator, AppKeyboard, CompactPicker

ROOT = Path(__file__).resolve().parent
STATE_DIR = resolve_state_dir()
THEME_TITLES = {'light':'Светлая','dark':'Тёмная','graphite':'Графит','violet':'Фиалка','forest':'Лес','amber':'Янтарь','rose':'Роза'}
DRAFT = STATE_DIR/'draft.txt'
THREAD = DRAFT.parent/'thread-id'
THEME = DRAFT.parent/'theme'

def command(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT, timeout=4).strip()

def clean_text(text):
    return ''.join(ch for ch in text if ch.isprintable() or ch in '\n\t').strip()

class Panel(Gtk.Application):
    def __init__(self):
        self.gaming_mode=os.environ.get('DECK_AI_GAMING')=='1'
        super().__init__(application_id='local.deck.DeckAIGaming' if self.gaming_mode else 'local.deck.DeckAI', flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.recording = False
        self.busy = False
        self.stop_event = threading.Event()
        self.recorder = None
        self.model = None
        self.voice_models = {}
        self.keyboard_top = -1
        self.target = None
        self.audio_level = 0.0
        try:self.remote_host=(DRAFT.parent/'remote-host').read_text().strip()
        except OSError:self.remote_host=''
        self.thread_id = self.thread_file().read_text().strip() if self.thread_file().exists() else None
        if self.thread_id:
            try:uuid.UUID(self.thread_id)
            except ValueError:self.thread_id=None
        self.sending = False
        self.backend = None
        self.connecting = False
        self.recovery_terminal_opened = False
        self.history_ready = False
        self.pending_events = []
        self.remote_polling=False
        self.remote_history_digest=''
        self.messages = {}
        self.pending_messages = {}
        self.engine_active = False
        self.turn_id = None
        try:self.empty_threads=json.loads((DRAFT.parent/'empty-chats.json').read_text())
        except (OSError,ValueError):self.empty_threads={}
        self.thread_cache=dict(self.empty_threads)
        # Keep recently viewed histories in memory so device/chat switching
        # can paint immediately while the live app-server refresh runs.
        self.history_cache={}
        self.device_thread_caches={'':dict(self.thread_cache)}
        self.codex_thread_cache=dict(self.thread_cache)
        self.loading_thread_id=None
        self.thread_cursor=None
        self.loading_threads=False
        self.model_by_thread={}
        try:self.model_by_thread=json.loads((DRAFT.parent/'model-preferences.json').read_text())
        except (OSError,ValueError):pass
        self.available_models=[]
        self.provider='codex'
        self.external_threads={'claude':{},'deepseek':{},'tokenharbor':{}}
        self.external_thread_ids={'claude':'','deepseek':'','tokenharbor':''}
        self.external_models={'claude':[{'id':'sonnet','name':'Claude Sonnet · актуальная версия'}, {'id':'opus','name':'Claude Opus · актуальная версия'}, {'id':'haiku','name':'Claude Haiku · актуальная версия'}], 'deepseek':[],'tokenharbor':providers.tokenharbor_models()}
        try:
            provider_state=json.loads((DRAFT.parent/'provider-chats.json').read_text())
            for key in self.external_threads:
                self.external_threads[key]=provider_state.get('chats',{}).get(key,{})
                self.external_thread_ids[key]=provider_state.get('selected',{}).get(key,'')
        except (OSError,ValueError,TypeError):pass
        self.custom_providers=providers.load_custom(STATE_DIR)
        try:saved_chats=json.loads((DRAFT.parent/'provider-chats.json').read_text())
        except (OSError,ValueError,TypeError):saved_chats={}
        for entry in self.custom_providers:
            self.external_threads[entry['id']]=saved_chats.get('chats',{}).get(entry['id'],{})
            self.external_thread_ids[entry['id']]=saved_chats.get('selected',{}).get(entry['id'],'')
            self.external_models[entry['id']]=[]
        self.codex_thread_id=self.thread_id
        self.current_model=None
        self.current_effort=None
        self.current_tier=None
        try:self.runtime_preferences=json.loads((DRAFT.parent/'runtime-preferences.json').read_text())
        except (OSError,ValueError):self.runtime_preferences={}
        try:self.outbox=json.loads((DRAFT.parent/'outbox.json').read_text())
        except (OSError,ValueError):self.outbox=[]
        for job in self.outbox:
            if job.get('status')=='editing':job['status']='queued'
            if job.get('status')=='sending':job['status']='error';job['error']='Отправка была прервана. Проверьте историю и нажмите «Повторить», если сообщение не отправилось.'
        self.thread_activity={}
        self.outbox_view_signature=None
        self.voice_refinement=self.runtime_preferences.get('voiceRefinement',False)
        self.auto_approve=bool(self.runtime_preferences.get('autoApprove',False))
        self.speech_player=None
        self.speech_cancel=None
        self.language_settings=None
        self.outbox_loading=False
        self._updating_model=False
        self.follow_tail=True
        self._scroll_dragging=False
        self._tail_idle_pending=False
        self._programmatic_scroll=False
        self.dirty_messages=set()
        self.theme = THEME.read_text().strip() if THEME.exists() else 'dark'
        if self.theme not in THEME_TITLES:self.theme='dark'
        for name, callback in [('show',lambda *_:self.activate()),('hide',lambda *_:self.close()),('keyboard',lambda *_:self.keyboard()),('quit',lambda *_:self.shutdown_app())]:
            action=Gio.SimpleAction.new(name,None)
            action.connect('activate',callback)
            self.add_action(action)
        self.update_controller=None;self.update_lease=updates.Lease(STATE_DIR)
        try:self.update_controller=updates.Controller()
        except Exception:pass
        action=Gio.SimpleAction.new('updates',None);action.connect('activate',self.show_updates);self.add_action(action)
        action=Gio.SimpleAction.new('select-chat',GLib.VariantType.new('s'))
        action.connect('activate',lambda _,value:self.switch_thread(value.get_string()))
        self.add_action(action)
        action=Gio.SimpleAction.new('new-chat',None)
        action.connect('activate',self.new_chat);self.add_action(action)
        for name,theme in [('theme-light','light'),('theme-dark','dark')]:
            action=Gio.SimpleAction.new(name,None)
            action.connect('activate',lambda *_,value=theme:self.apply_theme(value))
            self.add_action(action)

    def do_activate(self):
        if hasattr(self, 'window'):
            self.window.present()
            if not self.backend or not self.backend.connected:self.reconnect()
            return
        if not self.gaming_mode:self.hold()
        Gtk.Window.set_default_icon_from_file(str(ROOT/'deck-ai.png'))
        self.window = Gtk.ApplicationWindow(application=self, title='Deck AI')
        self.window.set_wmclass('deckai', 'DeckAI')
        self.window.set_decorated(False)
        self.window.connect('delete-event', self.close)
        self.window.connect('key-press-event',self.application_key_pressed)
        self.window.set_name('voice-panel')
        self.window.set_icon_from_file(str(ROOT/'deck-ai.png'))
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=9)
        box.set_margin_start(20); box.set_margin_end(20)
        box.set_margin_top(13); box.set_margin_bottom(11)
        self.window.add(box)
        header = Gtk.Box(spacing=11)
        header.get_style_context().add_class('titlebar')
        box.pack_start(header, False, False, 0)
        logo_frame=Gtk.Frame()
        logo_frame.set_shadow_type(Gtk.ShadowType.NONE)
        logo_frame.set_valign(Gtk.Align.CENTER)
        logo_frame.get_style_context().add_class('logo-emblem')
        logo=Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_scale(str(ROOT/'deck-ai.png'),29,29,True))
        logo_frame.add(logo)
        header.pack_start(logo_frame,False,False,0)
        brand = Gtk.Label()
        brand.set_markup('<span weight="bold" size="15000">Deck AI</span>')
        header.pack_start(brand, False, False, 0)
        subtitle = UILabel(label='ИИ-помощник')
        subtitle.get_style_context().add_class('subtitle')
        header.pack_start(subtitle, False, False, 7)
        header.pack_start(Gtk.Box(),True,True,0)
        self.device_strip=Gtk.Box(spacing=3)
        self.device_strip.get_style_context().add_class('device-strip')
        header.pack_start(self.device_strip,False,False,0)
        self.add_device_button=self.button('list-add-symbolic',None,self.show_connect_menu,'icon-only')
        self.add_device_button.set_tooltip_text('Подключить ИИ-провайдера или устройство')
        header.pack_start(self.add_device_button,False,False,0)
        self.refresh_devices_button=self.button('view-refresh-symbolic',None,self.refresh_device_list,'icon-only')
        self.refresh_devices_button.set_tooltip_text('Обновить список устройств из SSH-конфигурации')
        header.pack_start(self.refresh_devices_button,False,False,0)
        self.refresh_device_list()
        self.status_dot = UILabel(label='●')
        self.status_dot.get_style_context().add_class('status-dot')
        header.pack_start(self.status_dot, False, False, 1)
        self.status = UILabel(label='Готов к работе')
        self.status.set_xalign(0); self.status.set_ellipsize(Pango.EllipsizeMode.END)
        self.status.get_style_context().add_class('status-text')
        header.pack_start(self.status, True, True, 0)
        theme_switch=Gtk.Box(spacing=0)
        theme_switch.get_style_context().add_class('theme-switch')
        self.theme_buttons={}
        for value,label,icon in [('light','Светлая','display-brightness-symbolic'),('dark','Тёмная','weather-clear-night-symbolic')]:
            button=Gtk.ToggleButton()
            inner=Gtk.Box(spacing=0,halign=Gtk.Align.CENTER)
            image=Gtk.Image.new_from_icon_name(icon,Gtk.IconSize.MENU)
            image.set_pixel_size(14)
            inner.pack_start(image,False,False,0)
            button.add(inner);button.get_style_context().add_class('theme-choice')
            button.set_focus_on_click(False)
            button.set_tooltip_text(label)
            button.connect('clicked',lambda _,v=value:self.apply_theme(v))
            theme_switch.pack_start(button,False,False,0)
            self.theme_buttons[value]=button
        header.pack_start(theme_switch,False,False,6)
        self.keyboard_button = self.button('input-keyboard-symbolic', 'Клавиатура', self.keyboard, 'quiet')
        header.pack_start(self.keyboard_button, False, False, 0)
        menu_button=Gtk.MenuButton()
        menu_button.add(Gtk.Image.new_from_icon_name('open-menu-symbolic',Gtk.IconSize.MENU))
        menu_button.get_style_context().add_class('icon-only')
        menu=Gtk.Menu()
        self.app_menu=menu
        self.account_item=Gtk.MenuItem(label=translator.text('Аккаунт: проверка…'))
        account_menu=Gtk.Menu();self.account_status_item=Gtk.MenuItem(label=translator.text('Аккаунт: проверка…'));self.account_status_item.set_sensitive(False);account_menu.append(self.account_status_item)
        self.account_login_item=Gtk.MenuItem(label=translator.text('Войти или сменить аккаунт'));self.account_login_item.connect('activate',self.begin_account_login);account_menu.append(self.account_login_item)
        self.account_logout_item=Gtk.MenuItem(label=translator.text('Выйти из аккаунта'));self.account_logout_item.connect('activate',self.confirm_account_logout);account_menu.append(self.account_logout_item)
        self.account_item.set_submenu(account_menu);menu.append(self.account_item);menu.append(Gtk.SeparatorMenuItem())
        theme_item=Gtk.MenuItem(label=translator.text('Цветовая тема'));theme_item.translation_source='Цветовая тема'
        theme_menu=Gtk.Menu()
        for key,title in THEME_TITLES.items():
            entry=Gtk.MenuItem(label=translator.text(title));entry.connect('activate',lambda _,value=key:self.apply_theme(value));theme_menu.append(entry)
        theme_item.set_submenu(theme_menu);menu.append(theme_item)
        self.voice_refinement_item=Gtk.CheckMenuItem(label='Точное распознавание речи (медленнее)')
        self.voice_refinement_item.set_active(self.voice_refinement)
        self.voice_refinement_item.connect('toggled',self.toggle_voice_refinement)
        menu.append(self.voice_refinement_item)
        self.auto_approve_item=Gtk.CheckMenuItem(label='Автоодобрять разрешения')
        self.auto_approve_item.set_tooltip_text('Автоматически разрешать команды, изменения файлов и запрошенный доступ. Вопросы с вводом ответа остаются ручными.')
        self.auto_approve_item.set_active(self.auto_approve)
        self.auto_approve_item.connect('toggled',self.toggle_auto_approve)
        menu.append(self.auto_approve_item)
        update_item=Gtk.MenuItem(label=translator.text('Обновления Deck AI'));update_item.connect('activate',self.show_updates);menu.append(update_item)
        item=Gtk.MenuItem(label=translator.text('Язык и голос'))
        item.translation_source='Язык и голос'
        item.connect('activate',self.show_language_settings)
        menu.append(item)
        for label,callback in [('Скрыть окно',self.close),('Свернуть',lambda *_:self.window.iconify())]:
            item=Gtk.MenuItem(label=label);item.translation_source=label;item.connect('activate',callback);menu.append(item)
        exit_item=Gtk.MenuItem(label='Завершить приложение')
        exit_item.translation_source='Завершить приложение'
        exit_item.connect('activate',lambda *_:self.shutdown_app())
        menu.append(exit_item);menu.show_all();menu_button.set_popup(menu)
        header.pack_start(menu_button,False,False,0)

        body=Gtk.Box(spacing=16)
        box.pack_start(body,True,True,0)
        sidebar=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
        sidebar.set_size_request(224,-1)
        sidebar.get_style_context().add_class('sidebar')
        sidebar_scroll=Gtk.ScrolledWindow()
        sidebar_scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC)
        sidebar_scroll.set_size_request(240,-1)
        sidebar_scroll.add(sidebar)
        body.pack_start(sidebar_scroll,False,False,0)
        provider_label=UILabel(label='Выбрать ИИ-провайдера',xalign=0);provider_label.get_style_context().add_class('sidebar-caption')
        sidebar.pack_start(provider_label,False,False,0)
        self.provider_picker=CompactPicker()
        self.provider_titles=[('codex','Codex · ChatGPT'),('claude','Claude Code · свой доступ'),('deepseek','DeepSeek · OpenRouter'),('tokenharbor','DeepSeek · TokenHarbor')]+[(entry['id'],entry['name']) for entry in self.custom_providers]
        for ident,title in self.provider_titles:self.provider_picker.append(ident,translator.text(title))
        self.provider_picker.set_active_id('codex')
        self.provider_picker.connect('changed',self.provider_changed)
        sidebar.pack_start(self.provider_picker,False,False,0)
        self.provider_controls=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=4)
        sidebar.pack_start(self.provider_controls,False,False,0)
        self.new_chat_button=self.button('list-add-symbolic','Новый чат',self.new_chat,'new-chat')
        sidebar.pack_start(self.new_chat_button,False,False,0)
        self.chat_search=Gtk.SearchEntry()
        self.chat_search.set_placeholder_text('Найти чат')
        self.chat_search.connect('search-changed',lambda *_:self.render_thread_list())
        sidebar.pack_start(self.chat_search,False,False,0)
        saved_label=UILabel(label='Чаты',xalign=0)
        saved_label.get_style_context().add_class('sidebar-caption')
        sidebar.pack_start(saved_label,False,False,0)
        list_scroll=Gtk.ScrolledWindow()
        self.thread_scroll=list_scroll
        list_scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC)
        list_scroll.set_overlay_scrolling(False)
        self.thread_list=Gtk.ListBox()
        self.thread_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.thread_list.connect('row-activated',lambda _,row:self.switch_thread(row.thread_id))
        list_scroll.add(self.thread_list);sidebar.pack_start(list_scroll,True,True,0)
        self.more_chats_button=self.button('view-more-symbolic','Ещё чаты',lambda *_:self.refresh_threads(True),'quiet')
        self.more_chats_button.set_no_show_all(True)
        sidebar.pack_start(self.more_chats_button,False,False,0)
        model_heading=Gtk.Box(spacing=3)
        model_label=UILabel(label='Модель и режим',xalign=0)
        model_label.set_ellipsize(Pango.EllipsizeMode.END);model_label.set_width_chars(1);model_label.set_max_width_chars(23)
        model_label.get_style_context().add_class('sidebar-caption')
        model_heading.pack_start(model_label,True,True,0)
        refresh_models=self.button('view-refresh-symbolic',None,lambda *_:self.load_models(),'icon-only')
        refresh_models.set_tooltip_text('Обновить полный список моделей')
        model_heading.pack_start(refresh_models,False,False,0)
        sidebar.pack_start(model_heading,False,False,0)
        self.model_menu_button=Gtk.MenuButton()
        self.model_menu_button.get_style_context().add_class('compact-picker')
        self.model_menu_button.get_style_context().add_class('model-settings-button')
        self.model_menu_label=Gtk.Label(xalign=0)
        self.model_menu_label.set_ellipsize(Pango.EllipsizeMode.END)
        menu_content=Gtk.Box(spacing=8)
        menu_content.pack_start(self.model_menu_label,True,True,0)
        menu_content.pack_end(Gtk.Image.new_from_icon_name('pan-down-symbolic',Gtk.IconSize.MENU),False,False,0)
        self.model_menu_button.add(menu_content)
        self.model_menu_popover=Gtk.Popover.new(self.model_menu_button)
        self.model_menu_popover.get_style_context().add_class('model-settings-popover')
        self.model_menu_popover.set_position(Gtk.PositionType.BOTTOM)
        self.model_menu_popover.set_size_request(270,-1)
        model_settings=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=7,margin=10)
        self.model_picker=CompactPicker()
        for renderer in self.model_picker.get_cells():
            if isinstance(renderer,Gtk.CellRendererText):renderer.set_property('ellipsize',Pango.EllipsizeMode.END);renderer.set_property('width-chars',21)
        self.model_picker.connect('changed',self.model_changed)
        model_caption=UILabel(label='Модель',xalign=0);model_caption.get_style_context().add_class('sidebar-caption')
        model_settings.pack_start(model_caption,False,False,0)
        model_settings.pack_start(self.model_picker,False,False,0)
        for title,attribute in [('Глубина обработки','effort_picker'),('Скорость','speed_picker')]:
            label=UILabel(label=title,xalign=0);label.get_style_context().add_class('sidebar-caption')
            model_settings.pack_start(label,False,False,0)
            picker=CompactPicker();picker.connect('changed',self.runtime_changed)
            for renderer in picker.get_cells():
                if isinstance(renderer,Gtk.CellRendererText):renderer.set_property('ellipsize',Pango.EllipsizeMode.END);renderer.set_property('width-chars',21)
            setattr(self,attribute,picker);model_settings.pack_start(picker,False,False,0)
        self.provider_action_button=self.button('preferences-system-symbolic',translator.text('Настроить DeepSeek / OpenRouter'),self.configure_openrouter,'quiet')
        self.provider_action_button.set_no_show_all(True)
        self.provider_controls.pack_start(self.provider_action_button,False,False,0)
        self.tokenharbor_action_button=self.button('preferences-system-symbolic',translator.text('Настроить TokenHarbor'),self.configure_tokenharbor,'quiet')
        self.tokenharbor_action_button.set_no_show_all(True)
        self.provider_controls.pack_start(self.tokenharbor_action_button,False,False,0)
        self.claude_action_button=self.button('system-users-symbolic',translator.text('Настроить Claude Code'),self.launch_claude_login,'quiet')
        self.claude_action_button.set_no_show_all(True)
        self.provider_controls.pack_start(self.claude_action_button,False,False,0)
        self.model_menu_popover.add(model_settings)
        self.model_menu_button.set_popover(self.model_menu_popover)
        # Popover children are not reliably made visible by the parent window's
        # show_all() in GTK; explicitly realize the settings controls here.
        model_settings.show_all()
        self.model_menu_popover.set_no_show_all(True)
        self.model_menu_popover.hide()
        sidebar.pack_start(self.model_menu_button,False,False,0)
        self.speed_picker.set_tooltip_text('Fast — приоритетная обработка, которая может расходовать больше лимита.')
        self.sidebar=sidebar
        content=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=9)
        content.set_hexpand(True);body.pack_start(content,True,True,0)
        self.chat_title=UILabel(label='Текущий разговор',xalign=0)
        self.chat_title.set_ellipsize(Pango.EllipsizeMode.END)
        self.chat_title.get_style_context().add_class('chat-title')
        content.pack_start(self.chat_title,False,False,0)
        self.chat_scroll = Gtk.ScrolledWindow()
        self.chat_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.chat_scroll.set_overlay_scrolling(False)
        self.chat_scroll.set_kinetic_scrolling(True)  # finger drag scrolls the messages
        self.chat = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.chat.set_margin_top(12); self.chat.set_margin_bottom(12)
        self.chat.set_margin_start(10); self.chat.set_margin_end(14)
        self.chat_scroll.add(self.chat)
        content.pack_start(self.chat_scroll, True, True, 0)
        self.chat_scroll.get_vadjustment().connect('changed', self.scroll_changed)
        self.chat_scroll.get_vadjustment().connect('value-changed',self.scroll_value_changed)
        self.chat_scroll.connect('scroll-event',self.manual_scroll)
        # GTK owns pointer grabs and releases, including focus loss and hide.
        # A manual Gdk.Device grab could keep all clicks on the scrollbar.
        scrollbar=self.chat_scroll.get_vscrollbar()
        scrollbar.connect('button-press-event',self.manual_scroll)
        self.outbox_expander=Gtk.Expander(label=translator.text('Очередь')+' · 0')
        self.outbox_list=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=5)
        queue_scroll=Gtk.ScrolledWindow()
        queue_scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC)
        queue_scroll.set_min_content_height(70);queue_scroll.set_max_content_height(190)
        queue_scroll.set_propagate_natural_height(True)
        queue_scroll.add(self.outbox_list)
        self.outbox_expander.add(queue_scroll)
        content.pack_start(self.outbox_expander,False,False,0)
        activity = Gtk.Box(spacing=8)
        self.spinner = Gtk.Spinner()
        activity.pack_start(self.spinner, False, False, 0)
        self.activity = UILabel(label='Подключаюсь к вашему диалогу…')
        self.activity.set_xalign(0); self.activity.set_ellipsize(Pango.EllipsizeMode.END)
        self.activity.get_style_context().add_class('activity')
        activity.pack_start(self.activity, True, True, 0)
        self.stop_button = self.button('media-playback-stop-symbolic', 'Остановить', self.interrupt, 'quiet')
        self.stop_button.set_sensitive(False)
        activity.pack_start(self.stop_button, False, False, 0)
        self.reconnect_button = self.button('view-refresh-symbolic', 'Подключиться', self.reconnect, 'quiet')
        activity.pack_start(self.reconnect_button, False, False, 0)
        self.terminal_button = self.button('utilities-terminal-symbolic', 'Терминал', self.open_terminal, 'quiet')
        self.terminal_button.set_tooltip_text('Открыть командную строку без повторного входа в Codex')
        activity.pack_start(self.terminal_button, False, False, 0)
        self.recovery_button = self.button('utilities-terminal-symbolic', 'Войти через терминал', self.launch_codex_login, 'quiet')
        activity.pack_start(self.recovery_button, False, False, 0)
        self.read_answer_button=self.button('audio-volume-high-symbolic',None,self.read_latest_answer,'icon-only')
        self.read_answer_button.set_tooltip_text('Озвучить последний ответ / остановить озвучку')
        activity.pack_start(self.read_answer_button,False,False,0)
        content.pack_start(activity, False, False, 0)

        composer = Gtk.Box(spacing=10); content.pack_start(composer, False, False, 0)
        editor = Gtk.Overlay()
        editor_frame = Gtk.Frame()
        editor_frame.set_shadow_type(Gtk.ShadowType.NONE)
        editor_frame.get_style_context().add_class('editor')
        editor_frame.add(editor)
        scroll = Gtk.ScrolledWindow(); scroll.set_size_request(180, 65)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.text = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD_CHAR)
        self.text.set_property("im-module", "gtk-im-context-simple")
        self.text.set_left_margin(17); self.text.set_right_margin(12)
        self.text.set_top_margin(12); self.text.set_bottom_margin(8)
        scroll.add(self.text); editor.add(scroll)
        self.placeholder = UILabel(label='Что сделаем сегодня? Напишите или продиктуйте…')
        self.placeholder.set_xalign(0); self.placeholder.set_valign(Gtk.Align.START)
        self.placeholder.set_margin_start(18); self.placeholder.set_margin_top(14)
        self.placeholder.set_ellipsize(Pango.EllipsizeMode.END)
        self.placeholder.get_style_context().add_class('placeholder')
        editor.add_overlay(self.placeholder); editor.set_overlay_pass_through(self.placeholder, True)
        self.placeholder.set_no_show_all(True)
        if DRAFT.is_file():
            self.text.get_buffer().set_text(DRAFT.read_text())
        self.text.get_buffer().connect('changed', self.save_draft)
        self.text.get_buffer().connect('changed', self.draft_changed)
        composer.pack_start(editor_frame, True, True, 0)
        self.mic = Gtk.Button()
        self.mic.get_style_context().add_class('microphone')
        mic_box = Gtk.Box(spacing=10, halign=Gtk.Align.CENTER)
        self.wave = Gtk.DrawingArea(); self.wave.set_size_request(23, 26)
        self.wave.connect('draw', self.draw_wave)
        mic_box.pack_start(self.wave, False, False, 0)
        self.mic_text = UILabel(label='Говорить')
        mic_box.pack_start(self.mic_text, False, False, 0)
        self.mic.add(mic_box); self.mic.set_size_request(166, 65)
        self.mic.connect('clicked', self.toggle_record)
        self.mic.set_tooltip_text('Нажмите, произнесите фразу, затем нажмите ещё раз')
        composer.pack_start(self.mic, False, False, 0)
        self.send_button = self.button('go-up-symbolic', 'Отправить', self.send, 'primary')
        self.send_button.set_size_request(163, 65)
        composer.pack_start(self.send_button, False, False, 0)

        footer = Gtk.Box(spacing=7); content.pack_start(footer, False, False, 0)
        footer.get_style_context().add_class('footer')
        footer.pack_start(Gtk.Image.new_from_icon_name('channel-secure-symbolic', Gtk.IconSize.MENU), False, False, 0)
        footer.pack_start(UILabel(label='Распознавание на устройстве'), False, False, 0)
        voice_setting=STATE_DIR/'voice-language'
        self.voice_language=voice_setting.read_text().strip() if voice_setting.exists() else translator.language
        language = Gtk.Button(label='🎙 '+self.voice_language.upper())
        language.get_style_context().add_class('clear')
        language.connect('clicked',lambda b:self.switch_voice_language(b))
        self.voice_language_button=language
        footer.pack_start(language, False, False, 5)
        self.fast_voice=Gtk.CheckButton(label='Быстрая пунктуация')
        self.fast_voice.set_active(not self.voice_refinement)
        self.fast_voice.set_sensitive(self.voice_language in ('ru','en'))
        self.fast_voice.set_tooltip_text('Базовые запятые, заглавные буквы и окончания предложений без повторного распознавания. Для русского и английского; другим языкам нужна многоязычная модель.')
        self.fast_voice.connect('toggled',lambda button:self.set_voice_refinement(not button.get_active()))
        footer.pack_start(self.fast_voice,False,False,0)
        hint = UILabel(label='Проверьте текст перед отправкой'); hint.set_xalign(1)
        footer.pack_start(hint, True, True, 0)
        clear = self.button('edit-clear-symbolic', 'Очистить', self.clear, 'clear')
        footer.pack_start(clear, False, False, 4)
        self.app_keyboard=AppKeyboard(self.text,self.keyboard,ROOT)
        box.pack_start(self.app_keyboard,False,False,0)
        self.app_keyboard.set_no_show_all(True)
        self.css = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.apply_theme(self.theme)
        settings=Gtk.Settings.get_default()
        settings.set_property('gtk-enable-animations',False)
        settings.set_property('gtk-primary-button-warps-slider',True)
        self.window.show_all()
        self.refresh_outbox_view()
        self.draft_changed(self.text.get_buffer())
        self.position()
        GLib.timeout_add(80, self.animate)
        GLib.timeout_add(50,self.flush_message_updates)
        GLib.timeout_add_seconds(30,self.refresh_threads)
        GLib.timeout_add_seconds(3,self.poll_remote_history)
        GLib.timeout_add(1000,self.pump_outbox)
        GLib.timeout_add(1000,self.poll_updates)
        try:
            from decky import library_art
            library_art.start_setup_worker(Path(__file__).resolve().parent/'decky',Path.home(),STATE_DIR)
        except Exception:pass
        if self.update_controller:self.update_controller.start()
        Gdk.Screen.get_default().connect('monitors-changed', lambda *_: self.position())
        self.window.connect('destroy', lambda *_: self.shutdown_app() if self.gaming_mode else self.stop_event.set())
        self.closed = threading.Event()
        self.change_language(translator.language)
        self.reconnect()

    def application_key_pressed(self,widget,event):
        control=bool(event.state & Gdk.ModifierType.CONTROL_MASK)
        key=Gdk.keyval_name(event.keyval)
        shift=bool(event.state & Gdk.ModifierType.SHIFT_MASK)
        if key in ('Return','KP_Enter') and (control or (not shift and self.window.get_focus() is self.text)):
            # Enter sends from the message field; Shift+Enter inserts a new line.
            self.send()
            return True
        if control and key in ('l','L'):
            self.text.grab_focus()
            return True
        if control and key in ('n','N'):
            self.new_chat()
            return True
        return False

    def toggle_maximize(self,*_):
        if self.gaming_mode:return
        if self.window.is_maximized():self.window.unmaximize()
        else:self.window.maximize()

    def apply_theme(self, theme):
        if getattr(self,'_applying_theme',False):return
        if theme not in THEME_TITLES:return
        self.theme=theme
        if not hasattr(self,'css'):return
        self._applying_theme=True
        palette=json.loads((ROOT/'themes.json').read_text())[theme]
        colors='\n'.join('@define-color '+key+' '+value+';' for key,value in palette.items())
        self.css.load_from_data((colors+'\n'+(ROOT/'style.css').read_text()).encode())
        Gtk.Settings.get_default().set_property('gtk-application-prefer-dark-theme',theme!='light')
        for value,button in self.theme_buttons.items():button.set_active(value==theme)
        if hasattr(self,'wave'):self.wave.queue_draw()
        THEME.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        THEME.write_text(theme)
        self._applying_theme=False

    def scroll_changed(self, adjustment):
        if self.follow_tail and not self._scroll_dragging and not self._tail_idle_pending:
            self._tail_idle_pending=True
            GLib.idle_add(self.scroll_to_end)

    def scroll_to_end(self):
        self._tail_idle_pending=False
        if not self.follow_tail or self._scroll_dragging or not self.chat_scroll.get_realized():return
        adjustment=self.chat_scroll.get_vadjustment()
        self._programmatic_scroll=True
        adjustment.set_value(max(0,adjustment.get_upper()-adjustment.get_page_size()))
        self._programmatic_scroll=False

    def scroll_value_changed(self, adjustment):
        if self._programmatic_scroll or (self._tail_idle_pending and self.follow_tail):return
        if not self._scroll_dragging:
            self.follow_tail=adjustment.get_upper()-adjustment.get_page_size()-adjustment.get_value()<24

    def manual_scroll(self,*_):
        self.follow_tail=False
        return False

    def flush_message_updates(self):
        for ident in list(self.dirty_messages):
            message=self.messages.get(ident)
            if message:self.render_message_body(message)
        self.dirty_messages.clear()
        return True

    def reconnect(self, *_):
        if self.connecting or (self.backend and self.backend.connected): return
        self.connecting = True
        self.history_ready = False
        self.pending_events = []
        self.reconnect_button.set_sensitive(False)
        self.message('Подключаюсь…')
        self.activity.set_text('Загружаю историю разговора…')
        threading.Thread(target=self.connect_backend,daemon=True).start()

    def thread_file(self):
        return DRAFT.parent/('thread-id-remote-'+self.remote_host if getattr(self,'remote_host','') else 'thread-id')

    def ssh_hosts(self):
        hosts=[]
        ssh=Path.home()/'.ssh'
        files=[ssh/'config',*sorted((ssh/'config.d').glob('*.conf'))]
        for path in files:
            try:lines=path.read_text(errors='ignore').splitlines()
            except OSError:continue
            for line in lines:
                try:parts=shlex.split(line,comments=True)
                except ValueError:continue
                if len(parts)<2 or parts[0].lower()!='host':continue
                for alias in parts[1:]:
                    if alias.startswith('!') or any(ch in alias for ch in '*?[') or alias.lower()=='all':continue
                    if alias not in hosts:hosts.append(alias)
        return hosts

    def refresh_device_list(self,*_):
        if not hasattr(self,'device_strip'):return
        hosts=self.ssh_hosts()
        if self.remote_host and self.remote_host not in hosts:hosts.insert(0,self.remote_host)
        self._refreshing_devices=True
        for child in self.device_strip.get_children():child.destroy()
        options=[('', 'Deck', 'Steam Deck · локальные чаты')]+[(host,host,host+' · удалённый Codex') for host in hosts]
        for host,label,tooltip in options:
            button=Gtk.ToggleButton(label=label);button.set_active(host==self.remote_host)
            button.set_tooltip_text(tooltip);button.set_focus_on_click(False)
            button.get_style_context().add_class('device-choice')
            button.connect('clicked',lambda widget,target=host:self.device_button_clicked(widget,target))
            self.device_strip.pack_start(button,False,False,0);button.show_all()
        self._refreshing_devices=False

    def device_button_clicked(self,button,host):
        if not button.get_active():button.set_active(True);return
        if not getattr(self,'_refreshing_devices',False):self.select_device(host)

    def prompt_remote_host(self,*_):
        dialog=Gtk.Dialog(title='Подключить удалённый Codex',transient_for=self.window,flags=Gtk.DialogFlags.MODAL)
        translator.watch_dialog(dialog)
        dialog.add_buttons('Отмена',Gtk.ResponseType.CANCEL,'Подключить',Gtk.ResponseType.OK)
        box=dialog.get_content_area();box.set_spacing(8);box.set_margin_start(16);box.set_margin_end(16);box.set_margin_top(12);box.set_margin_bottom(12)
        box.pack_start(Gtk.Label(label='Добавьте устройство или выберите готовый SSH-алиас.',xalign=0),False,False,0)
        grid=Gtk.Grid(column_spacing=10,row_spacing=7)
        entries={}
        for row,(key,title,placeholder) in enumerate([
            ('alias','Имя в Codex','например, macbook'),('hostname','Адрес компьютера','IP или имя в сети'),
            ('user','Пользователь SSH','учётная запись Mac/Windows'),('identity','Путь к SSH-ключу','~/.ssh/id_ed25519')]):
            grid.attach(Gtk.Label(label=title,xalign=0),0,row,1,1)
            entry=Gtk.Entry();entry.set_placeholder_text(placeholder)
            if key=='alias':entry.set_text(self.remote_host)
            if key=='identity':entry.set_text('~/.ssh/id_ed25519')
            grid.attach(entry,1,row,1,1);entries[key]=entry
        box.pack_start(grid,False,False,0)
        box.pack_start(Gtk.Label(label='Для нового подключения укажите адрес и пользователя. На втором компьютере включите SSH и разрешите вход по вашему публичному ключу; Codex CLI должен быть установлен и авторизован.',xalign=0,wrap=True),False,False,0)
        dialog.show_all();response=dialog.run()
        alias=entries['alias'].get_text().strip();hostname=entries['hostname'].get_text().strip();user=entries['user'].get_text().strip();identity=entries['identity'].get_text().strip();dialog.destroy()
        if response!=Gtk.ResponseType.OK:return
        if not re.fullmatch(r'[A-Za-z0-9_.@-]{1,120}',alias):self.message('Укажите короткое имя устройства латиницей.');return
        if hostname:
            if not re.fullmatch(r'[A-Za-z0-9.:_%+-]{1,253}',hostname) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,64}',user):self.message('Проверьте адрес и имя пользователя SSH.');return
            if not identity or any(ch in identity for ch in '\r\n'):self.message('Проверьте путь к SSH-ключу.');return
            ssh=Path.home()/'.ssh';ssh.mkdir(mode=0o700,parents=True,exist_ok=True);config=ssh/'config'
            try:existing=config.read_text() if config.exists() else ''
            except OSError:existing=''
            aliases=set(self.ssh_hosts())
            if alias not in aliases:
                identity=identity.replace('~',str(Path.home()),1)
                with config.open('a') as stream:stream.write(f'\nHost {alias}\n  HostName {hostname}\n  User {user}\n  IdentityFile {shlex.quote(identity)}\n  IdentitiesOnly yes\n')
                config.chmod(0o600)
            self.refresh_device_list()
        self.select_device(alias)

    def select_device(self,host):
        if self.provider!='codex':return
        host=host.strip()
        if host==self.remote_host:return
        if host and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.@-]{0,119}',host):self.message('Введите SSH-алиас без пробелов.');return
        if self.busy or self.sending or self.connecting:self.message('Закончите текущую отправку перед сменой устройства.');return
        self.save_draft(self.text.get_buffer())
        if self.thread_id and self.history_ready:
            cached=self.history_cache.get((self.remote_host,self.thread_id))
            if cached:cached['savedAt']=time.monotonic()
        self.device_thread_caches[self.remote_host]=dict(self.thread_cache)
        previous=self.backend
        if previous:
            try:previous.close()
            except Exception:pass
        self.backend=None;self.remote_host=host;self.loading_thread_id=None
        path=DRAFT.parent/'remote-host';path.parent.mkdir(parents=True,exist_ok=True,mode=0o700);path.write_text(host+'\n');path.chmod(0o600)
        self.thread_id=self.thread_file().read_text().strip() if self.thread_file().exists() else None
        if not host:
            try:self.empty_threads=json.loads((DRAFT.parent/'empty-chats.json').read_text())
            except (OSError,ValueError):self.empty_threads={}
        else:self.empty_threads={}
        self.thread_cache=dict(self.device_thread_caches.get(host, self.empty_threads if not host else {}));self.thread_cursor=None;self.messages={};self.pending_messages={};self.thread_activity={}
        self.refresh_device_list()
        self.history_ready=False;self.connecting=False;self.reconnect()

    def refresh_threads(self, more=False):
        if self.provider!='codex':return True
        if self.loading_threads or not self.backend or not self.backend.connected:return True
        self.loading_threads=True
        def load():
            try:
                params={'limit':50,'sortKey':'updated_at','archived':False}
                if more and self.thread_cursor:params['cursor']=self.thread_cursor
                result=self.backend.request('thread/list',params)
                GLib.idle_add(self.threads_loaded,result)
            except Exception:GLib.idle_add(self.threads_failed)
        threading.Thread(target=load,daemon=True).start()
        return True

    def threads_failed(self):
        self.loading_threads=False

    def threads_loaded(self, result):
        self.loading_threads=False
        cache=self.thread_cache if self.provider=='codex' else self.device_thread_caches.setdefault(self.remote_host,dict(self.codex_thread_cache))
        for thread in result.get('data',[]):cache[thread['id']]=thread
        self.device_thread_caches[self.remote_host]=dict(cache)
        if self.provider=='codex':self.codex_thread_cache=dict(cache)
        self.thread_cursor=result.get('nextCursor')
        self.more_chats_button.get_child().show_all()
        self.more_chats_button.set_visible(bool(self.thread_cursor))
        self.render_thread_list()

    def thread_title(self, thread):
        return (thread.get('name') or thread.get('preview') or translator.text('Новый чат')).split('\n')[0][:120]

    def render_thread_list(self):
        if not hasattr(self,'thread_list'):return
        adjustment=self.thread_scroll.get_vadjustment()
        previous=adjustment.get_value()
        for child in self.thread_list.get_children():child.destroy()
        search=self.chat_search.get_text().casefold().strip()
        source_threads=self.thread_cache if self.provider=='codex' else {ident:{'id':ident,'name':chat.get('name') or translator.text('Новый чат'),'updatedAt':chat.get('updatedAt',0),'createdAt':chat.get('createdAt',0)} for ident,chat in self.external_threads[self.provider].items()}
        threads=sorted(source_threads.values(),key=lambda t:t.get('updatedAt',0),reverse=True)
        for thread in threads:
            title=self.thread_title(thread)
            if search and search not in title.casefold():continue
            row=Gtk.ListBoxRow();row.thread_id=thread['id']
            row.set_tooltip_text(title)
            stack=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6,margin=12)
            label=Gtk.Label(label=title,xalign=0)
            label.set_line_wrap(True);label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
            label.set_lines(2);label.set_ellipsize(Pango.EllipsizeMode.END);label.set_max_width_chars(25);label.set_width_chars(1)
            label.get_style_context().add_class('thread-name')
            stack.pack_start(label,False,False,0)
            stamp=thread.get('updatedAt') or thread.get('createdAt')
            date=datetime.fromtimestamp(stamp).strftime('%d.%m · %H:%M') if stamp else translator.text('Только что')
            date_label=Gtk.Label(label=date,xalign=0)
            date_label.get_style_context().add_class('thread-date')
            stack.pack_start(date_label,False,False,0);row.add(stack)
            self.thread_list.add(row);row.show_all()
            if row.thread_id==self.thread_id:self.thread_list.select_row(row)
        GLib.idle_add(lambda:adjustment.set_value(min(previous,max(0,adjustment.get_upper()-adjustment.get_page_size()))))

    def switch_thread(self, thread_id):
        if thread_id==self.thread_id:return
        if self.busy or self.sending or self.connecting:
            self.message('Закончите ввод или отправку перед сменой чата.');return
        if self.provider in self.external_threads:
            chat=self.external_threads[self.provider].get(thread_id)
            if not chat:return
            self.thread_id=thread_id;self.external_thread_ids[self.provider]=thread_id
            self.save_provider_chats();self.render_external_history(chat);self.render_thread_list();return
        if not self.backend or not self.backend.connected:return
        self.save_draft(self.text.get_buffer())
        self.loading_thread_id=thread_id
        self.begin_thread_switch()
        if thread_id in self.empty_threads:
            thread=self.empty_threads[thread_id]
            self.finish_thread_switch({'model':thread.get('model')},thread)
            return
        cached=self.history_cache.get((self.remote_host,thread_id))
        if cached:
            thread=cached['thread']
            self.finish_thread_switch({'model':thread.get('model'),'reasoningEffort':thread.get('reasoningEffort')},thread)
            # Refresh the cached view in the background; this keeps the UI
            # responsive and still picks up messages from the Mac promptly.
            self.refresh_selected_thread(thread_id)
            return
        self.refresh_selected_thread(thread_id)

    def refresh_selected_thread(self,thread_id):
        host=self.remote_host
        def load():
            try:
                result,thread=self.backend.select_thread(thread_id)
                if host!=self.remote_host:return
                if self.thread_id==thread_id and host:
                    digest=json.dumps(thread.get('turns',[]),sort_keys=True,ensure_ascii=False,default=str)
                    GLib.idle_add(self.refresh_remote_history,host,thread_id,thread,digest)
                elif self.loading_thread_id==thread_id:
                    GLib.idle_add(self.finish_thread_switch,result,thread)
            except Exception:
                if host==self.remote_host and self.loading_thread_id==thread_id:GLib.idle_add(self.thread_switch_failed)
        threading.Thread(target=load,daemon=True).start()

    def begin_thread_switch(self):
        self.connecting=True;self.history_ready=False;self.pending_events=[]
        self.thread_list.set_sensitive(False);self.new_chat_button.set_sensitive(False)
        self.spinner.start();self.activity.set_text('Открываю чат…')
        self.draft_changed(self.text.get_buffer())

    def finish_thread_switch(self,result,thread):
        self.loading_thread_id=None
        self.thread_id=thread['id']
        if self.provider=='codex':self.codex_thread_id=self.thread_id
        path_thread=self.thread_file();path_thread.parent.mkdir(parents=True,exist_ok=True,mode=0o700);path_thread.write_text(self.thread_id);path_thread.chmod(0o600)
        path=self.draft_path(self.thread_id)
        self.text.get_buffer().set_text(path.read_text() if path.exists() else '')
        self.load_history(result,thread)

    def thread_switch_failed(self):
        self.loading_thread_id=None
        self.connecting=False;self.history_ready=True
        self.thread_list.set_sensitive(True);self.new_chat_button.set_sensitive(True)
        self.set_working(self.engine_active)
        self.activity.set_text('Не удалось открыть чат. Текущий разговор сохранён.')
        self.draft_changed(self.text.get_buffer())
        events,self.pending_events=self.pending_events,[]
        for event in events:self.on_event(event)

    def new_chat(self,*_):
        if self.busy or self.sending or self.connecting:return
        if self.provider in self.external_threads:
            self.save_draft(self.text.get_buffer());self.create_external_chat();return
        if not self.backend or not self.backend.connected:return
        self.save_draft(self.text.get_buffer())
        self.begin_thread_switch()
        thread={'id':str(uuid.uuid4()),'name':translator.text('Новый чат'),'preview':'','turns':[],'createdAt':int(time.time()),'updatedAt':int(time.time()),'model':self.current_model,'localDraft':True,'host':self.remote_host}
        self.empty_threads[thread['id']]=thread
        self.save_empty_threads()
        self.finish_thread_switch({'model':self.current_model},thread)

    def save_empty_threads(self):
        (DRAFT.parent/'empty-chats.json').write_text(json.dumps(self.empty_threads,ensure_ascii=False))

    def promote_empty_thread(self,old_id,result,done):
        thread=result['thread'];new_id=thread['id']
        self.empty_threads.pop(old_id,None)
        self.empty_threads[new_id]=thread
        self.thread_cache.pop(old_id,None);self.thread_cache[new_id]=thread
        if old_id in self.model_by_thread:self.model_by_thread[new_id]=self.model_by_thread.pop(old_id)
        if old_id in self.runtime_preferences:self.runtime_preferences[new_id]=self.runtime_preferences.pop(old_id)
        for job in self.outbox:
            if job['threadId']==old_id:job['threadId']=new_id
        old_draft=self.draft_path(old_id);new_draft=self.draft_path(new_id)
        if old_draft.exists():new_draft.parent.mkdir(parents=True,exist_ok=True,mode=0o700);new_draft.write_text(old_draft.read_text());new_draft.chmod(0o600)
        if self.thread_id==old_id:
            self.thread_id=new_id;self.thread_file().write_text(new_id)
            self.current_model=result.get('model')
            self.save_draft(self.text.get_buffer())
        self.thread_activity[new_id]=False
        self.save_empty_threads();self.save_outbox();self.render_thread_list()
        done.set()

    def save_provider_chats(self):
        path=DRAFT.parent/'provider-chats.json';path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        temporary=path.with_suffix('.json.tmp')
        fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
        with os.fdopen(fd,'w') as stream:json.dump({'chats':self.external_threads,'selected':self.external_thread_ids},stream,ensure_ascii=False)
        os.replace(temporary,path)

    def provider_changed(self,picker):
        if self._updating_model:return
        target=picker.get_active_id() or 'codex'
        if target==self.provider:return
        if self.busy or self.sending or self.connecting:
            self._updating_model=True;picker.set_active_id(self.provider);self._updating_model=False
            self.message('Дождитесь завершения текущего запроса перед сменой источника.');return
        if self.provider in self.external_thread_ids:self.external_thread_ids[self.provider]=self.thread_id or ''
        else:self.codex_thread_id=self.thread_id
        self.provider=target
        local_codex=target=='codex'
        self.device_strip.set_visible(local_codex);self.add_device_button.set_visible(True);self.refresh_devices_button.set_visible(local_codex)
        self.chat_search.set_text('')
        self.available_models=[]
        self.current_model=None
        self.thread_list.set_sensitive(True);self.new_chat_button.set_sensitive(True)
        if target=='codex':
            self.thread_id=''
            self.thread_cache=dict(self.device_thread_caches.get(self.remote_host,self.codex_thread_cache))
            target_id=self.codex_thread_id
            self.provider_action_button.hide()
            self.claude_action_button.hide()
            self.more_chats_button.set_visible(bool(self.thread_cursor))
            if target_id and self.backend and self.backend.connected:
                self.loading_thread_id=target_id;self.begin_thread_switch();self.refresh_selected_thread(target_id)
            elif self.backend and self.backend.connected:
                self.connecting=False;self.history_ready=True;self.thread_id='';self.render_thread_list();self.new_chat()
            else:self.reconnect()
            return
        self.thread_id=self.external_thread_ids.get(target,'')
        self.thread_cache={ident:{'id':ident,'name':chat.get('name') or translator.text('Новый чат'),'updatedAt':chat.get('updatedAt',0),'createdAt':chat.get('createdAt',0)} for ident,chat in self.external_threads[target].items()}
        self.provider_action_button.set_visible(target=='deepseek')
        self.tokenharbor_action_button.set_visible(target=='tokenharbor')
        self.claude_action_button.set_visible(target=='claude')
        self.more_chats_button.hide()
        if target=='claude' and not providers.claude_code_available():
            self.message('Для этого источника нужен официальный Claude Code. Установите его и настройте собственный доступ по инструкции Anthropic.')
        if target=='deepseek' or target.startswith('custom:'):self.load_models()
        else:
            catalog=self.external_models[target]
            self.available_models=[{'id':item['id'],'model':item['id'],'displayName':item['name'],'supportedReasoningEfforts':[]} for item in catalog]
            self.update_model_picker()
        self.render_thread_list()
        if self.thread_id and self.thread_id in self.external_threads[target]:self.render_external_history(self.external_threads[target][self.thread_id])
        else:self.new_chat()

    def launch_claude_login(self,*_,console=False):
        if not providers.claude_code_available():
            subprocess.Popen(['/usr/bin/xdg-open','https://code.claude.com/docs/en/setup'],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
            self.message('Открыл официальную инструкцию установки Claude Code. После установки нажмите «Настроить Claude Code».');return
        try:
            providers.launch_claude_setup(console=console)
            self.message('Открыт официальный вход Anthropic Console. API-расходы оплачиваются по вашему доступу.' if console else 'Открыт официальный Claude Code: выберите собственный доступ. Для смены входа используйте /login. Аккаунт, API или облачная платформа могут иметь отдельные расходы.')
        except providers.ProviderError as exc:self.message(str(exc))

    def show_connect_menu(self,*_):
        """Offer AI providers and remote Codex from the header's add button."""
        menu=Gtk.Menu()
        choices=[
            ('Подключить Codex на другом компьютере',self.prompt_remote_host),
            ('Управлять этим Steam Deck с Mac / ПК',self.show_remote_access),
            ('Подключить Claude Code',self.connect_claude_provider),
            ('Войти через Anthropic Console (API)',self.connect_claude_console),
            ('Подключить DeepSeek через OpenRouter',self.connect_deepseek_provider),
            ('Подключить DeepSeek через TokenHarbor',self.connect_tokenharbor_provider),
            ('Подключить свой ИИ (любой API)…',self.configure_custom_provider),
        ]
        for label,callback in choices:
            item=Gtk.MenuItem(label=translator.text(label));item.connect('activate',callback);menu.append(item)
        menu.show_all()
        menu.popup_at_widget(self.add_device_button,Gdk.Gravity.SOUTH_WEST,Gdk.Gravity.NORTH_WEST,None)

    def show_remote_access(self,*_):
        import remote_access
        remote_access.show(self.window,translator.language)

    def connect_claude_console(self,*_):
        self.provider_picker.set_active_id('claude')
        GLib.idle_add(lambda:self.launch_claude_login(console=True))

    def connect_claude_provider(self,*_):
        self.provider_picker.set_active_id('claude')
        GLib.idle_add(self.launch_claude_login)

    def connect_deepseek_provider(self,*_):
        self.provider_picker.set_active_id('deepseek')
        GLib.idle_add(self.configure_openrouter)

    def connect_tokenharbor_provider(self,*_):
        self.provider_picker.set_active_id('tokenharbor')
        if not providers.read_tokenharbor_key():GLib.idle_add(self.configure_tokenharbor)

    def configure_openrouter(self,*_):
        dialog=Gtk.Dialog(title='DeepSeek через OpenRouter',transient_for=self.window,flags=Gtk.DialogFlags.MODAL)
        translator.watch_dialog(dialog)
        dialog.add_buttons('Отмена',Gtk.ResponseType.CANCEL,'Сохранить ключ',Gtk.ResponseType.OK)
        dialog.set_default_size(430,-1)
        box=dialog.get_content_area();box.set_spacing(10);box.set_margin_top(14);box.set_margin_bottom(14);box.set_margin_start(14);box.set_margin_end(14)
        note=Gtk.Label(label='Введите API-ключ OpenRouter. Он сохранится в системном хранилище секретов SteamOS и не попадёт в файлы проекта.',xalign=0);note.set_line_wrap(True);box.pack_start(note,False,False,0)
        entry=Gtk.Entry();entry.set_visibility(False);entry.set_placeholder_text('sk-or-v1-…');entry.set_activates_default(True);box.pack_start(entry,False,False,0)
        try:
            current=providers.read_openrouter_key()
            entry.set_placeholder_text('Ключ уже сохранён · введите новый для замены' if current else 'sk-or-v1-…')
        except providers.ProviderError:pass
        dialog.set_default_response(Gtk.ResponseType.OK);box.show_all()
        if dialog.run()==Gtk.ResponseType.OK:
            try:
                providers.save_openrouter_key(entry.get_text())
                self.message('Ключ сохранён в системном хранилище секретов. Загружаю каталог DeepSeek…')
                self.load_models()
            except providers.ProviderError as exc:self.message(str(exc))
        dialog.destroy()

    def configure_custom_provider(self,*_):
        """Any cloud AI with an OpenAI-compatible API: OpenAI, Gemini, Groq, Mistral, DeepSeek, xAI, OpenRouter."""
        dialog=Gtk.Dialog(title='Свой ИИ',transient_for=self.window,flags=Gtk.DialogFlags.MODAL)
        dialog.add_buttons('Отмена',Gtk.ResponseType.CANCEL,'Добавить',Gtk.ResponseType.OK)
        dialog.set_default_size(470,-1)
        box=dialog.get_content_area();box.set_spacing(8);box.set_margin_top(14);box.set_margin_bottom(14);box.set_margin_start(14);box.set_margin_end(14)
        note=Gtk.Label(label='Подойдёт любой облачный сервис с OpenAI-совместимым API (OpenAI, Gemini, Groq, Mistral, DeepSeek, xAI…). Нужен https-адрес и ключ API; ключ сохранится в системном хранилище секретов. Локальные серверы не поддерживаются.',xalign=0);note.set_line_wrap(True);box.pack_start(note,False,False,0)
        preset=Gtk.ComboBoxText();preset.append_text('Выберите готовый пример…')
        for title,_url in providers.CUSTOM_PRESETS:preset.append_text(title)
        preset.set_active(0);box.pack_start(preset,False,False,0)
        name=Gtk.Entry();name.set_placeholder_text('Название, например: Groq');box.pack_start(name,False,False,0)
        url=Gtk.Entry();url.set_placeholder_text('Адрес API, например: https://api.groq.com/openai/v1');box.pack_start(url,False,False,0)
        models=Gtk.Entry();models.set_placeholder_text('Модели через запятую (необязательно)');box.pack_start(models,False,False,0)
        key=Gtk.Entry();key.set_visibility(False);key.set_placeholder_text('Ключ API');box.pack_start(key,False,False,0)
        def choose(combo):
            index=combo.get_active()
            if index>0:
                title,address=providers.CUSTOM_PRESETS[index-1];url.set_text(address)
                if not name.get_text():name.set_text(title.split(' · ')[0])
        preset.connect('changed',choose);box.show_all()
        if dialog.run()==Gtk.ResponseType.OK:
            try:
                ident=providers.save_custom(STATE_DIR,name.get_text(),url.get_text(),models.get_text(),key.get_text())
                self.custom_providers=providers.load_custom(STATE_DIR)
                entry=self.custom_entry(ident)
                self.external_threads.setdefault(ident,{});self.external_thread_ids.setdefault(ident,'');self.external_models[ident]=[]
                if ident not in [row[0] for row in self.provider_titles]:
                    self.provider_titles.append((ident,entry['name']));self.provider_picker.append(ident,entry['name'])
                self.provider_picker.set_active_id(ident)
            except providers.ProviderError as exc:self.message(str(exc))
        dialog.destroy()

    def configure_tokenharbor(self,*_):
        dialog=Gtk.Dialog(title='DeepSeek через TokenHarbor',transient_for=self.window,flags=Gtk.DialogFlags.MODAL)
        translator.watch_dialog(dialog)
        dialog.add_buttons('Отмена',Gtk.ResponseType.CANCEL,'Сохранить ключ',Gtk.ResponseType.OK)
        dialog.set_default_size(430,-1)
        box=dialog.get_content_area();box.set_spacing(10);box.set_margin_top(14);box.set_margin_bottom(14);box.set_margin_start(14);box.set_margin_end(14)
        note=Gtk.Label(label='Ключ TokenHarbor сохраняется в системном хранилище SteamOS. Модель DeepSeek V4.1 Flash · бесплатно.',xalign=0);note.set_line_wrap(True);box.pack_start(note,False,False,0)
        entry=Gtk.Entry();entry.set_visibility(False);entry.set_placeholder_text('Введите новый ключ для замены');entry.set_activates_default(True);box.pack_start(entry,False,False,0)
        dialog.set_default_response(Gtk.ResponseType.OK);box.show_all()
        if dialog.run()==Gtk.ResponseType.OK:
            try:
                providers.save_tokenharbor_key(entry.get_text())
                self.message('Ключ TokenHarbor сохранён в системном хранилище.')
            except providers.ProviderError as exc:self.message(str(exc))
        dialog.destroy()

    def refresh_provider_model_list(self,models,source=None):
        source=source or self.provider
        if source not in ('deepseek','tokenharbor') and not source.startswith('custom:') or self.provider!=source:return False
        self.external_models[source]=models
        def price(model):
            if model.get('inputPrice')==0 and model.get('outputPrice')==0:return 'бесплатно'
            if model.get('inputPrice') is None:return 'цена не указана'
            return f"${model['inputPrice']*1_000_000:.2f}/${model['outputPrice']*1_000_000:.2f} за 1M токенов"
        self.available_models=[{'id':m['id'],'model':m['id'],'displayName':m['name']+('' if source.startswith('custom:') else ' · '+price(m)),'supportedReasoningEfforts':[]} for m in models]
        self.update_model_picker()

    def create_external_chat(self):
        ident=str(uuid.uuid4());now=int(time.time())
        chat={'id':ident,'provider':self.provider,'name':translator.text('Новый чат'),'createdAt':now,'updatedAt':now,'model':self.model_picker.get_active_id(),'messages':[]}
        self.external_threads[self.provider][ident]=chat;self.external_thread_ids[self.provider]=ident;self.thread_id=ident
        self.save_provider_chats()
        self.thread_cache[ident]={'id':ident,'name':chat['name'],'createdAt':now,'updatedAt':now}
        self.render_thread_list();self.render_external_history(chat)

    def render_external_history(self,chat):
        for child in self.chat.get_children():child.destroy()
        self.messages={};self.pending_messages={};self.engine_active=False;self.turn_id=None
        self.current_model=chat.get('model')
        self.chat_title.set_text(chat.get('name') or 'Новый чат')
        self.update_model_picker()
        for item in chat.get('messages',[]):
            kind='userMessage' if item.get('role')=='user' else 'agentMessage'
            self.add_item({'id':item.get('id') or str(uuid.uuid4()),'type':kind,'content':[{'type':'text','text':item.get('text','')}], 'text':item.get('text',''),'images':item.get('images',[])})
        self.set_working(False)

    def external_send(self,text):
        chat=self.external_threads[self.provider].get(self.thread_id)
        if not chat:raise RuntimeError('Сначала создайте чат этого источника.')
        self.sending=True;self.send_button.set_sensitive(False)
        self.message('Отправляю запрос…')
        selected=self.model_picker.get_active_id() or chat.get('model')
        if not selected:raise providers.ProviderError('Сначала загрузите список моделей этого источника.')
        prior=[{'role':item['role'],'content':item['text']} for item in chat.get('messages',[]) if item.get('role') in ('user','assistant')]
        user={'id':str(uuid.uuid4()),'role':'user','text':text}
        chat['messages'].append(user);chat['updatedAt']=int(time.time())
        if chat.get('name') in ('','Новый чат','New chat'):
            chat['name']=text.splitlines()[0][:100]
        chat['model']=selected
        self.external_thread_ids[self.provider]=chat['id'];self.save_provider_chats()
        self.thread_cache[chat['id']]={'id':chat['id'],'name':chat['name'],'createdAt':chat['createdAt'],'updatedAt':chat['updatedAt']}
        self.render_thread_list();self.render_external_history(chat)
        self.set_working(True)
        self.text.get_buffer().set_text('')
        provider=self.provider;session=chat['id'];working_dir=str(Path.home());resume=bool(chat.get('claudeStarted'))
        if provider=='claude':chat['claudeStarted']=True;self.save_provider_chats()
        def worker():
            try:
                if provider=='deepseek':answer=providers.openrouter_reply(selected,prior,text)
                elif provider=='tokenharbor':answer=providers.tokenharbor_reply(selected,prior,text)
                elif provider.startswith('custom:'):answer=providers.custom_reply(self.custom_entry(provider),selected,prior,text)
                else:answer=providers.claude_code_reply(selected,session,text,working_dir,resume)
                error=''
            except Exception as exc:answer='';error=str(exc)
            GLib.idle_add(self.external_reply_finished,provider,session,answer,error)
        threading.Thread(target=worker,daemon=True).start()

    def external_reply_finished(self,provider,session,answer,error):
        chat=self.external_threads.get(provider,{}).get(session)
        if not chat:return False
        if answer:chat['messages'].append({'id':str(uuid.uuid4()),'role':'assistant','text':answer})
        else:chat['messages'].append({'id':str(uuid.uuid4()),'role':'assistant','text':'Ошибка: '+error})
        chat['updatedAt']=int(time.time());self.save_provider_chats()
        if self.provider==provider and self.thread_id==session:self.render_external_history(chat)
        self.sending=False;self.send_button.set_sensitive(True)
        entry=self.custom_entry(provider)
        self.message(error or ('Ответ Claude готов' if provider=='claude' else ('Ответ: '+entry['name']) if entry else 'Ответ DeepSeek готов'))
        if answer and self.provider==provider and self.thread_id==session and self.runtime_preferences.get('readReplies'):self.speak_text(answer)
        return False

    def custom_entry(self,ident):
        return next((entry for entry in self.custom_providers if entry['id']==ident),None)

    def load_models(self):
        if self.provider.startswith('custom:'):
            source=self.provider;entry=self.custom_entry(source)
            def load_custom():
                try:GLib.idle_add(self.refresh_provider_model_list,providers.custom_models(entry),source)
                except Exception as exc:GLib.idle_add(self.message,'Не удалось получить список моделей: '+str(exc))
            threading.Thread(target=load_custom,daemon=True).start();return
        if self.provider in ('deepseek','tokenharbor'):
            source=self.provider
            def load_external():
                try:
                    models=providers.list_deepseek_models() if source=='deepseek' else providers.tokenharbor_models()
                    GLib.idle_add(self.refresh_provider_model_list,models,source)
                except Exception as exc:GLib.idle_add(self.message,'Не удалось загрузить DeepSeek: '+str(exc))
            threading.Thread(target=load_external,daemon=True).start();return
        def load():
            try:
                models=[];cursor=None
                while True:
                    params={'limit':100,'includeHidden':True}
                    if cursor:params['cursor']=cursor
                    result=self.backend.request('model/list',params)
                    models.extend(result.get('data',[]));cursor=result.get('nextCursor')
                    if not cursor:break
                GLib.idle_add(self.models_loaded,models)
            except Exception as exc:GLib.idle_add(self.message,'Не удалось обновить модели: '+str(exc))
        threading.Thread(target=load,daemon=True).start()

    def models_loaded(self,models):
        if self.provider!='codex':return False
        self.available_models=models
        self.update_model_picker()

    def update_model_picker(self):
        self._updating_model=True
        self.model_picker.remove_all()
        selected=self.model_by_thread.get(self.thread_id,self.current_model)
        if not selected:
            default=next((model for model in self.available_models if model.get('isDefault')),None)
            if default:selected=default.get('model') or default['id']
            elif self.available_models:selected=self.available_models[0].get('model') or self.available_models[0]['id']
        known=set()
        for model in self.available_models:
            ident=model.get('model') or model['id']
            if ident in known:continue
            title=model.get('displayName') or ident
            if model.get('hidden'):title+=' · служебная'
            known.add(ident);self.model_picker.append(ident,title)
        if selected and selected not in known:self.model_picker.append(selected,selected)
        if selected:self.model_picker.set_active_id(selected)
        self._updating_model=False
        self.update_runtime_pickers()

    def update_runtime_pickers(self):
        self._updating_model=True
        selected=self.model_picker.get_active_id()
        model=next((m for m in self.available_models if (m.get('model') or m['id'])==selected),{})
        prefs=self.runtime_preferences.get(self.thread_id,{}).get(selected,{})
        labels={'none':'Без рассуждений','minimal':'Минимальная','low':'Низкая · быстрее','medium':'Средняя · баланс','high':'Высокая','xhigh':'Очень высокая','max':'Максимальная','ultra':'Ultra'}
        efforts=[p['reasoningEffort'] for p in model.get('supportedReasoningEfforts',[])]
        self.effort_picker.remove_all()
        for effort in efforts:self.effort_picker.append(effort,translator.text(labels.get(effort,effort)))
        effort=prefs.get('effort') or (self.current_effort if selected==self.current_model else None) or model.get('defaultReasoningEffort')
        if effort not in efforts:effort=efforts[0] if efforts else None
        if effort:self.effort_picker.set_active_id(effort)
        self.speed_picker.remove_all();self.speed_picker.append('default',translator.text('Обычная'))
        tiers={'default'}
        for tier in model.get('serviceTiers') or []:
            ident=tier['id']
            if ident not in tiers:self.speed_picker.append(ident,translator.text('Fast · приоритет') if ident=='priority' else tier.get('name',ident));tiers.add(ident)
        if 'fast' in (model.get('additionalSpeedTiers') or []) and 'priority' not in tiers:
            self.speed_picker.append('priority',translator.text('Fast · приоритет'));tiers.add('priority')
        tier=prefs.get('tier') or (self.current_tier if selected==self.current_model else None) or 'default'
        self.speed_picker.set_active_id(tier if tier in tiers else 'default')
        codex_source=self.provider=='codex'
        self.effort_picker.set_sensitive(codex_source and bool(efforts));self.speed_picker.set_sensitive(codex_source and len(tiers)>1)
        self.update_model_menu_label(selected,model,effort,tier,labels)
        self._updating_model=False

    def update_model_menu_label(self,selected=None,model=None,effort=None,tier=None,labels=None):
        if not hasattr(self,'model_menu_label'):return
        selected=selected or self.model_picker.get_active_id()
        model=model or next((m for m in self.available_models if (m.get('model') or m['id'])==selected),{})
        labels=labels or {'none':'Без рассуждений','minimal':'Минимальная','low':'Низкая','medium':'Средняя','high':'Высокая','xhigh':'Очень высокая','max':'Максимальная','ultra':'Ultra'}
        effort=effort or self.effort_picker.get_active_id()
        tier=tier or self.speed_picker.get_active_id() or 'default'
        model_name=next((m.get('displayName') or (m.get('model') or m['id']) for m in self.available_models if (m.get('model') or m['id'])==selected),selected or 'Выбрать модель')
        effort_name=translator.text(labels.get(effort,effort)) if effort else translator.text('авто')
        tier_name='Fast' if tier=='priority' else translator.text('обычная')
        self.model_menu_label.set_text(model_name if self.provider!='codex' else f'{model_name}  ·  {effort_name}  ·  {tier_name}')

    def runtime_changed(self,*_):
        if self._updating_model:return
        model=self.model_picker.get_active_id()
        if not model:return
        prefs={'effort':self.effort_picker.get_active_id(),'tier':self.speed_picker.get_active_id() or 'default'}
        self.runtime_preferences.setdefault(self.thread_id,{})[model]=prefs
        (DRAFT.parent/'runtime-preferences.json').write_text(json.dumps(self.runtime_preferences))
        self.update_model_menu_label()
        self.message('Настройки применятся к следующему сообщению')

    def model_changed(self,picker):
        if self._updating_model:return
        model=picker.get_active_id()
        if model:
            self.model_by_thread[self.thread_id]=model
            (DRAFT.parent/'model-preferences.json').write_text(json.dumps(self.model_by_thread))
            chat=self.external_threads.get(self.provider,{}).get(self.thread_id)
            if chat:chat['model']=model;self.save_provider_chats()
            entry=self.custom_entry(self.provider)
            provider_name={'codex':'Codex','claude':'Claude','deepseek':'DeepSeek','tokenharbor':'DeepSeek · TokenHarbor'}.get(self.provider,entry['name'] if entry else 'Deck AI')
            self.message('Модель для следующего сообщения: '+provider_name+' · '+model)
            self.update_runtime_pickers()

    def draft_path(self,thread_id):
        name=str(uuid.UUID(thread_id))
        return DRAFT.parent/'drafts'/(name+'.txt')

    def connect_backend(self):
        backend = Backend(lambda event:GLib.idle_add(self.on_event,event),lambda:GLib.idle_add(self.disconnected),self.remote_host)
        self.backend = backend
        try:
            codex_id=self.codex_thread_id if self.provider!='codex' else self.thread_id
            empty=self.empty_threads.get(codex_id)
            backend.connect(None)
            result, thread = {}, {}
            if self.provider=='codex' and codex_id and not empty:
                try:result, thread = backend.select_thread(codex_id)
                except Exception as exc:
                    if not backend.connected:raise
                    GLib.idle_add(self.message,'Старый диалог не загрузился: '+str(exc)[:180])
            account=backend.request('account/read',{},timeout=12).get('account')
            GLib.idle_add(self.update_account_menu,account)
            if self.provider!='codex':GLib.idle_add(self.external_backend_connected);return
            if empty:result,thread={'model':empty.get('model')},empty
            GLib.idle_add(self.load_history, result, thread)
        except Exception as exc:
            GLib.idle_add(self.connection_failed,str(exc))

    def external_backend_connected(self):
        self.connecting=False;self.history_ready=True
        self.reconnect_button.set_sensitive(False);self.reconnect_button.hide()
        self.thread_list.set_sensitive(True);self.new_chat_button.set_sensitive(True)
        self.set_working(False)
        return False

    def connection_failed(self, error):
        self.connecting = False
        if self.backend:self.backend.close()
        self.reconnect_button.set_sensitive(True)
        self.reconnect_button.show_all()
        self.message('Нет подключения')
        self.activity.set_text('Ошибка: '+str(error)[:240])
        self.activity.set_tooltip_text(str(error))
        self.open_recovery_terminal()
        self.draft_changed(self.text.get_buffer())

    def disconnected(self):
        if self.connecting: return
        self.open_recovery_terminal()
        self.message('Соединение прервано')
        self.activity.set_text('Черновик сохранён. Нажмите «Подключиться».')
        self.reconnect_button.set_sensitive(True)
        self.reconnect_button.show_all()
        self.spinner.stop()
        self.stop_button.set_sensitive(False)
        self.draft_changed(self.text.get_buffer())

    def load_history(self, result, thread):
        if not thread.get('id'):
            self.connecting=False
            self.new_chat()
            return False
        if thread.get('id'):
            key=(self.remote_host,thread['id'])
            self.history_cache[key]={'thread':thread,'savedAt':time.monotonic()}
            # Bound memory use and discard stale conversations after 30 min.
            cutoff=time.monotonic()-1800
            for old_key,value in list(self.history_cache.items()):
                if value.get('savedAt',0)<cutoff: self.history_cache.pop(old_key,None)
            while len(self.history_cache)>12:
                oldest=min(self.history_cache,key=lambda k:self.history_cache[k].get('savedAt',0))
                self.history_cache.pop(oldest,None)
        for child in self.chat.get_children(): child.destroy()
        self.messages = {}
        self.pending_messages = {}
        self.connecting = False
        self.engine_active = False
        self.turn_id = None
        self.dirty_messages.clear()
        self.follow_tail=True
        self.current_model=result.get('model') or thread.get('model')
        self.current_effort=result.get('reasoningEffort') or thread.get('reasoningEffort')
        self.current_tier=result.get('serviceTier') or 'default'
        if self.provider=='codex':self.codex_thread_id=thread['id']
        self.thread_cache[thread['id']]={key:value for key,value in thread.items() if key!='turns'}
        if self.remote_host:self.remote_history_digest=json.dumps(thread.get('turns',[]),sort_keys=True,ensure_ascii=False,default=str)
        self.chat_title.set_text(self.thread_title(thread))
        self.update_model_picker()
        self.thread_list.set_sensitive(True);self.new_chat_button.set_sensitive(True)
        for turn in thread.get('turns',[]):
            for item in turn.get('items',[]): self.add_item(item)
            if turn.get('status') == 'inProgress':
                self.engine_active = True; self.turn_id = turn['id']
        self.thread_activity[self.thread_id]=self.engine_active
        for job in self.outbox:
            if job['threadId']==self.thread_id:self.show_outbox_job(job)
        self.history_ready = True
        for event in self.pending_events: self.on_event(event)
        self.pending_events = []
        self.reconnect_button.set_sensitive(False)
        self.reconnect_button.hide()
        self.set_working(self.engine_active)
        self.draft_changed(self.text.get_buffer())
        GLib.idle_add(self.scroll_to_end)
        self.refresh_threads()
        if not self.available_models:self.load_models()

    def poll_remote_history(self):
        if not self.remote_host or not self.thread_id or not self.history_ready or self.remote_polling or not self.backend or not self.backend.connected:return True
        self.remote_polling=True;backend=self.backend;thread_id=self.thread_id;host=self.remote_host
        def poll():
            try:
                thread=backend.request('thread/read',{'threadId':thread_id,'includeTurns':True},timeout=20).get('thread',{})
                digest=json.dumps(thread.get('turns',[]),sort_keys=True,ensure_ascii=False,default=str)
                if digest!=self.remote_history_digest:GLib.idle_add(self.refresh_remote_history,host,thread_id,thread,digest)
            except Exception:pass
            finally:self.remote_polling=False
        threading.Thread(target=poll,daemon=True).start()
        return True

    def refresh_remote_history(self,host,thread_id,thread,digest):
        if host!=self.remote_host or thread_id!=self.thread_id:return False
        if digest==self.remote_history_digest:return False
        self.remote_history_digest=digest
        self.load_history({'model':thread.get('model'),'reasoningEffort':thread.get('reasoningEffort')},thread)
        return False

    def add_item(self, item):
        kind = item.get('type')
        if kind not in ('userMessage','agentMessage'): return
        ident = item['id']
        media=attachments(item)
        if kind == 'userMessage':
            text = '\n'.join(p.get('text','') for p in item.get('content',[]) if p.get('type')=='text')
            # Environment metadata is not a chat message.
            text = re.sub(r'<environment_context>.*?</environment_context>','',text,flags=re.S).strip()
            if not text and not media: return
        else: text = item.get('text','')
        text=display_text(text)
        pending_id = item.get('clientId')
        if kind=='userMessage' and pending_id not in self.pending_messages:
            if ident in self.pending_messages: pending_id=ident
            else:
                pending_id=next((key for key,old in self.pending_messages.items() if self.messages.get(old,{}).get('text')==text),None)
        if pending_id in self.pending_messages:
            old = self.pending_messages.pop(pending_id)
            self.messages[ident] = self.messages.pop(old)
            message=self.messages[ident]
            if 'queue_status' in message:message['queue_status'].hide();message['retry'].hide()
        if ident not in self.messages:
            frame = Gtk.Frame(); frame.set_shadow_type(Gtk.ShadowType.NONE)
            frame.get_style_context().add_class('chat-message')
            frame.get_style_context().add_class('user-message' if kind=='userMessage' else 'assistant-message')
            content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=7,margin=14)
            custom=self.custom_entry(getattr(self,'provider','codex'))
            assistant_name={'claude':'CLAUDE','deepseek':'DEEPSEEK','tokenharbor':'DEEPSEEK','codex':'CODEX'}.get(getattr(self,'provider','codex'),custom['name'].upper()[:20] if custom else 'CODEX')
            heading = UILabel(label='ВЫ' if kind=='userMessage' else assistant_name)
            heading.set_xalign(0); heading.get_style_context().add_class('message-author')
            heading_row=Gtk.Box(spacing=8)
            heading_row.pack_start(heading,True,True,0)
            if kind=='agentMessage':
                copy=self.button('edit-copy-symbolic','Копировать ответ',lambda _,key=ident:self.copy_message(key),'quiet')
                heading_row.pack_start(copy,False,False,0)
            content.pack_start(heading_row,False,False,0)
            label = Gtk.Label()
            label.set_xalign(0); label.set_yalign(0)
            label.set_line_wrap(True); label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
            label.set_selectable(True);label.set_width_chars(1);label.set_max_width_chars(80)
            label.get_style_context().add_class('message-body')
            content.pack_start(label,True,True,0)
            rich=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=9)
            rich.set_no_show_all(True)
            content.pack_start(rich,False,False,0);frame.add(content)
            self.chat.pack_start(frame,False,False,0)
            media_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
            content.pack_start(media_box,False,False,0)
            self.messages[ident] = {'label':label,'text':'','frame':frame,'media_box':media_box,'attachments':[],'type':kind,'rich_box':rich,'block_widgets':[]}
            frame.show_all()
        self.messages[ident]['text'] = text
        self.render_message_body(self.messages[ident])
        message=self.messages[ident]
        if message.get('attachments')!=media:
            box=message['media_box']
            for child in box.get_children():child.destroy()
            for attachment in media:
                if attachment['preview']:
                    loader=GdkPixbuf.PixbufLoader.new()
                    loader.write(base64.b64decode(attachment['preview'].split(',',1)[1]));loader.close()
                    pixbuf=loader.get_pixbuf()
                    scale=min(1,320/pixbuf.get_width(),200/pixbuf.get_height())
                    thumbnail=pixbuf.scale_simple(max(1,int(pixbuf.get_width()*scale)),max(1,int(pixbuf.get_height()*scale)),GdkPixbuf.InterpType.BILINEAR)
                    button=Gtk.Button();button.set_halign(Gtk.Align.START)
                    button.add(Gtk.Image.new_from_pixbuf(thumbnail));button.set_tooltip_text(attachment['name'])
                    button.connect('clicked',lambda _,image=pixbuf,name=attachment['name']:self.show_attachment(image,name))
                    box.pack_start(button,False,False,0)
                else:
                    caption=Gtk.Label(label='📎 '+attachment['name']+' · '+('изображение недоступно' if attachment['kind']=='image' else 'файл'),xalign=0)
                    caption.set_line_wrap(True);box.pack_start(caption,False,False,0)
            message['attachments']=media;box.show_all()
        self.dirty_messages.discard(ident)

    def copy_text(self,text):
        if not text:return False
        try:
            clipboard=Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(text,-1);clipboard.store()
            self.message(translator.text('Текст скопирован'))
            return True
        except Exception:
            self.message(translator.text('Не удалось скопировать текст'));return False

    def copy_message(self,ident):
        message=self.messages.get(ident)
        if message:self.copy_text(message['text'])

    def render_message_body(self,message):
        text=message['text']
        if message.get('rendered_text')==text:return
        message['rendered_text']=text
        message['label'].set_text(text or '…')
        if message.get('type')!='agentMessage' or 'rich_box' not in message:return
        parts=split_message(text)
        rich=message['rich_box']
        if not any(part['kind']!='text' for part in parts):
            message['label'].set_no_show_all(False);message['label'].show()
            rich.set_no_show_all(True);rich.hide()
            return
        message['label'].set_no_show_all(True);message['label'].hide()
        existing=message['block_widgets']
        structure=[(part['kind'],part['language']) for part in parts]
        if message.get('block_structure')!=structure:
            for child in rich.get_children():child.destroy()
            existing=[]
            for part in parts:
                record={'text':part['text']}
                label=Gtk.Label(xalign=0,yalign=0)
                label.set_selectable(True);label.set_line_wrap(True)
                label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                label.set_width_chars(1);label.set_max_width_chars(80)
                label.get_style_context().add_class('message-body')
                record['label']=label
                if part['kind']=='text':rich.pack_start(label,False,False,0)
                else:
                    frame=Gtk.Frame();frame.set_shadow_type(Gtk.ShadowType.NONE)
                    frame.get_style_context().add_class('copy-block')
                    block=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6,margin=10)
                    header=Gtk.Box(spacing=8)
                    title={'code':'Код','command':'Команда','post':'Готовый текст','quote':'Текст'}.get(part['kind'],'Текст')
                    caption=UILabel(label=title)
                    header.pack_start(caption,True,True,0)
                    button=self.button('edit-copy-symbolic','Копировать',lambda _,current=record:self.copy_text(current['text']),'quiet')
                    header.pack_start(button,False,False,0);record['copy_button']=button
                    if part['kind'] in ('code','command'):label.get_style_context().add_class('code-body')
                    block.pack_start(header,False,False,0);block.pack_start(label,False,False,0)
                    frame.add(block);rich.pack_start(frame,False,False,0)
                existing.append(record)
            message['block_widgets']=existing;message['block_structure']=structure
        for record,part in zip(existing,parts):
            record['text']=part['text'];record['label'].set_text(part['text'])
        rich.set_no_show_all(False);rich.show_all()

    def show_attachment(self,pixbuf,name):
        dialog=Gtk.Dialog(title=name,transient_for=self.window,modal=True)
        translator.watch_dialog(dialog)
        dialog.add_button('Закрыть',Gtk.ResponseType.CLOSE)
        dialog.get_content_area().add(Gtk.Image.new_from_pixbuf(pixbuf))
        dialog.connect('response',lambda window,*_:window.destroy())
        dialog.show_all()

    def set_working(self, working):
        self.engine_active = working
        self.publish_update_activity()
        self.stop_button.set_sensitive(working and self.turn_id is not None)
        if working:
            self.spinner.start(); self.activity.set_text('Deck AI работает…')
            if not self.busy: self.message('В работе')
        else:
            self.spinner.stop(); self.activity.set_text('Продолжите разговор голосом или текстом')
            if not self.busy: self.message('Готов к работе')

    def on_event(self, event):
        method = event.get('method',''); params = event.get('params',{})
        if method in ('account/updated','account/login/completed'):
            GLib.idle_add(self.refresh_account_status)
            if method=='account/login/completed':GLib.idle_add(self.message,'Аккаунт Codex обновлён' if params.get('success') else (params.get('error') or 'Не удалось войти в аккаунт Codex.'))
            return
        if not self.history_ready:
            self.pending_events.append(event); return
        tid=params.get('threadId')
        if tid and method in ('turn/started','turn/completed'):self.thread_activity[tid]=method=='turn/started'
        if 'id' in event:
            self.server_request(event); return
        if params.get('threadId') not in (None,self.thread_id): return
        if method in ('item/started','item/completed'):
            item = params.get('item',{})
            self.add_item(item)
            if item.get('type')=='commandExecution': self.activity.set_text('Выполняю действие на устройстве…')
            elif item.get('type')=='fileChange': self.activity.set_text('Сохраняю изменения…')
        elif method == 'item/agentMessage/delta':
            ident = params['itemId']
            if ident not in self.messages: self.add_item({'type':'agentMessage','id':ident,'text':''})
            message = self.messages[ident]
            message['text'] += params.get('delta','')
            self.dirty_messages.add(ident)
        elif method == 'turn/started':
            self.turn_id = params['turn']['id']; self.set_working(True)
        elif method == 'turn/completed':
            self.set_working(False)
            if self.runtime_preferences.get('readReplies') and not params.get('turn',{}).get('error'):self.read_latest_answer(automatic=True)
            self.refresh_threads()
            error = params.get('turn',{}).get('error')
            if error:
                self.activity.set_text(error.get('message','Не удалось завершить ответ.'))
                self.add_item({'type':'agentMessage','id':'error-'+str(uuid.uuid4()),'text':'Codex сообщил об ошибке:\n'+error.get('message','Не удалось завершить ответ.')})
        elif method == 'error':
            self.activity.set_text(params.get('error',{}).get('message','Ошибка Codex'))

    def update_account_menu(self, account):
        if not hasattr(self,'account_item'):return False
        self.current_account=account
        signed=bool(account)
        label=(account or {}).get('email') or translator.text('Вход не выполнен')
        plan=(account or {}).get('planType')
        self.account_item.set_label(translator.text('Аккаунт')+': '+label)
        self.account_status_item.set_label(label+(' · '+plan if plan else ''))
        self.account_logout_item.set_sensitive(signed)
        self.account_login_item.set_label(translator.text('Войти или сменить аккаунт' if signed else 'Войти через ChatGPT'))
        self.account_item.show_all()
        return False

    def refresh_account_status(self):
        backend=self.backend
        if not backend or not backend.connected:return False
        def worker():
            try:account=backend.request('account/read',{},timeout=12).get('account')
            except Exception:return
            GLib.idle_add(self.update_account_menu,account)
        threading.Thread(target=worker,daemon=True).start()
        return False

    def open_recovery_terminal(self):
        if self.recovery_terminal_opened:return False
        if self.launch_codex_terminal(False):self.recovery_terminal_opened=True
        return False

    def open_terminal(self,*_):
        self.launch_codex_terminal(False)

    def launch_codex_login(self,*_):
        self.launch_codex_terminal(True)

    def confirm_terminal_login(self):
        dialog,content=self.request_dialog('Войти через терминал?')
        label=Gtk.Label(label='Вы точно уверены?\n\nПовторный вход может завершить текущую сессию авторизации Codex и прервать выполняющийся запрос. После входа может потребоваться повторное подключение.\n\nЧтобы просто открыть командную строку, нажмите «Отмена» и выберите «Терминал».',xalign=0)
        label.set_line_wrap(True);label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        label.set_max_width_chars(60);label.set_width_chars(1)
        content.pack_start(label,False,False,0)
        dialog.add_button('Отмена',Gtk.ResponseType.CANCEL)
        dialog.add_button('Продолжить вход',Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.CANCEL)
        dialog.show_all()
        try:return dialog.run()==Gtk.ResponseType.OK
        finally:dialog.destroy()

    def launch_codex_terminal(self,login):
        terminal=shutil.which('konsole') or shutil.which('xterm')
        if not terminal:
            self.message('Откройте терминал и выполните: codex login')
            return False
        if login and not self.confirm_terminal_login():return False
        if self.remote_host:
            command=['ssh','-t',self.remote_host,'codex login' if login else 'exec "$SHELL" -l']
        elif login:command=[CODEX,'login']
        else:command=['/bin/bash','-i']
        # Native terminals must not inherit bundled libraries or Steam preload hooks.
        environment=dict(os.environ)
        environment.pop('LD_LIBRARY_PATH',None)
        environment.pop('LD_PRELOAD',None)
        try:
            args=[terminal]+(['--hold'] if terminal.endswith('konsole') and login else ['-hold'] if login else [])+['-e']+command
            subprocess.Popen(args,start_new_session=True,env=environment)
            self.message('Терминал открыт. После входа нажмите «Подключиться».' if login else 'Терминал открыт без повторного входа в Codex.')
            return True
        except OSError as exc:
            self.message('Не удалось открыть терминал: '+str(exc)[:180])
            return False

    def begin_account_login(self,*_):
        backend=self.backend
        if not backend or not backend.connected:self.launch_codex_login();return
        self.account_login_item.set_sensitive(False)
        def worker():
            try:
                result=backend.request('account/login/start',{'type':'chatgptDeviceCode' if self.remote_host else 'chatgpt'},timeout=20)
                url=result.get('authUrl') or result.get('verificationUrl')
                if not url:raise RuntimeError('Codex не вернул ссылку для входа.')
                try:
                    subprocess.Popen(['/usr/bin/xdg-open',url],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
                    GLib.idle_add(self.message,('Код входа: '+result['userCode']+' · '+url) if result.get('userCode') else 'Страница входа открыта в браузере.')
                except OSError:GLib.idle_add(self.message,'Откройте '+url+(' · код '+result['userCode'] if result.get('userCode') else ''))
            except Exception as exc:
                GLib.idle_add(self.message,'Не удалось начать вход: '+str(exc)[:180])
                GLib.idle_add(self.launch_codex_login)
            finally:GLib.idle_add(self.account_login_item.set_sensitive,True)
        threading.Thread(target=worker,daemon=True).start()

    def confirm_account_logout(self,*_):
        dialog=Gtk.MessageDialog(transient_for=self.window,flags=Gtk.DialogFlags.MODAL,message_type=Gtk.MessageType.QUESTION,buttons=Gtk.ButtonsType.YES_NO,text='Выйти из аккаунта Codex?')
        translator.watch_dialog(dialog)
        dialog.format_secondary_text('Для продолжения работы потребуется снова войти в ChatGPT.')
        response=dialog.run();dialog.destroy()
        if response==Gtk.ResponseType.YES:self.logout_account()

    def logout_account(self):
        backend=self.backend
        if not backend or not backend.connected:self.message('Сначала подключитесь к Codex.');return
        self.account_logout_item.set_sensitive(False)
        def worker():
            try:
                backend.request('account/logout',{},timeout=20)
                GLib.idle_add(self.update_account_menu,None);GLib.idle_add(self.message,'Вы вышли из аккаунта Codex.')
                GLib.idle_add(self.load_models)
            except Exception as exc:GLib.idle_add(self.message,'Не удалось выйти: '+str(exc)[:180])
            finally:GLib.idle_add(self.refresh_account_status)
        threading.Thread(target=worker,daemon=True).start()

    def interrupt(self, *_):
        if not self.turn_id or not self.backend or not self.backend.connected: return
        self.stop_button.set_sensitive(False)
        thread_id,turn_id=self.thread_id,self.turn_id
        def stop():
            try: self.backend.request('turn/interrupt',{'threadId':thread_id,'turnId':turn_id})
            except Exception: GLib.idle_add(self.message,'Не удалось остановить. Попробуйте снова.')
        threading.Thread(target=stop,daemon=True).start()

    def request_dialog(self,title):
        dialog=Gtk.Dialog(title=title,transient_for=self.window,modal=True)
        translator.watch_dialog(dialog)
        dialog.set_name('voice-panel')
        dialog.get_style_context().add_class('request-panel')
        dialog.get_action_area().get_style_context().add_class('request-actions')
        display=Gdk.Display.get_default()
        monitor=display.get_monitor_at_window(self.window.get_window()) if self.window.get_window() else display.get_monitor(0)
        rect=monitor.get_workarea()
        if self.gaming_mode:
            # Gamescope scales a small dialog independently of the main window.
            # Keep the same native surface size and identity as the application.
            width,height=self.window.get_size()
            if width<320 or height<240:
                geometry=monitor.get_geometry();width,height=geometry.width,geometry.height
            dialog.set_wmclass('deckai','DeckAI')
            dialog.set_decorated(False)
            dialog.set_default_size(width,height)
            dialog.resize(width,height)
            dialog.fullscreen()
        else:
            dialog.set_default_size(min(720,max(280,rect.width-40)),min(520,max(180,rect.height-60)))
            dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        outer=dialog.get_content_area();outer.set_spacing(8);outer.set_border_width(12)
        scroll=Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.ALWAYS)
        scroll.set_overlay_scrolling(False)
        scroll.set_min_content_height(0)
        content=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10)
        scroll.add(content);outer.pack_start(scroll,True,True,0)
        dialog.request_scroll=scroll
        down=Gtk.Button(label='Вниз ↓')
        down.set_halign(Gtk.Align.END)
        down.connect('clicked',lambda *_:scroll.get_vadjustment().set_value(max(0,scroll.get_vadjustment().get_upper()-scroll.get_vadjustment().get_page_size())))
        outer.pack_start(down,False,False,0)
        return dialog,content

    @staticmethod
    def approval_result(method,params,accepted):
        if method=='item/permissions/requestApproval':
            return {'permissions':params.get('permissions',{}) if accepted else {},'scope':'turn'}
        return {'decision':'accept' if accepted else 'decline'}

    def server_request(self, event):
        method=event['method'];params=event.get('params',{});ident=event['id']
        backend=self.backend
        if method.endswith('/requestUserInput'):
            self.input_request(ident,params);return
        supported={'item/commandExecution/requestApproval','item/fileChange/requestApproval','item/permissions/requestApproval'}
        if method in supported:
            available=params.get('availableDecisions')
            can_accept=available is None or 'accept' in available
            if self.auto_approve and can_accept:
                backend.respond(ident,self.approval_result(method,params,True))
                self.activity.set_text('Автоодобрено: '+str(params.get('reason') or params.get('command') or method)[:140])
                return
            dialog,content=self.request_dialog('Codex запрашивает разрешение')
            details=params.get('reason') or 'Проверьте действие перед подтверждением.'
            if params.get('command'):details+='\n\n'+str(params['command'])
            if params.get('cwd'):details+='\n\nПапка: '+str(params['cwd'])
            if params.get('grantRoot'):details+='\n\nДоступ к: '+str(params['grantRoot'])
            for field in ('permissions','additionalPermissions'):
                if params.get(field):details+='\n\n'+json.dumps(params[field],ensure_ascii=False,indent=2)
            text=Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD_CHAR)
            text.set_editable(False);text.set_cursor_visible(False)
            text.get_buffer().set_text(details)
            scroll=dialog.request_scroll
            scroll.remove(scroll.get_child());scroll.add(text)
            dialog.add_button('Отклонить',Gtk.ResponseType.CANCEL)
            allow=dialog.add_button('Разрешить',Gtk.ResponseType.OK)
            allow.set_sensitive(can_accept)
            def answer(widget,response):
                backend.respond(ident,self.approval_result(method,params,response==Gtk.ResponseType.OK and can_accept))
                widget.destroy()
            dialog.connect('response',answer);self.window.present();dialog.show_all()
        else:
            backend.respond(ident,error={'code':-32601,'message':'This client does not support '+method})
            self.activity.set_text('Для этого действия пока нет интерфейса в приложении.')

    def input_request(self, ident, params):
        backend=self.backend
        dialog,box=self.request_dialog('Вопрос от Codex')
        dialog.add_button('Отмена',Gtk.ResponseType.CANCEL)
        dialog.add_button('Ответить',Gtk.ResponseType.OK)
        fields={}
        for question in params.get('questions',[]):
            label=Gtk.Label(label=question['question'],xalign=0)
            label.set_line_wrap(True);label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
            label.set_max_width_chars(60);label.set_width_chars(1)
            box.pack_start(label,False,False,0)
            entry=Gtk.ComboBoxText.new_with_entry()
            for option in question.get('options') or []:entry.append_text(option['label'])
            if question.get('isSecret'):entry.get_child().set_visibility(False)
            box.pack_start(entry,False,False,0);fields[question['id']]=entry
        def answer(widget,response):
            answers={key:{'answers':[entry.get_child().get_text()] if response==Gtk.ResponseType.OK else []} for key,entry in fields.items()}
            backend.respond(ident,{'answers':answers});widget.destroy()
        dialog.connect('response',answer);self.window.present();dialog.show_all()

    def button(self, icon, label, callback, style):
        button = Gtk.Button(); button.get_style_context().add_class(style)
        row = Gtk.Box(spacing=8, halign=Gtk.Align.CENTER)
        row.pack_start(Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.LARGE_TOOLBAR if style == 'primary' else Gtk.IconSize.MENU), False, False, 0)
        if label:
            button.title_label=UILabel(label=label)
            row.pack_start(button.title_label, False, False, 0)
        button.add(row); button.connect('clicked', callback)
        if style == 'icon-only': button.set_tooltip_text('Закрыть панель')
        return button

    def draw_wave(self, widget, cr):
        width, height = widget.get_allocated_width(), widget.get_allocated_height()
        steel=(.72,.76,.81) if self.theme!='light' else (.32,.36,.40)
        cr.set_source_rgb(*((1, .33, .31) if self.recording else steel))
        cr.set_line_width(2.7); cr.set_line_cap(1)
        for i, base in enumerate([7, 14, 22, 14, 7]):
            amount = (0.25 + self.audio_level*0.75) if self.recording else 0.65
            h = max(4, base*amount)
            x = 2.5 + i*4.5
            cr.move_to(x, height/2-h/2); cr.line_to(x, height/2+h/2)
        cr.stroke()

    def animate(self):
        if hasattr(self, 'closed') and self.closed.is_set(): return False
        if self.recording: self.wave.queue_draw()
        return True

    def draft_changed(self, buffer):
        self.placeholder.set_visible(buffer.get_char_count() == 0)
        ready = self.provider in self.external_threads or (self.history_ready and self.backend is not None and self.backend.connected)
        self.send_button.set_sensitive(buffer.get_char_count() > 0 and not self.busy and not self.sending and ready)

    def recording_style(self, active):
        for widget in [self.mic, self.status_dot]:
            context = widget.get_style_context()
            if active: context.add_class('recording')
            else: context.remove_class('recording')
        self.draft_changed(self.text.get_buffer())
        self.wave.queue_draw()

    def watch_keyboard(self):
        # CoreKeyboard deliberately bypasses KWin; inspect its X11 map state.
        while not self.closed.is_set():
            top = -1
            try:
                tree = command('xwininfo', '-root', '-tree')
                for line in tree.splitlines():
                    if '("corekeyboard" "CoreKeyboard")' not in line:
                        continue
                    info = command('xwininfo', '-id', line.split()[0])
                    if 'IsViewable' in info:
                        match = re.search(r'Absolute upper-left Y:\s*(-?\d+)', info)
                        if match: top = int(match[1])
            except subprocess.SubprocessError:
                pass
            GLib.idle_add(self.keyboard_geometry, top)
            self.closed.wait(.65)

    def keyboard_geometry(self, top):
        scale = self.window.get_scale_factor()
        value = top // scale if top >= 0 else -1
        changed = value != self.keyboard_top
        self.keyboard_top = value
        if changed: self.position()
        context = self.keyboard_button.get_style_context()
        if self.keyboard_top >= 0: context.add_class('selected')
        else: context.remove_class('selected')

    def position(self):
        if self.gaming_mode:
            self.window.fullscreen()
            return
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() or display.get_monitor(0)
        rect = monitor.get_workarea()
        bottom = rect.y+rect.height
        if self.keyboard_top >= rect.y: bottom = min(bottom,self.keyboard_top-4)
        self.window.unmaximize()
        self.window.move(rect.x, rect.y)
        self.window.resize(rect.width, max(360,bottom-rect.y))

    def message(self, text):
        self.status.set_text(text)

    def clear(self, *_):
        self.text.get_buffer().set_text('')

    def save_draft(self, buffer):
        try:
            DRAFT.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
            paths=[DRAFT]
            if self.thread_id:
                path=self.draft_path(self.thread_id)
                path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
                paths.append(path)
            for path in paths:
                fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
                with os.fdopen(fd,'w') as f:f.write(text)
            return True
        except OSError:
            self.message('Не удалось сохранить черновик на диск.');return False

    def change_language(self, code):
        translator.set_language(code)
        self.provider_picker.remove_all()
        self._updating_model=True
        for ident,title in self.provider_titles:self.provider_picker.append(ident,translator.text(title))
        self.provider_picker.set_active_id(self.provider)
        self._updating_model=False
        self.provider_action_button.title_label.set_text(translator.text('Настроить DeepSeek / OpenRouter'))
        self.claude_action_button.title_label.set_text(translator.text('Настроить Claude Code'))
        self.chat_search.set_placeholder_text(translator.text('Найти чат'))
        for item in self.app_menu.get_children():
            source=getattr(item,'translation_source',None)
            if source:item.set_label(translator.text(source))
        self.update_account_menu(getattr(self,'current_account',None))
        self.update_runtime_pickers()
        self.app_keyboard.refresh()
        translator.bind_tree(self.window)
        translator.bind_tree(self.app_menu)

    def save_runtime_preferences(self):
        path=DRAFT.parent/'runtime-preferences.json'
        path.parent.mkdir(parents=True,exist_ok=True)
        temporary=path.with_suffix('.json.tmp')
        fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
        with os.fdopen(fd,'w') as stream:json.dump(self.runtime_preferences,stream)
        os.replace(temporary,path)

    def toggle_auto_approve(self,item):
        self.auto_approve=item.get_active()
        self.runtime_preferences['autoApprove']=self.auto_approve
        self.save_runtime_preferences()
        self.message('Автоодобрение разрешений включено' if self.auto_approve else 'Разрешения подтверждаются вручную')

    def install_directory(self):return ROOT

    def state_directory(self):return STATE_DIR

    def show_language_settings(self,*_):
        if self.language_settings is not None and not self.language_settings.closed:
            self.language_settings.dialog.present();return
        from language_settings import LanguageSettings
        self.language_settings=LanguageSettings(self)

    def stop_speaking(self,*_):
        if self.speech_cancel:self.speech_cancel.set()
        if self.speech_player:self.speech_player.stop()

    def speak_text(self,text,voice_id=None):
        from language_support import SpeechPlayer,Cancelled
        voice_id=voice_id or self.runtime_preferences.get('ttsVoice')
        if not voice_id or voice_id=='none':
            self.message(translator.text('Выберите голос в настройках языка'));return
        if not text.strip():return
        self.stop_speaking()
        if self.speech_player is None:self.speech_player=SpeechPlayer()
        player=self.speech_player;cancel=threading.Event();self.speech_cancel=cancel
        def worker():
            try:player.speak(text,voice_id,ROOT,cancel)
            except Cancelled:pass
            except Exception as error:GLib.idle_add(self.message,str(error)[:300])
        threading.Thread(target=worker,daemon=True).start()

    def read_latest_answer(self,*_,automatic=False):
        if not automatic and self.speech_player and self.speech_player.playing:
            self.stop_speaking();return
        message=next((item for item in reversed(list(self.messages.values())) if item.get('type')=='agentMessage' and item.get('text','').strip()),None)
        if message:self.speak_text(message['text'])
        else:self.message(translator.text('Нет ответа для озвучки'))

    def set_voice_refinement(self,enabled):
        self.voice_refinement=bool(enabled)
        self.runtime_preferences['voiceRefinement']=self.voice_refinement
        self.save_runtime_preferences()
        if self.voice_refinement_item.get_active()!=self.voice_refinement:
            self.voice_refinement_item.set_active(self.voice_refinement)
        if hasattr(self,'fast_voice') and self.fast_voice.get_active()==self.voice_refinement:
            self.fast_voice.set_active(not self.voice_refinement)

    def toggle_voice_refinement(self,item):
        self.set_voice_refinement(item.get_active())

    def switch_voice_language(self, button):
        if self.busy or self.recording:return
        from speech_accuracy import SPEECH_LANGUAGES
        menu=Gtk.Menu()
        def choose(item,code):
            self.voice_language=code;button.set_label('🎙 '+code.upper())
            self.fast_voice.set_sensitive(code in ('ru','en'))
            STATE_DIR.mkdir(parents=True,exist_ok=True)
            (STATE_DIR/'voice-language').write_text(code)
        for code,name in [('auto','Определять автоматически'),('ru',SPEECH_LANGUAGES.get('ru','Русский')),('en','English')]+[(code,name) for code,name in sorted(SPEECH_LANGUAGES.items(),key=lambda item:item[1]) if code not in ('ru','en')]:
            item=Gtk.MenuItem(label=name);item.connect('activate',choose,code);menu.append(item)
        menu.show_all();menu.popup_at_widget(button,Gdk.Gravity.NORTH_WEST,Gdk.Gravity.SOUTH_WEST,None)

    def keyboard(self, *_):
        visible=not self.app_keyboard.get_visible()
        if visible:
            self.app_keyboard.set_no_show_all(False)
            self.app_keyboard.show_all()
            self.app_keyboard.set_no_show_all(True)
        else:self.app_keyboard.hide()
        context=self.keyboard_button.get_style_context()
        if visible:context.add_class('selected')
        else:context.remove_class('selected')
        self.text.grab_focus()

    def toggle_record(self, *_):
        if self.recording:
            self.stop_event.set()
            self.mic.set_sensitive(False)
            self.message('Распознаю…')
        elif not self.busy:
            from language_support import recognition_ready
            if not recognition_ready(ROOT,self.voice_language):
                self.message(translator.text('Для этого языка нужно подготовить модель распознавания'))
                self.show_language_settings();return
            self.stop_speaking()
            self.recording = self.busy = True
            self.stop_event = threading.Event()
            self.mic_text.set_text('Закончить')
            self.recording_style(True)
            self.message('Подготовка микрофона…')
            threading.Thread(target=self.record, daemon=True).start()

    def record(self):
        result = ''; error = None; refiner = None
        stop = self.stop_event
        try:
            lang=self.voice_language
            if lang in ('ru','en'):
                try:from vosk import Model, KaldiRecognizer, SetLogLevel
                except ImportError:raise RuntimeError('Откройте Настройки → Языки и загрузите языковой пакет для диктовки.')
                SetLogLevel(-1)
            from speech_accuracy import fast_punctuation
            refine=self.voice_refinement or lang not in ('ru','en')
            path=ROOT/'models'/('vosk-model-small-en-us-0.15' if lang=='en' else 'vosk-model-small-ru-0.22')
            source = command('pactl', 'get-default-source')
            if source.endswith('.monitor'):
                raise RuntimeError('Выбран звук динамиков. Выберите микрофон в настройках звука.')
            self.recorder = subprocess.Popen(['ffmpeg', '-nostdin', '-loglevel', 'error', '-thread_queue_size', '1024', '-f', 'pulse', '-i', source, '-ac', '1', '-ar', '16000', '-f', 's16le', 'pipe:1'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            recorder = self.recorder
            recognizer=None
            if lang in ('ru','en'):
                if lang not in self.voice_models:self.voice_models[lang]=Model(str(path))
                recognizer=KaldiRecognizer(self.voice_models[lang],16000)
            from speech_accuracy import prewarm_worker
            refiner = prewarm_worker(lang, ROOT)
            GLib.idle_add(self.message, '● Слушаю · нажмите «Закончить»')
            parts = [];pcm=[]
            def stop_capture():
                stop.wait(90)
                stop.set()
                if recorder.poll() is None:
                    recorder.terminate()
            threading.Thread(target=stop_capture, daemon=True).start()
            while not stop.is_set():
                data = self.recorder.stdout.read(1600)
                if not data: break
                if refine:pcm.append(data)
                samples = array('h', data)
                self.audio_level = min(1.0, math.sqrt(sum(s*s for s in samples)/len(samples))/3000)
                if recognizer is None:continue
                if recognizer.AcceptWaveform(data):
                    parts.append(json.loads(recognizer.Result()).get('text', ''))
                partial = json.loads(recognizer.PartialResult()).get('partial', '')
                if partial:
                    GLib.idle_add(self.message, '● ' + partial[-85:])
            parts.append(json.loads(recognizer.FinalResult()).get('text', '') if recognizer else '')
            result = ' '.join((fast_punctuation(part,lang) if not refine else part) for part in parts if part).strip()
            if refine and not lang.endswith('-fast'):
                GLib.idle_add(self.message,'Уточняю распознанную речь…')
                from speech_accuracy import refine_dictation
                result=refine_dictation(b''.join(pcm),lang,result,ROOT,refiner);refiner=None
            from speech_accuracy import apply_corrections
            result=apply_corrections(result)
            if self.recorder.poll() not in (None, 0, -15, 255):
                raise RuntimeError('Не удалось записать микрофон. Проверьте настройки звука.')
        except Exception as exc:
            error = str(exc)
        finally:
            stop.set()
            if refiner is not None:
                from speech_accuracy import cancel_worker
                cancel_worker(refiner)
            if self.recorder is not None:
                if self.recorder.poll() is None: self.recorder.terminate()
                try: self.recorder.wait(timeout=3)
                except subprocess.TimeoutExpired: self.recorder.kill()
                self.recorder = None
            GLib.idle_add(self.finished, result, error)

    def finished(self, result, error):
        self.recording = self.busy = False
        self.mic_text.set_text('Говорить'); self.mic.set_sensitive(True)
        self.recording_style(False)
        if result:
            buffer = self.text.get_buffer()
            old = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
            buffer.set_text(old + ('' if not old or old[-1].isspace() else ' ') + result.strip() + ' ')
            buffer.place_cursor(buffer.get_end_iter())
            self.text.grab_focus()
            self.text.scroll_mark_onscreen(buffer.get_insert())
        self.message(error or ('Проверьте текст и нажмите «Отправить»' if result else 'Речь не распознана. Попробуйте ещё раз.'))

    def send(self, *_):
        if updates.updating(STATE_DIR):self.message(translator.text('Deck AI обновляется. Черновик сохранён.'));return
        if self.sending:
            self.message('Сообщение уже отправляется…'); return
        if self.busy:
            self.message('Сначала закончите запись.'); return
        if self.provider in self.external_threads:
            buffer = self.text.get_buffer()
            text = clean_text(buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False))
            if not text:return
            try:self.external_send(text)
            except Exception as exc:self.sending=False;self.send_button.set_sensitive(True);self.message(str(exc))
            return
        if not self.backend or not self.backend.connected or not self.history_ready:
            self.message('Сначала подключитесь к Codex. Черновик сохранён.'); return
        buffer = self.text.get_buffer()
        text = clean_text(buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False))
        if not text: return
        try:
            if not self.thread_id:
                raise RuntimeError('Диалог Codex не выбран. Текст сохранён.')
            self.sending = True
            self.send_button.set_sensitive(False)
            self.message('Отправляю…')
            client_id=str(uuid.uuid4())
            ident='pending-'+client_id
            self.add_item({'id':ident,'type':'userMessage','content':[{'type':'text','text':text}]})
            self.pending_messages[client_id]=ident
            job={'id':client_id,'threadId':self.thread_id,'host':self.remote_host,'text':text,'model':self.model_picker.get_active_id() or self.current_model,'effort':self.effort_picker.get_active_id(),'tier':self.speed_picker.get_active_id() or 'default','status':'queued','createdAt':int(time.time())}
            self.outbox.append(job);self.save_outbox()
            self.sent(text,None,client_id)
            self.show_outbox_job(job)
            self.message('Сообщение в очереди — выбранные настройки сохранены')
        except Exception as exc:
            self.sending=False
            self.draft_changed(self.text.get_buffer())
            self.message(str(exc))

    def save_outbox(self):
        path=DRAFT.parent/'outbox.json'
        temporary=path.with_suffix('.json.tmp')
        fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
        with os.fdopen(fd,'w') as stream:json.dump(self.outbox,stream,ensure_ascii=False)
        os.replace(temporary,path)
        self.refresh_outbox_view()

    def show_outbox_job(self,job):
        if self.provider!='codex' or job.get('host','')!=self.remote_host or job['threadId']!=self.thread_id:return
        ident='pending-'+job['id']
        self.add_item({'id':ident,'type':'userMessage','content':[{'type':'text','text':job['text']}]})
        self.pending_messages[job['id']]=ident
        message=self.messages[ident]
        if 'queue_status' not in message:
            label=Gtk.Label(xalign=0);label.set_line_wrap(True);label.set_max_width_chars(70)
            label.set_width_chars(1);label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
            label.get_style_context().add_class('thread-date')
            retry=self.button('view-refresh-symbolic','Повторить',lambda _,ident=job['id']:self.retry_outbox(ident),'quiet')
            message['frame'].get_child().pack_start(label,False,False,0)
            message['frame'].get_child().pack_start(retry,False,False,0)
            message['queue_status']=label;message['retry']=retry
        message['queue_status'].set_text(job.get('error') if job['status']=='error' else ('Отправляю' if job['status']=='sending' else 'В очереди')+' · '+(job.get('model') or 'Codex'))
        message['queue_status'].show()
        message['retry'].get_child().show_all()
        message['retry'].set_visible(job['status']=='error')

    def refresh_outbox_view(self):
        if not hasattr(self,'outbox_expander'):return
        signature=(self.remote_host,self.provider,json.dumps(self.outbox,sort_keys=True,ensure_ascii=False))
        if signature==self.outbox_view_signature:return
        self.outbox_view_signature=signature
        for child in self.outbox_list.get_children():child.destroy()
        self.outbox_expander.set_label(translator.text('Очередь')+' · '+str(len(self.outbox)))
        if not self.outbox:
            self.outbox_list.pack_start(Gtk.Label(label=translator.text('Нет ожидающих сообщений'),xalign=0),False,False,0)
        for job in self.outbox:
            row=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=3)
            title=Gtk.Label(xalign=0)
            state={'queued':'В очереди','sending':'Отправляю','error':'Ошибка','editing':'Редактирование'}.get(job['status'],job['status'])
            title.set_text(translator.text(state)+' · '+(job.get('host') or 'Steam Deck')+' · '+(job.get('error') or job['text']).replace('\n',' '))
            title.set_ellipsize(Pango.EllipsizeMode.END);title.set_max_width_chars(65)
            title.set_tooltip_text(job.get('error') or job['text'])
            row.pack_start(title,False,False,0)
            buttons=Gtk.Box(spacing=5)
            editable=job['status'] in ('queued','error')
            for label,callback in [('Изменить',self.edit_outbox),('Отменить',self.cancel_outbox),('Отправить сейчас',self.send_outbox_now)]:
                button=Gtk.Button(label=translator.text(label))
                button.connect('clicked',lambda _,ident=job['id'],action=callback:action(ident))
                enabled=editable
                if callback==self.send_outbox_now:
                    enabled=enabled and self.provider=='codex' and job.get('host','')==self.remote_host and not any(j['threadId']==job['threadId'] and j.get('host','')==job.get('host','') and j['status'] in ('sending','editing') for j in self.outbox)
                button.set_sensitive(enabled)
                buttons.pack_start(button,False,False,0)
            row.pack_start(buttons,False,False,0)
            self.outbox_list.pack_start(row,False,False,0)
        self.outbox_list.show_all()

    def remove_outbox_preview(self,job):
        ident=self.pending_messages.pop(job['id'],'pending-'+job['id'])
        message=self.messages.pop(ident,None)
        self.dirty_messages.discard(ident)
        if message:message['frame'].destroy()

    def cancel_outbox(self,ident):
        job=next((j for j in self.outbox if j['id']==ident),None)
        if not job or job['status'] not in ('queued','error'):return
        self.outbox.remove(job)
        self.remove_outbox_preview(job)
        self.save_outbox()
        self.message('Сообщение удалено из очереди')

    def edit_outbox(self,ident):
        job=next((j for j in self.outbox if j['id']==ident),None)
        if not job or job['status'] not in ('queued','error'):return
        previous=job['status'];job['status']='editing';self.save_outbox()
        dialog=Gtk.Dialog(title='Изменить сообщение',transient_for=self.window,modal=True)
        translator.watch_dialog(dialog)
        dialog.add_buttons('Назад',Gtk.ResponseType.CANCEL,'Сохранить',Gtk.ResponseType.OK)
        dialog.set_default_size(560,280)
        editor=Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD_CHAR)
        editor.get_buffer().set_text(job['text'])
        scroll=Gtk.ScrolledWindow();scroll.add(editor)
        dialog.get_content_area().pack_start(scroll,True,True,8)
        dialog.show_all()
        try:
            response=dialog.run()
            buffer=editor.get_buffer()
            text=clean_text(buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter(),False))
            if response==Gtk.ResponseType.OK and text:
                job['text']=text;job.pop('error',None);previous='queued'
                self.remove_outbox_preview(job)
        finally:
            dialog.destroy();job['status']=previous
            self.save_outbox();self.show_outbox_job(job)

    def send_outbox_now(self,ident):
        job=next((j for j in self.outbox if j['id']==ident),None)
        if not job or job['status'] not in ('queued','error'):return
        if self.provider!='codex' or job.get('host','')!=self.remote_host or not self.backend or not self.backend.connected or not self.history_ready:
            self.message('Подключитесь к устройству этого сообщения');return
        if any(j is not job and j['threadId']==job['threadId'] and j.get('host','')==self.remote_host and j['status'] in ('sending','editing') for j in self.outbox):return
        job['status']='sending';job.pop('error',None)
        self.save_outbox();self.show_outbox_job(job)
        threading.Thread(target=self.deliver_job,args=(job,True),daemon=True).start()

    def retry_outbox(self,ident):
        job=next((j for j in self.outbox if j['id']==ident),None)
        if not job:return
        job.update({'status':'queued','error':None,'model':self.model_picker.get_active_id(),'effort':self.effort_picker.get_active_id(),'tier':self.speed_picker.get_active_id() or 'default'})
        self.save_outbox();self.show_outbox_job(job)

    def pump_outbox(self):
        if updates.updating(STATE_DIR):return True
        self.refresh_outbox_view()
        if self.provider!='codex':return True
        if not self.backend or not self.backend.connected or not self.history_ready:return True
        active={j['threadId'] for j in self.outbox if j.get('host','')==self.remote_host and j.get('status') in ('sending','editing')}
        for job in self.outbox:
            if job.get('status')!='queued' or job.get('host','')!=self.remote_host or job['threadId'] in active or self.thread_activity.get(job['threadId']) is True:continue
            job['status']='sending';active.add(job['threadId'])
            self.show_outbox_job(job);self.save_outbox()
            threading.Thread(target=self.deliver_job,args=(job,),daemon=True).start()
        return True

    @staticmethod
    def is_thread_busy(error):
        text=str(error).lower()
        return any(phrase in text for phrase in ['already has an active turn','turn is already in progress','turn is in progress','another turn is active','thread is busy','turn already running'])

    def deliver_job(self,job,send_now=False):
        try:
            tid=job['threadId']
            if send_now and tid not in self.empty_threads:
                _,thread=self.backend.select_thread(tid)
                turn=next((t for t in reversed(thread.get('turns',[])) if t.get('status')=='inProgress'),None)
                if turn:
                    self.backend.request('turn/steer',{'threadId':tid,'expectedTurnId':turn['id'],'clientUserMessageId':job['id'],'input':[{'type':'text','text':job['text'],'text_elements':[]}]})
                    GLib.idle_add(self.job_finished,job,None)
                    return
            if tid in self.empty_threads:
                start={'cwd':self.backend.cwd if self.remote_host else str(Path.home()),'ephemeral':False}
                if job.get('model'):start['model']=job['model']
                result=self.backend.request('thread/start',start)
                done=threading.Event()
                GLib.idle_add(self.promote_empty_thread,tid,result,done)
                if not done.wait(15):raise RpcError('Не удалось открыть новый чат.')
                tid=job['threadId']
            else:
                _,thread=self.backend.select_thread(tid)
                busy=any(turn.get('status')=='inProgress' for turn in thread.get('turns',[]))
                if busy:GLib.idle_add(self.job_waiting,job,True);return
            params={'threadId':tid,'input':[{'type':'text','text':job['text'],'text_elements':[]}],'clientUserMessageId':job['id'],'serviceTier':job.get('tier') or 'default'}
            if job.get('model'):params['model']=job['model']
            if job.get('effort'):params['effort']=job['effort']
            self.backend.request('turn/start',params)
            GLib.idle_add(self.job_finished,job,None)
        except Exception as exc:
            if self.is_thread_busy(exc):GLib.idle_add(self.job_waiting,job,True)
            else:GLib.idle_add(self.job_finished,job,str(exc))

    def job_waiting(self,job,busy):
        job['status']='queued';self.thread_activity[job['threadId']]=busy
        self.save_outbox();self.show_outbox_job(job)

    def job_finished(self,job,error):
        if error:
            job['status']='error';job['error']='Codex: '+error
            self.show_outbox_job(job)
            if job['threadId']==self.thread_id:self.activity.set_text('Отправка не удалась. Причина показана под сообщением.')
        else:
            self.outbox=[j for j in self.outbox if j['id']!=job['id']]
            self.empty_threads.pop(job['threadId'],None);self.save_empty_threads()
            if job['threadId']==self.thread_id:
                self.current_model=job.get('model');self.current_effort=job.get('effort');self.current_tier=job.get('tier')
                pending=self.messages.get('pending-'+job['id'])
                if pending and 'queue_status' in pending:pending['queue_status'].hide();pending['retry'].hide()
        self.save_outbox()

    def sent(self, sent_text, error, client_id=None):
        self.sending = False
        buffer = self.text.get_buffer()
        current = clean_text(buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False))
        if not error and current == sent_text: buffer.set_text('')
        if error and client_id in self.pending_messages:
            ident=self.pending_messages.pop(client_id)
            pending=self.messages.pop(ident,None)
            if pending:pending['frame'].destroy()
        self.draft_changed(buffer)
        self.message(error or 'Сообщение передано в Codex')

    def close(self, *_):
        if self.gaming_mode:
            self.shutdown_app()
            return True
        self.stop_event.set()
        if self.recorder is not None and self.recorder.poll() is None:
            self.recorder.terminate()
        self.window.hide()
        return True

    def update_is_busy(self):
        modal=any(w is not self.window and w.get_visible() and w.get_modal() and not getattr(w,'_deck_ai_update_dialog',False) for w in Gtk.Window.list_toplevels()) if hasattr(self,'window') else False
        return bool(self.busy or self.sending or self.engine_active or modal or any(j.get('status') in ('queued','sending','recovering','editing') for j in self.outbox))

    def publish_update_activity(self):
        if not hasattr(self,'update_lease'):return
        try:self.update_lease.publish(self.update_is_busy())
        except OSError:pass

    def show_updates(self,*_):
        if not self.update_controller:self.message(translator.text('Проверка обновлений недоступна'));return
        import update_ui
        def begin(value):
            self.publish_update_activity()
            return self.update_controller.begin(value,restart_app=True,guard=self.update_is_busy)
        return update_ui.show(self.window,self.update_controller,begin)

    def poll_updates(self):
        if getattr(self,'closed',None) is not None and self.closed.is_set():return False
        self.publish_update_activity()
        job=updates.active_job(STATE_DIR)
        if job.get('phase')=='quiescing' and not self.update_is_busy():
            if self.save_draft(self.text.get_buffer()) is False:
                self.update_lease.publish(True);return True
            self.shutdown_app();return False
        if self.update_controller:
            try:
                value=self.update_controller.status()
                if value.get('notificationPending') and value['preferences']['automatic'] and self.window.get_visible() and not self.gaming_mode:
                    available=value['available'];notice=Gio.Notification.new(translator.text('Доступно обновление Deck AI'))
                    notice.set_body(available['version']);notice.set_default_action('app.updates');self.send_notification('deck-ai-update',notice);self.update_controller.acknowledge(available['version'])
            except Exception:pass
        return True

    def shutdown_app(self):
        self.stop_speaking()
        if self.language_settings is not None:self.language_settings.cancel.set()
        if hasattr(self,'closed'):self.closed.set()
        self.stop_event.set()
        if self.recorder is not None and self.recorder.poll() is None:self.recorder.terminate()
        if self.backend:self.backend.close()
        if hasattr(self,'update_lease'):self.update_lease.close()
        if getattr(self,'update_controller',None):self.update_controller.close()
        self.quit()

if __name__ == '__main__':
    Panel().run(None)
