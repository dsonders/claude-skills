---
name: compound
description: Capture learnings after completing a feature or session to make future work easier. Net-zero-or-better on file size — prunes as much as it adds. Determines if new skills or CLAUDE.md updates are needed.
---

# Compound: Knowledge Capture & Pruning

Formalizes the "compound" step of compound engineering: capture learnings so each feature makes the next one easier, **WITHOUT adding bloat**. Every step that adds knowledge has a matching gate or a pruning companion.

## Core Philosophy

> "Each unit of engineering work should make subsequent units easier — not just documented more."

The learning loop:
1. Patterns get documented so they can be reused
2. Decisions get recorded so they don't get re-debated
3. Failures get encoded into rules/hooks to prevent recurrence
4. Repeated workflows get turned into skills or commands
5. **Stale knowledge gets deleted so signal-to-noise stays high**

If this session adds more to CLAUDE.md or the Pattern Index than it removes, you're probably compounding in the wrong direction. Dead weight degrades compliance on every other rule.

## When to Use

- Just completed a significant feature or bug fix
- Session is ending and valuable learnings should be preserved
- Discovered a pattern worth documenting
- A bug was tricky and the fix should prevent recurrence

Don't use for:
- Active debugging (use `deep-debug`)
- Writing tests (use `app-testing`)
- Research tasks (use `tech-research`)

---

## Workflow

### Step 1: Gather Context

```bash
git diff main...HEAD        # what changed
git log main..HEAD --oneline # how it got there
```

Answer internally:
- What feature or fix was completed?
- What worked well? What took longer than expected?
- What did Claude initially misunderstand?
- What edge cases were discovered?

### Step 2: Classify the Learning

| Type | Description | Where |
|---|---|---|
| **Pattern** | Reusable approach that worked well | `docs/lessons-learned/` doc. Pattern Index ONLY if Step 4 gate passes. |
| **Decision** | Choice between alternatives with rationale | Inline in the lessons-learned doc, or `docs/architecture/` |
| **Failure/Fix** | Bug root cause + prevention | `docs/lessons-learned/` (consider a hook if deterministically catchable) |
| **Workflow** | Repeated sequence of steps | New skill ONLY if Step 5 gate passes |
| **Rule** | Constraint that must always be followed | CLAUDE.md cardinal rule ONLY if truly non-negotiable (rare; most go in @docs/pitfalls.md or memory) |

### Step 3: Write the Lessons-Learned Doc (short form)

One file per feature/fix in `docs/lessons-learned/`, named by feature. Use this minimal template — **do NOT expand it**. Most learnings are 50–150 lines total.

```markdown
# [Feature Name]

**Status:** [Shipped / Partially shipped / Abandoned]
**Date:** [YYYY-MM-DD]

## Context
[1–3 sentences: what was the goal, what did we try, what shipped.]

## What Worked
- [Concrete insight per bullet. Not vague platitudes.]

## What Didn't
- [What blocked progress, what was discarded, what was harder than expected.]

## Agent Mistakes to Prevent
- [What Claude initially misunderstood. Phrase as "don't do X because Y".
  This is a first-class output — future sessions should read this first.]

## Reusable Pattern (if any)
- **Name:** [Short name]
- **Use when:** [1 line]
- **Key insight:** [1–2 lines]
- **Admission check:** does this pass Step 4's gate, or is it RO-bot-specific?

## References
- Code: [file paths touched]
- PRs/commits: [links]
```

**Do NOT include:** Executive Summary, Architecture Compliance Analysis, Data Flow diagrams, Future Applications, Replication Template. These inflate docs without improving future sessions. Git + code are the authoritative source for implementation details.

### Step 4: Pattern Index Gate (default: NO)

Default action: **do NOT add to `docs/lessons-learned/INDEX.md`**. The lessons-learned doc alone is enough for most learnings.

Only add an INDEX row if BOTH are true:

- [ ] **Cross-project test:** A new engineer working on an unrelated project (not RO-bot) would benefit from this pattern.
- [ ] **Non-obvious test:** The insight would NOT be rediscovered in an hour of reading the codebase.

If either fails:
- **RO-bot-specific:** add a row to `memory/reference_ro_bot_internal_patterns.md` instead.
- **Obvious from code:** no INDEX row. The lessons-learned doc is enough for archival.

The INDEX flows into every session's context via CLAUDE.md. Each row has a compliance cost. Over 30+ sessions, adding one row per session is how a CLAUDE.md grows from 100 lines to 335.

### Step 5: Skill / Command Creation Gate (default: NO)

Creating a skill costs context in every session. Default: **don't create**.

Create a new skill only if ALL are true:

- [ ] Will be used >3 times across unrelated features (extrapolate from evidence, not hope)
- [ ] No existing skill covers it (check `~/.claude/skills/`)
- [ ] Workflow has decision points a bash script can't handle

Make it a command instead if:
- Single repeatable operation, expressible as a bash script or command sequence
- Saves >2 minutes per use

Skills: `~/.claude/skills/{name}/SKILL.md`. Project commands: `.claude/commands/{name}.md`.

### Step 6: Update Memory Index

Read `MEMORY.md` and update to current truth:

1. **Update stale entries** — commit counts, status dates, "remaining" items that are now done.
2. **Add new memory file pointers** if you created memory files this session (keep each pointer under ~150 chars).
3. **Remove obsolete entries** for completed/merged features that no longer need tracking. This is the most important update — MEMORY.md lines decay fast.

MEMORY.md is loaded into every conversation. Stale entries = future sessions start with wrong assumptions.

### Step 7: PRUNE (net-zero check) ⭐

The step most compounding workflows skip. Before committing, look for deletions:

- [ ] **CLAUDE.md size:** `wc -l CLAUDE.md`. Target <150. Over? Identify sections to cut or move to `@docs/...` imports.
- [ ] **Pattern Index rows:** any rows that reference deleted code, superseded approaches, or are no longer relevant? Remove.
- [ ] **Lessons-learned docs >6 months old** not referenced in current code or memory? Archive to `docs/lessons-learned/archived/`.
- [ ] **Memory entries** for completed/merged features still marked "active"? Move to Completed or delete.
- [ ] **Dead rules** in CLAUDE.md referencing renamed files, deleted features, or past projects? Delete.

A compound session that adds 0 INDEX rows and removes 1 stale one is a **WIN**. Net-negative compounding is the goal when the repo is already mature.

### Step 8: Verify and Commit

1. Review the lessons-learned doc for accuracy and terseness.
2. Confirm CLAUDE.md / INDEX.md / MEMORY.md changes reflect reality (including deletions from Step 7).
3. Commit:
   ```
   docs: compound learnings from [feature name]

   - Added [pattern/fix] documentation
   - Removed [stale entry/rule] from [file]
   - [Created new skill/command if applicable]
   ```

### Step 9: Sync Skills (if modified)

If you created or modified skills this session:

```bash
cd ~/.claude/skills
git add -A
git diff --cached --quiet || git commit -m "Update skills from compound session"
git push origin main
```

---

## Integration with Other Skills

```
tech-research → Plan
    ↓
(coding)      → Work
    ↓
app-testing   → Verify
    ↓
deep-debug    → Fix (if needed)
    ↓
compound      → Learn + Prune + Codify (net-zero size goal)
    ↓
(next feature, now easier — without the file being bigger)
```

## Example Session

**User:** "We just finished the issue labels feature. Let's compound."

**Claude:**
1. `git diff main...HEAD` — reviews changes.
2. Identifies: testing was skipped initially (failure pattern).
3. Writes `docs/lessons-learned/issue-labels-feature.md` using short template.
4. **Step 4 gate:** "always run tests before shipping" is too obvious for INDEX — skip the row.
5. **Step 5 gate:** no new skill — existing `app-testing` skill covers this.
6. **Step 7 prune:** checks CLAUDE.md size (110 lines ✓); removes one stale Pattern Index row referencing a deleted feature.
7. Commits.

**Outcome:** one new lessons-learned doc (preserved), zero bloat in always-loaded files, one stale row removed. Net signal went up.

---

## References

- [Compound Engineering Plugin](https://github.com/EveryInc/compound-engineering-plugin) — Every's original workflow
- [Compound Engineering: How Every Codes With Agents](https://every.to/chain-of-thought/compound-engineering-how-every-codes-with-agents) — Dan Shipper's explanation
- [HumanLayer: Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) — on instruction budget and compliance degradation
- [Anthropic: Claude Code Best Practices](https://code.claude.com/docs/en/best-practices) — on verification, hooks, and when rules become hooks

**Key insight:** The compound methodology inverts traditional engineering (where each feature makes the next harder). But it only works if compounding is net-additive on *useful signal*, not on *volume*. Pruning is half the job.
