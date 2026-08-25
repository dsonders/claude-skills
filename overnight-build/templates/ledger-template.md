# ☀️ Morning ledger — overnight run of <DATE>

**Bottom line:** <N merged, M parked, what's blocked on Dave — one sentence.>

## Merged overnight (nothing is live until you republish)
| PR | What a user sees (before → after) | Revert |
|---|---|---|
| #NNNN | <one plain-language line> | `git revert -m 1 <sha>` |

## Waiting on you
- **#NNNN — <name>**: <the question, answerable in one word, with my recommendation first>

## Hard floor — merged but NOT executed
- <backfill/script>: run with `<command>` after your go.

## Watch-outs
- <anything a reverting eye should look at first; new-visibility notes; population facts>

## After you republish (mine)
- `npm run smoke:prod` · `verify:deploy -- --expect "<sentinel>"` per PR · live pass on
  <highest-risk surface> · kanban + memory updates · fixture cleanup (<ids>)

Rounds spent: <Codex rounds per PR>. Parked follow-ups recorded in <memory entry>.
