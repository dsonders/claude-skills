# Lab Skill Testing Notes

## Triggering Test Cases

### Should Trigger
- "Optimize this API endpoint - it's too slow"
- "Make this function faster"
- "Refine the UI to match the Figma design"
- "Tune the AI prompts to improve output quality"
- "Run some iterations to improve the test pass rate"
- "Set up a lab to optimize performance"
- "I need to iteratively improve this feature"

### Should NOT Trigger
- "Fix this bug" (→ /deep-debug)
- "Add tests for this feature" (→ /app-testing)
- "Research how to implement X" (→ /tech-research)
- "Create a new skill" (→ /create-skill)
- "Document what we learned" (→ /compound)

## Description Keywords Analysis

The description includes these key trigger phrases:
- "Autonomous iterative refinement laboratory"
- "optimization, testing, and improvement cycles"
- "instrumentation, establishes baselines"
- "hypothesis-driven iterations"
- "think → build → test → review → repeat"
- "before/after reports"
- "performance optimization"
- "UI refinement"
- "AI prompt tuning"
- "measured improvement"

## Differentiation from Other Skills

| User Request | Correct Skill | Why |
|--------------|---------------|-----|
| "Optimize X" | `/lab` | Iterative improvement with measurement |
| "Fix bug in X" | `/deep-debug` | Finding and fixing, not optimizing |
| "Add tests for X" | `/app-testing` | Creating coverage, not iterating |
| "Research X" | `/tech-research` | Understanding, not implementing |
| "Refine UI" | `/lab` or `/ui-design` | /lab if measuring iterations, /ui-design for one-pass |

## Execution Test Scenarios

### Scenario 1: Performance Optimization
```
User: "This API is slow, optimize it"
Expected:
1. Create timing harness
2. Measure baseline
3. Identify hypotheses
4. Iterate through fixes
5. Generate report
```

### Scenario 2: AI Prompt Tuning
```
User: "The AI output quality isn't good enough, can you tune it?"
Expected:
1. Create test scenarios with rubric
2. Score baseline
3. Form hypotheses about prompt improvements
4. Iterate through changes
5. Generate before/after report
```

### Scenario 3: UI Refinement
```
User: "Refine this component to match the Figma"
Expected:
1. Set up screenshot comparison
2. List all differences
3. Fix one at a time
4. Verify each fix
5. Report what was fixed
```
