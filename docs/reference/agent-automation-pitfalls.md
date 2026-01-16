# Agent Automation Pitfalls and Best Practices
<!-- lint-ignore-git -->

**Type:** Reference
**Audience:** All Agents
**Status:** Production Ready
**Importance:** High
**Created:** 2026-01-10
**Last Updated:** 2026-01-13

---

**Purpose:** Common pitfalls when building automated agents and LLM-based workflows

> ⚠️ **Note:** This document includes manual git examples only to illustrate pitfalls.
> Use automation in this repo: `./scripts/ai_commit.sh` and `./scripts/recover_git_state.sh`.

## Table of Contents

1. [Terminal and Shell Issues](#terminal-and-shell-issues)
2. [Git Operations](#git-operations)
3. [Interactive Commands](#interactive-commands)
4. [File System Operations](#file-system-operations)
5. [Process Management](#process-management)
6. [Best Practices Summary](#best-practices-summary)

---

## Terminal and Shell Issues

### Pitfall 1: Git Pager Lockup (CRITICAL)

**Problem:** Git commands trigger pager (`less`), terminal enters alternate buffer mode, agent cannot send keystrokes to quit.

**Symptoms:**
```
> git status
The command opened the alternate buffer.

> git merge --abort
The command opened the alternate buffer.

[All subsequent commands blocked]
```

**Root Cause:** Git's pager (`less`) waits for keyboard input (`q` to quit). Agents cannot send keyboard events.

**Solution:**

```bash
# Option 1: Disable pager globally (RECOMMENDED)
git config --global core.pager cat
git config --global pager.status false
git config --global pager.branch false
git config --global pager.diff false

# Option 2: Use --no-pager flag
git --no-pager status
git --no-pager log
git --no-pager diff

# Option 3: Use short-format commands
git status --short
git status --porcelain
git log --oneline -n 20
git diff --name-only
```

**Prevention Checklist:**
- [ ] Set `GIT_PAGER=cat` in environment
- [ ] Disable pager in git config (global or per-repo)
- [ ] Always use `--short`, `--oneline`, or `--no-pager` flags
- [ ] Test all git commands before deploying agent

**High-Risk Commands:**
- `git log` (almost always pages)
- `git diff` (pages on file changes)
- `git show` (always pages)
- `git status` (pages if output > 24 lines)
- `git blame [large-file]` (pages on large files)

**Refs:**
- [Agent 8 Git Operations](../agents/guides/agent-8-git-ops.md#git-pager-prevention)
- [Agent 8 Mistakes Guide](../agents/guides/agent-8-mistakes-prevention-guide.md#high-terminal-stuck-in-git-pager-alternate-buffer)

---

### Pitfall 2: Less/More Pager in Other Commands

**Problem:** Other commands also use pagers (man, apt, systemctl, journalctl).

**Commands affected:**
```bash
man [command]           # Always pages
apt list               # Pages on long output
systemctl status       # Pages on long output
journalctl -xe         # Always pages
docker logs [id]       # Pages on long output
kubectl logs [pod]     # Pages on long output
```

**Solution:**

```bash
# Set PAGER environment variable
export PAGER=cat

# Or disable paging per-command
man -P cat [command]
systemctl status --no-pager
journalctl --no-pager
docker logs --follow=false [id]  # No pager in non-follow mode
kubectl logs [pod] --tail=100    # Limit output
```

---

### Pitfall 3: Interactive Prompts Blocking

**Problem:** Commands prompt for user input (y/n, password, confirmation), agent cannot respond.

**Examples:**
```bash
# Prompts for confirmation
rm -i file.txt          # Prompt: "remove file.txt? (y/n)"
apt-get install pkg     # Prompt: "Do you want to continue? [Y/n]"
git clean -i            # Interactive mode

# Prompts for input
git rebase -i HEAD~5    # Opens editor for commits
ssh user@host           # May prompt for password
sudo command            # Prompts for password
```

**Solution:**

```bash
# Use non-interactive flags
rm -f file.txt                    # Force, no prompt
apt-get install -y pkg            # Auto-yes
git clean -fd                     # Force, no interactive
git rebase HEAD~5                 # Non-interactive (or set GIT_EDITOR=:)
ssh -o BatchMode=yes user@host   # Fail if password required
echo "password" | sudo -S command # Pipe password (use with caution)

# Or use expect/autoexpect for complex interactions
```

**Prevention Checklist:**
- [ ] Always use `-y`, `-f`, `--yes`, `--force` flags
- [ ] Set `GIT_EDITOR=:` for non-interactive git operations
- [ ] Use SSH keys instead of passwords
- [ ] Test commands with `--help` to find non-interactive flags

---

### Pitfall 4: Text Editor Blocking

**Problem:** Commands open text editors (vim, nano, emacs), terminal waits for editor to close.

**Triggers:**
```bash
git commit              # Opens editor for commit message
git rebase -i           # Opens editor for rebase
crontab -e              # Opens editor for cron jobs
visudo                  # Opens editor for sudoers
```

**Solution:**

```bash
# Always provide message inline
git commit -m "message"              # No editor
git commit --amend --no-edit         # No editor

# Set EDITOR to non-blocking command
export GIT_EDITOR=":"                # Noop editor
export EDITOR="echo"                 # Echo editor
export VISUAL="cat"                  # Cat editor

# Or use heredoc for multi-line (keep lines <= 72 chars)
git commit -m "$(cat <<'EOF'
docs: add watchdog note to Streamlit quick start

Document optional watchdog install to suppress dev server warnings
and improve local reload performance.
EOF
)"
```

---

## Git Operations

### Pitfall 5: Amend After Push Creates Conflicts

**Problem:** Running `git commit --amend` after push rewrites history, causes divergence.

**Fatal Pattern:**
```bash
git commit -m "message"
[pre-commit hooks modify files]
git push                         # ← Original commit pushed
git commit --amend --no-edit     # ← Rewrites to different hash
git push                         # ← REJECTED (diverged)
```

**Solution:**

```bash
# ✅ CORRECT ORDER
git pull --ff-only              # [1] Pull first
git commit -m "message"
[pre-commit hooks modify files]
git add .
git commit --amend --no-edit    # [2] Amend BEFORE any push
git pull --ff-only              # [3] Pull again (race condition safety)
git push                        # [4] Push

# NEVER amend after push (unless you want force push)
```

**Ref:** [Agent 8 Mistakes Guide](../agents/guides/agent-8-mistakes-prevention-guide.md#critical-the-merge-commit-spike-disaster)

---

### Pitfall 6: Merge Conflicts with --ours Auto-Resolve

**Problem:** Using `git checkout --ours` silently discards remote changes.

**Risky Pattern:**
```bash
git pull
# CONFLICT in file.py
git checkout --ours file.py     # ← Keeps local, discards remote
git add file.py
git commit -m "merge"           # ← Silent data loss
```

**Solution:**

```bash
# Manual conflict resolution (preferred)
git pull
# CONFLICT in file.py
# Manually edit file.py, choose which changes to keep
git add file.py
git commit -m "merge: resolved conflict in file.py"

# Or use diff3 conflict style for better visibility
git config --global merge.conflictStyle diff3

# Or abort and retry
git merge --abort
git pull --rebase  # Try rebase instead
```

---

## Interactive Commands

### Pitfall 7: Commands Requiring TTY

**Problem:** Some commands require a TTY (terminal), fail when run by agents.

**Examples:**
```bash
# Fail in non-TTY
ssh -t user@host "interactive_command"  # Requires TTY
docker run -it image bash                # Requires TTY
screen                                   # Requires TTY
tmux                                     # Requires TTY
```

**Solution:**

```bash
# Remove interactive flags
docker run image command        # No -it flags
docker exec container command   # No -it flags

# Or allocate pseudo-TTY
script -q -c "command" /dev/null  # Linux
script -q /dev/null command       # macOS

# Or use expect
expect << EOF
spawn ssh user@host
expect "$ "
send "command\r"
expect "$ "
send "exit\r"
EOF
```

---

### Pitfall 8: Progress Bars and Spinners

**Problem:** Commands with progress bars can clutter logs or hang.

**Examples:**
```bash
curl [url]              # Shows progress bar
wget [url]              # Shows progress bar
npm install             # Shows progress spinner
pip install pkg         # Shows progress bar
```

**Solution:**

```bash
# Disable progress output
curl -s [url]           # Silent
curl --progress-bar     # Simple progress
wget -q [url]           # Quiet
npm install --quiet     # No spinner
pip install --quiet pkg # No progress
```

---

## File System Operations

### Pitfall 9: Race Conditions on File Creation

**Problem:** Checking if file exists, then creating it (TOCTOU vulnerability).

**Risky Pattern:**
```bash
if [ ! -f "file.txt" ]; then
    echo "content" > file.txt  # ← Race condition
fi
```

**Solution:**

```bash
# Atomic operations
mkdir -p "dir"                    # No error if exists
touch "file.txt"                  # Idempotent
echo "content" >> file.txt        # Append (safer than >)

# Or use noclobber
set -C                            # Prevent > from overwriting
echo "content" >| file.txt        # Explicit overwrite with >|

# Or use mv with rename
echo "content" > file.txt.tmp
mv file.txt.tmp file.txt          # Atomic on same filesystem
```

---

### Pitfall 10: Assuming File Paths Work

**Problem:** Paths with spaces, special characters, or globbing break commands.

**Broken Examples:**
```bash
cd path with spaces       # ❌ Broken (3 args)
rm *.txt                  # ❌ Deletes all .txt files (globbing)
file="test file.txt"
cat $file                 # ❌ Broken (2 args: "test" and "file.txt")
```

**Solution:**

```bash
# Always quote paths
cd "path with spaces"              # ✅ Works
rm "*.txt"                         # ✅ Deletes file named "*.txt"
file="test file.txt"
cat "$file"                        # ✅ Works

# Use arrays for multiple files
files=("file1.txt" "file 2.txt" "file-3.txt")
cat "${files[@]}"                  # ✅ Works

# Escape special characters
touch "file\$name.txt"             # Escape $
```

---

## Process Management

### Pitfall 11: Orphaned Background Processes

**Problem:** Starting background processes without cleanup leaves zombies.

**Risky Pattern:**
```bash
long_running_command &
pid=$!
# ... do other work ...
# Exit without killing $pid  # ← Orphaned process
```

**Solution:**

```bash
# Use trap for cleanup
cleanup() {
    kill $pid 2>/dev/null
    wait $pid 2>/dev/null
}
trap cleanup EXIT

long_running_command &
pid=$!
# ... do work ...
# cleanup runs automatically on exit

# Or use process groups
set -m  # Enable job control
long_running_command &
pid=$!
# Kill entire process group
kill -TERM -$pid  # Negative PID kills process group
```

---

### Pitfall 12: Not Checking Exit Codes

**Problem:** Continuing after command failures silently corrupts state.

**Risky Pattern:**
```bash
git pull
git push  # ← May push with conflicts if pull failed
```

**Solution:**

```bash
# Use set -e (exit on error)
set -e
git pull    # Script exits if pull fails
git push    # Only runs if pull succeeded

# Or check manually
if ! git pull; then
    echo "Pull failed, aborting"
    exit 1
fi
git push

# Or use || for fallback
git pull || { echo "Pull failed"; exit 1; }
git push
```

---

## Best Practices Summary

### Shell Script Best Practices

```bash
#!/bin/bash
set -euo pipefail  # Exit on error, undefined var, pipe failure

# Disable pagers
export GIT_PAGER=cat
export PAGER=cat

# Set non-interactive editors
export GIT_EDITOR=":"
export EDITOR="echo"

# Validate prerequisites
command -v git >/dev/null 2>&1 || { echo "git not found"; exit 1; }

# Quote all variables
file="$1"
cat "$file"

# Check exit codes
if ! git pull; then
    echo "Pull failed"
    exit 1
fi

# Cleanup on exit
cleanup() {
    rm -f /tmp/tempfile-$$
}
trap cleanup EXIT

# Avoid interactive prompts
git commit -m "message"  # Not: git commit
rm -f file              # Not: rm -i file
apt-get install -y pkg  # Not: apt-get install pkg
```

### Git Command Best Practices

```bash
# Always use short/porcelain formats
git status --short
git status --porcelain
git log --oneline -n 20
git diff --name-only

# Or disable pager
git --no-pager status
git --no-pager log
git --no-pager diff

# Provide messages inline
git commit -m "message"
git commit --amend --no-edit

# Pull before push
git pull --ff-only
git push

# Never amend after push (unless force push intended)
```

### Python Subprocess Best Practices

```python
import subprocess

# Use list args (avoids shell injection)
subprocess.run(["git", "status", "--short"], check=True)  # ✅
# Not: subprocess.run("git status", shell=True)  # ❌

# Capture output
result = subprocess.run(
    ["git", "status", "--porcelain"],
    capture_output=True,
    text=True,
    check=True,
    env={"GIT_PAGER": "cat"}  # Disable pager
)
print(result.stdout)

# Handle errors
try:
    subprocess.run(["git", "pull"], check=True)
except subprocess.CalledProcessError as e:
    print(f"Pull failed: {e}")
    sys.exit(1)

# Set timeout
subprocess.run(
    ["long_command"],
    timeout=60,  # Kill after 60 seconds
    check=True
)
```

---

## Testing Automation Scripts

### Pre-Deployment Checklist

Before deploying any automation:

- [ ] Test with `set -x` (show all commands executed)
- [ ] Test with `set -e` (exit on first error)
- [ ] Test with non-existent files/directories
- [ ] Test with files containing spaces in names
- [ ] Test with no internet connection (if network-dependent)
- [ ] Test with minimal permissions (non-root user)
- [ ] Test in clean environment (fresh docker container)
- [ ] Test all error branches (not just happy path)
- [ ] Test cleanup functions (trap EXIT)
- [ ] Test timeout behavior
- [ ] Test with pager-triggering output
- [ ] Test interactive command fallbacks

### Common Test Scenarios

```bash
# Test 1: No pager triggered
output=$(git log --oneline -n 100 2>&1)
if echo "$output" | grep -q "alternate buffer"; then
    echo "❌ Pager triggered"
    exit 1
fi

# Test 2: No interactive prompts
timeout 5s ./script.sh || {
    echo "❌ Script timed out (likely waiting for input)"
    exit 1
}

# Test 3: Exit code handling
./script.sh
if [ $? -ne 0 ]; then
    echo "❌ Script failed"
    exit 1
fi

# Test 4: Cleanup runs on error
./script.sh || true
if [ -f /tmp/tempfile-$$ ]; then
    echo "❌ Cleanup didn't run"
    exit 1
fi
```

---

## Additional Resources

- **Agent 8 Git Operations:** [agent-8-git-ops.md](../agents/guides/agent-8-git-ops.md)
- **Agent 8 Mistakes Guide:** [agent-8-mistakes-prevention-guide.md](../agents/guides/agent-8-mistakes-prevention-guide.md)
- **Bash Pitfalls:** https://mywiki.wooledge.org/BashPitfalls
- **Shell Check:** https://www.shellcheck.net/ (lint bash scripts)
- **Advanced Bash Guide:** https://tldp.org/LDP/abs/html/

---

**Last Updated:** 2026-01-10
**Maintainer:** Agent 8 (GIT OPERATIONS)
**Contributions:** Submit issues/PRs with additional pitfalls encountered
