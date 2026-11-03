"""Protocol-level stand-in for `codex app-server --listen stdio://` (JSON lines).

It is NOT the real server: it only mirrors the methods Deck AI uses, so the
Backend/bridge transport, turn tracking, approvals and notifications can be
exercised end to end without a Codex install.
"""
import json, sys

def send(message):
    sys.stdout.write(json.dumps(message) + '\n'); sys.stdout.flush()

THREAD = {'id': 't1', 'name': 'Удалённая задача', 'updatedAt': 5, 'status': {'type': 'idle'}, 'turns': []}

initialized = False
loaded = set()
if '--noise' in sys.argv:
    print('shell startup banner', flush=True)

for raw in sys.stdin:
    message = json.loads(raw)
    method, ident, params = message.get('method'), message.get('id'), message.get('params', {})
    if method == 'initialize':
        send({'id': ident, **({'error': {'code': -32000, 'message': 'initialization rejected'}} if '--reject-init' in sys.argv else {'result': {}})})
        continue
    if method == 'initialized':
        initialized = True
        continue
    if method and ident is not None and not initialized:
        send({'id': ident, 'error': {'code': -32000, 'message': 'Not initialized'}})
        continue
    if method == 'thread/resume':
        loaded.add(params['threadId'])
        send({'id': ident, 'result': {'thread': THREAD}})
        continue
    if method == 'turn/start':
        if params['threadId'] not in loaded:
            send({'id': ident, 'error': {'code': -32000, 'message': 'Thread not loaded; resume it first'}})
            continue
        send({'id': ident, 'result': {'turn': {'id': 'turn1'}}})
        text = params['input'][0]['text']
        send({'method': 'turn/started', 'params': {'threadId': params['threadId'], 'turn': {'id': 'turn1'}}})
        if 'approve' in text:
            approval_thread = params['threadId']
            send({'id': 'srv1', 'method': 'item/commandExecution/requestApproval', 'params': {'threadId': params['threadId'], 'command': 'rm -rf build'}})
            continue  # completes after the client answers
        send({'method': 'turn/completed', 'params': {'threadId': params['threadId'], 'turn': {'id': 'turn1', 'status': 'completed'}}})
    elif ident == 'srv1' and 'result' in message:
        send({'method': 'turn/completed', 'params': {'threadId': approval_thread, 'turn': {'id': 'turn1', 'status': 'completed' if message['result'].get('decision') == 'accept' else 'failed'}}})
    elif method == 'thread/start':
        loaded.add('t2')
        send({'id': ident, 'result': {'thread': {'id': 't2'}}})
    elif method == 'thread/list':
        send({'id': ident, 'result': {'data': [{k: v for k, v in THREAD.items() if k != 'turns'}]}})
    elif method == 'thread/read':
        send({'id': ident, 'result': {'thread': THREAD}})
    elif ident is not None and method:
        send({'id': ident, 'result': {}})  # initialize, thread/resume, ...
