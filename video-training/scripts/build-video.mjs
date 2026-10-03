// Slides + narration + footage -> the narrated video.
//
//   node build-video.mjs <project-dir>
//
// Run build-slides.mjs and narrate.mjs first. Each card is held for the length
// of its narration; a card with footage plays the clip inside the phone frame and
// runs as long as the longer of the two.
import { writeFileSync, mkdirSync, rmSync, existsSync } from 'node:fs';
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
const voice = (n) => `[${n}:a]aresample=48000,atempo=${SPEED},adelay=${Math.round(LEAD * 1000)}:all=1,apad[a]`;
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
    // footage: { clip: 'A-hold', runs: [[firstFrame, frameCount], ...] } at 30 fps
    const runs = c.footage.runs;
    len = Math.max(len, runs.reduce((n, r) => n + r[1], 0) / 30);
    const inputs = runs.flatMap(([start]) => ['-framerate', '30', '-start_number', String(start), '-i', `${DIR}/footage/${c.footage.clip}/f%05d.jpg`]);
    const n = runs.length;
    const trims = runs.map(([, count], k) => `[${k}:v]trim=end_frame=${count},setpts=PTS-STARTPTS[r${k}]`).join(';');
    const joined = n > 1 ? `${runs.map((_, k) => `[r${k}]`).join('')}concat=n=${n}:v=1:a=0[fj]` : '[r0]null[fj]';
    ffmpeg([...inputs, ...still, '-i', `${LAYERS}/${c.id}-hole.png`, '-i', wav, '-filter_complex',
      `${trims};${joined};[fj]scale=${PH.w}:${PH.h}:flags=lanczos,setsar=1,tpad=stop_mode=clone:stop_duration=30[f];` +
      `color=black:s=1080x1920:r=30[bg];[bg][f]overlay=${PH.x}:${PH.y}[u];[u][${n}:v]overlay=0:0[v];${voice(n + 1)}`,
      '-map', '[v]', '-map', '[a]', '-t', len.toFixed(2), ...V, ...A, seg]);
    kind = '(footage)';
  } else if (c.arrow) {
    // The arrow bounces on its target: tip at arrow[x, y] in phone px.
    const ax = Math.round(PH.x - 0.6 + c.arrow[0] * K - 60), ay = Math.round(PH.y + c.arrow[1] * K - 170);
    ffmpeg([...still, '-i', `${LAYERS}/${c.id}-noarrow.png`, ...still, '-i', `${LAYERS}/arrow.png`, '-i', wav, '-filter_complex',
      `[0:v][1:v]overlay=x=${ax}:y='${ay}-18*abs(sin(PI*t*1.7))'[v];${voice(2)}`,
      '-map', '[v]', '-map', '[a]', '-t', len.toFixed(2), ...V, ...A, seg]);
    kind = '(arrow)';
  } else {
    ffmpeg([...still, '-i', slide, '-i', wav, '-filter_complex', voice(1), '-map', '0:v', '-map', '[a]', '-t', len.toFixed(2), '-tune', 'stillimage', ...V, ...A, seg]);
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
