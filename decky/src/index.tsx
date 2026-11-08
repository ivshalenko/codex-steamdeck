import { UpdatesPanel } from './updates-panel';
import { updateStore, startUpdatePolling, type UpdateState } from './updates';
import { t, systemText, getUILanguage, setUILanguage, subscribeUILanguage, speechLanguageName, type UILanguage } from "./i18n";
import { useCallback, useEffect, useRef, useState, type CSSProperties, type ReactNode, type ComponentType, type HTMLAttributes, type RefAttributes } from "react";
import { callable, definePlugin, routerHook, toaster } from "@decky/api";
import { DialogButton, Dropdown, Focusable, TextField, ConfirmModal, showModal, ScrollPanel, Navigation, Router } from "@decky/ui";
import {workspaceNavigation} from './navigation';
import {LibraryPanel} from './library-panel';
import {Icon} from './icons';
import {BrandLogo,Handheld} from './brand';
import css from "./style.css";
import { appendAttachments, createDraftStore, createSnapshotReader, createViewGate, draftOwner } from "./drafts";
import { chatFailures, queueCounts, queueStatus, sameChat, type QueueJob } from "./queue";
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
type Item = {id:string;role:"user"|"assistant"|"tool";text:string;textEn?:string;attachments?:Attachment[]};
type Media = {path:string;name:string;when?:number};
type Approval={key:string;id:string|number;threadId:string;title:string;summary:string};
type TaskRow={host:string;id:string;name:string;updatedAt:number;running:boolean};
type DeviceEvent={id:number;kind:string;title:string;host:string;at:number;summary?:string};
type Share={fingerprints?:string[];sshActive:boolean;user:string;hostname:string;addresses:string[];keys:number;codex:boolean;snippet:string;enableHint:string};
type Check={name:string;ok:boolean;detail:string};
type Model = {id:string;name:string;efforts:{id:string;name:string}[];defaultEffort:string;tiers:string[]};
type Snapshot = {uiLanguage?:UILanguage;historyWarning?:string;hasOlderMessages?:boolean;ready:boolean;status:string;provider:string;account?:{email?:string;planType?:string}|null;loginPending?:boolean;remoteHost?:string;sshHosts:string[];threads:{id:string;name:string;updatedAt:number;running?:boolean}[];runningCount?:number;approvals?:Approval[];retryIn?:number;allTasks?:TaskRow[];loadedModels?:number;readOnly?:boolean;watchHosts?:string[];watchStatus?:Record<string,string>;recentEvents?:DeviceEvent[];customProviders?:{id:string;name:string;baseUrl:string}[];presets?:{name:string;url:string}[];threadId:string;messages:Item[];active:boolean;models:Model[];model:string;effort:string;tier:string;screenshots:Media[];videos:Media[];outbox:QueueJob[];queueTotal?:number;speechVersion?:number;speechReady?:boolean;voiceId?:string;voiceState:string;voiceText:string;voiceError:string};
const snapshot=callable<[],Snapshot>("get_snapshot");
const refresh=callable<[],Snapshot>("refresh");
const saveInterfaceLanguage=callable<[language:UILanguage],{uiLanguage:UILanguage}>("set_interface_language");
type KeyboardStatus={supported:boolean;enabled:boolean;active:boolean;restartRequired:boolean;conflict:boolean;sessionActive:boolean};
const keyboardStatus=callable<[],KeyboardStatus>('keyboard_status');
const configureKeyboard=callable<[enabled:boolean],KeyboardStatus>('keyboard_configure');
const selectThread=callable<[id:string],Snapshot>("select_thread");
const newThread=callable<[],Snapshot>("new_thread");
const saveSettings=callable<[model:string,effort:string,tier:string],unknown>("save_settings");
type SendContext={provider:string;host:string;threadId:string};
const sendContext=(value:Snapshot):SendContext=>({provider:value.provider,host:value.remoteHost||"",threadId:value.threadId});
const sendMessage=callable<[text:string,images:string[],model:string,effort:string,tier:string,expected:SendContext],{queued:boolean;threadId?:string}>("send_message");
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
const updateClient={
 status:callable<[],UpdateState>('update_status'),check:callable<[],UpdateState>('update_check'),
 configure:callable<[automatic:boolean,channel:string],UpdateState>('update_preferences'),
 begin:callable<[version:string,workspaceClean:boolean],UpdateState>('update_begin'),
 acknowledge:callable<[version:string],unknown>('update_ack')
};
const pollEvents=callable<[since:number|null],{uiLanguage?:UILanguage;latest:number;notifications:{id:number;kind:string;title:string;host:string;summary?:string;threadId?:string}[]}>("poll_events");
const approve=callable<[id:string,decision:string],unknown>("approve");
const diagnose=callable<[],{checks:Check[]}>("diagnose");
const watchHosts=callable<[hosts:string[]],unknown>("watch");
const setReadOnly=callable<[value:boolean],unknown>("read_only");
const queueFront=callable<[id:string],unknown>("queue_front");
const queueRemove=callable<[id:string],unknown>("queue_remove");
const fileList=callable<[path:string,host?:string],{path:string;entries:string[];host:string}>("file_list");
const fileRead=callable<[path:string,host?:string],{path:string;text:string;sha256:string;host:string}>("file_read");
const fileWrite=callable<[path:string,text:string,expected:string,host?:string],{saved:boolean;sha256:string}>("file_write");
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
const readPolledSnapshot=createSnapshotReader(snapshot);
function Action({children,onClick,disabled=false,primary=false,recording=false,selected}:{children:ReactNode;onClick:()=>void;disabled?:boolean;primary?:boolean;recording?:boolean;selected?:boolean}) {
 return <DialogButton className={"dai-button"+(primary?" dai-primary":"")+(recording?" dai-recording":"")+(selected?" dai-selected":"")} aria-pressed={selected} disabled={disabled} onClick={onClick}>{children}</DialogButton>;
}
function Segmented({label,value,options,onChange}:{label:string;value:string;options:readonly {id:string;name:string}[];onChange:(id:string)=>void}){
 return <div className="dai-field"><span className="dai-label">{label}</span><Focusable className="dai-segmented" flow-children="horizontal">{options.map(option=><Action key={option.id} selected={value===option.id} onClick={()=>onChange(option.id)}>{t(option.name)}</Action>)}</Focusable></div>;
}
function MessageAttachments({items}:{items:Attachment[]}){
 return <div className="dai-message-attachments">{items.map(item=><div className="dai-message-attachment" key={item.id}>
  {item.preview?<DialogButton className="dai-image-button" onClick={()=>showModal(<ConfirmModal strTitle={item.name.length>48?item.name.slice(0,45)+"…":item.name} strOKButtonText={t("Закрыть")} bAlertDialog><img className="dai-image-expanded" style={{display:"block",maxWidth:"100%",maxHeight:"55vh",width:"auto",height:"auto",objectFit:"contain",margin:"auto"}} src={item.preview} alt={item.name}/></ConfirmModal>)}><img src={item.preview} alt={item.name}/></DialogButton>:<span className="dai-muted">📎 {item.name} · {item.kind==="image"?t("изображение недоступно"):t("файл")}</span>}
 </div>)}</div>;
}
function GameCheckbox({checked,onChange}:{checked:boolean;onChange:()=>void}){
 return <div className="dai-game-check" role="checkbox" aria-checked={checked} aria-label={t("Игра")}><DialogButton className="dai-button" onClick={onChange}><span className="dai-check-box" aria-hidden="true">{checked?"✓":""}</span>{t("Игра")}</DialogButton></div>;
}
function Choice({label,value,options,onChange,disabled=false}:{label:string;value:string;options:{data:string;label:string}[];onChange:(value:string)=>void;disabled?:boolean}) {
 return <div className="dai-field"><span className="dai-label">{label}</span><Dropdown menuLabel={label} selectedOption={value} rgOptions={options} disabled={disabled||!options.length} strDefaultLabel={t("Выберите…")} onChange={item=>onChange(String(item.data))}/></div>;
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
const workspace=workspaceNavigation(localStorage,window);
let fullscreenOrigin=Router.MainRunningAppID?"/apprunning":"/";
let returnToPanel:ReturnType<typeof setTimeout>|undefined;
function openFullscreen(tab:Tab){
 workspace.request(tab);
 const current=window.location.pathname.replace(/^\/routes/,"")||"/";
 if(current!==FULLSCREEN_PATH)fullscreenOrigin=current;
 if(returnToPanel)clearTimeout(returnToPanel);
 // Steam can retain a mounted workspace in another browser context.
 // Deliver the requested tab even when that context reports another pathname.
 if(current!==FULLSCREEN_PATH)Navigation.Navigate(FULLSCREEN_PATH);
 Navigation.CloseSideMenus();
}
function closeFullscreen(panel=true){
 if(returnToPanel)clearTimeout(returnToPanel);
 // Replace the workspace entry: old duplicate /deck-ai history entries must
 // never trap Back/Return to game on the same full-screen page.
 Router.Navigate(fullscreenOrigin,true);
 if(panel)returnToPanel=setTimeout(()=>Navigation.OpenQuickAccessMenu(999),150);
}
function FullscreenPage(){return <Panel fullscreen initialTab={workspace.current()}/>;}
function Panel({fullscreen=false,initialTab="chat"}:{fullscreen?:boolean;initialTab?:Tab}) {
 const [uiLanguage,updateUILanguage]=useState(getUILanguage);
 useEffect(()=>subscribeUILanguage(updateUILanguage),[]);
 const [textScale,setTextScale]=useTextScale();
 const [appearance,setAppearanceChoice]=useAppearance();
 const layout=effectiveLayout(appearance.layout,fullscreen);
 const [gameContextEnabled,toggleGameContext]=useGameContextEnabled();
 const [data,setData]=useState<Snapshot|null>(session.snapshot);
 const [tab,setTab]=useState<Tab>(initialTab);
 const [physicalKeyboard,setPhysicalKeyboard]=useState<KeyboardStatus|null>(null);
 useEffect(()=>{let cancelled=false;void keyboardStatus().then(value=>{if(!cancelled)setPhysicalKeyboard(value);}).catch(()=>{});return()=>{cancelled=true;};},[tab]);
 useEffect(()=>{
  if(!fullscreen)return;
  const change=(next:Tab)=>{setTab(next);setMediaOpen(false);setQueueOpen(false);};
  return workspace.subscribe(change);
 },[fullscreen]);
 const [draft,setDraft]=useState(()=>drafts.read(draftOwner(session.snapshot)));
 const draftId=useRef(draftOwner(session.snapshot));
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
 const pendingAuto=useRef<{owner:string;text:string}|null>(null);
 const countdownDraft=useRef<{owner:string;text:string}|null>(null);
 const [quickOpen,setQuickOpen]=useState(false);
 const [quickSource,setQuickSource]=useState<string|null>(()=>localStorage.getItem("deck-ai-quick"));
 const quickActions=parseQuickActions(quickSource);
 const autoSendRef=useRef(autoSend);autoSendRef.current=autoSend;
 const [confirmApproval,setConfirmApproval]=useState("");
 const [filesOpen,setFilesOpen]=useState(false);
 const [folder,setFolder]=useState("~");
 const [folderHost,setFolderHost]=useState("");
 const [entries,setEntries]=useState<string[]>([]);
 const [file,setFile]=useState<{path:string;text:string;sha256:string;host:string}|null>(null);
 const [fileText,setFileText]=useState("");
 const updateView=useRef(Symbol('deck-ai-view'));
 const updateDirty=!!file&&fileText!==file.text||images.length>0||countdown!==null;
 useEffect(()=>{const id=updateView.current;updateStore.block(id,updateDirty);return()=>updateStore.block(id,false);},[updateDirty]);

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
  if(incoming.uiLanguage&&incoming.uiLanguage!==getUILanguage())setUILanguage(incoming.uiLanguage);
  setVoicePolling(["recording","stopping","processing"].includes(incoming.voiceState));
  const next=incoming.voiceId===session.finishedVoice&&incoming.voiceText?{...incoming,voiceState:"done"}:incoming;
  // Change the draft and its storage key together; polling must never copy a
  // draft into a different chat when the selected conversation changes.
  const nextOwner=draftOwner(next);
  if(nextOwner!==draftId.current){
   draftId.current=nextOwner;setDraft(drafts.read(nextOwner));setImagesState(session.attachments.get(nextOwner)||[]);
   pendingAuto.current=null;countdownDraft.current=null;setCountdown(null);
   followTail.current=true;setShowLatest(false);
  }
  historySnapshots.set(historyKey(next),next);
  while(historySnapshots.size>12)historySnapshots.delete(historySnapshots.keys().next().value!);
  session.snapshot=next;setData(next);
  if(next.voiceId&&["recording","stopping","processing"].includes(next.voiceState)){
   session.dictation=bindDictation(session.dictation,next.voiceId,nextOwner,drafts.read(nextOwner));
   localStorage.setItem(dictationKey,JSON.stringify(session.dictation));
  }
  if(next.voiceId&&next.voiceId!==session.discardedVoice&&next.voiceText&&next.voiceState==="done"){
   const id=next.voiceId;
   const owner=session.dictation?.id===id?session.dictation.thread:nextOwner;
   const update=updateDictation(session.dictation,id,owner,next.voiceText,drafts.read(owner));
   session.dictation=update.session;
   localStorage.setItem(dictationKey,JSON.stringify(session.dictation));
   if(update.value!==null){
    drafts.write(owner,update.value);if(owner===draftId.current)setDraft(update.value);
    if(autoSendRef.current&&owner===draftId.current)pendingAuto.current={owner,text:update.value};
   }
   lastVoice.current=next.voiceText;session.voiceText=next.voiceText;
  }else if(!next.voiceId&&next.voiceState==="done"&&next.voiceText&&next.voiceText!==session.voiceText){
   lastVoice.current=next.voiceText;session.voiceText=next.voiceText;
   const existing=drafts.read(nextOwner).trimEnd();
   drafts.write(nextOwner,(existing?existing+" ":"")+next.voiceText.trim()+" ");
  }
  if(next.voiceError&&next.voiceError!==lastVoiceError.current){lastVoiceError.current=next.voiceError;session.voiceError=next.voiceError;setError(next.voiceError);}
 },[]);
 const load=useCallback(async()=>{
  if(inFlight.current||viewGate.busy())return;
  inFlight.current=true;const revision=viewGate.token();
  try{const next=await readPolledSnapshot(revision,voicePolling?440:2350);if(mounted.current&&viewGate.current(revision)){accept(next);setConnectionError("");}}catch{if(mounted.current&&viewGate.current(revision))setConnectionError(t("Связь с Deck AI прервалась. Повторяю подключение…"));}finally{inFlight.current=false;}
 },[accept,voicePolling]);
 useEffect(()=>{mounted.current=true;void load();const timer=setInterval(()=>void load(),voicePolling?500:2500);return()=>{mounted.current=false;clearInterval(timer);};},[load,voicePolling]);
 useEffect(()=>{const el=chatRef.current;if(el&&followTail.current)el.scrollTop=el.scrollHeight;},[data?.messages,tab]);
 const editDraft=(value:string,owner=draftId.current)=>{
  if(owner===draftId.current){pendingAuto.current=null;countdownDraft.current=null;setCountdown(null);}
  drafts.write(owner,value);
 };
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
  editDraft("");setNotice(t("Поле сообщения очищено"));
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
  }catch(e){setError(t("Не удалось завершить диктовку: ")+String(e));}
  finally{setVoiceStarting(false);}
 };
 const currentGame=()=>readGameContext({appId:Router.MainRunningAppID,overview:id=>window.appStore?.GetAppOverviewByAppID(id),player:()=>window.friendStore?.GetFriendState(window.friendStore.currentUserSteamID)});
 const game=currentGame();
 const currentScreenshots=gameScreenshots(data?.screenshots||[],game);
 const gameStatus=gameContextEnabled&&game?game.name:model?.name||t("Готов");
 const submit=()=>void run(async()=>{
  if(!data||!draft.trim()){setError(t("Нет текста для отправки. Завершите диктовку или введите сообщение."));return;}
  const sentThread=draftId.current,sentDraft=draft;
  const sentAttachments=session.attachments.get(sentThread);
  await sendMessage(withGameContext(sentDraft,currentGame(),localStorage.getItem("deck-ai-game-context")==="on",t("\n\nИгра: ")),images.map(x=>x.path),model?.id||"",effort,tier,sendContext(data));
  if(drafts.read(sentThread)===sentDraft){
   drafts.write(sentThread,"");
   if(draftId.current===sentThread)setDraft("");
  }
  if(session.attachments.get(sentThread)===sentAttachments)publishAttachments(sentThread,[]);
  setNotice(t("Запрос принят · в очереди"));followTail.current=true;accept(await snapshot());
 });
 const submitRef=useRef(submit);submitRef.current=submit;
 useEffect(()=>{
  const pending=pendingAuto.current;
  if(pending?.owner===draftId.current&&!recording&&!voiceProcessing&&draft.trim()){
   pendingAuto.current=null;
   if(pending.text===draft){countdownDraft.current=pending;setCountdown(3);}
  }
 },[draft,recording,voiceProcessing]);
 useEffect(()=>{
  if(countdown===null)return;
  if(countdown<=0){
   setCountdown(null);
   const pending=countdownDraft.current;countdownDraft.current=null;
   if(pending?.owner===draftId.current&&drafts.read(pending.owner)===pending.text)submitRef.current();
   return;
  }
  const timer=setTimeout(()=>setCountdown(value=>value===null?null:value-1),1000);
  return()=>clearTimeout(timer);
 },[countdown]);
 const quick=(text:string)=>void run(async()=>{if(!data)return;await sendMessage(text,[],model?.id||"",effort,tier,sendContext(data));setNotice(t("Запрос принят · в очереди"));setQuickOpen(false);followTail.current=true;accept(await snapshot());});
 const ro=!!data?.readOnly;
 const filesStale=(file?.host??folderHost)!==(data?.remoteHost||"");
 const names:Record<string,string>={...providerNames,...Object.fromEntries((data?.customProviders||[]).map(c=>[c.id,c.name]))};
 const isCustom=!!data?.customProviders?.some(c=>c.id===data.provider);
 const [custom,setCustom]=useState({name:"",url:"",models:"",key:""});
 const decide=(item:Approval,decision:string)=>void run(async()=>{
  // Allowing runs a command on the machine: require a second, deliberate press.
  if(decision!=="decline"&&confirmApproval!==item.key){setConfirmApproval(item.key);setNotice(t("Нажмите «Разрешить» ещё раз, чтобы подтвердить"));return;}
  setConfirmApproval("");await approve(item.key,decision);setNotice(decision==="decline"?t("Отклонено"):t("Разрешено"));accept(await snapshot());
 });
 const openFolder=(path:string)=>void run(async()=>{const result=await fileList(path,data?.remoteHost||"");setFolder(result.path);setFolderHost(result.host);setEntries(sortEntries(result.entries));setFile(null);});
 const openFile=(path:string)=>void run(async()=>{const result=await fileRead(path,folderHost);setFile(result);setFileText(result.text);});
 const saveFile=()=>void run(async()=>{if(!file)return;const result=await fileWrite(file.path,fileText,file.sha256,file.host);setFile({...file,text:fileText,sha256:result.sha256});setNotice(t("Файл сохранён · копия: ")+file.path.split("/").pop()+".deckai.bak");});
 const chooseThread=(id:string)=>void run(async()=>{
  
  const current=session.snapshot;
  if(current){const cached=historySnapshots.get(historyKey({...current,threadId:id}));accept(cached?{...cached,threads:current.threads}:{...current,threadId:id,messages:[],active:false,status:t("Загружаю диалог…")});}
  accept(await selectThread(id));setTab("chat");
 });
 const startChat=()=>void run(async()=>{accept(await newThread());setTab("chat");});
 const openFiles=()=>{setTab("history");setFilesOpen(true);openFolder("~");};
 const sortedThreads=[...(data?.threads||[])].sort((a,b)=>Number(!!b.running)-Number(!!a.running));
 const sidebar=fullscreen&&layout==="split"?<GameScroll className="dai-split-side"><div className="dai-stack-content">
  <Action primary disabled={busy||!data?.ready||ro||data?.active} onClick={startChat}><Icon name="plus"/>{t("Новый чат")}</Action>
  {sortedThreads.map(thread=><div className={"dai-history-item "+(thread.id===data?.threadId?"selected":"")+(thread.running?" running":"")} key={thread.id}><Action disabled={busy||(data?.active&&thread.id!==data.threadId&&!data.remoteHost)} onClick={()=>chooseThread(thread.id)}><span>{thread.running&&<span className="dai-dot working" aria-label={t("Выполняется")}/>}{thread.name||t("Новый чат")}</span></Action></div>)}
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
   try{if(!doc.execCommand("copy"))throw new Error(t("Не удалось скопировать. Выделите текст сообщения для копирования."));}
   finally{field.remove();focused?.focus();}
  }
  setNotice(t("Текст скопирован"));
 });
 const jumpToLatest=()=>{followTail.current=true;setShowLatest(false);const el=chatRef.current;if(el)el.scrollTop=el.scrollHeight;};
 const settings=(id:string,depth:string,speed:string)=>void run(async()=>{await saveSettings(id,depth,speed);accept(await snapshot());});
 const attachMedia=(incoming:Media[])=>{
  const previous=session.attachments.get(draftId.current)||[];
  const result=appendAttachments(previous,incoming);
  if(result.omitted&&!result.added){setError(t("Достигнут лимит пяти изображений. Уберите лишние вложения, чтобы прикрепить другое."));return;}
  if(result.omitted)setNotice(t("Добавлено изображений: {0}. Для остальных освободите место. Лимит — пять.",result.added));
  setImages(result.images);setMediaOpen(false);
 };
 const attach=(media?:Media)=>{if(media)attachMedia([media]);};
 const signIn=()=>void run(async()=>{const result=await accountLogin();setLoginUrl(result.url+(result.userCode?t(" · Код: ")+result.userCode:""));setNotice(result.opened?t("Откройте страницу входа и завершите авторизацию."):t("Ссылка для входа показана ниже."));accept(await snapshot());});
 const disconnect=!data?.ready;
 return <Focusable style={{"--dai-text-scale":textScale} as CSSProperties} data-text-scale={textScale} data-language={uiLanguage} data-theme={appearance.theme} data-density={appearance.density} data-bubbles={appearance.bubbles} data-layout={layout} data-brand="midnight" className={"dai-root"+(fullscreen?" dai-fullscreen":"")} onSecondaryButton={()=>{if(tab==="chat"&&!busy)void toggleVoice();}} onSecondaryActionDescription={tab==="chat"?(recording?t("Стоп"):t("Голос")):undefined} onCancel={event=>{
  if(queueOpen){event.stopPropagation();setQueueOpen(false);}
  else if(mediaOpen){event.stopPropagation();setMediaOpen(false);}
  else if(fullscreen){event.stopPropagation();closeFullscreen();}
 }}><style>{css}</style><span ref={touchAnchor} hidden/>
  {fullscreen&&<Focusable className="dai-full-header" flow-children="horizontal">
   <div className="dai-full-brand"><BrandLogo size={28}/><h1>Deck AI</h1><span>{tab==="repair"?t("Локальная диагностика"):disconnect?t("Нет соединения"):data?.active?t("Deck AI работает…"):gameStatus}</span></div>
   <GameCheckbox checked={gameContextEnabled} onChange={toggleGameContext}/>
   <Action onClick={()=>closeFullscreen()}><Icon name="collapse"/>{t("В панель")}</Action>
   <Action onClick={()=>closeFullscreen(false)}><Icon name="back"/>{t("К игре")}</Action>
  </Focusable>}
  <Focusable className="dai-tabs" flow-children="horizontal" role="tablist" aria-label="Deck AI">
   {([["chat",t("Чат"),<Icon name="chat"/>],["history",t("История"),<Icon name="history"/>],["repair",t("Ремонт"),<Icon name="game"/>],["settings",t("Настройки"),<Icon name="settings"/>]] as const).map(([id,label,icon])=><div key={id} role="tab" aria-selected={tab===id} className={"dai-tab "+(tab===id?"selected":"")}><Action disabled={busy} onClick={()=>{if((id==="settings"||id==="repair")&&!fullscreen)openFullscreen(id);else{setTab(id);setMediaOpen(false);setQueueOpen(false);}}}>{icon}<span>{label}</span></Action></div>)}
  </Focusable>
  <div className="dai-viewbar"><div className="dai-status"><span className={"dai-dot "+(disconnect?"offline":data?.active?"working":"")}/><span>{!data?t("Подключение…"):data.ready?(data.active?t("Deck AI работает…"):gameStatus):(data.retryIn?t("Нет связи · повтор через {0} с",data.retryIn):t("Нет соединения"))}</span>{data?.remoteHost&&<small>{data.remoteHost}</small>}{!!data?.runningCount&&<small className="dai-running-count">{data.runningCount}{t(" в работе")}</small>}</div>{!fullscreen&&<GameCheckbox checked={gameContextEnabled} onChange={toggleGameContext}/>}{!fullscreen&&<Action disabled={busy} onClick={()=>openFullscreen(tab)}><Icon name="expand"/>{t("На весь экран")}</Action>}</div>
  {tab!=="repair"&&(error||connectionError)&&<div className="dai-banner" role="alert"><span>{systemText(error||connectionError)}</span><Action onClick={()=>{setError("");setConnectionError("");}}>{t("Закрыть")}</Action></div>}
  {tab!=="repair"&&!error&&!connectionError&&(data?.historyWarning||data?.ready===false)&&<div className="dai-banner" role="status"><span>{systemText(data.historyWarning||data.status)}</span><Action disabled={busy} onClick={()=>void run(async()=>{accept(await refresh());})}>{t("Повторить подключение")}</Action></div>}
  {notice&&<div className="dai-notice" role="status">{systemText(notice)}</div>}
  <div className="dai-page" role="tabpanel" aria-label={tab==="chat"?t("Чат"):tab==="history"?t("История"):tab==="repair"?t("Ремонт"):t("Настройки")}>
  {tab==="repair"&&<GameScroll className="dai-scroll dai-stack"><RepairPanel copy={copyMessage}/></GameScroll>}
  {tab==="chat"&&<div className="dai-chat-layout">{sidebar}<div className={"dai-chat-main"+(data?.approvals?.length?" has-approvals":"")}>
   {queueOpen?<GameScroll key="queue" ref={queueRef} className="dai-scroll dai-stack dai-queue-view"><div className="dai-stack-content">
    <Action onClick={()=>setQueueOpen(false)}>{t("← К сообщению")}</Action>
    <h3>{t("Очередь запросов · ")}{data?.queueTotal??data?.outbox.length??0}</h3>
    <p className="dai-muted">{t("Ожидающие запросы ещё не отправлены. Запросы выполняются по очереди; занятый чат ждёт завершения текущего ответа.")}</p>
    <p className="dai-muted">{t("В этом чате ожидают: ")}{queueCounts(data?.outbox||[],data?.threadId||"",data?.remoteHost||"").current}{t(". В других чатах: ")}{queueCounts(data?.outbox||[],data?.threadId||"",data?.remoteHost||"").other}.</p>
    {(data?.queueTotal||0)>(data?.outbox.length||0)&&<p className="dai-muted">{t("Показаны последние ")}{data?.outbox.length}{t(" запросов.")}</p>}
    {!data?.outbox.length&&<p className="dai-muted">{t("Очередь пуста.")}</p>}
    {data?.outbox.map(job=><section className="dai-section dai-queue-item" key={job.id}>
     <strong>{systemText(queueStatus(job))}</strong>
     <small className="dai-muted">{sameChat(job,data.threadId,data.remoteHost||"")?t("Этот чат"):(job.host||"")!==(data.remoteHost||"")?t("Другое устройство · ")+(job.host||"Steam Deck"):(data.threads.find(thread=>thread.id===job.threadId)?.name||t("Другой чат")).slice(0,80)}{job.createdAt?" · "+new Date(job.createdAt*1000).toLocaleString():""}</small>
     <p className="dai-queue-text">{expandedJob===job.id?job.text:job.text.slice(0,180)+(job.text.length>180?"…":"")}</p>
     {job.text.length>180&&<Action onClick={()=>setExpandedJob(expandedJob===job.id?"":job.id)}>{expandedJob===job.id?t("Свернуть текст"):t("Весь текст запроса")}</Action>}
     {job.error&&<p className="dai-muted">{systemText(job.error)}</p>}
     {job.status==="queued"&&<Action disabled={busy||ro} onClick={()=>void run(async()=>{await queueFront(job.id);accept(await snapshot());})}>{t("↑ Отправить первым")}</Action>}
     {(job.status==="queued"||job.status==="error")&&<Action disabled={busy||ro} onClick={()=>void run(async()=>{await queueRemove(job.id);accept(await snapshot());})}>{t("Удалить из очереди")}</Action>}
     {job.threadId&&<Action disabled={busy} onClick={()=>void run(async()=>{if((job.host||"")!==(data?.remoteHost||""))accept(await remoteHost(job.host||""));accept(await selectThread(job.threadId!));setTab("chat");setQueueOpen(false);})}>{t("Открыть чат")}</Action>}
    </section>)}
   </div></GameScroll>:mediaOpen?<GameScroll className="dai-scroll dai-stack"><div className="dai-stack-content">
    <Action onClick={()=>setMediaOpen(false)}>{t("← К сообщению")}</Action>
    <section className="dai-section dai-game-context"><h3><Icon name="game"/>{t(" Контекст игры")}</h3>
     <p className="dai-muted">{game?game.name:t("Сейчас Steam не сообщает о запущенной игре.")}</p>
     {game&&<p className="dai-muted">{game.status||t("Игра не передаёт описание текущего места или задания.")}</p>}
     {game?.details.map(([key,value])=><p className="dai-muted" key={key}>{key}: {value}</p>)}
     <GameCheckbox checked={gameContextEnabled} onChange={toggleGameContext}/>
     {game&&<Action disabled={!currentScreenshots.length} onClick={()=>attach(currentScreenshots[0])}>{t("Снимок из этой игры")}{currentScreenshots[0]?.when?" · "+new Date(currentScreenshots[0].when*1000).toLocaleString():""}</Action>}
     <p className="dai-muted">{t("Чтобы показать, где вы сейчас: сделайте снимок в игре — Steam + R1, затем прикрепите его здесь. Галочка «Игра» добавляет к вопросу только название игры.")}</p>
    </section>
    <h3>{t("Другие вложения")}</h3>
    <Action disabled={!data?.screenshots.length} onClick={()=>attach(data?.screenshots[0])}>{t("Последний скриншот")}</Action>
    <Choice label={t("Другой скриншот")} value={shot} options={(data?.screenshots||[]).map(x=>({data:x.path,label:x.name}))} onChange={setShot}/>
    <Action disabled={!shot} onClick={()=>attach(data?.screenshots.find(x=>x.path===shot))}>{t("Прикрепить скриншот")}</Action>
    <Choice label={t("Видеозапись")} value={video} options={(data?.videos||[]).map(x=>({data:x.path,label:x.name}))} onChange={setVideo}/>
    <Action disabled={!video||busy} onClick={()=>void run(async()=>{const result=await videoFrames(video);attachMedia(result.frames);})}>{t("Добавить кадры из видео")}</Action>
    {!data?.screenshots.length&&!data?.videos.length&&<p className="dai-muted">{t("Сделайте скриншот в игре: Steam + R1. Он появится здесь.")}</p>}
   </div></GameScroll>:<>
    <Focusable className="dai-toolbar" flow-children="horizontal">
     <Action disabled={busy||disconnect||ro||data?.active} onClick={startChat}><Icon name="plus"/><span>{t("Новый")}</span></Action>
     <Action disabled={busy||disconnect} onClick={openFiles}><Icon name="folder"/><span>{t("Файлы")}</span></Action>
     <Action disabled={busy} onClick={()=>{setMediaOpen(true);setQuickOpen(false);}}><Icon name="attachment"/><span>{t("Вложения")}</span></Action>
     <Action onClick={()=>setQueueOpen(true)}><Icon name="queue"/><span>{t("Очередь")}{(data?.queueTotal||data?.outbox.length)?" · "+(data?.queueTotal??data?.outbox.length):""}</span></Action>
     <Action disabled={busy} onClick={()=>void run(async()=>{accept(await refresh());setNotice(t("Обновлено"));})}><Icon name="refresh"/><span>{t("Обновить")}</span></Action>
    </Focusable>
    <GameScroll className="dai-messages" ref={chatRef} onScroll={()=>{const el=chatRef.current;if(el){followTail.current=el.scrollHeight-el.scrollTop-el.clientHeight<60;setShowLatest(!followTail.current);}}}>
     <div className="dai-message-list">{!data?.messages.length&&<div className="dai-empty"><Handheld/><h3>{t("Помощь прямо в игре")}</h3><p>{t("Задайте вопрос текстом или голосом.")}<br/>{t("Можно добавить скриншот.")}</p>{disconnect&&<Action onClick={()=>void run(async()=>accept(await refresh()))} disabled={busy}>{busy?t("Подключение…"):t("Подключиться")}</Action>}</div>}
     {data?.hasOlderMessages&&<Action disabled={busy} onClick={()=>void run(async()=>{followTail.current=false;accept(await olderMessages());requestAnimationFrame(()=>{if(chatRef.current)chatRef.current.scrollTop=0;});})}>{t("Показать предыдущие сообщения")}</Action>}
     {data?.messages.map((message,i)=>message.role==="tool"?<Focusable key={message.id||i} className="dai-message tool" focusClassName="dai-focused" onActivate={()=>setOpenTool(openTool===(message.id||String(i))?"":(message.id||String(i)))}><pre>{(()=>{const text=uiLanguage==="en"?(message.textEn??message.text):message.text;return openTool===(message.id||String(i))?text:text.split("\n").slice(0,3).join("\n")+(text.split("\n").length>3?"\n…":"");})()}</pre></Focusable>:<Focusable key={message.id||i} className={"dai-message "+message.role} focusClassName="dai-focused"><small>{message.role==="user"?t("Вы"):names[data.provider]?.split(" · ")[0]||"AI"}</small><div>{message.text}</div>{!!message.attachments?.length&&<MessageAttachments items={message.attachments}/>}<div className="dai-message-tools"><Action onClick={()=>copyMessage(message.text)}><Icon name="copy"/>{t("Копировать")}</Action>{message.role==="assistant"&&!!(window as unknown as {speechSynthesis?:unknown}).speechSynthesis&&<Action onClick={()=>speak(message.id||String(i),message.text)}>{speaking===(message.id||String(i))?t("■ Стоп"):t("🔊 Озвучить")}</Action>}</div></Focusable>)}
     {(data?chatFailures(data.outbox,data.threadId,data.remoteHost||""):[]).map(x=><div className="dai-failed" key={x.id}><p>{systemText(x.error||t("Не удалось отправить"))}</p><Action disabled={busy} onClick={()=>void run(async()=>{await retry(x.id);accept(await snapshot());})}>{t("Повторить отправку")}</Action></div>)}
    </div></GameScroll>
    {showLatest&&<div className="dai-latest"><Action onClick={jumpToLatest}>{t("↓ К последнему сообщению")}</Action></div>}
    {ro&&<div className="dai-notice" role="status">{t("Режим только чтения: отправка, подтверждения и правки отключены.")}</div>}
    {!!data?.approvals?.length&&<GameScroll className="dai-approvals" role="alert">{data.approvals.map(item=><div className="dai-approval" key={item.key}><strong>{t("Нужно подтверждение · ")}{item.title}</strong><span className="dai-muted">{systemText(item.summary)}</span><Focusable className="dai-compose-actions" flow-children="horizontal"><Action primary disabled={busy||ro} onClick={()=>decide(item,"accept")}>{confirmApproval===item.key?t("Нажмите ещё раз"):t("Разрешить")}</Action><Action disabled={busy||ro} onClick={()=>decide(item,"decline")}>{t("Отклонить")}</Action></Focusable></div>)}</GameScroll>}
    <div className="dai-composer">
     {countdown!==null&&<div className="dai-notice" role="status">{t("Отправка через ")}{countdown}{t(" с")}<Action onClick={()=>setCountdown(null)}>{t("Отменить отправку")}</Action></div>}
     {quickOpen&&data?.threadId&&<Focusable className="dai-quick" flow-children="horizontal">{quickActions.map(([label,text])=><Action key={label} disabled={busy||disconnect||ro} onClick={()=>quick(quickSource===null?t(text):text)}>{quickSource===null?t(label):label}</Action>)}</Focusable>}
     {data?.outbox.some(job=>job.status==="recovering")&&<p className="dai-muted dai-queue-state" role="status">{t("Проверяю состояние отправленного запроса…")}</p>}
     {!!data?.outbox.length&&<div className="dai-queue-summary"><Action onClick={()=>setQueueOpen(true)}>{t("Очередь · ")}{data.queueTotal??data.outbox.length}{t(" · посмотреть")}</Action></div>}
     {images.length>0&&<div className="dai-attachments">{images.map((image,i)=><Action key={image.path+":"+i} onClick={()=>setImages(old=>old.filter((_,n)=>n!==i))}>× {image.name}</Action>)}</div>}
     {(recording||voiceProcessing)&&<div className="dai-voice-preview" role="status" aria-live="polite"><span className="dai-record-dot" aria-hidden="true"/><div><strong>{recording?t("● Запись · распознанный текст"):t("Завершаю распознавание…")}</strong><span role="textbox" aria-label={t("Распознанная речь")} aria-readonly="true">{(data?.voiceId!==session.discardedVoice?data?.voiceText:"")||(["ru","en","ru-fast","en-fast"].includes(lang)?t("Здесь появится распознанная речь"):t("Записываю. Текст появится после «Стоп»."))}</span></div></div>}
     {data?.threadId&&draftOwner(data)!==data.threadId&&!draft&&!!drafts.read(data.threadId)&&
      <Action disabled={busy||recording||voiceProcessing} onClick={()=>editDraft(drafts.read(data.threadId))}>{t("Восстановить старый черновик")}</Action>}
     <form style={{display:"contents"}} onSubmit={e=>{e.preventDefault();submit();}}><div className="dai-draft-field" key={draftOwner(data)||"new"} data-draft-owner={draftOwner(data)} onInputCapture={e=>{const target=e.target as HTMLInputElement;if(target.tagName==="INPUT")editDraft(target.value,e.currentTarget.dataset.draftOwner||"");}}><TextField disabled={recording||voiceProcessing} value={draft} placeholder={t("Спросить об игре…")} onChange={e=>editDraft(e.target.value,e.target.closest<HTMLElement>(".dai-draft-field")?.dataset.draftOwner??draftId.current)} onKeyDown={e=>{if((e.key==="Enter"||e.keyCode===13)&&!e.shiftKey&&!(e.nativeEvent as KeyboardEvent).isComposing){e.preventDefault();submit();}}}/></div></form>
     <Focusable className="dai-compose-actions" flow-children="horizontal">
      <Action recording={recording||voiceProcessing} disabled={!data||voiceProcessing||busy} onClick={()=>void toggleVoice()}><Icon name="microphone"/>{recording?t("Стоп"):t("Голос")}</Action>
      {!!data?.threadId&&<Action disabled={recording||voiceProcessing} onClick={()=>setQuickOpen(!quickOpen)}>⚡</Action>}
      <Action disabled={voiceStarting||(!draft.trim()&&!recording&&!voiceProcessing)} onClick={clearDraft}>{t("Очистить")}</Action>
      {fullscreen&&data?.active&&data.provider==="codex"&&<Action disabled={busy} onClick={()=>void run(async()=>{await stop();accept(await snapshot());})}>{t("Стоп")}</Action>}
      <Action primary disabled={busy||disconnect||ro||recording||voiceProcessing||!draft.trim()} onClick={submit}>{busy?"…":t("Отправить")}</Action>
     </Focusable>
     {!fullscreen&&data?.active&&data.provider==="codex"&&<Action disabled={busy} onClick={()=>void run(async()=>{await stop();accept(await snapshot());})}>{t("Остановить ответ")}</Action>}
    </div>
   </>}
  </div></div>}
  {tab==="history"&&filesOpen&&<GameScroll className="dai-scroll dai-stack"><div className="dai-stack-content">
   <Action disabled={busy} onClick={()=>{if(file)setFile(null);else setFilesOpen(false);}}>← {file?t("К папке"):t("Назад")}</Action>
   <h3>{file?file.path.split("/").pop():folder}</h3>
   <p className="dai-muted">{t("Устройство · ")}{(file?.host??folderHost)||"Steam Deck"}</p>
   {filesStale&&<p role="status">{t("Выбрано другое устройство. Вернитесь к исходному устройству, чтобы сохранить правки или продолжить просмотр папки.")}</p>}
   {!file&&<><Action disabled={busy||filesStale} onClick={()=>openFolder(parentPath(folder))}>{t("⬑ Вверх")}</Action>
    {entries.map(name=><Action key={name} disabled={busy||filesStale} onClick={()=>isFolder(name)?openFolder(joinPath(folder,name)):openFile(joinPath(folder,name))}>{isFolder(name)?"📁 ":"📄 "}{name}</Action>)}
    {!entries.length&&<p className="dai-muted">{t("Папка пуста. Доступна только домашняя папка; ключи и секреты скрыты.")}</p>}</>}
   {file&&<><textarea className="dai-textarea" value={fileText} spellCheck={false} onChange={e=>setFileText(e.target.value)}/>
    <p className="dai-muted">{fileText===file.text?t("Без изменений"):t("Есть несохранённые правки")}{t(" · до 64 КБ · перед записью создаётся копия .deckai.bak")}</p>
    <Action primary disabled={busy||ro||filesStale||fileText===file.text} onClick={saveFile}>{t("Сохранить на устройстве")}</Action>
    <Action disabled={busy||fileText===file.text} onClick={()=>setFileText(file.text)}>{t("Отменить правки")}</Action></>}
  </div></GameScroll>}
  {tab==="history"&&!filesOpen&&<GameScroll className="dai-scroll dai-stack"><div className="dai-stack-content">
   <Action primary disabled={busy||disconnect||ro||data?.active} onClick={()=>void run(async()=>{accept(await newThread());setTab("chat");})}>{t("＋ Новый чат")}</Action>
   <Action disabled={busy||disconnect} onClick={()=>{setFilesOpen(true);openFolder("~");}}>{t("📁 Файлы на устройстве")}{data?.remoteHost?" · "+data.remoteHost:""}</Action>
   {!!data?.recentEvents?.length&&<section className="dai-section dai-events"><h3>{t("Что произошло")}</h3>{data.recentEvents.slice(0,8).map(item=><p className="dai-muted" key={item.id}>{item.kind==="approval"?"⏸":item.kind==="failed"?"✗":"✓"} {new Date(item.at*1000).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})} · {(item.host||"Steam Deck")+" · "+item.title}</p>)}</section>}
   {(data?.provider==="codex"||!data)&&<Choice label={t("Устройство")} value={data?.remoteHost||""} options={[{data:"",label:t("Этот Steam Deck")},...(data?.sshHosts||[]).map(x=>({data:x,label:x}))]} disabled={busy||data?.active} onChange={value=>void run(async()=>accept(await remoteHost(value)))}/>}
   {data?.remoteHost&&<Action disabled={busy} onClick={()=>void run(async()=>{accept(await refresh());setNotice(t("Список задач обновлён"));})}>{t("↻ Обновить задачи на ")}{data.remoteHost}</Action>}
   <TextField value={historyQuery} placeholder={t("Найти разговор…")} onChange={e=>setHistoryQuery(e.target.value)}/>
   {(data?.allTasks||[]).some(task=>task.host!==(data?.remoteHost||"")||task.running)&&<section className="dai-section dai-all-tasks"><h3>{t("Задачи на всех устройствах")}</h3>{(data?.allTasks||[]).filter(task=>task.host!==(data?.remoteHost||"")||task.running).slice(0,12).map(task=><Action key={task.host+":"+task.id} disabled={busy||(data?.active&&!data.remoteHost&&task.host==="")} onClick={()=>void run(async()=>{if(task.host!==(data?.remoteHost||""))accept(await remoteHost(task.host));accept(await selectThread(task.id));setTab("chat");})}><span>{task.running&&<span className="dai-dot working" aria-label={t("Выполняется")}/>}{(task.host||"Steam Deck")+" · "+task.name}</span></Action>)}</section>}
   {!data?.threads.length&&<p className="dai-muted">{t("Ваши разговоры появятся здесь.")}</p>}
   {data?.threads.filter(x=>x.name.toLocaleLowerCase().includes(historyQuery.toLocaleLowerCase())).sort((a,b)=>Number(!!b.running)-Number(!!a.running)).map(thread=><div className={"dai-history-item "+(thread.id===data.threadId?"selected":"")+(thread.running?" running":"")} key={thread.id}><Action disabled={busy||(data.active&&thread.id!==data.threadId&&!data.remoteHost)} onClick={()=>chooseThread(thread.id)}><span>{thread.running&&<span className="dai-dot working" aria-label={t("Выполняется")}/>}{thread.name||t("Новый чат")}</span>{thread.id===data.threadId&&<small>{t("Текущий")}</small>}</Action></div>)}
  </div></GameScroll>}
  {tab==="settings"&&<GameScroll className="dai-scroll dai-stack dai-settings"><div className="dai-settings-grid"><div className="dai-settings-column"><UpdatesPanel client={updateClient} busy={busy}/><LibraryPanel disabled={busy||!!data?.readOnly}/>
   <section className="dai-section dai-model-settings"><h3>{t("Модель и ответ")}</h3><div className="dai-model-fields">
    <Choice label={t("Сервис")} value={data?.provider||"codex"} options={Object.entries(names).map(([data,label])=>({data,label:data.startsWith("custom:")?label:t(label)}))} disabled={busy||data?.active} onChange={value=>void run(async()=>{accept(await setProvider(value));setKey("");})}/>
    <Choice label={t("Модель")} value={model?.id||""} options={(data?.models||[]).map(x=>({data:x.id,label:x.name}))} disabled={busy} onChange={id=>{const next=data?.models.find(x=>x.id===id);settings(id,next?.defaultEffort||next?.efforts[0]?.id||"","default");}}/>
    {data?.provider==="codex"&&<><Choice label={t("Глубина обработки")} value={effort} options={(model?.efforts||[]).map(x=>({data:x.id,label:t(x.name)}))} disabled={busy} onChange={value=>settings(model?.id||"",value,tier)}/><Choice label={t("Скорость")} value={tier} options={[{data:"default",label:t("Обычная")},...(model?.tiers.includes("priority")?[{data:"priority",label:t("Приоритетная")}]:[])]} disabled={busy} onChange={value=>settings(model?.id||"",effort,value)}/></>}
    </div>{(data?.provider==="deepseek"||data?.provider==="tokenharbor"||isCustom)&&<><TextField bIsPassword value={key} placeholder={t("Ключ API")} onChange={e=>setKey(e.target.value)}/><Action disabled={busy||!key.trim()} onClick={()=>void run(async()=>{await setProviderKey(key.trim());setKey("");accept(await refresh());setNotice(t("Ключ сохранён"));})}>{t("Сохранить ключ")}</Action><p className="dai-muted">{t("Ключ хранится в системном хранилище SteamOS.")}</p></>}
    {data?.provider==="claude"&&<p className="dai-muted">{t("Desktop Mode → Deck AI → + → Подключить Claude Code или Anthropic Console (API). Вход выполняется в официальном CLI: свой аккаунт, API-ключ или облачный доступ. Расходы зависят от способа доступа.")}</p>}
    {isCustom&&<><p className="dai-muted">{t("Для этого облачного сервиса нужен API-ключ. Он хранится в системном хранилище SteamOS.")}</p><Action disabled={busy||ro} onClick={()=>showModal(<ConfirmModal strTitle={t("Удалить «")+(names[data!.provider]||"")+"»?"} strOKButtonText={t("Удалить")} strCancelButtonText={t("Отмена")} onOK={()=>void run(async()=>{await customRemove(data!.provider);accept(await refresh());})}/>)}>{t("Удалить это подключение")}</Action></>}
   </section>
   <section className="dai-section dai-appearance"><h3>{t("Оформление")}</h3>
    <div className="dai-field"><span className="dai-label">{t("Цветовая тема")}</span>
     <Focusable className="dai-swatches" flow-children="horizontal">{themes.map(theme=><DialogButton key={theme.id} className={"dai-button dai-swatch"+(appearance.theme===theme.id?" dai-selected":"")} aria-pressed={appearance.theme===theme.id} onClick={()=>setAppearanceChoice("theme",theme.id)}><span className="dai-swatch-dot" style={{background:theme.swatch}}/>{t(theme.name)}</DialogButton>)}</Focusable></div>
    <Segmented label={t("Сообщения")} value={appearance.bubbles} options={bubbleStyles} onChange={id=>setAppearanceChoice("bubbles",id)}/>
    <Segmented label={t("Плотность")} value={appearance.density} options={densities} onChange={id=>setAppearanceChoice("density",id)}/>
    <Segmented label={t("Компоновка")} value={appearance.layout} options={layouts} onChange={id=>setAppearanceChoice("layout",id)}/>
    {appearance.layout==="split"&&!fullscreen&&<p className="dai-muted">{t("Две колонки включатся в режиме «На весь экран».")}</p>}
   </section>
   <section className="dai-section dai-custom-ai"><h3>{t("Свой облачный ИИ")}</h3>
    <p className="dai-muted">{t("Подойдёт любой облачный сервис с OpenAI-совместимым API: OpenAI, Gemini, Groq, Mistral, DeepSeek, xAI, OpenRouter и другие. Выберите готовый адрес или укажите свой (только https). Локальные серверы не поддерживаются.")}</p>
    <Focusable className="dai-quick" flow-children="horizontal">{(data?.presets||[]).map(p=><Action key={p.url} onClick={()=>setCustom(old=>({...old,name:old.name||p.name.split(" · ")[0],url:p.url}))}>{p.name}</Action>)}</Focusable>
    <TextField value={custom.name} placeholder={t("Название (например, Groq)")} onChange={e=>setCustom({...custom,name:e.target.value})}/>
    <TextField value={custom.url} placeholder={t("Адрес API, например https://api.groq.com/openai/v1")} onChange={e=>setCustom({...custom,url:e.target.value})}/>
    <TextField value={custom.models} placeholder={t("Модели через запятую (необязательно)")} onChange={e=>setCustom({...custom,models:e.target.value})}/>
    <TextField bIsPassword value={custom.key} placeholder={t("Ключ API")} onChange={e=>setCustom({...custom,key:e.target.value})}/>
    <Action primary disabled={busy||ro||!custom.name.trim()||!custom.url.trim()||!custom.key.trim()} onClick={()=>void run(async()=>{const result=await customSave(custom.name.trim(),custom.url.trim(),custom.models,custom.key.trim());setCustom({name:"",url:"",models:"",key:""});accept(await setProvider(result.id));setNotice(t("Подключение добавлено"));})}>{t("Добавить и выбрать")}</Action></section>
   <section className="dai-section dai-physical-keyboard"><h3>{t("Физическая клавиатура")}</h3>
    <p className="dai-muted">{t("Для USB- и Bluetooth-клавиатуры в Gaming Mode. Язык меню и диктовки на раскладку не влияет.")}</p>
    {physicalKeyboard?.supported?<>
     <p role="status">{physicalKeyboard.enabled?t("English / Русский · Alt+Shift"):t("Раскладка SteamOS")}</p>
     {physicalKeyboard.restartRequired&&<p className="dai-notice" role="status">{t("Сохранено. Для применения выйдите в Desktop Mode и вернитесь в Gaming Mode. Сначала сохраните игру.")}</p>}
     {physicalKeyboard.enabled&&!physicalKeyboard.sessionActive&&<p className="dai-muted">{t("EN/RU включатся при следующем входе в Gaming Mode.")}</p>}
     {physicalKeyboard.active&&<p className="dai-muted">{t("EN/RU работают. Переключение: Alt+Shift.")}</p>}
     <Focusable className="dai-quick" flow-children="horizontal"><Action disabled={busy||ro||physicalKeyboard.enabled||physicalKeyboard.conflict} onClick={()=>void run(async()=>setPhysicalKeyboard(await configureKeyboard(true)))}>{t("Включить EN/RU")}</Action><Action disabled={busy||ro||!physicalKeyboard.enabled} onClick={()=>void run(async()=>setPhysicalKeyboard(await configureKeyboard(false)))}>{t("Вернуть раскладку SteamOS")}</Action></Focusable>
     {physicalKeyboard.conflict&&<p className="dai-notice">{t("Файл настройки изменён отдельно. Deck AI сохранил ваши изменения.")}</p>}
    </>:<p className="dai-muted">{t("Системная настройка доступна на SteamOS с Gaming Mode.")}</p>}
   </section>
   <section className="dai-section dai-text-settings"><h3>{t("Интерфейс и голос")}</h3>
   <Choice label={t("Язык интерфейса")} value={uiLanguage} options={[{data:"en",label:"English"},{data:"ru",label:t("Русский")}]} onChange={value=>void run(async()=>{const result=await saveInterfaceLanguage(value as UILanguage);setUILanguage(result.uiLanguage);accept(await snapshot());})}/>
   <p className="dai-muted">{t("Язык меню не меняет текст ваших разговоров и язык диктовки.")}</p><div className="dai-personal-fields"><div className="dai-field"><span className="dai-label">{t("Масштаб чата и кнопок")}</span>
    <Focusable className="dai-scale-controls" flow-children="horizontal">
     <Action disabled={textScale<=.7} onClick={()=>setTextScale(textScale-.1)}>{t("А−")}</Action>
     <span className="dai-scale-value" aria-live="polite">{Math.round(textScale*100)}%</span>
     <Action disabled={textScale>=1.5} onClick={()=>setTextScale(textScale+.1)}>{t("А+")}</Action>
     <Action disabled={textScale===1} onClick={()=>setTextScale(1)}>{t("Сброс")}</Action>
    </Focusable></div>
   <Choice label={t("Язык распознавания")} value={lang} options={!data?.speechReady?[{data:"ru",label:t("Русский")},{data:"en",label:"English"}]:[{data:"auto",label:t("Определять автоматически")},...Object.entries(speechLanguages).sort(([a],[b])=>a==="ru"?-1:b==="ru"?1:a==="en"?-1:b==="en"?1:0).map(([data,label])=>({data,label:speechLanguageName(data,label)})),{data:"ru-fast",label:t("Русский · экономный")},{data:"en-fast",label:t("English · экономный")}]} onChange={value=>{setLang(value);localStorage.setItem("codex-game-voice",value);}}/></div>
    {data?.speechVersion===2&&!data.speechReady&&<p className="dai-muted">{t("Для других языков установите многоязычную модель: scripts/download-models.sh --accurate-ru")}</p>}
    <div className="dai-game-setting"><span className="dai-muted">{t("Добавлять только название игры")}</span><GameCheckbox checked={gameContextEnabled} onChange={toggleGameContext}/></div>
    <div className="dai-game-setting"><span className="dai-muted">{t("Сообщать о готовности задач (уведомления Steam)")}</span><GameCheckbox checked={notify} onChange={()=>{const next=!notify;localStorage.setItem("deck-ai-notify",next?"on":"off");setNotify(next);}}/></div>
    <div className="dai-game-setting"><span className="dai-muted">{t("Отправлять голосовое сообщение через 3 с после «Стоп»")}</span><GameCheckbox checked={autoSend} onChange={()=>{const next=!autoSend;localStorage.setItem("deck-ai-auto-send",next?"on":"off");setAutoSend(next);}}/></div>
    <div className="dai-game-setting"><span className="dai-muted">{t("Только чтение (без отправки, подтверждений и правок)")}</span><GameCheckbox checked={ro} onChange={()=>void run(async()=>{await setReadOnly(!ro);accept(await snapshot());})}/></div>
    <div className="dai-field"><span className="dai-label">{t("Быстрые фразы ⚡ (строка: название | текст)")}</span><textarea className="dai-textarea dai-textarea-small" value={quickSource??parseQuickActions(null).map(([a,b])=>a===b?t(a):t(a)+" | "+t(b)).join("\n")} onChange={e=>{setQuickSource(e.target.value);localStorage.setItem("deck-ai-quick",e.target.value);}}/></div>
    <Action disabled={busy||!data?.loadedModels} onClick={()=>void run(async()=>{await unloadModels();accept(await snapshot());setNotice(t("Модели распознавания выгружены из памяти"));})}>{t("Освободить память")}{data?.loadedModels?t(" · загружено моделей: {0}",data.loadedModels):""}</Action></section>
   </div><div className="dai-settings-column">
   <section className="dai-section dai-connection-settings"><h3>{t("Подключение Codex")}</h3><div className="dai-connection-bar">
    <p className="dai-muted">{(data?.active?t("Deck AI работает…"):systemText(data?.status||""))||t("Сервер пока недоступен. Можно повторить подключение.")}</p>
    <Action disabled={busy} onClick={()=>void run(async()=>{accept(await refresh());setNotice(t("Соединение обновлено"));})}>{busy?t("Подключение…"):t("Переподключиться")}</Action></div>
    {(!data||data.provider==="codex")&&<><Choice label={t("Устройство")} value={data?.remoteHost||""} options={[{data:"",label:t("Этот Steam Deck")},...(data?.sshHosts||[]).map(x=>({data:x,label:x}))]} disabled={busy||data?.active} onChange={value=>void run(async()=>accept(await remoteHost(value)))}/><div className="dai-host-entry"><TextField value={host} placeholder={t("Другой SSH-алиас")} onChange={e=>setHost(e.target.value)}/><Action disabled={busy||!host.trim()||data?.active} onClick={()=>void run(async()=>{accept(await remoteHost(host.trim()));setHost("");})}>{t("Подключить")}</Action></div></>}
   </section>
   {!!data?.sshHosts.length&&<section className="dai-section dai-watch"><h3>{t("Следить в фоне")}</h3><p className="dai-muted">{t("Уведомления и подтверждения с этих машин приходят, даже когда они не выбраны. До 5 машин.")}</p>
    {data.sshHosts.map(name=>{const on=!!data.watchHosts?.includes(name);return <div className="dai-game-setting" key={name}><span className="dai-muted">{name}{on&&data.watchStatus?.[name]?" · "+({connected:t("на связи"),offline:t("нет связи"),connecting:t("подключаюсь"),active:t("выбрана")} as Record<string,string>)[data.watchStatus[name]]:""}</span><GameCheckbox checked={on} onChange={()=>void run(async()=>{const next=on?(data.watchHosts||[]).filter(x=>x!==name):[...(data.watchHosts||[]),name];await watchHosts(next);accept(await snapshot());})}/></div>;})}</section>}
   <section className="dai-section dai-share"><h3>{t("Доступ с другого компьютера")}</h3>
    <p className="dai-muted">{t("Управляйте задачами этого Deck с Mac или ПК по SSH: команды из вашего Codex появятся здесь.")}</p>
    <Action disabled={busy} onClick={()=>void run(async()=>setShare(await shareStatus()))}>{t("Показать данные подключения")}</Action>
    {share&&<><p className={"dai-muted dai-check "+(share.sshActive?"ok":"bad")}>{share.sshActive?t("✓ SSH-сервер работает"):t("✗ SSH-сервер выключен")}{t(" · ключей: ")}{share.keys}{share.codex?"":t(" · Codex не найден")}</p>
     {!share.sshActive&&<p className="dai-muted">{share.enableHint}</p>}
     <p className="dai-muted">{t("Пользователь ")}{share.user}{t(" · адреса: ")}{share.addresses.join(", ")||t("не найдены")}</p>
     <p className="dai-muted">{t("На Mac или ПК запустите мастер connect-deck.py из архива Remote Control. Адрес устройства указан выше.")}</p><p className="dai-muted">{t("Отпечатки SSH для проверки первого соединения:")}</p><pre className="dai-snippet">{(share.fingerprints||[]).join("\n")||t("SSH ещё не создал ключи: сначала включите сервер.")}</pre><p className="dai-muted">{t("Для ручной настройки ~/.ssh/config:")}</p><pre className="dai-snippet">{share.snippet}</pre>
     <p className="dai-muted">{t("Вставьте публичный ключ из мастера на Mac или ПК:")}</p>
     <TextField value={shareKey} placeholder="ssh-ed25519 AAAA…" onChange={e=>setShareKey(e.target.value)}/>
     <Action disabled={busy||ro||!shareKey.trim()} onClick={()=>void run(async()=>{const result=await shareAddKey(shareKey.trim());setShareKey("");setShare(await shareStatus());setNotice(result.added?t("Ключ добавлен"):t("Такой ключ уже есть"));})}>{t("Разрешить этому компьютеру")}</Action></>}
   </section>
   <section className="dai-section dai-diagnostics"><h3>{t("Диагностика")}</h3>
    <Action disabled={busy} onClick={()=>void run(async()=>{setChecks(null);const result=await diagnose();setChecks(result.checks);})}>{busy?t("Проверяю…"):t("Проверить подключение")}</Action>
    {checks?.map(check=><p className={"dai-muted dai-check "+(check.ok?"ok":"bad")} key={check.name}>{check.ok?"✓":"✗"} {systemText(check.name)}{check.detail?" · "+systemText(check.detail):""}</p>)}</section>
   <section className="dai-section dai-account-settings"><h3>{t("Аккаунт ChatGPT")}</h3>
    <div className="dai-account-meta"><p className="dai-account">{data?.account?.email||t("Вход не выполнен")}</p>{data?.account?.planType&&<p className="dai-muted">{data.account.planType}</p>}</div><div className="dai-account-actions">
    <Action disabled={busy} onClick={signIn}>{data?.account?t("Сменить аккаунт"):t("Войти в аккаунт")}</Action>
    {data?.loginPending&&<Action disabled={busy} onClick={()=>void run(async()=>{await accountCancelLogin();setLoginUrl("");accept(await snapshot());})}>{t("Отменить вход")}</Action>}
    {loginUrl&&<p className="dai-login-url">{loginUrl}</p>}
    {data?.account&&<Action disabled={busy} onClick={()=>showModal(<ConfirmModal strTitle={t("Выйти из ChatGPT?")} strDescription={t("Для работы Codex потребуется снова войти.")} strOKButtonText={t("Выйти")} strCancelButtonText={t("Отмена")} onOK={()=>void run(async()=>{await accountLogout();accept(await refresh());})}/>)}>{t("Выйти из аккаунта")}</Action>}
   </div></section>
  </div></div></GameScroll>}
  </div>
 </Focusable>;
}
let lastEvent:number|null=null;
async function showNotifications(){
 try{
  const result=await pollEvents(lastEvent);
  if(result.uiLanguage&&result.uiLanguage!==getUILanguage())setUILanguage(result.uiLanguage);
  const first=lastEvent===null;lastEvent=result.latest;
  // The open panel already shows approvals and results; do not toast on top.
  if(first||panelMounted>0||!flag("deck-ai-notify",true))return;
  for(const item of result.notifications.slice(-3)){
   const where=item.host?" · "+item.host:"";
   toaster.toast({
    logo:<BrandLogo size={32}/>,icon:<Icon name={item.kind==="failed"?"warning":item.kind==="approval"?"warning":item.kind==="cancelled"?"stop":"check"}/>,
    title:item.kind==="approval"?t("Deck AI · нужно подтверждение"):item.kind==="failed"?t("Deck AI · ошибка"):item.kind==="cancelled"?t("Deck AI · задача остановлена"):t("Deck AI · задача готова"),
    body:(item.kind==="approval"&&item.summary?systemText(item.summary):item.title)+where,
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
 const stopUpdates=startUpdatePolling(updateClient,async state=>{
  if(state.uiLanguage&&state.uiLanguage!==getUILanguage())setUILanguage(state.uiLanguage);
  const offer=state.available;
  if(offer&&state.notificationPending&&state.preferences.automatic){
   const key='deck-ai-update-notified',token=offer.version+':'+(state.notificationId||'');
   if(localStorage.getItem(key)!==token){
    toaster.toast({logo:<BrandLogo size={32}/>,icon:<Icon name="download"/>,title:t('Доступно обновление Deck AI'),body:t('Версия {0}. Нажмите, чтобы открыть обновление.',offer.version),duration:10000,onClick:()=>openFullscreen('settings')});
    localStorage.setItem(key,token);
   }
   await updateClient.acknowledge(offer.version);
  }
  const job=state.job;
  if(job&&['completed','failed'].includes(job.phase)&&localStorage.getItem('deck-ai-update-result')!==job.id){
   toaster.toast({logo:<BrandLogo size={32}/>,icon:<Icon name={job.phase==='completed'?'check':'warning'}/>,title:job.phase==='completed'?t('Deck AI обновлён'):t('Обновление Deck AI не завершено'),body:job.phase==='completed'?job.version:t('Откройте настройки обновлений, чтобы посмотреть подробности.'),duration:10000,onClick:()=>openFullscreen('settings')});
   localStorage.setItem('deck-ai-update-result',job.id);
  }
 });
 const stopRepairPolling=startRepairPolling();
 return {name:"Deck AI",titleView:<span style={{display:"inline-flex",alignItems:"center",gap:8}}><BrandLogo size={22}/>Deck AI</span>,content:<Panel/>,icon:<BrandLogo size={20}/>,onDismount(){
  if(returnToPanel)clearTimeout(returnToPanel);
  clearInterval(notifier);
  stopRepairPolling();
  stopUpdates();
  routerHook.removeRoute(FULLSCREEN_PATH);
 }};
});
