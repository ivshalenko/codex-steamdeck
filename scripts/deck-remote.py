#!/usr/bin/env python3
"""Control the Codex on a Steam Deck (or any SSH host) from a Mac or PC.

    python3 scripts/deck-remote.py steamdeck list
    python3 scripts/deck-remote.py steamdeck read THREAD_ID
    python3 scripts/deck-remote.py steamdeck send THREAD_ID "run the tests" --wait
    python3 scripts/deck-remote.py steamdeck new "start a new task" --wait

HOST is an alias from ~/.ssh/config (see `deck_share.py status` on the Deck).
Only Python 3 and ssh are needed. Messages appear in the Deck AI app because
both use the same Codex chat storage on the Deck.
"""
import argparse
import subprocess
import sys
import threading
import re
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend import Backend, RpcError


class Session:
    def __init__(self, host, ask=None, out=print):
        self.host, self.ask, self.out = host, ask, out
        self.done = threading.Event()
        self.turn_id = None
        self.thread_id = None
        self.completions = {}
        self.status = None
        self.backend = Backend(self.on_event, lambda: self.done.set(), host)

    def on_event(self, message):
        method, params = message.get('method'), message.get('params', {})
        if 'id' in message and method and method.endswith('requestApproval'):
            summary = params.get('command') or params.get('reason') or method
            try:
                answer = (self.ask or input)(f'Агент просит разрешение: {summary}\nРазрешить? [y/N] ').strip().lower()
            except EOFError:  # no terminal attached: never approve silently
                answer = ''
            self.backend.respond(message['id'], {'decision': 'accept' if answer in ('y', 'yes', 'д', 'да') else 'decline'})
        elif method == 'turn/completed' and params.get('threadId') == self.thread_id:
            turn = params.get('turn') or {}
            self.completions[turn.get('id')] = turn.get('status') or 'completed'
            if self.turn_id is not None and turn.get('id') == self.turn_id:
                self.status = self.completions[self.turn_id]
                self.done.set()

    def __enter__(self):
        self.backend.connect(None)
        return self

    def __exit__(self, *_):
        self.backend.close()

    def threads(self):
        return self.backend.request('thread/list', {'limit': 30, 'sortKey': 'updated_at', 'archived': False}, timeout=25).get('data', [])

    def read(self, thread_id):
        return self.backend.request('thread/read', {'threadId': thread_id, 'includeTurns': True}, timeout=30).get('thread', {})

    def send(self, thread_id, text, wait=False, timeout=900):
        self.done.clear()
        self.turn_id = self.status = None
        self.completions.clear()
        if thread_id is None:
            started = self.backend.request('thread/start', {'cwd': self.backend.cwd, 'ephemeral': False}, timeout=35)
            thread_id = (started.get('thread') or started)['id']
        else:
            self.backend.request('thread/resume', {'threadId': thread_id, 'excludeTurns': True}, timeout=50)
        self.thread_id = thread_id
        params = {'threadId': thread_id, 'input': [{'type': 'text', 'text': text, 'text_elements': []}], 'clientUserMessageId': str(uuid.uuid4())}
        self.turn_id = self.backend.request('turn/start', params, timeout=35).get('turn', {}).get('id')
        if self.turn_id in self.completions:
            self.status = self.completions[self.turn_id]
            self.done.set()
        if wait and not self.done.wait(timeout):
            raise RpcError('Агент не завершил задачу за отведённое время.')
        if wait and self.status != 'completed':
            raise RpcError('Задача не завершена: ' + (self.status or 'соединение прервано'))
        return thread_id


def setup(alias, address, user='deck', assume_yes=False, home=None, ask=input, out=print):
    """Guided one-time setup on the Mac/PC: key, ~/.ssh/config block, connection test."""
    ssh_dir = Path(home or Path.home())/'.ssh'
    ssh_dir.mkdir(mode=0o700, exist_ok=True)
    key = ssh_dir/'id_ed25519'
    def confirm(question):
        return assume_yes or ask(question + ' [y/N] ').strip().lower() in ('y', 'yes', 'д', 'да')
    if not key.exists():
        if not confirm(f'SSH-ключа нет. Создать {key}?'):
            return 'Без ключа продолжить нельзя.'
        subprocess.run(['ssh-keygen', '-t', 'ed25519', '-N', '', '-C', 'deck-ai', '-f', str(key)], check=True, capture_output=True)
    config = ssh_dir/'config'
    existing = config.read_text() if config.exists() else ''
    if re.search(rf'^\s*Host\s+{re.escape(alias)}\s*$', existing, re.M):
        out(f'Блок Host {alias} уже есть в {config}, не меняю.')
    elif confirm(f'Добавить блок Host {alias} в {config}?'):
        block = (f'\nHost {alias}\n    HostName {address}\n    User {user}\n    IdentityFile {key}\n'
                 f'    ServerAliveInterval 15\n    ControlMaster auto\n    ControlPath ~/.ssh/cm-%C\n    ControlPersist 10m\n')
        config.write_text(existing + block)
        config.chmod(0o600)
    public = (key.with_suffix('.pub')).read_text().strip()
    out('\nНа Steam Deck (Desktop Mode, терминал) один раз выполните:')
    out('  sudo systemctl enable --now sshd')
    for directory in ('deck-ai', 'deck-voice'):
        out(f"  test ! -f ~/.local/share/{directory}/deck_share.py || python3 ~/.local/share/{directory}/deck_share.py add-key '{public}'")
    out('(или вставьте этот ключ в Deck AI → Настройки → «Доступ с другого компьютера»)\n')
    if assume_yes or ask('Нажмите Enter, когда сделаете это (или n, чтобы проверить позже): ').strip().lower() != 'n':
        result = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', alias, 'echo ok'], capture_output=True, text=True)
        out('Подключение работает.' if result.returncode == 0 and 'ok' in result.stdout else 'Пока не подключается: проверьте, что sshd включён и ключ добавлен.')
    return 0


def last_answer(thread):
    for turn in reversed(thread.get('turns', [])):
        for item in reversed(turn.get('items', [])):
            if item.get('type') == 'agentMessage' and item.get('text'):
                return item['text']
    return ''


def main(argv=None, out=print):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('host', help='SSH alias (for `setup`: the alias to create)')
    sub = parser.add_subparsers(dest='command', required=True)
    prepare = sub.add_parser('setup', help='one-time guided setup: key, ssh config, test')
    prepare.add_argument('address', help='Deck IP address or name'); prepare.add_argument('--user', default='deck'); prepare.add_argument('--yes', action='store_true')
    sub.add_parser('list')
    read = sub.add_parser('read'); read.add_argument('thread')
    send = sub.add_parser('send'); send.add_argument('thread'); send.add_argument('text'); send.add_argument('--wait', action='store_true')
    new = sub.add_parser('new'); new.add_argument('text'); new.add_argument('--wait', action='store_true')
    args = parser.parse_args(argv)
    if args.command == 'setup':
        return setup(args.host, args.address, args.user, args.yes, out=out)
    try:
        with Session(args.host, out=out) as session:
            if args.command == 'list':
                for thread in session.threads():
                    out(f"{thread['id']}  {thread.get('name') or thread.get('preview') or 'Без названия'}")
            elif args.command == 'read':
                thread = session.read(args.thread)
                out(last_answer(thread) or '(ответов пока нет)')
            else:
                thread_id = session.send(None if args.command == 'new' else args.thread, args.text, args.wait)
                if args.wait:
                    out(last_answer(session.read(thread_id)) or f'Готово ({session.status}).')
                else:
                    out(f'Отправлено в чат {thread_id}. Результат появится в Deck AI.')
    except (RpcError, RuntimeError, OSError) as exc:
        return str(exc)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
