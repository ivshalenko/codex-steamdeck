import test from 'node:test';
import assert from 'node:assert/strict';
import {chatFailures,queueCounts,queueStatus} from '../src/queue.ts';
test('waiting requests from other chats are not presented as this chat queue',()=>{
 const jobs=[{id:'1',threadId:'other',status:'queued',text:'first'},{id:'2',threadId:'other',status:'sending',text:'working'}];
 assert.deepEqual(queueCounts(jobs,'current'),{waiting:1,current:0,other:1});
 assert.deepEqual(queueCounts(jobs,'other'),{waiting:1,current:1,other:0});
});
test('queue status distinguishes waiting, recovery, errors and long-running work',()=>{
 assert.equal(queueStatus({status:'queued'}),'Ожидает отправки');
 assert.equal(queueStatus({status:'recovering'}),'Проверяется на сервере');
 assert.equal(queueStatus({status:'error'}),'Ошибка');
 assert.equal(queueStatus({status:'sending',createdAt:100},120000),'Выполняется');
 assert.equal(queueStatus({status:'sending',createdAt:100},2000000),'Долго выполняется · проверьте чат');
 assert.equal(queueStatus({status:'sending',createdAt:100,startedAt:1999},2000000),'Выполняется');
});

test('old errors stay in their own conversation and device',()=>{
 const jobs=[{id:'1',threadId:'old',status:'error',text:''},{id:'2',threadId:'visible',host:'mac',status:'error',text:''},{id:'3',threadId:'visible',status:'error',text:''}];
 assert.deepEqual(chatFailures(jobs,'visible').map(j=>j.id),['3']);
 assert.deepEqual(chatFailures(jobs,'visible','mac').map(j=>j.id),['2']);
 assert.deepEqual(chatFailures(jobs,'new'),[]);
});
