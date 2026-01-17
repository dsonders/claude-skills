---
name: sync-skills
description: Manually sync skills to GitHub. Run before ending a web session.
---

Commit and push any skill changes to the central repository:

```bash
cd ~/.claude/skills
git add -A
if ! git diff --cached --quiet; then
  git commit -m "Manual sync: $(date +%Y-%m-%d\ %H:%M)"
  git push origin main
  echo "✅ Skills synced to GitHub"
else
  echo "ℹ️ No skill changes to sync"
fi
```
