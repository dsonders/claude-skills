---
name: live-pass
description: Post-republish live verification of the RO-bot app (app/ only). Use when Dave says a Replit republish is complete, "smoke and verify live", "check the release-verification list", or invokes /live-pass. Orchestrates verify:deploy + smoke:prod, one Opus agent per awaiting file with browsers and the iOS Simulator, the escalation ladder + refuter before any row goes to Dave, the fixture sweep, the ledger PR, and a NEW date-stamped hand-checks page for his 📱 rows.
---

# Live pass — what closes the release-verification queue

Orchestration only. The mechanics live in the repo and are authoritative over this file:
`docs/release-verification.md` (playbook, top section), `docs/release-verification/awaiting/README.md`
(the queue), `__tests__/workflow/live-pass/README.md` + `PREAMBLE.md` + `lib.mjs` (the harness, its
idioms and its **Ceilings** list). Memory `reference_release_verification_queue` holds the recurring traps.

Run in a pool worktree (`.claude/worktrees/build-N`, claim → `reset --hard origin/main` → branch
`docs/live-pass-<date>`). One plain command per Bash call, absolute paths, never `cd`.

## 0. Is it real, and is it mine?

1. `npm run verify:deploy -- --base https://app.tenthgear.ai` — the pass starts only when
   `index.html built <time>` moved past the last ledger's time (a "Published your App" commit is NOT a
   signal). Record `/api/version`'s sha.
2. `ListAgents` + `SendMessage` every sibling session: "running the live pass of <sha> — are you?" Wait
   for the answers. Two passes on one republish collide on logins and fixtures.
3. `git log <last verified tree>..<this tree> --oneline` vs `ls docs/release-verification/awaiting/` —
   every merged PR that can only be proven live has a file; a missing one is written NOW (RULE #5), not
   after the pass.
4. **Read Dave's ticks back** from every hand-checks page listed in the Verified block headers since the
   last pass: `ArtifactData` list on collection `checks` per page URL. A ticked `data-id` moves its row to
   Verified as `✅ <date> (Dave, hand-check)` before anything is driven. Unticked rows age by one republish.

## 1. Bundle + smoke

- Every awaiting sentinel in ONE `verify:deploy` run (single-quote a `$`); a sentinel that pre-exists
  elsewhere is inverted (`--expect "<OLD literal>"` must go RED).
- `npm run smoke:prod` unpiped. Transcribe the result; a red suite is replayed alone before it is a finding.

## 2. Drive the rows

- Slice each awaiting file into `sec-*.md` (`sed -n`), fill the PREAMBLE blanks, prepend a COMMON.md
  (worktree shell rules, uids, routes, testids, the rulings of record). Briefs carry the ROW TEXT
  verbatim and the exact entry points.
- One Opus agent per file or small group. Logins are disjoint per browser agent (`tech` / `tech_b` /
  `advisor` / `admin` / `parts`; TD2 for multi-player rows); API-only agents share tokens. Writers of
  per-USER or ORG-level state run in sequence, never beside a reader. Never browser-drive prod while the
  suites run.
- The `Driver` column (awaiting README) says where a row STARTS, never where it ends: `headless` →
  Chromium/Playwright or the API; `simulator` → `/ios-verify`; `📱` → the whole ladder in §3 first — a
  `📱` tag written by a PR author is a guess, not a verdict.
- Every FAILED is replayed locally before it is written; a real one gets a fix PR plus its own awaiting
  file the same session. Re-read rows against same-batch siblings before calling a regression.

## 3. Drive it yourself — Dave's page is the failure case, not the handoff ⭐

**The target number of rows on Dave's page is ZERO.** Every card on it is a row the pass failed to
drive, and the card has to prove that failure. "Needs a real device", "touch feel", "only Dave has the
phone" are not reasons; a numbered ceiling with quoted attempts is. Report `rows to Dave / rows total`
in the ledger and in the message to Dave; the number is expected to fall every pass.

**Driver inventory on this Mac (use ALL of it before writing a card):**

| Driver | Reaches | Use it for |
|---|---|---|
| API (`lib.mjs` `api()`, role tokens) | every server behaviour, footprints, Firestore state via the debug routes | the first attempt for any row whose Expected is a stored value or a status |
| Playwright Chromium (headless, phone viewport, `hasTouch`, `fakeCam`, TTS dictation via `routeTts`) | every client behaviour that is not engine-specific; file inputs; HTML5 drag; mic/camera via fakes | the default for UI rows |
| Playwright WebKit (`webkit-2359` = the desktop Safari engine) | Safari-engine rendering, drag, inputs, `date`/`number` quirks | any row that says "Safari" — BEFORE deciding it is Dave's |
| Playwright device emulation (iPhone descriptors) | viewport, UA, touch events, `safe-area` declarations | layout rows; never for "the keyboard rises" |
| iOS Simulator, real Mobile Safari via safaridriver (`/ios-verify`, iPhone 17 booted) | WebKit-on-iOS truth: fixed-position, momentum scroll, `dvh`, PWA install flow via Safari UI, mock camera | any row that still reads "iOS" after WebKit passed |
| computer-use on the Simulator WINDOW (`request_access(["Simulator"])`, native app, full tier) | PROVED 2026-10-27: the real iOS keyboard (⌘K "Toggle Software Keyboard" once per boot, then tap the field), the Home Screen (window-chrome Home button → a standalone PWA icon), lock (⌘L) and unlock (Home twice); `simctl openurl` to load a page, `simctl io screenshot` for the whole device | every keyboard / Home Screen / lock / app-switch row, paired with a safaridriver session for rects and JS (memory `reference_ios_simulator_webdriver_recipe`) |
| claude-in-chrome (Dave's real Chrome, his logins) | real-browser Chrome with real extensions and cookies | a desktop row where headless Chromium passed but "real Chrome" is the claim |
| Gmail MCP (TD1 tech mailbox dave@ro-bot.io) | email bodies, links, timing | every "an email arrives" row |
| Fixture changes (feature flag ON, TD1/TD2 mode flip, `mintRo`, cold-store/restore) | rows blocked by the test org's state | "the test org has it off" is never a reason — set it and test |

Not on this Mac: an Android emulator (no `adb` / `emulator`). An Android-only row is the ONE class that
goes to Dave without a ladder attempt; say so on the card, and note in the ledger that installing the
Android Studio emulator would remove the class (his spend call).

**The ladder (every rung attempted IN ORDER, each attempt quoted on the card: the command or action,
what happened, how long it took):**

1. API / footprint → 2. Playwright Chromium → 3. Playwright WebKit → 4. iOS Simulator via safaridriver →
5. computer-use on the Simulator window (proved: keyboard, Home Screen, lock) → 6. Android emulator
(Playwright's `_android` over adb, once installed) → 7. a fixture change that makes any of 1–6 work.

A row goes on Dave's page only when ALL hold:

- **A ceiling is named by number** from the harness README's Ceilings list, and that ceiling is the
  rung where the attempt actually stopped (a ceiling-1 keyboard row that was never tried through rung 5
  is not finished).
- **The row was split.** Whatever half CAN be proved (the declaration, the rect, the state after the
  action, the API footprint) is proved and ticked in the file; only the residue goes to Dave, reworded
  to that residue. A residue of "and it feels right" is dropped, not handed over.
- **An independent refuter signed off.** One Opus agent per batch of candidate cards, briefed with the
  cards' text, the harness README and this inventory, whose only job is to drive ANY of them. It gets
  real time (up to 20 min per row) and the same logins. A refuted row is driven and ticked; the
  refuter's verdict is quoted on every surviving card.
- **Carried-over rows are re-tried**, not re-copied: a row carried from a previous page gets the
  ladder again with any new rung (a new driver, a fixture that now exists), and its age is on the card.

## 4. Fixture sweep, promotion, ledger

1. `node __tests__/workflow/live-pass/sweep-fixtures.mjs` (dry run) → read the list → `--apply`. Runs
   unconditionally, before the ledger PR, both orgs if TD2 was used.
2. For every file whose rows all proved and whose surface is stable: promote API rows into
   `__tests__/workflow/` cases and UI rows into a creds-gated Playwright spec (the
   `ui-permission-gates.spec.ts` shape; labels are guarded by `e2e-label-pins-exist.test.ts`). Note
   `promoted → <test file>` on the Verified `###` line, or `promotion: deferred (<why>)`.
3. Ledger PR (docs-only, auto-merge via `npm run pr:automerge -- <n>`): move closed files to Verified
   under one `Republish of <date>` header that carries the sha, the counts (proved / partial /
   not-drivable / failed), the judgement calls for Dave, the hand-checks page URL, and every 📱 row older
   than three republishes listed for his ruling (run it next pass, or close as `accepted on first tech
   report`).

## 5. The hand-checks page — new every pass

- Build from `hand-checks-template.html` in this skill dir (db-backed ticks, localStorage fallback, CSS
  overlay annotations). Publish with the Artifact tool, `capabilities: {db: {}, user: {}}`, title
  `Hand-Checks <YYYY-MM-DD>`, icon `checklist`, screenshots via `files` + `root`.
- One card per surviving row: Where / Do / Expect in Dave's words, an annotated capture FROM THE PASS
  (the agents' own screenshots, boxes positioned in percent; never fresh captures, no image libraries),
  the named ceiling, the ladder evidence, the refuter's verdict. Group by device; carried-over rows last
  with their age. Reuse a carried row's `data-id` so its ticks follow it.
- Verify the empty `checks` collection reads back with `ArtifactData` before reporting.
- Report to Dave: sha, counts, the page URL, the fix PRs, and the rows awaiting his ruling. Then update
  memory `reference_release_verification_queue`'s *Latest state* line only (one line; narratives live in
  the Verified history).

## Don'ts

- Never add a `###` under the main doc's *Awaiting republish* heading (`check:awaiting-anchor`).
- Never rewrite the Verified half; append-then-move, and on a same-anchor conflict take main's structure
  and re-add only your own moves.
- Never flip an org-level prod setting from an agent brief without Dave's word (the classifier denies it;
  re-wording the brief is not the fix).
- Never a blanket "needs a real phone" line on the page — the reason is per card, with the rung evidence.
- Never hand Dave a row because it is faster than driving it. The pass has the time; he does not.
