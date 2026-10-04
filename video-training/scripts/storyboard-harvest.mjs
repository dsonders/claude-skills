// Read Dave's edits back off the storyboard canvas and merge them into
// storyboard.json. He rules by EDITING the canvas, not by replying in chat, so
// every changed string here is a ruling.
//
//   node storyboard-harvest.mjs <project-dir> <folder holding the pulled project/> [--write]
//
// Pull first with the Artifact tool: action "read", the canvas url, `paths` =
// project/canvas.json plus every project/*.dc.html, and an `out_dir`.
// Without --write this only prints what changed.
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { loadStoryboard, saveStoryboard } from './lib.mjs';

const DIR = resolve(process.argv[2] || '.');
const LIVE = resolve(process.argv[3] || '.');
const WRITE = process.argv.includes('--write');
const sb = loadStoryboard(DIR);
const S = 0.86;

const decode = (t) => t.replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'");
/** Inner markup of the first element carrying `cls`, tag-balanced. */
function inner(html, cls) {
  const open = new RegExp(`<(\\w+)[^>]*class="[^"]*\\b${cls}\\b[^"]*"[^>]*>`).exec(html);
  if (!open) return null;
  const tag = open[1], from = open.index + open[0].length;
  const re = new RegExp(`<${tag}\\b[^>]*>|</${tag}>`, 'g');
  re.lastIndex = from;
  for (let depth = 1, m; (m = re.exec(html));) {
    depth += m[0].startsWith('</') ? -1 : 1;
    if (depth === 0) return html.slice(from, m.index);
  }
  return null;
}
const all = (html, cls) => { const out = []; let rest = html; for (let m; (m = new RegExp(`<\\w+[^>]*class="[^"]*\\b${cls}\\b[^"]*"[^>]*>`).exec(rest));) { out.push(m[0]); rest = rest.slice(m.index + m[0].length); } return out; };
/** Card words back to storyboard text: chips become [[Label]], other tags drop. */
const words = (h) => h == null ? null : decode(h
  .replace(/<span[^>]*class="[^"]*\bsb-chip\b[^"]*"[^>]*>([\s\S]*?)<\/span>/g, (_, t) => `[[${t.replace(/<[^>]+>/g, '').trim()}]]`)
  .replace(/<br\s*\/?>/g, '\n').replace(/<[^>]+>/g, '')).replace(/[ \t]+/g, ' ').trim();
const px = (tag, k) => { const m = new RegExp(`(?:^|[;"\\s])${k}:\\s*(-?[\\d.]+)px`).exec(tag); return m ? parseFloat(m[1]) : null; };

const changes = [], problems = [];
const set = (obj, key, val, label) => {
  if (val === undefined && key.endsWith('Style')) { if (obj[key] !== undefined) { changes.push({ label, from: obj[key], to: '(none)' }); delete obj[key]; } return; }
  if (val == null) { problems.push(`${label}: could not be read off the canvas, check it by eye`); return; }
  if (JSON.stringify(obj[key] ?? '') === JSON.stringify(val)) return;
  changes.push({ label, from: obj[key], to: val });
  obj[key] = val;
};

const index = JSON.parse(readFileSync(`${LIVE}/project/canvas.json`, 'utf8'));
const notes = index.notes || {};

// Boards Dave designs himself (the cover, the end page) are kept VERBATIM in
// storyboard/boards/, so the slides and video show his layout, not a template.
// Their words are also read into storyboard.json, for the record and the voice.
const keep = [];
const keepBoard = (owner, file, label) => {
  const src = `${LIVE}/project/${file}`, rel = `storyboard/boards/${file}`;
  const now = readFileSync(src, 'utf8'), before = existsSync(`${DIR}/${rel}`) ? readFileSync(`${DIR}/${rel}`, 'utf8') : null;
  if (now !== before) changes.push({ label: `${label} design`, from: before ? '(kept copy)' : '(none kept yet)', to: `${file} as drawn on the canvas` });
  if (owner.board !== rel) owner.board = rel;
  keep.push([src, rel, now]);
};
/** Text of every element carrying `cls`, its child blocks joined by a space. */
const allWords = (h, cls) => { const out = []; let rest = h; for (let m; (m = new RegExp(`class="[^"]*\\b${cls}\\b`).exec(rest));) { const at = rest.lastIndexOf('<', m.index); out.push(words((inner(rest.slice(at), cls) || '').replace(/<\/div>/g, ' </div>'))); rest = rest.slice(m.index + 10); } return out; };

// cover
{
  const f = `${LIVE}/project/Main.dc.html`;
  if (existsSync(f)) {
    const h = readFileSync(f, 'utf8');
    const heads = allWords(h, 'sb-cover-heading');
    set(sb.cover, 'heading', heads[0] ?? null, 'cover heading');
    if (heads[1] || sb.cover.subheading) set(sb.cover, 'subheading', heads[1] ?? '', 'cover subheading');
    set(sb.cover, 'sub', words(inner(h, 'sb-cover-sub')), 'cover subhead');
    set(sb.cover, 'help', allWords(h, 'sb-cover-help')[0] ?? null, 'cover footer');
    const items = allWords(h, 'sb-cover-item');
    if (items.length) set(sb.cover, 'items', items, 'cover list');
    keepBoard(sb.cover, 'Main.dc.html', 'cover');
  } else problems.push('cover: Main.dc.html is gone from the canvas');
  if (notes['vo-cover']) set(sb.cover, 'narration', notes['vo-cover'].text.trim(), 'cover voice');
}

// end page: sb.end = { canvasFile, voiceNote, ... } names Dave's own artboard
if (sb.end) {
  const e = sb.end, f = `${LIVE}/project/${e.canvasFile}`;
  if (existsSync(f)) {
    const h = readFileSync(f, 'utf8');
    set(e, 'heading', allWords(h, 'sb-cover-heading')[0] ?? null, 'end heading');
    set(e, 'items', allWords(h, 'sb-cover-item'), 'end list');
    set(e, 'help', allWords(h, 'sb-cover-help')[0] ?? null, 'end footer');
    keepBoard(e, e.canvasFile, 'end page');
    const b = index.boards?.[e.canvasFile];
    if (b) { const at = { x: b.x, y: b.y, title: b.title }; if (JSON.stringify(e.at) !== JSON.stringify(at)) e.at = at; }
  } else problems.push(`end page: ${e.canvasFile} is gone from the canvas`);
  const vo = notes[e.voiceNote];
  if (vo) set(e, 'narration', vo.text.trim(), 'end voice'); else problems.push(`end page: its voice note ${e.voiceNote} was deleted`);
}

// steps
const files = Object.keys(index.boards || {});
sb.steps.forEach((s, i) => {
  const name = files.find((f) => new RegExp(`^S\\d+-${s.id}\\.dc\\.html$`).test(f));
  const label = `step ${i + 1} (${s.id})`;
  if (!name || !existsSync(`${LIVE}/project/${name}`)) { problems.push(`${label}: its card was removed from the canvas. Drop the step?`); return; }
  const h = readFileSync(`${LIVE}/project/${name}`, 'utf8');
  set(s, 'title', words(inner(h, 'sb-title')), `${label} title`);
  set(s, 'body', words(inner(h, 'sb-body')) ?? '', `${label} body`);
  // Layout Dave set by hand on the words (a width that forces his line break, bold):
  // every declaration beyond the generator's own is kept and rendered by the builds.
  for (const [cls, key, base] of [['sb-title', 'titleStyle', ['font-size', 'line-height', 'font-weight', 'padding-top']], ['sb-body', 'bodyStyle', ['font-size', 'line-height', 'color']]]) {
    const tag = new RegExp(`<\\w+[^>]*class="[^"]*\\b${cls}\\b[^"]*"[^>]*>`).exec(h)?.[0] || '';
    const style = /style="([^"]*)"/.exec(tag)?.[1] || '';
    const seen = new Set(); const extra = [];
    for (const d of style.split(';').map((x) => x.trim()).filter(Boolean).reverse()) { const k = d.split(':')[0].trim(); if (!base.includes(k) && !seen.has(k)) { seen.add(k); extra.unshift(d.replace(/\s*:\s*/, ': ')); } }
    set(s, key, extra.join('; ') || undefined, `${label} ${key === 'titleStyle' ? 'title' : 'body'} layout`);
  }
  const rings = all(h, 'sb-ring').map((t) => [px(t, 'left'), px(t, 'top'), px(t, 'width'), px(t, 'height')]);
  if (rings.every((r) => r.every((v) => v != null))) {
    const back = rings.map(([L, T, W, H], k) => { const b = [(L + 4) / S, (T + 4) / S, (W - 8) / S, (H - 8) / S].map(Math.round); const side = (s.boxes?.[k] || [])[4]; return side ? [...b, side] : b; });
    const moved = back.length !== (s.boxes || []).length || back.some((b, k) => b.slice(0, 4).some((v, j) => Math.abs(v - s.boxes[k][j]) > 2));
    if (moved) set(s, 'boxes', back, `${label} callouts`);
  } else problems.push(`${label}: a callout lost its position, check it by eye`);
  const arrows = all(h, 'sb-arrow');
  if (s.arrow && !arrows.length) { changes.push({ label: `${label} arrow`, from: s.arrow, to: 'removed' }); delete s.arrow; }
  if (arrows.length) { const a = [Math.round((px(arrows[0], 'left') + 30) / S), Math.round((px(arrows[0], 'top') + 85) / S)]; if (!s.arrow || a.some((v, j) => Math.abs(v - s.arrow[j]) > 2)) set(s, 'arrow', a, `${label} arrow`); }
  const vo = notes[`vo-${s.id}`];
  if (vo) set(s, 'narration', vo.text.trim(), `${label} voice`); else problems.push(`${label}: its voice note was deleted`);
});

// Order on the canvas: a card dragged to a new place is a reorder request.
const posOrder = sb.steps.map((s) => { const n = files.find((f) => new RegExp(`^S\\d+-${s.id}\\.dc\\.html$`).test(f)); const b = index.boards[n]; return b ? { id: s.id, y: Math.round(b.y / 400), x: b.x } : null; }).filter(Boolean).sort((a, b) => a.y - b.y || a.x - b.x).map((o) => o.id);
const was = sb.steps.map((s) => s.id).filter((id) => posOrder.includes(id));
if (JSON.stringify(posOrder) !== JSON.stringify(was)) problems.push(`cards were moved on the canvas. Order there now: ${posOrder.join(', ')}. Confirm with Dave before reordering steps.`);

// Notes Dave wrote himself are instructions to act on, not data to merge.
const ours = (id) => /^(vo-|fx-|t-\d+$|readme$)/.test(id) || id === sb.end?.voiceNote;
const his = Object.entries(notes).filter(([id, n]) => !ours(id) && n.text && !['rect', 'oval', 'pen', 'line', 'arrow', 'image'].includes(n.kind));
const strays = files.filter((f) => f !== 'Main.dc.html' && f !== sb.end?.canvasFile && !sb.steps.some((s) => new RegExp(`^S\\d+-${s.id}\\.dc\\.html$`).test(f)));

console.log(`\n${changes.length} change(s) read off the canvas`);
for (const c of changes) console.log(`\n  ${c.label}\n    was: ${JSON.stringify(c.from)}\n    now: ${JSON.stringify(c.to)}`);
if (his.length) { console.log(`\n${his.length} note(s) Dave added. Read each one and act on it:`); for (const [id, n] of his) console.log(`\n  [${id}] near x=${Math.round(n.x)} y=${Math.round(n.y)}\n    ${n.text.replace(/\n/g, '\n    ')}`); }
if (strays.length) console.log(`\nartboards Dave added: ${strays.join(', ')}. Open each and ask what it is for. An end page: set storyboard.json "end": { "canvasFile": "<file>", "voiceNote": "<its voice note id>" } and rerun.`);
if (problems.length) { console.log(`\n${problems.length} thing(s) to check by hand:`); for (const p of problems) console.log('  - ' + p); }
if (WRITE && changes.length) { for (const [, rel, body] of keep) { mkdirSync(`${DIR}/storyboard/boards`, { recursive: true }); writeFileSync(`${DIR}/${rel}`, body); } saveStoryboard(DIR, sb); console.log('\nstoryboard.json updated. Changed voice lines are re-narrated on the next narrate.mjs run; the rest keep their take.'); }
else if (changes.length) console.log('\n(dry run: pass --write to save these into storyboard.json)');
