#!/usr/bin/env python3
"""Add a mouse/keyboard default only for Deck AI shortcuts lacking a layout."""
import argparse
from pathlib import Path
import os
import re
import shutil
import struct
import tempfile
import time

TEMPLATE='controller_neptune_wasd.vdf'


def read_shortcuts(data):
    offset=0
    def read():
        nonlocal offset
        result={}
        while offset<len(data):
            kind=data[offset];offset+=1
            if kind==8:return result
            end=data.index(b'\0',offset);key=data[offset:end].decode('utf-8');offset=end+1
            if kind==0:value=read()
            elif kind==1:
                end=data.index(b'\0',offset);value=data[offset:end].decode('utf-8');offset=end+1
            elif kind in (2,3,4,6):value=struct.unpack_from('<I',data,offset)[0];offset+=4
            elif kind==7:value=struct.unpack_from('<Q',data,offset)[0];offset+=8
            else:raise ValueError('Unsupported shortcut record')
            result[key]=value
        raise ValueError('Incomplete shortcut file')
    return read().get('shortcuts',{})


def add_default(text,key):
    tokens=list(re.finditer(r'"(?:\\.|[^"\\])*"|[{}]',text))
    if len(tokens)<3 or tokens[0][0]!='"controller_config"' or tokens[1][0]!='{':raise ValueError('Invalid controller config')
    depth=0;existing=set();end=None
    for index,token in enumerate(tokens[1:],1):
        value=token[0]
        if value=='{':depth+=1
        elif value=='}':
            depth-=1
            if depth==0:
                if index!=len(tokens)-1:raise ValueError('Unexpected trailing config')
                end=token.start()
            if depth<0:raise ValueError('Unbalanced controller config')
        elif depth==1:
            if index+1>=len(tokens) or tokens[index+1][0]!='{':raise ValueError('Invalid controller layout entry')
            existing.add(value[1:-1].casefold())
    if depth or end is None:raise ValueError('Incomplete controller config')
    if key.casefold() in existing:return text
    if any(ch in key for ch in ('"','\\','\n','\r')):raise ValueError('Invalid shortcut name')
    newline='\r\n' if '\r\n' in text else '\n'
    entry='\t"'+key.casefold()+'"'+newline+'\t{'+newline+'\t\t"template"\t\t"'+TEMPLATE+'"'+newline+'\t}'+newline
    return text[:end]+entry+text[end:]


def configure(steam_root):
    steam_root=Path(steam_root)
    if not (steam_root/'controller_base/templates'/TEMPLATE).is_file():return []
    changed=[]
    for shortcut in (steam_root/'userdata').glob('*/config/shortcuts.vdf'):
        try:entries=read_shortcuts(shortcut.read_bytes())
        except (OSError,ValueError,UnicodeError,struct.error):continue
        names=[]
        for item in entries.values():
            if not isinstance(item,dict):continue
            fields={key.casefold():value for key,value in item.items()}
            name=str(fields.get('appname',''))
            if name.casefold()=='deck ai' and 'deck-ai-steam' in str(fields.get('exe','')):names.append(name)
        if not names:continue
        account=shortcut.parent.parent.name
        target=steam_root/'steamapps/common/Steam Controller Configs'/account/'config/configset_controller_neptune.vdf'
        original=target.read_bytes() if target.exists() else b'"controller_config"\n{\n}\n'
        text=original.decode('utf-8-sig')
        for name in names:text=add_default(text,name)
        updated=text.encode('utf-8-sig' if original.startswith(b'\xef\xbb\xbf') else 'utf-8')
        if updated==original:continue
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():shutil.copy2(target,target.with_name(target.name+'.deck-ai-backup-'+str(time.time_ns())))
        descriptor,temporary=tempfile.mkstemp(prefix='.deck-ai-input-',dir=target.parent)
        try:
            with os.fdopen(descriptor,'wb') as stream:stream.write(updated)
            os.replace(temporary,target)
        finally:
            if os.path.exists(temporary):os.unlink(temporary)
        changed.append(target)
    return changed


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--quiet',action='store_true')
    parser.add_argument('--steam-root',default=str(Path.home()/'.local/share/Steam'))
    options=parser.parse_args()
    try:
        changed=configure(options.steam_root)
        if not options.quiet:print('Deck AI mouse/keyboard defaults added:',len(changed),'; existing custom layouts preserved.')
    except (OSError,ValueError) as error:
        if not options.quiet:print('Steam Input layout was not changed:',str(error))
        raise SystemExit(1)
