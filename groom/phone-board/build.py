import os, json, html, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import sil
from decisions import DEC, STAGE, STAGE_NOTE, BAKED, HOLD
import option_frames as OF
import bg_frames as BG
import os as _os
O=os.path.dirname(os.path.abspath(__file__))
cards=json.load(open(O+'/cards.json'))
board_css=open(O+'/board.css').read()

SECTION_ORDER=["MPI & Video","Parts page & queue","RO page — advisor, admin, tech","Dashboards","Customer page","Store settings — labor rates & money","Platform & tooling"]

# ---- Flip / walkthrough frames per card (Today | Proposed over one frame) ----
def frames_for(key):
    if key=="BG":
        return dict(kind="flip", caption="The technician, at the bottom of an inspection step — the store has the setting OFF.",
            today=BG.tech_step(False), proposed=BG.tech_step(True))
    return dict(kind="none")

# Per-decision clarifiers. CONTEXT[dec_id] = one situation paragraph. OPT_VIS[dec_id][letter] = {'frame': html, 'why': implication}.
# GALLERY[dec_id] = list of (label, html, note) shown above the options.
CONTEXT, OPT_VIS, GALLERY = {}, {}, {}
GALLERY_WIDE, GALLERY_FULL, OPTS_FULL = set(), set(), set()

import base64 as _b64
REAL = _os.path.join(O, 'real')
import struct as _struct
def _jpeg_size(path):
    with open(path,'rb') as f:
        data = f.read()
    i = 2
    while i < len(data):
        if data[i] != 0xFF: i += 1; continue
        marker = data[i+1]
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = _struct.unpack('>HH', data[i+5:i+9]); return w, h
        seg = _struct.unpack('>H', data[i+2:i+4])[0]; i += 2 + seg
    return None, None
def real_img(name, alt, dpr=2):
    """A real screenshot at its real CSS size (captures are 2× device pixels unless dpr says otherwise)."""
    path = f'{REAL}/{name}.jpg'
    b = _b64.b64encode(open(path,'rb').read()).decode()
    w, h = _jpeg_size(path)
    css_w = f'width:{w//dpr}px;aspect-ratio:{w}/{h};' if w else 'width:100%;'
    # aspect-ratio reserves the box before the image decodes, so a re-render never shifts the page under a tap
    return f'<img src="data:image/jpeg;base64,{b}" alt="{alt}" width="{w}" height="{h}" style="display:block;{css_w}max-width:100%;height:auto;">'
def has_real(name): return _os.path.exists(f'{REAL}/{name}.jpg')

# ================= MPI & Video =================
# ----- BG: the bulk-green setting -----
CONTEXT['BG-1'] = 'The admin Settings page, drawn in the pattern of the card above it (“MPI → Labor Line Promotion”). The switch state carries the rule; there is no helper sentence beyond the one that names it. An unset store reads ON.'
OPT_VIS['BG-1'] = {
 'A': {'frame': BG.settings_card('a'), 'why': 'Reads as a permission — what technicians may do — and the switch is the rule.'},
 'B': {'frame': BG.settings_card('b'), 'why': 'Names the button the tech knows; “Allowed” as the helper.'},
 'C': {'frame': BG.settings_card('c'), 'why': 'Mirrors the promotion card exactly, a menu instead of a switch — two words to read.'},
 'D': {'why': 'Type the label and the switch words below; the card gets redrawn.'},
 'E': {'why': 'Nothing changes for anyone; the request from the admins is closed as “no”.'},
 'F': {'why': 'Every tech everywhere marks each item; no store can turn it back on.'},
}
CONTEXT['BG-2'] = 'Checked in the code: today the app deliberately strips a recognized “all other items green” phrase out of the review list so it can never become a review row. A stops that sweep and the phrase disappears with it — the cheap build. B and C need a new “recognized but refused” state so the sentence can be shown. The row would carry the app’s existing label for a clause that did not apply: “Part of a note that matched something else”.'
OPT_VIS['BG-2'] = {
 'A': {'frame': BG.review_sheet('silent'), 'why': 'The tech sees two findings and 22 pending items; nothing tells him his last sentence did nothing.'},
 'B': {'frame': BG.review_sheet('parked'), 'why': 'His words never vanish — the sentence sits on the review card and the pending rows are the state. Costs the new state.'},
 'C': {'frame': BG.review_sheet('reason'), 'why': 'Same as B with one line of explanation; the app’s own rule is no helper lines unless they name a problem — this one does.'},
}
OPTS_FULL.add('BG-1'); OPTS_FULL.add('BG-2')
GALLERY['BG-3'] = [('The desktop entry — today, and with the setting OFF', BG.desktop_entry_button(False) + BG.desktop_entry_button(True), '')]
OPT_VIS['BG-3'] = {'A': {'why': 'Both labels of the one button go — “All Green” and “Mark the Rest Green” are the same control in two states.'}, 'B': {'why': 'A tech who has touched one item can still green the rest in one tap; the setting only removes the untouched-inspection shortcut.'}}
OPT_VIS['BG-4'] = {'A': {'why': 'A video whose narration ends “everything else is good” greens nothing at an OFF store; the same rows stay pending.'}, 'B': {'why': 'Video keeps the shortcut; only dictation and the buttons obey the switch — two rules for one phrase.'}}

# ----- NG: three negations -----
CONTEXT['NG-1'] = 'Measured on the app as it runs today: “All the belts do not look good” is caught; “All the belts don’t look good” — straight or curly apostrophe — is not, and the belts go green.'
OPT_VIS['NG-1'] = {'A': {'why': 'The three spellings become one word to every rule that reads a technician’s words; the full dictation test set runs before it ships.'}, 'B': {'why': 'A tech who says “don’t” keeps getting an all-clear he did not give.'}, 'C': {'why': 'Safer on paper, but it would also refuse honest all-clears such as “no leaks, everything else is fine”.'}}
CONTEXT['NG-2'] = 'The deterministic rules refuse every collective “no” except “no leaks”; the AI reader, reading the same sentence, greens Drive Belts 3 times in 3 for “No cracked belts.” It has done so since before the 8 Sep run.'
OPT_VIS['NG-2'] = {'A': {'why': 'A specific item named with a specific defect that is absent is a finding; the tech gets the green he meant.'}, 'B': {'why': 'Consistent with the collective rule; one more tap for the tech on every “no …” sentence.'}, 'C': {'why': 'The green stands and the tech can see where it came from — one new mark on the row.'}}
CONTEXT['NG-3'] = 'From the 9/11 review of the “I recommend …” floor: the sentence is split at “or”, so the “do not” before “recommend” never reaches “suggest”, and the row is held back from green as if the tech had recommended work.'
OPT_VIS['NG-3'] = {'A': {'why': 'One word dropped from the split list; the row greens as he meant.'}, 'B': {'why': 'The row stays held; the sentence is written into the test set as accepted so it never surprises anyone again.'}, 'C': {'why': 'The tech decides on the review sheet; more taps, no guessing.'}}

# ----- VRC: the video review sheet as built -----
GALLERY['VRC-1'] = [
 ('Step 1 — the header IS the step: “N MPI Items To Review”, no total above it', real_img('vr-step1','Step 1'), ''),
 ('Step 2 — unmatched items; “Apply Selected” stays even with rows unticked', real_img('vr-step2','Step 2'), ''),
 ('“Dismiss All” asks once, then works row by row and stops at the first refusal', real_img('vr-dismiss','Dismiss all'), ''),
]
GALLERY_FULL.add('VRC-1')
CONTEXT['VRC-1'] = 'Three calls the 8 Sep build made on your copy (card VR) that you have not seen:\n1 · A total above a per-step header was the busyness you objected to, so the step header is the top header.\n2 · “Apply all results” over a half-ticked list would be a false claim, so the button reads “Apply Selected”.\n3 · There is no bulk dismiss on the server, so “Dismiss All” runs row by row and any row it could not dismiss stays on the sheet asking.'
OPT_VIS['VRC-1'] = {'A': {'why': 'Nothing to build.'}, 'B': {'why': 'Say which of the three below; it becomes its own small build.'}, 'C': {'why': 'A second number above the step header — the shape you called busy on 7 Sep.'}}

# ----- NEG: three more places a spoken "no" is ignored (non-UX: no frames) -----
CONTEXT['NEG-1'] = ('The damage words the app listens for — crack, leak, grinding — colour a row on their own, without checking whether the tech said them inside a “no”.')
OPT_VIS['NEG-1'] = {
 'A': {'why': 'A tech who says “didn’t see any leaks” stops getting a red row — and a defect he phrased oddly could be missed.'},
 'B': {'why': 'A stated defect is never lost, and “didn’t see any leaks” keeps turning the row red.'},
 'C': {'why': 'Nothing is decided for him — one more row on the review sheet every time he says it.'},
}
CONTEXT['NEG-2'] = ('The words the app already reads as a “no” do not include these eight. Widening the list touches three features that already ship, so the full dictation test set runs first.')
OPT_VIS['NEG-2'] = {
 'A': {'why': 'A tech who says “couldn’t find any leaks” gets the reading he meant.'},
 'B': {'why': 'A tech who says “couldn’t find any leaks” keeps getting a reading he did not give.'},
 'C': {'why': 'Nothing is decided for him — the sentence lands on the review sheet instead.'},
}
CONTEXT['NEG-3'] = ('When a tech names a colour the app files it, with nothing checking whether he said it inside a '
 '“no” — so “it’s not green, it’s yellow” can file green.')
OPT_VIS['NEG-3'] = {
 'A': {'why': 'The tech gets the yellow he said, not the green he ruled out.'},
 'B': {'why': 'A tech correcting himself mid-sentence keeps getting the colour he just ruled out.'},
 'C': {'why': 'The tech picks the colour himself, one row at a time.'},
}

# ----- VC7 / VC8 -----
CONTEXT['VC7-1'] = ('The app hands the good corner readings to the writer every time. On the test set the writer left them '
 'off the rear-tires card in every run, and off one rear-brakes card in three.')
OPT_VIS['VC7-1'] = {
 'A': {'why': 'The customer hears the good fronts on the same card that carries the bad rears.'},
 'B': {'why': 'The writer reads the other corners first — every other kind of card changes too, so the test set decides.'},
 'C': {'why': 'The tech remembers the fronts on camera, or the customer never hears them.'},
 'D': {'why': 'The corners are always there, in the app’s own line under the writer’s sentences.'},
}
CONTEXT['VC8-1'] = ('A good-news shot is one the tech chooses to add, and the app prints “Looks good — reassure the '
 'customer” under it. Handing it the failed corners means that card could read “rear tires 2/32″” under its '
 'own good-news line.')
OPT_VIS['VC8-1'] = {
 'A': {'why': 'The good news stays good news; the customer hears the failed corners on their own card.'},
 'B': {'why': '“All four tires 7/32″” when it is true, and nothing when a corner failed.'},
 'C': {'why': 'The customer hears the worn rears on the card that was meant to reassure them.'},
 'D': {'why': 'The tech loses the good-news shot he chose to add.'},
}

CONTEXT['VC8-2'] = ('A good-news card exists only because the item was green on the MPI and the tech added the shot from the green section of the '
 'shot picker; the app ends it with “Looks good — reassure the customer”. Under your VC8 rule a “Front Tires” card now also carries the rears at 2/32″.')
OPT_VIS['VC8-2'] = {
 'A': {'why': 'The card never reassures over a failed reading; the failed corner’s own red card still carries the reassurance for nothing.'},
 'B': {'why': '“Rear tires 2/32″” and “Looks good” on one card.'},
 'C': {'why': 'The tech’s chosen good-news shot loses the one line that said so.'},
 'D': {'why': 'Back to VC8-1 option A — the good news stays good news.'},
}
# ----- BGO: a standalone "everything else is good" note at a store with bulk green off -----
CONTEXT['BGO-1'] = ('With bulk green off, a note that only says “everything else is good” finds nothing to apply, so '
 'the app gives it the look it gives any note that applied nothing. Nothing about it reaches the review sheet.')
GALLERY['BGO-1'] = [('Today — the tech’s notepad after a note that only says “everything else is good”', BG.notepad_standalone('today'), '')]
OPT_VIS['BGO-1'] = {
 'A': {'why': 'The tech sees his sentence did nothing, and the pending items are the rest of the answer.'},
 'B': {'frame': BG.notepad_standalone('plain', step=False), 'why': 'Nothing tells the tech his sentence did nothing.'},
 'C': {'frame': BG.notepad_standalone('reason', step=False), 'why': 'The tech reads why in one line — the app’s own rule is no helper lines unless they name a problem, and this one does.'},
}

# ================= Parts page & queue =================
TRI_SM = OF.TRI.replace('width="20" height="20"', 'width="14" height="14"')
def hint_frame(sentence):
    return OF.app(f'<div style="display:flex;flex-direction:column;gap:6px;"><div style="min-height:44px;border-radius:6px;background:#2563eb;color:#fff;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:600;">Send to advisor</div><div style="font-size:12.5px;line-height:1.4;color:#92400e;display:flex;gap:6px;align-items:flex-start;"><span style="flex:none;">{TRI_SM}</span><span>{sentence}</span></div></div>')
SO_A = '2 parts have no price — their lines will be quoted with those parts counted as $0.00.'
SO_B = '2 parts still need pricing. Those lines will be quoted to the customer with the unpriced parts counted as $0.00 — and the customer can approve them at that price.'
GALLERY['SO-1'] = [('Today — under the button', hint_frame(SO_A), ''), ('Today — in the dialog', OF.send_gate_today(), '')]
CONTEXT['SO-1'] = ('The internal and warranty warnings already say the same thing in both places. Only the customer pay one '
 'has two wordings.')
OPT_VIS['SO-1'] = {
 'A': {'frame': OF.dialog('Some parts aren’t priced yet', SO_A, 'Send anyway', 'Cancel', icon=OF.TRI), 'why': 'The parts user reads the same short sentence in both places.'},
 'B': {'frame': hint_frame(SO_B), 'why': 'The longer sentence in both places — it names the customer and that they can approve at $0.00.'},
 'C': {'why': 'Two wordings for one fact, as today.'},
 'D': {'frame': OF.app('<div style="min-height:44px;border-radius:6px;background:#2563eb;color:#fff;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:600;">Send to advisor</div>'), 'why': 'One warning, in the dialog that can stop the send.'},
}

# ================= RO page =================
# ----- BM: moving several lines at once on the advisor's desktop (real captures) -----
BMH = json.load(open(REAL+'/bm-heights.json')) if _os.path.exists(REAL+'/bm-heights.json') else None
def _bm(name, alt, fallback=None):
    if has_real(name): return real_img(name, alt)
    return real_img(fallback, alt, dpr=1) if fallback and has_real(fallback) else None
def _h(v, k):
    try: return f"{BMH[v][k]} px tall" if BMH and BMH.get(v,{}).get(k) is not None else ''
    except Exception: return ''
gal = []
t_sel = _bm('bm-today-select','Today, select', 'bm-fallback-select'); t_ask = _bm('bm-today-ask','Today, ask', 'bm-fallback-ask')
if t_sel: gal.append(('Today — choosing the pay type: Internal and Cancel sit under the customer link panel, so a click on Internal lands on the panel', t_sel, _h('today','select')))
if t_ask: gal.append(('Today — the question about rewriting the stories: the two buttons take the whole row and the question itself has no room left', t_ask, _h('today','ask')))
GALLERY['BM-1'] = gal
GALLERY_FULL.add('BM-1'); OPTS_FULL.add('BM-1')
CONTEXT['BM-1'] = ('Real screens of the advisor’s RO page with three lines selected. The tech’s page has no customer '
 'link panel, so the same bar has the full width there and reads fine.')
w_sel = _bm('bm-wrap-select','Wrapped, select'); w_ask = _bm('bm-wrap-ask','Wrapped, ask'); n_sel = _bm('bm-nopanel-select','No panel, select'); n_ask = _bm('bm-nopanel-ask','No panel, ask')
def _join(*fr): return ''.join(f'<div style="margin-bottom:8px;">{f}</div>' for f in fr if f)
OPT_VIS['BM-1'] = {
 'A': {'frame': (_join(w_sel, w_ask) or None), 'why': 'The advisor sees the question and reaches every pill; measured, the bar grows from 62 px to 170 px while he picks the pay type, and the tech’s bar is untouched.'},
 'B': {'frame': (_join(n_sel, n_ask) or None), 'why': 'The panel steps aside for the seconds the bar is up; the right half of the page is empty meanwhile.'},
 'C': {'why': 'The advisor never sees the question and cannot pick Internal on this screen.'},
 'D': {'why': 'One shape on both devices — but a sheet over the whole page for a three-line move is heavy.'},
}

# ----- PH: who changed a price (design-heavy -> his raw take first) -----
GALLERY['PH-1'] = [('Where it would live — the Parts & Labor card today', real_img('pbw-locked','Parts and Labor card today'), '')]
GALLERY_FULL.add('PH-1')
CONTEXT['PH-1'] = ('Already recorded for every change: what changed (part price, quantity, stock answer, note, labor hours, '
 'labor rate), the value before and after, who made it and when. None of it reaches the customer’s page.')
OPT_VIS['PH-2'] = {
 'A': {'why': 'The advisor gets the answer to “who changed this price” and nothing else.'},
 'B': {'why': 'A longer list — a stock answer or a note edit reads beside a price change.'},
 'C': {'why': 'The record keeps building; the screen waits for a real ask.'},
 'D': {'why': 'Every price edit becomes a note in the thread, and a ten-part line makes ten.'},
}
# ----- PH-3 / PH-4: real screens, advisor @1440, TD1 fixture RO 6672 (closed after) — every datum a recorded change -----
CONTEXT['PH-3'] = ('Real screens of the advisor’s RO page. A fixture RO with two lines — the second the worst shape, six parts each priced then '
 're-priced — made 37 recorded changes and 2 real notes; every name, time and figure on these frames was written by the app’s own recorder. '
 'Your note: ⟦I think we can record these events in “internal notes” but I need to see some mockups before we build. It might get too noisy in there '
 'with events from all lines flowing in. We should also mock up a couple options that either live on the line tab, or a centralized log that clearly '
 'separates actions on different lines.⟧ Not recorded today, so never shown: the cause / correction text, and what a change did to the line total.')
GALLERY['PH-3'] = [('Today — Internal notes in the header dock, 2 notes', real_img('ph-today-notes-open','Internal notes today'), '303 px tall'),
                   ('Today — the Parts & Labor card', real_img('ph-today-parts-card','Parts and Labor card today'), '')]
GALLERY_FULL.add('PH-3'); OPTS_FULL.add('PH-3')
OPT_VIS['PH-3'] = {
 'A': {'frame': _join(real_img('ph-a-collapsed','A collapsed bar'), real_img('ph-a-thread-full','A every change in the thread')), 'why': 'The thread grows from 303 px to 2 125 px; 39 rows, 2 of them things a person wrote — the advisor’s “customer is waiting in the lounge” sits under 22 price rows, and the collapsed bar’s preview stops being the last thing a human said.'},
 'B': {'frame': _join(real_img('ph-a2-thread-collapsed','B folded'), real_img('ph-a2-thread-group-open','B one group open')), 'why': '936 px closed, 1 301 px with the 18-change group open; both human notes stay in the top third. Two kinds of row to build, and the fold is a rule of thumb.'},
 'C': {'frame': _join(real_img('ph-b-card-link','C the link'), real_img('ph-b-line2-open','C line 2 open')), 'why': 'Who changed this price, where the price is; Internal notes stay human. The worst line’s panel runs 1 182 px, so it scrolls inside a cap. Nothing about the RO as a whole.'},
 'D': {'frame': real_img('ph-c-open','D one RO log'), 'why': 'One place for a 2-line RO and a 9-line RO, line headers keep it readable, the RO-level changes have a home; 1 998 px for 37 changes, so it scrolls inside a cap.'},
 'E': {'why': 'The record keeps building; nobody sees it.'},
}
CONTEXT['PH-4'] = 'Desktop only — a phone has no hover. Shows the most recent change of that one figure; not a substitute for the list.'
OPT_VIS['PH-4'] = {
 'A': {'frame': real_img('ph-d-hover','Hover on a price'), 'why': 'The most common question answered without opening anything; 34 px.'},
 'B': {'why': 'One less thing on the card.'},
}

# ================= Dashboards =================
GALLERY['D3-1'] = [('Today — filters on', OF.toolbar(False), ''), ('Proposed', OF.toolbar(True), '')]
CONTEXT['D3-1'] = ('The desktop admin dashboard with all four filters on. The filter boxes already show “…” when '
 'they run out of room; the switch does not.')
OPT_VIS['D3-1'] = {
 'A': {'why': 'The admin reads “List” on every filtered view.'},
 'C': {'why': 'The switch keeps clipping whenever a filter is on.'},
}
CONTEXT['SA-7b-1'] = ('Your question — ⟦“a part waiting on the store”⟧ is a part the parts user adds to '
 'an internal line the advisor had already approved, which withdraws that approval until the advisor approves the part on the '
 'RO page. The dashboard counts those together with parts waiting on a customer, so the badge can only say “Needs '
 'approval”.')
GALLERY['SA-7b-1'] = [('The RO page today — an internal line waiting on the store', OF.ledger_store_ok(), ''), ('Today — the dashboard badge', OF.dash_badge(['Needs approval']), '')]
OPT_VIS['SA-7b-1'] = {
 'A': {'frame': OF.dash_badge(['Needs customer OK','Needs store OK']), 'why': 'The advisor reads who is waiting straight off the dashboard — one badge each when both apply.'},
 'B': {'frame': OF.dash_badge(['Needs customer OK']), 'why': 'One count, as today, labelled “Needs customer OK” — wrong whenever only the store is waiting.'},
 'C': {'frame': OF.dash_badge([]), 'why': 'No badge; the advisor scans the row colour and the LINES column instead.'},
}
OPT_VIS['SA-7b-2'] = {
 'A': {'why': 'The dashboard says what the RO page already says about the same part.'},
}
GALLERY['X-1'] = [('Today', OF.booked(), '')]
CONTEXT['X-1'] = ('The cell still carries its old count, but it looks for lines with no total — and every line has one now, '
 'so it is always zero.')
OPT_VIS['X-1'] = {
 'A': {'frame': OF.booked('+2 price gaps'), 'why': 'The admin sees on the dashboard what the RO page already shows.'},
 'B': {'why': 'The dashboard keeps showing no gaps while the RO page and the parts page show them.'},
}
OPT_VIS['X-2'] = {
 'A': {'frame': OF.booked_hover(True), 'why': 'The admin sees which lines are missing a price without opening the RO.'},
 'B': {'frame': OF.booked_hover(False), 'why': 'The count alone; the admin opens the RO to see which lines.'},
}
OPT_VIS['D1-1'] = {
 'A': {'frame': OF.money_row('Total'), 'why': 'Every money row reads “Total”; the number and its colour never move.'},
 'B': {'frame': OF.money_row('Total Booked'), 'why': 'Every money row keeps reading “Total Booked”.'},
}
CONTEXT['D1-2'] = ('The customer’s page never uses the word “booked” — it is staff-only, so this changes '
 'nothing either way.')

# ================= Store settings =================
OPT_VIS['T-1'] = {
 'A': {'why': 'A later rate change leaves an approved line alone; hours and parts keep re-figuring as they do today.'},
 'B': {'why': 'The line remembers what was agreed, so any later edit reads as a change from it — more to store, less to reason about.'},
 'C': {'why': 'The next new money path has to remember the rule too, as the last one did not.'},
}
OPT_VIS['T-2'] = {
 'A': {'why': 'A one-time cleanup you run gives every approved line a rate; a line with no hours cannot be worked back and stays on its total.'},
 'B': {'why': 'Old lines keep the special case until they close; only lines approved after the build carry a rate.'},
}

# ================= Platform & tooling =================
CONTEXT['EH-1'] = ('The fix ships either way: a save that carries the story through unchanged stops being recorded as an edit. '
 'This decides only the records already written — about two per pricing or decision save at McGrath.')
OPT_VIS['EH-1'] = {
 'A': {'why': 'The statistics read true for the whole period; one cleanup, run once.'},
 'B': {'why': 'The records stay, and every reader has to know to skip them.'},
 'C': {'why': 'Everything recorded before the fix stays counted as an advisor rewrite.'},
 'D': {'why': 'Nothing to clean, and one less thing to keep — if nobody reads the numbers.'},
}
CONTEXT['Y3-1'] = ('The eight, each with the recommendation:\n'
 '1 · An automatic re-grade that runs a second and a half after a story edit, which nothing on the page can reach — delete it; the Re-Grade button is the live one. '
 '\n2 · Typing in a line’s Cause saves to the RO once per keystroke — 94 saves for 93 characters — so fix it to save once after you stop typing. '
 '\n3 · Three permission checks are missing on the server: the labor-rate sweep, the fields that ride an RO close, and Re-open — fix as defects in one reviewed change. '
 '\n4 · Two money paths decide whether a store approval is withdrawn from a setting read before the write — read it inside the write, and refuse the write if the store cannot be read. '
 '\n5 · A cleanup script can leave a stale “declined at close” mark — clear it the next time the script is touched. '
 '\n6 · Two older checks keep their own copy of a shared reader — move them onto the shared one when no build is in flight. '
 '\n7 · The store-scoping check misses one shape it should catch — teach it that shape, with one test that must catch it and one that must pass. '
 '\n8 · Pin the version of the review bot, and comment on any change whose squash deletes test files — comment, not block.')
OPT_VIS['Y3-1'] = {
 'A': {'why': 'Eight small changes in the next run; the permission one gets the extra review.'},
 'B': {'why': 'Name the number(s) to hold below; the rest ship.'},
 'C': {'why': 'Nothing ships — the keystroke storm and the three permission gaps stay.'},
}
OPT_VIS['Y2-1'] = {
 'A': {'why': 'The three recommendations in the table ship as one small change.'},
 'B': {'why': 'Name the one to hold below; the other two ship.'},
 'C': {'why': 'Nothing ships.'},
}
OPT_VIS['Y-1'] = {
 'A': {'why': 'The seven recommendations in the table ship as one small change.'},
 'B': {'why': 'Name the one(s) to hold below; the rest ship.'},
 'C': {'why': 'Nothing ships.'},
}
OPT_VIS['Z-1'] = {
 'A': {'why': 'A session that tries to take a claimed workspace is stopped, instead of wiping the other’s work.'},
 'B': {'why': 'A session that ignores the claim can still wipe another’s work.'},
}
OPT_VIS['Z-2'] = {
 'A': {'why': 'One copy of the setup script; nothing to keep in sync.'},
 'B': {'why': 'A second copy inside the project; every change has to be made twice or the two drift.'},
}
OPT_VIS['EX5-1'] = {
 'A': {'why': 'Nothing changes now; the move is picked up when the current version reaches end of life or an advisory reaches this app.'},
 'B': {'why': 'A medium build now, with a live pass on every request path before it ships.'},
}
OPT_VIS['EX5-2'] = {
 'A': {'why': 'The first step is reviewable on its own, and the switch that follows is small.'},
 'B': {'why': 'One large change — review rounds scale with size, and a live problem is harder to pin to a cause.'},
}

TRIAGE_MOCK = {}
data_cards=[]
for c in cards:
    decs=[]
    for i,(q,opts) in enumerate(DEC[c['key']],1):
        did=f"{c['key']}-{i}"
        ov=OPT_VIS.get(did,{})
        bk = BAKED.get(did)
        decs.append(dict(id=did, n=i, q=q, options=[dict(l=l,t=t,rec=r, frame=ov.get(l,{}).get('frame'), why=ov.get(l,{}).get('why')) for l,t,r in opts], text=(len(opts)==0), context=CONTEXT.get(did), gallery=[dict(label=a,html=b,note=n) for a,b,n in GALLERY.get(did,[])], galleryWide=(did in GALLERY_WIDE), galleryFull=(did in GALLERY_FULL), optsFull=(did in OPTS_FULL), baked=(dict(choice=bk[0], note=bk[1]) if bk else None)))
    fr=frames_for(c['key'])
    NO_BLOCKS = {'SA-7b','D3','X','D1'}
    blocks=''.join(c['blocks']) if (fr['kind']=='none' and c['key'] not in NO_BLOCKS) else ''
    visual = any(d['gallery'] or any(o.get('frame') for o in d['options']) for d in decs)
    data_cards.append(dict(key=c['key'], section=c['section'], title=c['title'], sub=c['sub'], dims=c['dims'], pop=c['pop'], ruled=c['ruled'], blocks=blocks, frames=fr, decisions=decs, stage=STAGE.get(c['key'],'groomed'), hold=HOLD.get(c['key']), triageMock=TRIAGE_MOCK.get(c['key']), visual=visual))

# ruled / queued items for the dashboard (ruled in chat, filed in BACKLOG, not yet built)
ruled_items=[
 ("MPI & Video","BGO","With bulk green off, a note that only says “everything else is good” shows as a pink bubble","ruled 15 Sep · leave it — closed"),
 ("RO page — advisor, admin, tech","—","A tech can change the labor hours on an internal line until the line is approved or the RO closes","shipped 15 Sep · live 16 Sep"),
 ("RO page — advisor, admin, tech","—","A tech can’t delete a line that was in the estimate the customer was sent","shipped 15 Sep · live 16 Sep"),
 ("Store settings — labor rates & money","SA-19","Saving a new labor rate re-prices every open RO in the store, with no question asked","ruled · waits on T"),
]

LEGACY=json.load(open(O+'/legacy_blocks.json')) if os.path.exists(O+'/legacy_blocks.json') else {}
DATA=dict(legacy={k: dict(title={'risk':'Risk grid','icebox':'Icebox','archive':'Archive'}[k], html=v) for k,v in LEGACY.items()}, sections=SECTION_ORDER, cards=data_cards, ruled=[dict(section=s,key=k,title=t,status=st) for s,k,t,st in ruled_items], icebox="Waiting on something specific", archive="Archive — 84 items shipped since the 29 Aug board", built=__import__("datetime").date.today().strftime("%-d %b %Y"))

PAGE_CSS = """
/* ---------- phone board: type scale (Dave 9/8: bigger) ---------- */
.m-wrap{font-size:16px}
.m-row .t{font-size:15.5px}
.m-open{font-size:12.5px}
.m-title{font-size:19px}
.m-sub{font-size:15.5px}
.m-q{font-size:16.5px}
.m-btn{font-size:16px;min-height:52px}
.m-btn .m-opt{font-size:12.5px}
.m-field{font-size:16px}
.m-hint,.m-details,.m-frame-cap,.m-ruled-line,.m-ruled-line button{font-size:14px}
.m-cap{font-size:11px}
.m-steps > div > div:first-of-type + div,.m-steps span{font-size:15px}
.m-blocks .viz{font-size:15px}
.m-blocks table,.m-blocks .story li,.m-blocks .viz-foot,.m-blocks .scap{font-size:14.5px}
}
.m-empty{font-size:14.5px}
.m-total{font-size:15.5px}
.m-status{font-size:13px}
/* ---------- filed decisions: one line ---------- */
.m-dec.compact{gap:4px;padding-top:12px}
.m-bakedline{display:flex;gap:8px;align-items:flex-start;font-size:14px;color:var(--ink-2);line-height:1.4}
.m-bakedline .m-opt{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11.5px;font-weight:600;color:#fff;background:var(--ink);border:1px solid var(--ink);border-radius:3px;padding:1px 6px;flex:none;margin-top:2px}
.m-bakedans{font-size:14px;color:var(--teal);padding-left:34px;line-height:1.4}
.m-bakednote{color:var(--muted)}
/* ---------- clarifiers ---------- */
.m-ctx{font-size:15px;color:var(--ink-2);line-height:1.45;white-space:pre-line}
.m-gallery{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:4px 0 2px}
.m-gal{margin:0;display:flex;flex-direction:column;gap:6px;min-width:0}
.m-gal figcaption{display:flex;flex-direction:column;gap:1px;font-size:12.5px;line-height:1.3;color:var(--ink)}
.m-gal figcaption span{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:10.5px;color:var(--muted)}
.m-gal-frame{border:1px solid var(--line);border-radius:6px;overflow:hidden;background:#fff;height:300px;position:relative}
.m-gal-inner{width:390px;transform:scale(.437);transform-origin:top left;position:absolute;left:0;top:0}
.m-gallery.one{grid-template-columns:minmax(0,1fr)}
.m-gallery.one .m-gal-frame{height:auto}
.m-gallery.one .m-gal-inner{width:auto;transform:none;position:static}
.m-gallery.full{grid-template-columns:minmax(0,1fr) !important}
.m-gallery.full .m-gal-frame{width:fit-content;max-width:100%}
.m-opts.full{grid-template-columns:minmax(0,1fr) !important}
.m-opts.full .m-btn .m-optframe{width:fit-content;max-width:100%;align-self:flex-start}
.m-btn .m-optframe{width:fit-content;max-width:100%;align-self:flex-start}
.m-btn{flex-direction:column;align-items:stretch;gap:8px}
.m-btn .m-optrow{display:flex;align-items:center;gap:10px;width:100%}
.m-btn .m-optframe{border:1px solid var(--line);border-radius:6px;overflow:hidden;background:#fff;max-width:100%}
.m-btn .m-why{font-size:14px;line-height:1.45;color:var(--ink-2);font-weight:400}
.m-btn:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.m-dec.baked .m-btn{cursor:default}
.m-dec.baked .m-ruled-line span{color:var(--teal)}
/* ---------- stage ---------- */
.m-stage{margin:12px 16px 0;border-radius:var(--radius);border:1px solid var(--line);background:var(--surface);padding:9px 14px;display:flex;flex-direction:column;gap:8px}
.m-stage.triage.ruled{border-color:var(--teal);background:var(--teal-soft)}
.m-stage.triage.ruled .m-stage-lbl{color:var(--teal)}
.m-stage.triage.ruled .m-stage-lbl i{background:var(--teal)}
.m-stage.triage{border-color:var(--amber);background:var(--amber-soft)}
.m-stage-lbl{display:flex;align-items:center;gap:8px;font-size:13px;font-weight:600;color:var(--ink-2)}
.m-stage.triage .m-stage-lbl{color:var(--amber)}
.m-stage-lbl i{width:9px;height:9px;border-radius:999px;background:var(--teal);display:inline-block;flex:none}
.m-stage.triage .m-stage-lbl i{background:var(--amber)}
.m-stage .m-q{font-size:16.5px}
.m-stage .m-btn{background:var(--surface)}
.m-stage.ruled .m-btn{opacity:.45}
.m-stage.ruled .m-btn.chosen{opacity:1;border-color:var(--ink);box-shadow:inset 0 0 0 1px var(--ink)}
.m-stage .m-note{font-size:14px;color:var(--ink-2);line-height:1.45}
.m-groom{flex:none;font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:12.5px;font-weight:600;color:var(--amber);background:var(--amber-soft);border:1px solid var(--amber);border-radius:999px;padding:2px 9px;white-space:nowrap}
.m-row .key.amber{background:var(--amber);color:#fff}
.m-sechdr{font-size:16.5px;font-weight:600;line-height:1.4;padding:22px 16px 0}
.m-sechdr small{display:block;font-size:14px;font-weight:400;color:var(--muted);margin-top:2px}
/* ---------- phone board ---------- */
.app{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#0f172a;line-height:1.35}
.sil{display:inline-block;height:10px;border-radius:3px;background:#cbd5e1;vertical-align:middle}
.ring{box-shadow:0 0 0 3px rgba(56,189,248,.45);border-radius:3px}
body{padding:0}
.m-wrap{max-width:560px;margin:0 auto;padding:0 0 40px;overflow-x:hidden}
html,body{overflow-x:hidden}
#flip-body,.m-steps,.m-steps .frame,.m-frame{max-width:100%;overflow:hidden;min-width:0}
.m-cap{font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.m-h2{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:14px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--ink);line-height:1.3}
.m-badge{flex:none;font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:12px;font-weight:600;font-variant-numeric:tabular-nums;color:var(--accent);background:var(--accent-soft);border:1px solid var(--accent);border-radius:999px;padding:2px 9px;white-space:nowrap}
.m-badge.done{color:var(--teal);background:var(--teal-soft);border-color:var(--teal)}
.m-card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);display:flex;flex-direction:column}
.m-row{display:flex;gap:10px;align-items:center;padding:11px 12px 11px 14px;border-top:1px solid var(--line-2);min-height:52px;color:inherit;text-decoration:none;cursor:pointer;-webkit-tap-highlight-color:transparent}
.m-row:first-child{border-top:0}
.m-row:active{background:var(--surface-2)}
.m-row .t{flex:1 1 auto;min-width:0;font-size:14px;line-height:1.35;color:var(--ink);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.m-row.ruled .t{color:var(--muted)}
.m-row .key.soft{background:var(--teal-soft);color:var(--teal)}
.m-open{flex:none;font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11.5px;font-weight:600;color:var(--accent);background:var(--accent-soft);border:1px solid var(--accent);border-radius:999px;padding:2px 9px;white-space:nowrap}
.m-done{flex:none;font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--teal);background:var(--teal-soft);border-radius:999px;padding:3px 8px;white-space:nowrap}
.m-note-dot{flex:none;width:8px;height:8px;border-radius:999px;background:var(--amber)}
.m-chev{flex:none;color:var(--muted)}
.m-top{padding:calc(14px + env(safe-area-inset-top)) 16px 0}
.m-back{display:inline-flex;align-items:center;gap:4px;color:var(--accent);font-size:14px;min-height:44px;text-decoration:none}
.m-title{display:flex;gap:10px;align-items:flex-start;font-size:17px;font-weight:600;line-height:1.3;letter-spacing:-.01em}
.m-sub{font-size:13.5px;color:var(--ink-2);line-height:1.45;margin-top:6px;max-width:none}
.m-seg{display:flex;border:1px solid var(--line);border-radius:999px;padding:3px;background:var(--surface);font-size:13px;font-weight:500;margin:14px 16px 0}
.m-seg button{flex:1;text-align:center;padding:7px 0;border-radius:999px;color:var(--muted);min-height:38px;border:0;background:none;font:inherit;cursor:pointer}
.m-seg button.on{background:var(--ink);color:#fff}
.m-frame{margin:12px 16px 0;border:1px solid var(--line);border-radius:6px;overflow:hidden;background:#fff}
.m-frame-cap{margin:6px 16px 0;font-size:12.5px;color:var(--muted);line-height:1.45}
.m-steps{padding:6px 16px 0;display:flex;flex-direction:column;gap:14px}
.m-steps .frame{border:1px solid var(--line);border-radius:6px;overflow:hidden;background:#fff}
.m-blocks{padding:0 16px}
.m-blocks .viz{margin-top:14px}
.m-dec{padding:18px 16px 0;display:flex;flex-direction:column;gap:8px}
.m-q{font-size:15px;font-weight:600;line-height:1.4}
.m-btn{display:flex;align-items:center;gap:10px;min-height:48px;padding:10px 14px;border-radius:var(--radius);border:1px solid var(--line);background:var(--surface);font:inherit;font-size:14.5px;line-height:1.35;color:var(--ink);text-align:left;width:100%;cursor:pointer;-webkit-tap-highlight-color:transparent}
.m-btn .m-opt{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11.5px;font-weight:600;color:var(--accent);border:1px solid var(--accent);border-radius:3px;padding:1px 6px;background:var(--accent-soft);flex:none}
.m-btn .m-rec{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--teal);background:var(--surface);border:1px solid var(--teal);border-radius:999px;padding:0 6px;white-space:nowrap;flex:none;line-height:18px;margin-left:auto}
.m-btn.is-rec{border-color:var(--teal);background:var(--teal-soft)}
.m-btn.is-rec .m-opt{color:var(--teal);border-color:var(--teal);background:var(--surface)}
.m-dec.ruled .m-btn{opacity:.45}
.m-dec.ruled .m-btn.chosen{opacity:1;border-color:var(--ink);box-shadow:inset 0 0 0 1px var(--ink)}
.m-dec.ruled .m-btn.chosen .m-opt{color:#fff;background:var(--ink);border-color:var(--ink)}
.m-ruled-line{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:12.5px;color:var(--teal)}
.m-ruled-line button{border:0;background:none;color:var(--muted);font:inherit;font-size:12.5px;text-decoration:underline;cursor:pointer;min-height:32px;padding:0}
.m-field{width:100%;min-height:48px;border:1px dashed var(--line);border-radius:var(--radius);background:var(--surface-2);padding:12px 14px;font:inherit;font-size:14px;color:var(--ink);resize:vertical;box-sizing:border-box}
.m-field::placeholder{color:var(--muted)}
.m-field:focus{outline:2px solid var(--accent);outline-offset:1px;border-style:solid}
.m-field.filled{border-style:solid;background:var(--surface)}
.m-hint{font-size:12px;color:var(--muted)}
.m-foot{margin-top:22px;padding:14px 16px 24px;border-top:1px solid var(--line-2);display:flex;align-items:center;justify-content:space-between;gap:10px}
.m-next{display:inline-flex;align-items:center;gap:4px;color:var(--accent);font-size:14px;font-weight:500;white-space:nowrap;text-decoration:none;min-height:44px}
.m-details{font-size:12.5px;color:var(--muted);line-height:1.45}
.m-details summary{cursor:pointer;min-height:44px;display:flex;align-items:center;gap:6px;list-style:none}
.m-details summary::-webkit-details-marker{display:none}
.m-status{margin:10px 16px 0;font-size:12px;color:var(--muted);display:flex;align-items:center;gap:6px}
.m-status i{width:8px;height:8px;border-radius:999px;background:var(--line);display:inline-block}
.m-status.live i{background:var(--teal)}
.m-status.local i{background:var(--amber)}
.m-empty{border:1px dashed var(--line);border-radius:var(--radius);padding:12px 14px;font-size:13px;color:var(--muted);line-height:1.45}
.m-hero{padding:calc(20px + env(safe-area-inset-top)) 16px 0;display:flex;flex-direction:column;gap:4px}
.m-hero h1{font-size:30px;margin:0;letter-spacing:-.02em}
.m-total{font-size:14px;color:var(--muted)}
.m-sec{padding:14px 16px 0;display:flex;flex-direction:column;gap:6px}
.m-sechead{display:flex;align-items:center;gap:10px;width:100%;min-height:44px;padding:0 2px;border:0;background:none;font:inherit;text-align:left;cursor:pointer;-webkit-tap-highlight-color:transparent}
.m-sechead .m-h2{flex:1 1 auto}
.m-sechead .m-chev{transition:transform .15s ease}
.m-sec.collapsed .m-sechead .m-chev{transform:rotate(-90deg)}
.m-secbody{display:grid;grid-template-rows:1fr;transition:grid-template-rows .28s ease}
.m-sec.collapsed .m-secbody{grid-template-rows:0fr}
.m-secclip{overflow:hidden;min-height:0}
.m-sec.collapsed .m-secclip{visibility:hidden;transition:visibility 0s .28s}
.m-secclip{visibility:visible}
.m-deskbody{display:grid;grid-template-rows:0fr;transition:grid-template-rows .3s ease}
.m-deskcard.open .m-deskbody{grid-template-rows:1fr}
.m-deskclip{overflow:hidden;min-height:0}
.m-deskhead .m-chev{transition:transform .2s ease}
.m-cardfoot{display:flex;justify-content:flex-end;padding:6px 16px 14px}
.m-collapse{display:inline-flex;align-items:center;gap:7px;min-height:40px;padding:0 12px;border:1px solid var(--line);border-radius:var(--radius);background:var(--surface-2);font:inherit;font-size:13px;color:var(--ink-2);cursor:pointer}
.m-collapse svg{transform:rotate(180deg)}
.m-collapse:hover{border-color:var(--accent);color:var(--ink)}
@media (prefers-reduced-motion: reduce){.m-secbody,.m-deskbody,.m-deskhead .m-chev{transition:none}}
@media (prefers-reduced-motion: reduce){.m-sechead .m-chev{transition:none}}

/* ---------- desktop (≥900px): same anatomy, wider ---------- */
.m-opts{display:flex;flex-direction:column;gap:8px}
@media (min-width: 900px){
  .m-wrap{max-width:1180px;padding:0 24px 60px}
  .m-hero{padding-top:36px}
  .m-deskcard{border-top:1px solid var(--line-2)}
  .m-deskcard:first-child{border-top:0}
  .m-deskcard.open{background:var(--surface)}
  .m-deskhead{cursor:pointer;border-top:0}
  .m-deskcard.open .m-deskhead .m-chev{transform:rotate(90deg)}
  .m-deskcard.open .m-deskclip{border-top:1px dashed var(--line)}
.m-deskinner{padding:0 8px 8px}
  .m-legacy-status{padding:0 14px 10px 50px;font-size:13px;color:var(--teal)}
  .m-both{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;padding:14px 16px 0;align-items:start}
  .m-both .m-frame{margin:0}
  .m-both .m-steps{padding:0}
  .m-both-cap{margin:0 0 8px}
  .m-opts{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:12px;align-items:start}
  .m-opts-stage{grid-template-columns:repeat(3,minmax(0,1fr))}
  .m-gallery.desk{grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:14px}
  .m-gallery.desk .m-gal-frame{height:auto}
  .m-gallery.desk .m-gal-inner{width:auto;transform:none;position:static}
  .m-dec{padding-left:16px;padding-right:16px}
  .m-trimock{max-width:420px}
  .m-legacy .card{border:0;box-shadow:none;padding:16px 20px}
  .m-blocks{max-width:none}
}
/* Dave's own words on a card — amber, the colour of the 'ruled · discuss' pill (⛔ Dave 10 Sep): ⟦…⟧ in the data → .m-dave; words he types on the board are his too */
.m-dave{color:var(--amber);font-weight:500}
.m-field.filled{color:var(--amber)}
/* ---------- phone only: Dave 9/10 "On mobile, the card text is too small. Go bigger." (+2 px across the scale; LAST in PAGE_CSS — the base rules below the 9/8 block override anything placed above them) ---------- */
@media (max-width: 899px){
.m-wrap{font-size:18px}
.m-row .t{font-size:17.5px}
.m-title{font-size:22px}
.m-sub{font-size:17.5px}
.m-q{font-size:18.5px}
.m-btn{font-size:18px;min-height:56px}
.m-opt,.m-btn .m-opt{font-size:14px}
.m-field{font-size:18px}
.m-hint,.m-details,.m-frame-cap,.m-ruled-line,.m-ruled-line button{font-size:16px}
.m-cap{font-size:12.5px}
.m-bakedans,.m-bakedline{font-size:16.5px}
.m-why{font-size:16.5px}
.m-ctx{font-size:17px}
.m-stage-lbl{font-size:15.5px}
.m-open,.m-groom{font-size:14px}
.m-done,.m-rec{font-size:11.5px}
.m-status{font-size:14.5px}
.m-empty{font-size:16px}
.m-total{font-size:17px}
.m-h2{font-size:15.5px}
.m-seg{font-size:15px}
.m-next{font-size:16px}
.m-legacy-status{font-size:15px}
.m-gal figcaption{font-size:14.5px}
.m-gal figcaption span{font-size:12px}
.m-steps > div > div:first-of-type + div,.m-steps span{font-size:17px}
.m-blocks .viz{font-size:17px}
.m-blocks table,.m-blocks .story li,.m-blocks .viz-foot,.m-blocks .scap{font-size:16.5px}
"""

JS = open(os.path.join(O, "app.js")).read()


DATA_JSON = json.dumps(DATA).replace("</", "<\\/")
page = f"""<title>Grooming Board</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
{board_css}
{PAGE_CSS}
</style>
<div class="m-wrap"><div id="app"></div></div>
<script id="board-data" type="application/json">{DATA_JSON}</script>
<script>{JS}</script>
"""
open(O+'/grooming-board-phone.html','w').write(page)
print('bytes', len(page), 'cards', len(data_cards), 'decisions', sum(len(c['decisions']) for c in data_cards))
