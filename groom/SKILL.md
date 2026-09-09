---
name: groom
description: Interactive triage + grooming session for the RO-bot backlog on a visual board — prioritize items, present each with standard dimensions and visual-first explanations, ballot UX decisions with mockups, and write Dave's rulings verbatim into docs/overnight/BACKLOG.md for the overnight-build run. Use when Dave says "groom", "let's groom the backlog", "triage these", "grooming board", "update the board", or wants follow-ups presented for decisions. Designed 2026-08-25 with Dave; the format rules below are his.
---

# Groom: Visual Triage + Grooming Board

One interactive skill, two passes on ONE standing artifact (the Grooming Board). Pass 1
(triage) ranks everything cheaply; Dave picks what advances; pass 2 (groom) spends real
visuals only on what survived. Output = ⛔ rulings written verbatim into
`docs/overnight/BACKLOG.md` (Queued section), which `/overnight-build` consumes.

## Core Rules (Dave's format, 2026-08-25 — don't drift)

0. **The board is written for Dave — not for an engineer, not for an LLM.** He decides from
   what he'd SEE in the app. The first version of this skill produced cards full of predicate
   boxes, `file:line` anchors, field names and "provenance chips"; he rejected it outright
   ("putting code references in a box does not make it a mockup"). Code anchors belong in
   BACKLOG.md's Queued entry (files-to-read), never on a card. See "Card anatomy" below.
1. **Show more than tell.** Visuals carry the explanation; text is sparse. If he has
   questions, he'll ask. Walls of prose are the failure mode this skill replaces.
2. **The board presents; the file records.** The board is REGENERATED FROM BACKLOG.md —
   every ruling lands in the file verbatim (⛔-marked) in the same turn it's made.
3. **One standing artifact, stable URL.** Republish the same board every cycle (its URL is
   kept in BACKLOG.md's header; from a new session, pass it as `url`). Never a new page per
   session. Everything to be triaged AND groomed lives on it — no terminal↔Chrome bouncing.
   Since 2026-09-09 the ONE board serves desktop AND phone (the page lays itself out ≥900px: cards expand in
   place, Today and Proposed side by side, options in a row; below: the phone flow) — one URL, one store. The 8/25
   desktop board (6612d0d8) is retired to archive.
4. **Priority order:** UX-impacting items first; among those, reliability/performance
   implications outrank pure polish. Behind-the-scenes (tech debt, security) after. Icebox last.
5. **Votes come back by letter in chat** (or as artifact comments — those reach the session).
6. **Each open decision sits directly under the options it decides** (Dave, 2026-08-28: "It's hard to
   follow the design options and the decisions that need to be made. Put each open decision adjacent to
   its design options."). No single ballot block at the bottom while a card still has open questions; a
   "Decisions — all ruled" block at the end is fine once everything is ruled. **And feedback on a mockup is
   answered IN the mockup (Dave, 2026-09-04: "I want to work mainly from the UX / UI spaces (review, iterate,
   make decisions)… I expect iteration to happen in that mockup, not simply that new content / decisions needed
   in the DECISIONS / VOTING area"):** a question about a frame ("what happens if he taps Link?") → draw the
   frame and its result; never a chat answer, a table, or a new ballot line in its place. Each decision strip
   sits full-width right under the frame it decides; the bottom ballot exists only once everything is ruled.
7. **Walkthrough shape (Dave, 2026-08-30): one short walkthrough per actor** — (the "draw ONLY the recommended direction" half was SUPERSEDED 2026-09-08 by guiding principle 1: each UX option gets its own frame; the walkthrough is the shape of a complex item's frames) —
   "Case 1 — the tech…: what they see → what the approver sees", ≤ ~6 frames per card; alternatives are one
   text row each in a small table, never drawn. A full directions × screens matrix is built ONLY when Dave
   explicitly asks to see each option ("I need to see each of these mocked up") — rejected 8/30 as "too many
   UI drawings, too much redundancy". Every frame's caption names the actor AND that it is THEIR OWN action
   ("The parts user, when they price a part") — without it a per-actor frame reads as "everyone sees everyone's
   change" (the SA-7-C misread). Mock copy follows app design.md "Notice & status copy": event + consequence
   plainly; one subject one surface; never render what's derivable.
8. **When redrawing a ruled direction, keep every existing control the ruling didn't remove** (the V1
   checklist lost its drag handles; Dave: "we're not losing the drag and drop handles, right?"). A ruling
   that strips chrome lists what goes; everything else stays.

## Guiding principles (⛔ Dave, 2026-09-08 → 09 — both boards; cards share ONE anatomy, each optimized for its screen)

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
14. **Extra text is not free.** Use restraint: only what adds real value to the decision. No extra notes or labels
    when the information is already present or obvious from the screen. Every sentence costs him a read.
15. **When several options need a decision, weigh in: the rec and its rationale**, marked on the option, one sentence
    about the person it affects.

The desktop board adopts this anatomy (card for it in BACKLOG.md → Needs grooming); until then, new desktop cards
follow these principles and the older "Card anatomy" below only where it does not conflict.

## Card anatomy (the approved example — copy it, don't reinvent it)

`reference-board.html` next to this file is the board Dave approved on 2026-08-25 ("SO MUCH
BETTER"). Card A on it is the template. Every groomed card, top to bottom:

1. **Head** — letter key, title in product words, rank badge if it's #1 ("Why #1" in one
   sentence about the customer, never about the code), status pill.
2. **One-line sub** — what happens to the person, e.g. "A part added after the RO is already
   Ready gets approved — but the RO never returns to the parts queue, so nobody pulls it."
3. **Dimension chips** (the standard set below) + **Who hits it** (one sentence).
4. **The story strip** — 3–4 comic-strip boxes in product words, the breaking step tinted red:
   "① Parts adds a part → ② Advisor OKs it → ③ Today: RO drops off the queue → ④ Car delivered
   without it." Caption = Dave's own rule the item violates, if he made one.
5. **App screens, today vs proposed** — drawn in the APP's light look (white surface, the
   app's slate greys, its real row colors/pills/chips, system sans), side by side, wrapping on
   narrow widths. Read the real component first so the drawing matches (columns, labels, pill
   styles). The proposed change gets a soft highlight ring so the eye lands on it — ON ONE ELEMENT per frame at most, never on a header, a button or a whole section, and NEVER on a frame Dave is ruling the DESIGN of (2026-09-07: "there are some unintended blue outlines in the mockup. Please redraw so I can rule on the actual design proposal" — rings on a proposed sheet read as part of the design). When there's
   no single obvious design: pick a recommendation, draw ONLY it, and list the other lettered
   directions as text rows with one trade-off line each (rule 7 — drawn variants only on request). Mobile surfaces = 390px phone frames of the real header/strip. The board renders in
   light or dark; the screen frames pin their own literal light palette (scoped `.app-screen`)
   so they look like the app in both.
6. **Consequence line** — one sentence: what the user gets, e.g. "Parts sees the RO again, with
   the reason, and it drops off by itself when the last part is pulled — no new status, no new
   screen."
7. **Decisions** — ids = card letter + number (A1, A2…), each one a full-width strip DIRECTLY UNDER
   the frame it decides (rule 6); plain question, the recommended answer marked `REC: YES` /
   `REC: THE SHEET` first, one-sentence why about the person. A single "Decisions — all ruled"
   block at the bottom only once every line is ruled. The data-provenance check (below) collapses
   to at most ONE line: "This needs one new piece of stored information on each RO — build it as
   part of this?"

**Never on a card:** file names, function/field names, predicates, `code` chips, provenance
strips, "sensitivity" banners in engineering terms, counts like "4 to vote", status IDs
(use the label the app shows: "Waiting for Parts", never `waiting_for_parts`), or the words
denorm/flag/predicate/backfill (say "stored information", "a one-time cleanup you run").

**Every card head is a collapse toggle, MIRRORED by a "Collapse card" caret at the bottom of every card** (Dave, 2026-08-26: "I don't want to look at them after
they are decided"; 2026-09-07: "put a mirrored expand/collapse toggle (e.g. caret) at the bottom of each card. I like to collapse a card manually as soon as I've ruled on it" — the script appends `.card-foot .chev-foot` to each card and it shares the head's toggle + localStorage key; it hides itself when collapsed because `.card.collapsed > :not(.card-head)` is display:none). The reference board's script does it: click/Enter on `.card-head` toggles
`.collapsed` (hides everything but the head); cards with a `Queued` key or a status pill reading
"ruled …" (and NOT "to vote") start collapsed; the viewer's choice is remembered in
`localStorage` keyed by the card title. Keep the script when regenerating the board, and keep the
status-pill wording convention so auto-collapse keeps working.

Triage cards (pass 1) are the same anatomy minus 5–7: head, sub, chips, who-hits-it, ONE cheap
visual (a 3-box story strip, a mini table, or the dot on the risk grid), and the open questions
as chips. Behind-the-scenes items still get product-word screens (a request→response card,
a "who gets told today" table), not diagrams of code.

## Standard dimensions — every item card carries these

| Dimension | Values |
|---|---|
| UX impact | High / Med / Low, + a ⚡reliability/perf flag when applicable |
| T-shirt size | S / M / L / XL |
| Est. Codex rounds | 0–1 / 2–3 / 4+ (permission/model rewrites trend 4+ → split candidates) |
| Reversibility | revert-cheap code ↔ touches data (decides the overnight hard floor) |
| Population | who actually hits it — pre-answer "do we have customers using this?" |

**Bug/risk items additionally:** plot on a likelihood × impact grid (one shared 2×2 with all
risk items as dots — a glance, not paragraphs) + ONE line: the real-world scenario in which
the bad outcome occurs.

## Workflow

### Step 0 — Sweep the phone board (EVERY groom or overnight-build session, before anything else)
Dave rules from his phone or desktop with no session running (built 2026-09-08, one responsive page 9/9). The **board** —
https://claude.ai/code/artifact/5089d5b5-577e-402b-95ec-8b0fd421576d (URL also in BACKLOG.md's header) — saves
each tap into the artifact's own store; nothing reads it until a session sweeps it. The sweep:
1. `Artifact action:"read_db" db_op:"list" collection:"rulings"` and the same for `collection:"notes"`.
   Docs: `rulings/<KEY>-<n>` = `{choice:"A", words:"…", at}` — a choice decision is ruled when `choice` is set, a
   text-only decision when `words` is non-empty; `rulings/<KEY>-stage` = `{choice:"advance"|"keep"|"icebox"}` = Dave's
   triage call on a NOT-YET-GROOMED item (`advance` → groom it this session with real screens; `keep` → stays in Needs
   grooming; `icebox` → Icebox with a revisit trigger); `notes/<KEY>` = `{text, at}` = the "Questions & feedback" field.
2. Write every ruling ⛔-VERBATIM into `docs/overnight/BACKLOG.md` under its item (`words` is Dave's wording; the
   letter maps to the option text in the phone board's `decisions` data — quote the option text, never just "A").
   An item whose every decision is ruled moves to **Queued** with files-to-read + sensitivity, exactly as a chat ruling.
3. Every staged note is a question to answer IN THE FRAMES (rule 6): redraw / extend the item's card on the board
   and the phone board, never a chat reply or a ballot line. A note that is itself a ruling gets filed as one.
4. Commit the doc (one branch per session, auto-merge). ORDER MATTERS (9/8 lesson — the store was cleared first and the
   ruled items briefly read as open again): once the PR is on `origin/main`, add each swept ruling to `BAKED` in
   `phone-board/decisions.py` (id → letter + "filed #PR"), rebuild + republish the phone board (baked decisions render
   ruled and untappable; a fully baked item reads "ruled · queued"), THEN delete the swept docs with
   `write_db db_op:"delete"` (rulings and notes). A ruling is not swept until its ⛔ line is on main. (9/9 lesson: a
   device that still held swept docs locally re-pushed them on reconnect — the page now pushes only docs written while
   the store was unreachable, so deleted = gone.)
5. Rebuild the phone board whenever the backlog changes (new to-vote cards, a card re-drawn): source in
   `phone-board/` next to this file (README there) — `decisions.py` turns every card's questions into lettered
   options with the rec marked (open-ended questions = text-only decisions) and `STAGE` marks which cards are still
   triage. ⛔ Dave 9/8, the not-yet-groomed page is CURATED for a fast call: title + one-line sub, "Not yet groomed",
   ONE basic app-UI mockup (`triage_frames.py` — visual beats text; a UX item always gets one), the three buttons
   (Advance to grooming / Keep in backlog / Send to Icebox), the feedback field, and nothing else — the grooming
   questions and chips fold under Details. No helper sentences. On the dashboard it wears an amber "groom?" pill.
   `python3 build.py`, run the Playwright checks, republish with the phone board's URL as `url`.
   Keep the card keys stable — the store is keyed on them.

### Pass 1 — Triage (cheap, whole backlog)
1. Read `docs/overnight/BACKLOG.md` (from `origin/main` — the primary checkout lags) + any new
   items Dave names (Notion cards, chat, memory follow-ups). Investigate the code enough to fill
   the dimensions honestly — delegate repo sweeps to an Opus Explore agent; never guess a
   dimension. The code facts feed the CHIPS and BACKLOG.md; they do not appear on the card.
2. **Prioritize by judgment BEFORE building the board** — every groomable item ranked most→
   least important, top to bottom of the artifact; the ORDER is the recommendation. Weigh, in
   roughly this order: (a) UX impact, with reliability/perf implications outranking polish;
   (b) population — how many real users hit it, how often; (c) risk-grid position for
   bugs/risks (likelihood × impact); (d) anything Dave flagged urgent or a customer reported;
   (e) cluster/sequencing dependencies (an item that unblocks others rises). State the #1
   item's why in one line on its card. Sections are PRODUCT SURFACES (Dave, 2026-09-03: "that's how I'd like
   to roll through the backlog, with MPI and Video items at the top"): MPI & Video → Parts page &
   queue → RO page (advisor/admin/tech) → Dashboards → Customer page → Store settings (labor rates &
   money) → Platform & tooling → Risk grid → Icebox → Archive. Queued (ruled) cards sit at the TOP of
   their surface section, collapsed; WITHIN a section the order is the ranking.
3. Build/refresh the board in that order (Opus agent builds the HTML from `reference-board.html`
   + a content brief written in product words; load `artifact-design` before writing). Triage
   cards per "Card anatomy". No mockups yet.
4. **Look at it before publishing.** Screenshot the board (repo Playwright: copy a script into
   `/ro-bot/app` so `playwright` resolves; `article.card` locator) and check each card against
   the "Never on a card" list. The reviewer who let the engineer-style cards through was the
   author.
5. Publish (same URL — `action: read` the live artifact first, Read the saved file in full, then
   publish with `url`), hand Dave the link + a one-line ask: "pick what advances."

### Pass 2 — Groom (deep, only what Dave picked)
For each advanced item, extend its card on the SAME board per "Card anatomy" 4–7:
- **UX items:** today vs proposed app screens (desktop + mobile when the surface has both);
  the recommended direction drawn, other lettered directions as text rows (rule 7). Text =
  captions and trade-off lines only. (Full multi-round ballots may graduate to a design canvas — link it
  from the card, but the decision summary stays on the board.)
- **Behind-the-scenes items:** the same anatomy in product words (what the user/agent asked
  for → what they got today → what they'd get). Include the risk-grid dot + the one-line
  scenario.
- **AI-generated output = a gallery of ≥10 REAL worst-shape inputs on the board BEFORE the decision strip (2026-09-07):** the 28 Aug golden set was hand-written and short; the real McGrath write-ups (10–30 sentences) turned a three-times-recommended cue-card direction into "back to the drawing board" the moment Dave saw ten of each. Probe the real population, take the longest/messiest ten, render them under the rule, print the counts.
- **Real figures only + a before/after table when a rule changes money (2026-08-26, card K):**
  every $ on a mockup is read from the actual record (read-only probe of the real RO + the org's
  rates), never an illustrative number; every story step is what the app actually allows for
  that role today (probe `requested_by`/authorship — a row's author can contradict the code
  comment). When a proposed rule changes arithmetic, the card carries a per-line table
  (decision · inputs · today · after rule A · after rule A+B) so Dave can see the logic, not
  just the new total. Use the app's own nouns; a coined term ("note row") stops the vote.
- **Data provenance check (engineering step, not a card element):** before drawing, verify
  every datum a mockup RENDERS (a name, timestamp, count, status label) exists / is derivable /
  is MISSING — and that any status or vocabulary the mock uses actually exists in the app
  ("Recs Approved" was not a status; the approved destination is "Waiting for Parts"). MISSING →
  one plain ballot line ("needs a new piece of stored information — build it too?"), never a
  build-time surprise (the #1564 completion-stamp lesson). The verification facts go into
  BACKLOG.md when the item is Queued.
- Every card ends with its BALLOT per anatomy 7.
- Screenshot-check again before publishing.
5. Dave votes by letter in chat → write each ruling VERBATIM (⛔) into BACKLOG.md, move the
   item to Queued with files-to-read + sensitivity + sentinel notes (THIS is where the
   file:line anchors from the Explore sweep land), commit the doc, republish the board showing
   the item as Ready to run. **ONE open doc branch per voting session** — each ruling is a new
   commit on it (auto-merge takes it when the session pauses); back-to-back PRs inserting at the
   same BACKLOG anchor go DIRTY on GitHub as each merges (6 PRs, 2 rebuilds on 2026-09-04). Auto-merge lands
  each doc PR in ~2 minutes, so "one branch per session" only holds if you ARM auto-merge at the session's close —
  otherwise it is one PR per ruling (nine on 6–7 Sep; harmless, but sequential). A per-ruling script (move the card
  to Queued + mark the board card ruled + re-splice) makes each vote a one-call turn. A
   "sensitivity" note picks the pre-push mirror and the ledger emphasis — NEVER a merge hold: a
   groomed item's every decision is Dave's, so green = merge (his standing rule; re-asked 9/4).

### Close
- Recap in chat: what's Queued (run-ready), what's still open, what got iceboxed with its
  revisit trigger. If Dave says run tonight → invoke `/overnight-build`.

## Building the board — what actually works (2026-08-27/28)
- **One Opus builder per card (or per pass), never one giant rewrite** — a builder asked to regenerate the
  whole board stalled at the 600s no-progress watchdog after writing the file; it recovered only because
  the file was already on disk. Brief: write each card to `scratchpad/cards/<key>.html`, splice with a
  short Python script, run three checks (article count, banned-term grep, every class defined), STOP.
- **The template's shared mock CSS lives inside the archived cards' `<style>` blocks** (`.story`,
  `.screens`, `.app-screen`, `.as-*`, `.conseq`, phone plate/tabs) — hoist them into the main stylesheet
  before dropping the archive, or every new card renders unstyled.
- **Read the real screens and the real records BEFORE the brief** (Explore agent for component anatomy +
  a read-only Firestore probe for a real RO/video): the sweep changed the V6 story (there is no Stop
  button) and produced the whole V1 fixture (RO 832936's shot list). Shot numbering: content shots only,
  bookends unnumbered — a locked ruling the builder will get wrong unless told.
- **Screenshot every card before publishing and check the datums, not just the layout** — the builder
  invented a line title, a $ figure, a note and a status label across four cards in one pass; only the
  screenshot pass caught them. Silhouettes (grey bars, "Part 1", "Line title") are the fix when no real
  value exists.
- The publish gate requires the live artifact file to be Read in full (4–5 chunks of ≤1000 lines) before
  the first republish of a session; budget for it.
- A deleted artifact ends the watch with "artifact not found"; republish WITHOUT `url` to a new one and
  update the URL in BACKLOG.md's header + the pipeline memory the same turn.
- **An account switch (`/login` to another email) makes the artifact invisible too** — publish
  without `url`, update the header URL + memory (2026-09-03: dsonders@gmail → dave@tenthgear).
- **Probe the COUNT, not the excerpt.** MPI-6's frames drew 3 notes; the record had 4, and "McGrath
  techs are saying this" was ONE tech on ONE inspection — the read-only probe over the whole org
  caught both. Before drawing from a real record, query the full population and state it honestly.
- **Edit the board with tag-depth-aware splicing, never `.*?</div>` regexes** — a row-cloning regex
  nested the 4th note inside the 3rd on two sheets; a 12-line depth counter (`<div`/`</div>` tokens →
  block end) fixed it. Keep `cards/<KEY>.html` as the unit; re-splice by `<span class="key">` match.
- **Screenshot only after `document.fonts.ready`** — before the webfont lands, ballot lines render
  unwrapped and look clipped; a real bug was chased for a round on that false alarm.
- **Every builder/Explore brief opens with, verbatim:** "NEVER `cd` in a Bash command — every
  command uses absolute paths"; a soft "use absolute paths" mid-brief was ignored and each
  `cd … && grep relative-file` popped a permission prompt for Dave even under claude-yolo.

## Cost control
Triage cards are cheap on purpose; mockups only after Dave advances an item. A deep UX groom
≈ one mockup round of tokens — say so if he advances 5+ UX items at once. Ask ONE question
before a redo when the answer changes what gets built (e.g. real screenshots vs drawn mocks —
he chose drawn, in the app's style); assume the rest and say what you assumed.

## Integration
- Upstream: Notion (capture inbox) → items named in chat → this skill.
- Downstream: `docs/overnight/BACKLOG.md` (Queued, ⛔ rulings) → `/overnight-build`.
- Sideways: the phone board's store (Step 0) → swept into BACKLOG.md at the start of every session; ⛔ Dave 9/8: the phone shows APP-UI frames only (Flip for simple items, the walkthrough inside a Flip for complex ones, no drawing for non-UX items) — memory `project_groom_board_mobile_ruling`.
- `artifact-design` loaded before board HTML; mockup/board building delegated to Opus agents
  briefed in product words with `reference-board.html` as the template.

## Success criteria
- [ ] Board current, one URL, all items carded with honest dimensions
- [ ] Zero code identifiers on any card (screenshot-checked before publish)
- [ ] Every advanced item decided by ballot; zero rulings left only in chat
- [ ] BACKLOG.md updated + committed in the same session; board republished to match
