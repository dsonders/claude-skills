# Phone board — build source (groom skill Step 0)

Published artifact: https://claude.ai/code/artifact/5089d5b5-577e-402b-95ec-8b0fd421576d (capability `db`; republish by
passing that URL as `url` from any session).

- `build.py` — writes `grooming-board-phone.html` next to itself. Run `python3 build.py` from anywhere (absolute paths).
- `decisions.py` — the lettered options + rec for every to-vote card's questions. EDIT THIS when the backlog changes.
  Keys are the board card keys; ids are `<KEY>-<n>` and the store is keyed on them — keep them stable.
- `cards.json` — title / sub / dims / figures per to-vote card, extracted from the desktop board's HTML
  (the extraction script is in the 2026-09-08 session; re-extract with the same regexes when cards change).
- `triage_frames.py` — the ONE basic mockup per not-yet-groomed item (keyed in `build.py`'s `TRIAGE_MOCK`).
- `lib.py`, `parts_card.py`, `admin_card.py` — the drawn app frames (RO line panel, customer page, parts card, admin
  Parts & Labor card). Add a `frames_for(key)` branch in `build.py` for each new Flip / walkthrough item.
- `board.css` — the desktop board's stylesheet, carried in so ported figures render.
- `test.mjs`, `test2.mjs` — Playwright checks at 390px (routing, tapping, words, notes, persistence; scroll stability
  under a simulated store). Run with `node` from `/ro-bot/app` so `playwright` resolves (the scripts use absolute paths).

Store layout: `rulings/<KEY>-<n>` = `{choice, words, at}` · `rulings/<KEY>-stage` = `{choice: advance|keep|icebox}` (triage items) · `notes/<KEY>` = `{text, at}`. `STAGE` / `STAGE_NOTE` in `decisions.py` mark triage items. Sweep protocol: groom skill Step 0.
