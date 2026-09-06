---
name: compound
description: Capture learnings after a feature or session so future work compounds — technical lessons AND how Claude and the user work together. Net-zero-or-better on always-loaded files: updates existing docs instead of duplicating, prunes as much as it adds, and routes process learnings into memory.
---

# Compound: Knowledge Capture & Pruning

Formalizes the "compound" step of compound engineering: capture learnings so each unit of work makes the next one easier, **WITHOUT adding bloat**. Every step that adds knowledge has a matching gate, an update-don't-duplicate check, or a pruning companion.

## Core Philosophy

> "Each unit of engineering work should make subsequent units easier — not just documented more."

The learning loop:
1. Patterns get documented (or an existing doc gets refreshed) so they can be reused
2. Decisions get recorded so they don't get re-debated
3. Failures get encoded into rules/hooks to prevent recurrence
4. **Collaboration frictions get encoded into memory** so Claude and the user work together better next time
5. Repeated workflows get turned into skills or commands
6. **Stale knowledge gets deleted** so signal-to-noise stays high

If a session adds more to the always-loaded files (AGENTS.md — the shared rulebook — and the CLAUDE.md that imports it, design.md, any Pattern Index, MEMORY.md) than it removes, you're probably compounding in the wrong direction. Dead weight degrades compliance on *every other* rule.

**Two artifacts compound, not one.** Most compound workflows only capture *technical* lessons. This one also captures *process* lessons — what this session revealed about how Claude and the user should work together — because improving the collaboration compounds across every future feature, not just the next one in this domain.

## When to Use

- Just completed a significant feature or bug fix
- Session is ending and valuable learnings should be preserved
- Discovered a pattern, or a friction in how we worked, worth encoding
- A bug was tricky and the fix should prevent recurrence

Don't use for:
- Active debugging (use `deep-debug`)
- Writing tests (use `app-testing`)
- Research tasks (use `tech-research`)

## Modes

| Mode | When | Behavior |
|---|---|---|
| **Interactive** (default) | A human is in the loop | Lead with a recommendation on judgment calls; ask only where the call is genuinely the user's. End conversationally. |
| **Non-interactive** | Invoked by another skill (e.g., `handoff-session`), or the request says "headless"/"auto"/"just compound it" | No blocking questions. Take the conservative default at every gate (capture + full prune; gates default NO). Emit the compact report (see end) instead of back-and-forth. |

Both modes run the same steps and produce the same artifacts — non-interactive just stops asking and reports.

## Delegation (token economics)

**Every agent brief opens with this constraint, verbatim:** "NEVER `cd` in a Bash command — every command uses absolute paths (`git -C /abs/repo …`); a `cd` + relative path raises a permission prompt for Dave even under bypass mode." And tell Dave in one line, before launching, that helper agents may raise read-only permission prompts that are safe to approve (memory `feedback_no_cd_in_subagent_bash`).

When the main session runs a premium model (Fable) and cheaper capable agents exist (Opus), the read-heavy and draft-heavy steps delegate; every gate and judgment stays in the main loop. This also keeps the bulk reads OUT of the main session's context — which matters, since compound usually runs when that context is at its heaviest.

- **Delegate to ONE background agent (Agent tool, `model: "opus"`)**: Step 1's `git diff`/`git log` gather (return a change summary, not the raw diff), Step 2.7's overlap grep (return candidate docs + their 5-dimension scores + quoted evidence), Step 7's prune sweep (return candidates + evidence — the agent never deletes), and — once the main session has decided what to capture — Step 3's doc drafting against the template (main session reviews for accuracy + terseness per Step 8).
- **Keep in the main loop**: Step 1's process/collaboration reflection (it's about THIS conversation, which no agent can see), the Step 4/5 gates, Step 6 memory writes (small, high-precision, session-context-dependent), Step 6.5's fact-ripple judgment, and all deletions + commits (Steps 7–9).
- Main session on a non-premium model → skip delegation; coordination overhead beats the savings.

---

## Workflow

### Step 1: Gather Context

```bash
git diff main...HEAD        # what changed
git log main..HEAD --oneline # how it got there
```

Answer internally — the last two are the ones most workflows skip:
- What feature or fix shipped? What worked? What took longer than expected?
- What edge cases were discovered?
- **What did Claude initially misunderstand?** (→ "Agent Mistakes" in the doc, a first-class output)
- **What did this session reveal about how Claude and the user should work together?** A correction, a confirmed approach, a preference, a friction. This is a *process* learning, not a code one — it routes to memory in Step 6, not to a lessons-learned doc.
- **Scan the MEMORY.md block already in your context** (no extra tool call — it's injected each session). Does this session make any entry stale? Would a learning here duplicate one that exists? Note both for Steps 2.7 and 6.

### Step 2: Classify the Learning

| Type | Description | Where (default) |
|---|---|---|
| **Pattern** | Reusable approach that worked well | `docs/lessons-learned/` doc. Pattern Index ONLY if Step 4 gate passes. |
| **Decision** | Choice between alternatives with rationale | Inline in the lessons-learned doc, or `docs/architecture/` |
| **Failure/Fix** | Bug root cause + prevention | `docs/lessons-learned/` (consider a hook if deterministically catchable) |
| **Process / Collaboration** | How Claude and the user should work together — a correction, confirmed approach, or preference | Memory `feedback_*` entry (see Step 6). Never a lessons-learned doc. |
| **Workflow** | Repeated sequence of steps | New skill ONLY if Step 5 gate passes |
| **Rule** | Constraint that must always hold | `AGENTS.md` cardinal rule ONLY if truly non-negotiable (rare; most go in `docs/pitfalls.md` or memory). AGENTS.md is the SHARED rulebook (Codex loads it natively; CLAUDE.md `@`-imports it) — a rule written into CLAUDE.md's Claude-only section is invisible to Codex, so only Claude mechanics (skills, memory paths, `@` auto-imports) go there. |
| **Product fact** | A user-facing fact copy/marketing depends on (counts, mode names, workflow names) | A shared/source-of-truth file if one exists (e.g., `shared/product-facts.md`); else the closest single-source doc. Never duplicate across rulebooks. |

### Step 2.5: Route the Learning (read the project's routing table)

Before writing anything, check whether the project's root or workspace rulebook (`AGENTS.md`; its `CLAUDE.md` is an import stub) has a **routing table** for where each learning type belongs. Multi-subproject workspaces usually have a shared knowledge area for cross-cutting facts and a per-subproject docs area for stack-specific patterns.

If a routing table exists, use it:
- Cross-project insight (helps an unrelated project) → shared INDEX/docs.
- Stack-specific insight (only makes sense in this subproject's stack) → subproject INDEX/docs.
- Product fact → shared product-facts file, NOT lessons-learned.
- Process/collaboration → user memory.

If no routing table exists, default per Step 2: write to `docs/lessons-learned/` of the current working tree.

### Step 2.7: Overlap Check — Update, Don't Duplicate ⭐

The highest-leverage net-zero move, and the one most workflows skip. **Before writing a new doc, look for an existing one on the same problem.** Grep the target `docs/lessons-learned/` dir (and the relevant shared area) for the feature, module, error string, or component.

Score overlap with any candidate across five dimensions — problem statement, root cause, solution approach, files touched, prevention rule:

| Overlap | Action |
|---|---|
| **High** (4–5 match) — essentially the same problem again | **Update the existing doc.** Fold in the fresher context (new code refs, added prevention), add a dated note. Do NOT create a second file. |
| **Moderate** (2–3) — same area, different angle | **Create the new doc**, and flag the pair for Step 7 consolidation review. |
| **Low** (0–1) — related but distinct | **Create the new doc** normally. |

Why update beats create: two docs describing the same problem inevitably drift apart and eventually contradict each other — silently, because nothing forces them to be read together. The newer context is fresher and more trustworthy, so fold it in.

### Step 3: Write the Lessons-Learned Doc (short form)

One file per feature/fix, named by feature. Use this minimal template — **do NOT expand it.** Most learnings are 50–150 lines.

```markdown
# [Feature Name]

**Status:** [Shipped / Partially shipped / Abandoned]
**Date:** [YYYY-MM-DD]

## Context
[1–3 sentences: goal, what we tried, what shipped.]

## What Worked
- [Concrete insight per bullet. Not vague platitudes.]

## What Didn't
- [What blocked progress, what was discarded, what was harder than expected.]

## Agent Mistakes to Prevent
- [What Claude initially misunderstood. Phrase as "don't do X because Y".
  Future sessions should read this first.]

## Reusable Pattern (if any)
- **Name / Use when / Key insight** — one line each.
- **Admission check:** does this pass Step 4's gate, or is it project-specific?

## References
- Code: [file paths]   PRs/commits: [links]
```

**Do NOT include:** Executive Summary, Architecture Compliance Analysis, Data Flow diagrams, Future Applications, Replication Template. These inflate docs without improving future sessions. Git + code are the authoritative source for implementation detail.

### Step 4: Pattern Index Gate (default: NO)

Default: **do NOT add a row to any INDEX.** The lessons-learned doc alone is enough for most learnings.

Add an INDEX row only if BOTH hold:
- [ ] **Cross-project test:** an engineer on an *unrelated* project would benefit.
- [ ] **Non-obvious test:** the insight would NOT be rediscovered in an hour of reading the codebase.

If both pass, route per Step 2.5: cross-project → shared INDEX; stack-specific-but-still-passing → subproject INDEX. If either fails: project-internal pattern → `memory/reference_{project}_internal_patterns.md`; obvious-from-code → no row (the doc is enough).

Every INDEX row flows into a CLAUDE.md's context and carries a compliance cost. One row per session is how a CLAUDE.md grows from 100 to 335 lines.

**Row shape (Dave, 2026-09-04):** an INDEX/pitfalls row is ONE line — the tell, the rule, a pointer to the doc. PR numbers, round-by-round narratives and "3rd hit" histories live in the linked doc, never in the row. The 9/5 audit found the always-loaded rulebook at ~25k words (5× since May) while its most-emphasized rule (org isolation) still drew 28 Codex findings in two weeks — prose emphasis doesn't scale.

**Promotion ladder — prose is a TODO for code.** When a lesson recurs, don't lengthen the row; move it up:
- **1st hit** → a lessons-learned doc (and a row only if the gate above passes).
- **2nd hit** → the fix ships with a **pin** (a test or a grep guard that goes red if the pattern returns) and the doc records the hit count.
- **3rd hit** → the rule becomes **code**: a helper that is the only way to do the operation, or a required CI check (the way `check:org-scoping` / `check:status-literals` already do). The row shrinks to one line pointing at the helper/guard. Ask, every time: *"what code would make this lesson unnecessary?"* — and if there is no code shape (a design smell like "a write path satisfies part of a read gate"), keep a short checklist, not a paragraph.

**The ladder is MECHANICAL, not remembered (Dave, 2026-09-06: guardrail work is auto-approved — "if I'd be saying yes automatically every time it doesn't need to be groomed").** Every `docs/lessons-learned/*.md` carries one line near its top: `<!-- recurrence: hits=N prs=#a,#b guard=<path-or-none> -->` (see `docs/lessons-learned/README-recurrence.md`). This skill maintains it: on every new hit of an existing lesson, bump `hits` and append the PR; when a guardrail ships, set `guard=` to its path. `scripts/review-economics.py --guardrails` reads these lines (plus Codex finding recurrence) and prints what is due; the overnight-build run queues each due item as a pre-ruled card and builds it without grooming. A doc with no recurrence line shows up as `LESSON-NOLINE` in that report — add the line, never leave it. A lesson with NO code shape (a design smell, a triage rule like the CodeQL false-positive class) closes with `guard=n/a: <one-line reason>` once its checklist is in the doc — any non-`none` value counts as guarded, so it stops showing as due instead of nagging forever.

### Step 5: Skill / Command Creation Gate (default: NO)

Creating a skill costs context in every session. Default: **don't create.**

Create a skill only if ALL hold:
- [ ] Will be used >3 times across *unrelated* features (extrapolate from evidence, not hope)
- [ ] No existing skill covers it (check `~/.claude/skills/`)
- [ ] Workflow has decision points a bash script can't handle

Make it a **command** instead when it's a single repeatable operation expressible as a script and saving >2 min/use. Skills: `~/.claude/skills/{name}/SKILL.md`. Commands: `.claude/commands/{name}.md`.

### Step 6: Capture Memories (process + index)

Two memory jobs. Both matter; the first is the one this skill newly insists on.

**1. Write the process/collaboration learning from Step 1** (if any) as a memory entry — this is how the *way we work together* compounds. Memory format:

```markdown
---
name: feedback_<short-slug>
description: <one-line — used for recall>
metadata:
  type: feedback   # or: user | project | reference
---

<the guidance in one or two sentences>
**Why:** <the reason it matters — this is what makes it stick>
**How to apply:** <the concrete behavior change next time>
```

- **Check for an existing memory to update first** (you scanned MEMORY.md in Step 1) — refine it rather than adding a near-duplicate. One fact per file.
- After writing, add a one-line pointer to `MEMORY.md`. Link related memories with `[[other-slug]]`.
- Only capture what was *non-obvious*. Don't memorialize what the code, git history, or CLAUDE.md already records.

**2. Update the MEMORY.md index to current truth** — the most decay-prone always-loaded file:
- Fix stale entries (commit counts, status dates, "remaining" items now done).
- Add pointers for any memory files created this session (keep each <~150 chars).
- **Remove obsolete entries** for completed/merged features that no longer need tracking. This is the most important update — stale MEMORY.md lines make future sessions start with wrong assumptions.

### Step 6.5: Cross-Cutting Fact Check ⭐

If this session changed a feature, count, mode name, workflow name, deploy target, or other product fact, check whether it shifts a fact recorded in a shared/source-of-truth file (`shared/product-facts.md`, `shared/deployment.md`, `shared/brand.md`).

For each shared file the project maintains:
1. Read the relevant section. Does the change make any line stale?
2. If yes, update it in the same logical change. Update the "Last verified" date.
3. Grep the rest of the workspace for stale references to the old fact (e.g., `grep -ri "7 criteria" website/`); list them in the commit message or a follow-up TODO. Don't leave silent drift.
4. Each repo gets its own commit (shared edits are a separate commit in the shared repo).

Skip if the project has no shared facts file.

### Step 7: PRUNE (net-zero check) ⭐

The step most compounding workflows skip. Before committing, actively look for deletions. For every candidate stale artifact, pick one outcome — don't default to Keep just because the general advice still sounds fine:

| Outcome | When |
|---|---|
| **Keep** | Still accurate and useful. No edit — don't leave a review breadcrumb. |
| **Update** | Core is right, references drifted (paths, names, links). Fix in place. |
| **Consolidate** | Two docs cover the same ground. Merge unique content into the canonical one, delete the other. |
| **Replace** | Old guidance is now misleading and you have a verified successor. Write it, delete the old. |
| **Delete** | Code/problem-domain gone, or fully redundant. Remove it. |

Sweep:
- [ ] **Rulebook size:** `wc -c AGENTS.md CLAUDE.md design.md`. Baseline after the 2026-09-06 prune (app): AGENTS.md ~12.5K, CLAUDE.md ~1.8K, design.md ~9.8K — every session loads all three. Over? Cut, or move rationale/spec into a linked doc (`docs/worktree-sop.md`, `docs/plans/...`), never into another auto-loaded file.
- [ ] **Rewriting a rulebook or doctrine file?** Read it from `origin/main` inside the worktree (never an earlier primary-checkout read — a 3-day-stale read silently dropped four rules, #1849), diff the rewrite against that same copy, and grep `__tests__/` for source pins (`read('design.md')`, literal doctrine phrases) before rewording anything (#1850 lost a CI round to one).
- [ ] **Pattern Index rows** referencing deleted code, superseded approaches, or moderate-overlap pairs from Step 2.7 → Update/Consolidate/Delete.
- [ ] **Lessons-learned docs** that overlap (drift silently) or reference code that no longer exists → Consolidate or Delete.
- [ ] **MEMORY.md entries** for merged features still marked "active" → Delete.
- [ ] **Dead rules** in AGENTS.md / CLAUDE.md naming renamed files or past projects → Delete. (Every workspace dir — root, app, website, GTM, shared — uses the AGENTS.md-shared + CLAUDE.md-stub pair since 2026-09-06; edit the rule in AGENTS.md so both tools see it.)

**Delete, don't archive.** Git history *is* the archive (`git log --diff-filter=D` recovers anything). A `docs/lessons-learned/archived/` directory just accumulates docs nobody reads and pollutes search — skip it. A session that adds 0 INDEX rows and removes 1 stale one is a **WIN**. Net-negative compounding is the goal once a repo is mature.

### Step 8: Verify and Commit

1. Review the doc / memory edits for accuracy and terseness.
2. Confirm CLAUDE.md / INDEX / MEMORY.md reflect reality, including this session's deletions.
3. Commit:
   ```
   docs: compound learnings from [feature name]

   - Updated [existing doc] with fresh context  (or: Added [doc])
   - Captured [process learning] to memory
   - Removed [stale entry/rule] from [file]
   ```

### Step 9: Sync Skills + Shared (if modified)

If you created/modified **skills** this session:
```bash
cd ~/.claude/skills && git add -A && git diff --cached --quiet || git commit -m "Update skills from compound session" && git push origin main
```

If you edited a **shared/source-of-truth** repo:
```bash
git -C <abs>/shared add <the files you edited> && git -C <abs>/shared diff --cached --quiet || git -C <abs>/shared commit -m "compound: <what fact changed>" && git -C <abs>/shared push origin main 2>/dev/null || echo "shared has no remote — skipping push"
```
(No `cd`, explicit paths, never `-A` — the same rules the agent briefs open with.)

Do NOT auto-commit the subproject repos — those follow normal commit/PR rules per the subproject's AGENTS.md. This skill commits only the meta-files (skills + shared knowledge + memory).

---

## Where This Sits in the Loop

Compound is the last step of the engineering loop, and the one that feeds the next pass:

```
tech-research → Plan        ui-design / coding → Work
        ↓                            ↓
   app-testing → Verify  ──→  deep-debug → Fix (if needed)
        ↓                            ↓
   code-review / simplify → Review & Polish
        ↓
   compound → Learn + Prune + Codify   (net-zero size goal)
        ↓
   next feature is easier — AND the collaboration is sharper —
   without the always-loaded files getting bigger
```

`handoff-session` invokes this skill non-interactively as part of end-of-session wrap-up. When it does, run in non-interactive mode and return the compact report.

## Non-Interactive Report

When run non-interactively, end with this instead of conversation:

```
✓ Compound complete

Doc:      <path> (created | updated — high overlap with <path>) | none
Memory:   <feedback_slug captured | MEMORY.md: N updated, M removed | none>
INDEX:    <none | +1 row to <path> | -N stale rows>
Shared:   <none | updated <file> — fact: <what changed>>
Pruned:   <0 | N deletions/consolidations: list>
Net:      <+N / -M lines across always-loaded files>
```

## Example (compressed)

"We finished issue labels. Compound." → `git diff`; testing was skipped initially (failure pattern) **and** Claude assumed the wrong filter scope twice (process learning). Step 2.7: an existing `issue-filtering.md` covers 4/5 dimensions → **update it**, don't create a new doc. Step 4 gate: "run tests before shipping" is too obvious for INDEX — skip. Step 6: capture `feedback_confirm_filter_scope` to memory. Step 7: CLAUDE.md is 110 lines ✓; remove one Pattern Index row for a deleted feature. **Outcome:** one doc refreshed (not added), one process memory, one stale row gone. Net signal up, net lines down.

---

## References

- [Compound Engineering Guide](https://every.to/guides/compound-engineering) — Every's full methodology (Ideate→Brainstorm→Plan→Work→Review→Polish→Compound), updated 2026.
- [compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) — Every's `ce-compound` / `ce-compound-refresh` source; origin of the overlap-check, update-don't-duplicate, and delete-don't-archive patterns adopted here.
- [Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) — instruction-budget and compliance degradation.
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices) — verification, hooks, when a rule becomes a hook.

**Key insight:** The compound methodology inverts traditional engineering, where each feature makes the next harder. But it only works if compounding is net-additive on *useful signal* — not on *volume*, and not only on *code*. Update before you duplicate; capture how-we-work alongside what-we-built; prune as much as you add. For frontier models, keep this skill's prescription lean: spell out the mechanical steps (paths, gates, commit flow), trust the model on judgment. Over-prescription degrades output.
