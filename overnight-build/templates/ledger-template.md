# ☀️ Morning ledger — overnight run of <DATE>

FORMAT RULE (Dave, 2026-08-28): scannable, never prose. One idea per line; tables for anything
with ≥3 parallel items; a state glyph at the left edge of every row (✅ merged · 🟡 needs Dave ·
⛔ blocked · 📝 review · 🔍 needs a check · ⏸ parked · 🚫 not built); a decision = the question in
bold on its own line, then `➜ rec:` on the next. Detail lives in PR bodies + memory, not here.

**Bottom line:** <one sentence — N merged, M waiting on you, what's blocked.>

## Board
| | PR | Item | State | You |
|---|---|---|---|---|
| ✅ | #NNNN | <name> | merged | nothing — revert `git revert -m 1 <sha>` if you dislike it |
| 🟡 | #NNNN | <name> | open, Dave reviews | <one-word ask> |
| ⛔ | #NNNN | <name> | Codex-blocked rN | round N+1 or park? |

## Your calls (answer top to bottom)
**1. <question, one line>** — #NNNN
➜ rec: <one line>
<one line of why, optional>

## Not built / hard floor
- 🚫 <item> — <one-line reason>
- ⏸ <backfill/script>: merged, NOT run; `<command>` after your go

## Watch-outs
- <one line each>

## After you republish (mine)
`smoke:prod` · `verify:deploy -- --expect "<sentinel>"` per PR · live pass on <surface> · fixtures <ids> · memory

Rounds spent: <per PR>.
