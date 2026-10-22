import test from 'node:test';
import assert from 'node:assert/strict';
import {updateDictation,restoreDictation,bindDictation} from '../src/dictation.ts';
test('partials replace each other, preserve draft and finalize without duplication',()=>{
 let u=updateDictation(null,'one','chat','где','Вопрос:');assert.equal(u.value,'Вопрос: где ');
 u=updateDictation(u.session,'one','chat','где находится','Вопрос: где ');assert.equal(u.value,'Вопрос: где находится ');
 u=updateDictation(u.session,'one','chat','где находится выход','Вопрос: где находится ');assert.equal(u.value,'Вопрос: где находится выход ');
 assert.equal(updateDictation(u.session,'one','chat','где находится выход',u.value).value,null);
});
test('identical phrases in separate recordings append again; switching chat never copies dictation',()=>{
 const a=updateDictation(null,'one','chat','привет','');
 assert.equal(updateDictation(a.session,'two','chat','привет',a.value).value,'привет привет ');
 assert.equal(updateDictation(a.session,'one','other','привет всем','another draft').value,null);
});

test('late recognition cannot restore a sent or cleared draft or overwrite edits',()=>{
 const a=updateDictation(null,'one','chat','где выход','');
 assert.equal(updateDictation(a.session,'one','chat','где находится выход','').value,null);
 assert.equal(updateDictation(a.session,'one','chat','где находится выход','мой исправленный вопрос').value,null);
 assert.equal(updateDictation(a.session,'one','chat','где находится выход',a.value).value,'где находится выход ');
});

test('restored dictation cannot append again after a frontend reload',()=>{
 const first=updateDictation(null,'v','chat','мой вопрос','');
 const restored=restoreDictation(JSON.stringify(first.session));
 assert.equal(updateDictation(restored,'v','chat','мой вопрос',first.value).value,null);
 assert.equal(updateDictation(restored,'v','chat','уточнённый вопрос','').value,null);
 assert.equal(restoreDictation('broken'),null);
 assert.equal(restoreDictation('{"id":1}'),null);
});
test('a recording remains bound to its original chat when the selected chat changes',()=>{
 const recording=bindDictation(null,'v','original','черновик');
 assert.deepEqual(bindDictation(recording,'v','other','другой'),recording);
 const final=updateDictation(recording,'v',recording.thread,'запись','черновик');
 assert.equal(final.session.thread,'original');
 assert.equal(final.value,'черновик запись ');
 assert.equal(bindDictation(recording,'next','other','другой').thread,'other');
});
