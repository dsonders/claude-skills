import { chromium } from '/Users/davidsonders/ro-bot/app/node_modules/playwright/index.mjs';
import fs from 'fs';
const O='/private/tmp/claude-501/-Users-davidsonders-ro-bot-app/502c56fe-c8cb-46e3-9c57-a296facb4678/scratchpad/build';
const html = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0">' + fs.readFileSync(O+'/grooming-board-phone.html','utf8') + '</body></html>';
fs.writeFileSync(O+'/local.html', html);
const b = await chromium.launch();
const p = await (await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true})).newPage();
const errors=[]; p.on('pageerror', e=>errors.push(String(e)));
// fake a db namespace so the snapshot path runs: an in-memory store with onSnapshot firing after set
await p.addInitScript(() => {
  const docs = {}; const subs = [];
  function snap(coll){ const ds = Object.keys(docs).filter(k=>k.startsWith(coll+'/')).map(k=>({id:k.split('/')[1], exists:true, data:()=>docs[k]})); return {docs:ds, size:ds.length, empty:!ds.length, docChanges:()=>[], metadata:{fromCache:false,hasPendingWrites:false}}; }
  function fire(coll){ subs.filter(s=>s.coll===coll).forEach(s=>setTimeout(()=>s.fn(snap(coll)),30)); }
  const db = { doc(path){ const coll=path.split('/')[0]; return { get: async()=>({exists:!!docs[path], data:()=>docs[path]}), set: async(d)=>{ docs[path]=d; fire(coll); }, delete: async()=>{ delete docs[path]; fire(coll); } }; },
    collection(coll){ return { get: async()=>snap(coll), onSnapshot(fn){ subs.push({coll,fn}); setTimeout(()=>fn(snap(coll)),30); return ()=>{}; } }; } };
  window.claude = { use: async(n)=> n==='db' ? db : null };
});
await p.goto('file://'+O+'/local.html#/item/D2'); await p.waitForTimeout(600);
console.log('status', await p.evaluate(()=>document.querySelector('.m-status')?.textContent));
await p.evaluate(()=>window.scrollTo(0, 400)); await p.waitForTimeout(100);
const y0 = await p.evaluate(()=>window.scrollY);
await p.click('button[data-dec="D2-2"][data-choose="A"]'); await p.waitForTimeout(400);
const y1 = await p.evaluate(()=>window.scrollY);
console.log('scrollY before/after tap', y0, y1, y0===y1 ? 'STABLE' : 'JUMPED');
console.log('ruled line', await p.evaluate(()=>document.getElementById('rl-D2-2').textContent));
console.log('unruled line empty', await p.evaluate(()=>document.getElementById('rl-D2-1').textContent === ''));
console.log('feedback heading class', await p.evaluate(()=>document.getElementById('note-field').previousElementSibling.className));
// words while store snapshot arrives
await p.fill('textarea[data-words="D2-1"]', 'teal'); await p.waitForTimeout(900);
console.log('words kept + focus', await p.evaluate(()=>({v: document.querySelector('textarea[data-words="D2-1"]').value, focused: document.activeElement === document.querySelector('textarea[data-words="D2-1"]'), y: window.scrollY})));
await p.screenshot({path:O+'/t2.png', fullPage:true});
console.log('ERRORS', JSON.stringify(errors));
await b.close();
