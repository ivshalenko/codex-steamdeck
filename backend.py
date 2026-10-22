"""JSON-RPC client for the local Codex daemon. No terminal or API key needed."""
import json
import os
from pathlib import Path
import subprocess
import threading
import shlex
import shutil
from websockets.sync.client import unix_connect

CODEX = shutil.which('codex') or str(Path.home()/'.local/bin/codex')

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

    def connect(self, thread_id):
        if self.remote_host:
            # SSH transports JSONL over stdin/stdout. No listener or port is
            # opened on either machine; authentication uses the user's SSH config.
            probe=subprocess.run(['/usr/bin/ssh','-T','-o','BatchMode=yes','-o','ConnectTimeout=8',self.remote_host,'pwd'],capture_output=True,text=True,timeout=12)
            if probe.returncode:raise RuntimeError('SSH не подключился. Проверьте алиас в ~/.ssh/config и доступ без пароля.')
            self.cwd=probe.stdout.strip() or '~'
            self.process = subprocess.Popen(
                ['/usr/bin/ssh', '-T', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8',
                 self.remote_host, 'codex app-server --listen stdio://'],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                text=True, bufsize=1, env={**os.environ, 'TERM': 'dumb'})
            self.ws = self
            self.connected = True
            threading.Thread(target=self.read, daemon=True).start()
            self.request('initialize', {'clientInfo': {'name':'deck_voice','title':'Codex для Steam Deck','version':'2.0'}, 'capabilities': {'experimentalApi':True}})
            self.notify('initialized')
            return self.select_thread(thread_id) if thread_id else ({},{})
        path = str(Path.home()/'.codex/app-server-control/app-server-control.sock')
        try:
            self.ws = unix_connect(path, uri='ws://localhost/', open_timeout=5, max_size=32*1024*1024)
        except (OSError, TimeoutError):
            subprocess.run([CODEX, 'app-server', 'daemon', 'start'], check=True, capture_output=True, timeout=40)
            self.ws = unix_connect(path, uri='ws://localhost/', open_timeout=10, max_size=32*1024*1024)
        self.connected = True
        threading.Thread(target=self.read, daemon=True).start()
        self.request('initialize', {'clientInfo': {'name':'deck_voice','title':'Codex для Steam Deck','version':'2.0'}, 'capabilities': {'experimentalApi':True}})
        self.notify('initialized')
        return self.select_thread(thread_id) if thread_id else ({},{})

    def select_thread(self, thread_id):
        if self.remote_host:
            history=self.request('thread/read',{'threadId':thread_id,'includeTurns':True},timeout=30)
            thread=history.get('thread',{})
            return {'model':thread.get('model'),'reasoningEffort':thread.get('reasoningEffort')},thread
        result=self.request('thread/resume',{'threadId':thread_id,'excludeTurns':True},timeout=50)
        history=self.request('thread/read',{'threadId':thread_id,'includeTurns':True},timeout=30)
        return result,history['thread']

    def queue_message(self, thread_id, text, model=None, effort=None, tier='default'):
        if not self.remote_host:raise RpcError('SSH-очередь доступна только для удалённого компьютера.')
        command=['codex','queue','--thread',thread_id,'--message',text]
        if model:command += ['--model',model]
        if effort:command += ['-c',f'model_reasoning_effort={effort}']
        if tier=='priority':command += ['-c','service_tier="priority"']
        remote_command=' '.join(shlex.quote(part) for part in command)
        result=subprocess.run(['/usr/bin/ssh','-T','-o','BatchMode=yes','-o','ConnectTimeout=8',self.remote_host,remote_command],capture_output=True,text=True,timeout=45)
        if result.returncode:
            raise RpcError((result.stderr or result.stdout or 'Не удалось поставить запрос в очередь Codex на удалённом компьютере.')[-1200:])
        return {'queued':True,'output':result.stdout.strip()}

    def read(self):
        try:
            source = self.process.stdout if self.process else self.ws
            for raw in source:
                message = json.loads(raw)
                if 'method' in message:
                    self.event(message)
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
            with self.lock:
                for pending in self.pending.values():
                    pending['reply'] = {'error':{'message':'Соединение с Codex прервано'}}
                    pending['done'].set()
            self.disconnected()

    def request(self, method, params, timeout=25):
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
