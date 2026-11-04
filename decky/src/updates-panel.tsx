import {useEffect,useState} from 'react';
import {DialogButton,Dropdown} from '@decky/ui';
import {t} from './i18n';
import {updateStore,updateActive,type UpdateClient} from './updates';
export function UpdatesPanel({client,busy=false}:{client:UpdateClient;busy?:boolean}){
 const [,redraw]=useState(0);useEffect(()=>updateStore.subscribe(()=>redraw(x=>x+1)),[]);
 const state=updateStore.snapshot(),data=state.data,active=updateActive(data),candidate=data?.available;
 const invoke=(action:()=>Promise<import('./updates').UpdateState>)=>void updateStore.request(action).catch(()=>{});
 const phase=data?.job?.phase||'';
 const stages:Record<string,string>={queued:t('Подготовка обновления'),downloading:t('Загрузка и проверка файлов'),quiescing:t('Сохранение черновика и закрытие настольного окна'),installing:t('Установка обновления'),verifying:t('Проверка новой версии'), 'rolling-back':t('Восстановление предыдущей версии'),completed:t('Обновление установлено'),failed:t('Не удалось обновить. Откройте подробности и повторите попытку.')};
 const blocked=updateStore.blocked()||data?.busyDesktop||data?.workBusy;
 return <section className="dai-section dai-updates"><h3>{t('Обновления Deck AI')}</h3>
  <p className="dai-muted">{t('Этот Steam Deck · плагин и установленное настольное приложение')}</p>
  {data&&<p className="dai-muted">{Object.entries(data.installed).map(([name,value])=>(name==='plugin'?t('Плагин'):t('Приложение'))+' '+value).join(' · ')}</p>}
  {active?<><p>{stages[phase]||t('Обновление…')}</p><progress max={1} value={data?.job?.progress||0} style={{width:'100%'}}/><p className="dai-muted">{t('Оставьте Steam и Decky включёнными. Чаты, настройки и модели сохраняются.')}</p></>:<>
   {candidate?<p>{t('Доступна версия {0}',candidate.version)}</p>:<p className="dai-muted">{data?t('Новой совместимой версии пока нет.'):t('Подключение к службе обновлений…')}</p>}
   {data?.job?.phase==='completed'&&<p className="dai-check ok">✓ {t('Обновление установлено')}: {data.job.version}</p>}
   {blocked&&<p className="dai-muted">{t('Завершите задачи и диктовку, сохраните правки и отправьте или уберите вложения перед обновлением.')}</p>}
   {data?.requiresInstaller&&<p>{t('Восстановление требует полного установщика. Откройте релиз на GitHub.')}</p>}
  </>}
  <div className="dai-toolbar">
   <DialogButton className="dai-button" disabled={busy||active||state.requesting||!candidate||!!blocked||!!data?.requiresInstaller} onClick={()=>candidate&&invoke(()=>client.begin(candidate.version,!updateStore.blocked()))}>{t('Обновить одной кнопкой')}</DialogButton>
   <DialogButton className="dai-button" disabled={busy||active||state.requesting||data?.checking} onClick={()=>invoke(client.check)}>{data?.checking?t('Проверяю…'):t('Проверить сейчас')}</DialogButton>
  </div>
  {data&&<>
   <DialogButton className="dai-button" disabled={active||state.requesting} onClick={()=>invoke(()=>client.configure(!data.preferences.automatic,data.preferences.channel))}>{data.preferences.automatic?'☑ ':'☐ '}{t('Автоматически проверять раз в неделю')}</DialogButton>
   <div className="dai-field"><Dropdown menuLabel={t('Канал обновлений')} selectedOption={data.preferences.channel} disabled={active||state.requesting} rgOptions={[
    {data:'automatic',label:t('Автоматически по установленной версии')},{data:'stable',label:t('Стабильные выпуски')},{data:'preview',label:t('Стабильные и предварительные выпуски')}
   ]} onChange={item=>invoke(()=>client.configure(data.preferences.automatic,String(item.data)))}/></div>
   <p className="dai-muted">{t('При автоматическом канале предварительная версия получает новые preview-выпуски, стабильная — только стабильные.')}</p>
  </>}
  {(state.error||data?.checkError||data?.job?.error)&&<details><summary>{t('Подробности проверки или ошибки')}</summary><pre className="dai-snippet">{state.error||data?.job?.error||data?.checkError}</pre></details>}
  {candidate&&<details><summary>{t('Что изменилось в версии {0}',candidate.version)}</summary><p className="dai-muted" style={{whiteSpace:'pre-wrap'}}>{candidate.notes}</p><a href={candidate.url} target="_blank" rel="noreferrer">{t('Открыть релиз на GitHub')}</a></details>}
 </section>;
}
