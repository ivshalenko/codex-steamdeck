import asyncio, json, os, subprocess, threading, time, sys, shutil
from pathlib import Path
import decky
sys.path.insert(0,str(Path(__file__).resolve().parent))
from runtime_paths import resolve_app_dir
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

class Plugin:
    async def _main(self):
        self.child=None;self.lock=threading.RLock();self.pending={};self.seq=0
        self.home=Path.home()
        app_dir=resolve_app_dir(self.home)
        self.base=Path(__file__).resolve().parent
        self.python=str(app_dir/"venv/bin/python") if (app_dir/"venv/bin/python").is_file() else (shutil.which("python3") or "/usr/bin/python3")
        self.start_bridge()
    def start_bridge(self):
        with self.lock:
            if self.child and self.child.poll() is None:return
            env=clean_subprocess_environment();env.update({"HOME":str(self.home),"XDG_RUNTIME_DIR":f"/run/user/{os.getuid()}","PYTHONNOUSERSITE":"1"})
            self.child=subprocess.Popen([self.python,"-u",str(self.base/"bridge.py")],
                cwd=str(self.base),env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
            self.stderr_tail=""
            threading.Thread(target=self.read_errors,args=(self.child,),daemon=True).start()
            self.reader=threading.Thread(target=self.read_bridge,args=(self.child,),daemon=True);self.reader.start()
    def read_errors(self,child):
        for line in child.stderr:
            if self.child is child:self.stderr_tail=(self.stderr_tail+line)[-1600:]
    def read_bridge(self,child):
        try:
            for line in child.stdout:
                try:message=json.loads(line)
                except ValueError:continue
                with self.lock:
                    future=self.pending.get(message.get("id"))
                    if future and future.get("child") is child:self.pending.pop(message.get("id"),None)
                    else:future=None
                if future:future["response"]=message;future["event"].set()
        except Exception:pass
        finally:
            with self.lock:
                for ident,future in list(self.pending.items()):
                    if future.get("child") is child:
                        future["response"]={"error":"Подключение к Deck AI прервано"};future["event"].set();self.pending.pop(ident,None)
    async def _rpc(self,method,params=None,timeout=35):
        return await asyncio.to_thread(self.rpc_sync,method,params or {},timeout)
    def rpc_sync(self,method,params,timeout):
        self.start_bridge()
        with self.lock:
            self.seq+=1;ident=self.seq;future={"event":threading.Event(),"child":self.child};self.pending[ident]=future
            try:self.child.stdin.write(json.dumps({"id":ident,"method":method,"params":params},ensure_ascii=False)+"\n");self.child.stdin.flush()
            except Exception:self.pending.pop(ident,None);raise RuntimeError("Не удалось связаться с Codex.")
        if not future["event"].wait(timeout):
            with self.lock:self.pending.pop(ident,None)
            raise RuntimeError("Codex долго не отвечает. Попробуйте ещё раз.")
        response=future["response"]
        if "error" in response:raise RuntimeError(str(response["error"]))
        return response.get("result")
    async def older_messages(self):return await self._rpc("older_messages",timeout=60)
    async def get_snapshot(self):return await self._rpc("snapshot",timeout=60)
    async def refresh(self):return await self._rpc("refresh",timeout=60)
    async def select_thread(self,ident):return await self._rpc("select_thread",{"id":ident},timeout=60)
    async def new_thread(self):return await self._rpc("new_thread",timeout=60)
    async def save_settings(self,model,effort,tier):return await self._rpc("settings",{"model":model,"effort":effort,"tier":tier})
    async def send_message(self,text,images,model,effort,tier):return await self._rpc("send",{"text":text,"images":images,"model":model,"effort":effort,"tier":tier},timeout=40)
    async def retry(self,ident):return await self._rpc("retry",{"id":ident})
    async def stop(self):return await self._rpc("stop",timeout=25)
    async def voice(self,language,silence=0):return await self._rpc("voice",{"language":language,"silence":silence},timeout=8)
    async def video_frames(self,path):return await self._rpc("video_frames",{"path":path},timeout=110)
    async def open_desktop(self):return await self._rpc("open_window")
    async def account_login(self):return await self._rpc("account_login",timeout=30)
    async def account_cancel_login(self):return await self._rpc("account_cancel_login",timeout=20)
    async def account_logout(self):return await self._rpc("account_logout",timeout=30)
    async def remote_host(self,host):return await self._rpc("remote_host",{"host":host},timeout=75)
    async def set_provider(self,provider):return await self._rpc("provider",{"provider":provider},timeout=60)
    async def watch(self,hosts):return await self._rpc("watch",{"hosts":hosts},timeout=15)
    async def read_only(self,value):return await self._rpc("read_only",{"value":value},timeout=10)
    async def queue_front(self,ident):return await self._rpc("queue_front",{"id":ident},timeout=10)
    async def queue_remove(self,ident):return await self._rpc("queue_remove",{"id":ident},timeout=10)
    async def file_list(self,path):return await self._rpc("file_list",{"path":path},timeout=40)
    async def file_read(self,path):return await self._rpc("file_read",{"path":path},timeout=40)
    async def file_write(self,path,text,expected):return await self._rpc("file_write",{"path":path,"text":text,"expected":expected},timeout=50)
    async def share_status(self):return await self._rpc("share_status",timeout=20)
    async def share_add_key(self,key):return await self._rpc("share_add_key",{"key":key},timeout=10)
    async def custom_save(self,name,base_url,models,key):return await self._rpc("custom_save",{"name":name,"baseUrl":base_url,"models":models,"key":key},timeout=20)
    async def custom_remove(self,ident):return await self._rpc("custom_remove",{"id":ident},timeout=20)
    async def poll_events(self,since=None):return await self._rpc("events",{"since":since},timeout=10)
    async def approve(self,ident,decision):return await self._rpc("approve",{"id":ident,"decision":decision},timeout=20)
    async def diagnose(self):return await self._rpc("diagnose",timeout=80)
    async def unload_models(self):return await self._rpc("unload_models",timeout=10)
    async def set_provider_key(self,key):return await self._rpc("provider_key",{"key":key},timeout=20)
    async def _unload(self):
        try:
            with self.lock:
                if self.child and self.child.poll() is None:
                    self.child.stdin.write('{"method":"shutdown"}\n');self.child.stdin.flush();self.child.terminate()
        except Exception:pass
    async def _uninstall(self):await self._unload()
