"""Bounded local image previews shared by GTK and Decky. Never fetches URLs."""
import base64
import hashlib
from pathlib import Path
import re
import tempfile
from urllib.parse import unquote,urlparse

IMAGE_SUFFIXES={'.png','.jpg','.jpeg','.webp','.gif'}
MAX_BYTES=30_000_000
_CACHE={}
LINK=re.compile(r'!?\[([^\]]*)\]\(<?((?:sandbox:|file:|https?://|/)[^\n]*?)>?\)')


def references(item):
    refs=[]
    for part in item.get('content',[]) or []:
        kind=part.get('type','')
        if kind in ('localImage','image','image_url','input_image','file','localFile','input_file'):
            source=part.get('path') or part.get('url') or part.get('image_url') or part.get('file_url') or part.get('file_path')
            if isinstance(source,dict):source=source.get('url')
            if isinstance(source,str):refs.append((source,part.get('name') or part.get('filename') or ''))
    text=item.get('text','') or '\n'.join(p.get('text','') for p in item.get('content',[]) if p.get('type')=='text')
    for match in LINK.finditer(text):
        source=match.group(2)
        if source.startswith(('sandbox:','file:','/')) or Path(urlparse(source).path).suffix.lower() in IMAGE_SUFFIXES:
            refs.append((source,match.group(1)))
    for source in item.get('images',[]) or []:
        if isinstance(source,str):refs.append((source,''))
    seen=set();result=[]
    for source,name in refs:
        identity=source[len('sandbox:'):] if source.startswith('sandbox:') else source
        if identity.startswith('file:'):identity=unquote(urlparse(identity).path)
        if identity.startswith('/'):identity=str(Path(identity).resolve())
        if identity not in seen:result.append((source,name));seen.add(identity)
    return result[:8]


def display_text(text):
    """Image markup is represented by the thumbnail, not printed as a path."""
    return LINK.sub(lambda match:'' if match.group(0).startswith('!') or Path(urlparse(match.group(2)).path).suffix.lower() in IMAGE_SUFFIXES else match.group(0),text).strip()


def local_path(source):
    if source.startswith('sandbox:'):source=source[len('sandbox:'):]
    if source.startswith('file:'):
        parsed=urlparse(source)
        if parsed.netloc not in ('','localhost'):raise ValueError('Nonlocal file URL')
        source=unquote(parsed.path)
    path=Path(source).expanduser().resolve(strict=True)
    if not path.is_relative_to(Path.home().resolve()) or not path.is_file():raise ValueError('Not a local user file')
    if path.stat().st_size>MAX_BYTES:raise ValueError('Attachment too large')
    return path


def image_preview(source):
    try:
        if source.startswith('data:'):
            if not source.startswith(('data:image/png;base64,','data:image/jpeg;base64,','data:image/webp;base64,','data:image/gif;base64,')) or len(source)>MAX_BYTES*4//3+100:return ''
            data=base64.b64decode(source.split(',',1)[1],validate=True)
            key=hashlib.sha256(data).hexdigest()
        else:
            path=local_path(source)
            if path.suffix.lower() not in IMAGE_SUFFIXES:return ''
            stat=path.stat();key=(str(path),stat.st_mtime_ns,stat.st_size)
            if key in _CACHE:return _CACHE[key]
            data=path.read_bytes()
        if key in _CACHE:return _CACHE[key]
        import gi
        gi.require_version('GdkPixbuf','2.0')
        from gi.repository import GdkPixbuf
        loader=GdkPixbuf.PixbufLoader.new()
        def size_ready(loader,width,height):
            scale=min(1,768/max(width,1),480/max(height,1))
            loader.set_size(max(1,int(width*scale)),max(1,int(height*scale)))
        loader.connect('size-prepared',size_ready)
        loader.write(data);loader.close();pixbuf=loader.get_pixbuf()
        ok,encoded=pixbuf.save_to_bufferv('jpeg',['quality'],['82'])
        if not ok:return ''
        result='data:image/jpeg;base64,'+base64.b64encode(encoded).decode()
        if len(_CACHE)>=48:_CACHE.pop(next(iter(_CACHE)))
        _CACHE[key]=result
        return result
    except Exception:
        return ''


def attachments(item):
    result=[]
    for source,label in references(item):
        preview=image_preview(source)
        name=label or ('Изображение' if source.startswith('data:') else Path(unquote(urlparse(source).path)).name) or 'Вложение'
        if re.fullmatch(r'[0-9a-f]{64}\.(?:png|jpe?g|webp|gif)',name,re.I):name='Изображение'
        result.append({'id':hashlib.sha256(source.encode()).hexdigest()[:20],'name':name[:160],'preview':preview,'available':bool(preview),'kind':'image' if preview or source.startswith('data:image/') or Path(urlparse(source).path).suffix.lower() in IMAGE_SUFFIXES else 'file'})
    return result


def archive_image(source,state):
    """Keep an owned copy so deleting a temporary capture cannot break history."""
    source=local_path(str(source))
    if source.suffix.lower() not in IMAGE_SUFFIXES:raise ValueError('Unsupported attachment')
    data=source.read_bytes()
    digest=hashlib.sha256(data).hexdigest()
    target=Path(state)/'chat-attachments'/(digest+source.suffix.lower())
    target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    if not target.exists():
        with tempfile.NamedTemporaryFile(dir=target.parent,prefix='.image-',delete=False) as stream:
            temporary=Path(stream.name);stream.write(data)
        try:temporary.replace(target)
        finally:temporary.unlink(missing_ok=True)
    return target
