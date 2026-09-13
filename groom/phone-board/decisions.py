# id suffix, question, options [(letter, text, rec)], text_only
# Every ballot carries a do-nothing / delete option and one off-pattern option (⛔ Dave 2026-09-11).
DEC = {
 # ----- MPI & Video -----
 "VC7": [
  ("How should the missing corners get onto the card?", [
    ("A","Add a tires example beside the brakes one in the writer’s rule — measured on the test set first",True),
    ("B","Move the related readings above the finding’s own notes, so the corners are read first — measure",False),
    ("C","Leave it — the tech can add the fronts on camera",False),
    ("D","Don’t ask the writer: the app appends the corners line itself under the card (LF 7/32″ · RF 7/32″), always there",False)]),
 ],
 "VC8": [
  ("A green good-news shot and the red axle:", [
    ("A","Green cards stay corner-blind — the red axle has its own red card in the same deck",True),
    ("B","Green cards carry siblings only when they are also green (“all four tires 7/32″”)",False),
    ("C","Full corners on green cards too, reds included",False),
    ("D","Take green shots out of the deck — the red card already carries the good corners",False)]),
 ],
 # ----- Parts page & queue -----
 "SO": [
  ("One customer sentence on both surfaces — which?", [
    ("A","The hint’s: “2 parts have no price — their lines will be quoted with those parts counted as $0.00.”",True),
    ("B","The dialog’s: “2 parts still need pricing. Those lines will be quoted to the customer with the unpriced parts counted as $0.00 — and the customer can approve them at that price.”",False),
    ("C","Leave both as they are",False),
    ("D","Drop the inline hint — the dialog is the gate, one warning is enough",False)]),
 ],
 # ----- RO page -----
 "BM": [
  ("Which fix?", [
    ("A","The bar wraps to two rows when it is narrow — the question on its own line, the pills wrap",True),
    ("B","Hide the Customer-link panel while the bar is up — the bar takes the full width, like the tech’s",False),
    ("C","Leave it — the buttons work; advisors rarely bulk-move at 1440 with the panel open",False),
    ("D","On the advisor’s desktop, open bulk move as the phone’s bottom sheet instead of a bar",False)]),
 ],
 "PH": [
  ("Before anything is drawn: how should this feel? Where would you look for it on the line, and what would you expect it to show?", []),
  ("Scope:", [
    ("A","Money changes only — price, quantity, labor hours and rate",True),
    ("B","Every recorded change — stock answer and note too",False),
    ("C","Not now — wait until an advisor asks who changed a price",False),
    ("D","No screen: put the changes in the RO’s internal notes as they happen, one note per change",False)]),
 ],
 # ----- Dashboards -----
 "D3": [
  ("Ship the fix as drawn — the switch keeps its full labels and the filter boxes give up the room instead?", [("A","Yes — ship it as drawn",True),("B","No — say what should give way instead, below",False),("C","Leave it — “Li” stays",False)]),
 ],
 "SA-7b": [
  ("Store one new piece of information on each RO so the two families can be told apart — build it as part of this?", [("A","Yes",True),("B","No — go back to “Needs customer OK” and accept it is wrong when only the store is waiting",False),("C","Drop the badge — the row colors and the LINES column already carry it",False)]),
  ("Wording per family — “Needs customer OK” / “Needs store OK”, the words the RO page’s band already uses?", [("A","Yes",True),("B","Other wording — say it below",False)]),
 ],
 "X": [
  ("Bring the count back as “price gaps” — the RO header’s rule (labor hours missing or 0, a part row blank or $0)? “Only blanks” can no longer count anything: since 8/27 every line carries a total.", [("A","Yes — “N price gaps”, the RO header’s rule",True),("B","No — drop the row; nothing is left for it to count",False)]),
  ("Hover lists the lines with a gap, and what the gap is?", [("A","Yes",True),("B","No — the count only",False)]),
 ],
 "D1": [
  ("Label only — one change, no behavior?", [("A","Yes",True),("B","No",False)]),
  ("If the customer page carries the word anywhere, change it there too? (Checked 9/8: it never does — the word is staff-only.)", [("A","Yes — change it there too",False),("B","No — customer page untouched",False)]),
 ],
 # ----- Store settings -----
 "T": [
  ("Store the rate only, or the whole agreed snapshot (rate, hours, parts)?", [("A","The rate only",False),("B","The whole snapshot",False),("C","Do nothing — keep the five special cases; they hold today",False)]),
  ("Old approved lines: work the rate back from the stored total, or leave them on the total?", [("A","Work it back",False),("B","Leave them on the total",False)]),
 ],
 # ----- Platform & tooling -----
 "EH": [
  ("The phantom rows already written — about two per pricing or decision save at McGrath since the recorder shipped:", [
    ("A","A one-time cleanup you run deletes them",True),
    ("B","Leave the rows; the statistics learn to skip an unchanged field with an empty after-text",False),
    ("C","Do nothing — the writer fix stops new ones; the old era stays inflated",False),
    ("D","Retire the edit statistics — if nobody reads them, there is nothing to fix",False)]),
 ],
 "Y3": [
  ("Take the eight recommendations as a block, or pull any one out?", [("A","All eight, as a block",True),("B","Pull one out — say which below",False),("C","Drop all eight",False)]),
 ],
 "Y2": [
  ("Take the three recommendations as a block, or pull any one out?", [("A","All three, as a block",False),("B","Pull one out — say which below",False),("C","Drop all three",False)]),
 ],
 "Y": [
  ("Take the seven recommendations as a block, or pull any one out?", [("A","All seven, as a block",False),("B","Pull one out — say which below",False),("C","Drop all seven",False)]),
 ],
 "Z": [
  ("Make the guard refuse?", [("A","Yes",True),("B","No",False)]),
  ("Also vendor the env-seeding script into the repo?", [("A","No — two copies drift",True),("B","Yes",False)]),
 ],
 "EX5": [
  ("Do it at all now?", [("A","Icebox — trigger: the current version’s end of life, or an advisory that reaches us",True),("B","Do it now",False)]),
  ("If yes later: two PRs — routes and types first under the current version, then the flip?", [("A","Two PRs",True),("B","One PR",False)]),
 ],
}

# Stage per card. "triage" = not yet groomed (Advance / Keep / Icebox). Anything not listed is "groomed" = ready to rule.
# 12 Sep: every new card came in groomed — the facts were complete and the frames cheap (real captures existed), so the
# advance-first round trip would only have cost Dave a day.
STAGE = {}
STAGE_NOTE = {}

# Rulings already SWEPT into BACKLOG.md (origin/main) — baked into the board so they read as ruled and filed.
# Add here at every sweep, after the doc PR lands and BEFORE deleting the store docs.
BAKED = {
 "D1-2": ("A", "phone board, 8 Sep · filed #1934 — the customer page never says “booked”, so nothing changes"),
 # 12 Sep evening taps, swept 13 Sep · filed #1996 · building in the 13 Sep overnight run
 "BG-1": ("A", "board, 12 Sep · filed #1996 — “Technicians can mark all remaining items green”, an on/off switch · queued"),
 "BG-2": ("A", "board, 12 Sep · filed #1996 — OFF + “all other items green”: nothing, the rest stay pending · queued"),
 "BG-3": ("A", "board, 12 Sep · filed #1996 — every bulk button goes · queued"),
 "BG-4": ("A", "board, 12 Sep · filed #1996 — one setting, every reader (video too) · queued"),
 "NG-1": ("A", "board, 12 Sep · filed #1996 — don’t / don’t / dont read as one word before matching · queued"),
 "NG-2": ("A", "board, 12 Sep · filed #1996 — the green off “No cracked belts” stands; pinned, no build"),
 "NG-3": ("A", "board, 12 Sep · filed #1996 — the “do not” governs the whole sentence · queued"),
 "VRC-1": ("B", "board, 12 Sep, his words ⟦Step 1: N matched items / Step 2: N unmatched items⟧ → chat 13 Sep ⟦N recognized items⟧ / ⟦N unrecognized items⟧ (“step 1” / “step 2” are not part of the headers) · filed #1996 · queued"),
}

# Items whose every decision is BAKED but which are NOT queued — Dave held them for a conversation.
HOLD = {}
