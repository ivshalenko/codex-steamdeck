import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { runInNewContext } from 'node:vm';

const app = readFileSync(new URL('../repair-web/app.js', import.meta.url), 'utf8');
const connected = {
  state: 'connected',
  case: {
    id: 'case', name: 'Fixture', checks: [], state: 'inspected',
    action: { id: 'approval', kind: 'reset', state: 'pending' },
  },
};

function response(value) {
  return { ok: true, json: async () => value };
}

async function openPage() {
  const elements = new Map();
  const listeners = new Map();
  const timers = new Map();
  const requests = [];
  const navigator = { onLine: true };
  const element = id => {
    if (!elements.has(id)) elements.set(id, { hidden: true, dataset: {}, replaceChildren() {} });
    return elements.get(id);
  };
  const eventTarget = { addEventListener: (event, handler) => listeners.set(event, handler) };
  const first = runInNewContext(`(async () => { ${app}\n })()`, {
    document: {
      ...eventTarget, getElementById: element, createElement: () => ({}),
      querySelectorAll: () => [], hidden: false,
    },
    window: eventTarget,
    navigator, location: { hash: '' }, AbortController,
    setTimeout(handler, delay) {
      const id = Symbol();
      timers.set(id, { handler, delay });
      return id;
    },
    clearTimeout: id => timers.delete(id),
    fetch(url) {
      if (!requests.length) {
        requests.push({ url });
        return Promise.resolve(response(connected));
      }
      return new Promise(resolve => requests.push({ url, resolve }));
    },
  });
  await first;
  return {
    element, requests,
    offline() { navigator.onLine = false; listeners.get('offline')(); },
    online() { navigator.onLine = true; listeners.get('online')(); },
    poll(expectedDelay) {
      const timer = [...timers].find(([, value]) => value.delay === expectedDelay);
      assert.ok(timer, `Missing poll scheduled after ${expectedDelay} ms`);
      timers.delete(timer[0]);
      timer[1].handler();
    },
  };
}

test('a late poll cannot reveal a pending approval while offline', async () => {
  const page = await openPage();
  page.poll(2200);
  page.offline();
  page.requests[1].resolve(response(connected));
  await new Promise(setImmediate);
  assert.equal(page.element('case').hidden, true);
  assert.match(page.element('status').textContent, /подключения к сети/);
  page.online();
  page.poll(0);
  page.requests[2].resolve(response(connected));
  await new Promise(setImmediate);
  assert.equal(page.element('case').hidden, false);
});

test('returning online during a slow approval triggers a fresh status check', async () => {
  const page = await openPage();
  page.element('accept').onclick();
  assert.equal(page.requests[1].url, '/api/decision');
  page.offline();
  page.online();
  page.poll(0);
  assert.equal(page.requests.length, 2);
  page.requests[1].resolve(response(connected));
  await new Promise(setImmediate);
  assert.equal(page.element('case').hidden, true);
  page.poll(0);
  page.requests[2].resolve(response(connected));
  await new Promise(setImmediate);
  assert.equal(page.element('case').hidden, false);
});
