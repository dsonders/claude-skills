---
name: pre-push-mirror
description: Pre-push mirror review for RO-bot app PRs in blocking domains — run BEFORE the first push of any PR touching org-isolation/tenancy, auth, schema/migrations, billing, destructive ops, customer-facing surfaces, or background/unattended writes. Runs /code-review high on the unpushed diff, triages findings by the mirror rules (fix correctness + whole class; defer behavior-preserving refactors; meta-probe fail-open guards), fixes, then pushes ONCE. Use when about to push a sensitive or blocking-domain PR, when the user says "pre-push mirror", "mirror review", or "run the mirror", or before opening any PR where a Codex block is plausible. RO-bot app only (/ro-bot/app/).
argument-hint: [none — operates on the current branch's unpushed diff]
---

# Pre-Push Mirror: Pass the Codex Gate on the First Try

The Codex review gate is a PAID adversarial reviewer that reports the first wall, not the whole wall — each block costs a round. This skill runs an internal review that mirrors Codex's rubric over the unpushed diff, fixes what it finds by explicit triage rules, and pushes once.

**Track record:** #1418 skipped it → 2 paid rounds. #1419, #1420, #1421 ran it → each passed Codex first-try, and the mirror surfaced real defects Codex never demanded (a missing Storage-existence proof, a fail-open wiring test proven by meta-probe, an unconverted sibling class). #1431 (pricing + background writes) → 6 real defects fixed pre-push (a torn two-clock read that rendered a clean finish as failure, a blur-storm from a healthy-path arm, an unhandled-rejection tail, a burned pass budget), Codex first-try green. #1465 (43-file money path, built by an Opus agent with 29 self-probes already run) → the mirror STILL found 10 real defects the builder's own probes couldn't (a no-keystroke blur that wrote a PATCH, a gate whose new field neither caller passed, an unreordered row variant, a figure that vanished on closed ROs, a same-value save dropping frozen money) — Codex first-try green. Build agents verify what they wrote; the mirror verifies what they didn't think of. **If the `/code-review` orchestrator dies mid-run (model limit), its finder agents' notifications still carry every finding — triage from those directly; don't re-run.**

**This is not gaming the gate.** Codex reviews the identical final diff either way; the mirror adds a partially-uncorrelated review before it, and deferrals are documented in the PR body where both Codex and Dave see them. Nothing is hidden, split, or crafted to evade the rubric.

## When to Use This Skill

**Use when the unpushed diff touches ANY blocking domain:**
- `organization_id` isolation / tenancy / auth (any of the three auth patterns)
- DB/Firestore schema, migrations, backfills
- Pricing, billing, subscriptions
- Destructive or bulk data operations
- Customer-facing surfaces that can leak internal data
- Background / unattended / fire-and-forget writes, transactions, race-prone ordering
- Any RULE #7 sensitive-category PR (Dave reviews these — the mirror is what makes his review cheap)
- Low confidence in the change, regardless of category

**Don't use for:**
- A PR that already FAILED the Codex gate → `/codex-fix` (the reactive complement).
- Trivial or advisory-scope diffs (docs, secret-free test-only) — Codex doesn't block there; push.
- Repos without a Codex gate (`website/`, `GTM/`).

## Workflow

### Step 1 — Preconditions

- All implementation work is COMMITTED locally (never review a dirty tree; probes need a committed baseline).
- Local gates already green: targeted jest, `npm run check:org-scoping` (if org/auth touched), tsc.
- The branch has NOT been pushed. If it has, and no Codex run happened yet, proceed anyway; if Codex already ran, switch to `/codex-fix`.

### Step 2 — Run the mirror

Invoke `/code-review high` on the branch diff (vs `origin/main`). Let it complete; it mirrors Codex's rubric (correctness → org/auth → security/leakage → wiring/regressions → failure-path and unattended-write contracts).

**Stall watch (known harness bug, hit twice 2026-08-15):** a backgrounded /code-review fork's final VERIFIER notification can be delivered to the MAIN session instead of back to the fork — the fork then reports "waiting on the final verifier" and sleeps forever while its verdicts sit in your transcript. If the review is quiet well past ~30 min: `ListAgents` (the fork won't be live), then `SendMessage` the fork its verifier's result verbatim and tell it to assemble the final findings from its transcript — do NOT re-run the review. Set yourself a check-in when you launch it; don't wait for the user to notice.

### Step 3 — Triage every finding (the rules that make this work)

| Finding type | Action |
|---|---|
| Correctness / security / tenancy defect | **Fix now.** |
| Partial-class coverage ("you converted 4 of 7 sibling paths") | **Widen the diff to close the WHOLE class** — Codex will demand it anyway, and a class half-closed reads as an oversight, not a scope choice. |
| A test/guard that is fail-open | **Fix, then META-PROBE it**: construct the exact broken build the old guard could not see and confirm old-guard-passes / new-guard-fails. |
| Behavior-preserving refactor of PROVEN code (consolidations, dedups, helper extraction in untouched paths) | **DEFER.** List it in the PR body as a follow-up. Review churn in a sensitive diff costs more than the cleanup buys. Exception: if it deletes code the diff itself introduced, just take it. |
| Advisory whose SUBJECT is a blocking domain (tenancy, races, paid-call budgets, **a missing mobile/touch affordance (RULE #3), pre-auth resource amplification/DoS, an enforcement gate's FAIL DIRECTION**) | **Not safely deferrable** — fix it or scope-reset; a PR-body safety argument does NOT survive a hole IN a blocking domain (#1362). Enforcement-gate corollary (#1509, 2 post-mirror blocks): any PERSISTENT fail-open state (malformed config, cached error) means the gate never enforces — "fail open, loudly logged" is not enforcement; and re-ask who ARMS a self-arming mechanism after every fix (it must be the population that always flows, never only the restricted one). 2026-08-20 double-proof: #1493 deferred a touch-removal gap ("lifecycle is desktop-scoped") and #1496 deferred doubled pre-auth multer buffering ("bounded by cap + limiter, documented") — Codex blocked on the documented deferral BOTH times, verbatim. If the mirror writes a residual paragraph for one of these domains, that paragraph is the next block. |
| Layer escalation / conflicts with one of Dave's recorded design rulings | **Ask Dave** — never auto-apply, never silently override a ruling to satisfy a reviewer. |

### Step 4 — Apply the fixes

- Route fixes to the SAME agent/context that implemented the PR (continuity beats a cold agent re-deriving the design).
- New commit — don't amend (keeps the mirror round reviewable).
- Probe every new/changed guard ONE AT A TIME (revert its fix, confirm red on the right assertion, restore by targeted re-edit — never `git checkout --` on uncommitted work).
- Re-run full local gates (full unit+API sweep, `check:org-scoping`, tsc with fresh tsbuildinfo).

### Step 5 — Push ONCE, then write the PR body honestly

The PR body must carry: what the mirror round changed and why, every DEFERRED item as a named follow-up, and residual risks for the reviewer. A clean gate must never read as "nothing to look at."

Then apply RULE #7: non-sensitive → `gh pr merge --auto --squash`; sensitive → no auto-merge, ask Dave to review.

### Step 6 — If Codex blocks anyway

Run `/codex-fix` and seed it with this mirror's full output — a block after a mirror is most often a finding the mirror mis-bucketed as advisory/deferred (#1355 pattern). Afterward, note the mirror's blind spot (one line, in memory or the lessons INDEX per the routing table) so the next run is tighter.

## Success Criteria

- [ ] Mirror ran on the complete committed diff before any push.
- [ ] Every finding triaged into exactly one bucket from the Step 3 table.
- [ ] Whole-class findings closed across ALL siblings, not just cited lines.
- [ ] Every new/changed guard probed individually; fail-open fixes meta-probed.
- [ ] Full gates green after the fix commit.
- [ ] One push; deferrals + residuals in the PR body.
- [ ] Sensitive carve-out respected (no auto-merge; Dave asked).

## Integration with Other Skills

- `/code-review` — the review engine this skill invokes and triages; use it bare for non-blocking-domain diffs.
- `/codex-fix` — the reactive complement, after a real Codex BLOCK. Its whole-class doctrine and probe rules are the same ones Step 3/4 apply proactively.
- `/compound` — if a mirror round surfaces a durable class worth recording.
