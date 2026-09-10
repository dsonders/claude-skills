# id suffix, question, options [(letter, text, rec)], text_only
DEC = {
 "SA-20b": [
  ("Stop recording a delivery state from the pricing-time answer? Nothing on any screen changes — the one thing that does is the advisor’s re-open warning below.", [("A","Yes — stop it; the re-open warning goes quiet",True),("B","Leave it as it is — the recorded state is invisible, and the warning still works",False),("C","Icebox",False)]),
 ],
 "Q": [
  ("Which variants go on the ballot — your three, plus which extras?", [("A","Your three only",False),("B","Your three + collapse the notes band",False),("C","Your three + the extras — notes band, part on one row, a per-user “Compact” setting",False),("D","Your combination — tighter padding, notes tile at today’s width with Story Notes / Complaint / Cause sharing the rest, eyebrow labels, the rail",True)]),
  ("Complaint / Cause: one line + hover, or keep two lines and shrink elsewhere?", [("A","One line + hover",False),("B","Keep two lines, shrink elsewhere",False)]),
  ("Is a sideways “Parts Needed” rail worth the legibility cost?", [("A","Yes",False),("B","No",False)]),
  ("Parts page only, or the advisor and tech cards too?", [("A","Parts page only",False),("B","Advisor and tech cards too",False)]),
  ("Target height for one line + two parts?", []),
 ],
 "P": [
  ("Locked view = the parts page’s row exactly, or the money ledger’s row with stock + note added?", [("A","The parts page’s row exactly — drawn above",True),("B","The ledger’s row, with stock + note added",False)]),
  ("Edit mode gets the Note cell and the Sum / Manual parts total too?", [("A","Yes",True),("B","No — pricing fields only",False)]),
  ("Admin gets the ⚠ unpriced flag and × delete per row?", [("A","Both",True),("B","The flag only",False),("C","Neither",False)]),
  ("If a parts user is mid-edit on the line — take over with the warning, or refuse?", [("A","Take over, with the warning",False),("B","Refuse until they finish",False)]),
  ("The card is 492 px wide. Keep today’s row, which already shows the note under the part with nothing off screen — or the parts page’s six-column row as ruled, which scrolls sideways?", [("A","Keep today’s row — revisits P-1",True),("B","Six-column row, with a note mark you hover",False),("C","Six-column row, with the note as a line under the part",False)]),
 ],
 "SA-6b": [
  ("Label it “Declined at close”, read from the RO’s own closed-without-a-response mark?", [("A","Yes — “Declined at close”",True),("B","No — keep “Declined by the customer”",False)]),
  ("Dashboards and money bands keep counting it as declined — only the banner names the reason?", [("A","Yes",True),("B","No — count it separately",False)]),
 ],
 "W": [
  ("Leave internal lines out of the warning entirely, or keep them with internal wording?", [("A","Leave internal lines out",False),("B","Keep them, with internal wording",False)]),
  ("Same for warranty and recall lines (the customer sees them at $0)?", [("A","Yes — same treatment",False),("B","No — warranty and recall stay in",False)]),
 ],
 "S": [
  ("Is the rule “no tech hour edits after the estimate is sent”, or “only in these stages”?", [("A","After the estimate is sent — one-way",False),("B","Only in these stages",False)]),
  ("If it is estimate-based: does un-parking legitimately re-open hours for a real re-diagnosis — and who re-sends?", [("A","No — hours stay locked after the estimate",False),("B","Yes — un-parking re-opens them; the advisor re-sends",False)]),
  ("Same rule for the advisor / admin ledger, which has no stage lock today?", [("A","Yes",False),("B","No",False)]),
 ],
 "D3": [
  ("Ship the fix as drawn — the switch keeps its full labels and the filter boxes give up the room instead?", [("A","Yes — ship it as drawn",True),("B","No — say what should give way instead, below",False)]),
 ],
 "SA-7b": [
  ("Store one new piece of information on each RO so the two families can be told apart — build it as part of this?", [("A","Yes",True),("B","No — go back to “Needs customer OK” and accept it is wrong when only the store is waiting",False)]),
  ("Wording per family — “Needs customer OK” / “Needs store OK”, the words the RO page’s band already uses?", [("A","Yes",True),("B","Other wording — say it below",False)]),
 ],
 "D2": [
  ("Ring, tinted fill, or both — and which color? Name the color below.", [("A","Ring",False),("B","Tinted fill",False),("C","Both",False)]),
  ("Does a default choice (“Newest”, “All statuses”) count as active?", [("A","No",True),("B","Yes",False)]),
  ("Count on Clear (“Clear 2”)?", [("A","Yes",False),("B","No",False)]),
 ],
 "X": [
  ("Bring the count back as “price gaps” — the RO header’s rule (labor hours missing or 0, a part row blank or $0)? “Only blanks” can no longer count anything: since 8/27 every line carries a total.", [("A","Yes — “N price gaps”, the RO header’s rule",True),("B","No — drop the row; nothing is left for it to count",False)]),
  ("Hover lists the lines with a gap, and what the gap is?", [("A","Yes",True),("B","No — the count only",False)]),
 ],
 "D1": [
  ("Label only — one change, no behavior?", [("A","Yes",True),("B","No",False)]),
  ("If the customer page carries the word anywhere, change it there too? (Checked 9/8: it never does — the word is staff-only.)", [("A","Yes — change it there too",False),("B","No — customer page untouched",False)]),
 ],
 "U": [
  ("Inline under the line, or a banner at the top of the page?", [("A","Inline under the line",True),("B","A banner at the top",False)]),
  ("Show the old price, or only the amount it came down?", [("A","The amount only",True),("B","Old price and new price",False)]),
  ("Every visit, or once?", [("A","Once",False),("B","Every visit",False)]),
 ],
 "T": [
  ("Store the rate only, or the whole agreed snapshot (rate, hours, parts)?", [("A","The rate only",False),("B","The whole snapshot",False)]),
  ("Old approved lines: work the rate back from the stored total, or leave them on the total?", [("A","Work it back",False),("B","Leave them on the total",False)]),
 ],
 "Y2": [
  ("Take the three recommendations as a block, or pull any one out?", [("A","All three, as a block",False),("B","Pull one out — say which below",False)]),
 ],
 "Y": [
  ("Take the seven recommendations as a block, or pull any one out?", [("A","All seven, as a block",False),("B","Pull one out — say which below",False)]),
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

# Stage per card. "triage" = not yet groomed: the decision needed NOW is whether to groom it at all
# (Advance to grooming / Keep in backlog / Send to Icebox); its questions are what grooming would settle and
# may be ruled early. Anything not listed is "groomed" = ready to rule. STAGE_NOTE says why it is waiting.
STAGE = {
 # Q and SA-20b were advanced by Dave from the phone on 2026-09-08 (rulings/Q-stage, rulings/SA-20b-stage) → groomed here.
}
STAGE_NOTE = {
 "Q": "Mockups on a real RO come next if this advances — the three shapes above are silhouettes, not the app.",
 "SA-20b": "The table above describes stored state, not a screen — the parts pricing grid has no delivery pill. A real frame comes with grooming.",
}

# Rulings already SWEPT into BACKLOG.md (origin/main) — baked into the board so they read as ruled and filed.
# Add here at every sweep, after the doc PR lands and BEFORE deleting the store docs.
BAKED = {
 "D2-1": ("A", "phone board, 8 Sep · filed #1934"),
 "D2-2": ("A", "phone board, 8 Sep · filed #1934"),
 "D2-3": ("B", "phone board, 8 Sep · filed #1934"),
 "U-1":  ("A", "phone board, 8 Sep · filed #1934"),
 "U-2":  ("A", "phone board, 8 Sep · filed #1934"),
 "U-3":  ("B", "phone board, 8 Sep · filed #1934"),
 "P-3":  ("C", "phone board, 8 Sep · filed #1934"),
 "D1-2": ("A", "phone board, 8 Sep · filed #1934 — the customer page never says “booked”, so nothing changes"),
 "P-1":  ("A", "phone board, 8 Sep · filed 9 Sep — see P-5: the card is 492 px wide"),
 "P-2":  ("A", "phone board, 8 Sep · filed 9 Sep"),
 "P-4":  ("A", "phone board, 8 Sep · filed 9 Sep"),
 "SA-6b-1": ("A", "phone board, 8 Sep · filed 9 Sep"),
 "SA-6b-2": ("A", "phone board, 8 Sep · filed 9 Sep"),
 "W-1":  ("B", "phone board, 8 Sep · filed 9 Sep — with your dialog copy"),
 "W-2":  ("A", "phone board, 8 Sep · filed 9 Sep"),
}
