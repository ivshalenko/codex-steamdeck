"""Extract explicit copy targets without executing or interpreting their contents."""
import re

FENCE=re.compile(r'^ {0,3}(`{3,}|~{3,})([^\r\n]*)$')
COMMAND=re.compile(r'^(?:sudo\s+)?(?:env|git|npm|npx|pnpm|yarn|pip|pip3|python|python3|curl|wget|cat|ls|cd|pwd|rg|grep|sed|systemctl|journalctl|echo|printf|flatpak|pacman|apt|apt-get|chmod|chown|bash|sh|source|export|mkdir|cp|mv|docker|podman|cargo|make)(?:\s|$)')
POST_LABELS={'готовый пост','текст поста','пост','готовый текст','текст для публикации','текст для копирования','post text','final post','ready-to-copy text'}
COMMENT_LABELS={'пояснение','пояснения','комментарий','комментарии','примечание','примечания','что изменено','explanation','notes','commentary'}


def heading(line):
    return line.strip().strip('*# ').rstrip(':').strip().casefold()


def is_command(line):
    stripped=line.strip()
    if stripped.startswith('$ '):stripped=stripped[2:]
    return bool(stripped and '<<' not in stripped and COMMAND.match(stripped))


def split_message(text):
    lines=text.splitlines(keepends=True);result=[];plain=[];index=0
    def add(kind,value,language=''):
        if not value.strip():return
        result.append({'kind':kind,'text':value,'language':language})
    def flush():
        if plain:add('text',''.join(plain));plain.clear()
    while index<len(lines):
        line=lines[index];match=FENCE.match(line.rstrip('\r\n'))
        if match:
            flush();marker=match[1];language=match[2].strip();body=[];index+=1
            closing=re.compile(r'^ {0,3}'+re.escape(marker[0])+'{'+str(len(marker))+r',}\s*$')
            while index<len(lines) and not closing.match(lines[index].rstrip('\r\n')):
                body.append(lines[index]);index+=1
            if index<len(lines):index+=1
            value=''.join(body)
            if value.endswith('\r\n'):value=value[:-2]
            elif value.endswith('\n'):value=value[:-1]
            kind='post' if language.lower() in ('text','txt','markdown','md','post') else 'code'
            add(kind,value,language);continue
        if line.lstrip().startswith('>'):
            flush();body=[]
            while index<len(lines) and lines[index].lstrip().startswith('>'):
                value=re.sub(r'^\s*> ?', '', lines[index]);body.append(value);index+=1
            add('quote',''.join(body).rstrip('\r\n'));continue
        if heading(line) in POST_LABELS:
            plain.append(line);flush();index+=1;body=[]
            while index<len(lines) and heading(lines[index]) not in COMMENT_LABELS and not FENCE.match(lines[index].rstrip('\r\n')):
                body.append(lines[index]);index+=1
            add('post',''.join(body).strip('\r\n'));continue
        if is_command(line):
            flush();body=[]
            while index<len(lines):
                current=lines[index].rstrip('\r\n')
                if not body or is_command(current) or body[-1].rstrip().endswith('\\'):
                    body.append(current[2:] if current.startswith('$ ') else current);index+=1
                else:break
            add('command','\n'.join(body),'sh');continue
        # Inline terminal commands become their own copy target. Other inline
        # code (such as filenames) remains part of the explanation.
        matches=[m for m in re.finditer(r'(?<!`)`([^`\n]+)`(?!`)',line) if is_command(m[1])]
        if matches:
            position=0
            for match in matches:
                plain.append(line[position:match.start()]);flush();add('command',match[1],'sh');position=match.end()
            plain.append(line[position:]);index+=1;continue
        plain.append(line);index+=1
    flush()
    return result
