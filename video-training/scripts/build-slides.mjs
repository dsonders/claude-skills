// storyboard.json -> annotated slides: one PNG per card, one PDF, and the layers
// the video needs (cards with a see-through phone screen, arrows on their own).
//
//   node build-slides.mjs <project-dir>
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { APP, PHONE, loadStoryboard, allCards, boardBody, screenOf, cardOf, textBox, captionsOf, CAPTION_BAND } from './lib.mjs';

const DIR = resolve(process.argv[2] || '.');
const sb = loadStoryboard(DIR);
const { W: CW, H: CH } = cardOf(sb), TB = textBox(sb), FOCUS = sb.format === 'focus';
const OUT = `${DIR}/out`, SLIDES = `${OUT}/slides`, LAYERS = `${OUT}/layers`;
for (const d of [SLIDES, LAYERS]) { if (existsSync(d)) rmSync(d, { recursive: true }); mkdirSync(d, { recursive: true }); }
const { chromium } = await import(`${APP}/node_modules/playwright/index.mjs`);

const b64 = (p, mime) => `data:${mime};base64,${readFileSync(p).toString('base64')}`;
const LOGO = b64('/Users/davidsonders/ro-bot/shared/brand-assets/SVGs/TenthGear_Logo2_A-3.svg', 'image/svg+xml');
export const S = 0.86; // phone px -> card px (card is 540 x 960, rendered at 2x)
const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;');
// [[Label]] renders as a button chip: every control the viewer is told to tap.
const chips = (t) => esc(t).replace(/\[\[(.+?)\]\]/g, '<span class="btn">$1</span>');
const ARROW = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 85" width="60" height="85"><polygon points="21,2 39,2 39,48 57,48 30,83 3,48 21,48" fill="#ffd23f" stroke="#000" stroke-width="3" stroke-linejoin="round"/></svg>';

const css = `
  * { box-sizing: border-box; }
  html, body { margin: 0; background: #000; }
  body { font-family: -apple-system, "SF Pro Text", "Helvetica Neue", Arial, sans-serif; color: #fff; }
  .card { width: ${CW}px; height: ${CH}px; background: #000; position: relative; overflow: hidden; page-break-after: always; break-after: page; }
  .top { position: absolute; left: ${TB.left}px; top: ${TB.top}px; width: ${TB.width}px; height: ${TB.height}px; padding: ${TB.padding}; }
  .part { font-size: 13px; letter-spacing: 1.6px; text-transform: uppercase; color: #9b9799; font-weight: 600; }
  .row { display: flex; gap: 14px; margin-top: 12px; align-items: flex-start; }
  .num { flex: 0 0 auto; width: 46px; height: 46px; border-radius: 23px; background: #fff; color: #000; font-weight: 800; font-size: 22px; display: flex; align-items: center; justify-content: center; font-variant-numeric: tabular-nums; }
  .title { font-size: ${TB.title}px; line-height: 1.15; font-weight: 800; letter-spacing: -0.2px; padding-top: 6px; }
  .body { font-size: ${TB.body}px; line-height: 1.35; color: #dedcdd; margin-top: 8px; white-space: pre-line; }
  .btn { display: inline-block; background: #fff; color: #000; font-weight: 700; border-radius: 8px; padding: 0 9px; font-size: 0.86em; line-height: 1.5; white-space: nowrap; box-shadow: 0 2px 0 #9b9799; letter-spacing: 0; }
  .phone { position: absolute; left: ${(540 - PHONE.w * S) / 2}px; top: 214px; width: ${PHONE.w * S}px; height: ${PHONE.h * S}px; border-radius: 26px; overflow: hidden; box-shadow: 0 0 0 5px #333132, 0 0 0 6px #4a4849; background: #111; }
  .phone img { width: 100%; height: 100%; display: block; }
  .ring { position: absolute; border: 3px solid #ffd23f; border-radius: 12px; box-shadow: 0 0 0 2px rgba(0,0,0,.55), 0 0 18px rgba(255,210,63,.55); }
  .tag { position: absolute; width: 24px; height: 24px; border-radius: 12px; background: #ffd23f; color: #000; font-weight: 800; font-size: 14px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 0 2px rgba(0,0,0,.6); }
  .arrow { position: absolute; width: 60px; height: 85px; filter: drop-shadow(0 3px 6px rgba(0,0,0,.6)); }
  .cap { position: absolute; left: 40px; right: 40px; top: ${CAPTION_BAND.top}px; height: ${CAPTION_BAND.height}px; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 22px; line-height: 1.25; font-weight: 600; color: #fff; text-wrap: balance; }
  .cover { display: flex; flex-direction: column; padding: 90px 44px 60px; }
  .cover img.logo { width: 300px; }
  .cover h1 { font-size: 44px; line-height: 1.08; margin: 120px 0 0; font-weight: 800; letter-spacing: -0.6px; white-space: pre-line; }
  .cover p.sub { font-size: 20px; color: #dedcdd; margin: 18px 0 0; line-height: 1.35; }
  .cover ol { list-style: none; padding: 0; margin: 70px 0 0; }
  .cover li { display: flex; gap: 16px; align-items: center; font-size: 21px; font-weight: 600; padding: 18px 0; border-top: 1px solid #333132; }
  .cover li:last-child { border-bottom: 1px solid #333132; }
  .cover li span { flex: 0 0 auto; width: 38px; height: 38px; border-radius: 19px; border: 2px solid #fff; display: flex; align-items: center; justify-content: center; font-size: 17px; }
  .cover .help { margin-top: auto; font-size: 16px; color: #9b9799; }
`;

/** Rings, tags and arrow for a step, positioned inside a phone frame scaled by `k`. */
export function marks(s, k = S) {
  const boxes = s.boxes || [];
  const rings = boxes.map(([x, y, w, h, side], i) => {
    const pad = 4, L = x * k - pad, T = y * k - pad, W = w * k + pad * 2, H = h * k + pad * 2;
    const tag = boxes.length > 1 ? `<div class="tag" style="left:${side === 'r' ? L + W - 12 : Math.max(2, L - 10)}px;top:${Math.max(2, T - 10)}px">${i + 1}</div>` : '';
    return `<div class="ring" style="left:${L}px;top:${T}px;width:${W}px;height:${H}px"></div>${tag}`;
  }).join('');
  const arrow = s.arrow ? `<div class="arrow" style="left:${s.arrow[0] * k - 30}px;top:${s.arrow[1] * k - 85}px">${ARROW}</div>` : '';
  return rings + arrow;
}

// Focus format: the screen alone, the narration as a subtitle under it (the PDF shows every
// sentence at once; the video shows each one as it is spoken, from the layers below).
const focusCard = (s) => `<section class="card" id="c-${s.id}">
  ${screenBox(s, `<img src="${b64(`${DIR}/frames/${s.img}.png`, 'image/png')}">`)}
  <div class="cap">${esc(captionsOf(s).join(' '))}</div>
</section>`;
const stepCard = (s, i) => FOCUS ? focusCard(s) : `<section class="card" id="c-${s.id}">
  <div class="top">
    <div class="part">Part ${s.part}: ${esc(sb.parts[s.part - 1])}</div>
    <div class="row"><div class="num">${i + 1}</div><div><div class="title" style="${esc(s.titleStyle || '')}">${chips(s.title)}</div>${s.body ? `<div class="body" style="${esc(s.bodyStyle || '')}">${chips(s.body)}</div>` : ''}</div></div>
  </div>
  ${screenBox(s, `<img src="${b64(`${DIR}/frames/${s.img}.png`, 'image/png')}">`)}
</section>`;
/** The screen (phone or laptop crop) at its place on the card, with the callouts on top. */
function screenBox(s, img) {
  const g = screenOf(sb, s);
  return `<div class="phone" style="left:${g.x}px;top:${g.y}px;width:${g.w}px;height:${g.h}px;border-radius:${g.radius}px">${img}${marks(s, g.k)}</div>`;
}

const c = sb.cover;
// A board Dave designed on the canvas renders verbatim; the template is the fallback.
const designed = (id, b) => `<section class="card" id="c-${id}">${boardBody(DIR, b.board)}</section>`;
const cover = c.board ? designed('cover', c) : `<section class="card cover" id="c-cover">
  <img class="logo" src="${LOGO}">
  <h1>${esc(c.heading)}</h1>
  <p class="sub">${esc(c.sub)}</p>
  <ol>${c.items.map((p, i) => `<li><span>${i + 1}</span>${esc(p)}</li>`).join('')}</ol>
  <div class="help">${esc(c.help || '')}</div>
</section>`;
const end = sb.end ? designed('end', sb.end) : '';

const html = `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>${cover}${sb.steps.map(stepCard).join('')}${end}</body></html>`;
writeFileSync(`${OUT}/slides.html`, html);

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: CW, height: CH }, deviceScaleFactor: 2 });
await page.goto('file://' + `${OUT}/slides.html`);
await page.waitForLoadState('load');
const cards = allCards(sb);
for (const [i, cd] of cards.entries()) await page.locator(`#c-${cd.id}`).screenshot({ path: `${SLIDES}/${String(i).padStart(2, '0')}-${cd.id}.png` });
await page.pdf({ path: `${OUT}/${sb.slug}.pdf`, width: `${CW}px`, height: `${CH}px`, printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });

// ── video layers ──────────────────────────────────────────────────────────────
// Footage steps: the card with the phone screen cut out (footage plays under it).
// Arrow steps: the card without its arrow (the video draws a moving one).
const footageIds = sb.steps.filter((s) => s.footage).map((s) => s.id);
const arrowIds = sb.steps.filter((s) => s.arrow && !s.footage).map((s) => s.id);
await page.evaluate(([fIds, aIds]) => {
  document.documentElement.style.background = 'transparent';
  document.body.style.background = 'transparent';
  for (const id of aIds) document.querySelector(`#c-${id} .arrow`)?.remove();
  for (const id of fIds) {
    const card = document.getElementById('c-' + id);
    card.style.background = 'transparent';
    const top = card.querySelector('.top'); if (top) top.style.zIndex = '2';
    card.querySelector('.cap')?.remove();
    const phone = card.querySelector('.phone');
    phone.innerHTML = '';
    phone.style.background = 'transparent';
    phone.style.boxShadow = '0 0 0 5px #333132, 0 0 0 6px #4a4849, 0 0 0 2000px #000';
  }
}, [footageIds, arrowIds]);
// Still cards in focus format lose their caption too: the video lays each sentence on in time.
if (FOCUS) await page.evaluate(() => document.querySelectorAll('.cap').forEach((e) => e.remove()));
if (FOCUS) for (const s of sb.steps.filter((x) => !x.footage && !x.arrow)) await page.locator(`#c-${s.id}`).screenshot({ path: `${LAYERS}/${s.id}-nocap.png` });
for (const id of arrowIds) await page.locator(`#c-${id}`).screenshot({ path: `${LAYERS}/${id}-noarrow.png` });
for (const id of footageIds) await page.locator(`#c-${id}`).screenshot({ path: `${LAYERS}/${id}-hole.png`, omitBackground: true });
const p2 = await browser.newPage({ viewport: { width: 60, height: 85 }, deviceScaleFactor: 2 });
await p2.setContent(`<html><body style="margin:0;background:transparent">${ARROW}</body></html>`);
await p2.screenshot({ path: `${LAYERS}/arrow.png`, omitBackground: true });
// The finger marker for still cards: lib.mjs touchOn's look at video card scale (56 px x 1.72).
const p3 = await browser.newPage({ viewport: { width: 97, height: 97 }, deviceScaleFactor: 1 });
await p3.setContent(`<html><body style="margin:0;background:transparent"><div style="position:absolute;left:5px;top:5px;width:87px;height:87px;box-sizing:border-box;border-radius:50%;background:rgba(255,255,255,.45);border:5px solid rgba(255,255,255,.95);box-shadow:0 0 0 3px rgba(0,0,0,.35)"></div></body></html>`);
await p3.screenshot({ path: `${LAYERS}/marker.png`, omitBackground: true });
// The tap animation for footage (⛔ Dave 10/11: "go with A, plus a small tap ring that expands
// from the yellow circle after the tap"): a yellow fingertip lands 0.5 s early, presses in on
// the tap and fades; a thin ring spreads out from it. 34 frames, tap at frame 15 (TAP_LEAD).
mkdirSync(`${LAYERS}/tap`, { recursive: true });
const p4 = await browser.newPage({ viewport: { width: 160, height: 160 }, deviceScaleFactor: 1 });
await p4.setContent('<canvas id="c" width="160" height="160"></canvas>');
for (let i = 0; i < 34; i++) {
  const url = await p4.evaluate((u) => {
    const c = document.getElementById('c').getContext('2d'), Y = '255,210,63', x = 80, y = 80;
    const clamp = (v) => Math.max(0, Math.min(1, v));
    c.clearRect(0, 0, 160, 160);
    if (u <= 0.35) {
      c.globalAlpha = clamp(u < -0.35 ? (u + 0.5) / 0.15 : u > 0.2 ? (0.35 - u) / 0.15 : 1);
      c.beginPath(); c.arc(x, y, 26 * (Math.abs(u) < 0.09 ? 0.82 : 1), 0, 7); c.fillStyle = `rgba(${Y},.5)`; c.fill();
      // a dark rim keeps the fingertip visible on yellow buttons (the TenthGear icon)
      c.lineWidth = 8; c.strokeStyle = 'rgba(0,0,0,.6)'; c.stroke();
      c.lineWidth = 4; c.strokeStyle = `rgb(${Y})`; c.stroke();
    }
    if (u >= 0.05) {
      const k = (u - 0.05) / 0.55;
      c.globalAlpha = clamp(0.95 * (1 - k));
      c.beginPath(); c.arc(x, y, 28 + 26 * (1 - Math.pow(1 - clamp(k), 2)), 0, 7);
      c.lineWidth = 3; c.strokeStyle = `rgb(${Y})`; c.stroke();
    }
    return document.getElementById('c').toDataURL('image/png');
  }, (i - 15) / 30);
  writeFileSync(`${LAYERS}/tap/t${String(i).padStart(3, '0')}.png`, Buffer.from(url.split(',')[1], 'base64'));
}
// One subtitle layer per sentence: the band only, see-through, at video scale.
if (FOCUS) {
  const pc = await browser.newPage({ viewport: { width: CW, height: CAPTION_BAND.height }, deviceScaleFactor: 2 });
  for (const s of sb.steps) for (const [k, t] of captionsOf(s).entries()) {
    await pc.setContent(`<html><head><style>${css} .cap { top: 0; text-shadow: 0 2px 6px rgba(0,0,0,.8); } html, body { background: transparent !important; }</style></head><body><div class="cap">${esc(t)}</div></body></html>`);
    await pc.screenshot({ path: `${LAYERS}/${s.id}-cap${k}.png`, omitBackground: true });
  }
}
await browser.close();
console.log(`slides: ${cards.length} cards -> ${SLIDES}`);
console.log(`pdf:    ${OUT}/${sb.slug}.pdf`);
