// Shared helpers for training-video capture and builds.
//
// Import by ABSOLUTE path from a project's capture script:
//   import * as vt from '/Users/davidsonders/.claude/skills/video-training/scripts/lib.mjs';
//
// Nothing here holds a credential. The login password comes from the environment
// (VT_PASSWORD), or for the demo store from the seeder's own default.
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';

export const APP = '/Users/davidsonders/ro-bot/app';
export const BASE = process.env.VT_BASE || 'https://app.tenthgear.ai';
export const PHONE = { w: 390, h: 844 };

/**
 * Where a step's screen sits on the 540 x 960 card, and its scale k (frame pt -> card px).
 * Phone (default): frames are sb.phone ({w,h} in points, default PHONE), drawn 335 px wide,
 * centred, as in every earlier video. Laptop (step.screen === 'laptop'): a CROP of a desktop
 * browser take, sb.laptop ({w,h} points, default 640 x 600), drawn 500 px wide so the
 * address bar stays readable on a portrait card. boxes/arrow/tap are in that frame's points.
 *
 * sb.format === 'landscape': a 960 x 540 card (1920 x 1080 video) for viewers on a laptop.
 * The words sit in a left column (textBox), the screen on the right, 470 px tall and
 * top-aligned for both kinds so nothing jumps between a laptop card and a phone card.
 */
export const cardOf = (sb) => (sb.format === 'landscape' || sb.format === 'focus' ? { W: 960, H: 540 } : { W: 540, H: 960 });
/**
 * sb.format === 'focus' (⛔ Dave 2026-10-11: "the browser window is the focus, no headlines or
 * helper text to read"): a 960 x 540 card with the screen alone, centred, 440 px tall, and the
 * narration as SUBTITLES in the band under it (captionsOf). No title, no body, no step number.
 */
export const CAPTION_BAND = { top: 458, height: 78 };
/** A card's subtitles: its narration written for the eye, one chunk per sentence. */
export function captionsOf(c) {
  const text = (c.caption ?? c.narration ?? '')
    .replace(/tenthgear dot a i/gi, 'tenthgear.ai').replace(/\bA I\b/g, 'AI').replace(/\bR O\b/g, 'RO');
  return text.split(/(?<=[.!?]["')]*)\s+/).map((t) => t.trim()).filter(Boolean); // a '.' inside a word (tenthgear.ai) is not a break
}
/** The words' box on a step card: a top band (portrait) or a left column (landscape). */
export const textBox = (sb) => (sb.format === 'landscape'
  ? { left: 0, top: 0, width: 420, height: 540, padding: '56px 28px 0px 44px', title: 32, body: 19 }
  : { left: 0, top: 0, width: 540, height: 200, padding: '22px 30px 0px 30px', title: 27, body: 17 });
export function screenOf(sb, s) {
  if (sb.format === 'focus') {
    const lap = s.screen === 'laptop', f = lap ? (sb.laptop || { w: 1280, h: 818 }) : (sb.phone || PHONE);
    const h = 440, k = h / f.h, w = Math.round(f.w * k);
    return { kind: lap ? 'laptop' : 'phone', fw: f.w, fh: f.h, k, x: Math.round((960 - w) / 2), y: 12, w, h, radius: lap ? 10 : 24 };
  }
  if (sb.format === 'landscape') {
    const lap = s.screen === 'laptop', f = lap ? (sb.laptop || { w: 640, h: 600 }) : (sb.phone || PHONE);
    const h = 470, k = h / f.h, w = Math.round(f.w * k), AREA_X = 420, AREA_W = 510;
    return { kind: lap ? 'laptop' : 'phone', fw: f.w, fh: f.h, k, x: AREA_X + Math.round((AREA_W - w) / 2), y: 35, w, h, radius: lap ? 12 : 24 };
  }
  if (s.screen === 'laptop') {
    const f = sb.laptop || { w: 640, h: 600 }, w = 500, k = w / f.w;
    return { kind: 'laptop', fw: f.w, fh: f.h, k, x: 20, y: 224, w, h: Math.round(f.h * k), radius: 12 };
  }
  const f = sb.phone || PHONE, w = PHONE.w * 0.86, k = w / f.w;
  return { kind: 'phone', fw: f.w, fh: f.h, k, x: (540 - w) / 2, y: 214, w, h: f.h * k, radius: 26 };
}
export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const harness = () => import(`${APP}/__tests__/workflow/live-pass/lib.mjs`);
const playwright = () => import(`${APP}/node_modules/playwright/index.mjs`);

/** Read + validate a project's storyboard.json. */
export function loadStoryboard(dir) {
  const sb = JSON.parse(readFileSync(`${dir}/storyboard.json`, 'utf8'));
  const ids = new Set();
  for (const s of sb.steps) {
    if (!s.id || ids.has(s.id)) throw new Error(`storyboard: step id missing or repeated: ${s.id}`);
    ids.add(s.id);
    if (!sb.parts[s.part - 1]) throw new Error(`storyboard: step ${s.id} names part ${s.part}, which does not exist`);
    if (!existsSync(`${dir}/frames/${s.img}.png`)) throw new Error(`storyboard: step ${s.id} key frame frames/${s.img}.png is missing`);
  }
  for (const [k, b] of [['cover', sb.cover], ['end', sb.end]]) {
    if (b?.board && !existsSync(`${dir}/${b.board}`)) throw new Error(`storyboard: ${k} board ${b.board} is missing (run storyboard-harvest.mjs --write)`);
  }
  return sb;
}
export const saveStoryboard = (dir, sb) => writeFileSync(`${dir}/storyboard.json`, JSON.stringify(sb, null, 2) + '\n');

/** Every card in play order: cover, the steps, then the end page if there is one. */
export const allCards = (sb) => [{ id: 'cover', ...sb.cover }, ...sb.steps, ...(sb.end ? [{ id: 'end', ...sb.end }] : [])];

// The white horizontal logo, for the black cards. On the canvas it is an uploaded
// asset ("logo-white" in storyboard/artifact.json).
export const LOGO_WHITE = '/Users/davidsonders/ro-bot/shared/brand-assets/exports/png/horizontal-white-2400w.png';

/**
 * A board Dave designed himself on the canvas (the cover, the end page), kept
 * VERBATIM in <project>/storyboard/boards/ by the harvest. Returns the card's
 * markup (the <x-dc> body without its <helmet>), with every canvas asset url
 * swapped for the local file as a data URI so it renders off the canvas.
 */
export function boardBody(dir, file) {
  const html = readFileSync(`${dir}/${file}`, 'utf8');
  const m = /<x-dc>([\s\S]*?)<\/x-dc>/.exec(html);
  if (!m) throw new Error(`board ${file}: no <x-dc> body`);
  const assets = JSON.parse(readFileSync(`${dir}/storyboard/artifact.json`, 'utf8')).assets || {};
  const local = Object.fromEntries(Object.entries(assets).map(([k, url]) => [url, k === 'logo-white' ? LOGO_WHITE : `${dir}/frames/${k}.png`]));
  return m[1].replace(/<helmet>[\s\S]*?<\/helmet>/, '').replace(/\/_blob\/[0-9a-f]+/g, (url) => {
    const f = local[url];
    if (!f || !existsSync(f)) throw new Error(`board ${file}: asset ${url} has no local file (add it to storyboard/artifact.json assets)`);
    return `data:image/png;base64,${readFileSync(f).toString('base64')}`;
  });
}
/** Password for the login. Never printed. */
export function password() {
  if (process.env.VT_PASSWORD) return process.env.VT_PASSWORD;
  if (process.env.DEMO_SEED_PASSWORD) return process.env.DEMO_SEED_PASSWORD;
  const m = readFileSync(`${APP}/server/scripts/seed-demo-dealership.ts`, 'utf8').match(/DEMO_SEED_PASSWORD\s*\|\|\s*"([^"]+)"/);
  if (!m) throw new Error('no VT_PASSWORD set and the demo seeder default was not found');
  return m[1];
}

/**
 * Headless phone-size browser. `dpr` 3 for stills, 2 for footage.
 * `mic: true` installs the harness's fake microphone so a press-and-hold really
 * records and the app really transcribes the clip you play into it.
 */
export async function phone({ dpr = 3, mic = false, desktop = false } = {}) {
  const { chromium } = await playwright();
  const browser = await chromium.launch({ headless: true, args: ['--autoplay-policy=no-user-gesture-required', '--use-gl=swiftshader'] });
  const context = await browser.newContext(desktop
    ? { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2, permissions: ['camera', 'microphone'] }
    : {
      viewport: { width: PHONE.w, height: PHONE.h }, isMobile: true, hasTouch: true, deviceScaleFactor: dpr,
      permissions: ['camera', 'microphone'],
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
    });
  if (mic) context.addInitScript((await harness()).fakeCam);
  const page = await context.newPage();
  page.on('console', (m) => { if (m.type() === 'error') console.log('  [console.error]', m.text().slice(0, 160)); });
  return { browser, context, page };
}

/** Real /login form, then purge the app shell cache. */
export async function login(page, email) {
  await page.goto(BASE + '/login', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForSelector('input[type="email"]', { timeout: 30000 });
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password());
  await Promise.all([
    page.waitForURL((u) => !u.pathname.startsWith('/login'), { timeout: 60000 }),
    page.locator('button[type="submit"]').first().click(),
  ]);
  await (await harness()).clearSiteCaches(page);
}

/** The app mounts phone and desktop twins of many controls: always take the VISIBLE one. */
export const tid = (page, t) => page.locator(`[data-testid="${t}"]:visible`).first();

/** Still + the boxes (phone px) of the controls the caption will point at. */
export function shooter(page, dir) {
  mkdirSync(`${dir}/frames`, { recursive: true });
  return async function shot(name, targets = []) {
    const boxes = [];
    for (const t of targets) {
      const b = await t.first().boundingBox().catch(() => null);
      if (b) boxes.push([b.x, b.y, b.width, b.height].map(Math.round));
    }
    await page.screenshot({ path: `${dir}/frames/${name}.png` });
    writeFileSync(`${dir}/frames/${name}.json`, JSON.stringify({ boxes }, null, 1));
    console.log(`  frame ${name}`, JSON.stringify(boxes));
  };
}

/** On-screen finger marker for footage, so the viewer sees where the tap lands. */
export async function touchOn(page, x, y) {
  await page.evaluate(([px, py]) => {
    let d = document.getElementById('__touch');
    if (!d) {
      d = document.createElement('div'); d.id = '__touch';
      d.style.cssText = 'position:fixed;width:56px;height:56px;margin:-28px 0 0 -28px;border-radius:28px;background:rgba(255,255,255,.45);border:3px solid rgba(255,255,255,.95);box-shadow:0 0 0 2px rgba(0,0,0,.35),0 4px 14px rgba(0,0,0,.45);z-index:2147483647;pointer-events:none;transition:transform .15s ease,opacity .2s ease;';
      document.documentElement.appendChild(d);
    }
    d.style.left = px + 'px'; d.style.top = py + 'px'; d.style.opacity = '1'; d.style.transform = 'scale(1.25)';
    requestAnimationFrame(() => { d.style.transform = 'scale(1)'; });
  }, [x, y]);
}
export const touchOff = (page) => page.evaluate(() => { const d = document.getElementById('__touch'); if (d) d.style.opacity = '0'; });
export const center = async (loc) => { const b = await loc.first().boundingBox(); return [b.x + b.width / 2, b.y + b.height / 2]; };

/**
 * Footage recorder: a screenshot loop at 2x, resampled to a steady 30 fps.
 * The browser's screencast and Playwright's recordVideo both capture at 1x
 * (390 px wide), which is blurry once scaled into the phone frame. The `clip`
 * with `scale: 2` is what makes captureScreenshot return 780 x 1688.
 */
export async function recorder(context, page, dir) {
  const cdp = await context.newCDPSession(page);
  let rec = null;
  const now = () => Date.now() / 1000;
  return {
    now,
    async start() {
      const r = { frames: [], on: true };
      r.done = (async () => {
        while (r.on) {
          const t = now();
          const s = await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: 90, clip: { x: 0, y: 0, width: PHONE.w, height: PHONE.h, scale: 2 }, captureBeyondViewport: false }).catch(() => null);
          if (s) r.frames.push({ data: s.data, ts: t });
          const spent = now() - t;
          if (spent < 1 / 30) await sleep((1 / 30 - spent) * 1000);
        }
      })();
      rec = r;
    },
    /** marks = { name: timestamp from now() }, written relative to the clip start, in seconds. */
    async stop(name, marks = {}) {
      rec.on = false; await rec.done;
      const end = now(), got = rec.frames; rec = null;
      const out = `${dir}/footage/${name}`; mkdirSync(out, { recursive: true });
      const t0 = got[0]?.ts ?? end;
      const total = Math.round((end - t0) * 30);
      for (let k = 0, j = 0; k < total; k++) {
        const t = t0 + k / 30;
        while (j + 1 < got.length && got[j + 1].ts <= t) j++;
        writeFileSync(`${out}/f${String(k).padStart(5, '0')}.jpg`, Buffer.from(got[j].data, 'base64'));
      }
      const rel = Object.fromEntries(Object.entries(marks).map(([k, v]) => [k, +(v - t0).toFixed(2)]));
      writeFileSync(`${out}/marks.json`, JSON.stringify({ frames: total, seconds: +(end - t0).toFixed(2), marks: rel }, null, 1));
      console.log(`  clip ${name}: ${total} frames, ${(end - t0).toFixed(1)}s`, JSON.stringify(rel));
    },
  };
}

/**
 * Dictation clips the fake microphone plays. lines = { A: 'text', ... }.
 * Returns a `say(key)` that feeds the clip into the mic; call it while the
 * press-and-hold button is down.
 */
export async function dictation(page, dir, lines) {
  const h = await harness();
  const out = `${dir}/dictation`; mkdirSync(out, { recursive: true });
  const wavs = {};
  for (const [k, text] of Object.entries(lines)) {
    const aiff = `${out}/${k}.aiff`, wav = `${out}/${k}.wav`;
    if (!existsSync(wav)) {
      execFileSync('say', ['-o', aiff, text]);
      execFileSync('afconvert', ['-f', 'WAVE', '-d', 'LEI16@16000', '-c', '1', aiff, wav]);
    }
    wavs[k] = wav;
  }
  await h.routeTts(page, wavs);
  return async function say(key) {
    await page.evaluate((k) => window.__playTts(k), key);
    await page.waitForFunction(() => window.__ttsState === 'ended', null, { timeout: 120000 });
  };
}

/** Length of an audio or video file, in seconds. */
export const seconds = (file) => parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', file]).toString());
export const ffmpeg = (args) => execFileSync('ffmpeg', ['-loglevel', 'error', '-y', ...args]);

// ── the arrow (look borrowed from bigarrow, MIT: github.com/franzenzenhofer/big-arrow-on-the-screen) ──
// A step's arrow is [x, y] (the tip, frame points, coming from above) or
// { at: [x, y], from: 'top' | 'top-left' | 'left' | 'bottom-left' | 'bottom' | ..., text: 'Tap here' }.
// `from` is the side the arrow comes from; `text` hangs a label on its tail.
const ARROW_FROM = { top: [0, 1], bottom: [0, -1], left: [1, 0], right: [-1, 0], 'top-left': [1, 1], 'top-right': [-1, 1], 'bottom-left': [1, -1], 'bottom-right': [-1, -1] };
export const ARROW_INK = { fill: '#ffd23f', edge: '#1c1c1e' };
export function arrowSpec(a) {
  if (!a) return null;
  const s = Array.isArray(a) ? { at: a } : { ...a };
  s.from = s.from || 'top';
  if (!ARROW_FROM[s.from]) throw new Error(`arrow from '${s.from}' is not one of ${Object.keys(ARROW_FROM).join(', ')}`);
  return s;
}
/** Shaft, head and label in card px, with the tip at (0, 0). head = the unit direction the head points. */
export function arrowGeometry(spec, { reach = 92, stroke = 11, headLen = 32, headW = 38 } = {}) {
  const [vx, vy] = ARROW_FROM[spec.from], m = Math.hypot(vx, vy), u = [vx / m, vy / m];
  const tail = [-u[0] * reach, -u[1] * reach];
  // A soft bend: the control point sits off the chord, always to the same hand.
  const bow = reach * 0.2, C = [tail[0] / 2 - u[1] * bow, tail[1] / 2 + u[0] * bow];
  const hm = Math.hypot(C[0], C[1]), h = [-C[0] / hm, -C[1] / hm], hp = [-h[1], h[0]];
  const base = [-h[0] * headLen, -h[1] * headLen], notch = [base[0] + h[0] * headLen * 0.28, base[1] + h[1] * headLen * 0.28];
  const head = [[0, 0], [base[0] + hp[0] * headW / 2, base[1] + hp[1] * headW / 2], notch, [base[0] - hp[0] * headW / 2, base[1] - hp[1] * headW / 2]];
  const end = [notch[0] + h[0] * 2, notch[1] + h[1] * 2];
  const shaft = `M${tail[0].toFixed(1)},${tail[1].toFixed(1)} Q${C[0].toFixed(1)},${C[1].toFixed(1)} ${end[0].toFixed(1)},${end[1].toFixed(1)}`;
  return { u, tail, C, shaft, head: head.map((p) => p.map((n) => n.toFixed(1)).join(',')).join(' '), dir: h, stroke };
}
/** The label's pill (card px): an estimate from its length, for the canvas, which cannot measure text. */
const labelSize = (text) => ({ w: Math.round(String(text).length * 10.6 + 30), h: 36 });
/** Which share of the label sits left of / above the tail, by the side the arrow comes from. */
const labelAnchor = (u) => [u[0] > 0.9 ? -1 : u[0] < -0.9 ? 0 : u[0] > 0 ? -0.78 : u[0] < 0 ? -0.22 : -0.5, u[1] > 0 ? -1 : u[1] < 0 ? 0 : -0.5];
/** The box around shaft, head and label (card px, relative to the tip; the label's width is estimated).
 *  The canvas makes this box the one thing Dave grabs, so a drag moves the whole arrow. */
export function arrowBox(spec) {
  // pad covers half the head's width and the stroke; the control point covers the bend.
  const g = arrowGeometry(spec), pad = 22, xs = [0, g.tail[0], g.C[0]], ys = [0, g.tail[1], g.C[1]];
  if (spec.text) {
    const { w, h } = labelSize(spec.text), [tx, ty] = labelAnchor(g.u), x0 = g.tail[0] + tx * w, y0 = g.tail[1] + ty * h;
    xs.push(x0, x0 + w); ys.push(y0, y0 + h);
  }
  const left = Math.floor(Math.min(...xs) - pad), top = Math.floor(Math.min(...ys) - pad);
  return { left, top, w: Math.ceil(Math.max(...xs) + pad) - left, h: Math.ceil(Math.max(...ys) + pad) - top };
}
/** The arrow as HTML, its tip at (left, top) of the box it is placed in. Borders draw under fills,
 *  so shaft, head and label read as one shape. */
export function arrowHtml(spec, left, top, { svgLabel = false } = {}) {
  const g = arrowGeometry(spec), B = 3, { fill, edge } = ARROW_INK;
  // svgLabel (the canvas): the label is drawn inside the SVG, so the editor sees no text to select
  // and a click grabs the whole arrow; its width is estimated and the text fitted to it.
  let pill = ['', ''];
  if (spec.text && svgLabel) {
    const { w, h } = labelSize(spec.text), [tx, ty] = labelAnchor(g.u);
    const x = g.tail[0] + g.u[0] * 4 + tx * w, y = g.tail[1] + g.u[1] * 4 + ty * h;
    const t = String(spec.text).replace(/&/g, '&amp;').replace(/</g, '&lt;');
    pill = [`<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${w}" height="${h}" rx="${h / 2}" fill="${fill}" stroke="${edge}" stroke-width="${2 * B}"/>`,
      `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${w}" height="${h}" rx="${h / 2}" fill="${fill}"/><text x="${(x + w / 2).toFixed(1)}" y="${(y + h / 2 + 6).toFixed(1)}" text-anchor="middle" textLength="${w - 30}" lengthAdjust="spacingAndGlyphs" fill="${edge}" font-family="-apple-system,'SF Pro Text','Helvetica Neue',Arial,sans-serif" font-size="18" font-weight="800">${t}</text>`];
  }
  const svg = (pass) => `<svg width="400" height="400" viewBox="-200 -200 400 400" style="position:absolute;left:-200px;top:-200px;overflow:visible">
    <path d="${g.shaft}" fill="none" stroke="${pass ? fill : edge}" stroke-width="${g.stroke + (pass ? 0 : 2 * B)}" stroke-linecap="round"/>
    <polygon points="${g.head}" fill="${pass ? fill : edge}" stroke="${pass ? fill : edge}" stroke-width="${pass ? 0.5 : 2 * B}" stroke-linejoin="round"/>${pill[pass]}</svg>`;
  let label = ['', ''];
  if (spec.text && !svgLabel) {
    const [tx, ty] = labelAnchor(g.u).map((v) => v * 100);
    // The label overlaps the tail by a few px, so the shaft grows out of it.
    const ox = g.u[0] * 4, oy = g.u[1] * 4;
    const box = (pass) => `<div style="position:absolute;left:${(g.tail[0] + ox).toFixed(1)}px;top:${(g.tail[1] + oy).toFixed(1)}px;transform:translate(${tx}%,${ty}%);white-space:nowrap;background:${fill};color:${pass ? edge : 'transparent'};font:800 18px/1 -apple-system,'SF Pro Text','Helvetica Neue',Arial,sans-serif;padding:9px 15px;border-radius:999px;${pass ? '' : `box-shadow:0 0 0 ${B}px ${edge};`}">${String(spec.text).replace(/&/g, '&amp;').replace(/</g, '&lt;')}</div>`;
    label = [box(0), box(1)];
  }
  return `<div class="arrow" style="position:absolute;left:${left}px;top:${top}px;width:0;height:0;filter:drop-shadow(0 3px 5px rgba(0,0,0,.55))">${svg(0)}${label[0]}${svg(1)}${label[1]}</div>`;
}
