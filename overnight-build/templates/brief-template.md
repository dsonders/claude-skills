# Overnight build brief — <DATE> (Dave-approved; all rulings locked)

Manager: this session. <N> build agents (Opus), each in its own worktree per RULE #4
(claim `.claude/worktrees/build-N` atomically via `mkdir .../.claim`, or mint fresh with
`git worktree add`; EnterWorktree/cd FIRST, branch INSIDE off origin/main; verify parked +
`git fetch && git reset --hard origin/main`; release with `.claim` removed LAST).
Repo: /Users/davidsonders/ro-bot/app.

RULES FOR ALL AGENTS
- Gates before every push: tsc (fresh tsbuildinfo if suspicious), targeted jest (worktree
  needs the testPathIgnorePatterns override — verify tests RAN), `npm run check:org-scoping`,
  `npm run check:status-literals`.
- Probe every new/updated source-content guard ONE AT A TIME (break → red → revert; assert
  the mutation applied before reading the verdict).
- Watch checks after every push (`gh pr checks --watch`). Codex block → fix the WHOLE CLASS,
  ONE re-push; second block → stop and report to the manager.
- MERGE POLICY (overnight-build): arm `gh pr merge --auto --squash` on every PR that
  implements only the rulings below — sensitive categories included. EXCEPTIONS: a PR
  carrying an un-ruled decision parks (no auto-merge, question in the PR body); never
  EXECUTE backfills/migrations/bulk-data scripts or touch billing overnight (merging the
  code is fine). Auth/login or org-isolation diffs ONLY: run the pre-push-mirror skill
  BEFORE the first push (every other domain ships on the Codex gate alone).
- PR SIZE CAP: ~800 non-test changed lines per PR. `git diff --stat origin/main` before the
  first push; over the cap = split into the stacked PRs named in your workstream section
  (or ask the manager for the seam). Blockers scale with lines — a 2,000-line PR is 4–5 rounds
  by construction.
- Commits end with: Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
- PR bodies: plain language for a non-engineer owner first (role × status-label before/after
  tables for permission changes), technical detail after, screenshots for visual changes,
  end with the 🤖 Generated with [Claude Code](https://claude.com/claude-code) footer.
- Park, don't guess: any ambiguity → PR body + final report. No new decisions — every ruling
  below is Dave's.
- Report at the end: PR numbers/URLs, merge state, gates, probe table, prod-verify sentinel
  (a string from YOUR diff that lands in the CLIENT bundle — never a server-only literal),
  parked items.

## Workstream A — <name> (<N> PRs, <auto-merge | park-for-decision>)
<Rulings, VERBATIM, each marked ⛔. Files + lesson docs to read FIRST. Root-cause findings
already established (don't re-derive). Sensitivity notes. Out-of-scope lines.>

## Workstream B — ...

## Morning ledger (manager)
Merged (one user-visible line + revert command each) / parked with question / hard-floor
items awaiting execution / Codex rounds spent / prod-verify checklist / kanban + memory updates.
