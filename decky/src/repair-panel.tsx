import { useEffect, useMemo, useRef, useState } from "react";
import { ConfirmModal, DialogButton, Dropdown, Focusable, Navigation, Router, showModal, TextField } from "@decky/ui";
import qrcode from "qrcode-generator";
import { inspectLaunch, libraryGames, originalLaunchOptions, repairCommand, repairScreenshots, repairView, steamAccount, subscribeRepair } from "./launch-repair";

const status = {
 inspected: "Диагностика готова.",
 applied: "Параметры сброшены. Повторите запуск из библиотеки Steam.",
 restored: "Исходные параметры восстановлены.",
 conflict: "Текущее значение отличается от ожидаемого. Проверьте свойства игры в Steam.",
};
const originKey = "deck-ai-repair-origin";

function Qr({ url }: { url: string }) {
 const src = useMemo(() => {
  const qr = qrcode(0, "M");
  qr.addData(url);
  qr.make();
  return qr.createDataURL(6);
 }, [url]);
 return <img className="dai-repair-qr" src={src} alt="QR для сопряжения браузера с этой диагностикой" />;
}

export function RepairPanel({ copy }: { copy: (value: string) => void }) {
 const [view, setView] = useState(repairView);
 const [query, setQuery] = useState("");
 const [appId, setAppId] = useState(0);
 const [shot, setShot] = useState("");
 const [shots, setShots] = useState<Awaited<ReturnType<typeof repairScreenshots>>>([]);
 const [preview, setPreview] = useState("");
 const [error, setError] = useState("");
 const [busy, setBusy] = useState(false);
 const operationPending = useRef(false);
 const [pairOpen, setPairOpen] = useState(false);
 const [address, setAddress] = useState(() => localStorage.getItem(originKey) || "");
 useEffect(() => subscribeRepair(setView), []);
 const current = view.case;
 const account = steamAccount();
 const games = current ? [] : libraryGames(query, Router.MainRunningAppID ?? 0);
 const selected = games.find(game => game.appId === appId) || games[0];
 useEffect(() => {
  let stale = false;
  setShots([]);
  setShot("");
  if (selected && account && !current) {
   void repairScreenshots(selected.appId, selected.shortcut).then(items => {
    if (!stale) setShots(items);
   }).catch(() => {});
  }
  return () => { stale = true; };
 }, [selected?.appId, selected?.shortcut, account, current?.id]);
 useEffect(() => { setPreview(""); }, [account]);

 async function run(operation: () => Promise<unknown>) {
  if(operationPending.current)return;
  operationPending.current = true;
  setBusy(true);
  setError("");
  try { await operation(); }
  catch (failure) { setError(String(failure)); }
  finally { operationPending.current = false; setBusy(false); }
 }
 const action = current?.action;
 const remote = view.remote;
 const send = (verb: string, fields?: object) => {
  if (current) void run(() => repairCommand(current.id, verb, fields));
 };
 const message = error || view.error;

 return <Focusable className="dai-stack-content dai-repair" flow-children="vertical">
  <section className="dai-section">
   <h3>Разобрать ошибку запуска</h3>
   <p className="dai-muted">Проверка этой Steam Deck. Можно выбрать игру, которая уже закрылась.</p>
   {message && <p className="dai-repair-error" role="alert">{message}</p>}
   {!current && <>
    <TextField value={query} placeholder="Название игры или App ID" onChange={event => setQuery(event.target.value)} />
    {selected ? <>
     <span className="dai-label">Игра из библиотеки</span>
     <Dropdown selectedOption={selected.appId} disabled={busy}
      rgOptions={games.map(game => ({ data: game.appId, label: game.name }))}
      onChange={option => setAppId(option.data)} />
     {!!shots.length && <><span className="dai-label">Скриншот Steam</span>
      <Dropdown selectedOption={shot} disabled={busy}
      rgOptions={[{ data: "", label: "Без скриншота" }, ...shots.map(item => ({ data: item.path, label: item.name }))]}
      onChange={option => setShot(option.data)} /></>}
     <DialogButton className="dai-button dai-primary" disabled={busy || !account} onClick={() => void run(async () => {
      const result = await inspectLaunch(selected.appId, shot);
      setPreview(result.preview);
     })}>{busy ? "Читаю свойства Steam…" : "Проверить запуск"}</DialogButton>
    </> : <p className="dai-muted">В библиотеке нет подходящей локальной игры. Проверьте название.</p>}
   </>}
   {current && <>
    <h4>{current.name}</h4>
    <p className="dai-muted">{current.proton ? "Совместимость Steam · " + current.proton : "Steam не указал инструмент совместимости."}</p>
    {preview && <img className="dai-repair-preview" src={preview} alt="Выбранный скриншот Steam" />}
    <ul className="dai-repair-checks">{current.checks.map(check => <li key={check}>{check}</li>)}</ul>
    <p role="status">{action?.state === "pending" ? "Ожидаю подтверждение." : action ? "Сверяю параметры со Steam…" :
     current.state === "applied" && current.launchResult ? "Параметры сброшены. Результат запуска отмечен." : status[current.state]}</p>
    {current.detail && <p className="dai-muted">{current.detail}</p>}
    <Focusable className="dai-repair-actions" flow-children="horizontal">
     <DialogButton className="dai-button" disabled={busy || !!action} onClick={() => send("recheck")}>Повторить проверку</DialogButton>
     <DialogButton className="dai-button" onClick={() => copy([
      `${current.name} · Steam App ID ${current.appId}`,
      current.proton && `Совместимость Steam · ${current.proton}`,
      ...current.checks,
     ].filter(Boolean).join("\n"))}>Скопировать сводку</DialogButton>
    </Focusable>
    {current.readOnly && <p className="dai-muted">Изменения приостановлены в режиме «Только чтение».</p>}
    {current.note && <p className="dai-muted">Уточнение с пульта · {current.note}</p>}
    {!action && current.canReset && <>
     <p>Есть пользовательские параметры запуска. Попробуйте запуск со стандартным значением. Сохраним текущие параметры для отката.</p>
     <DialogButton className="dai-button" disabled={busy || current.readOnly} onClick={() => send("request", { kind: "reset" })}>Предложить сброс параметров</DialogButton>
    </>}
    {!action && current.state === "inspected" && !current.canReset &&
     <p>Пользовательские параметры запуска пусты. По этой проверке исправление не требуется.</p>}
    {action?.state === "pending" && <div className="dai-repair-confirm">
     <p>{action.kind === "reset" ? "Временно сбросить параметры запуска этой игры?" : "Вернуть исходные параметры запуска этой игры?"}</p>
     <Focusable className="dai-repair-actions" flow-children="horizontal">
      <DialogButton className="dai-button dai-primary" disabled={busy || current.readOnly}
       onClick={() => send("decide", { actionId: action.id, decision: true })}>Подтвердить</DialogButton>
      <DialogButton className="dai-button" disabled={busy}
       onClick={() => send("decide", { actionId: action.id, decision: false })}>Отклонить</DialogButton>
     </Focusable>
    </div>}
    {current.canEndWait && action && <DialogButton className="dai-button" disabled={busy}
     onClick={() => send("end_wait", { actionId: action.id })}>Завершить ожидание Steam</DialogButton>}
    {current.hasBackup && !action && <DialogButton className="dai-button" disabled={busy}
     onClick={() => void run(async () => copy(await originalLaunchOptions(current.id)))}>Скопировать исходные параметры</DialogButton>}
    {!action && current.state === "applied" && <>
     {!current.launchResult && <DialogButton className="dai-button"
      onClick={() => Navigation.Navigate("/library/app/" + current.appId)}>Открыть игру в библиотеке</DialogButton>}
     {current.launchResult ? <p>{current.launchResult === "started" ? "Отмечено: игра запустилась." : "Отмечено: игра не запустилась."}</p> : <>
      <p>Игра запустилась после сброса?</p>
      <Focusable className="dai-repair-actions" flow-children="horizontal">
       <DialogButton className="dai-button" disabled={busy} onClick={() => send("result", { result: "started" })}>Запустилась</DialogButton>
       <DialogButton className="dai-button" disabled={busy} onClick={() => send("result", { result: "failed" })}>Не запустилась</DialogButton>
      </Focusable>
     </>}
     <DialogButton className="dai-button" disabled={busy || current.readOnly}
      onClick={() => send("request", { kind: "restore" })}>Предложить откат</DialogButton>
    </>}
    {!action && <DialogButton className="dai-button" disabled={busy}
     onClick={() => {
      const close = () => void run(async () => { await repairCommand(current.id, "close"); setPreview(""); });
      if (current.state !== "applied" && current.state !== "conflict") { close(); return; }
      showModal(<ConfirmModal strTitle="Завершить диагностику?"
       strDescription="Deck AI удалит сохранённое значение параметров запуска. Автоматический откат станет недоступен."
       strOKButtonText="Завершить" strCancelButtonText="Продолжить" onOK={close} />);
     }}>Завершить диагностику</DialogButton>}
   </>}
  </section>
  {current && <section className="dai-section">
   <h3>Пульт на телефоне или ПК</h3>
   {remote.state === "off" && <>
    <DialogButton className="dai-button" onClick={() => setPairOpen(!pairOpen)}>Подключить браузер</DialogButton>
    {pairOpen && <>
     <p className="dai-muted">Введите частный HTTPS-адрес пульта. Настройка Tailscale Serve и HTTPS-прокси описана в инструкции к релизу.</p>
     <TextField value={address} placeholder="https://deck.example.ts.net:8443" onChange={event => setAddress(event.target.value)} />
     <DialogButton className="dai-button dai-primary" disabled={busy || !address.trim()}
      onClick={() => void run(async () => {
       await repairCommand(current.id, "pair", { address });
       localStorage.setItem(originKey, address.trim());
      })}>Показать QR</DialogButton>
    </>}
   </>}
   {remote.state === "pairing" && remote.url && <>
    <Qr url={remote.url} />
    <p className="dai-muted">Откройте QR на телефоне. Для ПК можно скопировать одноразовую ссылку.</p>
    <DialogButton className="dai-button" onClick={() => { if (remote.url) copy(remote.url); }}>Скопировать ссылку</DialogButton>
   </>}
   {remote.state === "pending" && <>
    <p>Код браузера <strong>{remote.code}</strong>. Сверьте его с экраном телефона или ПК.</p>
    <DialogButton className="dai-button dai-primary" disabled={busy}
     onClick={() => send("pair_confirm", { code: remote.code })}>Код совпадает, подключить</DialogButton>
   </>}
   {remote.state === "connected" && <p role="status">Браузер подключён к этой диагностике.</p>}
   {remote.state !== "off" && <DialogButton className="dai-button" disabled={busy}
    onClick={() => send("pair_stop")}>Отключить пульт</DialogButton>}
  </section>}
 </Focusable>;
}
