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
 */
export function screenOf(sb, s) {
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
