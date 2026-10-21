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


class ProviderError(RuntimeError):
    pass


def _secret_tool(*args, secret=None):
    tool = shutil.which('secret-tool')
    if not tool:
        raise ProviderError('Не найдено системное хранилище секретов (secret-tool). Установите libsecret-tools и откройте приложение снова.')
    command = [tool, *args, 'application', 'codex-steamdeck', 'account', 'openrouter']
    try:
        result = subprocess.run(command, input=secret, text=True, capture_output=True, timeout=12, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ProviderError('Не удалось обратиться к системному хранилищу секретов.') from exc
    if result.returncode:
        if 'No such secret' in result.stderr or 'not found' in result.stderr.lower():
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
