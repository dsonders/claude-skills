# shipped-prs

A Claude Code mod: a band above the prompt listing the PRs this session opened
(`gh pr create` in any Bash call), numbers only on a narrow window, one line with
the title on a wide one. Open PRs are re-read through `gh` every minute so merges
show up on their own.

The band shows from session start (an empty line until the first PR).

Commands: `/prs` toggles the band · `/prs add <n|url>` · `/prs refresh` · `/prs clear`

Lives in `~/.claude/skills/shipped-prs/`, which Claude Code auto-loads every session.

Install elsewhere:

```
/plugin install shipped-prs --marketplace dsonders/claude-skills
```
