import { useCallback, useEffect, useRef, useState, type CSSProperties, type ReactNode, type ComponentType, type HTMLAttributes, type RefAttributes } from "react";
import { callable, definePlugin, routerHook, toaster } from "@decky/api";
import { DialogButton, Dropdown, Focusable, TextField, ConfirmModal, showModal, ScrollPanel, Navigation, Router } from "@decky/ui";
import { FaMicrophone, FaComment, FaHistory, FaCog, FaExpand, FaCompress, FaArrowLeft, FaGamepad, FaCopy, FaPlus, FaFolderOpen, FaListUl, FaSyncAlt } from "react-icons/fa";
import logo from "../deck-ai.png";
import css from "./style.css";
import { createDraftStore, createViewGate } from "./drafts";
import { chatFailures, queueCounts, queueStatus, type QueueJob } from "./queue";
import { speechLanguages } from "./speech-languages";
import { parseQuickActions } from "./quick";
import { themes, densities, bubbleStyles, layouts, readAppearance, withChoice, effectiveLayout, appearanceKey, type Appearance } from "./appearance";
import { attachTouchScroll, type Box } from "./touch-scroll";
import { joinPath, parentPath, isFolder, sortEntries } from "./files";
import { updateDictation, restoreDictation, bindDictation } from "./dictation";
import { readGameContext, withGameContext, gameScreenshots } from "./game-context";
import { startRepairPolling } from "./launch-repair";
import { RepairPanel } from "./repair-panel";

type Attachment={id:string;name:string;preview:string;available:boolean;kind:"image"|"file"};
type Item = {id:string;role:"user"|"assistant"|"tool";text:string;attachments?:Attachment[]};
type Media = {path:string;name:string;when?:number};
type Approval={key:string;id:string|number;threadId:string;title:string;summary:string};
type TaskRow={host:string;id:string;name:string;updatedAt:number;running:boolean};
type DeviceEvent={id:number;kind:string;title:string;host:string;at:number;summary?:string};
type Share={fingerprints?:string[];sshActive:boolean;user:string;hostname:string;addresses:string[];keys:number;codex:boolean;snippet:string;enableHint:string};
type Check={name:string;ok:boolean;detail:string};
type Model = {id:string;name:string;efforts:{id:string;name:string}[];defaultEffort:string;tiers:string[]};
type Snapshot = {historyWarning?:string;hasOlderMessages?:boolean;ready:boolean;status:string;provider:string;account?:{email?:string;planType?:string}|null;loginPending?:boolean;remoteHost?:string;sshHosts:string[];threads:{id:string;name:string;updatedAt:number;running?:boolean}[];runningCount?:number;approvals?:Approval[];retryIn?:number;allTasks?:TaskRow[];loadedModels?:number;readOnly?:boolean;watchHosts?:string[];watchStatus?:Record<string,string>;recentEvents?:DeviceEvent[];customProviders?:{id:string;name:string;baseUrl:string}[];presets?:{name:string;url:string}[];threadId:string;messages:Item[];active:boolean;models:Model[];model:string;effort:string;tier:string;screenshots:Media[];videos:Media[];outbox:QueueJob[];queueTotal?:number;speechVersion?:number;speechReady?:boolean;voiceId?:string;voiceState:string;voiceText:string;voiceError:string};
const snapshot=callable<[],Snapshot>("get_snapshot");
const refresh=callable<[],Snapshot>("refresh");
const selectThread=callable<[id:string],Snapshot>("select_thread");
const newThread=callable<[],Snapshot>("new_thread");
const saveSettings=callable<[model:string,effort:string,tier:string],unknown>("save_settings");
const sendMessage=callable<[text:string,images:string[],model:string,effort:string,tier:string],{queued:boolean;threadId?:string}>("send_message");
const retry=callable<[id:string],unknown>("retry");
const stop=callable<[],unknown>("stop");
const gameVoice=callable<[language:string,silence:number],{voiceState:string;voiceText?:string;voiceId?:string}>("voice");
const videoFrames=callable<[path:string],{frames:Media[]}>("video_frames");
const accountLogin=callable<[],{opened:boolean;url:string;userCode?:string}>("account_login");
const accountCancelLogin=callable<[],unknown>("account_cancel_login");
const accountLogout=callable<[],unknown>("account_logout");
const remoteHost=callable<[host:string],Snapshot>("remote_host");
const setProvider=callable<[provider:string],Snapshot>("set_provider");
const olderMessages=callable<[],Snapshot>("older_messages");
const pollEvents=callable<[since:number|null],{latest:number;notifications:{id:number;kind:string;title:string;host:string;summary?:string;threadId?:string}[]}>("poll_events");
const approve=callable<[id:string,decision:string],unknown>("approve");
const diagnose=callable<[],{checks:Check[]}>("diagnose");
const watchHosts=callable<[hosts:string[]],unknown>("watch");
const setReadOnly=callable<[value:boolean],unknown>("read_only");
const queueFront=callable<[id:string],unknown>("queue_front");
const queueRemove=callable<[id:string],unknown>("queue_remove");
const fileList=callable<[path:string],{path:string;entries:string[]}>("file_list");
const fileRead=callable<[path:string],{path:string;text:string;sha256:string}>("file_read");
const fileWrite=callable<[path:string,text:string,expected:string],{saved:boolean;sha256:string}>("file_write");
const shareStatus=callable<[],Share>("share_status");
const shareAddKey=callable<[key:string],{added:boolean;keys:number}>("share_add_key");
const customSave=callable<[name:string,baseUrl:string,models:string,key:string],{id:string}>("custom_save");
const customRemove=callable<[id:string],unknown>("custom_remove");
const unloadModels=callable<[],unknown>("unload_models");
const setProviderKey=callable<[key:string],unknown>("set_provider_key");
const GameScroll=ScrollPanel as ComponentType<HTMLAttributes<HTMLDivElement> & RefAttributes<HTMLDivElement>>;
type Tab = "chat"|"history"|"repair"|"settings";
const providerNames:Record<string,string>={codex:"Codex · ChatGPT",claude:"Claude Code · свой доступ",deepseek:"DeepSeek · OpenRouter",tokenharbor:"DeepSeek · TokenHarbor"};
const drafts=createDraftStore(localStorage);
const viewGate=createViewGate();
function Action({children,onClick,disabled=false,primary=false,recording=false,selected}:{children:ReactNode;onClick:()=>void;disabled?:boolean;primary?:boolean;recording?:boolean;selected?:boolean}) {
 return <DialogButton className={"dai-button"+(primary?" dai-primary":"")+(recording?" dai-recording":"")+(selected?" dai-selected":"")} aria-pressed={selected} disabled={disabled} onClick={onClick}>{children}</DialogButton>;
}
function Segmented({label,value,options,onChange}:{label:string;value:string;options:readonly {id:string;name:string}[];onChange:(id:string)=>void}){
 return <div className="dai-field"><span className="dai-label">{label}</span><Focusable className="dai-segmented" flow-children="horizontal">{options.map(option=><Action key={option.id} selected={value===option.id} onClick={()=>onChange(option.id)}>{option.name}</Action>)}</Focusable></div>;
}
function MessageAttachments({items}:{items:Attachment[]}){
 return <div className="dai-message-attachments">{items.map(item=><div className="dai-message-attachment" key={item.id}>
  {item.preview?<DialogButton className="dai-image-button" onClick={()=>showModal(<ConfirmModal strTitle={item.name.length>48?item.name.slice(0,45)+"…":item.name} strOKButtonText="Закрыть" bAlertDialog><img className="dai-image-expanded" style={{display:"block",maxWidth:"100%",maxHeight:"55vh",width:"auto",height:"auto",objectFit:"contain",margin:"auto"}} src={item.preview} alt={item.name}/></ConfirmModal>)}><img src={item.preview} alt={item.name}/></DialogButton>:<span className="dai-muted">📎 {item.name} · {item.kind==="image"?"изображение недоступно":"файл"}</span>}
 </div>)}</div>;
}
function GameCheckbox({checked,onChange}:{checked:boolean;onChange:()=>void}){
 return <div className="dai-game-check" role="checkbox" aria-checked={checked} aria-label="Игра"><DialogButton className="dai-button" onClick={onChange}><span className="dai-check-box" aria-hidden="true">{checked?"✓":""}</span>Игра</DialogButton></div>;
}
function Choice({label,value,options,onChange,disabled=false}:{label:string;value:string;options:{data:string;label:string}[];onChange:(value:string)=>void;disabled?:boolean}) {
 return <div className="dai-field"><span className="dai-label">{label}</span><Dropdown menuLabel={label} selectedOption={value} rgOptions={options} disabled={disabled||!options.length} strDefaultLabel="Выберите…" onChange={item=>onChange(String(item.data))}/></div>;
}
// The compact panel and the full-screen route use the same session. Moving
// between them must preserve the draft, attachments and consumed dictation.
const dictationKey="deck-ai-dictation-v1";
const historySnapshots=new Map<string,Snapshot>();
const historyKey=(s:Pick<Snapshot,"provider"|"remoteHost"|"threadId">)=>JSON.stringify([s.provider,s.remoteHost||"",s.threadId]);
const session={snapshot:null as Snapshot|null,attachments:new Map<string,Media[]>(),voiceText:"",voiceError:"",discardedVoice:localStorage.getItem("deck-ai-discarded-voice")||"",finishedVoice:"",dictation:restoreDictation(localStorage.getItem(dictationKey))};
const attachmentListeners=new Set<(thread:string,items:Media[])=>void>();
function publishAttachments(thread:string,items:Media[]){
 if(items.length)session.attachments.set(thread,items);else session.attachments.delete(thread);
 for(const listener of attachmentListeners)listener(thread,items);
}
const textScaleKey="deck-ai-text-scale";
const textScaleListeners=new Set<(value:number)=>void>();
function readTextScale(){
 const value=Number(localStorage.getItem(textScaleKey)||1);
 return Number.isFinite(value)?Math.max(.7,Math.min(1.5,Math.round(value*10)/10)):1;
}
function useTextScale(){
 const [scale,setScale]=useState(readTextScale);
 useEffect(()=>{textScaleListeners.add(setScale);return()=>{textScaleListeners.delete(setScale);};},[]);
 return [scale,(value:number)=>{
  const next=Math.max(.7,Math.min(1.5,Math.round(value*10)/10));
  localStorage.setItem(textScaleKey,String(next));
  textScaleListeners.forEach(listener=>listener(next));
 }] as const;
}
const appearanceListeners=new Set<(value:Appearance)=>void>();
function useAppearance(){
 const [appearance,setAppearance]=useState(()=>readAppearance(localStorage.getItem(appearanceKey)));
 useEffect(()=>{appearanceListeners.add(setAppearance);return()=>{appearanceListeners.delete(setAppearance);};},[]);
 return [appearance,(key:keyof Appearance,choice:string)=>{
  const next=withChoice(readAppearance(localStorage.getItem(appearanceKey)),key,choice);
  localStorage.setItem(appearanceKey,JSON.stringify(next));
  appearanceListeners.forEach(listener=>listener(next));
 }] as const;
}
const gameContextListeners=new Set<(enabled:boolean)=>void>();
function useGameContextEnabled(){
 const [enabled,setEnabled]=useState(()=>localStorage.getItem("deck-ai-game-context")==="on");
 useEffect(()=>{gameContextListeners.add(setEnabled);return()=>{gameContextListeners.delete(setEnabled);};},[]);
 const toggle=()=>{
  const next=localStorage.getItem("deck-ai-game-context")!=="on";
  localStorage.setItem("deck-ai-game-context",next?"on":"off");
  gameContextListeners.forEach(listener=>listener(next));
 };
 return [enabled,toggle] as const;
}
const FULLSCREEN_PATH="/deck-ai";
let panelMounted=0;
const flag=(key:string,fallback:boolean)=>{const value=localStorage.getItem(key);return value===null?fallback:value==="on";};
let requestedTab:Tab="chat";
let fullscreenOrigin=Router.MainRunningAppID?"/apprunning":"/";
const fullscreenViews=new Set<(tab:Tab)=>void>();
let returnToPanel:ReturnType<typeof setTimeout>|undefined;
function openFullscreen(tab:Tab){
 requestedTab=tab;
 const current=window.location.pathname.replace(/^\/routes/,"")||"/";
 if(current!==FULLSCREEN_PATH)fullscreenOrigin=current;
 if(returnToPanel)clearTimeout(returnToPanel);
 if(current===FULLSCREEN_PATH&&fullscreenViews.size)fullscreenViews.forEach(change=>change(tab));
 else Navigation.Navigate(FULLSCREEN_PATH);
 Navigation.CloseSideMenus();
}
function closeFullscreen(panel=true){
 if(returnToPanel)clearTimeout(returnToPanel);
 // Replace the workspace entry: old duplicate /deck-ai history entries must
 // never trap Back/Return to game on the same full-screen page.
 Router.Navigate(fullscreenOrigin,true);
 if(panel)returnToPanel=setTimeout(()=>Navigation.OpenQuickAccessMenu(999),150);
}
function FullscreenPage(){return <Panel fullscreen initialTab={requestedTab}/>;}
function Panel({fullscreen=false,initialTab="chat"}:{fullscreen?:boolean;initialTab?:Tab}) {
 const [textScale,setTextScale]=useTextScale();
 const [appearance,setAppearanceChoice]=useAppearance();
 const layout=effectiveLayout(appearance.layout,fullscreen);
 const [gameContextEnabled,toggleGameContext]=useGameContextEnabled();
 const [data,setData]=useState<Snapshot|null>(session.snapshot);
 const [tab,setTab]=useState<Tab>(initialTab);
 useEffect(()=>{
  if(!fullscreen)return;
  const change=(next:Tab)=>{setTab(next);setMediaOpen(false);setQueueOpen(false);};
  fullscreenViews.add(change);
  return()=>{fullscreenViews.delete(change);};
 },[fullscreen]);
 const [draft,setDraft]=useState(()=>drafts.read(session.snapshot?.threadId));
 const draftId=useRef(session.snapshot?.threadId||"");
 const [busy,setBusy]=useState(false);
 useEffect(()=>viewGate.subscribe(setBusy),[]);
 const [voiceStarting,setVoiceStarting]=useState(false);
 const [voicePolling,setVoicePolling]=useState(false);
 const actionLock=useRef(false);
 const [error,setError]=useState("");
 const [connectionError,setConnectionError]=useState("");
 const [notice,setNotice]=useState("");
 const [showLatest,setShowLatest]=useState(false);
 useEffect(()=>{if(!notice)return;const timer=setTimeout(()=>setNotice(""),4000);return()=>clearTimeout(timer);},[notice]);
 const [lang,setLang]=useState(()=>localStorage.getItem("codex-game-voice")||"ru");
 const [mediaOpen,setMediaOpen]=useState(false);
 const [queueOpen,setQueueOpen]=useState(false);
 const [expandedJob,setExpandedJob]=useState("");
 const [images,setImagesState]=useState<Media[]>(()=>session.attachments.get(draftId.current)||[]);
 const setImages=(update:Media[]|((old:Media[])=>Media[]))=>{
  const owner=draftId.current,old=session.attachments.get(owner)||[];
  publishAttachments(owner,typeof update==="function"?update(old):update);
 };
 useEffect(()=>{
  const unsubscribe=drafts.subscribe((owner,text)=>{if(owner===draftId.current)setDraft(text);});
  const receive=(owner:string,items:Media[])=>{if(owner===draftId.current)setImagesState(items);};
  attachmentListeners.add(receive);
  return()=>{unsubscribe();attachmentListeners.delete(receive);};
 },[]);
 const [shot,setShot]=useState("");const [video,setVideo]=useState("");
 const [key,setKey]=useState("");const [host,setHost]=useState("");
 const [loginUrl,setLoginUrl]=useState("");
 const [historyQuery,setHistoryQuery]=useState("");
 const [notify,setNotify]=useState(()=>flag("deck-ai-notify",true));
 const [autoSend,setAutoSend]=useState(()=>flag("deck-ai-auto-send",false));
 const [countdown,setCountdown]=useState<number|null>(null);
 const pendingAuto=useRef(false);
 const [quickOpen,setQuickOpen]=useState(false);
 const [quickSource,setQuickSource]=useState<string|null>(()=>localStorage.getItem("deck-ai-quick"));
 const quickActions=parseQuickActions(quickSource);
 const autoSendRef=useRef(autoSend);autoSendRef.current=autoSend;
 const [confirmApproval,setConfirmApproval]=useState("");
 const [filesOpen,setFilesOpen]=useState(false);
 const [folder,setFolder]=useState("~");
 const [entries,setEntries]=useState<string[]>([]);
 const [file,setFile]=useState<{path:string;text:string;sha256:string}|null>(null);
 const [fileText,setFileText]=useState("");
 const [speaking,setSpeaking]=useState("");
 const touchAnchor=useRef<HTMLSpanElement>(null);
 useEffect(()=>{
  const root=touchAnchor.current?.closest(".dai-root") as HTMLElement|null;
  const view=root?.ownerDocument.defaultView;
  if(!root||!view)return;
  return attachTouchScroll(root as unknown as Parameters<typeof attachTouchScroll>[0],(el:Box)=>{const node=el as unknown as HTMLElement;const overflow=view.getComputedStyle(node).overflowY;return (overflow==="auto"||overflow==="scroll")&&node.scrollHeight>node.clientHeight;},fn=>{view.requestAnimationFrame(fn);});
 },[]);
 const [share,setShare]=useState<Share|null>(null);
 const [shareKey,setShareKey]=useState("");
 const [checks,setChecks]=useState<Check[]|null>(null);
 const [openTool,setOpenTool]=useState("");
 useEffect(()=>{panelMounted++;return()=>{panelMounted--;};},[]);
 const lastVoice=useRef(session.voiceText);const lastVoiceError=useRef(session.voiceError);
 const inFlight=useRef(false);const mounted=useRef(true);
 const queueRef=useRef<HTMLDivElement>(null);
 useEffect(()=>{if(queueOpen)requestAnimationFrame(()=>{const el=queueRef.current;if(el){el.scrollTop=0;el.querySelector<HTMLButtonElement>("button")?.focus();}});},[queueOpen]);
 const chatRef=useRef<HTMLDivElement>(null);const followTail=useRef(true);
 const accept=useCallback((incoming:Snapshot)=>{
  setVoicePolling(["recording","stopping","processing"].includes(incoming.voiceState));
  const next=incoming.voiceId===session.finishedVoice&&incoming.voiceText?{...incoming,voiceState:"done"}:incoming;
  // Change the draft and its storage key together; polling must never copy a
  // draft into a different chat when the selected conversation changes.
  if(next.threadId!==draftId.current){draftId.current=next.threadId;setDraft(drafts.read(next.threadId));setImagesState(session.attachments.get(next.threadId)||[]);followTail.current=true;setShowLatest(false);}
  historySnapshots.set(historyKey(next),next);
  while(historySnapshots.size>12)historySnapshots.delete(historySnapshots.keys().next().value!);
  session.snapshot=next;setData(next);
  if(next.voiceId&&["recording","stopping","processing"].includes(next.voiceState)){
   session.dictation=bindDictation(session.dictation,next.voiceId,next.threadId,drafts.read(next.threadId));
   localStorage.setItem(dictationKey,JSON.stringify(session.dictation));
  }
  if(next.voiceId&&next.voiceId!==session.discardedVoice&&next.voiceText&&next.voiceState==="done"){
   const id=next.voiceId;
   const owner=session.dictation?.id===id?session.dictation.thread:next.threadId;
   const update=updateDictation(session.dictation,id,owner,next.voiceText,drafts.read(owner));
   session.dictation=update.session;
   localStorage.setItem(dictationKey,JSON.stringify(session.dictation));
   if(update.value!==null){drafts.write(owner,update.value);if(owner===draftId.current)setDraft(update.value);if(autoSendRef.current&&owner===draftId.current){pendingAuto.current=true;setTimeout(()=>{pendingAuto.current=false;},8000);}}
   lastVoice.current=next.voiceText;session.voiceText=next.voiceText;
  }else if(!next.voiceId&&next.voiceState==="done"&&next.voiceText&&next.voiceText!==session.voiceText){lastVoice.current=next.voiceText;session.voiceText=next.voiceText;drafts.write(next.threadId,(drafts.read(next.threadId).trimEnd()?drafts.read(next.threadId).trimEnd()+" ":"")+next.voiceText.trim()+" ");}
  if(next.voiceError&&next.voiceError!==lastVoiceError.current){lastVoiceError.current=next.voiceError;session.voiceError=next.voiceError;setError(next.voiceError);}
 },[]);
 const load=useCallback(async()=>{
  if(inFlight.current||viewGate.busy())return;
  inFlight.current=true;const revision=viewGate.token();
  try{const next=await snapshot();if(mounted.current&&viewGate.current(revision)){accept(next);setConnectionError("");}}catch{if(mounted.current)setConnectionError("Связь с Deck AI прервалась. Повторяю подключение…");}finally{inFlight.current=false;}
 },[accept]);
 useEffect(()=>{mounted.current=true;void load();const timer=setInterval(()=>void load(),voicePolling?500:2500);return()=>{mounted.current=false;clearInterval(timer);};},[load,voicePolling]);
 useEffect(()=>{const el=chatRef.current;if(el&&followTail.current)el.scrollTop=el.scrollHeight;},[data?.messages,tab]);
 const editDraft=(value:string,owner=draftId.current)=>drafts.write(owner,value);
 const run=async(work:()=>Promise<void>)=>{if(actionLock.current||!viewGate.begin())return;actionLock.current=true;setBusy(true);setError("");setNotice("");try{await work();}catch(e){setError(String(e));}finally{actionLock.current=false;viewGate.end();setBusy(false);}};
 const model=data?.models.find(x=>x.id===data.model)||data?.models[0];
 const effort=data?.effort||model?.defaultEffort||model?.efforts[0]?.id||"";
 const tier=data?.tier||"default";
 const recording=voiceStarting||data?.voiceState==="recording";
 const voiceProcessing=data?.voiceState==="stopping"||data?.voiceState==="processing";
 const clearDraft=()=>{
  session.discardedVoice=data?.voiceId||"";
  localStorage.setItem("deck-ai-discarded-voice",session.discardedVoice);
  if(data?.voiceText){lastVoice.current=data.voiceText;session.voiceText=data.voiceText;}
  editDraft("");setNotice("Поле сообщения очищено");
 };
 const toggleVoice=async()=>{
  if(voiceStarting)return;
  setVoiceStarting(true);setError("");
  const stopping=recording;
  try{
   // RU/EN use the streaming recognizer: no second, blocking model pass.
   const result=await gameVoice(lang==="ru"?"ru-fast":lang==="en"?"en-fast":lang,stopping||!autoSend?0:2.5);
   const latest=session.snapshot;
   if(stopping&&latest){
    session.finishedVoice=latest.voiceId||"";
    accept({...latest,...result,voiceState:(result.voiceText||latest.voiceText)?"done":result.voiceState});
   }else if(latest){session.finishedVoice="";accept({...latest,...result,voiceText:""});}
   void load();
  }catch(e){setError("Не удалось завершить диктовку: "+String(e));}
  finally{setVoiceStarting(false);}
 };
 const currentGame=()=>readGameContext({appId:Router.MainRunningAppID,overview:id=>window.appStore?.GetAppOverviewByAppID(id),player:()=>window.friendStore?.GetFriendState(window.friendStore.currentUserSteamID)});
 const game=currentGame();
 const currentScreenshots=gameScreenshots(data?.screenshots||[],game);
 const gameStatus=gameContextEnabled&&game?game.name:model?.name||"Готов";
 const submit=()=>void run(async()=>{
  if(!data||!draft.trim()){setError("Нет текста для отправки. Завершите диктовку или введите сообщение.");return;}
  const sentThread=draftId.current,sentDraft=draft;
  await sendMessage(withGameContext(sentDraft,currentGame(),localStorage.getItem("deck-ai-game-context")==="on"),images.map(x=>x.path),model?.id||"",effort,tier);
  if(drafts.read(sentThread)===sentDraft){
   drafts.write(sentThread,"");
   if(draftId.current===sentThread)setDraft("");
  }
  publishAttachments(sentThread,[]);
  if(draftId.current===sentThread)setImagesState([]);
  setNotice("Запрос принят · в очереди");followTail.current=true;accept(await snapshot());
 });
 const submitRef=useRef(submit);submitRef.current=submit;
 useEffect(()=>{if(pendingAuto.current&&!recording&&!voiceProcessing&&draft.trim()){pendingAuto.current=false;setCountdown(3);}},[draft,recording,voiceProcessing]);
 useEffect(()=>{
  if(countdown===null)return;
  if(countdown<=0){setCountdown(null);submitRef.current();return;}
  const timer=setTimeout(()=>setCountdown(value=>value===null?null:value-1),1000);
  return()=>clearTimeout(timer);
 },[countdown]);
 const quick=(text:string)=>void run(async()=>{await sendMessage(text,[],model?.id||"",effort,tier);setNotice("Запрос принят · в очереди");setQuickOpen(false);followTail.current=true;accept(await snapshot());});
 const ro=!!data?.readOnly;
 const names:Record<string,string>={...providerNames,...Object.fromEntries((data?.customProviders||[]).map(c=>[c.id,c.name]))};
 const isCustom=!!data?.customProviders?.some(c=>c.id===data.provider);
 const [custom,setCustom]=useState({name:"",url:"",models:"",key:""});
 const decide=(item:Approval,decision:string)=>void run(async()=>{
  // Allowing runs a command on the machine: require a second, deliberate press.
  if(decision!=="decline"&&confirmApproval!==item.key){setConfirmApproval(item.key);setNotice("Нажмите «Разрешить» ещё раз, чтобы подтвердить");return;}
  setConfirmApproval("");await approve(item.key,decision);setNotice(decision==="decline"?"Отклонено":"Разрешено");accept(await snapshot());
 });
 const openFolder=(path:string)=>void run(async()=>{const result=await fileList(path);setFolder(result.path);setEntries(sortEntries(result.entries));setFile(null);});
 const openFile=(path:string)=>void run(async()=>{const result=await fileRead(path);setFile(result);setFileText(result.text);});
 const saveFile=()=>void run(async()=>{if(!file)return;const result=await fileWrite(file.path,fileText,file.sha256);setFile({...file,text:fileText,sha256:result.sha256});setNotice("Файл сохранён · копия: "+file.path.split("/").pop()+".deckai.bak");});
 const chooseThread=(id:string)=>void run(async()=>{
  
  const current=session.snapshot;
  if(current){const cached=historySnapshots.get(historyKey({...current,threadId:id}));accept(cached?{...cached,threads:current.threads}:{...current,threadId:id,messages:[],active:false,status:"Загружаю диалог…"});}
  accept(await selectThread(id));setTab("chat");
 });
 const startChat=()=>void run(async()=>{accept(await newThread());setTab("chat");});
 const openFiles=()=>{setTab("history");setFilesOpen(true);openFolder("~");};
 const sortedThreads=[...(data?.threads||[])].sort((a,b)=>Number(!!b.running)-Number(!!a.running));
 const sidebar=fullscreen&&layout==="split"?<GameScroll className="dai-split-side"><div className="dai-stack-content">
  <Action primary disabled={busy||!data?.ready||ro||data?.active} onClick={startChat}><FaPlus/>Новый чат</Action>
  {sortedThreads.map(thread=><div className={"dai-history-item "+(thread.id===data?.threadId?"selected":"")+(thread.running?" running":"")} key={thread.id}><Action disabled={busy||(data?.active&&thread.id!==data.threadId&&!data.remoteHost)} onClick={()=>chooseThread(thread.id)}><span>{thread.running&&<span className="dai-dot working" aria-label="Выполняется"/>}{thread.name||"Новый чат"}</span></Action></div>)}
 </div></GameScroll>:null;
 const speak=(id:string,text:string)=>{
  const synth=(window as unknown as {speechSynthesis?:SpeechSynthesis}).speechSynthesis;
  if(!synth)return;
  if(speaking===id){synth.cancel();setSpeaking("");return;}
  synth.cancel();
  const utterance=new SpeechSynthesisUtterance(text.slice(0,4000));
  utterance.lang=/[а-яё]/i.test(text)?"ru-RU":"en-US";
  utterance.onend=utterance.onerror=()=>setSpeaking("");
  setSpeaking(id);synth.speak(utterance);
 };
 const copyMessage=(text:string)=>void run(async()=>{
  const doc=chatRef.current?.ownerDocument||document;
  try{await doc.defaultView!.navigator.clipboard.writeText(text);}
  catch{
   const focused=doc.activeElement as HTMLElement|null;
   const field=doc.createElement("textarea");field.value=text;field.style.cssText="position:fixed;left:0;top:0;opacity:0";doc.body.appendChild(field);field.select();
   try{if(!doc.execCommand("copy"))throw new Error("Не удалось скопировать. Выделите текст сообщения для копирования.");}
   finally{field.remove();focused?.focus();}
  }
  setNotice("Текст скопирован");
 });
 const jumpToLatest=()=>{followTail.current=true;setShowLatest(false);const el=chatRef.current;if(el)el.scrollTop=el.scrollHeight;};
 const settings=(id:string,depth:string,speed:string)=>void run(async()=>{await saveSettings(id,depth,speed);accept(await snapshot());});
 const attach=(media?:Media)=>{if(!media)return;setImages(old=>old.some(x=>x.path===media.path)?old:[...old,media]);setMediaOpen(false);};
 const signIn=()=>void run(async()=>{const result=await accountLogin();setLoginUrl(result.url+(result.userCode?" · Код: "+result.userCode:""));setNotice(result.opened?"Откройте страницу входа и завершите авторизацию.":"Ссылка для входа показана ниже.");accept(await snapshot());});
 const disconnect=!data?.ready;
 return <Focusable style={{"--dai-text-scale":textScale} as CSSProperties} data-text-scale={textScale} data-theme={appearance.theme} data-density={appearance.density} data-bubbles={appearance.bubbles} data-layout={layout} className={"dai-root"+(fullscreen?" dai-fullscreen":"")} onSecondaryButton={()=>{if(tab==="chat"&&!busy)void toggleVoice();}} onSecondaryActionDescription={tab==="chat"?(recording?"Стоп":"Голос"):undefined} onCancel={event=>{
  if(queueOpen){event.stopPropagation();setQueueOpen(false);}
  else if(mediaOpen){event.stopPropagation();setMediaOpen(false);}
  else if(fullscreen){event.stopPropagation();closeFullscreen();}
 }}><style>{css}</style><span ref={touchAnchor} hidden/>
  {fullscreen&&<Focusable className="dai-full-header" flow-children="horizontal">
   <div className="dai-full-brand"><h1>Deck AI</h1><span>{tab==="repair"?"Локальная диагностика":disconnect?"Нет соединения":data?.active?"Deck AI работает…":gameStatus}</span></div>
   <GameCheckbox checked={gameContextEnabled} onChange={toggleGameContext}/>
   <Action onClick={()=>closeFullscreen()}><FaCompress/>В панель</Action>
   <Action onClick={()=>closeFullscreen(false)}><FaArrowLeft/>К игре</Action>
  </Focusable>}
  <Focusable className="dai-tabs" flow-children="horizontal" role="tablist" aria-label="Deck AI">
   {([["chat","Чат",<FaComment/>],["history","История",<FaHistory/>],["repair","Ремонт",<FaGamepad/>],["settings","Настройки",<FaCog/>]] as const).map(([id,label,icon])=><div key={id} role="tab" aria-selected={tab===id} className={"dai-tab "+(tab===id?"selected":"")}><Action disabled={busy} onClick={()=>{if((id==="settings"||id==="repair")&&!fullscreen)openFullscreen(id);else{setTab(id);setMediaOpen(false);setQueueOpen(false);}}}>{icon}<span>{label}</span></Action></div>)}
  </Focusable>
  <div className="dai-viewbar"><div className="dai-status"><span className={"dai-dot "+(disconnect?"offline":data?.active?"working":"")}/><span>{!data?"Подключение…":data.ready?(data.active?"Deck AI работает…":gameStatus):(data.retryIn?`Нет связи · повтор через ${data.retryIn} с`:"Нет соединения")}</span>{data?.remoteHost&&<small>{data.remoteHost}</small>}{!!data?.runningCount&&<small className="dai-running-count">{data.runningCount} в работе</small>}</div>{!fullscreen&&<GameCheckbox checked={gameContextEnabled} onChange={toggleGameContext}/>}{!fullscreen&&<Action disabled={busy} onClick={()=>openFullscreen(tab)}><FaExpand/>На весь экран</Action>}</div>
  {tab!=="repair"&&(error||connectionError)&&<div className="dai-banner" role="alert"><span>{error||connectionError}</span><Action onClick={()=>{setError("");setConnectionError("");}}>Закрыть</Action></div>}
  {tab!=="repair"&&!error&&!connectionError&&(data?.historyWarning||data?.ready===false)&&<div className="dai-banner" role="status"><span>{data.historyWarning||data.status}</span><Action disabled={busy} onClick={()=>void run(async()=>{accept(await refresh());})}>Повторить подключение</Action></div>}
  {notice&&<div className="dai-notice" role="status">{notice}</div>}
  <div className="dai-page" role="tabpanel" aria-label={tab==="chat"?"Чат":tab==="history"?"История":tab==="repair"?"Ремонт":"Настройки"}>
  {tab==="repair"&&<GameScroll className="dai-scroll dai-stack"><RepairPanel copy={copyMessage}/></GameScroll>}
  {tab==="chat"&&<div className="dai-chat-layout">{sidebar}<div className={"dai-chat-main"+(data?.approvals?.length?" has-approvals":"")}>
   {queueOpen?<GameScroll key="queue" ref={queueRef} className="dai-scroll dai-stack dai-queue-view"><div className="dai-stack-content">
    <Action onClick={()=>setQueueOpen(false)}>← К сообщению</Action>
    <h3>Очередь запросов · {data?.queueTotal??data?.outbox.length??0}</h3>
    <p className="dai-muted">Ожидающие запросы ещё не отправлены. Запросы выполняются по очереди; занятый чат ждёт завершения текущего ответа.</p>
    <p className="dai-muted">В этом чате ожидают: {queueCounts(data?.outbox||[],data?.threadId||"").current}. В других чатах: {queueCounts(data?.outbox||[],data?.threadId||"").other}.</p>
    {(data?.queueTotal||0)>(data?.outbox.length||0)&&<p className="dai-muted">Показаны последние {data?.outbox.length} запросов.</p>}
    {!data?.outbox.length&&<p className="dai-muted">Очередь пуста.</p>}
    {data?.outbox.map(job=><section className="dai-section dai-queue-item" key={job.id}>
     <strong>{queueStatus(job)}</strong>
     <small className="dai-muted">{job.threadId===data.threadId?"Этот чат":(data.threads.find(thread=>thread.id===job.threadId)?.name||"Другой чат").slice(0,80)}{job.createdAt?" · "+new Date(job.createdAt*1000).toLocaleString():""}</small>
     <p className="dai-queue-text">{expandedJob===job.id?job.text:job.text.slice(0,180)+(job.text.length>180?"…":"")}</p>
     {job.text.length>180&&<Action onClick={()=>setExpandedJob(expandedJob===job.id?"":job.id)}>{expandedJob===job.id?"Свернуть текст":"Весь текст запроса"}</Action>}
     {job.error&&<p className="dai-muted">{job.error}</p>}
     {job.status==="queued"&&<Action disabled={busy||ro} onClick={()=>void run(async()=>{await queueFront(job.id);accept(await snapshot());})}>↑ Отправить первым</Action>}
     {(job.status==="queued"||job.status==="error")&&<Action disabled={busy||ro} onClick={()=>void run(async()=>{await queueRemove(job.id);accept(await snapshot());})}>Удалить из очереди</Action>}
     {job.threadId&&<Action disabled={busy} onClick={()=>void run(async()=>{if((job.host||"")!==(data?.remoteHost||""))accept(await remoteHost(job.host||""));accept(await selectThread(job.threadId!));setTab("chat");setQueueOpen(false);})}>Открыть чат</Action>}
    </section>)}
   </div></GameScroll>:mediaOpen?<GameScroll className="dai-scroll dai-stack"><div className="dai-stack-content">
    <Action onClick={()=>setMediaOpen(false)}>← К сообщению</Action>
    <section className="dai-section dai-game-context"><h3><FaGamepad/> Контекст игры</h3>
     <p className="dai-muted">{game?game.name:"Сейчас Steam не сообщает о запущенной игре."}</p>
     {game&&<p className="dai-muted">{game.status||"Игра не передаёт описание текущего места или задания."}</p>}
     {game?.details.map(([key,value])=><p className="dai-muted" key={key}>{key}: {value}</p>)}
     <GameCheckbox checked={gameContextEnabled} onChange={toggleGameContext}/>
     {game&&<Action disabled={!currentScreenshots.length} onClick={()=>attach(currentScreenshots[0])}>Снимок из этой игры{currentScreenshots[0]?.when?" · "+new Date(currentScreenshots[0].when*1000).toLocaleString():""}</Action>}
     <p className="dai-muted">Чтобы показать, где вы сейчас: сделайте снимок в игре — Steam + R1, затем прикрепите его здесь. Галочка «Игра» добавляет к вопросу только название игры.</p>
    </section>
    <h3>Другие вложения</h3>
    <Action disabled={!data?.screenshots.length} onClick={()=>attach(data?.screenshots[0])}>Последний скриншот</Action>
    <Choice label="Другой скриншот" value={shot} options={(data?.screenshots||[]).map(x=>({data:x.path,label:x.name}))} onChange={setShot}/>
    <Action disabled={!shot} onClick={()=>attach(data?.screenshots.find(x=>x.path===shot))}>Прикрепить скриншот</Action>
    <Choice label="Видеозапись" value={video} options={(data?.videos||[]).map(x=>({data:x.path,label:x.name}))} onChange={setVideo}/>
    <Action disabled={!video||busy} onClick={()=>void run(async()=>{const result=await videoFrames(video);setImages(old=>[...old,...result.frames]);setMediaOpen(false);})}>Добавить кадры из видео</Action>
    {!data?.screenshots.length&&!data?.videos.length&&<p className="dai-muted">Сделайте скриншот в игре: Steam + R1. Он появится здесь.</p>}
   </div></GameScroll>:<>
    <Focusable className="dai-toolbar" flow-children="horizontal">
     <Action disabled={busy||disconnect||ro||data?.active} onClick={startChat}><FaPlus/><span>Новый</span></Action>
     <Action disabled={busy||disconnect} onClick={openFiles}><FaFolderOpen/><span>Файлы</span></Action>
     <Action onClick={()=>setQueueOpen(true)}><FaListUl/><span>Очередь{(data?.queueTotal||data?.outbox.length)?" · "+(data?.queueTotal??data?.outbox.length):""}</span></Action>
     <Action disabled={busy} onClick={()=>void run(async()=>{accept(await refresh());setNotice("Обновлено");})}><FaSyncAlt/><span>Обновить</span></Action>
    </Focusable>
    <GameScroll className="dai-messages" ref={chatRef} onScroll={()=>{const el=chatRef.current;if(el){followTail.current=el.scrollHeight-el.scrollTop-el.clientHeight<60;setShowLatest(!followTail.current);}}}>
     <div className="dai-message-list">{!data?.messages.length&&<div className="dai-empty"><FaComment/><h3>Помощь прямо в игре</h3><p>Задайте вопрос текстом или голосом.<br/>Можно добавить скриншот.</p>{disconnect&&<Action onClick={()=>void run(async()=>accept(await refresh()))} disabled={busy}>{busy?"Подключение…":"Подключиться"}</Action>}</div>}
     {data?.hasOlderMessages&&<Action disabled={busy} onClick={()=>void run(async()=>{followTail.current=false;accept(await olderMessages());requestAnimationFrame(()=>{if(chatRef.current)chatRef.current.scrollTop=0;});})}>Показать предыдущие сообщения</Action>}
     {data?.messages.map((message,i)=>message.role==="tool"?<Focusable key={message.id||i} className="dai-message tool" focusClassName="dai-focused" onActivate={()=>setOpenTool(openTool===(message.id||String(i))?"":(message.id||String(i)))}><pre>{openTool===(message.id||String(i))?message.text:message.text.split("\n").slice(0,3).join("\n")+(message.text.split("\n").length>3?"\n…":"")}</pre></Focusable>:<Focusable key={message.id||i} className={"dai-message "+message.role} focusClassName="dai-focused"><small>{message.role==="user"?"Вы":names[data.provider]?.split(" · ")[0]||"AI"}</small><div>{message.text}</div>{!!message.attachments?.length&&<MessageAttachments items={message.attachments}/>}<div className="dai-message-tools"><Action onClick={()=>copyMessage(message.text)}><FaCopy/>Копировать</Action>{message.role==="assistant"&&!!(window as unknown as {speechSynthesis?:unknown}).speechSynthesis&&<Action onClick={()=>speak(message.id||String(i),message.text)}>{speaking===(message.id||String(i))?"■ Стоп":"🔊 Озвучить"}</Action>}</div></Focusable>)}
     {(data?chatFailures(data.outbox,data.threadId,data.remoteHost||""):[]).map(x=><div className="dai-failed" key={x.id}><p>{x.error||"Не удалось отправить"}</p><Action disabled={busy} onClick={()=>void run(async()=>{await retry(x.id);accept(await snapshot());})}>Повторить отправку</Action></div>)}
    </div></GameScroll>
    {showLatest&&<div className="dai-latest"><Action onClick={jumpToLatest}>↓ К последнему сообщению</Action></div>}
    {ro&&<div className="dai-notice" role="status">Режим только чтения: отправка, подтверждения и правки отключены.</div>}
    {!!data?.approvals?.length&&<GameScroll className="dai-approvals" role="alert">{data.approvals.map(item=><div className="dai-approval" key={item.key}><strong>Нужно подтверждение · {item.title}</strong><span className="dai-muted">{item.summary}</span><Focusable className="dai-compose-actions" flow-children="horizontal"><Action primary disabled={busy||ro} onClick={()=>decide(item,"accept")}>{confirmApproval===item.key?"Нажмите ещё раз":"Разрешить"}</Action><Action disabled={busy||ro} onClick={()=>decide(item,"decline")}>Отклонить</Action></Focusable></div>)}</GameScroll>}
    <div className="dai-composer">
     {countdown!==null&&<div className="dai-notice" role="status">Отправка через {countdown} с<Action onClick={()=>setCountdown(null)}>Отменить отправку</Action></div>}
     {quickOpen&&data?.threadId&&<Focusable className="dai-quick" flow-children="horizontal">{quickActions.map(([label,text])=><Action key={label} disabled={busy||disconnect||ro} onClick={()=>quick(text)}>{label}</Action>)}</Focusable>}
     {data?.outbox.some(job=>job.status==="recovering")&&<p className="dai-muted dai-queue-state" role="status">Проверяю состояние отправленного запроса…</p>}
     {!!data?.outbox.length&&<div className="dai-queue-summary"><Action onClick={()=>setQueueOpen(true)}>Очередь · {data.queueTotal??data.outbox.length} · посмотреть</Action></div>}
     {images.length>0&&<div className="dai-attachments">{images.map((image,i)=><Action key={image.path+":"+i} onClick={()=>setImages(old=>old.filter((_,n)=>n!==i))}>× {image.name}</Action>)}</div>}
     {(recording||voiceProcessing)&&<div className="dai-voice-preview" role="status" aria-live="polite"><span className="dai-record-dot" aria-hidden="true"/><div><strong>{recording?"● Запись · распознанный текст":"Завершаю распознавание…"}</strong><span role="textbox" aria-label="Распознанная речь" aria-readonly="true">{(data?.voiceId!==session.discardedVoice?data?.voiceText:"")||(["ru","en","ru-fast","en-fast"].includes(lang)?"Здесь появится распознанная речь":"Записываю. Текст появится после «Стоп».")}</span></div></div>}
     <form style={{display:"contents"}} onSubmit={e=>{e.preventDefault();submit();}}><div className="dai-draft-field" key={data?.threadId||"new"} data-draft-owner={data?.threadId||""} onInputCapture={e=>{const target=e.target as HTMLInputElement;if(target.tagName==="INPUT")editDraft(target.value,e.currentTarget.dataset.draftOwner||"");}}><TextField disabled={recording||voiceProcessing} value={draft} placeholder="Спросить об игре…" onChange={e=>editDraft(e.target.value,e.target.closest<HTMLElement>(".dai-draft-field")?.dataset.draftOwner??draftId.current)} onKeyDown={e=>{if((e.key==="Enter"||e.keyCode===13)&&!e.shiftKey&&!(e.nativeEvent as KeyboardEvent).isComposing){e.preventDefault();submit();}}}/></div></form>
     <Focusable className="dai-compose-actions" flow-children="horizontal">
      <Action recording={recording||voiceProcessing} disabled={!data||voiceProcessing||busy} onClick={()=>void toggleVoice()}><FaMicrophone/>{recording?"Стоп":"Голос"}</Action>
      {!!data?.threadId&&<Action disabled={recording||voiceProcessing} onClick={()=>setQuickOpen(!quickOpen)}>⚡</Action>}
      <Action disabled={voiceStarting||(!draft.trim()&&!recording&&!voiceProcessing)} onClick={clearDraft}>Очистить</Action>
      {fullscreen&&data?.active&&data.provider==="codex"&&<Action disabled={busy} onClick={()=>void run(async()=>{await stop();accept(await snapshot());})}>Стоп</Action>}
      <Action primary disabled={busy||disconnect||ro||recording||voiceProcessing||!draft.trim()} onClick={submit}>{busy?"…":"Отправить"}</Action>
     </Focusable>
     {!fullscreen&&data?.active&&data.provider==="codex"&&<Action disabled={busy} onClick={()=>void run(async()=>{await stop();accept(await snapshot());})}>Остановить ответ</Action>}
    </div>
   </>}
  </div></div>}
  {tab==="history"&&filesOpen&&<GameScroll className="dai-scroll dai-stack"><div className="dai-stack-content">
   <Action onClick={()=>{if(file)setFile(null);else setFilesOpen(false);}}>← {file?"К папке":"Назад"}</Action>
   <h3>{file?file.path.split("/").pop():folder}</h3>
   {!file&&<><Action onClick={()=>openFolder(parentPath(folder))}>⬑ Вверх</Action>
    {entries.map(name=><Action key={name} disabled={busy} onClick={()=>isFolder(name)?openFolder(joinPath(folder,name)):openFile(joinPath(folder,name))}>{isFolder(name)?"📁 ":"📄 "}{name}</Action>)}
    {!entries.length&&<p className="dai-muted">Папка пуста. Доступна только домашняя папка; ключи и секреты скрыты.</p>}</>}
   {file&&<><textarea className="dai-textarea" value={fileText} spellCheck={false} onChange={e=>setFileText(e.target.value)}/>
    <p className="dai-muted">{fileText===file.text?"Без изменений":"Есть несохранённые правки"} · до 64 КБ · перед записью создаётся копия .deckai.bak</p>
    <Action primary disabled={busy||ro||fileText===file.text} onClick={saveFile}>Сохранить на устройстве</Action>
    <Action disabled={busy||fileText===file.text} onClick={()=>setFileText(file.text)}>Отменить правки</Action></>}
  </div></GameScroll>}
  {tab==="history"&&!filesOpen&&<GameScroll className="dai-scroll dai-stack"><div className="dai-stack-content">
   <Action primary disabled={busy||disconnect||ro||data?.active} onClick={()=>void run(async()=>{accept(await newThread());setTab("chat");})}>＋ Новый чат</Action>
   <Action disabled={busy||disconnect} onClick={()=>{setFilesOpen(true);openFolder("~");}}>📁 Файлы на устройстве{data?.remoteHost?" · "+data.remoteHost:""}</Action>
   {!!data?.recentEvents?.length&&<section className="dai-section dai-events"><h3>Что произошло</h3>{data.recentEvents.slice(0,8).map(item=><p className="dai-muted" key={item.id}>{item.kind==="approval"?"⏸":item.kind==="failed"?"✗":"✓"} {new Date(item.at*1000).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})} · {(item.host||"Steam Deck")+" · "+item.title}</p>)}</section>}
   {(data?.provider==="codex"||!data)&&<Choice label="Устройство" value={data?.remoteHost||""} options={[{data:"",label:"Этот Steam Deck"},...(data?.sshHosts||[]).map(x=>({data:x,label:x}))]} disabled={busy||data?.active} onChange={value=>void run(async()=>accept(await remoteHost(value)))}/>}
   {data?.remoteHost&&<Action disabled={busy} onClick={()=>void run(async()=>{accept(await refresh());setNotice("Список задач обновлён");})}>↻ Обновить задачи на {data.remoteHost}</Action>}
   <TextField value={historyQuery} placeholder="Найти разговор…" onChange={e=>setHistoryQuery(e.target.value)}/>
   {(data?.allTasks||[]).some(t=>t.host!==(data?.remoteHost||"")||t.running)&&<section className="dai-section dai-all-tasks"><h3>Задачи на всех устройствах</h3>{(data?.allTasks||[]).filter(t=>t.host!==(data?.remoteHost||"")||t.running).slice(0,12).map(t=><Action key={t.host+":"+t.id} disabled={busy||(data?.active&&!data.remoteHost&&t.host==="")} onClick={()=>void run(async()=>{if(t.host!==(data?.remoteHost||""))accept(await remoteHost(t.host));accept(await selectThread(t.id));setTab("chat");})}><span>{t.running&&<span className="dai-dot working" aria-label="Выполняется"/>}{(t.host||"Steam Deck")+" · "+t.name}</span></Action>)}</section>}
   {!data?.threads.length&&<p className="dai-muted">Ваши разговоры появятся здесь.</p>}
   {data?.threads.filter(x=>x.name.toLocaleLowerCase().includes(historyQuery.toLocaleLowerCase())).sort((a,b)=>Number(!!b.running)-Number(!!a.running)).map(thread=><div className={"dai-history-item "+(thread.id===data.threadId?"selected":"")+(thread.running?" running":"")} key={thread.id}><Action disabled={busy||(data.active&&thread.id!==data.threadId&&!data.remoteHost)} onClick={()=>chooseThread(thread.id)}><span>{thread.running&&<span className="dai-dot working" aria-label="Выполняется"/>}{thread.name||"Новый чат"}</span>{thread.id===data.threadId&&<small>Текущий</small>}</Action></div>)}
  </div></GameScroll>}
  {tab==="settings"&&<GameScroll className="dai-scroll dai-stack dai-settings"><div className="dai-settings-grid"><div className="dai-settings-column">
   <section className="dai-section dai-model-settings"><h3>Модель и ответ</h3><div className="dai-model-fields">
    <Choice label="Сервис" value={data?.provider||"codex"} options={Object.entries(names).map(([data,label])=>({data,label}))} disabled={busy||data?.active} onChange={value=>void run(async()=>{accept(await setProvider(value));setKey("");})}/>
    <Choice label="Модель" value={model?.id||""} options={(data?.models||[]).map(x=>({data:x.id,label:x.name}))} disabled={busy} onChange={id=>{const next=data?.models.find(x=>x.id===id);settings(id,next?.defaultEffort||next?.efforts[0]?.id||"","default");}}/>
    {data?.provider==="codex"&&<><Choice label="Глубина обработки" value={effort} options={(model?.efforts||[]).map(x=>({data:x.id,label:x.name}))} disabled={busy} onChange={value=>settings(model?.id||"",value,tier)}/><Choice label="Скорость" value={tier} options={[{data:"default",label:"Обычная"},...(model?.tiers.includes("priority")?[{data:"priority",label:"Приоритетная"}]:[])]} disabled={busy} onChange={value=>settings(model?.id||"",effort,value)}/></>}
    </div>{(data?.provider==="deepseek"||data?.provider==="tokenharbor"||isCustom)&&<><TextField bIsPassword value={key} placeholder="Ключ API" onChange={e=>setKey(e.target.value)}/><Action disabled={busy||!key.trim()} onClick={()=>void run(async()=>{await setProviderKey(key.trim());setKey("");accept(await refresh());setNotice("Ключ сохранён");})}>Сохранить ключ</Action><p className="dai-muted">Ключ хранится в системном хранилище SteamOS.</p></>}
    {data?.provider==="claude"&&<p className="dai-muted">Desktop Mode → Deck AI → + → Подключить Claude Code или Anthropic Console (API). Вход выполняется в официальном CLI: свой аккаунт, API-ключ или облачный доступ. Расходы зависят от способа доступа.</p>}
    {isCustom&&<><p className="dai-muted">Для этого облачного сервиса нужен API-ключ. Он хранится в системном хранилище SteamOS.</p><Action disabled={busy||ro} onClick={()=>showModal(<ConfirmModal strTitle={"Удалить «"+(names[data!.provider]||"")+"»?"} strOKButtonText="Удалить" strCancelButtonText="Отмена" onOK={()=>void run(async()=>{await customRemove(data!.provider);accept(await refresh());})}/>)}>Удалить это подключение</Action></>}
   </section>
   <section className="dai-section dai-appearance"><h3>Оформление</h3>
    <div className="dai-field"><span className="dai-label">Цветовая тема</span>
     <Focusable className="dai-swatches" flow-children="horizontal">{themes.map(theme=><DialogButton key={theme.id} className={"dai-button dai-swatch"+(appearance.theme===theme.id?" dai-selected":"")} aria-pressed={appearance.theme===theme.id} onClick={()=>setAppearanceChoice("theme",theme.id)}><span className="dai-swatch-dot" style={{background:theme.swatch}}/>{theme.name}</DialogButton>)}</Focusable></div>
    <Segmented label="Сообщения" value={appearance.bubbles} options={bubbleStyles} onChange={id=>setAppearanceChoice("bubbles",id)}/>
    <Segmented label="Плотность" value={appearance.density} options={densities} onChange={id=>setAppearanceChoice("density",id)}/>
    <Segmented label="Компоновка" value={appearance.layout} options={layouts} onChange={id=>setAppearanceChoice("layout",id)}/>
    {appearance.layout==="split"&&!fullscreen&&<p className="dai-muted">Две колонки включатся в режиме «На весь экран».</p>}
   </section>
   <section className="dai-section dai-custom-ai"><h3>Свой облачный ИИ</h3>
    <p className="dai-muted">Подойдёт любой облачный сервис с OpenAI-совместимым API: OpenAI, Gemini, Groq, Mistral, DeepSeek, xAI, OpenRouter и другие. Выберите готовый адрес или укажите свой (только https). Локальные серверы не поддерживаются.</p>
    <Focusable className="dai-quick" flow-children="horizontal">{(data?.presets||[]).map(p=><Action key={p.url} onClick={()=>setCustom(old=>({...old,name:old.name||p.name.split(" · ")[0],url:p.url}))}>{p.name}</Action>)}</Focusable>
    <TextField value={custom.name} placeholder="Название (например, Groq)" onChange={e=>setCustom({...custom,name:e.target.value})}/>
    <TextField value={custom.url} placeholder="Адрес API, например https://api.groq.com/openai/v1" onChange={e=>setCustom({...custom,url:e.target.value})}/>
    <TextField value={custom.models} placeholder="Модели через запятую (необязательно)" onChange={e=>setCustom({...custom,models:e.target.value})}/>
    <TextField bIsPassword value={custom.key} placeholder="Ключ API" onChange={e=>setCustom({...custom,key:e.target.value})}/>
    <Action primary disabled={busy||ro||!custom.name.trim()||!custom.url.trim()||!custom.key.trim()} onClick={()=>void run(async()=>{const result=await customSave(custom.name.trim(),custom.url.trim(),custom.models,custom.key.trim());setCustom({name:"",url:"",models:"",key:""});accept(await setProvider(result.id));setNotice("Подключение добавлено");})}>Добавить и выбрать</Action></section>
   <section className="dai-section dai-text-settings"><h3>Интерфейс и голос</h3><div className="dai-personal-fields"><div className="dai-field"><span className="dai-label">Масштаб чата и кнопок</span>
    <Focusable className="dai-scale-controls" flow-children="horizontal">
     <Action disabled={textScale<=.7} onClick={()=>setTextScale(textScale-.1)}>А−</Action>
     <span className="dai-scale-value" aria-live="polite">{Math.round(textScale*100)}%</span>
     <Action disabled={textScale>=1.5} onClick={()=>setTextScale(textScale+.1)}>А+</Action>
     <Action disabled={textScale===1} onClick={()=>setTextScale(1)}>Сброс</Action>
    </Focusable></div>
   <Choice label="Язык распознавания" value={lang} options={!data?.speechReady?[{data:"ru",label:"Русский"},{data:"en",label:"English"}]:[{data:"auto",label:"Определять автоматически"},...Object.entries(speechLanguages).sort(([a],[b])=>a==="ru"?-1:b==="ru"?1:a==="en"?-1:b==="en"?1:0).map(([data,label])=>({data,label})),{data:"ru-fast",label:"Русский · экономный"},{data:"en-fast",label:"English · экономный"}]} onChange={value=>{setLang(value);localStorage.setItem("codex-game-voice",value);}}/></div>
    {data?.speechVersion===2&&!data.speechReady&&<p className="dai-muted">Для других языков установите многоязычную модель: scripts/download-models.sh --accurate-ru</p>}
    <div className="dai-game-setting"><span className="dai-muted">Добавлять только название игры</span><GameCheckbox checked={gameContextEnabled} onChange={toggleGameContext}/></div>
    <div className="dai-game-setting"><span className="dai-muted">Сообщать о готовности задач (уведомления Steam)</span><GameCheckbox checked={notify} onChange={()=>{const next=!notify;localStorage.setItem("deck-ai-notify",next?"on":"off");setNotify(next);}}/></div>
    <div className="dai-game-setting"><span className="dai-muted">Отправлять голосовое сообщение через 3 с после «Стоп»</span><GameCheckbox checked={autoSend} onChange={()=>{const next=!autoSend;localStorage.setItem("deck-ai-auto-send",next?"on":"off");setAutoSend(next);}}/></div>
    <div className="dai-game-setting"><span className="dai-muted">Только чтение (без отправки, подтверждений и правок)</span><GameCheckbox checked={ro} onChange={()=>void run(async()=>{await setReadOnly(!ro);accept(await snapshot());})}/></div>
    <div className="dai-field"><span className="dai-label">Быстрые фразы ⚡ (строка: название | текст)</span><textarea className="dai-textarea dai-textarea-small" value={quickSource??parseQuickActions(null).map(([a,b])=>a===b?a:a+" | "+b).join("\n")} onChange={e=>{setQuickSource(e.target.value);localStorage.setItem("deck-ai-quick",e.target.value);}}/></div>
    <Action disabled={busy||!data?.loadedModels} onClick={()=>void run(async()=>{await unloadModels();accept(await snapshot());setNotice("Модели распознавания выгружены из памяти");})}>Освободить память{data?.loadedModels?` · загружено моделей: ${data.loadedModels}`:""}</Action></section>
   </div><div className="dai-settings-column">
   <section className="dai-section dai-connection-settings"><h3>Подключение Codex</h3><div className="dai-connection-bar">
    <p className="dai-muted">{(data?.active?"Deck AI работает…":data?.status)||"Сервер пока недоступен. Можно повторить подключение."}</p>
    <Action disabled={busy} onClick={()=>void run(async()=>{accept(await refresh());setNotice("Соединение обновлено");})}>{busy?"Подключение…":"Переподключиться"}</Action></div>
    {(!data||data.provider==="codex")&&<><Choice label="Устройство" value={data?.remoteHost||""} options={[{data:"",label:"Этот Steam Deck"},...(data?.sshHosts||[]).map(x=>({data:x,label:x}))]} disabled={busy||data?.active} onChange={value=>void run(async()=>accept(await remoteHost(value)))}/><div className="dai-host-entry"><TextField value={host} placeholder="Другой SSH-алиас" onChange={e=>setHost(e.target.value)}/><Action disabled={busy||!host.trim()||data?.active} onClick={()=>void run(async()=>{accept(await remoteHost(host.trim()));setHost("");})}>Подключить</Action></div></>}
   </section>
   {!!data?.sshHosts.length&&<section className="dai-section dai-watch"><h3>Следить в фоне</h3><p className="dai-muted">Уведомления и подтверждения с этих машин приходят, даже когда они не выбраны. До 5 машин.</p>
    {data.sshHosts.map(name=>{const on=!!data.watchHosts?.includes(name);return <div className="dai-game-setting" key={name}><span className="dai-muted">{name}{on&&data.watchStatus?.[name]?" · "+({connected:"на связи",offline:"нет связи",connecting:"подключаюсь",active:"выбрана"} as Record<string,string>)[data.watchStatus[name]]:""}</span><GameCheckbox checked={on} onChange={()=>void run(async()=>{const next=on?(data.watchHosts||[]).filter(x=>x!==name):[...(data.watchHosts||[]),name];await watchHosts(next);accept(await snapshot());})}/></div>;})}</section>}
   <section className="dai-section dai-share"><h3>Доступ с другого компьютера</h3>
    <p className="dai-muted">Управляйте задачами этого Deck с Mac или ПК по SSH: команды из вашего Codex появятся здесь.</p>
    <Action disabled={busy} onClick={()=>void run(async()=>setShare(await shareStatus()))}>Показать данные подключения</Action>
    {share&&<><p className={"dai-muted dai-check "+(share.sshActive?"ok":"bad")}>{share.sshActive?"✓ SSH-сервер работает":"✗ SSH-сервер выключен"} · ключей: {share.keys}{share.codex?"":" · Codex не найден"}</p>
     {!share.sshActive&&<p className="dai-muted">{share.enableHint}</p>}
     <p className="dai-muted">Пользователь {share.user} · адреса: {share.addresses.join(", ")||"не найдены"}</p>
     <p className="dai-muted">На Mac или ПК запустите мастер connect-deck.py из архива Remote Control. Адрес устройства указан выше.</p><p className="dai-muted">Отпечатки SSH для проверки первого соединения:</p><pre className="dai-snippet">{(share.fingerprints||[]).join("\n")||"SSH ещё не создал ключи: сначала включите сервер."}</pre><p className="dai-muted">Для ручной настройки ~/.ssh/config:</p><pre className="dai-snippet">{share.snippet}</pre>
     <p className="dai-muted">Вставьте публичный ключ из мастера на Mac или ПК:</p>
     <TextField value={shareKey} placeholder="ssh-ed25519 AAAA…" onChange={e=>setShareKey(e.target.value)}/>
     <Action disabled={busy||ro||!shareKey.trim()} onClick={()=>void run(async()=>{const result=await shareAddKey(shareKey.trim());setShareKey("");setShare(await shareStatus());setNotice(result.added?"Ключ добавлен":"Такой ключ уже есть");})}>Разрешить этому компьютеру</Action></>}
   </section>
   <section className="dai-section dai-diagnostics"><h3>Диагностика</h3>
    <Action disabled={busy} onClick={()=>void run(async()=>{setChecks(null);const result=await diagnose();setChecks(result.checks);})}>{busy?"Проверяю…":"Проверить подключение"}</Action>
    {checks?.map(check=><p className={"dai-muted dai-check "+(check.ok?"ok":"bad")} key={check.name}>{check.ok?"✓":"✗"} {check.name}{check.detail?" · "+check.detail:""}</p>)}</section>
   <section className="dai-section dai-account-settings"><h3>Аккаунт ChatGPT</h3>
    <div className="dai-account-meta"><p className="dai-account">{data?.account?.email||"Вход не выполнен"}</p>{data?.account?.planType&&<p className="dai-muted">{data.account.planType}</p>}</div><div className="dai-account-actions">
    <Action disabled={busy} onClick={signIn}>{data?.account?"Сменить аккаунт":"Войти в аккаунт"}</Action>
    {data?.loginPending&&<Action disabled={busy} onClick={()=>void run(async()=>{await accountCancelLogin();setLoginUrl("");accept(await snapshot());})}>Отменить вход</Action>}
    {loginUrl&&<p className="dai-login-url">{loginUrl}</p>}
    {data?.account&&<Action disabled={busy} onClick={()=>showModal(<ConfirmModal strTitle="Выйти из ChatGPT?" strDescription="Для работы Codex потребуется снова войти." strOKButtonText="Выйти" strCancelButtonText="Отмена" onOK={()=>void run(async()=>{await accountLogout();accept(await refresh());})}/>)}>Выйти из аккаунта</Action>}
   </div></section>
  </div></div></GameScroll>}
  </div>
 </Focusable>;
}
let lastEvent:number|null=null;
async function showNotifications(){
 try{
  const result=await pollEvents(lastEvent);
  const first=lastEvent===null;lastEvent=result.latest;
  // The open panel already shows approvals and results; do not toast on top.
  if(first||panelMounted>0||!flag("deck-ai-notify",true))return;
  for(const item of result.notifications.slice(-3)){
   const where=item.host?" · "+item.host:"";
   toaster.toast({
    title:item.kind==="approval"?"Deck AI · нужно подтверждение":item.kind==="failed"?"Deck AI · ошибка":item.kind==="cancelled"?"Deck AI · задача остановлена":"Deck AI · задача готова",
    body:(item.kind==="approval"&&item.summary?item.summary:item.title)+where,
    critical:item.kind==="approval",duration:item.kind==="approval"?15000:6000,
    onClick:()=>{void(async()=>{
     try{if((session.snapshot?.remoteHost||"")!==item.host)await remoteHost(item.host);
      if(item.threadId)session.snapshot=await selectThread(item.threadId);
     }finally{openFullscreen("chat");}
    })().catch(()=>{});}
   });
  }
 }catch{}
}
export default definePlugin(()=>{
 routerHook.addRoute(FULLSCREEN_PATH,FullscreenPage,{exact:true});
 void showNotifications();
 const notifier=setInterval(()=>void showNotifications(),2000);
 const stopRepairPolling=startRepairPolling();
 return {name:"Deck AI",titleView:<span>Deck AI</span>,content:<Panel/>,icon:<img src={logo} alt="Deck AI" style={{width:20,height:20,objectFit:"contain"}}/>,onDismount(){
  if(returnToPanel)clearTimeout(returnToPanel);
  clearInterval(notifier);
  stopRepairPolling();
  routerHook.removeRoute(FULLSCREEN_PATH);
 }};
});
