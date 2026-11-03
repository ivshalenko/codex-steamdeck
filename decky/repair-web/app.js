const element = id => document.getElementById(id);
const show = (id, visible) => { element(id).hidden = !visible; };
const text = (id, value) => { element(id).textContent = value; };
const buttons = [...document.querySelectorAll("button")];
const labels = {
  inspected: "Диагностика готова.",
  applied: "Параметры сброшены. Проверьте запуск игры.",
  restored: "Исходные параметры восстановлены.",
  conflict: "Состояние изменилось. Откройте диагностику на Steam Deck.",
};
let current = null;
let rendered = "";
let busy = false;
let fetching = false;
let viewRevision = 0;
let timer;
let delay = 2200;
let ended = false;

class HttpError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

async function api(path, body) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5500);
  try {
    const response = await fetch("/api/" + path, {
      ...(body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {}),
      cache: "no-store",
      signal: controller.signal,
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new HttpError(response.status, result.error || "Связь с Deck прервана.");
    if (!result.state) throw new Error("Пульт получил неполный ответ от Deck.");
    return result;
  } finally {
    clearTimeout(timeout);
  }
}

function render(value) {
  const serialized = JSON.stringify(value);
  if (serialized === rendered) return;
  rendered = serialized;
  current = value.case || null;
  show("pairing", value.state === "pending");
  show("case", Boolean(current));
  text("status", current ? "Подключено к Steam Deck" : "Ожидаю подтверждение на Steam Deck");
  if (!current) {
    text("code", value.code || "");
    return;
  }
  const { name, proton, checks, state, detail, action, launchResult, note, readOnly } = current;
  text("game", name);
  text("proton", proton ? "Совместимость Steam · " + proton : "Steam не указал инструмент совместимости.");
  element("checks").replaceChildren(...checks.map(check => {
    const li = document.createElement("li");
    li.textContent = check;
    return li;
  }));
  const actionStatus = action?.state === "pending" ? "Требуется подтверждение." :
    action ? "Steam Deck проверяет изменение." :
    state === "applied" && launchResult ? "Параметры сброшены. Результат запуска отмечен." : labels[state];
  text("repair-status", [actionStatus, detail, readOnly && "Режим только чтения."].filter(Boolean).join(" "));
  show("decision", action?.state === "pending");
  element("accept").disabled = readOnly;
  text("question", action?.kind === "restore" ? "Восстановить исходные параметры этой игры?" :
    "Временно сбросить параметры запуска этой игры? Deck сохранит исходное значение для отката.");
  show("result", state === "applied" && !action && !launchResult);
  text("result-status", launchResult === "started" ? "Отмечено: игра запустилась." :
    launchResult === "failed" ? "Отмечено: игра не запустилась." : "");
  show("last-note", Boolean(note));
  text("last-note", note ? "Последнее уточнение · " + note : "");
}

function problem(error) {
  const message = error instanceof Error && error.name !== "AbortError" ? error.message : "Связь с Deck прервана.";
  text("error", message);
  show("error", true);
}

async function action(path, fields) {
  if (!current || busy) return;
  busy = true;
  const revision = ++viewRevision;
  buttons.forEach(button => { button.disabled = true; });
  show("error", false);
  try {
    const value = await api(path, { ...fields, caseId: current.id });
    if (revision === viewRevision) render(value);
    if (path === "note" && element("note").value === fields.note) element("note").value = "";
  } catch (error) {
    if (revision === viewRevision) problem(error);
  } finally {
    buttons.forEach(button => { button.disabled = false; });
    element("accept").disabled = Boolean(current?.readOnly);
    busy = false;
    schedule(0);
  }
}

element("accept").onclick = () => void action("decision", { actionId: current?.action?.id, decision: true });
element("decline").onclick = () => void action("decision", { actionId: current?.action?.id, decision: false });
element("started").onclick = () => void action("result", { result: "started" });
element("failed").onclick = () => void action("result", { result: "failed" });
element("send-note").onclick = () => void action("note", { note: element("note").value });

function schedule(ms) {
  clearTimeout(timer);
  if (ended || document.hidden || !navigator.onLine) return;
  timer = setTimeout(() => void refresh(), ms);
}

async function refresh() {
  if (busy || fetching || ended || document.hidden || !navigator.onLine) return;
  fetching = true;
  const revision = viewRevision;
  try {
    const value = await api("status");
    if (revision !== viewRevision) return;
    render(value);
    delay = 2200;
    if (element("error").dataset.connection) show("error", false);
    delete element("error").dataset.connection;
  } catch (error) {
    if (revision !== viewRevision) return;
    rendered = "";
    current = null;
    show("case", false);
    show("pairing", false);
    ended = error instanceof HttpError && (error.status === 401 || error.status === 410);
    text("status", ended ? "Нужен новый QR с Steam Deck" : "Подключение приостановлено");
    delay = Math.min(20000, delay * 2);
    problem(error);
    element("error").dataset.connection = "1";
  } finally {
    fetching = false;
    schedule(revision === viewRevision ? delay : 0);
  }
}

function networkLost() {
  clearTimeout(timer);
  if (ended) return;
  viewRevision++;
  text("status", "Ожидаю подключения к сети");
  current = null;
  rendered = "";
  show("case", false);
  show("pairing", false);
}

const challenge = location.hash.slice(1);
if (challenge) {
  history.replaceState(null, "", "/");
  try { render(await api("pair", { challenge })); }
  catch (error) { problem(error); }
}
document.addEventListener("visibilitychange", () => schedule(0));
window.addEventListener("online", () => schedule(0));
window.addEventListener("offline", networkLost);
if (navigator.onLine) await refresh();
else networkLost();
