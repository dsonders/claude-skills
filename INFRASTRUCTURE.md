# Skills Infrastructure: How It Works

**Last Updated:** February 15, 2026

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
| **Terminal** | Global `~/.claude/settings.json` SessionStart hook | Global Stop hook | PAT from `~/.claude/secrets/skills-pat` |
| **Mac Desktop App** | Same as terminal (shares `~/.claude/`) | Same as terminal | Same as terminal |
| **Web (per-repo)** | Per-project `.claude/settings.json` SessionStart hook | Per-project Stop hook (web-only) | `CLAUDE_SKILLS_PAT` env var, written to secrets file by `session-start.sh` |

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

### 2. `.claude/hooks/fetch-global-skills.sh`

```bash
#!/bin/bash
# Fetch global skills from dsonders/claude-skills on SessionStart

set -euo pipefail

SECRETS_FILE="$HOME/.claude/secrets/skills-pat"
if [ -n "${CLAUDE_SKILLS_PAT:-}" ]; then
  GITHUB_PAT="$CLAUDE_SKILLS_PAT"
elif [ -f "$SECRETS_FILE" ]; then
  GITHUB_PAT="$(tr -d '[:space:]' < "$SECRETS_FILE")"
else
  echo "Warning: No PAT found. Set CLAUDE_SKILLS_PAT or create $SECRETS_FILE" >&2
  exit 0
fi

SKILLS_REPO="https://${GITHUB_PAT}@github.com/dsonders/claude-skills.git"
SKILLS_DIR="$HOME/.claude/skills"

mkdir -p "$HOME/.claude"

if [ -d "$SKILLS_DIR/.git" ]; then
  cd "$SKILLS_DIR"
  git remote set-url origin "$SKILLS_REPO" 2>/dev/null || true
  if ! git pull --rebase origin main >/dev/null 2>&1; then
    cd "$HOME/.claude"
    rm -rf "$SKILLS_DIR"
    git clone --quiet "$SKILLS_REPO" "$SKILLS_DIR" 2>&1 || echo "Warning: Skills clone failed" >&2
  fi
elif [ -d "$SKILLS_DIR" ]; then
  rm -rf "$SKILLS_DIR"
  git clone --quiet "$SKILLS_REPO" "$SKILLS_DIR" 2>&1 || echo "Warning: Skills clone failed" >&2
else
  git clone --quiet "$SKILLS_REPO" "$SKILLS_DIR" 2>&1 || echo "Warning: Skills clone failed" >&2
fi
```

### 3. `.claude/hooks/push-global-skills.sh`

```bash
#!/bin/bash
# Push skill changes back on session end (web-only)

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

SKILLS_DIR="$HOME/.claude/skills"
[ -d "$SKILLS_DIR/.git" ] || exit 0

SECRETS_FILE="$HOME/.claude/secrets/skills-pat"
if [ -n "${CLAUDE_SKILLS_PAT:-}" ]; then
  GITHUB_PAT="$CLAUDE_SKILLS_PAT"
elif [ -f "$SECRETS_FILE" ]; then
  GITHUB_PAT="$(tr -d '[:space:]' < "$SECRETS_FILE")"
else
  exit 0
fi

cd "$SKILLS_DIR"
git remote set-url origin "https://${GITHUB_PAT}@github.com/dsonders/claude-skills.git" 2>/dev/null || true
git config user.email "claude-code-web@dsonders.dev" 2>/dev/null || true
git config user.name "Claude Code Web" 2>/dev/null || true

git add -A
git diff --cached --quiet && exit 0
git commit -m "Auto-sync from web: $(date +%Y-%m-%d\ %H:%M)" >/dev/null 2>&1
git push origin main >/dev/null 2>&1 || echo "Warning: Skills push failed" >&2
```

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

### 3. Always use HTTPS+PAT, never SSH
SSH keys aren't available in web containers. HTTPS+PAT works everywhere: terminal, Mac app, and web.

### 4. Always `git remote set-url` before pull/push
The clone URL includes the PAT. If the PAT was rotated, the stored remote URL has the old PAT. Setting the URL on every run ensures the current PAT is always used.

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
1. Check `~/.claude/secrets/skills-pat` exists and has content
2. Run `~/.claude/hooks/fetch-global-skills.sh` manually
3. Check `ls ~/.claude/skills/` for populated directories

**Skills stale (not updating):**
1. Check if `async: true` is in the fetch hook (remove it)
2. Run `cd ~/.claude/skills && git pull --rebase origin main` manually
3. Check if remote URL has expired PAT: `cd ~/.claude/skills && git remote -v`

**Push failing silently:**
1. Check PAT has write access to `dsonders/claude-skills`
2. Run push hook manually: `CLAUDE_CODE_REMOTE=true ~/.claude/hooks/push-global-skills.sh`
3. Check for merge conflicts: `cd ~/.claude/skills && git status`
