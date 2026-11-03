#!/usr/bin/env python3
"""Release metadata and allowlist checks; never dumps suspected secrets."""
import importlib.util,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FORBIDDEN={'node_modules','venv','.venv','__pycache__','.git','state','sessions','logs','cache'}
SECRET_PATTERNS=[re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),re.compile(rb'\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}\b'),re.compile(rb'\bgh[pousr]_[A-Za-z0-9]{30,}\b'),re.compile(rb'\bthk_live_[A-Za-z0-9_-]{20,}\b')]

def source_files(root=ROOT):
    root=Path(root)
    exact={'app.py','chat_media.py','language_support.py','language_settings.py', 'remote_access.py','message_blocks.py','backend.py','providers.py','ui_extras.py','speech_accuracy.py','deck_share.py','speech-languages.json','style.css','themes.json','deck-ai.png','requirements.txt','requirements-speech.txt','VERSION','README.md','CHANGELOG.md','SECURITY.md','LICENSE','NOTICE','install.sh','uninstall.sh','.gitignore'}
    directories={'scripts','tests','.github','docs'}
    plugin_root={'LICENSE','NOTICE','THIRD_PARTY_NOTICES.txt','main.py','bridge.py','runtime_paths.py','README.md','package.json','package-lock.json','plugin.json','rollup.config.mjs','tsconfig.json','deck-ai.png'}
    files=[]
    for path in root.rglob('*'):
        rel=path.relative_to(root)
        if not path.is_file() or any(part in FORBIDDEN for part in rel.parts):continue
        if path.is_symlink():raise ValueError('Symlink in release source: '+str(rel))
        include=str(rel) in exact or (rel.parts[0] in directories and path.suffix in ('.py','.sh','.yml','.yaml','.md','.png','.jpg','.webp')) or str(rel)=='scripts/deck-ai-steam' or (rel.parts[0]=='decky' and ((len(rel.parts)==2 and path.name in plugin_root) or (len(rel.parts)>2 and rel.parts[1] in ('src','tests','dist') and path.suffix in ('.ts','.tsx','.css','.mjs','.js','.png','.svg','.json')))) or str(rel) in ('decky/vendor/websockets-15.0.1-py3-none-any.whl','decky/vendor/LICENSE-websockets.txt','models/README.md')
        if include and path.suffix not in ('.map','.pyc','.pyo'):
            if path.name.startswith('.env') or path.name in ('auth.json','known_hosts','config.toml'):raise ValueError('Personal file in release: '+str(rel))
            if path.stat().st_size>15_000_000:raise ValueError('Unexpected large release file: '+str(rel))
            if any(pattern.search(path.read_bytes()) for pattern in SECRET_PATTERNS):raise ValueError('Credential pattern in release file: '+str(rel))
            files.append(rel)
    return sorted(files)


def check(root=ROOT):
    root=Path(root);version=(root/'VERSION').read_text().strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-(?:rc|beta|alpha)\.\d+)?',version):raise ValueError('Invalid release version')
    for filename in ('package.json','package-lock.json'):
        data=json.loads((root/'decky'/filename).read_text())
        if data['version']!=version:raise ValueError('Version mismatch: '+filename)
    if '-' not in version and not (root/'LICENSE').is_file():raise ValueError('Stable release requires an explicitly selected LICENSE')
    spec=importlib.util.spec_from_file_location('release_install_manager',root/'scripts/manage-install.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.source_files(root)
    files=source_files(root)
    for required in ('speech_accuracy.py','speech-languages.json','decky/runtime_paths.py','install.sh','uninstall.sh','decky/dist/index.js'):
        if Path(required) not in files:raise ValueError('Required release source omitted: '+required)
    return version,files

if __name__=='__main__':
    try:
        version,files=check();print(f'Package check passed: {version}, {len(files)} allowlisted files')
    except (OSError,ValueError,KeyError) as exc:raise SystemExit(str(exc))
