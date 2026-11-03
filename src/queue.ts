export type QueueJob={id:string;status:string;text:string;error?:string;threadId?:string;host?:string;createdAt?:number;startedAt?:number;model?:string};
export function queueCounts(jobs:QueueJob[],threadId:string){
 return {waiting:jobs.filter(job=>job.status==='queued').length,current:jobs.filter(job=>job.threadId===threadId&&job.status==='queued').length,other:jobs.filter(job=>job.threadId!==threadId&&job.status==='queued').length};
}
export function queueStatus(job:QueueJob,now=Date.now()){
 const began=job.startedAt??job.createdAt;
 if(job.status==='sending')return began&&now-began*1000>15*60*1000?'Долго выполняется · проверьте чат':'Выполняется';
 return ({queued:'Ожидает отправки',recovering:'Проверяется на сервере',error:'Ошибка'} as Record<string,string>)[job.status]||job.status;
}

export function chatFailures(jobs:QueueJob[],threadId:string,host=""){
 return jobs.filter(job=>job.status==='error'&&job.threadId===threadId&&(job.host||'')===host);
}
