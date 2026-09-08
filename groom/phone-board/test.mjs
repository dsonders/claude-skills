import { chromium } from '/Users/davidsonders/ro-bot/app/node_modules/playwright/index.mjs';
import fs from 'fs';
const O='/private/tmp/claude-501/-Users-davidsonders-ro-bot-app/502c56fe-c8cb-46e3-9c57-a296facb4678/scratchpad/build';
const html = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0">' + fs.readFileSync(O+'/grooming-board-phone.html','utf8') + '</body></html>';
fs.writeFileSync(O+'/local.html', html);
const b = await chromium.launch();
const ctx = await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true});
const p = await ctx.newPage();
const errors=[]; p.on('pageerror', e=>errors.push(String(e))); p.on('console', m=>{ if (m.type()==='error') errors.push(m.text()); });
await p.goto('file://'+O+'/local.html'); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(500);
const dash = await p.evaluate(()=>({total: document.querySelector('.m-total')?.textContent, rows: document.querySelectorAll('.m-row').length, opens: [...document.querySelectorAll('.m-open')].map(e=>e.textContent), scrollW: document.documentElement.scrollWidth, status: document.querySelector('.m-status')?.textContent}));
console.log('DASH', JSON.stringify(dash));
await p.screenshot({path:O+'/t-dash.png', fullPage:true});
// open SA-6b
await p.click('a.m-row[href="#/item/SA-6b"]'); await p.waitForTimeout(300);
let it = await p.evaluate(()=>({title: document.querySelector('.m-title')?.textContent.trim().slice(0,60), decs: document.querySelectorAll('.m-dec').length, btns: document.querySelectorAll('.m-btn').length, scrollW: document.documentElement.scrollWidth, seg: !!document.querySelector('.m-seg'), frame: !!document.querySelector('#flip-body')}));
console.log('ITEM', JSON.stringify(it));
await p.screenshot({path:O+'/t-item-proposed.png', fullPage:true});
await p.click('button[data-flip="today"]'); await p.waitForTimeout(200);
console.log('TODAY sub-line', await p.evaluate(()=>document.querySelector('#flip-body .app')?.textContent.includes('Declined by the customer')));
// rule decision 1 = A, type words on 2, type a note
await p.click('button[data-dec="SA-6b-1"][data-choose="A"]'); await p.waitForTimeout(200);
await p.fill('textarea[data-words="SA-6b-2"]', 'count it as declined, fine'); await p.waitForTimeout(900);
await p.fill('#note-field', 'What does the customer page show for this line after close?'); await p.waitForTimeout(900);
const after = await p.evaluate(()=>({d1: document.getElementById('rl-SA-6b-1').textContent, d2: document.getElementById('rl-SA-6b-2').textContent, hint: document.getElementById('note-hint').textContent, ls: localStorage.getItem('groomphone.v1')}));
console.log('AFTER', JSON.stringify(after));
await p.screenshot({path:O+'/t-item-ruled.png', fullPage:true});
// back to dash, check counts + note dot persist across reload
await p.goto('file://'+O+'/local.html#/'); await p.reload(); await p.waitForTimeout(400);
const dash2 = await p.evaluate(()=>({total: document.querySelector('.m-total')?.textContent, sa6: document.querySelector('a.m-row[href="#/item/SA-6b"]')?.textContent, dot: !!document.querySelector('a.m-row[href="#/item/SA-6b"] .m-note-dot')}));
console.log('DASH2', JSON.stringify(dash2));
// text-only decision (Q-5) + walkthrough P + blocks item (D2) + clear
await p.goto('file://'+O+'/local.html#/item/Q'); await p.waitForTimeout(300);
await p.fill('textarea[data-words="Q-5"]', 'about 420px'); await p.waitForTimeout(900);
console.log('Q5', await p.evaluate(()=>document.getElementById('rl-Q-5').textContent));
await p.click('button[data-clear="Q-5"]'); await p.waitForTimeout(200);
console.log('Q5 cleared', await p.evaluate(()=>document.getElementById('rl-Q-5').textContent));
await p.goto('file://'+O+'/local.html#/item/P'); await p.waitForTimeout(400);
console.log('P', await p.evaluate(()=>({steps: document.querySelectorAll('.m-steps > div').length, scrollW: document.documentElement.scrollWidth})));
await p.screenshot({path:O+'/t-item-P.png', fullPage:true});
await p.goto('file://'+O+'/local.html#/item/D2'); await p.waitForTimeout(400);
console.log('D2', await p.evaluate(()=>({viz: document.querySelectorAll('.m-blocks .viz').length, scrollW: document.documentElement.scrollWidth})));
await p.screenshot({path:O+'/t-item-D2.png', fullPage:true});
await p.goto('file://'+O+'/local.html#/item/Y'); await p.waitForTimeout(400);
console.log('Y', await p.evaluate(()=>({viz: document.querySelectorAll('.m-blocks .viz').length, scrollW: document.documentElement.scrollWidth})));
await p.screenshot({path:O+'/t-item-Y.png', fullPage:true});
console.log('ERRORS', JSON.stringify(errors));
await b.close();
