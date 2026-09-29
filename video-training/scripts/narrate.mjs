// storyboard.json -> one narration clip per card, via OpenAI text to speech.
// A clip is regenerated ONLY when its words (or the voice settings) changed, so
// an approved take survives every later rebuild.
//
//   cd /Users/davidsonders/ro-bot/app
//   NODE_OPTIONS='-r dotenv/config' node <skill>/scripts/narrate.mjs <project-dir>
//
// The key is read from the environment and never printed.
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';
import { loadStoryboard, sleep } from './lib.mjs';

const DIR = resolve(process.argv[2] || '.');
const sb = loadStoryboard(DIR);
const OUT = `${DIR}/narration`; mkdirSync(OUT, { recursive: true });
const MAN = `${OUT}/manifest.json`;
const manifest = existsSync(MAN) ? JSON.parse(readFileSync(MAN, 'utf8')) : {};

const v = { model: 'gpt-4o-mini-tts', voice: 'ash', style: 'Warm, clear and confident, like an experienced shop foreman walking a new technician through an app on a phone. Natural and conversational, never salesy. Keep a brisk, efficient pace with no long pauses.', ...(sb.voice || {}) };
export const hashOf = (text) => createHash('sha256').update(JSON.stringify([v.model, v.voice, v.style, text])).digest('hex').slice(0, 16);

async function speak(text, path) {
  const KEY = process.env.OPENAI_API_KEY;
  if (!KEY) throw new Error('OPENAI_API_KEY is not set (run from the app folder with -r dotenv/config)');
  for (let attempt = 1; attempt <= 3; attempt++) {
    const r = await fetch('https://api.openai.com/v1/audio/speech', {
      method: 'POST',
      headers: { authorization: `Bearer ${KEY}`, 'content-type': 'application/json' },
      body: JSON.stringify({ model: v.model, voice: v.voice, input: text, instructions: v.style, response_format: 'wav' }),
    });
    if (r.ok) { writeFileSync(path, Buffer.from(await r.arrayBuffer())); return; }
    const msg = (await r.text()).replace(/sk-[A-Za-z0-9_-]+/g, 'sk-***').slice(0, 200);
    if (attempt === 3) throw new Error(`text to speech ${r.status}: ${msg}`);
    await sleep(1500 * attempt);
  }
}

const cards = [{ id: 'cover', narration: sb.cover.narration }, ...sb.steps];
let made = 0;
for (const c of cards) {
  if (!c.narration) throw new Error(`card ${c.id} has no narration`);
  const h = hashOf(c.narration), file = `${OUT}/${c.id}.wav`;
  if (manifest[c.id]?.hash === h && existsSync(file)) continue;
  if (process.env.DRY) { console.log('  would regenerate', c.id); continue; }
  await speak(c.narration, file);
  manifest[c.id] = { hash: h, text: c.narration };
  writeFileSync(MAN, JSON.stringify(manifest, null, 1));
  made++;
  console.log('  narrated', c.id);
}
console.log(`narration: ${made} new, ${cards.length - made} kept`);
