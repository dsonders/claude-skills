# PH hover — the "Changes · N" link needs a hover state (real desktop frames, 2026-09-21)

Dave, 21 Sep: *"I like C, but this element also needs a hover state, so the user doesn't necessarily
need to click it to see the price change history. Mock that up as well."*

Advisor at 1440 on **app.tenthgear.ai**, RO **6672** (TD1), same fixture as the 15 Sep PH frames:
line 1 **Fuel gauge · 13 changes**, line 2 **Brakes · 21 changes**, all built from this RO's own
`ro_change_events` rows. Every name, time, part, price and before/after below was written by the
app's recorder while a real E2E user made the change through the API. Nothing is drawn.

The resting link is unchanged — `ph-b-card-link.jpg` still is TODAY. It was re-captured this run and
came back identical, so that frame is reused rather than replaced.

---

## H1 — hover opens the whole panel
`ph-h1-line1.jpg` · `ph-h1-line2.jpg` · `ph-h1-pinned.jpg` · `ph-h1-line2-capped.jpg`

Resting the mouse on "Changes · 13" opens **the same panel the click opens** — under the card, over
the page, this line's events only, newest first. The only difference from the clicked state is the
header's right slot: on hover it reads a faint *Click to keep open*; once you click it becomes the
close **×** (`ph-h1-pinned.jpg`). The link itself goes from a 1px underline / gray-700 to a 2px
underline / gray-900. Moving away closes it.

- Link **73 × 18 px**. Panel **492 px wide** — the card's own width — left-aligned to the card,
  **12 px** below its bottom edge (340 px below the link).
- Line 1: panel **837 px** (13 rows). Card + gap + panel = **1 208 px**.
- Line 2: panel **1 292 px** (21 rows). Card + gap + panel = **1 747 px**.
- **It needs a cap.** At 1440 × 900, even with the card parked at the very top of the viewport, line 1
  overflows the fold by **308 px** and line 2 by **847 px** — and on the real page the card sits about
  850 px down, so an uncapped hover panel starts entirely below the fold. `ph-h1-line2-capped.jpg`
  shows a **420 px** scrolling body: panel **469 px**, **7 of 21** rows visible. 420 still runs 24 px
  over a 900-tall viewport with the card at the top, so the honest cap is **~390 px**, plus a
  flip-above-the-card fallback for a card low on the screen.
- Honest caveat: a scrolling panel you can only keep open by not moving the mouse is a contradiction —
  to scroll those 21 rows you have to travel from the link into the panel, so the close rule has to be
  "leave the link *and* the panel", with a grace delay. That is the real cost of H1.

**Build shape:** one `LineChangesPanel` component, two triggers. Hover and click render the identical
panel; the trigger owns `open` / `pinned`, and `pinned` swaps the hint for the ×. No second component,
no second formatter. Desktop only — `useCanHover() && !useAnyCoarsePointer()`, or the Radix trigger
eats the tap on a phone (`docs/pitfalls.md` §Radix).

---

## H2 — hover shows a compact card: the last 3 changes + "and N more"
`ph-h2-line1.jpg` · `ph-h2-line2.jpg` — and the same card moved clear of the line:
`ph-h2-line1-right.jpg` · `ph-h2-line2-right.jpg`

A small card anchored to the link, **360 px wide**, three rows newest first in the same row format
(time · sentence · actor + role), then one footer line: *"and 10 more · click to see all"*. Clicking
opens the full H1/B panel.

- **Its height does not grow with the line** — **279 px** for line 1's 13 events, **261 px** for
  line 2's 21. That is H2's whole argument: one size, always on screen, never a scroll.
- Right-aligned under the link (as specified) it sits at x = 155, 8 px below the link — and **covers
  the card it belongs to**. On line 1 that is 279 px of a 359 px card: Labor, both part rows, Parts
  subtotal and the Line total all disappear behind it. On the taller line-2 card the subtotal and Line
  total survive, but the Labor row and every part name go. Those are the numbers the advisor is
  hovering in order to reason about. The two `-right`
  frames move it to **card right edge + 14 px** (x = 602), which clears the line completely and lands
  on the Customer-link column instead. Same card, same content, only the anchor differs.
- Honest caveat: three rows answers "what just happened", not "who changed this price". On line 2 the
  three newest rows are a labor-rate change plus two of Dan Roberts' six re-prices, all stamped
  10:46 PM — so the preview shows two thirds of one burst and the footer ("and 18 more") is doing most
  of the work. The row that matters to an advisor asking *why is this line $896.70* is somewhere in
  the 18.

**Build shape:** a `RowHoverCard` (the existing hover route, per `design.md`) whose body is the first
three rows of the same `describeChange()` output, plus a count line. The full panel still has to exist
for the click, so H2 is H1 **plus** a second, smaller renderer — slightly more to build than H1, not less.

---

## Two different hovers on the same card
`ph-d-hover.jpg` (unchanged, 15 Sep) is the other one: hovering **the part's price** shows
*"$179.95 · was $184.20 · Dan Roberts · 10:50 PM"* inline, 34 px, one field's last change. H1/H2 hover
the **header link** and answer for the whole line. They are compatible — the price hover is the
one-question shortcut, the link hover is the list — but shipping both means two hover behaviours on one
card, and the price hover already answers the single most common question for free.

## Recommendation
**H1 with a ~390 px cap.** It is one component instead of two, it is the same thing whether you hover
or click (nothing new to learn, nothing hidden behind a count), and the cap plus a flip-above fallback
is a solved layout problem. H2's flat height is genuinely nice, but it buys that by showing three rows
that, on the worst-shape line, are three versions of the same event — and it still needs the full panel
underneath it.
