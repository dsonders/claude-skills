---
name: deep-debug
description: Systematic debugging workflow for persistent, tricky, or recurring bugs. Creates reproduction tests, investigates with git archaeology, uses automated testing to validate fixes, and prevents regressions. Particularly effective for data isolation issues, mobile browser quirks, and bugs that seemed fixed but returned.
---

# Deep Debug: Systematic Debugging for Persistent Issues

This skill provides a structured workflow for investigating bugs that are:
- Persistent and difficult to diagnose
- Recurring after seemingly being fixed
- Related to data isolation or mobile browser issues
- Requiring systematic hypothesis testing

## Core Principles

1. **Test-Driven Debugging:** Create reproduction tests before fixing
2. **One Issue at a Time:** Never stack multiple changes
3. **Git Archaeology:** Use commit history to understand when/how bugs were introduced
4. **Automated Validation:** Use tests instead of manual clicking
5. **Regression Prevention:** Ensure bugs can't return silently

## Testing Frameworks Available

**Jest** - For API endpoints, server-side logic, data isolation
**Playwright** - For mobile browser issues, service worker behavior, iOS Safari quirks
**React Testing Library** - For frontend component testing

## Workflow

Make a todo list for all tasks in this workflow and work through them systematically.

### Step 0: Read Project Context

**First, read the project context file:**

Read the file `CLAUDE_CODE_CONTEXT.md` located in the `docs` directory - it has all the project context, architecture rules, and working style preferences. This ensures you understand the codebase structure and follow the correct patterns during debugging.

### Step 1: Bug Intake & Classification

Gather comprehensive information about the bug:

1. **Symptoms:** What's happening vs. what should happen?
2. **Reproduction Steps:** Exact steps to trigger the bug
3. **Environment:** Browser, device, network conditions
4. **History:** When first noticed? Has it occurred before?
5. **Recent Changes:** Any related code changes recently?

**Classify the bug type:**
- **Data Isolation:** Cross-organization data leakage, missing organization_id filters
- **Mobile Browser:** iOS Safari issues, service worker problems, touch events
- **API/Backend:** Server-side logic, Firebase queries, authentication
- **AI Output:** Inference mode issues, fabricated details, character limits
- **UI/Frontend:** React components, user interactions, styling

Ask clarifying questions if needed before proceeding.

### Step 2: Propose Reproduction Test

Based on the bug classification, propose an appropriate test:

**For Data Isolation Bugs (Jest):**
```javascript
// Example: Test organization_id filtering
describe('Repair Orders API', () => {
  it('should only return repair orders for user org', async () => {
    // Test that queries include organization_id filter
  });
});
```

**For Mobile Browser Issues (Playwright):**
```javascript
// Example: Test iOS Safari video upload
test('video upload completes on iOS Safari', async ({ page }) => {
  // Test the full upload flow on mobile
});
```

**For API Endpoint Issues (Jest):**
```javascript
// Example: Test API validation
describe('POST /api/endpoint', () => {
  it('should validate required fields', async () => {
    // Test proper error handling
  });
});
```

**Show the proposed test to the user and ask:**
"Should I create this reproduction test? It will help us:
- Verify when the bug is actually fixed
- Catch regressions if the bug returns
- Reduce manual testing time"

**If user says yes:** Create the test file in the appropriate location
**If user says no:** Proceed with manual debugging

### Step 3: Run the Test (Should Fail)

If a test was created, run it to verify it fails with current code:

```bash
# For Jest tests
npm test path/to/test-file

# For Playwright tests
npx playwright test path/to/test-file
```

**Expected:** Test should fail, confirming it reproduces the bug.
**Document:** Save the test output for reference.

### Step 4: Code Archaeology

Investigate when and how this bug was introduced:

1. **Git Blame:** Check when relevant code was last changed
   ```bash
   git blame path/to/suspect-file.js
   ```

2. **Git Log:** Search for related changes
   ```bash
   git log --all --grep="keyword" --oneline
   git log -S"specific code" --oneline  # Search for code additions/removals
   ```

3. **Check Related PRs/Commits:** Read commit messages and changes
   ```bash
   git show <commit-hash>
   ```

4. **Look for Similar Patterns:** Search codebase for similar issues
   - Missing organization_id filters
   - iOS Safari workarounds
   - Service worker patterns

**Document findings:**
- When was related code last modified?
- Were there previous attempts to fix this?
- Are there similar issues elsewhere in the codebase?

### Step 5: Offer Git Bisect (for Regressions)

If the bug is a regression (it worked before), offer git bisect:

**Ask the user:**
"This appears to be a regression. Should I use git bisect to automatically find the exact commit that introduced this bug? This will:
- Save time vs. manual commit searching
- Pinpoint the exact change that broke it
- Help understand what went wrong"

**If user agrees:**

1. Create a bisect test script:
   ```bash
   cat > /tmp/bisect-test.sh << 'EOF'
   #!/bin/bash
   # Run the reproduction test
   npm test path/to/reproduction-test || exit 1
   exit 0
   EOF
   chmod +x /tmp/bisect-test.sh
   ```

2. Run git bisect:
   ```bash
   git bisect start
   git bisect bad HEAD  # Current version has the bug
   git bisect good <known-good-commit>  # User provides or we estimate
   git bisect run /tmp/bisect-test.sh
   ```

3. Document the guilty commit and analyze what changed.

### Step 6: Generate Hypotheses

Based on archaeology and test results, list potential root causes:

Example format:
```
Hypothesis 1: Missing organization_id filter in query
- Evidence: Similar queries elsewhere include it
- Test: Check if query includes organization_id parameter

Hypothesis 2: iOS Safari Blob transfer failing
- Evidence: Works on desktop, fails on iOS
- Test: Check if using postMessage for large Blobs

Hypothesis 3: Service worker not reading from IndexedDB
- Evidence: Upload progress stalls at 0%
- Test: Check service worker implementation
```

**Present hypotheses to user and work through them systematically.**

### Step 7: Test Hypotheses Systematically

For each hypothesis:

1. **Explain what you're testing**
2. **Make ONE targeted investigation** (read specific files, add logging, etc.)
3. **Report findings**
4. **Either eliminate or confirm hypothesis**
5. **Wait for user feedback before next hypothesis**

**Never stack multiple investigations in one step.**

### Step 8: Implement Fix

Once root cause is confirmed:

1. **Explain the fix approach**
2. **Show the specific code changes**
3. **Get user approval before implementing**
4. **Make the changes**
5. **Run the reproduction test** (should now pass)

**Critical checks for RO-bot:**
- Does fix maintain organization_id filtering?
- Does it follow server-centric pattern (API endpoints, not client Firestore)?
- Will it work on mobile (especially iOS Safari)?
- Does it avoid fabricating details in AI outputs?

### Step 9: Regression Testing

Run the full test suite to ensure no side effects:

```bash
# Run all tests
npm test

# Run Playwright tests if mobile-related
npx playwright test
```

**If any tests fail:**
- Investigate the failure
- Determine if it's a real regression or test issue
- Fix before proceeding

### Step 10: Test Creation for Mandatory Categories

**Mandatory test creation for these bug types** (even if not created earlier):

- **Data Isolation bugs:** Must have Jest test verifying organization_id filtering
- **Mobile browser issues:** Should have Playwright test for critical flows
- **API endpoint changes:** Must have Jest test for the endpoint
- **Security-critical code:** Must have comprehensive test coverage

**Ask user:** "Should I create additional tests to prevent this bug from recurring?"

### Step 11: Documentation

Create a clear summary of the investigation:

**Format:**
```
## Bug: [Brief Description]

**Root Cause:** [What actually caused the bug]

**Investigation Path:**
- [Key discoveries during debugging]
- [Dead ends that were eliminated]
- [The breakthrough that led to the fix]

**Fix Applied:**
- [Specific changes made]
- [Files modified with line numbers]

**Tests Created:**
- [Reproduction test location]
- [Regression tests added]

**Verification:**
- ✅ Reproduction test now passes
- ✅ Full test suite passes
- ✅ Manual testing completed on [devices/browsers]

**Prevention:**
- [What tests prevent recurrence]
- [Code patterns to watch for]
```

**Save this documentation** in a comment or commit message.

### Step 12: Commit Changes

Create a clear commit following git best practices:

```bash
# Stage relevant files
git add [modified files]

# Create descriptive commit
git commit -m "$(cat <<'EOF'
Fix: [Brief description of bug]

Root cause: [One sentence explanation]

Changes:
- [Specific changes made]

Tests:
- [Tests added/modified]

Fixes [issue number if applicable]
EOF
)"
```

**Push to the designated branch** (usually starts with `claude/`).

## Special Considerations for RO-bot

### Data Isolation Bugs - Critical Priority

**Always verify:**
- All queries include organization_id filtering
- No cross-organization data leakage possible
- Test with multiple organizations

**Test pattern:**
```javascript
it('prevents cross-org data access', async () => {
  // Create data for org A
  // Try to access from org B
  // Should fail or return empty
});
```

### iOS Safari Issues

**Common patterns to check:**
- Large Blob transfers (use IndexedDB, not postMessage)
- Microphone permissions (requires specific flow)
- Touch event handling (differs from desktop)
- Service worker behavior (test on real devices)

**Test with Playwright:**
```javascript
test.use({
  ...devices['iPhone 13'],
  browserName: 'webkit'  // Safari engine
});
```

### Mobile-First Debugging

**Remember:**
- Most usage is on mobile devices
- Test on actual devices, not just simulators
- Consider poor connectivity scenarios
- Handle interrupted workflows gracefully

## Rubber Duck Mode

If investigation is stuck, systematically ask:

1. **What exactly is the symptom?** (Not what we think causes it)
2. **What changed recently?** (Code, dependencies, environment)
3. **What assumptions am I making?** (Challenge each one)
4. **What haven't I checked yet?** (Service worker logs, network tab, IndexedDB)
5. **Does it work in a simpler case?** (Minimal reproduction)
6. **What do the tests tell me?** (Exact failure point)

**Present these questions to the user to think through together.**

## Success Criteria

The bug is fully resolved when:

- ✅ Reproduction test passes (if created)
- ✅ Full test suite passes
- ✅ Manual verification on relevant devices/browsers
- ✅ Root cause is understood and documented
- ✅ Regression tests prevent recurrence
- ✅ Code follows RO-bot architectural rules
- ✅ Changes are committed and pushed

## When to Use This Skill

**Use this skill when:**
- Bug has occurred multiple times
- Bug seems fixed but keeps returning
- Bug is difficult to reproduce manually
- Bug involves data isolation or mobile browsers
- User wants to reduce manual testing time
- Bug requires systematic investigation

**Don't use this skill for:**
- Simple typos or obvious fixes
- Initial exploratory debugging
- UI styling tweaks
- Configuration issues

---

Remember: Systematic debugging saves time in the long run. Taking time to understand root causes and create tests prevents the frustration of bugs that keep coming back.
