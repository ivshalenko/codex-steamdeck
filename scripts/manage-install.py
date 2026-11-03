#!/usr/bin/env python3
"""Allowlisted installation/update; uninstall never removes chats or models."""
import argparse,hashlib,json,os,shlex,shutil,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'decky'))
from runtime_paths import resolve_app_dir
ROOT_FILES=('app.py', 'install.sh', 'chat_media.py', 'backend.py', 'providers.py', 'ui_extras.py', 'speech_accuracy.py', 'deck_share.py', 'speech-languages.json', 'style.css', 'themes.json', 'deck-ai.png', 'requirements.txt', 'requirements-speech.txt', 'VERSION', 'README.md', 'CHANGELOG.md', 'SECURITY.md', 'uninstall.sh', 'message_blocks.py', 'language_support.py', 'language_settings.py', 'remote_access.py')
PLUGIN_FILES=('THIRD_PARTY_NOTICES.txt','main.py','bridge.py','runtime_paths.py','plugin.json','package.json','deck-ai.png')
SCRIPTS=('backup-state.py', 'deck-remote.py', 'download-models.sh', 'deck-ai-steam', 'check-environment.py', 'manage-install.py', 'configure-steam-input.py', 'package-plugin.py', 'install-plugin.py', 'install-decky.sh', 'setup.py', 'connect-deck.py', 'install-codex.py')


def source_files(source):
    source=Path(source)
    paths=[Path(x) for x in ROOT_FILES]+[Path('decky')/x for x in PLUGIN_FILES]+[Path('scripts')/x for x in SCRIPTS]
    for legal in ('LICENSE','NOTICE'):
        if (source/legal).is_file():paths.append(Path(legal))
        if (source/'decky'/legal).is_file():paths.append(Path('decky')/legal)
    paths.extend(p.relative_to(source) for p in (source/'decky/vendor').glob('*') if p.is_file() and p.name in ('websockets-15.0.1-py3-none-any.whl','LICENSE-websockets.txt'))
    paths.extend(p.relative_to(source) for p in (source/'decky/dist').rglob('*') if p.is_file() and p.suffix!='.map')
    if not (source/'decky/dist/index.js').is_file():raise ValueError('Missing Decky build. Run npm ci && npm test in decky first.')
    for rel in paths:
        if not (source/rel).is_file():raise ValueError('Missing release file: '+str(rel))
        if (source/rel).is_symlink():raise ValueError('Release source must not contain symlinks: '+str(rel))
    return sorted(set(paths))


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def install(source,home=None):
    source=Path(source).resolve();home=Path(home) if home is not None else Path.home();app=resolve_app_dir(home)
    files=source_files(source);app.mkdir(parents=True,exist_ok=True)
    contents={app/rel:((source/rel).read_bytes(),0o755 if str(rel).startswith('scripts/') else 0o644) for rel in files}
    launcher='#!/usr/bin/env bash\n# Deck AI managed launcher\nset -euo pipefail\nAPP_DIR='+shlex.quote(str(app))+'''\nif [[ "${1:-}" == "--version" ]]; then cat "$APP_DIR/VERSION"; exit 0; fi
if [[ "${1:-}" == "--check" ]]; then exec "$APP_DIR/venv/bin/python" "$APP_DIR/scripts/check-environment.py"; fi
exec "$APP_DIR/venv/bin/python" "$APP_DIR/app.py" "$@"
'''
    for name in ('deck-ai','codex-steamdeck'):contents[home/'.local/bin'/name]=(launcher.encode(),0o755)
    contents[home/'.local/bin/deck-ai-uninstall']=(('#!/usr/bin/env bash\n# Deck AI managed launcher\nexec python3 '+shlex.quote(str(app/'scripts/manage-install.py'))+' uninstall '+shlex.quote(str(app))+'\n').encode(),0o755)
    contents[home/'.local/bin/deck-ai-steam']=((source/'scripts/deck-ai-steam').read_bytes(),0o755)
    icon=home/'.local/share/icons/hicolor/256x256/apps/deck-ai.png';contents[icon]=((source/'deck-ai.png').read_bytes(),0o644)
    executable=str(home/'.local/bin/deck-ai').replace('\\','\\\\').replace('"','\\"').replace('%','%%')
    desktop=f'[Desktop Entry]\nType=Application\nName=Deck AI\nComment=AI assistant for Steam Deck\nExec="{executable}"\nIcon=deck-ai\nTerminal=false\nCategories=Utility;Accessibility;\n'
    contents[home/'.local/share/applications/codex-steamdeck.desktop']=(desktop.encode(),0o644)
    manifest={'version':(source/'VERSION').read_text().strip(),'files':{str(path.relative_to(home)):hashlib.sha256(data).hexdigest() for path,(data,mode) in contents.items()}}
    contents[app/'install-manifest.json']=((json.dumps(manifest,indent=2)+'\n').encode(),0o600)
    applied=[]
    with tempfile.TemporaryDirectory(prefix='.deck-ai-install-',dir=app.parent) as directory:
        staging=Path(directory);saved={}
        try:
            for i,(target,(data,mode)) in enumerate(contents.items()):
                if target.is_symlink():raise ValueError('Refusing to replace a symlink: '+str(target))
                temporary=staging/str(i);temporary.write_bytes(data);temporary.chmod(mode)
                if target.exists():
                    old=staging/(str(i)+'.old');shutil.copy2(target,old);saved[target]=old
                target.parent.mkdir(parents=True,exist_ok=True);os.replace(temporary,target);applied.append(target)
        except Exception:
            for target in reversed(applied):
                if target in saved:os.replace(saved[target],target)
                else:target.unlink(missing_ok=True)
            raise
    return app


def uninstall(home=None):
    home=Path(home) if home is not None else Path.home();app=resolve_app_dir(home);manifest=app/'install-manifest.json'
    if not manifest.is_file():raise ValueError('No managed installation manifest. No files were removed.')
    entries=json.loads(manifest.read_text())['files'];allowed=[app,home/'.local/bin',home/'.local/share/applications',home/'.local/share/icons/hicolor/256x256/apps']
    candidates=[]
    for relative,expected in entries.items():
        target=home/relative
        if Path(relative).is_absolute() or '..' in Path(relative).parts or not any(target.is_relative_to(root) for root in allowed):raise ValueError('Invalid installation manifest path')
        external={home/'.local/bin'/name for name in ('deck-ai','deck-ai-uninstall','codex-steamdeck','deck-ai-steam')}
        external.update([home/'.local/share/applications/codex-steamdeck.desktop',home/'.local/share/icons/hicolor/256x256/apps/deck-ai.png'])
        if target.is_relative_to(app):
            rel=target.relative_to(app)
            owned=str(rel) in ROOT_FILES or str(rel) in ('LICENSE','NOTICE','decky/LICENSE','decky/NOTICE') or rel in {Path('decky')/x for x in PLUGIN_FILES} or rel in {Path('scripts')/x for x in SCRIPTS} or rel.is_relative_to(Path('decky/dist')) or (rel.parent==Path('decky/vendor') and rel.name in ('websockets-15.0.1-py3-none-any.whl','LICENSE-websockets.txt'))
            if not owned or not target.resolve().is_relative_to(app.resolve()):raise ValueError('Manifest refers to user data or an external path')
        elif target not in external:raise ValueError('Unexpected external installation file')
        if target.is_symlink():raise ValueError('Refusing to remove symlink: '+str(target))
        # Never erase locally edited or user-created files.
        if target.is_file() and digest(target)==expected:candidates.append(target)
    for target in candidates:target.unlink()
    manifest.unlink();return app


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['validate','install','uninstall']);parser.add_argument('source',type=Path);args=parser.parse_args()
    try:
        if args.action=='validate':source_files(args.source)
        elif args.action=='install':print(install(args.source))
        else:print('Removed managed app files. Chats, settings, models and Python environment were preserved in',uninstall())
    except (OSError,ValueError,KeyError) as exc:parser.exit(1,str(exc)+'\n')
