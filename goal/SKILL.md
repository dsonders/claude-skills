---
name: goal
description: Run an autonomous, self-verifying goal loop — a Claude Code recreation of OpenAI Codex's /goal command. Claude turns an objective into a verifiable goal (outcome, verification surface, constraints, boundaries, iteration policy, blocked-stop), then repeatedly works → prints raw evidence → has an INDEPENDENT verification subagent judge achieved/unmet/blocked → iterates, until the finish line is verified, a turn/budget cap is hit, or it is blocked. Use when the user invokes /goal, or asks Claude to keep working autonomously toward a checkable finish line (tests pass, coverage threshold, every section filled, a benchmark target) without nudging every turn. Also handles lifecycle: /goal status, /goal pause, /goal resume, /goal clear, /goal complete. Skip for one-off edits, exploratory or subjective work, or any objective with no verifiable completion condition.
---

# Goal: Autonomous Self-Verifying Objective Loop

Recreates OpenAI Codex's `/goal` command for Claude Code. You (the agent) take an objective, harden it into a *verifiable* goal, then loop **work → print evidence → independent verification → iterate** until the finish line is objectively met, a cap is hit, or you are blocked. The defining idea: **you do not get to declare yourself done — a separate verification subagent reads your printed evidence and rules on it.**

This is a **pure-skill** implementation: no `settings.json` Stop hook, no Python, no SQLite. The loop runs in-session and persists its state to a file so `status`/`pause`/`resume` survive across turns and context compaction. (For true cross-turn "cannot stop until done" enforcement à la Codex, a Stop hook would be required — out of scope here; see "Differences from Codex".)

## When to Use This Skill

**Use it when:**
- The user types `/goal <objective>` or a lifecycle command (`/goal status|pause|resume|clear|complete`).
- The objective has a **clear finish line but an uncertain path** — the next step depends on what each attempt reveals.
- Completion is **checkable from evidence you can print**: tests pass, a coverage threshold, a benchmark target, every section of a brief filled, a comparison table with no blank cells, a build that compiles.
- The work spans **multiple iterations** and you'd otherwise need the user to nudge "keep going" each turn.

**Don't use it for** (do the work directly instead):
- One-off edits, single-file changes, or simple explanations — the verification overhead isn't worth it.
- **Exploratory or subjective work** ("make this nicer", "improve auth") — no objective finish line to verify against.
- Tasks needing human judgment mid-process, or a brief still being shaped.
- Anything where the completion condition can't be reduced to printable evidence. If you can't name the one command/artifact that proves "done", stop and turn it into a real goal first.

Related skills: `/loop` (run a prompt on an interval — pair with this for very long cross-turn runs); `/lab` (instrumented hypothesis-driven refinement); `/deep-research` (multi-source research harness). Use `/goal` when the spine is **verify-and-iterate toward one checkable finish line**.

## Core Principles

1. **The agent does not grade its own homework.** An independent verification subagent (fresh context) reads ONLY the evidence you printed and rules achieved/unmet/blocked. Default to *unmet* when evidence is missing.
2. **Evidence must be printed, not asserted.** The checker can't run commands or open files. Print raw proof into the conversation — test output, counts, the table, the diff, the benchmark number. "I verified it" is not evidence.
3. **No guessing, no placeholders.** Never fabricate a result, fill a cell with a guess, or stub to make the check pass. A blocked condition is reported as blocked, not faked.
4. **Bounded autonomy.** Every goal has a turn cap and (optionally) a token budget. Hitting a cap ends the run as *budget-limited* with an honest progress summary — it is not the same as achieving the goal.
5. **Verifiable conditions only.** "Good", "clean", "better" are not finish lines. Every finish-line condition must be objectively checkable.

## Command Surface

| Command | Action |
|---|---|
| `/goal <objective>` | Draft + lock a goal, then start the loop. |
| `/goal --turns N <objective>` | Same, with a turn cap of N (default 30, hard max 50). |
| `/goal --tokens 250K <objective>` | Same, with a soft token budget (advisory; reported, not hard-enforced). |
| `/goal` or `/goal status` | Show the current goal, its state, turn count, and last verdict. |
| `/goal pause` | Suspend the loop (state → `paused`); stop iterating. |
| `/goal resume` | Resume a paused goal from where it left off. |
| `/goal clear` | Delete the active goal and its state. |
| `/goal complete` | Force-mark the goal complete (user override of the checker). |

Dispatch on the args first: a lifecycle keyword (`status|pause|resume|clear|complete`) operates on the existing state file; anything else is a new objective.

## The Structured Goal

Before looping, convert the raw objective into these six components (from OpenAI's "Using Goals in Codex" guidance, plus the practitioner "prove it / show me" framing). This is the contract the verifier checks against.

1. **Outcome** — what must be true when work concludes. The end state.
2. **Verification surface** — the exact test / command / artifact / count that *proves* the outcome. The one-liner the checker relies on.
3. **Constraints** — what must NOT regress while working (e.g. "correctness suite stays green", "no public API changes").
4. **Boundaries** — which files/dirs/tools are in scope; everything else read-only.
5. **Iteration policy** — how to choose the next action after each attempt (e.g. "fix the single largest failing check first").
6. **Blocked stop condition** — when to halt and report instead of looping forever (e.g. "if a required service is unreachable, log it and stop — do not guess").

Template lives in `templates/goal.md`. One-line shape:

> *"`<outcome>` verified by `<verification surface>` while preserving `<constraints>`. Work only within `<boundaries>`. Between iterations, `<iteration policy>`. If blocked or no valid path remains, `<blocked stop condition>`."*

## Workflow

Make a todo list and work the steps in order.

### Step 0 — Dispatch
Read `<project>/.claude/goal-state.md` if it exists.
- Lifecycle keyword in args → perform it (show status / set paused / set/resume / delete file / mark complete) and stop.
- New objective + an *active* goal already exists → tell the user, offer to `clear` first. Don't silently stack goals (Codex allows one goal at a time).
- New objective + no active goal → continue to Step 1.

### Step 1 — Draft and lock the goal
- Parse the objective into the six components. If the objective is **vague or missing a verification surface**, draft a tightened version and show it to the user for a quick confirm (the two-step "describe → draft → tighten" workflow). A drafted goal is almost always sharper than the user's first phrasing.
- If the objective has **no checkable finish line**, say so and stop — don't start a loop you can't end.
- Set the turn cap (`--turns`, else default 30) and any token budget (`--tokens`).
- **For code goals:** recommend a scratch branch and confirm the write boundary. A vague goal on a dirty tree can burn budget on off-target changes.

### Step 2 — Initialize state
Write `<project>/.claude/goal-state.md` (format below) with the structured goal, `status: pursuing`, `turn: 0`, the cap, the budget, and an empty iteration log. This file is the durable record — it survives compaction, so on any later turn you can reload the goal and continue.

### Step 3 — Iterate (the loop)
Repeat until a termination condition (Step 5):

a. **Work** one focused increment toward the Outcome, within Boundaries, preserving Constraints, following the Iteration policy. Address the *top gap* from the previous verdict first.

b. **Print evidence.** Run the Verification surface and print the **raw** result into the conversation — the actual test summary, the count, the rendered table, the benchmark number, the relevant diff. Print proof for *every* finish-line condition. If a condition can't be evidenced, say why (that's a blocked/unmet signal, not something to paper over).

c. **Verify** — spawn the independent verification subagent (Step 4). It returns a structured verdict.

d. **Record** — append the iteration (what you did, evidence summary, verdict, top gap) to the state file; increment `turn`.

e. **Decide** — `achieved` → Step 5 (success). `unmet` & under cap → loop with the top gap as the next target. `blocked` → Step 5 (blocked). cap/budget reached → Step 5 (budget-limited).

### Step 4 — The verification subagent
Spawn a subagent (Agent tool; `Explore` or `general-purpose`) with a **fresh context** so it judges independently, not from your reasoning. Give it: the structured goal (all six components) and the **evidence text you printed this iteration** (paste it — the subagent can't see your conversation). Instruct it:

> You are an adversarial completion checker. Judge ONLY from the evidence provided below — do not assume, do not run anything, do not give benefit of the doubt. For each finish-line condition, decide whether the printed evidence *proves* it. If a condition has no supporting evidence, it is UNMET (never "achieved"). If progress is structurally impossible from here, it is BLOCKED. Default to `unmet` when uncertain.

Require this verdict shape (use the `schema` option so it's validated):

```json
{
  "status": "achieved | unmet | blocked",
  "met": ["conditions the evidence proves"],
  "unmet": ["conditions not proven by the evidence"],
  "top_gap": "the single most important thing to fix next (empty if achieved)",
  "evidence_gaps": ["claims that lacked printable proof"],
  "reasoning": "1-3 sentences"
}
```

For a high-stakes goal, run 3 checkers in parallel and take the majority (adversarial-verify pattern) — see `reference.md`.

### Step 5 — Terminate and report
- **Achieved:** state the goal met, list which conditions the checker confirmed, and print a budget report: `turns used / cap` and approximate tokens (or "budget N, soft limit not enforced"). Set `status: achieved`. Hand off whatever the goal's "show me" asked for.
- **Blocked:** execute the Blocked stop condition. Report what you tried, the exact blocker, and what's needed to unblock. Never fake a result to escape. Set `status: blocked`.
- **Budget-limited:** stop, set `status: budget-limited`, and give an honest progress summary — conditions met, conditions remaining, the current top gap, and a recommended next goal. This is explicitly *not* success.

## Guardrails

- **Turn cap** default 30, hard max 50 — a vague goal otherwise keeps going until *it* decides it's done, which can burn a lot of tokens (Codex goals run ~2.6×–4.5× a single prompt). Never raise the hard max silently.
- **Inject the no-guess constraint** into every iteration: "Do not guess. Do not use placeholders. If blocked, report it."
- **Scratch branch + read-only boundary** for code goals; confirm before writing outside the boundary.
- **Cost warning up front** for large goals so the spend is a choice, not a surprise.
- **One goal at a time.** Don't infer a goal from an ordinary request — only enter the loop on explicit `/goal` or an explicit "work autonomously until verified" ask.

## Goal-state file format

`<project>/.claude/goal-state.md` (create the `.claude/` dir if needed; add to `.gitignore` — it's session state, not a tracked artifact):

```markdown
# Goal State
status: pursuing        # pursuing | paused | achieved | unmet | blocked | budget-limited
turn: 2
turn_cap: 30
token_budget: 250000    # or "none"

## Objective (structured)
- Outcome: <...>
- Verification surface: <...>
- Constraints: <...>
- Boundaries: <...>
- Iteration policy: <...>
- Blocked stop: <...>

## Iteration log
- turn 1 — did <...>; evidence <...>; verdict unmet; top_gap <...>
- turn 2 — did <...>; evidence <...>; verdict unmet; top_gap <...>
```

## Examples

**Coverage goal:**
`/goal raise src/auth test coverage from 38% to 75%; only edit src/auth and its tests; done when the suite passes and coverage ≥75%.`
→ Outcome: coverage ≥75% & suite green. Verification surface: `npm test -- --coverage` summary. Constraints: no existing test breaks. Boundaries: `src/auth/**`. Iteration policy: cover the lowest-covered file next. Blocked stop: if a module needs un-mockable I/O, log it and stop.

**Research report goal:**
`/goal build report.md answering every section of brief.md, comparison table with no blank cells, every claim sourced.`
→ Verification surface: print all section headings, the filled table, and any unresolved questions. Blocked stop: mark an un-verifiable cell "Not verified" and explain — do not guess.

More worked examples and a Codex feature-comparison are in `reference.md`.

## Success Criteria

The skill run is complete when:
- [ ] The objective was hardened into the six structured components with a real verification surface (or rejected as un-verifiable).
- [ ] State was persisted to `.claude/goal-state.md` and kept current each turn.
- [ ] Each iteration printed raw evidence and was judged by an independent verification subagent.
- [ ] The loop ended on a genuine verdict (achieved/blocked) or a cap (budget-limited) — never a self-declared "done".
- [ ] The final report states which conditions were verified and the budget used.

## Troubleshooting

| Problem | Fix |
|---|---|
| Loop won't end / keeps finding new work | Finish line is too broad. Pause, re-scope to a single checkable condition, restart. |
| Checker keeps saying `unmet` but it looks done | You're asserting, not printing. Print the *raw* verification-surface output for the exact unmet condition. |
| Burning budget fast | Lower `--turns`; tighten Boundaries; confirm you're on a scratch branch. |
| Goal lost after context compaction | Reload `.claude/goal-state.md` (that's why it exists) and continue from the iteration log. |
| User wants true "can't stop until done" across turns | That needs a Stop hook in `settings.json` (use `/update-config`) — beyond this pure-skill scope; see `reference.md`. |

## Differences from Codex `/goal`

Codex's `/goal` is a runtime feature: a persisted objective in SQLite, asymmetric `create_goal`/`update_goal` tools, and system-controlled budget/pause. This skill reproduces the **behavior** (verify-and-iterate to a checkable finish line, lifecycle, budgets) in pure prompt + file state, and adds an **explicit independent verification subagent** (Codex's completion check is declarative). The one thing it can't do without a Stop hook is hard-block the session from ending between turns — here, `pause`/`resume` and the state file stand in for that.
