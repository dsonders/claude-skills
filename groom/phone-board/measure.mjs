import { chromium } from '/Users/davidsonders/ro-bot/app/node_modules/playwright/index.mjs';
import fs from 'fs';
const S='/Users/davidsonders/.claude/skills/groom/phone-board';
fs.writeFileSync(S+'/local.html', '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0">' + fs.readFileSync(S+'/grooming-board-phone.html','utf8') + '</body></html>');
const b = await chromium.launch(); const p = await (await b.newContext({viewport:{width:390,height:844}})).newPage();
const errors=[]; p.on('pageerror', e=>errors.push(String(e)));
await p.goto('file://'+S+'/local.html#/item/Q'); await p.waitForTimeout(500);
// measure each gallery card's inner card height at 1:1 (the inner is 390px wide, scaled) — use the unscaled scrollHeight of .q-var
const m = await p.evaluate(()=>{ const out={}; const keys=['today','pad','cc','rail','notes','onerow','footer','compact']; document.querySelectorAll('.m-gal-inner .q-var').forEach((el,i)=>{ out[keys[i]] = Math.round(el.querySelector(':scope > div').getBoundingClientRect().height / 0.437); }); return out; });
console.log(JSON.stringify(m)); fs.writeFileSync(S+'/measured.json', JSON.stringify(m));
console.log('ERRORS', JSON.stringify(errors)); await b.close();
