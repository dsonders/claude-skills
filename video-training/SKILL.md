---
name: video-training
description: Produce a narrated training or walkthrough video (plus matching annotated slides and PDF) that shows the real TenthGear app. Starts with a storyboard on a design canvas (key frames, callouts, voice track) that Dave edits in place, then captures stills and footage from the live app, narrates with OpenAI text to speech, and assembles the video. Use when asked for a training video, getting-started guide, quick start, how-to video, walkthrough, annotated screenshots for technicians or advisors, or to revise an existing training video.
---

# Video Training: storyboard first, then the real app on screen

A training video here is a set of phone-shaped cards. Each card has a headline, one line of help, a key frame from the real app with callouts, and a line of narration. Some cards play a short clip of the app instead of a still. The same cards are delivered as slides and a PDF.

One file drives everything: `storyboard.json`. Dave edits it through a design canvas; every build script reads it.

## When to use

**Use for:**
- A training, getting-started, quick-start or how-to video that shows the app
- Annotated screenshots or a slide guide for technicians, advisors or parts staff
- A revision to a video made with this skill (new wording, new card, new clip)

**Do not use for:**
- Marketing or promotional video (different tone, different rules; ask Dave)
- Customer inspection videos recorded inside the product
- A mockup of a screen that does not exist yet (use `/visual`)

## Principles

1. **Storyboard before production.** Nothing is narrated or assembled until Dave has edited the storyboard canvas and said he is done.
2. **Show the real app, doing the real thing.** Real scan, real dictation, real generated story. Never a mocked screen, never typed-in results.
3. **Dave rules on the canvas, not in chat.** Read the canvas back and diff it. Do not rebuild his direction from the conversation.
4. **An approved take is kept.** Narration is regenerated only for lines whose words changed. Never overwrite a version Dave has reviewed; ship `-v2`, `-v3`.
5. **Claude cannot hear or watch.** Say so in every hand-back. Prove the words by transcription and the pictures by sample frames, and name what was not checked.
6. **Leave the store as found.** Mode restored and confirmed, retake repair orders closed.

## Read first

- `/Users/davidsonders/ro-bot/shared/product-facts.md` and `shared/brand.md`: names, counts, banned words. No em dashes, no emojis, "TenthGear" as one word. Never say "single player" or "multi-player" in anything a viewer sees or hears.
- `reference.md` in this folder: the technical traps, each one paid for once already.
- Memory notes on the design canvas: `reference_design_canvas_mechanics`, `reference_design_canvas_roundtrip`, `reference_design_canvas_entity_crash`.

## Where things live

| What | Where |
|---|---|
| A video's project folder | `/Users/davidsonders/ro-bot/training-videos/<slug>/` (never the session scratchpad, which dies with the session) |
| The one source of truth | `<project>/storyboard.json` |
| Key frames, clips, narration | `<project>/frames/`, `footage/`, `narration/` |
| Builds | `<project>/out/` |
| What Dave receives | `~/Desktop/<Title>/` |
| Worked example | `training-videos/story-writer-getting-started/` and `examples/story-writer/` here |

Scripts are in `scripts/` here. They take the project folder as their first argument.

## Workflow

Make a todo list for these steps and work through them in order.

### Step 0: Settle the brief

Find these in the request. Ask only for what is missing, one question, recommendation first.

| Decide | Default |
|---|---|
| Who watches, and in which role | Technician |
| Phone or desktop | Phone, 390 x 844 |
| Which flow, start to finish | Dave's outline |
| Store and workflow mode | Ask Dave. See Step 2. |
| Stills only, or stills plus clips | Clips wherever the screen moves: recording, loading, open and close |
| Length | Under 2:30 |

### Step 1: Storyboard on a design canvas

This is the first thing Dave sees and the place he edits the script and the callouts.

1. **Create the project folder** and render any props (`props/render-paper.mjs` makes the sample paper repair order).
2. **Scout the flow for key frames.** Key frames come from the real app, so this step needs a capture run (Step 2 and Step 3, stills only). Copy `examples/story-writer/capture-stills.mjs` into the project and rewrite the flow. Look at every frame before going on.
3. **Draft `storyboard.json`.** One card per thing the viewer does. Shape:

   ```json
   { "id": "write-story", "part": 2, "img": "10-write-story",
     "title": "Tap [[Write Story]]",
     "body": "The AI writer will review your notes and write 3Cs for you.",
     "boxes": [[183, 400, 191, 44]], "arrow": [162, 768],
     "footage": { "clip": "C-write", "runs": [[15, 336]], "note": "What the clip shows" },
     "narration": "When you are ready, tap Write Story." }
   ```

   `boxes` and `arrow` are in phone pixels; the capture writes each control's box beside its frame. `[[Label]]` draws a button chip. Follow the style rulings below from the first draft.
4. **Create the canvas.** Artifact tool: `quickstart` with intent `design`, then publish with the `type_url` it returns and a title. Save the url in `<project>/storyboard/artifact.json`.
5. **Upload the key frames** to the canvas as assets (JPEG, 1688 px tall, staged in the scratchpad so they go in one call). Record each returned `/_blob/...` url under `assets` in `artifact.json`, keyed by frame name.
6. **Generate and publish.** `node scripts/storyboard-canvas.mjs <project>` writes `storyboard/project/`. Copy that folder into the scratchpad and publish it: `canvas.json` as `file_path`, every `.dc.html` in `files`.
7. **Hand Dave the link and stop.** Tell him: retype any words on a card, the blue note under each card is the voice track, drag the yellow callouts, write anything else on a note. Do not start production.
8. **Harvest his edits.** Artifact `read` with `paths` (the index and every artboard) and an `out_dir`, then `node scripts/storyboard-harvest.mjs <project> <out_dir>`. Read the report to him in plain words, act on any notes he added, then rerun with `--write`.
9. **Another round?** Read `project/canvas.json` back, regenerate with `--live <that file>`, republish. A publish that does not start from the live index is refused.

### Step 2: Borrow a store

The app has to be in the mode the video shows. Only test stores may be used.

| Store | Id | Normal mode | Notes |
|---|---|---|---|
| Summit Auto Group (demo) | `demo-dealership` | team workflow | Dave's prospect demo. Logins `tyler@demo.test` (tech), `marcus@` (advisor), `priya@` (parts). Used for the first video. |
| Test Dealership 1 | `mlTaPo12wbpUtJB9GXJM` | team workflow | Shared with build sessions. Often busy. |

1. `ListAgents`, then `SendMessage` each peer: is it using the store, and does it need the mode? Wait for the answer. If a peer needs it, use the other store or ask Dave.
2. Read the mode first: `NODE_OPTIONS='-r dotenv/config' npm run --silent manage-org -- info <id>` from the app folder.
3. Change it only for the minutes a capture runs, in the same command chain as the capture and the restore. Then read it again and confirm.
4. Never touch a customer store. Never change a test account's preferences.

### Step 3: Capture

- **Stills:** `dpr: 3`. One frame per card, taken after the screen has settled.
- **Clips:** `dpr: 2` with `vt.recorder`. Open each clip with a beat of stillness, show the finger marker, then act. Read `marks.json` to choose `footage.runs`.
- **Dictation is real.** `vt.dictation` plays a spoken clip into a fake microphone; the app records and transcribes it. Print every transcript and read it: the transcriber rewrites numbers and brand names.
- A retake needs a fresh repair order. Number them upward and list each id in `created-ros.txt`.

### Step 4: Slides

`node scripts/build-slides.mjs <project>` writes `out/slides/*.png`, the PDF, and the layers the video needs. Look at a contact sheet of every card. Check that no callout covers the thing it points at.

### Step 5: Narration

```
cd /Users/davidsonders/ro-bot/app
NODE_OPTIONS='-r dotenv/config' node ~/.claude/skills/video-training/scripts/narrate.mjs <project>
```

Voice `ash`, model `gpt-audio-1.5` (moved from `gpt-4o-mini-tts`, which OpenAI shuts off 2027-01-06). A take whose transcript doesn't match the card's words is retried, then refused. Dave approved this voice and rejected the Mac's built-in voices as robotic. It uses the app's OpenAI key and costs a few cents a build: say so in the brief for each new video, so the spend is never a surprise. `DRY=1` lists what would be regenerated.

Write narration for the ear: "R O", "three Cs", "tenthgear dot A I". Announce each part on its first card.

### Step 6: Video

`node scripts/build-video.mjs <project>`. Speed is 1.25 (QuickTime's "Fast"), the pace Dave approved. A card with a clip runs as long as the longer of its narration and its clip.

### Step 7: Verify, and say what was not verified

1. `check-audio.mjs` transcribes the video and scores each card. Read every `LOOK` line.
2. Pull one frame from each card that has a clip or an arrow and look at it.
3. In the hand-back, state plainly: not listened to, not watched end to end.

### Step 8: Deliver

Copy the video, the PDF and `out/slides/` to `~/Desktop/<Title>/`. Keep earlier versions. Give the length, what changed, and anything Dave may notice (a different repair order number in a clip, a callout dropped over footage).

### Step 9: Clean up

- Store mode restored, then read back and confirmed.
- `node scripts/close-ros.mjs <project> <email> <org-id>` closes the retakes. Deleting repair orders is Dave's call.
- Tell any peer you messaged that the store is free.

## Style rulings (Dave, 2026-09-29)

| Rule | Example |
|---|---|
| A button the viewer taps is drawn as a button | Tap `[[New RO]]` |
| Part headers are short, with no "of 3" | PART 2: WARRANTY STORY |
| The cover has no step count | |
| One card per step. Merge cards that show one decision. | Review and save are one card |
| Drop a card whose point is self-evident | Reading Cause and Correction |
| Say who acts and with what | "Add a voice note", not "Add a note" |
| When two things on screen could be meant, point at the one | Arrow on the green button |
| Anything that moves in the app should move in the video | Waveform, spinner, card opening |
| Shop-floor words | RO, line, story, 3Cs, CP |

Dave gives slide edits by PDF page number. Page 1 is the cover, so "pg 7" is step 6. Restate each edit by step name before applying it.

## Success criteria

- [ ] Dave edited the storyboard canvas and his edits were harvested, not guessed
- [ ] Every frame and clip is the real app, in the mode the video is about
- [ ] Slides, PDF and video all come from the same `storyboard.json`
- [ ] Narration checked by transcription; unclear lines named
- [ ] The hand-back says what was not listened to or watched
- [ ] Store mode restored and confirmed; retake repair orders closed
- [ ] Project folder kept outside the scratchpad

## Related skills

- `/visual` for mockups of screens that do not exist yet
- `/app-testing` for the test accounts and the live-pass harness this borrows
- `/compound` afterwards, if a capture exposed a product bug or a new trap
