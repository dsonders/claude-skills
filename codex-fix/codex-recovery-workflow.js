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
// The harness can deliver `args` as a JSON STRING rather than an object (seen
// live on #1195: reviewers ran without the Codex findings and the plan missed
// the actual flagged class). Parse defensively before reading any field.
let a = args
if (typeof a === 'string') {
  try { a = JSON.parse(a) } catch { a = null }
}
const prNumber = (a && a.prNumber) || 'current'
const baseRef = (a && a.baseRef) || 'origin/main'
const rawFindings = (a && a.codexFindings) || ''
const codexFindings = rawFindings.trim() || '(Codex comment text was not captured — review the full diff against the rubric from scratch.)'
if (!rawFindings.trim()) {
  // No-silent-caps: reviewers grade against the actual Codex finding; running without
  // it quietly weakens every downstream agent. Surface it so the invoker can re-run
  // with the comment text from Step 2 unless it is genuinely unavailable.
  log('⚠ codexFindings NOT provided — reviewers are running WITHOUT the actual Codex finding text (Step 2 gathers it; pass it via args.codexFindings)')
}
const changedFiles = (a && a.changedFiles) || []
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
You are an ADVERSARIAL verifier. Default to refuted=true unless you can prove the finding is a real, reachable, diff-INTRODUCED defect. Codex itself does NOT flag (and neither should we): pre-existing code the diff didn't touch; pure style/formatting/naming; speculative "an attacker could…/a future caller might…" with no concrete trigger in this diff; concerns the diff already guards against. Read the actual code at the cited location before deciding.

TOUCHED-FUNNEL EXCEPTION (do NOT refute as "pre-existing"): when the diff adds a gate/option/guard to a WRITE FUNNEL (a PATCH handler, an update/storage method, a mutation helper), Codex audits that ENTIRE funnel as new surface — every client-trusted field flowing through it is in scope even if the trusting code predates the diff. #905 (concernSeverity rode a pre-existing PATCH), #907 r2 (pre-existing parts[].customerApproved passthrough) and #907 r3 (pre-existing organization_id stamp through the newly-scoped write) were all real Codex BLOCKS on pre-existing lines of a touched funnel, each refuted as "pre-existing" by this verifier and each costing a paid round. If the finding names a request-derived value the touched funnel still trusts, it is admissible; judge it on reachability, not on diff-introduced.

SIBLING-GAP EXCEPTION (do NOT refute as "pre-existing pattern"): a NEW writer/reader the diff introduces that omits a field or step is a NEW instance of the gap, even when an off-diff sibling has the identical omission. "update-cause doesn't persist generated_by either" does not refute "this diff's new write path doesn't persist generated_by" — Codex blocked on exactly that after this verifier refuted it (#1355 r4; the missing provenance stamp bypassed the fallback review-carefully banner). The sibling's gap is out of scope; the diff's copy of it is not.`

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
        required: ['severity', 'confidence', 'file', 'line', 'evidence', 'problem', 'fix', 'className', 'siblingLocations', 'diffIntroduced', 'reachable'],
        properties: {
          severity: { type: 'string', enum: ['P0', 'P1', 'P2', 'P3'] },
          confidence: { type: 'string', enum: ['high', 'medium', 'low'], description: 'how sure you are this is a real defect (not how severe it is)' },
          file: { type: 'string' },
          line: { type: 'string' },
          evidence: { type: 'string', description: 'the EXACT line(s) of code from the diff that exhibit the defect, quoted verbatim — not a paraphrase. A finding with no verbatim quote is not admissible.' },
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
  required: ['isReal', 'severity', 'confidence', 'evidence', 'reason'],
  properties: {
    isReal: { type: 'boolean' },
    severity: { type: 'string', enum: ['P0', 'P1', 'P2', 'P3'] },
    confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
    evidence: { type: 'string', description: 'the EXACT code you read that CONFIRMS the defect (if isReal) or that REFUTES it (if not) — quoted verbatim from the file/diff. A verdict with no verbatim quote defaults to refuted.' },
    reason: { type: 'string' },
    refutedAs: { type: 'string', description: 'if not real: pre-existing | speculative | style | already-guarded | not-reachable | cited-code-not-in-diff', },
  },
}

const FIX_ITEM = {
  type: 'object',
  additionalProperties: false,
  required: ['severity', 'confidence', 'title', 'className', 'locations', 'problem', 'fix', 'regressionTest', 'origin'],
  properties: {
    severity: { type: 'string', enum: ['P0', 'P1', 'P2', 'P3'] },
    confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
    title: { type: 'string' },
    className: { type: 'string' },
    locations: { type: 'array', items: { type: 'string' }, description: 'EVERY location to change (whole class), not just the flagged one' },
    problem: { type: 'string' },
    fix: { type: 'string' },
    regressionTest: { type: 'string', description: 'a unit/API test that would FAIL before this fix and PASS after — the test to write first. "n/a — not unit-testable (UI/iOS feel)" if genuinely none applies; do NOT default to n/a to skip the test.' },
    fixLayer: { type: 'string', description: 'the layer this fix changes: client-render | client-state | server-route | server-query-scope | schema | type. Used to flag layer-escalation under gate pressure.' },
    origin: { type: 'string', enum: ['codex', 'internal-review'] },
  },
}

const PLAN_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['summary', 'fixes', 'advisory', 'sweepsToRun', 'sensitive', 'layerEscalations', 'residualRisks'],
  properties: {
    summary: { type: 'string' },
    // MUST-FIX before re-push: the Codex finding's whole class + any high-confidence P0/P1
    // that is diff-introduced. Gating the re-push on THIS list (not every nit) keeps the
    // fix focused and avoids the over-fix/churn that erodes trust and burns rounds.
    fixes: { type: 'array', items: FIX_ITEM, description: 'MUST fix before re-push: high-confidence P0/P1 that is diff-introduced — the Codex class + anything that would itself BLOCK. Nothing else belongs here.' },
    // ADVISORY: real but lower-severity/lower-confidence. Note them; fix only if cheap and
    // in-scope. Do NOT let these expand the diff or the layer of the change.
    advisory: { type: 'array', items: FIX_ITEM, description: 'P2/P3 or lower-confidence findings: worth noting, NOT required before re-push. Fix only if trivial and in the same layer.' },
    sweepsToRun: { type: 'array', items: { type: 'string' }, description: 'local gates/greps to run before pushing, e.g. "npm run check:org-scoping"' },
    sensitive: { type: 'boolean', description: 'RULE #7 carve-out. true ONLY if a MUST-FIX changes: auth/access-control logic; server-side organization_id query scoping; DB/Firestore schema, a migration, or a backfill; pricing/billing/subscription math; a destructive or bulk data op; or a surface CUSTOMERS see (the Owner Page). It is NOT sensitive just because the code is in a data-heavy area: a client-side filter/sort/render over data that is ALREADY fetched and ALREADY org-scoped server-side is NOT sensitive, and an internal staff dashboard that merely DISPLAYS customer-related fields is NOT a customer-facing surface. When unsure between the two, set false but list it in residualRisks so the human confirms.' },
    // A fix that resolves a finding by changing a HARDER/deeper layer than the bug lives at
    // (client gate → server query, soft guard → schema/type, local fix → migration) is a
    // DESIGN decision, not a reflex remediation. Surface it so the human decides — don't
    // silently over-encode under gate pressure.
    layerEscalations: { type: 'array', items: { type: 'string' }, description: 'any fix that resolves the bug at a harder/deeper layer than where it occurs (client→server, soft-guard→schema/type) — flag for human sign-off, do not auto-apply' },
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
    focus: `**RULE #1 org isolation + the three auth patterns (HIGHEST priority — most-blocked class).** Every user-data read/write MUST filter by organization_id and be a SCOPED QUERY, never \`doc(id).get()\`+post-check (that's a P0). Audit all THREE auth patterns for any new/changed route: authenticateWithOrganization middleware, inline getUserId routes, zero-auth/requireAuth-only sub-routes — a fix to one with a sibling left open is a bypass. Check that a removed/renamed route didn't un-shadow an unauthenticated duplicate. Flag any missing org filter as P0. When the diff adds a FIELD riding a PRE-EXISTING write funnel (a new key through PATCH → storage.updateIssue/updateRepairOrder), audit the funnel's OWN lookup scoping too — Codex treats the funnel as new attack surface for the new field, so a default unscoped by-id write lookup (e.g. updateIssue without \`scopeWritesToOrg: true\`) is a P0 even though the call site predates the diff (#905 r2). WRITE-TIME PROOF (#1718 r2, a class this workflow itself missed): a pre-existing select-then-write (\`.get()\` then \`docRef.delete()\`/\`.update()\`) that the diff RECOMBINES into a new cascade, batch or multi-doc write is diff-introduced — every ref the write acts on must come from a \`txn.get(query)\` carrying the org predicate INSIDE the writing transaction (\`db.batch()\` locks nothing), and once the write is in a txn every route-level gate it relied on (closed-RO lock, frozen line, access) must be re-judged from the txn's own reads (#1553). Never prescribe a batch over pre-txn refs as the fix.`,
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
  {
    key: 'failure-paths',
    focus: `**Failure-path state machines (blind spot that cost #1222 r3 — reviews audit happy paths and races, nobody walks the failure exits).** For EVERY user action the diff adds/changes, walk EVERY failure exit (empty result, thrown persistence, rejected network write, dead handle) and check: (a) ALL interaction state re-arms — locks/refs cleared, busy flags reset, stale handles nulled — so the user can retry (a button stuck on its in-progress label over a dead resource is the tell); (b) NO advance/navigation/success render happens before the persistence it claims has settled — an optimistic advance on a failed write is a FALSE SUCCESS (the #1046 class: UI claims a server fact its write never landed), and any optimistic cache write must roll back on failure; (c) a timer/timeout that arms an in-progress state has a settle path from EVERY intermediate state, not just the expected one.`,
  },
  {
    key: 'population-render-matrix',
    focus: `**Population-admission render matrix + documented "accepted holes" (cost #1324 r2 AND r3 — two paid rounds).** (a) When the diff WIDENS a membership/filter predicate (a new field cleared a gate, a filter dropped a conjunct), a NEW POPULATION reaches every surface downstream of it. The membership/state/$ consumers get audited; the RENDER consumers don't. For the newly-admitted population, walk every surface that TITLES or DESCRIBES the entity (cards, chips, rows, hovers, dialogs, notifications) and ask: what does THIS population actually render there? A field promoted into an identity/membership predicate must also be threaded into the render chain (title/body fallbacks), through ONE shared derivation — and two render chains fed by the SAME field must dedupe against each other (#1324 r3: title AND body both fell back to the complaint → the sentence printed twice). (b) Any comment in the diff that documents a KNOWN hole as "accepted"/"left open deliberately"/"not worth a guard" is an invitation for the gate to block on exactly that line — if closing it costs a trim()/one-line guard, CLOSE IT and delete the essay; only leave a hole open when closing it is a genuine layer escalation, and then say WHERE the real fix lives.`,
  },
  {
    key: 'stale-echo-monotonic',
    focus: `**Stale-echo reversion of server-side progress (cost #1222 r1+r4).** Any client write that sends a WHOLE object/array rebuilt from its own cache can echo STALE values over fields the server (or another device) progressed AFTER that cache was taken — background-job outputs, another tab's flags, async stamps. For each client-editable field in a bulk write path ask: does anything server-side or cross-device advance this field, and does it only ever move ONE WAY (empty→filled, false→true)? One-way fields must LATCH at the server merge seam (client input can complete them, never revert them); also check whether any GATE/freeze/derivation reads the field — a stale echo that reverts it can dissolve the gate (an all-false echo un-froze #1222 r2's order lock until r4 latched it). And enforce structural freezes at the WRITE SITE on EVERY writer (PATCH and siblings like appends — an append that looks structurally safe still changes a completion DENOMINATOR any every-item predicate reads, #1222 r6).`,
  },
  {
    key: 'unattended-write-contract',
    focus: `**Unattended/background write contract (cost #1355 SIX rounds — Codex surfaced one clause per round; enumerate ALL of them in one pass).** Any write the diff makes WITHOUT a user watching (a fire-and-forget job, a post-response continuation, a deferred callback racing a live editing surface) must satisfy EVERY clause: (1) every precondition — tenancy, parentage, target-state — decided INSIDE the writing transaction on the txn read, never on a read taken before a long await; (2) the guard inspects EVERY field the write set touches, including fields helpers append in place (auto-translate's spanish_/french_* + one-way *_modified flags — a State-4 org's human text never lands in the English field); (3) if the write bypasses a storage funnel, list the funnel's post-write effects (denorms, mirrors, recorders) and re-attach each — and any follow-up that echoes a CAPTURED value (an Issue#1→RO mirror) goes INSIDE the txn, never post-commit; (4) INPUT freshness: the txn recomputes what fed the generation (transcript/complaint/rubric selector) and skips on mismatch — a cause derived from superseded notes must not commit; (5) provenance stamps persist (generated_by; check multi-pass pipelines don't rebuild the result object and drop it); (6) paid-call BUDGET: each background call consumes the SAME per-user store the interactive routes use — verify "shared" by grepping for rival stores/file-local limiters, not by reading comments — and no request-level limiter may sit on a route whose core (non-AI) function must survive budget exhaustion; (7) every skip/failure/crash exit clears any client-facing in-progress flag the work armed, with a client-side age bound as the deploy-restart backstop.`,
  },
]

// --- run ---
phase('Map')
const map = await agent(
  `${groundingBlock}\n\nProduce a complete INVENTORY of this PR's diff: every changed file with the functions/classes/components it touches and a risk tag, plus — for EACH Codex finding above — the systemic CLASS it belongs to and every other place in the repo that class appears (grep the repo). This map grounds the reviewers; be exhaustive and accurate.`,
  // model pinned to opus: this fan-out inherits the session model by default, and a
  // Fable-managed session burned ~2.5M Fable tokens on one recovery run (2026-07-23).
  // Grep-and-verify review work is Opus-grade; the human session does final judgment.
  { label: 'map-diff', phase: 'Map', schema: MAP_SCHEMA, model: 'opus' },
)

const mapDigest = `\n## Diff inventory (from the mapping pass)\n${JSON.stringify(map, null, 2)}\n`

phase('Review')
const reviewed = await pipeline(
  DIMENSIONS,
  (d) =>
    agent(
      `${groundingBlock}${mapDigest}${wholeClassRule}\n\n## Your lens\n${d.focus}\n\nReview the FULL diff through THIS lens only. For every defect you MUST: read the real code; QUOTE the exact offending line(s) verbatim into \`evidence\` (a finding with no verbatim quote from the actual diff is inadmissible — do not invent line numbers); confirm it is introduced by this diff (\`diffIntroduced\`) and reachable (\`reachable\`); give a concrete fix; name its class; list EVERY sibling location repo-wide; and rate your \`confidence\` (high only if you quoted code that unambiguously exhibits the defect). Return [] if your lens is clean — manufacturing P2/P3 padding lowers the signal and trains the maintainer to ignore you.`,
      { label: `review:${d.key}`, phase: 'Review', schema: FINDINGS_SCHEMA, model: 'opus' },
    ),
  (review, dim) =>
    parallel(
      ((review && review.findings) || []).map((f) => () =>
        agent(
          `${verifierBias}\n\n## Finding to refute (from the ${dim.key} lens, PR #${prNumber})\n${JSON.stringify(f, null, 2)}\n\nIndependently re-derive this — do NOT trust the finding's own quote. Open the cited code yourself (\`${DIFF_CMD} -- ${f.file}\` and the file itself) and PASTE the exact line(s) you read into \`evidence\`. Then decide: is this a real, reachable, diff-INTRODUCED defect? If the cited code isn't actually in this diff, refute it as cited-code-not-in-diff. Free-form agreement without a verbatim quote = refuted by default. Set isReal + confidence accordingly; if not real, name the non-issue kind in refutedAs.`,
          { label: `verify:${f.file}`, phase: 'Verify', schema: VERDICT_SCHEMA, model: 'opus' },
        ).then((v) => ({ ...f, verdict: v })),
      ),
    ),
)

const verifiedReal = reviewed
  .flat()
  .filter(Boolean)
  .filter((f) => f.verdict && f.verdict.isReal)

// Mechanical citation gate (deterministic, no model): a finding whose cited file is not in
// the PR's changed-file set is either pre-existing (out of scope per Codex's own rubric) or
// hallucinated — either way it must NOT gate the re-push. Partition rather than drop, so the
// synthesizer can still note a genuine off-diff observation as advisory. Skip the gate only
// if we weren't given a changed-file list (can't verify → don't silently discard).
const norm = (p) => String(p || '').replace(/^\.?\/*/, '').trim()
const changedSet = changedFiles.map(norm)
const inDiff = (file) => {
  if (!changedSet.length) return true // no list provided → can't gate, treat as in-diff
  const f = norm(file)
  return changedSet.some((cf) => cf === f || cf.endsWith('/' + f) || f.endsWith('/' + cf))
}
const confirmed = verifiedReal.filter((f) => inDiff(f.file))
const offDiff = verifiedReal.filter((f) => !inDiff(f.file))

log(
  `${confirmed.length} verified in-diff finding(s) after adversarial + citation gating` +
    (offDiff.length ? ` (${offDiff.length} dropped to advisory: cited file not in the diff)` : ''),
)

phase('Synthesize')
const plan = await agent(
  `${groundingBlock}\n\n## Verified IN-DIFF findings (adversarially confirmed real, cited code is in this diff)\n${JSON.stringify(confirmed, null, 2)}\n\n## Off-diff observations (verified real but cited code is NOT in this diff — advisory at most, never a must-fix)\n${JSON.stringify(offDiff, null, 2)}\n\nProduce ONE fix plan for PR #${prNumber}, graded against the actual Codex finding above as the reference (does each fix resolve the cited P0/P1 and its whole class?).\n\nSplit findings into two buckets:\n- \`fixes\` = MUST fix before re-push: high-confidence, diff-introduced P0/P1 — the Codex class plus anything that would itself BLOCK. Dedupe defects seen through multiple lenses (merge their sibling locations). \`locations\` MUST list EVERY place to change (the whole class). Each needs a \`regressionTest\` (a test that fails before, passes after) unless genuinely not unit-testable.\n- \`advisory\` = real but P2/P3 or lower-confidence (incl. all off-diff observations): note them; do NOT require them before re-push and do NOT let them expand the diff.\n\nFor \`sweepsToRun\`: always include "npm run check" and the relevant "/test:safe"; add "npm run check:org-scoping" if any fix touches org/auth.\n\nSet \`sensitive\` per its definition (only a MUST-FIX in the carve-out categories). Populate \`layerEscalations\` with any fix that would resolve the bug at a HARDER/deeper layer than where it occurs (a client-side bug fixed by changing a server query or the schema, a soft guard turned into a type/DB constraint) — those are design calls for the human, not reflex remediations. Note residual risks the fixes don't cover.`,
  { label: 'synthesize-plan', schema: PLAN_SCHEMA, effort: 'high', model: 'opus' },
)

return { prNumber, plan, verifiedCount: confirmed.length, offDiffCount: offDiff.length, map }
