// Slides + narration + footage -> the narrated video.
//
//   node build-video.mjs <project-dir>
//
// Run build-slides.mjs and narrate.mjs first. Each card is held for the length
// of its narration; a card with footage plays the clip inside the phone frame and
// runs as long as the longer of the two.
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';
import { loadStoryboard, allCards, seconds, ffmpeg } from './lib.mjs';

const DIR = resolve(process.argv[2] || '.');
const sb = loadStoryboard(DIR);
const OUT = `${DIR}/out`, SLIDES = `${OUT}/slides`, LAYERS = `${OUT}/layers`, WORK = `${OUT}/segments`;
if (existsSync(WORK)) rmSync(WORK, { recursive: true });
mkdirSync(WORK, { recursive: true });

// 1.25 = QuickTime's "Fast", the pace Dave approved. Pitch is preserved.
const SPEED = sb.speed || 1.25;
const LEAD = 0.35 / SPEED, TAIL = 0.75 / SPEED;
// Where the phone screen sits on the 1080 x 1920 card (card px x 2).
const K = 0.86 * 2, PH = { x: 205, y: 428, w: 670, h: 1452 };
const V = ['-c:v', 'libx264', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', '30'];
const A = ['-c:a', 'aac', '-b:a', '128k', '-ac', '2', '-ar', '48000'];
const voice = (n, extra = 0) => `[${n}:a]aresample=48000,atempo=${SPEED},adelay=${Math.round((LEAD + extra) * 1000)}:all=1,apad[a]`;

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
  return LEAD + hits[nth - 1].t / SPEED;
}
// The finger marker, the same look the recordings draw (lib.mjs touchOn), at card scale.
const MW = Math.round(56 * K);
const marker = (c, x, y, from, to) => `overlay=x=${Math.round(PH.x + x * K - MW / 2)}:y=${Math.round(PH.y + y * K - MW / 2)}:enable='between(t,${from.toFixed(2)},${to.toFixed(2)})'`;
const ring = ([x, y, w, h], from) => `drawbox=x=${Math.round(PH.x + x * K - 7)}:y=${Math.round(PH.y + y * K - 7)}:w=${Math.round(w * K + 14)}:h=${Math.round(h * K + 14)}:color=0xffd23f:t=6:enable='gte(t,${from.toFixed(2)})'`;
const still = ['-loop', '1', '-framerate', '30'];

const cards = allCards(sb);
const list = [];
let total = 0;
for (const [i, c] of cards.entries()) {
  const n2 = String(i).padStart(2, '0');
  const slide = `${SLIDES}/${n2}-${c.id}.png`, wav = `${DIR}/narration/${c.id}.wav`, seg = `${WORK}/${n2}.mp4`;
  if (!existsSync(wav)) throw new Error(`no narration for ${c.id}: run narrate.mjs`);
  let len = LEAD + seconds(wav) / SPEED + TAIL;
  let kind = '';
  if (c.footage) {
    // footage: { clip, runs: [[firstFrame, frameCount], ...] } at 30 fps,
    //   sync: { frame, word, nth } -> that clip frame lands on that spoken word,
    //   rings: [{ box: [x,y,w,h], word, nth }] -> a callout drawn from that word on.
    const runs = c.footage.runs;
    const clipLen = runs.reduce((n, r) => n + r[1], 0) / 30;
    let pad = 0, extra = 0;
    if (c.footage.sync) {
      const { frame, word, nth } = c.footage.sync;
      let at = 0, acc = 0;
      for (const [start, count] of runs) { if (frame >= start && frame < start + count) { at = acc + (frame - start) / 30; break; } acc += count; }
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
      `color=black:s=1080x1920:r=30[bg];[bg][f]overlay=${PH.x}:${PH.y}[u];[u][${n}:v]overlay=0:0${rings.length ? ',' + rings.join(',') : ''}[v];${voice(n + 1, extra)}`,
      '-map', '[v]', '-map', '[a]', '-t', len.toFixed(2), ...V, ...A, seg]);
    kind = `(footage${pad ? ` +${pad.toFixed(1)}s hold` : ''}${extra ? ` voice +${extra.toFixed(1)}s` : ''})`;
  } else {
    // A still card. tap: { at: [x, y], word, nth, hold } draws the finger on the
    // control from the word that names it (hold = seconds, or to the card's end).
    const base = c.arrow ? `${LAYERS}/${c.id}-noarrow.png` : slide;
    const ins = [...still, '-i', base];
    let chain = '[0:v]null[b0]', last = 'b0', k = 1;
    if (c.arrow) {
      const ax = Math.round(PH.x - 0.6 + c.arrow[0] * K - 60), ay = Math.round(PH.y + c.arrow[1] * K - 170);
      ins.push(...still, '-i', `${LAYERS}/arrow.png`);
      chain += `;[${last}][${k}:v]overlay=x=${ax}:y='${ay}-18*abs(sin(PI*t*1.7))'[b${k}]`; last = `b${k}`; k++;
    }
    if (c.tap) {
      const from = (await wordAt(c.id, c.tap.word || 'tap', c.tap.nth)) - 0.15;
      const to = c.tap.hold === 'end' ? len + 1 : from + (c.tap.hold || 0.9);
      ins.push(...still, '-i', `${LAYERS}/marker.png`);
      chain += `;[${last}][${k}:v]${marker(c, c.tap.at[0], c.tap.at[1], from, to)}[b${k}]`; last = `b${k}`; k++;
    }
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
const m = Math.floor(total / 60), s = Math.round(total % 60);
console.log(`video: ${m}:${String(s).padStart(2, '0')} -> ${out}`);
