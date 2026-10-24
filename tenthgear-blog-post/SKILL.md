---
name: tenthgear-blog-post
description: End-to-end workflow for producing a new blog post on the TenthGear marketing site at /ro-bot/website/. Covers ideation, drafting, hero image, infographic, SEO/AEO optimization, two-way internal linking, distribution drafts, build verification, and deploy. Use ONLY when working in /ro-bot/website/ — the blog frontmatter schema, Astro content collection, and deploy pipeline described here are website-specific.
---

# TenthGear Blog Post Workflow

**Scope:** This skill is specific to the TenthGear marketing website at `/ro-bot/website/`. The Astro content collection in `src/content/blog/`, the frontmatter schema in `src/content.config.ts`, the Netlify deploy step, and the build-verification commands all assume that subproject's structure. Do not invoke from `app/` or `GTM/`.

End-to-end workflow to produce and ship a blog post on the TenthGear marketing site (`tenthgear.ai`). The goal is to publish something high-quality in one session with the user only in the loop at 6 clear checkpoints.

**Before drafting, read `/ro-bot/shared/product-facts.md` and `/ro-bot/shared/brand.md`** to ensure the post doesn't propagate stale facts or use banned words.

## When to use

Use this skill when the user asks to:
- Add, write, or draft a new blog post
- Come up with blog post ideas
- "Do a blog post about X"
- "Write up a post on Y"

Do not use this skill for:
- Editing an existing post (just do it directly)
- Homepage / product page copy changes
- Marketing strategy discussions (use `marketing-plan` skill)

## Core Principles

- **Phases are sequential, but within a phase you automate everything.** The user is only in the loop at the 5 checkpoints below.
- **Never skip the voice/tone rules.** CLAUDE.md bans specific words and punctuation. Violating this is the fastest way to make a post sound like an LLM wrote it.
- **Always target a primary keyword.** Without a keyword, a post is just vibes. Pick one before drafting.
- **Two-way internal linking.** New posts should link TO older posts AND the skill should update older posts to link TO the new one.
- **A post isn't done until it's deployed AND has distribution drafts ready.**

## Mandatory Reading Before Starting

Read these files before Phase 1:
- `AGENTS.md` (the website's shared rulebook — `CLAUDE.md` is a stub that imports it; brand + banned words live in `../shared/brand.md`)
- `src/content.config.ts` (current frontmatter schema)
- `src/layouts/BlogPost.astro` (how frontmatter renders)

---

## Phase 1: Ideate

### Auto-steps

1. **Read all existing posts** — `src/content/blog/*.md`. For each, extract: slug, title, date, category, tags, primaryKeyword, pillar.
2. **Categorize coverage** by the three product pillars (Find More Work / Sell More Work / Get Paid for More Work) plus founder/social-proof posts.
3. **Identify gaps** — topics not yet covered relative to the target audience (Fixed Ops Directors at small-to-medium dealer groups). Reference CLAUDE.md Part 1 for audience details.
4. **Propose 5 ideas** with the following structure for each:
   - Working title
   - Angle (1-2 sentences)
   - Pillar
   - Audience (Fixed Ops Director / Service Manager / Technician / Broad)
   - **Primary keyword** and 2-3 secondary keywords
   - **Search intent** (informational / commercial / transactional / navigational)
   - Why it's a gap worth filling
5. **Flag one recommendation** — usually the one with the best combination of audience fit, search intent, and timeliness. If there's a timely hook (Q1 close, industry event, recent news), lean into it.

### Checkpoint 1

> Present the 5 ideas to the user. Ask which one to write (or whether they want more options).

---

## Phase 2: Draft

### Pre-draft research (audience voice)

Before drafting audience-specific content, research how the audience actually talks. Industry tropes are usually wrong, and a draft built from tropes reads generic and gets called out.

For Fixed Ops / technician content, sources in order of value:
- **Reddit:** r/MechanicAdvice, r/AskMechanics, r/Justrolledintotheshop, r/askcarsales. Search the topic plus "flat rate", "warranty pay", "leaving the dealer", "dispatch", "skating".
- **WrenchWay annual technician survey** — primary source for compensation-preference and "why I left" data.
- **Tech forums:** Humble Mechanic, ScannerDanner, brand-specific Nation forums. These mirror Reddit voice as a secondary source.
- **Industry reporting:** Auto Dealer Today, Automotive News Fixed Ops Journal, Digital Dealer.

**Reddit access (as of 2026-10-13):** curl/WebFetch get 403, and live reddit.com now sends even headed real Chrome to a login wall and a CAPTCHA (do not solve it). The route that works is **Wayback Machine snapshots** of thread URLs (`https://web.archive.org/web/2025/https://www.reddit.com/r/{sub}/comments/...`); find thread URLs with WebSearch (indexes Reddit poorly) or the Wayback CDX index `web.archive.org/cdx/search/cdx?url=reddit.com/r/{sub}/comments/*` (slow, rate-limited). Snapshots lack per-comment permalinks, so cite by username. Coverage is thin (one good thread is typical); say so in the draft notes. Try the older Playwright same-origin fetch first only if Reddit's wall lifts. Target subs: r/serviceadvisors, r/askcarsales, r/MechanicAdvice, r/AskMechanics, r/Justrolledintotheshop, r/Service_Technicians.

Want: top 5-7 reasons the audience does X in their own words, plus what is non-obvious or contradicts conventional wisdom. Full write-up: `shared/lessons-learned/reddit-403-browser-fetch.md`.

Verified ground truth for dealership-tech content (from past research; do not re-litigate in the draft):
- Pay is **flat-rate** (book hours × flag rate), NOT hourly. Variance is the pain, not the rate.
- The villain in tech voice is the service writer/advisor, NOT the customer.
- "Younger techs want phone-first tools" is marketing fluff. Techs of every age hate friction.
- Warranty book times are tight; warranty documentation is a wage-clawback risk when claims get denied.

### Auto-steps

1. **Assign sequential asset number** — look at `public/blog-assets/` for the highest numeric prefix (e.g., `8-warranty-audit-playbook`) and increment.
2. **Generate slug** — lowercase, hyphenated, keyword-bearing, under 60 chars. Avoid stopwords at the start.
3. **Set date** — today's date in `YYYY-MM-DD` format.
4. **Write the post** following these rules:

#### Voice and tone (from CLAUDE.md)
- 800-1200 words
- Direct, second-person ("you already know..."), shop-floor language
- Use words from the shop: RO, wrench time, bays, 3Cs, stories, warranty, flag time
- Lead with outcomes, not features
- Confident without being salesy
- Use "AI" sparingly — it's a capability, not the headline

#### Banned words/phrases (hard no)
- revolutionize, revolutionary, game-changer, cutting-edge, state-of-the-art
- seamless, seamlessly, leverage (as verb), harness the power of
- empower, empowering, robust
- solution (as standalone noun — be specific)
- Em dashes (`—`) and en dashes (`–`) — use commas, periods, or restructure
- Emojis — anywhere, ever
- "Let's dive in", "In today's fast-paced world", "It's not just X, it's Y"
- "Unlock", "elevate", "transform" (used generically)

#### AEO-friendly structure (do these every time)
- **TL;DR block** near the top (2-3 sentences, 30-50 words) that directly answers the post's core question. LLMs extract these. Place after the hook paragraph.
- **At least one H2 phrased as a natural-language question** people would type ("What do warranty auditors look for?"). Question-form H2s get cited more often by LLM-based search.
- **Define key terms** in a sentence before using them (e.g., "The 3Cs — complaint, cause, correction — are..."). LLMs love definitional content.
- **Structured content** where the topic allows: numbered lists, tables, definition blocks. These tokenize better than prose.
- **Cite external sources** with outbound links where natural — industry reports, manufacturer docs, BLS. Credibility signal for both Google and LLMs.
- **Answer the core question in the first 100 words.** Old Google advice that applies directly to AEO now.

#### Internal linking (two directions)
- From the new post: link to 1-2 related existing posts using descriptive anchor text. Identify candidates from the Phase 1 existing-posts read.
- (Phase 4 will add links FROM older posts TO this new one — don't forget.)

#### Frontmatter (required fields)
```yaml
---
title: "{title}"
date: "{YYYY-MM-DD}"
category: "{category}"
tags: [{tags}]
excerpt: "{1-2 sentence hook, different from metaDescription}"
metaDescription: "{150-160 char, click-through optimized}"
primaryKeyword: "{primary keyword}"
secondaryKeywords: [{2-3 keywords}]
---
```

Note: `ogImage` is optional. Set it if you want a custom social share image different from the hero. Otherwise the site default (`/browser.png`) is used.

Note: `updatedDate` is NOT set on new posts. Only set it when a post is genuinely revised later.

#### Hero image concept
Propose a hero image concept with enough detail that you could hand it to a photographer or image-gen tool. Reference the editorial style of Jobber and WSJ feature photography. Avoid AI purple/neon, pastel, cartoon illustrations, and generic stock auto shop photos.

#### Infographic concept (optional)
If the post has a section with compelling math or a data story, propose an inline HTML infographic instead of prose. Use brand colors from `tailwind.config.mjs`:
- `bg-surface` / `border-gray-200` for stat cards
- `text-navy` for big numbers
- `bg-teal` with `text-white` for the payoff card
- `border-red-500 bg-red-50` for risk callouts (only when semantically warranted)
- Wrap the whole thing in `<div class="not-prose my-10">` to escape prose styles

#### Content upgrade suggestion (soft flag)
If the post naturally pairs with a downloadable asset (checklist, template, calculator, scorecard), mention it. Example: a warranty audit post pairs with a "Warranty Audit Self-Check Checklist" PDF. The PDF creation stays manual but flagging it helps the user capture leads.

### Checkpoint 2

> Present the full draft in the chat (including frontmatter), plus the hero concept and infographic concept. Ask the user to approve or request edits. Loop until approved.

---

## Phase 3: Assets

### Auto-steps

1. **Write a Nano Banana prompt** for the hero image, tuned to:
   - Editorial, documentary photo style (not illustration)
   - Specific composition, lighting, and color palette (muted, slightly desaturated)
   - Named objects and text on signage/papers (Nano Banana handles short text reasonably well)
   - Shallow depth of field with intentional focus point
   - Explicit "no hands in frame, no logos, no AI-style gradient lighting"
   - 16:9 aspect ratio
   - Reference WSJ / editorial photography, never stock photo
2. **Frame the subject for a 2:1 center crop** (the desktop hero). Fal output has no watermark, so nothing at the edges needs to be expendable.

3. **Generate the hero yourself — don't hand Dave the prompt.** Run it as soon as the first HTML mockup is built (Phase 4 step 1–2), so his first look at the page already has the real image. Save the prompt to the scratchpad, then (~$0.15 per image on Fal, key in `app/.env`):
   ```bash
   NODE_OPTIONS='-r /Users/davidsonders/ro-bot/app/node_modules/dotenv/config' DOTENV_CONFIG_PATH=/Users/davidsonders/ro-bot/app/.env DOTENV_CONFIG_QUIET=true \
     node ~/.claude/skills/tenthgear-blog-post/hero.mjs {scratchpad}/hero-prompt.txt {scratchpad}/hero 2
   ```
   Look at both results yourself (Read the PNGs). Reject garbled text, hands, logos, or a subject that won't survive the 2:1 crop. Process the best one (step 4) straight into `hero.jpg`.

   **Fix a near-miss with an edit, not a regenerate.** A fresh generation throws away the composition. Pass the image as a 4th argument and the script uses `nano-banana-pro/edit`, which keeps the composition and applies the prompt as a fix (prompts in the iteration table below). For garbled text, spell out every label exactly:
   ```bash
   ... hero.mjs {scratchpad}/fix-prompt.txt {scratchpad}/hero-fix 1 {scratchpad}/hero-1.png
   ```

### Checkpoint 3

> Dave reviews the hero in the mockup itself. If he wants changes, run an edit pass with a prompt from the iteration table and replace `hero.jpg`. Never put the prompt on the page.

### Auto-steps (image processing)

4. **Resize and compress with sips** (Fal returns 2752x1536 with no watermark, so no crop):
   ```bash
   sips -Z 1600 -s format jpeg -s formatOptions 82 {source} --out {dest}
   ```
   Lands around 270 KB; keep it under 500 KB.
5. **Save with clean name** to `public/blog-assets/{N}-{slug}/hero.jpg` (or a descriptive filename like `warranty-audit-letter.jpg`).

---

## Phase 4: Integrate

### Auto-steps

1. **Create the markdown file** at `src/content/blog/{slug}.md` with frontmatter and body from Phase 2.
2. **Wire in the hero image through frontmatter, never in the body** (website PR #147). `BlogPost.astro` renders it: on desktop a 2:1 crop rising into the navy header, on phones full width 16:9. Write the Nano Banana prompt so the subject survives a 2:1 center crop.
   ```yaml
   heroImage: "/blog-assets/{N}-{slug}/hero.jpg"
   heroAlt: "{alt with primary keyword if natural}"
   heroPosition: "50% 35%"   # optional, only if the 2:1 crop cuts the subject
   ```
   Changing the content schema needs a dev-server restart AND may still serve stale data; verify with `npm run build` + `npx astro preview` if the hero doesn't appear.

   **The first mockup triggers the hero.** As soon as the page builds, run Phase 3 step 3 and drop the processed image at this path before showing Dave. No placeholder image, no hero prompt on the page.
3. **Build the infographic inline** (if planned in Phase 2) using brand colors and `not-prose` wrapper. See existing example in `src/content/blog/warranty-audit-playbook.md` for a reference pattern.
4. **Two-way internal linking** — identify 1-2 older posts that should link TO this new one. Propose specific sentences to add or edit. Add them.
5. **Run `npm run build`** and verify:
   - Build passes with 0 errors
   - `/blog/{slug}/` appears in the page list
   - `grep` the built HTML for the primary keyword and any infographic key values to confirm they rendered
6. **Append to keyword tracker** — add a row to `docs/seo/keyword-tracker.md` with slug, publish date, primary keyword, and placeholders for rank tracking.
7. **Start the dev server** in the background: `npm run dev` with `run_in_background: true`.
8. **Visual verification (render before claiming success).** Do not pass the post to the user with phrases like "this should match your reference." Render via headless Chrome and read the screenshot first. If the user has to call out a visual problem you could have caught by looking, you wasted a round-trip.

   One-time setup (in `/tmp` so it doesn't pollute the repo):
   ```bash
   cd /tmp && mkdir -p pw-tools && cd pw-tools && npm install --silent playwright
   ```

   Per-iteration screenshot script (saves the design block, prints its rendered dimensions for layout math):
   ```js
   // /tmp/pw-tools/inspect.mjs
   import { chromium } from 'playwright';
   const browser = await chromium.launch({ channel: 'chrome' }); // uses installed Chrome, no download
   const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
   await page.goto('http://localhost:4321/blog/{slug}/', { waitUntil: 'networkidle' });
   const block = page.locator('.bg-surface.rounded-xl').first(); // adjust selector per post
   await block.scrollIntoViewIfNeeded();
   console.log('Block:', JSON.stringify(await block.boundingBox()));
   await block.screenshot({ path: '/tmp/pw-tools/block.png' });
   await browser.close();
   ```
   Run with `cd /tmp/pw-tools && node inspect.mjs`, then `Read /tmp/pw-tools/block.png` to see the render. For image-cropping math when using `object-cover`: container ratio < image ratio means image upscales to fill width, cropping vertically. Use `object-top` to preserve the top of the image (e.g., a meme caption).

9. **Share `http://localhost:4321/blog/{slug}/` with the user** for their visual review.

### Checkpoint 4

> User reviews on localhost. They may request style tweaks (image size, infographic colors, copy edits). Hot reload handles this live. Loop until approved.

### Auto-steps (after approval)

10. **Stop the dev server** — `pkill -f "astro dev"`.

---

## Phase 4.5: Distribution drafts

### Auto-steps

Create `docs/distribution/{slug}.md` with:

### LinkedIn post draft
- 1200 chars max
- Hook in the first line (the most punchy stat or a one-sentence provocation)
- 3-5 short paragraphs with line breaks between them
- No links in the body of a LinkedIn post (LinkedIn down-ranks them). Put the link in the first comment instead, and note that in the doc.
- End with a soft CTA: "Full post in the comments" or similar
- Match Dave's voice: direct, no emojis, no "Excited to share..."

### Email announcement draft
**Write it in Dave's newsletter voice: model it on the last email he sent** (the newest `docs/distribution/{slug}.md` before this one; skip the `archive/` folder). He rewrote the last two drafts into this shape:
1. Opener: "In the latest installment of the TenthGear blog, we're {going deep on / building} {topic}."
2. The metric stores track and why it misleads: "Most stores track X. Great metric, in theory. But..."
3. What the post is: "The new post is {what it is}. It also covers..."
4. The free printable, if there is one, with a light nod to the app doing it faster.
5. `Read it here: {link}`, then `Dave`.

Lead with the post, not with a provocation; save the hook-style opening for LinkedIn.

`scripts/newsletter.mjs` parses this section verbatim (Phase 6), so keep the exact shape:
- `**Subject:**` line (under 50 chars) and `**Preview text:**` line (under 90 chars)
- `**Body:**` then the body in ONE fenced code block: 3-4 short paragraphs, the CTA link as `https://tenthgear.ai/blog/{slug}/` (trailing slash), sign off on its own line as `Dave` (no dash), an optional P.S.
- The last two lines of the block are exactly:
  ```
  ---
  Unsubscribe: [unsubscribe-link]
  ```
- No em or en dashes and no `shared/brand.md` banned words; the script warns on both. No `{{first_name}}` or other merge tags: the list holds only email addresses.

### Pull quote card concept
- Identify the single most screenshot-worthy stat or sentence
- Describe a simple design treatment (big number in navy, short context line, TenthGear mark)
- Mention it can be made in Canva or similar

No checkpoint here — these are generated as output files for the user to pick up later.

---

## Phase 5: Deploy

### Checkpoint 5

> Wait for explicit "deploy" or "let's ship it" from the user. Don't push on your own authority.

### Auto-steps

0. **Pre-flight:**
   - `grep -rn 'data-build-artifact' src/content/blog/` must return nothing. If it hits, remove the leftover review-only block and rebuild before staging.
   - `docs/distribution/{slug}.md` must exist. If it doesn't, Phase 4.5 got skipped; write the drafts now, before the commit.
1. **Stage specific files only** (never `-A` or `.`):
   - `src/content/blog/{slug}.md`
   - `public/blog-assets/{N}-{slug}/{filename}`
   - `docs/seo/keyword-tracker.md`
   - `docs/distribution/{slug}.md`
   - Any older posts you edited for two-way linking
2. **Commit with a clear message** using HEREDOC format:
   ```
   Add {topic} blog post

   New post targeting {audience} on {angle}. Includes {infographic/
   hero/etc.} and {two-way internal linking to older post if applicable}.

   Co-Authored-By: {the model co-author line the current harness specifies}
   ```
   Do not hardcode a model version here. Use whatever `Co-Authored-By` line the running harness tells you to use.
3. **Push the branch and open a PR. Never push to `main`.** Website `CLAUDE.md` RULE #5 is explicit: new session = new branch, open a PR; Dave's "ship it" is the merge approval (step 5). Recent history (#53 onward) is all PR-merged.
   ```bash
   git push -u origin {branch}
   gh pr create --base main --head {branch} --title "..." --body "..."
   ```
   Report the PR URL.
4. **If the session also produced an unrelated fix** (a layout bug, a stale link), that is its own branch and its own PR, per "PR per logical change." Push the fix PR too and tell Dave which to merge first. If the content branch has the fix as an ancestor, say so, since merging the fix first collapses the content diff to content only.
5. **On "ship it", merge it yourself.** Website `settings.local.json` allows `gh pr merge`; the required checks (Codex Review, CodeQL, Netlify preview) still gate it:
   ```bash
   gh pr merge {N} --squash --delete-branch --auto
   ```
   Netlify deploys about 2 minutes after the merge, not on push. Poll until the live page has the post's content, then go to Phase 6:
   ```bash
   curl -s https://tenthgear.ai/blog/{slug}/ | grep -c "{a distinctive phrase from the post}"
   ```

---

## Phase 6: Announce to subscribers

Runs only after the post is live on tenthgear.ai (Netlify deploy finished after Dave's merge). The subscriber list is the Resend segment "Blog subscribers", fed from the Netlify newsletter form; `docs/newsletter-runbook.md` has the details.

1. Dry run. Fix anything the pre-flight flags in `docs/distribution/{slug}.md`, then re-run until it is clean:
   ```bash
   npm run newsletter:announce -- --slug {slug}
   ```
2. Test email to Dave:
   ```bash
   npm run newsletter:announce -- --slug {slug} --test dave@tenthgear.ai
   ```
3. **Checkpoint 6:** Dave reads the test and says "send".
4. Send. The command syncs the form into the segment first, asks for the slug as confirmation, then creates and sends the Resend Broadcast. The Bash tool can't answer the prompt, so pipe the slug in (Dave's "send" is the confirmation):
   ```bash
   echo {slug} | npm run newsletter:announce -- --slug {slug} --send
   ```
   dave@tenthgear.ai is in the segment (added directly in Resend, 2026-10-24), so Dave gets the real send too; the count reads "N (N-1 from the form)".
   Report the recipient count and the Resend broadcast link. A post is not finished until this has run.

---

## Quick Reference: The 6 Checkpoints

| # | Phase | What the user does |
|---|---|---|
| 1 | Ideate | Picks one of 5 proposed ideas |
| 2 | Draft | Approves draft + visual direction |
| 3 | Assets | Reviews the hero I generated, in the mockup; asks for changes if needed |
| 4 | Integrate | Reviews on localhost, requests tweaks |
| 5 | Deploy | Says "deploy" |
| 6 | Announce | Reads the test email, says "send" |

Everything else is automated.

---

## Nano Banana Prompt Template

This template consistently produces editorial-quality hero images. Swap the bracketed sections for the specific post.

```
A photorealistic overhead flat-lay photograph of [subject scene], shot in documentary editorial style.

[Center subject: describe the main object(s), angle, and any readable text on them, e.g., "a cream-colored envelope with a letter reading 'WARRANTY CLAIM AUDIT' in clean serif type"].

[Secondary objects: 1-2 supporting items with specific placement, e.g., "a printed repair order to the right with a red pen resting across it diagonally"].

[Background object for atmosphere, e.g., "a white ceramic coffee mug in the upper right corner, half full"].

The surface is [material and color, e.g., "warm medium-toned wood with visible grain"]. Natural [time of day] light comes from [direction], casting soft directional shadows. The color palette is muted and slightly desaturated: [list 3-4 specific colors].

Shot from directly overhead, 16:9 aspect ratio, 50mm equivalent lens, shallow depth of field with [primary focus subject] in sharp focus and the edges of the frame falling off softly. The mood is [serious and quiet / focused / contemplative], not dramatic.

Think Wall Street Journal feature photography, not stock photo. No hands in frame, no brand logos, no AI-style rainbow gradients, no plastic sheen.
```

### Common iteration follow-ups

| Problem | Fix prompt |
|---|---|
| Garbled text | "Keep everything the same. Redo just the [element] so the text reads clearly: '...'. All other elements stay exactly as they are." |
| Text is the wrong size | "Keep everything the same but make the [element] text uniformly small and dense, like a ledger, from top to bottom of the document." |
| List is too short | "Keep everything the same. Extend the [document] downward so it becomes a much longer list running past the bottom edge of the frame, so the reader can't tell how many items there are." |
| Too clean / stock-y | "Add realistic imperfections: slight paper texture, faint coffee ring stain, minor wood grain variation." |

---

## File Locations Reference

| What | Where |
|---|---|
| Blog post markdown | `src/content/blog/{slug}.md` |
| Blog assets | `public/blog-assets/{N}-{slug}/` |
| Content schema | `src/content.config.ts` |
| Blog layout | `src/layouts/BlogPost.astro` |
| Tailwind brand colors | `tailwind.config.mjs` |
| SEO keyword tracker | `docs/seo/keyword-tracker.md` |
| Distribution drafts | `docs/distribution/{slug}.md` |
| Project rules | `AGENTS.md` (imported by `CLAUDE.md`) |

---

## Commit Message Reference

```
Add {topic} blog post

{1-2 sentence summary of what the post covers and who it targets}.

Co-Authored-By: {the model co-author line the current harness specifies}
```

Commit on a branch and open a PR. Never push to `main` (RULE #5). See Phase 5.
