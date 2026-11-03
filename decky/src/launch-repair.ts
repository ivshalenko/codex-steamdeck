import { callable } from "@decky/api";

export type RepairAction = { id: string; kind: "reset" | "restore"; state: "pending" | "approved" | "running" };
export type RepairCase = {
 id: string; appId: number; name: string; proton: string; checks: string[];
 state: "inspected" | "applied" | "restored" | "conflict"; action: RepairAction | null;
 detail: string; launchResult: "" | "started" | "failed"; note: string; canReset: boolean; readOnly: boolean;
 canEndWait?: boolean; hasBackup?: boolean;
};
type Pairing = { state: "off" | "pairing" | "pending" | "connected"; url?: string; code?: string };
type View = { case: RepairCase | null; remote: Pairing; error?: string };
type Game = { appId: number; name: string; shortcut: boolean };
type GameDetails = Game & { options: string; proton: string; shortcutExe?:string; folderIndex?:number; location?:string };
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
   shortcutExe: shortcut ? details.strShortcutExe : undefined,
   folderIndex: shortcut ? undefined : details.iInstallFolder,
  };
 } finally {
  clearTimeout(timer);
  subscription?.unregister();
 }
}

async function libraryPath(game:GameDetails){
 if(game.shortcut)return game.shortcutExe||"";
 const folder=window.SteamClient?.InstallFolder;
 if(!folder?.GetInstallFolders)return "";
 let timer:ReturnType<typeof setTimeout>|undefined;
 try{
  const timeout=new Promise<null>(resolve=>{timer=setTimeout(()=>resolve(null),1000);});
  const folders=await Promise.race([folder.GetInstallFolders(),timeout]);
  return folders?.find(item=>item.nFolderIndex===game.folderIndex)?.strFolderPath||"";
 }catch{
  return "";
 }finally{
  clearTimeout(timer);
 }
}

const emptyView: View = { case: null, remote: { state: "off" } };
let view = emptyView;
let viewOwner = "";
const listeners = new Set<(value: View) => void>();
let wakePolling = () => {};

export function repairView() { return viewOwner === steamAccount() ? view : emptyView; }
export function subscribeRepair(listener: (value: View) => void) {
 listeners.add(listener);
 listener(repairView());
 wakePolling();
 return () => { listeners.delete(listener); };
}
function publish(value: View, account:string) {
 if (account===viewOwner && JSON.stringify(value) === JSON.stringify(view)) return;
 view = value;
 viewOwner = account;
 for (const listener of listeners) listener(view);
}

export async function inspectLaunch(appId: number, screenshot: string) {
 const account = steamAccount();
 if (!account) throw new Error("Откройте библиотеку Steam под своим аккаунтом.");
 const game = await liveDetails(appId);
 game.location = await libraryPath(game);
 if (steamAccount() !== account) throw new Error("Аккаунт Steam изменился.");
 try {
  return await inspect(account, game, screenshot);
 } finally {
  wakePolling();
 }
}

export function repairScreenshots(appId: number, shortcut: boolean) { return screenshots(steamAccount(), appId, shortcut); }
export async function repairCommand(caseId: string, verb: string, fields: object = {}) {
 try {
  return await command(steamAccount(), caseId, verb, fields);
 } finally {
  wakePolling();
 }
}

export async function originalLaunchOptions(caseId:string){
 const result=await repairCommand(caseId,"original") as {options:string};
 return result.options;
}

const delay = (ms: number) => new Promise<void>(resolve => setTimeout(resolve, ms));

export function startRepairPolling() {
 let disposed = false;
 let polling = false;
 let requested = false;
 let failures = 0;
 let timer: ReturnType<typeof setTimeout> | undefined;
 const sameAccount = (account: string) => !disposed && steamAccount() === account;
 const needsPolling = () => listeners.size > 0 || view.remote.state !== "off"
  || view.case?.action?.state === "approved" || view.case?.action?.state === "running";
 function schedule(ms: number) {
  clearTimeout(timer);
  if (!disposed) timer = setTimeout(() => void tick(), ms);
 }
 function wake() {
  if (polling) requested = true;
  else schedule(0);
 }
 wakePolling = wake;
 async function tick() {
  if (polling || disposed) return;
  polling = true;
  const account = steamAccount();
  let failed = false;
  try {
   const value = await repairStatus(account);
   if (!sameAccount(account)) return;
   publish(value,account);
   failures = 0;
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
   failed = true;
   failures++;
   if (sameAccount(account)) publish({ ...repairView(), error: String(error) },account);
  } finally {
   polling = false;
   if (requested) {
    requested = false;
    schedule(0);
   } else if (needsPolling() || failed) {
    const recoveryDelay = needsPolling() ? 3500 : Math.min(30000, 3500 * 2 ** Math.min(failures - 1, 4));
    schedule(failed ? recoveryDelay : 1800);
   }
  }
 }
 void tick();
 return () => {
  disposed = true;
  clearTimeout(timer);
  if (wakePolling === wake) wakePolling = () => {};
 };
}
