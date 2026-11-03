// Finger-drag scrolling for the chat, history, queue and settings lists.
// Steam's scroll panels follow the gamepad and wheel; dragging a finger over
// them did nothing, so the drag is translated into scrollTop here.
export type Box={scrollTop:number;scrollHeight:number;clientHeight:number;parentElement:Box|null};
export type Touchy={clientY:number};
export const DRAG_THRESHOLD=6;

export function scrollableFrom(start:Box|null,canScroll:(el:Box)=>boolean,root:Box|null):Box|null{
 for(let el=start;el;el=el.parentElement){
  if(canScroll(el))return el;
  if(el===root)return null;
 }
 return null;
}
export function dragTop(box:Box,startTop:number,startY:number,y:number){
 return Math.max(0,Math.min(box.scrollHeight-box.clientHeight,startTop+(startY-y)));
}
// Pixels per frame to keep scrolling after the finger lifts (simple momentum).
export function decay(velocity:number){const next=velocity*0.94;return Math.abs(next)<0.4?0:next;}

type Listener=(event:any)=>void;
type Target={addEventListener:(name:string,fn:Listener,options?:any)=>void;removeEventListener:(name:string,fn:Listener,options?:any)=>void};
export function attachTouchScroll(root:Target&Box,canScroll:(el:Box)=>boolean,frame:(fn:()=>void)=>void=fn=>setTimeout(fn,16)){
 let box:Box|null=null,startY=0,startTop=0,dragging=false,lastY=0,lastTime=0,velocity=0,alive=true;
 const start:Listener=event=>{
  const touch=event.touches?.[0];
  box=touch&&event.touches.length===1?scrollableFrom(event.target,canScroll,root):null;
  dragging=false;velocity=0;
  if(box&&touch){startY=lastY=touch.clientY;startTop=box.scrollTop;lastTime=Date.now();}
 };
 const move:Listener=event=>{
  const touch=event.touches?.[0];
  if(!box||!touch)return;
  if(!dragging&&Math.abs(startY-touch.clientY)<DRAG_THRESHOLD)return;
  dragging=true;
  const now=Date.now();
  velocity=(lastY-touch.clientY)/Math.max(1,now-lastTime)*16;lastY=touch.clientY;lastTime=now;
  box.scrollTop=dragTop(box,startTop,startY,touch.clientY);
  if(event.cancelable)event.preventDefault(); // stop the native pan so we do not scroll twice
 };
 const end:Listener=()=>{
  const target=box;let speed=dragging?velocity:0;box=null;dragging=false;
  const glide=()=>{
   if(!alive||!target||!speed)return;
   const before=target.scrollTop;
   target.scrollTop=Math.max(0,Math.min(target.scrollHeight-target.clientHeight,before+speed));
   speed=target.scrollTop===before?0:decay(speed);
   if(speed)frame(glide);
  };
  glide();
 };
 root.addEventListener("touchstart",start,{passive:true});
 root.addEventListener("touchmove",move,{passive:false});
 root.addEventListener("touchend",end,{passive:true});
 root.addEventListener("touchcancel",end,{passive:true});
 return()=>{alive=false;root.removeEventListener("touchstart",start);root.removeEventListener("touchmove",move);root.removeEventListener("touchend",end);root.removeEventListener("touchcancel",end);};
}
