# One basic app-UI mockup per not-yet-groomed item (Dave 9/8: the groom-or-not call must be fast; visual beats text).
from lib import sil
HASH = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="position: absolute; left: 8px; top: 50%; transform: translateY(-50%);"><path d="M4 9h16M4 15h16M10 3 8 21M16 3l-2 18"/></svg>'
PLUS = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12h14"/></svg>'

def _tile(label, lines):
    body = ''.join(f'<div style="margin-top: 4px;">{sil(w)}</div>' for w in lines) if lines else '<div style="margin-top: 4px; font-size: 12px; font-style: italic; color: #94a3b8;">—</div>'
    return f'<div style="border-radius: 8px; border: 1px solid #e2e8f0; background: #fff; padding: 8px 10px;"><div style="font-size: 11px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: #64748b;">{label}</div>{body}</div>'

def _part_row(num, name, stock_sel):
    segs = ''
    for lbl in ['Yes','No','?']:
        on = lbl == stock_sel
        bg = {'Yes':'#78BC61','No':'#B9314F','?':'#64748b'}[lbl] if on else '#fff'
        col = '#0f172a' if (on and lbl=='Yes') else ('#fff' if on else '#4b5563')
        segs += f'<span style="flex: 1; display: grid; place-items: center; font-size: 13px; font-weight: {600 if on else 400}; color: {col}; background: {bg}; border-right: 1px solid #e5e7eb;">{lbl}</span>'
    return f'''<div style="display: grid; grid-template-columns: 152px 150px 164px; gap: 8px; align-items: center; padding: 6px 0;">
        <div style="position: relative; height: 36px; border: 1px solid #e5e7eb; border-radius: 6px; background: #fff; display: flex; align-items: center; padding-left: 28px; font-size: 14px; color: #0f172a;">{HASH}{num}</div>
        <div style="height: 36px; border: 1px solid #e5e7eb; border-radius: 6px; background: #fff; display: flex; align-items: center; padding-left: 10px; font-size: 14px; color: #0f172a; white-space: nowrap; overflow: hidden;">{name}</div>
        <div style="display: inline-flex; height: 36px; border: 1px solid #e5e7eb; border-radius: 6px; overflow: hidden; background: #fff;">{segs}</div>
      </div>'''

def parts_card_tall():
    """The parts user's RO page: one labor line with two parts, at its real proportions, taller than the phone."""
    rows = _part_row('RC-FP-002', 'Fuel pump module', '?') + _part_row(sil(70), sil(96), 'Yes')
    return f"""
<div class="app" style="background: #fff; position: relative; height: 430px; overflow: hidden;">
  <div style="padding: 10px;">
    <div style="border-radius: 10px; border: 1px solid #cbd5e1; border-left: 4px solid #fbbf24; background: #e2e8f0; color: #0f172a; box-shadow: 0 1px 2px rgba(0,0,0,.05);">
      <div style="padding: 24px 24px 16px; display: grid; grid-template-columns: auto minmax(0, 1fr); column-gap: 12px; row-gap: 2px; align-items: baseline;">
        <span></span><span style="justify-self: start; display: inline-block; border-radius: 999px; border: 1px solid #e9d5ff; background: #f3e8ff; color: #6b21a8; font-size: 10px; font-weight: 700; letter-spacing: .05em; text-transform: uppercase; padding: 0 8px; line-height: 16px;">Recall</span>
        <span style="font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 22px; font-weight: 600; color: #94a3b8;">#</span><span style="font-size: 22px; font-weight: 700;">{sil(150, 14, '#0f172a')}</span>
      </div>
      <div style="padding: 0 24px 24px; display: flex; flex-direction: column; gap: 12px;">
        <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 8px;">{_tile('Story notes', [])}<div style="display: flex; flex-direction: column; gap: 8px;">{_tile('Complaint', [180, 120])}{_tile('Cause', [150])}</div></div>
        <div style="border-radius: 8px; border: 1px solid #e2e8f0; background: #fff; box-shadow: 0 1px 2px rgba(0,0,0,.05); padding: 12px; overflow: hidden;">
          <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 6px;"><span style="font-size: 14px; font-weight: 600; color: #1f2937;">Parts Needed<span style="margin-left: 4px; font-size: 12px; font-weight: 400; color: #9ca3af;">2</span></span></div>
          <div style="overflow: hidden; width: 100%;"><div style="width: 960px;">
            <div style="display: grid; grid-template-columns: 152px 150px 164px; gap: 8px; padding-bottom: 4px; font-size: 10px; font-weight: 600; letter-spacing: .05em; text-transform: uppercase; color: #9ca3af;"><span>Part #</span><span>Part Name</span><span>In Stock?</span></div>
            {rows}
          </div></div>
          <div style="margin-top: 10px; display: flex; align-items: center; gap: 8px;"><span style="display: inline-flex; align-items: center; gap: 6px; min-height: 44px; border: 1px dashed #d1d5db; border-radius: 6px; padding: 6px 12px; font-size: 14px; font-weight: 500; color: #0369a1;">{PLUS}Add part</span></div>
          <div style="margin-top: 10px; display: flex; flex-direction: column; align-items: flex-end; gap: 4px;"><div style="display: flex; align-items: center; gap: 10px;"><span style="font-size: 11px; font-weight: 600; letter-spacing: .05em; text-transform: uppercase; color: #6b7280;">Parts Total</span><div style="width: 96px; height: 36px; border: 1px solid #e2e8f0; border-radius: 6px; background: #fff; display: flex; align-items: center; justify-content: flex-end; padding: 0 10px; font-size: 14px; color: #9ca3af;">$&nbsp;&nbsp;0.00</div></div><div style="font-size: 11px; white-space: nowrap;"><span style="font-weight: 600; color: #0f172a;">Sum of lines above</span> <span style="color: #d1d5db;">|</span> <span style="color: #9ca3af;">Manual total</span></div></div>
        </div>
      </div>
    </div>
  </div>
  <div style="position: absolute; left: 0; right: 0; bottom: 0; height: 90px; background: linear-gradient(rgba(255,255,255,0), #fff 80%);"></div>
</div>"""

def stock_answer_row():
    """The parts user's pricing row, 'In stock? Yes' just tapped."""
    return f"""
<div class="app" style="background: #fff; padding: 12px;">
  <div style="border-radius: 8px; border: 1px solid #e2e8f0; background: #fff; box-shadow: 0 1px 2px rgba(0,0,0,.05); padding: 12px; overflow: hidden;">
    <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 6px;"><span style="font-size: 14px; font-weight: 600; color: #1f2937;">Parts Needed<span style="margin-left: 4px; font-size: 12px; font-weight: 400; color: #9ca3af;">1</span></span></div>
    <div style="overflow: hidden; width: 100%;"><div style="width: 960px; margin-left: -176px;">
      <div style="display: grid; grid-template-columns: 152px 150px 164px 100px; gap: 8px; padding-bottom: 4px; font-size: 10px; font-weight: 600; letter-spacing: .05em; text-transform: uppercase; color: #9ca3af;"><span>Part #</span><span>Part Name</span><span>In Stock?</span><span>Note</span></div>
      {_part_row(sil(70), sil(110), 'Yes')}
    </div></div>
    <div style="font-size: 11px; color: #94a3b8; padding-top: 4px;">← scrolled to the In Stock? column</div>
  </div>
</div>"""
