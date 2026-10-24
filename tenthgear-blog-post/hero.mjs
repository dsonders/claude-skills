// Generate a blog hero with Nano Banana Pro on Fal (~$0.15 per image) and save the raw image.
//   NODE_OPTIONS='-r /Users/davidsonders/ro-bot/app/node_modules/dotenv/config' DOTENV_CONFIG_PATH=/Users/davidsonders/ro-bot/app/.env DOTENV_CONFIG_QUIET=true \
//     node ~/.claude/skills/tenthgear-blog-post/hero.mjs <prompt.txt> <out-without-ext> [n=1] [source.png]
// With source.png it runs the /edit endpoint instead: keeps the composition, applies the prompt as a fix
// (garbled text, a stray element). Writes <out>-1.png, <out>-2.png, ... Never prints the key.
import fs from "node:fs";

const [promptFile, out, n = "1", source] = process.argv.slice(2);
if (!promptFile || !out) throw new Error("usage: hero.mjs <prompt.txt> <out-without-ext> [n]");
const KEY = process.env.FAL_KEY;
if (!KEY) throw new Error("FAL_KEY not set");
const H = { Authorization: `Key ${KEY}`, "Content-Type": "application/json" };
const scrub = (s) => String(s).split(KEY).join("***");

const input = { prompt: fs.readFileSync(promptFile, "utf8").trim(), aspect_ratio: "16:9", resolution: "2K", num_images: Number(n), output_format: "png" };
if (source) input.image_urls = [`data:image/png;base64,${fs.readFileSync(source).toString("base64")}`];
const model = source ? "fal-ai/nano-banana-pro/edit" : "fal-ai/nano-banana-pro";
let res = await fetch(`https://queue.fal.run/${model}`, { method: "POST", headers: H, body: JSON.stringify(input) });
if (!res.ok) throw new Error(scrub(`submit HTTP ${res.status} ${(await res.text()).slice(0, 400)}`));
const job = await res.json();
for (;;) {
  await new Promise((r) => setTimeout(r, 5000));
  const s = await (await fetch(job.status_url, { headers: H })).json();
  if (s.status === "COMPLETED") break;
  if (s.status !== "IN_QUEUE" && s.status !== "IN_PROGRESS") throw new Error(scrub(JSON.stringify(s).slice(0, 400)));
}
res = await fetch(job.response_url, { headers: H });
if (!res.ok) throw new Error(scrub(`result HTTP ${res.status} ${(await res.text()).slice(0, 400)}`));
const { images = [] } = await res.json();
if (!images.length) throw new Error("no images returned");
for (const [i, img] of images.entries()) {
  const f = `${out}-${i + 1}.png`;
  fs.writeFileSync(f, Buffer.from(await (await fetch(img.url)).arrayBuffer()));
  console.log(`saved ${f}`);
}
