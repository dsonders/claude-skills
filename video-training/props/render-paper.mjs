// Renders the sample paper repair order to a JPEG that reads like a phone photo.
//   node render-paper.mjs <project-dir> [ro-number]
// Edit paper-ro.html for a different store, vehicle or line. Keep it free of
// op codes and other print noise: the scanner copies them into the complaint.
import { mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from '/Users/davidsonders/ro-bot/app/node_modules/playwright/index.mjs';
const HERE = dirname(fileURLToPath(import.meta.url));
const dir = resolve(process.argv[2] || '.'), ro = process.argv[3] || '418207';
mkdirSync(`${dir}/props`, { recursive: true });
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1500, height: 2000 } });
await page.goto('file://' + resolve(HERE, 'paper-ro.html') + '?ro=' + ro);
await page.screenshot({ path: `${dir}/props/paper-ro-${ro}.jpg`, type: 'jpeg', quality: 88 });
await browser.close();
console.log(`${dir}/props/paper-ro-${ro}.jpg`);
