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
let mutation = 0;

async function api(path, body) {
  const response = await fetch("/api/" + path, {
    ...(body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {}),
    cache: "no-store",
    signal: AbortSignal.timeout(5500),
  });
  const result = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(result.error || "Связь с Deck прервана.");
  if (!result.state) throw new Error("Пульт получил неполный ответ от Deck.");
  return result;
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
    action ? "Steam Deck проверяет изменение." : labels[state];
  text("repair-status", [actionStatus, detail, readOnly && "Режим только чтения."].filter(Boolean).join(" "));
  show("decision", action?.state === "pending" && !readOnly);
  text("question", action?.kind === "restore" ? "Восстановить исходные параметры этой игры?" :
    "Временно сбросить параметры запуска этой игры? Deck сохранит исходное значение для отката.");
  show("result", state === "applied" && !action && !launchResult);
  text("result-status", launchResult === "started" ? "Отмечено: игра запустилась." :
    launchResult === "failed" ? "Отмечено: игра не запустилась." : "");
  show("last-note", Boolean(note));
  text("last-note", note ? "Последнее уточнение · " + note : "");
}

function problem(error) {
  text("error", error instanceof Error ? error.message : "Связь с Deck прервана.");
  show("error", true);
}

async function action(path, fields) {
  if (!current || busy) return;
  busy = true;
  mutation++;
  buttons.forEach(button => { button.disabled = true; });
  show("error", false);
  try {
    render(await api(path, { ...fields, caseId: current.id }));
    if (path === "note") element("note").value = "";
  } catch (error) {
    problem(error);
  } finally {
    buttons.forEach(button => { button.disabled = false; });
    busy = false;
  }
}

element("accept").onclick = () => void action("decision", { actionId: current?.action?.id, decision: true });
element("decline").onclick = () => void action("decision", { actionId: current?.action?.id, decision: false });
element("started").onclick = () => void action("result", { result: "started" });
element("failed").onclick = () => void action("result", { result: "failed" });
element("send-note").onclick = () => void action("note", { note: element("note").value });

async function refresh() {
  if (busy || fetching) return;
  fetching = true;
  const revision = mutation;
  try {
    const value = await api("status");
    if (revision !== mutation) return;
    render(value);
    if (element("error").dataset.connection) show("error", false);
    delete element("error").dataset.connection;
  } catch (error) {
    if (revision !== mutation) return;
    rendered = "";
    current = null;
    show("case", false);
    show("pairing", false);
    text("status", "Подключение приостановлено");
    problem(error);
    element("error").dataset.connection = "1";
  } finally {
    fetching = false;
  }
}

const challenge = location.hash.slice(1);
if (challenge) {
  history.replaceState(null, "", "/");
  try { render(await api("pair", { challenge })); }
  catch (error) { problem(error); }
}
await refresh();
setInterval(() => void refresh(), 2200);
