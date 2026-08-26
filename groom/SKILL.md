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
1. Read `docs/overnight/BACKLOG.md` + any new items Dave names (Notion cards, chat, memory
   follow-ups). Investigate the code enough to fill the dimensions honestly — delegate repo
   sweeps to an Opus Explore/general agent; never guess a dimension.
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
3. Build/refresh the board in that order (Opus agent builds the HTML; load `artifact-design`
   before writing it). Each item = a CARD: name, the dimension row, and ONE cheap visual —
   a screenshot crop, a mini table, a 5-box flow, or its dot on the risk grid. No mockups yet.
4. Publish (same URL), hand Dave the link + a one-line ask: "pick what advances."

### Pass 2 — Groom (deep, only what Dave picked)
For each advanced item, extend its card on the SAME board:
- **UX items:** visual representation of the CURRENT UX (screen, series of screens, or flow
  diagram) beside the PROPOSED change. When there's no single obvious design → THREE lettered
  directions. Desktop + mobile when the surface has both. Text = captions and trade-off
  bullets only. (Full multi-round ballots may graduate to a design canvas — link it from the
  card, but the decision summary stays on the board.)
- **Behind-the-scenes items:** current situation vs proposed as a diagram/table (before/after
  boxes, the write path, the gate that's missing) — slightly visual beats prose. Include the
  risk-grid dot and the one-line scenario.
- Every card ends with its BALLOT: the specific questions, lettered, with a recommendation
  first (recommendation = the manager's, argued in one line).
5. Dave votes by letter in chat → write each ruling VERBATIM (⛔) into BACKLOG.md, move the
   item to Queued with files-to-read + sensitivity + sentinel notes, commit the doc
   (doc-only branch + PR + auto-merge), republish the board showing the item as Ready to run.

### Close
- Recap in chat: what's Queued (run-ready), what's still open, what got iceboxed with its
  revisit trigger. If Dave says run tonight → invoke `/overnight-build`.

## Cost control
Triage cards are cheap on purpose; mockups only after Dave advances an item. A deep UX groom
≈ one mockup round of tokens — say so if he advances 5+ UX items at once.

## Integration
- Upstream: Notion (capture inbox) → items named in chat → this skill.
- Downstream: `docs/overnight/BACKLOG.md` (Queued, ⛔ rulings) → `/overnight-build`.
- `artifact-design` loaded before board HTML; mockup/board building delegated to Opus agents.

## Success criteria
- [ ] Board current, one URL, all items carded with honest dimensions
- [ ] Every advanced item decided by ballot; zero rulings left only in chat
- [ ] BACKLOG.md updated + committed in the same session; board republished to match
