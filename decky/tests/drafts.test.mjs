import test from 'node:test';
import assert from 'node:assert/strict';
import {createDraftStore,createSnapshotReader,createViewGate,draftOwner} from '../src/drafts.ts';
function storage(){const data=new Map();return {getItem:key=>data.get(key)??null,setItem:(key,value)=>data.set(key,value)};}
test('editing QAM updates an already-mounted full screen and preserves another chat',()=>{
 const store=createDraftStore(storage());store.write('other','keep');let panel='',full='';
 store.subscribe((id,text)=>{if(id==='chat')panel=text;});const off=store.subscribe((id,text)=>{if(id==='chat')full=text;});
 store.write('chat','typing before navigation');assert.equal(panel,'typing before navigation');assert.equal(full,panel);assert.equal(store.read('other'),'keep');
 off();store.write('chat','next');assert.equal(full,'typing before navigation');assert.equal(store.read('chat'),'next');
});
test('late input belonging to old chat cannot replace current chat draft',()=>{
 const store=createDraftStore(storage());store.write('new','my new text');store.write('old','late old callback');assert.equal(store.read('new'),'my new text');
});
test('polls from either view and mid-action polls cannot overwrite navigation',()=>{
 const gate=createViewGate(),before=gate.token();assert.equal(gate.begin(),true);const during=gate.token();assert.equal(gate.begin(),false);assert.equal(gate.current(before),false);assert.equal(gate.current(during),false);gate.end();assert.equal(gate.current(before),false);assert.equal(gate.current(during),false);assert.equal(gate.current(gate.token()),true);
});
test('new drafts and mirrored chat IDs are isolated by device and provider',()=>{
 const store=createDraftStore(storage());
 for(const threadId of ['', 'same-thread']){
  const views=[{provider:'codex',threadId},{provider:'codex',remoteHost:'deck',threadId},
   {provider:'codex',remoteHost:'work',threadId},{provider:'claude',threadId}];
  assert.equal(draftOwner(views[0]),threadId);
  views.forEach((view,index)=>store.write(draftOwner(view),String(index)));
  assert.deepEqual(views.map(view=>store.read(draftOwner(view))),['0','1','2','3']);
 }
});
test('two views share one pending snapshot and invalidate it on navigation',async()=>{
 let now=0, calls=0;
 const pending=[];
 const read=createSnapshotReader(()=>{calls++;return new Promise(resolve=>pending.push(resolve));},()=>now);
 const first=read(0,2000);
 assert.equal(first,read(0,2000));
 const switched=read(1,2000);
 await Promise.resolve();
 assert.equal(calls,2);
 pending[1]('new');pending[0]('old');
 assert.equal(await switched,'new');
 assert.equal(await first,'old');
 now=1950;
 assert.equal(await read(1,2000),'new');
 now=2050;
 const expired=read(1,2000);
 await Promise.resolve();
 assert.equal(calls,3);
 pending[2]('updated');
 assert.equal(await expired,'updated');
});
