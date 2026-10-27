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
- The `Driver` column (awaiting README) says where a row starts: `headless` → Chromium/Playwright or
  the API; `simulator` → `/ios-verify` (real Mobile Safari); `📱` → still TRY the ladder below first.
- Every FAILED is replayed locally before it is written; a real one gets a fix PR plus its own awaiting
  file the same session. Re-read rows against same-batch siblings before calling a regression.

## 3. The ladder — no row reaches Dave without it ⭐

A row goes on Dave's page only when ALL of the following are true, and the card says so with evidence:

1. **A ceiling is named by number** from the harness README's Ceilings list. "Touch feel" or "needs a
   real device" without a number is not a reason.
2. **Every rung below it was tried, in order, and the attempt is quoted** (the command or action, and
   what happened): headless Chromium → Playwright WebKit → iOS Simulator via safaridriver → the Simulator
   WINDOW through computer-use (native app, full tier — can it raise the keyboard, open the Home Screen
   app, lock the screen? record the answer either way) → a fixture change that makes it drivable (feature
   flag ON, org mode flip, TD2, a minted RO; "the test org has it off" is never a reason).
3. **The row was split.** Whatever half CAN be proved is proved and ticked in the file; only the residue
   goes to Dave, reworded to that residue.
4. **An independent refuter signed off.** One Opus agent per batch of candidate rows, briefed with the
   cards' "Why I can't" text and the harness README, whose only job is to drive ONE of them anyway. A
   refuted row is driven and ticked; the refuter's verdict is quoted on every surviving card.

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
