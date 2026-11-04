import type {CSSProperties} from 'react';
const paths={
 chat:'M5 4h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H9l-5 3v-4a2 2 0 0 1-1-1V6a2 2 0 0 1 2-2Z',
 history:'M3 11a9 9 0 1 1 2.5 7M3 4v7h7M12 7v5l3 2',
 settings:'M9 3h6l1 3 3 1 2 5-2 5-3 1-1 3H9l-1-3-3-1-2-5 2-5 3-1 1-3ZM12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z',
 game:'M7 7h10c3 0 5 10 3 12-2 1-4-3-5-3H9c-1 0-3 4-5 3-2-2 0-12 3-12ZM6 11v4m-2-2h4m8-1h.01m3 2h.01',
 microphone:'M9 5a3 3 0 0 1 6 0v7a3 3 0 0 1-6 0V5ZM6 10v2a6 6 0 0 0 12 0v-2M12 18v4m-4 0h8',
 expand:'M9 3H3v6m12-6h6v6M3 15v6h6m6 0h6v-6',
 collapse:'M3 9h6V3m6 0v6h6M3 15h6v6m6 0v-6h6',
 back:'M20 12H4m7-7-7 7 7 7',copy:'M9 9h12v12H9V9ZM5 15H3V3h12v2',
 plus:'M12 4v16M4 12h16',folder:'M3 6h6l2 3h10v11H3V6Z',
 attachment:'m8 12 7-7a4 4 0 0 1 6 6L10 22a6 6 0 0 1-8-8L13 3m-8 14 10-10',
 queue:'M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01',
 refresh:'M20 9a8 8 0 0 0-14-4L3 8m0-5v5h5m-4 7a8 8 0 0 0 14 4l3-3m0 5v-5h-5',
 check:'m5 12 4 4L20 5',warning:'M12 3 2 21h20L12 3Zm0 6v5m0 3h.01',
 stop:'M5 5h14v14H5V5Z',download:'M12 3v12m-5-5 5 5 5-5M4 17v4h16v-4',
};
export type IconName=keyof typeof paths;
export function Icon({name,style}:{name:IconName;style?:CSSProperties}){
 return <svg className="dai-icon" data-dai-icon={name} width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false" style={style}><path d={paths[name]}/></svg>;
}
