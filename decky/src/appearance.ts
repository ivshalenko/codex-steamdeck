// Look and layout choices for the Deck AI panel. Stored per Deck in localStorage.
export type Theme={id:string;name:string;swatch:string};
export const themes:Theme[]=[
 {id:"ocean",name:"Океан",swatch:"#a8e1fa"},
 {id:"graphite",name:"Графит",swatch:"#9aa7b4"},
 {id:"violet",name:"Фиалка",swatch:"#8b6cf0"},
 {id:"forest",name:"Лес",swatch:"#2fa66a"},
 {id:"amber",name:"Янтарь",swatch:"#d99a2b"},
 {id:"rose",name:"Роза",swatch:"#e0577d"},
 {id:"light",name:"Светлая",swatch:"#f2f5f8"},
];
export const densities=[{id:"compact",name:"Компактно"},{id:"normal",name:"Обычно"},{id:"roomy",name:"Просторно"}] as const;
export const bubbleStyles=[{id:"bubbles",name:"Пузыри"},{id:"flat",name:"Строки"},{id:"cards",name:"Карточки"}] as const;
export const layouts=[{id:"classic",name:"Вкладки сверху"},{id:"bottom",name:"Вкладки снизу"},{id:"split",name:"Две колонки"}] as const;
export type Appearance={theme:string;density:string;bubbles:string;layout:string};
export const defaultAppearance:Appearance={theme:"ocean",density:"normal",bubbles:"bubbles",layout:"classic"};
export const appearanceKey="deck-ai-appearance";
const allowed:Record<keyof Appearance,string[]>={theme:themes.map(t=>t.id),density:densities.map(d=>d.id),bubbles:bubbleStyles.map(b=>b.id),layout:layouts.map(l=>l.id)};
// Unknown or damaged values fall back to the defaults, field by field.
export function readAppearance(raw:string|null):Appearance{
 let value:Record<string,unknown>={};
 try{const parsed=JSON.parse(raw||"{}");if(parsed&&typeof parsed==="object")value=parsed;}catch{}
 const result={...defaultAppearance};
 for(const key of Object.keys(allowed) as (keyof Appearance)[]){
  const candidate=value[key];
  if(typeof candidate==="string"&&allowed[key].includes(candidate))result[key]=candidate;
 }
 return result;
}
export function withChoice(current:Appearance,key:keyof Appearance,choice:string):Appearance{
 return allowed[key].includes(choice)?{...current,[key]:choice}:current;
}
// Two-column layout only makes sense where there is room for it.
export function effectiveLayout(layout:string,fullscreen:boolean){return layout==="split"&&!fullscreen?"classic":layout;}
