type DraftStorage=Pick<Storage,'getItem'|'setItem'>;
const key=(thread?:string)=>'codex-game-draft:'+(thread||'new');
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
