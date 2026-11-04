import test from 'node:test';
import assert from 'node:assert/strict';
import {makeUpdateStore,startUpdatePolling,updateStore,updateActive} from '../src/updates.ts';
const state=(phase=null)=>({installed:{plugin:'1.0.0-rc.16'},available:null,preferences:{automatic:true,channel:'automatic'},channel:'preview',checkedAt:1,checking:false,checkError:'',job:phase?{id:'test',phase,version:'1.0.0-rc.17',progress:.2}:null,busyDesktop:false,notificationPending:false});

test('unsaved work in any mounted view blocks an update until every view is clean',()=>{
 const store=makeUpdateStore(),a=Symbol(),b=Symbol();let notifications=0;store.subscribe(()=>notifications++);
 store.block(a,true);store.block(b,true);store.block(a,false);assert.equal(store.blocked(),true);
 store.block(b,false);assert.equal(store.blocked(),false);assert.equal(notifications,4);
});
test('concurrent install requests cannot replace an in-flight request and failures clear its state',async()=>{
 const store=makeUpdateStore();let resolve;
 const first=store.request(()=>new Promise(done=>resolve=done));
 await assert.rejects(store.request(async()=>state()),/already running/);assert.equal(store.snapshot().requesting,true);
 resolve(state('downloading'));await first;assert.equal(store.snapshot().requesting,false);assert.equal(updateActive(store.snapshot().data),true);
 await assert.rejects(store.request(async()=>{throw Error('offline');}),/offline/);assert.equal(store.snapshot().requesting,false);assert.equal(store.snapshot().error,'offline');
 assert.equal(store.snapshot().data.job.phase,'downloading');
});
test('polling follows installation progress and stopping discards a late reply',async()=>{
 const scheduled=[];let resolve,seen=0;const timer={set:(fn,ms)=>{scheduled.push({fn,ms});return scheduled.length;},clear:()=>{}};
 const client={status:()=>new Promise(done=>resolve=done)};
 const stop=startUpdatePolling(client,async()=>{seen++;},timer);resolve(state('installing'));await new Promise(done=>setImmediate(done));
 assert.equal(scheduled[0].ms,2000);assert.equal(seen,1);
 scheduled[0].fn();stop();resolve(state('completed'));await new Promise(done=>setImmediate(done));
 assert.equal(seen,1);assert.equal(updateStore.snapshot().data.job.phase,'installing');
});
test('completed and failed transactions are terminal rather than active update locks',()=>{
 for(const phase of ['completed','failed'])assert.equal(updateActive(state(phase)),false);
 for(const phase of ['queued','quiescing','rolling-back','verifying'])assert.equal(updateActive(state(phase)),true);
});
