import test from 'node:test';
import assert from 'node:assert/strict';
import {readAppearance,withChoice,effectiveLayout,defaultAppearance,themes} from '../src/appearance.ts';
test('appearance: defaults, validation per field, bad json',()=>{
 assert.deepEqual(readAppearance(null),defaultAppearance);
 assert.deepEqual(readAppearance("{broken"),defaultAppearance);
 assert.deepEqual(readAppearance('{"theme":"violet","density":"huge","layout":"split"}'),{...defaultAppearance,theme:"violet",layout:"split"});
 assert.deepEqual(readAppearance('[1,2]'),defaultAppearance);
});
test('appearance: choices are validated and split needs full screen',()=>{
 assert.equal(withChoice(defaultAppearance,"theme","forest").theme,"forest");
 assert.equal(withChoice(defaultAppearance,"theme","<script>"),defaultAppearance);
 assert.equal(effectiveLayout("split",false),"classic");assert.equal(effectiveLayout("split",true),"split");assert.equal(effectiveLayout("bottom",false),"bottom");
 assert.ok(themes.length>=6&&new Set(themes.map(t=>t.id)).size===themes.length);
});
