import { chromium } from '/Users/davidsonders/ro-bot/app/node_modules/playwright/index.mjs';
import fs from 'fs';
const S='/Users/davidsonders/.claude/skills/groom/phone-board';
fs.writeFileSync(S+'/local.html', '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0">' + fs.readFileSync(S+'/grooming-board-phone.html','utf8') + '</body></html>');
const b = await chromium.launch(); const p = await (await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2})).newPage();
const errors=[]; p.on('pageerror', e=>errors.push(String(e)));
for (const k of ['P','W','S','SA-7b','D3','X','D1','SA-20b']) {
  await p.goto('file://'+S+'/local.html#/item/'+k); await p.waitForTimeout(500);
  const w = await p.evaluate(()=>document.documentElement.scrollWidth);
  console.log(k, 'scrollW', w);
  await p.screenshot({path:S+'/v-'+k+'.png', fullPage:true});
}
console.log('ERRORS', JSON.stringify(errors)); await b.close();
