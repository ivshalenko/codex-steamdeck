#!/usr/bin/env python3
"""Source embedded verbatim in the downloadable desktop launcher by build-release.py."""
import base64
import os
import threading
import shutil
import hashlib
import http.client
import ssl
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
import urllib.parse
from pathlib import Path
from updates import release_response
VERSION='@VERSION@'
BASE='https://github.com/ivshalenko/codex-steamdeck/releases/download/v'+VERSION+'/'
BANNER_SVG='@INSTALLER_BANNER@'
BUNDLED_ARCHIVE_SHA256='@BUNDLED_ARCHIVE_SHA256@'
DOWNLOAD_PROGRESS=None
def download(name, destination, limit):
    destination = Path(destination)
    temporary = destination.with_name(destination.name + ".part")
    for attempt in range(3):
        print("Downloading " + name, flush=True)
        try:
            with release_response(BASE + name, timeout=25) as response, temporary.open("wb") as out:
                expected = response.headers.get("Content-Length")
                expected = int(expected) if expected and expected.isdecimal() else None
                if expected is not None and expected > limit:
                    raise ValueError("Unexpected download size")
                size = 0
                checksum = hashlib.sha256()
                while block := response.read(256 * 1024):
                    size += len(block)
                    if size > limit:
                        raise ValueError("Unexpected download size")
                    out.write(block); checksum.update(block)
                    if DOWNLOAD_PROGRESS:DOWNLOAD_PROGRESS(name,size,expected)
                if expected is not None and size != expected:
                    raise http.client.IncompleteRead(b"", expected - size)
                if getattr(response,'deck_asset_digest',None) and checksum.hexdigest()!=response.deck_asset_digest:
                    raise ValueError('GitHub asset checksum mismatch. Nothing was installed.')
            temporary.replace(destination)
            return
        except urllib.error.HTTPError as error:
            if attempt == 2 or error.code not in (408, 429, 500, 502, 503, 504):
                raise
        except urllib.error.URLError as error:
            if attempt == 2 or isinstance(error.reason, ssl.SSLCertVerificationError):
                raise
        except (TimeoutError, ConnectionError, http.client.IncompleteRead):
            if attempt == 2:
                raise
        finally:
            temporary.unlink(missing_ok=True)
        print("Download interrupted. Retrying…", flush=True)
        time.sleep(attempt + 1)
def unpack(archive, destination):
    with tarfile.open(archive) as tar:
        members = []
        paths = set()
        total = 0
        for member in tar:
            path = Path(member.name)
            if (path.is_absolute() or ".." in path.parts or not path.parts
                    or path.parts[0] != "deck-ai-" + VERSION or path in paths
                    or not (member.isfile() or member.isdir())):
                raise ValueError("Unsafe release archive")
            total += member.size
            if total > 200_000_000 or len(members) >= 10000:
                raise ValueError("Unexpected extracted size")
            members.append(member)
            paths.add(path)
        options = {"filter": "data"} if sys.version_info >= (3, 12) else {}
        tar.extractall(destination, members=members, **options)
def prepare(root,launcher=None):
 root=Path(root);name='deck-ai-'+VERSION+'-steamdeck.tar.gz';archive=root/name
 bundled=BUNDLED_ARCHIVE_SHA256 and not BUNDLED_ARCHIVE_SHA256.startswith('@')
 if bundled:
  location=launcher if launcher is not None else sys.argv[1] if len(sys.argv)>1 else ''
  if not location:raise ValueError('Extract the ZIP first, then open Install Deck AI inside the extracted folder. / Сначала распакуйте ZIP и запустите Install Deck AI из распакованной папки.')
  parsed=urllib.parse.urlsplit(str(location))
  if parsed.scheme:
   if parsed.scheme!='file' or parsed.netloc not in ('','localhost'):raise ValueError('Open the extracted installer from Dolphin.')
   location=urllib.request.url2pathname(parsed.path)
  archive=Path(location).resolve().parent/name
  if archive.is_symlink() or not archive.is_file() or not 0<archive.stat().st_size<=100_000_000:
   raise ValueError('Extract all ZIP contents together before opening Install Deck AI. / Распакуйте ZIP целиком перед запуском Install Deck AI.')
  expected=BUNDLED_ARCHIVE_SHA256
 else:
  download('SHA256SUMS.txt',root/'SHA256SUMS.txt',100_000);download(name,archive,100_000_000)
  sums={line.split('  ',1)[1]:line.split('  ',1)[0] for line in (root/'SHA256SUMS.txt').read_text().splitlines()};expected=sums.get(name)
 if hashlib.sha256(archive.read_bytes()).hexdigest()!=expected:raise ValueError('Release checksum mismatch. Please download again.')
 unpack(archive,root);return root/('deck-ai-'+VERSION)
def graphical_setup():
    import gi
    gi.require_version('Gtk','3.0')
    from gi.repository import Gtk,GLib,GdkPixbuf
    class DownloadWindow(Gtk.Window):
        def __init__(self):
            super().__init__(title='Deck AI · Download')
            self.language='en';self.busy=False;self.closed=False
            self.set_default_size(800,420);self.set_border_width(20);self.set_position(Gtk.WindowPosition.CENTER)
            self.connect('delete-event',self.close)
            box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=14);self.add(box)
            try:
                loader=GdkPixbuf.PixbufLoader.new_with_type('svg');loader.set_size(760,133)
                loader.write(base64.b64decode(BANNER_SVG));loader.close();box.pack_start(Gtk.Image.new_from_pixbuf(loader.get_pixbuf()),False,False,0)
            except Exception:box.pack_start(Gtk.Label(label='Deck AI'),False,False,0)
            self.heading=Gtk.Label(xalign=0);self.heading.set_markup('<big><b>Preparing your installer</b></big>');box.pack_start(self.heading,False,False,0)
            self.combo=Gtk.ComboBoxText();self.combo.append('en','English');self.combo.append('ru','Русский');self.combo.set_active_id('en');self.combo.connect('changed',self.change_language);box.pack_start(self.combo,False,False,0)
            self.note=Gtk.Label(xalign=0);self.note.set_line_wrap(True);box.pack_start(self.note,False,False,0)
            self.progress=Gtk.ProgressBar();self.progress.set_show_text(True);box.pack_start(self.progress,False,False,0)
            self.error=Gtk.Label(xalign=0);self.error.set_line_wrap(True);self.error.set_selectable(True);box.pack_start(self.error,True,True,0)
            actions=Gtk.Box(spacing=10);box.pack_start(actions,False,False,0)
            self.guide=Gtk.LinkButton.new_with_label('https://github.com/ivshalenko/codex-steamdeck/blob/main/docs/QUICKSTART.md','Installation guide');actions.pack_start(self.guide,True,True,0)
            self.cancel=Gtk.Button();self.cancel.connect('clicked',self.close);actions.pack_end(self.cancel,False,False,0)
            self.retry=Gtk.Button();self.retry.connect('clicked',self.start);actions.pack_end(self.retry,False,False,0)
            self.change_language();self.show_all();self.retry.hide();GLib.timeout_add(200,self.start)
        def t(self,en,ru):return ru if self.language=='ru' else en
        def change_language(self,*_):
            self.language=self.combo.get_active_id() or 'en'
            self.set_title(self.t('Deck AI · Download','Deck AI · Загрузка'))
            self.guide.set_label(self.t('Installation guide','Инструкция установки'))
            self.guide.set_uri('https://github.com/ivshalenko/codex-steamdeck/blob/main/docs/'+('QUICKSTART.ru.md' if self.language=='ru' else 'QUICKSTART.md'))
            self.cancel.set_label(self.t('Cancel','Отмена'))
            self.heading.set_markup('<big><b>'+self.t('Preparing your installer','Подготовка установщика')+'</b></big>')
            self.note.set_text(self.t('Downloading and checking the release. Choose a language now; the full installer will keep it. Nothing is installed until you choose Install.','Загружаем и проверяем выпуск. Выберите язык — полный установщик сохранит выбор. Установка начнётся только после нажатия «Установить».'))
            self.retry.set_label(self.t('Retry download','Повторить загрузку'))
        def notify(self,name,size,total):
            if self.closed:raise RuntimeError('Download cancelled.')
            def update():
                if self.closed:return False
                if total:self.progress.set_fraction(min(.95,size/total))
                else:self.progress.pulse()
                self.progress.set_text(self.t('Downloading: ','Загрузка: ')+f'{size/1048576:.1f} MB');return False
            GLib.idle_add(update)
        def start(self,*_):
            if self.busy or self.closed:return False
            self.busy=True;self.retry.hide();self.error.set_text('')
            threading.Thread(target=self.download,daemon=True).start();return False
        def download(self):
            global DOWNLOAD_PROGRESS
            DOWNLOAD_PROGRESS=self.notify
            try:
                with tempfile.TemporaryDirectory(prefix='deck-ai-setup-') as directory:
                    source=prepare(directory)
                    if self.closed:return
                    launch=threading.Event();selection=[]
                    def handoff():
                        if self.closed:return False
                        selection.append(self.language);self.hide();launch.set();return False
                    GLib.idle_add(handoff)
                    if not launch.wait(15) or self.closed:return
                    subprocess.run([sys.executable,str(source/'scripts/setup.py'),'--language',selection[0]],cwd=source,check=True)
                GLib.idle_add(Gtk.main_quit)
            except Exception as exc:
                message=str(exc)
                def failure():
                    if self.closed:return False
                    self.busy=False;self.show();self.error.set_text(self.t('Download or setup stopped. Retry, or see the installation guide. Details: ','Загрузка или установка остановлена. Повторите попытку или откройте инструкцию. Подробности: ')+message);self.retry.show();return False
                GLib.idle_add(failure)
            finally:DOWNLOAD_PROGRESS=None
        def close(self,*_):self.closed=True;self.destroy();Gtk.main_quit();return False
    DownloadWindow();Gtk.main()

if __name__=='__main__':
    try:
        if sys.platform!='linux':raise ValueError('Run this installer on Steam Deck in Desktop Mode. For Mac/PC download Remote Control instead.')
        if BUNDLED_ARCHIVE_SHA256 and not BUNDLED_ARCHIVE_SHA256.startswith('@'):
            with tempfile.TemporaryDirectory(prefix='deck-ai-setup-') as directory:
                source=prepare(directory)
                location=urllib.parse.urlsplit(sys.argv[1]);launcher=urllib.request.url2pathname(location.path) if location.scheme=='file' else sys.argv[1]
                bundle=Path(launcher).resolve().parent/'codex'
                subprocess.run([sys.executable,str(source/'scripts/setup.py')],cwd=source,check=True,env={**os.environ,'DECK_AI_CODEX_BUNDLE_DIR':str(bundle)})
        else:graphical_setup()
    except Exception as exc:
        message='Setup stopped: '+str(exc)+'\nHelp: https://github.com/ivshalenko/codex-steamdeck/blob/main/docs/QUICKSTART.md'
        print(message,flush=True)
        if shutil.which('kdialog'):subprocess.run(['kdialog','--error',message])
        elif shutil.which('zenity'):subprocess.run(['zenity','--error','--text',message])
        sys.exit(1)
