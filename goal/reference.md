# `/goal` Reference

Deep reference for the `goal` skill. SKILL.md is the operating procedure; this is the "why" and the edge cases.

## Where the idea comes from

OpenAI Codex shipped `/goal` ("Goal mode"): a **persisted objective** the agent works toward across turns until it's achieved, paused, cleared, or budget-limited. Key facts from OpenAI's docs and the implementation:

- **Persistence:** one goal per thread in SQLite; statuses `active | paused | budget_limited | complete`; each goal has a UUID that resets on replacement.
- **Asymmetric tools:** the model can `create_goal` (objective + optional token budget) and `update_goal` (only to mark `complete`); `get_goal` is read-only. Pause/resume/budget are *system*-controlled — the model can't grant itself those.
- **Guidance:** *"Create a goal only when explicitly requested by the user or system/developer instructions; do not infer goals from ordinary tasks."*
- **Completion is declarative + budgeted:** marking complete returns a budget report (tokens/time used vs. limit). Budgets are enforced atomically; crossing the limit flips status to `budget_limited` and halts continuation.
- **Lifecycle UI:** `/goal` to view, `/goal pause|resume|clear`; states surfaced as pursuing/paused/achieved/unmet/budget-limited.

This skill reproduces the *behavior* in pure prompt + file state, and **adds an explicit independent verification subagent** — because in Codex the completion check is declarative (the model asserts done), whereas the most common failure mode of autonomous agents is exactly a false "done". An adversarial checker that reads only printed evidence is the cheap insurance against that.

## OpenAI's six components of a strong goal

1. **Outcome** — what should be true when work concludes.
2. **Verification surface** — the test/benchmark/report/artifact that proves success.
3. **Constraints** — what must not regress.
4. **Boundaries** — which files/tools/resources are permitted.
5. **Iteration policy** — how to choose the next action after each attempt.
6. **Blocked stop condition** — when to halt and report that no defensible path remains.

OpenAI's strong examples:
- *Performance:* "Reduce p95 checkout latency below 120 ms, verified by the checkout benchmark, while keeping the correctness suite green."
- *Research:* "Produce the strongest evidence-backed reproduction using available materials… end with a report separating reproduced mechanics, approximate results, blocked exact replay, and remaining uncertainty."

## Practitioner best practices (jdhodges, the aibyaakash Substack, r/codex)

- **Two-step authoring:** describe the work in plain language, ask the agent to draft a goal, then tighten the success condition, verification surface, constraints, and blocked-stop before running. Drafted goals are usually sharper than the first phrasing.
- **5-point pre-flight rubric:** (1) measurable artifact — what file/output marks done? (2) verification command — the one-liner that proves it; (3) allowed write scope — exact dir, rest read-only; (4) stop condition — the literal sentence/schema the agent must produce; (5) pause condition — what should trigger a pause.
- **Bad vs good:** `/goal improve auth` ❌ vs `/goal raise src/auth coverage from 38% to 75%, only edit src/auth and tests, stop when npm test passes and the coverage threshold is met` ✅.
- **Cost:** goals run **~2.6×–4.5×** a single prompt (multiple verification turns). Real r/codex data: a refactor burned ~20% of a weekly quota over 6.5h; a migration ~9% over 8h. Use only when value justifies it.
- **Sandbox honesty:** when a tool/service is unavailable, a good goal reports the limitation rather than fabricating — design the Blocked stop so honesty is the cheapest path.
- **Pause aggressively** if the agent drifts; run against scratch branches with read-only constraints.

### When it shines
Migrations with a test suite · coverage expansion · TDD feature builds · flaky-test reproduction · refactors with a validation loop · performance/benchmark targets · research audits with an inspectable artifact.

### When to skip
One-off edits · vague/subjective finish lines · no reliable completion condition · work where uncertainty should stay visible for a human to weigh.

## Verifier re-run vs evidence-only

The verification subagent (Step 5) has two modes:

- **Re-run (default for runnable surfaces).** The checker executes the verification command itself in a fresh, read/execute-only context (`Explore` — Bash + read, no Edit/Write) and judges from the output it observes. Strictly stronger than reading a paste: it catches a fabricated, stale, partial, or cherry-picked evidence block, and it can't "fix" the code to pass because it has no write tools. Use it for tests, coverage, builds, lint, benchmarks.
- **Evidence-only (Codex-parity fallback).** The checker reads the evidence you printed. Use only when the surface can't be reproduced independently — a research artifact judged by reading it, or a command that's expensive, flaky, or network/credential-bound where a second run would be unreliable or costly.

**Cost.** Re-run executes the surface twice per iteration (worker prints evidence, checker reproduces it). Negligible for a cheap deterministic command; for an expensive suite, have the checker run a **scoped subset** (the affected file/target) rather than dropping to evidence-only — a scoped independent run still catches fabrication.

**Isolation.** The checker runs against the same working tree, so it sees the worker's (possibly uncommitted) changes — correct, it's verifying the real current state. It needs no git worktree of its own because it's read/execute-only. If a goal's worker mutates global state a re-run would disturb, prefer evidence-only or a scoped read.

**Disagreement = checker wins.** If the re-run verdict contradicts the printed evidence, trust the checker's `observed` output and loop on the real gap — a contradiction usually means the paste was stale or partial.

## High-stakes verification: 3-checker majority

For goals where a false "achieved" is expensive, run the verification subagent **3× in parallel** with the same evidence and take the majority verdict. Give each a slightly different lens (correctness / completeness / does-the-evidence-actually-prove-it) so they catch different failure modes rather than agreeing by rote. Treat `blocked` from any checker as a signal to investigate before continuing.

## Optional hardening: a real Stop hook (out of the box scope)

This skill is pure-prompt: between turns nothing *forces* the session to keep going. To get Codex-grade "the session cannot end while a goal is active," add a **Stop hook** in `settings.json` (via `/update-config`) that re-injects "goal not yet verified — continue" unless the goal file is `paused`/`cleared`/`achieved`, with a runaway guard (a max-continuations counter, e.g. 500, env-overridable). Reference implementation: `github.com/jthack/claude-goal` (skill + `scripts/claude_goal.py` + SQLite + Stop hook). Adopt that directly if you want the full runtime version rather than the prompt-level one here.

Tradeoff to flag before adding the hook: it affects **every** session globally, not just goal runs, and a forgotten `/goal clear` means sessions won't end on their own.

## Sources

- OpenAI Codex — Goal mode / commands: `developers.openai.com/codex/app/commands`, `developers.openai.com/codex/cli/slash-commands`
- OpenAI Cookbook — "Using Goals in Codex": `developers.openai.com/cookbook/examples/codex/using_goals_in_codex`
- Implementation notes (asymmetric tools, SQLite, budget): gist `patleeman/b1b5768393f9bf2f60865b1defeeb819`
- Claude Code recreation (three-part prompt, secondary-model check): aibyaakash.com "/goal command Claude Code"
- Hands-on findings + rubric: `jdhodges.com/blog/codex-goal-feature-review/`
- Reference Stop-hook implementation: `github.com/jthack/claude-goal`
