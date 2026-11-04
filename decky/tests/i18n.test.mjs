import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import ts from 'typescript';
import {english,getUILanguage,setUILanguage,subscribeUILanguage,t,systemText,speechLanguageName,languageKey} from '../src/i18n.ts';

test('UI language persists across views without changing stored conversations or voice settings',()=>{
 const original=Object.getOwnPropertyDescriptor(globalThis,'localStorage');
 const saved=new Map([['codex-game-voice','ru'],['codex-game-draft:demo','Мой черновик']]);
 Object.defineProperty(globalThis,'localStorage',{configurable:true,value:{getItem:k=>saved.get(k)??null,setItem:(k,v)=>saved.set(k,v)}});
 const compact=[],full=[];const offA=subscribeUILanguage(v=>compact.push(v)),offB=subscribeUILanguage(v=>full.push(v));
 try{
  setUILanguage('en');assert.equal(getUILanguage(),'en');assert.equal(t('Настройки'),'Settings');
  assert.deepEqual(compact,['en']);assert.deepEqual(full,['en']);assert.equal(saved.get(languageKey),'en');
  assert.equal(saved.get('codex-game-voice'),'ru');assert.equal(saved.get('codex-game-draft:demo'),'Мой черновик');
  offB();setUILanguage('ru');assert.equal(t('Настройки'),'Настройки');assert.deepEqual(full,['en']);
  setUILanguage('invalid');assert.equal(getUILanguage(),'ru');
 }finally{offA();offB();setUILanguage('ru');if(original)Object.defineProperty(globalThis,'localStorage',original);else delete globalThis.localStorage;}
});

test('English formatting preserves values and unknown content; Russian remains the fallback',()=>{
 try{
  setUILanguage('en');assert.equal(t('Нет связи · повтор через {0} с',7),'Disconnected · retrying in 7s');
  assert.equal(t(' Очередь '),' Queue ');assert.equal(t('/home/deck/Мои файлы'),'/home/deck/Мои файлы');
  assert.equal(systemText('ValueError: Нет соединения с Codex.'),'ValueError: Not connected to Codex.');
  assert.equal(systemText('Свободно в домашнем разделе Steam Deck · 37.2 ГБ.'),'Free space on the Steam Deck home partition · 37.2 GB.');
  assert.equal(systemText('Steam (предыдущий журнал) зарегистрировал завершение процесса · 2026-11-04 · код 9.'),'Steam (previous log) recorded a process exit · 2026-11-04 · exit code 9.');
  assert.equal(systemText('Unknown tool error: сохраните лог'),'Unknown tool error: сохраните лог');
  assert.equal(speechLanguageName('es','испанский'),'Spanish');
  setUILanguage('ru');assert.equal(t('Нет связи · повтор через {0} с',7),'Нет связи · повтор через 7 с');
  assert.equal(speechLanguageName('es','испанский'),'испанский');
 }finally{setUILanguage('ru');}
});

test('storage failure does not prevent changing the current interface language',()=>{
 const original=Object.getOwnPropertyDescriptor(globalThis,'localStorage');
 Object.defineProperty(globalThis,'localStorage',{configurable:true,value:{setItem(){throw new Error('full');}}});
 try{setUILanguage('en');assert.equal(t('Вложения'),'Attachments');}
 finally{setUILanguage('ru');if(original)Object.defineProperty(globalThis,'localStorage',original);else delete globalThis.localStorage;}
});

test('every static UI translation exists and keeps its interpolation fields',()=>{
 const fields=value=>[...value.matchAll(/\{\d+\}/g)].map(m=>m[0]).sort();
 for(const [source,value] of Object.entries(english))assert.deepEqual(fields(value),fields(source),source);
 for(const name of ['index.tsx','repair-panel.tsx','launch-repair.ts','game-context.ts','updates-panel.tsx']){
  const source=fs.readFileSync(new URL('../src/'+name,import.meta.url),'utf8');
  const tree=ts.createSourceFile(name,source,ts.ScriptTarget.Latest,true,name.endsWith('.tsx')?ts.ScriptKind.TSX:ts.ScriptKind.TS);
  function visit(node){
   if(ts.isCallExpression(node)&&ts.isIdentifier(node.expression)&&node.expression.text==='t'&&ts.isStringLiteralLike(node.arguments[0])){
    const key=node.arguments[0].text;assert.ok(english[key]||english[key.trim()],name+': '+JSON.stringify(key));
   }
   if(ts.isJsxText(node))assert.ok(!/[А-Яа-яЁё]/.test(node.text),name+': untranslated JSX');
   ts.forEachChild(node,visit);
  }
  visit(tree);
 }
});

test('a fresh view starts in English and an explicit Russian choice survives reload',async()=>{
 const original=Object.getOwnPropertyDescriptor(globalThis,'localStorage');
 try{
  Object.defineProperty(globalThis,'localStorage',{configurable:true,value:{getItem:()=>null}});
  const fresh=await import('../src/i18n.ts?fresh-english');assert.equal(fresh.getUILanguage(),'en');
  Object.defineProperty(globalThis,'localStorage',{configurable:true,value:{getItem:()=> 'ru'}});
  const russian=await import('../src/i18n.ts?chosen-russian');assert.equal(russian.getUILanguage(),'ru');
 }finally{if(original)Object.defineProperty(globalThis,'localStorage',original);else delete globalThis.localStorage;}
});
