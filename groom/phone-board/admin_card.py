PKG = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#374151" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>'
PEN = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#374151" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"/></svg>'
HASH2 = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="position: absolute; left: 8px; top: 50%; transform: translateY(-50%);"><path d="M4 9h16M4 15h16M10 3 8 21M16 3l-2 18"/></svg>'

def _inp(text, w, extra="", ph=False, pad="0 10px", align="left"):
    col = "#9ca3af" if ph else "#0f172a"
    return f'<div style="position: relative; width: {w}px; height: 36px; border: 1px solid #e2e8f0; border-radius: 6px; background: #fff; display: flex; align-items: center; justify-content: {"flex-end" if align=="right" else "flex-start"}; padding: {pad}; font-size: 14px; color: {col}; white-space: nowrap; overflow: hidden; box-sizing: border-box; {extra}">{text}</div>'

def _stock(disabled=False):
    op = "opacity: .6;" if disabled else ""
    return f'<div style="display: inline-flex; width: 130px; height: 36px; border: 1px solid #e5e7eb; border-radius: 6px; overflow: hidden; background: #fff; {op}"><span style="flex: 1; display: grid; place-items: center; font-size: 13px; color: #4b5563; border-right: 1px solid #e5e7eb;">Yes</span><span style="flex: 1; display: grid; place-items: center; font-size: 13px; color: #4b5563; border-right: 1px solid #e5e7eb;">No</span><span style="flex: 1; display: grid; place-items: center; font-size: 13px; font-weight: 600; color: #fff; background: #64748b;">?</span></div>'

def _hdr(cols, widths):
    return '<div style="display: grid; grid-template-columns: ' + ' '.join(f'{w}px' for w in widths) + '; gap: 8px; align-items: end; padding-bottom: 6px; font-size: 10px; font-weight: 600; letter-spacing: .05em; text-transform: uppercase; color: #9ca3af;">' + ''.join(f'<span>{c}</span>' for c in cols) + '</div>'

def _row(cells, widths, ring=False):
    r = ' class="ring"' if ring else ''
    return f'<div{r} style="display: grid; grid-template-columns: ' + ' '.join(f'{w}px' for w in widths) + '; gap: 8px; align-items: center; padding: 2px;">' + ''.join(cells) + '</div>'

def _labor(edit=False):
    rate = f'<span style="font-size: 12px; color: #6b7280; white-space: nowrap;">hrs × </span>{sil(34, 10, "#cbd5e1")}<span style="font-size: 12px; color: #6b7280;">/hr</span>' if not edit else f'<span style="font-size: 12px; color: #6b7280; white-space: nowrap;">hrs ×</span>{_inp("$", 64, ph=True, pad="0 6px 0 8px")}<span style="font-size: 12px; color: #6b7280;">/hr</span><span style="font-size: 12px; color: #9ca3af;">this line</span>'
    return f'<div style="border-radius: 6px; border: 1px solid #e5e7eb; background: #fff; padding: 8px 12px; display: flex; align-items: center; gap: 8px; font-size: 14px; flex-wrap: wrap;"><span style="font-weight: 600; color: #1f2937;">Labor</span>{_inp("TBD", 64, ph=True, align="right")}{rate}<span style="margin-left: auto; min-width: 60px; text-align: right; font-size: 14px; font-weight: 600; color: #d1d5db;">—</span></div>'

def _entry_row():
    return f'<div style="border-top: 1px solid #f3f4f6; padding: 10px 0 2px; display: flex; flex-wrap: wrap; align-items: center; gap: 8px;">{_inp("Add a part…", 150, ph=True)}<span style="font-size: 11px; color: #9ca3af;">Qty</span>{_inp("", 48)}<div style="position: relative;">{HASH2}{_inp("", 96, pad="0 0 0 28px")}</div></div>'

def _footer_strips(state):
    total = '<span style="font-size: 14px; font-style: italic; font-weight: 500; color: #cbd5e1;">Pricing to follow</span>'
    return f"""
    <div style="display: flex; align-items: flex-start; gap: 8px; border-radius: 6px; border: 1px solid #e2e8f0; background: #f8fafc; padding: 8px 12px; font-size: 14px;"><span style="color: #4b5563;">Parts subtotal</span><span style="margin-left: auto; color: #9ca3af;">—</span></div>
    <div style="display: flex; align-items: center; gap: 8px; border-radius: 6px; background: #0f172a; padding: 10px 12px; font-size: 14px; color: #fff;"><span style="flex: 1; font-weight: 600;">Line total</span>{total}</div>"""

def _parts_total_footer(ring=False):
    r = ' class="ring"' if ring else ''
    return f"""<div{r} style="margin-top: 8px; padding: 4px 2px 2px; display: flex; flex-direction: column; gap: 4px; align-items: flex-end;">
      <div style="display: flex; align-items: center; gap: 10px;"><span style="font-size: 11px; font-weight: 600; letter-spacing: .05em; text-transform: uppercase; color: #6b7280;">Parts Total</span>{_inp("$&nbsp;&nbsp;0.00", 96, ph=True, align="right")}</div>
      <div style="display: flex; align-items: center; gap: 6px; font-size: 11px; white-space: nowrap;"><span style="font-weight: 600; color: #0f172a;">Sum of lines above</span><span style="color: #d1d5db;">|</span><span style="color: #9ca3af;">Manual total</span></div>
    </div>"""

def ADMIN_CARD(state):
    edit = state.endswith("edit")
    proposed = state.startswith("proposed")
    ctrl = '<span style="display: inline-flex; align-items: center; height: 28px; border-radius: 6px; background: #0f172a; color: #fff; padding: 0 12px; font-size: 12px; font-weight: 600;">Done</span>' if edit else f'<span style="display: inline-flex; align-items: center; gap: 4px; font-size: 12px; color: #374151;">{PEN}Edit pricing</span>'
    panel_style = "border: 1px solid #7dd3fc; box-shadow: 0 0 0 1px #bae6fd;" if edit else "border: 1px solid #e5e7eb;"
    if state == "today_locked":
        body = _entry_row(); count = ''
    elif state == "today_edit":
        W = [150, 120, 48, 130, 96]
        body = _hdr(["Part Name","Part #","Qty","In Stock?","Unit Price"], W) + _row([_inp("Fuel pump module", 150), '<div style="position: relative;">'+HASH2+_inp("RC-FP-002", 120, pad="0 0 0 28px")+'</div>', _inp("1", 48, pad="0", align="left", extra="justify-content: center;"), _stock(), _inp("$&nbsp;&nbsp;0.00", 96, ph=True, align="right")], W) + _entry_row(); count = '<span style="margin-left: 4px; font-size: 12px; font-weight: 400; color: #9ca3af;">1</span>'
    elif state == "proposed_locked":
        W = [120, 150, 130, 100, 48, 96]
        ro = "background: #f8fafc; border-color: #f1f5f9;"
        body = _hdr(["Part #","Part Name","In Stock?","Note","Qty","Unit Price"], W) + _row(['<div style="position: relative;">'+HASH2+_inp("RC-FP-002", 120, pad="0 0 0 28px", extra=ro)+'</div>', _inp("Fuel pump module", 150, extra=ro), _stock(disabled=True), _inp("+ Note", 100, ph=True, extra="border: 1px solid #cbd5e1; opacity: .6;"), _inp("1", 48, pad="0", extra="justify-content: center; "+ro), _inp("—", 96, ph=True, align="right", extra=ro)], W, ring=True); count = '<span style="margin-left: 4px; font-size: 12px; font-weight: 400; color: #9ca3af;">1</span>'
    else:  # proposed_edit
        W = [120, 150, 130, 100, 48, 96]
        body = _hdr(["Part #","Part Name","In Stock?","Note","Qty","Unit Price"], W) + _row(['<div style="position: relative;">'+HASH2+_inp("RC-FP-002", 120, pad="0 0 0 28px")+'</div>', _inp("Fuel pump module", 150), _stock(), _inp("+ Note", 100, ph=True, extra="border: 1px solid #cbd5e1;"), _inp("1", 48, pad="0", extra="justify-content: center;"), _inp("$&nbsp;&nbsp;0.00", 96, ph=True, align="right")], W) + _entry_row(); count = '<span style="margin-left: 4px; font-size: 12px; font-weight: 400; color: #9ca3af;">1</span>'
    return f"""
<div class="app" style="background: #fff; padding: 10px;">
  <div style="border-radius: 6px; border: 1px solid #9ca3af; background: #d1d5db; padding: 12px; display: flex; flex-direction: column; gap: 12px;">
    <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;"><span style="display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600; letter-spacing: .025em; text-transform: uppercase; color: #374151;">{PKG}Parts &amp; Labor</span>{ctrl}</div>
    {_labor(edit)}
    <div style="border-radius: 6px; background: #fff; padding: 12px; {panel_style}">
      <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 4px;"><span style="font-size: 14px; font-weight: 600; color: #1f2937;">Parts{count}</span>{'<span style="font-size: 11px; color: #0284c7;">scrolls →</span>' if state != "today_locked" else ''}</div>
      <div style="overflow: hidden; width: 100%;"><div style="width: 760px;">{body}</div></div>{_parts_total_footer(ring=True) if state == "proposed_edit" else ""}
    </div>
    {_footer_strips(state)}
  </div>
</div>"""
