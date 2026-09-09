import { chromium } from '/Users/davidsonders/ro-bot/app/node_modules/playwright/index.mjs';
import fs from 'fs';
const S='/Users/davidsonders/.claude/skills/groom/phone-board';
fs.writeFileSync(S+'/local.html', '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0">' + fs.readFileSync(S+'/grooming-board-phone.html','utf8') + '</body></html>');
const b = await chromium.launch(); const p = await (await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2})).newPage();
const errors=[]; p.on('pageerror', e=>errors.push(String(e)));
for (const k of ['Q','W','D3']) { await p.goto('file://'+S+'/local.html#/item/'+k); await p.waitForTimeout(600); console.log(k, await p.evaluate(()=>({w: document.documentElement.scrollWidth, gal: [...document.querySelectorAll('.m-gal-frame')].map(f=>Math.round(f.getBoundingClientRect().height))}))); await p.screenshot({path:S+'/v2-'+k+'.png', fullPage:true}); }
console.log('ERRORS', JSON.stringify(errors)); await b.close();
