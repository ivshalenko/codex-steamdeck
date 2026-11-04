import logo from '../deck-ai.png';
import handheld from '../../docs/brand/steam-deck.svg';
export function BrandLogo({size=24}:{size?:number}){
 return <img className="dai-brand-logo" src={logo} alt="Deck AI" width={size} height={size} style={{width:size,height:size,objectFit:'contain',flexShrink:0,borderRadius:Math.round(size*.22)}}/>;
}
export function Handheld(){return <img className="dai-handheld" src={handheld} alt="" aria-hidden="true"/>;}
