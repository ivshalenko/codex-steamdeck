import test from 'node:test';
import assert from 'node:assert/strict';
import {createDraftStore,createViewGate} from '../src/drafts.ts';
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
