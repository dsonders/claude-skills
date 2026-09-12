"""App-UI frames for board card BG — "A store can switch OFF technicians' bulk
'all green' in the MPI" (Dave, 2026-09-09).

Every frame is drawn from the REAL component anatomy, read 2026-09-12:

  · client/src/pages/admin/settings.tsx           L1236-1307 (the "MPI → Labor
        Line Promotion" Card: CardHeader + ClipboardCheck icon, the
        `p-4 rounded-lg border bg-gray-50` row, the `w-48` Select) and
        L1324-1349 / L1354-1385 (the "Advisor Access" and "ALL CAPS" cards —
        the same row with a shadcn Switch on the right; boolean settings on
        this page DO use a Switch, not a Select).
  · client/src/components/ui/switch.tsx           whole file (h-6 w-11,
        border-2 border-transparent, checked = bg-primary, thumb h-5 w-5
        translate-x-5). --primary = hsl(172 57% 39%) → #2a9d8f
        (client/src/index.css L358).
  · client/src/components/mpi/MPILocationStep.tsx L119-215 (white rounded-xl
        card, sticky #2A9D8F header, `p-4 space-y-4` body, and the bottom
        action area `p-4 border-t border-gray-100 bg-gray-50` holding the
        `w-full h-12 bg-gray-500` button — "All Green" / "Mark the Rest Green",
        rendered only while `hasPendingItems`).
  · client/src/components/mpi/MPIItemCard.tsx     whole file (row = `flex
        items-center gap-3 p-3 rounded-lg border-l-4`, 40px status circle,
        `font-medium text-gray-900 line-clamp-2` label, ChevronRight; pending =
        white bg / border-l-gray-300 / white circle with a gray Square).
  · shared/config/mpi-items.ts                    L42, L296-345 (real
        techGroup label "Under Hood" and real techLabels).
  · client/src/components/mpi/MPIDesktopEntry.tsx L1244-1254 (the desktop
        entry's `w-full h-12 bg-green-600` "Mark All Items Green" /
        "Mark the Rest Green" button).
  · client/src/components/mpi/MPIReview.tsx       L220-370 (the Review slide:
        sticky teal "Review" header, the needs-review card FIRST, then the
        green Passed card, the red "Needs Work" and amber "Keep an Eye On"
        cards, then "Save & Create (N) Lines" and "Save Only").
  · client/src/components/mpi/MPINeedsReview.tsx  whole file (the review sheet
        / card rows: verbatim italic quoted text, the uppercase
        "Part of a note that matched something else" label on an unplaced
        fragment, the parked chip + why line, and the three action buttons
        "Add as new MPI item" / "Link to an item" / "Dismiss").
  · client/src/lib/mpi-review-rows.ts             whole file (`mpiReviewTitle`
        → "1 note needs review"; the row kinds; there is NO "Unrecognized
        Voice Notes" list in the app — that surface is the needs-review list).

Every datum drawn is real app copy or a real catalog label, so no `sil()`
silhouettes were needed. Pure module: no I/O, no imports.
"""

# ---- icons (lucide, the app's only icon set) ----------------------------------
CLIPBOARD_CHECK = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                   'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex:none">'
                   '<rect x="8" y="2" width="8" height="4" rx="1"/>'
                   '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>'
                   '<path d="m9 14 2 2 4-4"/></svg>')
CHECK_WHITE = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
               'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex:none">'
               '<path d="M20 6 9 17l-5-5"/></svg>')
SQUARE = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
          'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
          '<rect x="3" y="3" width="18" height="18" rx="2"/></svg>')
CHEVRON_R = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" '
             'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex:none">'
             '<path d="m9 18 6-6-6-6"/></svg>')
CHEVRON_D = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" '
             'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex:none;opacity:.6">'
             '<path d="m6 9 6 6 6-6"/></svg>')
ALERT_TRI = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
             'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex:none">'
             '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/>'
             '<path d="M12 9v4M12 17h.01"/></svg>')
X_CIRCLE = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex:none">'
            '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6M9 9l6 6"/></svg>')
ALERT_AMBER = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" '
               'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex:none">'
               '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/>'
               '<path d="M12 9v4M12 17h.01"/></svg>')
PLUS = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex:none">'
        '<path d="M5 12h14M12 5v14"/></svg>')
LINK2 = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex:none">'
         '<path d="M9 17H7A5 5 0 0 1 7 7h2M15 7h2a5 5 0 0 1 0 10h-2M8 12h8"/></svg>')

TEAL = '#2A9D8F'          # the MPI wizard header + --primary (hsl(172 57% 39%))
FADE = ('<div style="position: absolute; left: 0; right: 0; bottom: 0; height: 84px; '
        'background: linear-gradient(rgba(249,250,251,0), #f9fafb 82%);"></div>')


# ══════════════════════════════════════════════════════════════════════════════
# 1 · The admin Settings page card for the new setting (desktop, ~900px column)
# ══════════════════════════════════════════════════════════════════════════════

def _switch_on():
    """shadcn Switch, checked: h-6 w-11 rounded-full, bg-primary, thumb h-5 w-5 at +20px."""
    return (f'<span style="display: inline-flex; align-items: center; width: 44px; height: 24px; '
            f'border-radius: 999px; background: {TEAL}; border: 2px solid transparent; '
            f'box-sizing: border-box; flex: none;">'
            f'<span style="width: 20px; height: 20px; border-radius: 999px; background: #fff; '
            f'box-shadow: 0 4px 6px rgba(0,0,0,.18); transform: translateX(20px);"></span></span>')


def _select_w48(value):
    """shadcn SelectTrigger className="w-48": 192px, h-10, rounded-md border, text-sm."""
    return (f'<span style="display: inline-flex; align-items: center; justify-content: space-between; '
            f'width: 192px; height: 40px; flex: none; border: 1px solid #e2e8f0; border-radius: 6px; '
            f'background: #fff; padding: 0 12px; font-size: 14px; color: #0f172a;">'
            f'<span>{value}</span>{CHEVRON_D}</span>')


def settings_card(wording):
    """The new Settings card, in the MPI → Labor Line Promotion card's pattern.

    wording: 'a' | 'b' | 'c' — the three label variants, each drawn in its
    ON / Allowed state.
    """
    title = 'MPI → Bulk Green'
    if wording == 'a':
        label = 'Technicians can mark all remaining items green'
        helper = 'One tap or one voice note marks every untouched item green.'
        control = _switch_on()
    elif wording == 'b':
        label = 'Bulk &ldquo;All Green&rdquo; for technicians'
        helper = 'Allowed.'
        control = _switch_on()
    elif wording == 'c':
        label = 'Marking the rest green'
        helper = 'Allowed.'
        control = _select_w48('Allowed')
    else:
        raise ValueError(f'unknown wording variant: {wording!r}')

    return f"""
<div class="app" style="background: #f9fafb; padding: 16px;">
  <div style="max-width: 900px; margin: 0 auto; border: 1px solid #e5e7eb; border-radius: 8px;
              background: #fff; box-shadow: 0 1px 2px rgba(0,0,0,.05);">
    <div style="padding: 24px 24px 0;">
      <div style="display: flex; align-items: center; gap: 8px; font-size: 24px; font-weight: 600;
                  letter-spacing: -.02em; line-height: 1; color: #0f172a;">{CLIPBOARD_CHECK}<span>{title}</span></div>
    </div>
    <div style="padding: 24px;">
      <div style="display: flex; align-items: center; justify-content: space-between; gap: 16px;
                  padding: 16px; border: 1px solid #e5e7eb; border-radius: 8px; background: #f9fafb;">
        <div style="min-width: 0;">
          <p style="margin: 0; font-size: 16px; font-weight: 500; color: #111827;">{label}</p>
          <p style="margin: 4px 0 0; font-size: 14px; line-height: 1.45; color: #6b7280;">{helper}</p>
        </div>
        {control}
      </div>
      <p style="margin: 12px 0 0; font-size: 12px; color: #6b7280;">
        Applies to inspections from now on. Items already marked green are not changed.
      </p>
    </div>
  </div>
</div>"""


# ══════════════════════════════════════════════════════════════════════════════
# 2 · The tech's phone MPI step (MPILocationStep at 390px)
# ══════════════════════════════════════════════════════════════════════════════

def _mpi_item_row(label, status='pending'):
    """MPIItemCard: p-3 rounded-lg border-l-4, 40px status circle, label, chevron."""
    if status == 'green':
        bg, border, circle, icon = '#f0fdf4', '#22c55e', 'background: #22c55e; color: #fff;', CHECK_WHITE
    else:
        bg, border, circle, icon = ('#ffffff', '#d1d5db',
                                    'background: #fff; border: 2px solid #d1d5db; color: #9ca3af; box-sizing: border-box;',
                                    SQUARE)
    return (f'<div style="display: flex; align-items: center; gap: 12px; padding: 12px; '
            f'border-radius: 8px; border-left: 4px solid {border}; background: {bg};">'
            f'<span style="width: 40px; height: 40px; border-radius: 999px; flex: none; '
            f'display: grid; place-items: center; {circle}">{icon}</span>'
            f'<span style="flex: 1; min-width: 0; font-size: 15px; font-weight: 500; color: #111827; '
            f'line-height: 1.3;">{label}</span>{CHEVRON_R}</div>')


def tech_step(off: bool):
    """The tech's phone MPI step. off=False → today's bottom "All Green" button;
    off=True → the bottom action area is simply gone."""
    rows = ''.join(_mpi_item_row(l) for l in [
        'Belts / Tensioners',
        'Engine Cooling System Hoses &amp; Connections',
        'Heater Hoses &amp; Connections',
        'Engine Air Filter',
    ])
    footer = '' if off else (
        '<div style="flex: none; padding: 16px; border-top: 1px solid #f3f4f6; background: #f9fafb;">'
        '<div style="display: flex; align-items: center; justify-content: center; gap: 8px; '
        'width: 100%; height: 48px; border-radius: 6px; background: #6b7280; color: #fff; '
        'font-size: 16px; font-weight: 600;">' + CHECK_WHITE + '<span>All Green</span></div></div>'
    )
    return f"""
<div class="app" style="background: #f3f4f6; padding: 10px;">
  <div style="border-radius: 12px; border: 1px solid #e5e7eb; background: #fff; overflow: hidden;
              box-shadow: 0 1px 2px rgba(0,0,0,.05); display: flex; flex-direction: column;">
    <div style="background: {TEAL}; padding: 12px 16px; flex: none;">
      <div style="font-size: 18px; font-weight: 600; color: #fff; line-height: 1.3;">Under Hood</div>
    </div>
    <div style="flex: 1; padding: 16px; display: flex; flex-direction: column; gap: 8px;">{rows}</div>
    {footer}
  </div>
</div>"""


# ══════════════════════════════════════════════════════════════════════════════
# 3 · The desktop MPI entry's bulk-green button (cropped strip)
# ══════════════════════════════════════════════════════════════════════════════

def desktop_entry_button(off: bool):
    """A cropped strip of the desktop MPI entry around the "Mark All Items Green"
    button — today vs gone."""
    button = '' if off else (
        '<div style="display: flex; align-items: center; justify-content: center; gap: 8px; '
        'width: 100%; height: 48px; border-radius: 6px; background: #16a34a; color: #fff; '
        'font-size: 16px; font-weight: 600;">' + CHECK_WHITE + '<span>Mark All Items Green</span></div>'
    )
    return f"""
<div class="app" style="background: #f9fafb; padding: 12px 16px; width: 600px; box-sizing: border-box;
     height: 120px; overflow: hidden; position: relative;">
  <div style="display: flex; flex-direction: column; gap: 16px;">
    {button}
    <div style="border: 1px solid #e5e7eb; border-radius: 8px; background: #fff;
                box-shadow: 0 1px 2px rgba(0,0,0,.05); overflow: hidden;">
      <div style="display: flex;">
        <div style="width: 40px; flex: none; background: #f9fafb; border-right: 1px solid #e5e7eb;"></div>
        <div style="flex: 1; padding: 16px;">
          <div style="display: flex; align-items: center; gap: 12px;">
            <span style="width: 32px; height: 32px; border-radius: 999px; border: 2px solid #d1d5db;
                         box-sizing: border-box; flex: none;"></span>
            <span style="font-size: 15px; font-weight: 500; color: #111827;">Belts / Tensioners</span>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div style="position: absolute; left: 0; right: 0; bottom: 0; height: 36px;
              background: linear-gradient(rgba(249,250,251,0), #f9fafb 82%);"></div>
</div>"""


# ══════════════════════════════════════════════════════════════════════════════
# 4 · The review surface after a voice note ending "all other items green"
#     while the setting is OFF (the Review slide — MPIReview + MpiNeedsReviewCard)
# ══════════════════════════════════════════════════════════════════════════════

def _review_action_buttons():
    """MpiReviewActionButtons: Add as new MPI item / Link to an item / Dismiss."""
    return (
        '<div style="margin-top: 10px; display: flex; flex-wrap: wrap; gap: 8px;">'
        '<span style="display: inline-flex; align-items: center; gap: 6px; min-height: 44px; '
        'border-radius: 8px; background: #2563eb; color: #fff; padding: 0 12px; font-size: 14px; '
        'font-weight: 600;">' + PLUS + 'Add as new MPI item</span>'
        '<span style="display: inline-flex; align-items: center; gap: 6px; min-height: 44px; '
        'border-radius: 8px; border: 1px solid #d1d5db; color: #374151; padding: 0 12px; '
        'font-size: 14px; font-weight: 500;">' + LINK2 + 'Link to an item</span>'
        '<span style="display: inline-flex; align-items: center; min-height: 44px; border-radius: 8px; '
        'padding: 0 12px; font-size: 14px; font-weight: 500; color: #6b7280;">Dismiss</span>'
        '</div>'
    )


def _needs_review_card(reason_line=None):
    """MpiNeedsReviewCard with one unplaced-fragment row carrying the bulk phrase."""
    why = ('<p style="margin: 4px 0 0; font-size: 12px; line-height: 1.45; color: #4b5563;">'
           f'{reason_line}</p>') if reason_line else ''
    return f"""
<div style="border: 1px solid #fcd34d; border-radius: 12px; background: #fffbeb; padding: 16px;">
  <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px; font-size: 16px;
              font-weight: 600; color: #78350f;">{ALERT_TRI}<span>1 note needs review</span></div>
  <div style="border: 1px solid #e5e7eb; border-radius: 8px; background: #fff; padding: 12px;">
    <p style="margin: 0; font-size: 14px; font-style: italic; color: #1f2937; line-height: 1.4;">
      &ldquo;All other items green&rdquo;</p>
    <p style="margin: 4px 0 0; font-size: 11px; font-weight: 500; letter-spacing: .05em;
              text-transform: uppercase; color: #6b7280;">Part of a note that matched something else</p>
    {why}
    {_review_action_buttons()}
  </div>
</div>"""


def _finding_row(icon, label):
    return (f'<div style="display: flex; align-items: center; justify-content: space-between; '
            f'gap: 8px; padding: 10px 8px; margin: 0 -8px; border-radius: 8px;">'
            f'<div style="display: flex; align-items: center; gap: 10px; min-width: 0; flex: 1;">'
            f'{icon}<span style="font-size: 14px; font-weight: 500; color: #111827; '
            f'white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{label}</span></div>'
            f'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex:none">'
            f'<path d="m9 18 6-6-6-6"/></svg></div>')


def _count_badge(n, bg):
    return (f'<span style="display: inline-flex; align-items: center; justify-content: center; '
            f'min-width: 20px; height: 20px; padding: 0 6px; border-radius: 999px; background: {bg}; '
            f'color: #fff; font-size: 12px; font-weight: 700; font-variant-numeric: tabular-nums;">{n}</span>')


def review_sheet(variant):
    """The tech's Review surface after a note that ended "all other items green"
    with the setting OFF.

    variant:
      'silent' — only the recognized findings; the bulk phrase is nowhere, and
                 the untouched items simply stay pending.
      'parked' — the same, plus the note's leftover words as a review row.
      'reason' — 'parked' plus one muted line saying why.
    """
    if variant == 'silent':
        top = ''
    elif variant == 'parked':
        top = _needs_review_card()
    elif variant == 'reason':
        top = _needs_review_card('Bulk green is off for this store.')
    else:
        raise ValueError(f'unknown review_sheet variant: {variant!r}')

    passed = f"""
<div style="border: 1px solid #bbf7d0; border-radius: 12px; background: #f0fdf4; padding: 16px;">
  <div style="display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600;
              letter-spacing: .05em; text-transform: uppercase; color: #15803d;">
    {_count_badge(22, '#16a34a')}Passed</div>
</div>"""

    needs_work = f"""
<div style="border: 1px solid #fecaca; border-radius: 12px; background: #fef2f2; padding: 16px;">
  <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px; font-size: 14px;
              font-weight: 600; letter-spacing: .05em; text-transform: uppercase; color: #b91c1c;">
    {_count_badge(1, '#dc2626')}Needs Work</div>
  {_finding_row(X_CIRCLE, 'Belts / Tensioners')}
</div>"""

    keep_eye = f"""
<div style="border: 1px solid #fde68a; border-radius: 12px; background: #fffbeb; padding: 16px;">
  <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px; font-size: 14px;
              font-weight: 600; letter-spacing: .05em; text-transform: uppercase; color: #b45309;">
    {_count_badge(1, '#f59e0b')}Keep an Eye On</div>
  {_finding_row(ALERT_AMBER, 'Engine Air Filter')}
</div>"""

    footer = """
<div style="padding-top: 8px;">
  <div style="display: flex; align-items: center; justify-content: center; width: 100%; height: 40px;
              border-radius: 6px; background: #2563eb; color: #fff; font-size: 14px; font-weight: 600;">
    Save &amp; Create (2) Lines</div>
  <p style="margin: 8px 0 0; font-size: 12px; color: #6b7280; text-align: center;">
    All Red &amp; Yellow items will become new labor lines</p>
</div>"""

    body = ''.join(f'<div>{b}</div>' for b in [top, passed, needs_work, keep_eye, footer] if b)

    return f"""
<div class="app" style="background: #f3f4f6; padding: 10px; position: relative; height: 460px; overflow: hidden;">
  <div style="border-radius: 12px; border: 1px solid #e5e7eb; background: #fff; overflow: hidden;
              box-shadow: 0 1px 2px rgba(0,0,0,.05);">
    <div style="background: {TEAL}; padding: 12px 16px;">
      <div style="font-size: 18px; font-weight: 600; color: #fff; line-height: 1.3;">Review</div>
    </div>
    <div style="padding: 16px; display: flex; flex-direction: column; gap: 16px;">{body}</div>
  </div>
  <div style="position: absolute; left: 0; right: 0; bottom: 0; height: 76px;
              background: linear-gradient(rgba(243,244,246,0), #f3f4f6 84%);"></div>
</div>"""
