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
const toaster = api.toaster;
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
function FaSyncAlt (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M370.72 133.28C339.458 104.008 298.888 87.962 255.848 88c-77.458.068-144.328 53.178-162.791 126.85-1.344 5.363-6.122 9.15-11.651 9.15H24.103c-7.498 0-13.194-6.807-11.807-14.176C33.933 94.924 134.813 8 256 8c66.448 0 126.791 26.136 171.315 68.685L463.03 40.97C478.149 25.851 504 36.559 504 57.941V192c0 13.255-10.745 24-24 24H345.941c-21.382 0-32.09-25.851-16.971-40.971l41.75-41.749zM32 296h134.059c21.382 0 32.09 25.851 16.971 40.971l-41.75 41.75c31.262 29.273 71.835 45.319 114.876 45.28 77.418-.07 144.315-53.144 162.787-126.849 1.344-5.363 6.122-9.15 11.651-9.15h57.304c7.498 0 13.194 6.807 11.807 14.176C478.067 417.076 377.187 504 256 504c-66.448 0-126.791-26.136-171.315-68.685L48.97 471.03C33.851 486.149 8 475.441 8 454.059V320c0-13.255 10.745-24 24-24z"},"child":[]}]})(props);
}function FaPlus (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M416 208H272V64c0-17.67-14.33-32-32-32h-32c-17.67 0-32 14.33-32 32v144H32c-17.67 0-32 14.33-32 32v32c0 17.67 14.33 32 32 32h144v144c0 17.67 14.33 32 32 32h32c17.67 0 32-14.33 32-32V304h144c17.67 0 32-14.33 32-32v-32c0-17.67-14.33-32-32-32z"},"child":[]}]})(props);
}function FaMicrophone (props) {
  return GenIcon({"attr":{"viewBox":"0 0 352 512"},"child":[{"tag":"path","attr":{"d":"M176 352c53.02 0 96-42.98 96-96V96c0-53.02-42.98-96-96-96S80 42.98 80 96v160c0 53.02 42.98 96 96 96zm160-160h-16c-8.84 0-16 7.16-16 16v48c0 74.8-64.49 134.82-140.79 127.38C96.71 376.89 48 317.11 48 250.3V208c0-8.84-7.16-16-16-16H16c-8.84 0-16 7.16-16 16v40.16c0 89.64 63.97 169.55 152 181.69V464H96c-8.84 0-16 7.16-16 16v16c0 8.84 7.16 16 16 16h160c8.84 0 16-7.16 16-16v-16c0-8.84-7.16-16-16-16h-56v-33.77C285.71 418.47 352 344.9 352 256v-48c0-8.84-7.16-16-16-16z"},"child":[]}]})(props);
}function FaListUl (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M48 48a48 48 0 1 0 48 48 48 48 0 0 0-48-48zm0 160a48 48 0 1 0 48 48 48 48 0 0 0-48-48zm0 160a48 48 0 1 0 48 48 48 48 0 0 0-48-48zm448 16H176a16 16 0 0 0-16 16v32a16 16 0 0 0 16 16h320a16 16 0 0 0 16-16v-32a16 16 0 0 0-16-16zm0-320H176a16 16 0 0 0-16 16v32a16 16 0 0 0 16 16h320a16 16 0 0 0 16-16V80a16 16 0 0 0-16-16zm0 160H176a16 16 0 0 0-16 16v32a16 16 0 0 0 16 16h320a16 16 0 0 0 16-16v-32a16 16 0 0 0-16-16z"},"child":[]}]})(props);
}function FaHistory (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M504 255.531c.253 136.64-111.18 248.372-247.82 248.468-59.015.042-113.223-20.53-155.822-54.911-11.077-8.94-11.905-25.541-1.839-35.607l11.267-11.267c8.609-8.609 22.353-9.551 31.891-1.984C173.062 425.135 212.781 440 256 440c101.705 0 184-82.311 184-184 0-101.705-82.311-184-184-184-48.814 0-93.149 18.969-126.068 49.932l50.754 50.754c10.08 10.08 2.941 27.314-11.313 27.314H24c-8.837 0-16-7.163-16-16V38.627c0-14.254 17.234-21.393 27.314-11.314l49.372 49.372C129.209 34.136 189.552 8 256 8c136.81 0 247.747 110.78 248 247.531zm-180.912 78.784l9.823-12.63c8.138-10.463 6.253-25.542-4.21-33.679L288 256.349V152c0-13.255-10.745-24-24-24h-16c-13.255 0-24 10.745-24 24v135.651l65.409 50.874c10.463 8.137 25.541 6.253 33.679-4.21z"},"child":[]}]})(props);
}function FaGamepad (props) {
  return GenIcon({"attr":{"viewBox":"0 0 640 512"},"child":[{"tag":"path","attr":{"d":"M480.07 96H160a160 160 0 1 0 114.24 272h91.52A160 160 0 1 0 480.07 96zM248 268a12 12 0 0 1-12 12h-52v52a12 12 0 0 1-12 12h-24a12 12 0 0 1-12-12v-52H84a12 12 0 0 1-12-12v-24a12 12 0 0 1 12-12h52v-52a12 12 0 0 1 12-12h24a12 12 0 0 1 12 12v52h52a12 12 0 0 1 12 12zm216 76a40 40 0 1 1 40-40 40 40 0 0 1-40 40zm64-96a40 40 0 1 1 40-40 40 40 0 0 1-40 40z"},"child":[]}]})(props);
}function FaFolderOpen (props) {
  return GenIcon({"attr":{"viewBox":"0 0 576 512"},"child":[{"tag":"path","attr":{"d":"M572.694 292.093L500.27 416.248A63.997 63.997 0 0 1 444.989 448H45.025c-18.523 0-30.064-20.093-20.731-36.093l72.424-124.155A64 64 0 0 1 152 256h399.964c18.523 0 30.064 20.093 20.73 36.093zM152 224h328v-48c0-26.51-21.49-48-48-48H272l-64-64H48C21.49 64 0 85.49 0 112v278.046l69.077-118.418C86.214 242.25 117.989 224 152 224z"},"child":[]}]})(props);
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

var css = "/* The Quick Access panel is about 300px wide. Keep all rules local to Deck AI. */\n.dai-root{--dai-line:rgba(255,255,255,.12);--dai-muted:#aab6c3;display:flex;flex-direction:column;gap:8px;box-sizing:border-box;width:100%;max-width:100%;height:clamp(300px,calc(100vh - 180px),580px);min-height:0;padding:0 12px 10px;color:#f0f4f8;font-size:14px;line-height:1.4;overflow:hidden}\n.dai-root *{box-sizing:border-box}.dai-root h3{font-size:14px;font-weight:650;margin:0 0 9px}.dai-root p{margin:0}.dai-tabs{display:flex;gap:4px;flex-shrink:0;border-bottom:1px solid var(--dai-line);padding-bottom:7px}.dai-tab{flex:1;min-width:0}.dai-root .dai-button{display:flex;align-items:center;justify-content:center;gap:6px;width:100%;min-width:0;min-height:38px;height:auto;padding:8px 9px;border-radius:3px;font-size:13px;line-height:1.3;white-space:normal;overflow-wrap:anywhere;box-shadow:none}.dai-tab .dai-button{background:transparent;color:var(--dai-muted);padding:9px 4px;font-size:12px;gap:5px}.dai-tab.selected .dai-button{background:#34495d;color:white}.dai-root .dai-button:focus,.dai-root .dai-button.gpfocus,.dai-root .dai-focused{outline:2px solid #fff;outline-offset:-2px;background:#dce8f1;color:#152638}.dai-root .dai-primary{background:#1a77b9;color:white}.dai-root .dai-button:disabled{opacity:.4}.dai-status{display:flex;align-items:center;gap:6px;min-height:18px;font-size:11px;color:var(--dai-muted);flex-shrink:0}.dai-status>span:nth-child(2){overflow:hidden;white-space:nowrap;text-overflow:ellipsis;flex:1;min-width:0}.dai-status small{max-width:75px;overflow:hidden;text-overflow:ellipsis}.dai-dot{height:6px;width:6px;border-radius:50%;background:#69c49a;flex-shrink:0}.dai-dot.offline{background:#e59980}.dai-dot.working{background:#e4c56e}.dai-page{display:flex;flex-direction:column;flex:1;min-height:0;overflow:hidden}.dai-scroll{flex:1;min-height:0;overflow-y:auto;overflow-x:hidden;padding:2px 2px 10px;scrollbar-width:thin}.dai-stack{display:flex;flex-direction:column;gap:10px}.dai-section{display:flex;flex-direction:column;gap:10px;padding:4px 0 14px;border-bottom:1px solid var(--dai-line);flex-shrink:0}.dai-section:last-child{border:0}.dai-section h3{color:#fff;margin:0}.dai-field{display:flex;flex-direction:column;gap:5px;min-width:0}.dai-label{font-size:12px;color:var(--dai-muted)}.dai-field>div{min-width:0;max-width:100%}.dai-muted{font-size:12px;color:var(--dai-muted);line-height:1.45}.dai-account{overflow-wrap:anywhere}.dai-login-url{overflow-wrap:anywhere;font-size:11px;user-select:text}.dai-messages{flex:1;min-height:65px;overflow-y:auto;overflow-x:hidden;scrollbar-width:thin;display:flex;flex-direction:column;gap:9px;padding:3px 2px 10px}.dai-message{flex-shrink:0;padding:10px;border-radius:4px;background:rgba(255,255,255,.045);overflow-wrap:anywhere;white-space:pre-wrap;font-size:14px;line-height:1.5;user-select:text}.dai-message.user{background:rgba(100,165,220,.12)}.dai-message small{display:block;font-size:10px;font-weight:650;color:var(--dai-muted);margin-bottom:4px}.dai-empty{margin:auto 0;text-align:center;padding:12px 3px;color:var(--dai-muted)}.dai-empty>svg{font-size:23px;opacity:.7;margin:0 0 8px}.dai-empty h3{color:#fff;margin-bottom:5px}.dai-empty p{font-size:13px;line-height:1.6;margin-bottom:12px}.dai-composer{display:flex;flex-direction:column;gap:8px;flex-shrink:0;border-top:1px solid var(--dai-line);padding-top:9px}.dai-compose-actions{display:flex;gap:5px}.dai-compose-actions>.dai-button{flex:1;padding:9px 4px;font-size:12px}.dai-compose-actions>.dai-button svg{flex-shrink:0}.dai-attachments{display:flex;flex-direction:column;gap:4px;max-height:80px;overflow-y:auto}.dai-attachments .dai-button{font-size:11px;min-height:30px;justify-content:flex-start}.dai-banner{display:flex;flex-direction:column;gap:5px;flex-shrink:0;padding:7px;background:#502f36;border-radius:3px;font-size:12px}.dai-banner>span{max-height:65px;overflow-y:auto;overflow-wrap:anywhere}.dai-banner .dai-button{min-height:26px;padding:4px;font-size:11px}.dai-notice{font-size:11px;color:#a9cddb;flex-shrink:0;max-height:40px;overflow-y:auto}.dai-history-item .dai-button{flex-direction:column;align-items:flex-start;text-align:left;padding:10px}.dai-history-item.selected{border-left:3px solid #66b5ef}.dai-history-item small{font-size:10px;color:var(--dai-muted)}.dai-failed{display:flex;flex-direction:column;gap:6px;font-size:12px;color:#ffc9b7}\n@media(max-height:600px){.dai-root{height:clamp(260px,calc(100vh - 140px),460px);gap:5px}.dai-root .dai-button{min-height:34px}.dai-composer{gap:5px;padding-top:6px}}\n\n.dai-stack-content{display:flex;flex-direction:column;gap:10px;flex-shrink:0}.dai-message-list{display:flex;flex-direction:column;gap:9px;min-height:100%;flex-shrink:0}.dai-settings-grid{flex-shrink:0}\n\n.dai-root .dai-button{box-sizing:border-box!important}\n.dai-tab:first-child{flex:.8}.dai-tab:last-child{flex:1.25}.dai-tab .dai-button{white-space:nowrap}.dai-tab .dai-button svg{flex-shrink:0}\n/* Gaming Mode's .DialogButton rules have higher specificity than desktop\n   styles. Override only this plugin's dimensions so Steam cannot impose its\n   160px minimum on each control in the 300px Quick Access column. */\n.dai-root .dai-button.DialogButton{width:100%!important;min-width:0!important;max-width:100%!important;min-height:38px!important;height:auto!important;padding:8px 6px!important;font-size:13px!important;line-height:1.3!important;border-radius:4px!important}\n.dai-root .dai-tab .dai-button.DialogButton{font-size:12px!important;padding:8px 4px!important;background:transparent!important;color:var(--dai-muted)!important}\n.dai-root .dai-tab.selected .dai-button.DialogButton{background:#34495d!important;color:#fff!important}\n.dai-root .dai-button.dai-primary{background:#1a77b9!important;color:#fff!important}\n.dai-root .dai-button.DialogButton.gpfocus,.dai-root .dai-button.DialogButton:focus{background:#dce8f1!important;color:#152638!important}\n.dai-viewbar{display:flex;align-items:center;gap:6px;flex-shrink:0;min-width:0}.dai-viewbar>.dai-status{flex:1;min-width:0}.dai-root .dai-viewbar>.dai-button.DialogButton{width:126px!important;flex-shrink:0;font-size:11px!important;min-height:32px!important;padding:6px 4px!important}\n/* Full-screen UI uses Steam's 854x534 CSS viewport on a 1280x800 Deck.\n   Reserve its top/bottom bars and keep primary controls visible together. */\n.dai-draft-field{min-width:0;width:100%}\n.dai-root.dai-fullscreen{position:fixed;inset:40px 0;width:100vw;max-width:none;height:calc(100vh - 80px);max-height:none;min-height:0;margin:0;padding:10px 16px;background:#101923;gap:6px;font-size:12px;line-height:1.35}\n.dai-full-header{display:flex;align-items:center;gap:8px;flex-shrink:0;min-width:0}\n.dai-full-brand{flex:1;min-width:0;display:flex;align-items:center;gap:12px}\n.dai-full-brand h1{font-size:18px;line-height:1.2;margin:0;white-space:nowrap}\n.dai-full-brand span{font-size:11px;color:var(--dai-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}\n.dai-root.dai-fullscreen .dai-button.DialogButton{font-size:12px!important;min-height:32px!important;padding:6px 8px!important;line-height:1.3!important}\n.dai-root.dai-fullscreen .dai-full-header>.dai-button.DialogButton{width:106px!important;flex:none}\n.dai-fullscreen>.dai-tabs{max-width:540px;padding-bottom:5px;gap:6px}\n.dai-root.dai-fullscreen .dai-tab .dai-button.DialogButton{font-size:12px!important;padding:6px!important;min-height:30px!important}\n.dai-fullscreen>.dai-viewbar{display:none}\n.dai-fullscreen .dai-page{width:100%;max-width:1200px;margin:0 auto}\n.dai-fullscreen .dai-scroll{padding:0 2px 2px}\n.dai-fullscreen .dai-message{padding:9px 12px;font-size:13px;line-height:1.45}\n.dai-fullscreen .dai-message-list{gap:7px}\n.dai-fullscreen .dai-message small{font-size:10px;margin-bottom:3px}\n.dai-fullscreen .dai-messages{padding:2px 2px 8px}\n.dai-fullscreen .dai-composer{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:6px;padding-top:7px}\n.dai-fullscreen .dai-composer>.dai-attachments,.dai-fullscreen .dai-composer>.dai-muted{grid-column:1/-1}\n.dai-fullscreen .dai-compose-actions{gap:5px;justify-content:flex-end}\n.dai-root.dai-fullscreen .dai-compose-actions>.dai-button.DialogButton{width:auto!important;flex:none;padding:6px 9px!important}\n.dai-fullscreen .dai-settings-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;align-items:start}\n.dai-settings-column{display:flex;flex-direction:column;gap:9px;min-width:0}\n.dai-fullscreen .dai-section,.dai-fullscreen .dai-section:last-child{padding:10px;border:1px solid var(--dai-line);border-radius:5px;background:rgba(255,255,255,.025);gap:7px;min-width:0}\n.dai-fullscreen .dai-section h3{font-size:14px;line-height:1.25;margin:0}\n.dai-model-fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}\n.dai-fullscreen .dai-label{font-size:11px;line-height:1.25}\n.dai-fullscreen .dai-field{gap:4px;min-width:0}\n.dai-fullscreen .dai-field>button[role=combobox]{width:100%!important;max-width:100%!important;min-width:0!important;min-height:32px!important;height:32px!important;padding:5px 8px!important;font-size:12px!important;line-height:1.3!important;box-sizing:border-box!important}\n.dai-fullscreen .DialogDropDown_CurrentDisplay{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px!important;line-height:1.3!important}\n.dai-fullscreen .dai-field>button[role=combobox] svg{width:14px;height:14px;flex-shrink:0}\n.dai-fullscreen input.DialogInput{font-size:12px!important;line-height:1.3!important;height:32px!important;min-height:32px!important;max-width:100%;box-sizing:border-box!important;padding:6px 8px!important}\n.dai-fullscreen .DialogInput_Wrapper{min-width:0;width:100%;margin:0}\n.dai-fullscreen .dai-muted{font-size:11px;line-height:1.35}\n.dai-connection-bar{display:flex;align-items:center;gap:8px;min-width:0}\n.dai-connection-bar>.dai-muted{flex:1;min-width:0;overflow-wrap:anywhere}\n.dai-root.dai-fullscreen .dai-connection-bar>.dai-button.DialogButton{width:140px!important;flex:none;font-size:11px!important}\n.dai-host-entry{display:grid;grid-template-columns:minmax(0,1fr) 100px;gap:6px;align-items:center}\n.dai-account-meta{display:flex;align-items:center;gap:8px;min-width:0}\n.dai-account-meta>.dai-account{flex:1;min-width:0;font-size:12px}\n.dai-account-actions{display:flex;gap:6px;flex-wrap:wrap}\n.dai-account-actions>.dai-button{flex:1;min-width:0}\n.dai-account-actions>.dai-login-url{width:100%;font-size:10px}\n@media(max-width:650px){.dai-root.dai-fullscreen{padding:8px;gap:5px}.dai-fullscreen .dai-settings-grid{grid-template-columns:minmax(0,1fr)}.dai-full-brand span{display:none}.dai-root.dai-fullscreen .dai-full-header>.dai-button.DialogButton{width:96px!important}.dai-fullscreen .dai-composer{grid-template-columns:minmax(0,1fr)}.dai-fullscreen .dai-compose-actions{justify-content:stretch}.dai-root.dai-fullscreen .dai-compose-actions>.dai-button.DialogButton{flex:1}}\n\n/* Scale reading text without enlarging navigation in the narrow Steam panel. */\n.dai-root .dai-message{font-size:calc(14px * var(--dai-text-scale,1))}\n.dai-root.dai-fullscreen .dai-message{font-size:calc(13px * var(--dai-text-scale,1))}\n.dai-root .dai-message small{font-size:calc(10px * var(--dai-text-scale,1))}\n.dai-root .dai-label,.dai-root .dai-muted{font-size:calc(12px * var(--dai-text-scale,1))}\n.dai-root.dai-fullscreen .dai-label,.dai-root.dai-fullscreen .dai-muted{font-size:calc(11px * var(--dai-text-scale,1))}\n.dai-root .dai-section h3{font-size:calc(14px * var(--dai-text-scale,1))}\n.dai-root input.DialogInput,.dai-root .DialogDropDown_CurrentDisplay{font-size:calc(12px * var(--dai-text-scale,1))!important;line-height:1.3!important}\n.dai-root input.DialogInput{min-height:calc(20px + 12px * var(--dai-text-scale,1))!important;height:auto!important}\n.dai-root .dai-field>button[role=combobox]{min-height:calc(20px + 12px * var(--dai-text-scale,1))!important;height:auto!important}\n.dai-scale-controls{display:flex;align-items:center;gap:6px;min-width:0}\n.dai-scale-value{flex:1;min-width:44px;text-align:center;font-size:calc(13px * var(--dai-text-scale,1));font-variant-numeric:tabular-nums}\n.dai-root .dai-scale-controls>.dai-button.DialogButton{width:52px!important;flex:none}\n.dai-root .dai-scale-controls>.dai-button.DialogButton:last-child{width:70px!important}\n\n/* Smaller text also frees vertical space for the conversation. Keep enlarged\n   text independent so navigation stays usable in the narrow Quick Access UI. */\n.dai-root{--dai-density:min(1,var(--dai-text-scale,1));gap:calc(8px * var(--dai-density))}\n.dai-root .dai-tabs{gap:calc(4px * var(--dai-density));padding-bottom:calc(7px * var(--dai-density))}\n.dai-root .dai-button.DialogButton{font-size:calc(13px * var(--dai-density))!important;min-height:calc(38px * var(--dai-density))!important;padding:calc(8px * var(--dai-density)) calc(6px * var(--dai-density))!important;gap:calc(6px * var(--dai-density))}\n.dai-root .dai-tab .dai-button.DialogButton{font-size:calc(12px * var(--dai-density))!important;padding:calc(8px * var(--dai-density)) calc(4px * var(--dai-density))!important}\n.dai-root .dai-viewbar>.dai-button.DialogButton{width:calc(126px * var(--dai-density))!important;min-height:calc(32px * var(--dai-density))!important;font-size:calc(11px * var(--dai-density))!important}\n.dai-root .dai-composer{gap:calc(8px * var(--dai-density));padding-top:calc(9px * var(--dai-density))}\n.dai-root .dai-message{padding:calc(10px * var(--dai-density));line-height:1.4}\n.dai-root .dai-message-list{gap:calc(9px * var(--dai-density))}\n.dai-root input.DialogInput{min-height:calc(32px * var(--dai-density))!important;padding:calc(6px * var(--dai-density)) calc(8px * var(--dai-density))!important}\n.dai-root.dai-fullscreen{gap:calc(6px * var(--dai-density));padding:calc(10px * var(--dai-density)) 16px}\n.dai-root.dai-fullscreen .dai-button.DialogButton{font-size:calc(12px * var(--dai-density))!important;min-height:calc(32px * var(--dai-density))!important;padding:calc(6px * var(--dai-density)) calc(8px * var(--dai-density))!important}\n.dai-root.dai-fullscreen .dai-tab .dai-button.DialogButton{min-height:calc(30px * var(--dai-density))!important}\n.dai-root.dai-fullscreen .dai-composer{gap:calc(6px * var(--dai-density));padding-top:calc(7px * var(--dai-density))}\n.dai-root.dai-fullscreen .dai-message{padding:calc(9px * var(--dai-density)) calc(12px * var(--dai-density))}\n.dai-root.dai-fullscreen .dai-message-list{gap:calc(7px * var(--dai-density))}\n.dai-root .dai-empty p{font-size:calc(13px * var(--dai-text-scale,1))}\n\n/* Keep the top and bottom chat controls shallow in both Decky views. */\n.dai-root .dai-message{font-size:calc(13px * var(--dai-text-scale,1))}\n.dai-root.dai-fullscreen .dai-message{font-size:calc(12px * var(--dai-text-scale,1))}\n.dai-root .dai-tabs{padding-bottom:calc(4px * var(--dai-density))}\n.dai-root .dai-tab .dai-button.DialogButton,\n.dai-root .dai-compose-actions>.dai-button.DialogButton,\n.dai-root.dai-fullscreen .dai-tab .dai-button.DialogButton,\n.dai-root.dai-fullscreen .dai-compose-actions>.dai-button.DialogButton{min-height:22px!important;padding:3px 5px!important;font-size:calc(11px * var(--dai-density))!important;line-height:1.2!important;gap:4px}\n.dai-root .dai-viewbar>.dai-button.DialogButton{min-height:22px!important;padding:3px 4px!important}\n.dai-root.dai-fullscreen .dai-full-header>.dai-button.DialogButton{min-height:22px!important;padding:3px 6px!important;font-size:calc(11px * var(--dai-density))!important}\n.dai-root .dai-compose-actions{gap:4px}\n.dai-root .dai-composer{gap:4px;padding-top:4px}\n.dai-root.dai-fullscreen .dai-composer{gap:4px;padding-top:4px}\n.dai-root .dai-composer input.DialogInput{min-height:24px!important;padding:4px 6px!important}\n\n/* Settings use four aligned cards: service and connection, then personal\n   preferences and account. Card rows share their height rather than drifting. */\n.dai-fullscreen .dai-settings-grid{grid-template-areas:\"model connection\" \"personal account\";gap:12px;align-items:stretch;width:100%}\n.dai-fullscreen .dai-settings-column{display:contents}\n.dai-fullscreen .dai-model-settings{grid-area:model}\n.dai-fullscreen .dai-connection-settings{grid-area:connection}\n.dai-fullscreen .dai-text-settings{grid-area:personal}\n.dai-fullscreen .dai-account-settings{grid-area:account}\n.dai-fullscreen .dai-section,.dai-fullscreen .dai-section:last-child{padding:12px;gap:10px;border-color:rgba(170,190,210,.16);background:#16212d;border-radius:7px}\n.dai-fullscreen .dai-section h3{padding-bottom:8px;border-bottom:1px solid var(--dai-line);font-size:12px;color:#dce8f3;letter-spacing:.15px}\n.dai-fullscreen .dai-model-fields{gap:10px 12px}\n.dai-fullscreen .dai-personal-fields{display:grid;grid-template-columns:1.15fr 1fr;gap:12px;align-items:start}\n.dai-fullscreen .dai-scale-controls{gap:4px;min-height:32px}\n.dai-root.dai-fullscreen .dai-scale-controls>.dai-button.DialogButton{width:36px!important;min-height:30px!important;padding:5px 4px!important}\n.dai-root.dai-fullscreen .dai-scale-controls>.dai-button.DialogButton:last-child{width:48px!important}\n.dai-fullscreen .dai-scale-value{min-width:30px;font-size:11px}\n.dai-fullscreen .dai-connection-bar{min-height:30px}\n.dai-fullscreen .dai-account-meta{min-height:32px;flex-wrap:wrap}\n.dai-fullscreen .dai-account-meta>.dai-account{font-size:11px}\n.dai-fullscreen .dai-account-actions{margin-top:auto}\n.dai-fullscreen .dai-field>button[role=combobox]{background:#223243!important;border-radius:4px!important}\n.dai-fullscreen .dai-settings input.DialogInput{background:#223243!important;border-radius:4px!important}\n@media(max-width:650px){.dai-fullscreen .dai-settings-grid{grid-template-columns:minmax(0,1fr);grid-template-areas:\"model\" \"connection\" \"personal\" \"account\"}.dai-fullscreen .dai-personal-fields{grid-template-columns:minmax(0,1fr)}}\n\n/* Fill Decky's actual content slot, including after reopening or resizing.\n   Its generated wrappers otherwise add 16px padding and a viewport clamp. */\ndiv:has(> div > .dai-root:not(.dai-fullscreen)){display:flex!important;flex-direction:column!important;height:100%!important;min-height:0!important;box-sizing:border-box!important}\ndiv:has(> div > .dai-root:not(.dai-fullscreen))>div:not(:has(>.dai-root)){flex-shrink:0}\ndiv:has(> .dai-root:not(.dai-fullscreen)){display:flex!important;flex-direction:column!important;flex:1!important;min-height:0!important;height:auto!important;padding-top:0!important;overflow:hidden}\n.dai-root:not(.dai-fullscreen){height:100%!important;max-height:none!important;min-height:0!important;flex:1;padding-bottom:4px}\n.dai-root:not(.dai-fullscreen)>.dai-page{flex:1;min-height:0}\n.dai-root:not(.dai-fullscreen) .dai-messages{flex:1;min-height:0}\n.dai-root:not(.dai-fullscreen) .dai-composer{margin-top:auto;flex-shrink:0}\n\n/* Decky's sticky title casts a shadow below its layout box. Keep tabs clear\n   of that overlay while the outer panel still fills the available height. */\n.dai-root:not(.dai-fullscreen){padding-top:16px}\n\n.dai-game-setting{display:flex;align-items:center;gap:8px;border-top:1px solid var(--dai-line);padding-top:8px;margin-top:2px}\n.dai-game-setting>.dai-muted{flex:1;min-width:0}\n.dai-root.dai-fullscreen .dai-game-setting>.dai-button.DialogButton{width:82px!important;flex:none}\n.dai-game-context h3{display:flex;align-items:center;gap:6px}\n\n/* Dictation has its own preview; only finalized speech enters the draft. */\n.dai-voice-preview{display:flex;align-items:flex-start;gap:7px;padding:7px 8px;background:rgba(211,55,65,.12);border:1px solid rgba(239,86,96,.45);border-radius:4px;flex-shrink:0;min-width:0;grid-column:1/-1}\n.dai-record-dot{width:7px;height:7px;flex:none;background:#ff5362;border-radius:50%;margin-top:3px;box-shadow:0 0 5px rgba(255,83,98,.45)}\n.dai-voice-preview>div{display:flex;flex-direction:column;gap:3px;min-width:0;flex:1}\n.dai-voice-preview strong{font-size:10px;color:#ff9ca4;line-height:1.2}\n.dai-voice-preview>div>span{font-size:calc(12px * var(--dai-text-scale,1));line-height:1.35;white-space:pre-wrap;overflow-wrap:anywhere;max-height:54px;overflow-y:auto;color:#f5e9eb}\n.dai-root .dai-button.DialogButton.dai-recording{background:#aa2635!important;color:#fff!important;box-shadow:inset 0 0 0 1px #ff7a86!important;opacity:1}\n.dai-root .dai-button.DialogButton.dai-recording:focus,.dai-root .dai-button.DialogButton.dai-recording.gpfocus{background:#cf3546!important;outline:2px solid #fff;outline-offset:-2px}\n\n.dai-game-check{flex:none;min-width:0}\n.dai-root .dai-game-check>.dai-button.DialogButton{width:62px!important;min-height:22px!important;padding:3px 4px!important;font-size:10px!important;gap:4px}\n.dai-check-box{display:inline-flex;align-items:center;justify-content:center;width:12px;height:12px;border:1px solid currentColor;border-radius:2px;font-size:11px;line-height:1;flex:none}\n.dai-game-check[aria-checked=true] .dai-check-box{background:#64b9ef;color:#122432;border-color:#64b9ef}\n\n.dai-message{position:relative}\n.dai-message-tools{position:absolute;top:3px;right:4px;opacity:0;pointer-events:none;transition:opacity .1s}\n.dai-message:hover .dai-message-tools,.dai-message:focus-within .dai-message-tools,.dai-message.dai-focused .dai-message-tools,.dai-message.gpfocus .dai-message-tools{opacity:1;pointer-events:auto}\n.dai-root .dai-message-tools .dai-button.DialogButton,.dai-root.dai-fullscreen .dai-message-tools .dai-button.DialogButton{width:auto!important;min-height:18px!important;padding:2px 5px!important;font-size:9px!important;gap:3px;background:#26394b}\n.dai-latest{flex:none;align-self:center;padding:3px 0}\n.dai-root .dai-latest .dai-button.DialogButton{width:auto!important;min-height:22px!important;padding:3px 8px!important;font-size:10px!important}\n.dai-queue-state{grid-column:1/-1}\n\n.dai-message-attachments{display:flex;flex-wrap:wrap;gap:6px;min-width:0;margin-top:6px}\n.dai-message-attachment{min-width:0;max-width:100%}\n.dai-root .dai-image-button.DialogButton{padding:0!important;min-height:0!important;width:auto!important;max-width:100%;background:transparent!important;overflow:hidden;border-radius:5px}\n.dai-image-button img{display:block;width:auto;max-width:100%;max-height:160px;object-fit:contain}\n.dai-fullscreen .dai-image-button img{max-height:240px}\n.dai-image-expanded{display:block;max-width:100%;max-height:65vh;object-fit:contain;margin:auto}\n\n.dai-queue-summary{grid-column:1/-1;min-width:0}\n.dai-root .dai-queue-summary .dai-button.DialogButton{min-height:20px!important;padding:2px 5px!important;font-size:10px!important}\n.dai-queue-item{display:flex;flex-direction:column;gap:5px;min-width:0}\n.dai-queue-item strong,.dai-queue-item small{overflow-wrap:anywhere}\n.dai-queue-text{white-space:pre-wrap;overflow-wrap:anywhere;font-size:calc(11px * var(--dai-text-scale,1));line-height:1.4}\n\n.dai-root .dai-queue-item>strong{font-size:12px;line-height:1.3}\n.dai-root .dai-queue-item>small{font-size:10px;line-height:1.3}\n.dai-root .dai-queue-item .dai-button.DialogButton{min-height:24px!important;padding:3px 5px!important;font-size:11px!important}\n.dai-running-count{color:#e4c56e;white-space:nowrap}.dai-history-item.running .dai-button>span{display:flex;align-items:center;gap:6px}.dai-history-item.running .dai-dot{animation:dai-pulse 1.4s ease-in-out infinite}@keyframes dai-pulse{50%{opacity:.35}}\n.dai-message.tool{background:rgba(255,255,255,.025);padding:6px 8px}.dai-message.tool pre{margin:0;font:11px/1.4 monospace;white-space:pre-wrap;overflow-wrap:anywhere;color:var(--dai-muted)}.dai-approvals{display:flex;flex-direction:column;gap:6px;flex-shrink:0}.dai-approval{display:flex;flex-direction:column;gap:5px;padding:8px;background:#4a3d1f;border-radius:3px;font-size:12px}.dai-quick{display:grid;grid-template-columns:1fr 1fr;gap:5px}.dai-check.ok{color:#8fd1ac}.dai-check.bad{color:#f0a58c}\n.dai-textarea{width:100%;min-height:220px;resize:vertical;box-sizing:border-box;background:#0e141b;color:#e5edf4;border:1px solid var(--dai-line);border-radius:3px;padding:8px;font:12px/1.5 monospace}.dai-textarea-small{min-height:90px}.dai-textarea:focus{outline:2px solid #fff}\n.dai-snippet{margin:0;padding:6px;background:#0e141b;border-radius:3px;font:11px/1.4 monospace;white-space:pre-wrap;user-select:text;overflow-wrap:anywhere}\n\n/* ===== Appearance layer: colour themes, density, message style, layouts =====\n   Tokens (--t-*) are set per data-theme on .dai-root. Rules below are scoped\n   with [data-theme] so they win over the structural rules above without\n   changing them. */\n.dai-root,.dai-root[data-theme=ocean]{--t-bg:#101923;--t-card:#16212d;--t-input:#223243;--t-btn:rgba(255,255,255,.07);--t-accent:#1a77b9;--t-accent-text:#fff;--t-tab-on:#34495d;--t-tab-on-text:#fff;--t-user:#1d3347;--t-assistant:#17222e;--t-text:#f0f4f8;--t-muted:#aab6c3;--t-line:rgba(255,255,255,.12);--t-focus-bg:#dce8f1;--t-focus-text:#152638;--t-focus-ring:#fff;--t-warn:#4a3d1f;--t-warn-line:#e4c56e;--t-bad:#502f36;--t-ok:#69c49a;--t-working:#e4c56e;--t-offline:#e59980;--t-notice:#a9cddb;--t-thumb:#3b4d5f;--dai-radius:10px;--dai-radius-sm:7px}\n.dai-root[data-theme=graphite]{--t-bg:#15171a;--t-card:#1e2125;--t-input:#2a2e33;--t-btn:rgba(255,255,255,.07);--t-accent:#8aa0b8;--t-accent-text:#10151a;--t-tab-on:#363c43;--t-tab-on-text:#fff;--t-user:#2b3138;--t-assistant:#1b1e22;--t-text:#ececec;--t-muted:#a2a9b0;--t-line:rgba(255,255,255,.11);--t-focus-bg:#ececec;--t-focus-text:#15171a;--t-focus-ring:#8aa0b8;--t-warn:#3d3a2c;--t-bad:#46302f;--t-notice:#b7c4d1;--t-thumb:#444a51}\n.dai-root[data-theme=violet]{--t-bg:#14111f;--t-card:#1d1830;--t-input:#2a2344;--t-btn:rgba(200,180,255,.09);--t-accent:#8b6cf0;--t-accent-text:#fff;--t-tab-on:#3a3060;--t-tab-on-text:#fff;--t-user:#2c2350;--t-assistant:#1a1629;--t-text:#efeaff;--t-muted:#b2a8d0;--t-line:rgba(190,170,255,.16);--t-focus-bg:#e7deff;--t-focus-text:#241a4a;--t-focus-ring:#fff;--t-warn:#44381f;--t-bad:#4d2a3a;--t-notice:#c9bcf5;--t-thumb:#463b72}\n.dai-root[data-theme=forest]{--t-bg:#0f1a15;--t-card:#15241c;--t-input:#1f3328;--t-btn:rgba(160,255,200,.07);--t-accent:#2fa66a;--t-accent-text:#06150d;--t-tab-on:#25433a;--t-tab-on-text:#fff;--t-user:#1c3a2c;--t-assistant:#14231b;--t-text:#e9f4ee;--t-muted:#9fb8aa;--t-line:rgba(160,230,190,.15);--t-focus-bg:#dcf2e5;--t-focus-text:#0d2a1b;--t-focus-ring:#fff;--t-warn:#423c1d;--t-bad:#4a2f2f;--t-notice:#a9dcc0;--t-thumb:#2f4a3b}\n.dai-root[data-theme=amber]{--t-bg:#1a140c;--t-card:#251c10;--t-input:#33271a;--t-btn:rgba(255,220,160,.07);--t-accent:#d99a2b;--t-accent-text:#1c1204;--t-tab-on:#4a3a1c;--t-tab-on-text:#fff;--t-user:#3a2d14;--t-assistant:#221a0f;--t-text:#f6eee0;--t-muted:#c2b394;--t-line:rgba(255,215,150,.15);--t-focus-bg:#f7e7c6;--t-focus-text:#2b1d06;--t-focus-ring:#fff;--t-warn:#4a3a14;--t-bad:#4e2f2a;--t-notice:#e0c48a;--t-thumb:#54421f}\n.dai-root[data-theme=rose]{--t-bg:#1c1015;--t-card:#281820;--t-input:#38222d;--t-btn:rgba(255,190,210,.07);--t-accent:#e0577d;--t-accent-text:#fff;--t-tab-on:#50263a;--t-tab-on-text:#fff;--t-user:#43202f;--t-assistant:#25151c;--t-text:#fbeaf0;--t-muted:#cfa9b8;--t-line:rgba(255,170,200,.15);--t-focus-bg:#fbdbe6;--t-focus-text:#40101f;--t-focus-ring:#fff;--t-warn:#4a3a1f;--t-bad:#5a2430;--t-notice:#f0b6c9;--t-thumb:#5a3041}\n.dai-root[data-theme=light]{--t-bg:#f3f6f9;--t-card:#fff;--t-input:#e9eff5;--t-btn:rgba(20,60,100,.08);--t-accent:#1a77b9;--t-accent-text:#fff;--t-tab-on:#dbe8f3;--t-tab-on-text:#10304a;--t-user:#dbeaf7;--t-assistant:#fff;--t-text:#1b2733;--t-muted:#5a6b7b;--t-line:rgba(20,40,60,.14);--t-focus-bg:#1a77b9;--t-focus-text:#fff;--t-focus-ring:#0d4f7d;--t-warn:#fff1cf;--t-warn-line:#c98a12;--t-bad:#fde3e3;--t-ok:#1f8a5b;--t-working:#b7791f;--t-offline:#c2543a;--t-notice:#1c6aa3;--t-thumb:#b9c6d3}\n.dai-root[data-theme]{--dai-line:var(--t-line);--dai-muted:var(--t-muted);background:var(--t-bg)!important;color:var(--t-text);border-radius:var(--dai-radius)}\n.dai-root[data-theme].dai-fullscreen{border-radius:0}\n.dai-root[data-theme] h3,.dai-root[data-theme] .dai-section h3,.dai-root[data-theme] .dai-empty h3,.dai-root[data-theme].dai-fullscreen .dai-section h3{color:var(--t-text)}\n/* Buttons */\n.dai-root[data-theme] .dai-button.DialogButton{background:var(--t-btn)!important;color:var(--t-text)!important;border-radius:var(--dai-radius-sm)!important;transition:background .12s}\n.dai-root[data-theme] .dai-button.DialogButton:disabled{opacity:.45}\n.dai-root[data-theme] .dai-image-button.DialogButton{background:transparent!important}\n.dai-root[data-theme] .dai-tab .dai-button.DialogButton{background:transparent!important;color:var(--t-muted)!important;border-radius:999px!important}\n.dai-root[data-theme] .dai-tab.selected .dai-button.DialogButton{background:var(--t-tab-on)!important;color:var(--t-tab-on-text)!important;font-weight:650}\n.dai-root[data-theme] .dai-button.dai-primary.DialogButton,.dai-root[data-theme] .dai-button.DialogButton.dai-selected{background:var(--t-accent)!important;color:var(--t-accent-text)!important}\n.dai-root[data-theme] .dai-button.DialogButton.dai-recording{background:#aa2635!important;color:#fff!important}\n.dai-root[data-theme] .dai-button.DialogButton.gpfocus,.dai-root[data-theme] .dai-button.DialogButton:focus,.dai-root[data-theme] .dai-focused{background:var(--t-focus-bg)!important;color:var(--t-focus-text)!important;outline:2px solid var(--t-focus-ring)!important;outline-offset:-2px}\n/* Tab bar as a pill; optional bottom placement (thumb-friendly) */\n.dai-root[data-theme] .dai-tabs{background:var(--t-card);border:1px solid var(--t-line);border-radius:999px;padding:3px;gap:3px}\n.dai-root[data-layout=bottom] .dai-tabs{order:50}\n.dai-root[data-layout=bottom] .dai-page{order:10}\n/* Status */\n.dai-root[data-theme] .dai-dot{background:var(--t-ok)}\n.dai-root[data-theme] .dai-dot.working{background:var(--t-working)}\n.dai-root[data-theme] .dai-dot.offline{background:var(--t-offline)}\n.dai-root[data-theme] .dai-running-count{color:var(--t-working)}\n.dai-root[data-theme] .dai-notice{color:var(--t-notice)}\n.dai-root[data-theme] .dai-banner{background:var(--t-bad);border-radius:var(--dai-radius-sm)}\n.dai-root[data-theme] .dai-approval{background:var(--t-warn);border-left:3px solid var(--t-warn-line,#e4c56e);border-radius:var(--dai-radius-sm)}\n.dai-root[data-theme] .dai-check.ok{color:var(--t-ok)}\n/* Cards for settings blocks and the composer */\n.dai-root[data-theme] .dai-section,.dai-root[data-theme] .dai-section:last-child,.dai-root[data-theme].dai-fullscreen .dai-section,.dai-root[data-theme].dai-fullscreen .dai-section:last-child{background:var(--t-card);border:1px solid var(--t-line);border-radius:var(--dai-radius);padding:12px}\n.dai-root[data-theme] .dai-composer,.dai-root[data-theme].dai-fullscreen .dai-composer{background:var(--t-card);border:1px solid var(--t-line);border-radius:var(--dai-radius);padding:8px}\n.dai-root[data-theme] input.DialogInput,.dai-root[data-theme] .dai-field>button[role=combobox],.dai-root[data-theme].dai-fullscreen .dai-settings input.DialogInput,.dai-root[data-theme].dai-fullscreen .dai-field>button[role=combobox]{background:var(--t-input)!important;color:var(--t-text)!important;border-radius:var(--dai-radius-sm)!important}\n.dai-root[data-theme] .dai-textarea,.dai-root[data-theme] .dai-snippet{background:var(--t-input);color:var(--t-text);border-color:var(--t-line)}\n.dai-root[data-theme] .dai-game-check[aria-checked=true] .dai-check-box{background:var(--t-accent);border-color:var(--t-accent);color:var(--t-accent-text)}\n.dai-root[data-theme] .dai-history-item.selected{border-left-color:var(--t-accent)}\n.dai-root[data-theme] .dai-scroll,.dai-root[data-theme] .dai-messages{scrollbar-color:var(--t-thumb) transparent}\n/* Messages: three styles */\n.dai-root[data-theme] .dai-message{background:var(--t-assistant);color:var(--t-text);border-radius:var(--dai-radius)}\n.dai-root[data-theme] .dai-message.user{background:var(--t-user)}\n.dai-root[data-theme] .dai-message.tool{background:transparent;border:1px dashed var(--t-line)}\n.dai-root[data-theme] .dai-message small{color:var(--t-muted);letter-spacing:.3px;text-transform:uppercase}\n.dai-root[data-theme] .dai-message.user small{color:var(--t-accent)}\n.dai-root[data-theme][data-bubbles=bubbles] .dai-message.user{align-self:flex-end;max-width:92%;border-bottom-right-radius:3px}\n.dai-root[data-theme][data-bubbles=bubbles] .dai-message.assistant{align-self:flex-start;max-width:97%;border-bottom-left-radius:3px;border:1px solid var(--t-line)}\n.dai-root[data-theme][data-bubbles=flat] .dai-message,.dai-root[data-theme][data-bubbles=flat] .dai-message.user{background:transparent;border-radius:0;border-bottom:1px solid var(--t-line);padding-left:2px;padding-right:2px}\n.dai-root[data-theme][data-bubbles=cards] .dai-message{border-left:3px solid var(--t-line)}\n.dai-root[data-theme][data-bubbles=cards] .dai-message.user{border-left-color:var(--t-accent)}\n.dai-root[data-theme][data-bubbles=cards] .dai-message.assistant{border-left-color:var(--t-working)}\n/* Density */\n.dai-root[data-density=compact] .dai-message{padding:6px 9px;line-height:1.35}\n.dai-root[data-density=compact] .dai-message-list,.dai-root[data-density=compact] .dai-messages{gap:5px}\n.dai-root[data-density=roomy] .dai-message{padding:14px 16px;line-height:1.6}\n.dai-root[data-density=roomy] .dai-message-list,.dai-root[data-density=roomy] .dai-messages{gap:14px}\n.dai-root[data-density=roomy] .dai-section{padding:16px}\n/* Quick toolbar above the conversation */\n.dai-toolbar{display:flex;gap:6px;flex-shrink:0}\n.dai-root .dai-toolbar>.dai-button.DialogButton{flex:1 1 0;min-height:36px!important;padding:4px 2px!important;flex-direction:column;gap:1px!important;font-size:10px!important;line-height:1.1!important;border-radius:var(--dai-radius-sm)!important}\n.dai-toolbar .dai-button svg{font-size:13px}\n.dai-toolbar .dai-button span{max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}\n.dai-root.dai-fullscreen .dai-toolbar>.dai-button.DialogButton{flex-direction:row;gap:6px!important;min-height:26px!important;font-size:11px!important}\n/* Two columns: chat list beside the conversation (full screen only) */\n.dai-chat-layout{display:flex;flex-direction:column;flex:1;min-height:0;min-width:0}\n.dai-chat-main{display:flex;flex-direction:column;flex:1;min-height:0;min-width:0;gap:inherit}\n.dai-root[data-layout=split].dai-fullscreen .dai-chat-layout{flex-direction:row;gap:10px}\n.dai-split-side{flex:none;width:230px;min-height:0;overflow-y:auto;border:1px solid var(--t-line);border-radius:var(--dai-radius);background:var(--t-card);padding:8px}\n.dai-split-side .dai-history-item .dai-button{padding:7px 9px!important;min-height:30px!important}\n.dai-split-side .dai-history-item span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:190px;display:flex;align-items:center;gap:6px}\n/* Appearance settings */\n.dai-swatches{display:flex;flex-wrap:wrap;gap:6px}\n.dai-root .dai-swatches>.dai-button.DialogButton{width:auto!important;flex:1 1 28%;min-width:78px;min-height:28px!important;font-size:11px!important;gap:6px!important}\n.dai-swatch-dot{width:12px;height:12px;border-radius:50%;flex:none;border:1px solid rgba(128,128,128,.6)}\n.dai-segmented{display:flex;gap:4px}\n.dai-root .dai-segmented>.dai-button.DialogButton{flex:1;min-height:28px!important;font-size:11px!important}\n/* Keep \"Отправить\" on one line in the narrow panel: give the main action more room. */\n.dai-root:not(.dai-fullscreen) .dai-compose-actions>.dai-button.dai-primary.DialogButton{flex:1.9;white-space:nowrap!important}\n.dai-root:not(.dai-fullscreen) .dai-compose-actions>.dai-button.DialogButton{padding-left:3px!important;padding-right:3px!important;white-space:nowrap!important}\n\n/* Keep long permission requests inside the available chat area. */\n.dai-chat-main.has-approvals .dai-messages{min-height:0}\n.dai-approvals{flex:0 1 auto;min-height:48px;max-height:45%;overflow-y:auto;overflow-x:hidden;scrollbar-width:thin}\n.dai-approval{flex-shrink:0;overflow-wrap:anywhere}\n";

const key = (thread) => 'codex-game-draft:' + (thread || 'new');
function createDraftStore(storage) {
    const listeners = new Set();
    return {
        read: (thread) => storage.getItem(key(thread)) || '',
        write(thread, text) { storage.setItem(key(thread), text); for (const listener of listeners)
            listener(thread, text); },
        subscribe(listener) { listeners.add(listener); return () => { listeners.delete(listener); }; }
    };
}
// Both mounted views share this gate: a poll from either must not win over a
// newer navigation/action in the other, including a poll started mid-action.
function createViewGate() {
    let revision = 0;
    let active = false;
    const listeners = new Set();
    return {
        token: () => revision,
        busy: () => active,
        current: (token) => !active && token === revision,
        begin() { if (active)
            return false; active = true; revision++; for (const listener of listeners)
            listener(true); return true; },
        end() { active = false; revision++; for (const listener of listeners)
            listener(false); },
        subscribe(listener) { listeners.add(listener); listener(active); return () => { listeners.delete(listener); }; }
    };
}

function queueCounts(jobs, threadId) {
    return { waiting: jobs.filter(job => job.status === 'queued').length, current: jobs.filter(job => job.threadId === threadId && job.status === 'queued').length, other: jobs.filter(job => job.threadId !== threadId && job.status === 'queued').length };
}
function queueStatus(job, now = Date.now()) {
    const began = job.startedAt ?? job.createdAt;
    if (job.status === 'sending')
        return began && now - began * 1000 > 15 * 60 * 1000 ? 'Долго выполняется · проверьте чат' : 'Выполняется';
    return { queued: 'Ожидает отправки', recovering: 'Проверяется на сервере', error: 'Ошибка' }[job.status] || job.status;
}
function chatFailures(jobs, threadId, host = "") {
    return jobs.filter(job => job.status === 'error' && job.threadId === threadId && (job.host || '') === host);
}

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

const defaultQuickActions = [["Продолжай", "Продолжай"], ["Покажи diff", "Покажи diff последних изменений"], ["Запусти тесты", "Запусти тесты и покажи результат"], ["Объясни ошибку", "Объясни последнюю ошибку и предложи исправление"]];
// One phrase per line: "Label | text to send". Without "|" the line is both label and text.
function parseQuickActions(source) {
    if (source === null)
        return defaultQuickActions;
    const result = [];
    for (const line of source.split("\n")) {
        const [label, ...rest] = line.split("|");
        const name = label.trim(), text = (rest.length ? rest.join("|") : label).trim();
        if (name && text)
            result.push([name.slice(0, 24), text.slice(0, 2000)]);
        if (result.length === 8)
            break;
    }
    return result.length ? result : defaultQuickActions;
}

const themes = [
    { id: "ocean", name: "Океан", swatch: "#1a77b9" },
    { id: "graphite", name: "Графит", swatch: "#9aa7b4" },
    { id: "violet", name: "Фиалка", swatch: "#8b6cf0" },
    { id: "forest", name: "Лес", swatch: "#2fa66a" },
    { id: "amber", name: "Янтарь", swatch: "#d99a2b" },
    { id: "rose", name: "Роза", swatch: "#e0577d" },
    { id: "light", name: "Светлая", swatch: "#f2f5f8" },
];
const densities = [{ id: "compact", name: "Компактно" }, { id: "normal", name: "Обычно" }, { id: "roomy", name: "Просторно" }];
const bubbleStyles = [{ id: "bubbles", name: "Пузыри" }, { id: "flat", name: "Строки" }, { id: "cards", name: "Карточки" }];
const layouts = [{ id: "classic", name: "Вкладки сверху" }, { id: "bottom", name: "Вкладки снизу" }, { id: "split", name: "Две колонки" }];
const defaultAppearance = { theme: "ocean", density: "normal", bubbles: "bubbles", layout: "classic" };
const appearanceKey = "deck-ai-appearance";
const allowed = { theme: themes.map(t => t.id), density: densities.map(d => d.id), bubbles: bubbleStyles.map(b => b.id), layout: layouts.map(l => l.id) };
// Unknown or damaged values fall back to the defaults, field by field.
function readAppearance(raw) {
    let value = {};
    try {
        const parsed = JSON.parse(raw || "{}");
        if (parsed && typeof parsed === "object")
            value = parsed;
    }
    catch { }
    const result = { ...defaultAppearance };
    for (const key of Object.keys(allowed)) {
        const candidate = value[key];
        if (typeof candidate === "string" && allowed[key].includes(candidate))
            result[key] = candidate;
    }
    return result;
}
function withChoice(current, key, choice) {
    return allowed[key].includes(choice) ? { ...current, [key]: choice } : current;
}
// Two-column layout only makes sense where there is room for it.
function effectiveLayout(layout, fullscreen) { return layout === "split" && !fullscreen ? "classic" : layout; }

const DRAG_THRESHOLD = 6;
function scrollableFrom(start, canScroll, root) {
    for (let el = start; el; el = el.parentElement) {
        if (canScroll(el))
            return el;
        if (el === root)
            return null;
    }
    return null;
}
function dragTop(box, startTop, startY, y) {
    return Math.max(0, Math.min(box.scrollHeight - box.clientHeight, startTop + (startY - y)));
}
// Pixels per frame to keep scrolling after the finger lifts (simple momentum).
function decay(velocity) { const next = velocity * 0.94; return Math.abs(next) < 0.4 ? 0 : next; }
function attachTouchScroll(root, canScroll, frame = fn => setTimeout(fn, 16)) {
    let box = null, startY = 0, startTop = 0, dragging = false, lastY = 0, lastTime = 0, velocity = 0, alive = true;
    const start = event => {
        const touch = event.touches?.[0];
        box = touch && event.touches.length === 1 ? scrollableFrom(event.target, canScroll, root) : null;
        dragging = false;
        velocity = 0;
        if (box && touch) {
            startY = lastY = touch.clientY;
            startTop = box.scrollTop;
            lastTime = Date.now();
        }
    };
    const move = event => {
        const touch = event.touches?.[0];
        if (!box || !touch)
            return;
        if (!dragging && Math.abs(startY - touch.clientY) < DRAG_THRESHOLD)
            return;
        dragging = true;
        const now = Date.now();
        velocity = (lastY - touch.clientY) / Math.max(1, now - lastTime) * 16;
        lastY = touch.clientY;
        lastTime = now;
        box.scrollTop = dragTop(box, startTop, startY, touch.clientY);
        if (event.cancelable)
            event.preventDefault(); // stop the native pan so we do not scroll twice
    };
    const end = () => {
        const target = box;
        let speed = dragging ? velocity : 0;
        box = null;
        dragging = false;
        const glide = () => {
            if (!alive || !target || !speed)
                return;
            const before = target.scrollTop;
            target.scrollTop = Math.max(0, Math.min(target.scrollHeight - target.clientHeight, before + speed));
            speed = target.scrollTop === before ? 0 : decay(speed);
            if (speed)
                frame(glide);
        };
        glide();
    };
    root.addEventListener("touchstart", start, { passive: true });
    root.addEventListener("touchmove", move, { passive: false });
    root.addEventListener("touchend", end, { passive: true });
    root.addEventListener("touchcancel", end, { passive: true });
    return () => { alive = false; root.removeEventListener("touchstart", start); root.removeEventListener("touchmove", move); root.removeEventListener("touchend", end); root.removeEventListener("touchcancel", end); };
}

function joinPath(folder, name) { return folder.replace(/\/+$/, "") + "/" + name.replace(/\/$/, ""); }
function parentPath(path) { const trimmed = path.replace(/\/+$/, ""); const cut = trimmed.lastIndexOf("/"); return cut <= 0 ? "/" : trimmed.slice(0, cut); }
function isFolder(entry) { return entry.endsWith("/"); }
function sortEntries(entries) { return [...entries].sort((a, b) => Number(isFolder(b)) - Number(isFolder(a)) || a.localeCompare(b)); }

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
const olderMessages = callable("older_messages");
const pollEvents = callable("poll_events");
const approve = callable("approve");
const diagnose = callable("diagnose");
const watchHosts = callable("watch");
const setReadOnly = callable("read_only");
const queueFront = callable("queue_front");
const queueRemove = callable("queue_remove");
const fileList = callable("file_list");
const fileRead = callable("file_read");
const fileWrite = callable("file_write");
const shareStatus = callable("share_status");
const shareAddKey = callable("share_add_key");
const customSave = callable("custom_save");
const customRemove = callable("custom_remove");
const unloadModels = callable("unload_models");
const setProviderKey = callable("set_provider_key");
const GameScroll = DFL.ScrollPanel;
const providerNames = { codex: "Codex · ChatGPT", claude: "Claude Code · свой доступ", deepseek: "DeepSeek · OpenRouter", tokenharbor: "DeepSeek · TokenHarbor" };
const drafts = createDraftStore(localStorage);
const viewGate = createViewGate();
function Action({ children, onClick, disabled = false, primary = false, recording = false, selected }) {
    return SP_JSX.jsx(DFL.DialogButton, { className: "dai-button" + (primary ? " dai-primary" : "") + (recording ? " dai-recording" : "") + (selected ? " dai-selected" : ""), "aria-pressed": selected, disabled: disabled, onClick: onClick, children: children });
}
function Segmented({ label, value, options, onChange }) {
    return SP_JSX.jsxs("div", { className: "dai-field", children: [SP_JSX.jsx("span", { className: "dai-label", children: label }), SP_JSX.jsx(DFL.Focusable, { className: "dai-segmented", "flow-children": "horizontal", children: options.map(option => SP_JSX.jsx(Action, { selected: value === option.id, onClick: () => onChange(option.id), children: option.name }, option.id)) })] });
}
function MessageAttachments({ items }) {
    return SP_JSX.jsx("div", { className: "dai-message-attachments", children: items.map(item => SP_JSX.jsx("div", { className: "dai-message-attachment", children: item.preview ? SP_JSX.jsx(DFL.DialogButton, { className: "dai-image-button", onClick: () => DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: item.name.length > 48 ? item.name.slice(0, 45) + "…" : item.name, strOKButtonText: "\u0417\u0430\u043A\u0440\u044B\u0442\u044C", bAlertDialog: true, children: SP_JSX.jsx("img", { className: "dai-image-expanded", style: { display: "block", maxWidth: "100%", maxHeight: "55vh", width: "auto", height: "auto", objectFit: "contain", margin: "auto" }, src: item.preview, alt: item.name }) })), children: SP_JSX.jsx("img", { src: item.preview, alt: item.name }) }) : SP_JSX.jsxs("span", { className: "dai-muted", children: ["\uD83D\uDCCE ", item.name, " \u00B7 ", item.kind === "image" ? "изображение недоступно" : "файл"] }) }, item.id)) });
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
const historySnapshots = new Map();
const historyKey = (s) => JSON.stringify([s.provider, s.remoteHost || "", s.threadId]);
const session = { snapshot: null, attachments: new Map(), voiceText: "", voiceError: "", discardedVoice: localStorage.getItem("deck-ai-discarded-voice") || "", finishedVoice: "", dictation: restoreDictation(localStorage.getItem(dictationKey)) };
const attachmentListeners = new Set();
function publishAttachments(thread, items) {
    if (items.length)
        session.attachments.set(thread, items);
    else
        session.attachments.delete(thread);
    for (const listener of attachmentListeners)
        listener(thread, items);
}
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
const appearanceListeners = new Set();
function useAppearance() {
    const [appearance, setAppearance] = SP_REACT.useState(() => readAppearance(localStorage.getItem(appearanceKey)));
    SP_REACT.useEffect(() => { appearanceListeners.add(setAppearance); return () => { appearanceListeners.delete(setAppearance); }; }, []);
    return [appearance, (key, choice) => {
            const next = withChoice(readAppearance(localStorage.getItem(appearanceKey)), key, choice);
            localStorage.setItem(appearanceKey, JSON.stringify(next));
            appearanceListeners.forEach(listener => listener(next));
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
let panelMounted = 0;
const flag = (key, fallback) => { const value = localStorage.getItem(key); return value === null ? fallback : value === "on"; };
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
    const [appearance, setAppearanceChoice] = useAppearance();
    const layout = effectiveLayout(appearance.layout, fullscreen);
    const [gameContextEnabled, toggleGameContext] = useGameContextEnabled();
    const [data, setData] = SP_REACT.useState(session.snapshot);
    const [tab, setTab] = SP_REACT.useState(initialTab);
    SP_REACT.useEffect(() => {
        if (!fullscreen)
            return;
        const change = (next) => { setTab(next); setMediaOpen(false); setQueueOpen(false); };
        fullscreenViews.add(change);
        return () => { fullscreenViews.delete(change); };
    }, [fullscreen]);
    const [draft, setDraft] = SP_REACT.useState(() => drafts.read(session.snapshot?.threadId));
    const draftId = SP_REACT.useRef(session.snapshot?.threadId || "");
    const [busy, setBusy] = SP_REACT.useState(false);
    SP_REACT.useEffect(() => viewGate.subscribe(setBusy), []);
    const [voiceStarting, setVoiceStarting] = SP_REACT.useState(false);
    const [voicePolling, setVoicePolling] = SP_REACT.useState(false);
    const actionLock = SP_REACT.useRef(false);
    const [error, setError] = SP_REACT.useState("");
    const [connectionError, setConnectionError] = SP_REACT.useState("");
    const [notice, setNotice] = SP_REACT.useState("");
    const [showLatest, setShowLatest] = SP_REACT.useState(false);
    SP_REACT.useEffect(() => { if (!notice)
        return; const timer = setTimeout(() => setNotice(""), 4000); return () => clearTimeout(timer); }, [notice]);
    const [lang, setLang] = SP_REACT.useState(() => localStorage.getItem("codex-game-voice") || "ru");
    const [mediaOpen, setMediaOpen] = SP_REACT.useState(false);
    const [queueOpen, setQueueOpen] = SP_REACT.useState(false);
    const [expandedJob, setExpandedJob] = SP_REACT.useState("");
    const [images, setImagesState] = SP_REACT.useState(() => session.attachments.get(draftId.current) || []);
    const setImages = (update) => {
        const owner = draftId.current, old = session.attachments.get(owner) || [];
        publishAttachments(owner, typeof update === "function" ? update(old) : update);
    };
    SP_REACT.useEffect(() => {
        const unsubscribe = drafts.subscribe((owner, text) => { if (owner === draftId.current)
            setDraft(text); });
        const receive = (owner, items) => { if (owner === draftId.current)
            setImagesState(items); };
        attachmentListeners.add(receive);
        return () => { unsubscribe(); attachmentListeners.delete(receive); };
    }, []);
    const [shot, setShot] = SP_REACT.useState("");
    const [video, setVideo] = SP_REACT.useState("");
    const [key, setKey] = SP_REACT.useState("");
    const [host, setHost] = SP_REACT.useState("");
    const [loginUrl, setLoginUrl] = SP_REACT.useState("");
    const [historyQuery, setHistoryQuery] = SP_REACT.useState("");
    const [notify, setNotify] = SP_REACT.useState(() => flag("deck-ai-notify", true));
    const [autoSend, setAutoSend] = SP_REACT.useState(() => flag("deck-ai-auto-send", false));
    const [countdown, setCountdown] = SP_REACT.useState(null);
    const pendingAuto = SP_REACT.useRef(false);
    const [quickOpen, setQuickOpen] = SP_REACT.useState(false);
    const [quickSource, setQuickSource] = SP_REACT.useState(() => localStorage.getItem("deck-ai-quick"));
    const quickActions = parseQuickActions(quickSource);
    const autoSendRef = SP_REACT.useRef(autoSend);
    autoSendRef.current = autoSend;
    const [confirmApproval, setConfirmApproval] = SP_REACT.useState("");
    const [filesOpen, setFilesOpen] = SP_REACT.useState(false);
    const [folder, setFolder] = SP_REACT.useState("~");
    const [entries, setEntries] = SP_REACT.useState([]);
    const [file, setFile] = SP_REACT.useState(null);
    const [fileText, setFileText] = SP_REACT.useState("");
    const [speaking, setSpeaking] = SP_REACT.useState("");
    const touchAnchor = SP_REACT.useRef(null);
    SP_REACT.useEffect(() => {
        const root = touchAnchor.current?.closest(".dai-root");
        const view = root?.ownerDocument.defaultView;
        if (!root || !view)
            return;
        return attachTouchScroll(root, (el) => { const node = el; const overflow = view.getComputedStyle(node).overflowY; return (overflow === "auto" || overflow === "scroll") && node.scrollHeight > node.clientHeight; }, fn => { view.requestAnimationFrame(fn); });
    }, []);
    const [share, setShare] = SP_REACT.useState(null);
    const [shareKey, setShareKey] = SP_REACT.useState("");
    const [checks, setChecks] = SP_REACT.useState(null);
    const [openTool, setOpenTool] = SP_REACT.useState("");
    SP_REACT.useEffect(() => { panelMounted++; return () => { panelMounted--; }; }, []);
    const lastVoice = SP_REACT.useRef(session.voiceText);
    const lastVoiceError = SP_REACT.useRef(session.voiceError);
    const inFlight = SP_REACT.useRef(false);
    const mounted = SP_REACT.useRef(true);
    const queueRef = SP_REACT.useRef(null);
    SP_REACT.useEffect(() => { if (queueOpen)
        requestAnimationFrame(() => { const el = queueRef.current; if (el) {
            el.scrollTop = 0;
            el.querySelector("button")?.focus();
        } }); }, [queueOpen]);
    const chatRef = SP_REACT.useRef(null);
    const followTail = SP_REACT.useRef(true);
    const accept = SP_REACT.useCallback((incoming) => {
        setVoicePolling(["recording", "stopping", "processing"].includes(incoming.voiceState));
        const next = incoming.voiceId === session.finishedVoice && incoming.voiceText ? { ...incoming, voiceState: "done" } : incoming;
        // Change the draft and its storage key together; polling must never copy a
        // draft into a different chat when the selected conversation changes.
        if (next.threadId !== draftId.current) {
            draftId.current = next.threadId;
            setDraft(drafts.read(next.threadId));
            setImagesState(session.attachments.get(next.threadId) || []);
            followTail.current = true;
            setShowLatest(false);
        }
        historySnapshots.set(historyKey(next), next);
        while (historySnapshots.size > 12)
            historySnapshots.delete(historySnapshots.keys().next().value);
        session.snapshot = next;
        setData(next);
        if (next.voiceId && ["recording", "stopping", "processing"].includes(next.voiceState)) {
            session.dictation = bindDictation(session.dictation, next.voiceId, next.threadId, drafts.read(next.threadId));
            localStorage.setItem(dictationKey, JSON.stringify(session.dictation));
        }
        if (next.voiceId && next.voiceId !== session.discardedVoice && next.voiceText && next.voiceState === "done") {
            const id = next.voiceId;
            const owner = session.dictation?.id === id ? session.dictation.thread : next.threadId;
            const update = updateDictation(session.dictation, id, owner, next.voiceText, drafts.read(owner));
            session.dictation = update.session;
            localStorage.setItem(dictationKey, JSON.stringify(session.dictation));
            if (update.value !== null) {
                drafts.write(owner, update.value);
                if (owner === draftId.current)
                    setDraft(update.value);
                if (autoSendRef.current && owner === draftId.current) {
                    pendingAuto.current = true;
                    setTimeout(() => { pendingAuto.current = false; }, 8000);
                }
            }
            lastVoice.current = next.voiceText;
            session.voiceText = next.voiceText;
        }
        else if (!next.voiceId && next.voiceState === "done" && next.voiceText && next.voiceText !== session.voiceText) {
            lastVoice.current = next.voiceText;
            session.voiceText = next.voiceText;
            drafts.write(next.threadId, (drafts.read(next.threadId).trimEnd() ? drafts.read(next.threadId).trimEnd() + " " : "") + next.voiceText.trim() + " ");
        }
        if (next.voiceError && next.voiceError !== lastVoiceError.current) {
            lastVoiceError.current = next.voiceError;
            session.voiceError = next.voiceError;
            setError(next.voiceError);
        }
    }, []);
    const load = SP_REACT.useCallback(async () => {
        if (inFlight.current || viewGate.busy())
            return;
        inFlight.current = true;
        const revision = viewGate.token();
        try {
            const next = await snapshot();
            if (mounted.current && viewGate.current(revision)) {
                accept(next);
                setConnectionError("");
            }
        }
        catch {
            if (mounted.current)
                setConnectionError("Связь с Deck AI прервалась. Повторяю подключение…");
        }
        finally {
            inFlight.current = false;
        }
    }, [accept]);
    SP_REACT.useEffect(() => { mounted.current = true; void load(); const timer = setInterval(() => void load(), voicePolling ? 500 : 2500); return () => { mounted.current = false; clearInterval(timer); }; }, [load, voicePolling]);
    SP_REACT.useEffect(() => { const el = chatRef.current; if (el && followTail.current)
        el.scrollTop = el.scrollHeight; }, [data?.messages, tab]);
    const editDraft = (value, owner = draftId.current) => drafts.write(owner, value);
    const run = async (work) => { if (actionLock.current || !viewGate.begin())
        return; actionLock.current = true; setBusy(true); setError(""); setNotice(""); try {
        await work();
    }
    catch (e) {
        setError(String(e));
    }
    finally {
        actionLock.current = false;
        viewGate.end();
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
            const result = await gameVoice(lang === "ru" ? "ru-fast" : lang === "en" ? "en-fast" : lang, stopping || !autoSend ? 0 : 2.5);
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
        if (drafts.read(sentThread) === sentDraft) {
            drafts.write(sentThread, "");
            if (draftId.current === sentThread)
                setDraft("");
        }
        publishAttachments(sentThread, []);
        if (draftId.current === sentThread)
            setImagesState([]);
        setNotice("Запрос принят · в очереди");
        followTail.current = true;
        accept(await snapshot());
    });
    const submitRef = SP_REACT.useRef(submit);
    submitRef.current = submit;
    SP_REACT.useEffect(() => { if (pendingAuto.current && !recording && !voiceProcessing && draft.trim()) {
        pendingAuto.current = false;
        setCountdown(3);
    } }, [draft, recording, voiceProcessing]);
    SP_REACT.useEffect(() => {
        if (countdown === null)
            return;
        if (countdown <= 0) {
            setCountdown(null);
            submitRef.current();
            return;
        }
        const timer = setTimeout(() => setCountdown(value => value === null ? null : value - 1), 1000);
        return () => clearTimeout(timer);
    }, [countdown]);
    const quick = (text) => void run(async () => { await sendMessage(text, [], model?.id || "", effort, tier); setNotice("Запрос принят · в очереди"); setQuickOpen(false); followTail.current = true; accept(await snapshot()); });
    const ro = !!data?.readOnly;
    const names = { ...providerNames, ...Object.fromEntries((data?.customProviders || []).map(c => [c.id, c.name])) };
    const isCustom = !!data?.customProviders?.some(c => c.id === data.provider);
    const [custom, setCustom] = SP_REACT.useState({ name: "", url: "", models: "", key: "" });
    const decide = (item, decision) => void run(async () => {
        // Allowing runs a command on the machine: require a second, deliberate press.
        if (decision !== "decline" && confirmApproval !== item.key) {
            setConfirmApproval(item.key);
            setNotice("Нажмите «Разрешить» ещё раз, чтобы подтвердить");
            return;
        }
        setConfirmApproval("");
        await approve(item.key, decision);
        setNotice(decision === "decline" ? "Отклонено" : "Разрешено");
        accept(await snapshot());
    });
    const openFolder = (path) => void run(async () => { const result = await fileList(path); setFolder(result.path); setEntries(sortEntries(result.entries)); setFile(null); });
    const openFile = (path) => void run(async () => { const result = await fileRead(path); setFile(result); setFileText(result.text); });
    const saveFile = () => void run(async () => { if (!file)
        return; const result = await fileWrite(file.path, fileText, file.sha256); setFile({ ...file, text: fileText, sha256: result.sha256 }); setNotice("Файл сохранён · копия: " + file.path.split("/").pop() + ".deckai.bak"); });
    const chooseThread = (id) => void run(async () => {
        const current = session.snapshot;
        if (current) {
            const cached = historySnapshots.get(historyKey({ ...current, threadId: id }));
            accept(cached ? { ...cached, threads: current.threads } : { ...current, threadId: id, messages: [], active: false, status: "Загружаю диалог…" });
        }
        accept(await selectThread(id));
        setTab("chat");
    });
    const startChat = () => void run(async () => { accept(await newThread()); setTab("chat"); });
    const openFiles = () => { setTab("history"); setFilesOpen(true); openFolder("~"); };
    const sortedThreads = [...(data?.threads || [])].sort((a, b) => Number(!!b.running) - Number(!!a.running));
    const sidebar = fullscreen && layout === "split" ? SP_JSX.jsx(GameScroll, { className: "dai-split-side", children: SP_JSX.jsxs("div", { className: "dai-stack-content", children: [SP_JSX.jsxs(Action, { primary: true, disabled: busy || !data?.ready || ro || data?.active, onClick: startChat, children: [SP_JSX.jsx(FaPlus, {}), "\u041D\u043E\u0432\u044B\u0439 \u0447\u0430\u0442"] }), sortedThreads.map(thread => SP_JSX.jsx("div", { className: "dai-history-item " + (thread.id === data?.threadId ? "selected" : "") + (thread.running ? " running" : ""), children: SP_JSX.jsx(Action, { disabled: busy || (data?.active && thread.id !== data.threadId && !data.remoteHost), onClick: () => chooseThread(thread.id), children: SP_JSX.jsxs("span", { children: [thread.running && SP_JSX.jsx("span", { className: "dai-dot working", "aria-label": "\u0412\u044B\u043F\u043E\u043B\u043D\u044F\u0435\u0442\u0441\u044F" }), thread.name || "Новый чат"] }) }) }, thread.id))] }) }) : null;
    const speak = (id, text) => {
        const synth = window.speechSynthesis;
        if (!synth)
            return;
        if (speaking === id) {
            synth.cancel();
            setSpeaking("");
            return;
        }
        synth.cancel();
        const utterance = new SpeechSynthesisUtterance(text.slice(0, 4000));
        utterance.lang = /[а-яё]/i.test(text) ? "ru-RU" : "en-US";
        utterance.onend = utterance.onerror = () => setSpeaking("");
        setSpeaking(id);
        synth.speak(utterance);
    };
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
    const signIn = () => void run(async () => { const result = await accountLogin(); setLoginUrl(result.url + (result.userCode ? " · Код: " + result.userCode : "")); setNotice(result.opened ? "Откройте страницу входа и завершите авторизацию." : "Ссылка для входа показана ниже."); accept(await snapshot()); });
    const disconnect = !data?.ready;
    return SP_JSX.jsxs(DFL.Focusable, { style: { "--dai-text-scale": textScale }, "data-text-scale": textScale, "data-theme": appearance.theme, "data-density": appearance.density, "data-bubbles": appearance.bubbles, "data-layout": layout, className: "dai-root" + (fullscreen ? " dai-fullscreen" : ""), onSecondaryButton: () => { if (tab === "chat" && !busy)
            void toggleVoice(); }, onSecondaryActionDescription: tab === "chat" ? (recording ? "Стоп" : "Голос") : undefined, onCancel: event => {
            if (queueOpen) {
                event.stopPropagation();
                setQueueOpen(false);
            }
            else if (mediaOpen) {
                event.stopPropagation();
                setMediaOpen(false);
            }
            else if (fullscreen) {
                event.stopPropagation();
                closeFullscreen();
            }
        }, children: [SP_JSX.jsx("style", { children: css }), SP_JSX.jsx("span", { ref: touchAnchor, hidden: true }), fullscreen && SP_JSX.jsxs(DFL.Focusable, { className: "dai-full-header", "flow-children": "horizontal", children: [SP_JSX.jsxs("div", { className: "dai-full-brand", children: [SP_JSX.jsx("h1", { children: "Deck AI" }), SP_JSX.jsx("span", { children: disconnect ? "Нет соединения" : data?.active ? "Deck AI работает…" : gameStatus })] }), SP_JSX.jsx(GameCheckbox, { checked: gameContextEnabled, onChange: toggleGameContext }), SP_JSX.jsxs(Action, { onClick: () => closeFullscreen(), children: [SP_JSX.jsx(FaCompress, {}), "\u0412 \u043F\u0430\u043D\u0435\u043B\u044C"] }), SP_JSX.jsxs(Action, { onClick: () => closeFullscreen(false), children: [SP_JSX.jsx(FaArrowLeft, {}), "\u041A \u0438\u0433\u0440\u0435"] })] }), SP_JSX.jsx(DFL.Focusable, { className: "dai-tabs", "flow-children": "horizontal", role: "tablist", "aria-label": "Deck AI", children: [["chat", "Чат", SP_JSX.jsx(FaComment, {})], ["history", "История", SP_JSX.jsx(FaHistory, {})], ["settings", "Настройки", SP_JSX.jsx(FaCog, {})]].map(([id, label, icon]) => SP_JSX.jsx("div", { role: "tab", "aria-selected": tab === id, className: "dai-tab " + (tab === id ? "selected" : ""), children: SP_JSX.jsxs(Action, { disabled: busy, onClick: () => { if (id === "settings" && !fullscreen)
                            openFullscreen("settings");
                        else {
                            setTab(id);
                            setMediaOpen(false);
                            setQueueOpen(false);
                        } }, children: [icon, SP_JSX.jsx("span", { children: label })] }) }, id)) }), SP_JSX.jsxs("div", { className: "dai-viewbar", children: [SP_JSX.jsxs("div", { className: "dai-status", children: [SP_JSX.jsx("span", { className: "dai-dot " + (disconnect ? "offline" : data?.active ? "working" : "") }), SP_JSX.jsx("span", { children: !data ? "Подключение…" : data.ready ? (data.active ? "Deck AI работает…" : gameStatus) : (data.retryIn ? `Нет связи · повтор через ${data.retryIn} с` : "Нет соединения") }), data?.remoteHost && SP_JSX.jsx("small", { children: data.remoteHost }), !!data?.runningCount && SP_JSX.jsxs("small", { className: "dai-running-count", children: [data.runningCount, " \u0432 \u0440\u0430\u0431\u043E\u0442\u0435"] })] }), !fullscreen && SP_JSX.jsx(GameCheckbox, { checked: gameContextEnabled, onChange: toggleGameContext }), !fullscreen && SP_JSX.jsxs(Action, { disabled: busy, onClick: () => openFullscreen(tab), children: [SP_JSX.jsx(FaExpand, {}), "\u041D\u0430 \u0432\u0435\u0441\u044C \u044D\u043A\u0440\u0430\u043D"] })] }), (error || connectionError) && SP_JSX.jsxs("div", { className: "dai-banner", role: "alert", children: [SP_JSX.jsx("span", { children: error || connectionError }), SP_JSX.jsx(Action, { onClick: () => { setError(""); setConnectionError(""); }, children: "\u0417\u0430\u043A\u0440\u044B\u0442\u044C" })] }), !error && !connectionError && (data?.historyWarning || data?.ready === false) && SP_JSX.jsxs("div", { className: "dai-banner", role: "status", children: [SP_JSX.jsx("span", { children: data.historyWarning || data.status }), SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { accept(await refresh()); }), children: "\u041F\u043E\u0432\u0442\u043E\u0440\u0438\u0442\u044C \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u0435" })] }), notice && SP_JSX.jsx("div", { className: "dai-notice", role: "status", children: notice }), SP_JSX.jsxs("div", { className: "dai-page", role: "tabpanel", "aria-label": tab === "chat" ? "Чат" : tab === "history" ? "История" : "Настройки", children: [tab === "chat" && SP_JSX.jsxs("div", { className: "dai-chat-layout", children: [sidebar, SP_JSX.jsx("div", { className: "dai-chat-main" + (data?.approvals?.length ? " has-approvals" : ""), children: queueOpen ? SP_JSX.jsx(GameScroll, { ref: queueRef, className: "dai-scroll dai-stack dai-queue-view", children: SP_JSX.jsxs("div", { className: "dai-stack-content", children: [SP_JSX.jsx(Action, { onClick: () => setQueueOpen(false), children: "\u2190 \u041A \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044E" }), SP_JSX.jsxs("h3", { children: ["\u041E\u0447\u0435\u0440\u0435\u0434\u044C \u0437\u0430\u043F\u0440\u043E\u0441\u043E\u0432 \u00B7 ", data?.queueTotal ?? data?.outbox.length ?? 0] }), SP_JSX.jsx("p", { className: "dai-muted", children: "\u041E\u0436\u0438\u0434\u0430\u044E\u0449\u0438\u0435 \u0437\u0430\u043F\u0440\u043E\u0441\u044B \u0435\u0449\u0451 \u043D\u0435 \u043E\u0442\u043F\u0440\u0430\u0432\u043B\u0435\u043D\u044B. \u0417\u0430\u043F\u0440\u043E\u0441\u044B \u0432\u044B\u043F\u043E\u043B\u043D\u044F\u044E\u0442\u0441\u044F \u043F\u043E \u043E\u0447\u0435\u0440\u0435\u0434\u0438; \u0437\u0430\u043D\u044F\u0442\u044B\u0439 \u0447\u0430\u0442 \u0436\u0434\u0451\u0442 \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043D\u0438\u044F \u0442\u0435\u043A\u0443\u0449\u0435\u0433\u043E \u043E\u0442\u0432\u0435\u0442\u0430." }), SP_JSX.jsxs("p", { className: "dai-muted", children: ["\u0412 \u044D\u0442\u043E\u043C \u0447\u0430\u0442\u0435 \u043E\u0436\u0438\u0434\u0430\u044E\u0442: ", queueCounts(data?.outbox || [], data?.threadId || "").current, ". \u0412 \u0434\u0440\u0443\u0433\u0438\u0445 \u0447\u0430\u0442\u0430\u0445: ", queueCounts(data?.outbox || [], data?.threadId || "").other, "."] }), (data?.queueTotal || 0) > (data?.outbox.length || 0) && SP_JSX.jsxs("p", { className: "dai-muted", children: ["\u041F\u043E\u043A\u0430\u0437\u0430\u043D\u044B \u043F\u043E\u0441\u043B\u0435\u0434\u043D\u0438\u0435 ", data?.outbox.length, " \u0437\u0430\u043F\u0440\u043E\u0441\u043E\u0432."] }), !data?.outbox.length && SP_JSX.jsx("p", { className: "dai-muted", children: "\u041E\u0447\u0435\u0440\u0435\u0434\u044C \u043F\u0443\u0441\u0442\u0430." }), data?.outbox.map(job => SP_JSX.jsxs("section", { className: "dai-section dai-queue-item", children: [SP_JSX.jsx("strong", { children: queueStatus(job) }), SP_JSX.jsxs("small", { className: "dai-muted", children: [job.threadId === data.threadId ? "Этот чат" : (data.threads.find(thread => thread.id === job.threadId)?.name || "Другой чат").slice(0, 80), job.createdAt ? " · " + new Date(job.createdAt * 1000).toLocaleString() : ""] }), SP_JSX.jsx("p", { className: "dai-queue-text", children: expandedJob === job.id ? job.text : job.text.slice(0, 180) + (job.text.length > 180 ? "…" : "") }), job.text.length > 180 && SP_JSX.jsx(Action, { onClick: () => setExpandedJob(expandedJob === job.id ? "" : job.id), children: expandedJob === job.id ? "Свернуть текст" : "Весь текст запроса" }), job.error && SP_JSX.jsx("p", { className: "dai-muted", children: job.error }), job.status === "queued" && SP_JSX.jsx(Action, { disabled: busy || ro, onClick: () => void run(async () => { await queueFront(job.id); accept(await snapshot()); }), children: "\u2191 \u041E\u0442\u043F\u0440\u0430\u0432\u0438\u0442\u044C \u043F\u0435\u0440\u0432\u044B\u043C" }), (job.status === "queued" || job.status === "error") && SP_JSX.jsx(Action, { disabled: busy || ro, onClick: () => void run(async () => { await queueRemove(job.id); accept(await snapshot()); }), children: "\u0423\u0434\u0430\u043B\u0438\u0442\u044C \u0438\u0437 \u043E\u0447\u0435\u0440\u0435\u0434\u0438" }), job.threadId && SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { if ((job.host || "") !== (data?.remoteHost || ""))
                                                            accept(await remoteHost(job.host || "")); accept(await selectThread(job.threadId)); setTab("chat"); setQueueOpen(false); }), children: "\u041E\u0442\u043A\u0440\u044B\u0442\u044C \u0447\u0430\u0442" })] }, job.id))] }) }, "queue") : mediaOpen ? SP_JSX.jsx(GameScroll, { className: "dai-scroll dai-stack", children: SP_JSX.jsxs("div", { className: "dai-stack-content", children: [SP_JSX.jsx(Action, { onClick: () => setMediaOpen(false), children: "\u2190 \u041A \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044E" }), SP_JSX.jsxs("section", { className: "dai-section dai-game-context", children: [SP_JSX.jsxs("h3", { children: [SP_JSX.jsx(FaGamepad, {}), " \u041A\u043E\u043D\u0442\u0435\u043A\u0441\u0442 \u0438\u0433\u0440\u044B"] }), SP_JSX.jsx("p", { className: "dai-muted", children: game ? game.name : "Сейчас Steam не сообщает о запущенной игре." }), game && SP_JSX.jsx("p", { className: "dai-muted", children: game.status || "Игра не передаёт описание текущего места или задания." }), game?.details.map(([key, value]) => SP_JSX.jsxs("p", { className: "dai-muted", children: [key, ": ", value] }, key)), SP_JSX.jsx(GameCheckbox, { checked: gameContextEnabled, onChange: toggleGameContext }), game && SP_JSX.jsxs(Action, { disabled: !currentScreenshots.length, onClick: () => attach(currentScreenshots[0]), children: ["\u0421\u043D\u0438\u043C\u043E\u043A \u0438\u0437 \u044D\u0442\u043E\u0439 \u0438\u0433\u0440\u044B", currentScreenshots[0]?.when ? " · " + new Date(currentScreenshots[0].when * 1000).toLocaleString() : ""] }), SP_JSX.jsx("p", { className: "dai-muted", children: "\u0427\u0442\u043E\u0431\u044B \u043F\u043E\u043A\u0430\u0437\u0430\u0442\u044C, \u0433\u0434\u0435 \u0432\u044B \u0441\u0435\u0439\u0447\u0430\u0441: \u0441\u0434\u0435\u043B\u0430\u0439\u0442\u0435 \u0441\u043D\u0438\u043C\u043E\u043A \u0432 \u0438\u0433\u0440\u0435 \u2014 Steam + R1, \u0437\u0430\u0442\u0435\u043C \u043F\u0440\u0438\u043A\u0440\u0435\u043F\u0438\u0442\u0435 \u0435\u0433\u043E \u0437\u0434\u0435\u0441\u044C. \u0413\u0430\u043B\u043E\u0447\u043A\u0430 \u00AB\u0418\u0433\u0440\u0430\u00BB \u0434\u043E\u0431\u0430\u0432\u043B\u044F\u0435\u0442 \u043A \u0432\u043E\u043F\u0440\u043E\u0441\u0443 \u0442\u043E\u043B\u044C\u043A\u043E \u043D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u0438\u0433\u0440\u044B." })] }), SP_JSX.jsx("h3", { children: "\u0414\u0440\u0443\u0433\u0438\u0435 \u0432\u043B\u043E\u0436\u0435\u043D\u0438\u044F" }), SP_JSX.jsx(Action, { disabled: !data?.screenshots.length, onClick: () => attach(data?.screenshots[0]), children: "\u041F\u043E\u0441\u043B\u0435\u0434\u043D\u0438\u0439 \u0441\u043A\u0440\u0438\u043D\u0448\u043E\u0442" }), SP_JSX.jsx(Choice, { label: "\u0414\u0440\u0443\u0433\u043E\u0439 \u0441\u043A\u0440\u0438\u043D\u0448\u043E\u0442", value: shot, options: (data?.screenshots || []).map(x => ({ data: x.path, label: x.name })), onChange: setShot }), SP_JSX.jsx(Action, { disabled: !shot, onClick: () => attach(data?.screenshots.find(x => x.path === shot)), children: "\u041F\u0440\u0438\u043A\u0440\u0435\u043F\u0438\u0442\u044C \u0441\u043A\u0440\u0438\u043D\u0448\u043E\u0442" }), SP_JSX.jsx(Choice, { label: "\u0412\u0438\u0434\u0435\u043E\u0437\u0430\u043F\u0438\u0441\u044C", value: video, options: (data?.videos || []).map(x => ({ data: x.path, label: x.name })), onChange: setVideo }), SP_JSX.jsx(Action, { disabled: !video || busy, onClick: () => void run(async () => { const result = await videoFrames(video); setImages(old => [...old, ...result.frames]); setMediaOpen(false); }), children: "\u0414\u043E\u0431\u0430\u0432\u0438\u0442\u044C \u043A\u0430\u0434\u0440\u044B \u0438\u0437 \u0432\u0438\u0434\u0435\u043E" }), !data?.screenshots.length && !data?.videos.length && SP_JSX.jsx("p", { className: "dai-muted", children: "\u0421\u0434\u0435\u043B\u0430\u0439\u0442\u0435 \u0441\u043A\u0440\u0438\u043D\u0448\u043E\u0442 \u0432 \u0438\u0433\u0440\u0435: Steam + R1. \u041E\u043D \u043F\u043E\u044F\u0432\u0438\u0442\u0441\u044F \u0437\u0434\u0435\u0441\u044C." })] }) }) : SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsxs(DFL.Focusable, { className: "dai-toolbar", "flow-children": "horizontal", children: [SP_JSX.jsxs(Action, { disabled: busy || disconnect || ro || data?.active, onClick: startChat, children: [SP_JSX.jsx(FaPlus, {}), SP_JSX.jsx("span", { children: "\u041D\u043E\u0432\u044B\u0439" })] }), SP_JSX.jsxs(Action, { disabled: busy || disconnect, onClick: openFiles, children: [SP_JSX.jsx(FaFolderOpen, {}), SP_JSX.jsx("span", { children: "\u0424\u0430\u0439\u043B\u044B" })] }), SP_JSX.jsxs(Action, { onClick: () => setQueueOpen(true), children: [SP_JSX.jsx(FaListUl, {}), SP_JSX.jsxs("span", { children: ["\u041E\u0447\u0435\u0440\u0435\u0434\u044C", (data?.queueTotal || data?.outbox.length) ? " · " + (data?.queueTotal ?? data?.outbox.length) : ""] })] }), SP_JSX.jsxs(Action, { disabled: busy, onClick: () => void run(async () => { accept(await refresh()); setNotice("Обновлено"); }), children: [SP_JSX.jsx(FaSyncAlt, {}), SP_JSX.jsx("span", { children: "\u041E\u0431\u043D\u043E\u0432\u0438\u0442\u044C" })] })] }), SP_JSX.jsx(GameScroll, { className: "dai-messages", ref: chatRef, onScroll: () => { const el = chatRef.current; if (el) {
                                                followTail.current = el.scrollHeight - el.scrollTop - el.clientHeight < 60;
                                                setShowLatest(!followTail.current);
                                            } }, children: SP_JSX.jsxs("div", { className: "dai-message-list", children: [!data?.messages.length && SP_JSX.jsxs("div", { className: "dai-empty", children: [SP_JSX.jsx(FaComment, {}), SP_JSX.jsx("h3", { children: "\u041F\u043E\u043C\u043E\u0449\u044C \u043F\u0440\u044F\u043C\u043E \u0432 \u0438\u0433\u0440\u0435" }), SP_JSX.jsxs("p", { children: ["\u0417\u0430\u0434\u0430\u0439\u0442\u0435 \u0432\u043E\u043F\u0440\u043E\u0441 \u0442\u0435\u043A\u0441\u0442\u043E\u043C \u0438\u043B\u0438 \u0433\u043E\u043B\u043E\u0441\u043E\u043C.", SP_JSX.jsx("br", {}), "\u041C\u043E\u0436\u043D\u043E \u0434\u043E\u0431\u0430\u0432\u0438\u0442\u044C \u0441\u043A\u0440\u0438\u043D\u0448\u043E\u0442."] }), disconnect && SP_JSX.jsx(Action, { onClick: () => void run(async () => accept(await refresh())), disabled: busy, children: busy ? "Подключение…" : "Подключиться" })] }), data?.hasOlderMessages && SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { followTail.current = false; accept(await olderMessages()); requestAnimationFrame(() => { if (chatRef.current)
                                                            chatRef.current.scrollTop = 0; }); }), children: "\u041F\u043E\u043A\u0430\u0437\u0430\u0442\u044C \u043F\u0440\u0435\u0434\u044B\u0434\u0443\u0449\u0438\u0435 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F" }), data?.messages.map((message, i) => message.role === "tool" ? SP_JSX.jsx(DFL.Focusable, { className: "dai-message tool", focusClassName: "dai-focused", onActivate: () => setOpenTool(openTool === (message.id || String(i)) ? "" : (message.id || String(i))), children: SP_JSX.jsx("pre", { children: openTool === (message.id || String(i)) ? message.text : message.text.split("\n").slice(0, 3).join("\n") + (message.text.split("\n").length > 3 ? "\n…" : "") }) }, message.id || i) : SP_JSX.jsxs(DFL.Focusable, { className: "dai-message " + message.role, focusClassName: "dai-focused", children: [SP_JSX.jsx("small", { children: message.role === "user" ? "Вы" : names[data.provider]?.split(" · ")[0] || "AI" }), SP_JSX.jsx("div", { children: message.text }), !!message.attachments?.length && SP_JSX.jsx(MessageAttachments, { items: message.attachments }), SP_JSX.jsxs("div", { className: "dai-message-tools", children: [SP_JSX.jsxs(Action, { onClick: () => copyMessage(message.text), children: [SP_JSX.jsx(FaCopy, {}), "\u041A\u043E\u043F\u0438\u0440\u043E\u0432\u0430\u0442\u044C"] }), message.role === "assistant" && !!window.speechSynthesis && SP_JSX.jsx(Action, { onClick: () => speak(message.id || String(i), message.text), children: speaking === (message.id || String(i)) ? "■ Стоп" : "🔊 Озвучить" })] })] }, message.id || i)), (data ? chatFailures(data.outbox, data.threadId, data.remoteHost || "") : []).map(x => SP_JSX.jsxs("div", { className: "dai-failed", children: [SP_JSX.jsx("p", { children: x.error || "Не удалось отправить" }), SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { await retry(x.id); accept(await snapshot()); }), children: "\u041F\u043E\u0432\u0442\u043E\u0440\u0438\u0442\u044C \u043E\u0442\u043F\u0440\u0430\u0432\u043A\u0443" })] }, x.id))] }) }), showLatest && SP_JSX.jsx("div", { className: "dai-latest", children: SP_JSX.jsx(Action, { onClick: jumpToLatest, children: "\u2193 \u041A \u043F\u043E\u0441\u043B\u0435\u0434\u043D\u0435\u043C\u0443 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044E" }) }), ro && SP_JSX.jsx("div", { className: "dai-notice", role: "status", children: "\u0420\u0435\u0436\u0438\u043C \u0442\u043E\u043B\u044C\u043A\u043E \u0447\u0442\u0435\u043D\u0438\u044F: \u043E\u0442\u043F\u0440\u0430\u0432\u043A\u0430, \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u044F \u0438 \u043F\u0440\u0430\u0432\u043A\u0438 \u043E\u0442\u043A\u043B\u044E\u0447\u0435\u043D\u044B." }), !!data?.approvals?.length && SP_JSX.jsx(GameScroll, { className: "dai-approvals", role: "alert", children: data.approvals.map(item => SP_JSX.jsxs("div", { className: "dai-approval", children: [SP_JSX.jsxs("strong", { children: ["\u041D\u0443\u0436\u043D\u043E \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u0435 \u00B7 ", item.title] }), SP_JSX.jsx("span", { className: "dai-muted", children: item.summary }), SP_JSX.jsxs(DFL.Focusable, { className: "dai-compose-actions", "flow-children": "horizontal", children: [SP_JSX.jsx(Action, { primary: true, disabled: busy || ro, onClick: () => decide(item, "accept"), children: confirmApproval === item.key ? "Нажмите ещё раз" : "Разрешить" }), SP_JSX.jsx(Action, { disabled: busy || ro, onClick: () => decide(item, "decline"), children: "\u041E\u0442\u043A\u043B\u043E\u043D\u0438\u0442\u044C" })] })] }, item.key)) }), SP_JSX.jsxs("div", { className: "dai-composer", children: [countdown !== null && SP_JSX.jsxs("div", { className: "dai-notice", role: "status", children: ["\u041E\u0442\u043F\u0440\u0430\u0432\u043A\u0430 \u0447\u0435\u0440\u0435\u0437 ", countdown, " \u0441", SP_JSX.jsx(Action, { onClick: () => setCountdown(null), children: "\u041E\u0442\u043C\u0435\u043D\u0438\u0442\u044C \u043E\u0442\u043F\u0440\u0430\u0432\u043A\u0443" })] }), quickOpen && data?.threadId && SP_JSX.jsx(DFL.Focusable, { className: "dai-quick", "flow-children": "horizontal", children: quickActions.map(([label, text]) => SP_JSX.jsx(Action, { disabled: busy || disconnect || ro, onClick: () => quick(text), children: label }, label)) }), data?.outbox.some(job => job.status === "recovering") && SP_JSX.jsx("p", { className: "dai-muted dai-queue-state", role: "status", children: "\u041F\u0440\u043E\u0432\u0435\u0440\u044F\u044E \u0441\u043E\u0441\u0442\u043E\u044F\u043D\u0438\u0435 \u043E\u0442\u043F\u0440\u0430\u0432\u043B\u0435\u043D\u043D\u043E\u0433\u043E \u0437\u0430\u043F\u0440\u043E\u0441\u0430\u2026" }), !!data?.outbox.length && SP_JSX.jsx("div", { className: "dai-queue-summary", children: SP_JSX.jsxs(Action, { onClick: () => setQueueOpen(true), children: ["\u041E\u0447\u0435\u0440\u0435\u0434\u044C \u00B7 ", data.queueTotal ?? data.outbox.length, " \u00B7 \u043F\u043E\u0441\u043C\u043E\u0442\u0440\u0435\u0442\u044C"] }) }), images.length > 0 && SP_JSX.jsx("div", { className: "dai-attachments", children: images.map((image, i) => SP_JSX.jsxs(Action, { onClick: () => setImages(old => old.filter((_, n) => n !== i)), children: ["\u00D7 ", image.name] }, image.path + ":" + i)) }), (recording || voiceProcessing) && SP_JSX.jsxs("div", { className: "dai-voice-preview", role: "status", "aria-live": "polite", children: [SP_JSX.jsx("span", { className: "dai-record-dot", "aria-hidden": "true" }), SP_JSX.jsxs("div", { children: [SP_JSX.jsx("strong", { children: recording ? "● Запись · распознанный текст" : "Завершаю распознавание…" }), SP_JSX.jsx("span", { role: "textbox", "aria-label": "\u0420\u0430\u0441\u043F\u043E\u0437\u043D\u0430\u043D\u043D\u0430\u044F \u0440\u0435\u0447\u044C", "aria-readonly": "true", children: (data?.voiceId !== session.discardedVoice ? data?.voiceText : "") || (["ru", "en", "ru-fast", "en-fast"].includes(lang) ? "Здесь появится распознанная речь" : "Записываю. Текст появится после «Стоп».") })] })] }), SP_JSX.jsx("form", { style: { display: "contents" }, onSubmit: e => { e.preventDefault(); submit(); }, children: SP_JSX.jsx("div", { className: "dai-draft-field", "data-draft-owner": data?.threadId || "", onInputCapture: e => { const target = e.target; if (target.tagName === "INPUT")
                                                            editDraft(target.value, e.currentTarget.dataset.draftOwner || ""); }, children: SP_JSX.jsx(DFL.TextField, { disabled: recording || voiceProcessing, value: draft, placeholder: "\u0421\u043F\u0440\u043E\u0441\u0438\u0442\u044C \u043E\u0431 \u0438\u0433\u0440\u0435\u2026", onChange: e => editDraft(e.target.value, e.target.closest(".dai-draft-field")?.dataset.draftOwner ?? draftId.current), onKeyDown: e => { if ((e.key === "Enter" || e.keyCode === 13) && !e.shiftKey && !e.nativeEvent.isComposing) {
                                                                e.preventDefault();
                                                                submit();
                                                            } } }) }, data?.threadId || "new") }), SP_JSX.jsxs(DFL.Focusable, { className: "dai-compose-actions", "flow-children": "horizontal", children: [SP_JSX.jsxs(Action, { recording: recording || voiceProcessing, disabled: !data || voiceProcessing || busy, onClick: () => void toggleVoice(), children: [SP_JSX.jsx(FaMicrophone, {}), recording ? "Стоп" : "Голос"] }), !!data?.threadId && SP_JSX.jsx(Action, { disabled: recording || voiceProcessing, onClick: () => setQuickOpen(!quickOpen), children: "\u26A1" }), SP_JSX.jsx(Action, { disabled: voiceStarting || (!draft.trim() && !recording && !voiceProcessing), onClick: clearDraft, children: "\u041E\u0447\u0438\u0441\u0442\u0438\u0442\u044C" }), fullscreen && data?.active && data.provider === "codex" && SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { await stop(); accept(await snapshot()); }), children: "\u0421\u0442\u043E\u043F" }), SP_JSX.jsx(Action, { primary: true, disabled: busy || disconnect || ro || recording || voiceProcessing || !draft.trim(), onClick: submit, children: busy ? "…" : "Отправить" })] }), !fullscreen && data?.active && data.provider === "codex" && SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { await stop(); accept(await snapshot()); }), children: "\u041E\u0441\u0442\u0430\u043D\u043E\u0432\u0438\u0442\u044C \u043E\u0442\u0432\u0435\u0442" })] })] }) })] }), tab === "history" && filesOpen && SP_JSX.jsx(GameScroll, { className: "dai-scroll dai-stack", children: SP_JSX.jsxs("div", { className: "dai-stack-content", children: [SP_JSX.jsxs(Action, { onClick: () => { if (file)
                                        setFile(null);
                                    else
                                        setFilesOpen(false); }, children: ["\u2190 ", file ? "К папке" : "Назад"] }), SP_JSX.jsx("h3", { children: file ? file.path.split("/").pop() : folder }), !file && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(Action, { onClick: () => openFolder(parentPath(folder)), children: "\u2B11 \u0412\u0432\u0435\u0440\u0445" }), entries.map(name => SP_JSX.jsxs(Action, { disabled: busy, onClick: () => isFolder(name) ? openFolder(joinPath(folder, name)) : openFile(joinPath(folder, name)), children: [isFolder(name) ? "📁 " : "📄 ", name] }, name)), !entries.length && SP_JSX.jsx("p", { className: "dai-muted", children: "\u041F\u0430\u043F\u043A\u0430 \u043F\u0443\u0441\u0442\u0430. \u0414\u043E\u0441\u0442\u0443\u043F\u043D\u0430 \u0442\u043E\u043B\u044C\u043A\u043E \u0434\u043E\u043C\u0430\u0448\u043D\u044F\u044F \u043F\u0430\u043F\u043A\u0430; \u043A\u043B\u044E\u0447\u0438 \u0438 \u0441\u0435\u043A\u0440\u0435\u0442\u044B \u0441\u043A\u0440\u044B\u0442\u044B." })] }), file && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx("textarea", { className: "dai-textarea", value: fileText, spellCheck: false, onChange: e => setFileText(e.target.value) }), SP_JSX.jsxs("p", { className: "dai-muted", children: [fileText === file.text ? "Без изменений" : "Есть несохранённые правки", " \u00B7 \u0434\u043E 64 \u041A\u0411 \u00B7 \u043F\u0435\u0440\u0435\u0434 \u0437\u0430\u043F\u0438\u0441\u044C\u044E \u0441\u043E\u0437\u0434\u0430\u0451\u0442\u0441\u044F \u043A\u043E\u043F\u0438\u044F .deckai.bak"] }), SP_JSX.jsx(Action, { primary: true, disabled: busy || ro || fileText === file.text, onClick: saveFile, children: "\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u043D\u0430 \u0443\u0441\u0442\u0440\u043E\u0439\u0441\u0442\u0432\u0435" }), SP_JSX.jsx(Action, { disabled: busy || fileText === file.text, onClick: () => setFileText(file.text), children: "\u041E\u0442\u043C\u0435\u043D\u0438\u0442\u044C \u043F\u0440\u0430\u0432\u043A\u0438" })] })] }) }), tab === "history" && !filesOpen && SP_JSX.jsx(GameScroll, { className: "dai-scroll dai-stack", children: SP_JSX.jsxs("div", { className: "dai-stack-content", children: [SP_JSX.jsx(Action, { primary: true, disabled: busy || disconnect || ro || data?.active, onClick: () => void run(async () => { accept(await newThread()); setTab("chat"); }), children: "\uFF0B \u041D\u043E\u0432\u044B\u0439 \u0447\u0430\u0442" }), SP_JSX.jsxs(Action, { disabled: busy || disconnect, onClick: () => { setFilesOpen(true); openFolder("~"); }, children: ["\uD83D\uDCC1 \u0424\u0430\u0439\u043B\u044B \u043D\u0430 \u0443\u0441\u0442\u0440\u043E\u0439\u0441\u0442\u0432\u0435", data?.remoteHost ? " · " + data.remoteHost : ""] }), !!data?.recentEvents?.length && SP_JSX.jsxs("section", { className: "dai-section dai-events", children: [SP_JSX.jsx("h3", { children: "\u0427\u0442\u043E \u043F\u0440\u043E\u0438\u0437\u043E\u0448\u043B\u043E" }), data.recentEvents.slice(0, 8).map(item => SP_JSX.jsxs("p", { className: "dai-muted", children: [item.kind === "approval" ? "⏸" : item.kind === "failed" ? "✗" : "✓", " ", new Date(item.at * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }), " \u00B7 ", (item.host || "Steam Deck") + " · " + item.title] }, item.id))] }), (data?.provider === "codex" || !data) && SP_JSX.jsx(Choice, { label: "\u0423\u0441\u0442\u0440\u043E\u0439\u0441\u0442\u0432\u043E", value: data?.remoteHost || "", options: [{ data: "", label: "Этот Steam Deck" }, ...(data?.sshHosts || []).map(x => ({ data: x, label: x }))], disabled: busy || data?.active, onChange: value => void run(async () => accept(await remoteHost(value))) }), data?.remoteHost && SP_JSX.jsxs(Action, { disabled: busy, onClick: () => void run(async () => { accept(await refresh()); setNotice("Список задач обновлён"); }), children: ["\u21BB \u041E\u0431\u043D\u043E\u0432\u0438\u0442\u044C \u0437\u0430\u0434\u0430\u0447\u0438 \u043D\u0430 ", data.remoteHost] }), SP_JSX.jsx(DFL.TextField, { value: historyQuery, placeholder: "\u041D\u0430\u0439\u0442\u0438 \u0440\u0430\u0437\u0433\u043E\u0432\u043E\u0440\u2026", onChange: e => setHistoryQuery(e.target.value) }), (data?.allTasks || []).some(t => t.host !== (data?.remoteHost || "") || t.running) && SP_JSX.jsxs("section", { className: "dai-section dai-all-tasks", children: [SP_JSX.jsx("h3", { children: "\u0417\u0430\u0434\u0430\u0447\u0438 \u043D\u0430 \u0432\u0441\u0435\u0445 \u0443\u0441\u0442\u0440\u043E\u0439\u0441\u0442\u0432\u0430\u0445" }), (data?.allTasks || []).filter(t => t.host !== (data?.remoteHost || "") || t.running).slice(0, 12).map(t => SP_JSX.jsx(Action, { disabled: busy || (data?.active && !data.remoteHost && t.host === ""), onClick: () => void run(async () => { if (t.host !== (data?.remoteHost || ""))
                                                accept(await remoteHost(t.host)); accept(await selectThread(t.id)); setTab("chat"); }), children: SP_JSX.jsxs("span", { children: [t.running && SP_JSX.jsx("span", { className: "dai-dot working", "aria-label": "\u0412\u044B\u043F\u043E\u043B\u043D\u044F\u0435\u0442\u0441\u044F" }), (t.host || "Steam Deck") + " · " + t.name] }) }, t.host + ":" + t.id))] }), !data?.threads.length && SP_JSX.jsx("p", { className: "dai-muted", children: "\u0412\u0430\u0448\u0438 \u0440\u0430\u0437\u0433\u043E\u0432\u043E\u0440\u044B \u043F\u043E\u044F\u0432\u044F\u0442\u0441\u044F \u0437\u0434\u0435\u0441\u044C." }), data?.threads.filter(x => x.name.toLocaleLowerCase().includes(historyQuery.toLocaleLowerCase())).sort((a, b) => Number(!!b.running) - Number(!!a.running)).map(thread => SP_JSX.jsx("div", { className: "dai-history-item " + (thread.id === data.threadId ? "selected" : "") + (thread.running ? " running" : ""), children: SP_JSX.jsxs(Action, { disabled: busy || (data.active && thread.id !== data.threadId && !data.remoteHost), onClick: () => chooseThread(thread.id), children: [SP_JSX.jsxs("span", { children: [thread.running && SP_JSX.jsx("span", { className: "dai-dot working", "aria-label": "\u0412\u044B\u043F\u043E\u043B\u043D\u044F\u0435\u0442\u0441\u044F" }), thread.name || "Новый чат"] }), thread.id === data.threadId && SP_JSX.jsx("small", { children: "\u0422\u0435\u043A\u0443\u0449\u0438\u0439" })] }) }, thread.id))] }) }), tab === "settings" && SP_JSX.jsx(GameScroll, { className: "dai-scroll dai-stack dai-settings", children: SP_JSX.jsxs("div", { className: "dai-settings-grid", children: [SP_JSX.jsxs("div", { className: "dai-settings-column", children: [SP_JSX.jsxs("section", { className: "dai-section dai-model-settings", children: [SP_JSX.jsx("h3", { children: "\u041C\u043E\u0434\u0435\u043B\u044C \u0438 \u043E\u0442\u0432\u0435\u0442" }), SP_JSX.jsxs("div", { className: "dai-model-fields", children: [SP_JSX.jsx(Choice, { label: "\u0421\u0435\u0440\u0432\u0438\u0441", value: data?.provider || "codex", options: Object.entries(names).map(([data, label]) => ({ data, label })), disabled: busy || data?.active, onChange: value => void run(async () => { accept(await setProvider(value)); setKey(""); }) }), SP_JSX.jsx(Choice, { label: "\u041C\u043E\u0434\u0435\u043B\u044C", value: model?.id || "", options: (data?.models || []).map(x => ({ data: x.id, label: x.name })), disabled: busy, onChange: id => { const next = data?.models.find(x => x.id === id); settings(id, next?.defaultEffort || next?.efforts[0]?.id || "", "default"); } }), data?.provider === "codex" && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(Choice, { label: "\u0413\u043B\u0443\u0431\u0438\u043D\u0430 \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u043A\u0438", value: effort, options: (model?.efforts || []).map(x => ({ data: x.id, label: x.name })), disabled: busy, onChange: value => settings(model?.id || "", value, tier) }), SP_JSX.jsx(Choice, { label: "\u0421\u043A\u043E\u0440\u043E\u0441\u0442\u044C", value: tier, options: [{ data: "default", label: "Обычная" }, ...(model?.tiers.includes("priority") ? [{ data: "priority", label: "Приоритетная" }] : [])], disabled: busy, onChange: value => settings(model?.id || "", effort, value) })] })] }), (data?.provider === "deepseek" || data?.provider === "tokenharbor" || isCustom) && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.TextField, { bIsPassword: true, value: key, placeholder: "\u041A\u043B\u044E\u0447 API", onChange: e => setKey(e.target.value) }), SP_JSX.jsx(Action, { disabled: busy || !key.trim(), onClick: () => void run(async () => { await setProviderKey(key.trim()); setKey(""); accept(await refresh()); setNotice("Ключ сохранён"); }), children: "\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u043A\u043B\u044E\u0447" }), SP_JSX.jsx("p", { className: "dai-muted", children: "\u041A\u043B\u044E\u0447 \u0445\u0440\u0430\u043D\u0438\u0442\u0441\u044F \u0432 \u0441\u0438\u0441\u0442\u0435\u043C\u043D\u043E\u043C \u0445\u0440\u0430\u043D\u0438\u043B\u0438\u0449\u0435 SteamOS." })] }), data?.provider === "claude" && SP_JSX.jsx("p", { className: "dai-muted", children: "Desktop Mode \u2192 Deck AI \u2192 + \u2192 \u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0438\u0442\u044C Claude Code \u0438\u043B\u0438 Anthropic Console (API). \u0412\u0445\u043E\u0434 \u0432\u044B\u043F\u043E\u043B\u043D\u044F\u0435\u0442\u0441\u044F \u0432 \u043E\u0444\u0438\u0446\u0438\u0430\u043B\u044C\u043D\u043E\u043C CLI: \u0441\u0432\u043E\u0439 \u0430\u043A\u043A\u0430\u0443\u043D\u0442, API-\u043A\u043B\u044E\u0447 \u0438\u043B\u0438 \u043E\u0431\u043B\u0430\u0447\u043D\u044B\u0439 \u0434\u043E\u0441\u0442\u0443\u043F. \u0420\u0430\u0441\u0445\u043E\u0434\u044B \u0437\u0430\u0432\u0438\u0441\u044F\u0442 \u043E\u0442 \u0441\u043F\u043E\u0441\u043E\u0431\u0430 \u0434\u043E\u0441\u0442\u0443\u043F\u0430." }), isCustom && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx("p", { className: "dai-muted", children: "\u0414\u043B\u044F \u044D\u0442\u043E\u0433\u043E \u043E\u0431\u043B\u0430\u0447\u043D\u043E\u0433\u043E \u0441\u0435\u0440\u0432\u0438\u0441\u0430 \u043D\u0443\u0436\u0435\u043D API-\u043A\u043B\u044E\u0447. \u041E\u043D \u0445\u0440\u0430\u043D\u0438\u0442\u0441\u044F \u0432 \u0441\u0438\u0441\u0442\u0435\u043C\u043D\u043E\u043C \u0445\u0440\u0430\u043D\u0438\u043B\u0438\u0449\u0435 SteamOS." }), SP_JSX.jsx(Action, { disabled: busy || ro, onClick: () => DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: "Удалить «" + (names[data.provider] || "") + "»?", strOKButtonText: "\u0423\u0434\u0430\u043B\u0438\u0442\u044C", strCancelButtonText: "\u041E\u0442\u043C\u0435\u043D\u0430", onOK: () => void run(async () => { await customRemove(data.provider); accept(await refresh()); }) })), children: "\u0423\u0434\u0430\u043B\u0438\u0442\u044C \u044D\u0442\u043E \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u0435" })] })] }), SP_JSX.jsxs("section", { className: "dai-section dai-appearance", children: [SP_JSX.jsx("h3", { children: "\u041E\u0444\u043E\u0440\u043C\u043B\u0435\u043D\u0438\u0435" }), SP_JSX.jsxs("div", { className: "dai-field", children: [SP_JSX.jsx("span", { className: "dai-label", children: "\u0426\u0432\u0435\u0442\u043E\u0432\u0430\u044F \u0442\u0435\u043C\u0430" }), SP_JSX.jsx(DFL.Focusable, { className: "dai-swatches", "flow-children": "horizontal", children: themes.map(theme => SP_JSX.jsxs(DFL.DialogButton, { className: "dai-button dai-swatch" + (appearance.theme === theme.id ? " dai-selected" : ""), "aria-pressed": appearance.theme === theme.id, onClick: () => setAppearanceChoice("theme", theme.id), children: [SP_JSX.jsx("span", { className: "dai-swatch-dot", style: { background: theme.swatch } }), theme.name] }, theme.id)) })] }), SP_JSX.jsx(Segmented, { label: "\u0421\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F", value: appearance.bubbles, options: bubbleStyles, onChange: id => setAppearanceChoice("bubbles", id) }), SP_JSX.jsx(Segmented, { label: "\u041F\u043B\u043E\u0442\u043D\u043E\u0441\u0442\u044C", value: appearance.density, options: densities, onChange: id => setAppearanceChoice("density", id) }), SP_JSX.jsx(Segmented, { label: "\u041A\u043E\u043C\u043F\u043E\u043D\u043E\u0432\u043A\u0430", value: appearance.layout, options: layouts, onChange: id => setAppearanceChoice("layout", id) }), appearance.layout === "split" && !fullscreen && SP_JSX.jsx("p", { className: "dai-muted", children: "\u0414\u0432\u0435 \u043A\u043E\u043B\u043E\u043D\u043A\u0438 \u0432\u043A\u043B\u044E\u0447\u0430\u0442\u0441\u044F \u0432 \u0440\u0435\u0436\u0438\u043C\u0435 \u00AB\u041D\u0430 \u0432\u0435\u0441\u044C \u044D\u043A\u0440\u0430\u043D\u00BB." })] }), SP_JSX.jsxs("section", { className: "dai-section dai-custom-ai", children: [SP_JSX.jsx("h3", { children: "\u0421\u0432\u043E\u0439 \u043E\u0431\u043B\u0430\u0447\u043D\u044B\u0439 \u0418\u0418" }), SP_JSX.jsx("p", { className: "dai-muted", children: "\u041F\u043E\u0434\u043E\u0439\u0434\u0451\u0442 \u043B\u044E\u0431\u043E\u0439 \u043E\u0431\u043B\u0430\u0447\u043D\u044B\u0439 \u0441\u0435\u0440\u0432\u0438\u0441 \u0441 OpenAI-\u0441\u043E\u0432\u043C\u0435\u0441\u0442\u0438\u043C\u044B\u043C API: OpenAI, Gemini, Groq, Mistral, DeepSeek, xAI, OpenRouter \u0438 \u0434\u0440\u0443\u0433\u0438\u0435. \u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435 \u0433\u043E\u0442\u043E\u0432\u044B\u0439 \u0430\u0434\u0440\u0435\u0441 \u0438\u043B\u0438 \u0443\u043A\u0430\u0436\u0438\u0442\u0435 \u0441\u0432\u043E\u0439 (\u0442\u043E\u043B\u044C\u043A\u043E https). \u041B\u043E\u043A\u0430\u043B\u044C\u043D\u044B\u0435 \u0441\u0435\u0440\u0432\u0435\u0440\u044B \u043D\u0435 \u043F\u043E\u0434\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u044E\u0442\u0441\u044F." }), SP_JSX.jsx(DFL.Focusable, { className: "dai-quick", "flow-children": "horizontal", children: (data?.presets || []).map(p => SP_JSX.jsx(Action, { onClick: () => setCustom(old => ({ ...old, name: old.name || p.name.split(" · ")[0], url: p.url })), children: p.name }, p.url)) }), SP_JSX.jsx(DFL.TextField, { value: custom.name, placeholder: "\u041D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 (\u043D\u0430\u043F\u0440\u0438\u043C\u0435\u0440, Groq)", onChange: e => setCustom({ ...custom, name: e.target.value }) }), SP_JSX.jsx(DFL.TextField, { value: custom.url, placeholder: "\u0410\u0434\u0440\u0435\u0441 API, \u043D\u0430\u043F\u0440\u0438\u043C\u0435\u0440 https://api.groq.com/openai/v1", onChange: e => setCustom({ ...custom, url: e.target.value }) }), SP_JSX.jsx(DFL.TextField, { value: custom.models, placeholder: "\u041C\u043E\u0434\u0435\u043B\u0438 \u0447\u0435\u0440\u0435\u0437 \u0437\u0430\u043F\u044F\u0442\u0443\u044E (\u043D\u0435\u043E\u0431\u044F\u0437\u0430\u0442\u0435\u043B\u044C\u043D\u043E)", onChange: e => setCustom({ ...custom, models: e.target.value }) }), SP_JSX.jsx(DFL.TextField, { bIsPassword: true, value: custom.key, placeholder: "\u041A\u043B\u044E\u0447 API", onChange: e => setCustom({ ...custom, key: e.target.value }) }), SP_JSX.jsx(Action, { primary: true, disabled: busy || ro || !custom.name.trim() || !custom.url.trim() || !custom.key.trim(), onClick: () => void run(async () => { const result = await customSave(custom.name.trim(), custom.url.trim(), custom.models, custom.key.trim()); setCustom({ name: "", url: "", models: "", key: "" }); accept(await setProvider(result.id)); setNotice("Подключение добавлено"); }), children: "\u0414\u043E\u0431\u0430\u0432\u0438\u0442\u044C \u0438 \u0432\u044B\u0431\u0440\u0430\u0442\u044C" })] }), SP_JSX.jsxs("section", { className: "dai-section dai-text-settings", children: [SP_JSX.jsx("h3", { children: "\u0418\u043D\u0442\u0435\u0440\u0444\u0435\u0439\u0441 \u0438 \u0433\u043E\u043B\u043E\u0441" }), SP_JSX.jsxs("div", { className: "dai-personal-fields", children: [SP_JSX.jsxs("div", { className: "dai-field", children: [SP_JSX.jsx("span", { className: "dai-label", children: "\u041C\u0430\u0441\u0448\u0442\u0430\u0431 \u0447\u0430\u0442\u0430 \u0438 \u043A\u043D\u043E\u043F\u043E\u043A" }), SP_JSX.jsxs(DFL.Focusable, { className: "dai-scale-controls", "flow-children": "horizontal", children: [SP_JSX.jsx(Action, { disabled: textScale <= .7, onClick: () => setTextScale(textScale - .1), children: "\u0410\u2212" }), SP_JSX.jsxs("span", { className: "dai-scale-value", "aria-live": "polite", children: [Math.round(textScale * 100), "%"] }), SP_JSX.jsx(Action, { disabled: textScale >= 1.5, onClick: () => setTextScale(textScale + .1), children: "\u0410+" }), SP_JSX.jsx(Action, { disabled: textScale === 1, onClick: () => setTextScale(1), children: "\u0421\u0431\u0440\u043E\u0441" })] })] }), SP_JSX.jsx(Choice, { label: "\u042F\u0437\u044B\u043A \u0440\u0430\u0441\u043F\u043E\u0437\u043D\u0430\u0432\u0430\u043D\u0438\u044F", value: lang, options: !data?.speechReady ? [{ data: "ru", label: "Русский" }, { data: "en", label: "English" }] : [{ data: "auto", label: "Определять автоматически" }, ...Object.entries(speechLanguages).sort(([a], [b]) => a === "ru" ? -1 : b === "ru" ? 1 : a === "en" ? -1 : b === "en" ? 1 : 0).map(([data, label]) => ({ data, label })), { data: "ru-fast", label: "Русский · экономный" }, { data: "en-fast", label: "English · экономный" }], onChange: value => { setLang(value); localStorage.setItem("codex-game-voice", value); } })] }), data?.speechVersion === 2 && !data.speechReady && SP_JSX.jsx("p", { className: "dai-muted", children: "\u0414\u043B\u044F \u0434\u0440\u0443\u0433\u0438\u0445 \u044F\u0437\u044B\u043A\u043E\u0432 \u0443\u0441\u0442\u0430\u043D\u043E\u0432\u0438\u0442\u0435 \u043C\u043D\u043E\u0433\u043E\u044F\u0437\u044B\u0447\u043D\u0443\u044E \u043C\u043E\u0434\u0435\u043B\u044C: scripts/download-models.sh --accurate-ru" }), SP_JSX.jsxs("div", { className: "dai-game-setting", children: [SP_JSX.jsx("span", { className: "dai-muted", children: "\u0414\u043E\u0431\u0430\u0432\u043B\u044F\u0442\u044C \u0442\u043E\u043B\u044C\u043A\u043E \u043D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u0438\u0433\u0440\u044B" }), SP_JSX.jsx(GameCheckbox, { checked: gameContextEnabled, onChange: toggleGameContext })] }), SP_JSX.jsxs("div", { className: "dai-game-setting", children: [SP_JSX.jsx("span", { className: "dai-muted", children: "\u0421\u043E\u043E\u0431\u0449\u0430\u0442\u044C \u043E \u0433\u043E\u0442\u043E\u0432\u043D\u043E\u0441\u0442\u0438 \u0437\u0430\u0434\u0430\u0447 (\u0443\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u044F Steam)" }), SP_JSX.jsx(GameCheckbox, { checked: notify, onChange: () => { const next = !notify; localStorage.setItem("deck-ai-notify", next ? "on" : "off"); setNotify(next); } })] }), SP_JSX.jsxs("div", { className: "dai-game-setting", children: [SP_JSX.jsx("span", { className: "dai-muted", children: "\u041E\u0442\u043F\u0440\u0430\u0432\u043B\u044F\u0442\u044C \u0433\u043E\u043B\u043E\u0441\u043E\u0432\u043E\u0435 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0435 \u0447\u0435\u0440\u0435\u0437 3 \u0441 \u043F\u043E\u0441\u043B\u0435 \u00AB\u0421\u0442\u043E\u043F\u00BB" }), SP_JSX.jsx(GameCheckbox, { checked: autoSend, onChange: () => { const next = !autoSend; localStorage.setItem("deck-ai-auto-send", next ? "on" : "off"); setAutoSend(next); } })] }), SP_JSX.jsxs("div", { className: "dai-game-setting", children: [SP_JSX.jsx("span", { className: "dai-muted", children: "\u0422\u043E\u043B\u044C\u043A\u043E \u0447\u0442\u0435\u043D\u0438\u0435 (\u0431\u0435\u0437 \u043E\u0442\u043F\u0440\u0430\u0432\u043A\u0438, \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u0439 \u0438 \u043F\u0440\u0430\u0432\u043E\u043A)" }), SP_JSX.jsx(GameCheckbox, { checked: ro, onChange: () => void run(async () => { await setReadOnly(!ro); accept(await snapshot()); }) })] }), SP_JSX.jsxs("div", { className: "dai-field", children: [SP_JSX.jsx("span", { className: "dai-label", children: "\u0411\u044B\u0441\u0442\u0440\u044B\u0435 \u0444\u0440\u0430\u0437\u044B \u26A1 (\u0441\u0442\u0440\u043E\u043A\u0430: \u043D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 | \u0442\u0435\u043A\u0441\u0442)" }), SP_JSX.jsx("textarea", { className: "dai-textarea dai-textarea-small", value: quickSource ?? parseQuickActions(null).map(([a, b]) => a === b ? a : a + " | " + b).join("\n"), onChange: e => { setQuickSource(e.target.value); localStorage.setItem("deck-ai-quick", e.target.value); } })] }), SP_JSX.jsxs(Action, { disabled: busy || !data?.loadedModels, onClick: () => void run(async () => { await unloadModels(); accept(await snapshot()); setNotice("Модели распознавания выгружены из памяти"); }), children: ["\u041E\u0441\u0432\u043E\u0431\u043E\u0434\u0438\u0442\u044C \u043F\u0430\u043C\u044F\u0442\u044C", data?.loadedModels ? ` · загружено моделей: ${data.loadedModels}` : ""] })] })] }), SP_JSX.jsxs("div", { className: "dai-settings-column", children: [SP_JSX.jsxs("section", { className: "dai-section dai-connection-settings", children: [SP_JSX.jsx("h3", { children: "\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u0435 Codex" }), SP_JSX.jsxs("div", { className: "dai-connection-bar", children: [SP_JSX.jsx("p", { className: "dai-muted", children: (data?.active ? "Deck AI работает…" : data?.status) || "Сервер пока недоступен. Можно повторить подключение." }), SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { accept(await refresh()); setNotice("Соединение обновлено"); }), children: busy ? "Подключение…" : "Переподключиться" })] }), (!data || data.provider === "codex") && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(Choice, { label: "\u0423\u0441\u0442\u0440\u043E\u0439\u0441\u0442\u0432\u043E", value: data?.remoteHost || "", options: [{ data: "", label: "Этот Steam Deck" }, ...(data?.sshHosts || []).map(x => ({ data: x, label: x }))], disabled: busy || data?.active, onChange: value => void run(async () => accept(await remoteHost(value))) }), SP_JSX.jsxs("div", { className: "dai-host-entry", children: [SP_JSX.jsx(DFL.TextField, { value: host, placeholder: "\u0414\u0440\u0443\u0433\u043E\u0439 SSH-\u0430\u043B\u0438\u0430\u0441", onChange: e => setHost(e.target.value) }), SP_JSX.jsx(Action, { disabled: busy || !host.trim() || data?.active, onClick: () => void run(async () => { accept(await remoteHost(host.trim())); setHost(""); }), children: "\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0438\u0442\u044C" })] })] })] }), !!data?.sshHosts.length && SP_JSX.jsxs("section", { className: "dai-section dai-watch", children: [SP_JSX.jsx("h3", { children: "\u0421\u043B\u0435\u0434\u0438\u0442\u044C \u0432 \u0444\u043E\u043D\u0435" }), SP_JSX.jsx("p", { className: "dai-muted", children: "\u0423\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u044F \u0438 \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u044F \u0441 \u044D\u0442\u0438\u0445 \u043C\u0430\u0448\u0438\u043D \u043F\u0440\u0438\u0445\u043E\u0434\u044F\u0442, \u0434\u0430\u0436\u0435 \u043A\u043E\u0433\u0434\u0430 \u043E\u043D\u0438 \u043D\u0435 \u0432\u044B\u0431\u0440\u0430\u043D\u044B. \u0414\u043E 5 \u043C\u0430\u0448\u0438\u043D." }), data.sshHosts.map(name => { const on = !!data.watchHosts?.includes(name); return SP_JSX.jsxs("div", { className: "dai-game-setting", children: [SP_JSX.jsxs("span", { className: "dai-muted", children: [name, on && data.watchStatus?.[name] ? " · " + { connected: "на связи", offline: "нет связи", connecting: "подключаюсь", active: "выбрана" }[data.watchStatus[name]] : ""] }), SP_JSX.jsx(GameCheckbox, { checked: on, onChange: () => void run(async () => { const next = on ? (data.watchHosts || []).filter(x => x !== name) : [...(data.watchHosts || []), name]; await watchHosts(next); accept(await snapshot()); }) })] }, name); })] }), SP_JSX.jsxs("section", { className: "dai-section dai-share", children: [SP_JSX.jsx("h3", { children: "\u0414\u043E\u0441\u0442\u0443\u043F \u0441 \u0434\u0440\u0443\u0433\u043E\u0433\u043E \u043A\u043E\u043C\u043F\u044C\u044E\u0442\u0435\u0440\u0430" }), SP_JSX.jsx("p", { className: "dai-muted", children: "\u0423\u043F\u0440\u0430\u0432\u043B\u044F\u0439\u0442\u0435 \u0437\u0430\u0434\u0430\u0447\u0430\u043C\u0438 \u044D\u0442\u043E\u0433\u043E Deck \u0441 Mac \u0438\u043B\u0438 \u041F\u041A \u043F\u043E SSH: \u043A\u043E\u043C\u0430\u043D\u0434\u044B \u0438\u0437 \u0432\u0430\u0448\u0435\u0433\u043E Codex \u043F\u043E\u044F\u0432\u044F\u0442\u0441\u044F \u0437\u0434\u0435\u0441\u044C." }), SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => setShare(await shareStatus())), children: "\u041F\u043E\u043A\u0430\u0437\u0430\u0442\u044C \u0434\u0430\u043D\u043D\u044B\u0435 \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u044F" }), share && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsxs("p", { className: "dai-muted dai-check " + (share.sshActive ? "ok" : "bad"), children: [share.sshActive ? "✓ SSH-сервер работает" : "✗ SSH-сервер выключен", " \u00B7 \u043A\u043B\u044E\u0447\u0435\u0439: ", share.keys, share.codex ? "" : " · Codex не найден"] }), !share.sshActive && SP_JSX.jsx("p", { className: "dai-muted", children: share.enableHint }), SP_JSX.jsxs("p", { className: "dai-muted", children: ["\u041F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u044C ", share.user, " \u00B7 \u0430\u0434\u0440\u0435\u0441\u0430: ", share.addresses.join(", ") || "не найдены"] }), SP_JSX.jsx("p", { className: "dai-muted", children: "\u041D\u0430 Mac \u0438\u043B\u0438 \u041F\u041A \u0437\u0430\u043F\u0443\u0441\u0442\u0438\u0442\u0435 \u043C\u0430\u0441\u0442\u0435\u0440 connect-deck.py \u0438\u0437 \u0430\u0440\u0445\u0438\u0432\u0430 Remote Control. \u0410\u0434\u0440\u0435\u0441 \u0443\u0441\u0442\u0440\u043E\u0439\u0441\u0442\u0432\u0430 \u0443\u043A\u0430\u0437\u0430\u043D \u0432\u044B\u0448\u0435." }), SP_JSX.jsx("p", { className: "dai-muted", children: "\u041E\u0442\u043F\u0435\u0447\u0430\u0442\u043A\u0438 SSH \u0434\u043B\u044F \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0438 \u043F\u0435\u0440\u0432\u043E\u0433\u043E \u0441\u043E\u0435\u0434\u0438\u043D\u0435\u043D\u0438\u044F:" }), SP_JSX.jsx("pre", { className: "dai-snippet", children: (share.fingerprints || []).join("\n") || "SSH ещё не создал ключи: сначала включите сервер." }), SP_JSX.jsx("p", { className: "dai-muted", children: "\u0414\u043B\u044F \u0440\u0443\u0447\u043D\u043E\u0439 \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438 ~/.ssh/config:" }), SP_JSX.jsx("pre", { className: "dai-snippet", children: share.snippet }), SP_JSX.jsx("p", { className: "dai-muted", children: "\u0412\u0441\u0442\u0430\u0432\u044C\u0442\u0435 \u043F\u0443\u0431\u043B\u0438\u0447\u043D\u044B\u0439 \u043A\u043B\u044E\u0447 \u0438\u0437 \u043C\u0430\u0441\u0442\u0435\u0440\u0430 \u043D\u0430 Mac \u0438\u043B\u0438 \u041F\u041A:" }), SP_JSX.jsx(DFL.TextField, { value: shareKey, placeholder: "ssh-ed25519 AAAA\u2026", onChange: e => setShareKey(e.target.value) }), SP_JSX.jsx(Action, { disabled: busy || ro || !shareKey.trim(), onClick: () => void run(async () => { const result = await shareAddKey(shareKey.trim()); setShareKey(""); setShare(await shareStatus()); setNotice(result.added ? "Ключ добавлен" : "Такой ключ уже есть"); }), children: "\u0420\u0430\u0437\u0440\u0435\u0448\u0438\u0442\u044C \u044D\u0442\u043E\u043C\u0443 \u043A\u043E\u043C\u043F\u044C\u044E\u0442\u0435\u0440\u0443" })] })] }), SP_JSX.jsxs("section", { className: "dai-section dai-diagnostics", children: [SP_JSX.jsx("h3", { children: "\u0414\u0438\u0430\u0433\u043D\u043E\u0441\u0442\u0438\u043A\u0430" }), SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { setChecks(null); const result = await diagnose(); setChecks(result.checks); }), children: busy ? "Проверяю…" : "Проверить подключение" }), checks?.map(check => SP_JSX.jsxs("p", { className: "dai-muted dai-check " + (check.ok ? "ok" : "bad"), children: [check.ok ? "✓" : "✗", " ", check.name, check.detail ? " · " + check.detail : ""] }, check.name))] }), SP_JSX.jsxs("section", { className: "dai-section dai-account-settings", children: [SP_JSX.jsx("h3", { children: "\u0410\u043A\u043A\u0430\u0443\u043D\u0442 ChatGPT" }), SP_JSX.jsxs("div", { className: "dai-account-meta", children: [SP_JSX.jsx("p", { className: "dai-account", children: data?.account?.email || "Вход не выполнен" }), data?.account?.planType && SP_JSX.jsx("p", { className: "dai-muted", children: data.account.planType })] }), SP_JSX.jsxs("div", { className: "dai-account-actions", children: [SP_JSX.jsx(Action, { disabled: busy, onClick: signIn, children: data?.account ? "Сменить аккаунт" : "Войти в аккаунт" }), data?.loginPending && SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { await accountCancelLogin(); setLoginUrl(""); accept(await snapshot()); }), children: "\u041E\u0442\u043C\u0435\u043D\u0438\u0442\u044C \u0432\u0445\u043E\u0434" }), loginUrl && SP_JSX.jsx("p", { className: "dai-login-url", children: loginUrl }), data?.account && SP_JSX.jsx(Action, { disabled: busy, onClick: () => DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: "\u0412\u044B\u0439\u0442\u0438 \u0438\u0437 ChatGPT?", strDescription: "\u0414\u043B\u044F \u0440\u0430\u0431\u043E\u0442\u044B Codex \u043F\u043E\u0442\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044F \u0441\u043D\u043E\u0432\u0430 \u0432\u043E\u0439\u0442\u0438.", strOKButtonText: "\u0412\u044B\u0439\u0442\u0438", strCancelButtonText: "\u041E\u0442\u043C\u0435\u043D\u0430", onOK: () => void run(async () => { await accountLogout(); accept(await refresh()); }) })), children: "\u0412\u044B\u0439\u0442\u0438 \u0438\u0437 \u0430\u043A\u043A\u0430\u0443\u043D\u0442\u0430" })] })] })] })] }) })] })] });
}
let lastEvent = null;
async function showNotifications() {
    try {
        const result = await pollEvents(lastEvent);
        const first = lastEvent === null;
        lastEvent = result.latest;
        // The open panel already shows approvals and results; do not toast on top.
        if (first || panelMounted > 0 || !flag("deck-ai-notify", true))
            return;
        for (const item of result.notifications.slice(-3)) {
            const where = item.host ? " · " + item.host : "";
            toaster.toast({
                title: item.kind === "approval" ? "Deck AI · нужно подтверждение" : item.kind === "failed" ? "Deck AI · ошибка" : item.kind === "cancelled" ? "Deck AI · задача остановлена" : "Deck AI · задача готова",
                body: (item.kind === "approval" && item.summary ? item.summary : item.title) + where,
                critical: item.kind === "approval", duration: item.kind === "approval" ? 15000 : 6000,
                onClick: () => {
                    void (async () => {
                        try {
                            if ((session.snapshot?.remoteHost || "") !== item.host)
                                await remoteHost(item.host);
                            if (item.threadId)
                                session.snapshot = await selectThread(item.threadId);
                        }
                        finally {
                            openFullscreen("chat");
                        }
                    })().catch(() => { });
                }
            });
        }
    }
    catch { }
}
var index = definePlugin(() => {
    routerHook.addRoute(FULLSCREEN_PATH, FullscreenPage, { exact: true });
    void showNotifications();
    const notifier = setInterval(() => void showNotifications(), 2000);
    return { name: "Deck AI", titleView: SP_JSX.jsx("span", { children: "Deck AI" }), content: SP_JSX.jsx(Panel, {}), icon: SP_JSX.jsx("img", { src: logo, alt: "Deck AI", style: { width: 20, height: 20, objectFit: "contain" } }), onDismount() {
            if (returnToPanel)
                clearTimeout(returnToPanel);
            clearInterval(notifier);
            routerHook.removeRoute(FULLSCREEN_PATH);
        } };
});

export { index as default };
