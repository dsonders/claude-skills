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

# ----- VC7 / VC8 -----
CONTEXT['VC7-1'] = 'Measured on the cue-card test set (20 real inputs × 3 runs): Rear Tires RO-11 shows the green front 7/32″ in 0 of 3 cards; Rear Brakes RO-12 in 1 of 3; Rear Brakes RO-09 and Front Tires RO-16 in 3 of 3. The corners are handed to the writer every time; the writer leaves them out when the finding’s own notes already carry two corners. The rule’s only example is brakes.'
OPT_VIS['VC7-1'] = {'A': {'why': 'The cheapest change to the writer, with the before/after numbers in the build’s record.'}, 'B': {'why': 'Reorders what the writer reads; may help or hurt other cards — the test set decides.'}, 'C': {'why': 'The tech remembers the fronts on camera, or doesn’t.'}, 'D': {'why': 'Always on the card, nothing to teach — but it is the app’s line under the writer’s, not one of his sentences.'}}
CONTEXT['VC8-1'] = 'Green shots are opt-in and carry the flag line “Looks good — reassure the customer”. Handing the writer the red rear corners on a green front-tires card means it may say “rear tires 2/32″” on the good-news shot, against its own flag line.'
OPT_VIS['VC8-1'] = {'A': {'why': 'The good news stays good news; the red card in the same deck carries the bad.'}, 'B': {'why': '“All four tires 7/32″” on a green card when it is true; silence when a sibling is red.'}, 'C': {'why': 'The tech gets every reading on every card, and a green card can contradict its own flag line.'}, 'D': {'why': 'Reverses the 3 Sep picker decision that let a tech add a good-news shot.'}}

# ================= Parts page & queue =================
TRI_SM = OF.TRI.replace('width="20" height="20"', 'width="14" height="14"')
def hint_frame(sentence):
    return OF.app(f'<div style="display:flex;flex-direction:column;gap:6px;"><div style="min-height:44px;border-radius:6px;background:#2563eb;color:#fff;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:600;">Send to advisor</div><div style="font-size:12.5px;line-height:1.4;color:#92400e;display:flex;gap:6px;align-items:flex-start;"><span style="flex:none;">{TRI_SM}</span><span>{sentence}</span></div></div>')
SO_A = '2 parts have no price — their lines will be quoted with those parts counted as $0.00.'
SO_B = '2 parts still need pricing. Those lines will be quoted to the customer with the unpriced parts counted as $0.00 — and the customer can approve them at that price.'
GALLERY['SO-1'] = [('Today — the hint under the button', hint_frame(SO_A), ''), ('Today — the dialog after tapping it', OF.send_gate_today(), '')]
CONTEXT['SO-1'] = 'The internal and warranty sentences already match on both surfaces (the 10–11 Sep builds). Only the customer sentence still has two versions.'
OPT_VIS['SO-1'] = {
 'A': {'frame': OF.dialog('Some parts aren’t priced yet', SO_A, 'Send anyway', 'Cancel', icon=OF.TRI), 'why': 'The shorter one; the dialog says what the hint said, one sentence.'},
 'B': {'frame': hint_frame(SO_B), 'why': 'The longer one under the button too — it names the customer and that they can approve at $0.00.'},
 'C': {'why': 'Two wordings for one fact, as today.'},
 'D': {'frame': OF.app('<div style="min-height:44px;border-radius:6px;background:#2563eb;color:#fff;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:600;">Send to advisor</div>'), 'why': 'The button stands alone; the dialog carries the warning.'},
}

# ================= RO page =================
# ----- BM: bulk move at 1440 (real captures, advisor role) -----
BMH = json.load(open(REAL+'/bm-heights.json')) if _os.path.exists(REAL+'/bm-heights.json') else None
def _bm(name, alt, fallback=None):
    if has_real(name): return real_img(name, alt)
    return real_img(fallback, alt, dpr=1) if fallback and has_real(fallback) else None
def _h(v, k):
    try: return f"{BMH[v][k]} px tall" if BMH and BMH.get(v,{}).get(k) is not None else ''
    except Exception: return ''
gal = []
t_sel = _bm('bm-today-select','Today, select', 'bm-fallback-select'); t_ask = _bm('bm-today-ask','Today, ask', 'bm-fallback-ask')
if t_sel: gal.append(('Today, 1440 — choosing the pay type: Internal and Cancel sit under the Customer-link panel; a click on Internal lands on the panel', t_sel, '62 px · 677 px of content in a 492 px column'))
if t_ask: gal.append(('Today, 1440 — the rewrite question: two buttons, the question line measures 0 px', t_ask, '62 px'))
GALLERY['BM-1'] = gal
GALLERY_FULL.add('BM-1'); OPTS_FULL.add('BM-1')
CONTEXT['BM-1'] = 'Real screens of the advisor’s RO page on the test store at 1440 wide, three lines selected. The tech’s page has no Customer-link panel, so the same bar has the full width and both stages read fine there.'
w_sel = _bm('bm-wrap-select','Wrapped, select'); w_ask = _bm('bm-wrap-ask','Wrapped, ask'); n_sel = _bm('bm-nopanel-select','No panel, select'); n_ask = _bm('bm-nopanel-ask','No panel, ask')
def _join(*fr): return ''.join(f'<div style="margin-bottom:8px;">{f}</div>' for f in fr if f)
OPT_VIS['BM-1'] = {
 'A': {'frame': (_join(w_sel, w_ask) or None), 'why': 'Every pill is reachable and the question gets its own line. Measured: 62 → 170 px while choosing the pay type (three rows — “Move to” and four pills do not fit on two at this width), 62 → 120 px at the question. The tech’s bar is untouched.'},
 'B': {'frame': (_join(n_sel, n_ask) or None), 'why': 'The panel steps aside for the seconds the bar is up and comes back after: one 62 px row like the tech’s, everything clickable. The right half of the page is empty meanwhile.'},
 'C': {'why': 'The move still lands and the buttons work; the advisor never sees the question and cannot pick Internal on this screen.'},
 'D': {'why': 'The phone’s stepped sheet on a desktop — one shape for both devices, but a sheet over a 1440 page for a three-line move is heavy.'},
}

# ----- PH: the Changes list (design-heavy → his raw take first) -----
GALLERY['PH-1'] = [('Where it would live — the admin’s Parts & Labor card today, on your 1920 screen', real_img('pbw-locked','Parts & Labor card today'), '')]
GALLERY_FULL.add('PH-1')
CONTEXT['PH-1'] = 'What is recorded already, per change, since June: the field (part price, quantity, stock answer, note, labor hours, labor rate), the value before and after, who made it and when. Actor names would show with the per-store name override. Nothing here reaches the customer’s page.'
OPT_VIS['PH-2'] = {'A': {'why': 'The list answers “who changed this price” and nothing else.'}, 'B': {'why': 'Longer list; a stock answer or a note edit reads beside a price change.'}, 'C': {'why': 'The record keeps accruing; the screen waits for a real ask.'}, 'D': {'why': 'No new screen — but every price edit becomes a note in the RO’s thread, and a ten-part line makes ten notes.'}}

# ================= Dashboards =================
GALLERY['D3-1'] = [('Today — filters on', OF.toolbar(False), ''), ('The fix', OF.toolbar(True), '')]
CONTEXT['D3-1'] = 'Desktop admin dashboard, all four filters on. Today the switch is the first thing to give up width, so “List” clips to “Li”. The fix keeps the switch whole and lets the filter boxes shrink first (they already show “…”).'
OPT_VIS['D3-1'] = {'C': {'why': 'The switch keeps clipping whenever a filter is on.'}}
CONTEXT['SA-7b-1'] = 'Your question: ⟦“a part waiting on the store”⟧ is a part the counter adds to an INTERNAL (store-pay) line after the advisor already authorized that line. The add withdraws the store’s OK, and the advisor approves or declines the part on the RO page, where it reads “Needs store OK” (below). The dashboard badge lumps those with parts waiting on a customer, so it can only say “Needs approval”.'
GALLERY['SA-7b-1'] = [('The situation — the advisor’s ledger on an internal line', OF.ledger_store_ok(), ''), ('Today — the dashboard badge', OF.dash_badge(['Needs approval']), '')]
OPT_VIS['SA-7b-1'] = {
 'A': {'frame': OF.dash_badge(['Needs customer OK','Needs store OK']), 'why': 'Each RO stores the two counts separately, so the badge can name the family — one badge per family when both apply.'},
 'B': {'frame': OF.dash_badge(['Needs customer OK']), 'why': 'One stored count, as today, labelled “Needs customer OK” again — wrong whenever only the store is waiting.'},
 'C': {'frame': OF.dash_badge([]), 'why': 'No badge at all; the row color and the LINES column are what the advisor scans.'},
}
OPT_VIS['SA-7b-2'] = {'A': {'why': 'The dashboard uses the words the RO page already uses for the same part.'}, 'B': {'why': 'Say the wording below.'}}
GALLERY['X-1'] = [('Today', OF.booked(), '')]
CONTEXT['X-1'] = 'The “+N TBD” row still exists in the cell, but it counts lines with no total — and since 8/27 every line has one, so it is always 0 and never shows.'
OPT_VIS['X-1'] = {'A': {'frame': OF.booked('+2 price gaps'), 'why': 'The same amber row, counting what the RO header counts: labor hours missing or 0, a part row blank or $0. One new number sent to the dashboard.'}, 'B': {'frame': OF.booked(), 'why': 'The cell stays as it looks today; the dashboard keeps showing no gaps while the RO page and parts page do.'}}
OPT_VIS['X-2'] = {'A': {'frame': OF.booked_hover(True), 'why': 'The existing Booked hover gains a “Price gaps” section: each line and what its gap is.'}, 'B': {'frame': OF.booked_hover(False), 'why': 'The hover stays as today; the count alone points to the RO page.'}}
OPT_VIS['D1-1'] = {'A': {'frame': OF.money_row('Total'), 'why': 'Every money row reads “Total”. Same number, same color, nothing else moves.'}, 'B': {'frame': OF.money_row('Total Booked'), 'why': 'Keep “Total Booked”.'}}
CONTEXT['D1-2'] = 'Checked in the code on 9/8: the customer’s page never uses “booked” anywhere — the word is staff-only. So this ruling changes nothing either way.'

# ================= Store settings =================
OPT_VIS['T-1'] = {'A': {'why': 'Each approved line remembers the labor rate it was agreed at. Hours and parts keep re-deriving; a later rate change leaves the line alone.'}, 'B': {'why': 'The line remembers rate, hours and parts as agreed, as one frozen snapshot. Any later edit is visibly a change from the agreed figures — more to store, simpler to reason about.'}, 'C': {'why': 'Five places keep their own “never re-figure a frozen line” rule; the next new money path has to remember it too.'}}
OPT_VIS['T-2'] = {'A': {'why': 'A one-time cleanup you run: every already-approved line gets a rate worked back from its stored total and hours. Lines with no hours can’t be worked back and stay on the total.'}, 'B': {'why': 'Old approved lines keep their stored total and the “never re-figure a frozen line” special case until they close; only lines approved after the build carry a rate.'}}

# ================= Platform & tooling =================
CONTEXT['EH-1'] = 'The writer fix ships either way: a save that carries the story through unchanged is no longer recorded as an edit. This decides the rows already written. Seen on McGrath RO 832799 (two phantom edits, 17:24 and 20:03) and RO 833321 — the stored text was never touched.'
OPT_VIS['EH-1'] = {'A': {'why': 'The statistics read true for the whole era; one script, run once.'}, 'B': {'why': 'History keeps the rows; every reader of the trail has to know to skip them.'}, 'C': {'why': 'The counts stay inflated for everything before the fix.'}, 'D': {'why': 'Nothing to clean, and one fewer thing to maintain — if the numbers have no reader.'}}
CONTEXT['Y3-1'] = ('The eight, each with the recommendation:\n'
 '1 · A 1.5-second automatic re-grade after a story edit that nothing on the page can reach (the Re-Grade button is the live one) — delete it. '
 '\n2 · Typing in a line’s Cause sends one save per keystroke to the RO (94 saves for 93 characters); the one-second wait is not working — fix it so it saves once after you stop typing. '
 '\n3 · Three permission checks named by the 9/11 sweep (the labor-rate sweep decides a stage from a captured mapping; assignment fields ride the close write with no check; Re-open passes none) — fix as defects in one mirrored PR. '
 '\n4 · Two money paths judge a store-approval withdrawal on a setting captured before the write — read it inside the write, and refuse the write if the store cannot be read. '
 '\n5 · A cleanup script can leave a stale “declined at close” mark — clear it the next time the script is touched. '
 '\n6 · Two older CI checks still carry their own copy of the diff reader — move them onto the shared one, own PR, when no build is in flight. '
 '\n7 · The store-scoping check is blind to a select taken outside a transaction whose record is then read inside one — teach it that shape, with a fixture that must flag and one that must pass. '
 '\n8 · Pin the version of the review bot the CI installs (exact, bumped by the bot) and comment on any PR whose squash deletes test files — comment, not block.')
OPT_VIS['Y3-1'] = {'A': {'why': 'Eight small PRs in the next run; the permission one gets the pre-push mirror.'}, 'B': {'why': 'Name the number(s) to hold below; the rest ship.'}, 'C': {'why': 'Nothing ships; the keystroke storm and the three permission gaps stay.'}}
OPT_VIS['Y2-1'] = {'A': {'why': 'The three recommendations in the table ship as one small PR.'}, 'B': {'why': 'Name the one to hold below; the other two ship.'}, 'C': {'why': 'Nothing ships.'}}
OPT_VIS['Y-1'] = {'A': {'why': 'The seven recommendations in the table ship as one small PR.'}, 'B': {'why': 'Name the one(s) to hold below; the rest ship.'}, 'C': {'why': 'Nothing ships.'}}
OPT_VIS['Z-1'] = {'A': {'why': 'A build session that tries to take a worktree another session holds is stopped with a message, instead of proceeding and wiping the other’s work.'}, 'B': {'why': 'The claim stays a convention; a session that ignores it can still wipe a sibling’s build.'}}
OPT_VIS['Z-2'] = {'A': {'why': 'One copy of the env-seeding script, outside the repo. Nothing to keep in sync.'}, 'B': {'why': 'A second copy inside the repo; every change has to be made twice or the two drift.'}}
OPT_VIS['EX5-1'] = {'A': {'why': 'Nothing changes now. The bot stops proposing the major bump; the move is picked up when the current version reaches end of life or an advisory reaches this app.'}, 'B': {'why': 'A medium build now: three catch-all routes rewritten, the error-forwarding change across ~200 handlers, and a live pass on every request path before it ships.'}}
OPT_VIS['EX5-2'] = {'A': {'why': 'Routes and types move first under the current version — reviewable on its own — then a small flip PR.'}, 'B': {'why': 'One large PR; Codex rounds scale with size, and a live regression is harder to pin to a cause.'}}

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
 ("Parts page & queue","—","Reject the retired “in stock” / “on order” values on a part’s pulled record","ruled 11 Sep · queued for the run after the next republish"),
 ("RO page — advisor, admin, tech","—","Internal-line labor hours: a tech edits them in every stage until the line is authorized or the RO closes","ruled 11 Sep · queued"),
 ("RO page — advisor, admin, tech","—","A tech cannot delete a line that was in the sent estimate","ruled 11 Sep · queued"),
 ("Store settings — labor rates & money","SA-19","Saving a new labor rate re-prices every open RO in the store — with no question asked","ruled 30 Aug · waits on T"),
]

LEGACY=json.load(open(O+'/legacy_blocks.json')) if os.path.exists(O+'/legacy_blocks.json') else {}
DATA=dict(legacy={k: dict(title={'risk':'Risk grid','icebox':'Icebox','archive':'Archive'}[k], html=v) for k,v in LEGACY.items()}, sections=SECTION_ORDER, cards=data_cards, ruled=[dict(section=s,key=k,title=t,status=st) for s,k,t,st in ruled_items], icebox="Waiting on something specific", archive="Archive — 77 items shipped since the 29 Aug board", built=__import__("datetime").date.today().strftime("%-d %b %Y"))

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
