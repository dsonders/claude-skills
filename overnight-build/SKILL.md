---
name: overnight-build
description: Run an autonomous overnight (or unattended) build of groomed backlog items in the RO-bot app — durable brief → parallel Opus build agents in worktrees → green=merge policy → morning ledger for pre-republish review. Use when Dave says "run overnight-build", "build these overnight / while I sleep", "start the overnight run", or asks to execute a set of groomed cards unattended. Requires every item to be GROOMED (all decisions ruled) first; grooming itself happens in normal conversation before invoking this skill.
---

# Overnight Build: Unattended Multi-PR Run from a Groomed Brief

Executes a batch of groomed work items overnight: one durable brief on disk, one build
agent per workstream in isolated worktrees, auto-merge on fully green checks, and a
morning ledger Dave reviews **before republishing** — the deploy button is the human gate,
not the merge button. First validated 2026-08-25 (P1 batch: 8 PRs, #1555–#1564).

## When to Use

**Use when:**
- Dave asks to run groomed items overnight / unattended ("run overnight-build", "build while I sleep")
- Multiple independent workstreams are fully groomed and the pipeline shouldn't wait for approvals

**Don't use for:**
- Ungroomed work — grooming (interview → locked rulings) is a PREREQUISITE, done in normal
  conversation first. An overnight run without rulings guesses, and guessing is the failure
  mode this skill exists to prevent.
- A single daytime PR (just build it), iterative refinement (`/lab`), or a single verifiable
  objective (`/goal`).

## Core Principles

1. **The brief is the contract.** Every ruling written verbatim into a file on disk before any
   agent launches. The run must survive session death, account resets, and agent crashes.
2. **Merge ≠ deploy.** Nothing reaches a customer until Dave republishes on Replit. That is
   why green=merge is safe: the human gate moved to the deploy boundary.
3. **An un-ruled decision parks the PR** — regardless of how green it is or what category it's in.
4. **Park, don't guess.** Ambiguity goes in the PR body and the ledger, never into code.
5. **Fable manages, Opus builds.** The manager session briefs, triages, probes, and reports;
   it does not write feature code.
6. **Paid reviews are budgeted.** Codex rounds cost money; the triage rules below decide when
   to spend another one.

## Merge Policy (Dave's ruling, 2026-08-25 — applies to overnight-build runs only)

- **Green = merge**, sensitive categories included (auth, schema, permissions), PROVIDED the
  PR implements only groomed rulings. Arm `gh pr merge --auto --squash` on every PR.
- **Parks regardless of green:** any PR carrying a decision the brief didn't cover.
- **Hard floor — never auto-EXECUTE overnight, even if the code merges green:**
  1. Anything that RUNS against production data (backfills, migrations, bulk deletes —
     merging the script is fine; executing it waits for Dave)
  2. Pricing / billing changes
  3. Destructive or irreversible operations
  These aren't reviewable-by-revert; a bad one is already spent.
- **Blocking-domain PRs still run `/pre-push-mirror` before their first push** (org-isolation,
  auth, schema, customer-facing, unattended writes). Green=merge changes who approves, not
  how carefully we build.
- **Morning gate:** Dave reviews the ledger (below), reverts anything he dislikes (cheap —
  nothing is deployed), then republishes. Daytime/normal sessions keep CLAUDE.md RULE #7
  unchanged — this policy is scoped to overnight-build runs.

## Workflow

Make a todo list and work through it.

### Step 1 — Preflight
- Confirm every workstream is groomed: each open question has a ruling. If any remain, STOP
  and finish grooming in conversation — do not launch.
- Spend headroom: warn Dave if a recent run hit the usage cap (agents die silently on it).
- Keep the machine awake: `nohup caffeinate -i >/dev/null 2>&1 & disown` (verify with `pgrep`).
- Note which PRs will be review-first anyway (un-ruled edges you already know about).

### Step 2 — Write the durable brief
- Source of items: `docs/overnight/BACKLOG.md` in the app repo — consume the **Queued** section
  only (Queued = every question carries a ⛔ ruling). After the run, remove shipped items in a
  doc commit; git history is the archive.
- Copy `templates/brief-template.md` → session scratchpad (`overnight-<date>-brief.md`).
- One section per workstream: the rulings VERBATIM (mark each ⛔ don't-re-decide), files/
  lesson-docs to read, sensitivity notes, merge instruction per PR, prod-verify sentinel.
- Header rules come from the template — don't retype them.

### Step 3 — Launch build agents
- One Opus agent per workstream (`Agent` tool, `model: "opus"`), prompt built from
  `templates/agent-prompt-block.md` + a pointer to the brief section. Agents READ the brief
  file; the prompt stays short.
- Parallel only when file territories are disjoint; overlapping territories = ONE agent,
  sequential stacked PRs (rebase after each squash).
- Worktrees per CLAUDE.md RULE #4 (atomic `.claim`, or mint fresh). Never the primary checkout.

### Step 4 — Manager loop (triage rules)
On each agent report / Codex block:
- **Real defect in groomed scope** → agent fixes the whole class, ONE re-push. Second block →
  agent stops; manager triages.
- **Finding = an un-ruled decision** → park the PR with the question stated plainly; ledger it.
- **Finding sized by data you can get** → run a read-only Firestore probe (memory:
  `reference_firestore_readonly_probe_recipe`) and convert "can't size the population" into a
  decision with evidence. Read-only needs no permission.
- **~7 Codex rounds on one PR** → hand to a FRESH agent with a narrow brief; round-N agents
  self-report judgment decay and they're right. Also: deep permission/model rewrites generate
  their own review surface — next time, split the PR.
- **Last small Codex-endorsed finding at night** → hold it and batch with Dave's morning
  decisions (one paid round instead of two) UNLESS the PR is otherwise mergeable tonight.
- **Agent transcript lost** (account reset, cap) → spawn fresh; the brief and working files
  on disk are the state. Never re-litigate rulings from memory.

### Step 5 — Morning ledger
Produce the debrief from `templates/ledger-template.md`: bottom line first; one plain-language
line per merged PR (what a user sees before/after) + `git revert -m 1 <sha>` command; parked
PRs with their question reduced to a one-word-answerable ask; hard-floor items awaiting
execution; then the checklist (republish → smoke → sentinels → kanban → fixtures cleanup).
Dave reads, reverts if needed, republishes.

### Step 6 — After republish
- `npm run smoke:prod`; `npm run verify:deploy -- --expect "<sentinel>"` per PR (collect
  sentinels in the brief as you go — client-bundle strings only, never server-only literals).
- Live-verify the highest-risk surface by hand (browser) — one representative flow per PR.
- Update the kanban cards; write/refresh the memory entry (rulings + follow-ups) so no future
  session re-litigates; `/compound` if the run surfaced a reusable lesson.

## Success Criteria
- [ ] Brief on disk before the first agent launched; zero decisions invented overnight
- [ ] Every PR either merged green, or parked with a stated question
- [ ] Nothing on the hard floor executed
- [ ] Morning ledger delivered; Dave's asks reduced to one-word answers
- [ ] Post-republish smoke + sentinels green; memory updated

## Integration
- Grooming (conversation, before) → **overnight-build** → `/compound` (after)
- `/pre-push-mirror` — blocking-domain PRs, before first push
- `/codex-fix` — available to agents for a full recovery on a blocked PR
- `/handoff-session` — NOT needed mid-run; the brief is the handoff

## Troubleshooting
- **Agent dies silently, no notification** → check the usage cap first (the documented cause);
  respawn from the brief.
- **Two agents want the same file** → you mis-planned Step 3; stop one, convert to stacked PRs.
- **A merged PR looks wrong in the morning** → revert before republish; nothing shipped.
- **Codex keeps finding new issues in each round's new code** → that's the split signal, not a
  retry signal.
