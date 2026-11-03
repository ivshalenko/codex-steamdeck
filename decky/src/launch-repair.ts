import { callable } from "@decky/api";

export type RepairAction = { id: string; kind: "reset" | "restore"; state: "pending" | "approved" | "running" };
export type RepairCase = {
 id: string; appId: number; name: string; proton: string; checks: string[];
 state: "inspected" | "applied" | "restored" | "conflict"; action: RepairAction | null;
 detail: string; launchResult: "" | "started" | "failed"; note: string; canReset: boolean; readOnly: boolean;
};
type Pairing = { state: "off" | "pairing" | "pending" | "connected"; url?: string; code?: string };
type View = { case: RepairCase | null; remote: Pairing; error?: string };
type Game = { appId: number; name: string; shortcut: boolean };
type GameDetails = Game & { options: string; proton: string };
type SteamDetails = NonNullable<ReturnType<Window["appDetailsStore"]["GetAppDetails"]>>;
type Screenshot = { path: string; name: string; when?: number };

const repairStatus = callable<[account: string], View>("repair_status");
const inspect = callable<[account: string, game: GameDetails, screenshot: string],
 { case: RepairCase; preview: string }>("repair_inspect");
const screenshots = callable<[account: string, appId: number, shortcut: boolean], Screenshot[]>("repair_screenshots");
const command = callable<[account: string, caseId: string, verb: string, fields: object], unknown>("repair_command");

export function steamAccount(): string {
 try {
  const id = window.friendStore?.currentUserSteamID || window.uiStore?.currentUserSteamID;
  return typeof id === "string" ? id : id?.ConvertTo64BitString() || "";
 } catch {
  return "";
 }
}

const shortcutType = 1073741824;

export function libraryGames(query: string, preferredId: number): Game[] {
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

async function liveDetails(appId: number): Promise<GameDetails> {
 const overview = window.appStore?.GetAppOverviewByAppID(appId);
 const apps = window.SteamClient?.Apps;
 if (!overview || !apps?.RegisterForAppDetails) throw new Error("Steam не предоставил свойства игры.");
 const shortcut = overview.app_type === shortcutType;
 let subscription: ReturnType<typeof apps.RegisterForAppDetails> | undefined;
 let timer: ReturnType<typeof setTimeout> | undefined;
 try {
  const details = await new Promise<SteamDetails>((resolve, reject) => {
   timer = setTimeout(() => reject(new Error("Steam не ответил на запрос свойств игры.")), 3500);
   subscription = apps.RegisterForAppDetails(appId, data => {
    if (!data) return;
    const options = shortcut ? data.strShortcutLaunchOptions : data.strLaunchOptions;
    if (data.unAppID === appId && typeof options === "string") resolve(data);
   });
  });
  return {
   appId, name: overview.display_name, shortcut,
   options: shortcut ? details.strShortcutLaunchOptions : details.strLaunchOptions,
   proton: details.strCompatToolDisplayName || details.strCompatToolName || "",
  };
 } finally {
  clearTimeout(timer);
  subscription?.unregister();
 }
}

let view: View = { case: null, remote: { state: "off" } };
const listeners = new Set<(value: View) => void>();

export function repairView() { return view; }
export function subscribeRepair(listener: (value: View) => void) {
 listeners.add(listener);
 return () => { listeners.delete(listener); };
}
function publish(value: View) {
 if (JSON.stringify(value) === JSON.stringify(view)) return;
 view = value;
 for (const listener of listeners) listener(view);
}

export async function inspectLaunch(appId: number, screenshot: string) {
 const account = steamAccount();
 if (!account) throw new Error("Откройте библиотеку Steam под своим аккаунтом.");
 const game = await liveDetails(appId);
 if (steamAccount() !== account) throw new Error("Аккаунт Steam изменился.");
 return inspect(account, game, screenshot);
}

export function repairScreenshots(appId: number, shortcut: boolean) { return screenshots(steamAccount(), appId, shortcut); }
export function repairCommand(caseId: string, verb: string, fields: object = {}) {
 return command(steamAccount(), caseId, verb, fields);
}

const delay = (ms: number) => new Promise<void>(resolve => setTimeout(resolve, ms));

export function startRepairPolling() {
 let disposed = false;
 let polling = false;
 const sameAccount = (account: string) => !disposed && steamAccount() === account;
 async function tick() {
  if (polling || disposed) return;
  polling = true;
  const account = steamAccount();
  try {
   const value = await repairStatus(account);
   if (!sameAccount(account)) return;
   publish(value);
   const current = value.case;
   const action = current?.action;
   if (!current || !action || action.state === "pending") return;
   const live = await liveDetails(current.appId);
   if (!sameAccount(account)) return;
   const actionId = action.id;
   if (action.state === "running") {
    await command(account, current.id, "observe", { actionId, options: live.options, shortcut: live.shortcut });
    return;
   }
   const apps = window.SteamClient?.Apps;
   const setter = live.shortcut ? apps?.SetShortcutLaunchOptions : apps?.SetAppLaunchOptions;
   if (!setter) throw new Error("В этой версии Steam сброс параметров недоступен.");
   const claim = await command(account, current.id, "claim", {
    actionId, options: live.options, shortcut: live.shortcut,
   }) as { options: string } | null;
   if (!claim || !sameAccount(account)) return;
   const beforeWrite = await liveDetails(current.appId);
   if (!sameAccount(account)) return;
   if (beforeWrite.options !== live.options || beforeWrite.shortcut !== live.shortcut) {
    await command(account, current.id, "abort", { actionId, options: beforeWrite.options, shortcut: live.shortcut });
    return;
   }
   setter.call(apps, current.appId, claim.options);
   for (let attempt = 0; attempt < 4; attempt++) {
    await delay(400);
    if (!sameAccount(account)) return;
    const observed = await liveDetails(current.appId);
    if (!sameAccount(account)) return;
    if (observed.options === claim.options) {
     await command(account, current.id, "observe", {
      actionId, options: observed.options, shortcut: observed.shortcut,
     });
     return;
    }
   }
  } catch (error) {
   if (sameAccount(account)) publish({ ...view, error: String(error) });
  } finally {
   polling = false;
  }
 }
 void tick();
 const timer = setInterval(() => void tick(), 1800);
 return () => { disposed = true; clearInterval(timer); };
}
