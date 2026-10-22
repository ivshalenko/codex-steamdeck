import test from 'node:test';
import assert from 'node:assert/strict';
import {queueCounts,queueStatus} from '../src/queue.ts';
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
