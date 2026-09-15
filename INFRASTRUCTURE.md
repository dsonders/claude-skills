# Skills Infrastructure: How It Works

**Last Updated:** September 15, 2026

This document explains how skills are fetched, synced, and made available across all Claude Code environments.

---

## Architecture Overview

```
                    dsonders/claude-skills (GitHub)
                         ↑              ↓
                     push on         pull on
                     session end     session start
                         ↑              ↓
                    ~/.claude/skills/ (local clone)
                         ↑
              Skills loaded into Claude Code session
```

Skills live in a single GitHub repo (`dsonders/claude-skills`) and are cloned into `~/.claude/skills/` on every session start. Edits made during a session are pushed back on session end.

---

## Environment Matrix

| Environment | Fetch trigger | Push trigger | Auth method |
|---|---|---|---|
| **Terminal** | Global `~/.claude/settings.json` SessionStart hook | Global Stop hook | SSH key registered with GitHub (no token, no secret file) |
| **Mac Desktop App** | Same as terminal (shares `~/.claude/`) | Same as terminal | Same as terminal |
| **Web (per-repo)** | Per-project `.claude/settings.json` SessionStart hook | Per-project Stop hook (web-only) | `CLAUDE_SKILLS_PAT` env var, written to the secrets file by `session-start.sh`, handed to git through a credential helper. The remote URL never contains it. |

---

## File Locations

### Global (on your Mac, `~/.claude/`)

```
~/.claude/
├── settings.json           # SessionStart + Stop hooks for terminal/Mac app
├── settings.local.json     # Permissions, additionalDirectories
├── secrets/
│   └── skills-pat          # GitHub PAT (chmod 600)
├── hooks/
│   ├── fetch-global-skills.sh   # Pulls skills repo
│   └── push-global-skills.sh    # Pushes skill changes
└── skills/                 # Clone of dsonders/claude-skills
    ├── app-testing/
    ├── compound/
    ├── ...
    └── INFRASTRUCTURE.md   # This file
```

### Per-Project (committed to each repo)

```
repo/
└── .claude/
    ├── settings.json       # Wires up hooks for web sessions
    └── hooks/
        ├── session-start.sh         # Web-only: writes PAT, installs deps
        ├── fetch-global-skills.sh   # Fetches skills (both environments)
        └── push-global-skills.sh    # Web-only: pushes skill changes
```

---

## Adding Skills Support to a New Repo

To make a new repo work with skills on the web, add these four files:

### 1. `.claude/hooks/session-start.sh`

```bash
#!/bin/bash
set -euo pipefail

# Only run in Claude Code on the web
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Set up PAT for fetch-global-skills hook
SECRETS_FILE="$HOME/.claude/secrets/skills-pat"
if [ ! -f "$SECRETS_FILE" ] && [ -n "${CLAUDE_SKILLS_PAT:-}" ]; then
  mkdir -p "$(dirname "$SECRETS_FILE")"
  echo "$CLAUDE_SKILLS_PAT" > "$SECRETS_FILE"
  chmod 600 "$SECRETS_FILE"
fi

# Install project dependencies (adjust for your package manager)
cd "$CLAUDE_PROJECT_DIR"
npm install
```

### 2. `.claude/hooks/fetch-global-skills.sh` and 3. `.claude/hooks/push-global-skills.sh`

Copy them byte-for-byte from `ro-bot/app/.claude/hooks/` (the `website/` copies are identical). Both are web-only (`CLAUDE_CODE_REMOTE` guard), keep the remote at the plain `https://github.com/dsonders/claude-skills.git`, and authenticate with:

```bash
CRED_HELPER='!f() { printf "username=x-access-token\npassword=%s\n" "$GIT_SKILLS_PAT"; }; f'
git_auth() { git -c credential.helper= -c "credential.helper=$CRED_HELPER" "$@"; }
```

git asks the helper for credentials and the helper answers from the exported env var, so the token is never in the URL, `.git/config`, the command line, or `ps`. A pull failure warns and keeps the local clone; it never deletes one.

### 4. `.claude/settings.json`

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Skill"]
  },
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh"
          }
        ]
      },
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/fetch-global-skills.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/push-global-skills.sh"
          }
        ]
      }
    ]
  }
}
```

Make all hooks executable: `chmod +x .claude/hooks/*.sh`

**Important:** `session-start.sh` must run BEFORE `fetch-global-skills.sh` in the SessionStart array, because it writes the PAT that fetch reads.

---

## Hard-Won Rules

These rules come from debugging real failures:

### 1. Never hardcode PATs in hook scripts
PATs committed to repos get rotated, diverge across branches, and are a security risk. Always read from `~/.claude/secrets/skills-pat` or `CLAUDE_SKILLS_PAT` env var.

### 2. Never use `async: true` in fetch hooks
Async hooks run in the background. Skills won't be loaded when the session starts, causing "skill not found" errors. Always run fetch synchronously.

### 3. The token never goes in the remote URL
An `https://PAT@github.com/...` remote leaks the token to `git remote -v`, to `.git/config`, and to every later session that opens the clone. That is how the PAT was exposed on 2026-07-02, and the per-project web hooks kept re-embedding it until 2026-09-15. Terminal and Mac app use SSH; web (no SSH key in the container) feeds the token to git through a credential helper. Both keep the URL clean.

### 4. Always `git remote set-url` before pull/push
Each environment's hook sets the URL it needs (SSH on terminal, plain https on web) on every run, so a clone left in the other state by a different environment is corrected before use.

### 5. Per-project push hooks must guard with `CLAUDE_CODE_REMOTE`
Terminal sessions use the global push hook from `~/.claude/hooks/`. If the per-project push hook also runs, you get duplicate commits. Guard with `if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then exit 0; fi`.

### 6. `settings.json` has strict validation
Claude Code validates settings files against a JSON schema. Malformed edits (trailing commas, missing brackets) will be rejected. Test edits carefully.

### 7. `settings.json` vs `settings.local.json`
Both are loaded. Use `settings.json` for hooks (they need to be consistent). Use `settings.local.json` for permissions and local-only config (not synced). If both define the same hook event, hooks from both files run.

### 8. Commit infrastructure changes to main
Hook and settings changes on feature branches won't be available in other branches or web sessions until merged. Always commit these directly to main.

---

## Repos with Skills Support

| Repo | Status | Notes |
|---|---|---|
| `dsonders/RO-bot-landing-page` | Active | Astro marketing site |
| `dsonders/RObot_032025` | Active | Main RO-bot app |
| `dsonders/claude-skills` | N/A | This is the skills repo itself |

---

## Troubleshooting

**Skills not loading in a session:**
1. Terminal: `ssh -T git@github.com` authenticates. Web: `~/.claude/secrets/skills-pat` exists and has content
2. Run `~/.claude/hooks/fetch-global-skills.sh` manually
3. Check `ls ~/.claude/skills/` for populated directories

**Skills stale (not updating):**
1. Check if `async: true` is in the fetch hook (remove it)
2. Run `cd ~/.claude/skills && git pull --rebase origin main` manually
3. `cd ~/.claude/skills && git remote -v` must show `git@github.com:` (terminal) or a plain `https://github.com/` URL (web). A token in the URL means an old hook ran; fix the hook, then `git remote set-url origin git@github.com:dsonders/claude-skills.git`

**Push failing silently:**
1. Check PAT has write access to `dsonders/claude-skills`
2. Run push hook manually: `CLAUDE_CODE_REMOTE=true ~/.claude/hooks/push-global-skills.sh`
3. Check for merge conflicts: `cd ~/.claude/skills && git status`
