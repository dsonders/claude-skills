from lib import *
HASH = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="position: absolute; left: 8px; top: 50%; transform: translateY(-50%);"><path d="M4 9h16M4 15h16M10 3 8 21M16 3l-2 18"/></svg>'
PLUS = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12h14"/></svg>'

# ---- Parts user's RO page, one line card, phone (real anatomy: parts-repair-order.tsx PartsLineCard + IssuePartList/PartRow) ----
def parts_card(part_added=True):
    row = f"""
      <div style="display: grid; grid-template-columns: 152px 150px 164px; gap: 8px; align-items: end; padding-bottom: 6px; font-size: 10px; font-weight: 600; letter-spacing: .05em; text-transform: uppercase; color: #9ca3af;"><span>Part #</span><span>Part Name</span><span>In Stock?</span></div>
      <div style="display: grid; grid-template-columns: 152px 150px 164px; gap: 8px; align-items: center;">
        <div style="position: relative; height: 36px; border: 1px solid #e5e7eb; border-radius: 6px; background: #fff; display: flex; align-items: center; padding-left: 28px; font-size: 14px; color: #0f172a;">{HASH}RC-FP-002</div>
        <div style="height: 36px; border: 1px solid #e5e7eb; border-radius: 6px; background: #fff; display: flex; align-items: center; padding-left: 10px; font-size: 14px; color: #0f172a; white-space: nowrap; overflow: hidden;">Fuel pump module</div>
        <div style="display: inline-flex; height: 36px; border: 1px solid #e5e7eb; border-radius: 6px; overflow: hidden; background: #fff;"><span style="flex: 1; display: grid; place-items: center; font-size: 13px; color: #4b5563; border-right: 1px solid #e5e7eb;">Yes</span><span style="flex: 1; display: grid; place-items: center; font-size: 13px; color: #4b5563; border-right: 1px solid #e5e7eb;">No</span><span style="flex: 1; display: grid; place-items: center; font-size: 13px; font-weight: 600; color: #fff; background: #64748b;">?</span></div>
      </div>""" if part_added else ''
    count = '<span style="margin-left: 4px; font-size: 12px; font-weight: 400; color: #9ca3af;">1</span>' if part_added else ''
    return f"""
<div class="app" style="background: #fff; padding: 10px;">
  <div style="border-radius: 10px; border: 1px solid #cbd5e1; border-left: 4px solid #fbbf24; background: #e2e8f0; color: #0f172a; box-shadow: 0 1px 2px rgba(0,0,0,.05);">
    <div style="padding: 16px 16px 12px; display: grid; grid-template-columns: auto minmax(0, 1fr); column-gap: 12px; row-gap: 2px; align-items: baseline;">
      <span></span><span style="justify-self: start; display: inline-block; border-radius: 999px; border: 1px solid #e9d5ff; background: #f3e8ff; color: #6b21a8; font-size: 10px; font-weight: 700; letter-spacing: .05em; text-transform: uppercase; padding: 0 8px; line-height: 16px;">Recall</span>
      <span style="font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 22px; font-weight: 600; color: #94a3b8;">#</span><span style="font-size: 22px; font-weight: 700; letter-spacing: -.01em;">{sil(150, 14, '#0f172a')}</span>
    </div>
    <div style="padding: 0 16px 16px;">
      <div style="border-radius: 8px; border: 1px solid #e2e8f0; background: #fff; box-shadow: 0 1px 2px rgba(0,0,0,.05); padding: 12px; overflow: hidden;">
        <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 6px;"><span style="font-size: 14px; font-weight: 600; color: #1f2937;">Parts Needed{count}</span></div>
        <div style="overflow: hidden; width: 100%;"><div style="width: 960px;">{row}</div></div>
        <div style="margin-top: 10px; display: flex; align-items: center; gap: 8px;"><span style="display: inline-flex; align-items: center; gap: 6px; min-height: 44px; border: 1px dashed #d1d5db; border-radius: 6px; padding: 6px 12px; font-size: 14px; font-weight: 500; color: #0369a1;">{PLUS}Add part</span></div>
      </div>
    </div>
  </div>
</div>"""

