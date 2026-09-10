import os, json, html, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import ro_panel, owner_page, step, sil
from parts_card import parts_card
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin_card.py')).read())
from decisions import DEC, STAGE, STAGE_NOTE, BAKED
from triage_frames import parts_card_tall, stock_answer_row, parts_line_variant, Q_VARIANTS
import option_frames as OF
import os as _os
MEASURED = json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),'measured.json'))) if _os.path.exists(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),'measured.json')) else {}
O=os.path.dirname(os.path.abspath(__file__))
cards=json.load(open(O+'/cards.json'))
board_css=open(O+'/board.css').read()

SECTION_ORDER=["MPI & Video","Parts page & queue","RO page — advisor, admin, tech","Dashboards","Customer page","Store settings — labor rates & money","Platform & tooling"]

# ---- frames for the three drawn items ----
def frames_for(key):
    if key=="SA-6b":
        return dict(kind="flip", caption="The advisor, opening the line after close.",
            today=ro_panel("Declined by the customer"), proposed=ro_panel("Declined at close", ring=True))
    if key=="U":
        return dict(kind="flip", caption="The customer, back on their own page after the drop — inline, the amount only.",
            today=owner_page(), proposed=owner_page(note=True))
    if key=="P":
        today = (step(1,"The parts counter,","on the parts page, adds the recall part to the line — number, name, stock still “?”, no price yet.", parts_card())
              + step(2,"The admin,","opening the same RO two minutes later, sees the line’s money card locked — and empty.", ADMIN_CARD("today_locked"))
              + step(3,"The admin","taps the edit control to price the line. Only now does the counter’s part appear.", ADMIN_CARD("today_edit"), last=True))
        prop = (step(1,"The parts counter,","on the parts page, adds the recall part to the line — number, name, stock still “?”, no price yet.", parts_card())
              + step(2,"The admin,","opening the same RO two minutes later, sees the counter’s part on the locked card — every field the counter sees, read-only; the row scrolls sideways for stock, note, qty and price, as on the parts page.", ADMIN_CARD("proposed_locked"))
              + step(3,"The admin","taps the edit control only to change pricing — nothing new appears, nothing was hidden.", ADMIN_CARD("proposed_edit"), last=True))
        return dict(kind="walk", caption="Same line, two minutes apart", today=f'<div class="m-steps">{today}</div>', proposed=f'<div class="m-steps">{prop}</div>')
    return dict(kind="none")

# Per-decision clarifiers (Dave 9/8: 'when you ask me this way or that way, I need to see what each looks like').
# CONTEXT[dec_id] = one situation paragraph. OPT_VIS[dec_id][letter] = {'frame': html, 'why': implication}. GALLERY[dec_id] = list of (label, html, note) shown above the options.
CONTEXT, OPT_VIS, GALLERY = {}, {}, {}
GALLERY_WIDE = {'Q-1'}
GALLERY_FULL = {'Q-1'}  # one column at every width — the frames are full desktop screens

import base64 as _b64
REAL = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'real')
RH = json.load(open(REAL+'/heights.json'))
def real_img(name, alt):
    b = _b64.b64encode(open(f'{REAL}/{name}.jpg','rb').read()).decode()
    return f'<img src="data:image/jpeg;base64,{b}" alt="{alt}" style="display:block;width:100%;height:auto;">'
def q_gallery():
    dk = RH['desktopHeights']
    def note(k): return f"{dk[k]} px" + (f" · saves {dk['today']-dk[k]}" if k!='today' and dk['today']-dk[k]>0 else (" · saves nothing on desktop — the three tiles share the tallest tile’s height" if k=='notes' else "")) + (" · the Complaint and Cause tiles now set the row’s height" if k=='dave' else "")
    items = [
      ('today',   'Today — the parts counter’s screen, 1440 wide'),
      ('dave',    'Your combination — tighter padding · notes tile at today’s width, Story Notes / Complaint / Cause sharing the rest equally, eyebrow labels · the rail'),
      ('pad',     '① Tighter padding'),
      ('cc',      '② Complaint / Cause one line each'),
      ('rail',    '③ “Parts Needed” rail sideways'),
      ('notes',   '④ Collapse the notes band'),
      ('onerow',  '⑤ Each part on one text row'),
      ('compact', '⑥ “Compact” = ①+②+④+⑤ together'),
    ]
    return [(label, real_img('qd-'+k, label), note(k)) for k,label in items]
GALLERY['Q-1'] = q_gallery()
CONTEXT['Q-1'] = 'Real screens of the parts page on the test store, one recall line with two parts, 1440 wide — the parts counter works on desktop. Each variant is applied to the live page and measured there. Two things the screens show: the notes tile carries an empty band because the three tiles share the tallest tile’s height, and “hover for all” sits on top of the clamped 3C text.'
CONTEXT['Q-2'] = 'Compare ② above with Today: one line each, the full text on hover (desktop) or tap (phone).'
CONTEXT['Q-3'] = 'Compare ③ above: the heading row goes, the label turns sideways on the left edge.'
OPT_VIS['Q-1'] = {'D': {'frame': real_img('qd-dave','Your combination'), 'why': 'Biggest saving that keeps every control where it is: 372 px against 477. Complaint and Cause carry their label as an eyebrow above two full-width lines of text, and “hover for all” sits clear of the text.'}}
OPT_VIS['Q-4'] = {'A': {'why': 'Only the parts counter’s card changes; the advisor’s and tech’s line cards keep today’s height, so the same line looks different per role.'}, 'B': {'why': 'One card shape for everyone; the advisor’s Parts & Labor card and the tech’s line card shrink the same way.'}}
CONTEXT['Q-5'] = 'Measured on the real page at 1440 wide: 477 px today, one line with two parts. A number here becomes the build’s target — leave it blank to take whatever the chosen variants give.'
OPT_VIS['SA-6b-2'] = {'A': {'why': 'Nothing moves on the dashboards or in the money bands — the line stays a declined line everywhere; only the banner’s words change.'}, 'B': {'why': 'A new bucket: dashboards and money bands would show “declined at close” apart from customer declines — new counts, new columns.'}}
OPT_VIS['T-1'] = {'A': {'why': 'Each approved line remembers the labor rate it was agreed at. Hours and parts keep re-deriving; a later rate change leaves the line alone.'}, 'B': {'why': 'The line remembers rate, hours and parts as agreed, as one frozen snapshot. Any later edit is visibly a change from the agreed figures — more to store, simpler to reason about.'}}
OPT_VIS['T-2'] = {'A': {'why': 'A one-time cleanup you run: every already-approved line gets a rate worked back from its stored total and hours. Lines with no hours can’t be worked back and stay on the total.'}, 'B': {'why': 'Old approved lines keep their stored total and the “never re-figure a frozen line” special case until they close; only lines approved after the build carry a rate.'}}
OPT_VIS['Z-1'] = {'A': {'why': 'A build session that tries to take a worktree another session holds is stopped with a message, instead of proceeding and wiping the other’s work.'}, 'B': {'why': 'The claim stays a convention; a session that ignores it can still wipe a sibling’s build.'}}
OPT_VIS['Z-2'] = {'A': {'why': 'One copy of the env-seeding script, outside the repo. Nothing to keep in sync.'}, 'B': {'why': 'A second copy inside the repo; every change has to be made twice or the two drift.'}}
OPT_VIS['EX5-1'] = {'A': {'why': 'Nothing changes now. The bot stops proposing the major bump; the move is picked up when the current version reaches end of life or an advisory reaches this app.'}, 'B': {'why': 'A medium build now: three catch-all routes rewritten, the error-forwarding change across ~200 handlers, and a live pass on every request path before it ships.'}}
OPT_VIS['EX5-2'] = {'A': {'why': 'Routes and types move first under the current version — reviewable on its own — then a small flip PR.'}, 'B': {'why': 'One large PR; Codex rounds scale with size, and a live regression is harder to pin to a cause.'}}
OPT_VIS['Y2-1'] = {'A': {'why': 'The three recommendations in the table ship as one small PR.'}, 'B': {'why': 'Name the one to hold below; the other two ship.'}}
OPT_VIS['Y-1'] = {'A': {'why': 'The seven recommendations in the table ship as one small PR.'}, 'B': {'why': 'Name the one(s) to hold below; the rest ship.'}}
OPT_VIS['W-2'] = {'A': {'why': 'Warranty and recall lines are treated like internal ones: they never trigger the customer-sees-a-gap warning.'}, 'B': {'why': 'Warranty and recall lines stay in the warning, since the customer’s page does list them (at $0).'}}
OPT_VIS['S-3'] = {'A': {'why': 'The advisor’s and admin’s hours field follows the same rule as the tech’s, so nobody can re-open hours under a sent estimate.'}, 'B': {'why': 'The advisor and admin keep editing hours at any stage, as today; the rule binds the tech only.'}}


# ----- P -----
def ledger_row_with_stock_note():
    return OF.app(f'<div style="border-radius: 6px; border: 1px solid #e5e7eb; background: #fff; padding: 12px;"><div style="font-size: 14px; font-weight: 600; color: #1f2937; margin-bottom: 8px;">Parts <span style="font-size: 12px; font-weight: 400; color: #9ca3af;">1</span></div><div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;"><span style="font-size: 14px; font-weight: 600; color: #0f172a;">Fuel pump module</span><span style="font-size: 12px; font-family: ui-monospace, Menlo, monospace; color: #9ca3af;"># RC-FP-002</span><span style="display: inline-flex; align-items: center; border-radius: 999px; background: #f1f5f9; color: #64748b; font-size: 10.5px; font-weight: 600; padding: 2px 8px;">Stock ?</span><span style="display: inline-flex; align-items: center; gap: 4px; font-size: 12px; color: #64748b;">📝 no note</span><span style="margin-left: auto; display: inline-flex; gap: 8px; align-items: center;"><span style="font-size: 12px; color: #6b7280;">×1</span><span style="font-family: ui-monospace, Menlo, monospace; font-size: 13px; color: #d1d5db;">—</span></span></div></div>', bg="#d1d5db")
OPT_VIS['P-1'] = {
 'A': {'frame': ADMIN_CARD("proposed_locked").replace(' class="ring"',''), 'why': 'The admin reads the same six columns the counter sees — Part # · Name · In stock? · Note · Qty · Unit price — as a locked copy of the parts page row. It scrolls sideways on a phone, as the parts page does.'},
 'B': {'frame': ledger_row_with_stock_note(), 'why': 'The ledger keeps its one-line money row and gains two chips: the stock answer and the note. Fits a phone without scrolling; parts fields are summarized, not shown.'},
}
CONTEXT['P-1'] = 'Locked = before the admin taps Edit pricing. Both frames show the same part the counter added.'
OPT_VIS['P-2'] = {
 'A': {'frame': ADMIN_CARD("proposed_edit").replace(' class="ring"',''), 'why': 'Edit mode matches the parts page 1:1 — the Note cell and the Parts Total footer with its Sum / Manual switch. A typed Parts Total goes through the same rules as on the parts page.'},
 'B': {'frame': ADMIN_CARD("today_edit"), 'why': 'Edit mode stays pricing-only, as today: name, part #, qty, stock, unit price. Notes and the Parts Total stay the counter’s.'},
}
OPT_VIS['P-4'] = {
 'A': {'frame': OF.takeover_dialog(), 'why': 'The admin gets the parts users’ own take-over dialog. The counter then sees the red “took over this RO” notice and may lose unsaved edits.'},
 'B': {'frame': OF.parts_hold_banner(button=False, hint='Try again when they are done.'), 'why': 'The admin sees who holds the RO and waits. Nothing of the counter’s is lost; the admin cannot price until the hold clears (12 minutes idle, or the counter leaves).'},
}
CONTEXT['P-4'] = 'The hold is per RO, not per line, and belongs to parts users. Today an admin who edits parts under a live hold is refused after the fact: the red toast below.'
GALLERY['P-4'] = [('Today — refused after the fact', OF.refused_toast(), '')]
OPT_VIS['P-5'] = {
 'A': {'frame': OF.note_row('icon'), 'why': 'A note mark sits by the part name, on screen without scrolling. Hover (desktop) or tap (phone) shows the note; no mark when there is none.'},
 'B': {'frame': OF.note_row('line'), 'why': 'The note prints as a second line under the part, always visible. Longer rows when notes are long; nothing to hover or tap.'},
}
CONTEXT['P-5'] = 'Your note: the admin needs to see the counter’s note on each part. With the parts page’s row (P-1), the Note cell is there but off the phone’s right edge until you scroll.'
# ----- W -----
GALLERY['W-1'] = [('Today — the same dialog on a recon-only RO', OF.send_gate_today(), ''),]
OPT_VIS['W-1'] = {
 'A': {'frame': OF.send_button_only(), 'why': 'Internal lines never feed the warning. A recon-only RO sends with no dialog; on a mixed RO the count covers customer-visible lines only.'},
 'B': {'frame': OF.send_gate_internal(), 'why': 'Internal lines stay counted, with words that are true for them: no customer, the store’s figures carry the $0 until priced.'},
}
CONTEXT['W-1'] = 'This is the parts counter’s Send to advisor button. The warning counts unpriced parts on every line, internal ones included, but talks about the customer.'
# ----- S -----
GALLERY['S-1'] = [('Today', OF.stage_strip('today'), ''), ('A — one-way after the link goes out', OF.stage_strip('A'), ''), ('B — stage rule, un-park never lands in Dispatched once sent', OF.stage_strip('B'), '')]
CONTEXT['S-1'] = 'What the tech’s Labor hours field allows, stage by stage. The RO already records when the customer link went out, so rule A has a fact to key off.'
OPT_VIS['S-1'] = {'A': {'why': 'Simple to explain: once the estimate has gone to the customer, a tech never edits hours again on that line — whatever stage the RO visits.'}, 'B': {'why': 'Keeps today’s stage-based rule and closes the hole at the un-park step only; a future stage or status could open a new hole.'}}
OPT_VIS['S-2'] = {'A': {'frame': OF.app(OF.hours_field(True, 'Hours lock once the estimate has gone to the customer'), bg="#f8fafc"), 'why': 'A real re-diagnosis goes through the advisor, who edits hours on the ledger and re-sends.'}, 'B': {'frame': OF.app(OF.hours_field(False, ''), bg="#f8fafc"), 'why': 'Un-parking re-opens the tech’s hours; the advisor is told to re-send the estimate (the re-ask notice under the field).'}}
# ----- SA-7b -----
CONTEXT['SA-7b-1'] = 'Your question: “a part waiting on the store” is a part the counter adds to an INTERNAL (store-pay) line after the advisor already authorized that line. The add withdraws the store’s OK, and the advisor approves or declines the part on the RO page, where it reads “Needs store OK” (below). The dashboard badge lumps those with parts waiting on a customer, so it can only say “Needs approval”.'
GALLERY['SA-7b-1'] = [('The situation — the advisor’s ledger on an internal line', OF.ledger_store_ok(), ''), ('Today — the dashboard badge', OF.dash_badge(['Needs approval']), '')]
OPT_VIS['SA-7b-1'] = {
 'A': {'frame': OF.dash_badge(['Needs customer OK','Needs store OK']), 'why': 'Each RO stores the two counts separately, so the badge can name the family — one badge per family when both apply.'},
 'B': {'frame': OF.dash_badge(['Needs customer OK']), 'why': 'One stored count, as today, labelled “Needs customer OK” again — wrong whenever only the store is waiting.'},
}
OPT_VIS['SA-7b-2'] = {'A': {'why': 'The dashboard uses the words the RO page already uses for the same part.'}, 'B': {'why': 'Say the wording below.'}}
# ----- D3 -----
GALLERY['D3-1'] = [('Today — filters on', OF.toolbar(False), ''), ('The fix', OF.toolbar(True), '')]
CONTEXT['D3-1'] = 'Desktop admin dashboard, all four filters on. Today the switch is the first thing to give up width, so “List” clips to “Li”. The fix keeps the switch whole and lets the filter boxes shrink first (they already show “…”).'
# ----- X -----
GALLERY['X-1'] = [('Today', OF.booked(), '')]
CONTEXT['X-1'] = 'The “+N TBD” row still exists in the cell, but it counts lines with no total — and since 8/27 every line has one, so it is always 0 and never shows.'
OPT_VIS['X-1'] = {'A': {'frame': OF.booked('+2 price gaps'), 'why': 'The same amber row, counting what the RO header counts: labor hours missing or 0, a part row blank or $0. One new number sent to the dashboard.'}, 'B': {'frame': OF.booked(), 'why': 'The cell stays as it looks today; the dashboard keeps showing no gaps while the RO page and parts page do.'}}
OPT_VIS['X-2'] = {'A': {'frame': OF.booked_hover(True), 'why': 'The existing Booked hover gains a “Price gaps” section: each line and what its gap is.'}, 'B': {'frame': OF.booked_hover(False), 'why': 'The hover stays as today; the count alone points to the RO page.'}}
# ----- D1 -----
OPT_VIS['D1-1'] = {'A': {'frame': OF.money_row('Total'), 'why': 'Every money row reads “Total”. Same number, same color, nothing else moves.'}, 'B': {'frame': OF.money_row('Total Booked'), 'why': 'Keep “Total Booked”.'}}
CONTEXT['D1-2'] = 'Checked in the code on 9/8: the customer’s page never uses “booked” anywhere — the word is staff-only. So this ruling changes nothing either way.'
# ----- SA-20b -----
CONTEXT['SA-20b-1'] = 'Re-open = after the customer has answered a line, the advisor can take it back: the customer’s decision is withdrawn, the line returns to pricing, and the customer is asked again once it is re-sent. The button lives on the advisor’s RO page, on a decided line (first frame). Checked in the code on 9/8: the recorded delivery state is not shown on any screen — every “In stock” / “Not in stock” chip is drawn from the Yes/No/? answer itself, and the parts queue only asks “pulled or not”. The single reader is the advisor’s re-open / start-over warning.'
GALLERY['SA-20b-1'] = [('Where re-open lives — the advisor’s RO page, on a decided line', OF.frozen_line_banner(), ''), ('The counter answers Yes while pricing', stock_answer_row(), ''), ('Today — the advisor re-opens the line later', OF.reopen_dialog(True), '')]
OPT_VIS['SA-20b-1'] = {'A': {'frame': OF.reopen_dialog(False), 'why': 'The answer is just an answer. The re-open dialog no longer says “already on order”, because nothing records an order any more.'}, 'B': {'frame': OF.reopen_dialog(True), 'why': 'Nothing changes; the “No” answer keeps standing in for “on order” in that one warning.'}, 'C': {'why': 'Revisit when an actual order step exists for the counter to take.'}}

TRIAGE_MOCK = {
 "Q": dict(html=parts_card_tall(), caption="Today — the parts counter, on one line with two parts: the card runs past the bottom of the phone (≈ 830 px), so the counter scrolls constantly."),
 "SA-20b": dict(html=stock_answer_row(), caption="Today — the parts counter answers “In stock? Yes” while pricing, and the part is recorded as in stock for delivery before anyone has pulled it. Proposed: the answer stays an answer; delivery is recorded when the counter pulls or orders."),
}
data_cards=[]
for c in cards:
    decs=[]
    for i,(q,opts) in enumerate(DEC[c['key']],1):
        did=f"{c['key']}-{i}"
        ov=OPT_VIS.get(did,{})
        bk = BAKED.get(did)
        decs.append(dict(id=did, n=i, q=q, options=[dict(l=l,t=t,rec=r, frame=ov.get(l,{}).get('frame'), why=ov.get(l,{}).get('why')) for l,t,r in opts], text=(len(opts)==0), context=CONTEXT.get(did), gallery=[dict(label=a,html=b,note=n) for a,b,n in GALLERY.get(did,[])], galleryWide=(did in GALLERY_WIDE), galleryFull=(did in GALLERY_FULL), baked=(dict(choice=bk[0], note=bk[1]) if bk else None)))
    fr=frames_for(c['key'])
    NO_BLOCKS = {'W','SA-7b','D3','X','D1','SA-20b','Q'}
    blocks=''.join(c['blocks']) if (fr['kind']=='none' and c['key'] not in NO_BLOCKS) else ''
    visual = any(d['gallery'] or any(o.get('frame') for o in d['options']) for d in decs)
    data_cards.append(dict(key=c['key'], section=c['section'], title=c['title'], sub=c['sub'], dims=c['dims'], pop=c['pop'], ruled=c['ruled'], blocks=blocks, frames=fr, decisions=decs, stage=STAGE.get(c['key'],'groomed'), triageMock=TRIAGE_MOCK.get(c['key']), visual=visual))

# ruled / queued items for the dashboard (from the live board)
ruled_items=[
 ("MPI & Video","OL","Dictation: “no leaks” leaves Oil and/or Fluid Leaks Pending — the one row whose all-clear is a negation","ruled 7 Sep"),
 ("MPI & Video","FC","Dictation: “All brake lights are good” puts four brake-pad rows on the review sheet and leaves the lights Pending","ruled 7 Sep"),
 ("MPI & Video","VG","Video: “All the belts look good” greens Drive Belts from a video, while the same words by dictation go through the new fixed list","ruled 7 Sep"),
 ("MPI & Video","UW","Dictation: the battery check stands down when the AI reader’s note uses a defect word it has never heard of","ruled 7 Sep"),
 ("MPI & Video","VR","Video review sheet: the copy Dave marked up on the 7 Sep sheet, and the split of matched and unmatched items into two steps","ruled 7–8 Sep"),
 ("MPI & Video","CT","Video: a “Couldn’t place” row can be titled “There is a rattle coming from” — a clipped fragment","ruled 8 Sep"),
 ("MPI & Video","SQ","Video: a stitched quote can refuse the tech’s own “brake pads” sentence","ruled 8 Sep"),
 ("MPI & Video","VC","Video cue cards: have the AI reader hand back the tech’s own sentences","ruled 7 Sep — back to the drawing board"),
 ("Store settings — labor rates & money","SA-19","Saving a new labor rate re-prices every open RO in the store — with no question asked","ruled 30 Aug"),
]

LEGACY=json.load(open(O+'/legacy_blocks.json')) if os.path.exists(O+'/legacy_blocks.json') else {}
DATA=dict(legacy={k: dict(title={'risk':'Risk grid','icebox':'Icebox','archive':'Archive'}[k], html=v) for k,v in LEGACY.items()}, sections=SECTION_ORDER, cards=data_cards, ruled=[dict(section=s,key=k,title=t,status=st) for s,k,t,st in ruled_items], icebox="Waiting on something specific", archive="Archive — 56 items shipped since the 29 Aug board", built=__import__("datetime").date.today().strftime("%-d %b %Y"))

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
.m-empty{font-size:14.5px}
.m-total{font-size:15.5px}
.m-status{font-size:13px}
/* ---------- clarifiers ---------- */
.m-ctx{font-size:15px;color:var(--ink-2);line-height:1.45}
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
