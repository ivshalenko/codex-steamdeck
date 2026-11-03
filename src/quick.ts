export type QuickAction=[label:string,text:string];
export const defaultQuickActions:QuickAction[]=[["Продолжай","Продолжай"],["Покажи diff","Покажи diff последних изменений"],["Запусти тесты","Запусти тесты и покажи результат"],["Объясни ошибку","Объясни последнюю ошибку и предложи исправление"]];
// One phrase per line: "Label | text to send". Without "|" the line is both label and text.
export function parseQuickActions(source:string|null):QuickAction[]{
 if(source===null)return defaultQuickActions;
 const result:QuickAction[]=[];
 for(const line of source.split("\n")){
  const [label,...rest]=line.split("|");
  const name=label.trim(),text=(rest.length?rest.join("|"):label).trim();
  if(name&&text)result.push([name.slice(0,24),text.slice(0,2000)]);
  if(result.length===8)break;
 }
 return result.length?result:defaultQuickActions;
}
export function serializeQuickActions(actions:QuickAction[]){return actions.map(([label,text])=>label===text?label:label+" | "+text).join("\n");}
