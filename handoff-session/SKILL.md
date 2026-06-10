---
name: handoff-session
description: End-of-session wrap-up before clearing context on a long build session. Tidies the working tree, updates documentation, runs /compound, creates final PRs, delivers a session debrief with epic progress bar to re-ground the user, then writes a copy-paste handoff prompt for the post-/clear session. Use when the context window is getting heavy, at a junction point in a large build, when the user says "clear context and continue", "wrap up this session", or asks for a handoff prompt or progress summary.
---

# Handoff Session: Tidy → Docs → Compound → PRs → Handoff

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

Make a todo list for these six steps and work through them in order.

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

- **Test gate first**: run `/test:safe` (web-safe) on the branch before pushing, or — if the suite already ran this session on the final state — skip and rely on CI, but say so in the handoff.
- Commit remaining logical units separately; push every branch (RULE #5 — Dave reviews on Replit/GitHub).
- Open PRs with `gh pr create` for each branch that's ready. Note draft vs. ready-for-review, and check `gh pr checks` so the handoff can report CI state (passing / pending / failing).
- **Stacked PRs**: if a base just merged, remember the repo squash-merges — `git rebase --onto origin/main <base> <branch>` + force-push, or GitHub shows a false conflict.
- **Backfill PR numbers into MEMORY.md**: `/compound` ran before these PRs existed, so any project-status entries it wrote reference branches, not PR numbers. Update them now.
- Record every PR number and state — the handoff prompt needs them.

### Step 5: Session Debrief (for the user — re-grounding, not handoff)

Output a short debrief in plain chat, NOT inside the handoff code block. The handoff prompt serves the next Claude session; this serves the human, who may be dozens of clears deep into a multi-day epic and losing the thread.

**1. Accomplished this session** — 3–6 bullets, outcome-focused plain language ("parts dashboard now filters by status", not "refactored useRoList"), each anchored to a PR/commit number.

**2. Where we are in the epic** — find the governing artifact for this workstream: the roadmap/plan doc in the repo, or the project memory entry tracking it. Derive position from that artifact, NOT from conversational recall (which is exactly what's about to be cleared). Render a progress bar plus phase list:

```
Epic: RO platform enhancements   [██████░░░░] 6/10 phases
✅ P0 status anchor model        (#480, merged)
✅ P1–P3 …                       (#482–#489, merged)
🔄 P4 column config              (#506 open, awaiting review)
⬜ P5 audit trail
⬜ P6 plan net-new projects
```

**3. Drift check** — one or two sentences: is the planned next task still the right next move, or did this session change the picture? Name any fork in the road the user should consciously choose rather than default into. This is the antidote to blindly trudging forward.

**If the epic has no governing artifact** (multi-session work tracked only in conversation), create one now — a project memory entry with the phase list and status — so the next wrap computes the bar instead of guessing. Keep it updated on every subsequent wrap; a stale bar is worse than none.

### Step 6: Write the Handoff Prompt

**Verify before you write**: handoff claims drift from reality. Execute the read-only startup commands yourself (`pwd`, `git branch --show-current`, `git status`) and paste the *actual* output into the startup sequence — never write it from memory. Confirm every file path you cite exists.

**Save it twice**: output the prompt as a single fenced code block in chat AND write the same content to a file (`/tmp/handoff-<workstream>-<date>.md`, or alongside the Step 2 brief if one was committed). Chat scrollback is the only other copy after `/clear` — tell the user the file path. Template:

```markdown
# Handoff: [workstream name] — continuing from [date] session

## State
[2-4 sentences: what shipped this session, what's in flight, what's next.]
Epic position: [phase X of Y per <governing roadmap doc / memory entry> — cite it so the fresh session reads it]

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
- [ ] `/compound` ran; MEMORY.md reflects current truth (including backfilled PR numbers)
- [ ] Tests ran (or CI state checked) before final PRs; branches pushed; PR numbers + CI state recorded
- [ ] Startup sequence verified by actually running it, not written from memory
- [ ] Session debrief delivered in plain chat: accomplishments, epic progress bar derived from a durable artifact, drift check
- [ ] Multi-session epic has a governing artifact (roadmap doc or project memory entry) — created this wrap if it didn't exist
- [ ] Handoff prompt delivered as one copy-paste block AND saved to a file, written against the FINAL state
- [ ] Handoff includes startup sequence + locked decisions + single next task + epic position

## Integration with Other Skills

```
(long build session)
    ↓
handoff-session ──→ /compound   (Step 3 — capture + prune + memory)
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
