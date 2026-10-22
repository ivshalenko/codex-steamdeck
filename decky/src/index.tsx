import { useCallback, useEffect, useRef, useState, type CSSProperties, type ReactNode, type ComponentType, type HTMLAttributes, type RefAttributes } from "react";
import { callable, definePlugin, routerHook } from "@decky/api";
import { DialogButton, Dropdown, Focusable, TextField, ConfirmModal, showModal, ScrollPanel, Navigation, Router } from "@decky/ui";
import { FaMicrophone, FaComment, FaHistory, FaCog, FaExpand, FaCompress, FaArrowLeft, FaGamepad, FaCopy } from "react-icons/fa";
import logo from "../deck-ai.png";
import css from "./style.css";
import { speechLanguages } from "./speech-languages";
import { updateDictation, restoreDictation, bindDictation } from "./dictation";
import { readGameContext, withGameContext, gameScreenshots } from "./game-context";

type Attachment={id:string;name:string;preview:string;available:boolean;kind:"image"|"file"};
type Item = {id:string;role:"user"|"assistant";text:string;attachments?:Attachment[]};
type Media = {path:string;name:string;when?:number};
type Model = {id:string;name:string;efforts:{id:string;name:string}[];defaultEffort:string;tiers:string[]};
type Snapshot = {ready:boolean;status:string;provider:string;account?:{email?:string;planType?:string}|null;loginPending?:boolean;remoteHost?:string;sshHosts:string[];threads:{id:string;name:string;updatedAt:number}[];threadId:string;messages:Item[];active:boolean;models:Model[];model:string;effort:string;tier:string;screenshots:Media[];videos:Media[];outbox:{id:string;status:string;error?:string;text:string}[];speechVersion?:number;speechReady?:boolean;voiceId?:string;voiceState:string;voiceText:string;voiceError:string};
const snapshot=callable<[],Snapshot>("get_snapshot");
const refresh=callable<[],Snapshot>("refresh");
const selectThread=callable<[id:string],Snapshot>("select_thread");
const newThread=callable<[],Snapshot>("new_thread");
const saveSettings=callable<[model:string,effort:string,tier:string],unknown>("save_settings");
const sendMessage=callable<[text:string,images:string[],model:string,effort:string,tier:string],{queued:boolean;threadId?:string}>("send_message");
const retry=callable<[id:string],unknown>("retry");
const stop=callable<[],unknown>("stop");
const gameVoice=callable<[language:string],{voiceState:string;voiceText?:string;voiceId?:string}>("voice");
const videoFrames=callable<[path:string],{frames:Media[]}>("video_frames");
const accountLogin=callable<[],{opened:boolean;url:string;userCode?:string}>("account_login");
const accountCancelLogin=callable<[],unknown>("account_cancel_login");
const accountLogout=callable<[],unknown>("account_logout");
const remoteHost=callable<[host:string],Snapshot>("remote_host");
const setProvider=callable<[provider:string],Snapshot>("set_provider");
const setProviderKey=callable<[key:string],unknown>("set_provider_key");
const GameScroll=ScrollPanel as ComponentType<HTMLAttributes<HTMLDivElement> & RefAttributes<HTMLDivElement>>;
type Tab = "chat"|"history"|"settings";
const providerNames:Record<string,string>={codex:"Codex · ChatGPT",claude:"Claude · Pro / Max",deepseek:"DeepSeek · OpenRouter",tokenharbor:"DeepSeek · TokenHarbor"};
const draftKey=(id?:string)=>"codex-game-draft:"+(id||"new");
function Action({children,onClick,disabled=false,primary=false,recording=false}:{children:ReactNode;onClick:()=>void;disabled?:boolean;primary?:boolean;recording?:boolean}) {
 return <DialogButton className={"dai-button"+(primary?" dai-primary":"")+(recording?" dai-recording":"")} disabled={disabled} onClick={onClick}>{children}</DialogButton>;
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
const session={snapshot:null as Snapshot|null,attachments:new Map<string,Media[]>(),voiceText:"",voiceError:"",discardedVoice:localStorage.getItem("deck-ai-discarded-voice")||"",finishedVoice:"",dictation:restoreDictation(localStorage.getItem(dictationKey))};
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
 const [gameContextEnabled,toggleGameContext]=useGameContextEnabled();
 const [data,setData]=useState<Snapshot|null>(session.snapshot);
 const [tab,setTab]=useState<Tab>(initialTab);
 useEffect(()=>{
  if(!fullscreen)return;
  const change=(next:Tab)=>{setTab(next);setMediaOpen(false);};
  fullscreenViews.add(change);
  return()=>{fullscreenViews.delete(change);};
 },[fullscreen]);
 const [draft,setDraft]=useState(()=>localStorage.getItem(draftKey(session.snapshot?.threadId))||"");
 const draftId=useRef(session.snapshot?.threadId||"");
 const [busy,setBusy]=useState(false);
 const [voiceStarting,setVoiceStarting]=useState(false);
 const [voicePolling,setVoicePolling]=useState(false);
 const actionLock=useRef(false);
 const [error,setError]=useState("");
 const [notice,setNotice]=useState("");
 const [showLatest,setShowLatest]=useState(false);
 useEffect(()=>{if(!notice)return;const timer=setTimeout(()=>setNotice(""),4000);return()=>clearTimeout(timer);},[notice]);
 const [lang,setLang]=useState(()=>localStorage.getItem("codex-game-voice")||"ru");
 const [mediaOpen,setMediaOpen]=useState(false);
 const [images,setImagesState]=useState<Media[]>(()=>session.attachments.get(draftId.current)||[]);
 const setImages=(update:Media[]|((old:Media[])=>Media[]))=>setImagesState(old=>{
  const next=typeof update==="function"?update(old):update;
  session.attachments.set(draftId.current,next);
  return next;
 });
 const [shot,setShot]=useState("");const [video,setVideo]=useState("");
 const [key,setKey]=useState("");const [host,setHost]=useState("");
 const [loginUrl,setLoginUrl]=useState("");
 const [historyQuery,setHistoryQuery]=useState("");
 const lastVoice=useRef(session.voiceText);const lastVoiceError=useRef(session.voiceError);
 const inFlight=useRef(false);const mounted=useRef(true);
 const chatRef=useRef<HTMLDivElement>(null);const followTail=useRef(true);
 const accept=useCallback((incoming:Snapshot)=>{
  setVoicePolling(["recording","stopping","processing"].includes(incoming.voiceState));
  const next=incoming.voiceId===session.finishedVoice&&incoming.voiceText?{...incoming,voiceState:"done"}:incoming;
  // Change the draft and its storage key together; polling must never copy a
  // draft into a different chat when the selected conversation changes.
  if(next.threadId!==draftId.current){draftId.current=next.threadId;setDraft(localStorage.getItem(draftKey(next.threadId))||"");setImagesState(session.attachments.get(next.threadId)||[]);followTail.current=true;setShowLatest(false);}
  session.snapshot=next;setData(next);
  if(next.voiceId&&["recording","stopping","processing"].includes(next.voiceState)){
   session.dictation=bindDictation(session.dictation,next.voiceId,next.threadId,localStorage.getItem(draftKey(next.threadId))||"");
   localStorage.setItem(dictationKey,JSON.stringify(session.dictation));
  }
  if(next.voiceId&&next.voiceId!==session.discardedVoice&&next.voiceText&&next.voiceState==="done"){
   const id=next.voiceId;
   const owner=session.dictation?.id===id?session.dictation.thread:next.threadId;
   const update=updateDictation(session.dictation,id,owner,next.voiceText,localStorage.getItem(draftKey(owner))||"");
   session.dictation=update.session;
   localStorage.setItem(dictationKey,JSON.stringify(session.dictation));
   if(update.value!==null){localStorage.setItem(draftKey(owner),update.value);if(owner===draftId.current)setDraft(update.value);}
   lastVoice.current=next.voiceText;session.voiceText=next.voiceText;
  }else if(!next.voiceId&&next.voiceState==="done"&&next.voiceText&&next.voiceText!==lastVoice.current){lastVoice.current=next.voiceText;session.voiceText=next.voiceText;setDraft(old=>{const value=(old?old.trimEnd()+" ":"")+next.voiceText.trim()+" ";localStorage.setItem(draftKey(next.threadId),value);return value;});}
  if(next.voiceError&&next.voiceError!==lastVoiceError.current){lastVoiceError.current=next.voiceError;session.voiceError=next.voiceError;setError(next.voiceError);}
 },[]);
 const load=useCallback(async()=>{
  if(inFlight.current)return;
  inFlight.current=true;
  try{const next=await snapshot();if(mounted.current)accept(next);}catch(e){if(mounted.current)setError(String(e));}finally{inFlight.current=false;}
 },[accept]);
 useEffect(()=>{mounted.current=true;void load();const timer=setInterval(()=>void load(),voicePolling?500:2500);return()=>{mounted.current=false;clearInterval(timer);};},[load,voicePolling]);
 useEffect(()=>{const el=chatRef.current;if(el&&followTail.current)el.scrollTop=el.scrollHeight;},[data?.messages,tab]);
 const editDraft=(value:string)=>{setDraft(value);localStorage.setItem(draftKey(draftId.current),value);};
 const run=async(work:()=>Promise<void>)=>{if(actionLock.current)return;actionLock.current=true;setBusy(true);setError("");setNotice("");try{await work();}catch(e){setError(String(e));}finally{actionLock.current=false;setBusy(false);}};
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
   const result=await gameVoice(lang==="ru"?"ru-fast":lang==="en"?"en-fast":lang);
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
  if(localStorage.getItem(draftKey(sentThread))===sentDraft){
   localStorage.setItem(draftKey(sentThread),"");
   if(draftId.current===sentThread)setDraft("");
  }
  session.attachments.delete(sentThread);
  if(draftId.current===sentThread)setImagesState([]);
  setNotice("Запрос принят · в очереди");followTail.current=true;void load();
 });
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
 const signIn=()=>void run(async()=>{const result=await accountLogin();setLoginUrl(result.url);setNotice(result.opened?"Откройте страницу входа и завершите авторизацию.":"Ссылка для входа показана ниже.");await load();});
 const disconnect=!data?.ready;
 return <Focusable style={{"--dai-text-scale":textScale} as CSSProperties} data-text-scale={textScale} className={"dai-root"+(fullscreen?" dai-fullscreen":"")} onCancel={event=>{
  if(mediaOpen){event.stopPropagation();setMediaOpen(false);}
  else if(fullscreen){event.stopPropagation();closeFullscreen();}
 }}><style>{css}</style>
  {fullscreen&&<Focusable className="dai-full-header" flow-children="horizontal">
   <div className="dai-full-brand"><h1>Deck AI</h1><span>{disconnect?"Нет соединения":data?.active?"Deck AI работает…":gameStatus}</span></div>
   <GameCheckbox checked={gameContextEnabled} onChange={toggleGameContext}/>
   <Action onClick={()=>closeFullscreen()}><FaCompress/>В панель</Action>
   <Action onClick={()=>closeFullscreen(false)}><FaArrowLeft/>К игре</Action>
  </Focusable>}
  <Focusable className="dai-tabs" flow-children="horizontal" role="tablist" aria-label="Deck AI">
   {([["chat","Чат",<FaComment/>],["history","История",<FaHistory/>],["settings","Настройки",<FaCog/>]] as const).map(([id,label,icon])=><div key={id} role="tab" aria-selected={tab===id} className={"dai-tab "+(tab===id?"selected":"")}><Action disabled={busy} onClick={()=>{if(id==="settings"&&!fullscreen)openFullscreen("settings");else{setTab(id);setMediaOpen(false);}}}>{icon}<span>{label}</span></Action></div>)}
  </Focusable>
  <div className="dai-viewbar"><div className="dai-status"><span className={"dai-dot "+(disconnect?"offline":data?.active?"working":"")}/><span>{!data?"Подключение…":data.ready?(data.active?"Deck AI работает…":gameStatus):"Нет соединения"}</span>{data?.remoteHost&&<small>{data.remoteHost}</small>}</div>{!fullscreen&&<GameCheckbox checked={gameContextEnabled} onChange={toggleGameContext}/>}{!fullscreen&&<Action disabled={busy} onClick={()=>openFullscreen(tab)}><FaExpand/>На весь экран</Action>}</div>
  {error&&<div className="dai-banner" role="alert"><span>{error}</span><Action onClick={()=>setError("")}>Закрыть</Action></div>}
  {notice&&<div className="dai-notice" role="status">{notice}</div>}
  <div className="dai-page" role="tabpanel" aria-label={tab==="chat"?"Чат":tab==="history"?"История":"Настройки"}>
  {tab==="chat"&&<>
   {mediaOpen?<GameScroll className="dai-scroll dai-stack"><div className="dai-stack-content">
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
    <GameScroll className="dai-messages" ref={chatRef} onScroll={()=>{const el=chatRef.current;if(el){followTail.current=el.scrollHeight-el.scrollTop-el.clientHeight<60;setShowLatest(!followTail.current);}}}>
     <div className="dai-message-list">{!data?.messages.length&&<div className="dai-empty"><FaComment/><h3>Помощь прямо в игре</h3><p>Задайте вопрос текстом или голосом.<br/>Можно добавить скриншот.</p>{disconnect&&<Action onClick={()=>void run(async()=>accept(await refresh()))} disabled={busy}>{busy?"Подключение…":"Подключиться"}</Action>}</div>}
     {data?.messages.map((message,i)=><Focusable key={message.id||i} className={"dai-message "+message.role} focusClassName="dai-focused"><small>{message.role==="user"?"Вы":providerNames[data.provider]?.split(" · ")[0]||"AI"}</small><div>{message.text}</div>{!!message.attachments?.length&&<MessageAttachments items={message.attachments}/>}<div className="dai-message-tools"><Action onClick={()=>copyMessage(message.text)}><FaCopy/>Копировать</Action></div></Focusable>)}
     {data?.outbox.filter(x=>x.status==="error").map(x=><div className="dai-failed" key={x.id}><p>{x.error||"Не удалось отправить"}</p><Action disabled={busy} onClick={()=>void run(async()=>{await retry(x.id);await load();})}>Повторить отправку</Action></div>)}
    </div></GameScroll>
    {showLatest&&<div className="dai-latest"><Action onClick={jumpToLatest}>↓ К последнему сообщению</Action></div>}
    <div className="dai-composer">
     {data?.outbox.some(job=>job.status==="recovering")&&<p className="dai-muted dai-queue-state" role="status">Проверяю состояние отправленного запроса…</p>}
     {data?.outbox.some(job=>job.status==="queued")&&<p className="dai-muted dai-queue-state" role="status">В очереди · {data.outbox.filter(job=>job.status==="queued").length}{data.outbox.length===8?"+":""} · после текущего ответа</p>}
     {images.length>0&&<div className="dai-attachments">{images.map((image,i)=><Action key={image.path+":"+i} onClick={()=>setImages(old=>old.filter((_,n)=>n!==i))}>× {image.name}</Action>)}</div>}
     {(recording||voiceProcessing)&&<div className="dai-voice-preview" role="status" aria-live="polite"><span className="dai-record-dot" aria-hidden="true"/><div><strong>{recording?"● Запись · распознанный текст":"Завершаю распознавание…"}</strong><span role="textbox" aria-label="Распознанная речь" aria-readonly="true">{(data?.voiceId!==session.discardedVoice?data?.voiceText:"")||(["ru","en","ru-fast","en-fast"].includes(lang)?"Здесь появится распознанная речь":"Записываю. Текст появится после «Стоп».")}</span></div></div>}
     <div className="dai-draft-field"><TextField disabled={recording||voiceProcessing} value={draft} placeholder="Спросить об игре…" onChange={e=>editDraft(e.target.value)} onKeyDown={e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();submit();}}}/></div>
     <Focusable className="dai-compose-actions" flow-children="horizontal">
      <Action recording={recording||voiceProcessing} disabled={!data||voiceProcessing||busy} onClick={()=>void toggleVoice()}><FaMicrophone/>{recording?"Стоп":"Голос"}</Action>
      <Action disabled={voiceStarting||(!draft.trim()&&!recording&&!voiceProcessing)} onClick={clearDraft}>Очистить</Action>
      {fullscreen&&data?.active&&data.provider==="codex"&&<Action disabled={busy} onClick={()=>void run(async()=>{await stop();await load();})}>Стоп</Action>}
      <Action primary disabled={busy||disconnect||recording||voiceProcessing||!draft.trim()} onClick={submit}>{busy?"…":"Отправить"}</Action>
     </Focusable>
     {!fullscreen&&data?.active&&data.provider==="codex"&&<Action disabled={busy} onClick={()=>void run(async()=>{await stop();await load();})}>Остановить ответ</Action>}
    </div>
   </>}
  </>}
  {tab==="history"&&<GameScroll className="dai-scroll dai-stack"><div className="dai-stack-content">
   <Action primary disabled={busy||disconnect||data?.active} onClick={()=>void run(async()=>{accept(await newThread());setTab("chat");})}>＋ Новый чат</Action>
   <TextField value={historyQuery} placeholder="Найти разговор…" onChange={e=>setHistoryQuery(e.target.value)}/>
   {!data?.threads.length&&<p className="dai-muted">Ваши разговоры появятся здесь.</p>}
   {data?.threads.filter(x=>x.name.toLocaleLowerCase().includes(historyQuery.toLocaleLowerCase())).map(thread=><div className={"dai-history-item "+(thread.id===data.threadId?"selected":"")} key={thread.id}><Action disabled={busy||data.active} onClick={()=>void run(async()=>{accept(await selectThread(thread.id));setTab("chat");})}><span>{thread.name||"Новый чат"}</span>{thread.id===data.threadId&&<small>Текущий</small>}</Action></div>)}
  </div></GameScroll>}
  {tab==="settings"&&<GameScroll className="dai-scroll dai-stack dai-settings"><div className="dai-settings-grid"><div className="dai-settings-column">
   <section className="dai-section dai-model-settings"><h3>Модель и ответ</h3><div className="dai-model-fields">
    <Choice label="Сервис" value={data?.provider||"codex"} options={Object.entries(providerNames).map(([data,label])=>({data,label}))} disabled={busy||data?.active} onChange={value=>void run(async()=>{accept(await setProvider(value));setKey("");})}/>
    <Choice label="Модель" value={model?.id||""} options={(data?.models||[]).map(x=>({data:x.id,label:x.name}))} disabled={busy} onChange={id=>{const next=data?.models.find(x=>x.id===id);settings(id,next?.defaultEffort||next?.efforts[0]?.id||"","default");}}/>
    {data?.provider==="codex"&&<><Choice label="Глубина обработки" value={effort} options={(model?.efforts||[]).map(x=>({data:x.id,label:x.name}))} disabled={busy} onChange={value=>settings(model?.id||"",value,tier)}/><Choice label="Скорость" value={tier} options={[{data:"default",label:"Обычная"},...(model?.tiers.includes("priority")?[{data:"priority",label:"Приоритетная"}]:[])]} disabled={busy} onChange={value=>settings(model?.id||"",effort,value)}/></>}
    </div>{(data?.provider==="deepseek"||data?.provider==="tokenharbor")&&<><TextField bIsPassword value={key} placeholder="Ключ API" onChange={e=>setKey(e.target.value)}/><Action disabled={busy||!key.trim()} onClick={()=>void run(async()=>{await setProviderKey(key.trim());setKey("");accept(await refresh());setNotice("Ключ сохранён");})}>Сохранить ключ</Action><p className="dai-muted">Ключ хранится в системном хранилище SteamOS.</p></>}
    {data?.provider==="claude"&&<p className="dai-muted">Используется вход Claude Code, настроенный в режиме рабочего стола.</p>}
   </section>
   <section className="dai-section dai-text-settings"><h3>Интерфейс и голос</h3><div className="dai-personal-fields"><div className="dai-field"><span className="dai-label">Масштаб чата и кнопок</span>
    <Focusable className="dai-scale-controls" flow-children="horizontal">
     <Action disabled={textScale<=.7} onClick={()=>setTextScale(textScale-.1)}>А−</Action>
     <span className="dai-scale-value" aria-live="polite">{Math.round(textScale*100)}%</span>
     <Action disabled={textScale>=1.5} onClick={()=>setTextScale(textScale+.1)}>А+</Action>
     <Action disabled={textScale===1} onClick={()=>setTextScale(1)}>Сброс</Action>
    </Focusable></div>
   <Choice label="Язык распознавания" value={lang} options={!data?.speechReady?[{data:"ru",label:"Русский"},{data:"en",label:"English"}]:[{data:"auto",label:"Определять автоматически"},...Object.entries(speechLanguages).sort(([a],[b])=>a==="ru"?-1:b==="ru"?1:a==="en"?-1:b==="en"?1:0).map(([data,label])=>({data,label})),{data:"ru-fast",label:"Русский · экономный"},{data:"en-fast",label:"English · экономный"}]} onChange={value=>{setLang(value);localStorage.setItem("codex-game-voice",value);}}/></div>
    {data?.speechVersion===2&&!data.speechReady&&<p className="dai-muted">Для других языков установите многоязычную модель: scripts/download-models.sh --accurate-ru</p>}
    <div className="dai-game-setting"><span className="dai-muted">Добавлять только название игры</span><GameCheckbox checked={gameContextEnabled} onChange={toggleGameContext}/></div></section>
   </div><div className="dai-settings-column">
   <section className="dai-section dai-connection-settings"><h3>Подключение Codex</h3><div className="dai-connection-bar">
    <p className="dai-muted">{(data?.active?"Deck AI работает…":data?.status)||"Сервер пока недоступен. Можно повторить подключение."}</p>
    <Action disabled={busy} onClick={()=>void run(async()=>{accept(await refresh());setNotice("Соединение обновлено");})}>{busy?"Подключение…":"Переподключиться"}</Action></div>
    {(!data||data.provider==="codex")&&<><Choice label="Устройство" value={data?.remoteHost||""} options={[{data:"",label:"Этот Steam Deck"},...(data?.sshHosts||[]).map(x=>({data:x,label:x}))]} disabled={busy||data?.active} onChange={value=>void run(async()=>accept(await remoteHost(value)))}/><div className="dai-host-entry"><TextField value={host} placeholder="Другой SSH-алиас" onChange={e=>setHost(e.target.value)}/><Action disabled={busy||!host.trim()||data?.active} onClick={()=>void run(async()=>{accept(await remoteHost(host.trim()));setHost("");})}>Подключить</Action></div></>}
   </section>
   <section className="dai-section dai-account-settings"><h3>Аккаунт ChatGPT</h3>
    <div className="dai-account-meta"><p className="dai-account">{data?.account?.email||"Вход не выполнен"}</p>{data?.account?.planType&&<p className="dai-muted">{data.account.planType}</p>}</div><div className="dai-account-actions">
    <Action disabled={busy} onClick={signIn}>{data?.account?"Сменить аккаунт":"Войти в аккаунт"}</Action>
    {data?.loginPending&&<Action disabled={busy} onClick={()=>void run(async()=>{await accountCancelLogin();setLoginUrl("");await load();})}>Отменить вход</Action>}
    {loginUrl&&<p className="dai-login-url">{loginUrl}</p>}
    {data?.account&&<Action disabled={busy} onClick={()=>showModal(<ConfirmModal strTitle="Выйти из ChatGPT?" strDescription="Для работы Codex потребуется снова войти." strOKButtonText="Выйти" strCancelButtonText="Отмена" onOK={()=>void run(async()=>{await accountLogout();accept(await refresh());})}/>)}>Выйти из аккаунта</Action>}
   </div></section>
  </div></div></GameScroll>}
  </div>
 </Focusable>;
}
export default definePlugin(()=>{
 routerHook.addRoute(FULLSCREEN_PATH,FullscreenPage,{exact:true});
 return {name:"Deck AI",titleView:<span>Deck AI</span>,content:<Panel/>,icon:<img src={logo} alt="Deck AI" style={{width:20,height:20,objectFit:"contain"}}/>,onDismount(){
  if(returnToPanel)clearTimeout(returnToPanel);
  routerHook.removeRoute(FULLSCREEN_PATH);
 }};
});
