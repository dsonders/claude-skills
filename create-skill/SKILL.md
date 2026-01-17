---
name: create-skill
description: Systematic workflow for creating or evaluating Claude Code skills. Validates need, researches existing skills, designs structure, writes the skill, and tests activation. Use when creating a new skill, evaluating external skills for adoption, automating a repeated workflow, or formalizing a process.
---

# Create Skill: Systematic Skill Development Workflow

This skill provides a research-first, systematic approach to creating new Claude Code skills. It ensures skills are well-designed, don't duplicate existing solutions, and follow established patterns.

## When to Use This Skill

**Use this skill when:**
- Creating a new skill from scratch
- Formalizing a workflow that's been repeated 5+ times
- Automating a multi-step process that's error-prone when done manually
- Building on patterns from existing skills
- Evaluating external skills for adoption (use research phase to assess fit)
- User explicitly asks to create a skill

**Don't use this skill for:**
- Simple one-off commands (use `.claude/commands/` instead)
- Documenting existing work (use `/compound` skill)
- Research without implementation intent (use `/tech-research` skill)

## Core Principles

1. **Research First**: Search for existing skills before building from scratch
2. **Validate Need**: Apply the 5-10 rule — done 5+ times, expect 10+ more
3. **Progressive Disclosure**: Keep SKILL.md under 500 lines, use supporting files
4. **Focused Scope**: One domain per skill; multiple focused skills compose better
5. **Description Determines Activation**: Write descriptions with specific trigger keywords
6. **Test Before Ship**: Verify both triggering and execution work correctly

## Skill Creation Workflow

Make a todo list for all tasks in this workflow and work through them systematically.

### Step 1: Validate the Need

Before creating a skill, validate that it's warranted.

**The 5-10 Rule:**
- Has this workflow been performed at least 5 times?
- Will it be performed at least 10 more times?
- Does it require 3+ steps to execute correctly?

**Differentiation Check:**
- Is this distinct from existing skills?
- Would it conflict with or duplicate another skill?
- Could an existing skill be extended instead?

**Ask the user:**
```
Before creating this skill, let me validate:
1. How many times have you done this workflow?
2. How often do you expect to do it in the future?
3. What goes wrong when the steps aren't followed precisely?
```

**If validation fails:** Suggest alternatives:
- Add to an existing skill
- Create a simple command instead (`.claude/commands/`)
- Document as a pattern in lessons-learned

### Step 2: Research Existing Skills

Search for existing skills that might solve the problem or inform the design.

**Search these resources:**

1. **Curated Skill Collections:**
   - [awesome-claude-skills (travisvn)](https://github.com/travisvn/awesome-claude-skills)
   - [awesome-claude-skills (VoltAgent)](https://github.com/VoltAgent/awesome-claude-skills)

2. **Web Search:**
   ```
   "[domain] claude code skill"
   "[workflow] claude skill github"
   "claude code [task] automation"
   ```

3. **Project Skills:**
   Review existing skills in `.claude/skills/` for patterns and integration points.

**Evaluation Criteria:**

| Criterion | Question |
|-----------|----------|
| **Adoptable** | Can we use this skill as-is? |
| **Adaptable** | Does it need modifications for our context? |
| **Learnable** | What patterns or approaches can we borrow? |
| **Secure** | Does it follow security best practices? |

**Security Review (for external skills):**
- [ ] No hardcoded credentials or secrets
- [ ] No suspicious external API calls
- [ ] Tool restrictions are appropriate
- [ ] Code is readable and understandable

**Document findings:**
```markdown
## Existing Skills Research

### Skills Found
- [Skill Name](URL) - [Brief description]
  - Verdict: Adopt / Adapt / Learn from / Skip
  - Reason: [Why this verdict]

### Patterns to Incorporate
- [Pattern from research]

### Gaps to Address
- [What existing skills don't cover]
```

### Step 3: Design the Skill Structure

Based on research and requirements, design the skill structure.

**Required Elements:**

```yaml
---
name: skill-name           # lowercase, hyphens, max 64 chars
description: [description] # max 1024 chars, include trigger keywords
---
```

**Description Writing Guidelines:**

The description determines when Claude activates your skill. Include:
- What the skill does (action words)
- When to use it (trigger scenarios)
- Key domain terms (for matching)

**Good Example:**
```yaml
description: Systematic debugging workflow for persistent, tricky, or recurring bugs. Creates reproduction tests, investigates with git archaeology, uses automated testing to validate fixes. Use when debugging difficult bugs, investigating regressions, or when a bug keeps returning.
```

**Bad Example:**
```yaml
description: Helps with bugs.
```

**Optional Frontmatter Fields:**

| Field | Use When |
|-------|----------|
| `allowed-tools` | Restricting which tools the skill can use |
| `context: fork` | Running in isolated sub-agent context |
| `user-invocable: false` | Skill should only be triggered by Claude, not user |

**File Structure Decision:**

```
Single File (< 300 lines):
skill-name/
└── SKILL.md

Multi-File (complex skills):
skill-name/
├── SKILL.md           # Overview, workflow (< 500 lines)
├── reference.md       # Detailed documentation
├── examples.md        # Usage examples
└── templates/         # Reusable templates
    └── template.md
```

### Step 4: Write the Skill Content

Follow the established pattern from existing skills in this project.

**Standard Structure:**

```markdown
---
name: skill-name
description: [Trigger-optimized description]
---

# Skill Name: Descriptive Title

[1-2 sentence overview of what this skill does]

## When to Use This Skill

**Use this skill when:**
- [Specific trigger scenario 1]
- [Specific trigger scenario 2]
- [Specific trigger scenario 3]

**Don't use this skill for:**
- [Out-of-scope scenario 1] (use `other-skill` instead)
- [Out-of-scope scenario 2]

## Core Principles

1. **[Principle Name]**: [Brief explanation]
2. **[Principle Name]**: [Brief explanation]
3. **[Principle Name]**: [Brief explanation]

## Workflow

Make a todo list for all tasks in this workflow and work through them systematically.

### Step 1: [Step Name]

[Instructions for this step]

**Key actions:**
- [Action 1]
- [Action 2]

### Step 2: [Step Name]
[Continue for each step...]

## [Domain] Specific Considerations

[Project-specific guidance, e.g., RO-bot mobile-first, data isolation]

## Integration with Other Skills

[How this skill relates to others in the ecosystem]

## Success Criteria

The skill execution is complete when:
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Troubleshooting

### [Common Issue]
**Problem:** [Description]
**Solution:** [How to fix]
```

**Writing Tips:**

1. **Be specific, not generic** — Include exact commands, file paths, code patterns
2. **Use tables for comparisons** — When to use X vs Y
3. **Include code examples** — Copy-paste ready templates
4. **Reference other skills** — For out-of-scope tasks
5. **Define success clearly** — Checklist of completion criteria

### Step 5: Test the Skill

Test both triggering and execution separately.

**Triggering Tests:**

Create test prompts that should activate the skill:

```markdown
## Triggering Test Cases

### Should Trigger
- "[Prompt that should activate this skill]"
- "[Another prompt that should activate]"

### Should NOT Trigger
- "[Prompt that should NOT activate this skill]"
- "[Edge case that might incorrectly trigger]"
```

**Run each test prompt and verify:**
- [ ] Skill activates for "should trigger" cases
- [ ] Skill does NOT activate for "should not trigger" cases
- [ ] If activation is inconsistent, broaden/narrow the description

**Execution Tests:**

Run through the full workflow with a real scenario:

- [ ] All steps are clear and executable
- [ ] No missing context or undefined terms
- [ ] Tool usage is appropriate
- [ ] Success criteria are achievable
- [ ] Error cases are handled

**If issues found:**
- Adjust description for triggering issues
- Add specificity to instructions for execution issues
- Add validation steps if outputs are inconsistent

### Step 6: Document and Integrate

After the skill is working:

**Update Pattern Index (if applicable):**

If this skill introduces a new pattern, add it to `docs/Claude.md`:

```markdown
## Skills Reference

| Skill | Use When |
|-------|----------|
| `/create-skill` | Creating new skills systematically |
```

**Integration Points:**

Document how this skill connects to others:

```markdown
## Skill Ecosystem

create-skill → (creates) → new-skill
    ↓
compound → (documents learnings from creation)
```

**Commit the skill:**

```bash
git add .claude/skills/[skill-name]/
git commit -m "feat: add /[skill-name] skill for [purpose]

- [Key feature 1]
- [Key feature 2]
- Integrates with [other skills]"
```

### Step 7: Run Compound

After creating the skill, use `/compound` to capture learnings:

- What patterns were used in creating this skill?
- What research was most valuable?
- Should the skill creation process itself be improved?

---

## Quick Reference: Skill Anatomy

```
┌─────────────────────────────────────────┐
│ FRONTMATTER                             │
│ - name (required)                       │
│ - description (required, triggers)      │
│ - allowed-tools (optional)              │
│ - context: fork (optional)              │
├─────────────────────────────────────────┤
│ HEADER                                  │
│ - Title with descriptive subtitle       │
│ - 1-2 sentence overview                 │
├─────────────────────────────────────────┤
│ SCOPE                                   │
│ - When to use (triggers)                │
│ - When NOT to use (boundaries)          │
├─────────────────────────────────────────┤
│ PRINCIPLES                              │
│ - 3-6 guiding principles                │
├─────────────────────────────────────────┤
│ WORKFLOW                                │
│ - Numbered steps                        │
│ - Clear actions per step                │
│ - Decision points marked                │
├─────────────────────────────────────────┤
│ DOMAIN SPECIFICS                        │
│ - Project-specific guidance             │
│ - Common patterns/anti-patterns         │
├─────────────────────────────────────────┤
│ INTEGRATION                             │
│ - Related skills                        │
│ - Handoff points                        │
├─────────────────────────────────────────┤
│ SUCCESS CRITERIA                        │
│ - Completion checklist                  │
├─────────────────────────────────────────┤
│ TROUBLESHOOTING                         │
│ - Common issues and fixes               │
└─────────────────────────────────────────┘
```

---

## RO-bot Specific Considerations

When creating skills for RO-bot, always consider:

1. **Mobile-First**: Will this skill's outputs work on iOS Safari?
2. **Data Isolation**: Does the skill handle organization_id correctly?
3. **Server-Centric**: Does it follow the API-first architecture?
4. **Testing Integration**: Should it reference `/app-testing` for verification?

---

## Integration with Other Skills

```
tech-research  → Research phase of skill creation
     ↓
create-skill   → Design and build the skill (this skill)
     ↓
app-testing    → Test skill-generated code (if applicable)
     ↓
compound       → Document learnings from skill creation
```

**Skill Relationships:**
- Use `/tech-research` for deep technical research before designing complex skills
- Use `/compound` after creating a skill to capture learnings
- Reference `/app-testing` in skills that generate testable code
- Reference `/deep-debug` in skills that involve debugging workflows

---

## Success Criteria

Skill creation is complete when:

- [ ] Skill passes the 5-10 validation rule
- [ ] Existing skills were researched (no duplication)
- [ ] SKILL.md follows the standard structure
- [ ] Description includes specific trigger keywords
- [ ] Triggering tests pass (activates when expected)
- [ ] Execution tests pass (workflow is complete and clear)
- [ ] Skill is integrated with related skills
- [ ] Skill is committed with descriptive message
- [ ] `/compound` captured creation learnings

---

## Troubleshooting

### Skill Doesn't Trigger

**Problem:** User prompts don't activate the skill
**Solutions:**
- Broaden description with more trigger keywords
- Add specific use cases to description
- Check for conflicts with other skill descriptions

### Skill Triggers Incorrectly

**Problem:** Skill activates for unrelated prompts
**Solutions:**
- Narrow description to be more specific
- Add domain-specific terms
- Use "Don't use when" section more explicitly

### Skill Workflow Is Incomplete

**Problem:** Users get stuck mid-workflow
**Solutions:**
- Add more specific instructions to ambiguous steps
- Include example outputs for each step
- Add decision tree for edge cases

### Skill Is Too Long

**Problem:** SKILL.md exceeds 500 lines
**Solutions:**
- Move detailed reference to `reference.md`
- Move examples to `examples.md`
- Keep SKILL.md as overview + workflow only

---

## References

**Official Documentation:**
- [Claude Code Skills Docs](https://code.claude.com/docs/en/skills) — Complete skill creation guide
- [Building Skills for Claude Code](https://claude.com/blog/building-skills-for-claude-code) — Best practices from Anthropic

**Skill Collections:**
- [awesome-claude-skills (travisvn)](https://github.com/travisvn/awesome-claude-skills) — Curated skill list
- [awesome-claude-skills (VoltAgent)](https://github.com/VoltAgent/awesome-claude-skills) — Community skills

**Meta-Prompting:**
- [Prompt Engineering Guide - Meta Prompting](https://www.promptingguide.ai/techniques/meta-prompting) — Creating prompts for prompts

**Project Skills:**
- `/compound` — Document learnings after skill creation
- `/tech-research` — Deep research for complex skill design
- `/app-testing` — Testing patterns for skill-generated code
