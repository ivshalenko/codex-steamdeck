"""Optional non-Codex model providers used by the desktop companion.

OpenRouter credentials are held by the desktop Secret Service (KWallet on
SteamOS), never in the application state or Codex configuration files.
"""
import base64
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

OPENROUTER_MODELS = 'https://openrouter.ai/api/v1/models'
OPENROUTER_CHAT = 'https://openrouter.ai/api/v1/chat/completions'
SECRET_LABEL = 'codex-steamdeck-openrouter'
TOKENHARBOR_CHAT = 'https://tokenharbor.ai/v1/chat/completions'
TOKENHARBOR_MODEL = 'deepseek-v4.1-flash:free'


class ProviderError(RuntimeError):
    pass


def _secret_tool(*args, secret=None, account='openrouter'):
    tool = shutil.which('secret-tool')
    if not tool:
        raise ProviderError('Не найдено системное хранилище секретов (secret-tool). Установите libsecret-tools и откройте приложение снова.')
    command = [tool, *args, 'application', 'codex-steamdeck', 'account', account]
    try:
        result = subprocess.run(command, input=secret, text=True, capture_output=True, timeout=12, check=False)
        # Some Plasma installations activate Secret Service under KDE's compat
        # name only. Start that service once, then retry the original operation.
        if result.returncode and 'not activatable' in result.stderr and shutil.which('ksecretd'):
            subprocess.run(['busctl', '--user', 'call', 'org.kde.secretservicecompat',
                            '/SecretService', 'org.freedesktop.DBus.Peer', 'Ping'],
                           capture_output=True, text=True, timeout=5, check=False)
            result = subprocess.run(command, input=secret, text=True, capture_output=True, timeout=12, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ProviderError('Не удалось открыть системное хранилище секретов. Разблокируйте KWallet и повторите попытку.') from exc
    if result.returncode:
        if 'No such secret' in result.stderr or 'not found' in result.stderr.lower() or (args[0] == 'lookup' and result.returncode == 1 and not result.stderr.strip()):
            return ''
        raise ProviderError('Системное хранилище секретов недоступно. Разблокируйте KWallet и повторите попытку.')
    return result.stdout.strip()


def save_openrouter_key(value):
    value = value.strip()
    if not value:
        raise ProviderError('Введите API-ключ OpenRouter.')
    if len(value) > 512 or any(ch.isspace() for ch in value):
        raise ProviderError('Проверьте формат API-ключа OpenRouter.')
    _secret_tool('store', '--label', SECRET_LABEL, secret=value)


def read_openrouter_key():
    return _secret_tool('lookup')


def clear_openrouter_key():
    _secret_tool('clear')


def save_tokenharbor_key(value):
    value = value.strip()
    if not value or len(value) > 512 or any(ch.isspace() for ch in value):
        raise ProviderError('Проверьте формат API-ключа TokenHarbor.')
    _secret_tool('store', '--label', 'codex-steamdeck-tokenharbor', secret=value, account='tokenharbor')


def read_tokenharbor_key():
    return _secret_tool('lookup', account='tokenharbor')


def tokenharbor_models():
    return [{'id': TOKENHARBOR_MODEL, 'name': 'DeepSeek V4.1 Flash · бесплатно',
             'inputPrice': 0.0, 'outputPrice': 0.0}]


def tokenharbor_reply(model, history, text, images=()):
    key = read_tokenharbor_key()
    if not key:
        raise ProviderError('Добавьте API-ключ TokenHarbor в настройках источника DeepSeek.')
    if model != TOKENHARBOR_MODEL:
        raise ProviderError('Неизвестная модель TokenHarbor.')
    messages = list(history)
    user_text = text
    if images:
        raise ProviderError('TokenHarbor сейчас подключён для текстовых запросов.')
    messages.append({'role': 'user', 'content': user_text})
    body = json.dumps({'model': model, 'messages': messages, 'stream': False}).encode()
    request = urllib.request.Request(TOKENHARBOR_CHAT, data=body, headers={
        'Authorization': 'Bearer ' + key,
        'Content-Type': 'application/json',
        'User-Agent': 'Deck-AI-for-Steam-Deck',
    })
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise ProviderError('TokenHarbor отклонил API-ключ. Проверьте ключ в настройках.') from None
        if exc.code == 429:
            raise ProviderError('TokenHarbor временно ограничил запрос. Повторите позже.') from None
        raise ProviderError(f'TokenHarbor не выполнил запрос (HTTP {exc.code}).') from None
    except (OSError, ValueError, urllib.error.URLError) as exc:
        raise ProviderError('Не удалось получить ответ от TokenHarbor. Проверьте подключение.') from exc
    try:
        answer = result['choices'][0]['message'].get('content')
    except (KeyError, IndexError, TypeError):
        raise ProviderError('TokenHarbor вернул ответ в неподдерживаемом формате.') from None
    if isinstance(answer, list):
        answer = '\n'.join(part.get('text', '') for part in answer if isinstance(part, dict))
    if not isinstance(answer, str) or not answer.strip():
        raise ProviderError('Модель TokenHarbor вернула пустой ответ.')
    return answer.strip()


def list_deepseek_models():
    query = urllib.parse.urlencode({'model_authors': 'deepseek', 'output_modalities': 'text'})
    request = urllib.request.Request(OPENROUTER_MODELS + '?' + query, headers={'User-Agent': 'Codex-for-Steam-Deck'})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            catalog = json.load(response).get('data', [])
    except (OSError, ValueError, urllib.error.URLError) as exc:
        raise ProviderError('Не удалось загрузить модели DeepSeek из OpenRouter. Проверьте подключение к интернету.') from exc
    models = []
    for item in catalog:
        model_id = item.get('id')
        if not model_id:
            continue
        pricing = item.get('pricing') or {}
        try:
            in_price = float(pricing.get('prompt') or 0)
            out_price = float(pricing.get('completion') or 0)
        except (ValueError, TypeError):
            in_price = out_price = None
        models.append({'id': model_id, 'name': item.get('name') or model_id,
                       'inputPrice': in_price, 'outputPrice': out_price})
    return models


def openrouter_reply(model, history, text, images=()):
    key = read_openrouter_key()
    if not key:
        raise ProviderError('Добавьте API-ключ OpenRouter в настройках источника DeepSeek.')
    messages = list(history)
    content = [{'type': 'text', 'text': text}]
    for path in images:
        try:
            source = Path(path)
            data = source.read_bytes()
            if len(data) > 30_000_000:
                raise ProviderError('Изображение превышает лимит 30 МБ.')
            suffix = source.suffix.lower()
            mime = {'jpg': 'image/jpeg', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                    '.png': 'image/png', '.webp': 'image/webp'}.get(suffix, 'image/jpeg')
            encoded = base64.b64encode(data).decode('ascii')
            content.append({'type': 'image_url', 'image_url': {'url': f'data:{mime};base64,{encoded}'}})
        except OSError as exc:
            raise ProviderError('Не удалось прочитать прикреплённый снимок.') from exc
    messages.append({'role': 'user', 'content': content if images else text})
    body = json.dumps({'model': model, 'messages': messages, 'stream': False}).encode()
    request = urllib.request.Request(OPENROUTER_CHAT, data=body, headers={
        'Authorization': 'Bearer ' + key,
        'Content-Type': 'application/json',
        'X-Title': 'Deck AI for Steam Deck',
    })
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        # Provider response bodies can echo request details; never display or log them.
        if exc.code in (401, 403):
            raise ProviderError('OpenRouter отклонил API-ключ. Проверьте его в настройках.') from None
        if exc.code == 429:
            raise ProviderError('OpenRouter временно ограничил запрос. Проверьте лимиты аккаунта и повторите позже.') from None
        raise ProviderError(f'OpenRouter не выполнил запрос (HTTP {exc.code}).') from None
    except (OSError, ValueError, urllib.error.URLError) as exc:
        raise ProviderError('Не удалось получить ответ от OpenRouter. Проверьте подключение.') from exc
    try:
        answer = result['choices'][0]['message'].get('content')
    except (KeyError, IndexError, TypeError):
        raise ProviderError('OpenRouter вернул ответ в неподдерживаемом формате.') from None
    if isinstance(answer, list):
        answer = '\n'.join(part.get('text', '') for part in answer if isinstance(part, dict))
    if not isinstance(answer, str) or not answer.strip():
        raise ProviderError('Модель вернула пустой ответ.')
    return answer.strip()


def claude_code_available():
    return shutil.which('claude')


def claude_subscription_status(binary=None):
    binary = binary or claude_code_available()
    if not binary:
        return {'loggedIn': False, 'method': 'none'}
    try:
        result = subprocess.run([binary, 'auth', 'status', '--json'], capture_output=True, text=True, timeout=12, check=False)
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return {'loggedIn': False, 'method': 'unknown'}
    method = payload.get('authMethod', 'none')
    return {'loggedIn': result.returncode == 0 and method in ('claude.ai', 'oauth_token'), 'method': method}


def claude_code_reply(model, session_id, text, cwd=None, resume=True):
    binary = claude_code_available()
    if not binary:
        raise ProviderError('Claude Code не установлен. Установите его с официального сайта Anthropic и выполните вход по Claude Pro/Max.')
    auth = claude_subscription_status(binary)
    if not auth['loggedIn']:
        raise ProviderError('Claude Code не вошёл через подписку Claude Pro/Max. Откройте «Войти в Claude Code» и выполните вход без Anthropic Console API.')
    command = [binary, '-p', '--output-format', 'json', '--model', model,
               '--permission-mode', 'acceptEdits', '--permission-prompts', 'none']
    if session_id and resume:
        command += ['--resume', session_id]
    else:
        command += ['--session-id', str(session_id or __import__('uuid').uuid4())]
    try:
        result = subprocess.run(command, input=text, text=True, capture_output=True,
                                cwd=cwd or str(Path.home()), timeout=300, check=False,
                                env={**os.environ, 'NO_COLOR': '1', 'ANTHROPIC_API_KEY': '', 'ANTHROPIC_AUTH_TOKEN': ''})
    except subprocess.TimeoutExpired as exc:
        raise ProviderError('Claude Code не завершил запрос за 5 минут.') from exc
    except OSError as exc:
        raise ProviderError('Не удалось запустить Claude Code.') from exc
    if result.returncode:
        # Keep diagnostics concise; never include the process environment.
        diagnostic = (result.stderr or result.stdout or '').strip().splitlines()
        safe = diagnostic[-1][:300] if diagnostic else 'проверьте вход Claude Code командой claude'
        raise ProviderError('Claude Code: ' + safe)
    try:
        payload = json.loads(result.stdout)
        answer = payload.get('result') or payload.get('message', {}).get('content')
        if isinstance(answer, list):
            answer = '\n'.join(block.get('text', '') for block in answer if isinstance(block, dict))
    except (ValueError, AttributeError):
        answer = result.stdout.strip()
    if not answer:
        raise ProviderError('Claude Code вернул пустой ответ.')
    return answer.strip()


# --- Any cloud AI with an OpenAI-compatible API: OpenAI, Gemini, Groq, Mistral, DeepSeek, xAI, OpenRouter... ---
CUSTOM_PRESETS = [
    ('OpenAI', 'https://api.openai.com/v1'),
    ('Google Gemini', 'https://generativelanguage.googleapis.com/v1beta/openai'),
    ('Groq', 'https://api.groq.com/openai/v1'),
    ('Mistral', 'https://api.mistral.ai/v1'),
    ('DeepSeek', 'https://api.deepseek.com'),
    ('xAI Grok', 'https://api.x.ai/v1'),
    ('Together', 'https://api.together.xyz/v1'),
    ('Fireworks', 'https://api.fireworks.ai/inference/v1'),
    ('OpenRouter', 'https://openrouter.ai/api/v1'),
]
CUSTOM_LIMIT = 8


def is_cloud_host(host):
    """Cloud services only: a public https host, never localhost, a LAN address or an internal name."""
    import ipaddress
    host = (host or '').lower().rstrip('.')
    try:
        return ipaddress.ip_address(host).is_global
    except ValueError:
        pass
    return '.' in host and not host.endswith(('.local', '.localhost', '.internal', '.lan', '.home', '.corp', '.intranet'))


def normalize_base_url(value):
    """Return the API base without a trailing slash; only https URLs of public cloud hosts, without credentials."""
    value = (value or '').strip().rstrip('/')
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or len(value) > 300:
        raise ProviderError('Укажите адрес облачного API вида https://хост/v1 (только https, без логина и пароля в адресе).')
    if not is_cloud_host(parsed.hostname):
        raise ProviderError('Подключаются только облачные сервисы: адрес должен вести на публичный сервер в интернете, а не на этот или локальный компьютер.')
    for suffix in ('/chat/completions',):
        if value.endswith(suffix):
            value = value[:-len(suffix)]
    return value


def _cloud_url(value):
    try:
        return bool(normalize_base_url(value))
    except ProviderError:
        return False


def _slug(name):
    slug = ''.join(ch if ch.isalnum() else '-' for ch in name.lower()).strip('-')
    return slug[:32] or 'ai'


def load_custom(state_dir):
    try:
        data = json.loads((Path(state_dir)/'custom-providers.json').read_text())
        return [item for item in data if isinstance(item, dict) and item.get('id', '').startswith('custom:') and _cloud_url(item.get('baseUrl'))][:CUSTOM_LIMIT]
    except (OSError, ValueError, TypeError):
        return []


def _write_custom(state_dir, items):
    path = Path(state_dir)/'custom-providers.json'
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(items, ensure_ascii=False))
    os.chmod(temp, 0o600)
    os.replace(temp, path)


def save_custom(state_dir, name, base_url, models='', key=''):
    """Add a cloud connection (or update the one with the same name). The API key goes to the system secret store."""
    name = (name or '').strip()[:40]
    if not name:
        raise ProviderError('Введите название подключения.')
    base = normalize_base_url(base_url)
    if isinstance(models, str):
        models = [m.strip() for m in models.replace('\n', ',').split(',')]
    models = [m for m in dict.fromkeys(models) if m and len(m) <= 120][:50]
    items = load_custom(state_dir)
    ident = 'custom:' + _slug(name)
    if not key.strip() and not read_custom_key(ident):
        raise ProviderError('Введите API-ключ облачного сервиса.')
    items = [item for item in items if item['id'] != ident]
    if len(items) >= CUSTOM_LIMIT:
        raise ProviderError(f'Можно хранить до {CUSTOM_LIMIT} подключений. Удалите ненужное.')
    items.append({'id': ident, 'name': name, 'baseUrl': base, 'models': models})
    _write_custom(state_dir, items)
    if key.strip():
        save_custom_key(ident, key)
    return ident


def remove_custom(state_dir, ident):
    items = load_custom(state_dir)
    if not any(item['id'] == ident for item in items):
        raise ProviderError('Подключение не найдено.')
    _write_custom(state_dir, [item for item in items if item['id'] != ident])
    try:
        _secret_tool('clear', account=ident.replace(':', '-'))
    except ProviderError:
        pass


def save_custom_key(ident, value):
    value = value.strip()
    if not value or len(value) > 512 or any(ch.isspace() for ch in value):
        raise ProviderError('Проверьте формат API-ключа.')
    _secret_tool('store', '--label', 'codex-steamdeck-' + ident.replace(':', '-'), secret=value, account=ident.replace(':', '-'))


def read_custom_key(ident):
    try:
        return _secret_tool('lookup', account=ident.replace(':', '-'))
    except ProviderError:
        return ''


def _headers(key):
    headers = {'Content-Type': 'application/json', 'User-Agent': 'Deck-AI-for-Steam-Deck', 'X-Title': 'Deck AI for Steam Deck'}
    if key:
        headers['Authorization'] = 'Bearer ' + key
    return headers


def custom_models(entry):
    """Models of a connection: the service's own /models list, else the names typed by the user."""
    request = urllib.request.Request(entry['baseUrl'] + '/models', headers=_headers(read_custom_key(entry['id'])))
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            data = json.load(response).get('data', [])
        found = [item['id'] for item in data if isinstance(item, dict) and item.get('id')]
    except (OSError, ValueError, urllib.error.URLError, AttributeError, TypeError):
        found = []
    ids = list(dict.fromkeys([*entry.get('models', []), *found]))
    return [{'id': model, 'name': model} for model in ids[:200]]


def custom_reply(entry, model, history, text, images=()):
    key = read_custom_key(entry['id'])
    if not key:
        raise ProviderError(f"Добавьте API-ключ для «{entry['name']}» в настройках этого сервиса.")
    content = [{'type': 'text', 'text': text}]
    for path in images:
        try:
            data = Path(path).read_bytes()
            if len(data) > 30_000_000:
                raise ProviderError('Изображение превышает лимит 30 МБ.')
            mime = {'.png': 'image/png', '.webp': 'image/webp'}.get(Path(path).suffix.lower(), 'image/jpeg')
            content.append({'type': 'image_url', 'image_url': {'url': f'data:{mime};base64,{base64.b64encode(data).decode("ascii")}'}})
        except OSError as exc:
            raise ProviderError('Не удалось прочитать прикреплённый снимок.') from exc
    messages = [*history, {'role': 'user', 'content': content if images else text}]
    request = urllib.request.Request(entry['baseUrl'] + '/chat/completions', headers=_headers(key),
                                     data=json.dumps({'model': model, 'messages': messages, 'stream': False}).encode())
    name = entry['name']
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        # Response bodies can echo request details; never show or log them.
        if exc.code in (401, 403):
            raise ProviderError(f'{name} отклонил API-ключ. Проверьте ключ в настройках.') from None
        if exc.code == 404:
            raise ProviderError(f'{name}: модель или адрес API не найдены. Проверьте адрес и название модели.') from None
        if exc.code == 429:
            raise ProviderError(f'{name} временно ограничил запросы. Повторите позже.') from None
        raise ProviderError(f'{name} не выполнил запрос (HTTP {exc.code}).') from None
    except (OSError, ValueError, urllib.error.URLError) as exc:
        raise ProviderError(f'Не удалось получить ответ от {name}. Проверьте адрес и что сервис запущен.') from exc
    try:
        answer = result['choices'][0]['message'].get('content')
    except (KeyError, IndexError, TypeError):
        raise ProviderError(f'{name} вернул ответ в неподдерживаемом формате.') from None
    if isinstance(answer, list):
        answer = '\n'.join(part.get('text', '') for part in answer if isinstance(part, dict))
    if not isinstance(answer, str) or not answer.strip():
        raise ProviderError(f'Модель {name} вернула пустой ответ.')
    return answer.strip()
