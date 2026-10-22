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
const routerHook = api.routerHook;
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
function FaMicrophone (props) {
  return GenIcon({"attr":{"viewBox":"0 0 352 512"},"child":[{"tag":"path","attr":{"d":"M176 352c53.02 0 96-42.98 96-96V96c0-53.02-42.98-96-96-96S80 42.98 80 96v160c0 53.02 42.98 96 96 96zm160-160h-16c-8.84 0-16 7.16-16 16v48c0 74.8-64.49 134.82-140.79 127.38C96.71 376.89 48 317.11 48 250.3V208c0-8.84-7.16-16-16-16H16c-8.84 0-16 7.16-16 16v40.16c0 89.64 63.97 169.55 152 181.69V464H96c-8.84 0-16 7.16-16 16v16c0 8.84 7.16 16 16 16h160c8.84 0 16-7.16 16-16v-16c0-8.84-7.16-16-16-16h-56v-33.77C285.71 418.47 352 344.9 352 256v-48c0-8.84-7.16-16-16-16z"},"child":[]}]})(props);
}function FaHistory (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M504 255.531c.253 136.64-111.18 248.372-247.82 248.468-59.015.042-113.223-20.53-155.822-54.911-11.077-8.94-11.905-25.541-1.839-35.607l11.267-11.267c8.609-8.609 22.353-9.551 31.891-1.984C173.062 425.135 212.781 440 256 440c101.705 0 184-82.311 184-184 0-101.705-82.311-184-184-184-48.814 0-93.149 18.969-126.068 49.932l50.754 50.754c10.08 10.08 2.941 27.314-11.313 27.314H24c-8.837 0-16-7.163-16-16V38.627c0-14.254 17.234-21.393 27.314-11.314l49.372 49.372C129.209 34.136 189.552 8 256 8c136.81 0 247.747 110.78 248 247.531zm-180.912 78.784l9.823-12.63c8.138-10.463 6.253-25.542-4.21-33.679L288 256.349V152c0-13.255-10.745-24-24-24h-16c-13.255 0-24 10.745-24 24v135.651l65.409 50.874c10.463 8.137 25.541 6.253 33.679-4.21z"},"child":[]}]})(props);
}function FaGamepad (props) {
  return GenIcon({"attr":{"viewBox":"0 0 640 512"},"child":[{"tag":"path","attr":{"d":"M480.07 96H160a160 160 0 1 0 114.24 272h91.52A160 160 0 1 0 480.07 96zM248 268a12 12 0 0 1-12 12h-52v52a12 12 0 0 1-12 12h-24a12 12 0 0 1-12-12v-52H84a12 12 0 0 1-12-12v-24a12 12 0 0 1 12-12h52v-52a12 12 0 0 1 12-12h24a12 12 0 0 1 12 12v52h52a12 12 0 0 1 12 12zm216 76a40 40 0 1 1 40-40 40 40 0 0 1-40 40zm64-96a40 40 0 1 1 40-40 40 40 0 0 1-40 40z"},"child":[]}]})(props);
}function FaExpand (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M0 180V56c0-13.3 10.7-24 24-24h124c6.6 0 12 5.4 12 12v40c0 6.6-5.4 12-12 12H64v84c0 6.6-5.4 12-12 12H12c-6.6 0-12-5.4-12-12zM288 44v40c0 6.6 5.4 12 12 12h84v84c0 6.6 5.4 12 12 12h40c6.6 0 12-5.4 12-12V56c0-13.3-10.7-24-24-24H300c-6.6 0-12 5.4-12 12zm148 276h-40c-6.6 0-12 5.4-12 12v84h-84c-6.6 0-12 5.4-12 12v40c0 6.6 5.4 12 12 12h124c13.3 0 24-10.7 24-24V332c0-6.6-5.4-12-12-12zM160 468v-40c0-6.6-5.4-12-12-12H64v-84c0-6.6-5.4-12-12-12H12c-6.6 0-12 5.4-12 12v124c0 13.3 10.7 24 24 24h124c6.6 0 12-5.4 12-12z"},"child":[]}]})(props);
}function FaCopy (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M320 448v40c0 13.255-10.745 24-24 24H24c-13.255 0-24-10.745-24-24V120c0-13.255 10.745-24 24-24h72v296c0 30.879 25.121 56 56 56h168zm0-344V0H152c-13.255 0-24 10.745-24 24v368c0 13.255 10.745 24 24 24h272c13.255 0 24-10.745 24-24V128H344c-13.2 0-24-10.8-24-24zm120.971-31.029L375.029 7.029A24 24 0 0 0 358.059 0H352v96h96v-6.059a24 24 0 0 0-7.029-16.97z"},"child":[]}]})(props);
}function FaCompress (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M436 192H312c-13.3 0-24-10.7-24-24V44c0-6.6 5.4-12 12-12h40c6.6 0 12 5.4 12 12v84h84c6.6 0 12 5.4 12 12v40c0 6.6-5.4 12-12 12zm-276-24V44c0-6.6-5.4-12-12-12h-40c-6.6 0-12 5.4-12 12v84H12c-6.6 0-12 5.4-12 12v40c0 6.6 5.4 12 12 12h124c13.3 0 24-10.7 24-24zm0 300V344c0-13.3-10.7-24-24-24H12c-6.6 0-12 5.4-12 12v40c0 6.6 5.4 12 12 12h84v84c0 6.6 5.4 12 12 12h40c6.6 0 12-5.4 12-12zm192 0v-84h84c6.6 0 12-5.4 12-12v-40c0-6.6-5.4-12-12-12H312c-13.3 0-24 10.7-24 24v124c0 6.6 5.4 12 12 12h40c6.6 0 12-5.4 12-12z"},"child":[]}]})(props);
}function FaComment (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M256 32C114.6 32 0 125.1 0 240c0 49.6 21.4 95 57 130.7C44.5 421.1 2.7 466 2.2 466.5c-2.2 2.3-2.8 5.7-1.5 8.7S4.8 480 8 480c66.3 0 116-31.8 140.6-51.4 32.7 12.3 69 19.4 107.4 19.4 141.4 0 256-93.1 256-208S397.4 32 256 32z"},"child":[]}]})(props);
}function FaCog (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M487.4 315.7l-42.6-24.6c4.3-23.2 4.3-47 0-70.2l42.6-24.6c4.9-2.8 7.1-8.6 5.5-14-11.1-35.6-30-67.8-54.7-94.6-3.8-4.1-10-5.1-14.8-2.3L380.8 110c-17.9-15.4-38.5-27.3-60.8-35.1V25.8c0-5.6-3.9-10.5-9.4-11.7-36.7-8.2-74.3-7.8-109.2 0-5.5 1.2-9.4 6.1-9.4 11.7V75c-22.2 7.9-42.8 19.8-60.8 35.1L88.7 85.5c-4.9-2.8-11-1.9-14.8 2.3-24.7 26.7-43.6 58.9-54.7 94.6-1.7 5.4.6 11.2 5.5 14L67.3 221c-4.3 23.2-4.3 47 0 70.2l-42.6 24.6c-4.9 2.8-7.1 8.6-5.5 14 11.1 35.6 30 67.8 54.7 94.6 3.8 4.1 10 5.1 14.8 2.3l42.6-24.6c17.9 15.4 38.5 27.3 60.8 35.1v49.2c0 5.6 3.9 10.5 9.4 11.7 36.7 8.2 74.3 7.8 109.2 0 5.5-1.2 9.4-6.1 9.4-11.7v-49.2c22.2-7.9 42.8-19.8 60.8-35.1l42.6 24.6c4.9 2.8 11 1.9 14.8-2.3 24.7-26.7 43.6-58.9 54.7-94.6 1.5-5.5-.7-11.3-5.6-14.1zM256 336c-44.1 0-80-35.9-80-80s35.9-80 80-80 80 35.9 80 80-35.9 80-80 80z"},"child":[]}]})(props);
}function FaArrowLeft (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M257.5 445.1l-22.2 22.2c-9.4 9.4-24.6 9.4-33.9 0L7 273c-9.4-9.4-9.4-24.6 0-33.9L201.4 44.7c9.4-9.4 24.6-9.4 33.9 0l22.2 22.2c9.5 9.5 9.3 25-.4 34.3L136.6 216H424c13.3 0 24 10.7 24 24v32c0 13.3-10.7 24-24 24H136.6l120.5 114.8c9.8 9.3 10 24.8.4 34.3z"},"child":[]}]})(props);
}

var logo = 'http://127.0.0.1:1337/plugins/Deck AI/assets/deck-ai-2f73c1d3.png';

var css = "/* The Quick Access panel is about 300px wide. Keep all rules local to Deck AI. */\n.dai-root{--dai-line:rgba(255,255,255,.12);--dai-muted:#aab6c3;display:flex;flex-direction:column;gap:8px;box-sizing:border-box;width:100%;max-width:100%;height:clamp(300px,calc(100vh - 180px),580px);min-height:0;padding:0 12px 10px;color:#f0f4f8;font-size:14px;line-height:1.4;overflow:hidden}\n.dai-root *{box-sizing:border-box}.dai-root h3{font-size:14px;font-weight:650;margin:0 0 9px}.dai-root p{margin:0}.dai-tabs{display:flex;gap:4px;flex-shrink:0;border-bottom:1px solid var(--dai-line);padding-bottom:7px}.dai-tab{flex:1;min-width:0}.dai-root .dai-button{display:flex;align-items:center;justify-content:center;gap:6px;width:100%;min-width:0;min-height:38px;height:auto;padding:8px 9px;border-radius:3px;font-size:13px;line-height:1.3;white-space:normal;overflow-wrap:anywhere;box-shadow:none}.dai-tab .dai-button{background:transparent;color:var(--dai-muted);padding:9px 4px;font-size:12px;gap:5px}.dai-tab.selected .dai-button{background:#34495d;color:white}.dai-root .dai-button:focus,.dai-root .dai-button.gpfocus,.dai-root .dai-focused{outline:2px solid #fff;outline-offset:-2px;background:#dce8f1;color:#152638}.dai-root .dai-primary{background:#1a77b9;color:white}.dai-root .dai-button:disabled{opacity:.4}.dai-status{display:flex;align-items:center;gap:6px;min-height:18px;font-size:11px;color:var(--dai-muted);flex-shrink:0}.dai-status>span:nth-child(2){overflow:hidden;white-space:nowrap;text-overflow:ellipsis;flex:1;min-width:0}.dai-status small{max-width:75px;overflow:hidden;text-overflow:ellipsis}.dai-dot{height:6px;width:6px;border-radius:50%;background:#69c49a;flex-shrink:0}.dai-dot.offline{background:#e59980}.dai-dot.working{background:#e4c56e}.dai-page{display:flex;flex-direction:column;flex:1;min-height:0;overflow:hidden}.dai-scroll{flex:1;min-height:0;overflow-y:auto;overflow-x:hidden;padding:2px 2px 10px;scrollbar-width:thin}.dai-stack{display:flex;flex-direction:column;gap:10px}.dai-section{display:flex;flex-direction:column;gap:10px;padding:4px 0 14px;border-bottom:1px solid var(--dai-line);flex-shrink:0}.dai-section:last-child{border:0}.dai-section h3{color:#fff;margin:0}.dai-field{display:flex;flex-direction:column;gap:5px;min-width:0}.dai-label{font-size:12px;color:var(--dai-muted)}.dai-field>div{min-width:0;max-width:100%}.dai-muted{font-size:12px;color:var(--dai-muted);line-height:1.45}.dai-account{overflow-wrap:anywhere}.dai-login-url{overflow-wrap:anywhere;font-size:11px;user-select:text}.dai-messages{flex:1;min-height:65px;overflow-y:auto;overflow-x:hidden;scrollbar-width:thin;display:flex;flex-direction:column;gap:9px;padding:3px 2px 10px}.dai-message{flex-shrink:0;padding:10px;border-radius:4px;background:rgba(255,255,255,.045);overflow-wrap:anywhere;white-space:pre-wrap;font-size:14px;line-height:1.5;user-select:text}.dai-message.user{background:rgba(100,165,220,.12)}.dai-message small{display:block;font-size:10px;font-weight:650;color:var(--dai-muted);margin-bottom:4px}.dai-empty{margin:auto 0;text-align:center;padding:12px 3px;color:var(--dai-muted)}.dai-empty>svg{font-size:23px;opacity:.7;margin:0 0 8px}.dai-empty h3{color:#fff;margin-bottom:5px}.dai-empty p{font-size:13px;line-height:1.6;margin-bottom:12px}.dai-composer{display:flex;flex-direction:column;gap:8px;flex-shrink:0;border-top:1px solid var(--dai-line);padding-top:9px}.dai-compose-actions{display:flex;gap:5px}.dai-compose-actions>.dai-button{flex:1;padding:9px 4px;font-size:12px}.dai-compose-actions>.dai-button svg{flex-shrink:0}.dai-attachments{display:flex;flex-direction:column;gap:4px;max-height:80px;overflow-y:auto}.dai-attachments .dai-button{font-size:11px;min-height:30px;justify-content:flex-start}.dai-banner{display:flex;flex-direction:column;gap:5px;flex-shrink:0;padding:7px;background:#502f36;border-radius:3px;font-size:12px}.dai-banner>span{max-height:65px;overflow-y:auto;overflow-wrap:anywhere}.dai-banner .dai-button{min-height:26px;padding:4px;font-size:11px}.dai-notice{font-size:11px;color:#a9cddb;flex-shrink:0;max-height:40px;overflow-y:auto}.dai-history-item .dai-button{flex-direction:column;align-items:flex-start;text-align:left;padding:10px}.dai-history-item.selected{border-left:3px solid #66b5ef}.dai-history-item small{font-size:10px;color:var(--dai-muted)}.dai-failed{display:flex;flex-direction:column;gap:6px;font-size:12px;color:#ffc9b7}\n@media(max-height:600px){.dai-root{height:clamp(260px,calc(100vh - 140px),460px);gap:5px}.dai-root .dai-button{min-height:34px}.dai-composer{gap:5px;padding-top:6px}}\n\n.dai-stack-content{display:flex;flex-direction:column;gap:10px;flex-shrink:0}.dai-message-list{display:flex;flex-direction:column;gap:9px;min-height:100%;flex-shrink:0}.dai-settings-grid{flex-shrink:0}\n\n.dai-root .dai-button{box-sizing:border-box!important}\n.dai-tab:first-child{flex:.8}.dai-tab:last-child{flex:1.25}.dai-tab .dai-button{white-space:nowrap}.dai-tab .dai-button svg{flex-shrink:0}\n/* Gaming Mode's .DialogButton rules have higher specificity than desktop\n   styles. Override only this plugin's dimensions so Steam cannot impose its\n   160px minimum on each control in the 300px Quick Access column. */\n.dai-root .dai-button.DialogButton{width:100%!important;min-width:0!important;max-width:100%!important;min-height:38px!important;height:auto!important;padding:8px 6px!important;font-size:13px!important;line-height:1.3!important;border-radius:4px!important}\n.dai-root .dai-tab .dai-button.DialogButton{font-size:12px!important;padding:8px 4px!important;background:transparent!important;color:var(--dai-muted)!important}\n.dai-root .dai-tab.selected .dai-button.DialogButton{background:#34495d!important;color:#fff!important}\n.dai-root .dai-button.dai-primary{background:#1a77b9!important;color:#fff!important}\n.dai-root .dai-button.DialogButton.gpfocus,.dai-root .dai-button.DialogButton:focus{background:#dce8f1!important;color:#152638!important}\n.dai-viewbar{display:flex;align-items:center;gap:6px;flex-shrink:0;min-width:0}.dai-viewbar>.dai-status{flex:1;min-width:0}.dai-root .dai-viewbar>.dai-button.DialogButton{width:126px!important;flex-shrink:0;font-size:11px!important;min-height:32px!important;padding:6px 4px!important}\n/* Full-screen UI uses Steam's 854x534 CSS viewport on a 1280x800 Deck.\n   Reserve its top/bottom bars and keep primary controls visible together. */\n.dai-draft-field{min-width:0;width:100%}\n.dai-root.dai-fullscreen{position:fixed;inset:40px 0;width:100vw;max-width:none;height:calc(100vh - 80px);max-height:none;min-height:0;margin:0;padding:10px 16px;background:#101923;gap:6px;font-size:12px;line-height:1.35}\n.dai-full-header{display:flex;align-items:center;gap:8px;flex-shrink:0;min-width:0}\n.dai-full-brand{flex:1;min-width:0;display:flex;align-items:center;gap:12px}\n.dai-full-brand h1{font-size:18px;line-height:1.2;margin:0;white-space:nowrap}\n.dai-full-brand span{font-size:11px;color:var(--dai-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}\n.dai-root.dai-fullscreen .dai-button.DialogButton{font-size:12px!important;min-height:32px!important;padding:6px 8px!important;line-height:1.3!important}\n.dai-root.dai-fullscreen .dai-full-header>.dai-button.DialogButton{width:106px!important;flex:none}\n.dai-fullscreen>.dai-tabs{max-width:540px;padding-bottom:5px;gap:6px}\n.dai-root.dai-fullscreen .dai-tab .dai-button.DialogButton{font-size:12px!important;padding:6px!important;min-height:30px!important}\n.dai-fullscreen>.dai-viewbar{display:none}\n.dai-fullscreen .dai-page{width:100%;max-width:1200px;margin:0 auto}\n.dai-fullscreen .dai-scroll{padding:0 2px 2px}\n.dai-fullscreen .dai-message{padding:9px 12px;font-size:13px;line-height:1.45}\n.dai-fullscreen .dai-message-list{gap:7px}\n.dai-fullscreen .dai-message small{font-size:10px;margin-bottom:3px}\n.dai-fullscreen .dai-messages{padding:2px 2px 8px}\n.dai-fullscreen .dai-composer{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:6px;padding-top:7px}\n.dai-fullscreen .dai-composer>.dai-attachments,.dai-fullscreen .dai-composer>.dai-muted{grid-column:1/-1}\n.dai-fullscreen .dai-compose-actions{gap:5px;justify-content:flex-end}\n.dai-root.dai-fullscreen .dai-compose-actions>.dai-button.DialogButton{width:auto!important;flex:none;padding:6px 9px!important}\n.dai-fullscreen .dai-settings-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;align-items:start}\n.dai-settings-column{display:flex;flex-direction:column;gap:9px;min-width:0}\n.dai-fullscreen .dai-section,.dai-fullscreen .dai-section:last-child{padding:10px;border:1px solid var(--dai-line);border-radius:5px;background:rgba(255,255,255,.025);gap:7px;min-width:0}\n.dai-fullscreen .dai-section h3{font-size:14px;line-height:1.25;margin:0}\n.dai-model-fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}\n.dai-fullscreen .dai-label{font-size:11px;line-height:1.25}\n.dai-fullscreen .dai-field{gap:4px;min-width:0}\n.dai-fullscreen .dai-field>button[role=combobox]{width:100%!important;max-width:100%!important;min-width:0!important;min-height:32px!important;height:32px!important;padding:5px 8px!important;font-size:12px!important;line-height:1.3!important;box-sizing:border-box!important}\n.dai-fullscreen .DialogDropDown_CurrentDisplay{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px!important;line-height:1.3!important}\n.dai-fullscreen .dai-field>button[role=combobox] svg{width:14px;height:14px;flex-shrink:0}\n.dai-fullscreen input.DialogInput{font-size:12px!important;line-height:1.3!important;height:32px!important;min-height:32px!important;max-width:100%;box-sizing:border-box!important;padding:6px 8px!important}\n.dai-fullscreen .DialogInput_Wrapper{min-width:0;width:100%;margin:0}\n.dai-fullscreen .dai-muted{font-size:11px;line-height:1.35}\n.dai-connection-bar{display:flex;align-items:center;gap:8px;min-width:0}\n.dai-connection-bar>.dai-muted{flex:1;min-width:0;overflow-wrap:anywhere}\n.dai-root.dai-fullscreen .dai-connection-bar>.dai-button.DialogButton{width:140px!important;flex:none;font-size:11px!important}\n.dai-host-entry{display:grid;grid-template-columns:minmax(0,1fr) 100px;gap:6px;align-items:center}\n.dai-account-meta{display:flex;align-items:center;gap:8px;min-width:0}\n.dai-account-meta>.dai-account{flex:1;min-width:0;font-size:12px}\n.dai-account-actions{display:flex;gap:6px;flex-wrap:wrap}\n.dai-account-actions>.dai-button{flex:1;min-width:0}\n.dai-account-actions>.dai-login-url{width:100%;font-size:10px}\n@media(max-width:650px){.dai-root.dai-fullscreen{padding:8px;gap:5px}.dai-fullscreen .dai-settings-grid{grid-template-columns:minmax(0,1fr)}.dai-full-brand span{display:none}.dai-root.dai-fullscreen .dai-full-header>.dai-button.DialogButton{width:96px!important}.dai-fullscreen .dai-composer{grid-template-columns:minmax(0,1fr)}.dai-fullscreen .dai-compose-actions{justify-content:stretch}.dai-root.dai-fullscreen .dai-compose-actions>.dai-button.DialogButton{flex:1}}\n\n/* Scale reading text without enlarging navigation in the narrow Steam panel. */\n.dai-root .dai-message{font-size:calc(14px * var(--dai-text-scale,1))}\n.dai-root.dai-fullscreen .dai-message{font-size:calc(13px * var(--dai-text-scale,1))}\n.dai-root .dai-message small{font-size:calc(10px * var(--dai-text-scale,1))}\n.dai-root .dai-label,.dai-root .dai-muted{font-size:calc(12px * var(--dai-text-scale,1))}\n.dai-root.dai-fullscreen .dai-label,.dai-root.dai-fullscreen .dai-muted{font-size:calc(11px * var(--dai-text-scale,1))}\n.dai-root .dai-section h3{font-size:calc(14px * var(--dai-text-scale,1))}\n.dai-root input.DialogInput,.dai-root .DialogDropDown_CurrentDisplay{font-size:calc(12px * var(--dai-text-scale,1))!important;line-height:1.3!important}\n.dai-root input.DialogInput{min-height:calc(20px + 12px * var(--dai-text-scale,1))!important;height:auto!important}\n.dai-root .dai-field>button[role=combobox]{min-height:calc(20px + 12px * var(--dai-text-scale,1))!important;height:auto!important}\n.dai-scale-controls{display:flex;align-items:center;gap:6px;min-width:0}\n.dai-scale-value{flex:1;min-width:44px;text-align:center;font-size:calc(13px * var(--dai-text-scale,1));font-variant-numeric:tabular-nums}\n.dai-root .dai-scale-controls>.dai-button.DialogButton{width:52px!important;flex:none}\n.dai-root .dai-scale-controls>.dai-button.DialogButton:last-child{width:70px!important}\n\n/* Smaller text also frees vertical space for the conversation. Keep enlarged\n   text independent so navigation stays usable in the narrow Quick Access UI. */\n.dai-root{--dai-density:min(1,var(--dai-text-scale,1));gap:calc(8px * var(--dai-density))}\n.dai-root .dai-tabs{gap:calc(4px * var(--dai-density));padding-bottom:calc(7px * var(--dai-density))}\n.dai-root .dai-button.DialogButton{font-size:calc(13px * var(--dai-density))!important;min-height:calc(38px * var(--dai-density))!important;padding:calc(8px * var(--dai-density)) calc(6px * var(--dai-density))!important;gap:calc(6px * var(--dai-density))}\n.dai-root .dai-tab .dai-button.DialogButton{font-size:calc(12px * var(--dai-density))!important;padding:calc(8px * var(--dai-density)) calc(4px * var(--dai-density))!important}\n.dai-root .dai-viewbar>.dai-button.DialogButton{width:calc(126px * var(--dai-density))!important;min-height:calc(32px * var(--dai-density))!important;font-size:calc(11px * var(--dai-density))!important}\n.dai-root .dai-composer{gap:calc(8px * var(--dai-density));padding-top:calc(9px * var(--dai-density))}\n.dai-root .dai-message{padding:calc(10px * var(--dai-density));line-height:1.4}\n.dai-root .dai-message-list{gap:calc(9px * var(--dai-density))}\n.dai-root input.DialogInput{min-height:calc(32px * var(--dai-density))!important;padding:calc(6px * var(--dai-density)) calc(8px * var(--dai-density))!important}\n.dai-root.dai-fullscreen{gap:calc(6px * var(--dai-density));padding:calc(10px * var(--dai-density)) 16px}\n.dai-root.dai-fullscreen .dai-button.DialogButton{font-size:calc(12px * var(--dai-density))!important;min-height:calc(32px * var(--dai-density))!important;padding:calc(6px * var(--dai-density)) calc(8px * var(--dai-density))!important}\n.dai-root.dai-fullscreen .dai-tab .dai-button.DialogButton{min-height:calc(30px * var(--dai-density))!important}\n.dai-root.dai-fullscreen .dai-composer{gap:calc(6px * var(--dai-density));padding-top:calc(7px * var(--dai-density))}\n.dai-root.dai-fullscreen .dai-message{padding:calc(9px * var(--dai-density)) calc(12px * var(--dai-density))}\n.dai-root.dai-fullscreen .dai-message-list{gap:calc(7px * var(--dai-density))}\n.dai-root .dai-empty p{font-size:calc(13px * var(--dai-text-scale,1))}\n\n/* Keep the top and bottom chat controls shallow in both Decky views. */\n.dai-root .dai-message{font-size:calc(13px * var(--dai-text-scale,1))}\n.dai-root.dai-fullscreen .dai-message{font-size:calc(12px * var(--dai-text-scale,1))}\n.dai-root .dai-tabs{padding-bottom:calc(4px * var(--dai-density))}\n.dai-root .dai-tab .dai-button.DialogButton,\n.dai-root .dai-compose-actions>.dai-button.DialogButton,\n.dai-root.dai-fullscreen .dai-tab .dai-button.DialogButton,\n.dai-root.dai-fullscreen .dai-compose-actions>.dai-button.DialogButton{min-height:22px!important;padding:3px 5px!important;font-size:calc(11px * var(--dai-density))!important;line-height:1.2!important;gap:4px}\n.dai-root .dai-viewbar>.dai-button.DialogButton{min-height:22px!important;padding:3px 4px!important}\n.dai-root.dai-fullscreen .dai-full-header>.dai-button.DialogButton{min-height:22px!important;padding:3px 6px!important;font-size:calc(11px * var(--dai-density))!important}\n.dai-root .dai-compose-actions{gap:4px}\n.dai-root .dai-composer{gap:4px;padding-top:4px}\n.dai-root.dai-fullscreen .dai-composer{gap:4px;padding-top:4px}\n.dai-root .dai-composer input.DialogInput{min-height:24px!important;padding:4px 6px!important}\n\n/* Settings use four aligned cards: service and connection, then personal\n   preferences and account. Card rows share their height rather than drifting. */\n.dai-fullscreen .dai-settings-grid{grid-template-areas:\"model connection\" \"personal account\";gap:12px;align-items:stretch;width:100%}\n.dai-fullscreen .dai-settings-column{display:contents}\n.dai-fullscreen .dai-model-settings{grid-area:model}\n.dai-fullscreen .dai-connection-settings{grid-area:connection}\n.dai-fullscreen .dai-text-settings{grid-area:personal}\n.dai-fullscreen .dai-account-settings{grid-area:account}\n.dai-fullscreen .dai-section,.dai-fullscreen .dai-section:last-child{padding:12px;gap:10px;border-color:rgba(170,190,210,.16);background:#16212d;border-radius:7px}\n.dai-fullscreen .dai-section h3{padding-bottom:8px;border-bottom:1px solid var(--dai-line);font-size:12px;color:#dce8f3;letter-spacing:.15px}\n.dai-fullscreen .dai-model-fields{gap:10px 12px}\n.dai-fullscreen .dai-personal-fields{display:grid;grid-template-columns:1.15fr 1fr;gap:12px;align-items:start}\n.dai-fullscreen .dai-scale-controls{gap:4px;min-height:32px}\n.dai-root.dai-fullscreen .dai-scale-controls>.dai-button.DialogButton{width:36px!important;min-height:30px!important;padding:5px 4px!important}\n.dai-root.dai-fullscreen .dai-scale-controls>.dai-button.DialogButton:last-child{width:48px!important}\n.dai-fullscreen .dai-scale-value{min-width:30px;font-size:11px}\n.dai-fullscreen .dai-connection-bar{min-height:30px}\n.dai-fullscreen .dai-account-meta{min-height:32px;flex-wrap:wrap}\n.dai-fullscreen .dai-account-meta>.dai-account{font-size:11px}\n.dai-fullscreen .dai-account-actions{margin-top:auto}\n.dai-fullscreen .dai-field>button[role=combobox]{background:#223243!important;border-radius:4px!important}\n.dai-fullscreen .dai-settings input.DialogInput{background:#223243!important;border-radius:4px!important}\n@media(max-width:650px){.dai-fullscreen .dai-settings-grid{grid-template-columns:minmax(0,1fr);grid-template-areas:\"model\" \"connection\" \"personal\" \"account\"}.dai-fullscreen .dai-personal-fields{grid-template-columns:minmax(0,1fr)}}\n\n/* Fill Decky's actual content slot, including after reopening or resizing.\n   Its generated wrappers otherwise add 16px padding and a viewport clamp. */\ndiv:has(> div > .dai-root:not(.dai-fullscreen)){display:flex!important;flex-direction:column!important;height:100%!important;min-height:0!important;box-sizing:border-box!important}\ndiv:has(> div > .dai-root:not(.dai-fullscreen))>div:not(:has(>.dai-root)){flex-shrink:0}\ndiv:has(> .dai-root:not(.dai-fullscreen)){display:flex!important;flex-direction:column!important;flex:1!important;min-height:0!important;height:auto!important;padding-top:0!important;overflow:hidden}\n.dai-root:not(.dai-fullscreen){height:100%!important;max-height:none!important;min-height:0!important;flex:1;padding-bottom:4px}\n.dai-root:not(.dai-fullscreen)>.dai-page{flex:1;min-height:0}\n.dai-root:not(.dai-fullscreen) .dai-messages{flex:1;min-height:0}\n.dai-root:not(.dai-fullscreen) .dai-composer{margin-top:auto;flex-shrink:0}\n\n/* Decky's sticky title casts a shadow below its layout box. Keep tabs clear\n   of that overlay while the outer panel still fills the available height. */\n.dai-root:not(.dai-fullscreen){padding-top:16px}\n\n.dai-game-setting{display:flex;align-items:center;gap:8px;border-top:1px solid var(--dai-line);padding-top:8px;margin-top:2px}\n.dai-game-setting>.dai-muted{flex:1;min-width:0}\n.dai-root.dai-fullscreen .dai-game-setting>.dai-button.DialogButton{width:82px!important;flex:none}\n.dai-game-context h3{display:flex;align-items:center;gap:6px}\n\n/* Dictation has its own preview; only finalized speech enters the draft. */\n.dai-voice-preview{display:flex;align-items:flex-start;gap:7px;padding:7px 8px;background:rgba(211,55,65,.12);border:1px solid rgba(239,86,96,.45);border-radius:4px;flex-shrink:0;min-width:0;grid-column:1/-1}\n.dai-record-dot{width:7px;height:7px;flex:none;background:#ff5362;border-radius:50%;margin-top:3px;box-shadow:0 0 5px rgba(255,83,98,.45)}\n.dai-voice-preview>div{display:flex;flex-direction:column;gap:3px;min-width:0;flex:1}\n.dai-voice-preview strong{font-size:10px;color:#ff9ca4;line-height:1.2}\n.dai-voice-preview>div>span{font-size:calc(12px * var(--dai-text-scale,1));line-height:1.35;white-space:pre-wrap;overflow-wrap:anywhere;max-height:54px;overflow-y:auto;color:#f5e9eb}\n.dai-root .dai-button.DialogButton.dai-recording{background:#aa2635!important;color:#fff!important;box-shadow:inset 0 0 0 1px #ff7a86!important;opacity:1}\n.dai-root .dai-button.DialogButton.dai-recording:focus,.dai-root .dai-button.DialogButton.dai-recording.gpfocus{background:#cf3546!important;outline:2px solid #fff;outline-offset:-2px}\n\n.dai-game-check{flex:none;min-width:0}\n.dai-root .dai-game-check>.dai-button.DialogButton{width:62px!important;min-height:22px!important;padding:3px 4px!important;font-size:10px!important;gap:4px}\n.dai-check-box{display:inline-flex;align-items:center;justify-content:center;width:12px;height:12px;border:1px solid currentColor;border-radius:2px;font-size:11px;line-height:1;flex:none}\n.dai-game-check[aria-checked=true] .dai-check-box{background:#64b9ef;color:#122432;border-color:#64b9ef}\n\n.dai-message{position:relative}\n.dai-message-tools{position:absolute;top:3px;right:4px;opacity:0;pointer-events:none;transition:opacity .1s}\n.dai-message:hover .dai-message-tools,.dai-message:focus-within .dai-message-tools,.dai-message.dai-focused .dai-message-tools,.dai-message.gpfocus .dai-message-tools{opacity:1;pointer-events:auto}\n.dai-root .dai-message-tools .dai-button.DialogButton,.dai-root.dai-fullscreen .dai-message-tools .dai-button.DialogButton{width:auto!important;min-height:18px!important;padding:2px 5px!important;font-size:9px!important;gap:3px;background:#26394b}\n.dai-latest{flex:none;align-self:center;padding:3px 0}\n.dai-root .dai-latest .dai-button.DialogButton{width:auto!important;min-height:22px!important;padding:3px 8px!important;font-size:10px!important}\n.dai-queue-state{grid-column:1/-1}\n";

// Languages present in the installed multilingual Whisper tokenizer.
const speechLanguages = {
    "af": "африкаанс",
    "am": "амхарский",
    "ar": "арабский",
    "as": "ассамский",
    "az": "азербайджанский",
    "ba": "башкирский",
    "be": "белорусский",
    "bg": "болгарский",
    "bn": "бенгальский",
    "bo": "тибетский",
    "br": "бретонский",
    "bs": "боснийский",
    "ca": "каталанский",
    "cs": "чешский",
    "cy": "валлийский",
    "da": "датский",
    "de": "немецкий",
    "el": "греческий",
    "en": "английский",
    "es": "испанский",
    "et": "эстонский",
    "eu": "баскский",
    "fa": "персидский",
    "fi": "финский",
    "fo": "фарерский",
    "fr": "французский",
    "gl": "галисийский",
    "gu": "гуджарати",
    "ha": "хауса",
    "haw": "гавайский",
    "he": "иврит",
    "hi": "хинди",
    "hr": "хорватский",
    "ht": "гаитянский",
    "hu": "венгерский",
    "hy": "армянский",
    "id": "индонезийский",
    "is": "исландский",
    "it": "итальянский",
    "ja": "японский",
    "jw": "яванский",
    "ka": "грузинский",
    "kk": "казахский",
    "km": "кхмерский",
    "kn": "каннада",
    "ko": "корейский",
    "la": "латинский",
    "lb": "люксембургский",
    "ln": "лингала",
    "lo": "лаосский",
    "lt": "литовский",
    "lv": "латышский",
    "mg": "малагасийский",
    "mi": "маори",
    "mk": "македонский",
    "ml": "малаялам",
    "mn": "монгольский",
    "mr": "маратхи",
    "ms": "малайский",
    "mt": "мальтийский",
    "my": "бирманский",
    "ne": "непальский",
    "nl": "нидерландский",
    "nn": "нюнорск",
    "no": "норвежский",
    "oc": "окситанский",
    "pa": "панджаби",
    "pl": "польский",
    "ps": "пушту",
    "pt": "португальский",
    "ro": "румынский",
    "ru": "русский",
    "sa": "санскрит",
    "sd": "синдхи",
    "si": "сингальский",
    "sk": "словацкий",
    "sl": "словенский",
    "sn": "шона",
    "so": "сомали",
    "sq": "албанский",
    "sr": "сербский",
    "su": "сунданский",
    "sv": "шведский",
    "sw": "суахили",
    "ta": "тамильский",
    "te": "телугу",
    "tg": "таджикский",
    "th": "тайский",
    "tk": "туркменский",
    "tl": "филиппинский",
    "tr": "турецкий",
    "tt": "татарский",
    "uk": "украинский",
    "ur": "урду",
    "uz": "узбекский",
    "vi": "вьетнамский",
    "yi": "идиш",
    "yo": "йоруба",
    "zh": "китайский"
};

function updateDictation(previous, id, thread, text, currentDraft) {
    const session = previous?.id === id ? previous : { id, thread, base: currentDraft, text: '' };
    const rendered = (session.base ? session.base.trimEnd() + ' ' : '') + session.text.trim() + ' ';
    if (session.thread !== thread || session.text === text || (session.text !== '' && currentDraft !== rendered))
        return { session, value: null };
    return { session: { ...session, text }, value: (session.base ? session.base.trimEnd() + ' ' : '') + text.trim() + ' ' };
}
function restoreDictation(raw) {
    try {
        const value = JSON.parse(raw || 'null');
        if (value && ['id', 'thread', 'base', 'text'].every(key => typeof value[key] === 'string'))
            return value;
    }
    catch { }
    return null;
}
function bindDictation(previous, id, thread, base) {
    return previous?.id === id ? previous : { id, thread, base, text: '' };
}

const detailKeys = new Set(['status', 'map', 'level', 'chapter', 'mission', 'mode', 'location', 'gamestatus']);
const clean = (value, max) => typeof value === 'string' ? value.replace(/[\u0000-\u001f\u007f]/g, ' ').trim().slice(0, max) : '';
function readGameContext(source) {
    try {
        const appId = source.appId;
        if (!appId || !Number.isSafeInteger(appId) || appId < 1)
            return null;
        const name = clean(source.overview?.(appId)?.display_name, 160);
        if (!name || /^deck\s*ai$/i.test(name))
            return null;
        const context = { appId, name, status: '', details: [] };
        // A missing/outdated friend status must never obscure the running app.
        try {
            const player = source.player?.();
            const matches = player?.persona?.m_gameid === String(appId) || player?.current_game_name === name;
            if (matches && player) {
                context.status = clean(player.current_game_rich_presence, 300);
                for (const [key, value] of player.persona?.m_mapRichPresence || []) {
                    const text = clean(value, 180);
                    if (detailKeys.has(key) && text && !text.startsWith('#') && text !== context.status)
                        context.details.push([key, text]);
                }
            }
        }
        catch { /* Rich Presence is optional. */ }
        return context;
    }
    catch {
        return null;
    }
}
function withGameContext(question, game, enabled) {
    return enabled && game ? question + '\n\nИгра: ' + game.name : question;
}
function gameScreenshots(screenshots, game) {
    if (!game)
        return [];
    return screenshots.filter(item => item.path.includes('/760/remote/' + game.appId + '/screenshots/')).sort((a, b) => (b.when || 0) - (a.when || 0));
}

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
const accountLogin = callable("account_login");
const accountCancelLogin = callable("account_cancel_login");
const accountLogout = callable("account_logout");
const remoteHost = callable("remote_host");
const setProvider = callable("set_provider");
const setProviderKey = callable("set_provider_key");
const GameScroll = DFL.ScrollPanel;
const providerNames = { codex: "Codex · ChatGPT", claude: "Claude · Pro / Max", deepseek: "DeepSeek · OpenRouter", tokenharbor: "DeepSeek · TokenHarbor" };
const draftKey = (id) => "codex-game-draft:" + (id || "new");
function Action({ children, onClick, disabled = false, primary = false, recording = false }) {
    return SP_JSX.jsx(DFL.DialogButton, { className: "dai-button" + (primary ? " dai-primary" : "") + (recording ? " dai-recording" : ""), disabled: disabled, onClick: onClick, children: children });
}
function GameCheckbox({ checked, onChange }) {
    return SP_JSX.jsx("div", { className: "dai-game-check", role: "checkbox", "aria-checked": checked, "aria-label": "\u0418\u0433\u0440\u0430", children: SP_JSX.jsxs(DFL.DialogButton, { className: "dai-button", onClick: onChange, children: [SP_JSX.jsx("span", { className: "dai-check-box", "aria-hidden": "true", children: checked ? "✓" : "" }), "\u0418\u0433\u0440\u0430"] }) });
}
function Choice({ label, value, options, onChange, disabled = false }) {
    return SP_JSX.jsxs("div", { className: "dai-field", children: [SP_JSX.jsx("span", { className: "dai-label", children: label }), SP_JSX.jsx(DFL.Dropdown, { menuLabel: label, selectedOption: value, rgOptions: options, disabled: disabled || !options.length, strDefaultLabel: "\u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435\u2026", onChange: item => onChange(String(item.data)) })] });
}
// The compact panel and the full-screen route use the same session. Moving
// between them must preserve the draft, attachments and consumed dictation.
const dictationKey = "deck-ai-dictation-v1";
const session = { snapshot: null, attachments: new Map(), voiceText: "", voiceError: "", discardedVoice: localStorage.getItem("deck-ai-discarded-voice") || "", finishedVoice: "", dictation: restoreDictation(localStorage.getItem(dictationKey)) };
const textScaleKey = "deck-ai-text-scale";
const textScaleListeners = new Set();
function readTextScale() {
    const value = Number(localStorage.getItem(textScaleKey) || 1);
    return Number.isFinite(value) ? Math.max(.7, Math.min(1.5, Math.round(value * 10) / 10)) : 1;
}
function useTextScale() {
    const [scale, setScale] = SP_REACT.useState(readTextScale);
    SP_REACT.useEffect(() => { textScaleListeners.add(setScale); return () => { textScaleListeners.delete(setScale); }; }, []);
    return [scale, (value) => {
            const next = Math.max(.7, Math.min(1.5, Math.round(value * 10) / 10));
            localStorage.setItem(textScaleKey, String(next));
            textScaleListeners.forEach(listener => listener(next));
        }];
}
const gameContextListeners = new Set();
function useGameContextEnabled() {
    const [enabled, setEnabled] = SP_REACT.useState(() => localStorage.getItem("deck-ai-game-context") === "on");
    SP_REACT.useEffect(() => { gameContextListeners.add(setEnabled); return () => { gameContextListeners.delete(setEnabled); }; }, []);
    const toggle = () => {
        const next = localStorage.getItem("deck-ai-game-context") !== "on";
        localStorage.setItem("deck-ai-game-context", next ? "on" : "off");
        gameContextListeners.forEach(listener => listener(next));
    };
    return [enabled, toggle];
}
const FULLSCREEN_PATH = "/deck-ai";
let requestedTab = "chat";
let fullscreenOrigin = DFL.Router.MainRunningAppID ? "/apprunning" : "/";
const fullscreenViews = new Set();
let returnToPanel;
function openFullscreen(tab) {
    requestedTab = tab;
    const current = window.location.pathname.replace(/^\/routes/, "") || "/";
    if (current !== FULLSCREEN_PATH)
        fullscreenOrigin = current;
    if (returnToPanel)
        clearTimeout(returnToPanel);
    if (current === FULLSCREEN_PATH && fullscreenViews.size)
        fullscreenViews.forEach(change => change(tab));
    else
        DFL.Navigation.Navigate(FULLSCREEN_PATH);
    DFL.Navigation.CloseSideMenus();
}
function closeFullscreen(panel = true) {
    if (returnToPanel)
        clearTimeout(returnToPanel);
    // Replace the workspace entry: old duplicate /deck-ai history entries must
    // never trap Back/Return to game on the same full-screen page.
    DFL.Router.Navigate(fullscreenOrigin, true);
    if (panel)
        returnToPanel = setTimeout(() => DFL.Navigation.OpenQuickAccessMenu(999), 150);
}
function FullscreenPage() { return SP_JSX.jsx(Panel, { fullscreen: true, initialTab: requestedTab }); }
function Panel({ fullscreen = false, initialTab = "chat" }) {
    const [textScale, setTextScale] = useTextScale();
    const [gameContextEnabled, toggleGameContext] = useGameContextEnabled();
    const [data, setData] = SP_REACT.useState(session.snapshot);
    const [tab, setTab] = SP_REACT.useState(initialTab);
    SP_REACT.useEffect(() => {
        if (!fullscreen)
            return;
        const change = (next) => { setTab(next); setMediaOpen(false); };
        fullscreenViews.add(change);
        return () => { fullscreenViews.delete(change); };
    }, [fullscreen]);
    const [draft, setDraft] = SP_REACT.useState(() => localStorage.getItem(draftKey(session.snapshot?.threadId)) || "");
    const draftId = SP_REACT.useRef(session.snapshot?.threadId || "");
    const [busy, setBusy] = SP_REACT.useState(false);
    const [voiceStarting, setVoiceStarting] = SP_REACT.useState(false);
    const [voicePolling, setVoicePolling] = SP_REACT.useState(false);
    const actionLock = SP_REACT.useRef(false);
    const [error, setError] = SP_REACT.useState("");
    const [notice, setNotice] = SP_REACT.useState("");
    const [showLatest, setShowLatest] = SP_REACT.useState(false);
    SP_REACT.useEffect(() => { if (!notice)
        return; const timer = setTimeout(() => setNotice(""), 4000); return () => clearTimeout(timer); }, [notice]);
    const [lang, setLang] = SP_REACT.useState(() => localStorage.getItem("codex-game-voice") || "ru");
    const [mediaOpen, setMediaOpen] = SP_REACT.useState(false);
    const [images, setImagesState] = SP_REACT.useState(() => session.attachments.get(draftId.current) || []);
    const setImages = (update) => setImagesState(old => {
        const next = typeof update === "function" ? update(old) : update;
        session.attachments.set(draftId.current, next);
        return next;
    });
    const [shot, setShot] = SP_REACT.useState("");
    const [video, setVideo] = SP_REACT.useState("");
    const [key, setKey] = SP_REACT.useState("");
    const [host, setHost] = SP_REACT.useState("");
    const [loginUrl, setLoginUrl] = SP_REACT.useState("");
    const [historyQuery, setHistoryQuery] = SP_REACT.useState("");
    const lastVoice = SP_REACT.useRef(session.voiceText);
    const lastVoiceError = SP_REACT.useRef(session.voiceError);
    const inFlight = SP_REACT.useRef(false);
    const mounted = SP_REACT.useRef(true);
    const chatRef = SP_REACT.useRef(null);
    const followTail = SP_REACT.useRef(true);
    const accept = SP_REACT.useCallback((incoming) => {
        setVoicePolling(["recording", "stopping", "processing"].includes(incoming.voiceState));
        const next = incoming.voiceId === session.finishedVoice && incoming.voiceText ? { ...incoming, voiceState: "done" } : incoming;
        // Change the draft and its storage key together; polling must never copy a
        // draft into a different chat when the selected conversation changes.
        if (next.threadId !== draftId.current) {
            draftId.current = next.threadId;
            setDraft(localStorage.getItem(draftKey(next.threadId)) || "");
            setImagesState(session.attachments.get(next.threadId) || []);
            followTail.current = true;
            setShowLatest(false);
        }
        session.snapshot = next;
        setData(next);
        if (next.voiceId && ["recording", "stopping", "processing"].includes(next.voiceState)) {
            session.dictation = bindDictation(session.dictation, next.voiceId, next.threadId, localStorage.getItem(draftKey(next.threadId)) || "");
            localStorage.setItem(dictationKey, JSON.stringify(session.dictation));
        }
        if (next.voiceId && next.voiceId !== session.discardedVoice && next.voiceText && next.voiceState === "done") {
            const id = next.voiceId;
            const owner = session.dictation?.id === id ? session.dictation.thread : next.threadId;
            const update = updateDictation(session.dictation, id, owner, next.voiceText, localStorage.getItem(draftKey(owner)) || "");
            session.dictation = update.session;
            localStorage.setItem(dictationKey, JSON.stringify(session.dictation));
            if (update.value !== null) {
                localStorage.setItem(draftKey(owner), update.value);
                if (owner === draftId.current)
                    setDraft(update.value);
            }
            lastVoice.current = next.voiceText;
            session.voiceText = next.voiceText;
        }
        else if (!next.voiceId && next.voiceState === "done" && next.voiceText && next.voiceText !== lastVoice.current) {
            lastVoice.current = next.voiceText;
            session.voiceText = next.voiceText;
            setDraft(old => { const value = (old ? old.trimEnd() + " " : "") + next.voiceText.trim() + " "; localStorage.setItem(draftKey(next.threadId), value); return value; });
        }
        if (next.voiceError && next.voiceError !== lastVoiceError.current) {
            lastVoiceError.current = next.voiceError;
            session.voiceError = next.voiceError;
            setError(next.voiceError);
        }
    }, []);
    const load = SP_REACT.useCallback(async () => {
        if (inFlight.current)
            return;
        inFlight.current = true;
        try {
            const next = await snapshot();
            if (mounted.current)
                accept(next);
        }
        catch (e) {
            if (mounted.current)
                setError(String(e));
        }
        finally {
            inFlight.current = false;
        }
    }, [accept]);
    SP_REACT.useEffect(() => { mounted.current = true; void load(); const timer = setInterval(() => void load(), voicePolling ? 500 : 2500); return () => { mounted.current = false; clearInterval(timer); }; }, [load, voicePolling]);
    SP_REACT.useEffect(() => { const el = chatRef.current; if (el && followTail.current)
        el.scrollTop = el.scrollHeight; }, [data?.messages, tab]);
    const editDraft = (value) => { setDraft(value); localStorage.setItem(draftKey(draftId.current), value); };
    const run = async (work) => { if (actionLock.current)
        return; actionLock.current = true; setBusy(true); setError(""); setNotice(""); try {
        await work();
    }
    catch (e) {
        setError(String(e));
    }
    finally {
        actionLock.current = false;
        setBusy(false);
    } };
    const model = data?.models.find(x => x.id === data.model) || data?.models[0];
    const effort = data?.effort || model?.defaultEffort || model?.efforts[0]?.id || "";
    const tier = data?.tier || "default";
    const recording = voiceStarting || data?.voiceState === "recording";
    const voiceProcessing = data?.voiceState === "stopping" || data?.voiceState === "processing";
    const clearDraft = () => {
        session.discardedVoice = data?.voiceId || "";
        localStorage.setItem("deck-ai-discarded-voice", session.discardedVoice);
        if (data?.voiceText) {
            lastVoice.current = data.voiceText;
            session.voiceText = data.voiceText;
        }
        editDraft("");
        setNotice("Поле сообщения очищено");
    };
    const toggleVoice = async () => {
        if (voiceStarting)
            return;
        setVoiceStarting(true);
        setError("");
        const stopping = recording;
        try {
            // RU/EN use the streaming recognizer: no second, blocking model pass.
            const result = await gameVoice(lang === "ru" ? "ru-fast" : lang === "en" ? "en-fast" : lang);
            const latest = session.snapshot;
            if (stopping && latest) {
                session.finishedVoice = latest.voiceId || "";
                accept({ ...latest, ...result, voiceState: (result.voiceText || latest.voiceText) ? "done" : result.voiceState });
            }
            else if (latest) {
                session.finishedVoice = "";
                accept({ ...latest, ...result, voiceText: "" });
            }
            void load();
        }
        catch (e) {
            setError("Не удалось завершить диктовку: " + String(e));
        }
        finally {
            setVoiceStarting(false);
        }
    };
    const currentGame = () => readGameContext({ appId: DFL.Router.MainRunningAppID, overview: id => window.appStore?.GetAppOverviewByAppID(id), player: () => window.friendStore?.GetFriendState(window.friendStore.currentUserSteamID) });
    const game = currentGame();
    const currentScreenshots = gameScreenshots(data?.screenshots || [], game);
    const gameStatus = gameContextEnabled && game ? game.name : model?.name || "Готов";
    const submit = () => void run(async () => {
        if (!data || !draft.trim()) {
            setError("Нет текста для отправки. Завершите диктовку или введите сообщение.");
            return;
        }
        const sentThread = draftId.current, sentDraft = draft;
        await sendMessage(withGameContext(sentDraft, currentGame(), localStorage.getItem("deck-ai-game-context") === "on"), images.map(x => x.path), model?.id || "", effort, tier);
        if (localStorage.getItem(draftKey(sentThread)) === sentDraft) {
            localStorage.setItem(draftKey(sentThread), "");
            if (draftId.current === sentThread)
                setDraft("");
        }
        session.attachments.delete(sentThread);
        if (draftId.current === sentThread)
            setImagesState([]);
        setNotice("Запрос принят · в очереди");
        followTail.current = true;
        void load();
    });
    const copyMessage = (text) => void run(async () => {
        const doc = chatRef.current?.ownerDocument || document;
        try {
            await doc.defaultView.navigator.clipboard.writeText(text);
        }
        catch {
            const focused = doc.activeElement;
            const field = doc.createElement("textarea");
            field.value = text;
            field.style.cssText = "position:fixed;left:0;top:0;opacity:0";
            doc.body.appendChild(field);
            field.select();
            try {
                if (!doc.execCommand("copy"))
                    throw new Error("Не удалось скопировать. Выделите текст сообщения для копирования.");
            }
            finally {
                field.remove();
                focused?.focus();
            }
        }
        setNotice("Текст скопирован");
    });
    const jumpToLatest = () => { followTail.current = true; setShowLatest(false); const el = chatRef.current; if (el)
        el.scrollTop = el.scrollHeight; };
    const settings = (id, depth, speed) => void run(async () => { await saveSettings(id, depth, speed); accept(await snapshot()); });
    const attach = (media) => { if (!media)
        return; setImages(old => old.some(x => x.path === media.path) ? old : [...old, media]); setMediaOpen(false); };
    const signIn = () => void run(async () => { const result = await accountLogin(); setLoginUrl(result.url); setNotice(result.opened ? "Откройте страницу входа и завершите авторизацию." : "Ссылка для входа показана ниже."); await load(); });
    const disconnect = !data?.ready;
    return SP_JSX.jsxs(DFL.Focusable, { style: { "--dai-text-scale": textScale }, "data-text-scale": textScale, className: "dai-root" + (fullscreen ? " dai-fullscreen" : ""), onCancel: event => {
            if (mediaOpen) {
                event.stopPropagation();
                setMediaOpen(false);
            }
            else if (fullscreen) {
                event.stopPropagation();
                closeFullscreen();
            }
        }, children: [SP_JSX.jsx("style", { children: css }), fullscreen && SP_JSX.jsxs(DFL.Focusable, { className: "dai-full-header", "flow-children": "horizontal", children: [SP_JSX.jsxs("div", { className: "dai-full-brand", children: [SP_JSX.jsx("h1", { children: "Deck AI" }), SP_JSX.jsx("span", { children: disconnect ? "Нет соединения" : data?.active ? "Deck AI работает…" : gameStatus })] }), SP_JSX.jsx(GameCheckbox, { checked: gameContextEnabled, onChange: toggleGameContext }), SP_JSX.jsxs(Action, { onClick: () => closeFullscreen(), children: [SP_JSX.jsx(FaCompress, {}), "\u0412 \u043F\u0430\u043D\u0435\u043B\u044C"] }), SP_JSX.jsxs(Action, { onClick: () => closeFullscreen(false), children: [SP_JSX.jsx(FaArrowLeft, {}), "\u041A \u0438\u0433\u0440\u0435"] })] }), SP_JSX.jsx(DFL.Focusable, { className: "dai-tabs", "flow-children": "horizontal", role: "tablist", "aria-label": "Deck AI", children: [["chat", "Чат", SP_JSX.jsx(FaComment, {})], ["history", "История", SP_JSX.jsx(FaHistory, {})], ["settings", "Настройки", SP_JSX.jsx(FaCog, {})]].map(([id, label, icon]) => SP_JSX.jsx("div", { role: "tab", "aria-selected": tab === id, className: "dai-tab " + (tab === id ? "selected" : ""), children: SP_JSX.jsxs(Action, { disabled: busy, onClick: () => { if (id === "settings" && !fullscreen)
                            openFullscreen("settings");
                        else {
                            setTab(id);
                            setMediaOpen(false);
                        } }, children: [icon, SP_JSX.jsx("span", { children: label })] }) }, id)) }), SP_JSX.jsxs("div", { className: "dai-viewbar", children: [SP_JSX.jsxs("div", { className: "dai-status", children: [SP_JSX.jsx("span", { className: "dai-dot " + (disconnect ? "offline" : data?.active ? "working" : "") }), SP_JSX.jsx("span", { children: !data ? "Подключение…" : data.ready ? (data.active ? "Deck AI работает…" : gameStatus) : "Нет соединения" }), data?.remoteHost && SP_JSX.jsx("small", { children: data.remoteHost })] }), !fullscreen && SP_JSX.jsx(GameCheckbox, { checked: gameContextEnabled, onChange: toggleGameContext }), !fullscreen && SP_JSX.jsxs(Action, { disabled: busy, onClick: () => openFullscreen(tab), children: [SP_JSX.jsx(FaExpand, {}), "\u041D\u0430 \u0432\u0435\u0441\u044C \u044D\u043A\u0440\u0430\u043D"] })] }), error && SP_JSX.jsxs("div", { className: "dai-banner", role: "alert", children: [SP_JSX.jsx("span", { children: error }), SP_JSX.jsx(Action, { onClick: () => setError(""), children: "\u0417\u0430\u043A\u0440\u044B\u0442\u044C" })] }), notice && SP_JSX.jsx("div", { className: "dai-notice", role: "status", children: notice }), SP_JSX.jsxs("div", { className: "dai-page", role: "tabpanel", "aria-label": tab === "chat" ? "Чат" : tab === "history" ? "История" : "Настройки", children: [tab === "chat" && SP_JSX.jsx(SP_JSX.Fragment, { children: mediaOpen ? SP_JSX.jsx(GameScroll, { className: "dai-scroll dai-stack", children: SP_JSX.jsxs("div", { className: "dai-stack-content", children: [SP_JSX.jsx(Action, { onClick: () => setMediaOpen(false), children: "\u2190 \u041A \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044E" }), SP_JSX.jsxs("section", { className: "dai-section dai-game-context", children: [SP_JSX.jsxs("h3", { children: [SP_JSX.jsx(FaGamepad, {}), " \u041A\u043E\u043D\u0442\u0435\u043A\u0441\u0442 \u0438\u0433\u0440\u044B"] }), SP_JSX.jsx("p", { className: "dai-muted", children: game ? game.name : "Сейчас Steam не сообщает о запущенной игре." }), game && SP_JSX.jsx("p", { className: "dai-muted", children: game.status || "Игра не передаёт описание текущего места или задания." }), game?.details.map(([key, value]) => SP_JSX.jsxs("p", { className: "dai-muted", children: [key, ": ", value] }, key)), SP_JSX.jsx(GameCheckbox, { checked: gameContextEnabled, onChange: toggleGameContext }), game && SP_JSX.jsxs(Action, { disabled: !currentScreenshots.length, onClick: () => attach(currentScreenshots[0]), children: ["\u0421\u043D\u0438\u043C\u043E\u043A \u0438\u0437 \u044D\u0442\u043E\u0439 \u0438\u0433\u0440\u044B", currentScreenshots[0]?.when ? " · " + new Date(currentScreenshots[0].when * 1000).toLocaleString() : ""] }), SP_JSX.jsx("p", { className: "dai-muted", children: "\u0427\u0442\u043E\u0431\u044B \u043F\u043E\u043A\u0430\u0437\u0430\u0442\u044C, \u0433\u0434\u0435 \u0432\u044B \u0441\u0435\u0439\u0447\u0430\u0441: \u0441\u0434\u0435\u043B\u0430\u0439\u0442\u0435 \u0441\u043D\u0438\u043C\u043E\u043A \u0432 \u0438\u0433\u0440\u0435 \u2014 Steam + R1, \u0437\u0430\u0442\u0435\u043C \u043F\u0440\u0438\u043A\u0440\u0435\u043F\u0438\u0442\u0435 \u0435\u0433\u043E \u0437\u0434\u0435\u0441\u044C. \u0413\u0430\u043B\u043E\u0447\u043A\u0430 \u00AB\u0418\u0433\u0440\u0430\u00BB \u0434\u043E\u0431\u0430\u0432\u043B\u044F\u0435\u0442 \u043A \u0432\u043E\u043F\u0440\u043E\u0441\u0443 \u0442\u043E\u043B\u044C\u043A\u043E \u043D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u0438\u0433\u0440\u044B." })] }), SP_JSX.jsx("h3", { children: "\u0414\u0440\u0443\u0433\u0438\u0435 \u0432\u043B\u043E\u0436\u0435\u043D\u0438\u044F" }), SP_JSX.jsx(Action, { disabled: !data?.screenshots.length, onClick: () => attach(data?.screenshots[0]), children: "\u041F\u043E\u0441\u043B\u0435\u0434\u043D\u0438\u0439 \u0441\u043A\u0440\u0438\u043D\u0448\u043E\u0442" }), SP_JSX.jsx(Choice, { label: "\u0414\u0440\u0443\u0433\u043E\u0439 \u0441\u043A\u0440\u0438\u043D\u0448\u043E\u0442", value: shot, options: (data?.screenshots || []).map(x => ({ data: x.path, label: x.name })), onChange: setShot }), SP_JSX.jsx(Action, { disabled: !shot, onClick: () => attach(data?.screenshots.find(x => x.path === shot)), children: "\u041F\u0440\u0438\u043A\u0440\u0435\u043F\u0438\u0442\u044C \u0441\u043A\u0440\u0438\u043D\u0448\u043E\u0442" }), SP_JSX.jsx(Choice, { label: "\u0412\u0438\u0434\u0435\u043E\u0437\u0430\u043F\u0438\u0441\u044C", value: video, options: (data?.videos || []).map(x => ({ data: x.path, label: x.name })), onChange: setVideo }), SP_JSX.jsx(Action, { disabled: !video || busy, onClick: () => void run(async () => { const result = await videoFrames(video); setImages(old => [...old, ...result.frames]); setMediaOpen(false); }), children: "\u0414\u043E\u0431\u0430\u0432\u0438\u0442\u044C \u043A\u0430\u0434\u0440\u044B \u0438\u0437 \u0432\u0438\u0434\u0435\u043E" }), !data?.screenshots.length && !data?.videos.length && SP_JSX.jsx("p", { className: "dai-muted", children: "\u0421\u0434\u0435\u043B\u0430\u0439\u0442\u0435 \u0441\u043A\u0440\u0438\u043D\u0448\u043E\u0442 \u0432 \u0438\u0433\u0440\u0435: Steam + R1. \u041E\u043D \u043F\u043E\u044F\u0432\u0438\u0442\u0441\u044F \u0437\u0434\u0435\u0441\u044C." })] }) }) : SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(GameScroll, { className: "dai-messages", ref: chatRef, onScroll: () => { const el = chatRef.current; if (el) {
                                        followTail.current = el.scrollHeight - el.scrollTop - el.clientHeight < 60;
                                        setShowLatest(!followTail.current);
                                    } }, children: SP_JSX.jsxs("div", { className: "dai-message-list", children: [!data?.messages.length && SP_JSX.jsxs("div", { className: "dai-empty", children: [SP_JSX.jsx(FaComment, {}), SP_JSX.jsx("h3", { children: "\u041F\u043E\u043C\u043E\u0449\u044C \u043F\u0440\u044F\u043C\u043E \u0432 \u0438\u0433\u0440\u0435" }), SP_JSX.jsxs("p", { children: ["\u0417\u0430\u0434\u0430\u0439\u0442\u0435 \u0432\u043E\u043F\u0440\u043E\u0441 \u0442\u0435\u043A\u0441\u0442\u043E\u043C \u0438\u043B\u0438 \u0433\u043E\u043B\u043E\u0441\u043E\u043C.", SP_JSX.jsx("br", {}), "\u041C\u043E\u0436\u043D\u043E \u0434\u043E\u0431\u0430\u0432\u0438\u0442\u044C \u0441\u043A\u0440\u0438\u043D\u0448\u043E\u0442."] }), disconnect && SP_JSX.jsx(Action, { onClick: () => void run(async () => accept(await refresh())), disabled: busy, children: busy ? "Подключение…" : "Подключиться" })] }), data?.messages.map((message, i) => SP_JSX.jsxs(DFL.Focusable, { className: "dai-message " + message.role, focusClassName: "dai-focused", children: [SP_JSX.jsx("small", { children: message.role === "user" ? "Вы" : providerNames[data.provider]?.split(" · ")[0] || "AI" }), SP_JSX.jsx("div", { children: message.text }), SP_JSX.jsx("div", { className: "dai-message-tools", children: SP_JSX.jsxs(Action, { onClick: () => copyMessage(message.text), children: [SP_JSX.jsx(FaCopy, {}), "\u041A\u043E\u043F\u0438\u0440\u043E\u0432\u0430\u0442\u044C"] }) })] }, message.id || i)), data?.outbox.filter(x => x.status === "error").map(x => SP_JSX.jsxs("div", { className: "dai-failed", children: [SP_JSX.jsx("p", { children: x.error || "Не удалось отправить" }), SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { await retry(x.id); await load(); }), children: "\u041F\u043E\u0432\u0442\u043E\u0440\u0438\u0442\u044C \u043E\u0442\u043F\u0440\u0430\u0432\u043A\u0443" })] }, x.id))] }) }), showLatest && SP_JSX.jsx("div", { className: "dai-latest", children: SP_JSX.jsx(Action, { onClick: jumpToLatest, children: "\u2193 \u041A \u043F\u043E\u0441\u043B\u0435\u0434\u043D\u0435\u043C\u0443 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044E" }) }), SP_JSX.jsxs("div", { className: "dai-composer", children: [data?.outbox.some(job => job.status === "recovering") && SP_JSX.jsx("p", { className: "dai-muted dai-queue-state", role: "status", children: "\u041F\u0440\u043E\u0432\u0435\u0440\u044F\u044E \u0441\u043E\u0441\u0442\u043E\u044F\u043D\u0438\u0435 \u043E\u0442\u043F\u0440\u0430\u0432\u043B\u0435\u043D\u043D\u043E\u0433\u043E \u0437\u0430\u043F\u0440\u043E\u0441\u0430\u2026" }), data?.outbox.some(job => job.status === "queued") && SP_JSX.jsxs("p", { className: "dai-muted dai-queue-state", role: "status", children: ["\u0412 \u043E\u0447\u0435\u0440\u0435\u0434\u0438 \u00B7 ", data.outbox.filter(job => job.status === "queued").length, data.outbox.length === 8 ? "+" : "", " \u00B7 \u043F\u043E\u0441\u043B\u0435 \u0442\u0435\u043A\u0443\u0449\u0435\u0433\u043E \u043E\u0442\u0432\u0435\u0442\u0430"] }), images.length > 0 && SP_JSX.jsx("div", { className: "dai-attachments", children: images.map((image, i) => SP_JSX.jsxs(Action, { onClick: () => setImages(old => old.filter((_, n) => n !== i)), children: ["\u00D7 ", image.name] }, image.path + ":" + i)) }), (recording || voiceProcessing) && SP_JSX.jsxs("div", { className: "dai-voice-preview", role: "status", "aria-live": "polite", children: [SP_JSX.jsx("span", { className: "dai-record-dot", "aria-hidden": "true" }), SP_JSX.jsxs("div", { children: [SP_JSX.jsx("strong", { children: recording ? "● Запись · распознанный текст" : "Завершаю распознавание…" }), SP_JSX.jsx("span", { role: "textbox", "aria-label": "\u0420\u0430\u0441\u043F\u043E\u0437\u043D\u0430\u043D\u043D\u0430\u044F \u0440\u0435\u0447\u044C", "aria-readonly": "true", children: (data?.voiceId !== session.discardedVoice ? data?.voiceText : "") || (["ru", "en", "ru-fast", "en-fast"].includes(lang) ? "Здесь появится распознанная речь" : "Записываю. Текст появится после «Стоп».") })] })] }), SP_JSX.jsx("div", { className: "dai-draft-field", children: SP_JSX.jsx(DFL.TextField, { disabled: recording || voiceProcessing, value: draft, placeholder: "\u0421\u043F\u0440\u043E\u0441\u0438\u0442\u044C \u043E\u0431 \u0438\u0433\u0440\u0435\u2026", onChange: e => editDraft(e.target.value), onKeyDown: e => { if (e.key === "Enter" && !e.shiftKey) {
                                                    e.preventDefault();
                                                    submit();
                                                } } }) }), SP_JSX.jsxs(DFL.Focusable, { className: "dai-compose-actions", "flow-children": "horizontal", children: [SP_JSX.jsxs(Action, { recording: recording || voiceProcessing, disabled: !data || voiceProcessing || busy, onClick: () => void toggleVoice(), children: [SP_JSX.jsx(FaMicrophone, {}), recording ? "Стоп" : "Голос"] }), SP_JSX.jsx(Action, { disabled: voiceStarting || (!draft.trim() && !recording && !voiceProcessing), onClick: clearDraft, children: "\u041E\u0447\u0438\u0441\u0442\u0438\u0442\u044C" }), fullscreen && data?.active && data.provider === "codex" && SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { await stop(); await load(); }), children: "\u0421\u0442\u043E\u043F" }), SP_JSX.jsx(Action, { primary: true, disabled: busy || disconnect || recording || voiceProcessing || !draft.trim(), onClick: submit, children: busy ? "…" : "Отправить" })] }), !fullscreen && data?.active && data.provider === "codex" && SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { await stop(); await load(); }), children: "\u041E\u0441\u0442\u0430\u043D\u043E\u0432\u0438\u0442\u044C \u043E\u0442\u0432\u0435\u0442" })] })] }) }), tab === "history" && SP_JSX.jsx(GameScroll, { className: "dai-scroll dai-stack", children: SP_JSX.jsxs("div", { className: "dai-stack-content", children: [SP_JSX.jsx(Action, { primary: true, disabled: busy || disconnect || data?.active, onClick: () => void run(async () => { accept(await newThread()); setTab("chat"); }), children: "\uFF0B \u041D\u043E\u0432\u044B\u0439 \u0447\u0430\u0442" }), SP_JSX.jsx(DFL.TextField, { value: historyQuery, placeholder: "\u041D\u0430\u0439\u0442\u0438 \u0440\u0430\u0437\u0433\u043E\u0432\u043E\u0440\u2026", onChange: e => setHistoryQuery(e.target.value) }), !data?.threads.length && SP_JSX.jsx("p", { className: "dai-muted", children: "\u0412\u0430\u0448\u0438 \u0440\u0430\u0437\u0433\u043E\u0432\u043E\u0440\u044B \u043F\u043E\u044F\u0432\u044F\u0442\u0441\u044F \u0437\u0434\u0435\u0441\u044C." }), data?.threads.filter(x => x.name.toLocaleLowerCase().includes(historyQuery.toLocaleLowerCase())).map(thread => SP_JSX.jsx("div", { className: "dai-history-item " + (thread.id === data.threadId ? "selected" : ""), children: SP_JSX.jsxs(Action, { disabled: busy || data.active, onClick: () => void run(async () => { accept(await selectThread(thread.id)); setTab("chat"); }), children: [SP_JSX.jsx("span", { children: thread.name || "Новый чат" }), thread.id === data.threadId && SP_JSX.jsx("small", { children: "\u0422\u0435\u043A\u0443\u0449\u0438\u0439" })] }) }, thread.id))] }) }), tab === "settings" && SP_JSX.jsx(GameScroll, { className: "dai-scroll dai-stack dai-settings", children: SP_JSX.jsxs("div", { className: "dai-settings-grid", children: [SP_JSX.jsxs("div", { className: "dai-settings-column", children: [SP_JSX.jsxs("section", { className: "dai-section dai-model-settings", children: [SP_JSX.jsx("h3", { children: "\u041C\u043E\u0434\u0435\u043B\u044C \u0438 \u043E\u0442\u0432\u0435\u0442" }), SP_JSX.jsxs("div", { className: "dai-model-fields", children: [SP_JSX.jsx(Choice, { label: "\u0421\u0435\u0440\u0432\u0438\u0441", value: data?.provider || "codex", options: Object.entries(providerNames).map(([data, label]) => ({ data, label })), disabled: busy || data?.active, onChange: value => void run(async () => { accept(await setProvider(value)); setKey(""); }) }), SP_JSX.jsx(Choice, { label: "\u041C\u043E\u0434\u0435\u043B\u044C", value: model?.id || "", options: (data?.models || []).map(x => ({ data: x.id, label: x.name })), disabled: busy, onChange: id => { const next = data?.models.find(x => x.id === id); settings(id, next?.defaultEffort || next?.efforts[0]?.id || "", "default"); } }), data?.provider === "codex" && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(Choice, { label: "\u0413\u043B\u0443\u0431\u0438\u043D\u0430 \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u043A\u0438", value: effort, options: (model?.efforts || []).map(x => ({ data: x.id, label: x.name })), disabled: busy, onChange: value => settings(model?.id || "", value, tier) }), SP_JSX.jsx(Choice, { label: "\u0421\u043A\u043E\u0440\u043E\u0441\u0442\u044C", value: tier, options: [{ data: "default", label: "Обычная" }, ...(model?.tiers.includes("priority") ? [{ data: "priority", label: "Приоритетная" }] : [])], disabled: busy, onChange: value => settings(model?.id || "", effort, value) })] })] }), (data?.provider === "deepseek" || data?.provider === "tokenharbor") && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.TextField, { bIsPassword: true, value: key, placeholder: "\u041A\u043B\u044E\u0447 API", onChange: e => setKey(e.target.value) }), SP_JSX.jsx(Action, { disabled: busy || !key.trim(), onClick: () => void run(async () => { await setProviderKey(key.trim()); setKey(""); accept(await refresh()); setNotice("Ключ сохранён"); }), children: "\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u043A\u043B\u044E\u0447" }), SP_JSX.jsx("p", { className: "dai-muted", children: "\u041A\u043B\u044E\u0447 \u0445\u0440\u0430\u043D\u0438\u0442\u0441\u044F \u0432 \u0441\u0438\u0441\u0442\u0435\u043C\u043D\u043E\u043C \u0445\u0440\u0430\u043D\u0438\u043B\u0438\u0449\u0435 SteamOS." })] }), data?.provider === "claude" && SP_JSX.jsx("p", { className: "dai-muted", children: "\u0418\u0441\u043F\u043E\u043B\u044C\u0437\u0443\u0435\u0442\u0441\u044F \u0432\u0445\u043E\u0434 Claude Code, \u043D\u0430\u0441\u0442\u0440\u043E\u0435\u043D\u043D\u044B\u0439 \u0432 \u0440\u0435\u0436\u0438\u043C\u0435 \u0440\u0430\u0431\u043E\u0447\u0435\u0433\u043E \u0441\u0442\u043E\u043B\u0430." })] }), SP_JSX.jsxs("section", { className: "dai-section dai-text-settings", children: [SP_JSX.jsx("h3", { children: "\u0418\u043D\u0442\u0435\u0440\u0444\u0435\u0439\u0441 \u0438 \u0433\u043E\u043B\u043E\u0441" }), SP_JSX.jsxs("div", { className: "dai-personal-fields", children: [SP_JSX.jsxs("div", { className: "dai-field", children: [SP_JSX.jsx("span", { className: "dai-label", children: "\u041C\u0430\u0441\u0448\u0442\u0430\u0431 \u0447\u0430\u0442\u0430 \u0438 \u043A\u043D\u043E\u043F\u043E\u043A" }), SP_JSX.jsxs(DFL.Focusable, { className: "dai-scale-controls", "flow-children": "horizontal", children: [SP_JSX.jsx(Action, { disabled: textScale <= .7, onClick: () => setTextScale(textScale - .1), children: "\u0410\u2212" }), SP_JSX.jsxs("span", { className: "dai-scale-value", "aria-live": "polite", children: [Math.round(textScale * 100), "%"] }), SP_JSX.jsx(Action, { disabled: textScale >= 1.5, onClick: () => setTextScale(textScale + .1), children: "\u0410+" }), SP_JSX.jsx(Action, { disabled: textScale === 1, onClick: () => setTextScale(1), children: "\u0421\u0431\u0440\u043E\u0441" })] })] }), SP_JSX.jsx(Choice, { label: "\u042F\u0437\u044B\u043A \u0440\u0430\u0441\u043F\u043E\u0437\u043D\u0430\u0432\u0430\u043D\u0438\u044F", value: lang, options: !data?.speechReady ? [{ data: "ru", label: "Русский" }, { data: "en", label: "English" }] : [{ data: "auto", label: "Определять автоматически" }, ...Object.entries(speechLanguages).sort(([a], [b]) => a === "ru" ? -1 : b === "ru" ? 1 : a === "en" ? -1 : b === "en" ? 1 : 0).map(([data, label]) => ({ data, label })), { data: "ru-fast", label: "Русский · экономный" }, { data: "en-fast", label: "English · экономный" }], onChange: value => { setLang(value); localStorage.setItem("codex-game-voice", value); } })] }), data?.speechVersion === 2 && !data.speechReady && SP_JSX.jsx("p", { className: "dai-muted", children: "\u0414\u043B\u044F \u0434\u0440\u0443\u0433\u0438\u0445 \u044F\u0437\u044B\u043A\u043E\u0432 \u0443\u0441\u0442\u0430\u043D\u043E\u0432\u0438\u0442\u0435 \u043C\u043D\u043E\u0433\u043E\u044F\u0437\u044B\u0447\u043D\u0443\u044E \u043C\u043E\u0434\u0435\u043B\u044C: scripts/download-models.sh --accurate-ru" }), SP_JSX.jsxs("div", { className: "dai-game-setting", children: [SP_JSX.jsx("span", { className: "dai-muted", children: "\u0414\u043E\u0431\u0430\u0432\u043B\u044F\u0442\u044C \u0442\u043E\u043B\u044C\u043A\u043E \u043D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u0438\u0433\u0440\u044B" }), SP_JSX.jsx(GameCheckbox, { checked: gameContextEnabled, onChange: toggleGameContext })] })] })] }), SP_JSX.jsxs("div", { className: "dai-settings-column", children: [SP_JSX.jsxs("section", { className: "dai-section dai-connection-settings", children: [SP_JSX.jsx("h3", { children: "\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u0435 Codex" }), SP_JSX.jsxs("div", { className: "dai-connection-bar", children: [SP_JSX.jsx("p", { className: "dai-muted", children: (data?.active ? "Deck AI работает…" : data?.status) || "Сервер пока недоступен. Можно повторить подключение." }), SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { accept(await refresh()); setNotice("Соединение обновлено"); }), children: busy ? "Подключение…" : "Переподключиться" })] }), (!data || data.provider === "codex") && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(Choice, { label: "\u0423\u0441\u0442\u0440\u043E\u0439\u0441\u0442\u0432\u043E", value: data?.remoteHost || "", options: [{ data: "", label: "Этот Steam Deck" }, ...(data?.sshHosts || []).map(x => ({ data: x, label: x }))], disabled: busy || data?.active, onChange: value => void run(async () => accept(await remoteHost(value))) }), SP_JSX.jsxs("div", { className: "dai-host-entry", children: [SP_JSX.jsx(DFL.TextField, { value: host, placeholder: "\u0414\u0440\u0443\u0433\u043E\u0439 SSH-\u0430\u043B\u0438\u0430\u0441", onChange: e => setHost(e.target.value) }), SP_JSX.jsx(Action, { disabled: busy || !host.trim() || data?.active, onClick: () => void run(async () => { accept(await remoteHost(host.trim())); setHost(""); }), children: "\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0438\u0442\u044C" })] })] })] }), SP_JSX.jsxs("section", { className: "dai-section dai-account-settings", children: [SP_JSX.jsx("h3", { children: "\u0410\u043A\u043A\u0430\u0443\u043D\u0442 ChatGPT" }), SP_JSX.jsxs("div", { className: "dai-account-meta", children: [SP_JSX.jsx("p", { className: "dai-account", children: data?.account?.email || "Вход не выполнен" }), data?.account?.planType && SP_JSX.jsx("p", { className: "dai-muted", children: data.account.planType })] }), SP_JSX.jsxs("div", { className: "dai-account-actions", children: [SP_JSX.jsx(Action, { disabled: busy, onClick: signIn, children: data?.account ? "Сменить аккаунт" : "Войти в аккаунт" }), data?.loginPending && SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { await accountCancelLogin(); setLoginUrl(""); await load(); }), children: "\u041E\u0442\u043C\u0435\u043D\u0438\u0442\u044C \u0432\u0445\u043E\u0434" }), loginUrl && SP_JSX.jsx("p", { className: "dai-login-url", children: loginUrl }), data?.account && SP_JSX.jsx(Action, { disabled: busy, onClick: () => DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: "\u0412\u044B\u0439\u0442\u0438 \u0438\u0437 ChatGPT?", strDescription: "\u0414\u043B\u044F \u0440\u0430\u0431\u043E\u0442\u044B Codex \u043F\u043E\u0442\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044F \u0441\u043D\u043E\u0432\u0430 \u0432\u043E\u0439\u0442\u0438.", strOKButtonText: "\u0412\u044B\u0439\u0442\u0438", strCancelButtonText: "\u041E\u0442\u043C\u0435\u043D\u0430", onOK: () => void run(async () => { await accountLogout(); accept(await refresh()); }) })), children: "\u0412\u044B\u0439\u0442\u0438 \u0438\u0437 \u0430\u043A\u043A\u0430\u0443\u043D\u0442\u0430" })] })] })] })] }) })] })] });
}
var index = definePlugin(() => {
    routerHook.addRoute(FULLSCREEN_PATH, FullscreenPage, { exact: true });
    return { name: "Deck AI", titleView: SP_JSX.jsx("span", { children: "Deck AI" }), content: SP_JSX.jsx(Panel, {}), icon: SP_JSX.jsx("img", { src: logo, alt: "Deck AI", style: { width: 20, height: 20, objectFit: "contain" } }), onDismount() {
            if (returnToPanel)
                clearTimeout(returnToPanel);
            routerHook.removeRoute(FULLSCREEN_PATH);
        } };
});

export { index as default };
