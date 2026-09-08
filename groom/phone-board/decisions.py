# id suffix, question, options [(letter, text, rec)], text_only
DEC = {
 "SA-20b": [
  ("Plain “Pending” at pricing time, or hide the delivery cell until the line is approved?", [("A","Pending — the Yes stays shown as the answer it is",True),("B","Hide the delivery cell until the line is approved",False)]),
 ],
 "Q": [
  ("Which variants go on the ballot — your three, plus which extras?", [("A","Your three only",False),("B","Your three + collapse the notes band",False),("C","Your three + all four extras — notes band, part on one row, one-line footer, per-user density",False)]),
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
  ("Ship the squashed Pipeline / List switch as a plain fix — no design decision?", [("A","Yes",True),("B","No — show me the fix first",False)]),
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
  ("Show “N price gaps” (blank or $0 part or hours — the RO band’s rule) or only blanks?", [("A","N price gaps — the RO band’s rule",False),("B","Only blanks",False)]),
  ("Hover lists the lines?", [("A","Yes",False),("B","No",False)]),
 ],
 "D1": [
  ("Label only — one change, no behavior?", [("A","Yes",True),("B","No",False)]),
  ("If the customer page carries the word anywhere, change it there too?", [("A","Yes — change it there too",False),("B","No — customer page untouched",False)]),
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
