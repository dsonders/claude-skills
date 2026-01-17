---
name: lab
description: Autonomous iterative refinement laboratory for optimization, testing, and improvement cycles. Sets up instrumentation, establishes baselines, runs hypothesis-driven iterations (think → build → test → review → repeat), and generates before/after reports. Use for performance optimization, UI refinement, AI prompt tuning, or any task requiring measured improvement.
---

# Lab: Autonomous Iterative Refinement Laboratory

This skill creates a structured "laboratory" environment for iterative improvement. Instead of ad-hoc changes, you build measurement infrastructure first, establish baselines, then systematically iterate with measurable results.

## When to Use This Skill

**Use this skill when:**
- Optimizing performance (making something faster)
- Refining UI to match a design (pixel-perfect implementation)
- Tuning AI prompts (improving output quality)
- Any task where you need to measure improvement
- User says "optimize", "refine", "improve", "make it better"
- You need autonomous iteration cycles with clear success criteria

**Don't use this skill for:**
- Finding and fixing bugs (use `/deep-debug` instead)
- Creating test coverage (use `/app-testing` instead)
- One-time implementations with no refinement needed
- Tasks without measurable outcomes

## Core Principles

1. **Instrumentation First**: Build measurement infrastructure before touching any code
2. **Baseline Before Changes**: Always know where you started
3. **Hypothesis-Driven**: Each iteration tests a specific hypothesis
4. **One Change at a Time**: Isolate variables to know what worked
5. **Measurable Outcomes**: If you can't measure it, you can't improve it
6. **Commit Checkpoints**: Save progress after each successful iteration

## Lab Types

The /lab skill adapts to different refinement scenarios:

| Lab Type | Goal | Instrumentation | Success Metric |
|----------|------|-----------------|----------------|
| **Performance** | Make it faster | Timing utilities, profilers | Execution time, memory |
| **UI Refinement** | Match design spec | Screenshots, visual diff | Design deviation count |
| **AI/Prompt** | Improve output quality | Test scenarios, rubrics | Rubric score, pass rate |
| **Quality** | Reduce errors | Error counters, logs | Error rate, severity |

## Workflow

Make a todo list for all tasks in this workflow and work through them systematically.

### Phase 1: Lab Setup & Instrumentation

**Before touching any code, build your laboratory.**

1. **Clarify the Goal**
   Ask the user:
   - What are we optimizing/refining?
   - What does "better" look like? (specific, measurable)
   - What constraints exist? (time, breaking changes, etc.)
   - How many iteration cycles should we run?

2. **Identify Lab Type**
   Based on the goal, determine which type of lab to set up:

   **Performance Lab:**
   ```typescript
   // Create timing harness
   const startTime = performance.now();
   // ... code to measure ...
   const duration = performance.now() - startTime;
   console.log(`[PERF] Operation took ${duration.toFixed(2)}ms`);
   ```
   - Add `console.time` markers to critical paths
   - Create a benchmark script that runs N iterations
   - Capture memory usage if relevant

   **UI Refinement Lab:**
   - Use browser automation (Playwright MCP, Chrome DevTools MCP) for screenshots
   - Create visual comparison workflow
   - List all elements to check: spacing, colors, typography, alignment

   **AI/Prompt Lab:**
   - Create test scenarios with inputs and expected outputs
   - Build scoring rubric (what makes output "good"?)
   - Create evaluation harness that runs all scenarios

   **Quality Lab:**
   - Instrument error logging
   - Create error categorization
   - Build metrics collection

3. **Create Lab Artifacts**
   Create files to track the lab:
   ```
   [feature]-lab/
   ├── baseline.md       # Initial measurements
   ├── hypotheses.md     # What we'll test
   ├── iterations.md     # Log of each iteration
   └── report.md         # Final before/after report
   ```

### Phase 2: Establish Baseline

**Record the current state before any changes.**

1. **Run Instrumentation**
   Execute your measurement harness against the current code.

2. **Document Baseline**
   ```markdown
   ## Baseline Measurements
   Date: [timestamp]
   Commit: [hash]

   ### Metrics
   - [Metric 1]: [value]
   - [Metric 2]: [value]
   - [Metric 3]: [value]

   ### Observations
   - [What you notice about current state]
   ```

3. **Identify Bottlenecks/Issues**
   Analyze the baseline to find the top 3-5 areas for improvement.

4. **Create Git Tag (optional)**
   ```bash
   git tag lab-baseline-[feature]
   ```

### Phase 3: Hypotheses

**Form specific, testable hypotheses before making changes.**

For each identified issue:

```markdown
## Hypothesis [N]

### Problem
[What's wrong - be specific]

### Theory
[Why you think this is happening]

### Proposed Fix
[Exactly what change you'll make]

### Expected Outcome
[Quantified prediction: "Should reduce X by Y%"]

### Research (optional)
[Any web search for known gotchas with libraries/patterns involved]
```

**Example Hypotheses:**

Performance:
> "The API is slow because we're making N+1 database queries. Batching queries should reduce response time from 800ms to under 200ms."

UI Refinement:
> "The button spacing is off because we're using margin-4 instead of margin-6. Changing to margin-6 should match the Figma spec exactly."

AI/Prompt:
> "The AI is adding tool references in Strict mode because the prohibition isn't explicit enough. Adding a specific 'CANNOT DO' example should eliminate this."

### Phase 4: Iteration Loop

**Work through each hypothesis one at a time.**

```
┌─────────────────────────────────────────────┐
│                ITERATION LOOP               │
│                                             │
│  1. SELECT hypothesis to test               │
│           ↓                                 │
│  2. MAKE the change (one change only)       │
│           ↓                                 │
│  3. RUN instrumentation                     │
│           ↓                                 │
│  4. COMPARE to baseline                     │
│           ↓                                 │
│  5. DECIDE: Keep? Revert? Modify?           │
│           ↓                                 │
│  6. COMMIT if keeping                       │
│           ↓                                 │
│  7. UPDATE baseline if improved             │
│           ↓                                 │
│  8. REPEAT with next hypothesis             │
└─────────────────────────────────────────────┘
```

**For each iteration, document:**

```markdown
## Iteration [N]: [Hypothesis Name]

### Change Made
[Specific code change]

### Results
- Before: [metric values]
- After: [metric values]
- Delta: [+/- change]

### Decision
[X] Keep - Improved by [X]%
[ ] Revert - No improvement / regression
[ ] Modify - Partial improvement, needs adjustment

### Commit
[commit hash if kept]
```

**Stopping Conditions:**
- All hypotheses tested
- Reached iteration limit (ask user for limit if not specified)
- Achieved target metric
- Diminishing returns (< 5% improvement per iteration)

### Phase 5: Report

**Generate a comprehensive before/after report.**

```markdown
# Lab Report: [Feature/Goal]

## Summary
- **Goal**: [What we were trying to improve]
- **Iterations**: [N] cycles
- **Duration**: [time spent]
- **Result**: [Success/Partial/Failed]

## Before vs After

| Metric | Baseline | Final | Improvement |
|--------|----------|-------|-------------|
| [Metric 1] | [value] | [value] | [+/- %] |
| [Metric 2] | [value] | [value] | [+/- %] |

## What Worked
1. [Change that improved metrics]
2. [Change that improved metrics]

## What Didn't Work
1. [Change that was reverted and why]

## Commits
- [hash] - [message]
- [hash] - [message]

## Recommendations
- [Any follow-up work needed]
- [Architectural changes flagged but not implemented]
```

**For UI refinement labs, include visual comparison:**
- Side-by-side screenshots (before/after)
- Or checklist of fixed issues

**For performance labs, include charts if possible:**
- Timing comparison bar chart
- Memory usage over time

## Handling Blockers

**When blocked, ask the user rather than guessing:**

- Missing API keys or credentials
- Need architectural decision
- Unclear acceptance criteria
- External dependency issues

**If you hit something requiring larger architectural change:**
1. Document it in the report
2. Flag it as "out of scope for this lab"
3. Move on to next hypothesis

## Environment Considerations

**Check environment capabilities before choosing instrumentation:**

| Environment | Available Tools | Limitations |
|-------------|-----------------|-------------|
| **Local terminal** | All tools, Playwright, profilers | None |
| **Claude Code web** | Jest, static analysis | No browser automation |
| **CI/CD** | Automated tests only | No interactive debugging |

If browser automation is needed but unavailable:
- Create manual testing checklist
- Document expected visual states
- Provide reproduction steps

## Integration with Other Skills

```
/lab (this skill)
  ├── May invoke /deep-debug if bugs found during iteration
  ├── May invoke /app-testing to create regression tests
  └── Should invoke /compound after completion to capture learnings

/tech-research → /lab (research informs optimization approach)
```

## RO-bot Specific Considerations

When running labs for RO-bot:

1. **Mobile-First**: Always test on iOS Safari if UI-related
2. **Data Isolation**: Verify organization_id not affected by changes
3. **Two-Pass System**: For AI writer labs, verify Pass 2 still conditional
4. **Character Limits**: Measure output lengths against org limits

## Success Criteria

Lab execution is complete when:

- [ ] Instrumentation was built before making changes
- [ ] Baseline was recorded with specific metrics
- [ ] Each iteration tested one hypothesis
- [ ] Changes that improved metrics were committed
- [ ] Changes that didn't improve were reverted
- [ ] Final report shows before/after comparison
- [ ] User has clear understanding of what improved

## Example Lab Sessions

### Performance Optimization Lab
```
User: "This API endpoint is too slow, optimize it"

Lab Setup:
- Add timing to endpoint
- Run 100 requests, record P50/P95/P99

Baseline:
- P50: 450ms, P95: 800ms, P99: 1200ms

Hypotheses:
1. N+1 queries - batch them
2. Missing database index
3. Unnecessary serialization

Iterations:
1. Added batching → P50: 180ms (-60%)
2. Added index → P50: 120ms (-33% more)
3. Lazy serialization → P50: 110ms (-8%)

Report: Improved P50 from 450ms to 110ms (76% faster)
```

### AI Prompt Tuning Lab
```
User: "The AI writer isn't using the new vocabulary"

Lab Setup:
- Create 7 test scenarios
- Build rubric (vocabulary used? conditions preserved?)
- Score each scenario pass/fail

Baseline:
- 3/7 scenarios passing

Hypotheses:
1. Transformations not explicit
2. Operating conditions not emphasized
3. Strict mode over-elaborating

Iterations:
1. Added explicit mappings → 5/7 passing
2. Added CRITICAL emphasis → 6/7 passing
3. Added CANNOT DO examples → 7/7 passing

Report: Improved from 43% to 100% pass rate
```

## Troubleshooting

### Can't Measure Improvement
**Problem:** No clear metric to track
**Solution:** Work with user to define success criteria before starting. If truly unmeasurable, this might not be a /lab task.

### Environment Limitations
**Problem:** Can't run automated tests (e.g., no API key, web sandbox)
**Solution:** Pivot to static analysis or create manual testing checklist. Document what would be tested with full environment.

### Iteration Not Improving
**Problem:** Multiple iterations with no improvement
**Solution:**
1. Verify instrumentation is correct
2. Check if hypothesis was valid
3. Consider if problem is elsewhere
4. Ask user for more context

### Too Many Hypotheses
**Problem:** Identified 10+ things to try
**Solution:** Prioritize by expected impact. Start with top 3-5. Re-evaluate after those complete.
