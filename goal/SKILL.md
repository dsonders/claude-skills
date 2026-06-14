---
name: goal
description: Run an autonomous, self-verifying goal loop — a Claude Code recreation of OpenAI Codex's /goal command. Claude turns an objective into a verifiable goal (an outcome plus the evidence that proves it), then loops work → print raw evidence → an INDEPENDENT verification subagent judges achieved/unmet/blocked → iterate, until the finish line is verified, a turn/budget cap is hit, or it is blocked. Before executing it runs a clarity gate — when the objective or its completion criteria are underspecified, it interviews the user one question at a time to lock the end state and required evidence, and won't start the loop until that threshold is met. Use when the user invokes /goal, or asks Claude to work autonomously toward a checkable finish line (tests pass, coverage threshold, a benchmark target) without nudging every turn. Also handles lifecycle commands (status, pause, resume, clear, complete). Skip one-off edits, exploratory or subjective work, or objectives with no verifiable completion.
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

1. **Clarity before autonomy.** Never start the loop on a fuzzy objective. The **end state** and the **evidence that proves it** must be unambiguous first — interview the user to that threshold (Step 1). A vague goal is the #1 way these loops waste budget and drift off-target.
2. **The agent does not grade its own homework.** An independent verification subagent (fresh context) rules achieved/unmet/blocked — and **re-runs the verification surface itself** when it's runnable (read/execute-only, so it can't fabricate or fix), falling back to reading your printed evidence only when the surface can't be re-run. Default to *unmet* when proof is missing.
3. **Evidence must be printed, not asserted.** The checker can't run commands or open files. Print raw proof into the conversation — test output, counts, the table, the diff, the benchmark number. "I verified it" is not evidence.
4. **No guessing, no placeholders.** Never fabricate a result, fill a cell with a guess, or stub to make the check pass. A blocked condition is reported as blocked, not faked.
5. **Bounded autonomy.** Every goal has a turn cap and (optionally) a token budget. Hitting a cap ends the run as *budget-limited* with an honest progress summary — it is not the same as achieving the goal.
6. **Verifiable conditions only.** "Good", "clean", "better" are not finish lines. Every finish-line condition must be objectively checkable.

## Command Surface

| Command | Action |
|---|---|
| `/goal <objective>` | Interview to clarity (if needed), lock the goal, then start the loop. |
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

### Step 1 — Clarity gate (interview to threshold)

**Do not start the loop until the goal is clear enough to verify.** Parse the objective, then test it against the clarity threshold — both must be true:

- **End state** — you can state, in one unambiguous sentence, what is true when the work is done (no vague adjectives like "good", "clean", "robust", "better").
- **Required completion evidence** — you can name the exact command / artifact / observable that *proves* the end state, say **what a passing result looks like** (the threshold or expected value), and confirm it's something you can actually produce and print.

Run this self-test: *Can I write the end state as one concrete sentence? Can I name the evidence that proves it and what "passing" looks like? Can I produce that evidence?* If any answer is "no", **interview the user before doing anything else** — do not begin work, do not write state.

**Interview rules:**
- Ask **one focused question at a time**, conversationally — never a multi-question form or a wall of questions. **Lead with a recommended answer** the user can confirm or tweak (e.g. *"I'd verify this with `npm test -- --coverage` and call it done at ≥80% — good, or a different bar?"*), not an open-ended *"what do you want?"*.
- Ask only about what's genuinely missing or ambiguous. If the objective already meets the threshold (e.g. a fully-filled template, or an already-precise goal), **skip the interview** and go to Step 2.
- Resolve the **end state** and **completion evidence** first — those are the mandatory gate. Draft sensible defaults for the rest (constraints, boundaries, iteration policy, blocked-stop) and fold a quick confirm into the same flow.
- Keep it tight: aim to clear the gate in **≤3–4 questions**. If it's still unclear after that, say exactly what's still ambiguous and ask the user to decide — never guess your way past the gate.
- If it becomes clear the objective has **no verifiable completion condition**, stop and say so. Don't start a loop you can't end — offer to reframe it as a checkable goal, or to just do the work directly without `/goal`.

### Step 2 — Lock the goal
- Convert the (now-clear) objective into the six structured components and **restate the full goal back to the user for one go-ahead** before looping.
- Set the turn cap (`--turns`, else default 30) and any token budget (`--tokens`).
- **For code goals:** recommend a scratch branch and confirm the write boundary. A vague goal on a dirty tree can burn budget on off-target changes.

### Step 3 — Initialize state
Write `<project>/.claude/goal-state.md` (format below) with the structured goal, `status: pursuing`, `turn: 0`, the cap, the budget, and an empty iteration log. This file is the durable record — it survives compaction, so on any later turn you can reload the goal and continue.

### Step 4 — Iterate (the loop)
Repeat until a termination condition (Step 6):

a. **Work** one focused increment toward the Outcome, within Boundaries, preserving Constraints, following the Iteration policy. Address the *top gap* from the previous verdict first.

b. **Print evidence.** Run the Verification surface and print the **raw** result into the conversation — the actual test summary, the count, the rendered table, the benchmark number, the relevant diff. Print proof for *every* finish-line condition. If a condition can't be evidenced, say why (that's a blocked/unmet signal, not something to paper over).

c. **Verify** — spawn the independent verification subagent (Step 5), passing it the verification command(s) so it can **re-run the surface itself** (the default for runnable surfaces). It returns a structured verdict.

d. **Record** — append the iteration (what you did, evidence summary, verdict, top gap) to the state file; increment `turn`.

e. **Decide** — `achieved` → Step 6 (success). `unmet` & under cap → loop with the top gap as the next target. `blocked` → Step 6 (blocked). cap/budget reached → Step 6 (budget-limited).

### Step 5 — The verification subagent
Spawn a subagent with a **fresh context** so it judges independently, not from your reasoning. Pick the mode by the verification surface — **prefer re-run**:

- **Mode A — Re-run (default when the surface is runnable).** Use this whenever the verification surface is a deterministic, reasonably cheap command (tests, coverage, build, lint, benchmark). The checker executes the surface *itself* and judges from what it observes — this catches a fabricated, stale, or cherry-picked paste, which evidence-only cannot. Spawn an **`Explore`** subagent: it can run Bash and read, but **cannot Edit/Write**, so it can't quietly make the goal pass. Give it the structured goal, the **exact** verification command(s), the pass threshold, and the boundary. Instruct it:

  > You are an adversarial completion checker. Run the verification command(s) below yourself, exactly as written, and judge ONLY from the output you observe — ignore any result you were told to expect. Do NOT edit, write, or fix anything; you are read/execute-only. For each finish-line condition, decide whether your observed output proves it; if not, it is UNMET. If a command can't run (missing dep, blocked service), it is BLOCKED — report the error, do not guess. Default to `unmet` when uncertain. Put the raw output you saw in `observed`.

- **Mode B — Evidence-only (fallback, Codex-parity).** Use when the surface is **not** independently runnable — a research artifact judged by reading it, or an expensive / flaky / network-bound command. Give the checker the structured goal + the **evidence text you printed** (paste it — the subagent can't see your conversation). Instruct it:

  > You are an adversarial completion checker. Judge ONLY from the evidence provided — do not assume, do not give benefit of the doubt. For each finish-line condition, decide whether the printed evidence *proves* it. No supporting evidence → UNMET. Structurally impossible → BLOCKED. Default to `unmet` when uncertain.

Require this verdict shape (use the `schema` option if your spawn path supports it; otherwise tell the subagent to return exactly this JSON):

```json
{
  "status": "achieved | unmet | blocked",
  "independent_run": true,
  "met": ["conditions proven"],
  "unmet": ["conditions not proven"],
  "top_gap": "the single most important thing to fix next (empty if achieved)",
  "evidence_gaps": ["claims that lacked printable proof"],
  "observed": "raw output the checker ran (Mode A) or read (Mode B)",
  "reasoning": "1-3 sentences"
}
```

`independent_run` is `true` only when the checker re-ran the surface (Mode A). **If a re-run verdict disagrees with your printed evidence, the checker is right** — trust its `observed` output (you likely pasted stale or partial results) and loop on the real gap.

Cost note: re-run executes the surface a second time per iteration. If that's expensive, have the checker run a **scoped subset** (e.g. just the affected test file) rather than dropping to evidence-only. For a high-stakes goal, run 3 checkers in parallel and take the majority, each with a different lens — see `reference.md`.

### Step 6 — Terminate and report
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
- [ ] The clarity gate was satisfied before any execution — end state and required completion evidence were unambiguous (interviewed one question at a time if not).
- [ ] The objective was hardened into the six structured components with a real verification surface (or rejected as un-verifiable).
- [ ] State was persisted to `.claude/goal-state.md` and kept current each turn.
- [ ] Each iteration printed raw evidence and was judged by an independent verification subagent — which re-ran the verification surface itself when it was runnable (`independent_run: true`), not just read the paste.
- [ ] The loop ended on a genuine verdict (achieved/blocked) or a cap (budget-limited) — never a self-declared "done".
- [ ] The final report states which conditions were verified and the budget used.

## Troubleshooting

| Problem | Fix |
|---|---|
| Objective is vague / no clear finish line | Don't start the loop. Interview to the clarity threshold (Step 1) — lock the end state + the evidence that proves it — or decline and do the work directly. |
| Loop won't end / keeps finding new work | Finish line is too broad. Pause, re-scope to a single checkable condition, restart. |
| Checker keeps saying `unmet` but it looks done | You're asserting, not printing. Print the *raw* verification-surface output for the exact unmet condition. |
| Burning budget fast | Lower `--turns`; tighten Boundaries; confirm you're on a scratch branch. |
| Goal lost after context compaction | Reload `.claude/goal-state.md` (that's why it exists) and continue from the iteration log. |
| User wants true "can't stop until done" across turns | That needs a Stop hook in `settings.json` (use `/update-config`) — beyond this pure-skill scope; see `reference.md`. |

## Differences from Codex `/goal`

Codex's `/goal` is a runtime feature: a persisted objective in SQLite, asymmetric `create_goal`/`update_goal` tools, and system-controlled budget/pause. This skill reproduces the **behavior** (verify-and-iterate to a checkable finish line, lifecycle, budgets) in pure prompt + file state, and adds an **explicit independent verification subagent** (Codex's completion check is declarative). The one thing it can't do without a Stop hook is hard-block the session from ending between turns — here, `pause`/`resume` and the state file stand in for that.
