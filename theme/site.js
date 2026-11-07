'use strict';
(() => {
  const lang = document.body.dataset.lang || 'zh';
  const zh = lang === 'zh';
  const supported = ['zh','en','es','ar','hi','ko','vi','fr','bn','pt','sw'];
  const query = new URLSearchParams(location.search);
  // Keep links shared from the older one-page guide usable.
  const preferred = query.get('lang');
  const root = location.pathname === '/';
  let hash = location.hash.slice(1);
  try { hash=decodeURIComponent(hash); } catch { hash=''; }
  const oldSections = {food:'food',events:'events',journal:'home',practical:'',transport:'move',life:'weekend',about:'about',home:'home'};
  const resolvedLang = supported.includes(preferred) ? preferred : lang;
  if (root && /^(place|practical|journal|ride|note|event)\/[a-z0-9-]+$/.test(hash)) {
    location.replace('/'+resolvedLang+'/guides/'+hash+'/'); return;
  }
  if (root && Object.hasOwn(oldSections,hash)) {
    const topic=oldSections[hash];
    location.replace('/'+resolvedLang+'/'+(topic==='home'?'':topic==='about'?'about/':'notes/'+(topic?'?topic='+topic:'')));return;
  }
  if (root && preferred && supported.includes(preferred) && preferred!=='zh') {location.replace('/'+preferred+'/');return;}
  document.getElementById('language')?.addEventListener('change',event=>{ location.href=event.target.value; });

  const input=document.getElementById('search');
  const items=[...document.querySelectorAll('.catalog-item')];
  if(input){
    let topic=query.get('topic') || 'all';
    const buttons=[...document.querySelectorAll('[data-topic]')];
    if(!buttons.some(b=>b.dataset.topic===topic))topic='all';
    input.value=query.get('q') || '';
    const normalize=s=>s.normalize('NFKC').toLocaleLowerCase();
    const apply=()=>{
      const words=normalize(input.value.trim()).split(/\s+/).filter(Boolean);let count=0;
      for(const item of items){const match=(topic==='all'||item.dataset.category===topic)&&words.every(w=>normalize(item.dataset.search).includes(w));item.hidden=!match;if(match)count++;}
      for(const button of buttons)button.setAttribute('aria-pressed',String(button.dataset.topic===topic));
      document.getElementById('results-count').textContent=count+(zh?' 篇笔记':' notes');
      document.getElementById('empty-state').hidden=count>0;
      const url=new URL(location.href);url.searchParams.delete('topic');url.searchParams.delete('q');
      if(topic!=='all')url.searchParams.set('topic',topic);
      if(input.value.trim())url.searchParams.set('q',input.value.trim());
      history.replaceState(null,'',url);
    };
    for(const button of buttons)button.addEventListener('click',()=>{topic=button.dataset.topic;apply();});
    input.addEventListener('input',apply);document.getElementById('search-form').addEventListener('submit',e=>{e.preventDefault();apply();});apply();
  }
  const dateParts=Object.fromEntries(new Intl.DateTimeFormat('en-CA',{timeZone:'America/Chicago',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date()).map(p=>[p.type,p.value]));
  const today=`${dateParts.year}-${dateParts.month}-${dateParts.day}`;
  for(const element of document.querySelectorAll('[data-event-end]')){
    const past=element.dataset.eventState==='past'||Boolean(element.dataset.eventEnd&&element.dataset.eventEnd<today);
    if(element.hasAttribute('data-event-notice'))element.hidden=!past;
    else if(past)element.textContent=zh?'往期回顾':'Past edition';
  }
  document.querySelector('[data-print]')?.addEventListener('click',()=>window.print());
  document.querySelector('[data-copy-url]')?.addEventListener('click',async()=>{
    const status=document.getElementById('copy-status');
    try{await navigator.clipboard.writeText(location.href.split('#')[0]);status.textContent=zh?'链接已复制。':'Link copied.';}
    catch{status.textContent=zh?'暂时无法复制，可复制浏览器中的网址。':'Copy the address from your browser instead.';}
  });
})();
