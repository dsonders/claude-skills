---
name: tldr
description: Distill Claude's most recent work report into a CEO-facing executive brief — a one-line TL;DR, the decisions and actions that need the user, what happened in plain language, and risks to watch. Use after a long, technical Claude Code run when the user (a product leader, not an engineer) wants to cut through the wall of text and see only what matters to them and what they must decide or do. Primarily invoked explicitly via /tldr; do not auto-run it unless the user asks.
allowed-tools: Read, Grep, Glob
---

# /tldr — Executive brief of Claude's last report

Re-read the work Claude just reported and rewrite it as a short executive brief for a product leader. This skill **summarizes; it never does new work.** No edits, no commits, no commands, no re-running anything — it only reads what's already in the conversation and reformats it.

## When to use

- Right after a long or heavily technical Claude Code response, when the user wants the signal without scanning the whole wall of text.
- Any time the user types `/tldr`.
- When a run ended and it's unclear whether anything is needed from the user.

## Don't use for

- Capturing learnings to files → use `/compound`.
- Doing or continuing the actual work → that's a normal turn, not this skill.
- Summarizing an external document the user pastes in (this is about *Claude's own last report*) — though if the user passes a target as an argument, focus the brief on that instead.

## Who you're writing for

The user is **Dave — solo founder, product leader, and CEO. He is not an engineer**; engineering is what he relies on Claude for. Write the brief the way you'd brief a busy CEO:

- **Lead with what needs him.** Decisions and actions go near the top and must be impossible to miss.
- **Translate engineer-speak into outcomes.** Say what changed for the product/business, not how it was implemented.
- **Cut the play-by-play.** He does not care about test names, function names, line numbers, or which files moved — unless that's the exact thing he must act on.
- **But never hide a required action just because it's technical.** If he must run a command or approve something, surface it verbatim, in `code font`, even if it looks like engineering.
- **Make it visual.** He should be able to *scan* the brief, not read it. Favor short labeled bullets, headers, whitespace, and the status markers below over prose paragraphs. (For a pure presentation re-render that keeps all the content, that's the sibling `/visual` skill.)

## What to summarize (scope)

- The work Claude reported **since the user's last instruction** — usually the most recent response, but cover the whole span if multiple responses happened.
- The **substance of the user-facing message(s)** — not Claude's internal reasoning, and not the tool-by-tool narration.
- If the user passed an argument with `/tldr` (e.g. `/tldr the deploy output`), focus the brief on that instead of the default last-report scope.

## Output format — use this exactly

```
## 🎯 TL;DR
<1–2 sentences: what just happened, and whether anything is needed from you.>

## ⚠️ Needs you
DECISION — <a choice only you can make: an open question, a fork, or an assumption I made that you should confirm or override.>
ACTION   — <something you must do that I can't or didn't: run a command, log in, approve/merge, deploy, review a PR, answer a question.>

## ✅ What happened
- <plain-language outcome>
- <plain-language outcome>

## ⚠️ Watch for
- <a real risk, caveat, or something left unverified>

_Ask me to expand any line._
```

### Section rules

- **🎯 TL;DR** — Always present. One or two sentences. If the user is blocked or you're mid-task, say so here.
- **⚠️ Needs you** — The most important section. **Always include it, even when empty.** If there is genuinely nothing to decide or do, replace its contents with exactly: `✅ Nothing needed from you — this is informational.` Never silently drop the section; an absent section reads as "did Claude forget?"
  - `DECISION` = only the user can choose. Include assumptions you made that he might want to reverse.
  - `ACTION` = a concrete thing he must do. Keep commands, URLs, PR numbers, filenames, and credentials **verbatim in `code font`** so they're copy-paste ready.
  - Order: decisions before actions; most consequential first.
- **✅ What happened** — 3–6 outcome bullets in plain language. Omit the section only if literally nothing was accomplished (then say so in the TL;DR).
- **⚠️ Watch for** — Only real risks/caveats/unverified things. **Omit the whole section if there are none** — a manufactured risk is just noise. (This is the opposite of "Needs you," which always stays.)
- **Footer** — Always end with `_Ask me to expand any line._` so he knows the detail is one question away.

Aim for **one screen.** If the run was huge, summarize at the altitude of outcomes, not steps.

## Translation guide (engineer-speak → product-speak)

| Claude reported | Brief should say |
|---|---|
| "Refactored auth middleware to use JWT" | "Made sign-ins more secure (no user-visible change)" |
| "Fixed a race condition in the Firestore listener" | "Fixed a bug that could show people stale data" |
| "Bumped the dependency, resolved peer conflicts" | "Updated a library — no product impact" |
| "Added 12 Jest tests, all green" | "Added safety checks so this doesn't break again" |
| "Deploy is blocked on missing env var" | ACTION — "Add the missing setting before this can go live" (keep the var name in `code font`) |

Keep verbatim, never translate away: exact commands, URLs, PR/issue numbers, prices/money, file or page the user must review, and anything customer-facing.

## Edge cases

- **Last response was already short** → give just the TL;DR and Needs-you, and note it was already brief.
- **You asked the user a question** (via AskUserQuestion or in text) → that's a `DECISION`; surface it verbatim at the top.
- **You're mid-task or blocked** → say so in the TL;DR and put the blocker under Needs you.
- **Nothing happened and nothing's needed** → say that plainly in one line; don't pad.

## What NOT to do

- **Don't take any new actions.** Tools are read-only on purpose. If something needs doing, list it as an `ACTION` for the user — don't do it yourself.
- **Don't invent** decisions or actions to fill the section. Empty is fine; say so.
- **Don't drop a real required action** because it's technical or you could "handle it later."
- **Don't summarize your reasoning** — summarize the result.
- **Don't auto-run this skill.** It's on-demand; only produce a brief when the user asks (typically by typing `/tldr`).

## Done when

- The brief fits ~one screen and leads with anything that needs the user.
- Every decision and action the user must take is present and unmissable (or the section explicitly says nothing is needed).
- Jargon is translated, but must-act specifics are preserved verbatim.
