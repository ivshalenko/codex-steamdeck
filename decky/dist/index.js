const manifest = {"name":"Deck AI"};
const API_VERSION = 2;
const internalAPIConnection = window.__DECKY_SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED_deckyLoaderAPIInit;
if (!internalAPIConnection) {
    throw new Error('[@decky/api]: Failed to connect to the loader as as the loader API was not initialized. This is likely a bug in Decky Loader.');
}
let api;
try {
    api = internalAPIConnection.connect(API_VERSION, manifest.name);
}
catch {
    api = internalAPIConnection.connect(1, manifest.name);
    console.warn(`[@decky/api] Requested API version ${API_VERSION} but the running loader only supports version 1. Some features may not work.`);
}
if (api._version != API_VERSION) {
    console.warn(`[@decky/api] Requested API version ${API_VERSION} but the running loader only supports version ${api._version}. Some features may not work.`);
}
const callable = api.callable;
const definePlugin = (fn) => {
    return (...args) => {
        return fn(...args);
    };
};

var DefaultContext = {
  color: undefined,
  size: undefined,
  className: undefined,
  style: undefined,
  attr: undefined
};
var IconContext = SP_REACT.createContext && /*#__PURE__*/SP_REACT.createContext(DefaultContext);

var _excluded = ["attr", "size", "title"];
function _objectWithoutProperties(e, t) { if (null == e) return {}; var o, r, i = _objectWithoutPropertiesLoose(e, t); if (Object.getOwnPropertySymbols) { var n = Object.getOwnPropertySymbols(e); for (r = 0; r < n.length; r++) o = n[r], -1 === t.indexOf(o) && {}.propertyIsEnumerable.call(e, o) && (i[o] = e[o]); } return i; }
function _objectWithoutPropertiesLoose(r, e) { if (null == r) return {}; var t = {}; for (var n in r) if ({}.hasOwnProperty.call(r, n)) { if (-1 !== e.indexOf(n)) continue; t[n] = r[n]; } return t; }
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function ownKeys(e, r) { var t = Object.keys(e); if (Object.getOwnPropertySymbols) { var o = Object.getOwnPropertySymbols(e); r && (o = o.filter(function (r) { return Object.getOwnPropertyDescriptor(e, r).enumerable; })), t.push.apply(t, o); } return t; }
function _objectSpread(e) { for (var r = 1; r < arguments.length; r++) { var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), true).forEach(function (r) { _defineProperty(e, r, t[r]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach(function (r) { Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r)); }); } return e; }
function _defineProperty(e, r, t) { return (r = _toPropertyKey(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e; }
function _toPropertyKey(t) { var i = _toPrimitive(t, "string"); return "symbol" == typeof i ? i : i + ""; }
function _toPrimitive(t, r) { if ("object" != typeof t || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r); if ("object" != typeof i) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function Tree2Element(tree) {
  return tree && tree.map((node, i) => /*#__PURE__*/SP_REACT.createElement(node.tag, _objectSpread({
    key: i
  }, node.attr), Tree2Element(node.child)));
}
function GenIcon(data) {
  return props => /*#__PURE__*/SP_REACT.createElement(IconBase, _extends({
    attr: _objectSpread({}, data.attr)
  }, props), Tree2Element(data.child));
}
function IconBase(props) {
  var elem = conf => {
    var attr = props.attr,
      size = props.size,
      title = props.title,
      svgProps = _objectWithoutProperties(props, _excluded);
    var computedSize = size || conf.size || "1em";
    var className;
    if (conf.className) className = conf.className;
    if (props.className) className = (className ? className + " " : "") + props.className;
    return /*#__PURE__*/SP_REACT.createElement("svg", _extends({
      stroke: "currentColor",
      fill: "currentColor",
      strokeWidth: "0"
    }, conf.attr, attr, svgProps, {
      className: className,
      style: _objectSpread(_objectSpread({
        color: props.color || conf.color
      }, conf.style), props.style),
      height: computedSize,
      width: computedSize,
      xmlns: "http://www.w3.org/2000/svg"
    }), title && /*#__PURE__*/SP_REACT.createElement("title", null, title), props.children);
  };
  return IconContext !== undefined ? /*#__PURE__*/SP_REACT.createElement(IconContext.Consumer, null, conf => elem(conf)) : elem(DefaultContext);
}

// THIS FILE IS AUTO GENERATED
function FaUserCircle (props) {
  return GenIcon({"attr":{"viewBox":"0 0 496 512"},"child":[{"tag":"path","attr":{"d":"M248 8C111 8 0 119 0 256s111 248 248 248 248-111 248-248S385 8 248 8zm0 96c48.6 0 88 39.4 88 88s-39.4 88-88 88-88-39.4-88-88 39.4-88 88-88zm0 344c-58.7 0-111.3-26.6-146.5-68.2 18.8-35.4 55.6-59.8 98.5-59.8 2.4 0 4.8.4 7.1 1.1 13 4.2 26.6 6.9 40.9 6.9 14.3 0 28-2.7 40.9-6.9 2.3-.7 4.7-1.1 7.1-1.1 42.9 0 79.7 24.4 98.5 59.8C359.3 421.4 306.7 448 248 448z"},"child":[]}]})(props);
}function FaSignOutAlt (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M497 273L329 441c-15 15-41 4.5-41-17v-96H152c-13.3 0-24-10.7-24-24v-96c0-13.3 10.7-24 24-24h136V88c0-21.4 25.9-32 41-17l168 168c9.3 9.4 9.3 24.6 0 34zM192 436v-40c0-6.6-5.4-12-12-12H96c-17.7 0-32-14.3-32-32V160c0-17.7 14.3-32 32-32h84c6.6 0 12-5.4 12-12V76c0-6.6-5.4-12-12-12H96c-53 0-96 43-96 96v192c0 53 43 96 96 96h84c6.6 0 12-5.4 12-12z"},"child":[]}]})(props);
}function FaPlus (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M416 208H272V64c0-17.67-14.33-32-32-32h-32c-17.67 0-32 14.33-32 32v144H32c-17.67 0-32 14.33-32 32v32c0 17.67 14.33 32 32 32h144v144c0 17.67 14.33 32 32 32h32c17.67 0 32-14.33 32-32V304h144c17.67 0 32-14.33 32-32v-32c0-17.67-14.33-32-32-32z"},"child":[]}]})(props);
}function FaMicrophone (props) {
  return GenIcon({"attr":{"viewBox":"0 0 352 512"},"child":[{"tag":"path","attr":{"d":"M176 352c53.02 0 96-42.98 96-96V96c0-53.02-42.98-96-96-96S80 42.98 80 96v160c0 53.02 42.98 96 96 96zm160-160h-16c-8.84 0-16 7.16-16 16v48c0 74.8-64.49 134.82-140.79 127.38C96.71 376.89 48 317.11 48 250.3V208c0-8.84-7.16-16-16-16H16c-8.84 0-16 7.16-16 16v40.16c0 89.64 63.97 169.55 152 181.69V464H96c-8.84 0-16 7.16-16 16v16c0 8.84 7.16 16 16 16h160c8.84 0 16-7.16 16-16v-16c0-8.84-7.16-16-16-16h-56v-33.77C285.71 418.47 352 344.9 352 256v-48c0-8.84-7.16-16-16-16z"},"child":[]}]})(props);
}function FaLaptop (props) {
  return GenIcon({"attr":{"viewBox":"0 0 640 512"},"child":[{"tag":"path","attr":{"d":"M624 416H381.54c-.74 19.81-14.71 32-32.74 32H288c-18.69 0-33.02-17.47-32.77-32H16c-8.8 0-16 7.2-16 16v16c0 35.2 28.8 64 64 64h512c35.2 0 64-28.8 64-64v-16c0-8.8-7.2-16-16-16zM576 48c0-26.4-21.6-48-48-48H112C85.6 0 64 21.6 64 48v336h512V48zm-64 272H128V64h384v256z"},"child":[]}]})(props);
}function FaExternalLinkAlt (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M432,320H400a16,16,0,0,0-16,16V448H64V128H208a16,16,0,0,0,16-16V80a16,16,0,0,0-16-16H48A48,48,0,0,0,0,112V464a48,48,0,0,0,48,48H400a48,48,0,0,0,48-48V336A16,16,0,0,0,432,320ZM488,0h-128c-21.37,0-32.05,25.91-17,41l35.73,35.73L135,320.37a24,24,0,0,0,0,34L157.67,377a24,24,0,0,0,34,0L435.28,133.32,471,169c15,15,41,4.5,41-17V24A24,24,0,0,0,488,0Z"},"child":[]}]})(props);
}function FaDesktop (props) {
  return GenIcon({"attr":{"viewBox":"0 0 576 512"},"child":[{"tag":"path","attr":{"d":"M528 0H48C21.5 0 0 21.5 0 48v320c0 26.5 21.5 48 48 48h192l-16 48h-72c-13.3 0-24 10.7-24 24s10.7 24 24 24h272c13.3 0 24-10.7 24-24s-10.7-24-24-24h-72l-16-48h192c26.5 0 48-21.5 48-48V48c0-26.5-21.5-48-48-48zm-16 352H64V64h448v288z"},"child":[]}]})(props);
}function FaCamera (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M512 144v288c0 26.5-21.5 48-48 48H48c-26.5 0-48-21.5-48-48V144c0-26.5 21.5-48 48-48h88l12.3-32.9c7-18.7 24.9-31.1 44.9-31.1h125.5c20 0 37.9 12.4 44.9 31.1L376 96h88c26.5 0 48 21.5 48 48zM376 288c0-66.2-53.8-120-120-120s-120 53.8-120 120 53.8 120 120 120 120-53.8 120-120zm-32 0c0 48.5-39.5 88-88 88s-88-39.5-88-88 39.5-88 88-88 88 39.5 88 88z"},"child":[]}]})(props);
}

var logo = 'http://127.0.0.1:1337/plugins/Deck AI/assets/deck-ai-2f73c1d3.png';

var css = ".cdx-root{height:100%;min-height:500px;display:flex;flex-direction:column;gap:10px;padding:9px 12px 13px;box-sizing:border-box;color:#ececec;font-family:Inter,\"Noto Sans\",system-ui,sans-serif;background:#171717;--cdx-border:rgba(255,255,255,.095);--cdx-raised:#222}\n.cdx-root button,.cdx-root select,.cdx-root textarea,.cdx-root input{font:inherit;color:inherit}.cdx-root button{border:1px solid var(--cdx-border);background:#252525;border-radius:11px;cursor:pointer}.cdx-root button:active{background:#3a3a3a}.cdx-header{display:flex;align-items:center;gap:9px;min-height:34px;border-bottom:1px solid var(--cdx-border);padding-bottom:7px}.cdx-icon{display:grid;place-items:center;width:30px;height:30px;background:transparent;border-radius:9px;font-size:17px}.cdx-brand{font-size:16px;font-weight:650;line-height:1.1}.cdx-brand span,.cdx-title span{display:block;color:#8d8d8d;font-size:8px;font-weight:600;letter-spacing:.12em;margin-top:2px}.cdx-state{margin-left:auto;color:#bcbcbc;font-size:11px;max-width:95px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.cdx-state:before{content:\"\";display:inline-block;width:6px;height:6px;background:#56b979;border-radius:50%;margin:0 6px 1px 0}.cdx-working:before{background:#ddac51}.cdx-iconbutton{width:30px;height:30px;display:grid;place-items:center;color:#bbb!important;font-size:17px}.cdx-title{font-weight:650;letter-spacing:.01em}.cdx-selects{display:flex;flex-direction:column;gap:6px}.cdx-provider-label{display:flex;flex-direction:column;gap:3px;color:#929292;font-size:9px;font-weight:650;letter-spacing:.06em;text-transform:uppercase}.cdx-key-entry{display:flex;gap:5px}.cdx-key-entry input{min-width:0;flex:1;background:#202020;border:1px solid var(--cdx-border);border-radius:9px;padding:7px 9px;font-size:11px;outline:none}.cdx-key-entry button,.cdx-claude-login{min-height:34px;padding:0 9px;font-size:10px;white-space:normal}.cdx-key-note{color:#888;font-size:9px;line-height:1.3}.cdx-chatrow,.cdx-modelrow,.cdx-controls{display:flex;gap:6px}.cdx-root select{appearance:none;background:#222;border:1px solid var(--cdx-border);border-radius:9px;min-height:36px;padding:5px 28px 5px 10px;font-size:12px;min-width:0;flex:1;background-image:linear-gradient(45deg,transparent 50%,#999 50%),linear-gradient(135deg,#999 50%,transparent 50%);background-position:calc(100% - 13px) 15px,calc(100% - 9px) 15px;background-size:4px 4px;background-repeat:no-repeat}.cdx-chatrow .cdx-small{width:36px;flex:none;font-size:19px}.cdx-controls select{font-size:11px}.cdx-chat{min-height:70px;flex:1;overflow-y:auto;display:flex;flex-direction:column;gap:8px;padding:2px 3px 6px;scrollbar-width:thin;scrollbar-color:#4b4b4b transparent}.cdx-msg{border:1px solid var(--cdx-border);border-radius:14px;padding:9px 10px;font-size:12px;line-height:1.4;white-space:pre-wrap;overflow-wrap:anywhere;background:#202020}.cdx-msg.user{background:#2c2c2c}.cdx-msg small{display:block;color:#aaa;font-size:9px;letter-spacing:.08em;font-weight:700;margin-bottom:4px}.cdx-typing{font-size:11px;color:#aaa;padding:3px 5px}.cdx-typing i{display:inline-block;width:7px;height:7px;border-radius:50%;background:#aaa;margin-right:7px;animation:cdxdot 1s infinite alternate}@keyframes cdxdot{to{opacity:.25}}.cdx-tools{display:flex;flex-direction:column;gap:6px;border-top:1px solid var(--cdx-border);padding-top:8px}.cdx-media{display:grid;grid-template-columns:minmax(0,1fr) 38px;gap:5px}.cdx-media select{min-height:32px;font-size:10px;padding-left:8px}.cdx-small{min-height:34px;font-size:11px;display:grid;place-items:center}.cdx-frames{font-size:10px}.cdx-attachments{display:flex;gap:4px;overflow-x:auto}.cdx-attachments button{font-size:10px;padding:4px 7px;white-space:nowrap}.cdx-root textarea{resize:vertical;min-height:58px;max-height:130px;border:1px solid var(--cdx-border);background:#202020;border-radius:12px;padding:9px;font-size:13px;line-height:1.4;outline:none}.cdx-root textarea:focus{border-color:#666}.cdx-compose{display:flex;align-items:center;gap:5px;min-height:36px}.cdx-voice,.cdx-send,.cdx-stop{height:34px;padding:0 10px;font-size:11px;display:flex;align-items:center;gap:6px}.cdx-voice.active{background:#573334}.cdx-hint{font-size:9px;color:#858585;flex:1}.cdx-send{background:#eee!important;color:#161616!important;font-weight:650;border-color:transparent!important}.cdx-send:disabled{opacity:.4}.cdx-stop{font-size:10px;color:#ffaaaa!important}.cdx-error{display:flex;gap:7px;align-items:center;padding:7px 8px;border-radius:8px;background:#572f32;color:#ffdede;font-size:11px;line-height:1.35}.cdx-error span{flex:1}.cdx-error button{width:25px;height:25px}.cdx-loading{display:grid;min-height:200px;place-items:center;align-content:center;gap:12px;color:#aaa;font-size:13px}.cdx-orb{width:26px;height:26px;border:2px solid #777;border-top-color:white;border-radius:50%;animation:cdxspin .9s linear infinite}@keyframes cdxspin{to{transform:rotate(360deg)}}\n.cdx-icon img{width:24px;height:24px;object-fit:contain;border-radius:6px}\n.cdx-account-active{color:#fff!important;background:#343434!important}.cdx-account{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:9px 10px;border:1px solid var(--cdx-border);border-radius:12px;background:#202020}.cdx-account-info{display:flex;align-items:center;gap:8px;min-width:0;color:#bbb;font-size:17px}.cdx-account-info div{display:flex;flex-direction:column;gap:3px;min-width:0}.cdx-account-info strong{font-size:11px;color:#eee;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.cdx-account-info small{font-size:9px;color:#929292}.cdx-account-actions{display:flex;gap:5px;flex:none}.cdx-account-actions button{display:flex;align-items:center;gap:5px;padding:0 8px;min-height:30px;font-size:10px}.cdx-account-actions .cdx-account-logout{color:#e8aaaa}\n.cdx-remote{display:flex;flex-direction:column;gap:5px;padding:8px 9px;border:1px solid var(--cdx-border);border-radius:11px;background:#202020}.cdx-remote>label{font-size:10px;font-weight:650;color:#ddd}.cdx-remote>div{display:flex;gap:5px}.cdx-remote input{min-width:0;flex:1;height:33px;padding:0 8px;border:1px solid var(--cdx-border);border-radius:8px;background:#171717;color:inherit;font:inherit;font-size:10px}.cdx-remote button{padding:0 9px;font-size:10px}.cdx-remote small{font-size:9px;color:#999;line-height:1.35}\n.cdx-devices{display:flex;flex-direction:column;gap:5px;padding:3px 1px}.cdx-devices>span{font-size:8px;font-weight:700;letter-spacing:.12em;color:#8e8e8e;padding-left:3px}.cdx-device-list{display:flex;gap:5px;overflow-x:auto;scrollbar-width:none}.cdx-device-list::-webkit-scrollbar{display:none}.cdx-device-list button{display:flex;align-items:center;justify-content:center;gap:6px;min-height:31px;padding:0 10px;white-space:nowrap;font-size:10px;color:#c9c9c9;background:#1f1f1f;border-color:#393939}.cdx-device-list button.selected{background:#393939;color:#fff;border-color:#626262}.cdx-device-list .cdx-device-add{width:32px;flex:none;padding:0;color:#aaa}.cdx-device-entry{display:flex;gap:5px}.cdx-device-entry input{min-width:0;flex:1;height:31px;padding:0 8px;border:1px solid var(--cdx-border);border-radius:8px;background:#171717;color:inherit;font:inherit;font-size:10px}.cdx-device-entry button{padding:0 9px;font-size:10px}\n.cdx-model-settings summary{display:flex;align-items:center;gap:7px;min-height:34px;padding:0 10px;border:1px solid var(--cdx-border);border-radius:9px;background:#222;color:#ddd;font-size:11px;list-style:none;cursor:pointer;white-space:nowrap;overflow:hidden}\n.cdx-model-settings summary::-webkit-details-marker{display:none}\n.cdx-model-settings summary:after{content:\"⌄\";margin-left:auto;color:#999}\n.cdx-model-settings summary span{overflow:hidden;text-overflow:ellipsis}\n.cdx-model-settings summary span:first-child{flex:1;text-align:left}\n.cdx-model-settings summary span+span{color:#aaa;font-size:10px}\n.cdx-model-settings[open] summary{border-color:#666;border-radius:9px 9px 0 0}\n.cdx-model-settings-menu{display:flex;flex-direction:column;gap:6px;padding:8px;border:1px solid var(--cdx-border);border-top:0;border-radius:0 0 9px 9px;background:#1c1c1c}\n.cdx-model-settings-menu label{display:flex;flex-direction:column;gap:3px;min-width:0;color:#999;font-size:9px}\n.cdx-model-settings-menu .cdx-controls label{flex:1}\n.cdx-model-settings-menu select{min-height:32px;font-size:11px}\n";

const snapshot = callable("get_snapshot");
const refresh = callable("refresh");
const selectThread = callable("select_thread");
const newThread = callable("new_thread");
const saveSettings = callable("save_settings");
const sendMessage = callable("send_message");
const retry = callable("retry");
const stop = callable("stop");
const gameVoice = callable("voice");
const videoFrames = callable("video_frames");
const openDesktop = callable("open_desktop");
const accountLogin = callable("account_login");
const accountCancelLogin = callable("account_cancel_login");
const accountLogout = callable("account_logout");
const remoteHost = callable("remote_host");
const setProvider = callable("set_provider");
const setProviderKey = callable("set_provider_key");
function Panel() {
    const [data, setData] = SP_REACT.useState(null);
    const [accountOpen, setAccountOpen] = SP_REACT.useState(false);
    const [accountBusy, setAccountBusy] = SP_REACT.useState(false);
    const [hostInput, setHostInput] = SP_REACT.useState("");
    const [hostBusy, setHostBusy] = SP_REACT.useState(false);
    const [hostEntryOpen, setHostEntryOpen] = SP_REACT.useState(false);
    const [draft, setDraft] = SP_REACT.useState(() => localStorage.getItem("codex-game-draft:new") || "");
    const [busy, setBusy] = SP_REACT.useState(false);
    const [error, setError] = SP_REACT.useState("");
    const [lang, setLang] = SP_REACT.useState(() => localStorage.getItem("codex-game-voice") || "en");
    const [images, setImages] = SP_REACT.useState([]);
    const [shot, setShot] = SP_REACT.useState("");
    const [video, setVideo] = SP_REACT.useState("");
    const [providerKey, setProviderKeyInput] = SP_REACT.useState("");
    const [providerBusy, setProviderBusy] = SP_REACT.useState(false);
    const lastVoice = SP_REACT.useRef("");
    const lastVoiceError = SP_REACT.useRef("");
    const endRef = SP_REACT.useRef(null);
    const load = SP_REACT.useCallback(async () => { try {
        const d = await snapshot();
        setData(d);
        if (d.voiceState === "done" && d.voiceText && d.voiceText !== lastVoice.current) {
            lastVoice.current = d.voiceText;
            setDraft(x => (x ? x.trimEnd() + " " : "") + d.voiceText.trim() + " ");
            if (d.voiceError && d.voiceError !== lastVoiceError.current) {
                lastVoiceError.current = d.voiceError;
                setError(d.voiceError);
            }
        }
        else if (d.voiceError && d.voiceError !== lastVoiceError.current) {
            lastVoiceError.current = d.voiceError;
            setError(d.voiceError);
        }
    }
    catch (e) {
        setError(String(e));
    } }, []);
    SP_REACT.useEffect(() => { const style = document.createElement("style"); style.textContent = css; document.head.appendChild(style); return () => style.remove(); }, []);
    SP_REACT.useEffect(() => { let alive = true; const run = async () => { try {
        const d = await snapshot();
        if (alive) {
            setData(d);
            if (d.voiceState === "done" && d.voiceText && d.voiceText !== lastVoice.current) {
                lastVoice.current = d.voiceText;
                setDraft(x => (x ? x.trimEnd() + " " : "") + d.voiceText.trim() + " ");
                if (d.voiceError && d.voiceError !== lastVoiceError.current) {
                    lastVoiceError.current = d.voiceError;
                    setError(d.voiceError);
                }
            }
            else if (d.voiceError && d.voiceError !== lastVoiceError.current) {
                lastVoiceError.current = d.voiceError;
                setError(d.voiceError);
            }
        }
    }
    catch (e) {
        if (alive)
            setError(String(e));
    } }; void run(); const timer = setInterval(run, 3000); return () => { alive = false; clearInterval(timer); }; }, []);
    SP_REACT.useEffect(() => { const key = "codex-game-draft:" + (data?.threadId || "new"); setDraft(localStorage.getItem(key) || ""); }, [data?.threadId]);
    SP_REACT.useEffect(() => { setHostInput(data?.remoteHost || ""); }, [data?.remoteHost]);
    SP_REACT.useEffect(() => { localStorage.setItem("codex-game-draft:" + (data?.threadId || "new"), draft); }, [draft, data?.threadId]);
    SP_REACT.useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" }); }, [data?.messages.length]);
    const model = data?.models.find(x => x.id === data.model) || data?.models[0];
    const effort = data?.effort || model?.defaultEffort || model?.efforts[0]?.id || "low";
    const tier = data?.tier || "default";
    const setModel = (id) => { if (!data)
        return; const next = data.models.find(x => x.id === id); const depth = next?.defaultEffort || next?.efforts[0]?.id || "low"; setData({ ...data, model: id, effort: depth, tier: "default" }); void saveSettings(id, depth, "default"); };
    const setEffort = (value) => { setData(old => old ? { ...old, effort: value } : old); if (data?.model)
        void saveSettings(data.model, value, tier); };
    const setTier = (value) => { setData(old => old ? { ...old, tier: value } : old); if (data?.model)
        void saveSettings(data.model, effort, value); };
    const attachShot = () => { const value = shot || data?.screenshots[0]?.path; if (!value)
        return; const media = data?.screenshots.find(x => x.path === value); setImages(old => old.some(x => x.path === value) ? old : [...old, { path: value, name: media?.name || "Steam screenshot" }]); };
    const attachFrames = async () => { if (!video)
        return; setBusy(true); setError(""); try {
        const result = await videoFrames(video);
        setImages(old => [...old, ...result.frames]);
        setError(result.frames.length + " game frame(s) attached");
    }
    catch (e) {
        setError(String(e));
    }
    finally {
        setBusy(false);
    } };
    const submit = async () => { if (busy || !data)
        return; if (!draft.trim() && !images.length)
        return; setBusy(true); setError(""); try {
        await sendMessage(draft, images.map(x => x.path), data.model, effort, tier);
        setDraft("");
        localStorage.removeItem("codex-game-draft:" + (data.threadId || "new"));
        setImages([]);
        setTimeout(() => void load(), 400);
    }
    catch (e) {
        setError(String(e));
    }
    finally {
        setBusy(false);
    } };
    const startVoice = async () => { if (!data)
        return; try {
        await gameVoice(lang);
        if (data.voiceState !== "recording" && data.voiceState !== "stopping")
            setError("Listening… press Stop to finish dictation.");
        else
            setError("Stopping recording…");
    }
    catch (e) {
        setError(String(e));
    } };
    const cycleVoice = () => { const next = lang === "ru" ? "en" : "ru"; localStorage.setItem("codex-game-voice", next); setLang(next); setError("Recognition language: " + next.toUpperCase()); };
    const signIn = async () => { setAccountBusy(true); setError(""); try {
        const result = await accountLogin();
        if (result.opened)
            setError("Opened Codex account sign-in page.");
        else
            setError("Open this sign-in link: " + result.url);
    }
    catch (e) {
        setError(String(e));
    }
    finally {
        setAccountBusy(false);
    } };
    const signOut = async () => { setAccountBusy(true); setError(""); try {
        await accountLogout();
        setData(await refresh());
        setError("Signed out of Codex.");
    }
    catch (e) {
        setError(String(e));
    }
    finally {
        setAccountBusy(false);
    } };
    const cancelSignIn = async () => { setAccountBusy(true); try {
        await accountCancelLogin();
        setData(await refresh());
        setError("Sign-in cancelled.");
    }
    catch (e) {
        setError(String(e));
    }
    finally {
        setAccountBusy(false);
    } };
    const connectHost = async (host = hostInput.trim()) => { setHostBusy(true); setError(""); try {
        setData(await remoteHost(host));
        setHostEntryOpen(false);
        setError(host ? "Connected to remote Codex over SSH." : "Using Codex on Steam Deck.");
    }
    catch (e) {
        setError(String(e));
    }
    finally {
        setHostBusy(false);
    } };
    const changeProvider = async (value) => { setHostBusy(true); setError(""); try {
        setData(await setProvider(value));
        setError(value === "claude" ? "Claude uses the Claude Code login on this Steam Deck." : value === "deepseek" ? "DeepSeek requests are sent to OpenRouter and may be billed to your OpenRouter account." : "Using your signed-in Codex account.");
    }
    catch (e) {
        setError(String(e));
    }
    finally {
        setHostBusy(false);
    } };
    const saveProviderKey = async () => { if (!providerKey.trim())
        return; setProviderBusy(true); setError(""); try {
        await setProviderKey(providerKey.trim());
        setProviderKeyInput("");
        setData(await refresh());
        setError("OpenRouter key saved in the system secret store.");
    }
    catch (e) {
        setError(String(e));
    }
    finally {
        setProviderBusy(false);
    } };
    if (!data && !error)
        return SP_JSX.jsxs("div", { className: "cdx-loading", children: [SP_JSX.jsx("span", { className: "cdx-orb" }), "Connecting to Codex\u2026"] });
    return SP_JSX.jsxs("div", { className: "cdx-root", children: [SP_JSX.jsxs("header", { className: "cdx-header", children: [SP_JSX.jsx("span", { className: "cdx-icon", children: SP_JSX.jsx("img", { src: logo, alt: "Deck AI" }) }), SP_JSX.jsxs("div", { className: "cdx-brand", children: ["Deck AI", SP_JSX.jsx("span", { children: "GAME MODE" })] }), SP_JSX.jsx("span", { className: "cdx-state " + (data?.active ? "cdx-working" : ""), children: data?.active ? "Working" : data?.status || "Not connected" }), SP_JSX.jsx("button", { className: "cdx-iconbutton " + (accountOpen ? "cdx-account-active" : ""), title: "Codex account", "aria-label": "Codex account", onClick: () => setAccountOpen(x => !x), children: SP_JSX.jsx(FaUserCircle, {}) }), SP_JSX.jsx("button", { className: "cdx-iconbutton", title: "Open desktop app", onClick: () => void openDesktop(), children: SP_JSX.jsx(FaDesktop, {}) }), SP_JSX.jsx("button", { className: "cdx-iconbutton", title: "Refresh", onClick: () => void refresh().then(setData), "aria-label": "Refresh", children: "\u21BB" })] }), accountOpen && SP_JSX.jsxs("section", { className: "cdx-account", children: [SP_JSX.jsxs("div", { className: "cdx-account-info", children: [SP_JSX.jsx(FaUserCircle, {}), SP_JSX.jsxs("div", { children: [SP_JSX.jsx("strong", { children: data?.account?.email || "No account connected" }), SP_JSX.jsx("small", { children: data?.account?.planType ? "Plan · " + data.account.planType : data?.loginPending ? "Waiting for sign-in in browser" : "Signed in with ChatGPT" })] })] }), SP_JSX.jsxs("div", { className: "cdx-account-actions", children: [data?.loginPending ? SP_JSX.jsx("button", { disabled: accountBusy, onClick: () => void cancelSignIn(), children: "Cancel sign-in" }) : SP_JSX.jsxs("button", { disabled: accountBusy, onClick: () => void signIn(), children: [SP_JSX.jsx(FaExternalLinkAlt, {}), data?.account ? "Switch account" : "Sign in"] }), data?.account && SP_JSX.jsxs("button", { className: "cdx-account-logout", disabled: accountBusy, onClick: () => void signOut(), children: [SP_JSX.jsx(FaSignOutAlt, {}), "Sign out"] })] })] }), data?.provider === "codex" && SP_JSX.jsxs("section", { className: "cdx-devices", "aria-label": "Codex devices", children: [SP_JSX.jsx("span", { children: "DEVICES" }), SP_JSX.jsxs("div", { className: "cdx-device-list", children: [SP_JSX.jsxs("button", { className: !data?.remoteHost ? "selected" : "", disabled: hostBusy, onClick: () => void connectHost(""), children: [SP_JSX.jsx(FaDesktop, {}), "Steam Deck"] }), (data?.sshHosts || []).map(host => SP_JSX.jsxs("button", { className: data?.remoteHost === host ? "selected" : "", disabled: hostBusy, onClick: () => void connectHost(host), children: [SP_JSX.jsx(FaLaptop, {}), host] }, host)), SP_JSX.jsx("button", { className: "cdx-device-add", title: "Add SSH host", onClick: () => setHostEntryOpen(x => !x), children: SP_JSX.jsx(FaPlus, {}) })] }), hostEntryOpen && SP_JSX.jsxs("div", { className: "cdx-device-entry", children: [SP_JSX.jsx("input", { "aria-label": "Codex SSH alias", placeholder: "SSH alias, e.g. Mac", value: hostInput, onChange: e => setHostInput(e.target.value), onKeyDown: e => { if (e.key === "Enter")
                                    void connectHost(); } }), SP_JSX.jsx("button", { disabled: hostBusy || !hostInput.trim(), onClick: () => void connectHost(), children: hostBusy ? "…" : "Connect" })] })] }), error && SP_JSX.jsxs("div", { className: "cdx-error", children: [SP_JSX.jsx("span", { children: error }), SP_JSX.jsx("button", { onClick: () => setError(""), children: "\u00D7" })] }), SP_JSX.jsxs("div", { className: "cdx-selects", children: [SP_JSX.jsxs("label", { className: "cdx-provider-label", children: ["Model provider", SP_JSX.jsxs("select", { "aria-label": "Model provider", value: data?.provider || "codex", onChange: e => void changeProvider(e.target.value), children: [SP_JSX.jsx("option", { value: "codex", children: "Codex \u00B7 ChatGPT plan" }), SP_JSX.jsx("option", { value: "claude", children: "Claude \u00B7 Pro / Max via Claude Code" }), SP_JSX.jsx("option", { value: "deepseek", children: "DeepSeek \u00B7 OpenRouter" })] })] }), data?.provider === "deepseek" && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsxs("div", { className: "cdx-key-entry", children: [SP_JSX.jsx("input", { type: "password", autoComplete: "off", spellCheck: false, "aria-label": "OpenRouter API key", placeholder: "OpenRouter API key", value: providerKey, onChange: e => setProviderKeyInput(e.target.value), onKeyDown: e => { if (e.key === "Enter")
                                            void saveProviderKey(); } }), SP_JSX.jsx("button", { disabled: providerBusy || !providerKey.trim(), onClick: () => void saveProviderKey(), children: providerBusy ? "…" : "Save key" })] }), SP_JSX.jsx("small", { className: "cdx-key-note", children: "Saved to the SteamOS system secret store. OpenRouter charges are separate from Codex." })] }), data?.provider === "claude" && SP_JSX.jsx("button", { className: "cdx-claude-login", onClick: () => void openDesktop(), children: "Open desktop app to install or sign in to Claude Code" }), SP_JSX.jsxs("div", { className: "cdx-chatrow", children: [SP_JSX.jsxs("select", { "aria-label": "Chat", value: data?.threadId || "", onChange: e => e.target.value ? void selectThread(e.target.value).then(setData) : void newThread().then(setData), children: [SP_JSX.jsx("option", { value: "", children: "\uFF0B New chat" }), data?.threads.map(x => SP_JSX.jsx("option", { value: x.id, children: x.name.slice(0, 52) }, x.id))] }), SP_JSX.jsx("button", { className: "cdx-small", onClick: () => void newThread().then(setData), children: "\uFF0B" })] }), SP_JSX.jsxs("details", { className: "cdx-model-settings", children: [SP_JSX.jsxs("summary", { title: "Choose model, reasoning effort, and speed", children: [SP_JSX.jsx("span", { children: model?.name || "Model" }), data?.provider === "codex" && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx("span", { children: effort }), SP_JSX.jsx("span", { children: tier === "priority" ? "Fast" : "Standard" })] })] }), SP_JSX.jsxs("div", { className: "cdx-model-settings-menu", children: [SP_JSX.jsxs("label", { children: ["Model", SP_JSX.jsx("select", { "aria-label": "Model", value: model?.id || "", onChange: e => setModel(e.target.value), children: data?.models.map(x => SP_JSX.jsx("option", { value: x.id, children: x.name }, x.id)) })] }), data?.provider === "codex" && SP_JSX.jsxs("div", { className: "cdx-controls", children: [SP_JSX.jsxs("label", { children: ["Reasoning", SP_JSX.jsx("select", { "aria-label": "Reasoning", value: effort, onChange: e => setEffort(e.target.value), children: model?.efforts.map(x => SP_JSX.jsx("option", { value: x.id, children: x.name }, x.id)) })] }), SP_JSX.jsxs("label", { children: ["Speed", SP_JSX.jsxs("select", { "aria-label": "Speed", value: tier, onChange: e => setTier(e.target.value), children: [SP_JSX.jsx("option", { value: "default", children: "Standard" }), model?.tiers.includes("priority") && SP_JSX.jsx("option", { value: "priority", children: "Fast \u00B7 quicker" })] })] })] })] })] })] }), SP_JSX.jsxs("div", { className: "cdx-chat", children: [data?.outbox.filter(j => j.status === "error").map(j => SP_JSX.jsxs("div", { className: "cdx-error", children: [SP_JSX.jsx("span", { children: j.error || "Send failed" }), SP_JSX.jsx("button", { onClick: () => void retry(j.id).then(load), children: "Retry" })] }, j.id)), data?.messages.map((m, i) => SP_JSX.jsxs("article", { className: "cdx-msg " + m.role, children: [SP_JSX.jsx("small", { children: m.role === "user" ? "YOU" : (data?.provider || "codex").toUpperCase() }), SP_JSX.jsx("div", { children: m.text.length > 4200 ? m.text.slice(-4200) : m.text })] }, m.id || i)), data?.active && SP_JSX.jsxs("div", { className: "cdx-typing", children: [SP_JSX.jsx("i", {}), data.provider === "claude" ? "Claude is working…" : data.provider === "deepseek" ? "DeepSeek is working…" : "Codex is working…"] }), SP_JSX.jsx("div", { ref: endRef })] }), SP_JSX.jsxs("section", { className: "cdx-tools", children: [SP_JSX.jsxs("div", { className: "cdx-media", children: [SP_JSX.jsxs("select", { "aria-label": "Steam screenshot", value: shot, onChange: e => setShot(e.target.value), children: [SP_JSX.jsx("option", { value: "", children: "Latest game screenshot\u2026" }), data?.screenshots.map(x => SP_JSX.jsxs("option", { value: x.path, children: [x.when ? new Date(x.when * 1000).toLocaleString() : "Steam", " \u00B7 ", x.name] }, x.path))] }), SP_JSX.jsx("button", { className: "cdx-small cdx-camera", title: "Attach selected screenshot", onClick: attachShot, children: SP_JSX.jsx(FaCamera, {}) }), SP_JSX.jsxs("select", { "aria-label": "Steam video", value: video, onChange: e => setVideo(e.target.value), children: [SP_JSX.jsx("option", { value: "", children: "Choose game recording\u2026" }), data?.videos.map(x => SP_JSX.jsx("option", { value: x.path, children: x.name }, x.path))] }), SP_JSX.jsx("button", { className: "cdx-small cdx-frames", title: "Attach video frames", disabled: !video || busy, onClick: () => void attachFrames(), children: "Frames" })] }), images.length > 0 && SP_JSX.jsx("div", { className: "cdx-attachments", children: images.map((x, i) => SP_JSX.jsxs("button", { onClick: () => setImages(old => old.filter((_, n) => n !== i)), children: ["\u25A7 ", x.name, " \u00D7"] }, x.path)) }), SP_JSX.jsx("textarea", { "aria-label": "Message Codex", placeholder: "Ask about the game or attach a screenshot\u2026", value: draft, onChange: e => setDraft(e.target.value), onKeyDown: e => { if (e.key === "Enter" && !e.shiftKey) {
                            e.preventDefault();
                            void submit();
                        } } }), SP_JSX.jsxs("div", { className: "cdx-compose", children: [SP_JSX.jsxs("button", { className: "cdx-voice " + (data?.voiceState === "recording" ? "active" : ""), onClick: () => void startVoice(), children: [SP_JSX.jsx(FaMicrophone, {}), data?.voiceState === "recording" || data?.voiceState === "stopping" ? "Stop" : "Voice"] }), SP_JSX.jsx("button", { className: "cdx-small", onClick: cycleVoice, title: "Switch dictation language", children: lang.toUpperCase() }), SP_JSX.jsx("span", { className: "cdx-hint", children: data?.voiceState === "recording" ? "Recording · press Stop" : "↵ send · Steam+B opens keyboard" }), data?.active && data?.provider === "codex" && SP_JSX.jsx("button", { className: "cdx-stop", onClick: () => void stop(), children: "Stop response" }), SP_JSX.jsx("button", { className: "cdx-send", disabled: busy || (!draft.trim() && !images.length), onClick: () => void submit(), children: busy ? "…" : "Send" })] })] })] });
}
var index = definePlugin(() => ({ name: "Deck AI", titleView: SP_JSX.jsxs("div", { className: "cdx-title", children: ["Deck AI ", SP_JSX.jsx("span", { children: "GAME MODE" })] }), content: SP_JSX.jsx(Panel, {}), icon: SP_JSX.jsx("img", { src: logo, alt: "Deck AI" }) }));

export { index as default };
