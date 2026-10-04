// storyboard.json -> the design canvas Dave edits: one artboard per card (key
// frame + callouts + on-screen words), the voice track on a sticky under it.
//
//   node storyboard-canvas.mjs <project-dir> [--live <canvas.json read back from the canvas>]
//
// Writes <project-dir>/storyboard/project/. Key frames must already be uploaded
// to the canvas; their urls live in <project-dir>/storyboard/artifact.json "assets".
// On a REVISION pass --live: the editor rewrites the index while the page is
// open, and a publish that does not start from the live copy is refused.
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { PHONE, loadStoryboard } from './lib.mjs';

const DIR = resolve(process.argv[2] || '.');
const liveAt = process.argv.indexOf('--live');
const sb = loadStoryboard(DIR);
const meta = JSON.parse(readFileSync(`${DIR}/storyboard/artifact.json`, 'utf8'));
const OUT = `${DIR}/storyboard/project`;
if (existsSync(OUT)) rmSync(OUT, { recursive: true });
mkdirSync(OUT, { recursive: true });

const W = 540, H = 960, S = 0.86;
const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const CHIP = 'display: inline-block; background: #ffffff; color: #000000; font-weight: 700; border-radius: 8px; padding: 0px 9px; font-size: 0.86em; line-height: 1.5; white-space: nowrap; box-shadow: 0 2px 0 #9b9799';
const chips = (t) => esc(t).replace(/\[\[(.+?)\]\]/g, `<span class="sb-chip" style="${CHIP}">$1</span>`);
const ARROW = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 85" width="60" height="85"><polygon points="21,2 39,2 39,48 57,48 30,83 3,48 21,48" fill="#ffd23f" stroke="#000000" stroke-width="3" stroke-linejoin="round"></polygon></svg>';

const page = (title, inner) => `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>${esc(title)}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<style>
body{margin:0;font-family:-apple-system,"SF Pro Text","Helvetica Neue",Helvetica,sans-serif;background:#000000;color:#ffffff}
a{color:#ffd23f}a:hover{color:#ffe27a}
</style>
</helmet>
<div class="sb-card" style="width: ${W}px; height: ${H}px; box-sizing: border-box; position: relative; overflow: hidden; background: #000000; color: #ffffff">
${inner}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{"$preview":{"width":${W},"height":${H}}}'>
class Component extends DCLogic {
renderVals() { return {}; }
}
</script>
</body>
</html>
`;

function stepBoard(s, i) {
  const boxes = s.boxes || [];
  const rings = boxes.map(([x, y, w, h, side], k) => {
    const pad = 4, L = x * S - pad, T = y * S - pad, Wd = w * S + pad * 2, Hd = h * S + pad * 2;
    const tag = boxes.length > 1 ? `<div class="sb-tag" style="position: absolute; left: ${side === 'r' ? L + Wd - 12 : Math.max(2, L - 10)}px; top: ${Math.max(2, T - 10)}px; width: 24px; height: 24px; border-radius: 12px; background: #ffd23f; color: #000000; font-weight: 800; font-size: 14px; display: flex; align-items: center; justify-content: center">${k + 1}</div>` : '';
    return `<div class="sb-ring" style="position: absolute; left: ${L}px; top: ${T}px; width: ${Wd}px; height: ${Hd}px; box-sizing: border-box; border: 3px solid #ffd23f; border-radius: 12px; box-shadow: 0 0 0 2px rgba(0,0,0,.55)"></div>${tag}`;
  }).join('\n');
  const arrow = s.arrow ? `<div class="sb-arrow" style="position: absolute; left: ${s.arrow[0] * S - 30}px; top: ${s.arrow[1] * S - 85}px; width: 60px; height: 85px">${ARROW}</div>` : '';
  return page(`Step ${i + 1}: ${s.title.replace(/\[\[|\]\]/g, '')}`, `<div style="position: absolute; left: 0px; right: 0px; top: 0px; height: 200px; box-sizing: border-box; padding: 22px 30px 0px 30px">
<div class="sb-part" style="font-size: 13px; letter-spacing: 1.6px; text-transform: uppercase; color: #9b9799; font-weight: 600">Part ${s.part}: ${esc(sb.parts[s.part - 1])}</div>
<div style="display: flex; gap: 14px; margin-top: 12px; align-items: flex-start">
<div style="flex: 0 0 auto; width: 46px; height: 46px; border-radius: 23px; background: #ffffff; color: #000000; font-weight: 800; font-size: 22px; display: flex; align-items: center; justify-content: center">${i + 1}</div>
<div style="display: flex; flex-direction: column; gap: 8px">
<div class="sb-title" style="font-size: 27px; line-height: 1.15; font-weight: 800; padding-top: 6px${s.titleStyle ? '; ' + s.titleStyle : ''}">${chips(s.title)}</div>
<div class="sb-body" style="font-size: 17px; line-height: 1.35; color: #dedcdd${s.bodyStyle ? '; ' + s.bodyStyle : ''}">${chips(s.body || '')}</div>
</div>
</div>
</div>
<div class="sb-phone" style="position: absolute; left: ${(W - PHONE.w * S) / 2}px; top: 214px; width: ${PHONE.w * S}px; height: ${PHONE.h * S}px; border-radius: 26px; overflow: hidden; box-shadow: 0 0 0 5px #333132; background: #111111">
<img src="${meta.assets[s.img]}" alt="Key frame: ${esc(s.img)}" style="width: 100%; height: 100%; display: block">
${rings}
${arrow}
</div>`);
}

const c = sb.cover;
const coverBoard = page(sb.title, `<div style="box-sizing: border-box; width: ${W}px; height: ${H}px; display: flex; flex-direction: column; padding: 90px 44px 60px 44px">
<div style="font-size: 26px; font-weight: 800; letter-spacing: 3px">TENTHGEAR</div>
<h1 class="sb-cover-heading" style="font-size: 44px; line-height: 1.08; margin: 120px 0px 0px 0px; font-weight: 800; white-space: pre-line">${esc(c.heading)}</h1>
<p class="sb-cover-sub" style="font-size: 20px; color: #dedcdd; margin: 18px 0px 0px 0px; line-height: 1.35">${esc(c.sub)}</p>
<div style="display: flex; flex-direction: column; margin-top: 70px">
${c.items.map((p, i) => `<div style="display: flex; gap: 16px; align-items: center; font-size: 21px; font-weight: 600; padding: 18px 0px; border-top: 1px solid #333132"><div style="flex: 0 0 auto; width: 38px; height: 38px; box-sizing: border-box; border-radius: 19px; border: 2px solid #ffffff; display: flex; align-items: center; justify-content: center; font-size: 17px">${i + 1}</div><div class="sb-cover-item">${esc(p)}</div></div>`).join('\n')}
</div>
<div class="sb-cover-help" style="margin-top: auto; font-size: 16px; color: #9b9799">${esc(c.help || '')}</div>
</div>`);

// ── files ─────────────────────────────────────────────────────────────────────
export const boardName = (s, i) => `S${String(i + 1).padStart(2, '0')}-${s.id}.dc.html`;
// A board Dave designed himself (harvested into storyboard/boards/) goes back verbatim.
writeFileSync(`${OUT}/Main.dc.html`, c.board ? readFileSync(`${DIR}/${c.board}`, 'utf8') : coverBoard);
if (sb.end?.board) writeFileSync(`${OUT}/${sb.end.canvasFile}`, readFileSync(`${DIR}/${sb.end.board}`, 'utf8'));
sb.steps.forEach((s, i) => writeFileSync(`${OUT}/${boardName(s, i)}`, stepBoard(s, i)));

// ── index: one row per part, the voice track on a sticky under each card ──────────────
const GX = 80, STICKY_DOWN = 44, VO_H = 230, NOTE_H = 150, TITLE_UP = 300;
const PITCH = H + STICKY_DOWN + VO_H + 20 + NOTE_H + TITLE_UP + 160;
const boards = {}, order = [], notes = {};
const place = (name, x, y, title) => { boards[name] = { x, y, w: W, h: H, title }; order.push(name); };
const voice = (id, x, y, text) => { notes[`vo-${id}`] = { x, y: y + H + STICKY_DOWN, w: W, maxH: VO_H, text, size: 'm', color: 'blue' }; };

place('Main.dc.html', 0, 0, 'Cover');
voice('cover', 0, 0, c.narration);
let col = 1, row = 0, lastPart = 1;
notes['t-1'] = { x: 0, y: -TITLE_UP, text: `Part 1: ${sb.parts[0]}`, kind: 'title1', maxW: 3600 };
sb.steps.forEach((s, i) => {
  if (s.part !== lastPart) {
    row += 1; col = 0; lastPart = s.part;
    notes[`t-${s.part}`] = { x: 0, y: row * PITCH - TITLE_UP, text: `Part ${s.part}: ${sb.parts[s.part - 1]}`, kind: 'title1', maxW: 3600 };
  }
  const x = col * (W + GX), y = row * PITCH;
  place(boardName(s, i), x, y, `${i + 1} · ${s.id}`);
  voice(s.id, x, y, s.narration);
  if (s.footage) notes[`fx-${s.id}`] = { x, y: y + H + STICKY_DOWN + VO_H + 20, w: W, maxH: NOTE_H, text: `VIDEO CLIP plays in the phone here.\n${s.footage.note || s.footage.clip}`, size: 's', color: 'orange' };
  else if (s.arrow) notes[`fx-${s.id}`] = { x, y: y + H + STICKY_DOWN + VO_H + 20, w: W, maxH: NOTE_H, text: 'In the video the arrow bounces on its target.', size: 's', color: 'orange' };
  col += 1;
});
if (sb.end?.board) {
  const e = sb.end, at = e.at || { x: col * (W + GX), y: row * PITCH, title: 'End page' };
  place(e.canvasFile, at.x, at.y, at.title);
  notes[e.voiceNote] = { x: at.x, y: at.y + H + STICKY_DOWN, w: W, maxH: VO_H, text: e.narration, size: 'm', color: 'blue' };
}
notes.readme = {
  x: -700, y: 0, w: 600, maxH: 900, size: 'm', color: 'teal',
  text: `${sb.title}\nStoryboard\n\nHOW TO EDIT\n\n1. Words on a card: click the text and retype it. A white chip marks a button the viewer taps.\n\n2. Voice track: the BLUE note under each card is what the narrator says on that card. Retype it.\n\n3. Callouts (yellow outlines and arrows): drag or resize them, or write what you want on a note.\n\n4. Add, drop or reorder a card: write it on a note next to the card. A new card needs a new key frame.\n\n5. ORANGE notes mark cards that play a video clip or an animation.\n\nWhen you are done, say so in the terminal. Every change is read back from here.`,
};

let index = { v: 3, createdOnFiles: { v: 1, at: new Date().toISOString().replace(/\.\d+Z$/, 'Z') }, title: `${sb.title}: storyboard`, launch: { view: 'canvas' }, pages: [], boards, order, notes, designSystems: [] };
if (liveAt > -1) {
  // Keep every key the editor owns; replace only the generated boards and notes,
  // and keep notes Dave added himself (any id that is not one of ours).
  const live = JSON.parse(readFileSync(resolve(process.argv[liveAt + 1]), 'utf8'));
  const ours = (id) => /^(vo-|fx-|t-\d+$|readme$)/.test(id) || id === sb.end?.voiceNote;
  const kept = Object.fromEntries(Object.entries(live.notes || {}).filter(([id]) => !ours(id)));
  index = { ...live, boards, order, notes: { ...kept, ...notes } };
}
writeFileSync(`${OUT}/canvas.json`, JSON.stringify(index, null, 1));
console.log(`${order.length} artboards, ${Object.keys(index.notes).length} notes -> ${OUT}`);
console.log('Publish: copy this folder into the session scratchpad (the publish root must sit under the working directory or the scratchpad), then send canvas.json as file_path and every .dc.html in files.');
