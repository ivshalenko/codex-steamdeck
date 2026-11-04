import {useEffect,useState} from 'react';
import {callable} from '@decky/api';
import {DialogButton,Navigation} from '@decky/ui';
import {t} from './i18n';
import {Icon} from './icons';
import {updateStore,updateActive} from './updates';
type LibraryState={available:boolean;hasBackup:boolean;appId?:number;version:string;restored?:boolean};
const read=callable<[],LibraryState>('library_status');
const apply=callable<[],LibraryState>('library_apply');
const restore=callable<[],LibraryState>('library_restore');
let operation=false;
const blocker=Symbol('library-artwork');
export function LibraryPanel({disabled=false}:{disabled?:boolean}){
 const [state,setState]=useState<LibraryState|null>(null),[busy,setBusy]=useState(false),[error,setError]=useState(''),[done,setDone]=useState('');
 const [,redraw]=useState(0);
 useEffect(()=>updateStore.subscribe(()=>redraw(x=>x+1)),[]);
 useEffect(()=>{let alive=true;void read().then(value=>{if(alive)setState(value);}).catch(error=>{if(alive)setError(String(error));});return()=>{alive=false;};},[]);
 async function change(revert=false){
  if(operation||disabled||updateActive(updateStore.snapshot().data))return;
  operation=true;updateStore.block(blocker,true);setBusy(true);setError('');setDone('');
  try{setState(await (revert?restore():apply()));setDone(revert?t('Прежние изображения восстановлены.'):t('Оформление Deck AI в библиотеке Steam готово.'));}
  catch(error){setError(String(error));}
  finally{operation=false;updateStore.block(blocker,false);setBusy(false);}
 }
 const blocked=disabled||busy||operation||updateActive(updateStore.snapshot().data);
 return <section className="dai-section dai-library-art"><h3>{t('Deck AI в библиотеке Steam')}</h3>
  <p className="dai-muted">{t('Обложка, широкий баннер, прозрачный логотип и значок в одном стиле. Изменяется только ярлык Deck AI; прежние изображения сохраняются для восстановления.')}</p>
  {state&&!state.available&&<p className="dai-muted">{t('Для ярлыка установите настольное приложение Deck AI полным установщиком.')}</p>}
  <div className="dai-toolbar"><DialogButton className="dai-button" disabled={blocked||!state?.available} onClick={()=>void change()}><Icon name="game"/>{busy?t('Применяю оформление…'):t('Добавить или обновить Deck AI в Steam')}</DialogButton>
   {state?.appId&&<DialogButton className="dai-button" disabled={blocked} onClick={()=>Navigation.Navigate('/library/app/'+state.appId)}>{t('Открыть в библиотеке')}</DialogButton>}
   {state?.hasBackup&&<DialogButton className="dai-button" disabled={blocked} onClick={()=>void change(true)}>{t('Вернуть прежние изображения')}</DialogButton>}
  </div>
  {done&&<p className="dai-check ok" role="status">{done}</p>}
  {error&&<details open><summary>{t('Не удалось изменить оформление')}</summary><pre className="dai-snippet">{error}</pre></details>}
 </section>;
}
