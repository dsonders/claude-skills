---
name: wrap-session
description: End-of-session wrap-up before clearing context on a long build session. Tidies the working tree, updates documentation, runs /compound, creates final PRs, then writes a copy-paste handoff prompt for the post-/clear session. Use when the context window is getting heavy, at a junction point in a large build, when the user says "clear context and continue", "wrap up this session", or asks for a handoff prompt.
---

# Wrap Session: Tidy → Docs → Compound → PRs → Handoff

Lands a long build session cleanly so work can continue in a fresh context window with zero re-litigation. The final deliverable is a **handoff prompt** the user pastes after `/clear`.

## When to Use This Skill

**Use this skill when:**
- The context window is getting heavy at a junction point in a multi-phase build
- The user says "clear context and continue in this window" or similar
- A session is ending mid-workstream and a fresh session will pick it up
- The user asks for a handoff prompt or session wrap-up

**Don't use this skill for:**
- Knowledge capture alone with no session switch (use `/compound` directly)
- A finished workstream with nothing to hand off (just `/compound` + final PR)
- Mid-task pauses where context will survive (no wrap needed; context summarization handles it)

## Core Principles

1. **Order is load-bearing**: handoff prompt comes LAST — it must reference final PR numbers, commit SHAs, and branch states that only exist after the earlier steps.
2. **The fresh session is blind**: decisions, rationale, and "what's not up for debate" live only in this conversation. If it's not in the handoff prompt, a file, or memory, it's gone.
3. **Leave nothing uncommitted**: every repo and worktree touched this session ends pushed (RULE #5). The handoff prompt should never say "there are uncommitted changes."
4. **Handoff ≠ memory**: memory holds durable project facts (`/compound` updates it); the handoff prompt holds the immediate next move and this-session context. Don't duplicate — point.

## Workflow

Make a todo list for these five steps and work through them in order.

### Step 1: Tidy Up

Sweep every repo/worktree touched this session:

```bash
git status                    # in each touched repo/worktree
git branch --show-current     # verify before ANY git op — sibling sessions move HEAD
```

- **Scratch files** (screenshots, repro files, one-off scripts in repo root): delete, or move to `/tmp` if still needed. Never leave them untracked in the repo.
- **Stray debug code**: grep for `console.log`/`debugger`/commented-out blocks added this session.
- **Worktrees**: note which are parked vs. active; stop dev servers you started unless the handoff needs them running.
- **Branch hygiene**: anything sitting on `main` uncommitted is a red flag — move it to a branch.

### Step 2: Update / Create Documentation

Only what this session made stale or necessary:

- Plan docs / design briefs that no longer match what was built → update or mark superseded.
- New pitfalls or patterns discovered → leave for `/compound` (Step 3) to route; don't double-write.
- If this was a **design-heavy session with many locked decisions**, commit a self-contained brief in the worktree (`docs/` if it outlives the build, `mockups/implementation-plan.md` if disposable) — the handoff prompt then references it instead of inlining everything.

### Step 3: Run /compound

Invoke the `/compound` skill. It handles: lessons-learned doc, INDEX gates, MEMORY.md updates (status, completed items, new pointers), shared-facts check, pruning, and the skills-repo sync.

Do not duplicate its outputs in later steps — the handoff prompt links to what compound wrote.

### Step 4: Create Final PRs

- Commit remaining logical units separately; push every branch (RULE #5 — Dave reviews on Replit/GitHub).
- Open PRs with `gh pr create` for each branch that's ready. Note draft vs. ready-for-review.
- **Stacked PRs**: if a base just merged, remember the repo squash-merges — `git rebase --onto origin/main <base> <branch>` + force-push, or GitHub shows a false conflict.
- Record every PR number and state — the handoff prompt needs them.

### Step 5: Write the Handoff Prompt

Output as a single fenced code block the user copies and pastes after `/clear`. Template:

```markdown
# Handoff: [workstream name] — continuing from [date] session

## State
[2-4 sentences: what shipped this session, what's in flight, what's next.]

## Startup sequence
- cd [exact path / worktree]
- git branch --show-current  → expect `[branch]`; if not, [recovery instruction]
- [dev server / env needed? exact command, or "none needed"]

## PRs
- #[N] [title] — [merged / open, awaiting review / draft, blocked on X]

## Locked decisions (do not re-litigate)
- [Decision] — because [one-line why]

## Next task
[The single next concrete action, precise enough to start without questions.
Include file paths and the relevant pitfalls.md / lessons-learned entries to read first.]

## Do not touch
- [Stable infrastructure / parked worktrees / sibling-session branches]

## Open questions for Dave
- [Anything that must be confirmed before coding — or "none"]

## Pointers
- [Brief/plan doc committed in Step 2, lessons-learned doc from /compound, memory entries updated]
```

Trim sections that are empty rather than padding them. If the session produced HTML mockups or visual sources of truth, instruct the fresh session to render them via Playwright MCP (`browser_navigate` to the `file://` URL + screenshot) before coding UI — text descriptions of visuals are fragile.

## Success Criteria

- [ ] `git status` clean in every touched repo/worktree (or intentionally-dirty state named in the handoff)
- [ ] `/compound` ran; MEMORY.md reflects current truth
- [ ] All session branches pushed; PRs created with numbers recorded
- [ ] Handoff prompt delivered as one copy-paste block, written against the FINAL state
- [ ] Handoff includes startup sequence + locked decisions + single next task

## Integration with Other Skills

```
(long build session)
    ↓
wrap-session ──→ /compound   (Step 3 — capture + prune + memory)
    ↓
(user runs /clear, pastes handoff prompt)
    ↓
(fresh session resumes with full context)
```

## Troubleshooting

### Handoff prompt is getting huge
Too many locked decisions to inline → commit a durable brief (Step 2) and have the handoff prompt point to it with a "read this first" instruction.

### PR can't be created (base branch just merged)
Squash-merge false conflict — rebase `--onto origin/main` per Step 4, don't merge main in.

### Not sure if something belongs in handoff or memory
Will it matter beyond the very next session? → memory (via `/compound`). Only needed to resume this workstream? → handoff prompt.
