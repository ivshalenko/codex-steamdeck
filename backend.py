"""JSON-RPC client for the local Codex daemon. No terminal or API key needed."""
import json
import os
from pathlib import Path
import subprocess
import threading
import uuid
import shlex
import shutil
import re

def clean_subprocess_environment(environ=None):
    """Keep Decky's frozen-process libraries out of normal child programs."""
    env = dict(os.environ if environ is None else environ)
    frozen = any(name.startswith('_PYI_') for name in env) or env.get('LD_LIBRARY_PATH', '').startswith('/tmp/_MEI')
    if frozen:
        original = env.pop('LD_LIBRARY_PATH_ORIG', None)
        env.pop('LD_LIBRARY_PATH', None)
        if original:
            env['LD_LIBRARY_PATH'] = original
        for name in tuple(env):
            if name.startswith('_PYI_') or name == '_MEIPASS2':
                env.pop(name, None)
    return env

def find_codex():
    for candidate in (shutil.which('codex'), Path.home()/'.local/bin/codex',
                      Path.home()/'.npm-global/bin/codex', '/opt/homebrew/bin/codex',
                      '/usr/local/bin/codex', '/Applications/Codex.app/Contents/Resources/codex'):
        if candidate and os.access(candidate, os.X_OK):
            return str(candidate)
    return str(Path.home()/'.local/bin/codex')


CODEX = find_codex()

# Non-interactive SSH sessions often don't inherit the npm/Homebrew PATH.
_REMOTE_CODEX = r'''
PATH="$HOME/.local/bin:$HOME/.npm-global/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
export PATH
if ! command -v codex >/dev/null 2>&1; then
    if [ -x /Applications/Codex.app/Contents/Resources/codex ]; then
        codex() { /Applications/Codex.app/Contents/Resources/codex "$@"; }
    else
        echo 'Codex CLI not found. Install Codex on this SSH host.' >&2
        exit 127
    fi
fi
'''
# The daemon socket speaks WebSocket, whereas SSH clients exchange JSONL.
# `codex app-server proxy` forwards raw bytes; it isn't a JSONL adapter.
_REMOTE_JSONL_PROXY = r'''
import os, sys, threading
from pathlib import Path
from websockets.sync.client import unix_connect
home = Path(os.environ.get('CODEX_HOME') or Path.home()/'.codex').expanduser()
with unix_connect(str(home/'app-server-control/app-server-control.sock'), uri='ws://localhost/', open_timeout=10, max_size=32*1024*1024) as ws:
    def forward_input():
        try:
            for line in sys.stdin:
                ws.send(line.rstrip('\n'))
        finally:
            ws.close()
    threading.Thread(target=forward_input, daemon=True).start()
    for message in ws:
        print(message, flush=True)
'''
_REMOTE_SERVER = _REMOTE_CODEX + r'''
# Reuse a remote companion's Python environment when it is installed.
if codex app-server proxy --help >/dev/null 2>&1 &&
   codex app-server daemon start >/dev/null 2>&1; then
    for python in "$HOME/.local/share/deck-ai/venv/bin/python" "$HOME/.local/share/deck-voice/venv/bin/python" python3; do
        if "$python" -c 'from websockets.sync.client import unix_connect' >/dev/null 2>&1; then
            exec "$python" -u -c ''' + shlex.quote(_REMOTE_JSONL_PROXY) + r'''
        fi
    done
fi
# Older installations still share persisted chats through the stdio server.
codex app-server --listen stdio://
'''


def valid_ssh_host(host):
    return isinstance(host, str) and bool(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.@-]{0,119}', host))


def ssh_command(host, *remote, connect_timeout=8):
    """Build an ssh argv that shares one connection per host.

    ControlMaster multiplexing turns the repeated probe, app-server and queue
    calls into one TCP/auth handshake, and keepalives detect a sleeping or
    unreachable remote computer in ~45s instead of hanging indefinitely.
    """
    if not valid_ssh_host(host):
        raise ValueError('Укажите SSH-алиас без пробелов и параметров командной строки.')
    control_dir = Path.home()/'.ssh'
    args = [shutil.which('ssh') or '/usr/bin/ssh', '-T', '-o', 'BatchMode=yes', '-o', f'ConnectTimeout={connect_timeout}',
            '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=3']
    if os.name!='nt' and control_dir.is_dir():
        # %C is a short hash, which keeps the socket path under the unix limit.
        args += ['-o', 'ControlMaster=auto', '-o', f'ControlPath={control_dir}/deck-ai-%C', '-o', 'ControlPersist=600']
    return [*args, '--', host, *remote]

class RpcError(RuntimeError):
    def __init__(self,message,code=None,data=None):
        super().__init__(message)
        self.code=code
        self.data=data

class Backend:
    def __init__(self, event, disconnected, remote_host=''):
        self.event = event
        self.disconnected = disconnected
        self.ws = None
        self.connected = False
        self.pending = {}
        self.lock = threading.Lock()
        # Requests can originate from UI actions and background refreshes at
        # the same time. Serialize writes so JSONL frames never interleave.
        self.write_lock = threading.Lock()
        self.next_id = 0
        self.remote_host = remote_host
        self.process = None
        self.cwd = str(Path.home())

    def _start_process(self, command):
        self.process = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding='utf-8', errors='replace', bufsize=1,
            env={**clean_subprocess_environment(), 'TERM': 'dumb'})
        self.ws = self
        self.stderr_tail = ''
        def drain(process):
            for line in process.stderr:
                self.stderr_tail = (self.stderr_tail + line)[-1600:]
        self.stderr_reader = threading.Thread(target=drain, args=(self.process,), daemon=True)
        self.stderr_reader.start()

    def connect(self, thread_id=None):
        if self.connected:
            return self.select_thread(thread_id) if thread_id else ({}, {})
        self.closing = False
        self.stderr_tail = ''
        try:
            if self.remote_host:
                probe = subprocess.run(ssh_command(self.remote_host, 'pwd'), capture_output=True,
                                       text=True, encoding='utf-8', timeout=12)
                if probe.returncode:
                    raise RpcError('SSH не подключился. Проверьте алиас, ключ и known_hosts в ~/.ssh. '
                                   + probe.stderr.strip()[-500:])
                self.cwd = probe.stdout.strip()
                if not self.cwd.startswith('/') or '\n' in self.cwd:
                    raise RpcError('SSH вернул неверную домашнюю папку. Уберите вывод из shell startup файлов.')
                self._start_process(ssh_command(self.remote_host, _REMOTE_SERVER))
            else:
                if not os.access(CODEX,os.X_OK):raise RpcError('Codex CLI не установлен. В Desktop Mode запустите Install Deck AI и выберите установку Codex; затем войдите в ChatGPT в настройках.')
                # Prefer the shared daemon; older official CLIs also work over stdio.
                codex_home = Path(os.environ.get('CODEX_HOME') or Path.home()/'.codex').expanduser()
                path = str(codex_home/'app-server-control/app-server-control.sock')
                try:
                    from websockets.sync.client import unix_connect
                    try:
                        self.ws = unix_connect(path, uri='ws://localhost/', open_timeout=5, max_size=32*1024*1024)
                    except (OSError, TimeoutError):
                        subprocess.run([CODEX, 'app-server', 'daemon', 'start'], check=True,
                                       capture_output=True, timeout=40, env=clean_subprocess_environment())
                        self.ws = unix_connect(path, uri='ws://localhost/', open_timeout=10, max_size=32*1024*1024)
                except (ImportError, OSError, TimeoutError, subprocess.SubprocessError):
                    self._start_process([CODEX, 'app-server', '--listen', 'stdio://'])
            self.connected = True
            self.reader = threading.Thread(target=self.read, daemon=True)
            self.reader.start()
            self.request('initialize', {'clientInfo': {'name':'deck_voice','title':'Codex для Steam Deck','version':'2.0'},
                                        'capabilities': {'experimentalApi':True}})
            self.notify('initialized')
            result = self.select_thread(thread_id) if thread_id else ({}, {})
            if self.remote_host:
                threading.Thread(target=self.cleanup_uploads, daemon=True).start()
            return result
        except Exception:
            self.close()
            raise

    def close(self):
        """Close our transport, without stopping the shared Codex daemon."""
        self.closing = True
        self.connected = False
        process = self.process
        if process:
            try:
                if process.poll() is None:
                    process.terminate()
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
            for worker in (getattr(self, 'reader', None), getattr(self, 'stderr_reader', None)):
                if worker and worker is not threading.current_thread():
                    worker.join(timeout=2)
            for stream in (process.stdin, process.stdout, process.stderr):
                if stream:
                    stream.close()
        elif self.ws and self.ws is not self:
            self.ws.close()
        self._fail_pending()

    def _fail_pending(self):
        with self.lock:
            for pending in self.pending.values():
                if not pending['done'].is_set():
                    detail = getattr(self, 'stderr_tail', '').strip()[-700:]
                    pending['reply'] = {'error': {'message': 'Соединение с Codex прервано' + (': ' + detail if detail else '')}}
                    pending['done'].set()

    def select_thread(self, thread_id):
        # Both transports must load the thread into the server handling turn/start.
        result = self.request('thread/resume', {'threadId':thread_id,'excludeTurns':True}, timeout=50)
        history = self.request('thread/read', {'threadId':thread_id,'includeTurns':True}, timeout=30)
        return result, history['thread']

    def queue_message(self, thread_id, text, model=None, effort=None, tier='default'):
        if not self.remote_host:raise RpcError('SSH-очередь доступна только для удалённого компьютера.')
        command=['codex','queue','--thread',thread_id,'--message',text]
        if model:command += ['--model',model]
        if effort:command += ['-c',f'model_reasoning_effort={effort}']
        if tier=='priority':command += ['-c','service_tier="priority"']
        remote_command=_REMOTE_CODEX + '\n' + ' '.join(shlex.quote(part) for part in command)
        result=subprocess.run(ssh_command(self.remote_host,remote_command),capture_output=True,text=True,timeout=45)
        if result.returncode:
            raise RpcError((result.stderr or result.stdout or 'Не удалось поставить запрос в очередь Codex на удалённом компьютере.')[-1200:])
        return {'queued':True,'output':result.stdout.strip()}

    def cleanup_uploads(self, days=7):
        """Best effort: remove screenshots sent to the remote computer a week ago."""
        try:
            subprocess.run(ssh_command(self.remote_host, f'find "$HOME/.cache/deck-ai-uploads" -type f -mtime +{int(days)} -delete 2>/dev/null; true'), capture_output=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            pass

    def upload_file(self, local_path):
        """Copy a local image to the remote computer over the shared SSH connection."""
        if not self.remote_host:raise RpcError('Загрузка нужна только для удалённого компьютера.')
        suffix=Path(local_path).suffix.lower()
        if suffix not in ('.png','.jpg','.jpeg','.webp'):raise RpcError('Можно передавать только изображения.')
        name=f'{uuid.uuid4().hex}{suffix}'
        script=f'd="$HOME/.cache/deck-ai-uploads"; mkdir -p "$d" && cat > "$d/{name}" && printf %s "$d/{name}"'
        with open(local_path,'rb') as source:
            result=subprocess.run(ssh_command(self.remote_host,script),stdin=source,capture_output=True,timeout=90)
        if result.returncode or not result.stdout:
            raise RpcError((result.stderr or b'').decode(errors='replace')[-600:] or 'Не удалось передать изображение на удалённый компьютер.')
        return result.stdout.decode().strip()

    def read(self):
        try:
            source = self.process.stdout if self.process else self.ws
            for raw in source:
                try:
                    message = json.loads(raw)
                except (ValueError, TypeError):
                    continue
                if not isinstance(message, dict):
                    continue
                if 'method' in message:
                    try:
                        self.event(message)
                    except Exception:
                        # A UI callback must not kill the RPC response reader.
                        continue
                elif 'id' in message:
                    with self.lock:
                        pending = self.pending.get(message['id'])
                        if pending:
                            pending['reply'] = message
                            pending['done'].set()
        except Exception:
            pass
        finally:
            self.connected = False
            self._fail_pending()
            if not getattr(self, 'closing', False):
                self.disconnected()

    def request(self, method, params, timeout=25):
        if not self.connected:
            raise RpcError('Нет соединения с Codex.')
        with self.lock:
            self.next_id += 1
            ident = self.next_id
            pending = {'done':threading.Event()}
            self.pending[ident] = pending
        try:
            payload=json.dumps({'id':ident,'method':method,'params':params})
            with self.write_lock:
                if self.process:
                    self.process.stdin.write(payload+'\n');self.process.stdin.flush()
                else:self.ws.send(payload)
            if not pending['done'].wait(timeout):
                raise RpcError('Codex не ответил вовремя. Попробуйте ещё раз.')
            reply = pending['reply']
            if 'error' in reply:
                error=reply['error']
                raise RpcError(error.get('message','Ошибка Codex'),error.get('code'),error.get('data'))
            return reply.get('result',{})
        finally:
            with self.lock: self.pending.pop(ident,None)

    def notify(self, method):
        payload=json.dumps({'method':method})
        with self.write_lock:
            if self.process:self.process.stdin.write(payload+'\n');self.process.stdin.flush()
            else:self.ws.send(payload)

    def respond(self, ident, result=None, error=None):
        value = {'id':ident}
        if error is not None: value['error'] = error
        else: value['result'] = result
        payload=json.dumps(value)
        with self.write_lock:
            if self.process:self.process.stdin.write(payload+'\n');self.process.stdin.flush()
            else:self.ws.send(payload)


# --- Device files: view and edit small text files on this device or over SSH ---
MAX_FILE_BYTES = 64 * 1024
PROTECTED_PARTS = {'.ssh', '.gnupg', '.aws', '.kube', '.password-store'}
PROTECTED_NAMES = ('auth.json', 'id_rsa', 'id_ed25519', 'known_hosts', 'credentials')

# Run on the remote side with the path as $1; stdout carries the result.
_SH_GUARD = r'''
d=$(dirname -- "$1"); b=$(basename -- "$1")
p=$(cd -- "$d" 2>/dev/null && pwd -P) || exit 3
f="$p/$b"
[ ! -L "$f" ] || exit 4
case "$f" in "$HOME"|"$HOME"/*) ;; *) exit 4 ;; esac
case "$f" in */.ssh/*|*/.gnupg/*|*/.aws/*|*/.kube/*|*/.password-store/*) exit 4 ;; esac
'''
_SH_LIST = r'''
[ "$1" = "~" ] && set -- "$HOME"
p=$(cd -- "$1" 2>/dev/null && pwd -P) || exit 3
case "$p" in "$HOME"|"$HOME"/*) ;; *) exit 4 ;; esac
case "$p/" in */.ssh/*|*/.gnupg/*|*/.aws/*|*/.kube/*|*/.password-store/*) exit 4 ;; esac
printf '%s\n' "$p"; ls -1Ap -- "$p" | head -300
'''
_SH_READ = _SH_GUARD + r'''
[ -f "$f" ] || exit 5
[ "$(wc -c < "$f")" -le 65536 ] || exit 6
cat -- "$f"
'''
_SH_WRITE_BODY = _SH_GUARD + r'''
set -e
[ -f "$f" ] || exit 5
[ ! -L "$f.deckai.bak" ] || exit 4
[ "$(wc -c < "$f")" -le 65536 ] || exit 6
if command -v sha256sum >/dev/null 2>&1; then
    checksum() { sha256sum -- "$f"; }
elif command -v shasum >/dev/null 2>&1; then
    checksum() { shasum -a 256 -- "$f"; }
else
    exit 10
fi
sum=$(checksum)
[ "${sum%% *}" = "$2" ] || exit 8
new=$(mktemp "$p/.deckai-write.XXXXXX")
saved=""
trap 'rm -f -- "$new" "$saved"' 0
trap 'exit 1' 1 2 15
saved=$(mktemp "$p/.deckai-backup.XXXXXX")
cp -p -- "$f" "$new"
cat > "$new"
sum=$(checksum)
[ "${sum%% *}" = "$2" ] || exit 8
cp -p -- "$f" "$saved"
mv -f -- "$saved" "$f.deckai.bak"
mv -f -- "$new" "$f"
'''
_SH_WRITE = _SH_GUARD + r'''
umask 077
lock="$p/.$b.deckai.lock"
[ ! -L "$lock" ] || exit 4
[ ! -e "$lock" ] || [ -f "$lock" ] || exit 4
if command -v flock >/dev/null 2>&1; then
    exec flock -n -E 7 "$lock" sh -c ''' + shlex.quote(_SH_WRITE_BODY) + r''' sh "$f" "$2"
elif command -v lockf >/dev/null 2>&1; then
    exec lockf -k -s -t 0 "$lock" sh -c ''' + shlex.quote(_SH_WRITE_BODY) + r''' sh "$f" "$2"
else
    exit 10
fi
'''

_FILE_ERRORS = {3: 'Папка или файл не найдены.', 4: 'Доступ закрыт: только домашняя папка, без ключей и секретов.',
                5: 'Это не обычный файл.', 6: 'Файл больше 64 КБ.',
                7: 'Файл сейчас сохраняется. Дождитесь завершения и откройте его заново.',
                75: 'Файл сейчас сохраняется. Дождитесь завершения и откройте его заново.',
                8: 'Файл изменился на устройстве. Откройте его заново, чтобы не потерять чужие правки.',
                10: 'Для сохранения на этом устройстве нужны flock или lockf и SHA-256.'}


def _check_name(path):
    parts = Path(path).parts
    name = Path(path).name.lower()
    if '\0' in path or '\n' in path:
        raise RpcError('Недопустимый путь.')
    if any(part in PROTECTED_PARTS for part in parts) or name.startswith('.env') or name in PROTECTED_NAMES:
        raise RpcError(_FILE_ERRORS[4])


def _remote_sh(host, script, path, data=None, timeout=30, expected_sha256=None):
    command = 'sh -c ' + shlex.quote(script) + ' sh ' + shlex.quote(path)
    if expected_sha256 is not None:
        command += ' ' + shlex.quote(expected_sha256)
    result = subprocess.run(ssh_command(host, command), input=data, capture_output=True, timeout=timeout)
    if result.returncode:
        raise RpcError(_FILE_ERRORS.get(result.returncode) or (result.stderr.decode(errors='replace')[-300:] or 'Не удалось выполнить операцию на устройстве.'))
    return result.stdout


def _local_checked(path, must_exist=True):
    home = Path.home().resolve()
    target = Path(path).expanduser().resolve()
    if target != home and not target.is_relative_to(home):
        raise RpcError(_FILE_ERRORS[4])
    _check_name(str(target))
    if any(part in PROTECTED_PARTS for part in target.parts):
        raise RpcError(_FILE_ERRORS[4])
    if must_exist and not target.exists():
        raise RpcError(_FILE_ERRORS[3])
    return target


def list_files(host, path):
    """Return (resolved folder, entries); entries ending in '/' are folders."""
    path = path or '~'
    if host:
        out = _remote_sh(host, _SH_LIST, path).decode(errors='replace').splitlines()
        return (out[0] if out else ''), [line for line in out[1:] if line]
    _check_name(path)
    folder = _local_checked(path)
    if not folder.is_dir():
        raise RpcError(_FILE_ERRORS[3])
    names = sorted(((child.name + '/') if child.is_dir() else child.name) for child in folder.iterdir()
                   if child.name not in PROTECTED_PARTS)[:300]
    return str(folder), names


def read_file(host, path):
    _check_name(path)
    if host:
        raw = _remote_sh(host, _SH_READ, path)
    else:
        target = _local_checked(path)
        if not target.is_file():
            raise RpcError(_FILE_ERRORS[5])
        if target.stat().st_size > MAX_FILE_BYTES:
            raise RpcError(_FILE_ERRORS[6])
        raw = target.read_bytes()
    if b'\0' in raw:
        raise RpcError('Это не текстовый файл.')
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError:
        raise RpcError('Файл не в кодировке UTF-8.')


def write_file(host, path, text, expected_sha256):
    """Save a small text file after checking its version under an exclusive lock."""
    import hashlib
    _check_name(path)
    data = text.encode('utf-8')
    if len(data) > MAX_FILE_BYTES:
        raise RpcError(_FILE_ERRORS[6])
    if host:
        current = read_file(host, path)
        if hashlib.sha256(current.encode('utf-8')).hexdigest() != expected_sha256:
            raise RpcError(_FILE_ERRORS[8])
        _remote_sh(host, _SH_WRITE, path, data=data, expected_sha256=expected_sha256)
    else:
        _write_local_file(path, data, expected_sha256)
    return {'saved': True, 'sha256': hashlib.sha256(data).hexdigest()}


def _write_local_file(path, data, expected_sha256):
    import fcntl
    import hashlib
    import stat
    import tempfile

    target = _local_checked(path)
    backup = target.with_name(target.name+'.deckai.bak')
    lock_path = target.with_name('.'+target.name+'.deckai.lock')
    if backup.is_symlink() or lock_path.is_symlink():
        raise RpcError(_FILE_ERRORS[4])
    lock_fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    if not stat.S_ISREG(os.fstat(lock_fd).st_mode):
        os.close(lock_fd)
        raise RpcError(_FILE_ERRORS[4])
    with os.fdopen(lock_fd, 'r+b') as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RpcError(_FILE_ERRORS[7]) from None
        current = read_file('', str(target)).encode('utf-8')
        if hashlib.sha256(current).hexdigest() != expected_sha256:
            raise RpcError(_FILE_ERRORS[8])
        mode = stat.S_IMODE(target.stat().st_mode)
        temporary = []
        try:
            for payload in (current, data):
                with tempfile.NamedTemporaryFile(prefix='.deckai-write-', dir=target.parent, delete=False) as staged:
                    temporary.append(Path(staged.name))
                    os.fchmod(staged.fileno(), mode)
                    staged.write(payload)
                    staged.flush()
                    os.fsync(staged.fileno())
            if read_file('', str(target)).encode('utf-8') != current:
                raise RpcError(_FILE_ERRORS[8])
            os.replace(temporary[0], backup)
            os.replace(temporary[1], target)
        finally:
            for staged in temporary:
                staged.unlink(missing_ok=True)
