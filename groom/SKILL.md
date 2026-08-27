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
4. **Priority order:** UX-impacting items first; among those, reliability/performance
   implications outrank pure polish. Behind-the-scenes (tech debt, security) after. Icebox last.
5. **Votes come back by letter in chat** (or as artifact comments — those reach the session).

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
   styles). The proposed change gets a soft highlight ring so the eye lands on it. When there's
   no single obvious design: THREE lettered directions (C-A / C-B / C-C), one trade-off line
   each. Mobile surfaces = 390px phone frames of the real header/strip. The board renders in
   light or dark; the screen frames pin their own literal light palette (scoped `.app-screen`)
   so they look like the app in both.
6. **Consequence line** — one sentence: what the user gets, e.g. "Parts sees the RO again, with
   the reason, and it drops off by itself when the last part is pulled — no new status, no new
   screen."
7. **Ballot** — plain questions, ids = card letter + number (A1, A2…), the recommended answer
   marked `REC: YES` / `REC: FIX THEM TOO` first, one-sentence why about the person. The
   data-provenance check (below) collapses to at most ONE ballot line: "This needs one new
   piece of stored information on each RO — build it as part of this?"

**Never on a card:** file names, function/field names, predicates, `code` chips, provenance
strips, "sensitivity" banners in engineering terms, counts like "4 to vote", status IDs
(use the label the app shows: "Waiting for Parts", never `waiting_for_parts`), or the words
denorm/flag/predicate/backfill (say "stored information", "a one-time cleanup you run").

**Every card head is a collapse toggle** (Dave, 2026-08-26: "I don't want to look at them after
they are decided"). The reference board's script does it: click/Enter on `.card-head` toggles
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
   item's why in one line on its card. Section structure stays (Ready to run / To groom UX /
   To groom behind-the-scenes / Icebox) but WITHIN sections the order is the ranking — and if
   a behind-the-scenes item genuinely outranks a UX item, say so on its card rather than
   silently reshuffling sections.
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
  three lettered directions when there's no single obvious design. Text = captions and
  trade-off lines only. (Full multi-round ballots may graduate to a design canvas — link it
  from the card, but the decision summary stays on the board.)
- **Behind-the-scenes items:** the same anatomy in product words (what the user/agent asked
  for → what they got today → what they'd get). Include the risk-grid dot + the one-line
  scenario.
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
   file:line anchors from the Explore sweep land), commit the doc (doc-only branch + PR +
   auto-merge), republish the board showing the item as Ready to run.

### Close
- Recap in chat: what's Queued (run-ready), what's still open, what got iceboxed with its
  revisit trigger. If Dave says run tonight → invoke `/overnight-build`.

## Cost control
Triage cards are cheap on purpose; mockups only after Dave advances an item. A deep UX groom
≈ one mockup round of tokens — say so if he advances 5+ UX items at once. Ask ONE question
before a redo when the answer changes what gets built (e.g. real screenshots vs drawn mocks —
he chose drawn, in the app's style); assume the rest and say what you assumed.

## Integration
- Upstream: Notion (capture inbox) → items named in chat → this skill.
- Downstream: `docs/overnight/BACKLOG.md` (Queued, ⛔ rulings) → `/overnight-build`.
- `artifact-design` loaded before board HTML; mockup/board building delegated to Opus agents
  briefed in product words with `reference-board.html` as the template.

## Success criteria
- [ ] Board current, one URL, all items carded with honest dimensions
- [ ] Zero code identifiers on any card (screenshot-checked before publish)
- [ ] Every advanced item decided by ballot; zero rulings left only in chat
- [ ] BACKLOG.md updated + committed in the same session; board republished to match
