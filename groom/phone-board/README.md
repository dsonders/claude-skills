# Grooming board (desktop + phone) — build source (groom skill Step 0)

Published artifact: https://claude.ai/code/artifact/f483bcdc-3eba-483e-ae79-7290e664f3bb (capability `db`; republish by
passing that URL as `url` from any session).

- `build.py` — writes `grooming-board-phone.html` (one responsive page: ≥900px = desktop layout) next to itself; the page script is `app.js`, per-option frames `option_frames.py`, the old desktop board's risk grid / icebox / archive carried in `legacy_blocks.json`. Run `python3 build.py` from anywhere (absolute paths).
- `decisions.py` — the lettered options + rec for every to-vote card's questions. EDIT THIS when the backlog changes.
  Keys are the board card keys; ids are `<KEY>-<n>` and the store is keyed on them — keep them stable.
- `cards.json` — title / sub / dims / figures per to-vote card, extracted from the desktop board's HTML
  (the extraction script is in the 2026-09-08 session; re-extract with the same regexes when cards change).
- `real-capture.mjs` + `real/` — REAL screenshots of the app with variants applied live (Q, 9/9): `MODE=inspect node real-capture.mjs` seeds a TD1 fixture RO and dumps the card's markup/sizes (keeps the RO open, prints its id); `RO_ID=<id> node real-capture.mjs` captures every variant at phone + desktop width, writes `heights.json`, closes the RO. Reads `__tests__/workflow/.env.test` in-process; prints no secrets. Add variants to `VARIANTS` as CSS/DOM overrides against the real testids.
- `triage_frames.py` — the ONE basic mockup per not-yet-groomed item (keyed in `build.py`'s `TRIAGE_MOCK`).
- `lib.py`, `parts_card.py`, `admin_card.py` — the drawn app frames (RO line panel, customer page, parts card, admin
  Parts & Labor card). Add a `frames_for(key)` branch in `build.py` for each new Flip / walkthrough item.
- `board.css` — the desktop board's stylesheet, carried in so ported figures render.
- `test.mjs`, `test2.mjs` — Playwright checks at 390px (routing, tapping, words, notes, persistence; scroll stability
  under a simulated store). Run with `node` from `/ro-bot/app` so `playwright` resolves (the scripts use absolute paths).

Store layout: `rulings/<KEY>-<n>` = `{choice, words, at}` · `rulings/<KEY>-stage` = `{choice: advance|keep|icebox}` (triage items) · `notes/<KEY>` = `{text, at}`. `STAGE` / `STAGE_NOTE` in `decisions.py` mark triage items. Sweep protocol: groom skill Step 0.

## The seven SOPs live in `../SKILL.md`; this file holds the how and the lessons

### Board data, in build order
`cards.json` (what an item is) → `decisions.py` (`DEC` questions + options + rec · `STAGE` / `STAGE_NOTE` triage items ·
`BAKED` filed rulings · `HOLD` items ruled but held for a conversation — pill "ruled · discuss", never queued) →
frames (`frames_for()` in `build.py` for Flip / walkthrough; `OPT_VIS[id][letter] = {frame, why}`; `CONTEXT[id]` one
situation paragraph; `GALLERY[id]` many-shape decisions, `GALLERY_FULL` / `OPTS_FULL` one per row at true size;
`TRIAGE_MOCK` one basic frame per triage item) → `build.py` → `grooming-board-phone.html` → `test9.mjs` → publish.

### Building the board — what actually works (2026-08-27 → 09-10)
- **One Opus builder per card (or per pass), never one giant rewrite** — a builder asked to regenerate the whole board
  stalled at the 600 s no-progress watchdog after writing the file. Brief: write each card, splice with a short script,
  run the checks, STOP. Every brief opens, verbatim, with "NEVER `cd` in a Bash command — every command uses absolute
  paths" (a soft "use absolute paths" mid-brief was ignored and each `cd … && grep` popped a permission prompt).
- **Read the real screens and the real records BEFORE the brief** (Explore agent for component anatomy + a read-only
  Firestore probe for a real RO): the sweep changed the V6 story (there is no Stop button) and produced the whole V1
  fixture. Shot numbering: content shots only, bookends unnumbered — a locked ruling a builder gets wrong unless told.
- **Screenshot every card before publishing and check the datums, not just the layout** — a builder invented a line
  title, a $ figure, a note and a status label across four cards in one pass. Silhouettes (grey bars, "Part 1", "Line
  title") are the fix when no real value exists. Screenshot only after `document.fonts.ready` — before the webfont lands,
  ballot lines render unwrapped and a real bug was chased for a round on that false alarm.
- **Probe the COUNT, not the excerpt.** MPI-6's frames drew 3 notes; the record had 4, and "McGrath techs are saying
  this" was ONE tech on ONE inspection.
- **Edit HTML with tag-depth-aware splicing, never `.*?</div>` regexes** — a row-cloning regex nested the 4th note inside
  the 3rd on two sheets.
- **Publishing:** the publish gate needs the live artifact read in full before a session's first republish — budget for
  it. A deleted artifact ends the watch with "artifact not found"; an account switch makes it invisible (9/3 gmail →
  tenthgear; 9/10 tenthgear → gmail, the weekly allowance ran out): publish WITHOUT `url`, update the BACKLOG.md header
  + memory `reference_grooming_board_account_and_url` the same turn. The store moves with the artifact — bake every
  filed ruling first so nothing is lost.
- **Sweep order (9/8 lesson):** file → PR on main → BAKED → rebuild + republish → delete store docs. Clearing first made
  ruled items read as open again. A reconnecting device re-pushed swept docs until 9/9 — the page now pushes only docs
  written while the store was unreachable.
- **Real captures (9/9):** the first capture of the parts page was at phone width — the wrong device for a desktop-only
  role; redone at 1440. `MODE=inspect` first: write overrides against the real testids, not the anatomy you assume.

### Retired
`reference-board.html` (the 8/25 desktop board Dave approved — "SO MUCH BETTER") was the card template until the one
responsive board replaced it on 2026-09-09; deleted 2026-09-10 (git history of this repo keeps it). Its card anatomy
survives as the guiding principles + the data files above.
