// Claude cannot hear. This transcribes the finished video's sound and lines it
// up against the script, so a garbled or missing line is caught before Dave
// listens. It proves the WORDS, never the tone.
//
//   cd /Users/davidsonders/ro-bot/app
//   NODE_OPTIONS='-r dotenv/config' node <skill>/scripts/check-audio.mjs <project-dir>
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { loadStoryboard, ffmpeg } from './lib.mjs';

const DIR = resolve(process.argv[2] || '.');
const sb = loadStoryboard(DIR);
const src = `${DIR}/out/${sb.slug}.mp4`, mp3 = `${DIR}/out/segments/check.mp3`;
ffmpeg(['-i', src, '-vn', '-ac', '1', '-ar', '16000', '-b:a', '48k', mp3]);
const fd = new FormData();
fd.append('file', new Blob([readFileSync(mp3)], { type: 'audio/mpeg' }), 'a.mp3');
fd.append('model', 'whisper-1');
const r = await fetch('https://api.openai.com/v1/audio/transcriptions', { method: 'POST', headers: { authorization: `Bearer ${process.env.OPENAI_API_KEY}` }, body: fd });
if (!r.ok) throw new Error('transcription failed: ' + r.status);
const heard = (await r.json()).text;

const norm = (t) => t.toLowerCase().replace(/[^a-z0-9 ]+/g, ' ').replace(/\s+/g, ' ').trim().split(' ');
const bag = new Set(norm(heard));
let worst = 1;
for (const c of [{ id: 'cover', narration: sb.cover.narration }, ...sb.steps]) {
  const words = norm(c.narration).filter((w) => w.length > 3);
  const missing = words.filter((w) => !bag.has(w));
  const score = words.length ? 1 - missing.length / words.length : 1;
  worst = Math.min(worst, score);
  console.log(`${score >= 0.85 ? 'ok  ' : 'LOOK'} ${c.id.padEnd(22)} ${Math.round(score * 100)}%${missing.length ? '  not heard: ' + [...new Set(missing)].join(', ') : ''}`);
}
console.log('\nheard:\n' + heard);
console.log(`\nlowest card: ${Math.round(worst * 100)}%. Names and numbers are often written differently by the transcriber ("10th Gear", "40,000"); read the LOOK lines before calling them faults.`);
