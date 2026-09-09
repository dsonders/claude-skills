# One frame per option for the open decisions (Dave 9/8: "I need to see what those directions will look like").
# Every frame is drawn from the real component anatomy read on 9/8 (see the session's Explore reports).
from lib import sil
CHECK = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 5 5 9-10"/></svg>'
XI = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>'
TRI = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex:none"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4M12 17h.01"/></svg>'
PHONE = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M15.05 5A5 5 0 0 1 19 8.95M15.05 1A9 9 0 0 1 23 8.94m-1 7.98v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'
LOCK = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>'
UNLOCK = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/></svg>'

def app(inner, bg="#fff", pad="12px"):
    return f'<div class="app" style="background: {bg}; padding: {pad};">{inner}</div>'

# ---------- shadcn AlertDialog / Dialog at 351px (max-w-[90vw]) ----------
def dialog(title, desc, primary, secondary, primary_style="background:#2a9d8f;color:#fff;", icon=None, note=None):
    ic = icon or ''
    n = f'<div style="font-size: 12.5px; color: #64748b; margin-top: 8px;">{note}</div>' if note else ''
    return f"""
<div class="app" style="background: rgba(15,23,42,.55); padding: 14px 10px;">
  <div style="background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,.25); display: flex; flex-direction: column; gap: 8px;">
    <div style="display: flex; align-items: center; gap: 8px; font-size: 17px; font-weight: 600; line-height: 1.3; color: #0f172a;">{ic}<span>{title}</span></div>
    <div style="font-size: 14px; line-height: 1.45; color: #64748b;">{desc}</div>{n}
    <div style="display: flex; flex-direction: column-reverse; gap: 8px; margin-top: 8px;">
      <div style="min-height: 40px; border-radius: 6px; border: 1px solid #e2e8f0; display: grid; place-items: center; font-size: 14px; font-weight: 500; color: #0f172a;">{secondary}</div>
      <div style="min-height: 40px; border-radius: 6px; display: grid; place-items: center; font-size: 14px; font-weight: 600; {primary_style}">{primary}</div>
    </div>
  </div>
</div>"""

# ---------- P-4: a parts user holds the RO ----------
def parts_hold_banner(button=True, hint=None):
    btn = '<span style="display: inline-flex; align-items: center; height: 32px; padding: 0 12px; border-radius: 6px; border: 1px solid #e2e8f0; background: #fff; font-size: 13px; font-weight: 500; color: #0f172a;">Take over</span>' if button else ''
    h = f'<div style="font-size: 12.5px; color: #92400e; margin-top: 6px;">{hint}</div>' if hint else ''
    return app(f'<div style="border-radius: 6px; border: 1px solid #fcd34d; background: #fffbeb; padding: 12px;"><div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap;"><span style="display: inline-flex; align-items: center; gap: 6px; font-size: 14px; color: #92400e;"><i style="width: 6px; height: 6px; border-radius: 999px; background: #f59e0b; display: inline-block;"></i>{sil(58, 11, "#b45309")} is editing this RO now.</span>{btn}</div>{h}</div>')

def takeover_dialog():
    return dialog(f'{sil(58, 12, "#0f172a")} is editing this RO.', 'Take over? (Some of their edits may be lost)', 'Yes, Take Over', 'No', primary_style="background:#d97706;color:#fff;")

def refused_toast():
    return app('<div style="border-radius: 6px; border: 1px solid #fecaca; background: #fef2f2; padding: 12px 14px; display: flex; flex-direction: column; gap: 2px;"><div style="font-size: 14px; font-weight: 600; color: #7f1d1d;">Someone else took over this RO</div><div style="font-size: 13px; line-height: 1.4; color: #991b1b;">Your changes weren’t saved — a parts user is editing this RO right now. Try again in a moment.</div></div>', bg="#f8fafc")

# ---------- W-1: the Send-to-advisor gate ----------
def send_gate_today(n=2):
    return dialog('Some parts aren’t priced yet', f'{n} parts still need pricing. Those lines will be quoted to the customer with the unpriced parts counted as $0.00 — and the customer can approve them at that price.', 'Send anyway', 'Cancel', icon=TRI)
def send_gate_internal(n=2):
    return dialog('Some internal parts aren’t priced yet', f'{n} parts on internal lines still need pricing. They never reach a customer; the store’s figures count them as $0.00 until they are priced.', 'Send anyway', 'Cancel', icon=TRI)
def send_button_only():
    return app('<div style="display: flex; flex-direction: column; gap: 6px;"><div style="min-height: 44px; border-radius: 6px; background: #2563eb; color: #fff; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 15px; font-weight: 600;">Send to advisor</div><div style="font-size: 12px; color: #64748b; text-align: center;">Recon-only RO — no customer, so no warning: it just sends.</div></div>')

# ---------- S-1: where a tech can edit hours, stage by stage ----------
STAGES = [("Intake","Unassigned"),("In service","Dispatched"),("Parts pricing","Parts Pricing"),("Advisor review","Advisor Review"),("Awaiting customer","Sent to Customer"),("In fulfillment","Waiting for Parts"),("Ready","Ready for Pickup"),("Holding","(store’s own status)"),("Closed","Closed")]
# today per TECH_LABOR_HOURS_STAGE_POLICY; A = one-way after the customer link is sent; B = stage rule, un-park can't land in In service once sent
TODAY = ["undecided","open","open","locked","locked","undecided","undecided","locked","locked"]
def stage_strip(mode):
    rows=''
    for i,(st,label) in enumerate(STAGES):
        t = TODAY[i]
        if mode=='today': v=t; note=''
        elif mode=='A':
            v = t if i<4 else ('locked' if t!='locked' else 'locked'); note=''
            if i in (1,2): note='until the link goes out'
            if i==1: v='open'
        else:
            v=t; note=''
        glyph = {'open':UNLOCK,'undecided':UNLOCK,'locked':LOCK}[v]
        col = {'open':'#047857','undecided':'#b45309','locked':'#64748b'}[v]
        txt = {'open':'editable','undecided':'editable while undecided','locked':'locked'}[v]
        if mode=='A' and i>=3: txt='locked once the link went out'; col='#64748b'; glyph=LOCK
        if mode=='A' and i in (1,2): txt='editable until the link goes out'; col='#047857'
        if mode=='B' and i==1: txt='editable — but un-park lands here only if no link was sent'; col='#047857'
        if mode=='B' and i==7: txt='locked · un-park goes back to Awaiting customer'; col='#64748b'
        rows += f'<div style="display: grid; grid-template-columns: 118px 1fr; gap: 8px; align-items: center; padding: 6px 0; border-top: 1px solid #f1f5f9;"><div><div style="font-size: 12.5px; font-weight: 600; color: #0f172a;">{st}</div><div style="font-size: 10.5px; color: #94a3b8;">{label}</div></div><div style="display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: {col};">{glyph}<span>{txt}</span></div></div>'
    hole = '<div style="margin-top: 8px; border-radius: 6px; border: 1px dashed #fca5a5; background: #fef2f2; padding: 8px 10px; font-size: 12px; color: #991b1b; line-height: 1.4;">The hole: Sent to Customer → park in Holding → un-park into Dispatched = hours open again under an estimate the customer already has.</div>' if mode=='today' else ''
    return app(f'<div style="border-radius: 8px; border: 1px solid #e2e8f0; background: #fff; padding: 4px 12px 8px;">{rows}</div>{hole}', bg="#f8fafc", pad="10px")

def hours_field(locked, hint):
    op = 'opacity: .5;' if locked else ''
    h = f'<div style="font-size: 12px; color: #64748b; width: 100%;">{hint}</div>' if hint else ''
    return f'<div style="border-radius: 6px; border: 1px solid #e2e8f0; background: #f1f5f9; padding: 12px; display: flex; flex-direction: column; gap: 8px; font-size: 14px;"><div style="display: flex; align-items: center; gap: 6px; font-weight: 600; color: #1f2937; min-height: 24px;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>Labor hours</div><div style="display: flex; align-items: center; gap: 8px; min-height: 44px;"><div style="width: 84px; height: 44px; border: 1px solid #e2e8f0; border-radius: 6px; background: #fff; display: flex; align-items: center; justify-content: flex-end; padding: 0 12px; font-size: 14px; color: #0f172a; {op}">1.5</div><span style="font-size: 12px; color: #6b7280;">hrs</span></div>{h}</div>'

# ---------- SA-7b: the dashboard RO cell badge + the ledger pill ----------
def ro_cell(badges):
    b = ''.join(f'<span style="display: inline-flex; align-items: center; gap: 2px; border-radius: 999px; border: 1px solid #fcd34d; background: #fef3c7; color: #92400e; font-size: 10px; font-weight: 600; letter-spacing: .05em; text-transform: uppercase; padding: 2px 6px; margin-top: 4px; white-space: nowrap;">{PHONE}{t}</span>' for t in badges)
    return f'<div style="display: flex; gap: 10px; align-items: stretch; border-radius: 8px; border: 1px solid #e2e8f0; background: #fff; padding: 8px 6px;"><div style="width: 118px; padding: 0 6px; display: flex; flex-direction: column; align-items: flex-start;"><span style="display: inline-flex; align-items: center; height: 22px; padding: 0 8px; border-radius: 6px; border: 1px solid #e2e8f0; background: #f8fafc; font-family: ui-monospace, Menlo, monospace; font-size: 12px; font-weight: 600; color: #1d4ed8;">{sil(44, 10, "#93c5fd")}</span>{b}</div><div style="flex: 1; min-width: 0; padding: 0 6px; display: flex; flex-direction: column; justify-content: center; gap: 4px;">{sil(120, 11, "#0f172a")}{sil(90, 9, "#94a3b8")}</div></div>'
def dash_badge(badges):
    return app(ro_cell(badges), bg="#f8fafc", pad="10px")
def ledger_store_ok():
    return app(f'<div style="border-radius: 6px; border: 1px solid #e5e7eb; background: #fff; padding: 12px;"><div style="font-size: 14px; font-weight: 600; color: #1f2937; margin-bottom: 8px;">Parts <span style="font-size: 12px; font-weight: 400; color: #9ca3af;">1</span></div><div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;"><span style="font-size: 14px; font-weight: 600; color: #0f172a;">{sil(96, 11, "#0f172a")}</span><span style="font-size: 12px; font-family: ui-monospace, Menlo, monospace; color: #9ca3af;"># {sil(48, 9)}</span><span style="display: inline-flex; align-items: center; border-radius: 999px; background: #fef3c7; color: #b45309; font-size: 10.5px; font-weight: 600; padding: 2px 8px;">Needs store OK</span><span style="margin-left: auto; font-family: ui-monospace, Menlo, monospace; font-size: 13px; font-weight: 600; color: #0f172a;">{sil(40, 10, "#0f172a")}</span></div><div style="display: flex; gap: 8px; margin-top: 8px;"><span style="flex: 1; min-height: 36px; border-radius: 6px; background: #0f172a; color: #fff; display: grid; place-items: center; font-size: 13px; font-weight: 600;">Approve part</span><span style="flex: 1; min-height: 36px; border-radius: 6px; border: 1px solid #e2e8f0; display: grid; place-items: center; font-size: 13px; font-weight: 500; color: #0f172a;">Decline part</span></div></div>', bg="#d1d5db")

# ---------- D3: the admin toolbar, filters on ----------
def toolbar(fixed):
    sel = lambda t,w: f'<span style="display: inline-flex; align-items: center; justify-content: space-between; height: 36px; width: {w}px; flex: 0 1 {w}px; min-width: {"96px" if fixed else "0"}; border: 1px solid #e1e7ef; border-radius: 6px; background: #fff; padding: 0 10px; font-size: 13px; color: #0f172a; white-space: nowrap; overflow: hidden;"><span style="overflow: hidden; text-overflow: ellipsis;">{t}</span><span style="opacity: .5; margin-left: 6px;">⌄</span></span>'
    toggle = f'<span style="display: inline-flex; height: 36px; border: 1px solid #e2e8f0; border-radius: 6px; overflow: hidden; font-size: 14px; {"flex: none;" if fixed else "flex: 0 1 auto; min-width: 0;"}"><span style="padding: 0 12px; display: grid; place-items: center; background: #64748b; color: #fff; white-space: nowrap;">Pipeline</span><span style="padding: 0 12px; display: grid; place-items: center; background: #fff; color: #475569; white-space: nowrap; {"" if fixed else "width: 22px; padding: 0 0 0 12px; overflow: hidden;"}">{"List" if fixed else "Li"}</span></span>'
    inner = f'<div style="display: flex; align-items: center; gap: 8px; width: 900px; padding: 8px; background: #fff; border-radius: 8px; border: 1px solid #e2e8f0;"><span style="flex: 1 1 {"160px" if fixed else "200px"}; min-width: {"160px" if fixed else "200px"}; max-width: 400px; height: 36px; border: 1px solid #e1e7ef; border-radius: 6px; background: #fff; display: flex; align-items: center; padding: 0 10px; font-size: 13px; color: #94a3b8;">Search RO, customer, vehicle…</span>{sel("Parts Pricing",140)}{sel("All Techs",140)}{sel("Derek Jozwiak",140)}{sel("At risk",140)}<span style="display: inline-flex; align-items: center; gap: 4px; height: 36px; padding: 0 10px; font-size: 13px; color: #64748b; flex: none;">{XI}Clear</span><span style="margin-left: auto; display: inline-flex; align-items: center; gap: 8px; {"flex: none;" if fixed else "min-width: 0;"}">{toggle}<span style="display: inline-flex; align-items: center; gap: 6px; height: 36px; padding: 0 12px; border-radius: 6px; background: #2a9d8f; color: #fff; font-size: 14px; font-weight: 500; white-space: nowrap; flex: none;">+ New RO ⌄</span></span></div>'
    # crop to the right-hand end of the toolbar (the last filter, Clear, the switch, New RO) at 70%
    return f'<div class="app" style="background: #f1f5f9; padding: 10px; overflow: hidden;"><div style="position: relative; height: 44px; overflow: hidden; border-radius: 6px;"><div style="position: absolute; left: -304px; top: 0; width: 900px; transform: scale(.7); transform-origin: top left;">{inner}</div></div><div style="font-size: 11px; color: #94a3b8; margin-top: 6px;">← the right end of the toolbar, filters on</div></div>'

# ---------- X: the Booked cell ----------
def booked_cell(extra=None):
    ex = f'<div style="display: flex; justify-content: flex-end;"><span style="font-size: 9px; font-weight: 500; letter-spacing: .05em; text-transform: uppercase; color: #b45309;">{extra}</span></div>' if extra else ''
    return f'<div style="width: 132px; border: 1px solid #e2e8f0; border-radius: 4px; padding: 6px; background: #fff; display: flex; flex-direction: column; gap: 2px; font-variant-numeric: tabular-nums; line-height: 1.2;"><div style="display: flex; justify-content: space-between; align-items: baseline;"><span style="font-size: 9px; font-weight: 700; letter-spacing: .05em; text-transform: uppercase; color: #0f172a;">Booked</span><span style="font-family: ui-monospace, Menlo, monospace; font-size: 12px; font-weight: 700; color: #0f172a;">$1,240</span></div>{ex}<div style="border-top: 1px solid #e2e8f0; margin: 2px 0;"></div><div style="display: flex; justify-content: space-between;"><span style="font-size: 9px; letter-spacing: .05em; text-transform: uppercase; color: #1d4ed8;">CP apr</span><span style="font-family: ui-monospace, Menlo, monospace; font-size: 11px; color: #1d4ed8;">$1,240</span></div><div style="display: flex; justify-content: space-between;"><span style="font-size: 9px; letter-spacing: .05em; text-transform: uppercase; color: #94a3b8;">Warr / Rec</span><span style="font-family: ui-monospace, Menlo, monospace; font-size: 11px; color: #94a3b8;">$0</span></div></div>'
def booked(extra=None):
    return app(f'<div style="display: flex; justify-content: center; transform: scale(1.35); transform-origin: top center; height: 96px;">{booked_cell(extra)}</div>', bg="#f8fafc", pad="12px 12px 44px")
def booked_hover(with_gaps):
    rows = [("Approved","#16a34a","3 lines · $1,240"),("Declined","#94a3b8","1 line · $180"),("Awaiting approval","#f59e0b","—"),("Not priced","#e2e8f0","2 lines")]
    body=''.join(f'<div style="display: flex; justify-content: space-between; align-items: center; gap: 8px; padding: 3px 0; border-top: 1px solid #f1f5f9; font-size: 12.5px;"><span style="display: inline-flex; align-items: center; gap: 6px; color: #475569;"><i style="width: 10px; height: 10px; border-radius: 2px; background: {c}; display: inline-block;"></i>{l}</span><span style="font-family: ui-monospace, Menlo, monospace; font-weight: 600; color: #0f172a;">{v}</span></div>' for l,c,v in rows)
    gaps = ''
    if with_gaps:
        gaps = f'<div style="margin-top: 8px; font-size: 10.5px; font-weight: 600; letter-spacing: .05em; text-transform: uppercase; color: #b45309;">Price gaps · 2 lines</div>' + ''.join(f'<div style="display: flex; justify-content: space-between; gap: 8px; padding: 3px 0; border-top: 1px solid #f1f5f9; font-size: 12.5px; color: #475569;"><span>{sil(w, 9)}</span><span style="font-size: 11px; color: #b45309;">{why}</span></div>' for w,why in [(96,'Labor hours missing'),(70,'A part row is $0')])
    return app(f'<div style="width: 256px; margin: 0 auto; border-radius: 8px; border: 1px solid #e2e8f0; background: #fff; box-shadow: 0 10px 30px rgba(0,0,0,.15); padding: 12px 14px; color: #0f172a;"><div style="font-size: 10.5px; font-weight: 600; letter-spacing: .05em; text-transform: uppercase; color: #64748b;">Booked · 6 lines</div><div style="margin-top: 6px; font-family: ui-monospace, Menlo, monospace; font-size: 18px; font-weight: 600; color: #1e40af; line-height: 1;">$1,420 <span style="font-family: inherit; font-size: 12px; font-weight: 400; color: #60a5fa;">estimated</span></div><div style="margin-top: 8px;">{body}</div>{gaps}</div>', bg="#f8fafc")

# ---------- D1: the RO header money row ----------
def money_row(label):
    return f'<div class="app" style="background: #0f172a; padding: 12px 14px; border-top: 1px solid #33415a; display: flex; align-items: flex-end; gap: 22px;"><div><div style="font-size: 10px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: #94a3b8;">{label}</div><div style="font-size: 21px; font-weight: 700; color: #4ade80; font-variant-numeric: tabular-nums; line-height: 1.1;">$4,120</div></div><div><div style="font-size: 10px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: #94a3b8;">CP approved</div><div style="font-size: 15px; font-weight: 600; color: #e2e8f0; font-variant-numeric: tabular-nums;">$3,940</div></div><div style="margin-left: auto; font-size: 12px; font-weight: 700; color: #fbbf24; white-space: nowrap;">2 Price Gaps</div></div>'

# ---------- SA-20b: the advisor's re-open warning ----------
def reopen_dialog(with_warning):
    desc = 'The customer’s approval is withdrawn and the line goes back to pricing.' + (' <b style="color:#0f172a;">2 parts are already on order.</b>' if with_warning else '')
    return dialog('Re-open this line?', desc, 'Re-open line', 'Cancel', icon=TRI)
