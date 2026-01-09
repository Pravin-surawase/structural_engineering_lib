# Fix Copilot Terminal Lockup - Manual Steps

## Problem
Copilot Agent's terminal is stuck in git pager mode. Commands open "alternate buffer" and nothing works.

---

## Step 1: Unblock Terminal (DO THIS NOW)

**In the terminal that's stuck, press:**
```
q
```

Just press the letter `q` on your keyboard. This quits the pager and unblocks the terminal.

If that doesn't work:
- Press `Ctrl+C` to force quit
- Or close the terminal tab and open a new one

---

## Step 2: Reload VSCode Window

After unblocking the terminal:

1. Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
2. Type: "Reload Window"
3. Select: "Developer: Reload Window"

This will reload VSCode with the new settings I just added to `.vscode/settings.json`.

---

## Step 3: Test in New Terminal

After reload, open a new terminal and test:

```bash
git status --short
```

Should work without opening pager!

---

## What I Fixed

I added environment variables to `.vscode/settings.json` that will:
- Set `GIT_PAGER=cat` for all VSCode terminals
- Set `PAGER=cat` for all commands
- Set `GIT_EDITOR=:` to prevent editor popups

These settings apply to:
- Your VSCode integrated terminals
- Copilot Agent's terminal sessions
- Any future terminal windows in this workspace

---

## For Copilot Agent

After reload, Copilot should be able to run git commands safely. But to be extra safe, tell Copilot to always use these formats:

**Safe:**
```bash
git status --short
git log --oneline -n 20
git diff --stat
git --no-pager [any-command]
```

**Unsafe (avoid):**
```bash
git status      # May page
git log         # Will page
git diff        # May page
```

---

## If It Still Doesn't Work

The VSCode settings should fix it, but if Copilot still has issues:

### Option 1: Use safe git commands only
Tell Copilot to prefix all git commands with `--no-pager`:
```bash
git --no-pager status
git --no-pager log
git --no-pager diff
```

### Option 2: Check global git config
Run in a normal terminal (not Copilot's):
```bash
git config --global core.pager
```

If it doesn't show `cat`, run:
```bash
git config --global core.pager cat
git config --global pager.status false
git config --global pager.branch false
git config --global pager.diff false
```

---

## Prevention

Going forward:
1. VSCode settings prevent pager in new terminals
2. Global git config prevents pager system-wide
3. Copilot should use safe command formats (see COPILOT-QUICK-START.md)

---

## Quick Reference

**Safe Commands:**
- `git status --short` ✅
- `git log --oneline -n 20` ✅
- `git diff --stat` ✅
- `git --no-pager [command]` ✅

**Dangerous Commands:**
- `git status` ❌
- `git log` ❌
- `git diff` ❌
- `git show` ❌

---

**Created:** 2026-01-10
**Issue:** Copilot terminal stuck in git pager
**Solution:** VSCode settings + manual terminal unblock
