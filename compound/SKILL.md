---
name: compound
description: Capture learnings after completing a feature or session to make future work easier. Documents patterns, decisions, failures, and determines if new skills or Claude.md updates are needed.
---

# Compound: Knowledge Capture & Codification

This skill formalizes the "compound" step of compound engineering: capturing learnings so each feature makes the next one easier.

## When to Use This Skill

**Use this skill when:**
- You've just completed a significant feature or bug fix
- A session is ending and valuable learnings should be preserved
- You discovered a pattern worth documenting for future sessions
- You want to review recent work and extract reusable knowledge
- A bug was particularly tricky and the fix should prevent recurrence

**Don't use this skill for:**
- Active debugging (use `deep-debug` skill instead)
- Writing tests (use `app-testing` skill)
- Research tasks (use `tech-research` skill)

## Core Philosophy

> "Each unit of engineering work should make subsequent units easier—not harder."

The goal is to create a **learning loop** where:
1. Patterns get documented so they can be reused
2. Decisions get recorded so they don't get re-debated
3. Failures get encoded into rules/hooks to prevent recurrence
4. Repeated workflows get turned into skills or commands

## Compounding Workflow

### Step 1: Gather Context

First, understand what was accomplished in this feature/session.

```
Review recent work:
- What feature or fix was completed?
- What files were changed? (git diff main...HEAD)
- What was the original problem/requirement?
- How long did it take vs. expected?
```

**Key Questions to Answer:**
- What worked well?
- What took longer than expected?
- What did I (Claude) initially misunderstand?
- What edge cases were discovered?
- What patterns were used or created?

### Step 2: Classify the Learning Type

Determine what type of knowledge was generated:

| Type | Description | Where to Codify |
|------|-------------|-----------------|
| **Pattern** | Reusable approach that worked well | `docs/lessons-learned/` + Claude.md pattern index |
| **Decision** | Choice between alternatives with rationale | `docs/architecture/` or inline in lessons-learned |
| **Failure/Fix** | Bug root cause and prevention | `docs/lessons-learned/` + possibly a hook |
| **Workflow** | Repeated sequence of steps | New skill or command |
| **Rule** | Constraint that must always be followed | Claude.md cardinal rules |

### Step 3: Create Documentation

Based on classification, create appropriate documentation.

#### For Patterns (Success Stories)

Create a file in `docs/lessons-learned/` following this template:

```markdown
# [Feature Name] - [Pattern Type] Documentation

**Feature**: [Brief description]
**Implementation Date**: [Date]
**Status**: [Production Ready / In Progress / Experimental]
**Architecture Compliance**: [% compliance with RO-bot governance]

---

## Executive Summary
[1-2 paragraphs on what was accomplished and key achievements]

---

## Implementation Approach
### Phase 1: [Phase Name]
**Outcome**: [What this phase proved/accomplished]
- [Bullet points of key steps]
- **Result**: [Concrete outcome]

[Repeat for each phase]

---

## Architecture Compliance Analysis
### [Rule Category]
- [Checkbox] [Specific compliance point]
[Repeat for each relevant rule]

---

## Technical Implementation Details
### Files Created/Modified
```
/path/to/file.ts - [Description]
```

### API Endpoints (if applicable)
```
METHOD /endpoint - [Description]
```

### Data Flow
```
[Step 1] → [Step 2] → [Step 3]
```

---

## Lessons Learned

### What Worked Well
1. [Specific success factor]

### What Could Be Improved
1. [Area for improvement]

### Agent Mistakes to Prevent
1. [What I (Claude) initially misunderstood and how to prevent it]

---

## Replication Template
[Prompt patterns or approach that can be reused for similar features]

---

## Future Applications
[Other features that could use this pattern]
```

#### For Failures/Fixes

Focus on prevention:

```markdown
# [Bug/Issue Name] - Root Cause Analysis

**Symptoms**: [What the user experienced]
**Root Cause**: [Technical explanation]
**Fix Applied**: [What was changed]
**Prevention Strategy**: [How to prevent recurrence]

## Should This Become a Hook or Rule?
- [ ] Add to Claude.md as a cardinal rule
- [ ] Create a pre-commit hook
- [ ] Add to an existing skill's checklist
- [ ] No codification needed (one-time issue)
```

### Step 4: Update Claude.md Pattern Index

If a significant pattern was documented, add it to the pattern index in `docs/Claude.md`:

```markdown
## Pattern Index (Quick Reference)

| Pattern | Use When | Doc Link |
|---------|----------|----------|
| VIN OCR Success | Camera/OCR features | [vin-ocr-success-pattern.md] |
| [New Pattern] | [Trigger condition] | [doc-link.md] |
```

### Step 5: Evaluate Skill/Command Creation

Ask these questions:

**Should this become a new skill?**
- [ ] Will this workflow be repeated more than 3 times?
- [ ] Does it require 5+ steps to execute properly?
- [ ] Would forgetting a step cause significant problems?
- [ ] Is it distinct from existing skills (app-testing, deep-debug, tech-research)?

**Should this become a new command?**
- [ ] Is it a single, repeatable operation (not a workflow)?
- [ ] Can it be expressed as a simple bash script or command sequence?
- [ ] Would it save >2 minutes each time it's used?

If yes to a skill, create in `.claude/skills/[name]/SKILL.md`.
If yes to a command, create in `.claude/commands/[name].md`.

### Step 6: Update Memory Index

Read `MEMORY.md` and verify it reflects the current state of the project:

1. **Update stale entries** — commit counts, status dates, "remaining" items that are now done
2. **Add new memory file pointers** if you created new memory files during this session
3. **Keep entries under 1 line each** — MEMORY.md is an index, not a document
4. **Remove obsolete entries** for completed/merged features that no longer need tracking

MEMORY.md is loaded into every conversation automatically. Stale entries cause future sessions to start with wrong assumptions (e.g., "22 commits" when there are 35, or "remaining: TTS audio" when it's been done for days).

### Step 7: Verify and Commit

1. **Review the documentation** for accuracy and completeness
2. **Check Claude.md** if updates were made
3. **Check MEMORY.md** is current (step 6)
4. **Commit with descriptive message**:
   ```
   docs: compound learnings from [feature name]

   - Added [pattern/fix] documentation
   - Updated Claude.md pattern index
   - [Created new skill/command if applicable]
   ```

### Step 8: Sync Skills (if modified)

If you created or modified any skills during this session:

```bash
cd ~/.claude/skills
git add -A
git diff --cached --quiet || git commit -m "Update skills from compound session"
git push origin main
```

---

## Quick Reference: Compounding Checklist

Use this checklist at the end of each significant feature:

```
## Compounding Checklist for [Feature Name]

### Knowledge Capture
- [ ] What patterns were used or discovered?
- [ ] What decisions were made and why?
- [ ] What took longer than expected?
- [ ] What did Claude initially misunderstand?

### Documentation
- [ ] Created/updated docs/lessons-learned/ entry?
- [ ] Updated Claude.md pattern index (if significant)?
- [ ] Documented architecture compliance?

### Codification
- [ ] Should any rules be added to Claude.md?
- [ ] Should a new skill be created?
- [ ] Should a new command be created?
- [ ] Should a hook be added to prevent issues?

### Memory Index
- [ ] MEMORY.md entries updated (status, dates, commit counts)?
- [ ] New memory file pointers added if needed?
- [ ] Stale/completed entries cleaned up?

### Commit
- [ ] All documentation committed?
- [ ] Descriptive commit message?

### Skills Sync (if skills modified)
- [ ] Skill changes committed and pushed?
```

---

## RO-bot Specific Considerations

When compounding knowledge for RO-bot, always consider:

1. **Mobile-First Impact**: Did this affect iOS Safari behavior? Document it.
2. **Data Isolation**: Any learnings about organization_id filtering?
3. **Architecture Compliance**: How well did this follow the direct-to-Firebase model?
4. **Voice/Video Features**: Any learnings about media handling?

---

## Integration with Other Skills

This skill completes the development loop:

```
tech-research → Plan
    ↓
 (coding)    → Work
    ↓
app-testing  → Verify
    ↓
deep-debug   → Fix (if needed)
    ↓
compound     → Learn & Codify
    ↓
(next feature, now easier)
```

---

## Example Session

**User**: "We just finished the issue labels feature. Let's compound the learnings."

**Claude**:
1. Reviews recent commits and changes
2. Identifies that testing was skipped initially (failure pattern)
3. Creates `docs/lessons-learned/issue-labels-feature.md`
4. Notes that a testing reminder should be added to Claude.md
5. Confirms no new skill needed (existing app-testing covers this)
6. Commits documentation with clear message

**Outcome**: Future features will have stronger testing discipline because the failure was codified.

---

## References

This skill is based on the compound engineering methodology developed at Every.to.

**Primary Sources:**
- [Compound Engineering Plugin](https://github.com/EveryInc/compound-engineering-plugin) — Official Claude Code plugin with full workflow implementation
- [Compound Engineering: How Every Codes With Agents](https://every.to/chain-of-thought/compound-engineering-how-every-codes-with-agents) — Dan Shipper's article explaining the methodology
- [How Two Engineers Ship Like a Team of 15 With AI Agents](https://every.to/podcast/how-two-engineers-ship-like-a-team-of-15-with-ai-agents) — Podcast with implementation details

**Pattern Documentation:**
- [Compounding Engineering Pattern](https://github.com/nibzard/awesome-agentic-patterns/blob/main/patterns/compounding-engineering-pattern.md) — Community pattern documentation with trade-offs analysis

**Key Insight:** The methodology inverts traditional engineering where each feature makes the next harder. By systematically capturing learnings, each feature makes the next *easier*.
