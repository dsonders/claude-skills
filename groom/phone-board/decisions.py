# id suffix, question, options [(letter, text, rec)], text_only
# Every ballot carries a do-nothing / delete option and one off-pattern option (⛔ Dave 2026-09-11).
DEC = {
 # ----- MPI & Video -----
 "NEG": [
  ("“Didn’t see any leaks” — what should the app do with the word “leaks”?", [
    ("A","The app can’t colour a row from a damage word the tech said inside a “no”.",True),
    ("B","Leave it — a damage word colours the row even inside a “no”.",False),
    ("C","A sentence with both a “no” and a damage word goes to the review sheet for the tech to decide.",False)]),
  ("Should the app read can’t, won’t, couldn’t, shouldn’t, wouldn’t, mustn’t, needn’t and cannot as a “no”?", [
    ("A","Yes — all eight read as a “no”, with the full dictation test set run before it ships.",True),
    ("B","Leave it — those eight words are not read as a “no”.",False),
    ("C","A sentence with one of those words goes to the review sheet for the tech to decide.",False)]),
  ("“It’s not green, it’s yellow” — should the app still file green?", [
    ("A","The app can’t file a colour the tech said inside a “no”.",True),
    ("B","Leave it — “it’s not green” can still file green.",False),
    ("C","A sentence that names a colour inside a “no” goes to the review sheet for the tech to decide.",False)]),
 ],
 "VC7": [
  ("How should the good readings from the other corners get onto the card?", [
    ("A","Show the writer an example with tires, beside the one it already has with brakes.",True),
    ("B","Hand the writer the other corners before the finding’s own notes, so it reads them first.",False),
    ("C","Leave it — the tech says the good fronts out loud on camera.",False),
    ("D","The app adds the other corners in its own line under the card, every time — the writer is not asked.",False)]),
 ],
 "VC8": [
  ("Should a good-news card mention the corners that failed?", [
    ("A","A good-news card shows only its own good readings; the failed corners have their own card.",True),
    ("B","A good-news card adds the other corners only when they are good too.",False),
    ("C","A good-news card shows every corner, the failed ones included.",False),
    ("D","Drop good-news shots from the video — the card about the failed corners already carries the good readings.",False)]),
 ],
 "BGO": [
  ("What should the tech see when a note only says “everything else is good” and bulk green is off?", [
    ("A","Leave it — the note reads as one that applied nothing.",True),
    ("B","The note reads like any other note.",False),
    ("C","The note reads like any other note, with one line under it: “Bulk green is off for this store”.",False)]),
 ],
 # ----- Parts page & queue -----
 "SO": [
  ("Which wording should both warnings use?", [
    ("A","“2 parts have no price — their lines will be quoted with those parts counted as $0.00.”",True),
    ("B","“2 parts still need pricing. Those lines will be quoted to the customer with the unpriced parts counted as $0.00 — and the customer can approve them at that price.”",False),
    ("C","Leave both as they are.",False),
    ("D","Drop the warning under the button — the dialog is the gate.",False)]),
 ],
 # ----- RO page -----
 "BM": [
  ("How should the bar fit?", [
    ("A","The bar wraps onto more rows when it is narrow, so the question gets its own line and every pill is reachable.",True),
    ("B","The customer link panel steps aside while the bar is up, so the bar gets the full width.",False),
    ("C","Leave it — the move still lands, and the advisor works around it.",False),
    ("D","On the desktop, move several lines in the phone’s bottom sheet instead of the bar.",False)]),
 ],
 "PH": [
  ("Before anything is drawn — how would you want this to feel, and where on the line would you look for it?", []),
  ("What should the list show?", [
    ("A","Price, quantity, labor hours and rate — money only.",True),
    ("B","Every change, the stock answer and notes included.",False),
    ("C","Not now — wait until an advisor actually asks who changed a price.",False),
    ("D","No new screen — each change lands in the RO’s internal notes as it happens.",False)]),
 ],
 # ----- Dashboards -----
 "D3": [
  ("Keep the switch whole and let the filter boxes give up the room instead?", [
    ("A","Yes — the switch keeps both words and the filter boxes shrink.",True),
    ("B","No — say below what should give way instead.",False),
    ("C","Leave it — “Li” stays.",False)]),
 ],
 "SA-7b": [
  ("Store a separate count for the customer and for the store, so the badge can say which?", [
    ("A","Yes — the badge names who is waiting.",True),
    ("B","No — go back to “Needs customer OK”, and accept it is wrong when only the store is waiting.",False),
    ("C","Drop the badge — the row colours and the LINES column already carry it.",False)]),
  ("Use the words the RO page already uses — “Needs customer OK” and “Needs store OK”?", [
    ("A","Yes",True),
    ("B","Other wording — say it below.",False)]),
 ],
 "X": [
  ("Bring the count back as “price gaps” — labor hours missing or zero, a part with no price or $0?", [
    ("A","Yes — the cell shows “N price gaps”.",True),
    ("B","No — drop the count; there is nothing left for the old rule to find.",False)]),
  ("Should hovering the cell list the lines and what each one is missing?", [
    ("A","Yes",True),
    ("B","No — the count only.",False)]),
 ],
 "D1": [
  ("Change the word everywhere the money row shows it?", [
    ("A","Yes — every money row reads “Total”.",True),
    ("B","No — keep “Total Booked”.",False)]),
  ("Change it on the customer page too, if it ever says the word?", [
    ("A","Yes — change it there too.",False),
    ("B","No — the customer page is untouched.",False)]),
 ],
 # ----- Store settings -----
 "T": [
  ("What should an approved line remember?", [
    ("A","The labor rate it was agreed at.",False),
    ("B","The rate, the hours and the parts it was agreed at.",False),
    ("C","Do nothing — keep the five separate “don’t re-figure this line” rules.",False)]),
  ("What happens to lines the customer already approved?", [
    ("A","Work each old line’s rate back from its stored total and hours.",False),
    ("B","Leave old lines on their stored total.",False)]),
 ],
 # ----- Platform & tooling -----
 "EH": [
  ("What happens to the false records already written?", [
    ("A","A one-time cleanup you run deletes them.",True),
    ("B","Leave them, and teach the statistics to skip a record where nothing actually changed.",False),
    ("C","Do nothing — the fix alone stops new ones.",False),
    ("D","Retire the edit statistics — if nobody reads them, there is nothing to fix.",False)]),
 ],
 "Y3": [
  ("Take the eight recommendations as a block, or pull any one out?", [("A","All eight, as a block",True),("B","Pull one out — say which below.",False),("C","Drop all eight.",False)]),
 ],
 "Y2": [
  ("Take the three recommendations as a block, or pull any one out?", [("A","All three, as a block",False),("B","Pull one out — say which below.",False),("C","Drop all three.",False)]),
 ],
 "Y": [
  ("Take the seven recommendations as a block, or pull any one out?", [("A","All seven, as a block",False),("B","Pull one out — say which below.",False),("C","Drop all seven.",False)]),
 ],
 "Z": [
  ("Should the guard refuse to take a workspace another session has claimed?", [
    ("A","Yes — a session that tries is stopped with a message.",True),
    ("B","No — the claim stays a convention.",False)]),
  ("Also keep a second copy of the setup script inside the project?", [
    ("A","No — two copies drift.",True),
    ("B","Yes",False)]),
 ],
 "EX5": [
  ("Do it now, or wait?", [
    ("A","Wait — pick it up when the current version reaches end of life, or an advisory reaches this app.",True),
    ("B","Do it now.",False)]),
  ("When it does happen — split it in two, or do it in one go?", [
    ("A","Two steps — the routes first under the current version, then the switch.",True),
    ("B","One step.",False)]),
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
