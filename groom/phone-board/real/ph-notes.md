# PH — Price-change history on the line (real desktop frames, 2026-09-15)

Advisor at 1440×900 on **app.tenthgear.ai**, RO **6672** (TD1 test store), every frame the live page
with a DOM override built from **this RO's own recorded `ro_change_events` rows**. No invented datum:
every name, time, part, before/after value below was written by the app's own recorder while a real
E2E user made the change through the API.

## What the fixture produced

| | Events |
|---|---|
| **Line 1 · Fuel gauge** (recall, 2 parts) | **13** |
| **Line 2 · Brakes** (customer pay, 6 parts — the worst shape) | **21** |
| **This repair order** (status ×2, technician assigned) | **3** |
| **Total** | **37** |
| Human internal notes on the RO | 2 |

Line 1 = price, re-price, re-price again, quantity, stock answer, note edit, labor hours ×2, labor rate.
Line 2 = 6 parts added, each priced once and re-priced once (18 parts events) + labor hours + labor rate + the line label.
Actors: **PJ Macklin** (advisor), **dave** (tech), **Dan Roberts** (parts), **Dave Sonders** (admin) — the real E2E accounts.

## The options

### A — every change as a system note in the real thread
`ph-a-collapsed.jpg` · `ph-a-thread-full.jpg` · `ph-a-dock-full.jpg`

Events and notes interleaved by time, same row shape as a note (avatar, name, role tag, absolute time),
with a line chip (`LINE 1 · FUEL GAUGE` / `THIS RO`) in front of the sentence.

- Thread goes **303 px → 2 125 px** (7×). 39 items, of which **2** are things a person wrote.
- The two human notes are at rows 2 and 25 — the advisor's "customer is waiting in the lounge" sits
  under 22 price rows. This is the honest picture of "too noisy": the thread stops being a place to
  *read* and becomes a place to *scroll*.
- The collapsed bar also changes meaning: badge reads **39**, and the one-line preview — today the last
  thing a human said — becomes "Dan: Fuel pump module price $184.20 → $179.95".

### A2 — same thread, each line+actor burst folded into one note
`ph-a2-thread-collapsed.jpg` · `ph-a2-thread-group-open.jpg`

A burst (same line, same person, within 10 min, 3+ changes) renders as one row —
*"LINE 2 · BRAKES · 18 changes · 10:45 PM–10:46 PM ▸"* — that opens in place.

- **936 px** closed (15 items), **1 301 px** with the 18-change group open.
- Both human notes stay in the top third; single events (labor hours, a lone labor-rate change, a status
  move) still render as their own row, so nothing is hidden behind a count.
- Cost: two thread objects to build and reason about (a note and a group), and the fold is a heuristic —
  two people pricing the same line in the same minute stay two rows.

### B — on the line: "Changes · N" in the Parts & Labor card
`ph-b-card-link.jpg` · `ph-b-line1-open.jpg` · `ph-b-line2-open.jpg`

A quiet link in the card header opens a panel **over the page**, directly under the card
(design.md: detail opens over the page, never by growing in place), this line's events only, newest first.

- Line 1 panel **716 px** (13 rows); line 2 panel **1 182 px** (21 rows) — at 1440 the line-2 panel runs
  past the fold, so it wants a max-height with its own scroll.
- The notes thread is untouched: it stays 303 px and stays human.
- What it cannot answer: "what happened on this RO" — you open it per line (2 lines here, 6+ on a real RO),
  and the 3 RO-level events (status moves, tech assignment) have no home.

### C — one centralized log for the RO
`ph-c-control.jpg` · `ph-c-open.jpg`

A `Changes · 37` control in the header beside **Internal notes**, opening one panel over the page with a
header per line (`Line 1 · Fuel gauge — 13 changes · last 10:50 PM`), newest group first, then
`This repair order` at the bottom.

- Panel **680 × 1 998 px** for 37 events — again wants a capped height + scroll; the line headers are what
  keep it readable at that length.
- One control, one place, works for a 2-line RO and a 9-line RO, and it is the only option that has a home
  for the RO-level events.

### D — hover a price for its last change
`ph-d-hover.jpg`

`$179.95 · was $184.20 · Dan Roberts · 10:50 PM` under the part's price. 34 px, costs nothing, answers the
single most common question without opening anything. Not a substitute for B or C — it shows only the most
recent change of that one field. Desktop-only affordance (no hover on a phone).

## Honest gaps — what the recorder does NOT capture

- **The 3C story text is not in this log.** `customer_complaint`, `cause`, `correction` and `notepad_content`
  are deliberately excluded (`RECORDER_OWNED_TEXT_KEYS`) — they are recorded in the older, separate
  `issue_edit_events` collection. A "changes" surface built only on `ro_change_events` will show a labor-hours
  edit but not the tech rewriting the cause.
- **No money consequence is stored.** An event has the field's before/after only. "Line total $725.45 → $X"
  is *not* derivable from the log, so no frame shows one.
- **Paired stamps are skipped by design** (who/when of a status move, `completed_at/by`, `parts_not_needed_by`,
  internal-auth money snapshots, the price-drop announcement stamps, parts-checkout heartbeats, DMS sync).
  The event they belong to is recorded once, with its actor — which is why no frame has a "…and X stamped Y" row.
- **Posting an internal note is not an event** (`internal_notes` is on the skip list) — so option A cannot
  double-count the notes it interleaves.
- **Recording is best-effort**: a failed event write is swallowed with a warning and never blocks the save,
  so the log can have holes with no error anywhere. A UI that says "13 changes" says it about what was recorded.
- `user_id` is `'system'` when no actor was threaded through — the frames have no such row, but a real RO can.
- Part add/remove rows store a JSON blob of the part, not a field pair; the frames render them as
  "X added to the line" / "removed from the line".
- Labor **rate** did record for both an admin and an advisor edit in this fixture (both PATCHes returned 204 and
  both produced a `labor_rate` event) — so the "who may change the rate" question is a permissions question,
  not a recording gap.

## Build shape (if one of these is chosen)

1. **Read endpoint** — `GET /api/repair-orders/:id/changes` (and/or `?issueId=`), org-scoped as a QUERY
   (`where organization_id == active org` + `repair_order_id`), ordered by `created_at` desc, paged.
   Needs a composite index on `(organization_id, repair_order_id, created_at desc)`; there is **no** per-RO
   reader today — the only consumer of `ro_change_events` is the platform overview count (`routes/platform.ts`).
2. **A shared formatter** — one `describeChange(event, partsById, names)` in `shared/` so the sentence is
   identical wherever it renders (thread row, line panel, RO log, hover chip). Part names come from the
   line's current `parts[]`; a removed part's name comes from the event's own blob.
3. **Actor names** resolve through the per-store membership override (`resolveMemberDisplayName`), never the
   global user doc alone.
4. **UI** — the chosen surface only. A (thread) needs a system-note row type in `TeamNotesThread`;
   B/C need a panel over the page with a capped height (`ph-heights.json` shows why) and the existing
   dark/light role palettes from `NoteRow`.
