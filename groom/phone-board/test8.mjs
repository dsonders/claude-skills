import { chromium } from '/Users/davidsonders/ro-bot/app/node_modules/playwright/index.mjs';
import fs from 'fs';
const S='/Users/davidsonders/.claude/skills/groom/phone-board';
fs.writeFileSync(S+'/local.html', '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0">' + fs.readFileSync(S+'/grooming-board-phone.html','utf8') + '</body></html>');
const b = await chromium.launch(); const p = await (await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2})).newPage();
const errors=[]; p.on('pageerror', e=>errors.push(String(e)));
// simulate: phone holds a stale local ruling the store no longer has (swept) + one offline ruling; store empty
await p.addInitScript(() => {
  localStorage.setItem('groomphone.v1', JSON.stringify({rulings:{'D2-1':{choice:'A',words:'',at:'2026-09-09T00:00:00Z'}, 'T-1':{choice:'B',words:'',at:'2026-09-09T00:00:00Z',offline:true}}, notes:{}}));
  const docs = {}; const subs = [];
  function snap(coll){ const ds = Object.keys(docs).filter(k=>k.startsWith(coll+'/')).map(k=>({id:k.split('/')[1], exists:true, data:()=>docs[k]})); return {docs:ds, size:ds.length, empty:!ds.length, docChanges:()=>[], metadata:{fromCache:false,hasPendingWrites:false}}; }
  function fire(coll){ subs.filter(s=>s.coll===coll).forEach(s=>setTimeout(()=>s.fn(snap(coll)),30)); }
  const db = { doc(path){ const coll=path.split('/')[0]; return { get: async()=>({exists:!!docs[path], data:()=>docs[path]}), set: async(d)=>{ docs[path]=d; fire(coll); }, delete: async()=>{ delete docs[path]; fire(coll); } }; },
    collection(coll){ return { get: async()=>snap(coll), onSnapshot(fn){ subs.push({coll,fn}); setTimeout(()=>fn(snap(coll)),30); return ()=>{}; } }; } };
  window.__docs = docs; window.claude = { use: async(n)=> n==='db' ? db : null };
});
await p.goto('file://'+S+'/local.html#/'); await p.waitForTimeout(800);
console.log('store after connect', await p.evaluate(()=>Object.keys(window.__docs)));
for (const k of ['Q','P','SA-20b','W']) { await p.goto('file://'+S+'/local.html#/item/'+k); await p.waitForTimeout(500); console.log(k, await p.evaluate(()=>({w: document.documentElement.scrollWidth, stage: document.querySelector('.m-stage-lbl')?.textContent, baked: document.querySelectorAll('.m-dec.baked').length, open: document.querySelectorAll('.m-dec:not(.baked):not(.ruled)').length}))); await p.screenshot({path:S+'/w-'+k+'.png', fullPage:true}); }
console.log('ERRORS', JSON.stringify(errors)); await b.close();
