import test from 'node:test';
import assert from 'node:assert/strict';
import {workspaceNavigation} from '../src/navigation.ts';
test('requested tab reaches an existing workspace and a fresh view across module reloads',()=>{
 const data=new Map(),storage={getItem:k=>data.get(k)||null,setItem:(k,v)=>data.set(k,v)},events=new EventTarget();
 const existing=workspaceNavigation(storage,events),compact=workspaceNavigation(storage,events),seen=[];
 const stop=existing.subscribe(tab=>seen.push(tab));compact.request('settings');
 assert.deepEqual(seen,['settings']);assert.equal(workspaceNavigation(storage,events).current(),'settings');
 const e=new Event('storage');Object.assign(e,{key:'deck-ai-workspace-tab',newValue:JSON.stringify({tab:'repair'})});events.dispatchEvent(e);
 assert.deepEqual(seen,['settings','repair']);stop();compact.request('chat');assert.equal(seen.length,2);
});
test('corrupt stored tab and unavailable storage do not prevent local navigation',()=>{
 const events=new EventTarget(),store={getItem:()=>'{broken',setItem:()=>{throw Error('quota')}};
 const nav=workspaceNavigation(store,events),seen=[];nav.subscribe(tab=>seen.push(tab));assert.equal(nav.current(),'chat');nav.request('settings');assert.equal(nav.current(),'settings');assert.deepEqual(seen,['settings']);
});
