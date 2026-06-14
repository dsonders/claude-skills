# Goal Template

Copy, fill, and pass to `/goal`. Every field should be objectively checkable — if you can't name the command or artifact that proves a line, it's not a finish line yet.

**You can leave fields blank** — `/goal` will interview you (one focused question at a time) to fill them. But it won't start the loop until the **Outcome** (end state) and **Verification surface** (completion evidence) are unambiguous — that's the clarity gate.

```
/goal <one-line objective>

Outcome (what must be true at the end):
- <verifiable end state>

Verification surface (the proof the checker reads — print this raw each turn):
- <test / command / artifact / count that proves the outcome>

Constraints (must NOT regress):
- <e.g. existing suite stays green; no public API changes>

Boundaries (in-scope only; everything else read-only):
- <files / dirs / tools allowed to change>

Iteration policy (how to pick the next action):
- <e.g. fix the single largest failing check first>

Blocked stop (when to halt and report, not loop):
- <e.g. if a required service is unreachable, log it and stop — do not guess>

Caps:
- turns: <default 30, hard max 50>
- tokens: <optional soft budget, e.g. 250K>
```

## One-line form

> "`<outcome>` verified by `<verification surface>` while preserving `<constraints>`. Work only within `<boundaries>`. Between iterations, `<iteration policy>`. If blocked or no valid path remains, `<blocked stop condition>`."

## Practitioner "prove it / show me" shorthand

If you prefer the lighter framing, these map onto the six components:

```
/goal <create or complete a specific artifact>

Finish line:        → Outcome + Constraints (verifiable conditions)
- <condition>
- <condition>

Prove it:           → Verification surface (evidence to print / test to run)
- <evidence>

Show me:            → the final handoff you want
- <recommendation / summary / artifact>

If blocked:         → Blocked stop condition
- <what to log, what to skip, when to stop>
```

Always append: **"Do not guess. Do not use placeholders. If blocked, report it."**
