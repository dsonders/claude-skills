import { chromium } from '/Users/davidsonders/ro-bot/app/node_modules/playwright/index.mjs';
import fs from 'fs';
const S='/Users/davidsonders/.claude/skills/groom/phone-board';
fs.writeFileSync(S+'/local.html', '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0">' + fs.readFileSync(S+'/grooming-board-phone.html','utf8') + '</body></html>');
const b = await chromium.launch();
const errors=[];
// ---- phone regression ----
const p = await (await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true})).newPage(); p.on('pageerror', e=>errors.push('phone '+e));
await p.goto('file://'+S+'/local.html#/'); await p.evaluate(()=>localStorage.clear()); await p.reload(); await p.waitForTimeout(400);
console.log('phone dash', await p.evaluate(()=>({total: document.querySelector('.m-total').textContent, rows: document.querySelectorAll('.m-row').length, w: document.documentElement.scrollWidth})));
await p.click('.m-sec[data-sec="Dashboards"] .m-sechead'); await p.click('a.m-row[href="#/item/X"]'); await p.waitForTimeout(400);
await p.evaluate(()=>window.scrollTo(0,500)); const y0 = await p.evaluate(()=>window.scrollY);
await p.click('[data-dec="X-1"][data-choose="A"]'); await p.waitForTimeout(200);
console.log('phone tap', await p.evaluate(()=>({rl: document.getElementById('rl-X-1').textContent, y: window.scrollY})), 'y0', y0);
await p.fill('[data-note="X"]', 'hover works for me'); await p.waitForTimeout(900);
console.log('phone note', await p.evaluate(()=>document.querySelector('[data-note-hint="X"]').textContent));
await p.click('button[data-flip="today"]').catch(()=>{}); 
await p.goto('file://'+S+'/local.html#/item/SA-6b'); await p.waitForTimeout(300); await p.click('button[data-flip="today"]'); await p.waitForTimeout(200);
console.log('phone flip today', await p.evaluate(()=>document.querySelector('.m-flipbody .app').textContent.includes('Declined by the customer')));
await p.screenshot({path:S+'/p9-X.png', fullPage:false});
// ---- desktop ----
const d = await (await b.newContext({viewport:{width:1280,height:900},deviceScaleFactor:1})).newPage(); d.on('pageerror', e=>errors.push('desk '+e));
await d.goto('file://'+S+'/local.html#/'); await d.waitForTimeout(400);
console.log('desk dash', await d.evaluate(()=>({total: document.querySelector('.m-total').textContent, cards: document.querySelectorAll('.m-deskcard').length, secs: document.querySelectorAll('.m-sec').length, w: document.documentElement.scrollWidth})));
await d.click('.m-sec[data-sec="RO page — advisor, admin, tech"] .m-sechead'); await d.waitForTimeout(200);
await d.click('[data-expand="P"]'); await d.waitForTimeout(600);
console.log('desk P open', await d.evaluate(()=>({body: !!document.querySelector('.m-deskbody[data-item="P"]'), both: document.querySelectorAll('.m-deskbody[data-item="P"] .m-both').length, opts: document.querySelectorAll('.m-deskbody[data-item="P"] .m-opts').length, w: document.documentElement.scrollWidth})));
await d.evaluate(()=>document.querySelector('[data-expand="P"]').scrollIntoView());
await d.screenshot({path:S+'/d9-P.png', fullPage:false});
await d.evaluate(()=>window.scrollBy(0,900)); await d.screenshot({path:S+'/d9-P2.png', fullPage:false});
// desktop ruling via store-less path + note
const y1 = await d.evaluate(()=>window.scrollY);
// tap the first OPEN decision on any expanded desktop card (never a hardcoded id — baked ids vanish)
const firstOpen = await d.evaluate(()=>{ const b=document.querySelector('.m-deskbody .m-dec:not(.baked) [data-choose="A"]'); return b ? b.getAttribute('data-dec') : null; });
if (!firstOpen) { await d.goto('file://'+S+'/local.html#/item/S'); await d.waitForTimeout(600); }
const openId = firstOpen || await d.evaluate(()=>document.querySelector('.m-deskbody .m-dec:not(.baked) [data-choose="A"]')?.getAttribute('data-dec'));
await d.click('[data-dec="'+openId+'"][data-choose="A"]'); await d.waitForTimeout(200);
console.log('desk tap', openId, await d.evaluate((id)=>({rl: document.getElementById('rl-'+id).textContent, y: window.scrollY}), openId), 'y1', y1);
// hash deep link expands on desktop
await d.goto('file://'+S+'/local.html#/item/Q'); await d.waitForTimeout(600);
console.log('desk Q link', await d.evaluate(()=>({open: !!document.querySelector('.m-deskbody[data-item="Q"]'), gal: document.querySelectorAll('.m-deskbody[data-item="Q"] .m-gallery.desk .m-gal').length, w: document.documentElement.scrollWidth})));
await d.evaluate(()=>document.querySelector('[data-expand="Q"]').scrollIntoView()); await d.evaluate(()=>window.scrollBy(0,300));
await d.screenshot({path:S+'/d9-Q.png', fullPage:false});
// legacy sections exist
console.log('desk legacy', await d.evaluate(()=>[...document.querySelectorAll('.m-sec[data-sec="risk"], .m-sec[data-sec="icebox"], .m-sec[data-sec="archive"]')].map(e=>e.getAttribute('data-sec'))));
await d.click('.m-sec[data-sec="risk"] .m-sechead'); await d.waitForTimeout(200); await d.evaluate(()=>document.querySelector('.m-sec[data-sec="risk"]').scrollIntoView()); await d.screenshot({path:S+'/d9-risk.png', fullPage:false});
console.log('ERRORS', JSON.stringify(errors)); await b.close();
