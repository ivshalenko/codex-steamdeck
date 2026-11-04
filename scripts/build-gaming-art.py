#!/usr/bin/env python3
"""Generate Deck AI library artwork from its approved shared Steam Deck master."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('brand',ROOT/'scripts/build-brand.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
OUT=ROOT/'docs/brand/gaming';OUT.mkdir(exist_ok=True)
def save(name,data):(OUT/(name+'.svg')).write_text(data)
save('capsule',b.canvas(600,900,'Deck AI',b.text(80,178,'Deck',112,b.TEXT,700,extra='letter-spacing="-4"')+b.text(352,178,'AI',112,b.ACCENT,700,extra='letter-spacing="-4"')+b.device(50,350,1.25,-8)+'<path d="M68 670H532" stroke="#304252"/>'+b.text(68,730,'CHAT',22,b.ACCENT,600,extra='letter-spacing="2.5"')+b.text(230,730,'FIX',22,b.TEXT,600,extra='letter-spacing="2.5"')+b.text(358,730,'CONTROL',22,b.MUTED,600,extra='letter-spacing="2.5"')))
save('header',b.canvas(920,430,'Deck AI',b.text(48,128,'Deck',82,b.TEXT,700,extra='letter-spacing="-3"')+b.text(249,128,'AI',82,b.ACCENT,700,extra='letter-spacing="-3"')+b.device(421,181,1.1,-6)))
save('hero',b.canvas(3840,1240,'Deck AI Steam library background',b.device(2024,420,3.3,-6)))
save('logo','<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="360" viewBox="0 0 1280 360" role="img" aria-labelledby="title"><title id="title">Deck AI</title>'+b.text(30,270,'Deck',260,b.TEXT,700,extra='letter-spacing="-9"')+b.text(677,270,'AI',260,b.ACCENT,700,extra='letter-spacing="-9"')+'</svg>\n')
print('Built Steam library capsule, header, hero and transparent logo vectors')
