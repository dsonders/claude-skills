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
   **Every agent brief opens with this constraint, verbatim:** "NEVER `cd` in a Bash command — every command uses absolute paths (`git -C /abs/repo …`); a `cd` + relative path raises a permission prompt for Dave even under bypass mode." And tell Dave in one line, before launching, that helper agents may raise read-only permission prompts that are safe to approve (memory `feedback_no_cd_in_subagent_bash`).
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
- **Auth / login and org-isolation PRs still run `/pre-push-mirror` before their first push** —
  ONLY those two domains (Dave, 2026-09-04: the 9/5 audit found no measurable round reduction
  from the mirror on size-matched PRs, so it's kept where a miss is a security hole, not as a
  blanket step). Green=merge changes who approves, not how carefully we build.
- **Morning gate:** Dave reviews the ledger (below), reverts anything he dislikes (cheap —
  nothing is deployed), then republishes. Daytime/normal sessions keep CLAUDE.md RULE #7
  unchanged — this policy is scoped to overnight-build runs.

## Workflow

Make a todo list and work through it.

### Step 1 — Preflight
- Confirm every workstream is groomed: each open question has a ruling. If any remain, STOP
  and finish grooming in conversation — do not launch.
- Spend headroom: warn Dave if a recent run hit the usage cap (agents die silently on it).
- Keep the machine awake: `nohup caffeinate -dis >/dev/null 2>&1 & disown` (verify with `pgrep`) — `-i` alone does NOT stop lid/system sleep (2026-08-30: the machine slept 30 min in, killing all 4 agents mid-turn). Lid stays open. **Sleep recovery:** agents die with context INTACT — SendMessage each one "the machine slept; re-orient from disk (`git status`/`log` in your tree), continue" instead of respawning; all 4 resumed cleanly.
- Decide parallel vs serial NOW: parallel agents need an un-isolated manager (see Step 3);
  if this session already entered a worktree, plan one agent running workstreams in sequence.
- Note which PRs will be review-first anyway (un-ruled edges you already know about).
- **Cross-check §Queued against merged PRs** before writing the brief: `gh pr list --state merged
  --limit 40` and grep each Queued heading's key phrase against merged titles. A groom-pass doc PR
  can silently RE-INTRODUCE sections a ledger PR removed (#1603 relisted four items #1593–#1596
  had shipped; two agents launched on them, 2026-08-27). The BACKLOG is the source of rulings,
  not of ship state — git is.

### Step 2 — Write the durable brief
- Source of items: `docs/overnight/BACKLOG.md` in the app repo — consume the **Queued** section
  only (Queued = every question carries a ⛔ ruling). After the run, remove shipped items in a
  doc commit; git history is the archive.
- Copy `templates/brief-template.md` → session scratchpad (`overnight-<date>-brief.md`).
- One section per workstream: the rulings VERBATIM (mark each ⛔ don't-re-decide), files/
  lesson-docs to read, sensitivity notes, merge instruction per PR, prod-verify sentinel.
- **Size the PRs in the brief, not in the agent's head: ~800 non-test changed lines is the cap
  per PR** (CLAUDE.md RULE #7; 9/5 audit — blockers scale with lines at every size, ~1 per 900,
  and PRs ≥800 lines were 36% of PRs but 76% of blocking rounds, while <100-line PRs passed
  first try 94%). A workstream that will exceed it is split HERE into stacked PRs with named
  seams (server model → client → follow-ups), each independently mergeable. The agent reports
  `git diff --stat` before its first push; over the cap = split before pushing, not after a
  block. Stacked children still get no Tests/Codex until retarget (Step 3) — budget for it.
- Header rules come from the template — don't retype them.

### Step 3 — Launch build agents
- One Opus agent per workstream (`Agent` tool, `model: "opus"`), prompt built from
  `templates/agent-prompt-block.md` + a pointer to the brief section. Agents READ the brief
  file; the prompt stays short.
- Parallel only when file territories are disjoint; overlapping territories = ONE agent,
  sequential stacked PRs (rebase after each squash). **Stacked child PRs get NO Tests/Codex
  while their base is the parent branch** (`pull_request: branches: [main]`), and the parent's
  squash auto-closes the child + clears auto-merge — so a child's first real review lands
  after retarget: budget a fresh Codex round for it (memory `reference_stacked_pr_actions_gotchas`).
- Worktrees per CLAUDE.md RULE #4 (atomic `.claim`, or mint fresh). Never the primary checkout.
  **Claim with a FILE inside the dir** (`mkdir .claim && touch .claim/lock`): an empty `.claim/` dir was
  eaten by an agent's `git stash -u` round-trip twice on 2026-08-28 and the tree sat unlocked for most
  of the run. **Manager shell hygiene:** a `cd <worktree>` inside any manager Bash command PERSISTS as
  the session cwd (subagents launched afterwards inherit the pin and `EnterWorktree` is refused) — end
  every worktree command with `cd <primary>` or run it as `git -C`.
- **Shared `.git`, moving base (2026-09-05, #1825 wiped MPI-9 off main, CI stayed green):** agents never
  `git reset --soft <remote ref>` to squash — squash via `rebase -i`/`--amend` on the branch's own history —
  and every push runs `git fetch origin && git diff origin/main...HEAD --stat` (three dots) IN THE SAME Bash
  call and confirms only the PR's files. A squash whose `--stat` deletes test files = stop the line
  (`git grep <sibling symbol> origin/main`). A pure revert of a safety change is un-mergeable by construction
  (Codex refuses it) — re-land in the same PR. Memory `feedback_no_reset_soft_squash_shared_git`.
- **Agent hygiene that bit 2026-09-05:** commit BEFORE any script that touches git (probe/eval scripts
  `git checkout` files — 3 uncommitted-fix wipes); long silent commands (eval, full sweeps, probe loops) trip
  the 10-min stream watchdog — background/tee; the scratchpad is SHARED — unique per-agent filenames
  (`pr-body.md` collision published the wrong PR body); jest in a `.claude` worktree tests the PRIMARY unless
  cwd is the tree (`npm --prefix <tree> run test -- …`); `cp` of `.env` into a minted tree is denied — symlink.
- **Parallel is only possible if the MANAGER session is not worktree-isolated.** A session that
  entered a worktree (EnterWorktree / `.claude/worktrees/*` cwd) pins EVERY subagent's shell to that
  one tree — a second agent in build-2/build-3 fails every Bash call with "This session is isolated
  in the worktree … refusing to run" (2026-08-27 run 2: Agent B and its helper were dead on arrival).
  Decide in Step 1: (a) run the manager from the primary checkout (read-only for the manager; agents
  claim their own trees) when ≥2 disjoint workstreams justify parallelism, or (b) serialize all
  workstreams through the one claimed tree (5 PRs took ~3h serially — usually fine). Never let an
  agent route around the guard by entering another agent's live tree or spawning helper agents.

### Step 4 — Manager loop (triage rules)
On each agent report / Codex block:
- **"Dave reviews" in the launch prompt ≠ hold a green PR.** Under the overnight policy a Codex-clean
  PR whose rulings are all Dave's gets auto-merge ARMED even if the prompt labeled it Dave-reviews; only
  an un-ruled decision parks it (Dave, 2026-08-29: "If codex is clean… isn't the protocol… merge?").
- **A verifier/grounding feature or a client-value/clock FENCE = one Codex finding per input path.**
  #1655 took 17 rounds (facts/recommendation/cue × words/numbers/negation/clauses/sources), #1650 took
  12 (wall-clock fence patched 3× before the model was replaced by a server generation). On the FIRST
  block of that shape, stop patching the flagged line: enumerate the whole matrix (or replace the
  instrument) in one round — see app `docs/lessons-learned/video-batch-2026-08-28.md`.
  **Since #1827 (2026-09-05) a phrasing counterexample on the three heuristic-parser files
  (`mpi-voice-processor.ts`, `video-findings.ts`, `video-talking-points-job.ts`) is P2 —
  advisory, not a block.** Don't patch the regex for it; add the sentence to the eval corpus
  (`__tests__/eval/mpi-matching/run.ts`) and `npm run eval:mpi` is the gate. What still
  blocks there: fabrication on the primary AI path, control-flow loss/dup, org-scoping, crashes.
- **Real defect in groomed scope** → agent fixes the whole class, ONE re-push. Second block →
  agent stops; manager triages. "Whole class" = a CENSUS of every consumer of the derivation
  (grep the field/flag + every `resolveStage(`/`isTerminalStage(` in touched files), listed in
  the PR body with a verdict per site — not "every site I edited". #1595 claimed "closed as a
  class" twice and Codex found the un-edited consumer both times (4 rounds, one class).
- **Finding = an un-ruled decision** → park the PR with the question stated plainly; ledger it.
- **Finding sized by data you can get** → run a read-only Firestore probe (memory:
  `reference_firestore_readonly_probe_recipe`) and convert "can't size the population" into a
  decision with evidence. Read-only needs no permission.
- **~7 Codex rounds on one PR** → hand to a FRESH agent with a narrow brief; round-N agents
  self-report judgment decay and they're right. Also: deep permission/model rewrites generate
  their own review surface — next time, split the PR.
- **Last small Codex-endorsed finding at night** → hold it and batch with Dave's morning
  decisions (one paid round instead of two) UNLESS the PR is otherwise mergeable tonight.
- **Re-firing dropped gates** → only ONE close/reopen, after `gh pr view --json mergeable` reads
  MERGEABLE (events fired during UNKNOWN are dropped), then re-arm auto-merge. Every extra
  reopen = a duplicate Codex run on identical code, and a second run CAN return a different
  verdict (#1595: pass, then block) — it's a required check, so the stricter one stands.
- **Eval-gated PRs:** a PROMPT addition is a behaviour change — require a per-case differential on the CRIT
  cases (OLD / branch / branch-minus-prompt-hunk ×6), not just a green eval; a hand-rolled scorer must IMPORT
  the eval's assertion (a lenient re-implementation called a real regression "a flake"); never read the rounded
  "100%" — compare exact counts (2026-09-05: 209/210 printed 100% and passed).
- **~7 rounds → fresh agent** stays; also split when the reviewer finds a NARROWER escape each round on one
  predicate (both → fallback → numeric → spoken): define the vocabulary once, table-driven test.
- **Sentinel strings** → copy from the MERGED diff yourself, never from the agent's report (a curly
  ’ vs ' made a live deploy read as absent; 2026-08-27 an agent named a FUNCTION as its sentinel —
  minification mangles identifiers, so it read as "not live" — and another reported an object key
  "removed" that the merged diff still added). Valid sentinels: a user-visible string literal, a
  `data-testid`, or an OBJECT KEY (property names survive minification); confirm with
  `git diff <merge>~1 <merge> -- client/src | grep '^+' | grep <string>` before `verify:deploy`.
  Server-only literals need a curl, not a bundle grep.
- **Agent transcript lost** (account reset, cap) → spawn fresh; the brief and working files
  on disk are the state. Never re-litigate rulings from memory.

### Step 5 — Morning ledger

**Morning review protocol (Dave's preferred flow, 2026-08-31):** after delivering the ledger, walk the needs-Dave items ONE at a time — a succinct briefing (user-visible before/after table, review state, what's baked in that he hasn't ruled) ending in ONE call with a rec; EXECUTE each ruling (merge/retarget/fix) before briefing the next item. Stacked children retarget via `git rebase --onto origin/main <ORIGINAL fork point>` — after the parent was itself rebased, its branch tip is NOT the child's upstream (memory `reference_stacked_pr_actions_gotchas`).

Produce the debrief from `templates/ledger-template.md`: bottom line first; one plain-language
line per merged PR (what a user sees before/after) + `git revert -m 1 <sha>` command; parked
PRs with their question reduced to a one-word-answerable ask; hard-floor items awaiting
execution; then the checklist (republish → smoke → sentinels → kanban → fixtures cleanup).
Dave reads, reverts if needed, republishes.

### Step 6 — After republish
- `npm run smoke:prod`; `npm run verify:deploy -- --expect "<sentinel>"` per PR (collect
  sentinels in the brief as you go — client-bundle strings only, never server-only literals).
- **Live-verify EVERY PR's user-facing surfaces on prod, per actor** — not one representative flow. 2026-09-01: the full pass found 4 client misses in a PR that had 12k green tests + mirror + Codex-clean (#1688 → fix #1705). Protocol: smoke FIRST; then 1–2 Opus agents on disjoint surfaces, TD1 only, fixtures closed on exit, verdict PROVED / FAILED-with-evidence / NOT-DRIVABLE-why per item, evidence in the scratchpad; a PR-body line "pinned by tests, not seen in a browser" names the first surfaces to drive.
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
- `/pre-push-mirror` — auth/login + org-isolation PRs ONLY, before first push
- `/codex-fix` — available to agents for a full recovery on a blocked PR
- `/handoff-session` — NOT needed mid-run; the brief is the handoff

## Troubleshooting
- **Every workflow dies in seconds with 0 steps, repo-wide** → GitHub org BILLING (failed payment /
  spending limit), not code: read the job's annotation (`gh api …/check-runs/<id>`). Only Dave
  can clear it; then `gh run rerun` the killed runs.
- **Agent dies silently, no notification** → check the usage cap first (the documented cause);
  respawn from the brief.
- **Two agents want the same file** → you mis-planned Step 3; stop one, convert to stacked PRs.
- **A merged PR looks wrong in the morning** → revert before republish; nothing shipped.
- **Codex keeps finding new issues in each round's new code** → that's the split signal, not a
  retry signal.
