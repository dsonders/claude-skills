// EXAMPLE capture script: key frames for "Story Writer: getting started".
// Copy into a project folder and rewrite the flow for the new video.
//
//   node capture-stills.mjs <project-dir>
//
// Needs the store in single player for the duration (see SKILL.md, Step 2).
// Every tap below was proven on prod 2026-09-29; the selectors are the app's own.
import { resolve } from 'node:path';
import { appendFileSync } from 'node:fs';
import * as vt from '/Users/davidsonders/.claude/skills/video-training/scripts/lib.mjs';

const DIR = resolve(process.argv[2] || '.');
const RO_NUMBER = process.env.RO_NUMBER || '418207';
const { browser, context, page } = await vt.phone({ dpr: 3, mic: true });
const shot = vt.shooter(page, DIR);
const tid = (t) => vt.tid(page, t);
const say = await vt.dictation(page, DIR, {
  A: 'Test drove the vehicle and verified a clunking noise from the left front over bumps at low speed.',
  B: 'Raised the vehicle on the lift and inspected the front suspension. Found excessive play in the left front stabilizer bar link. The ball joint is loose and the boot is torn.',
  C: 'I replaced the left front sway bar link and torqued it to spec. Test drove the vehicle over bumps and the noise is gone.',
  // "Scheduled maintenance" opens the service checklist whichever way the
  // transcript punctuates the mileage.
  M: 'Scheduled maintenance, forty thousand miles.',
});

await vt.login(page, 'tyler@demo.test');

// ── Part 1: scan the paper RO ───────────────────────────────────────────────────
await page.goto(vt.BASE + '/', { waitUntil: 'domcontentloaded' });
await tid('dashboard-new-ro').waitFor({ state: 'visible', timeout: 60000 });
await vt.sleep(2500);                       // the job list paints after the frame
await shot('01-dashboard', [tid('dashboard-new-ro')]);
await tid('dashboard-new-ro').tap();
await tid('new-ro-scan').waitFor({ state: 'visible', timeout: 15000 });
await vt.sleep(700);
await shot('02-new-ro-menu', [tid('new-ro-scan')]);
// The camera input is always in the DOM: hand it the sample sheet directly.
await page.locator('[data-testid="new-ro-scan-input"]').first().setInputFiles(`${DIR}/props/paper-ro-${RO_NUMBER}.jpg`);
await tid('ro-intake-scan-submit').waitFor({ state: 'visible', timeout: 30000 });
await vt.sleep(1200);
await shot('03-page-captured', [tid('ro-intake-scan-submit')]);
await tid('ro-intake-scan-submit').tap();
await tid('ro-intake-submit').waitFor({ state: 'visible', timeout: 120000 });
await vt.sleep(2500);                       // VIN decode settles
await tid('input-complaint-0').scrollIntoViewIfNeeded().catch(() => {});
await vt.sleep(600);
await shot('06-review-save', [tid('input-complaint-0'), tid('ro-intake-submit')]);
await tid('ro-intake-submit').tap();
const anyway = tid('ro-intake-vin-create-anyway'); // same VIN already open on a retake
if (await anyway.isVisible({ timeout: 4000 }).catch(() => false)) await anyway.tap();
await page.waitForURL(/\/repair-orders\/\d+/, { timeout: 60000 });
const roId = page.url().match(/repair-orders\/(\d+)/)[1];
appendFileSync(`${DIR}/created-ros.txt`, roId + '\n'); // so the retakes can be closed afterwards
console.log('RO', roId);

// ── Part 2: voice notes, then the warranty story ────────────────────────────────
const mic = page.getByRole('button', { name: /Press and hold to record a note/i });
const notesHeader = page.getByRole('button', { name: /^Story Notes/i });
const writeBtn = page.getByRole('button', { name: /^(Write|Update) Story$/ });
await mic.waitFor({ state: 'visible', timeout: 60000 });
await vt.sleep(3500);                       // the tab label arrives a moment after the RO opens

async function hold(key, frame) {
  const [x, y] = await vt.center(mic);
  const saved = page.waitForResponse((r) => /\/notepad-items/.test(r.url()) && r.request().method() === 'POST', { timeout: 120000 });
  await page.mouse.move(x, y);
  await page.mouse.down();                  // mouse events drive the hold, even in a touch context
  await vt.sleep(900);
  const spoken = say(key);
  if (frame) { await vt.sleep(1800); await shot(frame, []); }
  await spoken;
  await vt.sleep(700);
  await page.mouse.up();
  await saved;
  await vt.sleep(2500);
}
await shot('07-ro-open', [mic]);
await hold('A', '08-recording');
await hold('B');
await hold('C');
await notesHeader.first().tap();
await vt.sleep(1200);
await shot('09-notes', [notesHeader]);
await writeBtn.first().scrollIntoViewIfNeeded().catch(() => {});
await vt.sleep(500);
await shot('10-write-story', [writeBtn]);
const gen = page.waitForResponse((r) => /\/generate-all/.test(r.url()), { timeout: 180000 });
const grade = page.waitForResponse((r) => /\/analyze-completeness/.test(r.url()), { timeout: 240000 });
await writeBtn.first().tap();
await gen; await grade.catch(() => null);
await vt.sleep(3500);
await notesHeader.first().tap().catch(() => {});  // collapse the notes so the story leads the screen
await vt.sleep(900);
const gradeCard = page.getByText('Story Grade', { exact: false }).first();
await gradeCard.scrollIntoViewIfNeeded().catch(() => {});
// The RO page scrolls inside <body>, not the window.
await page.evaluate(() => { document.body.scrollTop += 260; });
await vt.sleep(900);
await shot('14-story-grade', [gradeCard]);

// ── Part 3: customer pay line, the service checklist, the story ───────────────────
await page.evaluate(() => { document.body.scrollTop = 0; });
await vt.sleep(800);
await shot('15-edit-lines', [tid('button-add-line-menu')]);
await tid('button-add-line-menu').tap();
await tid('add-line-blank').waitFor({ state: 'visible', timeout: 15000 });
await vt.sleep(500);
await shot('16-add-new-line', [tid('add-line-blank')]);
await tid('add-line-blank').tap();
await tid('add-line-paytype-cp').waitFor({ state: 'visible', timeout: 15000 });
await vt.sleep(500);
await shot('17-pick-customer-pay', [tid('add-line-paytype-cp')]);
await tid('add-line-paytype-cp').tap();
await vt.sleep(3000);
await hold('M');
await writeBtn.first().scrollIntoViewIfNeeded().catch(() => {});
await vt.sleep(600);
await shot('19-cp-note', [notesHeader, writeBtn]);
const pre = page.waitForResponse((r) => /\/maintenance-precheck/.test(r.url()), { timeout: 120000 });
await writeBtn.first().tap();
await pre;
const sheet = page.getByRole('dialog', { name: 'Confirm scheduled maintenance' });
await sheet.waitFor({ state: 'visible', timeout: 30000 });
await vt.sleep(1200);
await shot('21-checklist', [sheet]);
const items = sheet.getByRole('button');
const names = await items.allInnerTexts();
const services = names.map((t, i) => ({ t: t.trim(), i })).filter((x) => x.t && !/Write Story|Skip/.test(x.t));
const last = items.nth(services[services.length - 1].i);
await last.scrollIntoViewIfNeeded().catch(() => {});
await last.tap();
await vt.sleep(700);
const confirm = sheet.getByRole('button', { name: /Write Story/ });
await shot('22-checklist-unchecked', [last, confirm]);
const gen2 = page.waitForResponse((r) => /\/generate-all/.test(r.url()), { timeout: 180000 });
const grade2 = page.waitForResponse((r) => /\/analyze-completeness/.test(r.url()), { timeout: 240000 });
await confirm.tap();
await gen2; await grade2.catch(() => null);
await vt.sleep(3500);
await notesHeader.first().tap().catch(() => {});
await vt.sleep(900);
await page.locator('textarea[name="correction"]').scrollIntoViewIfNeeded().catch(() => {});
await vt.sleep(900);
await shot('23-cp-story', [page.locator('textarea[name="correction"]')]);

await context.close();
await browser.close();
console.log('done. RO', roId);
