import os, json
D=os.path.dirname(os.path.abspath(__file__))

CSS = """
    :root{--bg:#eef2f7;--surface:#ffffff;--surface-2:#f6f9fc;--surface-3:#e8eef6;--ink:#0d1826;--ink-2:#33445a;--muted:#64768c;--line:#d1dce8;--line-2:#e3eaf3;--accent:#0284c7;--accent-soft:#e0f2fe;--teal:#0d7d72;--teal-soft:#d3f5ef;--amber:#a15c07;--amber-soft:#fdf0d5;--danger:#c62828;--radius:5px}
    body{margin:0;font-family:"IBM Plex Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:15px;line-height:1.5;color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased}
    a{color:var(--accent)} a:hover{color:#0369a1}
    .cap{font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
    .key{display:inline-grid;place-items:center;min-width:26px;height:24px;padding:0 6px;border-radius:3px;background:var(--ink);color:var(--surface);font-family:"IBM Plex Mono",ui-monospace,monospace;font-weight:600;font-size:12px;flex:none}
    .rec{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--teal);background:var(--surface);border:1px solid var(--teal);border-radius:999px;padding:0 6px;white-space:nowrap;flex:none;line-height:18px;margin-left:auto}
    .btn{display:flex;align-items:center;gap:10px;min-height:48px;padding:10px 14px;border-radius:var(--radius);border:1px solid var(--line);background:var(--surface);font-size:14.5px;line-height:1.35;color:var(--ink)}
    .btn .opt{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11.5px;font-weight:600;color:var(--accent);border:1px solid var(--accent);border-radius:3px;padding:1px 6px;background:var(--accent-soft);flex:none}
    .btn.pick{border-color:var(--teal);background:var(--teal-soft)}
    .btn.pick .opt{color:var(--teal);border-color:var(--teal);background:var(--surface)}
    .field{min-height:48px;border:1px dashed var(--line);border-radius:var(--radius);background:var(--surface-2);padding:12px 14px;font-size:14px;color:var(--muted)}
    .frame{border:1px solid var(--line);border-radius:6px;overflow:hidden;background:#fff}
    .seg{display:flex;border:1px solid var(--line);border-radius:999px;padding:3px;background:var(--surface);font-size:13px;font-weight:500}
    .seg span{flex:1;text-align:center;padding:7px 0;border-radius:999px;color:var(--muted);min-height:34px}
    .seg span.on{background:var(--ink);color:#fff}
    /* ---- app screens: literal light colours, the app's system sans ---- */
    .app{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#0f172a;line-height:1.35}
    .sil{display:inline-block;height:10px;border-radius:3px;background:#cbd5e1;vertical-align:middle}
    .ring{box-shadow:0 0 0 3px rgba(56,189,248,.45);border-radius:3px}
"""
BACK = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 6-6 6 6 6"/></svg>'
NEXT = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 6 6 6-6 6"/></svg>'
DOWN = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>'
XI = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="flex: none;"><path d="M18 6 6 18M6 6l12 12"/></svg>'
CHECK = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 5 5 9-10"/></svg>'
LOCK = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>'
TREND = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="flex: none; margin-top: 1px;"><path d="m22 17-8.5-8.5-5 5L2 7"/><path d="M16 17h6v-6"/></svg>'
CHEV_SM = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>'

def sil(w, h=10, c="#cbd5e1"):
    return f'<span class="sil" style="width: {w}px; height: {h}px; background: {c};"></span>'

# ---- RO page line panel (advisor, phone): dark plate → tab strip → line banner → 3Cs ----
def ro_panel(sub_text, ring=False):
    ringcls = ' ring' if ring else ''
    return f"""
<div class="app" style="background: #f8fafc;">
  <div style="padding: 9px 12px 10px; border-top: 2px solid #2563eb; background: linear-gradient(160deg, #0f172a 0%, #16202f 46%, #1e293b 100%); display: flex; flex-direction: column; gap: 6px;">
    <div style="display: flex; align-items: center; gap: 8px;">{sil(132, 12, '#e2e8f0')}<span style="margin-left: auto; width: 22px; height: 22px; border-radius: 6px; border: 1px solid #3f4d61; background: #1b2635;"></span></div>
    <div style="display: flex; align-items: center; gap: 8px;">{sil(64, 9, '#94a3b8')}</div>
  </div>
  <div style="background: #f1f5f9; border-bottom: 3px solid #38bdf8; padding: 8px 0 0 10px; display: flex; align-items: flex-end; gap: 5px; overflow: hidden;">
    <div style="display: flex; flex-direction: column; align-items: flex-start; gap: 0;"><span style="font-size: 10px; font-weight: 700; letter-spacing: .09em; color: #94a3b8; padding: 0 3px 4px;">CP</span><span style="display: inline-flex; align-items: center; min-height: 32px; padding: 6px 11px; border-radius: 8px 8px 0 0; margin-bottom: 3px; background: #fff; border: 2px solid #1e293b; border-bottom: 0;">{sil(52)}</span></div>
    <div style="display: flex; flex-direction: column; align-items: flex-start; gap: 0;"><span style="font-size: 10px; font-weight: 700; letter-spacing: .09em; color: #94a3b8; padding: 0 3px 4px;">CP</span><span style="display: inline-flex; align-items: center; min-height: 32px; padding: 6px 11px; border-radius: 8px 8px 0 0; margin-bottom: 3px; background: #f1f5f9; border: 1px solid #e2e8f0; border-bottom: 0; position: relative;">{sil(66, 10, '#cbd5e1')}<span style="position: absolute; left: 9px; right: 9px; top: 50%; height: 1.5px; background: #94a3b8;"></span></span></div>
    <div style="display: flex; flex-direction: column; align-items: flex-start; gap: 0;"><span style="font-size: 10px; font-weight: 700; letter-spacing: .09em; color: #94a3b8; padding: 0 3px 4px;">Warranty</span><span style="display: inline-flex; align-items: center; min-height: 32px; padding: 6px 11px; border-radius: 8px 8px 0 0; margin-bottom: 3px; background: #fff; border: 1px dashed #cbd5e1; border-bottom: 0;">{sil(44)}</span></div>
  </div>
  <div style="display: flex; align-items: center; gap: 10px; min-height: 62px; padding: 9px 10px 9px 11px; background: #fff; border-left: 4px solid #cbd5e1; border-bottom: 1px solid #f1f5f9; box-sizing: border-box;">
    {XI}
    <div style="display: flex; flex-direction: column; gap: 2px; min-width: 0;">
      <div style="font-size: 15px; font-weight: 700; letter-spacing: -.01em; color: #64748b; white-space: nowrap;">Declined</div>
      <div style="font-size: 12px; line-height: 1.35; color: #64748b;"><span class="{ringcls.strip()}" style="padding: 0 2px;">{sub_text}</span></div>
    </div>
  </div>
  <div style="padding: 10px;">
    <div style="border: 1px solid #e2e8f0; border-radius: 8px; background: #fff; padding: 10px 12px; display: flex; flex-direction: column; gap: 8px;">
      <div style="font-size: 11px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: #64748b;">Complaint</div><div>{sil(210)}</div>
      <div style="font-size: 11px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: #64748b;">Cause</div><div>{sil(160)}</div>
    </div>
  </div>
</div>"""

# ---- Customer's own page (phone): header → Your decisions ----
def owner_page(note=None):
    n = f"""<div style="display: flex; align-items: flex-start; gap: 8px; padding: 0 16px 10px 46px; font-size: 12px; line-height: 1.4; color: #047857;"><span class="ring" style="display: flex; gap: 6px; align-items: flex-start; padding: 2px 4px;">{TREND}<span>Your price for RF WHEEL BENT came down $200 — nothing you need to do.</span></span></div>""" if note else ''
    return f"""
<div class="app" style="background: #f9fafb;">
  <div style="background: #fff; box-shadow: 0 1px 2px rgba(0,0,0,.05); padding: 14px 16px;">
    <div style="display: flex; align-items: center; gap: 10px; min-height: 40px;"><span style="width: 40px; height: 32px; border-radius: 4px; background: #e5e7eb;"></span>{sil(120, 12, '#9ca3af')}</div>
    <div style="margin-top: 8px; display: flex; align-items: center; gap: 6px;"><span style="width: 14px; height: 14px; border-radius: 3px; border: 2px solid #94a3b8; box-sizing: border-box;"></span>{sil(96, 10, '#93c5fd')}</div>
    <div style="margin-top: 10px; border-top: 1px solid #f3f4f6; padding-top: 10px; display: flex; flex-direction: column; gap: 6px;">{sil(150, 12, '#9ca3af')}{sil(70, 9, '#d1d5db')}</div>
  </div>
  <div style="padding: 16px;">
    <div style="border-radius: 16px; background: #fff; box-shadow: 0 2px 8px rgba(15,23,42,.08); overflow: hidden;">
      <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding: 12px 16px; font-size: 16px; font-weight: 800; color: #0f172a;"><span>🛒 Your decisions</span><span style="font-size: 12px; font-weight: 700; color: #64748b; display: inline-flex; align-items: center; gap: 4px;">{sil(14, 9)} of {sil(14, 9)} decided</span></div>
      <div style="display: flex; align-items: center; gap: 10px; min-height: 44px; padding: 10px 16px; background: #fff;">
        <span style="width: 22px; height: 22px; border-radius: 999px; background: #16a34a; display: inline-grid; place-items: center; flex: none;">{CHECK}</span>
        <span style="flex: 1; font-size: 13px; font-weight: 600; color: #0f172a;">RF WHEEL BENT</span>
        {sil(44, 11, '#334155')}
        {LOCK}
      </div>
      {n}
      <div style="display: flex; align-items: center; gap: 10px; min-height: 44px; padding: 10px 16px; border-top: 1px solid #f8fafc;">
        <span style="width: 22px; height: 22px; border-radius: 999px; background: #16a34a; display: inline-grid; place-items: center; flex: none;">{CHECK}</span>
        {sil(120, 11, '#0f172a')}<span style="flex: 1;"></span>{sil(38, 11, '#334155')}{LOCK}
      </div>
      <div style="display: flex; align-items: center; justify-content: space-between; border-top: 1px solid #f1f5f9; background: #f8fafc; padding: 12px 16px; font-size: 17px; font-weight: 800; color: #0f172a;"><span>Approved total</span>{sil(56, 13, '#0f172a')}</div>
    </div>
  </div>
</div>"""

def page(body, w=390, h=844):
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
  <style>{CSS}</style>
</helmet>
<div style="width: {w}px; min-height: {h}px; background: var(--bg); display: flex; flex-direction: column; box-sizing: border-box;">
{body}
</div>
</x-dc>
</body>
</html>"""

def top(key, title, sub, pos):
    return f"""
<div style="padding: 54px 16px 0; display: flex; align-items: center; justify-content: space-between;">
  <div style="display: flex; align-items: center; gap: 4px; color: var(--accent); font-size: 14px; min-height: 44px;">{BACK}<span>Board</span></div>
  <div class="cap">{pos}</div>
</div>
<div style="padding: 4px 16px 0; display: flex; flex-direction: column; gap: 6px;">
  <div style="display: flex; gap: 10px; align-items: flex-start;"><span class="key">{key}</span><div style="font-size: 17px; font-weight: 600; line-height: 1.3; letter-spacing: -.01em;">{title}</div></div>
  <div style="font-size: 13.5px; color: var(--ink-2); line-height: 1.45;">{sub}</div>
</div>"""

def decision(idn, q, opts, words=True):
    RECCHIP = '<span class="rec">rec</span>'
    b = "".join(f'<div class="btn{" pick" if r else ""}"><span class="opt">{l}</span><span>{t}</span>{RECCHIP if r else ""}</div>' for l,t,r in opts)
    f = '<div class="field">In your words — optional, filed verbatim</div>' if words else ''
    return f"""
<div style="padding: 16px 16px 0; display: flex; flex-direction: column; gap: 8px;">
  <div class="cap">Decision {idn}</div>
  <div style="font-size: 15px; font-weight: 600; line-height: 1.4;">{q}</div>
  {b}{f}
</div>"""

def foot(details, nxt):
    return f"""
<div style="margin-top: auto; padding: 14px 16px 24px; display: flex; align-items: center; justify-content: space-between; gap: 10px;">
  <div style="display: flex; align-items: center; gap: 8px; color: var(--muted); font-size: 12.5px; min-height: 44px;">{DOWN}<span>{details}</span></div>
  <div style="display: flex; align-items: center; gap: 4px; color: var(--accent); font-size: 14px; font-weight: 500; white-space: nowrap;">Next: {nxt} {NEXT}</div>
</div>"""

SA6_TITLE = "A line the close auto-declined reads “Declined by the customer”"
SA6_SUB = "Closing an RO settles every unanswered line as declined — and the line’s banner then borrows the customer’s name for it."
SA6_D1 = decision("SA-6b · 1", "Label it “Declined at close”, read from the RO’s own closed-without-a-response mark?", [("A","Yes — “Declined at close”",True),("B","No — keep “Declined by the customer”",False)])
SA6_D2 = decision("SA-6b · 2", "Dashboards and money bands keep counting it as declined — only the banner names the reason?", [("A","Yes",True),("B","No — count it separately",False)], words=False)
SA6_FOOT = foot("Details — Size S · code only · any RO closed with a line unanswered", "W")

def framed(cap, inner):
    return f'<div style="display: flex; flex-direction: column; gap: 6px;"><div class="cap">{cap}</div><div class="frame">{inner}</div></div>'

# ---- Direction: Flip (one frame, Today | Proposed) ----
FLIP = top("SA-6b", SA6_TITLE, SA6_SUB, "4 of 38") + f"""
<div style="padding: 14px 16px 0; display: flex; flex-direction: column; gap: 10px;">
  <div class="seg"><span>Today</span><span class="on">Proposed</span></div>
  <div class="frame">{ro_panel("Declined at close", ring=True)}</div>
  <div style="font-size: 12.5px; color: var(--muted); line-height: 1.45;">The advisor, opening the line after close. Flip to Today to see “Declined by the customer”.</div>
</div>""" + SA6_D1 + SA6_D2 + SA6_FOOT

# ---- Direction: Stack (today over proposed) — Main ----
STACK = top("SA-6b", SA6_TITLE, SA6_SUB, "4 of 38") + f"""
<div style="padding: 14px 16px 0; display: flex; flex-direction: column; gap: 14px;">
  {framed("Today — the advisor opens the line after close", ro_panel("Declined by the customer"))}
  {framed("Proposed", ro_panel("Declined at close", ring=True))}
</div>""" + SA6_D1 + SA6_D2 + SA6_FOOT

# ---- Direction: Walkthrough (the story, each step a screen where there is one) ----
def step(n, who, text, inner=None, last=False):
    scr = f'<div class="frame" style="margin-top: 8px;">{inner}</div>' if inner else ''
    line = '' if last else '<div style="position: absolute; left: 11px; top: 26px; bottom: -14px; width: 2px; background: var(--line);"></div>'
    return f"""
<div style="position: relative; padding-left: 36px;">
  {line}
  <div style="position: absolute; left: 0; top: 0; width: 24px; height: 24px; border-radius: 999px; border: 1.5px solid var(--ink); display: grid; place-items: center; font-family: 'IBM Plex Mono', monospace; font-size: 11px; font-weight: 600; background: var(--surface);">{n}</div>
  <div style="font-size: 13.5px; line-height: 1.45; color: var(--ink-2); min-height: 24px; display: flex; align-items: center;"><span><b style="color: var(--ink); font-weight: 600;">{who}</b> {text}</span></div>
  {scr}
</div>"""

deck_card = f"""
<div class="app" style="background: #f9fafb; padding: 14px;">
  <div style="width: 100%; border-radius: 20px; background: #fff; box-shadow: 0 2px 8px rgba(15,23,42,.08); padding: 12px; box-sizing: border-box; display: flex; flex-direction: column; gap: 8px;">
    <div style="height: 110px; border-radius: 14px; background: #e5e7eb;"></div>
    <div style="font-size: 19px; font-weight: 700; line-height: 1.2; color: #0f172a;">{sil(150, 14, '#0f172a')}</div>
    <div>{sil(230, 9, '#94a3b8')}</div>
    <div style="display: flex; align-items: baseline; gap: 6px;">{sil(64, 18, '#0f172a')}<span style="font-size: 13px; font-weight: 500; color: #94a3b8;">parts + labor</span></div>
  </div>
</div>"""

WALK = top("SA-6b", SA6_TITLE, SA6_SUB, "4 of 38") + f"""
<div style="padding: 16px 16px 0; display: flex; flex-direction: column; gap: 14px;">
  {step(1, "The customer,", "on their own page, never answers this one line.", deck_card)}
  {step(2, "The advisor", "closes the RO. The line is settled as declined at close.")}
  {step(3, "The advisor,", "opening the line later — today:", ro_panel("Declined by the customer"))}
  {step(4, "Proposed:", "the banner names what actually happened.", ro_panel("Declined at close", ring=True), last=True)}
</div>""" + SA6_D1 + SA6_D2 + SA6_FOOT

# ---- Stack applied to U (customer page) ----
U = top("U", "Tell the customer when their agreed price went DOWN", "Staff get a notice when a price drops after approval; the customer’s page just quietly shows the lower number.", "12 of 38") + f"""
<div style="padding: 14px 16px 0; display: flex; flex-direction: column; gap: 14px;">
  {framed("Today — the customer, back on their page after the drop", owner_page())}
  {framed("Proposed — inline, the amount only", owner_page(note=True))}
</div>""" + decision("U · 1", "Inline under the line, or a banner at the top of the page?", [("A","Inline under the line",True),("B","A banner at the top",False)]) \
  + decision("U · 2", "Show the old price, or only the amount it came down?", [("A","The amount only",True),("B","Old price and new price",False)], words=False) \
  + decision("U · 3", "Every visit, or once?", [("A","Once",False),("B","Every visit",False)], words=False) \
  + foot("Details — Size S–M · customer-facing, you review", "T")

# ---- An item with no screen change ----
T = top("T", "Remember the labor rate each line was agreed at", "A line stores its agreed total but not the rate behind it, so every part of the app that touches money has to special-case “never re-figure a frozen line” — five places already.", "13 of 38") + f"""
<div style="padding: 14px 16px 0;">
  <div style="border: 1px dashed var(--line); border-radius: var(--radius); padding: 12px 14px; font-size: 13.5px; color: var(--muted); line-height: 1.45;">No screen changes — nothing to draw. What the app shows stays the same; what it stores changes.</div>
</div>""" + decision("T · 1", "Store the rate only, or the whole agreed snapshot (rate, hours, parts)?", [("A","The rate only",False),("B","The whole snapshot",False)]) \
  + decision("T · 2", "Old approved lines: work the rate back from the stored total, or leave them on the total?", [("A","Work it back",False),("B","Leave them on the total",False)], words=False) \
  + foot("Details — Size L · touches data · every approved line", "Y2")

