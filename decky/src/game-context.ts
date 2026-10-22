export type GameContext={appId:number;name:string;status:string;details:[string,string][]};
type SteamSources={
 appId?:number;
 overview?:(id:number)=>{display_name?:string}|null;
 player?:()=>{current_game_name?:string;current_game_rich_presence?:string;persona?:{m_gameid?:string;m_mapRichPresence?:Map<string,string>}};
};
const detailKeys=new Set(['status','map','level','chapter','mission','mode','location','gamestatus']);
const clean=(value:unknown,max:number)=>typeof value==='string'?value.replace(/[\u0000-\u001f\u007f]/g,' ').trim().slice(0,max):'';
export function readGameContext(source:SteamSources):GameContext|null{
 try{
  const appId=source.appId;
  if(!appId||!Number.isSafeInteger(appId)||appId<1)return null;
  const name=clean(source.overview?.(appId)?.display_name,160);
  if(!name||/^deck\s*ai$/i.test(name))return null;
  const context:GameContext={appId,name,status:'',details:[]};
  // A missing/outdated friend status must never obscure the running app.
  try{
   const player=source.player?.();
   const matches=player?.persona?.m_gameid===String(appId)||player?.current_game_name===name;
   if(matches&&player){
    context.status=clean(player.current_game_rich_presence,300);
    for(const [key,value] of player.persona?.m_mapRichPresence||[]){
     const text=clean(value,180);
     if(detailKeys.has(key)&&text&&!text.startsWith('#')&&text!==context.status)context.details.push([key,text]);
    }
   }
  }catch{/* Rich Presence is optional. */}
  return context;
 }catch{return null;}
}
export function withGameContext(question:string,game:GameContext|null,enabled:boolean):string{
 return enabled&&game?question+'\n\nИгра: '+game.name:question;
}
export function gameScreenshots<T extends {path:string;when?:number}>(screenshots:T[],game:GameContext|null):T[]{
 if(!game)return [];
 return screenshots.filter(item=>item.path.includes('/760/remote/'+game.appId+'/screenshots/')).sort((a,b)=>(b.when||0)-(a.when||0));
}
