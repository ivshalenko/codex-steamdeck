export type DictationDraft={id:string;thread:string;base:string;text:string};
export function updateDictation(previous:DictationDraft|null,id:string,thread:string,text:string,currentDraft:string){
 const session=previous?.id===id?previous:{id,thread,base:currentDraft,text:''};
 const rendered=(session.base?session.base.trimEnd()+' ':'')+session.text.trim()+' ';
 if(session.thread!==thread||session.text===text||(session.text!==''&&currentDraft!==rendered))return {session,value:null};
 return {session:{...session,text},value:(session.base?session.base.trimEnd()+' ':'')+text.trim()+' '};
}

export function restoreDictation(raw:string|null):DictationDraft|null{
 try{
  const value=JSON.parse(raw||'null');
  if(value&&['id','thread','base','text'].every(key=>typeof value[key]==='string'))return value;
 }catch{}
 return null;
}
export function bindDictation(previous:DictationDraft|null,id:string,thread:string,base:string):DictationDraft{
 return previous?.id===id?previous:{id,thread,base,text:''};
}
