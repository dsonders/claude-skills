// Card P — Dave's 10 Sep brief applied LIVE to the real admin Parts & Labor card (TD1 fixture RO, admin role, 1440 wide).
// Outputs pb-*.jpg + pb-measure.json into ./real. Reads __tests__/workflow/.env.test in-process; prints no secrets.
import { chromium } from '/Users/davidsonders/ro-bot/app/node_modules/playwright/index.mjs';
import fs from 'fs';
const O='/Users/davidsonders/.claude/skills/groom/phone-board/real';
const ENV = Object.fromEntries(fs.readFileSync('/Users/davidsonders/ro-bot/app/__tests__/workflow/.env.test','utf8').split('\n').filter(l=>l.includes('=')&&!l.trim().startsWith('#')).map(l=>{const i=l.indexOf('=');return [l.slice(0,i).trim(), l.slice(i+1).trim().replace(/^"|"$/g,'')];}));
const BASE = 'https://app.tenthgear.ai'; const KEY = ENV.VITE_FIREBASE_API_KEY;
async function login(role){ const r = await fetch(`https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=${KEY}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:ENV[`E2E_${role}_EMAIL`],password:ENV[`E2E_${role}_PASSWORD`],returnSecureToken:true})}); if(!r.ok) throw new Error('login '+role+' '+r.status); const j=await r.json(); return {token:j.idToken, uid:j.localId, email:j.email}; }
async function api(tok, method, path, body){ const r = await fetch(BASE+path,{method,headers:{Authorization:'Bearer '+tok, ...(body!==undefined?{'Content-Type':'application/json'}:{})},body:body!==undefined?JSON.stringify(body):undefined}); let d=null; try{ d=await r.json(); }catch{} return {status:r.status, data:d}; }
const log = (...a)=>console.log(...a);
const advisor = await login('ADVISOR'), tech = await login('TECH_A'), parts = await login('PARTS'), admin = await login('ADMIN');
let roId = process.env.RO_ID ? Number(process.env.RO_ID) : null; const WIDTH = Number(process.env.WIDTH||1440); const TAG = process.env.TAG || 'pb';
const M = {};
try {
  if (!roId) {
    const stamp = new Date().toISOString().replace(/[:.]/g,'-');
    const veh = await api(advisor.token,'POST','/api/vehicles',{make:'Honda',model:'Pilot',year:2021,vin:`E2E-VIN-${Date.now()}`,color:'Silver',licensePlate:'None',additionalDetails:''}); if (veh.status!==201) throw new Error('vehicle '+veh.status);
    const ro = await api(advisor.token,'POST','/api/repair-orders',{vehicleId:veh.data.id,customerName:'E2E Fixture',customerPhone:'555-0100',status:'open',mileage:84120,createdByRole:'advisor',dealerRoNumber:`E2E-P-${stamp}`,saName:'PJ Macklin',skipPlaceholderIssue:true}); if (ro.status!==201) throw new Error('ro '+ro.status+' '+JSON.stringify(ro.data)); roId = ro.data.id; log('RO', roId);
    const issue = await api(advisor.token,'POST',`/api/repair-orders/${roId}/issues`,{customerComplaint:'Customer states fuel gauge reads empty after fill-up and engine cranks long before starting. Happens most mornings.',category:'recall'}); if (issue.status!==201) throw new Error('issue '+issue.status); const issueId = issue.data.id;
    let r = await api(advisor.token,'PATCH',`/api/repair-orders/${roId}`,{assignedTechnicianId:tech.uid,workflowStatus:'assigned_to_tech'}); if (r.status!==200) throw new Error('assign '+r.status);
    r = await api(tech.token,'PATCH',`/api/issues/${issueId}`,{cause:'Fuel pump module losing prime overnight; sender reads low. Matches recall bulletin.',correction:'Replace fuel pump module and sender per recall; clear codes; verify start and gauge.',laborHours:1.5}); if (r.status>=300) throw new Error('3c '+r.status);
    r = await api(tech.token,'PATCH',`/api/repair-orders/${roId}`,{workflowStatus:'parts_pricing'}); if (r.status!==200) throw new Error('to parts '+r.status);
    r = await api(parts.token,'POST',`/api/repair-orders/${roId}/take-over-parts`); if (r.status>=300) throw new Error('takeover '+r.status);
    r = await api(parts.token,'PATCH',`/api/issues/${issueId}`,{parts:[
      {id:`e2e-p1-${issueId}`,name:'Fuel pump module assembly with integrated level sender (recall kit)',quantity:1,partNumber:'RC-FP-002-KIT-2021-PILOT',price:214.5,inStock:true,partsNote:'Confirm the sender ships in the recall kit — if not, order RC-FS-011 separately',customerApproved:true,deliveryState:'pending'},
      {id:`e2e-p2-${issueId}`,name:'Fuel level sender',quantity:2,partNumber:'RC-FS-011',price:88,inStock:false,customerApproved:true,deliveryState:'pending'}]}); if (r.status>=300) throw new Error('parts '+r.status+' '+JSON.stringify(r.data));
    log('seeded');
  }
  const b = await chromium.launch();
  const ctx = await b.newContext({viewport:{width:WIDTH,height:900}, deviceScaleFactor:2});
  const p = await ctx.newPage();
  await p.goto(BASE+'/api/config');
  await p.evaluate(async ({key, user}) => { await new Promise((res, rej) => { const req = indexedDB.open('firebaseLocalStorageDb', 1); req.onupgradeneeded = () => { req.result.createObjectStore('firebaseLocalStorage', {keyPath:'fbase_key'}); }; req.onsuccess = () => { const db = req.result; const tx = db.transaction('firebaseLocalStorage','readwrite'); tx.objectStore('firebaseLocalStorage').put({fbase_key:`firebase:authUser:${key}:[DEFAULT]`, value:{uid:user.uid,email:user.email,emailVerified:true,isAnonymous:false,providerData:[],stsTokenManager:{refreshToken:'',accessToken:user.token,expirationTime:Date.now()+50*60*1000},createdAt:String(Date.now()),lastLoginAt:String(Date.now()),apiKey:key,appName:'[DEFAULT]'}}); tx.oncomplete = () => { db.close(); res(); }; tx.onerror = () => rej(tx.error); }; req.onerror = () => rej(req.error); }); }, {key: KEY, user: {uid: admin.uid, email: admin.email, token: admin.token}});
  await p.goto(BASE+'/'); await p.waitForTimeout(3000);
  const open = async()=>{ await p.goto(`${BASE}/repair-order/${roId}`); await p.waitForSelector('[data-testid^="advisor-edit-pricing-"]', {timeout: 60000}); await p.waitForTimeout(1500); await p.evaluate(()=>document.fonts.ready);
    await p.evaluate(()=>{ const el=[...document.querySelectorAll('button,div')].find(e=>e.childElementCount<4 && /Hold to make a note/.test(e.textContent||'')); let f=el; while(f && getComputedStyle(f).position!=='fixed') f=f.parentElement; if(f) f.style.display='none'; document.querySelectorAll('button,div').forEach(b=>{ const cs=getComputedStyle(b); if(cs.position==='fixed' && b.getBoundingClientRect().bottom>window.innerHeight-160 && b.getBoundingClientRect().height<200) b.style.display='none'; }); }); };
  const card = async()=>{ const btn = await p.$('[data-testid^="advisor-edit-pricing-"], [data-testid^="advisor-edit-pricing-done-"]'); const h = await p.evaluateHandle((b)=>{ let c=b; while(c && !(c.className||'').includes('bg-gray-300')) c=c.parentElement; return c; }, btn); return h.asElement(); };
  const shoot = async(name)=>{ await p.waitForTimeout(350); const c = await card(); const r = await c.boundingBox(); await c.screenshot({path:`${O}/${TAG}-${name}.jpg`, type:'jpeg', quality:88}); const scroll = await p.evaluate(()=>{ const btn=document.querySelector('[data-testid^="advisor-edit-pricing-"]'); let c=btn; while(c && !(c.className||'').includes('bg-gray-300')) c=c.parentElement; let sw=0; c.querySelectorAll('*').forEach(e=>{ const cs=getComputedStyle(e); if(/auto|scroll/.test(cs.overflowX) && e.scrollWidth>e.clientWidth+1) sw=Math.max(sw,e.scrollWidth-e.clientWidth); }); return sw; }); M[name]={w:Math.round(r.width),h:Math.round(r.height),sidewaysScroll:scroll}; log(name, JSON.stringify(M[name])); };
  // ---- shared override pieces (run in page) ----
  const BUBBLE = `(function(count, color){ const w=document.createElement('span'); w.setAttribute('data-pb','bubble'); w.style.cssText='position:relative;display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;flex:none;color:'+color+';'; w.innerHTML='<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>'; if(count){ const b=document.createElement('span'); b.textContent=String(count); b.style.cssText='position:absolute;top:-4px;right:-5px;min-width:14px;height:14px;padding:0 3px;border-radius:999px;background:#0369a1;color:#fff;font-size:9px;font-weight:700;line-height:14px;text-align:center;font-family:system-ui,sans-serif;'; w.appendChild(b);} return w; })`;
  const HOVERCARD = `(function(anchor, text, card, width){ card.style.position='relative'; const ar=anchor.getBoundingClientRect(), cr=card.getBoundingClientRect(); const d=document.createElement('div'); d.setAttribute('data-pb','hover'); d.style.cssText='position:absolute;z-index:20;left:'+Math.max(8, Math.min(ar.left-cr.left, cr.width-width-8))+'px;top:'+(ar.bottom-cr.top+6)+'px;width:'+width+'px;border-radius:8px;border:1px solid #e2e8f0;background:#fff;box-shadow:0 20px 25px -5px rgba(0,0,0,.1),0 8px 10px -6px rgba(0,0,0,.1);padding:6px 10px;font-size:12px;line-height:1.45;color:#0f172a;white-space:pre-wrap;word-break:break-word;'; d.textContent=text; card.appendChild(d); return d; })`;
  const lockedOverride = async(opts)=>{ await p.evaluate(({BUBBLE, badgeCount})=>{ const mkBubble=eval(BUBBLE);
      const btn=document.querySelector('[data-testid^="advisor-edit-pricing-"]'); let card=btn; while(card && !(card.className||'').includes('bg-gray-300')) card=card.parentElement;
      // 1. "Edit pricing" -> "Edit"
      [...btn.childNodes].forEach(n=>{ if(n.nodeType===3 && /Edit pricing/.test(n.textContent)) n.textContent='Edit'; });
      // 2. the add row goes (default view)
      const add=card.querySelector('input[placeholder="Add a part…"]'); if(add){ let row=add; while(row && !(row.className||'').includes('border-t')) row=row.parentElement; (row||add.closest('div')).style.display='none'; }
      // 3. each ledger row: name (truncates) · # (truncates) · stock badge · bubble · ×qty · $ · ✕ ; the note line under the part goes
      card.querySelectorAll('ul.divide-y > li').forEach(li=>{ const row=li.querySelector('.flex.items-center.gap-2'); if(!row) return; const head=row.firstElementChild; head.style.flexWrap='nowrap'; head.style.minWidth='0'; head.style.gap='8px';
        const name=head.querySelector('.font-semibold'); if(name){ name.style.cssText+='min-width:7rem;flex:1 1 auto;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'; name.setAttribute('data-pb','name'); }
        const num=head.querySelector('.font-mono'); if(num){ num.style.cssText+='flex:0 1 auto;min-width:3.5rem;max-width:8rem;overflow:hidden;white-space:nowrap;'; const txt=[...num.childNodes].find(n=>n.nodeType===3); if(txt){ const s=document.createElement('span'); s.textContent=txt.textContent; s.style.cssText='min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'; s.setAttribute('data-pb','num'); num.replaceChild(s,txt);} }
        const badge=head.querySelector('.rounded-full'); if(badge){ badge.style.flex='none'; }
        const note=li.querySelector('[data-testid="part-row-readonly-note"]'); const has=!!note; if(note) note.style.display='none';
        const bub=mkBubble(has ? (badgeCount ? 1 : 0) : 0, has ? '#0369a1' : '#cbd5e1'); if(!has) bub.setAttribute('data-pb','bubble-empty'); head.appendChild(bub); bub.style.marginLeft='auto';
      });
    }, {BUBBLE, badgeCount: opts.badgeCount}); };
  const editOverride = async(opts)=>{ await p.evaluate(({BUBBLE, badgeCount, showEntry})=>{ const mkBubble=eval(BUBBLE);
      const btn=document.querySelector('[data-testid^="advisor-edit-pricing-done-"]'); let card=btn; while(card && !(card.className||'').includes('bg-gray-300')) card=card.parentElement;
      const wrap=card.querySelector('.min-w-\\[25\\.5rem\\]'); if(!wrap) return; wrap.style.minWidth='0';
      const GRID='minmax(5rem,1fr) 5.5rem 2.75rem 5rem 1.5rem 5rem';
      const hdr=wrap.querySelector(':scope > .grid'); hdr.style.gridTemplateColumns=GRID; const hb=document.createElement('div'); hdr.insertBefore(hb, hdr.children[4]);
      const notes={}; document.querySelectorAll('[data-testid="part-row-readonly-note"]').forEach(()=>{});
      wrap.querySelectorAll('[data-testid^="part-row-name-"]').forEach(inp=>{ const grid=inp.closest('.grid'); grid.style.gridTemplateColumns=GRID; const id=inp.getAttribute('data-testid').replace('part-row-name-',''); const has=/e2e-p1/.test(id); const cell=document.createElement('div'); cell.style.cssText='display:flex;justify-content:center;'; const bub=mkBubble(has ? (badgeCount?1:0) : 0, has ? '#0369a1' : '#cbd5e1'); if(!has) bub.setAttribute('data-pb','bubble-empty'); cell.appendChild(bub); grid.insertBefore(cell, grid.children[4]); });
      // the entry row: hidden at rest, "+ Add part" in its place (parts page pattern); showEntry = after the tap
      const entry=wrap.querySelector('[data-testid^="part-list-add-"]'); if(entry){ const eg=entry.querySelector('.grid'); if(eg){ eg.style.gridTemplateColumns=GRID; const cell=document.createElement('div'); eg.insertBefore(cell, eg.children[4]); }
        if(!showEntry){ entry.style.display='none'; const b=document.createElement('button'); b.setAttribute('data-pb','addpart'); b.type='button'; b.style.cssText='display:inline-flex;align-items:center;gap:6px;margin-top:8px;padding:6px 12px;border-radius:6px;border:1px dashed #d1d5db;background:#fff;color:#0369a1;font-size:14px;font-weight:500;font-family:inherit;'; b.innerHTML='<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>Add part'; wrap.appendChild(b); }
        else { entry.style.borderTop='0'; entry.style.marginTop='6px'; const first=entry.querySelector('input'); if(first){ first.style.borderColor='#7dd3fc'; first.style.boxShadow='0 0 0 2px #e0f2fe'; } const x=document.createElement('button'); x.type='button'; x.setAttribute('aria-label','Cancel adding a part'); x.style.cssText='margin-top:6px;display:inline-flex;align-items:center;gap:4px;color:#6b7280;font-size:12px;background:none;border:0;font-family:inherit;'; x.innerHTML='<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>Cancel'; entry.appendChild(x); }
      }
    }, {BUBBLE, badgeCount: opts.badgeCount, showEntry: !!opts.showEntry}); };
  const hover = async(kind, text)=>{ await p.evaluate(({HOVERCARD, kind, text})=>{ const mk=eval(HOVERCARD); const btn=document.querySelector('[data-testid^="advisor-edit-pricing-"], [data-testid^="advisor-edit-pricing-done-"]'); let card=btn; while(card && !(card.className||'').includes('bg-gray-300')) card=card.parentElement; const a = kind==='bubble' ? card.querySelector('[data-pb="bubble"]') : kind==='name' ? card.querySelector('[data-pb="name"]') : card.querySelector('[data-pb="num"]'); if(a) mk(a, text, card, kind==='bubble'?260:kind==='name'?300:200); }, {HOVERCARD, kind, text}); };
  // ---- TODAY, locked ----
  await open(); await shoot('today-locked');
  // ---- PROPOSED, locked (badge count on) + hovers ----
  await open(); await lockedOverride({badgeCount:true}); await shoot('locked');
  await hover('bubble', 'Confirm the sender ships in the recall kit — if not, order RC-FS-011 separately'); await shoot('locked-hover-note');
  await open(); await lockedOverride({badgeCount:true}); await hover('name', 'Fuel pump module assembly with integrated level sender (recall kit)'); await shoot('locked-hover-name');
  await open(); await lockedOverride({badgeCount:true}); await hover('num', 'RC-FP-002-KIT-2021-PILOT'); await shoot('locked-hover-num');
  await open(); await lockedOverride({badgeCount:false}); await shoot('locked-nocount');
  // ---- TODAY, edit ----
  await open(); await p.click('[data-testid^="advisor-edit-pricing-"]'); await p.waitForSelector('[data-testid^="part-row-name-"]'); await shoot('today-edit');
  // ---- PROPOSED, edit: at rest, after the tap ----
  await open(); await p.click('[data-testid^="advisor-edit-pricing-"]'); await p.waitForSelector('[data-testid^="part-row-name-"]'); await editOverride({badgeCount:true}); await shoot('edit');
  await open(); await p.click('[data-testid^="advisor-edit-pricing-"]'); await p.waitForSelector('[data-testid^="part-row-name-"]'); await editOverride({badgeCount:true, showEntry:true}); await shoot('edit-adding');
  await open(); await p.click('[data-testid^="advisor-edit-pricing-"]'); await p.waitForSelector('[data-testid^="part-row-name-"]'); await editOverride({badgeCount:false}); await shoot('edit-nocount');
  await b.close();
  fs.writeFileSync(`${O}/${TAG}-measure.json`, JSON.stringify({width:WIDTH, roId, shots:M}, null, 1)); log(JSON.stringify(M));
} finally {
  if (roId && !process.env.KEEP) { const c = await api(admin.token,'PATCH',`/api/repair-orders/${roId}`,{workflowStatus:'closed'}); log('closed fixture RO', roId, c.status); }
}
