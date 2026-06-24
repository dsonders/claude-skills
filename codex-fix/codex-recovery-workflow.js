export const meta = {
  name: 'codex-recovery-review',
  description: 'Thorough multi-agent internal review of a PR that failed Codex review — mirrors Codex\'s own rubric across the FULL diff, adversarially verifies each finding, sweeps the whole class repo-wide, and returns one ordered fix plan so the next push passes in one round.',
  whenToUse: 'Invoked by the /codex-fix skill after a Codex BLOCK. Not run directly.',
  phases: [
    { title: 'Map', detail: 'inventory every changed file + symbol + the class each Codex finding belongs to' },
    { title: 'Review', detail: 'fan out reviewers across Codex\'s exact rubric over the full diff' },
    { title: 'Verify', detail: 'adversarially refute each finding; drop pre-existing/speculative/style' },
    { title: 'Synthesize', detail: 'dedupe across dimensions, group by class, emit one ordered fix plan' },
  ],
}

// args: { prNumber, baseRef, codexFindings, changedFiles }
//   prNumber     — the PR number (label/reporting only)
//   baseRef      — git ref to diff against (default 'origin/main'); agents run `git diff <baseRef>...HEAD`
//   codexFindings— the raw text of the Codex review comment (the P0/P1 lines). May be '' if not captured.
//   changedFiles — array of changed file paths (from `gh pr view --json files`)
const prNumber = (args && args.prNumber) || 'current'
const baseRef = (args && args.baseRef) || 'origin/main'
const codexFindings = (args && args.codexFindings) || '(Codex comment text was not captured — review the full diff against the rubric from scratch.)'
const changedFiles = (args && args.changedFiles) || []
const fileList = changedFiles.length ? changedFiles.join('\n') : '(file list not provided — derive it from `git diff --name-only ' + baseRef + '...HEAD`)'

const DIFF_CMD = 'git --no-pager diff ' + baseRef + '...HEAD'

const groundingBlock = `
## Ground truth (read FIRST, before forming any opinion)
- The PR under review is #${prNumber}. The change set is the diff of \`${DIFF_CMD}\`.
- Run that command yourself (and \`${DIFF_CMD} -- <file>\` per file) — review ONLY what this diff changes. Do NOT flag pre-existing code.
- Changed files:
${fileList}
- The Codex review that BLOCKED this PR said:
"""
${codexFindings}
"""
- The repo's cardinal rules live in AGENTS.md / CLAUDE.md at the repo root — read them and apply them strictly. Key ones: RULE #1 organization_id isolation (every user-data read/write is an org-scoped QUERY, never \`doc(id).get()\`+post-check), server-centric data ops, snake_case on raw Firestore reads, the new-Issue-field 5-step wiring checklist, the three auth patterns (authenticateWithOrganization middleware / inline getUserId / zero-auth sub-routes).
`

const wholeClassRule = `
## Whole-class rule (this is the whole point — RULE #7)
A Codex P0/P1 is almost always ONE instance of a SYSTEMIC gap. For EVERY finding you raise (whether Codex flagged it or you found it), you MUST grep the WHOLE repo for sibling instances of the same pattern and list every one in \`siblingLocations\`. Examples of a "class":
- a by-id Firestore read of user data → every other \`.doc(id).get()\` / by-id read of repair_orders/issues/vehicles/etc.
- a \`setCustomUserClaims\` that doesn't spread existing claims → every other claim-set site.
- an AI-route catch that echoes raw upstream text → every other AI route's catch.
- a new field with no read path → every layer of the 5-step Issue wiring.
- a sibling write-path that doesn't set a denorm gate field the read depends on → every writer of that field.
Fixing only the flagged line wastes a full (paid) Codex round per instance. Surface the whole class now.
`

const verifierBias = `
You are an ADVERSARIAL verifier. Default to refuted=true unless you can prove the finding is a real, reachable, diff-INTRODUCED defect. Codex itself does NOT flag (and neither should we): pre-existing code the diff didn't touch; pure style/formatting/naming; speculative "an attacker could…/a future caller might…" with no concrete trigger in this diff; concerns the diff already guards against. Read the actual code at the cited location before deciding.`

const MAP_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['files', 'codexClasses'],
  properties: {
    files: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['path', 'symbols', 'risk'],
        properties: {
          path: { type: 'string' },
          symbols: { type: 'array', items: { type: 'string' }, description: 'functions/classes/components changed in this file' },
          risk: { type: 'string', enum: ['auth-org', 'schema-data', 'pricing', 'destructive', 'customer-surface', 'ai-output', 'ui', 'other'] },
        },
      },
    },
    codexClasses: {
      type: 'array',
      description: 'For each Codex finding, the systemic class it belongs to and where else that class appears.',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['codexFinding', 'className', 'siblingLocations'],
        properties: {
          codexFinding: { type: 'string' },
          className: { type: 'string' },
          siblingLocations: { type: 'array', items: { type: 'string' } },
        },
      },
    },
  },
}

const FINDINGS_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['findings'],
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['severity', 'file', 'line', 'problem', 'fix', 'className', 'siblingLocations', 'diffIntroduced', 'reachable'],
        properties: {
          severity: { type: 'string', enum: ['P0', 'P1', 'P2', 'P3'] },
          file: { type: 'string' },
          line: { type: 'string' },
          problem: { type: 'string' },
          fix: { type: 'string', description: 'concrete, specific fix' },
          className: { type: 'string', description: 'the systemic pattern this is one instance of' },
          siblingLocations: { type: 'array', items: { type: 'string' }, description: 'every other file:line in the repo with the same class' },
          diffIntroduced: { type: 'boolean' },
          reachable: { type: 'boolean' },
        },
      },
    },
  },
}

const VERDICT_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['isReal', 'severity', 'reason'],
  properties: {
    isReal: { type: 'boolean' },
    severity: { type: 'string', enum: ['P0', 'P1', 'P2', 'P3'] },
    reason: { type: 'string' },
    refutedAs: { type: 'string', description: 'if not real: pre-existing | speculative | style | already-guarded | not-reachable', },
  },
}

const PLAN_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['summary', 'fixes', 'sweepsToRun', 'sensitive', 'residualRisks'],
  properties: {
    summary: { type: 'string' },
    fixes: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['severity', 'title', 'className', 'locations', 'problem', 'fix', 'origin'],
        properties: {
          severity: { type: 'string', enum: ['P0', 'P1', 'P2', 'P3'] },
          title: { type: 'string' },
          className: { type: 'string' },
          locations: { type: 'array', items: { type: 'string' }, description: 'EVERY location to change (whole class), not just the flagged one' },
          problem: { type: 'string' },
          fix: { type: 'string' },
          origin: { type: 'string', enum: ['codex', 'internal-review'] },
        },
      },
    },
    sweepsToRun: { type: 'array', items: { type: 'string' }, description: 'local gates/greps to run before pushing, e.g. "npm run check:org-scoping"' },
    sensitive: { type: 'boolean', description: 'RULE #7 carve-out. true ONLY if the FIX ITSELF changes: auth/access-control logic; server-side organization_id query scoping; DB/Firestore schema, a migration, or a backfill; pricing/billing/subscription math; a destructive or bulk data op; or a surface CUSTOMERS see (the Owner Page). It is NOT sensitive just because the code is in a data-heavy area: a client-side filter/sort/render over data that is ALREADY fetched and ALREADY org-scoped server-side is NOT sensitive, and an internal staff dashboard that merely DISPLAYS customer-related fields is NOT a customer-facing surface. When unsure between the two, set false but list it in residualRisks so the human confirms.' },
    residualRisks: { type: 'array', items: { type: 'string' } },
  },
}

// Reviewers mirror Codex's rubric (.github/codex/prompts/review.md) so one internal
// pass surfaces what Codex would across multiple rounds. Each gets the whole-class rule.
const DIMENSIONS = [
  {
    key: 'correctness',
    focus: `**Correctness.** Logic errors, unhandled edge cases, off-by-one, null/undefined, wrong async/await, broken control flow, incorrect error handling, response-shape mismatches. Walk each changed function's happy path AND failure paths.`,
  },
  {
    key: 'org-auth',
    focus: `**RULE #1 org isolation + the three auth patterns (HIGHEST priority — most-blocked class).** Every user-data read/write MUST filter by organization_id and be a SCOPED QUERY, never \`doc(id).get()\`+post-check (that's a P0). Audit all THREE auth patterns for any new/changed route: authenticateWithOrganization middleware, inline getUserId routes, zero-auth/requireAuth-only sub-routes — a fix to one with a sibling left open is a bypass. Check that a removed/renamed route didn't un-shadow an unauthenticated duplicate. Flag any missing org filter as P0.`,
  },
  {
    key: 'security-leak',
    focus: `**Security & data leakage.** Unvalidated input trusted; raw LLM-provider errors echoed to the client (the SDK 401 message embeds the API key — must funnel through classifyAIError); secrets in responses/logs; customer-facing surfaces (Owner Page) exposing internal fields like \`source\`/\`internalNotes\`; tainted format strings; missing rate-limit only where there's a real reachable abuse path.`,
  },
  {
    key: 'wiring-regressions',
    focus: `**Field wiring, data graveyards, mode/role variants & regressions.** New Issue/RO field present at ALL layers (type → mapFirestoreToIssue → updateIssue allowlist → convertIssueToAPI → Zod) or it silently no-ops (data graveyard / write-allowlist). snake_case on raw Firestore reads, camelCase only in API. Broken callers of a changed signature. A denorm gate field set on one write path but not its siblings. Shadowed/duplicate routes after a delete. **Mode & role variants (a recurring blind spot):** does the change behave correctly in BOTH single_player and multi_player, and across roles (admin/advisor/tech/parts)? A control shown in one mode/role but hidden in another can leave STALE state silently applied with no visible way to clear it (e.g. a status filter chosen in multi_player still narrowing the list in single_player where the dropdown is hidden), and MP-only surfaces/columns (RICH vs SIMPLE) differ from SP. Check every mode/role the changed surface renders in.`,
  },
  {
    key: 'ai-customer-surface',
    focus: `**AI output & customer-facing surfaces.** All AI-generated text funnels through removeMetaLanguage. AI must not fabricate diagnostic detail a tech didn't state (Strict/Standard/Enhanced modes). Pricing/billing math correct (null vs zero labor_hours → "Pricing to follow"; unpriced lines can't be approved). Destructive/bulk ops scoped and reversible. Mobile-first surfaces (iOS Safari) not broken for tech users.`,
  },
]

// --- run ---
phase('Map')
const map = await agent(
  `${groundingBlock}\n\nProduce a complete INVENTORY of this PR's diff: every changed file with the functions/classes/components it touches and a risk tag, plus — for EACH Codex finding above — the systemic CLASS it belongs to and every other place in the repo that class appears (grep the repo). This map grounds the reviewers; be exhaustive and accurate.`,
  { label: 'map-diff', phase: 'Map', schema: MAP_SCHEMA },
)

const mapDigest = `\n## Diff inventory (from the mapping pass)\n${JSON.stringify(map, null, 2)}\n`

phase('Review')
const reviewed = await pipeline(
  DIMENSIONS,
  (d) =>
    agent(
      `${groundingBlock}${mapDigest}${wholeClassRule}\n\n## Your lens\n${d.focus}\n\nReview the FULL diff through THIS lens only. For every defect: read the real code, confirm it's introduced by this diff and reachable, give a concrete fix, name its class, and list EVERY sibling location repo-wide. Return [] if your lens is clean — do not manufacture P2/P3 padding.`,
      { label: `review:${d.key}`, phase: 'Review', schema: FINDINGS_SCHEMA },
    ),
  (review, dim) =>
    parallel(
      ((review && review.findings) || []).map((f) => () =>
        agent(
          `${verifierBias}\n\n## Finding to refute (from the ${dim.key} lens, PR #${prNumber})\n${JSON.stringify(f, null, 2)}\n\nRead the cited code (\`${DIFF_CMD} -- ${f.file}\` and the file itself). Is this a real, reachable, diff-introduced defect? Set isReal accordingly; if not, say what kind of non-issue it is in refutedAs.`,
          { label: `verify:${f.file}`, phase: 'Verify', schema: VERDICT_SCHEMA },
        ).then((v) => ({ ...f, verdict: v })),
      ),
    ),
)

const confirmed = reviewed
  .flat()
  .filter(Boolean)
  .filter((f) => f.verdict && f.verdict.isReal)

log(`${confirmed.length} verified finding(s) after adversarial filtering`)

phase('Synthesize')
const plan = await agent(
  `${groundingBlock}\n\n## Verified findings (already adversarially confirmed real)\n${JSON.stringify(confirmed, null, 2)}\n\nProduce ONE ordered fix plan for PR #${prNumber}. Dedupe findings that are the same defect seen through different lenses (merge their sibling locations). For each fix, \`locations\` MUST list EVERY place to change (the whole class), not just the originally-flagged line. Order P0 → P1 → P2. List concrete local gates to run before pushing (always include "npm run check:org-scoping" if any org/auth fix; "npm run check" and the relevant "/test:safe"). Set \`sensitive: true\` if ANY fix touches auth/org-isolation, DB schema/migration, pricing/billing, destructive/bulk ops, or a customer-facing surface (RULE #7 carve-out). Note residual risks the fixes don't cover.`,
  { label: 'synthesize-plan', schema: PLAN_SCHEMA },
)

return { prNumber, plan, verifiedCount: confirmed.length, map }
