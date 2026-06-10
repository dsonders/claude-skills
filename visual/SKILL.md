---
name: visual
description: Re-render Claude's previous message in a more visual, scannable form — tables, grouped bullets, hierarchy, whitespace, and consistent status markers — keeping all the content but cutting the mental effort to digest it. Use when the last message was a dense wall of text, a long list, or a comparison that's hard to scan, and the user wants the same information laid out so it's easy to take in at a glance. Primarily invoked via /visual; do not auto-run it unless the user asks.
allowed-tools: Read, Grep, Glob
---

# /visual — Re-render the last message so it's easy to scan

Take Claude's previous message and present the **same content** in a far more visual, low-effort-to-read layout. This is a **presentation transform, not a summary** — don't drop information, don't add new analysis. The reader should be able to *scan* it in seconds instead of grinding through paragraphs.

## When to use

- The last message was a dense wall of text, a long list, or a multi-option comparison that's tiring to read.
- Any time the user types `/visual`.
- The user says something like "make this more visual" or "this takes too much mental effort to digest."

## Don't use for

- Cutting a long report down to *just decisions and actions* → use `/tldr` (that one deliberately drops detail; this one keeps it).
- Doing or continuing the actual work → that's a normal turn.

## Who you're writing for

Dave — solo founder and product leader, **not an engineer**. He should be able to glance at the message and immediately see the structure: what the items are, how they compare, what's most important. Optimize for *scanning*, not reading.

## Pick the layout that fits the content

| If the last message is… | Re-render it as… |
|---|---|
| A comparison of options/tools/approaches | A **table** — one row per option, columns for the attributes that matter |
| A list of items with attributes | A **table** or **grouped bullets** with a bold label per item |
| A sequence of steps or a process | A **numbered list**, one action per line |
| Pros and cons / trade-offs | **Two short columns** or a ✅ / ⚠️ split |
| Status of many things | A **checklist** with consistent markers (✅ done · ⚠️ caveat · ❌ blocked · → next) |
| One long argument or explanation | **Headers + short bullets**, leading with the punchline of each part |

## Visual techniques (apply liberally)

- **One idea per line.** Break dense, multi-clause sentences into separate bullets.
- **Bold the key term at the start of each bullet** so the left edge is scannable.
- **Group under clear headers**, with whitespace between groups.
- **Use status markers as anchors, not decoration** — pick a small consistent set (✅ ⚠️ ❌ → 🔑) and use them the same way throughout.
- **Tables for anything comparable.** If two or more items share attributes, a table beats prose every time.
- **Numbers and options as lists**, never buried in a paragraph.
- **Lead with the conclusion** of each section, then support it.
- Keep commands, URLs, and identifiers in `code font`.
- **Avoid:** walls of text, lists hidden inside paragraphs, inconsistent or purely decorative emoji.

## Rules

- **Keep all the information.** This is reformatting — if something was in the original message, it should still be findable here. (Want it trimmed to essentials instead? That's `/tldr`.)
- **Don't add** new content, opinions, or analysis that wasn't already there.
- **Don't take any actions.** Tools are read-only; this only re-presents text already in the conversation.
- If the user passed a target with `/visual` (e.g. `/visual the options above`), apply this to that target specifically.

## Done when

The reader can absorb the same content in a fraction of the time — clear structure, scannable left edge, no wall of text — with nothing from the original dropped.
