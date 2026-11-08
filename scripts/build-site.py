#!/usr/bin/env python3
"""Build the project web page (GitHub Pages) from README.md, CHANGELOG.md and VERSION.

The page is regenerated on every push, so it never drifts from the docs.
Usage: python3 scripts/build-site.py [output-dir]   (default: build/site)
"""
import html
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/ivshalenko/codex-steamdeck'


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    def image(match):
        alt = html.escape(html.unescape(match.group(1)), quote=True)
        url = html.unescape(match.group(2))
        if not re.match(r'https?://', url) and (url.startswith('/') or '..' in Path(url).parts or ':' in url):
            return match.group(0)
        return f'<img src="{html.escape(url, quote=True)}" alt="{alt}" loading="lazy">'
    text = re.sub(r'!\[([^\]]*)\]\(([^)\s]+)\)', image, text)
    def link(match):
        url = html.unescape(match.group(2))
        if not re.match(r'(https?://|#|mailto:)', url):
            url = f'{REPO}/blob/main/{url}'  # relative repo links work from the web page too
        return f'<a href="{html.escape(url, quote=True)}">{match.group(1)}</a>'
    text = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', link, text)
    return re.sub(r'&lt;(https?://[^&\s]+)&gt;', r'<a href="\1">\1</a>', text)


def slug(text):
    return re.sub(r'[^\w]+', '-', re.sub(r'<[^>]+>', '', text).lower()).strip('-') or 'section'


def markdown(source, shift=0):
    """Small Markdown subset with escaped source HTML, images and pipe tables."""
    out, paragraph, items, kind, lines = [], [], [], None, iter(source.splitlines())
    table = []
    def flush_table():
        if not table:
            return
        rows = [[cell.strip() for cell in row.strip().strip('|').split('|')] for row in table]
        head = '<thead><tr>' + ''.join(f'<th>{inline(cell)}</th>' for cell in rows[0]) + '</tr></thead>'
        body = []
        for row in rows[1:]:
            if all(re.fullmatch(r':?-{3,}:?', cell) for cell in row):
                continue
            body.append('<tr>' + ''.join(f'<td>{inline(cell)}</td>' for cell in row) + '</tr>')
        out.append('<table>' + head + '<tbody>' + ''.join(body) + '</tbody></table>')
        table.clear()
    def flush():
        nonlocal paragraph, items, kind
        if paragraph:
            out.append('<p>' + inline(' '.join(paragraph)) + '</p>'); paragraph = []
        if items:
            out.append(f'<{kind}>' + ''.join(f'<li>{inline(item)}</li>' for item in items) + f'</{kind}>'); items = []
    for line in lines:
        if line.startswith('|'):
            if not table:
                flush()
            table.append(line)
            continue
        flush_table()
        if line.startswith('```'):
            flush(); block = []
            for code in lines:
                if code.startswith('```'):
                    break
                block.append(code)
            out.append('<pre><code>' + html.escape('\n'.join(block)) + '</code></pre>'); continue
        heading = re.match(r'(#{1,4}) (.+)', line)
        bullet = re.match(r'[-*] (.+)', line)
        numbered = re.match(r'\d+\. (.+)', line)
        if heading:
            flush(); level = min(6, len(heading.group(1)) + shift)
            out.append(f'<h{level} id="{slug(heading.group(2))}">{inline(heading.group(2))}</h{level}>')
        elif bullet or numbered:
            new_kind = 'ul' if bullet else 'ol'
            if items and kind != new_kind:
                flush()
            if paragraph:
                flush()
            kind = new_kind; items.append((bullet or numbered).group(1))
        elif not line.strip():
            flush()
        elif items and line.startswith('  '):
            items[-1] += ' ' + line.strip()
        else:
            if items:
                flush()
            paragraph.append(line.strip())
    flush_table()
    flush()
    return '\n'.join(out)


def first_changelog_section(text):
    match = re.search(r'^## (.+?)\n(.*?)(?=^## |\Z)', text, re.S | re.M)
    return (match.group(1), match.group(2)) if match else ('', '')


PAGE = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Deck AI for Steam Deck</title>
<meta name="description" content="Multi-provider AI chat for Steam Deck: desktop app and Decky Loader plugin.">
<link rel="icon" href="deck-ai.png">
<meta property="og:title" content="Deck AI — Your AI. Right on Deck.">
<meta property="og:image" content="https://raw.githubusercontent.com/ivshalenko/codex-steamdeck/main/docs/brand/social.png">
<meta name="twitter:card" content="summary_large_image">
<style>
:root{{color-scheme:dark;--bg:#0b1119;--fg:#f1f7fb;--muted:#a8bdce;--card:#162330;--line:#304252;--accent:#a8e1fa;--code:#101c28}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:880px;margin:0 auto;padding:0 16px 64px}}header{{text-align:center;padding:48px 0 24px}}
header img{{width:100%;height:auto}}.sr-only{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}}h1{{font-size:2rem;margin:12px 0 4px}}.tag{{color:var(--muted);margin:0 0 20px}}
.buttons{{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}}
.button{{display:inline-block;padding:10px 18px;border-radius:6px;border:1px solid var(--line);color:var(--fg);text-decoration:none;background:var(--card)}}
.button.primary{{background:var(--accent);border-color:var(--accent);color:#0b1119}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 20px 14px;margin:20px 0}}
h2{{margin:24px 0 8px;font-size:1.35rem}}h3{{font-size:1.1rem}}a{{color:var(--accent)}}
pre{{background:var(--code);border:1px solid var(--line);border-radius:6px;padding:12px;overflow-x:auto;font-size:.9rem}}
code{{background:var(--code);border-radius:4px;padding:1px 5px;font-size:.92em}}pre code{{background:none;padding:0}}
img{{max-width:100%;height:auto}}table{{display:block;width:100%;border-collapse:collapse;overflow-x:auto;margin:20px 0}}th,td{{padding:12px;border:1px solid var(--line);text-align:left;vertical-align:top}}th{{background:var(--code)}}td img{{min-width:160px}}
nav{{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin:8px 0 0;font-size:.95rem}}footer{{text-align:center;color:var(--muted);font-size:.9rem;margin-top:40px}}
</style></head><body><main>
<header><img src="docs/brand/hero.svg" alt="Deck AI — Your AI. Right on Deck."><h1 class="sr-only">Deck AI for Steam Deck</h1>
<p class="tag">Chat with Codex, Claude, DeepSeek or any OpenAI-compatible AI — in Gaming Mode and on the desktop · version {version}</p>
<div class="buttons"><a class="button primary" href="install/">Get the installer</a><a class="button" href="{repo}">GitHub</a></div>
<nav><a href="#quick-start">Quick start</a><a href="#documentation">Documentation</a><a href="#whats-new">What's new</a></nav></header>
<section class="card" id="quick-start"><h2>Quick start</h2>
<p>On Steam Deck, switch to Desktop Mode, open <a href="install/">the download page</a> and download the setup ZIP. Extract it, open <strong>Install Deck AI</strong> inside the extracted folder, confirm the SteamOS launch prompt and choose Automatic. English and Russian are available. The app and official Codex are included. Installing a missing Decky Loader and signing in still need internet.</p>
<p>Advanced manual installation from a source checkout:</p>
<pre><code>git clone {repo}.git
cd codex-steamdeck
./install.sh --decky</code></pre>
<p>The manual script installs the desktop app and plugin; install and sign into Codex separately first. <a href="{repo}/blob/main/docs/QUICKSTART.md">Full setup guide</a>.</p>
<p>Control the Deck from a Mac or PC: <code>python3 scripts/deck-remote.py steamdeck setup DECK_ADDRESS</code> — see "Notifications, remote tasks and files" below.</p></section>
<section class="card" id="documentation"><h2>Documentation</h2>{readme}</section>
<section class="card" id="whats-new"><h2>What's new — {changelog_title}</h2>{changelog}</section>
<footer>Apache-2.0 · Created by ivshalenko · <a href="{repo}/blob/main/LICENSE">License</a> · generated from the repository on every push</footer>
</main></body></html>
'''


DOWNLOAD_PAGE = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Install Deck AI · Steam Deck</title><meta name="description" content="Download the Deck AI graphical installer for Steam Deck. English and Russian. Download, extract, open.">
<link rel="icon" href="../deck-ai.png"><style>
:root{color-scheme:dark;--bg:#0b1119;--fg:#f1f7fb;--muted:#a8bdce;--card:#162330;--line:#304252;--accent:#a8e1fa}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.55 system-ui,sans-serif}main{max-width:1000px;margin:auto;padding:22px 28px 45px}nav{display:flex;justify-content:space-between;align-items:center;gap:20px}a{color:var(--accent)}nav a{text-decoration:none}button{font:inherit;color:var(--fg);border:1px solid var(--line);border-radius:10px;padding:8px 15px;background:var(--card);cursor:pointer}button[aria-pressed=true]{color:var(--bg);background:var(--accent)}header{padding:30px 0 20px}header img{width:100%;max-height:210px}h1{font-size:clamp(30px,5vw,45px);line-height:1.12;margin:25px 0 14px;letter-spacing:-1px}p{margin:12px 0}.muted{color:var(--muted)}.download{display:inline-flex;align-items:center;gap:15px;padding:17px 27px;margin-top:12px;background:var(--accent);border-radius:13px;color:var(--bg);font-size:21px;font-weight:700;text-decoration:none;min-height:62px}.meta{font-size:14px}.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:24px 0}.step{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px}.number{font-size:14px;color:var(--accent);letter-spacing:2px}h2{font-size:21px;margin:12px 0 6px}.step p{font-size:15px;color:var(--muted)}.note{border-left:3px solid var(--accent);padding:4px 18px;margin:20px 0;color:var(--muted)}details{border-top:1px solid var(--line);padding:16px 0;font-size:15px}summary{cursor:pointer;color:var(--fg)}code{overflow-wrap:anywhere;font-size:13px}footer{display:flex;justify-content:space-between;gap:15px;flex-wrap:wrap;margin-top:26px;color:var(--muted);font-size:14px}[hidden]{display:none!important}:focus-visible{outline:3px solid var(--accent);outline-offset:5px}@media(max-width:650px){main{padding:18px}.steps{grid-template-columns:1fr}header{padding-top:20px}.download{width:100%;justify-content:center}h1{font-size:34px}}
</style></head><body><main>
<nav><a href="../">← Deck AI</a><div aria-label="Language"><button id="en" aria-pressed="true">English</button> <button id="ru" aria-pressed="false">Русский</button></div></nav>
<header><img src="../docs/brand/installer.svg" alt="Deck AI · Steam Deck">
<h1 data-en="Your Deck. Ready for AI." data-ru="Ваш Deck готов к ИИ.">Your Deck. Ready for AI.</h1>
<p class="muted" data-en="Desktop app and Gaming Mode plugin. One graphical setup, in your language." data-ru="Приложение и плагин Gaming Mode. Один графический установщик на вашем языке.">Desktop app and Gaming Mode plugin. One graphical setup, in your language.</p>
<a class="download" id="download" href="@FILE@" download="@FILE@"><span aria-hidden="true">↓</span><span data-en="Download for Steam Deck" data-ru="Скачать для Steam Deck">Download for Steam Deck</span></a>
<p class="meta muted">@VERSION@ · @SIZE@ MB · ZIP · SteamOS · English / Русский</p></header>
<div class="steps">
<section class="step"><span class="number">01</span><h2 data-en="Download" data-ru="Скачайте">Download</h2><p data-en="On the Deck, switch to Desktop Mode and press the download button above. Open the saved ZIP from Downloads." data-ru="На Deck перейдите в режим рабочего стола и нажмите кнопку выше. Откройте скачанный ZIP из папки «Загрузки».">On the Deck, switch to Desktop Mode and press the download button above. Open the saved ZIP from Downloads.</p></section>
<section class="step"><span class="number">02</span><h2 data-en="Extract" data-ru="Распакуйте">Extract</h2><p data-en="Choose Extract in the archive window. Keep all files together in the Deck AI Setup folder. Open that folder in Dolphin." data-ru="В окне архива нажмите «Извлечь». Сохраните все файлы вместе в папке Deck AI Setup. Откройте эту папку в Dolphin.">Choose Extract in the archive window. Keep all files together in the Deck AI Setup folder. Open that folder in Dolphin.</p></section>
<section class="step"><span class="number">03</span><h2 data-en="Open the installer" data-ru="Запустите установщик">Open the installer</h2><p data-en="Open Install Deck AI inside that folder. Confirm the SteamOS launch prompt, choose your language, then Automatic. Sign into your account when setup finishes." data-ru="Откройте Install Deck AI внутри папки. Подтвердите запуск SteamOS, выберите «Русский», затем «Автоматически». После установки войдите в свой аккаунт.">Open Install Deck AI inside that folder. Confirm the SteamOS launch prompt, choose your language, then Automatic. Sign into your account when setup finishes.</p></section>
</div>
<p class="note" data-en="The app and official Codex are already in the ZIP. Internet is required for a missing Decky Loader and account sign-in. SteamOS may ask you to confirm launch and enter your own administrator password in a separate terminal." data-ru="Приложение и официальный Codex уже внутри ZIP. Интернет нужен для отсутствующего Decky Loader и входа в аккаунт. SteamOS может запросить подтверждение запуска и ваш пароль администратора в отдельном терминале.">The app and official Codex are already in the ZIP. Internet is required for a missing Decky Loader and account sign-in. SteamOS may ask you to confirm launch and enter your own administrator password in a separate terminal.</p>
<details><summary data-en="Already have an older version?" data-ru="Уже установлена старая версия?">Already have an older version?</summary><p data-en="Close the older installer and run this setup. Existing chats and settings are kept. Do not delete your installed app or reinstall SteamOS." data-ru="Закройте старый установщик и запустите этот. Чаты и настройки сохранятся. Удалять приложение и переустанавливать SteamOS не нужно.">Close the older installer and run this setup. Existing chats and settings are kept. Do not delete your installed app or reinstall SteamOS.</p></details>
<details><summary data-en="Download verification" data-ru="Проверка загрузки">Download verification</summary><p>SHA-256: <code id="checksum">@SHA256@</code></p><p data-en="The launcher checks the included app archive before opening setup. The included official Codex package is checked independently." data-ru="Файл запуска проверяет архив приложения перед открытием мастера. Включённый официальный пакет Codex проверяется отдельно.">The launcher checks the included app archive before opening setup. The included official Codex package is checked independently.</p></details>
<footer><span data-en="Free · Preview release · Own AI account required" data-ru="Бесплатно · Предварительная версия · Нужен свой аккаунт ИИ">Free · Preview release · Own AI account required</span><a href="https://github.com/ivshalenko/codex-steamdeck">GitHub</a><a id="guide" href="https://github.com/ivshalenko/codex-steamdeck/blob/main/docs/QUICKSTART.md" data-en="Full guide" data-ru="Полная инструкция">Full guide</a></footer>
</main><script>
function language(code){document.documentElement.lang=code;document.querySelectorAll('[data-en]').forEach(node=>node.textContent=node.dataset[code]);['en','ru'].forEach(value=>document.getElementById(value).setAttribute('aria-pressed',String(value===code)));document.getElementById('guide').href='https://github.com/ivshalenko/codex-steamdeck/blob/main/docs/QUICKSTART'+(code==='ru'?'.ru':'')+'.md';}
document.getElementById('en').addEventListener('click',()=>language('en'));document.getElementById('ru').addEventListener('click',()=>language('ru'));if(new URLSearchParams(location.search).get('lang')==='ru')language('ru');
</script></body></html>'''

def fetch_installer(root,destination):
    sys.path.insert(0,str(root))
    import updates
    value=(Path(root)/'VERSION').read_text().strip();name='Deck-AI-Setup-'+value+'.zip'
    release,_=updates.request_json(updates.API+'/releases/tags/v'+value)
    if release.get('tag_name')!='v'+value or release.get('draft') or not release.get('published_at'):raise ValueError('Installer release is not published.')
    matches=[asset for asset in release.get('assets',[]) if asset.get('name')==name]
    if len(matches)!=1:raise ValueError('Published installer ZIP is missing or duplicated.')
    asset=matches[0];url=updates.WEB+'/releases/download/v'+value+'/'+name;digest=asset.get('digest','')
    if asset.get('browser_download_url')!=url or not isinstance(digest,str) or not re.fullmatch(r'sha256:[0-9a-f]{64}',digest):raise ValueError('Unexpected installer asset metadata.')
    target=Path(destination)/name;target.parent.mkdir(parents=True,exist_ok=True)
    updates.download(url,target,300_000_000,digest[7:]);return target

def build(root=ROOT, out_dir=None,installer=None):
    if installer is None:raise ValueError('A verified installer ZIP is required. Pass --release-installer or --installer FILE.')
    root = Path(root)
    out = Path(out_dir) if out_dir else root/'build'/'site'
    out.mkdir(parents=True, exist_ok=True)
    readme = (root/'README.md').read_text()
    body = re.sub(r'^!\[[^\]]*\]\(docs/brand/hero\.svg\)\n', '', readme, count=1)
    body = re.sub(r'^# .+\n', '', body, count=1)           # the page has its own title
    title, changes = first_changelog_section((root/'CHANGELOG.md').read_text())
    page = PAGE.format(version=(root/'VERSION').read_text().strip(), repo=REPO, readme=markdown(body, shift=0),
                       changelog_title=html.escape(title), changelog=markdown(changes))
    (out/'index.html').write_text(page)
    if installer is not None:
        installer=Path(installer);version=(root/'VERSION').read_text().strip();name='Deck-AI-Setup-'+version+'.zip'
        if installer.name!=name:raise ValueError('Installer ZIP version differs from the page.')
        folder=out/'install';folder.mkdir(exist_ok=True);shutil.copyfile(installer,folder/name)
        data=installer.read_bytes();digest=hashlib.sha256(data).hexdigest()
        download=DOWNLOAD_PAGE.replace('@VERSION@',html.escape(version)).replace('@FILE@',name).replace('@SIZE@',f'{len(data)/1048576:.1f}').replace('@SHA256@',digest)
        (folder/'index.html').write_text(download)
        (folder/(name+'.sha256')).write_text(digest+'  '+name+'\n')
        # A permanent download address; each release points it at its verified ZIP.
        short=out/'d';short.mkdir(exist_ok=True)
        target='../install/'+name
        (short/'index.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0;url='+target+'"><title>Download Deck AI</title></head><body><p><a href="'+target+'" download>Download Deck AI / Скачать Deck AI</a></p></body></html>')
    shutil.copy(root/'deck-ai.png', out/'deck-ai.png')
    for folder in ('brand', 'images', 'media/screenshots', 'media/en'):
        source = root/'docs'/folder
        if source.is_dir():
            shutil.copytree(source, out/'docs'/folder, dirs_exist_ok=True)
    (out/'.nojekyll').write_text('')
    return out/'index.html'


if __name__ == '__main__':
    import argparse,tempfile
    parser=argparse.ArgumentParser();parser.add_argument('output',nargs='?');parser.add_argument('--release-installer',action='store_true');parser.add_argument('--installer',type=Path);args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='deck-ai-site-') as temporary:
        installer=fetch_installer(ROOT,temporary) if args.release_installer else args.installer
        print('Built',build(ROOT,args.output,installer))
