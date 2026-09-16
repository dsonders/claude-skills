# Card D3 — Pipeline / List toggle: real desktop captures (2026-09-15)

Surface: `https://app.tenthgear.ai/admin/dashboard`, admin role, test org (multiplayer), live page,
every option applied as a CSS/DOM override on the real DOM. Viewport 1440×900 and 1120×900,
deviceScaleFactor 2. Filters applied in every shot: **Status = Parts Pricing · Technician = Cam
Drummond · Advisor = PJ Macklin** (9 rows still in the list), search box left empty, Age left at
"All Age" — so the "× Clear" button the card blames is on screen in every capture.
Measurements: `d3-heights.json`. No repo files were changed.

---

## Headline: the clipping does not reproduce on today's build

"List" truncating to "Li" **did not happen at any width I tested from 820 to 1440 px** (18 widths). The toggle held
**124 px** at every width, and its "List" label measured 23.2 px of text in 23.0 px of box —
i.e. it is painted whole, with no room to spare. What happens instead when the row runs out of
width is a **wrap**: the [Pipeline | List] + New RO group drops to a second row.

| Viewport | Toolbar block | What it does |
|---|---|---|
| 1440 / 1280 / 1260 / 1220 / 1200 / **1180** | 40 px | one row |
| **1160** / 1152 / 1120 / 1024 | 86 px | toggle + New RO wrap to row 2 |

The reason is already in the code: `md:shrink-0` on the toggle plus `md:flex-wrap` on the desktop
row, both added 2026-08-19 in #1475 ("compact toolbar labels") — eight days *before* the 8/27
screenshot behind this card. So the layout bug as written looks **already fixed**; what is left is
the design question Dave asked — four other ways to lay this part of the page out — plus the
honest fact that at ≤1160 px the toggle changes line, which is itself a layout decision nobody
ruled on.

Files: `d3-today.jpg` (1440, one row) · `d3-today-1280.jpg` · `d3-today-1180.jpg` (last one-row
width) · `d3-today-1160.jpg` (first wrapping width) · `d3-today-1120.jpg` (the pressure width used
for every option) · `d3-page.jpg` (top 320 px of the real page for context).

---

## The options

Each option has a 1440 shot (`d3-<x>.jpg`) and a 1120 pressure shot (`d3-<x>-1120.jpg`). At 1440
there is no pressure, so several options look identical to today there — the 1120 pair is where
they separate.

### A — toggle keeps both words, the filters give way (`d3-a.jpg`, `d3-a-1120.jpg`)
**What gives:** nothing wraps; the search box and the four selects shrink instead.
At 1440 it is **pixel-identical to today** (same 40 px band, same widths). At 1120 it holds one
40 px row: the selects shrink 140 → 127 px and the search input collapses to **102 px** (the
placeholder reads "Sea…"). Toggle stays 124 px, whole.
**Code:** `DashboardFilters.tsx` desktop row only — drop `md:flex-wrap`, give the search wrapper a
lower `min-w`, and let the `SelectTrigger`s shrink (`md:min-w-0`, `flex 0 1 140px` instead of a
hard `md:w-[140px]`). No change to `RoDashboardShell.tsx`.
**Caveat:** this is the direction the shipped code already takes, minus the wrap. Its cost is a
search box too narrow to read a typed RO number at ≤1200 px — which is why the wrap exists.

### B — two rows: search + toggle on top, filters + Clear underneath (`d3-b.jpg`, `d3-b-1120.jpg`)
**What gives:** vertical space, always. The block is **84 px at every width** (vs 40 today at
1440, 86 today at 1120). The search box grows to 413 px and every filter label is readable.
**Code:** split the `hidden md:flex` block in `DashboardFilters.tsx` into two rows. Because the
toolbar is permanently 44 px taller, `RoDashboardShell.tsx`'s `chromeOffset` must grow by the same
amount (admin passes `{ base: '13.5rem', md: '11rem' }`) or the table's bounded scroll region
runs off the bottom.
**Caveat:** vertical space is the scarce resource on this page (that is why the metrics glance
moved into the navbar) — B spends 44 px of table on every screen to fix a ≤1160 px problem.

### C — icon-only toggle, word as tooltip (`d3-c.jpg`, `d3-c-1120.jpg`)
**What gives:** the two words. Lucide columns + list glyphs, 44 px wide × 40 px tall hit boxes
(matching the row's 40 px controls), `title` + `aria-label` carrying "Pipeline" / "List".
Toggle shrinks 124 → **90 px**.
**Caveat — it does not solve the stated problem:** 34 px is not enough, so at 1120 the row
**still wraps** (90 px band). And the label only exists on hover, on a control whose two states
are not self-evident from a glyph. (Tests are safe: everything that touches the toggle targets it
by `data-testid` — `pipeline-dnd.spec.ts` — so no label pin breaks.)

### D — one "Filters · 4" button, selects in a popover (`d3-d.jpg`, `d3-d-open.jpg`, + 1120 pair)
**What gives:** the four dropdowns leave the row. The toolbar drops to search + sort + one
"Filters · 4" button + toggle + New RO — **one 40 px row at both widths captured (1440 and 1120)**,
with the widest clearance of any option. `d3-d-open.jpg` shows the panel open: the four real selects stacked with labels, Clear in
its footer (383 px tall panel).
**Code:** new small component (button + Radix Popover) in `DashboardFilters.tsx`; the count comes
free from the D2 `DashboardFilterActives` object that already drives the rings and Clear.
**Caveat:** the current values stop being visible — "Parts Pricing / Cam Drummond / PJ Macklin"
becomes "4". That is the exact failure ⛔ D2 was written to prevent ("a dropdown reading 'Derek
Jozwiak' looked identical to an untouched one"); a count badge is a weaker tell than the values.
A middle version — chips for the active filters, the popover for the inactive ones — was not
captured; say the word and I will shoot it.

### E — toggle moves to a page-title row (`d3-e.jpg`, `d3-e-1120.jpg`)
**What gives:** a new row above the toolbar carrying "Repair Orders" + the real active count
("13 active"), with the toggle right-aligned in it. The toolbar itself stays **one row at 1120**
(40 px), but the block totals 88 px.
**Code:** the toggle moves from `DashboardFilters.tsx` into `RoDashboardShell.tsx`'s title row —
which admin does **not** render today (`title` is advisor-only), so the row is new, and the same
`chromeOffset` adjustment as B applies.
**Caveat:** costs the same vertical row as B for a smaller gain, unless the toggle instead rides
the existing navbar metrics strip (not captured — the navbar is a shared component and that change
reaches every role's page).

### F — no standalone Clear; each active filter carries its own × (`d3-f.jpg`, `d3-f-1120.jpg`)
**What gives:** the "× Clear" button the card names as the thief (85 px). Every control whose
`data-active-filter="true"` gets an 18 px × inside it; "All Age" (inactive) gets none.
**One row at 1120** (40 px band), search input 128 px.
**Code:** `DashboardFilters.tsx` — drop `clearButton`, add the × to the ringed controls.
**Caveats:** (1) ⛔ **D2-3 (Dave, 2026-09-08) ruled the button stays "× Clear"** — F reverses that
ruling and needs a new one. (2) An × inside a Radix `SelectTrigger` must `stopPropagation` or the
click opens the menu instead of clearing; my override is display-only and does not prove that
interaction. (3) With four filters set, clearing all of them becomes four clicks.

---

## Things every shot shares (today's behaviour, not my overrides)

- The technician select reads **"Cam…"** — a 140 px select truncating "Cam Drummond". That is
  shipped behaviour and it shows in every option including today's.
- The advisor select wears a teal ring in the shots because it was the last control clicked
  (focus ring), not because it differs from the blue active-filter rings.
- The status select renders **blank** if the current filter combination returns zero ROs (the
  option unmounts from a list derived from the filtered set, so Radix has nothing to echo). Worth
  a look on its own — it is not part of this card, and every capture here deliberately uses a
  combination that keeps 9 rows.
