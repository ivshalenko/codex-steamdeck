export type UpdateState={
 uiLanguage?:'en'|'ru';installed:Record<string,string>;
 available:{version:string;url:string;notes:string}|null;
 preferences:{automatic:boolean;channel:'automatic'|'stable'|'preview'};
 channel:string;checkedAt:number;checking:boolean;checkError:string;
 job:null|{id:string;phase:string;version:string;progress:number;error?:string;note?:string};
 notificationId?:string;busyDesktop:boolean;workBusy?:boolean;requiresInstaller?:boolean;notificationPending:boolean;
};
export const updateActive=(state:UpdateState|null)=>!!state?.job&&['queued','downloading','quiescing','installing','verifying','rolling-back'].includes(state.job.phase);
export type UpdateClient={status:()=>Promise<UpdateState>;check:()=>Promise<UpdateState>;configure:(automatic:boolean,channel:string)=>Promise<UpdateState>;begin:(version:string,clean:boolean)=>Promise<UpdateState>;acknowledge:(version:string)=>Promise<unknown>};
export function makeUpdateStore(){
 let value:{data:UpdateState|null;error:string;requesting:boolean}={data:null,error:'',requesting:false};
 const listeners=new Set<()=>void>();const blockers=new Set<symbol>();
 const publish=()=>listeners.forEach(listener=>listener());
 return {
  snapshot:()=>value,subscribe:(listener:()=>void)=>{listeners.add(listener);return()=>{listeners.delete(listener);};},
  set:(data:UpdateState)=>{value={...value,data,error:''};publish();},
  block:(id:symbol,dirty:boolean)=>{const previous=blockers.has(id);if(dirty)blockers.add(id);else blockers.delete(id);if(previous!==dirty)publish();},
  blocked:()=>blockers.size>0,
  async request(action:()=>Promise<UpdateState>){
   if(value.requesting)throw Error('An update request is already running.');
   value={...value,requesting:true,error:''};publish();
   try{const data=await action();value={data,error:'',requesting:false};publish();return data;}
   catch(error){value={...value,requesting:false,error:error instanceof Error?error.message:String(error)};publish();throw error;}
  }
 };
}
export const updateStore=makeUpdateStore();
export function startUpdatePolling(client:UpdateClient,onState:(state:UpdateState)=>Promise<void>,timer:{set:(fn:()=>void,ms:number)=>unknown;clear:(id:unknown)=>void}={set:(fn,ms)=>setTimeout(fn,ms),clear:id=>clearTimeout(id as ReturnType<typeof setTimeout>)}):()=>void{
 let stopped=false,handle:unknown;
 const tick=async()=>{
  try{const state=await client.status();if(stopped)return;updateStore.set(state);await onState(state);}catch{}
  if(!stopped)handle=timer.set(()=>void tick(),updateActive(updateStore.snapshot().data)?2000:30000);
 };
 void tick();
 return()=>{stopped=true;if(handle!==undefined)timer.clear(handle);};
}
