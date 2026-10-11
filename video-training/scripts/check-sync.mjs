// Claude cannot watch. This proves the PICTURE keeps time with the VOICE, the way
// check-audio proves the words:
//   1. the finished video's audio has no holes (a hole is played early by players and
//      decoders that close it, so the voice drifts ahead of the screen, card by card);
//   2. every action a line names: the card's own audio is transcribed, and the frame
//      at the START of that word is pulled from the video. On the sheet, each action
//      should already be happening (finger pressing, screen reacting) in its frame.
//
//   cd /Users/davidsonders/ro-bot/app
//   NODE_OPTIONS='-r dotenv/config' node <skill>/scripts/check-sync.mjs <project-dir>
//
// Writes out/sync-sheet.png. Look at it, and say in the hand-back that you did.
import { readFileSync, existsSync, mkdirSync, rmSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { resolve } from 'node:path';
import { loadStoryboard, allCards, ffmpeg, screenOf } from './lib.mjs';

const DIR = resolve(process.argv[2] || '.');
const sb = loadStoryboard(DIR);
const OUT = `${DIR}/out`, SEG = `${OUT}/segments`, TMP = `${OUT}/sync`;
if (existsSync(TMP)) rmSync(TMP, { recursive: true });
mkdirSync(TMP, { recursive: true });

// ── 1. holes in the audio ─────────────────────────────────────────────────────
const pts = execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'a', '-show_entries', 'packet=pts_time', '-of', 'csv=p=0', `${OUT}/${sb.slug}.mp4`], { encoding: 'utf8' })
  .split('\n').map(parseFloat).filter((n) => !Number.isNaN(n));
const holes = [];
for (let i = 1; i < pts.length; i++) if (pts[i] - pts[i - 1] > 0.05) holes.push([pts[i - 1], pts[i]]);
console.log(holes.length ? `FAIL audio has ${holes.length} hole(s): ${holes.slice(0, 5).map(([a, b]) => `${a.toFixed(2)}->${b.toFixed(2)}s`).join(', ')}` : 'ok   audio: no holes');

// ── 2. the frame at each named action's word ─────────────────────────────────
const norm = (w) => w.toLowerCase().replace(/[^a-z0-9]/g, '');
async function words(file) {
  const wav = `${TMP}/a.wav`;
  ffmpeg(['-i', file, '-vn', '-ac', '1', '-ar', '16000', wav]);
  const fd = new FormData();
  fd.append('file', new Blob([readFileSync(wav)], { type: 'audio/wav' }), 'a.wav');
  fd.append('model', 'whisper-1'); fd.append('response_format', 'verbose_json'); fd.append('timestamp_granularities[]', 'word');
  const r = await fetch('https://api.openai.com/v1/audio/transcriptions', { method: 'POST', headers: { authorization: `Bearer ${process.env.OPENAI_API_KEY}` }, body: fd });
  if (!r.ok) throw new Error('transcription failed: ' + r.status);
  return ((await r.json()).words || []).map((w) => ({ w: norm(w.word), t: w.start }));
}
const tiles = [];
for (const [i, c] of allCards(sb).entries()) {
  const evs = [...(c.footage?.events || []).filter((e) => e.word), ...(c.tap ? [{ word: c.tap.word || 'tap', nth: c.tap.nth }] : [])];
  if (!evs.length) continue;
  const seg = `${SEG}/${String(i).padStart(2, '0')}.mp4`;
  const ws = await words(seg), g = screenOf(sb, c);
  const crop = `crop=${Math.floor(g.w * 2)}:${Math.round(g.h * 2)}:${Math.round(g.x * 2)}:${Math.round(g.y * 2)}`;
  for (const e of evs) {
    const key = norm(e.word), hit = ws.filter((w) => w.w === key || w.w.startsWith(key))[(e.nth || 1) - 1];
    const label = `${c.id}  "${e.word}"${e.plus ? ` +${e.plus}s` : ''}`;
    if (!hit) { console.log(`LOOK ${label}: word not heard in the card's audio`); continue; }
    const at = hit.t + (e.plus || 0), png = `${TMP}/t${String(tiles.length).padStart(3, '0')}.png`;
    ffmpeg(['-ss', at.toFixed(2), '-i', seg, '-frames:v', '1', '-vf', `${crop},scale=540:440:force_original_aspect_ratio=decrease,pad=560:474:(ow-iw)/2:34:black,drawtext=fontfile=/System/Library/Fonts/Helvetica.ttc:text='${label.replace(/[':]/g, '')}':x=6:y=8:fontsize=18:fontcolor=white`, png]);
    tiles.push(png);
    console.log(`ok   ${label} at ${at.toFixed(2)}s into the card`);
  }
}
if (tiles.length) {
  // every tile is 560 x 474 (made so above), so laptop and phone frames share one grid
  ffmpeg(['-framerate', '1', '-i', `${TMP}/t%03d.png`, '-vf', `tile=5x${Math.ceil(tiles.length / 5)}:padding=6:color=0x333333`, '-frames:v', '1', `${OUT}/sync-sheet.png`]);
  console.log(`\nsheet: ${OUT}/sync-sheet.png (${tiles.length} actions). Each frame is the instant its word starts: the press or click should already be on screen.`);
}
if (holes.length) process.exitCode = 1;
