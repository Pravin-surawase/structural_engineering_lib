# Git Workflow Quick Reference

**Canonical:** `docs/git-workflow-ai-agents.md`

**Last Updated:** 2026-01-06
**Status:** ✅ Production Ready (tested with 13 scenarios)

---

## ⚡ Quick Decision

```bash
# Stage your changes
git add <files>

# Check what workflow to use
./scripts/should_use_pr.sh --explain
```

**Output:**
- ✅ Exit 0 = Direct commit OK
- 🔀 Exit 1 = Use Pull Request

---

## ✅ Direct Commit (Low-Risk Only)

### Allowed For
- **Documentation:** `docs/**/*.md`
- **Tests:** `Python/tests/**/*.py` (no production code)
- **Scripts:** `scripts/**/*.sh` (tooling)
- **Config:** `.github/copilot-instructions.md`

### Commands
```bash
# After staging files
./scripts/ai_commit.sh "docs: fix typo in README"
./scripts/ai_commit.sh "test: add test case for X"
./scripts/ai_commit.sh "chore: update helper script"
```

---

## 🔀 Pull Request (Production Code)

### Required For
- **Production:** `Python/structural_lib/**/*.py`
- **VBA:** `VBA/**/*.bas`, `Excel/**/*.xlsm`
- **CI:** `.github/workflows/**/*.yml`
- **Dependencies:** `pyproject.toml`, `requirements*.txt`
- **Mixed changes:** Docs + Code

### Commands
```bash
# 1. Create feature branch + PR
./scripts/create_task_pr.sh TASK-XXX "description"

# 2. Make changes and commit
vim Python/structural_lib/flexure.py
./scripts/ai_commit.sh "feat: add calculate_xyz()"

# 3. When done, merge and cleanup
./scripts/finish_task_pr.sh TASK-XXX "description"
```

---

## 🧪 Testing

```bash
# Test the decision tool
./scripts/test_should_use_pr.sh

# Test git whitespace fix
./scripts/verify_git_fix.sh

# Test full workflow
./scripts/test_git_workflow.sh --verbose
```

---

## 📊 Examples

### ✅ Example 1: Doc Fix (Direct)
```bash
vim docs/README.md
git add docs/README.md
./scripts/should_use_pr.sh --explain
# Output: ✅ Direct commit (Documentation only)
./scripts/ai_commit.sh "docs: fix installation instructions"
```

### 🔀 Example 2: Add Function (PR)
```bash
vim Python/structural_lib/flexure.py
git add Python/structural_lib/flexure.py
./scripts/should_use_pr.sh --explain
# Output: 🔀 Pull Request (Production code changed)
./scripts/create_task_pr.sh TASK-163 "Add calculate_moment()"
```

### 🔀 Example 3: Mixed Changes (PR)
```bash
vim docs/API.md
vim Python/structural_lib/api.py
git add docs/API.md Python/structural_lib/api.py
./scripts/should_use_pr.sh --explain
# Output: 🔀 Pull Request (Production code changed)
./scripts/create_task_pr.sh TASK-XXX "Update API"
```

---

## ⚠️ Override Cases

**When tool says PR but you want direct commit:**

Only override if:
1. Testing the tool itself (like today's commit)
2. Emergency hotfix with full justification
3. Doc urgency (typo in production docs)

**Document in commit message:**
```bash
./scripts/ai_commit.sh "fix: emergency hotfix for X

Note: Overriding PR requirement because:
- Production issue affecting users
- Fix is 2 lines, fully tested
- CI will validate before deploy"
```

---

## 🎯 Decision Tree

```
Staged files?
├─ docs/** only? ──────────────────> ✅ Direct commit
├─ Python/tests/** only? ──────────> ✅ Direct commit
├─ scripts/** only? ───────────────> ✅ Direct commit
├─ docs/ + scripts/? ──────────────> ✅ Direct commit
├─ Python/structural_lib/**? ──────> 🔀 Pull Request
├─ VBA/** or Excel/**? ────────────> 🔀 Pull Request
├─ .github/workflows/**? ──────────> 🔀 Pull Request
├─ pyproject.toml or requirements?─> 🔀 Pull Request
└─ Mixed (docs + code)? ───────────> 🔀 Pull Request
```

---

## 📈 Metrics (Track Over 2 Weeks)

- ✅ **Zero breaking changes** on direct commits
- ✅ **<5 minute** merge time for PRs
- ✅ **Clear audit trail** for production changes
- ✅ **No friction** in workflow

---

## 🔧 Troubleshooting

**Q: Tool says PR but I think it's safe?**
A: Check staged files with `git status`. If truly low-risk (docs/tests/scripts only), re-check your staging.

**Q: Made mistake - committed code directly?**
A: `git reset --soft HEAD~1` then use PR workflow

**Q: PR taking too long?**
A: CI should be <30s. If slower, check `gh pr checks <num>`

**Q: Tool not working?**
A: Run tests: `./scripts/test_should_use_pr.sh`

---

## 📚 Full Documentation

- **Research:** `docs/research/git-workflow-production-stage.md`
- **Contributing:** `docs/contributing/github-workflow.md`
- **Agent Rules:** `.github/copilot-instructions.md`

---

**✅ Status:** Tested with 13 scenarios, all passing. Ready for production use.
