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
- A **proactive** pre-push review before a PR exists or before Codex has run → use `/pre-push-mirror` (which invokes `/code-review high` and triages by the mirror rules; this skill is the *reactive* complement).
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

**If a `/pre-push-mirror` review ran before this PR was pushed, retrieve its FULL output — especially the advisory/deferred bucket — and seed the review with it.** A block that lands despite a mirror is most often a finding the mirror mis-bucketed as advisory or deferred (#1355: several later blocks were sitting in earlier review outputs as mis-bucketed advisories), so those items are the prime suspects, already written down.

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
- **`plan.advisory[]`** — real but P2/P3 or lower-confidence (and anything whose cited file wasn't in the diff). Note these; fix only if trivial and in the same layer. Do NOT let them expand the diff — over-fixing is what erodes the gate's signal and burns rounds. **Two overrides from #1355 (6 rounds):** (a) an advisory whose SUBJECT is one of Codex's blocking domains — paid-cost/rate-limit accounting, a security/tenancy property, a data race — is NOT safely deferrable regardless of the plan's severity rating: either fix it or write the explicit safety argument into the PR body (#1355 r3: the plan's P2 "aiLimiter counts requests, the fan-out is unbounded" became Codex's P1 verbatim one round later). **CORRECTION (#1362 r3): the PR-body safety argument does NOT survive when the hole itself sits IN a blocking domain (trust/provenance/tenancy) — Codex blocked on a fully-documented design-boundary residual anyway. For those, the only exits are close the hole or scope-reset the feature; the safety-argument path works only for subjects OUTSIDE the blocking domains.** (b) **an advisory you TAKE is a design change, not a freebie** — enumerate its failure direction per population before pushing (#1355 r4: taking the plan's "add aiLimiter" advisory meant an exhausted AI budget 429'd core line creation; Codex blocked on the taken advisory itself).
- **`plan.layerEscalations[]`** — fixes that would resolve the bug at a *harder/deeper* layer than where it lives (a client-side bug "fixed" by changing a server query or the schema; a soft guard turned into a type/DB constraint). These are **design calls** — surface them to Dave, don't auto-apply (ties to "gate blocks on the user's design call"; don't expand scope under gate pressure).

The two findings-quality gates the workflow already applied for you: every finding had to **quote the offending code verbatim** (hallucinated line numbers are inadmissible) and was **independently re-verified** by a skeptic that defaults to "refuted"; findings citing a file outside the diff were dropped to advisory automatically.

**Scale note (fail closed on sensitive PRs):** you may skip the Workflow and do the map→review→whole-class-sweep inline **ONLY when ALL of** these hold: the diff is genuinely tiny (a few lines), touches no auth/org/schema, AND the PR is **not** in a RULE #7 sensitive category (auth / access-control / `organization_id` isolation, DB/Firestore schema or migrations, pricing/billing/subscription, destructive-or-bulk data ops, customer-facing surfaces that can leak internal data — e.g. the Owner Page / customer-approval flow). If the PR is sensitive OR the diff is non-trivial, **run the Workflow — no exceptions.** Do not talk yourself out of it with "I already reviewed this in /code-review" or "Codex only flagged one line": Codex reports the first wall, not the whole wall (Principle #1), and a sensitive change is exactly where a missed class is most expensive. Thoroughness here is cheaper than another paid Codex round.

Concretely: cart-model PR3 (#897) took **5 Codex rounds / 4 real blocks** because this exact skip was misapplied to a sensitive owner-page-approval diff — each round surfaced one more member of the same class (a return-submit clobber, a request-local total, a concurrent-tab conflict, a legacy-line bypass) that a single up-front whole-class review would have caught together.

**When the fix REPLACES a coarse invariant with a fine-grained one, enumerate before you push.** A blunt guard ("once the customer responds, freeze the WHOLE report") is safe precisely because it covers states you never had to think about — concurrent tabs, legacy/decision-less rows, hidden lines. Swapping in a fine-grained guard ("freeze each DECIDED line") silently drops every state the fine predicate doesn't recognize, and Codex will find them one at a time. Before re-pushing such a change: (1) list every state the coarse guard covered, (2) confirm the fine guard covers each (or intentionally opens it), and (3) prefer resolving the new predicate through the SAME function the rest of the system already trusts (e.g. a shared `resolveLineDecision` used by both the rollup and the lock) rather than a fresh re-derivation that can drift.

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

**On a SENSITIVE PR, verify the fix diff BEFORE the push — on EVERY push, including small follow-up rounds:** commit without pushing, re-run the Step 3 Workflow over the resulting diff (seed it with "these findings are believed fixed — verify they hold and hunt what the next round would find"), apply its must-fixes, then push once. **"This round's diff is only ~60 lines" is NOT an exemption** — #1355 ran the verification once (it caught a real P1), then fixed rounds 3–6 inline on exactly that reasoning and ate four more paid blocks, several of which were sitting in the earlier runs' outputs as mis-bucketed advisories or verifier-refuted findings. The per-round verification is cheaper than any one of those rounds. **Seed the CLASS as a predicate over the whole diff, not just the named finding** — reviewers verify the named sites and rubber-stamp the rest (#1345: round 1's verification confirmed the fixed helper and called the sibling mark-viewed "correct"; Codex round 2 blocked on it. The predicate "any write whose tenancy was proven by an earlier select" is what found the remaining members). For race/ordering classes, the predicate must cover ALL PAIRWISE ORDERINGS of ALL writers of the field — #1362 r2's verification modeled the snapshot race against one writer, called it safe-direction, and Codex blocked on a different pairing. Evidence (#1273/#1274, 2026-08-01): every pre-push verification run caught at least one real P1 the fix round had just introduced or missed (a UUID-vs-number filter that disabled a whole storage sweep, an unowned lease release, three write paths bypassing the new chokepoint); the single time it was skipped (#1274 r2) the next Codex round blocked on exactly what it would have found — the verification costs less than one paid round. Three probe rules from the same evidence: probe guards ONE AT A TIME (batch-probing N guards masks a fail-open one whose marker matches a neighbor); seed regression fixtures with PRODUCTION-SHAPED data (numeric ids where prod uses uuids made a green suite certify a dead code path); and when a fix HARDENS a fail-open test/guard, META-PROBE it — construct the exact broken build the old guard could not see and confirm the old guard passes against it while the new one fails (#1421: the meta-probe is what proved the `indexOf`-only 404 assertion really was blind to a success-response regression). **And never seed a blanket "pre-existing = out of scope" exclusion** — pre-existing code whose failure semantics the diff RECOMBINES is diff-introduced (#1361 r3: the profile-first reorder made pre-existing silent catches on the account deletes produce a NEW partial state — live account stripped of its profile under a success line; two verification rounds had excluded exactly those catches on "pre-existing" grounds, and Codex blocked on them). Scope exclusions to DESIGN CALLS only, never to interactions the diff touches.

Then **respect the sensitive carve-out**. `plan.sensitive` is **advisory** — confirm it with your own one-line reasoning, don't obey it blindly (the synth agent over-flags: a client-side filter/sort/render over data that's *already fetched and already org-scoped server-side* is NOT sensitive even though it shows customer-related fields). State the reasoning either way, then:
- **Not sensitive** → push and let auto-merge + the re-run Codex gate decide. Report the PR link and what class you fixed. Do NOT ask Dave to merge (RULE #7 default flow).
- **Sensitive** — the *fix itself* changes auth / org-isolation query scoping / DB schema / migration / pricing / billing / destructive-bulk ops / a customer-facing surface (the Owner Page customers see, not an internal dashboard) → push, then **explicitly ask Dave to review before merge** and surface the residual risks. Do not arm auto-merge.

Optionally watch the re-review instead of context-switching. **Don't whitespace-split `gh pr checks` output** — the check is named "Codex Review" (two words), so `awk '{print $2}'` reads the wrong column and you'll act on a stale verdict (this bit the first run). **And before reading ANY verdict, confirm the check run's `headSha` is your new commit** — right after a push, `gh pr checks`/`--watch` can settle on the PREVIOUS commit's runs (a re-block that is really the old round's result; #1357 burned a cycle on this — the "failing" Codex run predated the fix push, and a clean PASS posts no new comment, so the stale BLOCK comment stays the `last` one). Use JSON selection, and read the verdict from the *latest* Codex comment, not the tabular state:

```bash
gh run list --branch "$(git branch --show-current)" --limit 5 \
  --json databaseId,name,conclusion,headSha       # match runs to YOUR sha first
```

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
| Failure-path state machines | priority 1 (blind spot, #1222 r3) | every failure exit re-arms the UI; no advance/success before its write settles; optimistic writes roll back |
| Stale-echo / monotonicity | priority 1 (blind spot, #1222 r1/r4/r6) | bulk client writes echoing stale cache over server-progressed fields; one-way fields latch at the merge seam; freezes enforced on EVERY writer |
| Unattended-write contract | priorities 1–3 (blind spot, #1355 — 6 rounds, one clause each) | background/fire-and-forget writes: in-txn preconditions, full-write-set guards, funnel follow-ups (captured-value mirrors go IN the txn), input freshness, provenance stamps, genuinely-shared paid-call budget, in-progress flags cleared on every exit |
| Population-render matrix + accepted holes | priorities 1, 5 (blind spot, #1324 r2/r3) | a widened membership predicate admits a population no render surface handles (generic titles, empty bodies, double-rendered fallbacks); a diff comment documenting an "accepted hole" is what the gate blocks on — close one-line holes, don't essay them |

If `.github/codex/prompts/review.md` changes, glance at it and update the dimensions in `codex-recovery-workflow.js` to match.

## Success Criteria

- [ ] Confirmed the failing check is `Codex Review` (not Tests/CodeQL/Org-Scoping).
- [ ] Captured the full Codex comment + the full diff before fixing.
- [ ] Ran the multi-agent review (an inline pass is allowed ONLY for a tiny, non-auth/org/schema, NON-sensitive diff — sensitive PRs always run the Workflow).
- [ ] Worked `plan.fixes` (must-fix); routed `plan.advisory` to notes; escalated `plan.layerEscalations` to Dave rather than over-encoding.
- [ ] For each unit-testable fix: wrote the regression test, saw it RED, then GREEN, and kept it.
- [ ] Fixed the **whole class** for every finding — every `locations[]` entry, not just the flagged line.
- [ ] Local gates green: `check:org-scoping` (if org/auth), `check`, `/test:safe`.
- [ ] Self-reviewed the fix diff against Codex's rubric.
- [ ] Pushed; non-sensitive → auto-merge armed and reported; sensitive → Dave asked to review.

## Integration with Other Skills

- `/pre-push-mirror` — the **proactive** complement: runs `/code-review high` on the unpushed diff and triages by the mirror rules *before* the first push. Track record: PRs that ran it (#1419/#1420/#1421) passed Codex first-try; the one that skipped it (#1418) ate 2 paid rounds. Run `codex-fix` only when Codex blocks anyway — and seed it with the mirror's output (Step 2).
- `/app-testing` — for adding/repairing the Jest/Playwright coverage a fix needs.
- `/compound` — if a recovery surfaced a durable, non-obvious class worth recording.

## Troubleshooting

### Codex blocked again after the fix
The internal review missed a class. Read the new finding, find why the sweep didn't reach it (usually a grep too narrow, or a sibling in a file the map didn't tag), widen it, re-run from Step 3 on the new diff. One repeat is a tuning signal, not a loop — note it in Step 8.

**Stop-loss (~round 3) — recognize NON-CONVERGENCE (#1361, 6 rounds):** a destructive multi-system sequence (e.g. Firestore docs + Auth accounts — no atomicity) always has SOME abort window leaving partial state under a success line, so surgical fixes just relocate the window and each round finds the next one — even with a full verification Workflow before every push. When round ~3 arrives and the findings are still partial-state/false-success variants of the same destructive sequence, STOP fixing: (1) size the newest finding against LIVE data (a read-only query showing zero instances reframes it), (2) check whether it describes PRE-EXISTING behavior the diff merely sits near, then (3) present the user the real options — full convergent redesign, scope-reset to the never-flagged feature subset, park, or admin-merge over the gate. On #1361 the user chose scope-reset then admin-merge, three rounds after the pattern was visible; the feature subset itself had never been flagged once. **Second datapoint (#1362, 3 rounds): non-convergence is NOT only destructive sequences — a two-transaction CONSISTENCY structure (content write + separate provenance/denorm stamp) and an entity-wide scalar written by partial-field paths have the same relocating-window signature. Both stop-losses ended in scope-reset (revert the contested file to byte-identical main, ship the never-flagged subset) — lead the options list with it.** **Third datapoint + a NEW exit (#1401, 4 rounds, recovered without scope-reset): a multi-write REQUEST structure (one PATCH = generic update + N funnel writes) relocating partial-failure findings has a cheaper exit when the window only opens on a specific FIELD COMBINATION — reject the combined request shape at validation (422) so the ordering class becomes vacuous. Verify no legitimate client sends the shape FIRST (enumerate every call site); then the rejection is API-only and costs nothing. Add "make the conflicting shape unrepresentable" to the options list ahead of full redesign. Same recovery also produced the round-4 lesson: a gate that neutralizes one stale recorded verdict on re-entry must neutralize EVERY recorded verdict (authorized AND declined) — check verdict symmetry before pushing a staleness gate.**

### `gh pr view --json comments` returns no Codex comment
A clean PASS posts nothing, and the comment only appears on BLOCK/advisory/error. If the check is red but there's no comment, the review step errored (bad `OPENAI_API_KEY`) — the comment will say "produced no output"; that's an infra issue, not a code issue (rotate the secret), not something to fix in the diff.

### The "finding" is Dave's explicit design decision, not a bug
Don't admin-override or silently flip it to satisfy the gate. Split it out, fix the real bugs, and ask Dave about the design call (per "gate blocks on the user's design call"). **One resolution needs no ask:** when the reviewer's own stated alternative IS the epic's next planned leg (e.g. #1222 r5 blocked a staged rollout's gated window and suggested "ship the read surfaces in this PR" — which was PR 3d), fold that planned work into the PR instead of arguing the window or seeking an override. The design doesn't change; only the PR boundary does, and the locked plan already approved the work.

### Workflow returns zero verified findings but Codex blocked
Either the adversarial verifier was too aggressive, or Codex flagged something genuinely pre-existing/borderline. Re-read the Codex line directly against the code; if it's real, fix it by hand; if it's a Codex false positive, address it in the PR (a guard/comment/test) so the re-review passes — don't just re-push unchanged.
