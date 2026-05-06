---
name: ro-bot-blog-post
description: End-to-end workflow for producing a new blog post on the RO.bot marketing site at /ro-bot/website/. Covers ideation, drafting, hero image, infographic, SEO/AEO optimization, two-way internal linking, distribution drafts, build verification, and deploy. Use ONLY when working in /ro-bot/website/ — the blog frontmatter schema, Astro content collection, and deploy pipeline described here are website-specific.
---

# RO.bot Blog Post Workflow

**Scope:** This skill is specific to the RO.bot marketing website at `/ro-bot/website/`. The Astro content collection in `src/content/blog/`, the frontmatter schema in `src/content/config.ts`, the Netlify deploy step, and the build-verification commands all assume that subproject's structure. Do not invoke from `app/` or `GTM/`.

End-to-end workflow to produce and ship a blog post on the RO.bot marketing site (`ro-bot.io`). The goal is to publish something high-quality in one session with the user only in the loop at 5 clear checkpoints.

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
- `CLAUDE.md` (project instructions, banned words, voice rules)
- `src/content/config.ts` (current frontmatter schema)
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
2. **Frame the prompt so top/bottom 10% is expendable** — this lets you crop out the Gemini watermark (lower-right sparkle) cleanly without losing subject. Plan for this up front.

### Checkpoint 3

> Give the user the prompt in a single paste-ready code block. Wait for them to run Nano Banana externally, paste results, and iterate. Provide follow-up edit prompts for refinements (blur background, shift focal plane, extend elements out of frame, fix text garble, etc.). Loop until the user says "good enough" or similar.

### Auto-steps (after image approved)

3. **Process the hero image with sips**:
   ```bash
   # Get current dimensions
   sips -g pixelWidth -g pixelHeight {source}

   # Crop top and bottom 10% (new_height = floor(height * 0.8))
   # Also compress and convert to JPEG
   sips -c {new_height} {width} -s format jpeg -s formatOptions 82 {source} --out {dest}
   ```
4. **Save with clean name** to `public/blog-assets/{N}-{slug}/hero.jpg` (or a descriptive filename like `warranty-audit-letter.jpg`).
5. **Target file size under 500 KB** after compression. If larger, resize to max 1600px wide first.

---

## Phase 4: Integrate

### Auto-steps

1. **Create the markdown file** at `src/content/blog/{slug}.md` with frontmatter and body from Phase 2.
2. **Wire in the hero image** using this constrained block pattern (keeps the hero at 50% width on desktop, full on mobile):
   ```html
   <div class="not-prose my-8 mx-auto max-w-full md:max-w-[50%]">
     <img src="/blog-assets/{N}-{slug}/{filename}" alt="{alt with primary keyword if natural}" class="w-full rounded-lg" />
   </div>
   ```
3. **Build the infographic inline** (if planned in Phase 2) using brand colors and `not-prose` wrapper. See existing example in `src/content/blog/warranty-audit-playbook.md` for a reference pattern.
4. **Two-way internal linking** — identify 1-2 older posts that should link TO this new one. Propose specific sentences to add or edit. Add them.
5. **Run `npm run build`** and verify:
   - Build passes with 0 errors
   - `/blog/{slug}/` appears in the page list
   - `grep` the built HTML for the primary keyword and any infographic key values to confirm they rendered
6. **Append to keyword tracker** — add a row to `docs/seo/keyword-tracker.md` with slug, publish date, primary keyword, and placeholders for rank tracking.
7. **Start the dev server** in the background: `npm run dev` with `run_in_background: true`. Share `http://localhost:4321/blog/{slug}` with the user.

### Checkpoint 4

> User reviews on localhost. They may request style tweaks (image size, infographic colors, copy edits). Hot reload handles this live. Loop until approved.

### Auto-steps (after approval)

8. **Stop the dev server** — `pkill -f "astro dev"`.

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
- Subject line (under 50 chars)
- Preview text (under 90 chars)
- 3-4 paragraph body
- Clear CTA link to the post
- Unsubscribe footer placeholder

### Pull quote card concept
- Identify the single most screenshot-worthy stat or sentence
- Describe a simple design treatment (big number in navy, short context line, RO.bot logo)
- Mention it can be made in Canva or similar

No checkpoint here — these are generated as output files for the user to pick up later.

---

## Phase 5: Deploy

### Checkpoint 5

> Wait for explicit "deploy" or "let's ship it" from the user. Don't push on your own authority.

### Auto-steps

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

   Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
   ```
3. **Push to origin main** — `git push origin main`. Report the new commit SHA.
4. **Remind the user** that Netlify will auto-deploy from the GitHub webhook in ~2 minutes. The post will be live at `https://ro-bot.io/blog/{slug}`.

---

## Quick Reference: The 5 Checkpoints

| # | Phase | What the user does |
|---|---|---|
| 1 | Ideate | Picks one of 5 proposed ideas |
| 2 | Draft | Approves draft + visual direction |
| 3 | Assets | Runs Nano Banana externally, iterates until image is good |
| 4 | Integrate | Reviews on localhost, requests tweaks |
| 5 | Deploy | Says "deploy" |

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
| Gemini watermark visible | Crop it out in post-processing (top/bottom 10% works reliably). |
| Too clean / stock-y | "Add realistic imperfections: slight paper texture, faint coffee ring stain, minor wood grain variation." |

---

## File Locations Reference

| What | Where |
|---|---|
| Blog post markdown | `src/content/blog/{slug}.md` |
| Blog assets | `public/blog-assets/{N}-{slug}/` |
| Content schema | `src/content/config.ts` |
| Blog layout | `src/layouts/BlogPost.astro` |
| Tailwind brand colors | `tailwind.config.mjs` |
| SEO keyword tracker | `docs/seo/keyword-tracker.md` |
| Distribution drafts | `docs/distribution/{slug}.md` |
| Project rules | `CLAUDE.md` |

---

## Commit Message Reference

```
Add {topic} blog post

{1-2 sentence summary of what the post covers and who it targets}.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
```
