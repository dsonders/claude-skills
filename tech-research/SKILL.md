---
name: tech-research
description: Structured workflow for researching new features, technical capabilities, and third-party integrations. Analyzes existing architecture, researches solutions, evaluates options, and provides recommendations with proof-of-concept code.
---

# Research Skill: Feature & Technology Exploration

This skill provides a systematic approach to researching new features, UX elements, technical capabilities, and third-party integrations for the RO-bot application.

## When to Use This Skill

**Use this skill when:**
- Exploring a new feature idea or UX element
- Evaluating third-party libraries or services
- Researching technical approaches for a capability
- Understanding how a technology might integrate with existing architecture
- Comparing multiple solutions to a problem
- Need to understand external APIs or documentation

**Don't use this skill for:**
- Debugging existing features (use `deep-debug` instead)
- Simple implementation tasks with clear requirements
- Questions about existing code (use direct code exploration)

## Core Principles

1. **Understand Before Research:** Know your current architecture first
2. **Broad Then Narrow:** Start wide, then focus on promising options
3. **Evaluate Against Architecture:** Ensure compatibility with existing patterns
4. **Document Findings:** Create clear, actionable recommendations
5. **Validate with Examples:** Provide proof-of-concept code when possible

## Workflow

Make a todo list for all tasks in this workflow and work through them systematically.

### Step 1: Understand the Request

Gather information about what needs to be researched:

1. **Feature Description:** What capability or UX element is needed?
2. **Use Case:** How will users interact with this feature?
3. **Context:** Why is this needed now? What problem does it solve?
4. **Constraints:** Any technical, budget, or timeline constraints?
5. **Success Criteria:** What would make this a good solution?

**Ask clarifying questions if needed:**
- "What's the primary user problem this solves?"
- "Are there any existing solutions you've seen that you like?"
- "Any specific technologies you want to explore or avoid?"
- "What devices/browsers need to be supported?"

**Document the request clearly before proceeding.**

### Step 2: Analyze Existing Architecture

Before researching external solutions, understand the current codebase:

**First, read the project context:**
- Read the file `docs/CLAUDE_CODE_CONTEXT.md` - it has all the project context, architecture rules, and working style preferences.

**Key questions to answer:**
1. **What exists today?** Search for similar features or related code
2. **Architecture patterns:** What patterns does RO-bot use?
   - Server-centric API endpoints vs. client-side Firestore?
   - State management approaches?
   - UI component patterns?
3. **Technology stack:** What's already in use?
   - Frontend frameworks and libraries
   - Backend services and APIs
   - Third-party integrations
4. **Data flow:** How does data move through the system?
   - Organization-based filtering?
   - API patterns?
   - Real-time vs. request/response?

**Actions to take:**
```bash
# Search for related code
# Example: If researching video features
rg -i "video|media|upload" --type ts --type tsx

# Check package.json for existing dependencies
cat package.json | grep -A 50 "dependencies"

# Look for similar UX patterns
find src/components -name "*.tsx" | head -20
```

**Document findings:**
- Relevant existing code and patterns
- Libraries already in use
- Architectural constraints to respect
- Data security requirements (especially organization_id filtering)

### Step 3: Research Solutions

Now research external solutions, documentation, and best practices:

**Web Research Strategy:**

1. **Official Documentation**
   - Find official docs for relevant technologies
   - Look for getting started guides
   - Check API references and examples

2. **Best Practices & Comparisons**
   - Search for "best [technology] for [use case] 2024"
   - Look for comparison articles
   - Check developer community discussions (Stack Overflow, Reddit, GitHub)

3. **Real-World Examples**
   - Find open-source projects using the technology
   - Look for demo applications
   - Check CodeSandbox/CodePen examples

4. **Mobile Compatibility** (Critical for RO-bot)
   - Verify iOS Safari support
   - Check touch/mobile interaction patterns
   - Look for known mobile issues

**Web Search Examples:**
```
# For a new UI component
"react [component-type] library comparison 2024"
"[component] mobile-first iOS Safari"
"headless [component] react"

# For a third-party service
"[service] API documentation"
"[service] pricing tiers"
"[service] react integration example"

# For technical capability
"[capability] browser support 2024"
"[capability] mobile device compatibility"
"progressive web app [capability]"
```

**Document for each option:**
- Official documentation URL
- Key features and limitations
- Mobile/iOS Safari support
- Pricing (if applicable)
- Bundle size / performance impact
- Community activity (GitHub stars, recent updates)

### Step 4: Narrow Down Options

Based on research, identify 2-4 promising options:

**Evaluation Criteria:**

1. **Architectural Fit**
   - ✅ Matches RO-bot patterns (server-centric, organization filtering)
   - ✅ Works with existing tech stack (React, Firebase, Next.js, etc.)
   - ✅ Doesn't require major architectural changes

2. **Mobile-First Compatibility**
   - ✅ Works on iOS Safari (primary user base)
   - ✅ Touch-friendly interactions
   - ✅ Handles poor connectivity gracefully
   - ✅ Reasonable bundle size for mobile

3. **Developer Experience**
   - ✅ Good documentation
   - ✅ Active maintenance
   - ✅ TypeScript support
   - ✅ Clear examples available

4. **Production Readiness**
   - ✅ Stable version available
   - ✅ Used in production by others
   - ✅ Security considerations addressed
   - ✅ Performance characteristics acceptable

5. **Cost & Licensing**
   - ✅ Free tier or reasonable pricing
   - ✅ MIT/Apache or compatible license
   - ✅ No vendor lock-in

**Create a comparison table:**
```
| Option | Pros | Cons | Mobile Support | Cost | Fit Score (1-10) |
|--------|------|------|----------------|------|------------------|
| Option A | ... | ... | Excellent | Free | 8/10 |
| Option B | ... | ... | Good | $99/mo | 6/10 |
```

**Present to user:** "Based on my research, I've narrowed it down to these options. Which would you like me to explore further?"

### Step 5: Deep Dive on Top Choice(s)

For the most promising option(s), do a detailed investigation:

**Technical Deep Dive:**

1. **Read the Documentation**
   - Getting started guide
   - Core concepts
   - API reference for key features
   - Migration/integration guides

2. **Examine Example Code**
   - Official examples
   - Community examples
   - Real production implementations

3. **Check GitHub Repository** (if open source)
   - Issues related to iOS Safari or mobile
   - Recent commits and activity
   - Open security issues
   - Bundle size and dependencies

4. **Review Integration Steps**
   - Installation requirements
   - Configuration needed
   - Code changes required
   - Data migration considerations

**Document:**
- Step-by-step integration plan
- Potential gotchas or challenges
- Code examples specific to RO-bot's use case
- Timeline estimate for implementation

### Step 6: Create Proof of Concept

Demonstrate how the solution would work in RO-bot:

**For UI Components:**
```tsx
// Create a simple example component
// Example: New date picker component
import { DatePicker } from 'proposed-library';

export function RepairOrderDatePicker() {
  const [date, setDate] = useState<Date>();

  return (
    <DatePicker
      value={date}
      onChange={setDate}
      // Show how it fits RO-bot patterns
      className="mobile-friendly"
    />
  );
}
```

**For Third-Party APIs:**
```typescript
// Example: AI service integration
async function analyzeRepairImage(imageUrl: string, orgId: string) {
  // Show how it integrates with organization filtering
  const response = await fetch('/api/analyze-image', {
    method: 'POST',
    body: JSON.stringify({ imageUrl, organization_id: orgId }),
  });

  return response.json();
}
```

**For Technical Capabilities:**
```typescript
// Example: Offline storage strategy
// Show how it works with service workers and IndexedDB
async function saveForOfflineAccess(data: RepairOrder) {
  const db = await openDB('ro-bot-offline');
  await db.put('repair-orders', data);
}
```

**Ask user:** "Should I create this proof-of-concept in the codebase to test it out?"

### Step 7: Synthesize Recommendations

Create a comprehensive summary with clear recommendations:

**Format:**
```markdown
## Research Summary: [Feature/Capability]

### Request
[Brief description of what was researched]

### Existing Architecture Analysis
- **Relevant existing code:** [File paths and patterns]
- **Current patterns:** [How RO-bot currently handles similar features]
- **Constraints:** [Technical or architectural limitations]

### Options Evaluated
1. **[Option A]**
   - Pros: [Key benefits]
   - Cons: [Limitations]
   - Mobile support: [iOS Safari compatibility]
   - Integration effort: [Low/Medium/High]

2. **[Option B]**
   - [Same format]

### Recommended Approach: [Option Name]

**Why this option:**
- [Reason 1: e.g., Best mobile support]
- [Reason 2: e.g., Fits existing architecture]
- [Reason 3: e.g., Active community]

**Integration Plan:**
1. [Step 1: e.g., Install package]
2. [Step 2: e.g., Create wrapper component]
3. [Step 3: e.g., Update API endpoint]

**Estimated Effort:** [X hours/days]

**Risks & Mitigations:**
- Risk: [Potential issue]
  - Mitigation: [How to address]

**Next Steps:**
1. [Immediate action, e.g., Get user approval]
2. [Following action, e.g., Create proof of concept]
3. [Final action, e.g., Implement in feature branch]

### Resources
- [Documentation URLs]
- [Example implementations]
- [Community discussions]
```

**Present this to the user for feedback and approval.**

### Step 8: Implementation Plan (Optional)

If user approves, create a detailed implementation plan:

**Break down into phases:**

**Phase 1: Setup & Dependencies**
- Install required packages
- Update configuration files
- Set up any required services/API keys

**Phase 2: Core Integration**
- Create wrapper components/utilities
- Implement basic functionality
- Follow RO-bot architectural patterns

**Phase 3: Mobile Optimization**
- Test on iOS Safari
- Add touch-friendly interactions
- Handle offline scenarios

**Phase 4: Testing & Validation**
- Create unit tests
- Create Playwright tests for mobile
- Verify organization_id filtering

**Phase 5: Documentation**
- Update code comments
- Document new patterns
- Create usage examples

**Ask user:** "Should I proceed with implementation, or would you like to handle it yourself with this research?"

## Special Considerations for RO-bot

### Mobile-First Research

**Always verify:**
- iOS Safari compatibility (primary user device)
- Touch interaction support
- Performance on mobile devices
- Offline/poor connectivity behavior

**Research questions:**
- "Does [solution] work on iOS Safari?"
- "What's the bundle size impact?"
- "Are there mobile-specific gotchas?"

### Organization-Based Multi-Tenancy

**Always consider:**
- How will organization_id filtering work?
- Can data leak between organizations?
- Does this fit server-centric pattern?

**Research questions:**
- "How does [solution] handle multi-tenant data?"
- "Can we enforce org filtering at API level?"
- "Are there security implications?"

### Progressive Web App (PWA) Context

**Remember RO-bot is a PWA:**
- Service worker compatibility
- Offline functionality
- IndexedDB for local storage
- Background sync capabilities

**Research questions:**
- "Does [solution] work in PWA context?"
- "Can it function offline?"
- "Service worker implications?"

### AI-Generated Content

**If researching AI capabilities:**
- Avoid fabricated details (use inference mode)
- Character limits for prompts
- Cost per API call
- Rate limiting considerations

## Research Best Practices

### Efficient Web Research

1. **Start with official sources** (documentation, GitHub)
2. **Look for recent content** (2024-2025 for current best practices)
3. **Cross-reference multiple sources** (don't trust single articles)
4. **Check for mobile-specific information** (critical for RO-bot)
5. **Verify license compatibility** (MIT, Apache preferred)

### Evaluating Third-Party Services

**Questions to answer:**
1. **Pricing:** Free tier? Cost at scale? Hidden fees?
2. **Reliability:** SLA? Uptime history? Status page?
3. **Data Privacy:** GDPR compliant? Data ownership? SOC2?
4. **Integration:** REST API? SDKs? Webhooks?
5. **Support:** Documentation quality? Community? Paid support?

### Open Source Library Evaluation

**GitHub health checks:**
```bash
# Check recent activity
git log --since="3 months ago" --oneline | wc -l

# Check open issues
gh issue list --limit 50

# Check dependencies
npm view [package-name] dependencies
```

**NPM health checks:**
- Last publish date (should be recent)
- Weekly downloads (indicates adoption)
- Bundle size (use bundlephobia.com)
- TypeScript definitions included?

## Success Criteria

Research is complete when:

- ✅ User's question/need is fully understood
- ✅ Existing architecture has been analyzed
- ✅ Multiple options have been evaluated
- ✅ Mobile/iOS Safari compatibility is verified
- ✅ Security and multi-tenancy concerns are addressed
- ✅ Clear recommendation with rationale is provided
- ✅ Proof-of-concept or examples are available
- ✅ Implementation plan is outlined (if requested)
- ✅ Resources and documentation are linked
- ✅ User has information needed to make decision

## Common Research Scenarios

### Scenario 1: New UI Component

**Example:** "Research a date picker for repair order scheduling"

**Workflow:**
1. Check existing date/time inputs in RO-bot
2. Research mobile-friendly date picker libraries
3. Verify iOS Safari support (critical)
4. Compare bundle sizes
5. Test touch interaction patterns
6. Recommend best option with example code

### Scenario 2: Third-Party Service Integration

**Example:** "Research AI services for damage assessment from photos"

**Workflow:**
1. Understand current image upload flow
2. Research computer vision APIs (OpenAI, Google Vision, etc.)
3. Compare pricing and accuracy
4. Check API rate limits
5. Design server-side integration (not client-side)
6. Ensure organization_id association
7. Provide cost estimates and example implementation

### Scenario 3: Technical Capability

**Example:** "Research offline video recording in PWA"

**Workflow:**
1. Check current video recording implementation
2. Research MediaRecorder API mobile support
3. Investigate IndexedDB for large video storage
4. Check iOS Safari limitations
5. Find workarounds for mobile issues
6. Create example service worker code
7. Recommend implementation approach

### Scenario 4: Architecture Pattern

**Example:** "Research state management approaches for real-time updates"

**Workflow:**
1. Analyze current state management (React Context, etc.)
2. Research options (Redux, Zustand, Jotai, etc.)
3. Evaluate fit with Firebase real-time updates
4. Consider server-centric constraints
5. Compare bundle sizes and complexity
6. Recommend pattern with migration path

## Tips for Effective Research

1. **Use todos liberally:** Track each research task and finding
2. **Document as you go:** Don't wait until the end to summarize
3. **Share findings incrementally:** Update user on progress
4. **Focus on mobile:** RO-bot is mobile-first, always verify
5. **Think security:** Organization isolation is critical
6. **Be practical:** Balance ideal solutions with implementation effort
7. **Provide examples:** Show, don't just tell
8. **Consider costs:** Both time and money

## When to Stop Researching

**Stop researching when:**
- You have 2-3 solid options evaluated
- Clear recommendation emerges
- User has enough information to decide
- Diminishing returns on additional research

**Don't fall into:**
- Analysis paralysis (too many options)
- Perfectionism (waiting for perfect solution)
- Scope creep (researching tangential topics)

**If stuck, ask user:** "I've found these options. Should I go deeper on any specific one, or is this enough to make a decision?"

---

Remember: The goal is actionable recommendations, not exhaustive research. Help the user make an informed decision and move forward with confidence.
