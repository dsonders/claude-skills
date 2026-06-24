---
name: codex-fix
description: Recover a RO-bot app PR that FAILED the Codex review gate — in ONE round. Gathers every Codex finding, runs a thorough multi-agent internal review that mirrors Codex's own rubric across the FULL diff, fixes the WHOLE CLASS (not just the flagged line), self-reviews, runs local gates, then re-pushes. Use when a PR gets a Codex BLOCK / "CODEX_REVIEW_VERDICT: BLOCK", a red "Codex Review" check, or the user says a PR failed Codex / Codex review / code review and wants it fixed and re-pushed. RO-bot app only (/ro-bot/app/).
argument-hint: [PR number]
---

# Codex Fix: One-Round Recovery from a Codex Review BLOCK

When a PR fails the Codex review gate, the expensive failure mode is **fix the one flagged line → re-push → Codex finds the next instance of the same class → repeat**. Each round is a paid Codex run and a wasted cycle (history: #619/#644 ate 3–4 rounds, F3 #730 cost 6). This skill spends compute up front — a multi-agent review that mirrors Codex's exact rubric over the **whole diff** and fixes the **whole class** — so the next push passes the first time.

## When to Use This Skill

**Use this skill when:**
- A PR's `Codex Review` check is red / the PR has a "🤖 Codex independent review" comment ending `CODEX_REVIEW_VERDICT: BLOCK`.
- The user says a PR "failed Codex" / "failed the code review" / "Codex blocked it" and wants it fixed and re-pushed.
- You're about to react to a Codex BLOCK (don't hand-fix the single line — run this).

**Don't use this skill for:**
- A **proactive** pre-push review before a PR exists or before Codex has run → use `/code-review` (this skill is the *reactive* complement).
- CI failures that are NOT Codex: a red `Tests`/`TypeScript Check`/`Org-Scoping Guard` job → fix the test/types directly. A red `CodeQL` → triage as FP-or-fix per the CodeQL rule (`js/missing-rate-limiting` dismiss; `js/tainted-format-string` fix).
- The marketing `website/` or `GTM/` repos (no Codex gate there).
- An **advisory-scope** PR (docs-only or secret-free `__tests__/{unit,api,eval,fixtures}`): Codex comments but does NOT block, so there's nothing to recover — address findings only if you agree.

## Core Principles

1. **Codex is a PAID gate that reports the first wall, not the whole wall.** Even though its comment lists findings, re-pushing surfaces a *new* finding it focused on differently. Never loop fix→push→get-blocked. Map and fix the entire diff before re-pushing.
2. **A P0/P1 is one instance of a systemic class (RULE #7).** Always grep the whole repo for siblings and fix them all in one pass.
3. **Mirror Codex's rubric.** The internal review uses Codex's own priority order (correctness → security/isolation → cardinal rules → regressions) so it catches what Codex would across every round.
4. **Adversarially verify before fixing.** Codex down-weights pre-existing/speculative/style noise; so do we. Refute each candidate before it earns a fix — don't over-fix.
5. **Review own fixes against the rubric before pushing.** Codex surfaces ~1 finding/round across *different* files; the fix diff is new surface area. Self-review it the same way.
6. **Respect the sensitive carve-out.** Auto-push non-sensitive recoveries; for auth/org/schema/pricing/destructive/customer-surface changes, stop and ask Dave (RULE #7).

## Workflow

Make a todo list for these steps and work through them systematically.

### Step 1 — Pin the PR and confirm it's a real Codex BLOCK

```bash
PR=<number>                      # from the user, or `gh pr view --json number -q .number`
git branch --show-current        # RULE #4: confirm you're on the PR's branch, not main
gh pr view "$PR" --json number,title,headRefName,baseRefName,mergeStateStatus,files
gh pr checks "$PR"               # confirm the failing check is "Codex Review" (not Tests/CodeQL)
```

Then check out / sync the PR branch if you're not on it (`gh pr checkout "$PR"`), and refresh base so the diff and `origin/main` are current (Dave's local main can lag):

```bash
git fetch origin main
```

If the red check is NOT Codex, stop — this is the wrong skill (see "Don't use" above).

### Step 2 — Gather EVERY Codex finding + the full diff

Grab the latest Codex comment (a new one posts per push; take the **last** match) and the changed-file list:

```bash
# The Codex finding text (P0/P1 lines + verdict):
gh pr view "$PR" --json comments \
  --jq '[.comments[] | select(.body | contains("Codex independent review"))] | last | .body'

# The changed files and the canonical diff:
gh pr view "$PR" --json files --jq '.files[].path'
git --no-pager diff origin/main...HEAD
```

Read the Codex comment in full. Note every `**[P0|P1]** file:line — problem → fix` line. This is the *seed*, not the *scope* — the scope is the whole diff.

### Step 3 — Run the thorough multi-agent review (the Workflow)

Invoke the bundled review workflow. It maps the diff, fans out reviewers across Codex's rubric, adversarially verifies each finding, sweeps the whole class repo-wide, and returns one ordered fix plan. Pass the gathered context as `args`:

```
Workflow({
  scriptPath: "/Users/davidsonders/.claude/skills/codex-fix/codex-recovery-workflow.js",
  args: {
    prNumber: <PR>,
    baseRef: "origin/main",
    codexFindings: "<the full text of the Codex comment from Step 2>",
    changedFiles: ["server/...", "client/..."]   // from `gh pr view --json files`
  }
})
```

The workflow runs in the background and returns `{ plan, verifiedCount, offDiffCount, map }`. The `plan` separates work into two buckets — respect the split:
- **`plan.fixes[]`** — MUST fix before re-push: high-confidence, diff-introduced P0/P1 (the Codex class + anything that would itself block). Each has `locations[]` = **every** site to change, a `confidence`, a `regressionTest`, and an optional `fixLayer`.
- **`plan.advisory[]`** — real but P2/P3 or lower-confidence (and anything whose cited file wasn't in the diff). Note these; fix only if trivial and in the same layer. Do NOT let them expand the diff — over-fixing is what erodes the gate's signal and burns rounds.
- **`plan.layerEscalations[]`** — fixes that would resolve the bug at a *harder/deeper* layer than where it lives (a client-side bug "fixed" by changing a server query or the schema; a soft guard turned into a type/DB constraint). These are **design calls** — surface them to Dave, don't auto-apply (ties to "gate blocks on the user's design call"; don't expand scope under gate pressure).

The two findings-quality gates the workflow already applied for you: every finding had to **quote the offending code verbatim** (hallucinated line numbers are inadmissible) and was **independently re-verified** by a skeptic that defaults to "refuted"; findings citing a file outside the diff were dropped to advisory automatically.

**Scale note:** for a tiny diff (a few lines, no auth/org/schema) you may skip the Workflow and do the map→review→whole-class-sweep inline — but default to running it. Thoroughness here is cheaper than another Codex round.

### Step 4 — Reproduce, then fix the whole class

Work `plan.fixes` (the must-fix bucket) only — leave `plan.advisory` for a note unless an item is trivial and same-layer.

**Test-first, where the finding is unit-testable.** For each fix with a real `regressionTest`, write that test first, run it to confirm it's **RED** (proves it reproduces the defect — a test you never saw fail proves nothing), then fix, then confirm it's **GREEN**, and keep it. This both bounds the fix's scope and converts the Codex class into a permanent regression guard so the gate never has to catch it again. Skip only for genuinely non-unit-testable findings (iOS feel, visual layout) — `regressionTest: "n/a"`; don't use that as an escape hatch.

Then change **every** location in `fix.locations` — not just the one Codex flagged. One coherent change per class; prefer a single chokepoint over N scattered edits where one exists. Keep edits surgical and in the surrounding code's style.

Do NOT silently override one of Codex's findings if it's actually Dave's explicit design decision — split it out and ask (per "gate blocks on the user's design call"). Same for anything in `plan.layerEscalations`.

If a swept sibling location is **provably dead** (no consumer of its output), leave it and say why in your report rather than churning dead code — the whole-class rule is about preventing *drift*, and dead output can't drift. Fixing it is noise.

### Step 5 — Run the local gates the plan named

Run everything in `plan.sweepsToRun`, plus these by default:

```bash
npm run check:org-scoping        # ALWAYS if any org/auth fix (RULE #1 guard — same check CI runs)
npm run check                    # TypeScript
/test:safe                       # unit + API (web-safe)
```

Fix anything they surface before proceeding. Warn Dave before any build/full-suite (RULE #6).

### Step 6 — Self-review the fix diff against the rubric

The fixes are new surface area Codex hasn't seen. Re-read your own `git diff` and walk Codex's rubric once more (correctness, org/auth on all three patterns, secret-leak/customer-surface, field-wiring/regressions). Confirm: did any fix introduce a new by-id read? a broken caller? a field with no read path? a sibling write path still missed? Map the **whole** fix diff, not just the lines you think you changed.

### Step 7 — Commit, push, and report

```bash
git add -A
git commit   # clear message naming the CLASS fixed, not just the symptom
git push
```

Then **respect the sensitive carve-out**. `plan.sensitive` is **advisory** — confirm it with your own one-line reasoning, don't obey it blindly (the synth agent over-flags: a client-side filter/sort/render over data that's *already fetched and already org-scoped server-side* is NOT sensitive even though it shows customer-related fields). State the reasoning either way, then:
- **Not sensitive** → push and let auto-merge + the re-run Codex gate decide. Report the PR link and what class you fixed. Do NOT ask Dave to merge (RULE #7 default flow).
- **Sensitive** — the *fix itself* changes auth / org-isolation query scoping / DB schema / migration / pricing / billing / destructive-bulk ops / a customer-facing surface (the Owner Page customers see, not an internal dashboard) → push, then **explicitly ask Dave to review before merge** and surface the residual risks. Do not arm auto-merge.

Optionally watch the re-review instead of context-switching. **Don't whitespace-split `gh pr checks` output** — the check is named "Codex Review" (two words), so `awk '{print $2}'` reads the wrong column and you'll act on a stale verdict (this bit the first run). Use JSON selection, and read the verdict from the *latest* Codex comment, not the tabular state:

```bash
gh pr checks "$PR" --watch                                   # blocks until checks settle
gh pr checks "$PR" --json name,state \
  --jq '.[] | select(.name=="Codex Review") | .state'        # pass | fail (robust to the space)
gh pr view "$PR" --json comments \
  --jq '[.comments[] | select(.body | contains("Codex independent review"))] | last | .body'
```

If Codex blocks *again*, treat the new finding as a class miss in this pass — read why the sweep didn't catch it, widen the grep, and note it in Step 8.

### Step 8 — Capture any class the review missed

If this took more than one round anyway, the internal review had a blind spot. Briefly note what class slipped through (e.g. a sibling write-path the wiring lens didn't grep) so the workflow's dimensions can be tightened. If it's a durable pattern, route it per the CLAUDE.md table (memory for process; `docs/lessons-learned/` for a stack pattern). Don't add bloat for a one-off.

## The review dimensions (why they mirror Codex)

The workflow's reviewer panel is lifted from `.github/codex/prompts/review.md` so the internal pass sees through the same lens that will judge the re-push:

| Dimension | Mirrors Codex's | Catches |
|---|---|---|
| Correctness | priority 1 | logic/null/async/control-flow/error-handling |
| RULE #1 org + three auth patterns | priority 2–3, P0 heightened | by-id reads not org-scoped, auth-pattern gaps, un-shadowed routes |
| Security & leakage | priority 2, heightened | raw LLM-error/API-key leak, customer-surface internal fields, tainted input |
| Field wiring & regressions | priority 1, 4 | data graveyards, write-allowlist no-ops, broken callers, sibling write paths |
| AI output & customer surface | cardinal rules | removeMetaLanguage funnel, fabrication, pricing math, mobile-first |

If `.github/codex/prompts/review.md` changes, glance at it and update the dimensions in `codex-recovery-workflow.js` to match.

## Success Criteria

- [ ] Confirmed the failing check is `Codex Review` (not Tests/CodeQL/Org-Scoping).
- [ ] Captured the full Codex comment + the full diff before fixing.
- [ ] Ran the multi-agent review (or justified an inline pass for a tiny diff).
- [ ] Worked `plan.fixes` (must-fix); routed `plan.advisory` to notes; escalated `plan.layerEscalations` to Dave rather than over-encoding.
- [ ] For each unit-testable fix: wrote the regression test, saw it RED, then GREEN, and kept it.
- [ ] Fixed the **whole class** for every finding — every `locations[]` entry, not just the flagged line.
- [ ] Local gates green: `check:org-scoping` (if org/auth), `check`, `/test:safe`.
- [ ] Self-reviewed the fix diff against Codex's rubric.
- [ ] Pushed; non-sensitive → auto-merge armed and reported; sensitive → Dave asked to review.

## Integration with Other Skills

- `/code-review` — the **proactive** pre-push review. Run it *before* opening a PR so Codex rarely blocks at all; run `codex-fix` only when it does anyway.
- `/app-testing` — for adding/repairing the Jest/Playwright coverage a fix needs.
- `/compound` — if a recovery surfaced a durable, non-obvious class worth recording.

## Troubleshooting

### Codex blocked again after the fix
The internal review missed a class. Read the new finding, find why the sweep didn't reach it (usually a grep too narrow, or a sibling in a file the map didn't tag), widen it, re-run from Step 3 on the new diff. One repeat is a tuning signal, not a loop — note it in Step 8.

### `gh pr view --json comments` returns no Codex comment
A clean PASS posts nothing, and the comment only appears on BLOCK/advisory/error. If the check is red but there's no comment, the review step errored (bad `OPENAI_API_KEY`) — the comment will say "produced no output"; that's an infra issue, not a code issue (rotate the secret), not something to fix in the diff.

### The "finding" is Dave's explicit design decision, not a bug
Don't admin-override or silently flip it to satisfy the gate. Split it out, fix the real bugs, and ask Dave about the design call (per "gate blocks on the user's design call").

### Workflow returns zero verified findings but Codex blocked
Either the adversarial verifier was too aggressive, or Codex flagged something genuinely pre-existing/borderline. Re-read the Codex line directly against the code; if it's real, fix it by hand; if it's a Codex false positive, address it in the PR (a guard/comment/test) so the re-review passes — don't just re-push unchanged.
