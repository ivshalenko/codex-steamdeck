import asyncio, json, os, subprocess, threading, time
from pathlib import Path
import decky
class Plugin:
    async def _main(self):
        self.child=None;self.lock=threading.RLock();self.pending={};self.seq=0
        self.home=Path.home()
        app_dir=self.home/".local/share/deck-voice"
        if not (app_dir/"app.py").exists():app_dir=self.home/".local/share/codex-steamdeck"
        self.base=app_dir/"decky"
        self.start_bridge()
    def start_bridge(self):
        with self.lock:
            if self.child and self.child.poll() is None:return
            env=dict(os.environ);env.update({"HOME":str(self.home),"XDG_RUNTIME_DIR":f"/run/user/{os.getuid()}","PYTHONNOUSERSITE":"1"})
            self.child=subprocess.Popen([str(self.base.parent/"venv/bin/python"),"-u",str(self.base/"bridge.py")],
                cwd=str(self.base),env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,bufsize=1)
            self.reader=threading.Thread(target=self.read_bridge,daemon=True);self.reader.start()
    def read_bridge(self):
        child=self.child
        try:
            for line in child.stdout:
                try:message=json.loads(line)
                except ValueError:continue
                with self.lock:future=self.pending.pop(message.get("id"),None)
                if future:future["response"]=message;future["event"].set()
        except Exception:pass
        finally:
            with self.lock:
                for future in self.pending.values():future["response"]={"error":"Подключение к Codex прервано"};future["event"].set()
                self.pending.clear()
    async def _rpc(self,method,params=None,timeout=35):
        return await asyncio.to_thread(self.rpc_sync,method,params or {},timeout)
    def rpc_sync(self,method,params,timeout):
        self.start_bridge()
        with self.lock:
            self.seq+=1;ident=self.seq;future={"event":threading.Event()};self.pending[ident]=future
            try:self.child.stdin.write(json.dumps({"id":ident,"method":method,"params":params},ensure_ascii=False)+"\n");self.child.stdin.flush()
            except Exception:self.pending.pop(ident,None);raise RuntimeError("Не удалось связаться с Codex.")
        if not future["event"].wait(timeout):
            with self.lock:self.pending.pop(ident,None)
            raise RuntimeError("Codex долго не отвечает. Попробуйте ещё раз.")
        response=future["response"]
        if "error" in response:raise RuntimeError(str(response["error"]))
        return response.get("result")
    async def get_snapshot(self):return await self._rpc("snapshot",timeout=60)
    async def refresh(self):return await self._rpc("refresh",timeout=60)
    async def select_thread(self,ident):return await self._rpc("select_thread",{"id":ident},timeout=60)
    async def new_thread(self):return await self._rpc("new_thread",timeout=60)
    async def save_settings(self,model,effort,tier):return await self._rpc("settings",{"model":model,"effort":effort,"tier":tier})
    async def send_message(self,text,images,model,effort,tier):return await self._rpc("send",{"text":text,"images":images,"model":model,"effort":effort,"tier":tier},timeout=40)
    async def retry(self,ident):return await self._rpc("retry",{"id":ident})
    async def stop(self):return await self._rpc("stop",timeout=25)
    async def voice(self,language):return await self._rpc("voice",{"language":language},timeout=8)
    async def video_frames(self,path):return await self._rpc("video_frames",{"path":path},timeout=110)
    async def open_desktop(self):return await self._rpc("open_window")
    async def account_login(self):return await self._rpc("account_login",timeout=30)
    async def account_cancel_login(self):return await self._rpc("account_cancel_login",timeout=20)
    async def account_logout(self):return await self._rpc("account_logout",timeout=30)
    async def remote_host(self,host):return await self._rpc("remote_host",{"host":host},timeout=75)
    async def set_provider(self,provider):return await self._rpc("provider",{"provider":provider},timeout=60)
    async def set_provider_key(self,key):return await self._rpc("provider_key",{"key":key},timeout=20)
    async def _unload(self):
        try:
            with self.lock:
                if self.child and self.child.poll() is None:
                    self.child.stdin.write('{"method":"shutdown"}\n');self.child.stdin.flush();self.child.terminate()
        except Exception:pass
    async def _uninstall(self):await self._unload()
