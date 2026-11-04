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

var css = "/* The Quick Access panel is about 300px wide. Keep all rules local to Deck AI. */\n.dai-root{--dai-line:rgba(255,255,255,.12);--dai-muted:#aab6c3;display:flex;flex-direction:column;gap:8px;box-sizing:border-box;width:100%;max-width:100%;height:clamp(300px,calc(100vh - 180px),580px);min-height:0;padding:0 12px 10px;color:#f0f4f8;font-size:14px;line-height:1.4;overflow:hidden}\n.dai-root *{box-sizing:border-box}.dai-root h3{font-size:14px;font-weight:650;margin:0 0 9px}.dai-root p{margin:0}.dai-tabs{display:flex;gap:4px;flex-shrink:0;border-bottom:1px solid var(--dai-line);padding-bottom:7px}.dai-tab{flex:1;min-width:0}.dai-root .dai-button{display:flex;align-items:center;justify-content:center;gap:6px;width:100%;min-width:0;min-height:38px;height:auto;padding:8px 9px;border-radius:3px;font-size:13px;line-height:1.3;white-space:normal;overflow-wrap:anywhere;box-shadow:none}.dai-tab .dai-button{background:transparent;color:var(--dai-muted);padding:9px 4px;font-size:12px;gap:5px}.dai-tab.selected .dai-button{background:#34495d;color:white}.dai-root .dai-button:focus,.dai-root .dai-button.gpfocus,.dai-root .dai-focused{outline:2px solid #fff;outline-offset:-2px;background:#dce8f1;color:#152638}.dai-root .dai-primary{background:#1a77b9;color:white}.dai-root .dai-button:disabled{opacity:.4}.dai-status{display:flex;align-items:center;gap:6px;min-height:18px;font-size:11px;color:var(--dai-muted);flex-shrink:0}.dai-status>span:nth-child(2){overflow:hidden;white-space:nowrap;text-overflow:ellipsis;flex:1;min-width:0}.dai-status small{max-width:75px;overflow:hidden;text-overflow:ellipsis}.dai-dot{height:6px;width:6px;border-radius:50%;background:#69c49a;flex-shrink:0}.dai-dot.offline{background:#e59980}.dai-dot.working{background:#e4c56e}.dai-page{display:flex;flex-direction:column;flex:1;min-height:0;overflow:hidden}.dai-scroll{flex:1;min-height:0;overflow-y:auto;overflow-x:hidden;padding:2px 2px 10px;scrollbar-width:thin}.dai-stack{display:flex;flex-direction:column;gap:10px}.dai-section{display:flex;flex-direction:column;gap:10px;padding:4px 0 14px;border-bottom:1px solid var(--dai-line);flex-shrink:0}.dai-section:last-child{border:0}.dai-section h3{color:#fff;margin:0}.dai-field{display:flex;flex-direction:column;gap:5px;min-width:0}.dai-label{font-size:12px;color:var(--dai-muted)}.dai-field>div{min-width:0;max-width:100%}.dai-muted{font-size:12px;color:var(--dai-muted);line-height:1.45}.dai-account{overflow-wrap:anywhere}.dai-login-url{overflow-wrap:anywhere;font-size:11px;user-select:text}.dai-messages{flex:1;min-height:65px;overflow-y:auto;overflow-x:hidden;scrollbar-width:thin;display:flex;flex-direction:column;gap:9px;padding:3px 2px 10px}.dai-message{flex-shrink:0;padding:10px;border-radius:4px;background:rgba(255,255,255,.045);overflow-wrap:anywhere;white-space:pre-wrap;font-size:14px;line-height:1.5;user-select:text}.dai-message.user{background:rgba(100,165,220,.12)}.dai-message small{display:block;font-size:10px;font-weight:650;color:var(--dai-muted);margin-bottom:4px}.dai-empty{margin:auto 0;text-align:center;padding:12px 3px;color:var(--dai-muted)}.dai-empty>svg{font-size:23px;opacity:.7;margin:0 0 8px}.dai-empty h3{color:#fff;margin-bottom:5px}.dai-empty p{font-size:13px;line-height:1.6;margin-bottom:12px}.dai-composer{display:flex;flex-direction:column;gap:8px;flex-shrink:0;border-top:1px solid var(--dai-line);padding-top:9px}.dai-compose-actions{display:flex;gap:5px}.dai-compose-actions>.dai-button{flex:1;padding:9px 4px;font-size:12px}.dai-compose-actions>.dai-button svg{flex-shrink:0}.dai-attachments{display:flex;flex-direction:column;gap:4px;max-height:80px;overflow-y:auto}.dai-attachments .dai-button{font-size:11px;min-height:30px;justify-content:flex-start}.dai-banner{display:flex;flex-direction:column;gap:5px;flex-shrink:0;padding:7px;background:#502f36;border-radius:3px;font-size:12px}.dai-banner>span{max-height:65px;overflow-y:auto;overflow-wrap:anywhere}.dai-banner .dai-button{min-height:26px;padding:4px;font-size:11px}.dai-notice{font-size:11px;color:#a9cddb;flex-shrink:0;max-height:40px;overflow-y:auto}.dai-history-item .dai-button{flex-direction:column;align-items:flex-start;text-align:left;padding:10px}.dai-history-item.selected{border-left:3px solid #66b5ef}.dai-history-item small{font-size:10px;color:var(--dai-muted)}.dai-failed{display:flex;flex-direction:column;gap:6px;font-size:12px;color:#ffc9b7}\n@media(max-height:600px){.dai-root{height:clamp(260px,calc(100vh - 140px),460px);gap:5px}.dai-root .dai-button{min-height:34px}.dai-composer{gap:5px;padding-top:6px}}\n\n.dai-stack-content{display:flex;flex-direction:column;gap:10px;flex-shrink:0}.dai-message-list{display:flex;flex-direction:column;gap:9px;min-height:100%;flex-shrink:0}.dai-settings-grid{flex-shrink:0}\n\n.dai-root .dai-button{box-sizing:border-box!important}\n.dai-tab:first-child{flex:.8}.dai-tab:last-child{flex:1.25}.dai-tab .dai-button{white-space:nowrap}.dai-tab .dai-button svg{flex-shrink:0}\n/* Gaming Mode's .DialogButton rules have higher specificity than desktop\n   styles. Override only this plugin's dimensions so Steam cannot impose its\n   160px minimum on each control in the 300px Quick Access column. */\n.dai-root .dai-button.DialogButton{width:100%!important;min-width:0!important;max-width:100%!important;min-height:38px!important;height:auto!important;padding:8px 6px!important;font-size:13px!important;line-height:1.3!important;border-radius:4px!important}\n.dai-root .dai-tab .dai-button.DialogButton{font-size:12px!important;padding:8px 4px!important;background:transparent!important;color:var(--dai-muted)!important}\n.dai-root .dai-tab.selected .dai-button.DialogButton{background:#34495d!important;color:#fff!important}\n.dai-root .dai-button.dai-primary{background:#1a77b9!important;color:#fff!important}\n.dai-root .dai-button.DialogButton.gpfocus,.dai-root .dai-button.DialogButton:focus{background:#dce8f1!important;color:#152638!important}\n.dai-viewbar{display:flex;align-items:center;gap:6px;flex-shrink:0;min-width:0}.dai-viewbar>.dai-status{flex:1;min-width:0}.dai-root .dai-viewbar>.dai-button.DialogButton{width:126px!important;flex-shrink:0;font-size:11px!important;min-height:32px!important;padding:6px 4px!important}\n/* Full-screen UI uses Steam's 854x534 CSS viewport on a 1280x800 Deck.\n   Reserve its top/bottom bars and keep primary controls visible together. */\n.dai-draft-field{min-width:0;width:100%}\n.dai-root.dai-fullscreen{position:fixed;inset:40px 0;width:100vw;max-width:none;height:calc(100vh - 80px);max-height:none;min-height:0;margin:0;padding:10px 16px;background:#101923;gap:6px;font-size:12px;line-height:1.35}\n.dai-full-header{display:flex;align-items:center;gap:8px;flex-shrink:0;min-width:0}\n.dai-full-brand{flex:1;min-width:0;display:flex;align-items:center;gap:12px}\n.dai-full-brand h1{font-size:18px;line-height:1.2;margin:0;white-space:nowrap}\n.dai-full-brand span{font-size:11px;color:var(--dai-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}\n.dai-root.dai-fullscreen .dai-button.DialogButton{font-size:12px!important;min-height:32px!important;padding:6px 8px!important;line-height:1.3!important}\n.dai-root.dai-fullscreen .dai-full-header>.dai-button.DialogButton{width:106px!important;flex:none}\n.dai-fullscreen>.dai-tabs{max-width:540px;padding-bottom:5px;gap:6px}\n.dai-root.dai-fullscreen .dai-tab .dai-button.DialogButton{font-size:12px!important;padding:6px!important;min-height:30px!important}\n.dai-fullscreen>.dai-viewbar{display:none}\n.dai-fullscreen .dai-page{width:100%;max-width:1200px;margin:0 auto}\n.dai-fullscreen .dai-scroll{padding:0 2px 2px}\n.dai-fullscreen .dai-message{padding:9px 12px;font-size:13px;line-height:1.45}\n.dai-fullscreen .dai-message-list{gap:7px}\n.dai-fullscreen .dai-message small{font-size:10px;margin-bottom:3px}\n.dai-fullscreen .dai-messages{padding:2px 2px 8px}\n.dai-fullscreen .dai-composer{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:6px;padding-top:7px}\n.dai-fullscreen .dai-composer>.dai-attachments,.dai-fullscreen .dai-composer>.dai-muted{grid-column:1/-1}\n.dai-fullscreen .dai-compose-actions{gap:5px;justify-content:flex-end}\n.dai-root.dai-fullscreen .dai-compose-actions>.dai-button.DialogButton{width:auto!important;flex:none;padding:6px 9px!important}\n.dai-fullscreen .dai-settings-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;align-items:start}\n.dai-settings-column{display:flex;flex-direction:column;gap:9px;min-width:0}\n.dai-fullscreen .dai-section,.dai-fullscreen .dai-section:last-child{padding:10px;border:1px solid var(--dai-line);border-radius:5px;background:rgba(255,255,255,.025);gap:7px;min-width:0}\n.dai-fullscreen .dai-section h3{font-size:14px;line-height:1.25;margin:0}\n.dai-model-fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}\n.dai-fullscreen .dai-label{font-size:11px;line-height:1.25}\n.dai-fullscreen .dai-field{gap:4px;min-width:0}\n.dai-fullscreen .dai-field>button[role=combobox]{width:100%!important;max-width:100%!important;min-width:0!important;min-height:32px!important;height:32px!important;padding:5px 8px!important;font-size:12px!important;line-height:1.3!important;box-sizing:border-box!important}\n.dai-fullscreen .DialogDropDown_CurrentDisplay{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px!important;line-height:1.3!important}\n.dai-fullscreen .dai-field>button[role=combobox] svg{width:14px;height:14px;flex-shrink:0}\n.dai-fullscreen input.DialogInput{font-size:12px!important;line-height:1.3!important;height:32px!important;min-height:32px!important;max-width:100%;box-sizing:border-box!important;padding:6px 8px!important}\n.dai-fullscreen .DialogInput_Wrapper{min-width:0;width:100%;margin:0}\n.dai-fullscreen .dai-muted{font-size:11px;line-height:1.35}\n.dai-connection-bar{display:flex;align-items:center;gap:8px;min-width:0}\n.dai-connection-bar>.dai-muted{flex:1;min-width:0;overflow-wrap:anywhere}\n.dai-root.dai-fullscreen .dai-connection-bar>.dai-button.DialogButton{width:140px!important;flex:none;font-size:11px!important}\n.dai-host-entry{display:grid;grid-template-columns:minmax(0,1fr) 100px;gap:6px;align-items:center}\n.dai-account-meta{display:flex;align-items:center;gap:8px;min-width:0}\n.dai-account-meta>.dai-account{flex:1;min-width:0;font-size:12px}\n.dai-account-actions{display:flex;gap:6px;flex-wrap:wrap}\n.dai-account-actions>.dai-button{flex:1;min-width:0}\n.dai-account-actions>.dai-login-url{width:100%;font-size:10px}\n@media(max-width:650px){.dai-root.dai-fullscreen{padding:8px;gap:5px}.dai-fullscreen .dai-settings-grid{grid-template-columns:minmax(0,1fr)}.dai-full-brand span{display:none}.dai-root.dai-fullscreen .dai-full-header>.dai-button.DialogButton{width:96px!important}.dai-fullscreen .dai-composer{grid-template-columns:minmax(0,1fr)}.dai-fullscreen .dai-compose-actions{justify-content:stretch}.dai-root.dai-fullscreen .dai-compose-actions>.dai-button.DialogButton{flex:1}}\n\n/* Scale reading text without enlarging navigation in the narrow Steam panel. */\n.dai-root .dai-message{font-size:calc(14px * var(--dai-text-scale,1))}\n.dai-root.dai-fullscreen .dai-message{font-size:calc(13px * var(--dai-text-scale,1))}\n.dai-root .dai-message small{font-size:calc(10px * var(--dai-text-scale,1))}\n.dai-root .dai-label,.dai-root .dai-muted{font-size:calc(12px * var(--dai-text-scale,1))}\n.dai-root.dai-fullscreen .dai-label,.dai-root.dai-fullscreen .dai-muted{font-size:calc(11px * var(--dai-text-scale,1))}\n.dai-root .dai-section h3{font-size:calc(14px * var(--dai-text-scale,1))}\n.dai-root input.DialogInput,.dai-root .DialogDropDown_CurrentDisplay{font-size:calc(12px * var(--dai-text-scale,1))!important;line-height:1.3!important}\n.dai-root input.DialogInput{min-height:calc(20px + 12px * var(--dai-text-scale,1))!important;height:auto!important}\n.dai-root .dai-field>button[role=combobox]{min-height:calc(20px + 12px * var(--dai-text-scale,1))!important;height:auto!important}\n.dai-scale-controls{display:flex;align-items:center;gap:6px;min-width:0}\n.dai-scale-value{flex:1;min-width:44px;text-align:center;font-size:calc(13px * var(--dai-text-scale,1));font-variant-numeric:tabular-nums}\n.dai-root .dai-scale-controls>.dai-button.DialogButton{width:52px!important;flex:none}\n.dai-root .dai-scale-controls>.dai-button.DialogButton:last-child{width:70px!important}\n\n/* Smaller text also frees vertical space for the conversation. Keep enlarged\n   text independent so navigation stays usable in the narrow Quick Access UI. */\n.dai-root{--dai-density:min(1,var(--dai-text-scale,1));gap:calc(8px * var(--dai-density))}\n.dai-root .dai-tabs{gap:calc(4px * var(--dai-density));padding-bottom:calc(7px * var(--dai-density))}\n.dai-root .dai-button.DialogButton{font-size:calc(13px * var(--dai-density))!important;min-height:calc(38px * var(--dai-density))!important;padding:calc(8px * var(--dai-density)) calc(6px * var(--dai-density))!important;gap:calc(6px * var(--dai-density))}\n.dai-root .dai-tab .dai-button.DialogButton{font-size:calc(12px * var(--dai-density))!important;padding:calc(8px * var(--dai-density)) calc(4px * var(--dai-density))!important}\n.dai-root .dai-viewbar>.dai-button.DialogButton{width:calc(126px * var(--dai-density))!important;min-height:calc(32px * var(--dai-density))!important;font-size:calc(11px * var(--dai-density))!important}\n.dai-root .dai-composer{gap:calc(8px * var(--dai-density));padding-top:calc(9px * var(--dai-density))}\n.dai-root .dai-message{padding:calc(10px * var(--dai-density));line-height:1.4}\n.dai-root .dai-message-list{gap:calc(9px * var(--dai-density))}\n.dai-root input.DialogInput{min-height:calc(32px * var(--dai-density))!important;padding:calc(6px * var(--dai-density)) calc(8px * var(--dai-density))!important}\n.dai-root.dai-fullscreen{gap:calc(6px * var(--dai-density));padding:calc(10px * var(--dai-density)) 16px}\n.dai-root.dai-fullscreen .dai-button.DialogButton{font-size:calc(12px * var(--dai-density))!important;min-height:calc(32px * var(--dai-density))!important;padding:calc(6px * var(--dai-density)) calc(8px * var(--dai-density))!important}\n.dai-root.dai-fullscreen .dai-tab .dai-button.DialogButton{min-height:calc(30px * var(--dai-density))!important}\n.dai-root.dai-fullscreen .dai-composer{gap:calc(6px * var(--dai-density));padding-top:calc(7px * var(--dai-density))}\n.dai-root.dai-fullscreen .dai-message{padding:calc(9px * var(--dai-density)) calc(12px * var(--dai-density))}\n.dai-root.dai-fullscreen .dai-message-list{gap:calc(7px * var(--dai-density))}\n.dai-root .dai-empty p{font-size:calc(13px * var(--dai-text-scale,1))}\n\n/* Keep the top and bottom chat controls shallow in both Decky views. */\n.dai-root .dai-message{font-size:calc(13px * var(--dai-text-scale,1))}\n.dai-root.dai-fullscreen .dai-message{font-size:calc(12px * var(--dai-text-scale,1))}\n.dai-root .dai-tabs{padding-bottom:calc(4px * var(--dai-density))}\n.dai-root .dai-tab .dai-button.DialogButton,\n.dai-root .dai-compose-actions>.dai-button.DialogButton,\n.dai-root.dai-fullscreen .dai-tab .dai-button.DialogButton,\n.dai-root.dai-fullscreen .dai-compose-actions>.dai-button.DialogButton{min-height:22px!important;padding:3px 5px!important;font-size:calc(11px * var(--dai-density))!important;line-height:1.2!important;gap:4px}\n.dai-root .dai-viewbar>.dai-button.DialogButton{min-height:22px!important;padding:3px 4px!important}\n.dai-root.dai-fullscreen .dai-full-header>.dai-button.DialogButton{min-height:22px!important;padding:3px 6px!important;font-size:calc(11px * var(--dai-density))!important}\n.dai-root .dai-compose-actions{gap:4px}\n.dai-root .dai-composer{gap:4px;padding-top:4px}\n.dai-root.dai-fullscreen .dai-composer{gap:4px;padding-top:4px}\n.dai-root .dai-composer input.DialogInput{min-height:24px!important;padding:4px 6px!important}\n\n/* Settings use four aligned cards: service and connection, then personal\n   preferences and account. Card rows share their height rather than drifting. */\n.dai-fullscreen .dai-settings-grid{grid-template-areas:\"model connection\" \"personal account\";gap:12px;align-items:stretch;width:100%}\n.dai-fullscreen .dai-settings-column{display:contents}\n.dai-fullscreen .dai-model-settings{grid-area:model}\n.dai-fullscreen .dai-connection-settings{grid-area:connection}\n.dai-fullscreen .dai-text-settings{grid-area:personal}\n.dai-fullscreen .dai-account-settings{grid-area:account}\n.dai-fullscreen .dai-section,.dai-fullscreen .dai-section:last-child{padding:12px;gap:10px;border-color:rgba(170,190,210,.16);background:#16212d;border-radius:7px}\n.dai-fullscreen .dai-section h3{padding-bottom:8px;border-bottom:1px solid var(--dai-line);font-size:12px;color:#dce8f3;letter-spacing:.15px}\n.dai-fullscreen .dai-model-fields{gap:10px 12px}\n.dai-fullscreen .dai-personal-fields{display:grid;grid-template-columns:1.15fr 1fr;gap:12px;align-items:start}\n.dai-fullscreen .dai-scale-controls{gap:4px;min-height:32px}\n.dai-root.dai-fullscreen .dai-scale-controls>.dai-button.DialogButton{width:36px!important;min-height:30px!important;padding:5px 4px!important}\n.dai-root.dai-fullscreen .dai-scale-controls>.dai-button.DialogButton:last-child{width:48px!important}\n.dai-fullscreen .dai-scale-value{min-width:30px;font-size:11px}\n.dai-fullscreen .dai-connection-bar{min-height:30px}\n.dai-fullscreen .dai-account-meta{min-height:32px;flex-wrap:wrap}\n.dai-fullscreen .dai-account-meta>.dai-account{font-size:11px}\n.dai-fullscreen .dai-account-actions{margin-top:auto}\n.dai-fullscreen .dai-field>button[role=combobox]{background:#223243!important;border-radius:4px!important}\n.dai-fullscreen .dai-settings input.DialogInput{background:#223243!important;border-radius:4px!important}\n@media(max-width:650px){.dai-fullscreen .dai-settings-grid{grid-template-columns:minmax(0,1fr);grid-template-areas:\"model\" \"connection\" \"personal\" \"account\"}.dai-fullscreen .dai-personal-fields{grid-template-columns:minmax(0,1fr)}}\n\n/* Fill Decky's actual content slot, including after reopening or resizing.\n   Its generated wrappers otherwise add 16px padding and a viewport clamp. */\ndiv:has(> div > .dai-root:not(.dai-fullscreen)){display:flex!important;flex-direction:column!important;height:100%!important;min-height:0!important;box-sizing:border-box!important}\ndiv:has(> div > .dai-root:not(.dai-fullscreen))>div:not(:has(>.dai-root)){flex-shrink:0}\ndiv:has(> .dai-root:not(.dai-fullscreen)){display:flex!important;flex-direction:column!important;flex:1!important;min-height:0!important;height:auto!important;padding-top:0!important;overflow:hidden}\n.dai-root:not(.dai-fullscreen){height:100%!important;max-height:none!important;min-height:0!important;flex:1;padding-bottom:4px}\n.dai-root:not(.dai-fullscreen)>.dai-page{flex:1;min-height:0}\n.dai-root:not(.dai-fullscreen) .dai-messages{flex:1;min-height:0}\n.dai-root:not(.dai-fullscreen) .dai-composer{margin-top:auto;flex-shrink:0}\n\n/* Decky's sticky title casts a shadow below its layout box. Keep tabs clear\n   of that overlay while the outer panel still fills the available height. */\n.dai-root:not(.dai-fullscreen){padding-top:16px}\n\n.dai-game-setting{display:flex;align-items:center;gap:8px;border-top:1px solid var(--dai-line);padding-top:8px;margin-top:2px}\n.dai-game-setting>.dai-muted{flex:1;min-width:0}\n.dai-root.dai-fullscreen .dai-game-setting>.dai-button.DialogButton{width:82px!important;flex:none}\n.dai-game-context h3{display:flex;align-items:center;gap:6px}\n\n/* Dictation has its own preview; only finalized speech enters the draft. */\n.dai-voice-preview{display:flex;align-items:flex-start;gap:7px;padding:7px 8px;background:rgba(211,55,65,.12);border:1px solid rgba(239,86,96,.45);border-radius:4px;flex-shrink:0;min-width:0;grid-column:1/-1}\n.dai-record-dot{width:7px;height:7px;flex:none;background:#ff5362;border-radius:50%;margin-top:3px;box-shadow:0 0 5px rgba(255,83,98,.45)}\n.dai-voice-preview>div{display:flex;flex-direction:column;gap:3px;min-width:0;flex:1}\n.dai-voice-preview strong{font-size:10px;color:#ff9ca4;line-height:1.2}\n.dai-voice-preview>div>span{font-size:calc(12px * var(--dai-text-scale,1));line-height:1.35;white-space:pre-wrap;overflow-wrap:anywhere;max-height:54px;overflow-y:auto;color:#f5e9eb}\n.dai-root .dai-button.DialogButton.dai-recording{background:#aa2635!important;color:#fff!important;box-shadow:inset 0 0 0 1px #ff7a86!important;opacity:1}\n.dai-root .dai-button.DialogButton.dai-recording:focus,.dai-root .dai-button.DialogButton.dai-recording.gpfocus{background:#cf3546!important;outline:2px solid #fff;outline-offset:-2px}\n\n.dai-game-check{flex:none;min-width:0}\n.dai-root .dai-game-check>.dai-button.DialogButton{width:62px!important;min-height:22px!important;padding:3px 4px!important;font-size:10px!important;gap:4px}\n.dai-check-box{display:inline-flex;align-items:center;justify-content:center;width:12px;height:12px;border:1px solid currentColor;border-radius:2px;font-size:11px;line-height:1;flex:none}\n.dai-game-check[aria-checked=true] .dai-check-box{background:#64b9ef;color:#122432;border-color:#64b9ef}\n\n.dai-message{position:relative}\n.dai-message-tools{position:absolute;top:3px;right:4px;opacity:0;pointer-events:none;transition:opacity .1s}\n.dai-message:hover .dai-message-tools,.dai-message:focus-within .dai-message-tools,.dai-message.dai-focused .dai-message-tools,.dai-message.gpfocus .dai-message-tools{opacity:1;pointer-events:auto}\n.dai-root .dai-message-tools .dai-button.DialogButton,.dai-root.dai-fullscreen .dai-message-tools .dai-button.DialogButton{width:auto!important;min-height:18px!important;padding:2px 5px!important;font-size:9px!important;gap:3px;background:#26394b}\n.dai-latest{flex:none;align-self:center;padding:3px 0}\n.dai-root .dai-latest .dai-button.DialogButton{width:auto!important;min-height:22px!important;padding:3px 8px!important;font-size:10px!important}\n.dai-queue-state{grid-column:1/-1}\n\n.dai-message-attachments{display:flex;flex-wrap:wrap;gap:6px;min-width:0;margin-top:6px}\n.dai-message-attachment{min-width:0;max-width:100%}\n.dai-root .dai-image-button.DialogButton{padding:0!important;min-height:0!important;width:auto!important;max-width:100%;background:transparent!important;overflow:hidden;border-radius:5px}\n.dai-image-button img{display:block;width:auto;max-width:100%;max-height:160px;object-fit:contain}\n.dai-fullscreen .dai-image-button img{max-height:240px}\n.dai-image-expanded{display:block;max-width:100%;max-height:65vh;object-fit:contain;margin:auto}\n\n.dai-queue-summary{grid-column:1/-1;min-width:0}\n.dai-root .dai-queue-summary .dai-button.DialogButton{min-height:20px!important;padding:2px 5px!important;font-size:10px!important}\n.dai-queue-item{display:flex;flex-direction:column;gap:5px;min-width:0}\n.dai-queue-item strong,.dai-queue-item small{overflow-wrap:anywhere}\n.dai-queue-text{white-space:pre-wrap;overflow-wrap:anywhere;font-size:calc(11px * var(--dai-text-scale,1));line-height:1.4}\n\n.dai-root .dai-queue-item>strong{font-size:12px;line-height:1.3}\n.dai-root .dai-queue-item>small{font-size:10px;line-height:1.3}\n.dai-root .dai-queue-item .dai-button.DialogButton{min-height:24px!important;padding:3px 5px!important;font-size:11px!important}\n.dai-running-count{color:#e4c56e;white-space:nowrap}.dai-history-item.running .dai-button>span{display:flex;align-items:center;gap:6px}.dai-history-item.running .dai-dot{animation:dai-pulse 1.4s ease-in-out infinite}@keyframes dai-pulse{50%{opacity:.35}}\n.dai-message.tool{background:rgba(255,255,255,.025);padding:6px 8px}.dai-message.tool pre{margin:0;font:11px/1.4 monospace;white-space:pre-wrap;overflow-wrap:anywhere;color:var(--dai-muted)}.dai-approvals{display:flex;flex-direction:column;gap:6px;flex-shrink:0}.dai-approval{display:flex;flex-direction:column;gap:5px;padding:8px;background:#4a3d1f;border-radius:3px;font-size:12px}.dai-quick{display:grid;grid-template-columns:1fr 1fr;gap:5px}.dai-check.ok{color:#8fd1ac}.dai-check.bad{color:#f0a58c}\n.dai-textarea{width:100%;min-height:220px;resize:vertical;box-sizing:border-box;background:#0e141b;color:#e5edf4;border:1px solid var(--dai-line);border-radius:3px;padding:8px;font:12px/1.5 monospace}.dai-textarea-small{min-height:90px}.dai-textarea:focus{outline:2px solid #fff}\n.dai-snippet{margin:0;padding:6px;background:#0e141b;border-radius:3px;font:11px/1.4 monospace;white-space:pre-wrap;user-select:text;overflow-wrap:anywhere}\n\n/* ===== Appearance layer: colour themes, density, message style, layouts =====\n   Tokens (--t-*) are set per data-theme on .dai-root. Rules below are scoped\n   with [data-theme] so they win over the structural rules above without\n   changing them. */\n.dai-root,.dai-root[data-theme=ocean]{--t-bg:#101923;--t-card:#16212d;--t-input:#223243;--t-btn:rgba(255,255,255,.07);--t-accent:#1a77b9;--t-accent-text:#fff;--t-tab-on:#34495d;--t-tab-on-text:#fff;--t-user:#1d3347;--t-assistant:#17222e;--t-text:#f0f4f8;--t-muted:#aab6c3;--t-line:rgba(255,255,255,.12);--t-focus-bg:#dce8f1;--t-focus-text:#152638;--t-focus-ring:#fff;--t-warn:#4a3d1f;--t-warn-line:#e4c56e;--t-bad:#502f36;--t-ok:#69c49a;--t-working:#e4c56e;--t-offline:#e59980;--t-notice:#a9cddb;--t-thumb:#3b4d5f;--dai-radius:10px;--dai-radius-sm:7px}\n.dai-root[data-theme=graphite]{--t-bg:#15171a;--t-card:#1e2125;--t-input:#2a2e33;--t-btn:rgba(255,255,255,.07);--t-accent:#8aa0b8;--t-accent-text:#10151a;--t-tab-on:#363c43;--t-tab-on-text:#fff;--t-user:#2b3138;--t-assistant:#1b1e22;--t-text:#ececec;--t-muted:#a2a9b0;--t-line:rgba(255,255,255,.11);--t-focus-bg:#ececec;--t-focus-text:#15171a;--t-focus-ring:#8aa0b8;--t-warn:#3d3a2c;--t-bad:#46302f;--t-notice:#b7c4d1;--t-thumb:#444a51}\n.dai-root[data-theme=violet]{--t-bg:#14111f;--t-card:#1d1830;--t-input:#2a2344;--t-btn:rgba(200,180,255,.09);--t-accent:#8b6cf0;--t-accent-text:#fff;--t-tab-on:#3a3060;--t-tab-on-text:#fff;--t-user:#2c2350;--t-assistant:#1a1629;--t-text:#efeaff;--t-muted:#b2a8d0;--t-line:rgba(190,170,255,.16);--t-focus-bg:#e7deff;--t-focus-text:#241a4a;--t-focus-ring:#fff;--t-warn:#44381f;--t-bad:#4d2a3a;--t-notice:#c9bcf5;--t-thumb:#463b72}\n.dai-root[data-theme=forest]{--t-bg:#0f1a15;--t-card:#15241c;--t-input:#1f3328;--t-btn:rgba(160,255,200,.07);--t-accent:#2fa66a;--t-accent-text:#06150d;--t-tab-on:#25433a;--t-tab-on-text:#fff;--t-user:#1c3a2c;--t-assistant:#14231b;--t-text:#e9f4ee;--t-muted:#9fb8aa;--t-line:rgba(160,230,190,.15);--t-focus-bg:#dcf2e5;--t-focus-text:#0d2a1b;--t-focus-ring:#fff;--t-warn:#423c1d;--t-bad:#4a2f2f;--t-notice:#a9dcc0;--t-thumb:#2f4a3b}\n.dai-root[data-theme=amber]{--t-bg:#1a140c;--t-card:#251c10;--t-input:#33271a;--t-btn:rgba(255,220,160,.07);--t-accent:#d99a2b;--t-accent-text:#1c1204;--t-tab-on:#4a3a1c;--t-tab-on-text:#fff;--t-user:#3a2d14;--t-assistant:#221a0f;--t-text:#f6eee0;--t-muted:#c2b394;--t-line:rgba(255,215,150,.15);--t-focus-bg:#f7e7c6;--t-focus-text:#2b1d06;--t-focus-ring:#fff;--t-warn:#4a3a14;--t-bad:#4e2f2a;--t-notice:#e0c48a;--t-thumb:#54421f}\n.dai-root[data-theme=rose]{--t-bg:#1c1015;--t-card:#281820;--t-input:#38222d;--t-btn:rgba(255,190,210,.07);--t-accent:#e0577d;--t-accent-text:#fff;--t-tab-on:#50263a;--t-tab-on-text:#fff;--t-user:#43202f;--t-assistant:#25151c;--t-text:#fbeaf0;--t-muted:#cfa9b8;--t-line:rgba(255,170,200,.15);--t-focus-bg:#fbdbe6;--t-focus-text:#40101f;--t-focus-ring:#fff;--t-warn:#4a3a1f;--t-bad:#5a2430;--t-notice:#f0b6c9;--t-thumb:#5a3041}\n.dai-root[data-theme=light]{--t-bg:#f3f6f9;--t-card:#fff;--t-input:#e9eff5;--t-btn:rgba(20,60,100,.08);--t-accent:#1a77b9;--t-accent-text:#fff;--t-tab-on:#dbe8f3;--t-tab-on-text:#10304a;--t-user:#dbeaf7;--t-assistant:#fff;--t-text:#1b2733;--t-muted:#5a6b7b;--t-line:rgba(20,40,60,.14);--t-focus-bg:#1a77b9;--t-focus-text:#fff;--t-focus-ring:#0d4f7d;--t-warn:#fff1cf;--t-warn-line:#c98a12;--t-bad:#fde3e3;--t-ok:#1f8a5b;--t-working:#b7791f;--t-offline:#c2543a;--t-notice:#1c6aa3;--t-thumb:#b9c6d3}\n.dai-root[data-theme]{--dai-line:var(--t-line);--dai-muted:var(--t-muted);background:var(--t-bg)!important;color:var(--t-text);border-radius:var(--dai-radius)}\n.dai-root[data-theme].dai-fullscreen{border-radius:0}\n.dai-root[data-theme] h3,.dai-root[data-theme] .dai-section h3,.dai-root[data-theme] .dai-empty h3,.dai-root[data-theme].dai-fullscreen .dai-section h3{color:var(--t-text)}\n/* Buttons */\n.dai-root[data-theme] .dai-button.DialogButton{background:var(--t-btn)!important;color:var(--t-text)!important;border-radius:var(--dai-radius-sm)!important;transition:background .12s}\n.dai-root[data-theme] .dai-button.DialogButton:disabled{opacity:.45}\n.dai-root[data-theme] .dai-image-button.DialogButton{background:transparent!important}\n.dai-root[data-theme] .dai-tab .dai-button.DialogButton{background:transparent!important;color:var(--t-muted)!important;border-radius:999px!important}\n.dai-root[data-theme] .dai-tab.selected .dai-button.DialogButton{background:var(--t-tab-on)!important;color:var(--t-tab-on-text)!important;font-weight:650}\n.dai-root[data-theme] .dai-button.dai-primary.DialogButton,.dai-root[data-theme] .dai-button.DialogButton.dai-selected{background:var(--t-accent)!important;color:var(--t-accent-text)!important}\n.dai-root[data-theme] .dai-button.DialogButton.dai-recording{background:#aa2635!important;color:#fff!important}\n.dai-root[data-theme] .dai-button.DialogButton.gpfocus,.dai-root[data-theme] .dai-button.DialogButton:focus,.dai-root[data-theme] .dai-focused{background:var(--t-focus-bg)!important;color:var(--t-focus-text)!important;outline:2px solid var(--t-focus-ring)!important;outline-offset:-2px}\n/* Tab bar as a pill; optional bottom placement (thumb-friendly) */\n.dai-root[data-theme] .dai-tabs{background:var(--t-card);border:1px solid var(--t-line);border-radius:999px;padding:3px;gap:3px}\n.dai-root[data-layout=bottom] .dai-tabs{order:50}\n.dai-root[data-layout=bottom] .dai-page{order:10}\n/* Status */\n.dai-root[data-theme] .dai-dot{background:var(--t-ok)}\n.dai-root[data-theme] .dai-dot.working{background:var(--t-working)}\n.dai-root[data-theme] .dai-dot.offline{background:var(--t-offline)}\n.dai-root[data-theme] .dai-running-count{color:var(--t-working)}\n.dai-root[data-theme] .dai-notice{color:var(--t-notice)}\n.dai-root[data-theme] .dai-banner{background:var(--t-bad);border-radius:var(--dai-radius-sm)}\n.dai-root[data-theme] .dai-approval{background:var(--t-warn);border-left:3px solid var(--t-warn-line,#e4c56e);border-radius:var(--dai-radius-sm)}\n.dai-root[data-theme] .dai-check.ok{color:var(--t-ok)}\n/* Cards for settings blocks and the composer */\n.dai-root[data-theme] .dai-section,.dai-root[data-theme] .dai-section:last-child,.dai-root[data-theme].dai-fullscreen .dai-section,.dai-root[data-theme].dai-fullscreen .dai-section:last-child{background:var(--t-card);border:1px solid var(--t-line);border-radius:var(--dai-radius);padding:12px}\n.dai-root[data-theme] .dai-composer,.dai-root[data-theme].dai-fullscreen .dai-composer{background:var(--t-card);border:1px solid var(--t-line);border-radius:var(--dai-radius);padding:8px}\n.dai-root[data-theme] input.DialogInput,.dai-root[data-theme] .dai-field>button[role=combobox],.dai-root[data-theme].dai-fullscreen .dai-settings input.DialogInput,.dai-root[data-theme].dai-fullscreen .dai-field>button[role=combobox]{background:var(--t-input)!important;color:var(--t-text)!important;border-radius:var(--dai-radius-sm)!important}\n.dai-root[data-theme] .dai-textarea,.dai-root[data-theme] .dai-snippet{background:var(--t-input);color:var(--t-text);border-color:var(--t-line)}\n.dai-root[data-theme] .dai-game-check[aria-checked=true] .dai-check-box{background:var(--t-accent);border-color:var(--t-accent);color:var(--t-accent-text)}\n.dai-root[data-theme] .dai-history-item.selected{border-left-color:var(--t-accent)}\n.dai-root[data-theme] .dai-scroll,.dai-root[data-theme] .dai-messages{scrollbar-color:var(--t-thumb) transparent}\n/* Messages: three styles */\n.dai-root[data-theme] .dai-message{background:var(--t-assistant);color:var(--t-text);border-radius:var(--dai-radius)}\n.dai-root[data-theme] .dai-message.user{background:var(--t-user)}\n.dai-root[data-theme] .dai-message.tool{background:transparent;border:1px dashed var(--t-line)}\n.dai-root[data-theme] .dai-message small{color:var(--t-muted);letter-spacing:.3px;text-transform:uppercase}\n.dai-root[data-theme] .dai-message.user small{color:var(--t-accent)}\n.dai-root[data-theme][data-bubbles=bubbles] .dai-message.user{align-self:flex-end;max-width:92%;border-bottom-right-radius:3px}\n.dai-root[data-theme][data-bubbles=bubbles] .dai-message.assistant{align-self:flex-start;max-width:97%;border-bottom-left-radius:3px;border:1px solid var(--t-line)}\n.dai-root[data-theme][data-bubbles=flat] .dai-message,.dai-root[data-theme][data-bubbles=flat] .dai-message.user{background:transparent;border-radius:0;border-bottom:1px solid var(--t-line);padding-left:2px;padding-right:2px}\n.dai-root[data-theme][data-bubbles=cards] .dai-message{border-left:3px solid var(--t-line)}\n.dai-root[data-theme][data-bubbles=cards] .dai-message.user{border-left-color:var(--t-accent)}\n.dai-root[data-theme][data-bubbles=cards] .dai-message.assistant{border-left-color:var(--t-working)}\n/* Density */\n.dai-root[data-density=compact] .dai-message{padding:6px 9px;line-height:1.35}\n.dai-root[data-density=compact] .dai-message-list,.dai-root[data-density=compact] .dai-messages{gap:5px}\n.dai-root[data-density=roomy] .dai-message{padding:14px 16px;line-height:1.6}\n.dai-root[data-density=roomy] .dai-message-list,.dai-root[data-density=roomy] .dai-messages{gap:14px}\n.dai-root[data-density=roomy] .dai-section{padding:16px}\n/* Quick toolbar above the conversation */\n.dai-toolbar{display:flex;gap:6px;flex-shrink:0}\n.dai-root .dai-toolbar>.dai-button.DialogButton{flex:1 1 0;min-height:36px!important;padding:4px 2px!important;flex-direction:column;gap:1px!important;font-size:10px!important;line-height:1.1!important;border-radius:var(--dai-radius-sm)!important}\n.dai-toolbar .dai-button svg{font-size:13px}\n.dai-toolbar .dai-button span{max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}\n.dai-root.dai-fullscreen .dai-toolbar>.dai-button.DialogButton{flex-direction:row;gap:6px!important;min-height:26px!important;font-size:11px!important}\n/* Two columns: chat list beside the conversation (full screen only) */\n.dai-chat-layout{display:flex;flex-direction:column;flex:1;min-height:0;min-width:0}\n.dai-chat-main{display:flex;flex-direction:column;flex:1;min-height:0;min-width:0;gap:inherit}\n.dai-root[data-layout=split].dai-fullscreen .dai-chat-layout{flex-direction:row;gap:10px}\n.dai-split-side{flex:none;width:230px;min-height:0;overflow-y:auto;border:1px solid var(--t-line);border-radius:var(--dai-radius);background:var(--t-card);padding:8px}\n.dai-split-side .dai-history-item .dai-button{padding:7px 9px!important;min-height:30px!important}\n.dai-split-side .dai-history-item span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:190px;display:flex;align-items:center;gap:6px}\n/* Appearance settings */\n.dai-swatches{display:flex;flex-wrap:wrap;gap:6px}\n.dai-root .dai-swatches>.dai-button.DialogButton{width:auto!important;flex:1 1 28%;min-width:78px;min-height:28px!important;font-size:11px!important;gap:6px!important}\n.dai-swatch-dot{width:12px;height:12px;border-radius:50%;flex:none;border:1px solid rgba(128,128,128,.6)}\n.dai-segmented{display:flex;gap:4px}\n.dai-root .dai-segmented>.dai-button.DialogButton{flex:1;min-height:28px!important;font-size:11px!important}\n/* Keep \"Отправить\" on one line in the narrow panel: give the main action more room. */\n.dai-root:not(.dai-fullscreen) .dai-compose-actions>.dai-button.dai-primary.DialogButton{flex:1.9;white-space:nowrap!important}\n.dai-root:not(.dai-fullscreen) .dai-compose-actions>.dai-button.DialogButton{padding-left:3px!important;padding-right:3px!important;white-space:nowrap!important}\n\n/* Keep long permission requests inside the available chat area. */\n.dai-chat-main.has-approvals .dai-messages{min-height:0}\n.dai-approvals{flex:0 1 auto;min-height:48px;max-height:45%;overflow-y:auto;overflow-x:hidden;scrollbar-width:thin}\n.dai-approval{flex-shrink:0;overflow-wrap:anywhere}\n\n.dai-repair .dai-section{display:flex;flex-direction:column;gap:10px;overflow-wrap:anywhere}\n.dai-repair h4{margin:0;font-size:1.15em}\n.dai-repair-checks{margin:0;padding-left:1.25em}\n.dai-repair-checks li+li{margin-top:5px}\n.dai-repair-preview{max-width:100%;max-height:220px;object-fit:contain;align-self:flex-start;border-radius:8px}\n.dai-repair-qr{width:min(100%,260px);height:auto;align-self:flex-start;image-rendering:pixelated}\n.dai-repair-confirm{display:flex;flex-direction:column;gap:8px;padding:12px;border:1px solid var(--dai-line);border-radius:8px}\n.dai-repair-actions{display:flex;gap:8px;flex-wrap:wrap}\n.dai-root .dai-repair-actions>.dai-button.DialogButton{width:auto!important;flex:1}\n.dai-repair-error{color:#ffb9b3}\n";

const key = (thread) => 'codex-game-draft:' + (thread || 'new');
function draftOwner(view) {
    if (!view)
        return "";
    if (view.provider === "codex" && !view.remoteHost)
        return view.threadId;
    return JSON.stringify([view.provider, view.remoteHost || "", view.threadId]);
}
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
// The quick panel and the full-screen page can be mounted together. Share
// their periodic reads without reusing a response across navigation.
function createSnapshotReader(request, now = () => performance.now()) {
    let cached = null;
    return (revision, maxAge) => {
        if (cached?.revision === revision && (cached.received === null || now() - cached.received < maxAge)) {
            return cached.value;
        }
        // Decky serializes every argument to Python. Do not pass the fulfillment
        // value (undefined) as an extra argument to the no-argument snapshot RPC.
        const entry = { revision, received: null, value: Promise.resolve().then(() => request()) };
        cached = entry;
        return entry.value = entry.value.then(value => {
            entry.received = now();
            return value;
        }, error => {
            if (cached === entry)
                cached = null;
            throw error;
        });
    };
}
function appendAttachments(current, incoming) {
    const seen = new Set(current.map(image => image.path));
    const unique = [];
    for (const image of incoming) {
        if (!seen.has(image.path)) {
            seen.add(image.path);
            unique.push(image);
        }
    }
    const accepted = unique.slice(0, Math.max(0, 5 - current.length));
    return { images: [...current, ...accepted], added: accepted.length, omitted: unique.length - accepted.length };
}

function sameChat(job, threadId, host = "") {
    return job.threadId === threadId && (job.host || "") === host;
}
function queueCounts(jobs, threadId, host = "") {
    const waiting = jobs.filter(job => job.status === 'queued');
    const current = waiting.filter(job => sameChat(job, threadId, host)).length;
    return { waiting: waiting.length, current, other: waiting.length - current };
}
function queueStatus(job, now = Date.now()) {
    const began = job.startedAt ?? job.createdAt;
    if (job.status === 'sending')
        return began && now - began * 1000 > 15 * 60 * 1000 ? 'Долго выполняется · проверьте чат' : 'Выполняется';
    return { queued: 'Ожидает отправки', recovering: 'Проверяется на сервере', error: 'Ошибка' }[job.status] || job.status;
}
function chatFailures(jobs, threadId, host = "") {
    return jobs.filter(job => job.status === 'error' && sameChat(job, threadId, host));
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

const repairStatus = callable("repair_status");
const inspect = callable("repair_inspect");
const screenshots = callable("repair_screenshots");
const command = callable("repair_command");
function steamAccount() {
    try {
        const id = window.friendStore?.currentUserSteamID || window.uiStore?.currentUserSteamID;
        return typeof id === "string" ? id : id?.ConvertTo64BitString() || "";
    }
    catch {
        return "";
    }
}
const shortcutType = 1073741824;
function libraryGames(query, preferredId) {
    const search = query.trim().toLocaleLowerCase();
    return (window.appStore?.allApps || [])
        .filter(app => app.appid > 0 && (app.local_per_client_data?.installed || (app.size_on_disk ?? 0) > 0
        || app.appid === preferredId || app.app_type === shortcutType)
        && (app.app_type === 1 || app.app_type === 8 || app.app_type === shortcutType)
        && typeof app.display_name === "string" && app.display_name.toLocaleLowerCase() !== "deck ai"
        && (!search || app.display_name.toLocaleLowerCase().includes(search) || String(app.appid) === search))
        .sort((a, b) => Number(b.appid === preferredId) - Number(a.appid === preferredId)
        || (b.rt_last_time_locally_played || 0) - (a.rt_last_time_locally_played || 0)
        || a.display_name.localeCompare(b.display_name))
        .slice(0, 30)
        .map(app => ({ appId: app.appid, name: app.display_name, shortcut: app.app_type === shortcutType }));
}
async function liveDetails(appId) {
    const overview = window.appStore?.GetAppOverviewByAppID(appId);
    const apps = window.SteamClient?.Apps;
    if (!overview || !apps?.RegisterForAppDetails)
        throw new Error("Steam не предоставил свойства игры.");
    const shortcut = overview.app_type === shortcutType;
    let subscription;
    let timer;
    try {
        const details = await new Promise((resolve, reject) => {
            timer = setTimeout(() => reject(new Error("Steam не ответил на запрос свойств игры.")), 3500);
            subscription = apps.RegisterForAppDetails(appId, data => {
                if (!data)
                    return;
                const options = shortcut ? data.strShortcutLaunchOptions : data.strLaunchOptions;
                if (data.unAppID === appId && typeof options === "string")
                    resolve(data);
            });
        });
        return {
            appId, name: overview.display_name, shortcut,
            options: shortcut ? details.strShortcutLaunchOptions : details.strLaunchOptions,
            proton: details.strCompatToolDisplayName || details.strCompatToolName || "",
            shortcutExe: shortcut ? details.strShortcutExe : undefined,
            folderIndex: shortcut ? undefined : details.iInstallFolder,
        };
    }
    finally {
        clearTimeout(timer);
        subscription?.unregister();
    }
}
async function libraryPath(game) {
    if (game.shortcut)
        return game.shortcutExe || "";
    const folder = window.SteamClient?.InstallFolder;
    if (!folder?.GetInstallFolders)
        return "";
    let timer;
    try {
        const timeout = new Promise(resolve => { timer = setTimeout(() => resolve(null), 1000); });
        const folders = await Promise.race([folder.GetInstallFolders(), timeout]);
        return folders?.find(item => item.nFolderIndex === game.folderIndex)?.strFolderPath || "";
    }
    catch {
        return "";
    }
    finally {
        clearTimeout(timer);
    }
}
const emptyView = { case: null, remote: { state: "off" } };
let view = emptyView;
let viewOwner = "";
const listeners = new Set();
let wakePolling = () => { };
function repairView() { return viewOwner === steamAccount() ? view : emptyView; }
function subscribeRepair(listener) {
    listeners.add(listener);
    listener(repairView());
    wakePolling();
    return () => { listeners.delete(listener); };
}
function publish(value, account) {
    if (account === viewOwner && JSON.stringify(value) === JSON.stringify(view))
        return;
    view = value;
    viewOwner = account;
    for (const listener of listeners)
        listener(view);
}
async function inspectLaunch(appId, screenshot) {
    const account = steamAccount();
    if (!account)
        throw new Error("Откройте библиотеку Steam под своим аккаунтом.");
    const game = await liveDetails(appId);
    game.location = await libraryPath(game);
    if (steamAccount() !== account)
        throw new Error("Аккаунт Steam изменился.");
    try {
        return await inspect(account, game, screenshot);
    }
    finally {
        wakePolling();
    }
}
function repairScreenshots(appId, shortcut) { return screenshots(steamAccount(), appId, shortcut); }
async function repairCommand(caseId, verb, fields = {}) {
    try {
        return await command(steamAccount(), caseId, verb, fields);
    }
    finally {
        wakePolling();
    }
}
async function originalLaunchOptions(caseId) {
    const result = await repairCommand(caseId, "original");
    return result.options;
}
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));
function startRepairPolling() {
    let disposed = false;
    let polling = false;
    let requested = false;
    let failures = 0;
    let timer;
    const sameAccount = (account) => !disposed && steamAccount() === account;
    const needsPolling = () => listeners.size > 0 || view.remote.state !== "off"
        || view.case?.action?.state === "approved" || view.case?.action?.state === "running";
    function schedule(ms) {
        clearTimeout(timer);
        if (!disposed)
            timer = setTimeout(() => void tick(), ms);
    }
    function wake() {
        if (polling)
            requested = true;
        else
            schedule(0);
    }
    wakePolling = wake;
    async function tick() {
        if (polling || disposed)
            return;
        polling = true;
        const account = steamAccount();
        let failed = false;
        try {
            const value = await repairStatus(account);
            if (!sameAccount(account))
                return;
            publish(value, account);
            failures = 0;
            const current = value.case;
            const action = current?.action;
            if (!current || !action || action.state === "pending")
                return;
            const live = await liveDetails(current.appId);
            if (!sameAccount(account))
                return;
            const actionId = action.id;
            if (action.state === "running") {
                await command(account, current.id, "observe", { actionId, options: live.options, shortcut: live.shortcut });
                return;
            }
            const apps = window.SteamClient?.Apps;
            const setter = live.shortcut ? apps?.SetShortcutLaunchOptions : apps?.SetAppLaunchOptions;
            if (!setter)
                throw new Error("В этой версии Steam сброс параметров недоступен.");
            const claim = await command(account, current.id, "claim", {
                actionId, options: live.options, shortcut: live.shortcut,
            });
            if (!claim || !sameAccount(account))
                return;
            const beforeWrite = await liveDetails(current.appId);
            if (!sameAccount(account))
                return;
            if (beforeWrite.options !== live.options || beforeWrite.shortcut !== live.shortcut) {
                await command(account, current.id, "abort", { actionId, options: beforeWrite.options, shortcut: live.shortcut });
                return;
            }
            setter.call(apps, current.appId, claim.options);
            for (let attempt = 0; attempt < 4; attempt++) {
                await delay(400);
                if (!sameAccount(account))
                    return;
                const observed = await liveDetails(current.appId);
                if (!sameAccount(account))
                    return;
                if (observed.options === claim.options) {
                    await command(account, current.id, "observe", {
                        actionId, options: observed.options, shortcut: observed.shortcut,
                    });
                    return;
                }
            }
        }
        catch (error) {
            failed = true;
            failures++;
            if (sameAccount(account))
                publish({ ...repairView(), error: String(error) }, account);
        }
        finally {
            polling = false;
            if (requested) {
                requested = false;
                schedule(0);
            }
            else if (needsPolling() || failed) {
                const recoveryDelay = needsPolling() ? 3500 : Math.min(30000, 3500 * 2 ** Math.min(failures - 1, 4));
                schedule(failed ? recoveryDelay : 1800);
            }
        }
    }
    void tick();
    return () => {
        disposed = true;
        clearTimeout(timer);
        if (wakePolling === wake)
            wakePolling = () => { };
    };
}

//---------------------------------------------------------------------
//
// QR Code Generator for JavaScript
//
// Copyright (c) 2009 Kazuhiko Arase
//
// URL: http://www.d-project.com/
//
// Licensed under the MIT license:
//  http://www.opensource.org/licenses/mit-license.php
//
// The word 'QR Code' is registered trademark of
// DENSO WAVE INCORPORATED
//  http://www.denso-wave.com/qrcode/faqpatent-e.html
//
//---------------------------------------------------------------------

//---------------------------------------------------------------------
// qrcode
//---------------------------------------------------------------------

/**
 * qrcode
 * @param typeNumber 1 to 40
 * @param errorCorrectionLevel 'L','M','Q','H'
 */
const qrcode = function(typeNumber, errorCorrectionLevel) {

  const PAD0 = 0xEC;
  const PAD1 = 0x11;

  let _typeNumber = typeNumber;
  const _errorCorrectionLevel = QRErrorCorrectionLevel[errorCorrectionLevel];
  let _modules = null;
  let _moduleCount = 0;
  let _dataCache = null;
  const _dataList = [];

  const _this = {};

  const makeImpl = function(test, maskPattern) {

    _moduleCount = _typeNumber * 4 + 17;
    _modules = function(moduleCount) {
      const modules = new Array(moduleCount);
      for (let row = 0; row < moduleCount; row += 1) {
        modules[row] = new Array(moduleCount);
        for (let col = 0; col < moduleCount; col += 1) {
          modules[row][col] = null;
        }
      }
      return modules;
    }(_moduleCount);

    setupPositionProbePattern(0, 0);
    setupPositionProbePattern(_moduleCount - 7, 0);
    setupPositionProbePattern(0, _moduleCount - 7);
    setupPositionAdjustPattern();
    setupTimingPattern();
    setupTypeInfo(test, maskPattern);

    if (_typeNumber >= 7) {
      setupTypeNumber(test);
    }

    if (_dataCache == null) {
      _dataCache = createData(_typeNumber, _errorCorrectionLevel, _dataList);
    }

    mapData(_dataCache, maskPattern);
  };

  const setupPositionProbePattern = function(row, col) {

    for (let r = -1; r <= 7; r += 1) {

      if (row + r <= -1 || _moduleCount <= row + r) continue;

      for (let c = -1; c <= 7; c += 1) {

        if (col + c <= -1 || _moduleCount <= col + c) continue;

        if ( (0 <= r && r <= 6 && (c == 0 || c == 6) )
            || (0 <= c && c <= 6 && (r == 0 || r == 6) )
            || (2 <= r && r <= 4 && 2 <= c && c <= 4) ) {
          _modules[row + r][col + c] = true;
        } else {
          _modules[row + r][col + c] = false;
        }
      }
    }
  };

  const getBestMaskPattern = function() {

    let minLostPoint = 0;
    let pattern = 0;

    for (let i = 0; i < 8; i += 1) {

      makeImpl(true, i);

      const lostPoint = QRUtil.getLostPoint(_this);

      if (i == 0 || minLostPoint > lostPoint) {
        minLostPoint = lostPoint;
        pattern = i;
      }
    }

    return pattern;
  };

  const setupTimingPattern = function() {

    for (let r = 8; r < _moduleCount - 8; r += 1) {
      if (_modules[r][6] != null) {
        continue;
      }
      _modules[r][6] = (r % 2 == 0);
    }

    for (let c = 8; c < _moduleCount - 8; c += 1) {
      if (_modules[6][c] != null) {
        continue;
      }
      _modules[6][c] = (c % 2 == 0);
    }
  };

  const setupPositionAdjustPattern = function() {

    const pos = QRUtil.getPatternPosition(_typeNumber);

    for (let i = 0; i < pos.length; i += 1) {

      for (let j = 0; j < pos.length; j += 1) {

        const row = pos[i];
        const col = pos[j];

        if (_modules[row][col] != null) {
          continue;
        }

        for (let r = -2; r <= 2; r += 1) {

          for (let c = -2; c <= 2; c += 1) {

            if (r == -2 || r == 2 || c == -2 || c == 2
                || (r == 0 && c == 0) ) {
              _modules[row + r][col + c] = true;
            } else {
              _modules[row + r][col + c] = false;
            }
          }
        }
      }
    }
  };

  const setupTypeNumber = function(test) {

    const bits = QRUtil.getBCHTypeNumber(_typeNumber);

    for (let i = 0; i < 18; i += 1) {
      const mod = (!test && ( (bits >> i) & 1) == 1);
      _modules[Math.floor(i / 3)][i % 3 + _moduleCount - 8 - 3] = mod;
    }

    for (let i = 0; i < 18; i += 1) {
      const mod = (!test && ( (bits >> i) & 1) == 1);
      _modules[i % 3 + _moduleCount - 8 - 3][Math.floor(i / 3)] = mod;
    }
  };

  const setupTypeInfo = function(test, maskPattern) {

    const data = (_errorCorrectionLevel << 3) | maskPattern;
    const bits = QRUtil.getBCHTypeInfo(data);

    // vertical
    for (let i = 0; i < 15; i += 1) {

      const mod = (!test && ( (bits >> i) & 1) == 1);

      if (i < 6) {
        _modules[i][8] = mod;
      } else if (i < 8) {
        _modules[i + 1][8] = mod;
      } else {
        _modules[_moduleCount - 15 + i][8] = mod;
      }
    }

    // horizontal
    for (let i = 0; i < 15; i += 1) {

      const mod = (!test && ( (bits >> i) & 1) == 1);

      if (i < 8) {
        _modules[8][_moduleCount - i - 1] = mod;
      } else if (i < 9) {
        _modules[8][15 - i - 1 + 1] = mod;
      } else {
        _modules[8][15 - i - 1] = mod;
      }
    }

    // fixed module
    _modules[_moduleCount - 8][8] = (!test);
  };

  const mapData = function(data, maskPattern) {

    let inc = -1;
    let row = _moduleCount - 1;
    let bitIndex = 7;
    let byteIndex = 0;
    const maskFunc = QRUtil.getMaskFunction(maskPattern);

    for (let col = _moduleCount - 1; col > 0; col -= 2) {

      if (col == 6) col -= 1;

      while (true) {

        for (let c = 0; c < 2; c += 1) {

          if (_modules[row][col - c] == null) {

            let dark = false;

            if (byteIndex < data.length) {
              dark = ( ( (data[byteIndex] >>> bitIndex) & 1) == 1);
            }

            const mask = maskFunc(row, col - c);

            if (mask) {
              dark = !dark;
            }

            _modules[row][col - c] = dark;
            bitIndex -= 1;

            if (bitIndex == -1) {
              byteIndex += 1;
              bitIndex = 7;
            }
          }
        }

        row += inc;

        if (row < 0 || _moduleCount <= row) {
          row -= inc;
          inc = -inc;
          break;
        }
      }
    }
  };

  const createBytes = function(buffer, rsBlocks) {

    let offset = 0;

    let maxDcCount = 0;
    let maxEcCount = 0;

    const dcdata = new Array(rsBlocks.length);
    const ecdata = new Array(rsBlocks.length);

    for (let r = 0; r < rsBlocks.length; r += 1) {

      const dcCount = rsBlocks[r].dataCount;
      const ecCount = rsBlocks[r].totalCount - dcCount;

      maxDcCount = Math.max(maxDcCount, dcCount);
      maxEcCount = Math.max(maxEcCount, ecCount);

      dcdata[r] = new Array(dcCount);

      for (let i = 0; i < dcdata[r].length; i += 1) {
        dcdata[r][i] = 0xff & buffer.getBuffer()[i + offset];
      }
      offset += dcCount;

      const rsPoly = QRUtil.getErrorCorrectPolynomial(ecCount);
      const rawPoly = qrPolynomial(dcdata[r], rsPoly.getLength() - 1);

      const modPoly = rawPoly.mod(rsPoly);
      ecdata[r] = new Array(rsPoly.getLength() - 1);
      for (let i = 0; i < ecdata[r].length; i += 1) {
        const modIndex = i + modPoly.getLength() - ecdata[r].length;
        ecdata[r][i] = (modIndex >= 0)? modPoly.getAt(modIndex) : 0;
      }
    }

    let totalCodeCount = 0;
    for (let i = 0; i < rsBlocks.length; i += 1) {
      totalCodeCount += rsBlocks[i].totalCount;
    }

    const data = new Array(totalCodeCount);
    let index = 0;

    for (let i = 0; i < maxDcCount; i += 1) {
      for (let r = 0; r < rsBlocks.length; r += 1) {
        if (i < dcdata[r].length) {
          data[index] = dcdata[r][i];
          index += 1;
        }
      }
    }

    for (let i = 0; i < maxEcCount; i += 1) {
      for (let r = 0; r < rsBlocks.length; r += 1) {
        if (i < ecdata[r].length) {
          data[index] = ecdata[r][i];
          index += 1;
        }
      }
    }

    return data;
  };

  const createData = function(typeNumber, errorCorrectionLevel, dataList) {

    const rsBlocks = QRRSBlock.getRSBlocks(typeNumber, errorCorrectionLevel);

    const buffer = qrBitBuffer();

    for (let i = 0; i < dataList.length; i += 1) {
      const data = dataList[i];
      buffer.put(data.getMode(), 4);
      buffer.put(data.getLength(), QRUtil.getLengthInBits(data.getMode(), typeNumber) );
      data.write(buffer);
    }

    // calc num max data.
    let totalDataCount = 0;
    for (let i = 0; i < rsBlocks.length; i += 1) {
      totalDataCount += rsBlocks[i].dataCount;
    }

    if (buffer.getLengthInBits() > totalDataCount * 8) {
      throw 'code length overflow. ('
        + buffer.getLengthInBits()
        + '>'
        + totalDataCount * 8
        + ')';
    }

    // end code
    if (buffer.getLengthInBits() + 4 <= totalDataCount * 8) {
      buffer.put(0, 4);
    }

    // padding
    while (buffer.getLengthInBits() % 8 != 0) {
      buffer.putBit(false);
    }

    // padding
    while (true) {

      if (buffer.getLengthInBits() >= totalDataCount * 8) {
        break;
      }
      buffer.put(PAD0, 8);

      if (buffer.getLengthInBits() >= totalDataCount * 8) {
        break;
      }
      buffer.put(PAD1, 8);
    }

    return createBytes(buffer, rsBlocks);
  };

  _this.addData = function(data, mode) {

    mode = mode || 'Byte';

    let newData = null;

    switch(mode) {
    case 'Numeric' :
      newData = qrNumber(data);
      break;
    case 'Alphanumeric' :
      newData = qrAlphaNum(data);
      break;
    case 'Byte' :
      newData = qr8BitByte(data);
      break;
    case 'Kanji' :
      newData = qrKanji(data);
      break;
    default :
      throw 'mode:' + mode;
    }

    _dataList.push(newData);
    _dataCache = null;
  };

  _this.isDark = function(row, col) {
    if (row < 0 || _moduleCount <= row || col < 0 || _moduleCount <= col) {
      throw row + ',' + col;
    }
    return _modules[row][col];
  };

  _this.getModuleCount = function() {
    return _moduleCount;
  };

  _this.make = function() {
    if (_typeNumber < 1) {
      let typeNumber = 1;

      for (; typeNumber < 40; typeNumber++) {
        const rsBlocks = QRRSBlock.getRSBlocks(typeNumber, _errorCorrectionLevel);
        const buffer = qrBitBuffer();

        for (let i = 0; i < _dataList.length; i++) {
          const data = _dataList[i];
          buffer.put(data.getMode(), 4);
          buffer.put(data.getLength(), QRUtil.getLengthInBits(data.getMode(), typeNumber) );
          data.write(buffer);
        }

        let totalDataCount = 0;
        for (let i = 0; i < rsBlocks.length; i++) {
          totalDataCount += rsBlocks[i].dataCount;
        }

        if (buffer.getLengthInBits() <= totalDataCount * 8) {
          break;
        }
      }

      _typeNumber = typeNumber;
    }

    makeImpl(false, getBestMaskPattern() );
  };

  _this.createTableTag = function(cellSize, margin) {

    cellSize = cellSize || 2;
    margin = (typeof margin == 'undefined')? cellSize * 4 : margin;

    let qrHtml = '';

    qrHtml += '<table style="';
    qrHtml += ' border-width: 0px; border-style: none;';
    qrHtml += ' border-collapse: collapse;';
    qrHtml += ' padding: 0px; margin: ' + margin + 'px;';
    qrHtml += '">';
    qrHtml += '<tbody>';

    for (let r = 0; r < _this.getModuleCount(); r += 1) {

      qrHtml += '<tr>';

      for (let c = 0; c < _this.getModuleCount(); c += 1) {
        qrHtml += '<td style="';
        qrHtml += ' border-width: 0px; border-style: none;';
        qrHtml += ' border-collapse: collapse;';
        qrHtml += ' padding: 0px; margin: 0px;';
        qrHtml += ' width: ' + cellSize + 'px;';
        qrHtml += ' height: ' + cellSize + 'px;';
        qrHtml += ' background-color: ';
        qrHtml += _this.isDark(r, c)? '#000000' : '#ffffff';
        qrHtml += ';';
        qrHtml += '"/>';
      }

      qrHtml += '</tr>';
    }

    qrHtml += '</tbody>';
    qrHtml += '</table>';

    return qrHtml;
  };

  _this.createSvgTag = function(cellSize, margin, alt, title) {

    let opts = {};
    if (typeof arguments[0] == 'object') {
      // Called by options.
      opts = arguments[0];
      // overwrite cellSize and margin.
      cellSize = opts.cellSize;
      margin = opts.margin;
      alt = opts.alt;
      title = opts.title;
    }

    cellSize = cellSize || 2;
    margin = (typeof margin == 'undefined')? cellSize * 4 : margin;

    // Compose alt property surrogate
    alt = (typeof alt === 'string') ? {text: alt} : alt || {};
    alt.text = alt.text || null;
    alt.id = (alt.text) ? alt.id || 'qrcode-description' : null;

    // Compose title property surrogate
    title = (typeof title === 'string') ? {text: title} : title || {};
    title.text = title.text || null;
    title.id = (title.text) ? title.id || 'qrcode-title' : null;

    const size = _this.getModuleCount() * cellSize + margin * 2;
    let c, mc, r, mr, qrSvg='', rect;

    rect = 'l' + cellSize + ',0 0,' + cellSize +
      ' -' + cellSize + ',0 0,-' + cellSize + 'z ';

    qrSvg += '<svg version="1.1" xmlns="http://www.w3.org/2000/svg"';
    qrSvg += !opts.scalable ? ' width="' + size + 'px" height="' + size + 'px"' : '';
    qrSvg += ' viewBox="0 0 ' + size + ' ' + size + '" ';
    qrSvg += ' preserveAspectRatio="xMinYMin meet"';
    qrSvg += (title.text || alt.text) ? ' role="img" aria-labelledby="' +
        escapeXml([title.id, alt.id].join(' ').trim() ) + '"' : '';
    qrSvg += '>';
    qrSvg += (title.text) ? '<title id="' + escapeXml(title.id) + '">' +
        escapeXml(title.text) + '</title>' : '';
    qrSvg += (alt.text) ? '<description id="' + escapeXml(alt.id) + '">' +
        escapeXml(alt.text) + '</description>' : '';
    qrSvg += '<rect width="100%" height="100%" fill="white" cx="0" cy="0"/>';
    qrSvg += '<path d="';

    for (r = 0; r < _this.getModuleCount(); r += 1) {
      mr = r * cellSize + margin;
      for (c = 0; c < _this.getModuleCount(); c += 1) {
        if (_this.isDark(r, c) ) {
          mc = c*cellSize+margin;
          qrSvg += 'M' + mc + ',' + mr + rect;
        }
      }
    }

    qrSvg += '" stroke="transparent" fill="black"/>';
    qrSvg += '</svg>';

    return qrSvg;
  };

  _this.createDataURL = function(cellSize, margin) {

    cellSize = cellSize || 2;
    margin = (typeof margin == 'undefined')? cellSize * 4 : margin;

    const size = _this.getModuleCount() * cellSize + margin * 2;
    const min = margin;
    const max = size - margin;

    return createDataURL(size, size, function(x, y) {
      if (min <= x && x < max && min <= y && y < max) {
        const c = Math.floor( (x - min) / cellSize);
        const r = Math.floor( (y - min) / cellSize);
        return _this.isDark(r, c)? 0 : 1;
      } else {
        return 1;
      }
    } );
  };

  _this.createImgTag = function(cellSize, margin, alt) {

    cellSize = cellSize || 2;
    margin = (typeof margin == 'undefined')? cellSize * 4 : margin;

    const size = _this.getModuleCount() * cellSize + margin * 2;

    let img = '';
    img += '<img';
    img += '\u0020src="';
    img += _this.createDataURL(cellSize, margin);
    img += '"';
    img += '\u0020width="';
    img += size;
    img += '"';
    img += '\u0020height="';
    img += size;
    img += '"';
    if (alt) {
      img += '\u0020alt="';
      img += escapeXml(alt);
      img += '"';
    }
    img += '/>';

    return img;
  };

  const escapeXml = function(s) {
    let escaped = '';
    for (let i = 0; i < s.length; i += 1) {
      const c = s.charAt(i);
      switch(c) {
      case '<': escaped += '&lt;'; break;
      case '>': escaped += '&gt;'; break;
      case '&': escaped += '&amp;'; break;
      case '"': escaped += '&quot;'; break;
      default : escaped += c; break;
      }
    }
    return escaped;
  };

  const _createHalfASCII = function(margin) {
    const cellSize = 1;
    margin = (typeof margin == 'undefined')? cellSize * 2 : margin;

    const size = _this.getModuleCount() * cellSize + margin * 2;
    const min = margin;
    const max = size - margin;

    let y, x, r1, r2, p;

    const blocks = {
      '██': '█',
      '█ ': '▀',
      ' █': '▄',
      '  ': ' '
    };

    const blocksLastLineNoMargin = {
      '██': '▀',
      '█ ': '▀',
      ' █': ' ',
      '  ': ' '
    };

    let ascii = '';
    for (y = 0; y < size; y += 2) {
      r1 = Math.floor((y - min) / cellSize);
      r2 = Math.floor((y + 1 - min) / cellSize);
      for (x = 0; x < size; x += 1) {
        p = '█';

        if (min <= x && x < max && min <= y && y < max && _this.isDark(r1, Math.floor((x - min) / cellSize))) {
          p = ' ';
        }

        if (min <= x && x < max && min <= y+1 && y+1 < max && _this.isDark(r2, Math.floor((x - min) / cellSize))) {
          p += ' ';
        }
        else {
          p += '█';
        }

        // Output 2 characters per pixel, to create full square. 1 character per pixels gives only half width of square.
        ascii += (margin < 1 && y+1 >= max) ? blocksLastLineNoMargin[p] : blocks[p];
      }

      ascii += '\n';
    }

    if (size % 2 && margin > 0) {
      return ascii.substring(0, ascii.length - size - 1) + Array(size+1).join('▀');
    }

    return ascii.substring(0, ascii.length-1);
  };

  _this.createASCII = function(cellSize, margin) {
    cellSize = cellSize || 1;

    if (cellSize < 2) {
      return _createHalfASCII(margin);
    }

    cellSize -= 1;
    margin = (typeof margin == 'undefined')? cellSize * 2 : margin;

    const size = _this.getModuleCount() * cellSize + margin * 2;
    const min = margin;
    const max = size - margin;

    let y, x, r, p;

    const white = Array(cellSize+1).join('██');
    const black = Array(cellSize+1).join('  ');

    let ascii = '';
    let line = '';
    for (y = 0; y < size; y += 1) {
      r = Math.floor( (y - min) / cellSize);
      line = '';
      for (x = 0; x < size; x += 1) {
        p = 1;

        if (min <= x && x < max && min <= y && y < max && _this.isDark(r, Math.floor((x - min) / cellSize))) {
          p = 0;
        }

        // Output 2 characters per pixel, to create full square. 1 character per pixels gives only half width of square.
        line += p ? white : black;
      }

      for (r = 0; r < cellSize; r += 1) {
        ascii += line + '\n';
      }
    }

    return ascii.substring(0, ascii.length-1);
  };

  _this.renderTo2dContext = function(context, cellSize) {
    cellSize = cellSize || 2;
    const length = _this.getModuleCount();
    for (let row = 0; row < length; row++) {
      for (let col = 0; col < length; col++) {
        context.fillStyle = _this.isDark(row, col) ? 'black' : 'white';
        context.fillRect(col * cellSize, row * cellSize, cellSize, cellSize);
      }
    }
  };

  return _this;
};

//---------------------------------------------------------------------
// qrcode.stringToBytes
//---------------------------------------------------------------------

qrcode.stringToBytes = function(s) {
  const bytes = [];
  for (let i = 0; i < s.length; i += 1) {
    const c = s.charCodeAt(i);
    bytes.push(c & 0xff);
  }
  return bytes;
};

//---------------------------------------------------------------------
// qrcode.createStringToBytes
//---------------------------------------------------------------------

/**
 * @param unicodeData base64 string of byte array.
 * [16bit Unicode],[16bit Bytes], ...
 * @param numChars
 */
qrcode.createStringToBytes = function(unicodeData, numChars) {

  // create conversion map.

  const unicodeMap = function() {

    const bin = base64DecodeInputStream(unicodeData);
    const read = function() {
      const b = bin.read();
      if (b == -1) throw 'eof';
      return b;
    };

    let count = 0;
    const unicodeMap = {};
    while (true) {
      const b0 = bin.read();
      if (b0 == -1) break;
      const b1 = read();
      const b2 = read();
      const b3 = read();
      const k = String.fromCharCode( (b0 << 8) | b1);
      const v = (b2 << 8) | b3;
      unicodeMap[k] = v;
      count += 1;
    }
    if (count != numChars) {
      throw count + ' != ' + numChars;
    }

    return unicodeMap;
  }();

  const unknownChar = '?'.charCodeAt(0);

  return function(s) {
    const bytes = [];
    for (let i = 0; i < s.length; i += 1) {
      const c = s.charCodeAt(i);
      if (c < 128) {
        bytes.push(c);
      } else {
        const b = unicodeMap[s.charAt(i)];
        if (typeof b == 'number') {
          if ( (b & 0xff) == b) {
            // 1byte
            bytes.push(b);
          } else {
            // 2bytes
            bytes.push(b >>> 8);
            bytes.push(b & 0xff);
          }
        } else {
          bytes.push(unknownChar);
        }
      }
    }
    return bytes;
  };
};

//---------------------------------------------------------------------
// QRMode
//---------------------------------------------------------------------

const QRMode = {
  MODE_NUMBER :    1 << 0,
  MODE_ALPHA_NUM : 1 << 1,
  MODE_8BIT_BYTE : 1 << 2,
  MODE_KANJI :     1 << 3
};

//---------------------------------------------------------------------
// QRErrorCorrectionLevel
//---------------------------------------------------------------------

const QRErrorCorrectionLevel = {
  L : 1,
  M : 0,
  Q : 3,
  H : 2
};

//---------------------------------------------------------------------
// QRMaskPattern
//---------------------------------------------------------------------

const QRMaskPattern = {
  PATTERN000 : 0,
  PATTERN001 : 1,
  PATTERN010 : 2,
  PATTERN011 : 3,
  PATTERN100 : 4,
  PATTERN101 : 5,
  PATTERN110 : 6,
  PATTERN111 : 7
};

//---------------------------------------------------------------------
// QRUtil
//---------------------------------------------------------------------

const QRUtil = function() {

  const PATTERN_POSITION_TABLE = [
    [],
    [6, 18],
    [6, 22],
    [6, 26],
    [6, 30],
    [6, 34],
    [6, 22, 38],
    [6, 24, 42],
    [6, 26, 46],
    [6, 28, 50],
    [6, 30, 54],
    [6, 32, 58],
    [6, 34, 62],
    [6, 26, 46, 66],
    [6, 26, 48, 70],
    [6, 26, 50, 74],
    [6, 30, 54, 78],
    [6, 30, 56, 82],
    [6, 30, 58, 86],
    [6, 34, 62, 90],
    [6, 28, 50, 72, 94],
    [6, 26, 50, 74, 98],
    [6, 30, 54, 78, 102],
    [6, 28, 54, 80, 106],
    [6, 32, 58, 84, 110],
    [6, 30, 58, 86, 114],
    [6, 34, 62, 90, 118],
    [6, 26, 50, 74, 98, 122],
    [6, 30, 54, 78, 102, 126],
    [6, 26, 52, 78, 104, 130],
    [6, 30, 56, 82, 108, 134],
    [6, 34, 60, 86, 112, 138],
    [6, 30, 58, 86, 114, 142],
    [6, 34, 62, 90, 118, 146],
    [6, 30, 54, 78, 102, 126, 150],
    [6, 24, 50, 76, 102, 128, 154],
    [6, 28, 54, 80, 106, 132, 158],
    [6, 32, 58, 84, 110, 136, 162],
    [6, 26, 54, 82, 110, 138, 166],
    [6, 30, 58, 86, 114, 142, 170]
  ];
  const G15 = (1 << 10) | (1 << 8) | (1 << 5) | (1 << 4) | (1 << 2) | (1 << 1) | (1 << 0);
  const G18 = (1 << 12) | (1 << 11) | (1 << 10) | (1 << 9) | (1 << 8) | (1 << 5) | (1 << 2) | (1 << 0);
  const G15_MASK = (1 << 14) | (1 << 12) | (1 << 10) | (1 << 4) | (1 << 1);

  const _this = {};

  const getBCHDigit = function(data) {
    let digit = 0;
    while (data != 0) {
      digit += 1;
      data >>>= 1;
    }
    return digit;
  };

  _this.getBCHTypeInfo = function(data) {
    let d = data << 10;
    while (getBCHDigit(d) - getBCHDigit(G15) >= 0) {
      d ^= (G15 << (getBCHDigit(d) - getBCHDigit(G15) ) );
    }
    return ( (data << 10) | d) ^ G15_MASK;
  };

  _this.getBCHTypeNumber = function(data) {
    let d = data << 12;
    while (getBCHDigit(d) - getBCHDigit(G18) >= 0) {
      d ^= (G18 << (getBCHDigit(d) - getBCHDigit(G18) ) );
    }
    return (data << 12) | d;
  };

  _this.getPatternPosition = function(typeNumber) {
    return PATTERN_POSITION_TABLE[typeNumber - 1];
  };

  _this.getMaskFunction = function(maskPattern) {

    switch (maskPattern) {

    case QRMaskPattern.PATTERN000 :
      return function(i, j) { return (i + j) % 2 == 0; };
    case QRMaskPattern.PATTERN001 :
      return function(i, j) { return i % 2 == 0; };
    case QRMaskPattern.PATTERN010 :
      return function(i, j) { return j % 3 == 0; };
    case QRMaskPattern.PATTERN011 :
      return function(i, j) { return (i + j) % 3 == 0; };
    case QRMaskPattern.PATTERN100 :
      return function(i, j) { return (Math.floor(i / 2) + Math.floor(j / 3) ) % 2 == 0; };
    case QRMaskPattern.PATTERN101 :
      return function(i, j) { return (i * j) % 2 + (i * j) % 3 == 0; };
    case QRMaskPattern.PATTERN110 :
      return function(i, j) { return ( (i * j) % 2 + (i * j) % 3) % 2 == 0; };
    case QRMaskPattern.PATTERN111 :
      return function(i, j) { return ( (i * j) % 3 + (i + j) % 2) % 2 == 0; };

    default :
      throw 'bad maskPattern:' + maskPattern;
    }
  };

  _this.getErrorCorrectPolynomial = function(errorCorrectLength) {
    let a = qrPolynomial([1], 0);
    for (let i = 0; i < errorCorrectLength; i += 1) {
      a = a.multiply(qrPolynomial([1, QRMath.gexp(i)], 0) );
    }
    return a;
  };

  _this.getLengthInBits = function(mode, type) {

    if (1 <= type && type < 10) {

      // 1 - 9

      switch(mode) {
      case QRMode.MODE_NUMBER    : return 10;
      case QRMode.MODE_ALPHA_NUM : return 9;
      case QRMode.MODE_8BIT_BYTE : return 8;
      case QRMode.MODE_KANJI     : return 8;
      default :
        throw 'mode:' + mode;
      }

    } else if (type < 27) {

      // 10 - 26

      switch(mode) {
      case QRMode.MODE_NUMBER    : return 12;
      case QRMode.MODE_ALPHA_NUM : return 11;
      case QRMode.MODE_8BIT_BYTE : return 16;
      case QRMode.MODE_KANJI     : return 10;
      default :
        throw 'mode:' + mode;
      }

    } else if (type < 41) {

      // 27 - 40

      switch(mode) {
      case QRMode.MODE_NUMBER    : return 14;
      case QRMode.MODE_ALPHA_NUM : return 13;
      case QRMode.MODE_8BIT_BYTE : return 16;
      case QRMode.MODE_KANJI     : return 12;
      default :
        throw 'mode:' + mode;
      }

    } else {
      throw 'type:' + type;
    }
  };

  _this.getLostPoint = function(qrcode) {

    const moduleCount = qrcode.getModuleCount();

    let lostPoint = 0;

    // LEVEL1

    for (let row = 0; row < moduleCount; row += 1) {
      for (let col = 0; col < moduleCount; col += 1) {

        let sameCount = 0;
        const dark = qrcode.isDark(row, col);

        for (let r = -1; r <= 1; r += 1) {

          if (row + r < 0 || moduleCount <= row + r) {
            continue;
          }

          for (let c = -1; c <= 1; c += 1) {

            if (col + c < 0 || moduleCount <= col + c) {
              continue;
            }

            if (r == 0 && c == 0) {
              continue;
            }

            if (dark == qrcode.isDark(row + r, col + c) ) {
              sameCount += 1;
            }
          }
        }

        if (sameCount > 5) {
          lostPoint += (3 + sameCount - 5);
        }
      }
    }
    // LEVEL2

    for (let row = 0; row < moduleCount - 1; row += 1) {
      for (let col = 0; col < moduleCount - 1; col += 1) {
        let count = 0;
        if (qrcode.isDark(row, col) ) count += 1;
        if (qrcode.isDark(row + 1, col) ) count += 1;
        if (qrcode.isDark(row, col + 1) ) count += 1;
        if (qrcode.isDark(row + 1, col + 1) ) count += 1;
        if (count == 0 || count == 4) {
          lostPoint += 3;
        }
      }
    }

    // LEVEL3

    for (let row = 0; row < moduleCount; row += 1) {
      for (let col = 0; col < moduleCount - 6; col += 1) {
        if (qrcode.isDark(row, col)
            && !qrcode.isDark(row, col + 1)
            &&  qrcode.isDark(row, col + 2)
            &&  qrcode.isDark(row, col + 3)
            &&  qrcode.isDark(row, col + 4)
            && !qrcode.isDark(row, col + 5)
            &&  qrcode.isDark(row, col + 6) ) {
          lostPoint += 40;
        }
      }
    }

    for (let col = 0; col < moduleCount; col += 1) {
      for (let row = 0; row < moduleCount - 6; row += 1) {
        if (qrcode.isDark(row, col)
            && !qrcode.isDark(row + 1, col)
            &&  qrcode.isDark(row + 2, col)
            &&  qrcode.isDark(row + 3, col)
            &&  qrcode.isDark(row + 4, col)
            && !qrcode.isDark(row + 5, col)
            &&  qrcode.isDark(row + 6, col) ) {
          lostPoint += 40;
        }
      }
    }

    // LEVEL4

    let darkCount = 0;

    for (let col = 0; col < moduleCount; col += 1) {
      for (let row = 0; row < moduleCount; row += 1) {
        if (qrcode.isDark(row, col) ) {
          darkCount += 1;
        }
      }
    }

    const ratio = Math.abs(100 * darkCount / moduleCount / moduleCount - 50) / 5;
    lostPoint += ratio * 10;

    return lostPoint;
  };

  return _this;
}();

//---------------------------------------------------------------------
// QRMath
//---------------------------------------------------------------------

const QRMath = function() {

  const EXP_TABLE = new Array(256);
  const LOG_TABLE = new Array(256);

  // initialize tables
  for (let i = 0; i < 8; i += 1) {
    EXP_TABLE[i] = 1 << i;
  }
  for (let i = 8; i < 256; i += 1) {
    EXP_TABLE[i] = EXP_TABLE[i - 4]
      ^ EXP_TABLE[i - 5]
      ^ EXP_TABLE[i - 6]
      ^ EXP_TABLE[i - 8];
  }
  for (let i = 0; i < 255; i += 1) {
    LOG_TABLE[EXP_TABLE[i] ] = i;
  }

  const _this = {};

  _this.glog = function(n) {

    if (n < 1) {
      throw 'glog(' + n + ')';
    }

    return LOG_TABLE[n];
  };

  _this.gexp = function(n) {

    while (n < 0) {
      n += 255;
    }

    while (n >= 256) {
      n -= 255;
    }

    return EXP_TABLE[n];
  };

  return _this;
}();

//---------------------------------------------------------------------
// qrPolynomial
//---------------------------------------------------------------------

const qrPolynomial = function(num, shift) {

  if (typeof num.length == 'undefined') {
    throw num.length + '/' + shift;
  }

  const _num = function() {
    let offset = 0;
    while (offset < num.length && num[offset] == 0) {
      offset += 1;
    }
    const _num = new Array(num.length - offset + shift);
    for (let i = 0; i < num.length - offset; i += 1) {
      _num[i] = num[i + offset];
    }
    return _num;
  }();

  const _this = {};

  _this.getAt = function(index) {
    return _num[index];
  };

  _this.getLength = function() {
    return _num.length;
  };

  _this.multiply = function(e) {

    const num = new Array(_this.getLength() + e.getLength() - 1);

    for (let i = 0; i < _this.getLength(); i += 1) {
      for (let j = 0; j < e.getLength(); j += 1) {
        num[i + j] ^= QRMath.gexp(QRMath.glog(_this.getAt(i) ) + QRMath.glog(e.getAt(j) ) );
      }
    }

    return qrPolynomial(num, 0);
  };

  _this.mod = function(e) {

    if (_this.getLength() - e.getLength() < 0) {
      return _this;
    }

    const ratio = QRMath.glog(_this.getAt(0) ) - QRMath.glog(e.getAt(0) );

    const num = new Array(_this.getLength() );
    for (let i = 0; i < _this.getLength(); i += 1) {
      num[i] = _this.getAt(i);
    }

    for (let i = 0; i < e.getLength(); i += 1) {
      num[i] ^= QRMath.gexp(QRMath.glog(e.getAt(i) ) + ratio);
    }

    // recursive call
    return qrPolynomial(num, 0).mod(e);
  };

  return _this;
};

//---------------------------------------------------------------------
// QRRSBlock
//---------------------------------------------------------------------

const QRRSBlock = function() {

  const RS_BLOCK_TABLE = [

    // L
    // M
    // Q
    // H

    // 1
    [1, 26, 19],
    [1, 26, 16],
    [1, 26, 13],
    [1, 26, 9],

    // 2
    [1, 44, 34],
    [1, 44, 28],
    [1, 44, 22],
    [1, 44, 16],

    // 3
    [1, 70, 55],
    [1, 70, 44],
    [2, 35, 17],
    [2, 35, 13],

    // 4
    [1, 100, 80],
    [2, 50, 32],
    [2, 50, 24],
    [4, 25, 9],

    // 5
    [1, 134, 108],
    [2, 67, 43],
    [2, 33, 15, 2, 34, 16],
    [2, 33, 11, 2, 34, 12],

    // 6
    [2, 86, 68],
    [4, 43, 27],
    [4, 43, 19],
    [4, 43, 15],

    // 7
    [2, 98, 78],
    [4, 49, 31],
    [2, 32, 14, 4, 33, 15],
    [4, 39, 13, 1, 40, 14],

    // 8
    [2, 121, 97],
    [2, 60, 38, 2, 61, 39],
    [4, 40, 18, 2, 41, 19],
    [4, 40, 14, 2, 41, 15],

    // 9
    [2, 146, 116],
    [3, 58, 36, 2, 59, 37],
    [4, 36, 16, 4, 37, 17],
    [4, 36, 12, 4, 37, 13],

    // 10
    [2, 86, 68, 2, 87, 69],
    [4, 69, 43, 1, 70, 44],
    [6, 43, 19, 2, 44, 20],
    [6, 43, 15, 2, 44, 16],

    // 11
    [4, 101, 81],
    [1, 80, 50, 4, 81, 51],
    [4, 50, 22, 4, 51, 23],
    [3, 36, 12, 8, 37, 13],

    // 12
    [2, 116, 92, 2, 117, 93],
    [6, 58, 36, 2, 59, 37],
    [4, 46, 20, 6, 47, 21],
    [7, 42, 14, 4, 43, 15],

    // 13
    [4, 133, 107],
    [8, 59, 37, 1, 60, 38],
    [8, 44, 20, 4, 45, 21],
    [12, 33, 11, 4, 34, 12],

    // 14
    [3, 145, 115, 1, 146, 116],
    [4, 64, 40, 5, 65, 41],
    [11, 36, 16, 5, 37, 17],
    [11, 36, 12, 5, 37, 13],

    // 15
    [5, 109, 87, 1, 110, 88],
    [5, 65, 41, 5, 66, 42],
    [5, 54, 24, 7, 55, 25],
    [11, 36, 12, 7, 37, 13],

    // 16
    [5, 122, 98, 1, 123, 99],
    [7, 73, 45, 3, 74, 46],
    [15, 43, 19, 2, 44, 20],
    [3, 45, 15, 13, 46, 16],

    // 17
    [1, 135, 107, 5, 136, 108],
    [10, 74, 46, 1, 75, 47],
    [1, 50, 22, 15, 51, 23],
    [2, 42, 14, 17, 43, 15],

    // 18
    [5, 150, 120, 1, 151, 121],
    [9, 69, 43, 4, 70, 44],
    [17, 50, 22, 1, 51, 23],
    [2, 42, 14, 19, 43, 15],

    // 19
    [3, 141, 113, 4, 142, 114],
    [3, 70, 44, 11, 71, 45],
    [17, 47, 21, 4, 48, 22],
    [9, 39, 13, 16, 40, 14],

    // 20
    [3, 135, 107, 5, 136, 108],
    [3, 67, 41, 13, 68, 42],
    [15, 54, 24, 5, 55, 25],
    [15, 43, 15, 10, 44, 16],

    // 21
    [4, 144, 116, 4, 145, 117],
    [17, 68, 42],
    [17, 50, 22, 6, 51, 23],
    [19, 46, 16, 6, 47, 17],

    // 22
    [2, 139, 111, 7, 140, 112],
    [17, 74, 46],
    [7, 54, 24, 16, 55, 25],
    [34, 37, 13],

    // 23
    [4, 151, 121, 5, 152, 122],
    [4, 75, 47, 14, 76, 48],
    [11, 54, 24, 14, 55, 25],
    [16, 45, 15, 14, 46, 16],

    // 24
    [6, 147, 117, 4, 148, 118],
    [6, 73, 45, 14, 74, 46],
    [11, 54, 24, 16, 55, 25],
    [30, 46, 16, 2, 47, 17],

    // 25
    [8, 132, 106, 4, 133, 107],
    [8, 75, 47, 13, 76, 48],
    [7, 54, 24, 22, 55, 25],
    [22, 45, 15, 13, 46, 16],

    // 26
    [10, 142, 114, 2, 143, 115],
    [19, 74, 46, 4, 75, 47],
    [28, 50, 22, 6, 51, 23],
    [33, 46, 16, 4, 47, 17],

    // 27
    [8, 152, 122, 4, 153, 123],
    [22, 73, 45, 3, 74, 46],
    [8, 53, 23, 26, 54, 24],
    [12, 45, 15, 28, 46, 16],

    // 28
    [3, 147, 117, 10, 148, 118],
    [3, 73, 45, 23, 74, 46],
    [4, 54, 24, 31, 55, 25],
    [11, 45, 15, 31, 46, 16],

    // 29
    [7, 146, 116, 7, 147, 117],
    [21, 73, 45, 7, 74, 46],
    [1, 53, 23, 37, 54, 24],
    [19, 45, 15, 26, 46, 16],

    // 30
    [5, 145, 115, 10, 146, 116],
    [19, 75, 47, 10, 76, 48],
    [15, 54, 24, 25, 55, 25],
    [23, 45, 15, 25, 46, 16],

    // 31
    [13, 145, 115, 3, 146, 116],
    [2, 74, 46, 29, 75, 47],
    [42, 54, 24, 1, 55, 25],
    [23, 45, 15, 28, 46, 16],

    // 32
    [17, 145, 115],
    [10, 74, 46, 23, 75, 47],
    [10, 54, 24, 35, 55, 25],
    [19, 45, 15, 35, 46, 16],

    // 33
    [17, 145, 115, 1, 146, 116],
    [14, 74, 46, 21, 75, 47],
    [29, 54, 24, 19, 55, 25],
    [11, 45, 15, 46, 46, 16],

    // 34
    [13, 145, 115, 6, 146, 116],
    [14, 74, 46, 23, 75, 47],
    [44, 54, 24, 7, 55, 25],
    [59, 46, 16, 1, 47, 17],

    // 35
    [12, 151, 121, 7, 152, 122],
    [12, 75, 47, 26, 76, 48],
    [39, 54, 24, 14, 55, 25],
    [22, 45, 15, 41, 46, 16],

    // 36
    [6, 151, 121, 14, 152, 122],
    [6, 75, 47, 34, 76, 48],
    [46, 54, 24, 10, 55, 25],
    [2, 45, 15, 64, 46, 16],

    // 37
    [17, 152, 122, 4, 153, 123],
    [29, 74, 46, 14, 75, 47],
    [49, 54, 24, 10, 55, 25],
    [24, 45, 15, 46, 46, 16],

    // 38
    [4, 152, 122, 18, 153, 123],
    [13, 74, 46, 32, 75, 47],
    [48, 54, 24, 14, 55, 25],
    [42, 45, 15, 32, 46, 16],

    // 39
    [20, 147, 117, 4, 148, 118],
    [40, 75, 47, 7, 76, 48],
    [43, 54, 24, 22, 55, 25],
    [10, 45, 15, 67, 46, 16],

    // 40
    [19, 148, 118, 6, 149, 119],
    [18, 75, 47, 31, 76, 48],
    [34, 54, 24, 34, 55, 25],
    [20, 45, 15, 61, 46, 16]
  ];

  const qrRSBlock = function(totalCount, dataCount) {
    const _this = {};
    _this.totalCount = totalCount;
    _this.dataCount = dataCount;
    return _this;
  };

  const _this = {};

  const getRsBlockTable = function(typeNumber, errorCorrectionLevel) {

    switch(errorCorrectionLevel) {
    case QRErrorCorrectionLevel.L :
      return RS_BLOCK_TABLE[(typeNumber - 1) * 4 + 0];
    case QRErrorCorrectionLevel.M :
      return RS_BLOCK_TABLE[(typeNumber - 1) * 4 + 1];
    case QRErrorCorrectionLevel.Q :
      return RS_BLOCK_TABLE[(typeNumber - 1) * 4 + 2];
    case QRErrorCorrectionLevel.H :
      return RS_BLOCK_TABLE[(typeNumber - 1) * 4 + 3];
    default :
      return undefined;
    }
  };

  _this.getRSBlocks = function(typeNumber, errorCorrectionLevel) {

    const rsBlock = getRsBlockTable(typeNumber, errorCorrectionLevel);

    if (typeof rsBlock == 'undefined') {
      throw 'bad rs block @ typeNumber:' + typeNumber +
          '/errorCorrectionLevel:' + errorCorrectionLevel;
    }

    const length = rsBlock.length / 3;

    const list = [];

    for (let i = 0; i < length; i += 1) {

      const count = rsBlock[i * 3 + 0];
      const totalCount = rsBlock[i * 3 + 1];
      const dataCount = rsBlock[i * 3 + 2];

      for (let j = 0; j < count; j += 1) {
        list.push(qrRSBlock(totalCount, dataCount) );
      }
    }

    return list;
  };

  return _this;
}();

//---------------------------------------------------------------------
// qrBitBuffer
//---------------------------------------------------------------------

const qrBitBuffer = function() {

  const _buffer = [];
  let _length = 0;

  const _this = {};

  _this.getBuffer = function() {
    return _buffer;
  };

  _this.getAt = function(index) {
    const bufIndex = Math.floor(index / 8);
    return ( (_buffer[bufIndex] >>> (7 - index % 8) ) & 1) == 1;
  };

  _this.put = function(num, length) {
    for (let i = 0; i < length; i += 1) {
      _this.putBit( ( (num >>> (length - i - 1) ) & 1) == 1);
    }
  };

  _this.getLengthInBits = function() {
    return _length;
  };

  _this.putBit = function(bit) {

    const bufIndex = Math.floor(_length / 8);
    if (_buffer.length <= bufIndex) {
      _buffer.push(0);
    }

    if (bit) {
      _buffer[bufIndex] |= (0x80 >>> (_length % 8) );
    }

    _length += 1;
  };

  return _this;
};

//---------------------------------------------------------------------
// qrNumber
//---------------------------------------------------------------------

const qrNumber = function(data) {

  const _mode = QRMode.MODE_NUMBER;
  const _data = data;

  const _this = {};

  _this.getMode = function() {
    return _mode;
  };

  _this.getLength = function(buffer) {
    return _data.length;
  };

  _this.write = function(buffer) {

    const data = _data;

    let i = 0;

    while (i + 2 < data.length) {
      buffer.put(strToNum(data.substring(i, i + 3) ), 10);
      i += 3;
    }

    if (i < data.length) {
      if (data.length - i == 1) {
        buffer.put(strToNum(data.substring(i, i + 1) ), 4);
      } else if (data.length - i == 2) {
        buffer.put(strToNum(data.substring(i, i + 2) ), 7);
      }
    }
  };

  const strToNum = function(s) {
    let num = 0;
    for (let i = 0; i < s.length; i += 1) {
      num = num * 10 + chatToNum(s.charAt(i) );
    }
    return num;
  };

  const chatToNum = function(c) {
    if ('0' <= c && c <= '9') {
      return c.charCodeAt(0) - '0'.charCodeAt(0);
    }
    throw 'illegal char :' + c;
  };

  return _this;
};

//---------------------------------------------------------------------
// qrAlphaNum
//---------------------------------------------------------------------

const qrAlphaNum = function(data) {

  const _mode = QRMode.MODE_ALPHA_NUM;
  const _data = data;

  const _this = {};

  _this.getMode = function() {
    return _mode;
  };

  _this.getLength = function(buffer) {
    return _data.length;
  };

  _this.write = function(buffer) {

    const s = _data;

    let i = 0;

    while (i + 1 < s.length) {
      buffer.put(
        getCode(s.charAt(i) ) * 45 +
        getCode(s.charAt(i + 1) ), 11);
      i += 2;
    }

    if (i < s.length) {
      buffer.put(getCode(s.charAt(i) ), 6);
    }
  };

  const getCode = function(c) {

    if ('0' <= c && c <= '9') {
      return c.charCodeAt(0) - '0'.charCodeAt(0);
    } else if ('A' <= c && c <= 'Z') {
      return c.charCodeAt(0) - 'A'.charCodeAt(0) + 10;
    } else {
      switch (c) {
      case '\u0020' : return 36;
      case '$' : return 37;
      case '%' : return 38;
      case '*' : return 39;
      case '+' : return 40;
      case '-' : return 41;
      case '.' : return 42;
      case '/' : return 43;
      case ':' : return 44;
      default :
        throw 'illegal char :' + c;
      }
    }
  };

  return _this;
};

//---------------------------------------------------------------------
// qr8BitByte
//---------------------------------------------------------------------

const qr8BitByte = function(data) {

  const _mode = QRMode.MODE_8BIT_BYTE;
  const _bytes = qrcode.stringToBytes(data);

  const _this = {};

  _this.getMode = function() {
    return _mode;
  };

  _this.getLength = function(buffer) {
    return _bytes.length;
  };

  _this.write = function(buffer) {
    for (let i = 0; i < _bytes.length; i += 1) {
      buffer.put(_bytes[i], 8);
    }
  };

  return _this;
};

//---------------------------------------------------------------------
// qrKanji
//---------------------------------------------------------------------

const qrKanji = function(data) {

  const _mode = QRMode.MODE_KANJI;

  const stringToBytes = qrcode.stringToBytes;
  !function(c, code) {
    // self test for sjis support.
    const test = stringToBytes(c);
    if (test.length != 2 || ( (test[0] << 8) | test[1]) != code) {
      throw 'sjis not supported.';
    }
  }('\u53cb', 0x9746);

  const _bytes = stringToBytes(data);

  const _this = {};

  _this.getMode = function() {
    return _mode;
  };

  _this.getLength = function(buffer) {
    return ~~(_bytes.length / 2);
  };

  _this.write = function(buffer) {

    const data = _bytes;

    let i = 0;

    while (i + 1 < data.length) {

      let c = ( (0xff & data[i]) << 8) | (0xff & data[i + 1]);

      if (0x8140 <= c && c <= 0x9FFC) {
        c -= 0x8140;
      } else if (0xE040 <= c && c <= 0xEBBF) {
        c -= 0xC140;
      } else {
        throw 'illegal char at ' + (i + 1) + '/' + c;
      }

      c = ( (c >>> 8) & 0xff) * 0xC0 + (c & 0xff);

      buffer.put(c, 13);

      i += 2;
    }

    if (i < data.length) {
      throw 'illegal char at ' + (i + 1);
    }
  };

  return _this;
};

//=====================================================================
// GIF Support etc.
//

//---------------------------------------------------------------------
// byteArrayOutputStream
//---------------------------------------------------------------------

const byteArrayOutputStream = function() {

  const _bytes = [];

  const _this = {};

  _this.writeByte = function(b) {
    _bytes.push(b & 0xff);
  };

  _this.writeShort = function(i) {
    _this.writeByte(i);
    _this.writeByte(i >>> 8);
  };

  _this.writeBytes = function(b, off, len) {
    off = off || 0;
    len = len || b.length;
    for (let i = 0; i < len; i += 1) {
      _this.writeByte(b[i + off]);
    }
  };

  _this.writeString = function(s) {
    for (let i = 0; i < s.length; i += 1) {
      _this.writeByte(s.charCodeAt(i) );
    }
  };

  _this.toByteArray = function() {
    return _bytes;
  };

  _this.toString = function() {
    let s = '';
    s += '[';
    for (let i = 0; i < _bytes.length; i += 1) {
      if (i > 0) {
        s += ',';
      }
      s += _bytes[i];
    }
    s += ']';
    return s;
  };

  return _this;
};

//---------------------------------------------------------------------
// base64EncodeOutputStream
//---------------------------------------------------------------------

const base64EncodeOutputStream = function() {

  let _buffer = 0;
  let _buflen = 0;
  let _length = 0;
  let _base64 = '';

  const _this = {};

  const writeEncoded = function(b) {
    _base64 += String.fromCharCode(encode(b & 0x3f) );
  };

  const encode = function(n) {
    if (n < 0) {
      throw 'n:' + n;
    } else if (n < 26) {
      return 0x41 + n;
    } else if (n < 52) {
      return 0x61 + (n - 26);
    } else if (n < 62) {
      return 0x30 + (n - 52);
    } else if (n == 62) {
      return 0x2b;
    } else if (n == 63) {
      return 0x2f;
    } else {
      throw 'n:' + n;
    }
  };

  _this.writeByte = function(n) {

    _buffer = (_buffer << 8) | (n & 0xff);
    _buflen += 8;
    _length += 1;

    while (_buflen >= 6) {
      writeEncoded(_buffer >>> (_buflen - 6) );
      _buflen -= 6;
    }
  };

  _this.flush = function() {

    if (_buflen > 0) {
      writeEncoded(_buffer << (6 - _buflen) );
      _buffer = 0;
      _buflen = 0;
    }

    if (_length % 3 != 0) {
      // padding
      const padlen = 3 - _length % 3;
      for (let i = 0; i < padlen; i += 1) {
        _base64 += '=';
      }
    }
  };

  _this.toString = function() {
    return _base64;
  };

  return _this;
};

//---------------------------------------------------------------------
// base64DecodeInputStream
//---------------------------------------------------------------------

const base64DecodeInputStream = function(str) {

  const _str = str;
  let _pos = 0;
  let _buffer = 0;
  let _buflen = 0;

  const _this = {};

  _this.read = function() {

    while (_buflen < 8) {

      if (_pos >= _str.length) {
        if (_buflen == 0) {
          return -1;
        }
        throw 'unexpected end of file./' + _buflen;
      }

      const c = _str.charAt(_pos);
      _pos += 1;

      if (c == '=') {
        _buflen = 0;
        return -1;
      } else if (c.match(/^\s$/) ) {
        // ignore if whitespace.
        continue;
      }

      _buffer = (_buffer << 6) | decode(c.charCodeAt(0) );
      _buflen += 6;
    }

    const n = (_buffer >>> (_buflen - 8) ) & 0xff;
    _buflen -= 8;
    return n;
  };

  const decode = function(c) {
    if (0x41 <= c && c <= 0x5a) {
      return c - 0x41;
    } else if (0x61 <= c && c <= 0x7a) {
      return c - 0x61 + 26;
    } else if (0x30 <= c && c <= 0x39) {
      return c - 0x30 + 52;
    } else if (c == 0x2b) {
      return 62;
    } else if (c == 0x2f) {
      return 63;
    } else {
      throw 'c:' + c;
    }
  };

  return _this;
};

//---------------------------------------------------------------------
// gifImage (B/W)
//---------------------------------------------------------------------

const gifImage = function(width, height) {

  const _width = width;
  const _height = height;
  const _data = new Array(width * height);

  const _this = {};

  _this.setPixel = function(x, y, pixel) {
    _data[y * _width + x] = pixel;
  };

  _this.write = function(out) {

    //---------------------------------
    // GIF Signature

    out.writeString('GIF87a');

    //---------------------------------
    // Screen Descriptor

    out.writeShort(_width);
    out.writeShort(_height);

    out.writeByte(0x80); // 2bit
    out.writeByte(0);
    out.writeByte(0);

    //---------------------------------
    // Global Color Map

    // black
    out.writeByte(0x00);
    out.writeByte(0x00);
    out.writeByte(0x00);

    // white
    out.writeByte(0xff);
    out.writeByte(0xff);
    out.writeByte(0xff);

    //---------------------------------
    // Image Descriptor

    out.writeString(',');
    out.writeShort(0);
    out.writeShort(0);
    out.writeShort(_width);
    out.writeShort(_height);
    out.writeByte(0);

    //---------------------------------
    // Local Color Map

    //---------------------------------
    // Raster Data

    const lzwMinCodeSize = 2;
    const raster = getLZWRaster(lzwMinCodeSize);

    out.writeByte(lzwMinCodeSize);

    let offset = 0;

    while (raster.length - offset > 255) {
      out.writeByte(255);
      out.writeBytes(raster, offset, 255);
      offset += 255;
    }

    out.writeByte(raster.length - offset);
    out.writeBytes(raster, offset, raster.length - offset);
    out.writeByte(0x00);

    //---------------------------------
    // GIF Terminator
    out.writeString(';');
  };

  const bitOutputStream = function(out) {

    const _out = out;
    let _bitLength = 0;
    let _bitBuffer = 0;

    const _this = {};

    _this.write = function(data, length) {

      if ( (data >>> length) != 0) {
        throw 'length over';
      }

      while (_bitLength + length >= 8) {
        _out.writeByte(0xff & ( (data << _bitLength) | _bitBuffer) );
        length -= (8 - _bitLength);
        data >>>= (8 - _bitLength);
        _bitBuffer = 0;
        _bitLength = 0;
      }

      _bitBuffer = (data << _bitLength) | _bitBuffer;
      _bitLength = _bitLength + length;
    };

    _this.flush = function() {
      if (_bitLength > 0) {
        _out.writeByte(_bitBuffer);
      }
    };

    return _this;
  };

  const getLZWRaster = function(lzwMinCodeSize) {

    const clearCode = 1 << lzwMinCodeSize;
    const endCode = (1 << lzwMinCodeSize) + 1;
    let bitLength = lzwMinCodeSize + 1;

    // Setup LZWTable
    const table = lzwTable();

    for (let i = 0; i < clearCode; i += 1) {
      table.add(String.fromCharCode(i) );
    }
    table.add(String.fromCharCode(clearCode) );
    table.add(String.fromCharCode(endCode) );

    const byteOut = byteArrayOutputStream();
    const bitOut = bitOutputStream(byteOut);

    // clear code
    bitOut.write(clearCode, bitLength);

    let dataIndex = 0;

    let s = String.fromCharCode(_data[dataIndex]);
    dataIndex += 1;

    while (dataIndex < _data.length) {

      const c = String.fromCharCode(_data[dataIndex]);
      dataIndex += 1;

      if (table.contains(s + c) ) {

        s = s + c;

      } else {

        bitOut.write(table.indexOf(s), bitLength);

        if (table.size() < 0xfff) {

          if (table.size() == (1 << bitLength) ) {
            bitLength += 1;
          }

          table.add(s + c);
        }

        s = c;
      }
    }

    bitOut.write(table.indexOf(s), bitLength);

    // end code
    bitOut.write(endCode, bitLength);

    bitOut.flush();

    return byteOut.toByteArray();
  };

  const lzwTable = function() {

    const _map = {};
    let _size = 0;

    const _this = {};

    _this.add = function(key) {
      if (_this.contains(key) ) {
        throw 'dup key:' + key;
      }
      _map[key] = _size;
      _size += 1;
    };

    _this.size = function() {
      return _size;
    };

    _this.indexOf = function(key) {
      return _map[key];
    };

    _this.contains = function(key) {
      return typeof _map[key] != 'undefined';
    };

    return _this;
  };

  return _this;
};

const createDataURL = function(width, height, getPixel) {
  const gif = gifImage(width, height);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      gif.setPixel(x, y, getPixel(x, y) );
    }
  }

  const b = byteArrayOutputStream();
  gif.write(b);

  const base64 = base64EncodeOutputStream();
  const bytes = b.toByteArray();
  for (let i = 0; i < bytes.length; i += 1) {
    base64.writeByte(bytes[i]);
  }
  base64.flush();

  return 'data:image/gif;base64,' + base64;
};

const status = {
    inspected: "Диагностика готова.",
    applied: "Параметры сброшены. Повторите запуск из библиотеки Steam.",
    restored: "Исходные параметры восстановлены.",
    conflict: "Текущее значение отличается от ожидаемого. Проверьте свойства игры в Steam.",
};
const originKey = "deck-ai-repair-origin";
function Qr({ url }) {
    const src = SP_REACT.useMemo(() => {
        const qr = qrcode(0, "M");
        qr.addData(url);
        qr.make();
        return qr.createDataURL(6);
    }, [url]);
    return SP_JSX.jsx("img", { className: "dai-repair-qr", src: src, alt: "QR \u0434\u043B\u044F \u0441\u043E\u043F\u0440\u044F\u0436\u0435\u043D\u0438\u044F \u0431\u0440\u0430\u0443\u0437\u0435\u0440\u0430 \u0441 \u044D\u0442\u043E\u0439 \u0434\u0438\u0430\u0433\u043D\u043E\u0441\u0442\u0438\u043A\u043E\u0439" });
}
function RepairPanel({ copy }) {
    const [view, setView] = SP_REACT.useState(repairView);
    const [query, setQuery] = SP_REACT.useState("");
    const [appId, setAppId] = SP_REACT.useState(0);
    const [shot, setShot] = SP_REACT.useState("");
    const [shots, setShots] = SP_REACT.useState([]);
    const [preview, setPreview] = SP_REACT.useState("");
    const [error, setError] = SP_REACT.useState("");
    const [busy, setBusy] = SP_REACT.useState(false);
    const operationPending = SP_REACT.useRef(false);
    const [pairOpen, setPairOpen] = SP_REACT.useState(false);
    const [address, setAddress] = SP_REACT.useState(() => localStorage.getItem(originKey) || "");
    SP_REACT.useEffect(() => subscribeRepair(setView), []);
    const current = view.case;
    const account = steamAccount();
    const games = current ? [] : libraryGames(query, DFL.Router.MainRunningAppID ?? 0);
    const selected = games.find(game => game.appId === appId) || games[0];
    SP_REACT.useEffect(() => {
        let stale = false;
        setShots([]);
        setShot("");
        if (selected && account && !current) {
            void repairScreenshots(selected.appId, selected.shortcut).then(items => {
                if (!stale)
                    setShots(items);
            }).catch(() => { });
        }
        return () => { stale = true; };
    }, [selected?.appId, selected?.shortcut, account, current?.id]);
    SP_REACT.useEffect(() => { setPreview(""); }, [account]);
    async function run(operation) {
        if (operationPending.current)
            return;
        operationPending.current = true;
        setBusy(true);
        setError("");
        try {
            await operation();
        }
        catch (failure) {
            setError(String(failure));
        }
        finally {
            operationPending.current = false;
            setBusy(false);
        }
    }
    const action = current?.action;
    const remote = view.remote;
    const send = (verb, fields) => {
        if (current)
            void run(() => repairCommand(current.id, verb, fields));
    };
    const message = error || view.error;
    return SP_JSX.jsxs(DFL.Focusable, { className: "dai-stack-content dai-repair", "flow-children": "vertical", children: [SP_JSX.jsxs("section", { className: "dai-section", children: [SP_JSX.jsx("h3", { children: "\u0420\u0430\u0437\u043E\u0431\u0440\u0430\u0442\u044C \u043E\u0448\u0438\u0431\u043A\u0443 \u0437\u0430\u043F\u0443\u0441\u043A\u0430" }), SP_JSX.jsx("p", { className: "dai-muted", children: "\u041F\u0440\u043E\u0432\u0435\u0440\u043A\u0430 \u044D\u0442\u043E\u0439 Steam Deck. \u041C\u043E\u0436\u043D\u043E \u0432\u044B\u0431\u0440\u0430\u0442\u044C \u0438\u0433\u0440\u0443, \u043A\u043E\u0442\u043E\u0440\u0430\u044F \u0443\u0436\u0435 \u0437\u0430\u043A\u0440\u044B\u043B\u0430\u0441\u044C." }), message && SP_JSX.jsx("p", { className: "dai-repair-error", role: "alert", children: message }), !current && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.TextField, { value: query, placeholder: "\u041D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u0438\u0433\u0440\u044B \u0438\u043B\u0438 App ID", onChange: event => setQuery(event.target.value) }), selected ? SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx("span", { className: "dai-label", children: "\u0418\u0433\u0440\u0430 \u0438\u0437 \u0431\u0438\u0431\u043B\u0438\u043E\u0442\u0435\u043A\u0438" }), SP_JSX.jsx(DFL.Dropdown, { selectedOption: selected.appId, disabled: busy, rgOptions: games.map(game => ({ data: game.appId, label: game.name })), onChange: option => setAppId(option.data) }), !!shots.length && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx("span", { className: "dai-label", children: "\u0421\u043A\u0440\u0438\u043D\u0448\u043E\u0442 Steam" }), SP_JSX.jsx(DFL.Dropdown, { selectedOption: shot, disabled: busy, rgOptions: [{ data: "", label: "Без скриншота" }, ...shots.map(item => ({ data: item.path, label: item.name }))], onChange: option => setShot(option.data) })] }), SP_JSX.jsx(DFL.DialogButton, { className: "dai-button dai-primary", disabled: busy || !account, onClick: () => void run(async () => {
                                            const result = await inspectLaunch(selected.appId, shot);
                                            setPreview(result.preview);
                                        }), children: busy ? "Читаю свойства Steam…" : "Проверить запуск" })] }) : SP_JSX.jsx("p", { className: "dai-muted", children: "\u0412 \u0431\u0438\u0431\u043B\u0438\u043E\u0442\u0435\u043A\u0435 \u043D\u0435\u0442 \u043F\u043E\u0434\u0445\u043E\u0434\u044F\u0449\u0435\u0439 \u043B\u043E\u043A\u0430\u043B\u044C\u043D\u043E\u0439 \u0438\u0433\u0440\u044B. \u041F\u0440\u043E\u0432\u0435\u0440\u044C\u0442\u0435 \u043D\u0430\u0437\u0432\u0430\u043D\u0438\u0435." })] }), current && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx("h4", { children: current.name }), SP_JSX.jsx("p", { className: "dai-muted", children: current.proton ? "Совместимость Steam · " + current.proton : "Steam не указал инструмент совместимости." }), preview && SP_JSX.jsx("img", { className: "dai-repair-preview", src: preview, alt: "\u0412\u044B\u0431\u0440\u0430\u043D\u043D\u044B\u0439 \u0441\u043A\u0440\u0438\u043D\u0448\u043E\u0442 Steam" }), SP_JSX.jsx("ul", { className: "dai-repair-checks", children: current.checks.map(check => SP_JSX.jsx("li", { children: check }, check)) }), SP_JSX.jsx("p", { role: "status", children: action?.state === "pending" ? "Ожидаю подтверждение." : action ? "Сверяю параметры со Steam…" :
                                    current.state === "applied" && current.launchResult ? "Параметры сброшены. Результат запуска отмечен." : status[current.state] }), current.detail && SP_JSX.jsx("p", { className: "dai-muted", children: current.detail }), SP_JSX.jsxs(DFL.Focusable, { className: "dai-repair-actions", "flow-children": "horizontal", children: [SP_JSX.jsx(DFL.DialogButton, { className: "dai-button", disabled: busy || !!action, onClick: () => send("recheck"), children: "\u041F\u043E\u0432\u0442\u043E\u0440\u0438\u0442\u044C \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0443" }), SP_JSX.jsx(DFL.DialogButton, { className: "dai-button", onClick: () => copy([
                                            `${current.name} · Steam App ID ${current.appId}`,
                                            current.proton && `Совместимость Steam · ${current.proton}`,
                                            ...current.checks,
                                        ].filter(Boolean).join("\n")), children: "\u0421\u043A\u043E\u043F\u0438\u0440\u043E\u0432\u0430\u0442\u044C \u0441\u0432\u043E\u0434\u043A\u0443" })] }), current.readOnly && SP_JSX.jsx("p", { className: "dai-muted", children: "\u0418\u0437\u043C\u0435\u043D\u0435\u043D\u0438\u044F \u043F\u0440\u0438\u043E\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u044B \u0432 \u0440\u0435\u0436\u0438\u043C\u0435 \u00AB\u0422\u043E\u043B\u044C\u043A\u043E \u0447\u0442\u0435\u043D\u0438\u0435\u00BB." }), current.note && SP_JSX.jsxs("p", { className: "dai-muted", children: ["\u0423\u0442\u043E\u0447\u043D\u0435\u043D\u0438\u0435 \u0441 \u043F\u0443\u043B\u044C\u0442\u0430 \u00B7 ", current.note] }), !action && current.canReset && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx("p", { children: "\u0415\u0441\u0442\u044C \u043F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u044C\u0441\u043A\u0438\u0435 \u043F\u0430\u0440\u0430\u043C\u0435\u0442\u0440\u044B \u0437\u0430\u043F\u0443\u0441\u043A\u0430. \u041F\u043E\u043F\u0440\u043E\u0431\u0443\u0439\u0442\u0435 \u0437\u0430\u043F\u0443\u0441\u043A \u0441\u043E \u0441\u0442\u0430\u043D\u0434\u0430\u0440\u0442\u043D\u044B\u043C \u0437\u043D\u0430\u0447\u0435\u043D\u0438\u0435\u043C. \u0421\u043E\u0445\u0440\u0430\u043D\u0438\u043C \u0442\u0435\u043A\u0443\u0449\u0438\u0435 \u043F\u0430\u0440\u0430\u043C\u0435\u0442\u0440\u044B \u0434\u043B\u044F \u043E\u0442\u043A\u0430\u0442\u0430." }), SP_JSX.jsx(DFL.DialogButton, { className: "dai-button", disabled: busy || current.readOnly, onClick: () => send("request", { kind: "reset" }), children: "\u041F\u0440\u0435\u0434\u043B\u043E\u0436\u0438\u0442\u044C \u0441\u0431\u0440\u043E\u0441 \u043F\u0430\u0440\u0430\u043C\u0435\u0442\u0440\u043E\u0432" })] }), !action && current.state === "inspected" && !current.canReset &&
                                SP_JSX.jsx("p", { children: "\u041F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u044C\u0441\u043A\u0438\u0435 \u043F\u0430\u0440\u0430\u043C\u0435\u0442\u0440\u044B \u0437\u0430\u043F\u0443\u0441\u043A\u0430 \u043F\u0443\u0441\u0442\u044B. \u041F\u043E \u044D\u0442\u043E\u0439 \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0435 \u0438\u0441\u043F\u0440\u0430\u0432\u043B\u0435\u043D\u0438\u0435 \u043D\u0435 \u0442\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044F." }), action?.state === "pending" && SP_JSX.jsxs("div", { className: "dai-repair-confirm", children: [SP_JSX.jsx("p", { children: action.kind === "reset" ? "Временно сбросить параметры запуска этой игры?" : "Вернуть исходные параметры запуска этой игры?" }), SP_JSX.jsxs(DFL.Focusable, { className: "dai-repair-actions", "flow-children": "horizontal", children: [SP_JSX.jsx(DFL.DialogButton, { className: "dai-button dai-primary", disabled: busy || current.readOnly, onClick: () => send("decide", { actionId: action.id, decision: true }), children: "\u041F\u043E\u0434\u0442\u0432\u0435\u0440\u0434\u0438\u0442\u044C" }), SP_JSX.jsx(DFL.DialogButton, { className: "dai-button", disabled: busy, onClick: () => send("decide", { actionId: action.id, decision: false }), children: "\u041E\u0442\u043A\u043B\u043E\u043D\u0438\u0442\u044C" })] })] }), current.canEndWait && action && SP_JSX.jsx(DFL.DialogButton, { className: "dai-button", disabled: busy, onClick: () => send("end_wait", { actionId: action.id }), children: "\u0417\u0430\u0432\u0435\u0440\u0448\u0438\u0442\u044C \u043E\u0436\u0438\u0434\u0430\u043D\u0438\u0435 Steam" }), current.hasBackup && !action && SP_JSX.jsx(DFL.DialogButton, { className: "dai-button", disabled: busy, onClick: () => void run(async () => copy(await originalLaunchOptions(current.id))), children: "\u0421\u043A\u043E\u043F\u0438\u0440\u043E\u0432\u0430\u0442\u044C \u0438\u0441\u0445\u043E\u0434\u043D\u044B\u0435 \u043F\u0430\u0440\u0430\u043C\u0435\u0442\u0440\u044B" }), !action && current.state === "applied" && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.DialogButton, { className: "dai-button", onClick: () => DFL.Navigation.Navigate("/library/app/" + current.appId), children: "\u041E\u0442\u043A\u0440\u044B\u0442\u044C \u0438\u0433\u0440\u0443 \u0432 \u0431\u0438\u0431\u043B\u0438\u043E\u0442\u0435\u043A\u0435" }), current.launchResult ? SP_JSX.jsx("p", { children: current.launchResult === "started" ? "Отмечено: игра запустилась." : "Отмечено: игра не запустилась." }) : SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx("p", { children: "\u0418\u0433\u0440\u0430 \u0437\u0430\u043F\u0443\u0441\u0442\u0438\u043B\u0430\u0441\u044C \u043F\u043E\u0441\u043B\u0435 \u0441\u0431\u0440\u043E\u0441\u0430?" }), SP_JSX.jsxs(DFL.Focusable, { className: "dai-repair-actions", "flow-children": "horizontal", children: [SP_JSX.jsx(DFL.DialogButton, { className: "dai-button", disabled: busy, onClick: () => send("result", { result: "started" }), children: "\u0417\u0430\u043F\u0443\u0441\u0442\u0438\u043B\u0430\u0441\u044C" }), SP_JSX.jsx(DFL.DialogButton, { className: "dai-button", disabled: busy, onClick: () => send("result", { result: "failed" }), children: "\u041D\u0435 \u0437\u0430\u043F\u0443\u0441\u0442\u0438\u043B\u0430\u0441\u044C" })] })] }), SP_JSX.jsx(DFL.DialogButton, { className: "dai-button", disabled: busy || current.readOnly, onClick: () => send("request", { kind: "restore" }), children: "\u041F\u0440\u0435\u0434\u043B\u043E\u0436\u0438\u0442\u044C \u043E\u0442\u043A\u0430\u0442" })] }), !action && SP_JSX.jsx(DFL.DialogButton, { className: "dai-button", disabled: busy, onClick: () => {
                                    const close = () => void run(async () => { await repairCommand(current.id, "close"); setPreview(""); });
                                    if (current.state !== "applied" && current.state !== "conflict") {
                                        close();
                                        return;
                                    }
                                    DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: "\u0417\u0430\u0432\u0435\u0440\u0448\u0438\u0442\u044C \u0434\u0438\u0430\u0433\u043D\u043E\u0441\u0442\u0438\u043A\u0443?", strDescription: "Deck AI \u0443\u0434\u0430\u043B\u0438\u0442 \u0441\u043E\u0445\u0440\u0430\u043D\u0451\u043D\u043D\u043E\u0435 \u0437\u043D\u0430\u0447\u0435\u043D\u0438\u0435 \u043F\u0430\u0440\u0430\u043C\u0435\u0442\u0440\u043E\u0432 \u0437\u0430\u043F\u0443\u0441\u043A\u0430. \u0410\u0432\u0442\u043E\u043C\u0430\u0442\u0438\u0447\u0435\u0441\u043A\u0438\u0439 \u043E\u0442\u043A\u0430\u0442 \u0441\u0442\u0430\u043D\u0435\u0442 \u043D\u0435\u0434\u043E\u0441\u0442\u0443\u043F\u0435\u043D.", strOKButtonText: "\u0417\u0430\u0432\u0435\u0440\u0448\u0438\u0442\u044C", strCancelButtonText: "\u041F\u0440\u043E\u0434\u043E\u043B\u0436\u0438\u0442\u044C", onOK: close }));
                                }, children: "\u0417\u0430\u0432\u0435\u0440\u0448\u0438\u0442\u044C \u0434\u0438\u0430\u0433\u043D\u043E\u0441\u0442\u0438\u043A\u0443" })] })] }), current && SP_JSX.jsxs("section", { className: "dai-section", children: [SP_JSX.jsx("h3", { children: "\u041F\u0443\u043B\u044C\u0442 \u043D\u0430 \u0442\u0435\u043B\u0435\u0444\u043E\u043D\u0435 \u0438\u043B\u0438 \u041F\u041A" }), remote.state === "off" && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.DialogButton, { className: "dai-button", onClick: () => setPairOpen(!pairOpen), children: "\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0438\u0442\u044C \u0431\u0440\u0430\u0443\u0437\u0435\u0440" }), pairOpen && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx("p", { className: "dai-muted", children: "\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0447\u0430\u0441\u0442\u043D\u044B\u0439 HTTPS-\u0430\u0434\u0440\u0435\u0441 \u043F\u0443\u043B\u044C\u0442\u0430. \u041D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0430 Tailscale Serve \u0438 HTTPS-\u043F\u0440\u043E\u043A\u0441\u0438 \u043E\u043F\u0438\u0441\u0430\u043D\u0430 \u0432 \u0438\u043D\u0441\u0442\u0440\u0443\u043A\u0446\u0438\u0438 \u043A \u0440\u0435\u043B\u0438\u0437\u0443." }), SP_JSX.jsx(DFL.TextField, { value: address, placeholder: "https://deck.example.ts.net:8443", onChange: event => setAddress(event.target.value) }), SP_JSX.jsx(DFL.DialogButton, { className: "dai-button dai-primary", disabled: busy || !address.trim(), onClick: () => void run(async () => {
                                            await repairCommand(current.id, "pair", { address });
                                            localStorage.setItem(originKey, address.trim());
                                        }), children: "\u041F\u043E\u043A\u0430\u0437\u0430\u0442\u044C QR" })] })] }), remote.state === "pairing" && remote.url && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(Qr, { url: remote.url }), SP_JSX.jsx("p", { className: "dai-muted", children: "\u041E\u0442\u043A\u0440\u043E\u0439\u0442\u0435 QR \u043D\u0430 \u0442\u0435\u043B\u0435\u0444\u043E\u043D\u0435. \u0414\u043B\u044F \u041F\u041A \u043C\u043E\u0436\u043D\u043E \u0441\u043A\u043E\u043F\u0438\u0440\u043E\u0432\u0430\u0442\u044C \u043E\u0434\u043D\u043E\u0440\u0430\u0437\u043E\u0432\u0443\u044E \u0441\u0441\u044B\u043B\u043A\u0443." }), SP_JSX.jsx(DFL.DialogButton, { className: "dai-button", onClick: () => { if (remote.url)
                                    copy(remote.url); }, children: "\u0421\u043A\u043E\u043F\u0438\u0440\u043E\u0432\u0430\u0442\u044C \u0441\u0441\u044B\u043B\u043A\u0443" })] }), remote.state === "pending" && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsxs("p", { children: ["\u041A\u043E\u0434 \u0431\u0440\u0430\u0443\u0437\u0435\u0440\u0430 ", SP_JSX.jsx("strong", { children: remote.code }), ". \u0421\u0432\u0435\u0440\u044C\u0442\u0435 \u0435\u0433\u043E \u0441 \u044D\u043A\u0440\u0430\u043D\u043E\u043C \u0442\u0435\u043B\u0435\u0444\u043E\u043D\u0430 \u0438\u043B\u0438 \u041F\u041A."] }), SP_JSX.jsx(DFL.DialogButton, { className: "dai-button dai-primary", disabled: busy, onClick: () => send("pair_confirm", { code: remote.code }), children: "\u041A\u043E\u0434 \u0441\u043E\u0432\u043F\u0430\u0434\u0430\u0435\u0442, \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0438\u0442\u044C" })] }), remote.state === "connected" && SP_JSX.jsx("p", { role: "status", children: "\u0411\u0440\u0430\u0443\u0437\u0435\u0440 \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0451\u043D \u043A \u044D\u0442\u043E\u0439 \u0434\u0438\u0430\u0433\u043D\u043E\u0441\u0442\u0438\u043A\u0435." }), remote.state !== "off" && SP_JSX.jsx(DFL.DialogButton, { className: "dai-button", disabled: busy, onClick: () => send("pair_stop"), children: "\u041E\u0442\u043A\u043B\u044E\u0447\u0438\u0442\u044C \u043F\u0443\u043B\u044C\u0442" })] })] });
}

const snapshot = callable("get_snapshot");
const refresh = callable("refresh");
const selectThread = callable("select_thread");
const newThread = callable("new_thread");
const saveSettings = callable("save_settings");
const sendContext = (value) => ({ provider: value.provider, host: value.remoteHost || "", threadId: value.threadId });
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
const readPolledSnapshot = createSnapshotReader(snapshot);
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
    const [draft, setDraft] = SP_REACT.useState(() => drafts.read(draftOwner(session.snapshot)));
    const draftId = SP_REACT.useRef(draftOwner(session.snapshot));
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
    const pendingAuto = SP_REACT.useRef(null);
    const countdownDraft = SP_REACT.useRef(null);
    const [quickOpen, setQuickOpen] = SP_REACT.useState(false);
    const [quickSource, setQuickSource] = SP_REACT.useState(() => localStorage.getItem("deck-ai-quick"));
    const quickActions = parseQuickActions(quickSource);
    const autoSendRef = SP_REACT.useRef(autoSend);
    autoSendRef.current = autoSend;
    const [confirmApproval, setConfirmApproval] = SP_REACT.useState("");
    const [filesOpen, setFilesOpen] = SP_REACT.useState(false);
    const [folder, setFolder] = SP_REACT.useState("~");
    const [folderHost, setFolderHost] = SP_REACT.useState("");
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
        const nextOwner = draftOwner(next);
        if (nextOwner !== draftId.current) {
            draftId.current = nextOwner;
            setDraft(drafts.read(nextOwner));
            setImagesState(session.attachments.get(nextOwner) || []);
            pendingAuto.current = null;
            countdownDraft.current = null;
            setCountdown(null);
            followTail.current = true;
            setShowLatest(false);
        }
        historySnapshots.set(historyKey(next), next);
        while (historySnapshots.size > 12)
            historySnapshots.delete(historySnapshots.keys().next().value);
        session.snapshot = next;
        setData(next);
        if (next.voiceId && ["recording", "stopping", "processing"].includes(next.voiceState)) {
            session.dictation = bindDictation(session.dictation, next.voiceId, nextOwner, drafts.read(nextOwner));
            localStorage.setItem(dictationKey, JSON.stringify(session.dictation));
        }
        if (next.voiceId && next.voiceId !== session.discardedVoice && next.voiceText && next.voiceState === "done") {
            const id = next.voiceId;
            const owner = session.dictation?.id === id ? session.dictation.thread : nextOwner;
            const update = updateDictation(session.dictation, id, owner, next.voiceText, drafts.read(owner));
            session.dictation = update.session;
            localStorage.setItem(dictationKey, JSON.stringify(session.dictation));
            if (update.value !== null) {
                drafts.write(owner, update.value);
                if (owner === draftId.current)
                    setDraft(update.value);
                if (autoSendRef.current && owner === draftId.current)
                    pendingAuto.current = { owner, text: update.value };
            }
            lastVoice.current = next.voiceText;
            session.voiceText = next.voiceText;
        }
        else if (!next.voiceId && next.voiceState === "done" && next.voiceText && next.voiceText !== session.voiceText) {
            lastVoice.current = next.voiceText;
            session.voiceText = next.voiceText;
            const existing = drafts.read(nextOwner).trimEnd();
            drafts.write(nextOwner, (existing ? existing + " " : "") + next.voiceText.trim() + " ");
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
            const next = await readPolledSnapshot(revision, voicePolling ? 440 : 2350);
            if (mounted.current && viewGate.current(revision)) {
                accept(next);
                setConnectionError("");
            }
        }
        catch {
            if (mounted.current && viewGate.current(revision))
                setConnectionError("Связь с Deck AI прервалась. Повторяю подключение…");
        }
        finally {
            inFlight.current = false;
        }
    }, [accept, voicePolling]);
    SP_REACT.useEffect(() => { mounted.current = true; void load(); const timer = setInterval(() => void load(), voicePolling ? 500 : 2500); return () => { mounted.current = false; clearInterval(timer); }; }, [load, voicePolling]);
    SP_REACT.useEffect(() => { const el = chatRef.current; if (el && followTail.current)
        el.scrollTop = el.scrollHeight; }, [data?.messages, tab]);
    const editDraft = (value, owner = draftId.current) => {
        if (owner === draftId.current) {
            pendingAuto.current = null;
            countdownDraft.current = null;
            setCountdown(null);
        }
        drafts.write(owner, value);
    };
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
        const sentAttachments = session.attachments.get(sentThread);
        await sendMessage(withGameContext(sentDraft, currentGame(), localStorage.getItem("deck-ai-game-context") === "on"), images.map(x => x.path), model?.id || "", effort, tier, sendContext(data));
        if (drafts.read(sentThread) === sentDraft) {
            drafts.write(sentThread, "");
            if (draftId.current === sentThread)
                setDraft("");
        }
        if (session.attachments.get(sentThread) === sentAttachments)
            publishAttachments(sentThread, []);
        setNotice("Запрос принят · в очереди");
        followTail.current = true;
        accept(await snapshot());
    });
    const submitRef = SP_REACT.useRef(submit);
    submitRef.current = submit;
    SP_REACT.useEffect(() => {
        const pending = pendingAuto.current;
        if (pending?.owner === draftId.current && !recording && !voiceProcessing && draft.trim()) {
            pendingAuto.current = null;
            if (pending.text === draft) {
                countdownDraft.current = pending;
                setCountdown(3);
            }
        }
    }, [draft, recording, voiceProcessing]);
    SP_REACT.useEffect(() => {
        if (countdown === null)
            return;
        if (countdown <= 0) {
            setCountdown(null);
            const pending = countdownDraft.current;
            countdownDraft.current = null;
            if (pending?.owner === draftId.current && drafts.read(pending.owner) === pending.text)
                submitRef.current();
            return;
        }
        const timer = setTimeout(() => setCountdown(value => value === null ? null : value - 1), 1000);
        return () => clearTimeout(timer);
    }, [countdown]);
    const quick = (text) => void run(async () => { if (!data)
        return; await sendMessage(text, [], model?.id || "", effort, tier, sendContext(data)); setNotice("Запрос принят · в очереди"); setQuickOpen(false); followTail.current = true; accept(await snapshot()); });
    const ro = !!data?.readOnly;
    const filesStale = (file?.host ?? folderHost) !== (data?.remoteHost || "");
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
    const openFolder = (path) => void run(async () => { const result = await fileList(path, data?.remoteHost || ""); setFolder(result.path); setFolderHost(result.host); setEntries(sortEntries(result.entries)); setFile(null); });
    const openFile = (path) => void run(async () => { const result = await fileRead(path, folderHost); setFile(result); setFileText(result.text); });
    const saveFile = () => void run(async () => { if (!file)
        return; const result = await fileWrite(file.path, fileText, file.sha256, file.host); setFile({ ...file, text: fileText, sha256: result.sha256 }); setNotice("Файл сохранён · копия: " + file.path.split("/").pop() + ".deckai.bak"); });
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
    const attachMedia = (incoming) => {
        const previous = session.attachments.get(draftId.current) || [];
        const result = appendAttachments(previous, incoming);
        if (result.omitted && !result.added) {
            setError("Достигнут лимит пяти изображений. Уберите лишние вложения, чтобы прикрепить другое.");
            return;
        }
        if (result.omitted)
            setNotice(`Добавлено изображений: ${result.added}. Для остальных освободите место. Лимит — пять.`);
        setImages(result.images);
        setMediaOpen(false);
    };
    const attach = (media) => { if (media)
        attachMedia([media]); };
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
        }, children: [SP_JSX.jsx("style", { children: css }), SP_JSX.jsx("span", { ref: touchAnchor, hidden: true }), fullscreen && SP_JSX.jsxs(DFL.Focusable, { className: "dai-full-header", "flow-children": "horizontal", children: [SP_JSX.jsxs("div", { className: "dai-full-brand", children: [SP_JSX.jsx("h1", { children: "Deck AI" }), SP_JSX.jsx("span", { children: tab === "repair" ? "Локальная диагностика" : disconnect ? "Нет соединения" : data?.active ? "Deck AI работает…" : gameStatus })] }), SP_JSX.jsx(GameCheckbox, { checked: gameContextEnabled, onChange: toggleGameContext }), SP_JSX.jsxs(Action, { onClick: () => closeFullscreen(), children: [SP_JSX.jsx(FaCompress, {}), "\u0412 \u043F\u0430\u043D\u0435\u043B\u044C"] }), SP_JSX.jsxs(Action, { onClick: () => closeFullscreen(false), children: [SP_JSX.jsx(FaArrowLeft, {}), "\u041A \u0438\u0433\u0440\u0435"] })] }), SP_JSX.jsx(DFL.Focusable, { className: "dai-tabs", "flow-children": "horizontal", role: "tablist", "aria-label": "Deck AI", children: [["chat", "Чат", SP_JSX.jsx(FaComment, {})], ["history", "История", SP_JSX.jsx(FaHistory, {})], ["repair", "Ремонт", SP_JSX.jsx(FaGamepad, {})], ["settings", "Настройки", SP_JSX.jsx(FaCog, {})]].map(([id, label, icon]) => SP_JSX.jsx("div", { role: "tab", "aria-selected": tab === id, className: "dai-tab " + (tab === id ? "selected" : ""), children: SP_JSX.jsxs(Action, { disabled: busy, onClick: () => { if ((id === "settings" || id === "repair") && !fullscreen)
                            openFullscreen(id);
                        else {
                            setTab(id);
                            setMediaOpen(false);
                            setQueueOpen(false);
                        } }, children: [icon, SP_JSX.jsx("span", { children: label })] }) }, id)) }), SP_JSX.jsxs("div", { className: "dai-viewbar", children: [SP_JSX.jsxs("div", { className: "dai-status", children: [SP_JSX.jsx("span", { className: "dai-dot " + (disconnect ? "offline" : data?.active ? "working" : "") }), SP_JSX.jsx("span", { children: !data ? "Подключение…" : data.ready ? (data.active ? "Deck AI работает…" : gameStatus) : (data.retryIn ? `Нет связи · повтор через ${data.retryIn} с` : "Нет соединения") }), data?.remoteHost && SP_JSX.jsx("small", { children: data.remoteHost }), !!data?.runningCount && SP_JSX.jsxs("small", { className: "dai-running-count", children: [data.runningCount, " \u0432 \u0440\u0430\u0431\u043E\u0442\u0435"] })] }), !fullscreen && SP_JSX.jsx(GameCheckbox, { checked: gameContextEnabled, onChange: toggleGameContext }), !fullscreen && SP_JSX.jsxs(Action, { disabled: busy, onClick: () => openFullscreen(tab), children: [SP_JSX.jsx(FaExpand, {}), "\u041D\u0430 \u0432\u0435\u0441\u044C \u044D\u043A\u0440\u0430\u043D"] })] }), tab !== "repair" && (error || connectionError) && SP_JSX.jsxs("div", { className: "dai-banner", role: "alert", children: [SP_JSX.jsx("span", { children: error || connectionError }), SP_JSX.jsx(Action, { onClick: () => { setError(""); setConnectionError(""); }, children: "\u0417\u0430\u043A\u0440\u044B\u0442\u044C" })] }), tab !== "repair" && !error && !connectionError && (data?.historyWarning || data?.ready === false) && SP_JSX.jsxs("div", { className: "dai-banner", role: "status", children: [SP_JSX.jsx("span", { children: data.historyWarning || data.status }), SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { accept(await refresh()); }), children: "\u041F\u043E\u0432\u0442\u043E\u0440\u0438\u0442\u044C \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u0435" })] }), notice && SP_JSX.jsx("div", { className: "dai-notice", role: "status", children: notice }), SP_JSX.jsxs("div", { className: "dai-page", role: "tabpanel", "aria-label": tab === "chat" ? "Чат" : tab === "history" ? "История" : tab === "repair" ? "Ремонт" : "Настройки", children: [tab === "repair" && SP_JSX.jsx(GameScroll, { className: "dai-scroll dai-stack", children: SP_JSX.jsx(RepairPanel, { copy: copyMessage }) }), tab === "chat" && SP_JSX.jsxs("div", { className: "dai-chat-layout", children: [sidebar, SP_JSX.jsx("div", { className: "dai-chat-main" + (data?.approvals?.length ? " has-approvals" : ""), children: queueOpen ? SP_JSX.jsx(GameScroll, { ref: queueRef, className: "dai-scroll dai-stack dai-queue-view", children: SP_JSX.jsxs("div", { className: "dai-stack-content", children: [SP_JSX.jsx(Action, { onClick: () => setQueueOpen(false), children: "\u2190 \u041A \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044E" }), SP_JSX.jsxs("h3", { children: ["\u041E\u0447\u0435\u0440\u0435\u0434\u044C \u0437\u0430\u043F\u0440\u043E\u0441\u043E\u0432 \u00B7 ", data?.queueTotal ?? data?.outbox.length ?? 0] }), SP_JSX.jsx("p", { className: "dai-muted", children: "\u041E\u0436\u0438\u0434\u0430\u044E\u0449\u0438\u0435 \u0437\u0430\u043F\u0440\u043E\u0441\u044B \u0435\u0449\u0451 \u043D\u0435 \u043E\u0442\u043F\u0440\u0430\u0432\u043B\u0435\u043D\u044B. \u0417\u0430\u043F\u0440\u043E\u0441\u044B \u0432\u044B\u043F\u043E\u043B\u043D\u044F\u044E\u0442\u0441\u044F \u043F\u043E \u043E\u0447\u0435\u0440\u0435\u0434\u0438; \u0437\u0430\u043D\u044F\u0442\u044B\u0439 \u0447\u0430\u0442 \u0436\u0434\u0451\u0442 \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043D\u0438\u044F \u0442\u0435\u043A\u0443\u0449\u0435\u0433\u043E \u043E\u0442\u0432\u0435\u0442\u0430." }), SP_JSX.jsxs("p", { className: "dai-muted", children: ["\u0412 \u044D\u0442\u043E\u043C \u0447\u0430\u0442\u0435 \u043E\u0436\u0438\u0434\u0430\u044E\u0442: ", queueCounts(data?.outbox || [], data?.threadId || "", data?.remoteHost || "").current, ". \u0412 \u0434\u0440\u0443\u0433\u0438\u0445 \u0447\u0430\u0442\u0430\u0445: ", queueCounts(data?.outbox || [], data?.threadId || "", data?.remoteHost || "").other, "."] }), (data?.queueTotal || 0) > (data?.outbox.length || 0) && SP_JSX.jsxs("p", { className: "dai-muted", children: ["\u041F\u043E\u043A\u0430\u0437\u0430\u043D\u044B \u043F\u043E\u0441\u043B\u0435\u0434\u043D\u0438\u0435 ", data?.outbox.length, " \u0437\u0430\u043F\u0440\u043E\u0441\u043E\u0432."] }), !data?.outbox.length && SP_JSX.jsx("p", { className: "dai-muted", children: "\u041E\u0447\u0435\u0440\u0435\u0434\u044C \u043F\u0443\u0441\u0442\u0430." }), data?.outbox.map(job => SP_JSX.jsxs("section", { className: "dai-section dai-queue-item", children: [SP_JSX.jsx("strong", { children: queueStatus(job) }), SP_JSX.jsxs("small", { className: "dai-muted", children: [sameChat(job, data.threadId, data.remoteHost || "") ? "Этот чат" : (job.host || "") !== (data.remoteHost || "") ? "Другое устройство · " + (job.host || "Steam Deck") : (data.threads.find(thread => thread.id === job.threadId)?.name || "Другой чат").slice(0, 80), job.createdAt ? " · " + new Date(job.createdAt * 1000).toLocaleString() : ""] }), SP_JSX.jsx("p", { className: "dai-queue-text", children: expandedJob === job.id ? job.text : job.text.slice(0, 180) + (job.text.length > 180 ? "…" : "") }), job.text.length > 180 && SP_JSX.jsx(Action, { onClick: () => setExpandedJob(expandedJob === job.id ? "" : job.id), children: expandedJob === job.id ? "Свернуть текст" : "Весь текст запроса" }), job.error && SP_JSX.jsx("p", { className: "dai-muted", children: job.error }), job.status === "queued" && SP_JSX.jsx(Action, { disabled: busy || ro, onClick: () => void run(async () => { await queueFront(job.id); accept(await snapshot()); }), children: "\u2191 \u041E\u0442\u043F\u0440\u0430\u0432\u0438\u0442\u044C \u043F\u0435\u0440\u0432\u044B\u043C" }), (job.status === "queued" || job.status === "error") && SP_JSX.jsx(Action, { disabled: busy || ro, onClick: () => void run(async () => { await queueRemove(job.id); accept(await snapshot()); }), children: "\u0423\u0434\u0430\u043B\u0438\u0442\u044C \u0438\u0437 \u043E\u0447\u0435\u0440\u0435\u0434\u0438" }), job.threadId && SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { if ((job.host || "") !== (data?.remoteHost || ""))
                                                            accept(await remoteHost(job.host || "")); accept(await selectThread(job.threadId)); setTab("chat"); setQueueOpen(false); }), children: "\u041E\u0442\u043A\u0440\u044B\u0442\u044C \u0447\u0430\u0442" })] }, job.id))] }) }, "queue") : mediaOpen ? SP_JSX.jsx(GameScroll, { className: "dai-scroll dai-stack", children: SP_JSX.jsxs("div", { className: "dai-stack-content", children: [SP_JSX.jsx(Action, { onClick: () => setMediaOpen(false), children: "\u2190 \u041A \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044E" }), SP_JSX.jsxs("section", { className: "dai-section dai-game-context", children: [SP_JSX.jsxs("h3", { children: [SP_JSX.jsx(FaGamepad, {}), " \u041A\u043E\u043D\u0442\u0435\u043A\u0441\u0442 \u0438\u0433\u0440\u044B"] }), SP_JSX.jsx("p", { className: "dai-muted", children: game ? game.name : "Сейчас Steam не сообщает о запущенной игре." }), game && SP_JSX.jsx("p", { className: "dai-muted", children: game.status || "Игра не передаёт описание текущего места или задания." }), game?.details.map(([key, value]) => SP_JSX.jsxs("p", { className: "dai-muted", children: [key, ": ", value] }, key)), SP_JSX.jsx(GameCheckbox, { checked: gameContextEnabled, onChange: toggleGameContext }), game && SP_JSX.jsxs(Action, { disabled: !currentScreenshots.length, onClick: () => attach(currentScreenshots[0]), children: ["\u0421\u043D\u0438\u043C\u043E\u043A \u0438\u0437 \u044D\u0442\u043E\u0439 \u0438\u0433\u0440\u044B", currentScreenshots[0]?.when ? " · " + new Date(currentScreenshots[0].when * 1000).toLocaleString() : ""] }), SP_JSX.jsx("p", { className: "dai-muted", children: "\u0427\u0442\u043E\u0431\u044B \u043F\u043E\u043A\u0430\u0437\u0430\u0442\u044C, \u0433\u0434\u0435 \u0432\u044B \u0441\u0435\u0439\u0447\u0430\u0441: \u0441\u0434\u0435\u043B\u0430\u0439\u0442\u0435 \u0441\u043D\u0438\u043C\u043E\u043A \u0432 \u0438\u0433\u0440\u0435 \u2014 Steam + R1, \u0437\u0430\u0442\u0435\u043C \u043F\u0440\u0438\u043A\u0440\u0435\u043F\u0438\u0442\u0435 \u0435\u0433\u043E \u0437\u0434\u0435\u0441\u044C. \u0413\u0430\u043B\u043E\u0447\u043A\u0430 \u00AB\u0418\u0433\u0440\u0430\u00BB \u0434\u043E\u0431\u0430\u0432\u043B\u044F\u0435\u0442 \u043A \u0432\u043E\u043F\u0440\u043E\u0441\u0443 \u0442\u043E\u043B\u044C\u043A\u043E \u043D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u0438\u0433\u0440\u044B." })] }), SP_JSX.jsx("h3", { children: "\u0414\u0440\u0443\u0433\u0438\u0435 \u0432\u043B\u043E\u0436\u0435\u043D\u0438\u044F" }), SP_JSX.jsx(Action, { disabled: !data?.screenshots.length, onClick: () => attach(data?.screenshots[0]), children: "\u041F\u043E\u0441\u043B\u0435\u0434\u043D\u0438\u0439 \u0441\u043A\u0440\u0438\u043D\u0448\u043E\u0442" }), SP_JSX.jsx(Choice, { label: "\u0414\u0440\u0443\u0433\u043E\u0439 \u0441\u043A\u0440\u0438\u043D\u0448\u043E\u0442", value: shot, options: (data?.screenshots || []).map(x => ({ data: x.path, label: x.name })), onChange: setShot }), SP_JSX.jsx(Action, { disabled: !shot, onClick: () => attach(data?.screenshots.find(x => x.path === shot)), children: "\u041F\u0440\u0438\u043A\u0440\u0435\u043F\u0438\u0442\u044C \u0441\u043A\u0440\u0438\u043D\u0448\u043E\u0442" }), SP_JSX.jsx(Choice, { label: "\u0412\u0438\u0434\u0435\u043E\u0437\u0430\u043F\u0438\u0441\u044C", value: video, options: (data?.videos || []).map(x => ({ data: x.path, label: x.name })), onChange: setVideo }), SP_JSX.jsx(Action, { disabled: !video || busy, onClick: () => void run(async () => { const result = await videoFrames(video); attachMedia(result.frames); }), children: "\u0414\u043E\u0431\u0430\u0432\u0438\u0442\u044C \u043A\u0430\u0434\u0440\u044B \u0438\u0437 \u0432\u0438\u0434\u0435\u043E" }), !data?.screenshots.length && !data?.videos.length && SP_JSX.jsx("p", { className: "dai-muted", children: "\u0421\u0434\u0435\u043B\u0430\u0439\u0442\u0435 \u0441\u043A\u0440\u0438\u043D\u0448\u043E\u0442 \u0432 \u0438\u0433\u0440\u0435: Steam + R1. \u041E\u043D \u043F\u043E\u044F\u0432\u0438\u0442\u0441\u044F \u0437\u0434\u0435\u0441\u044C." })] }) }) : SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsxs(DFL.Focusable, { className: "dai-toolbar", "flow-children": "horizontal", children: [SP_JSX.jsxs(Action, { disabled: busy || disconnect || ro || data?.active, onClick: startChat, children: [SP_JSX.jsx(FaPlus, {}), SP_JSX.jsx("span", { children: "\u041D\u043E\u0432\u044B\u0439" })] }), SP_JSX.jsxs(Action, { disabled: busy || disconnect, onClick: openFiles, children: [SP_JSX.jsx(FaFolderOpen, {}), SP_JSX.jsx("span", { children: "\u0424\u0430\u0439\u043B\u044B" })] }), SP_JSX.jsxs(Action, { onClick: () => setQueueOpen(true), children: [SP_JSX.jsx(FaListUl, {}), SP_JSX.jsxs("span", { children: ["\u041E\u0447\u0435\u0440\u0435\u0434\u044C", (data?.queueTotal || data?.outbox.length) ? " · " + (data?.queueTotal ?? data?.outbox.length) : ""] })] }), SP_JSX.jsxs(Action, { disabled: busy, onClick: () => void run(async () => { accept(await refresh()); setNotice("Обновлено"); }), children: [SP_JSX.jsx(FaSyncAlt, {}), SP_JSX.jsx("span", { children: "\u041E\u0431\u043D\u043E\u0432\u0438\u0442\u044C" })] })] }), SP_JSX.jsx(GameScroll, { className: "dai-messages", ref: chatRef, onScroll: () => { const el = chatRef.current; if (el) {
                                                followTail.current = el.scrollHeight - el.scrollTop - el.clientHeight < 60;
                                                setShowLatest(!followTail.current);
                                            } }, children: SP_JSX.jsxs("div", { className: "dai-message-list", children: [!data?.messages.length && SP_JSX.jsxs("div", { className: "dai-empty", children: [SP_JSX.jsx(FaComment, {}), SP_JSX.jsx("h3", { children: "\u041F\u043E\u043C\u043E\u0449\u044C \u043F\u0440\u044F\u043C\u043E \u0432 \u0438\u0433\u0440\u0435" }), SP_JSX.jsxs("p", { children: ["\u0417\u0430\u0434\u0430\u0439\u0442\u0435 \u0432\u043E\u043F\u0440\u043E\u0441 \u0442\u0435\u043A\u0441\u0442\u043E\u043C \u0438\u043B\u0438 \u0433\u043E\u043B\u043E\u0441\u043E\u043C.", SP_JSX.jsx("br", {}), "\u041C\u043E\u0436\u043D\u043E \u0434\u043E\u0431\u0430\u0432\u0438\u0442\u044C \u0441\u043A\u0440\u0438\u043D\u0448\u043E\u0442."] }), disconnect && SP_JSX.jsx(Action, { onClick: () => void run(async () => accept(await refresh())), disabled: busy, children: busy ? "Подключение…" : "Подключиться" })] }), data?.hasOlderMessages && SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { followTail.current = false; accept(await olderMessages()); requestAnimationFrame(() => { if (chatRef.current)
                                                            chatRef.current.scrollTop = 0; }); }), children: "\u041F\u043E\u043A\u0430\u0437\u0430\u0442\u044C \u043F\u0440\u0435\u0434\u044B\u0434\u0443\u0449\u0438\u0435 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F" }), data?.messages.map((message, i) => message.role === "tool" ? SP_JSX.jsx(DFL.Focusable, { className: "dai-message tool", focusClassName: "dai-focused", onActivate: () => setOpenTool(openTool === (message.id || String(i)) ? "" : (message.id || String(i))), children: SP_JSX.jsx("pre", { children: openTool === (message.id || String(i)) ? message.text : message.text.split("\n").slice(0, 3).join("\n") + (message.text.split("\n").length > 3 ? "\n…" : "") }) }, message.id || i) : SP_JSX.jsxs(DFL.Focusable, { className: "dai-message " + message.role, focusClassName: "dai-focused", children: [SP_JSX.jsx("small", { children: message.role === "user" ? "Вы" : names[data.provider]?.split(" · ")[0] || "AI" }), SP_JSX.jsx("div", { children: message.text }), !!message.attachments?.length && SP_JSX.jsx(MessageAttachments, { items: message.attachments }), SP_JSX.jsxs("div", { className: "dai-message-tools", children: [SP_JSX.jsxs(Action, { onClick: () => copyMessage(message.text), children: [SP_JSX.jsx(FaCopy, {}), "\u041A\u043E\u043F\u0438\u0440\u043E\u0432\u0430\u0442\u044C"] }), message.role === "assistant" && !!window.speechSynthesis && SP_JSX.jsx(Action, { onClick: () => speak(message.id || String(i), message.text), children: speaking === (message.id || String(i)) ? "■ Стоп" : "🔊 Озвучить" })] })] }, message.id || i)), (data ? chatFailures(data.outbox, data.threadId, data.remoteHost || "") : []).map(x => SP_JSX.jsxs("div", { className: "dai-failed", children: [SP_JSX.jsx("p", { children: x.error || "Не удалось отправить" }), SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { await retry(x.id); accept(await snapshot()); }), children: "\u041F\u043E\u0432\u0442\u043E\u0440\u0438\u0442\u044C \u043E\u0442\u043F\u0440\u0430\u0432\u043A\u0443" })] }, x.id))] }) }), showLatest && SP_JSX.jsx("div", { className: "dai-latest", children: SP_JSX.jsx(Action, { onClick: jumpToLatest, children: "\u2193 \u041A \u043F\u043E\u0441\u043B\u0435\u0434\u043D\u0435\u043C\u0443 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044E" }) }), ro && SP_JSX.jsx("div", { className: "dai-notice", role: "status", children: "\u0420\u0435\u0436\u0438\u043C \u0442\u043E\u043B\u044C\u043A\u043E \u0447\u0442\u0435\u043D\u0438\u044F: \u043E\u0442\u043F\u0440\u0430\u0432\u043A\u0430, \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u044F \u0438 \u043F\u0440\u0430\u0432\u043A\u0438 \u043E\u0442\u043A\u043B\u044E\u0447\u0435\u043D\u044B." }), !!data?.approvals?.length && SP_JSX.jsx(GameScroll, { className: "dai-approvals", role: "alert", children: data.approvals.map(item => SP_JSX.jsxs("div", { className: "dai-approval", children: [SP_JSX.jsxs("strong", { children: ["\u041D\u0443\u0436\u043D\u043E \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u0435 \u00B7 ", item.title] }), SP_JSX.jsx("span", { className: "dai-muted", children: item.summary }), SP_JSX.jsxs(DFL.Focusable, { className: "dai-compose-actions", "flow-children": "horizontal", children: [SP_JSX.jsx(Action, { primary: true, disabled: busy || ro, onClick: () => decide(item, "accept"), children: confirmApproval === item.key ? "Нажмите ещё раз" : "Разрешить" }), SP_JSX.jsx(Action, { disabled: busy || ro, onClick: () => decide(item, "decline"), children: "\u041E\u0442\u043A\u043B\u043E\u043D\u0438\u0442\u044C" })] })] }, item.key)) }), SP_JSX.jsxs("div", { className: "dai-composer", children: [countdown !== null && SP_JSX.jsxs("div", { className: "dai-notice", role: "status", children: ["\u041E\u0442\u043F\u0440\u0430\u0432\u043A\u0430 \u0447\u0435\u0440\u0435\u0437 ", countdown, " \u0441", SP_JSX.jsx(Action, { onClick: () => setCountdown(null), children: "\u041E\u0442\u043C\u0435\u043D\u0438\u0442\u044C \u043E\u0442\u043F\u0440\u0430\u0432\u043A\u0443" })] }), quickOpen && data?.threadId && SP_JSX.jsx(DFL.Focusable, { className: "dai-quick", "flow-children": "horizontal", children: quickActions.map(([label, text]) => SP_JSX.jsx(Action, { disabled: busy || disconnect || ro, onClick: () => quick(text), children: label }, label)) }), data?.outbox.some(job => job.status === "recovering") && SP_JSX.jsx("p", { className: "dai-muted dai-queue-state", role: "status", children: "\u041F\u0440\u043E\u0432\u0435\u0440\u044F\u044E \u0441\u043E\u0441\u0442\u043E\u044F\u043D\u0438\u0435 \u043E\u0442\u043F\u0440\u0430\u0432\u043B\u0435\u043D\u043D\u043E\u0433\u043E \u0437\u0430\u043F\u0440\u043E\u0441\u0430\u2026" }), !!data?.outbox.length && SP_JSX.jsx("div", { className: "dai-queue-summary", children: SP_JSX.jsxs(Action, { onClick: () => setQueueOpen(true), children: ["\u041E\u0447\u0435\u0440\u0435\u0434\u044C \u00B7 ", data.queueTotal ?? data.outbox.length, " \u00B7 \u043F\u043E\u0441\u043C\u043E\u0442\u0440\u0435\u0442\u044C"] }) }), images.length > 0 && SP_JSX.jsx("div", { className: "dai-attachments", children: images.map((image, i) => SP_JSX.jsxs(Action, { onClick: () => setImages(old => old.filter((_, n) => n !== i)), children: ["\u00D7 ", image.name] }, image.path + ":" + i)) }), (recording || voiceProcessing) && SP_JSX.jsxs("div", { className: "dai-voice-preview", role: "status", "aria-live": "polite", children: [SP_JSX.jsx("span", { className: "dai-record-dot", "aria-hidden": "true" }), SP_JSX.jsxs("div", { children: [SP_JSX.jsx("strong", { children: recording ? "● Запись · распознанный текст" : "Завершаю распознавание…" }), SP_JSX.jsx("span", { role: "textbox", "aria-label": "\u0420\u0430\u0441\u043F\u043E\u0437\u043D\u0430\u043D\u043D\u0430\u044F \u0440\u0435\u0447\u044C", "aria-readonly": "true", children: (data?.voiceId !== session.discardedVoice ? data?.voiceText : "") || (["ru", "en", "ru-fast", "en-fast"].includes(lang) ? "Здесь появится распознанная речь" : "Записываю. Текст появится после «Стоп».") })] })] }), data?.threadId && draftOwner(data) !== data.threadId && !draft && !!drafts.read(data.threadId) &&
                                                    SP_JSX.jsx(Action, { disabled: busy || recording || voiceProcessing, onClick: () => editDraft(drafts.read(data.threadId)), children: "\u0412\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u0438\u0442\u044C \u0441\u0442\u0430\u0440\u044B\u0439 \u0447\u0435\u0440\u043D\u043E\u0432\u0438\u043A" }), SP_JSX.jsx("form", { style: { display: "contents" }, onSubmit: e => { e.preventDefault(); submit(); }, children: SP_JSX.jsx("div", { className: "dai-draft-field", "data-draft-owner": draftOwner(data), onInputCapture: e => { const target = e.target; if (target.tagName === "INPUT")
                                                            editDraft(target.value, e.currentTarget.dataset.draftOwner || ""); }, children: SP_JSX.jsx(DFL.TextField, { disabled: recording || voiceProcessing, value: draft, placeholder: "\u0421\u043F\u0440\u043E\u0441\u0438\u0442\u044C \u043E\u0431 \u0438\u0433\u0440\u0435\u2026", onChange: e => editDraft(e.target.value, e.target.closest(".dai-draft-field")?.dataset.draftOwner ?? draftId.current), onKeyDown: e => { if ((e.key === "Enter" || e.keyCode === 13) && !e.shiftKey && !e.nativeEvent.isComposing) {
                                                                e.preventDefault();
                                                                submit();
                                                            } } }) }, draftOwner(data) || "new") }), SP_JSX.jsxs(DFL.Focusable, { className: "dai-compose-actions", "flow-children": "horizontal", children: [SP_JSX.jsxs(Action, { recording: recording || voiceProcessing, disabled: !data || voiceProcessing || busy, onClick: () => void toggleVoice(), children: [SP_JSX.jsx(FaMicrophone, {}), recording ? "Стоп" : "Голос"] }), !!data?.threadId && SP_JSX.jsx(Action, { disabled: recording || voiceProcessing, onClick: () => setQuickOpen(!quickOpen), children: "\u26A1" }), SP_JSX.jsx(Action, { disabled: voiceStarting || (!draft.trim() && !recording && !voiceProcessing), onClick: clearDraft, children: "\u041E\u0447\u0438\u0441\u0442\u0438\u0442\u044C" }), fullscreen && data?.active && data.provider === "codex" && SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { await stop(); accept(await snapshot()); }), children: "\u0421\u0442\u043E\u043F" }), SP_JSX.jsx(Action, { primary: true, disabled: busy || disconnect || ro || recording || voiceProcessing || !draft.trim(), onClick: submit, children: busy ? "…" : "Отправить" })] }), !fullscreen && data?.active && data.provider === "codex" && SP_JSX.jsx(Action, { disabled: busy, onClick: () => void run(async () => { await stop(); accept(await snapshot()); }), children: "\u041E\u0441\u0442\u0430\u043D\u043E\u0432\u0438\u0442\u044C \u043E\u0442\u0432\u0435\u0442" })] })] }) })] }), tab === "history" && filesOpen && SP_JSX.jsx(GameScroll, { className: "dai-scroll dai-stack", children: SP_JSX.jsxs("div", { className: "dai-stack-content", children: [SP_JSX.jsxs(Action, { disabled: busy, onClick: () => { if (file)
                                        setFile(null);
                                    else
                                        setFilesOpen(false); }, children: ["\u2190 ", file ? "К папке" : "Назад"] }), SP_JSX.jsx("h3", { children: file ? file.path.split("/").pop() : folder }), SP_JSX.jsxs("p", { className: "dai-muted", children: ["\u0423\u0441\u0442\u0440\u043E\u0439\u0441\u0442\u0432\u043E \u00B7 ", (file?.host ?? folderHost) || "Steam Deck"] }), filesStale && SP_JSX.jsx("p", { role: "status", children: "\u0412\u044B\u0431\u0440\u0430\u043D\u043E \u0434\u0440\u0443\u0433\u043E\u0435 \u0443\u0441\u0442\u0440\u043E\u0439\u0441\u0442\u0432\u043E. \u0412\u0435\u0440\u043D\u0438\u0442\u0435\u0441\u044C \u043A \u0438\u0441\u0445\u043E\u0434\u043D\u043E\u043C\u0443 \u0443\u0441\u0442\u0440\u043E\u0439\u0441\u0442\u0432\u0443, \u0447\u0442\u043E\u0431\u044B \u0441\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u043F\u0440\u0430\u0432\u043A\u0438 \u0438\u043B\u0438 \u043F\u0440\u043E\u0434\u043E\u043B\u0436\u0438\u0442\u044C \u043F\u0440\u043E\u0441\u043C\u043E\u0442\u0440 \u043F\u0430\u043F\u043A\u0438." }), !file && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(Action, { disabled: busy || filesStale, onClick: () => openFolder(parentPath(folder)), children: "\u2B11 \u0412\u0432\u0435\u0440\u0445" }), entries.map(name => SP_JSX.jsxs(Action, { disabled: busy || filesStale, onClick: () => isFolder(name) ? openFolder(joinPath(folder, name)) : openFile(joinPath(folder, name)), children: [isFolder(name) ? "📁 " : "📄 ", name] }, name)), !entries.length && SP_JSX.jsx("p", { className: "dai-muted", children: "\u041F\u0430\u043F\u043A\u0430 \u043F\u0443\u0441\u0442\u0430. \u0414\u043E\u0441\u0442\u0443\u043F\u043D\u0430 \u0442\u043E\u043B\u044C\u043A\u043E \u0434\u043E\u043C\u0430\u0448\u043D\u044F\u044F \u043F\u0430\u043F\u043A\u0430; \u043A\u043B\u044E\u0447\u0438 \u0438 \u0441\u0435\u043A\u0440\u0435\u0442\u044B \u0441\u043A\u0440\u044B\u0442\u044B." })] }), file && SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx("textarea", { className: "dai-textarea", value: fileText, spellCheck: false, onChange: e => setFileText(e.target.value) }), SP_JSX.jsxs("p", { className: "dai-muted", children: [fileText === file.text ? "Без изменений" : "Есть несохранённые правки", " \u00B7 \u0434\u043E 64 \u041A\u0411 \u00B7 \u043F\u0435\u0440\u0435\u0434 \u0437\u0430\u043F\u0438\u0441\u044C\u044E \u0441\u043E\u0437\u0434\u0430\u0451\u0442\u0441\u044F \u043A\u043E\u043F\u0438\u044F .deckai.bak"] }), SP_JSX.jsx(Action, { primary: true, disabled: busy || ro || filesStale || fileText === file.text, onClick: saveFile, children: "\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u043D\u0430 \u0443\u0441\u0442\u0440\u043E\u0439\u0441\u0442\u0432\u0435" }), SP_JSX.jsx(Action, { disabled: busy || fileText === file.text, onClick: () => setFileText(file.text), children: "\u041E\u0442\u043C\u0435\u043D\u0438\u0442\u044C \u043F\u0440\u0430\u0432\u043A\u0438" })] })] }) }), tab === "history" && !filesOpen && SP_JSX.jsx(GameScroll, { className: "dai-scroll dai-stack", children: SP_JSX.jsxs("div", { className: "dai-stack-content", children: [SP_JSX.jsx(Action, { primary: true, disabled: busy || disconnect || ro || data?.active, onClick: () => void run(async () => { accept(await newThread()); setTab("chat"); }), children: "\uFF0B \u041D\u043E\u0432\u044B\u0439 \u0447\u0430\u0442" }), SP_JSX.jsxs(Action, { disabled: busy || disconnect, onClick: () => { setFilesOpen(true); openFolder("~"); }, children: ["\uD83D\uDCC1 \u0424\u0430\u0439\u043B\u044B \u043D\u0430 \u0443\u0441\u0442\u0440\u043E\u0439\u0441\u0442\u0432\u0435", data?.remoteHost ? " · " + data.remoteHost : ""] }), !!data?.recentEvents?.length && SP_JSX.jsxs("section", { className: "dai-section dai-events", children: [SP_JSX.jsx("h3", { children: "\u0427\u0442\u043E \u043F\u0440\u043E\u0438\u0437\u043E\u0448\u043B\u043E" }), data.recentEvents.slice(0, 8).map(item => SP_JSX.jsxs("p", { className: "dai-muted", children: [item.kind === "approval" ? "⏸" : item.kind === "failed" ? "✗" : "✓", " ", new Date(item.at * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }), " \u00B7 ", (item.host || "Steam Deck") + " · " + item.title] }, item.id))] }), (data?.provider === "codex" || !data) && SP_JSX.jsx(Choice, { label: "\u0423\u0441\u0442\u0440\u043E\u0439\u0441\u0442\u0432\u043E", value: data?.remoteHost || "", options: [{ data: "", label: "Этот Steam Deck" }, ...(data?.sshHosts || []).map(x => ({ data: x, label: x }))], disabled: busy || data?.active, onChange: value => void run(async () => accept(await remoteHost(value))) }), data?.remoteHost && SP_JSX.jsxs(Action, { disabled: busy, onClick: () => void run(async () => { accept(await refresh()); setNotice("Список задач обновлён"); }), children: ["\u21BB \u041E\u0431\u043D\u043E\u0432\u0438\u0442\u044C \u0437\u0430\u0434\u0430\u0447\u0438 \u043D\u0430 ", data.remoteHost] }), SP_JSX.jsx(DFL.TextField, { value: historyQuery, placeholder: "\u041D\u0430\u0439\u0442\u0438 \u0440\u0430\u0437\u0433\u043E\u0432\u043E\u0440\u2026", onChange: e => setHistoryQuery(e.target.value) }), (data?.allTasks || []).some(t => t.host !== (data?.remoteHost || "") || t.running) && SP_JSX.jsxs("section", { className: "dai-section dai-all-tasks", children: [SP_JSX.jsx("h3", { children: "\u0417\u0430\u0434\u0430\u0447\u0438 \u043D\u0430 \u0432\u0441\u0435\u0445 \u0443\u0441\u0442\u0440\u043E\u0439\u0441\u0442\u0432\u0430\u0445" }), (data?.allTasks || []).filter(t => t.host !== (data?.remoteHost || "") || t.running).slice(0, 12).map(t => SP_JSX.jsx(Action, { disabled: busy || (data?.active && !data.remoteHost && t.host === ""), onClick: () => void run(async () => { if (t.host !== (data?.remoteHost || ""))
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
    const stopRepairPolling = startRepairPolling();
    return { name: "Deck AI", titleView: SP_JSX.jsx("span", { children: "Deck AI" }), content: SP_JSX.jsx(Panel, {}), icon: SP_JSX.jsx("img", { src: logo, alt: "Deck AI", style: { width: 20, height: 20, objectFit: "contain" } }), onDismount() {
            if (returnToPanel)
                clearTimeout(returnToPanel);
            clearInterval(notifier);
            stopRepairPolling();
            routerHook.removeRoute(FULLSCREEN_PATH);
        } };
});

export { index as default };
