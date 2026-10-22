import test from 'node:test';
import assert from 'node:assert/strict';
import {readGameContext,withGameContext,gameScreenshots} from '../src/game-context.ts';
const base={appId:292030,overview:()=>({display_name:'The Witcher 3'})};
test('finds running game and only shares relevant presence fields',()=>{
 const g=readGameContext({...base,player:()=>({current_game_name:'The Witcher 3',current_game_rich_presence:'Velen',persona:{m_mapRichPresence:new Map([['chapter','Act II'],['connect','secret-server'],['steam_display','#playing']])}})});
 assert.equal(g.name,'The Witcher 3');assert.equal(g.status,'Velen');assert.deepEqual(g.details,[['chapter','Act II']]);
});
test('missing or stale persona preserves title without importing another game status',()=>{
 assert.equal(readGameContext({...base,player:()=>{throw Error('unavailable')}}).name,'The Witcher 3');
 const g=readGameContext({...base,player:()=>({current_game_name:'Other game',current_game_rich_presence:'Wrong level'})});
 assert.equal(g.status,'');assert.deepEqual(g.details,[]);
});
test('no running game, missing overview, Deck AI itself and failed Steam calls are handled',()=>{
 for(const source of [{},{appId:3},{...base,overview:()=>({display_name:'Deck AI'})},{...base,overview:()=>{throw Error()}}])assert.equal(readGameContext(source),null);
});
test('checkbox adds only game name; unchecked preserves user text exactly',()=>{
 const g={...readGameContext(base),status:'Velen',details:[['chapter','Act II']]},q='  Where should I go?\n';
 assert.equal(withGameContext(q,g,false),q);
 assert.equal(withGameContext(q,null,true),q);
 assert.equal(withGameContext(q,g,true),q+'\n\nИгра: The Witcher 3');
});
test('screenshots belong to current game and newest is first',()=>{
 const g=readGameContext(base),shot=(id,when)=>({path:`/Steam/userdata/1/760/remote/${id}/screenshots/${when}.jpg`,when});
 assert.deepEqual(gameScreenshots([shot(1,9),shot(292030,1),shot(292030,3),shot(2920300,10)],g),[shot(292030,3),shot(292030,1)]);
 assert.deepEqual(gameScreenshots([shot(292030,3)],null),[]);
});
