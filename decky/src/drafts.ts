type DraftStorage=Pick<Storage,'getItem'|'setItem'>;
const key=(thread?:string)=>'codex-game-draft:'+(thread||'new');
export function draftOwner(view?:{provider:string;remoteHost?:string;threadId:string}|null){
 if(!view)return "";
 if(view.provider==="codex"&&!view.remoteHost)return view.threadId;
 return JSON.stringify([view.provider,view.remoteHost||"",view.threadId]);
}
export function createDraftStore(storage:DraftStorage){
 const listeners=new Set<(thread:string,text:string)=>void>();
 return {
  read:(thread?:string)=>storage.getItem(key(thread))||'',
  write(thread:string,text:string){storage.setItem(key(thread),text);for(const listener of listeners)listener(thread,text);},
  subscribe(listener:(thread:string,text:string)=>void){listeners.add(listener);return ()=>{listeners.delete(listener);};}
 };
}
// Both mounted views share this gate: a poll from either must not win over a
// newer navigation/action in the other, including a poll started mid-action.
export function createViewGate(){
 let revision=0;let active=false;const listeners=new Set<(busy:boolean)=>void>();
 return {
  token:()=>revision,
  busy:()=>active,
  current:(token:number)=>!active&&token===revision,
  begin(){if(active)return false;active=true;revision++;for(const listener of listeners)listener(true);return true;},
  end(){active=false;revision++;for(const listener of listeners)listener(false);},
  subscribe(listener:(busy:boolean)=>void){listeners.add(listener);listener(active);return ()=>{listeners.delete(listener);};}
 };
}

// The quick panel and the full-screen page can be mounted together. Share
// their periodic reads without reusing a response across navigation.
export function createSnapshotReader<T>(request:()=>Promise<T>,now=()=>performance.now()){
 let cached:{revision:number;received:number|null;value:Promise<T>}|null=null;
 return (revision:number,maxAge:number)=>{
  if(cached?.revision===revision&&(cached.received===null||now()-cached.received<maxAge)){
   return cached.value;
  }
  // Decky serializes every argument to Python. Do not pass the fulfillment
  // value (undefined) as an extra argument to the no-argument snapshot RPC.
  const entry={revision,received:null as number|null,value:Promise.resolve().then(()=>request())};
  cached=entry;
  return entry.value=entry.value.then(value=>{
   entry.received=now();
   return value;
  },error=>{
   if(cached===entry)cached=null;
   throw error;
  });
 };
}
