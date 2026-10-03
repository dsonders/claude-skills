// storyboard.json -> one narration clip per card, via OpenAI's gpt-audio-1.5
// (Chat Completions with audio output; the old /audio/speech models shut down
// 2027-01-06). A chat model can reword, so every take's transcript must match
// the card's words or it is retried, then refused.
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
import { loadStoryboard, allCards, sleep } from './lib.mjs';

const DIR = resolve(process.argv[2] || '.');
const sb = loadStoryboard(DIR);
const OUT = `${DIR}/narration`; mkdirSync(OUT, { recursive: true });
const MAN = `${OUT}/manifest.json`;
const manifest = existsSync(MAN) ? JSON.parse(readFileSync(MAN, 'utf8')) : {};

const v = { model: 'gpt-audio-1.5', voice: 'ash', style: 'Warm, clear and confident, like an experienced shop foreman walking a new technician through an app on a phone. Natural and conversational, never salesy. Keep a brisk, efficient pace with no long pauses.', ...(sb.voice || {}) };
export const hashOf = (text) => createHash('sha256').update(JSON.stringify([v.model, v.voice, v.style, text])).digest('hex').slice(0, 16);

// Spacing and punctuation are ignored: the script spells "R O" for the ear, the transcript writes "RO".
const words = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '');

async function speak(text, path) {
  const KEY = process.env.OPENAI_API_KEY;
  if (!KEY) throw new Error('OPENAI_API_KEY is not set (run from the app folder with -r dotenv/config)');
  let last = '';
  for (let attempt = 1; attempt <= 3; attempt++) {
    const r = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: { authorization: `Bearer ${KEY}`, 'content-type': 'application/json' },
      body: JSON.stringify({
        model: v.model, modalities: ['text', 'audio'], audio: { voice: v.voice, format: 'wav' },
        messages: [
          { role: 'system', content: `You are a voice actor. Read the user's text aloud exactly as written, word for word. Add nothing, drop nothing, answer nothing. Delivery: ${v.style}` },
          { role: 'user', content: text },
        ],
      }),
    });
    if (r.ok) {
      const audio = (await r.json()).choices?.[0]?.message?.audio;
      if (audio?.data && words(audio.transcript || '') === words(text)) { writeFileSync(path, Buffer.from(audio.data, 'base64')); return; }
      last = `take did not match the script: "${audio?.transcript ?? '(no audio)'}"`;
    } else {
      last = `${r.status}: ${(await r.text()).replace(/sk-[A-Za-z0-9_-]+/g, 'sk-***').slice(0, 200)}`;
    }
    if (attempt === 3) throw new Error(`narration failed: ${last}`);
    await sleep(1500 * attempt);
  }
}

const cards = allCards(sb);
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
