import test from 'node:test';
import assert from 'node:assert/strict';
import {scrollableFrom,dragTop,decay,attachTouchScroll} from '../src/touch-scroll.ts';
const box=(over={},parent=null)=>({scrollTop:0,scrollHeight:1000,clientHeight:200,parentElement:parent,...over});
test('finds the nearest scrollable ancestor and stops at the root',()=>{
 const root=box({scrollHeight:200});const list=box({},root);const item=box({scrollHeight:30,clientHeight:30},list);
 const can=el=>el.scrollHeight>el.clientHeight;
 assert.equal(scrollableFrom(item,can,root),list);
 assert.equal(scrollableFrom(box({scrollHeight:10,clientHeight:10},root),can,root),null);
});
test('dragging up scrolls down and is clamped to the content',()=>{
 const b=box();
 assert.equal(dragTop(b,100,300,250),150);
 assert.equal(dragTop(b,100,300,900),0);
 assert.equal(dragTop(b,700,300,0),800);
});
test('momentum fades out',()=>{let v=20,n=0;while(v&&n<500){v=decay(v);n++;}assert.equal(v,0);assert.ok(n>5&&n<100);});
test('touch events scroll the list, cancel the native pan and glide afterwards',()=>{
 const list=box();const handlers={};
 const root={...box({scrollHeight:200}),addEventListener:(n,f)=>{handlers[n]=f;},removeEventListener:()=>{}};
 list.parentElement=root;const frames=[];
 const detach=attachTouchScroll(root,el=>el===list,fn=>frames.push(fn));
 handlers.touchstart({target:list,touches:[{clientY:400}]});
 let prevented=false;
 handlers.touchmove({touches:[{clientY:398}],cancelable:true,preventDefault:()=>{prevented=true;}});
 assert.equal(list.scrollTop,0);assert.equal(prevented,false); // below the tap threshold
 handlers.touchmove({touches:[{clientY:300}],cancelable:true,preventDefault:()=>{prevented=true;}});
 assert.equal(list.scrollTop,100);assert.equal(prevented,true);
 handlers.touchend({});
 for(let i=0;i<200&&frames.length;i++)frames.shift()();
 assert.ok(list.scrollTop>=100);
 detach();
});
