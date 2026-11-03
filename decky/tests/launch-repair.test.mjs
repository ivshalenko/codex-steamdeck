import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import ts from "typescript";

const account = "76561197960265729";
const appId = 42;
const original = "false %command%";
const source = await readFile(new URL("../src/launch-repair.ts", import.meta.url), "utf8");
const instrumented = source.replace('import { callable } from "@decky/api";', "const callable = globalThis.repairCallable;");
const { outputText } = ts.transpileModule(instrumented, {
 compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 },
});

test("Steam adapter writes only a claimed change, checks readback and detects a concurrent edit", async () => {
 let options = original;
 let manualEdit = false;
 let wrote = 0;
 let completion;
 const completed = () => new Promise(resolve => { completion = resolve; });
 const game = { appid: appId, display_name: "Test", app_type: 1, local_per_client_data: { installed: true } };
 const value = { case: { id: "case", appId, action: { id: "action", kind: "reset", state: "approved" } }, remote: { state: "off" } };
 globalThis.window = {
  friendStore: { currentUserSteamID: { ConvertTo64BitString: () => account } },
  appStore: { allApps: [game], GetAppOverviewByAppID: () => game },
  SteamClient: { Apps: {
   RegisterForAppDetails: (id, callback) => {
    callback({ unAppID: id, strLaunchOptions: options, strCompatToolDisplayName: "Proton Test" });
    return { unregister() {} };
   },
   SetAppLaunchOptions: (id, text) => { assert.equal(id, appId); options = text; wrote++; },
  } },
 };
 globalThis.repairCallable = method => async (...args) => {
  assert.equal(args[0], account);
  if (method === "repair_status") return value;
  if (method === "repair_inspect") return args[1];
  const [, id, verb, fields] = args;
  assert.equal(id, value.case.id);
  assert.equal(fields.actionId, "action");
  if (verb === "claim") {
   assert.equal(fields.options, original);
   if (manualEdit) options = "manually edited";
   return { options: "" };
  }
  completion({ verb, options: fields.options });
 };
 const repair = await import("data:text/javascript;base64," + Buffer.from(outputText).toString("base64"));
 assert.equal(repair.libraryGames("test", 0)[0].appId, appId);
 assert.equal((await repair.inspectLaunch(appId, "")).options, original);
 for (const changed of [false, true]) {
  options = original;
  manualEdit = changed;
  const done = completed();
  const stop = repair.startRepairPolling();
  let timer;
  try {
   const outcome = await Promise.race([done, new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error("Steam repair did not complete")), 1500);
   })]);
   assert.deepEqual(outcome, changed ? { verb: "abort", options: "manually edited" } : { verb: "observe", options: "" });
  } finally {
   clearTimeout(timer);
   stop();
  }
 }
 assert.equal(wrote, 1);
 assert.equal(options, "manually edited");
});
