---
name: ui-design
description: Mobile-first UI design and refinement workflow for RO-bot. Covers component creation, visual polish, iOS Safari compatibility, React render optimization, and pattern establishment with clear rules for stack, accessibility, animation, and performance. Use for React performance issues, re-render optimization, or memoization questions.
---

# UI Design Skill: Mobile-First Interface Development

This skill provides a systematic approach to UI design and refinement for the RO-bot application, emphasizing mobile-first development, iOS Safari compatibility, and consistent use of established patterns.

## When to Use This Skill

**Use this skill when:**
- Creating new UI components or screens
- Refining existing UI for mobile usability
- Fixing iOS Safari-specific visual issues
- Reducing visual clutter or improving information hierarchy
- Adding animations or micro-interactions
- Establishing new UI patterns for the codebase
- Optimizing React component re-renders or performance
- Questions about useMemo, useCallback, or memoization

**Don't use this skill for:**
- Pure logic/API changes with no UI impact
- Debugging non-UI bugs (use `/deep-debug` instead)
- Researching third-party UI libraries (use `/tech-research` instead)
- Writing tests (use `/app-testing` instead)

## Core Principles

1. **Mobile-First Always:** Design for iOS Safari on phone first, then scale up
2. **Use What Exists:** Check existing components before creating new ones
3. **Accessibility by Default:** Use primitives with built-in keyboard/focus behavior
4. **Animation with Purpose:** Only animate when it aids comprehension or feedback
5. **Test on Real Devices:** Browser dev tools are not sufficient for iOS Safari
6. **Document New Patterns:** Use `/compound` to capture patterns worth reusing

---

## Codebase Reference

Before making UI changes, know where things live:

| What | Location |
|------|----------|
| UI Primitives | `client/src/components/ui/` (47 shadcn/ui components) |
| Design Tokens | `client/src/index.css` (lines 209-263) |
| cn utility | `client/src/lib/utils.ts` |
| iOS Safari fixes | `client/src/index.css` (lines 1-130) |
| Layout/Safe Areas | `client/src/components/layout.tsx` |
| MPI Components | `client/src/components/mpi/` (good pattern examples) |

**Design Token Colors:**
```
Brand:   brand-teal (#2A9D8F), brand-orange (#FB923C), brand-blue (#3B82F6)
Status:  success (green), warning (amber), error (red), info (sky)
```

**Z-Index Scale (established):**
```
50      Dialog overlays, fixed headers
999     Full-screen modals
1000+   Voice/chat overlays
9999    PWA standalone background
```

---

## UI Rules

### Stack

- MUST use Tailwind CSS defaults (spacing, radius, shadows) before custom values
- MUST use `framer-motion` for JavaScript-driven animation (already in codebase)
- SHOULD use `tailwindcss-animate` for entrance and micro-animations
- MUST use `cn` utility (`clsx` + `tailwind-merge`) for class logic
- MUST use `cva` (class-variance-authority) for component variants

### Components

- MUST check `client/src/components/ui/` for existing primitives first
- MUST use Radix UI primitives (via shadcn/ui) for keyboard/focus behavior
- NEVER mix primitive systems within the same interaction surface
- MUST add `aria-label` to icon-only buttons
- NEVER rebuild keyboard or focus behavior by hand unless explicitly requested
- SHOULD use CVA pattern for components with multiple variants:

```tsx
const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground",
        destructive: "bg-destructive text-destructive-foreground",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 px-3",
        lg: "h-11 px-8",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)
```

### Interaction

- MUST use `AlertDialog` for destructive or irreversible actions
- SHOULD use structural skeletons for loading states
- NEVER use `h-screen`, use `h-dvh` (dynamic viewport height)
- MUST respect `safe-area-inset` for fixed elements (see iOS Safari section)
- MUST show errors next to where the action happens
- NEVER block paste in `input` or `textarea` elements
- MUST use minimum 44px touch targets for tappable elements
- SHOULD use minimum 8px gap between adjacent touch targets

### Animation

- NEVER add animation unless explicitly requested or clearly aids UX
- MUST animate only compositor props (`transform`, `opacity`)
- NEVER animate layout properties (`width`, `height`, `top`, `left`, `margin`, `padding`)
- SHOULD avoid animating paint properties (`background`, `color`) except for small UI elements
- SHOULD use `ease-out` on entrance animations
- NEVER exceed `200ms` for interaction feedback
- MUST pause looping animations when off-screen
- MUST respect `prefers-reduced-motion`:

```tsx
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
```

- NEVER introduce custom easing curves unless explicitly requested
- SHOULD avoid animating large images or full-screen surfaces

### Typography

- MUST use `text-balance` for headings and `text-pretty` for body/paragraphs
- MUST use `tabular-nums` for numeric data (measurements, prices, counts)
- SHOULD use `truncate` or `line-clamp` for dense UI
- NEVER modify `letter-spacing` (`tracking-`) unless explicitly requested

### Layout

- MUST use the established z-index scale (no arbitrary `z-[x]`)
- SHOULD use `size-x` for square elements instead of `w-x h-x`
- MUST use existing safe area utilities: `.ios-safe-bottom`, `.safe-area-top`

### Performance

- NEVER animate large `blur()` or `backdrop-filter` surfaces
- NEVER apply `will-change` outside an active animation
- NEVER use `useEffect` for anything that can be expressed as render logic
- SHOULD use `content-visibility: auto` for long scrollable lists (defers off-screen rendering)
- SHOULD hoist static JSX outside components (avoids recreation every render)

### React Render Optimization

These patterns prevent unnecessary re-renders in React components:

**State Updates:**
- MUST use functional setState when updating based on previous state:
```tsx
// ❌ Requires state as dependency
const addItem = useCallback((item: Item) => {
  setItems([...items, item])
}, [items])

// ✅ Stable callback, no dependencies
const addItem = useCallback((item: Item) => {
  setItems(prev => [...prev, item])
}, [])
```

- MUST use lazy initialization for expensive initial state:
```tsx
// ❌ Runs on every render
const [index, setIndex] = useState(buildSearchIndex(items))

// ✅ Runs only once
const [index, setIndex] = useState(() => buildSearchIndex(items))
```

**Dependencies:**
- SHOULD narrow effect dependencies to primitives:
```tsx
// ❌ Re-runs on any user field change
useEffect(() => {
  console.log(user.id)
}, [user])

// ✅ Re-runs only when id changes
useEffect(() => {
  console.log(user.id)
}, [user.id])
```

**Memoization:**
- SHOULD extract expensive computations into memoized child components:
```tsx
// ❌ Computes even when loading
function Profile({ user, loading }: Props) {
  const avatar = useMemo(() => computeAvatar(user), [user])
  if (loading) return <Skeleton />
  return <div>{avatar}</div>
}

// ✅ Skips computation when loading (early return)
function Profile({ user, loading }: Props) {
  if (loading) return <Skeleton />
  return <div><UserAvatar user={user} /></div>
}

const UserAvatar = memo(({ user }: { user: User }) => {
  const avatar = useMemo(() => computeAvatar(user), [user])
  return <Avatar src={avatar} />
})
```

**Derived State:**
- SHOULD subscribe to boolean state instead of continuous values:
```tsx
// ❌ Re-renders on every pixel
function Sidebar() {
  const width = useWindowWidth()
  const isMobile = width < 768
  return <nav className={isMobile ? 'mobile' : 'desktop'} />
}

// ✅ Re-renders only when boolean changes
function Sidebar() {
  const isMobile = useMediaQuery('(max-width: 767px)')
  return <nav className={isMobile ? 'mobile' : 'desktop'} />
}
```

### JavaScript Optimization

These micro-patterns have cumulative impact in hot paths:

- MUST use `Set`/`Map` for O(1) lookups instead of array `.includes()`:
```tsx
// ❌ O(n) per check
const allowedIds = ['a', 'b', 'c']
items.filter(item => allowedIds.includes(item.id))

// ✅ O(1) per check
const allowedIds = new Set(['a', 'b', 'c'])
items.filter(item => allowedIds.has(item.id))
```

- MUST use `.toSorted()` instead of `.sort()` to avoid mutating props/state:
```tsx
// ❌ Mutates original array (can corrupt React state)
const sorted = users.sort((a, b) => a.name.localeCompare(b.name))

// ✅ Creates new sorted array
const sorted = users.toSorted((a, b) => a.name.localeCompare(b.name))
```

- SHOULD use early returns when result is determined:
```tsx
// ❌ Processes all items even after finding error
function validate(users: User[]) {
  let hasError = false
  for (const user of users) {
    if (!user.email) hasError = true
  }
  return hasError ? { valid: false } : { valid: true }
}

// ✅ Returns immediately on first error
function validate(users: User[]) {
  for (const user of users) {
    if (!user.email) return { valid: false, error: 'Email required' }
  }
  return { valid: true }
}
```

- SHOULD build index Maps for repeated lookups:
```tsx
// ❌ O(n) per lookup = O(n²) total
const enriched = orders.map(order => ({
  ...order,
  user: users.find(u => u.id === order.userId)
}))

// ✅ O(1) per lookup = O(n) total
const userById = new Map(users.map(u => [u.id, u]))
const enriched = orders.map(order => ({
  ...order,
  user: userById.get(order.userId)
}))
```

### Design

- NEVER use gradients unless explicitly requested
- NEVER use purple or multicolor gradients
- NEVER use glow effects as primary affordances
- SHOULD use Tailwind CSS default shadow scale
- MUST give empty states one clear next action
- SHOULD limit accent color usage to one per view
- MUST use existing theme tokens before introducing new colors

---

## iOS Safari Patterns

iOS Safari is the primary browser for RO-bot users. These patterns are critical.

### Required Global Styles (already in index.css)

```css
* {
  -webkit-tap-highlight-color: transparent;
  -webkit-touch-callout: none;
  -webkit-overflow-scrolling: touch;
}
```

### Focus State Fix

iOS Safari triggers `:focus-visible` on tap, causing buttons to stay highlighted. Fix:

```tsx
const handleTap = (e: React.MouseEvent<HTMLButtonElement>) => {
  e.currentTarget.blur(); // Remove focus immediately
  // ... handle action
};

// Plus CSS overrides if needed:
className="focus:!ring-0 focus:!ring-offset-0 focus-visible:!ring-0"
```

### Touch Manipulation

For buttons and interactive elements, prevent tap delay:

```tsx
className="touch-manipulation"
```

### Safe Area Handling

For fixed bottom elements:

```tsx
// Use existing utility class
className="ios-safe-bottom"

// Or inline
style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
```

For fixed top elements:

```tsx
className="safe-area-top"
// Or
style={{ paddingTop: 'env(safe-area-inset-top)' }}
```

### Dialog/Modal Positioning

Dialogs need special handling on iOS:

```tsx
// Detect iOS
const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) ||
              (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);

// Apply iOS-specific styles
const iosStyles: React.CSSProperties = isIOS ? {
  position: 'fixed',
  touchAction: 'manipulation',
  WebkitTapHighlightColor: 'transparent',
} : {};
```

### Momentum Scrolling

For scrollable containers:

```tsx
style={{ WebkitOverflowScrolling: 'touch' }}
className="overscroll-behavior-none"
```

---

## Status Color System

RO-bot uses a consistent green/yellow/red status system:

```tsx
// Background colors (use for rows, cards)
function getStatusBgClass(status: 'green' | 'yellow' | 'red' | 'none') {
  switch (status) {
    case 'green': return 'bg-green-50 hover:bg-green-100';
    case 'yellow': return 'bg-orange-50 hover:bg-orange-100';
    case 'red': return 'bg-red-50 hover:bg-red-100';
    default: return 'hover:bg-gray-50';
  }
}

// Value/badge colors (use for indicators)
function getStatusValueClass(status: 'green' | 'yellow' | 'red' | 'none') {
  switch (status) {
    case 'green': return 'bg-green-500 text-white';
    case 'yellow': return 'bg-orange-500 text-white';
    case 'red': return 'bg-red-500 text-white';
    default: return 'bg-gray-200 text-gray-500';
  }
}
```

---

## Workflow

### For UI Refinement (polishing existing UI)

1. **Understand Current State**
   - Read the component(s) being refined
   - Identify specific issues (clutter, touch targets, iOS bugs, etc.)
   - Check if similar patterns exist elsewhere in codebase

2. **Plan Changes**
   - List specific changes with rationale
   - Verify changes follow UI rules above
   - Identify any iOS Safari considerations

3. **Implement Incrementally**
   - Make one logical change at a time
   - Test in browser dev tools (mobile viewport) after each change
   - Keep commits small and focused

4. **Test on Real Device**
   - Test on physical iOS Safari
   - Check touch targets, focus states, safe areas
   - Verify animations respect reduced motion

5. **Iterate or Revert**
   - If change doesn't work, `git revert HEAD` immediately
   - Don't iterate on a broken approach—try something different

6. **Document if Notable**
   - If you discovered a new pattern or gotcha, consider `/compound`

### For Pattern Establishment (creating new patterns)

1. **Justify the Need**
   - Why can't existing patterns solve this?
   - What's the scope of reuse for this new pattern?
   - Is this a one-off or will it be used 3+ times?

2. **Research First**
   - Check how similar apps solve this
   - Verify iOS Safari compatibility
   - Consider accessibility implications

3. **Prototype Minimally**
   - Build the simplest version that works
   - Don't over-engineer on first implementation
   - Get user feedback before polishing

4. **Validate on Device**
   - Test on physical iOS Safari
   - Test with VoiceOver if accessibility-critical
   - Verify performance on older devices

5. **Refine Based on Feedback**
   - Iterate based on real usage
   - Add variants only when needed
   - Keep API surface minimal

6. **Document the Pattern**
   - Use `/compound` to capture:
     - What the pattern solves
     - When to use it
     - Code example
     - Known gotchas

---

## Common Tasks

### Adding a New Button Variant

```tsx
// In the component or button.tsx
const buttonVariants = cva(
  "...", // base classes
  {
    variants: {
      variant: {
        // Add new variant here
        success: "bg-green-600 hover:bg-green-700 text-white",
      },
    },
  }
)
```

### Creating a Status Badge

```tsx
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

<Badge className={cn(
  status === 'green' && "bg-green-100 text-green-800",
  status === 'yellow' && "bg-orange-100 text-orange-800",
  status === 'red' && "bg-red-100 text-red-800",
)}>
  {label}
</Badge>
```

### Adding a Touch-Friendly Button

```tsx
<Button
  onClick={(e) => {
    e.currentTarget.blur();
    handleAction();
  }}
  className={cn(
    "h-14 text-lg touch-manipulation",
    "active:scale-95 transition-transform",
    "focus:!ring-0 focus-visible:!ring-0"
  )}
>
  <Icon className="h-5 w-5 mr-2" />
  Action Label
</Button>
```

### Fixing iOS Focus Ring Issues

```tsx
// Add to any button that shows persistent focus on iOS
className="focus:!ring-0 focus:!ring-offset-0 focus-visible:!ring-0 focus-visible:!ring-offset-0 focus:!outline-none focus-visible:!outline-none"

// Plus blur on tap
onClick={(e) => {
  e.currentTarget.blur();
  // ... rest of handler
}}
```

### Adding Safe Area Padding

```tsx
// Bottom fixed element
<div className="fixed bottom-0 left-0 right-0 ios-safe-bottom bg-white border-t">
  {/* content */}
</div>

// Or with style
<div
  className="fixed bottom-0 left-0 right-0"
  style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
>
  {/* content */}
</div>
```

---

## Testing Checklist

Before considering UI work complete:

- [ ] Tested in browser dev tools (mobile viewport)
- [ ] Tested on physical iOS Safari device
- [ ] Touch targets are minimum 44px
- [ ] No persistent focus rings after tap
- [ ] Safe areas respected on notched devices
- [ ] Animations respect `prefers-reduced-motion`
- [ ] No layout shift on load
- [ ] Empty states have clear next action
- [ ] Error states show near the action that caused them
- [ ] Loading states use skeletons (not spinners for content)

---

## Anti-Patterns to Avoid

| Don't | Do Instead |
|-------|------------|
| `h-screen` | `h-dvh` |
| `z-[999]` arbitrary values | Use established scale (50, 999, 1000) |
| Rebuild focus management | Use Radix/shadcn primitives |
| Animate `width`/`height` | Animate `transform`/`opacity` |
| Custom colors | Use theme tokens |
| New component for one use | Inline or use existing |
| Test only in Chrome | Test on iOS Safari |
| Add animation "because it's nice" | Add only when it aids UX |

---

## Success Criteria

UI work is complete when:

- [ ] Changes follow the UI rules in this skill
- [ ] iOS Safari testing passed on physical device
- [ ] No accessibility regressions (focus, labels, contrast)
- [ ] Performance is acceptable (no jank, fast interactions)
- [ ] User has approved the visual changes
- [ ] New patterns documented via `/compound` (if applicable)

---

## References

- [MPI Mobile UX Polish](../../docs/lessons-learned/mpi-mobile-ux-polish.md) - Example refinement session
- [iOS Safe Area Patterns](../../docs/bug-reports/ios-safe-area-patterns.md) - Safe area solutions
- [iOS Media Permission Patterns](../../docs/bug-reports/ios-media-permission-patterns.md) - iOS-specific fixes
- [Shadcn/ui Components](https://ui.shadcn.com/docs/components) - Component documentation
- [Radix Primitives](https://www.radix-ui.com/primitives) - Underlying primitive docs
- [Vercel React Best Practices](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices) - Source for React/JS optimization patterns (adapted for non-Next.js stack)
