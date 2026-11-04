export type WorkspaceTab='chat'|'history'|'repair'|'settings';
const key='deck-ai-workspace-tab',eventName='deck-ai-workspace-tab';
const valid=(value:unknown):value is WorkspaceTab=>['chat','history','repair','settings'].includes(String(value));
export function workspaceNavigation(storage:Pick<Storage,'getItem'|'setItem'>,events:Pick<EventTarget,'addEventListener'|'removeEventListener'|'dispatchEvent'>){
 let latest:WorkspaceTab='chat';
 const decode=(raw:string|null)=>{try{const value=JSON.parse(raw||'{}').tab;return valid(value)?value:null;}catch{return null;}};
 return {
  current():WorkspaceTab{try{return decode(storage.getItem(key))||latest;}catch{return latest;}},
  request(tab:WorkspaceTab){
   latest=tab;const value=JSON.stringify({tab,nonce:Date.now()+':'+Math.random()});
   try{storage.setItem(key,value);}catch{}
   events.dispatchEvent(new CustomEvent(eventName,{detail:tab}));
  },
  subscribe(receive:(tab:WorkspaceTab)=>void){
   const local=(event:Event)=>{const tab=(event as CustomEvent).detail;if(valid(tab)){latest=tab;receive(tab);}};
   const remote=(event:Event)=>{const value=event as StorageEvent;if(value.key===key){const tab=decode(value.newValue);if(tab){latest=tab;receive(tab);}}};
   events.addEventListener(eventName,local);events.addEventListener('storage',remote);
   return()=>{events.removeEventListener(eventName,local);events.removeEventListener('storage',remote);};
  }
 };
}
