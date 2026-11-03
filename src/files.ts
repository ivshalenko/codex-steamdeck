export function joinPath(folder:string,name:string){return folder.replace(/\/+$/,"")+"/"+name.replace(/\/$/,"");}
export function parentPath(path:string){const trimmed=path.replace(/\/+$/,"");const cut=trimmed.lastIndexOf("/");return cut<=0?"/":trimmed.slice(0,cut);}
export function isFolder(entry:string){return entry.endsWith("/");}
export function sortEntries(entries:string[]){return [...entries].sort((a,b)=>Number(isFolder(b))-Number(isFolder(a))||a.localeCompare(b));}
