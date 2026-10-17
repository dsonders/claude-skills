// Slides + narration + footage -> the narrated video.
//
//   node build-video.mjs <project-dir>
//
// Run build-slides.mjs and narrate.mjs first. Each card is held for the length
// of its narration; a card with footage plays the clip inside the phone frame and
// runs as long as the longer of the two.
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync, symlinkSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { resolve } from 'node:path';
import { loadStoryboard, allCards, seconds, ffmpeg, screenOf, cardOf, captionsOf, CAPTION_BAND } from './lib.mjs';

const DIR = resolve(process.argv[2] || '.');
const sb = loadStoryboard(DIR);
const { W: CW, H: CH } = cardOf(sb), SIZE = `${CW * 2}x${CH * 2}`;
const OUT = `${DIR}/out`, SLIDES = `${OUT}/slides`, LAYERS = `${OUT}/layers`, WORK = `${OUT}/segments`;
if (existsSync(WORK)) rmSync(WORK, { recursive: true });
mkdirSync(WORK, { recursive: true });

// 1.25 = QuickTime's "Fast", the pace Dave approved. Pitch is preserved.
const SPEED = sb.speed || 1.25;
const LEAD = 0.35 / SPEED, TAIL = 0.75 / SPEED;
// Where the screen sits on the card (1080 x 1920, or 1920 x 1080 when landscape) (card px x 2), set per card from
// screenOf(): the phone is { x: 205, y: 428, w: 670, h: 1452 } as before, a laptop crop
// sits wider. K = frame point -> video px.
let K, PH;
const place = (c) => { const g = screenOf(sb, c); K = g.k * 2; MW = Math.round(56 * K * (sb.format === 'focus' ? 1.3 : 1)); PH = { x: Math.round(g.x * 2), y: Math.round(g.y * 2), w: Math.floor(g.w * 2), h: Math.round(g.h * 2) }; };
const V = ['-c:v', 'libx264', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', '30'];
const A = ['-c:a', 'aac', '-b:a', '128k', '-ac', '2', '-ar', '48000'];
// card.pause = [{ before: word, nth, seconds }]: silence in the voice just before that word, so the
// screen gets time the narration does not (⛔ Dave 10/11: "Click Log In" happened too fast to see
// where Log In is). PAUSES holds the current card's, in narration seconds; every time below goes
// through tOut() so words, events and subtitles after a pause all move with it.
let PAUSES = [];
const pauseTotal = () => PAUSES.reduce((n, p) => n + p.sec, 0);
const tOut = (raw) => LEAD + raw / SPEED + PAUSES.filter((p) => p.at <= raw).reduce((n, p) => n + p.sec, 0);
async function pausesOf(c) {
  const out = [];
  for (const p of c.pause || []) {
    const ws = await wordsOf(c.id), key = p.before.toLowerCase().replace(/[^a-z0-9]/g, '');
    const hit = ws.filter((w) => w.w === key || w.w.startsWith(key))[(p.nth || 1) - 1];
    if (!hit) throw new Error(`card ${c.id}: pause before "${p.before}" (#${p.nth || 1}): word not heard`);
    out.push({ at: hit.t < 0.15 ? 0 : hit.t - 0.12, sec: p.seconds });
  }
  return out.sort((a, b) => a.at - b.at);
}
const voice = (n, extra = 0) => {
  // A pause before the card's first word is a later start, not a cut.
  const lead = PAUSES.filter((p) => p.at <= 0.001), mid = PAUSES.filter((p) => p.at > 0.001);
  // adelay only shifts timestamps: the MP4 then carries a HOLE, not silence, and a player or
  // decoder that closes holes plays the voice early, drifting further every card (⛔ Dave 10/11:
  // "the phone VO runs slightly ahead"). aresample async fills the hole with real silence.
  const tail = `adelay=${Math.round((LEAD + extra + lead.reduce((x, p) => x + p.sec, 0)) * 1000)}:all=1,aresample=async=1:first_pts=0,apad[a]`;
  if (!mid.length) return `[${n}:a]aresample=48000,atempo=${SPEED},${tail}`;
  const cuts = mid.map((p) => p.at / SPEED), k = cuts.length;
  let f = `[${n}:a]aresample=48000,atempo=${SPEED},asplit=${k + 1}${cuts.map((_, i) => `[s${i}]`).join('')}[s${k}]`;
  for (let i = 0; i <= k; i++) {
    const from = i ? cuts[i - 1] : 0, to = i < k ? cuts[i] : null;
    f += `;[s${i}]atrim=start=${from.toFixed(3)}${to != null ? `:end=${to.toFixed(3)}` : ''},asetpts=PTS-STARTPTS${i < k ? `,apad=pad_dur=${mid[i].sec}` : ''}[p${i}]`;
  }
  return f + `;${cuts.map((_, i) => `[p${i}]`).join('')}[p${k}]concat=n=${k + 1}:v=0:a=1,${tail}`;
};

// ── word timing ───────────────────────────────────────────────────────────────
// Taps are synced to the WORD that names them ("Tap Done" -> the finger lands on
// "Tap"). Word times come from Whisper on each narration clip, cached by take.
const WORDS = `${DIR}/narration/words.json`;
const wordCache = existsSync(WORDS) ? JSON.parse(readFileSync(WORDS, 'utf8')) : {};
async function wordsOf(id) {
  const wav = `${DIR}/narration/${id}.wav`;
  const h = createHash('sha256').update(readFileSync(wav)).digest('hex').slice(0, 16);
  if (wordCache[id]?.hash === h) return wordCache[id].words;
  if (!process.env.OPENAI_API_KEY) throw new Error('word timing needs OPENAI_API_KEY: run from the app folder with -r dotenv/config');
  const fd = new FormData();
  fd.append('file', new Blob([readFileSync(wav)], { type: 'audio/wav' }), 'a.wav');
  fd.append('model', 'whisper-1'); fd.append('response_format', 'verbose_json'); fd.append('timestamp_granularities[]', 'word');
  const r = await fetch('https://api.openai.com/v1/audio/transcriptions', { method: 'POST', headers: { authorization: `Bearer ${process.env.OPENAI_API_KEY}` }, body: fd });
  if (!r.ok) throw new Error('word timing failed: ' + r.status);
  const words = ((await r.json()).words || []).map((w) => ({ w: w.word.toLowerCase().replace(/[^a-z0-9]/g, ''), t: w.start }));
  wordCache[id] = { hash: h, words };
  writeFileSync(WORDS, JSON.stringify(wordCache, null, 1));
  return words;
}
/** Seconds into the card (before any extra voice delay) at which `word` (nth, 1-based) is spoken. */
async function wordAt(id, word, nth = 1) {
  const ws = await wordsOf(id), key = word.toLowerCase().replace(/[^a-z0-9]/g, '');
  const hits = ws.filter((w) => w.w === key || w.w.startsWith(key));
  if (!hits[nth - 1]) throw new Error(`card ${id}: the word "${word}" (#${nth}) was not heard in its narration`);
  return tOut(hits[nth - 1].t);
}

/**
 * Event-locked footage (Dave 2026-10-06: "the VO runs ahead, the edit needs to be snappier").
 * footage.events = [{ frame, word, nth } ..., { frame, end: true }]: each event frame
 * plays on the moment its word is spoken; the last { end: true } frame lands at the
 * card's end. The card is as long as its narration plus a short tail, never as long
 * as the raw take. Between two events the take plays at 1x and HOLDS just before the
 * next action when there is time to spare; when there is not, it speeds up (to 2x)
 * and past that JUMP-CUTS (first half, last half), which is invisible in a spinner.
 * Returns the source frame for every output frame (30 fps).
 */
const TAP_EARLY = 0.2;
const LEADIN = 15; // the finger marker shows ~0.45 s before a tap: keep those frames
function remap(events, startFrame, lastFrame, outFrames) {
  const seq = [];
  const span = (a, b, n) => {             // n output frames from source a..b
    const src = b - a;
    if (n <= 0) return;
    if (src <= 0) { for (let k = 0; k < n; k++) seq.push(a); return; }
    if (n >= src) {                         // time to spare: 1x, hold before the lead-in, lead-in
      const lead = Math.min(LEADIN, src), body = src - lead, hold = n - src;
      for (let k = 0; k < body; k++) seq.push(a + k);
      for (let k = 0; k < hold; k++) seq.push(a + body);
      for (let k = 0; k < lead; k++) seq.push(a + body + k);
    } else if (src <= 2 * n) {              // up to 2x: even speed-up
      for (let k = 0; k < n; k++) seq.push(Math.round(a + (k * src) / n));
    } else {                                // jump cut: first half, last half (the lead-in survives)
      const h = Math.floor(n / 2);
      for (let k = 0; k < h; k++) seq.push(a + k);
      for (let k = 0; k < n - h; k++) seq.push(b - (n - h) + k);
    }
  };
  let prevF = startFrame, prevT = 0;
  for (const e of events) {
    const t = Math.min(outFrames - 1, Math.max(prevT, Math.round(e.t * 30)));
    span(prevF, e.frame, t - prevT);
    prevF = e.frame; prevT = t;
  }
  span(prevF, lastFrame, outFrames - prevT);
  return seq.slice(0, outFrames);
}
// The finger marker, the same look the recordings draw (lib.mjs touchOn), at card scale:
// 56 frame px wide, so 96 px on a portrait phone card and smaller on a landscape one.
let MW = 96;
const marker = (c, x, y, from, to) => `overlay=x=${Math.round(PH.x + x * K - MW / 2)}:y=${Math.round(PH.y + y * K - MW / 2)}:enable='between(t,${from.toFixed(2)},${to.toFixed(2)})'`;
const ring = ([x, y, w, h], from, to) => `drawbox=x=${Math.round(PH.x + x * K - 7)}:y=${Math.round(PH.y + y * K - 7)}:w=${Math.round(w * K + 14)}:h=${Math.round(h * K + 14)}:color=0xffd23f:t=6:enable='${to == null ? `gte(t,${from.toFixed(2)})` : `between(t,${from.toFixed(2)},${to.toFixed(2)})`}'`;
// Subtitles (focus format): each sentence shows from its first spoken word to the next one.
// Sentence starts come from the Whisper word times; a word Whisper spells differently
// falls back to the sentence's share of the characters.
async function captionTimes(c, len) {
  const chunks = captionsOf(c);
  if (!chunks.length) return [];
  const ws = await wordsOf(c.id), norm = (w) => w.toLowerCase().replace(/[^a-z0-9]/g, '');
  const voiceEnd = tOut(seconds(`${DIR}/narration/${c.id}.wav`)), total = chunks.join(' ').length;
  const starts = [tOut(0) - 0.05]; // after any pause before the first word
  let chars = chunks[0].length + 1;
  for (let k = 1; k < chunks.length; k++) {
    // The sentence's first TWO words, nearest the estimate: one word ("The") also matches inside
    // the sentence before ("the top of the page").
    const [a, b2] = chunks[k].split(/\s+/).map(norm);
    const est = LEAD + (voiceEnd - LEAD) * (chars / total);
    const hits = ws.map((w, j) => (w.w === a && (!b2 || ws[j + 1]?.w === b2) ? tOut(w.t) : null)).filter((t) => t != null && t > starts[k - 1]);
    const best = hits.sort((x, y) => Math.abs(x - est) - Math.abs(y - est))[0];
    starts.push(best != null && Math.abs(best - est) < 2 ? best - 0.1 : est);
    chars += chunks[k].length + 1;
  }
  return chunks.map((_, k) => ({ k, from: starts[k], to: k + 1 < chunks.length ? starts[k + 1] : len + 1 }));
}
/** Adds the caption layers to a filter chain: returns the extra inputs and the new chain end. */
async function captionLayers(c, len, last, n) {
  if (sb.format !== 'focus' || !c.img) return { ins: [], chain: '', last, n };
  const ins = [], times = await captionTimes(c, len);
  let chain = '';
  for (const { k, from, to } of times) {
    ins.push(...still, '-i', `${LAYERS}/${c.id}-cap${k}.png`);
    chain += `;[${last}][${n}:v]overlay=x=0:y=${CAPTION_BAND.top * 2}:enable='between(t,${from.toFixed(2)},${to.toFixed(2)})'[c${n}]`; last = `c${n}`; n++;
  }
  return { ins, chain, last, n };
}
const still = ['-loop', '1', '-framerate', '30'];
// The card's arrow layer (build-slides): lands its tip on `at` and bounces back along its own
// direction, so an arrow from the left bounces sideways.
function arrowOverlay(c, at) {
  const { tip, dir } = JSON.parse(readFileSync(`${LAYERS}/${c.id}-arrow.json`, 'utf8'));
  const ax = Math.round(PH.x + at[0] * K - tip[0]), ay = Math.round(PH.y + at[1] * K - tip[1]);
  const b = (v) => (18 * v).toFixed(1), wave = 'abs(sin(PI*t*1.7))';
  return { png: `${LAYERS}/${c.id}-arrow.png`, xy: `x='${ax}-(${b(dir[0])})*${wave}':y='${ay}-(${b(dir[1])})*${wave}'` };
}

const cards = allCards(sb);
const list = [];
let total = 0;
for (const [i, c] of cards.entries()) {
  const n2 = String(i).padStart(2, '0');
  if (c.img) place(c);
  const slide = `${SLIDES}/${n2}-${c.id}.png`, wav = `${DIR}/narration/${c.id}.wav`, seg = `${WORK}/${n2}.mp4`;
  if (!existsSync(wav)) throw new Error(`no narration for ${c.id}: run narrate.mjs`);
  PAUSES = await pausesOf(c);
  let len = LEAD + seconds(wav) / SPEED + pauseTotal() + TAIL + (c.tail || 0); // tail: extra seconds after the voice, for the screen
  let kind = '';
  if (c.footage?.events) {
    const fo = c.footage, OUTF = Math.round(len * 30);
    const evs = [];
    for (const e of fo.events) {
      if (e.end) evs.push({ frame: e.frame, t: len - 0.35 });
      // plus: seconds after the word, for an action no word names. A finger tap (at) presses
      // TAP_EARLY before its word, so the screen is already reacting as the word is heard
      // (⛔ Dave 10/11: on the word exactly, "the taps aren't quite keeping up with the VO").
      else evs.push({ frame: e.frame, t: (await wordAt(c.id, e.word, e.nth)) + (e.plus || 0) - (e.at ? TAP_EARLY : 0) });
    }
    // Start so the first event plays at 1x: skip what came before it in the take.
    const first = evs[0];
    const start = Math.max(fo.from ?? 0, first.frame - Math.round(first.t * 30));
    const lastFrame = fo.to ?? evs[evs.length - 1].frame;
    const seq = remap(evs, start, lastFrame, OUTF);
    const dir = `${WORK}/${n2}-frames`; mkdirSync(dir, { recursive: true });
    seq.forEach((f, k) => symlinkSync(`${DIR}/footage/${fo.clip}/f${String(f).padStart(5, '0')}.jpg`, `${dir}/o${String(k).padStart(5, '0')}.jpg`));
    const rings = [];
    // rings: [{ box, word, nth, until, untilNth }]: a callout from that word on, or until another word.
    for (const r of fo.rings || []) rings.push(ring(r.box, await wordAt(c.id, r.word, r.nth), r.until ? (await wordAt(c.id, r.until, r.untilNth)) + 0.3 : null));
    // footage.arrow: { at: [x, y], until: word } -> the bouncing arrow on a control from the
    // card's start until that word (Dave 10/6: the camera button in card 11).
    // A video stream chain after the hole layer: [h] -> optional arrow -> optional finger taps -> [v].
    const ins = ['-framerate', '30', '-i', `${dir}/o%05d.jpg`, ...still, '-i', `${LAYERS}/${c.id}-hole.png`];
    let chain = '', last = 'h', n = 2;
    if (fo.arrow) {
      const until = fo.arrow.until ? (await wordAt(c.id, fo.arrow.until, fo.arrow.nth)) + 0.4 : len;
      const ao = arrowOverlay(c, fo.arrow.at);
      ins.push(...still, '-i', ao.png);
      chain += `;[${last}][${n}:v]overlay=${ao.xy}:enable='lt(t,${until.toFixed(2)})'[a${n}]`; last = `a${n}`; n++;
    }
    // An event with at: [x, y] (frame points) draws the finger marker on that control as the
    // take reaches it: for recordings that show no touches (the iOS Simulator).
    const taps = fo.events.map((e, k) => (e.at ? { at: e.at, t: evs[k].t } : null)).filter(Boolean);
    // Each tap plays the tap animation (build-slides layers/tap, 160 px, tap on its frame 15),
    // shifted so its tap frame lands on the event (⛔ Dave 10/11 "A + ring": no box on the button).
    for (const tp of taps) {
      const from = tp.t - 15 / 30;
      ins.push('-framerate', '30', '-i', `${LAYERS}/tap/t%03d.png`);
      chain += `;[${n}:v]setpts=PTS-STARTPTS+${from.toFixed(3)}/TB[tp${n}];[${last}][tp${n}]overlay=x=${Math.round(PH.x + tp.at[0] * K - 80)}:y=${Math.round(PH.y + tp.at[1] * K - 80)}:eof_action=pass[t${n}]`;
      last = `t${n}`; n++;
    }
    const cap = await captionLayers(c, len, last, n);
    ins.push(...cap.ins); chain += cap.chain; last = cap.last; n = cap.n;
    ins.push('-i', wav);
    ffmpeg([...ins, '-filter_complex',
      `[0:v]scale=${PH.w}:${PH.h}:flags=lanczos,setsar=1,tpad=stop_mode=clone:stop_duration=30[f];` +
      `color=black:s=${SIZE}:r=30[bg];[bg][f]overlay=${PH.x}:${PH.y}[u];[u][1:v]overlay=0:0${rings.length ? ',' + rings.join(',') : ''}[h]${chain};[${last}]null[v];${voice(n)}`,
      '-map', '[v]', '-map', '[a]', '-t', len.toFixed(2), ...V, ...A, seg]);
    kind = `(footage, ${evs.length} events, ${(seq.length / 30).toFixed(1)}s of a ${((lastFrame - start) / 30).toFixed(1)}s take)`;
  } else if (c.footage) {
    // footage: { clip, runs: [[firstFrame, frameCount], ...] } at 30 fps,
    //   sync: { frame, word, nth } -> that clip frame lands on that spoken word,
    //   rings: [{ box: [x,y,w,h], word, nth }] -> a callout drawn from that word on.
    const runs = c.footage.runs;
    const clipLen = runs.reduce((n, r) => n + r[1], 0) / 30;
    let pad = 0, extra = 0;
    if (c.footage.sync) {
      const { frame, word, nth } = c.footage.sync;
      let at = 0, acc = 0;
      for (const [start, count] of runs) { if (frame >= start && frame < start + count) { at = (acc + frame - start) / 30; break; } acc += count; }
      const said = await wordAt(c.id, word, nth);
      if (said > at) pad = said - at; else extra = at - said;
    }
    len = Math.max(len + extra, pad + clipLen);
    const inputs = runs.flatMap(([start]) => ['-framerate', '30', '-start_number', String(start), '-i', `${DIR}/footage/${c.footage.clip}/f%05d.jpg`]);
    const n = runs.length;
    const trims = runs.map(([, count], k) => `[${k}:v]trim=end_frame=${count},setpts=PTS-STARTPTS[r${k}]`).join(';');
    const joined = n > 1 ? `${runs.map((_, k) => `[r${k}]`).join('')}concat=n=${n}:v=1:a=0[fj]` : '[r0]null[fj]';
    const rings = [];
    for (const r of c.footage.rings || []) rings.push(ring(r.box, (await wordAt(c.id, r.word, r.nth)) + extra));
    const lead = pad > 0 ? `tpad=start_mode=clone:start_duration=${pad.toFixed(2)},` : '';
    ffmpeg([...inputs, ...still, '-i', `${LAYERS}/${c.id}-hole.png`, '-i', wav, '-filter_complex',
      `${trims};${joined};[fj]${lead}scale=${PH.w}:${PH.h}:flags=lanczos,setsar=1,tpad=stop_mode=clone:stop_duration=30[f];` +
      `color=black:s=${SIZE}:r=30[bg];[bg][f]overlay=${PH.x}:${PH.y}[u];[u][${n}:v]overlay=0:0${rings.length ? ',' + rings.join(',') : ''}[v];${voice(n + 1, extra)}`,
      '-map', '[v]', '-map', '[a]', '-t', len.toFixed(2), ...V, ...A, seg]);
    kind = `(footage${pad ? ` +${pad.toFixed(1)}s hold` : ''}${extra ? ` voice +${extra.toFixed(1)}s` : ''})`;
  } else {
    // A still card. tap: { at: [x, y], word, nth, hold } draws the finger on the
    // control from the word that names it (hold = seconds, or to the card's end).
    const base = c.arrow ? `${LAYERS}/${c.id}-noarrow.png` : sb.format === 'focus' && c.img ? `${LAYERS}/${c.id}-nocap.png` : slide;
    const ins = [...still, '-i', base];
    let chain = '[0:v]null[b0]', last = 'b0', k = 1;
    if (c.arrow) {
      const ao = arrowOverlay(c, Array.isArray(c.arrow) ? c.arrow : c.arrow.at);
      ins.push(...still, '-i', ao.png);
      chain += `;[${last}][${k}:v]overlay=${ao.xy}[b${k}]`; last = `b${k}`; k++;
    }
    if (c.tap) {
      const from = (await wordAt(c.id, c.tap.word || 'tap', c.tap.nth)) - 0.15;
      const to = c.tap.hold === 'end' ? len + 1 : from + (c.tap.hold || 0.9);
      ins.push(...still, '-i', `${LAYERS}/marker.png`);
      chain += `;[${k}:v]scale=${MW}:${MW}[m${k}];[${last}][m${k}]${marker(c, c.tap.at[0], c.tap.at[1], from, to)}[b${k}]`; last = `b${k}`; k++;
    }
    const cap = await captionLayers(c, len, last, k);
    ins.push(...cap.ins); chain += cap.chain; last = cap.last; k = cap.n;
    ins.push('-i', wav);
    ffmpeg([...ins, '-filter_complex', `${chain};[${last}]null[v];${voice(k)}`, '-map', '[v]', '-map', '[a]', '-t', len.toFixed(2), '-tune', 'stillimage', ...V, ...A, seg]);
    kind = [c.arrow && '(arrow)', c.tap && '(tap)'].filter(Boolean).join(' ');
  }
  total += len;
  list.push(`file '${seg}'`);
  console.log(n2, c.id, len.toFixed(2) + 's', kind);
}
writeFileSync(`${WORK}/list.txt`, list.join('\n'));
const out = `${OUT}/${sb.slug}.mp4`;
ffmpeg(['-f', 'concat', '-safe', '0', '-i', `${WORK}/list.txt`, '-c', 'copy', '-movflags', '+faststart', out]);
// A hole in the audio timestamps plays EARLY in players that close it (the v5 drift): refuse it.
const holes = execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'a', '-show_entries', 'packet=pts_time', '-of', 'csv=p=0', out], { encoding: 'utf8' })
  .split('\n').map(parseFloat).filter((n) => !Number.isNaN(n)).filter((t, i, a) => i && t - a[i - 1] > 0.05);
if (holes.length) { console.log(`FAIL the audio has ${holes.length} hole(s), first at ${holes[0].toFixed(2)}s: the voice will run ahead in some players`); process.exitCode = 1; }
const m = Math.floor(total / 60), s = Math.round(total % 60);
console.log(`video: ${m}:${String(s).padStart(2, '0')} -> ${out}`);
