#!/usr/bin/env python3
"""Build localized brand artwork from the approved Steam Deck vector.

SVGs have no remote fonts, scripts or raster dependencies. Rasterize icon.svg
at 512 px for the application and plugin icons when changing the artwork.
"""
from pathlib import Path
import re
from html import escape
ROOT=Path(__file__).resolve().parents[1]
BRAND=ROOT/'docs/brand'
BG='#0b1119';PANEL='#162330';LINE='#304252';TEXT='#f1f7fb';MUTED='#a8bdce';ACCENT='#a8e1fa'
FONT='Arial, Helvetica, sans-serif'
def text(x,y,value,size=18,color=TEXT,weight=400,extra=''):
 return f'<text x="{x}" y="{y}" fill="{color}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" {extra}>{escape(value)}</text>'
def canvas(w,h,title,content):
 return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">Deck AI artwork in midnight blue, ice blue and silver, with the approved Steam Deck illustration.</desc>
<defs><clipPath id="brand-clip"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="24"/></clipPath><linearGradient id="brand-bg" x2="1" y2="1"><stop stop-color="{PANEL}"/><stop offset="1" stop-color="{BG}"/></linearGradient><radialGradient id="brand-halo"><stop stop-color="#63bde9" stop-opacity=".18"/><stop offset="1" stop-color="#63bde9" stop-opacity="0"/></radialGradient></defs>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="24" fill="url(#brand-bg)" stroke="{LINE}"/>
<g clip-path="url(#brand-clip)"><ellipse cx="{w*.82}" cy="{h*.45}" rx="{w*.29}" ry="{h*.8}" fill="url(#brand-halo)"/></g>
{content}</svg>\n'''
def device(x,y,scale=1,angle=-6):
 source=(BRAND/'steam-deck.svg').read_text();inner=re.sub(r'^.*?<title[^>]*>.*?</title>','',source,flags=re.S).rsplit('</svg>',1)[0]
 return f'<g transform="translate({x} {y}) rotate({angle} 200 80) scale({scale})">{inner}</g>'
def write(name,content): (BRAND/name).write_text(content)
def rule(y):return f'<path d="M52 {y}H1148" stroke="{LINE}"/>'
def hero(ru=False):
 title='ИИ под рукой. Прямо на Deck.' if ru else 'Your AI. Right on Deck.'
 content=text(52,48,'ПОМОЩНИК ДЛЯ STEAM DECK' if ru else 'A COMPANION FOR STEAM DECK',12,MUTED,extra='letter-spacing="2.5"')
 content+=text(48,156,'Deck ',92,TEXT,700,extra='letter-spacing="-4"')+text(285,156,'AI',92,ACCENT,700,extra='letter-spacing="-4"')
 content+=text(52,215,title,29 if ru else 33,TEXT,600)+text(52,255,'Общайтесь. Решайте задачи. Играйте.' if ru else 'Chat, fix and control. Keep playing.',18,MUTED)
 content+=device(702,99,1.08)+rule(310)
 labels=['GAMING MODE','РАБОЧИЙ СТОЛ' if ru else 'DESKTOP','MAC / PC REMOTE']
 for x,label in zip((52,228,415),labels):content+=text(x,355,label,13,MUTED,extra='letter-spacing=".7"')
 content+=text(1148,355,'OPEN SOURCE / IVSHALENKO',12,'#7b95a9',extra='text-anchor="end"')
 return canvas(1200,400,'Deck AI — '+title,content)
def installer():
 return canvas(1200,210,'Deck AI installer',text(46,128,'Deck ',78,TEXT,700,extra='letter-spacing="-3"')+text(246,128,'AI',78,ACCENT,700,extra='letter-spacing="-3"')+f'<path d="M382 65V145" stroke="{LINE}"/>'+text(415,103,'STEAMOS',15,MUTED,extra='letter-spacing="2.5"')+text(415,134,'EN / RU',15,ACCENT,extra='letter-spacing="2.5"')+device(756,30,.9))
def install(ru=False):
 title='Скачать Deck AI' if ru else 'Get Deck AI'
 body='Установщик SteamOS · EN / RU' if ru else 'SteamOS installer · EN / RU'
 content=f'<circle cx="48" cy="52" r="22" fill="{ACCENT}"/><path d="M48 40v20m-7-7 7 7 7-7M39 67h18" fill="none" stroke="{BG}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
 content+=text(86,47,title,25,TEXT,700)+text(86,75,body,14,MUTED)
 content+=f'<path d="M542 55h26m-9-9 9 9-9 9" fill="none" stroke="{ACCENT}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
 return canvas(600,108,title,content)
def remote(ru=False):
 content=text(48,43,'КОМПЬЮТЕР → DECK' if ru else 'COMPUTER → DECK',12,ACCENT,extra='letter-spacing="2"')
 content+=f'<rect x="49" y="72" width="242" height="138" rx="9" fill="{BG}" stroke="#718ba1" stroke-width="2"/><path d="M32 222h276l-18 12H50Z" fill="#243c50" stroke="#718ba1"/><path d="m78 108 12 10-12 10m24 0h36" fill="none" stroke="{ACCENT}" stroke-width="3" stroke-linecap="round"/>'
 content+=text(170,174,'Ваш Mac / ПК' if ru else 'Your Mac / PC',22,TEXT,600,extra='text-anchor="middle"')
 content+=text(551,105,'SSH · ВАШ КЛЮЧ' if ru else 'SSH · YOUR KEY',13,ACCENT,extra='text-anchor="middle" letter-spacing="1.4"')
 content+=f'<path d="M367 145h340m-10-8 10 8-10 8M707 164H367m10-8-10 8 10 8" fill="none" stroke="{ACCENT}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
 content+=text(550,203,'ЗАДАЧА / ОТВЕТ' if ru else 'TASK / REPLY',12,MUTED,extra='text-anchor="middle" letter-spacing="1.2"')
 content+=device(767,76,.9,0)+text(948,263,'Codex работает здесь' if ru else 'Codex runs here',18,TEXT,600,extra='text-anchor="middle"')+rule(287)
 content+=text(48,322,'Одна доступная сеть · Оба устройства включены · Вне дома — ваш VPN' if ru else 'One reachable network · Keep both devices awake · Your own VPN away from home',16,MUTED)
 return canvas(1200,350,'Deck AI remote control',content)
def icon():
 return '''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 128 128" role="img" aria-labelledby="title"><title id="title">Deck AI</title><defs><linearGradient id="tile" x2="1" y2="1"><stop stop-color="#162330"/><stop offset="1" stop-color="#0b1119"/></linearGradient><linearGradient id="metal" x2="1" y2="1"><stop stop-color="#dff5ff"/><stop offset="1" stop-color="#718ba1"/></linearGradient></defs><rect x="1" y="1" width="126" height="126" rx="28" fill="url(#tile)" stroke="#304252"/><g fill="none" stroke-linecap="round" stroke-linejoin="round" transform="translate(0 1)"><path d="M31 78 49 96a21 21 0 0 0 30 0l18-18a21 21 0 0 0 0-30L79 30a21 21 0 0 0-30 0L31 48a21 21 0 0 0 0 30Z" stroke="url(#metal)" stroke-width="6.5"/><path d="m42 64 12 12 32-34" stroke="#a8e1fa" stroke-width="8"/><circle cx="94" cy="31" r="5" fill="#dff5ff"/></g></svg>\n'''
def build():
 for ru,suffix in ((False,''),(True,'-ru')):
  write('hero'+suffix+'.svg',hero(ru));write('install'+suffix+'.svg',install(ru));write('remote'+suffix+'.svg',remote(ru))
 write('installer.svg',installer());(ROOT/'icon.svg').write_text(icon())
 write('social.svg',canvas(1200,630,'Deck AI — Your AI. Right on Deck.',text(64,76,'A COMPANION FOR STEAM DECK',15,MUTED,extra='letter-spacing="3"')+text(57,220,'Deck ',122,TEXT,700,extra='letter-spacing="-6"')+text(375,220,'AI',122,ACCENT,700,extra='letter-spacing="-6"')+text(64,291,'Your AI. Right on Deck.',37,TEXT,600)+text(64,338,'Chat, fix and control. Keep playing.',23,MUTED)+device(693,342,1.12)+text(64,560,'GAMING MODE  /  DESKTOP  /  MAC + PC',16,ACCENT,extra='letter-spacing="1.2"')))
 print('Built 8 brand SVGs and icon.svg from the shared Steam Deck master')
if __name__=='__main__':build()
