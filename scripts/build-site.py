#!/usr/bin/env python3
"""Build the project web page (GitHub Pages) from README.md, CHANGELOG.md and VERSION.

The page is regenerated on every push, so it never drifts from the docs.
Usage: python3 scripts/build-site.py [output-dir]   (default: build/site)
"""
import html
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
<div class="buttons"><a class="button primary" href="{repo}/releases/tag/v{version}">Get the installer</a><a class="button" href="{repo}">GitHub</a></div>
<nav><a href="#quick-start">Quick start</a><a href="#documentation">Documentation</a><a href="#whats-new">What's new</a></nav></header>
<section class="card" id="quick-start"><h2>Quick start</h2>
<p>On Steam Deck, switch to Desktop Mode, download <strong>Install-Deck-AI.desktop</strong> from the release above, and open it in Dolphin. Allow execution if asked, follow the wizard and sign into your own ChatGPT account. Automatic setup offers the official Decky Loader installation if it is missing.</p>
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


def build(root=ROOT, out_dir=None):
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
    shutil.copy(root/'deck-ai.png', out/'deck-ai.png')
    for folder in ('brand', 'images', 'media/screenshots', 'media/en'):
        source = root/'docs'/folder
        if source.is_dir():
            shutil.copytree(source, out/'docs'/folder, dirs_exist_ok=True)
    (out/'.nojekyll').write_text('')
    return out/'index.html'


if __name__ == '__main__':
    print('Built', build(ROOT, sys.argv[1] if len(sys.argv) > 1 else None))
