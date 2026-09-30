// EXAMPLE footage script: three short clips of the real app for the video.
//   A-hold   press and hold the mic: recording screen, live waveform, release
//   B-notes  the Story Notes card closed, then open
//   C-write  Write Story: the writing animation, then the finished Cause
//
//   RO_ID=<an open RO with one warranty line and no notes> node capture-footage.mjs <project-dir>
//
// Each clip opens with a beat of stillness, shows the finger marker, then acts.
// marks.json beside each clip records when things happened, in seconds; use it to
// choose `footage.runs` (first frame, frame count, at 30 fps) in storyboard.json.
import { resolve } from 'node:path';
import * as vt from '/Users/davidsonders/.claude/skills/video-training/scripts/lib.mjs';

const DIR = resolve(process.argv[2] || '.');
const RO_ID = process.env.RO_ID;
if (!RO_ID) throw new Error('RO_ID is required');
const { browser, context, page } = await vt.phone({ dpr: 2, mic: true });
const rec = await vt.recorder(context, page, DIR);
const say = await vt.dictation(page, DIR, {
  A: 'Test drove the vehicle and verified a clunking noise from the left front over bumps at low speed.',
  B: 'Raised the vehicle on the lift and inspected the front suspension. Found excessive play in the left front stabilizer bar link. The ball joint is loose and the boot is torn.',
  C: 'I replaced the left front sway bar link and torqued it to spec. Test drove the vehicle over bumps and the noise is gone.',
});

await vt.login(page, 'tyler@demo.test');
await page.goto(`${vt.BASE}/repair-orders/${RO_ID}`, { waitUntil: 'domcontentloaded' });
const mic = page.getByRole('button', { name: /Press and hold to record a note/i });
const notesHeader = page.getByRole('button', { name: /^Story Notes/i });
const writeBtn = page.getByRole('button', { name: /^(Write|Update) Story$/ });
await mic.waitFor({ state: 'visible', timeout: 60000 });
await vt.sleep(4000);

async function hold(key, clip) {
  const [x, y] = await vt.center(mic);
  const saved = page.waitForResponse((r) => /\/notepad-items/.test(r.url()) && r.request().method() === 'POST', { timeout: 120000 });
  const marks = {};
  if (clip) { await rec.start(); await vt.sleep(1300); await vt.touchOn(page, x, y); await vt.sleep(350); marks.press = rec.now(); }
  await page.mouse.move(x, y);
  await page.mouse.down();
  await vt.sleep(900);
  await say(key);
  await vt.sleep(700);
  if (clip) marks.release = rec.now();
  await page.mouse.up();
  if (clip) await vt.touchOff(page);
  await saved;
  await vt.sleep(2500);
  if (clip) await rec.stop(clip, marks);
}

await hold('A', 'A-hold');
await hold('B');
await hold('C');
await page.evaluate(() => { document.body.scrollTop = 0; });
await vt.sleep(1500);

{
  await rec.start();
  await vt.sleep(1800);
  const [x, y] = await vt.center(notesHeader);
  await vt.touchOn(page, x, y); await vt.sleep(450);
  const marks = { tap: rec.now() };
  await notesHeader.first().tap();
  await vt.sleep(250); await vt.touchOff(page);
  await vt.sleep(4500);
  await rec.stop('B-notes', marks);
}

{
  await writeBtn.first().scrollIntoViewIfNeeded().catch(() => {});
  await vt.sleep(1200);
  await rec.start();
  await vt.sleep(1500);
  const [x, y] = await vt.center(writeBtn);
  const gen = page.waitForResponse((r) => /\/generate-all/.test(r.url()), { timeout: 180000 });
  const grade = page.waitForResponse((r) => /\/analyze-completeness/.test(r.url()), { timeout: 240000 });
  await vt.touchOn(page, x, y); await vt.sleep(450);
  const marks = { tap: rec.now() };
  await writeBtn.first().tap();
  await vt.sleep(250); await vt.touchOff(page);
  await gen; marks.written = rec.now();
  await vt.sleep(1500);
  await page.locator('textarea[name="cause"]').scrollIntoViewIfNeeded().catch(() => {});
  marks.cause = rec.now();
  await grade.catch(() => null); marks.graded = rec.now();
  await vt.sleep(3000);
  await rec.stop('C-write', marks);
}

await context.close();
await browser.close();
