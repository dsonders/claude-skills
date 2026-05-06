---
name: app-testing
description: Comprehensive automated testing workflow for the RO-bot main app (Express+React+Firestore at /ro-bot/app/). Creates proactive tests for new features, manages test suites, uses Playwright MCP for visual debugging, and ensures organization data isolation. Covers Jest unit + API tests, Playwright E2E, mobile/iOS Safari. Use ONLY in /ro-bot/app/ — not for the marketing website (Astro) or GTM workspace.
---

# App Testing: Comprehensive Automated Testing for RO-bot

**Scope:** This skill is specific to the RO-bot main app at `/ro-bot/app/`. The Jest config, Playwright setup, fixtures, organization-isolation patterns, and `__tests__/{unit,api,e2e}/` layout described here only exist in that subproject. Do not invoke from `website/` (Astro static site, no Jest setup) or `GTM/` (no test infrastructure).

This skill provides a systematic approach to creating and managing automated tests for the RO-bot application. It covers all testing layers from unit tests to visual E2E testing with Playwright MCP.

## When to Use This Skill

**Use this skill when:**
- Implementing a new feature (create tests proactively)
- Asked to "add tests for X" or "test this feature"
- Verifying data isolation between organizations
- Debugging mobile/iOS Safari issues visually
- Managing or organizing the test suite
- Before committing significant changes

**Don't use this skill for:**
- Debugging existing bugs (use `deep-debug` skill instead)
- Simple one-line fixes that don't need tests
- Research tasks (use `tech-research` skill)

## Core Principles

1. **Test Before or With Code:** Write tests alongside new features, not after
2. **Investigation First:** Understand what needs testing before writing tests
3. **Data Isolation is Critical:** All tests must verify organization_id filtering
4. **Mobile-First Testing:** iOS Safari is the primary user environment
5. **Layered Testing:** Use the right test type for each scenario

## Testing Layers Overview

| Layer | Tool | When to Use | RO-bot Focus |
|-------|------|-------------|--------------|
| **Unit** | Jest | Pure logic, data transformations | AI inference modes, warranty processing |
| **API** | Jest + Supertest | Endpoint validation | organization_id filtering, auth |
| **E2E** | Playwright | Full user workflows | Video upload, voice recording |
| **Visual** | Playwright MCP | UI debugging, screenshots | iOS Safari issues |

## Test Directory Structure

```
__tests__/
├── unit/                    # Jest unit tests
│   ├── services/            # Server service tests
│   └── lib/                 # Shared library tests
├── api/                     # API endpoint tests (Jest + Supertest)
│   ├── helpers/
│   │   └── test-setup.ts    # Auth mocking, test org setup
│   └── [endpoint].test.ts
├── e2e/                     # Playwright E2E tests
│   ├── flows/
│   │   └── [flow].spec.ts
│   └── helpers/
│       └── e2e-setup.ts     # Login, mobile gestures
└── fixtures/                # Shared test data
    └── mock-data.ts
```

## Workflow

Make a todo list for all tasks in this workflow and work through them systematically.

### Step 0: Read Project Context

**First, read the project context file:**

Read the file `docs/CLAUDE_CODE_CONTEXT.md` - it has all the project context, architecture rules, and working style preferences. This ensures you understand the critical patterns like organization_id filtering and server-centric architecture.

### Step 1: Identify What Needs Testing

Before writing any tests, understand what you're testing:

**For New Features:**
1. What is the feature's purpose?
2. What components are involved? (API endpoints, services, UI components)
3. What data flows through the feature?
4. Does it involve organization-scoped data? (Almost always YES in RO-bot)
5. Does it have mobile/touch interactions?

**For Existing Code:**
1. What functionality is untested?
2. What are the critical paths?
3. What has caused bugs before?

**Ask clarifying questions if needed:**
- "What's the most critical behavior to test here?"
- "Are there edge cases I should focus on?"
- "Should this feature work offline?"

### Step 2: Determine Test Types Needed

Based on Step 1, determine which test types are appropriate:

**Unit Tests (Jest) - Use When:**
- Testing pure functions or utilities
- Testing data transformations
- Testing business logic without external dependencies
- Testing AI prompt processing or inference modes

**API Tests (Jest + Supertest) - Use When:**
- Testing Express API endpoints
- Verifying authentication/authorization
- **CRITICAL: Testing organization_id data isolation**
- Testing error handling and validation

**E2E Tests (Playwright) - Use When:**
- Testing full user workflows
- Testing multi-step processes (video upload, voice recording)
- Testing mobile-specific behaviors
- Testing UI interactions

**Visual Tests (Playwright MCP) - Use When:**
- Debugging UI issues that are hard to describe
- Testing iOS Safari specific rendering
- Verifying visual layouts and animations
- Interactive debugging sessions

### Step 3: Write Unit Tests (If Applicable)

**File Location:** `__tests__/unit/[category]/[feature].test.ts`

**Pattern for RO-bot Services:**

```typescript
import { ServiceName } from '../../../server/services/service-name';

describe('ServiceName', () => {
  describe('methodName', () => {
    // Test normal behavior
    test('returns expected result for valid input', () => {
      const result = ServiceName.methodName(validInput);
      expect(result).toEqual(expectedOutput);
    });

    // Test edge cases
    test('handles empty input gracefully', () => {
      const result = ServiceName.methodName('');
      expect(result).toBeNull();
    });

    // Test error conditions
    test('throws error for invalid input', () => {
      expect(() => ServiceName.methodName(invalidInput)).toThrow();
    });
  });
});
```

**AI Inference Mode Testing Pattern:**

```typescript
describe('Warranty Processor Inference Modes', () => {
  test('strict mode only formats without adding details', async () => {
    const input = 'brake pads worn to 2mm';
    const result = await processWithMode(input, 'strict');

    // Strict mode should NOT add diagnostic details
    expect(result.cause).not.toContain('manufacturer minimum specification');
    expect(result.cause).toContain('2mm');
  });

  test('enhanced mode adds comprehensive details', async () => {
    const input = 'brake pads worn to 2mm';
    const result = await processWithMode(input, 'enhanced');

    // Enhanced mode SHOULD add diagnostic context
    expect(result.cause).toContain('manufacturer');
    expect(result.cause.length).toBeGreaterThan(100);
  });
});
```

### Step 4: Write API Tests (If Applicable)

**File Location:** `__tests__/api/[endpoint].test.ts`

**CRITICAL: All API tests MUST verify organization_id filtering**

**Pattern for RO-bot API Endpoints:**

```typescript
import request from 'supertest';
import { app } from '../../server/app';
import { TEST_ORGS, TEST_USERS, getAuthHeader } from './helpers/test-setup';

describe('GET /api/repair-orders', () => {
  describe('Organization Data Isolation', () => {
    // CRITICAL TEST: Cross-org data leakage prevention
    test('user from Org A cannot access Org B data', async () => {
      // Create repair order for Org B
      const orgBOrder = await createTestRepairOrder(TEST_ORGS.ORG_B.id);

      // Request as user from Org A
      const response = await request(app)
        .get('/api/repair-orders')
        .set(getAuthHeader(TEST_USERS.TECH_ORG_A))
        .expect(200);

      // Should NOT contain Org B's data
      const orders = response.body;
      expect(orders).not.toContainEqual(
        expect.objectContaining({ id: orgBOrder.id })
      );
    });

    test('returns only data for user organization', async () => {
      // Create orders for both orgs
      await createTestRepairOrder(TEST_ORGS.ORG_A.id);
      await createTestRepairOrder(TEST_ORGS.ORG_B.id);

      const response = await request(app)
        .get('/api/repair-orders')
        .set(getAuthHeader(TEST_USERS.TECH_ORG_A))
        .expect(200);

      // All returned orders should be from Org A
      response.body.forEach(order => {
        expect(order.organization_id).toBe(TEST_ORGS.ORG_A.id);
      });
    });
  });

  describe('Authentication', () => {
    test('returns 401 without auth token', async () => {
      await request(app)
        .get('/api/repair-orders')
        .expect(401);
    });

    test('returns 403 with invalid token', async () => {
      await request(app)
        .get('/api/repair-orders')
        .set('Authorization', 'Bearer invalid-token')
        .expect(403);
    });
  });

  describe('Endpoint Behavior', () => {
    test('returns repair orders for authenticated user', async () => {
      const response = await request(app)
        .get('/api/repair-orders')
        .set(getAuthHeader(TEST_USERS.TECH_ORG_A))
        .expect(200);

      expect(Array.isArray(response.body)).toBe(true);
    });
  });
});
```

### Step 5: Write E2E Tests (If Applicable)

**File Location:** `__tests__/e2e/flows/[flow].spec.ts`

**Pattern for RO-bot User Flows:**

```typescript
import { test, expect, devices } from '@playwright/test';
import { login, pressAndHoldToRecord, SELECTORS } from '../helpers/e2e-setup';

// Test on mobile Safari (primary RO-bot user environment)
test.describe('Video Upload Flow', () => {
  // Mobile Safari configuration
  test.use({
    ...devices['iPhone 13'],
    browserName: 'webkit',
  });

  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.goto('/repair-orders/123');
  });

  test('user can upload video inspection', async ({ page }) => {
    // Click video inspection button
    await page.click('[data-testid="start-video-inspection"]');

    // Verify shot list appears
    await expect(page.locator(SELECTORS.SHOT_LIST)).toBeVisible();

    // Upload video
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('./test-assets/sample-video.webm');

    // Wait for upload progress
    await expect(page.locator(SELECTORS.VIDEO_PROGRESS)).toBeVisible();

    // Wait for completion (allow up to 5 minutes for large videos)
    await expect(page.locator('[data-testid="upload-complete"]'))
      .toBeVisible({ timeout: 300000 });
  });

  test('upload survives page navigation (service worker)', async ({ page }) => {
    // Start upload
    await page.click('[data-testid="start-video-inspection"]');
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('./test-assets/sample-video.webm');

    // Wait for upload to start
    await expect(page.locator(SELECTORS.VIDEO_PROGRESS)).toBeVisible();

    // Navigate away
    await page.goto('/dashboard');

    // Navigate back
    await page.goto('/repair-orders/123');

    // Upload should still complete (handled by service worker)
    await expect(page.locator('[data-testid="upload-complete"]'))
      .toBeVisible({ timeout: 300000 });
  });
});

test.describe('Voice Recording Flow', () => {
  test.use({
    ...devices['iPhone 13'],
    permissions: ['microphone'],
  });

  test('press-and-hold recording works on iOS Safari', async ({ page }) => {
    await login(page);
    await page.goto('/repair-orders/123');

    // Test press-and-hold pattern
    await pressAndHoldToRecord(page, 3000);

    // Verify transcription appears
    await expect(page.locator('[data-testid="transcription-result"]'))
      .toBeVisible({ timeout: 10000 });
  });
});
```

### Step 6: Use Playwright MCP for Visual Debugging (If Needed)

**When to use Playwright MCP:**
- UI looks wrong but code seems correct
- iOS Safari rendering issues
- Animation/transition problems
- Complex interaction debugging

**How to invoke Playwright MCP:**

Say: "Use Playwright MCP to debug [issue]" or "Take a screenshot of [page/element]"

**Playwright MCP Capabilities:**
- Navigate to URLs
- Take screenshots
- Click elements
- Fill forms
- Analyze page accessibility tree
- Interact with the page visually

**Example debugging session:**

```
User: "The header animation doesn't work on iOS Safari"

Claude (using Playwright MCP):
1. Navigate to the page with iOS Safari emulation
2. Take screenshot of initial state
3. Trigger the animation
4. Take screenshot after animation
5. Compare expected vs actual behavior
6. Check for CSS transform overrides (common iOS issue)
```

**Common iOS Safari issues to check with Playwright MCP:**
- CSS transform overrides (check `@supports (-webkit-touch-callout: none)`)
- Touch event handling differences
- Viewport scaling issues
- Service worker behavior differences

### Step 7: Run and Verify Tests

**Run commands:**

```bash
# Run all Jest tests
npm test

# Run only unit tests
npm run test:unit

# Run only API tests
npm run test:api

# Run Playwright E2E tests
npm run test:e2e

# Run E2E with visible browser
npm run test:e2e:headed

# Run E2E on mobile only
npm run test:e2e:mobile

# Run with coverage
npm run test:coverage
```

**Verify test results:**
- All tests pass
- Coverage meets expectations
- No flaky tests
- Mobile tests pass (critical for RO-bot)

### Step 8: Document Test Coverage

After creating tests, document what's covered:

```markdown
## Test Coverage: [Feature Name]

### Unit Tests
- `__tests__/unit/services/[feature].test.ts`
  - ✅ [Test case 1]
  - ✅ [Test case 2]

### API Tests
- `__tests__/api/[endpoint].test.ts`
  - ✅ Organization data isolation
  - ✅ Authentication
  - ✅ [Endpoint behavior]

### E2E Tests
- `__tests__/e2e/flows/[flow].spec.ts`
  - ✅ Desktop Chrome
  - ✅ Mobile Safari (iOS)
  - ✅ Mobile Chrome (Android)

### Manual Testing Required
- [ ] Real device testing on iPhone
- [ ] Poor network conditions
```

## RO-bot Specific Testing Patterns

### Data Isolation Testing (CRITICAL)

**Every endpoint that returns user data MUST have this test:**

```typescript
test('prevents cross-organization data access', async () => {
  // Create data for Org A
  const orgAData = await createData(TEST_ORGS.ORG_A.id);

  // Create data for Org B
  const orgBData = await createData(TEST_ORGS.ORG_B.id);

  // Request as Org A user
  const response = await request(app)
    .get('/api/endpoint')
    .set(getAuthHeader(TEST_USERS.TECH_ORG_A));

  // MUST NOT contain Org B data
  expect(response.body).not.toContainEqual(
    expect.objectContaining({ organization_id: TEST_ORGS.ORG_B.id })
  );
});
```

### iOS Safari Testing (CRITICAL)

**Use Playwright with webkit browser:**

```typescript
test.use({
  ...devices['iPhone 13'],
  browserName: 'webkit',
});

test('feature works on iOS Safari', async ({ page }) => {
  // Test the feature
});
```

**Common iOS Safari issues to test:**
1. Large Blob transfers (use IndexedDB, not postMessage)
2. Touch events (different from mouse events)
3. CSS transforms (may be overridden)
4. Service worker behavior

### Video Upload Testing

```typescript
test.describe('Video Upload', () => {
  test('handles large videos via service worker', async ({ page }) => {
    // Verify upload uses IndexedDB pattern
    // NOT postMessage (fails on iOS Safari)
  });

  test('upload survives page navigation', async ({ page }) => {
    // Start upload, navigate away, verify completion
  });

  test('shows progress accurately', async ({ page }) => {
    // Verify progress indicator updates
  });
});
```

### Voice Recording Testing

```typescript
test.describe('Voice Recording', () => {
  test.use({
    permissions: ['microphone'],
  });

  test('press-and-hold pattern works', async ({ page }) => {
    // Simulate press, hold, release
    // Verify recording starts and stops correctly
  });

  test('transcription appears after recording', async ({ page }) => {
    // Record audio, verify Whisper transcription appears
  });
});
```

### AI Output Testing

```typescript
describe('AI Inference Modes', () => {
  test('strict mode never fabricates details', async () => {
    const input = 'brake pads worn';
    const result = await processWithMode(input, 'strict');

    // Strict mode should only format, not add
    expect(result).not.toContain('manufacturer specification');
    expect(result).not.toContain('recommended');
  });

  test('enhanced mode adds appropriate context', async () => {
    // Enhanced mode can add diagnostic context
    // But should never FABRICATE specific values
  });
});
```

## Test Helpers Reference

### API Test Helpers (`__tests__/api/helpers/test-setup.ts`)

```typescript
// Test organizations
TEST_ORGS.ORG_A, TEST_ORGS.ORG_B

// Test users
TEST_USERS.TECH_ORG_A, TEST_USERS.TECH_ORG_B, TEST_USERS.ADMIN_ORG_A

// Auth header for requests
getAuthHeader(TEST_USERS.TECH_ORG_A)

// Organization filter verification
expectOrganizationFilter(data, expectedOrgId)

// Data isolation test helper
await testDataIsolation({ createData, fetchData })
```

### E2E Test Helpers (`__tests__/e2e/helpers/e2e-setup.ts`)

```typescript
// Login helper
await login(page, credentials)

// Voice recording helper
await pressAndHoldToRecord(page, durationMs)

// iOS touch simulation
await iosTouchStart(page, selector)

// Upload completion wait
await waitForUploadComplete(page, timeoutMs)

// Poor network simulation
await simulatePoorNetwork(context)

// Mobile gestures
await mobileGestures.swipe(page, 'left', 200)
await mobileGestures.longPress(page, selector, 500)
```

### Mock Data (`__tests__/fixtures/mock-data.ts`)

```typescript
MOCK_VEHICLES.TOYOTA_CAMRY
MOCK_REPAIR_ORDERS.BRAKE_REPAIR
MOCK_VIDEO_INSPECTIONS.BRAKE_VIDEO
MOCK_TRANSCRIPTIONS.BRAKE_DIAGNOSIS
MOCK_AI_OUTPUTS.STRICT_MODE
MOCK_VIDEO_SIZES.SMALL_30_SECONDS
```

## Slash Commands for Manual Testing

Use these commands to manually trigger test runs:

- `/test` - Run all tests
- `/test:unit` - Run unit tests only
- `/test:api` - Run API tests only
- `/test:e2e` - Run E2E tests
- `/test:mobile` - Run mobile-specific E2E tests

## Success Criteria

Tests are complete when:

- ✅ All critical paths have test coverage
- ✅ Data isolation is verified for all user data endpoints
- ✅ Tests pass on mobile (especially iOS Safari)
- ✅ Tests run quickly (unit < 1s, API < 5s, E2E < 60s each)
- ✅ No flaky tests
- ✅ Coverage documented

## Troubleshooting

### Tests Pass Locally, Fail on Mobile

1. Check for iOS Safari specific CSS issues
2. Verify touch events vs mouse events
3. Check Blob transfer patterns (use IndexedDB)
4. Test on actual device, not just simulator

### Flaky E2E Tests

1. Add explicit waits instead of arbitrary timeouts
2. Use `expect(...).toBeVisible()` before interactions
3. Check for race conditions
4. Increase timeout for network-dependent tests

### Data Isolation Test Fails

1. Verify query includes `organization_id` filter
2. Check for missing WHERE clauses
3. Ensure test setup creates data in correct org
4. Verify auth middleware sets `req.userProfile.organization_id`

---

Remember: Testing is not just about finding bugs - it's about building confidence that the code works correctly, especially for data isolation and mobile compatibility which are critical for RO-bot.
