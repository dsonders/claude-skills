# Skill Research: [Skill Name]

**Date:** [Date]
**Domain:** [What domain this skill covers]
**Researcher:** Claude

---

## 1. Need Validation

### The 5-10 Rule

| Question | Answer |
|----------|--------|
| Times done before? | [Number] |
| Expected future uses? | [Number] |
| Steps required? | [Number] |
| Distinct from existing skills? | [Yes/No - explain] |

### Validation Result

- [ ] **PASS** - Proceed with skill creation
- [ ] **FAIL** - Consider alternatives below

**If FAIL, alternatives:**
- [ ] Extend existing skill: `[skill-name]`
- [ ] Create simple command instead
- [ ] Document as pattern in lessons-learned

---

## 2. Existing Skills Research

### Sources Searched

- [ ] [awesome-claude-skills (travisvn)](https://github.com/travisvn/awesome-claude-skills)
- [ ] [awesome-claude-skills (VoltAgent)](https://github.com/VoltAgent/awesome-claude-skills)
- [ ] Web search: "[domain] claude code skill"
- [ ] Project skills: `.claude/skills/`

### Skills Found

#### [Skill Name 1]
- **URL:** [link]
- **Description:** [what it does]
- **Verdict:** Adopt / Adapt / Learn from / Skip
- **Reason:** [why this verdict]
- **Patterns to borrow:** [if applicable]

#### [Skill Name 2]
- **URL:** [link]
- **Description:** [what it does]
- **Verdict:** Adopt / Adapt / Learn from / Skip
- **Reason:** [why this verdict]
- **Patterns to borrow:** [if applicable]

### Security Review (for external skills)

| Check | Status |
|-------|--------|
| No hardcoded credentials | [ ] Pass / [ ] Fail |
| No suspicious API calls | [ ] Pass / [ ] Fail |
| Appropriate tool restrictions | [ ] Pass / [ ] Fail |
| Code is readable | [ ] Pass / [ ] Fail |

---

## 3. Patterns to Incorporate

From existing skills and research:

1. **[Pattern Name]**: [How to apply it]
2. **[Pattern Name]**: [How to apply it]
3. **[Pattern Name]**: [How to apply it]

---

## 4. Gaps to Address

What existing skills don't cover that our skill needs:

1. [Gap 1]
2. [Gap 2]
3. [Gap 3]

---

## 5. Design Decisions

### Scope

**In scope:**
- [Feature 1]
- [Feature 2]

**Out of scope:**
- [Feature X] (covered by `[other-skill]`)
- [Feature Y] (too complex for v1)

### Structure

- [ ] Single file (< 300 lines)
- [ ] Multi-file (needs reference docs)

### Integration Points

- Prerequisite skills: [skills that should run before]
- Follow-up skills: [skills that should run after]
- Related skills: [skills that cover adjacent domains]

---

## 6. Description Draft

```yaml
description: [Draft description with trigger keywords]
```

**Trigger keywords included:**
- [keyword 1]
- [keyword 2]
- [keyword 3]

---

## 7. Next Steps

- [ ] Write SKILL.md using template
- [ ] Create supporting files (if multi-file)
- [ ] Test triggering
- [ ] Test execution
- [ ] Commit and push
- [ ] Run `/compound` to capture learnings
