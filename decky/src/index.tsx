import { useCallback, useEffect, useRef, useState } from "react";
import { callable, definePlugin } from "@decky/api";
import { FaMicrophone, FaCamera, FaDesktop, FaUserCircle, FaSignOutAlt, FaExternalLinkAlt, FaPlus, FaLaptop } from "react-icons/fa";
import logo from "../codex-official.png";
import css from "./style.css";

type Item = {id:string;role:"user"|"assistant";text:string};
type Media = {path:string;name:string;when?:number;size?:number};
type Model = {id:string;name:string;efforts:{id:string;name:string}[];defaultEffort:string;tiers:string[]};
type Account = {type?:string;email?:string;planType?:string}|null;
type Snapshot = {voiceState:string;voiceText:string;voiceError:string;ready:boolean;status:string;provider:string;account?:Account;loginPending?:boolean;remoteHost?:string;sshHosts:string[];threads:{id:string;name:string;updatedAt:number}[];threadId:string;messages:Item[];active:boolean;models:Model[];model:string;effort:string;tier:string;screenshots:Media[];videos:Media[];outbox:{id:string;status:string;error?:string;text:string}[]};
const snapshot=callable<[],Snapshot>("get_snapshot");
const refresh=callable<[],Snapshot>("refresh");
const selectThread=callable<[id:string],Snapshot>("select_thread");
const newThread=callable<[],Snapshot>("new_thread");
const saveSettings=callable<[model:string,effort:string,tier:string],unknown>("save_settings");
const sendMessage=callable<[text:string,images:string[],model:string,effort:string,tier:string],{queued:boolean}>("send_message");
const retry=callable<[id:string],unknown>("retry");
const stop=callable<[],unknown>("stop");
const gameVoice=callable<[language:string],{voiceState:string}>("voice");
const videoFrames=callable<[path:string],{frames:Media[]}>("video_frames");
const openDesktop=callable<[],unknown>("open_desktop");
const accountLogin=callable<[],{opened:boolean;url:string;userCode?:string}>("account_login");
const accountCancelLogin=callable<[],{cancelled:boolean}>("account_cancel_login");
const accountLogout=callable<[],{loggedOut:boolean}>("account_logout");
const remoteHost=callable<[host:string],Snapshot>("remote_host");
const setProvider=callable<[provider:string],Snapshot>("set_provider");
const setProviderKey=callable<[key:string],{saved:boolean}>("set_provider_key");

function Panel() {
 const [data,setData]=useState<Snapshot|null>(null);
 const [accountOpen,setAccountOpen]=useState(false);const [accountBusy,setAccountBusy]=useState(false);
 const [hostInput,setHostInput]=useState("");const [hostBusy,setHostBusy]=useState(false);
 const [hostEntryOpen,setHostEntryOpen]=useState(false);
 const [draft,setDraft]=useState(()=>localStorage.getItem("codex-game-draft:new")||"");const [busy,setBusy]=useState(false);const [error,setError]=useState("");const [lang,setLang]=useState(()=>localStorage.getItem("codex-game-voice")||"en");
 const [images,setImages]=useState<Media[]>([]);const [shot,setShot]=useState("");const [video,setVideo]=useState("");
 const [providerKey,setProviderKeyInput]=useState("");const [providerBusy,setProviderBusy]=useState(false);
 const lastVoice=useRef("");const lastVoiceError=useRef("");
 const endRef=useRef<HTMLDivElement>(null);
 const load=useCallback(async()=>{try{const d=await snapshot();setData(d);if(d.voiceState==="done"&&d.voiceText&&d.voiceText!==lastVoice.current){lastVoice.current=d.voiceText;setDraft(x=>(x?x.trimEnd()+" ":"")+d.voiceText.trim()+" ");if(d.voiceError&&d.voiceError!==lastVoiceError.current){lastVoiceError.current=d.voiceError;setError(d.voiceError);}}else if(d.voiceError&&d.voiceError!==lastVoiceError.current){lastVoiceError.current=d.voiceError;setError(d.voiceError);}}catch(e){setError(String(e));}},[]);
 useEffect(()=>{const style=document.createElement("style");style.textContent=css;document.head.appendChild(style);return()=>style.remove();},[]);
 useEffect(()=>{let alive=true;const run=async()=>{try{const d=await snapshot();if(alive){setData(d);if(d.voiceState==="done"&&d.voiceText&&d.voiceText!==lastVoice.current){lastVoice.current=d.voiceText;setDraft(x=>(x?x.trimEnd()+" ":"")+d.voiceText.trim()+" ");if(d.voiceError&&d.voiceError!==lastVoiceError.current){lastVoiceError.current=d.voiceError;setError(d.voiceError);}}else if(d.voiceError&&d.voiceError!==lastVoiceError.current){lastVoiceError.current=d.voiceError;setError(d.voiceError);}}}catch(e){if(alive)setError(String(e));}};void run();const timer=setInterval(run,3000);return()=>{alive=false;clearInterval(timer);};},[]);
 useEffect(()=>{const key="codex-game-draft:"+(data?.threadId||"new");setDraft(localStorage.getItem(key)||"");},[data?.threadId]);
 useEffect(()=>{setHostInput(data?.remoteHost||"");},[data?.remoteHost]);
 useEffect(()=>{localStorage.setItem("codex-game-draft:"+(data?.threadId||"new"),draft);},[draft,data?.threadId]);
 useEffect(()=>{endRef.current?.scrollIntoView({behavior:"smooth",block:"end"});},[data?.messages.length]);
 const model=data?.models.find(x=>x.id===data.model)||data?.models[0];
 const effort=data?.effort||model?.defaultEffort||model?.efforts[0]?.id||"low";
 const tier=data?.tier||"default";
 const setModel=(id:string)=>{if(!data)return;const next=data.models.find(x=>x.id===id);const depth=next?.defaultEffort||next?.efforts[0]?.id||"low";setData({...data,model:id,effort:depth,tier:"default"});void saveSettings(id,depth,"default");};
 const setEffort=(value:string)=>{setData(old=>old?{...old,effort:value}:old);if(data?.model)void saveSettings(data.model,value,tier);};
 const setTier=(value:string)=>{setData(old=>old?{...old,tier:value}:old);if(data?.model)void saveSettings(data.model,effort,value);};
 const attachShot=()=>{const value=shot||data?.screenshots[0]?.path;if(!value)return;const media=data?.screenshots.find(x=>x.path===value);setImages(old=>old.some(x=>x.path===value)?old:[...old,{path:value,name:media?.name||"Steam screenshot"}]);};
 const attachFrames=async()=>{if(!video)return;setBusy(true);setError("");try{const result=await videoFrames(video);setImages(old=>[...old,...result.frames]);setError(result.frames.length+" game frame(s) attached");}catch(e){setError(String(e));}finally{setBusy(false);}};
 const submit=async()=>{if(busy||!data)return;if(!draft.trim()&&!images.length)return;setBusy(true);setError("");try{await sendMessage(draft,images.map(x=>x.path),data.model,effort,tier);setDraft("");localStorage.removeItem("codex-game-draft:"+(data.threadId||"new"));setImages([]);setTimeout(()=>void load(),400);}catch(e){setError(String(e));}finally{setBusy(false);}};
 const startVoice=async()=>{if(!data)return;try{await gameVoice(lang);if(data.voiceState!=="recording"&&data.voiceState!=="stopping")setError("Listening… press Stop to finish dictation.");else setError("Stopping recording…");}catch(e){setError(String(e));}};
 const cycleVoice=()=>{const next=lang==="ru"?"en":"ru";localStorage.setItem("codex-game-voice",next);setLang(next);setError("Recognition language: "+next.toUpperCase());};
 const signIn=async()=>{setAccountBusy(true);setError("");try{const result=await accountLogin();if(result.opened)setError("Opened Codex account sign-in page.");else setError("Open this sign-in link: "+result.url);}catch(e){setError(String(e));}finally{setAccountBusy(false);}};
 const signOut=async()=>{setAccountBusy(true);setError("");try{await accountLogout();setData(await refresh());setError("Signed out of Codex.");}catch(e){setError(String(e));}finally{setAccountBusy(false);}};
 const cancelSignIn=async()=>{setAccountBusy(true);try{await accountCancelLogin();setData(await refresh());setError("Sign-in cancelled.");}catch(e){setError(String(e));}finally{setAccountBusy(false);}};
 const connectHost=async(host=hostInput.trim())=>{setHostBusy(true);setError("");try{setData(await remoteHost(host));setHostEntryOpen(false);setError(host?"Connected to remote Codex over SSH.":"Using Codex on Steam Deck.");}catch(e){setError(String(e));}finally{setHostBusy(false);}};
 const changeProvider=async(value:string)=>{setHostBusy(true);setError("");try{setData(await setProvider(value));setError(value==="claude"?"Claude uses the Claude Code login on this Steam Deck.":value==="deepseek"?"DeepSeek requests are sent to OpenRouter and may be billed to your OpenRouter account.":"Using your signed-in Codex account.");}catch(e){setError(String(e));}finally{setHostBusy(false);}};
 const saveProviderKey=async()=>{if(!providerKey.trim())return;setProviderBusy(true);setError("");try{await setProviderKey(providerKey.trim());setProviderKeyInput("");setData(await refresh());setError("OpenRouter key saved in the system secret store.");}catch(e){setError(String(e));}finally{setProviderBusy(false);}};
 if(!data&&!error)return <div className="cdx-loading"><span className="cdx-orb"/>Connecting to Codex…</div>;
 return <div className="cdx-root">
  <header className="cdx-header"><span className="cdx-icon"><img src={logo} alt="Codex"/></span><div className="cdx-brand">Codex<span>GAME MODE</span></div><span className={"cdx-state "+(data?.active?"cdx-working":"")}>{data?.active?"Working":data?.status||"Not connected"}</span><button className={"cdx-iconbutton "+(accountOpen?"cdx-account-active":"")} title="Codex account" aria-label="Codex account" onClick={()=>setAccountOpen(x=>!x)}><FaUserCircle/></button><button className="cdx-iconbutton" title="Open desktop app" onClick={()=>void openDesktop()}><FaDesktop/></button><button className="cdx-iconbutton" title="Refresh" onClick={()=>void refresh().then(setData)} aria-label="Refresh">↻</button></header>
  {accountOpen&&<section className="cdx-account"><div className="cdx-account-info"><FaUserCircle/><div><strong>{data?.account?.email||"No account connected"}</strong><small>{data?.account?.planType?"Plan · "+data.account.planType:data?.loginPending?"Waiting for sign-in in browser":"Signed in with ChatGPT"}</small></div></div><div className="cdx-account-actions">{data?.loginPending?<button disabled={accountBusy} onClick={()=>void cancelSignIn()}>Cancel sign-in</button>:<button disabled={accountBusy} onClick={()=>void signIn()}><FaExternalLinkAlt/>{data?.account?"Switch account":"Sign in"}</button>}{data?.account&&<button className="cdx-account-logout" disabled={accountBusy} onClick={()=>void signOut()}><FaSignOutAlt/>Sign out</button>}</div></section>}
  {data?.provider==="codex"&&<section className="cdx-devices" aria-label="Codex devices"><span>DEVICES</span><div className="cdx-device-list"><button className={!data?.remoteHost?"selected":""} disabled={hostBusy} onClick={()=>void connectHost("")}><FaDesktop/>Steam Deck</button>{(data?.sshHosts||[]).map(host=><button key={host} className={data?.remoteHost===host?"selected":""} disabled={hostBusy} onClick={()=>void connectHost(host)}><FaLaptop/>{host}</button>)}<button className="cdx-device-add" title="Add SSH host" onClick={()=>setHostEntryOpen(x=>!x)}><FaPlus/></button></div>{hostEntryOpen&&<div className="cdx-device-entry"><input aria-label="Codex SSH alias" placeholder="SSH alias, e.g. Mac" value={hostInput} onChange={e=>setHostInput(e.target.value)} onKeyDown={e=>{if(e.key==="Enter")void connectHost();}}/><button disabled={hostBusy||!hostInput.trim()} onClick={()=>void connectHost()}>{hostBusy?"…":"Connect"}</button></div>}</section>}
  {error&&<div className="cdx-error"><span>{error}</span><button onClick={()=>setError("")}>×</button></div>}
  <div className="cdx-selects"><label className="cdx-provider-label">Model provider<select aria-label="Model provider" value={data?.provider||"codex"} onChange={e=>void changeProvider(e.target.value)}><option value="codex">Codex · ChatGPT plan</option><option value="claude">Claude · Pro / Max via Claude Code</option><option value="deepseek">DeepSeek · OpenRouter</option></select></label>
   {data?.provider==="deepseek"&&<><div className="cdx-key-entry"><input type="password" autoComplete="off" spellCheck={false} aria-label="OpenRouter API key" placeholder="OpenRouter API key" value={providerKey} onChange={e=>setProviderKeyInput(e.target.value)} onKeyDown={e=>{if(e.key==="Enter")void saveProviderKey();}}/><button disabled={providerBusy||!providerKey.trim()} onClick={()=>void saveProviderKey()}>{providerBusy?"…":"Save key"}</button></div><small className="cdx-key-note">Saved to the SteamOS system secret store. OpenRouter charges are separate from Codex.</small></>}
   {data?.provider==="claude"&&<button className="cdx-claude-login" onClick={()=>void openDesktop()}>Open desktop app to install or sign in to Claude Code</button>}
   <div className="cdx-chatrow"><select aria-label="Chat" value={data?.threadId||""} onChange={e=>e.target.value?void selectThread(e.target.value).then(setData):void newThread().then(setData)}><option value="">＋ New chat</option>{data?.threads.map(x=><option key={x.id} value={x.id}>{x.name.slice(0,52)}</option>)}</select><button className="cdx-small" onClick={()=>void newThread().then(setData)}>＋</button></div>
   <details className="cdx-model-settings"><summary title="Choose model, reasoning effort, and speed"><span>{model?.name||"Model"}</span>{data?.provider==="codex"&&<><span>{effort}</span><span>{tier==="priority"?"Fast":"Standard"}</span></>}</summary><div className="cdx-model-settings-menu"><label>Model<select aria-label="Model" value={model?.id||""} onChange={e=>setModel(e.target.value)}>{data?.models.map(x=><option key={x.id} value={x.id}>{x.name}</option>)}</select></label>{data?.provider==="codex"&&<div className="cdx-controls"><label>Reasoning<select aria-label="Reasoning" value={effort} onChange={e=>setEffort(e.target.value)}>{model?.efforts.map(x=><option key={x.id} value={x.id}>{x.name}</option>)}</select></label><label>Speed<select aria-label="Speed" value={tier} onChange={e=>setTier(e.target.value)}><option value="default">Standard</option>{model?.tiers.includes("priority")&&<option value="priority">Fast · quicker</option>}</select></label></div>}</div></details>
  </div>
  <div className="cdx-chat">{data?.outbox.filter(j=>j.status==="error").map(j=><div key={j.id} className="cdx-error"><span>{j.error||"Send failed"}</span><button onClick={()=>void retry(j.id).then(load)}>Retry</button></div>)}{data?.messages.map((m,i)=><article key={m.id||i} className={"cdx-msg "+m.role}><small>{m.role==="user"?"YOU":(data?.provider||"codex").toUpperCase()}</small><div>{m.text.length>4200?m.text.slice(-4200):m.text}</div></article>)}{data?.active&&<div className="cdx-typing"><i/>{data.provider==="claude"?"Claude is working…":data.provider==="deepseek"?"DeepSeek is working…":"Codex is working…"}</div>}<div ref={endRef}/></div>
  <section className="cdx-tools"><div className="cdx-media">
   <select aria-label="Steam screenshot" value={shot} onChange={e=>setShot(e.target.value)}><option value="">Latest game screenshot…</option>{data?.screenshots.map(x=><option key={x.path} value={x.path}>{x.when?new Date(x.when*1000).toLocaleString():"Steam"} · {x.name}</option>)}</select><button className="cdx-small cdx-camera" title="Attach selected screenshot" onClick={attachShot}><FaCamera/></button>
   <select aria-label="Steam video" value={video} onChange={e=>setVideo(e.target.value)}><option value="">Choose game recording…</option>{data?.videos.map(x=><option key={x.path} value={x.path}>{x.name}</option>)}</select><button className="cdx-small cdx-frames" title="Attach video frames" disabled={!video||busy} onClick={()=>void attachFrames()}>Frames</button>
  </div>{images.length>0&&<div className="cdx-attachments">{images.map((x,i)=><button key={x.path} onClick={()=>setImages(old=>old.filter((_,n)=>n!==i))}>▧ {x.name} ×</button>)}</div>}
  <textarea aria-label="Message Codex" placeholder="Ask about the game or attach a screenshot…" value={draft} onChange={e=>setDraft(e.target.value)} onKeyDown={e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();void submit();}}}/>
  <div className="cdx-compose"><button className={"cdx-voice "+(data?.voiceState==="recording"?"active":"")} onClick={()=>void startVoice()}><FaMicrophone/>{data?.voiceState==="recording"||data?.voiceState==="stopping"?"Stop":"Voice"}</button><button className="cdx-small" onClick={cycleVoice} title="Switch dictation language">{lang.toUpperCase()}</button><span className="cdx-hint">{data?.voiceState==="recording"?"Recording · press Stop":"↵ send · Steam+B opens keyboard"}</span>{data?.active&&data?.provider==="codex"&&<button className="cdx-stop" onClick={()=>void stop()}>Stop response</button>}<button className="cdx-send" disabled={busy||(!draft.trim()&&!images.length)} onClick={()=>void submit()}>{busy?"…":"Send"}</button></div>
  </section>
 </div>;
}
export default definePlugin(()=>({name:"Codex",titleView:<div className="cdx-title">Codex <span>GAME MODE</span></div>,content:<Panel/>,icon:<img src={logo} alt="Codex"/>}));
