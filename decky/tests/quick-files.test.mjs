import test from 'node:test';
import assert from 'node:assert/strict';
import {parseQuickActions,serializeQuickActions,defaultQuickActions} from '../src/quick.ts';
import {joinPath,parentPath,sortEntries} from '../src/files.ts';
test('quick phrases: defaults, label|text, label-only, limits, empty input',()=>{
 assert.deepEqual(parseQuickActions(null),defaultQuickActions);
 assert.deepEqual(parseQuickActions("Деплой | Запусти деплой на стенд\nДа\n\n | \n"),[["Деплой","Запусти деплой на стенд"],["Да","Да"]]);
 assert.deepEqual(parseQuickActions("  \n"),defaultQuickActions);
 assert.equal(parseQuickActions(Array.from({length:12},(_,i)=>"п"+i).join("\n")).length,8);
 assert.deepEqual(parseQuickActions(serializeQuickActions(defaultQuickActions)),defaultQuickActions);
});
test('file paths: join, parent, folders first',()=>{
 assert.equal(joinPath("/home/u/","proj/"),"/home/u/proj");
 assert.equal(parentPath("/home/u/proj"),"/home/u");
 assert.equal(parentPath("/home"),"/");
 assert.deepEqual(sortEntries(["b.txt","z/","a.txt","m/"]),["m/","z/","a.txt","b.txt"]);
});
