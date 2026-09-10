---
name: groom
description: Interactive triage + grooming session for the RO-bot backlog on a visual board — prioritize items, present each with standard dimensions and visual-first explanations, ballot UX decisions with mockups, and write Dave's rulings verbatim into docs/overnight/BACKLOG.md for the overnight-build run. Use when Dave says "groom", "let's groom the backlog", "triage these", "grooming board", "update the board", or wants follow-ups presented for decisions. Designed 2026-08-25 with Dave; the format rules below are his.
---

# Groom: the grooming board and the rulings pipeline

ONE standing board (desktop + phone, one URL, one ruling store) presents the backlog as the app's own screens. Dave
rules on it — by letter in chat, or by tapping the board with no session running. Every ruling lands ⛔-verbatim in
`docs/overnight/BACKLOG.md`, whose **Queued** section `/overnight-build` consumes. Board URL + owning account:
BACKLOG.md's header and memory `reference_grooming_board_account_and_url`. Build source: `phone-board/` next to this
file — its README is the how-to (files, store layout, build lessons); this file is the rules and the seven SOPs.

## Core rules (Dave's, 2026-08-25 → 09-09 — don't drift)

0. **The board is written for Dave — not an engineer, not an LLM.** He decides from what he'd SEE in the app. Code
   anchors go in BACKLOG.md's Queued entry, never on a card ("putting code references in a box does not make it a mockup").
1. **Show more than tell.** Visuals carry the explanation; text is sparse. If he has questions, he'll ask.
2. **The board presents; the file records.** Every ruling lands in BACKLOG.md verbatim (⛔) in the turn it is made — or
   in the sweep that finds it.
3. **One standing artifact, stable URL, desktop AND phone** (≥900px: cards expand in place, Today | Proposed side by
   side, options in a row; below: the phone flow). Never a new page per session — every new URL splits the store.
4. **Priority order.** Sections are PRODUCT SURFACES (Dave 9/3): MPI & Video → Parts page & queue → RO page → Dashboards
   → Customer page → Store settings → Platform & tooling → Risk grid → Icebox → Archive. Within a section the order IS
   the ranking: UX impact (reliability/perf over polish) → population → risk position → Dave's flags → what unblocks
   others. Queued cards sit at the top of their section, collapsed.
5. **Rulings arrive by letter in chat, as artifact comments, or as taps on the board** (swept by SOP 1).
6. **Each open decision sits directly under the options it decides** (Dave 8/28). **Feedback on a mockup is answered IN
   the mockup** (Dave 9/4: "I expect iteration to happen in that mockup, not simply that new content / decisions needed
   in the DECISIONS / VOTING area") — redraw the frame and its result; never a chat answer, a table or a new ballot line.
7. **A walkthrough is one short per-actor strip** (≤ ~6 frames; Dave 8/30: a full directions × screens matrix is "too
   many UI drawings, too much redundancy"). Every caption names the actor AND that it is THEIR OWN action ("The parts
   user, when they price a part") — the SA-7-C misread. Mock copy follows app `design.md` "Notice & status copy".
8. **Redrawing a ruled direction keeps every control the ruling didn't remove** ("we're not losing the drag and drop
   handles, right?"). A ruling that strips chrome lists what goes; everything else stays.

## Guiding principles (⛔ Dave, 2026-09-08 → 09 — both screens; cards share ONE anatomy, each optimized for its screen)

1. **Every UX decision shows each option as a screen.** "This way or that way — I need to see what those directions will
   look like when implemented." An option that is a UX direction carries its own drawn frame; a non-UX option carries
   one implication line. A decision between many shapes gets a gallery. Never a ballot with no picture on a UX item.
2. **A question that is really a fact gets answered, not asked.** Check the code first; state the fact on the card
   and reframe or drop the decision (9/8: "booked" never on the customer page; delivery state shown nowhere; a count
   that is structurally zero).
3. **Stage first, then the one decision that moves the item forward.** Every card opens with its stage. A not-yet-
   groomed item asks exactly one thing: Advance to grooming / Keep in backlog / Send to Icebox.
4. **The groom-or-not call is a one-screen read.** Title, one line, ONE basic mockup for anything with UX
   implications, the three buttons, the feedback field. Everything else folds under Details.
5. **Flip for simple, walkthrough inside a Flip for complex.** Single user, single screen, 1–3 UIs → the Today |
   Proposed switch over one frame. Crossing users or screens → the per-actor walkthrough under the same switch.
6. **State shows as state, never as a sentence.** No "Not ruled yet", no helper lines under controls, no placeholder
   text, no explaining what the screen already shows (the app's own design rule, applied to the board).
7. **Orientation comes from counts and collapse, not from reading.** Sections start closed; each carries ruled/total;
   each item carries its open-decision count. He opens what he needs.
8. **Nothing moves under his thumb.** A tap saves in place; the page never jumps, re-renders from the top, or loses
   scroll position.
9. **Flag things in plain language, with a recommendation.** A double-check says what I saw, what it means for him,
   and whether he must act — in that order.
10. **His notes are the brief.** The staged feedback field is where he queues what must be worked through before he
    can rule. The next session reads those FIRST, answers them in the frames, files rulings verbatim, and clears them
    only after they landed. An item he already ruled never comes back as open.
11. **Honesty rules that make a visual trustworthy.** Real components (read them first), real figures from real
    records, grey bars for anything the record does not give, and any measured number labelled as measured in the
    drawing. A fake datum stops the vote. **Detailed UI work (density, spacing, a card's height) uses REAL SCREENS**
    (⛔ Dave 9/9, card Q): seed a fixture RO on the test store, open the real page headless as the real role, AT THE
    SCREEN THAT ROLE ACTUALLY USES (parts counter + admin + advisor = desktop, 1440 wide; tech + customer = phone —
    "Parts dept users will almost never use tenthgear on their phone"), apply each variant as a live style/DOM
    override, screenshot the element and measure it — recipe + script in `phone-board/real-capture.mjs` (reads
    `.env.test` in-process, closes the fixture RO). A drawing of the card missed what the real page showed (empty
    bands from equal-height tiles, a "hover for all" overlay); a phone capture of a desktop surface was the wrong
    device and had to be redone.
12. **Write for a product manager and designer, not an engineer.** Explanations and on-board communication are
    clear, concise, natural human language. No code names, no field names, no engineering nouns (the "Never on a card"
    list below).
13. **Never mingle my words with the UI.** Text on a mockup is text OUR USERS will see — nothing else goes on a frame.
    Captions, implications and answers sit outside the frame, in the board's own type.
14. **Extra text is not free — and neither are extra frames.** Use restraint: only what adds real value to the
    decision. No extra notes or labels when the information is already present or obvious from the screen. Every
    sentence costs him a read. **A ruled decision collapses to ONE line** (letter, question, the chosen option, where
    it was filed) — no options, no frames; frames belong only to what is still open (⛔ Dave 9/9, card P: "far too
    many UIs here… far too much to digest" — 15 drawn frames on a card with one open question became 6 real screens).
    Desktop screens go on the board at their real size, one per row, never scaled thumbnails.
15. **When several options need a decision, weigh in: the rec and its rationale**, marked on the option, one sentence
    about the person it affects.
16. **Desktop surface + detailed UI design work = REAL DESKTOP SCREENSHOTS, not drawings** (⛔ Dave, 2026-09-09, card Q:
    "When a user's primary product surface is desktop, and the issue or decision at hand is detailed UI design work,
    you need to create real desktop screenshots to help me visualize the options."). Detailed UI work = anything he
    judges by looking at density, spacing, alignment, sizes, a component's height or shape. Desktop-primary roles:
    parts counter, admin, advisor. Recipe: seed a fixture RO on the test store, open the REAL page headless as the
    REAL role at 1440 wide, apply each option as a live style/DOM override, screenshot the element and measure it —
    `phone-board/real-capture.mjs`. One screenshot per option, the real height in its caption, one column at full
    width on the board. Phone-primary roles (tech, customer) get the same treatment at 390 wide. A drawing is still
    fine for a flow, a label or a new element that does not exist yet — never for how an existing desktop screen
    should be laid out.
17. **Dave's own words on a card wear their own colour** (⛔ Dave, 2026-09-10: "we need to use a different visual
    treatment (for example a different color) for text that comes from me directly on a card") — the amber of the
    "ruled · discuss" pill, so he can tell his words from UI text and from mine. Every verbatim quote of his in the
    board data is wrapped `⟦…⟧` (`decisions.py` notes and `HOLD` lines, `CONTEXT`, option implications, gallery
    labels); the page renders it amber, and the words he types on the board are amber too. Paraphrase is not his
    words — only what he actually said gets the marker.

**Never on a card:** file names, function/field names, predicates, `code` chips, provenance strips, "sensitivity"
banners in engineering terms, counts like "4 to vote", status IDs (use the label the app shows: "Waiting for Parts",
never `waiting_for_parts`), or the words denorm/flag/predicate/backfill (say "stored information", "a one-time cleanup
you run"). Drawn frames use the app's light look with its real row colors, pills and chips; a highlight ring lands on
at most ONE element per frame — never on a header, a button, a section, or a frame whose DESIGN is being ruled (Dave
9/7: "unintended blue outlines… redraw so I can rule on the actual design proposal").

## Standard dimensions — every card carries these

| Dimension | Values |
|---|---|
| UX impact | High / Med / Low, + a ⚡reliability/perf flag when applicable |
| T-shirt size | S / M / L / XL |
| Est. Codex rounds | 0–1 / 2–3 / 4+ (permission/model rewrites trend 4+ → split candidates) |
| Reversibility | revert-cheap code ↔ touches data (decides the overnight hard floor) |
| Population | who actually hits it — pre-answer "do we have customers using this?" |

Bug/risk items also get a dot on the shared likelihood × impact grid + ONE line: the real-world scenario in which the
bad outcome occurs.

## Workflow — the seven SOPs (⛔ Dave 2026-09-10: "I like the seven new principles. Keep all.")

The pipeline, in one line: `cards.json` (what an item is) → `decisions.py` (what it asks: options, recs, STAGE, BAKED,
HOLD) → frames (`option_frames.py` / `triage_frames.py` / `real-capture.mjs`) → `build.py` → checks → publish → the
next session's sweep. File names are for you; none of them reach a card.

### 1 · Sweep — the first action of every groom or overnight-build session, and before ANY "what's open" answer

Dave rules on the board while the chat runs (10 Sep: P was "ruled · here" on his screen while the chat still called it
open). A status answer that did not start with a sweep is a guess.

1. **Account check.** `Artifact action:"list"` — the board's URL must be in the user's OWN list. If it is not, the
   session is on the other account: stop and tell Dave which account to `/login` as. (A `read_db` on the wrong account
   fails as "no such artifact … or no access".)
2. **Read the store.** `read_db db_op:"list"` on `rulings` and on `notes`. `rulings/<KEY>-<n>` = `{choice, words, at}`
   (a choice decision is ruled when `choice` is set; a text-only one when `words` is non-empty); `rulings/<KEY>-stage` =
   `{choice: advance|keep|icebox}` on a not-yet-groomed item; `notes/<KEY>` = `{text, at}`, the "Questions & feedback"
   field.
3. **File every ruling ⛔-VERBATIM** in BACKLOG.md under its item: quote the option's text, never just the letter; `words`
   is Dave's wording and goes in as typed. A staged note is one of three things — a question to answer IN the frames
   (SOP 4), a ruling to file, or a hold ("let's talk", "discuss before…") that keeps the item in Needs grooming (SOP 6).
   `advance` → groom it this session; `keep` → stays; `icebox` → Icebox with a revisit trigger.
4. **Commit on the session's doc branch, arm auto-merge, wait for main.**
5. **Then, in this order:** the PR is on `origin/main` → add each swept ruling to `BAKED` in `decisions.py` (id →
   letter + where filed; a held item also gets a `HOLD` line) → build + checks + republish (SOP 5) → THEN delete the
   swept docs with `write_db db_op:"delete"` (rulings and notes). A ruling is not swept until its ⛔ line is on main
   (9/8: the store was cleared first and ruled items briefly read as open again). Only docs written while the store was
   unreachable re-push from a device, so deleted = gone.

### 2 · Intake — an item becomes a card

- Sources: BACKLOG.md from `origin/main` (the primary checkout lags) + anything Dave names (Notion cards, chat, memory
  follow-ups). The originating session fills BACKLOG.md's capture template while its context is hot.
- A card = one entry in `cards.json`: key, section (rule 4), title in product words, one-line sub (what happens to the
  person), the standard dimensions, population. **Keys are stable forever** — the store is keyed on them.
- Fill the dimensions honestly from the code (delegate the sweep to an Explore agent; never guess). Code facts feed the
  chips and BACKLOG.md, not the card.
- Stage: `STAGE[key] = 'triage'` (+ a `STAGE_NOTE` saying why it waits) until Dave advances it. A triage page is
  curated for a fast call (principle 4): title, sub, "Not yet groomed", ONE basic app-UI mockup (`triage_frames.py`,
  keyed in `build.py`'s `TRIAGE_MOCK`; a UX item always gets one), the three buttons, the feedback field; the grooming
  questions and chips fold under Details. On the dashboard it wears the amber "groom?" pill.
- Bug/risk items also get their dot on the risk grid (`legacy_blocks.json`) with the one-line scenario.

### 3 · Decide — what each card asks

- `decisions.py` `DEC[key]`: one entry per question — the question in plain words, lettered options with the rec marked
  `True`, or `[]` for a text-only answer. Ids are `<KEY>-<n>`; never renumber a live one.
- **Fact or decision?** Before writing a question, check the code. A fact is stated (in the question itself or in
  `CONTEXT[id]`, one situation paragraph) and the decision is reframed or dropped (principle 2).
- **Data provenance** (engineering step, never a card element): every datum a frame renders exists / is derivable / is
  MISSING — MISSING becomes one plain option ("needs one new piece of stored information — build it too?"), never a
  build-time surprise (#1564). Every status or word a frame uses must exist in the app ("Recs Approved" was not a
  status). The verification facts go to BACKLOG.md when the item is queued.
- **Money rule changes** get a per-line before/after table from the real record (decision · inputs · today · after A ·
  after A+B), never an illustrative number. **AI-generated output** gets a gallery of ≥10 REAL worst-shape inputs on the
  board before the decision (9/7: ten real McGrath write-ups reversed a three-times-recommended cue-card direction).
- The rec and its rationale sit on the option: `OPT_VIS[id][letter]['why']`, one sentence about the person it affects
  (principle 15).

### 4 · Frame — what each option looks like

- Which shape: `frames_for(key)` in `build.py` — `flip` (Today | Proposed over one frame), the walkthrough (per-actor
  strip under the same switch), or `none` for a non-UX item (principle 5). Per-option frames go in
  `OPT_VIS[id][letter]['frame']`; a many-shape decision is a `GALLERY[id]` (`GALLERY_FULL` / `OPTS_FULL` = one per row at
  true size).
- **Drawn** (`lib.py`, `option_frames.py`, the `*_card.py` files) for a flow, a label, or an element that does not exist
  yet. Read the real component first so columns, labels and pill styles match; real values from a real record or grey
  bars; probe the COUNT, not the excerpt (MPI-6 drew 3 notes, the record had 4).
- **Captured** (`real-capture.mjs`) for density, spacing, alignment, sizes, a component's height or shape on an EXISTING
  screen — on the device the role uses (principles 11 and 16). `MODE=inspect` first to dump the real markup and block
  sizes; write each option as a CSS/DOM override against real testids; capture; the measured height goes in the caption;
  files land in `real/` + `heights.json`. One screenshot per option, one column at full width.
- A staged note about a frame is answered by redrawing the frame and its result (rule 6) — the answer is a picture, in
  the board's own type outside the frame (principle 13).

### 5 · Build, check, publish

- `python3 phone-board/build.py` (absolute paths; NEVER `cd`), then `node phone-board/test9.mjs` — phone + desktop
  routing, tapping, notes, scroll stability, zero page errors.
- **Screenshot pass before every publish**, after `document.fonts.ready`: every changed card at 1280 and at 390. Check
  the DATUMS (a builder invented a line title, a $ figure, a note and a status label in one pass) and the "Never on a
  card" list. The reviewer who let the engineer-style cards through was the author.
- Republish with the board's URL as `url`. A deleted or invisible artifact (account switch) → publish WITHOUT `url`,
  then update BACKLOG.md's header and memory `reference_grooming_board_account_and_url` the same turn.
- Delegation: one Opus builder per card, never a whole-board rewrite; every brief opens, verbatim, with "NEVER `cd` in a
  Bash command — every command uses absolute paths". Details and past failures: `phone-board/README.md`.

### 6 · File and queue

- **Every decision ruled** → the item's heading gains "⛔ RULED from the board, <date> — QUEUED" and the entry moves to
  **Queued** at the top of its surface, carrying: the rulings verbatim (option text + his words), **Sensitivity** (picks
  the pre-push mirror and the ledger emphasis — NEVER a merge hold: green = merge, Dave's standing rule), **Files to read
  first** (THIS is where `file:line` anchors from the Explore sweep land), **Sentinels**.
- **Held** ("let's talk", "discuss before the overnight run") → the partial rulings and his note go in verbatim, the
  item STAYS in Needs grooming with the code facts, and `HOLD[key]` in `decisions.py` makes the board read "ruled ·
  discuss". The overnight run never takes a held item. **A ruling or note that RAISES a question becomes a new lettered
  decision on the card — with the code facts in its question and a rec — in the same session** (⛔ Dave 2026-09-10, S:
  his S-2 words raised three questions that lived only in chat; "why did those open items not find their way into the
  card? That seems like a process miss"). Held means held for HIS rulings on the board, never for a chat conversation;
  a chat answer is a draft of the card, not a substitute for it.
- On the board a filed decision is ONE line (principle 14): `BAKED[id]` = letter + where it was filed.
- One doc branch per sitting; arm auto-merge at the close (each doc PR lands in ~2 minutes, so back-to-back PRs at the
  same BACKLOG anchor go dirty). Commits pushed to a branch after its PR merged go nowhere.

### 7 · Close

- Recap in chat: what is Queued (run-ready), what is still open, what is held and what the conversation must settle,
  what went to Icebox with its revisit trigger. Update the epic status in memory. If Dave says run tonight → `/overnight-build`.

## Cost control
Triage cards are cheap on purpose; frames only after Dave advances an item. A deep UX groom ≈ one mockup round of
tokens — say so if he advances 5+ UX items at once. Ask ONE question before a redo when the answer changes what gets
built; assume the rest and say what you assumed.

## Integration
- Upstream: Notion (capture inbox) → items named in chat → this skill.
- Downstream: `docs/overnight/BACKLOG.md` (Queued, ⛔ rulings) → `/overnight-build` (its preflight runs SOP 1 too).
- `artifact-design` loaded before any board HTML is written by hand; `artifact-capabilities` before a publish that
  declares `db`.
