# Video Training: traps and mechanics

Each entry cost at least one wasted run on 2026-09-29. Read the section for the step you are on.

## Capturing the app

| Trap | Tell | Do this |
|---|---|---|
| Phone and desktop twins | `strict mode violation ... resolved to 2 elements` | Select `[data-testid="x"]:visible`, first match. `vt.tid` does it. |
| A frame taken too early | Counts read zero, labels in italics | Wait for the element, then a short settle (1 to 3 s). The tab label arrives seconds after a repair order opens. |
| The page scrolls inside `<body>` | `window.scrollTo` does nothing on the RO page | `document.body.scrollTop`. |
| Press and hold in a touch context | Nothing records | `page.mouse.down()` and `up()` drive it. Hold 900 ms before speaking. |
| First mic press only asks permission | No recording on the first hold | Grant `microphone` on the context. `vt.phone` does. |
| Same number on a retake | 409 on save | A new RO number per run. Render a new paper RO for it. |
| Same VIN already open | A match dialog blocks the save | Tap `ro-intake-vin-create-anyway`. |
| The scanner copies print noise | "OP CODE: DIAG" inside the complaint | Keep the sample sheet clean. |
| Story generation takes 8 to 20 s | Timeouts | Wait on the `generate-all` and `analyze-completeness` responses, never on a sleep. |
| Never wait for network idle | The wait burns the whole timeout | The app polls. Wait for elements. |

## Footage

- **The browser's screencast and Playwright's `recordVideo` both capture at 1x** (390 px wide) whatever the device scale. Scaled into the phone frame it is blurry. `Page.captureScreenshot` with `clip: { ..., scale: 2 }` returns 780 x 1688 at about 30 frames a second. Without the `clip` it also returns 1x. `vt.recorder` does this and resamples to a steady 30 fps.
- Frames are saved as `f00000.jpg` upward. `footage.runs` is a list of `[firstFrame, frameCount]`. Several runs are joined with hard cuts; a cut inside a waveform or a spinner is invisible.
- The finger marker (`vt.touchOn`) is drawn into the page. Turn it off before a still.
- Footage cards lose their callouts: the card is drawn with the phone screen cut out and the clip plays underneath. If the narration points at something, keep it a still or add the pointer to the clip.

## Narration

- The Mac's built-in voices (`say`) were rejected as robotic. Only compact voices are installed.
- The style instruction (tested on `gpt-4o-mini-tts`; now passed as `gpt-audio-1.5`'s system prompt) is weak. Asking for "unhurried" made it slow; asking for "brisk" barely changed it. Pace is set by `speed` in the build, with pitch kept.
- Each card is a separate request, so tone can drift a little between cards.
- `gpt-audio-1.5` (10/1 test): about one in four takes mumbled a card's FIRST words ("Part one" heard as "AUT1") while its own transcript read clean, so narrate's word check can't see it. `check-audio.mjs` on the finished video does; delete that card's manifest entry to re-take.
- A garbled line shows up in `check-audio.mjs`. Reword it rather than retrying: "say the service" came out as "and Cs"; "name the service out loud" was clean.
- The transcriber writes "10th Gear" and "40,000". Those are not faults.

## The service checklist

The checklist opens only when the note reads as scheduled maintenance. "Scheduled maintenance, 40,000 miles" always does. The hyphen and "40k mile" forms were fixed in app PR #2212 (merged 2026-09-29); until a republish carries it, avoid them in a recording.

## Storyboard canvas

- Images must be uploaded assets referenced by their `/_blob/<id>` url. No data URIs, no file names.
- The first artboard must be `Main.dc.html`. Here it is the cover.
- The publish root must sit under the session's working directory or scratchpad. The project folder is outside both when the session starts in `app/`, so copy `storyboard/project/` into the scratchpad to publish.
- The open editor rewrites `canvas.json` seconds after a publish. Read it back and pass it to `storyboard-canvas.mjs --live` before publishing again.
- A plain `read` of the artifact url clears a save conflict; a `read` with `path` does not.
- Write apostrophes as real characters in artboard markup, never as `&#39;`.
- If the canvas spins or goes blank, open a canvas you have not touched. If that fails too, it is the service: publish the cards as a plain HTML page and carry on.
- `storyboard-harvest.mjs` was proven against the generator's own markup and simulated edits. The editor may reshape markup when Dave retypes text. Anything it cannot read is listed under "check by hand": open that artboard and read it.
- Notes Dave adds himself are instructions. The harvest prints them; it never merges them.
- Dave also leaves COMMENTS on the canvas ("swap in the logo here"). They arrive as comment notifications; read them with the ArtifactComments tool, make the change, reply and resolve.
- A revision adds cards, so board file names shift (`S11-pencil` becomes `S16-pencil`). Publish the renamed files and send the old names as `null`, or the old boards stay as stray frames. Do this ONLY before Dave has edited: once he has, never regenerate from `storyboard.json` without harvesting first.
- Dave adds artboards of his own (an end page, 2026-10-02: `Main-qgwm.dc.html`). The harvest and the build scripts do not know them. Read them by hand and extend the build before production.
- The logo: `/Users/davidsonders/ro-bot/shared/brand-assets/exports/png/horizontal-white-2400w.png` (white, for the black cards). Upload it as a canvas asset; the SVG export loses its fill on upload.

## Capturing a photo flow

- The camera button on the RO page is `button[aria-label="Add a photo to the notes"]`; its file input is the next sibling. `setInputFiles` on it opens the routing review (`photo-routing-review`, `photo-routing-story-notes`).
- The "Add to story notes" sheet is `role=dialog` named "Add photo to story notes"; wait on the `/photos/<id>/interpret` response, never a sleep. A long document is read in parts: each save re-opens the sheet on the next part.
- The RO page scrolls inside `<body>`: park a target with `document.body.scrollTop += box.y - <wanted y>`.
- **When the capture shows the app doing less than the script says, stop and raise it as a product question** (memory `feedback_capture_gap_is_product_question`). The first TSB capture summarised the bulletin; that was a product gap, not a wording problem.

## Secrets

- No password or key is written into this folder. `vt.password()` reads `VT_PASSWORD`, then `DEMO_SEED_PASSWORD`, then the demo seeder's own default.
- The OpenAI key is read from the app's environment by running from the app folder with `-r dotenv/config`. Error text is scrubbed of anything shaped like a key before it is printed.
- Bash commands that name a `.env` file are blocked. Let the script read it.

## Command shapes

```
S=~/.claude/skills/video-training/scripts
P=/Users/davidsonders/ro-bot/training-videos/<slug>

node ~/.claude/skills/video-training/props/render-paper.mjs $P 418207
node $S/storyboard-canvas.mjs $P [--live <canvas.json>]
node $S/storyboard-harvest.mjs $P <pulled folder> [--write]
node $S/build-slides.mjs $P
(cd /Users/davidsonders/ro-bot/app && NODE_OPTIONS='-r dotenv/config' node $S/narrate.mjs $P)
node $S/build-video.mjs $P
(cd /Users/davidsonders/ro-bot/app && NODE_OPTIONS='-r dotenv/config' node $S/check-audio.mjs $P)
node $S/close-ros.mjs $P tyler@demo.test demo-dealership
```

The mode change, the capture and the restore belong in ONE chain, so a failed capture still restores the store:

```
cd /Users/davidsonders/ro-bot/app
NODE_OPTIONS='-r dotenv/config' npm run --silent manage-org -- set-mode <id> single_player; \
node $P/capture-stills.mjs $P; \
NODE_OPTIONS='-r dotenv/config' npm run --silent manage-org -- set-mode <id> multi_player; \
NODE_OPTIONS='-r dotenv/config' npm run --silent manage-org -- info <id> | grep -i "workflow mode"
```
