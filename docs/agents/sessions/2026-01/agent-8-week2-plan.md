# Agent 8 Week 2 Implementation Plan
**Version:** 0.16.0
**Date:** 2026-01-09
**Status:** 📋 PLANNING
**Prerequisites:** Week 1 complete (4/4 optimizations merged, 90% speedup achieved)

---

## 🎯 Week 2 Objectives

**Goal:** Further optimize workflow through integration and intelligence

**Target Improvements:**
- **User Experience:** Seamless CI monitoring, smarter decision-making, faster hooks
- **Developer Productivity:** Automatic PR management, intelligent caching, parallel execution
- **System Reliability:** Comprehensive test coverage for all git operations

**Success Criteria:**
- CI Monitor auto-start integrated into workflow
- Pre-commit hooks optimized (conditional execution + parallelization)
- File risk assessment cached (avoid redundant analysis)
- Branch operations tested (comprehensive coverage)
- All changes deployed to production with zero regressions

---

## 📊 Week 2 Optimizations

### Optimization #5: CI Monitor Integration (2-3 hours)
**Status:** 📋 PLANNED
**Priority:** HIGH
**Dependencies:** Week 1 Optimization #3 (CI Monitor Daemon)

**Implementation:**
1. **Auto-start CI Monitor** (30 minutes)
   - Add daemon start to `scripts/agent_setup.sh`
   - Check if daemon is already running (avoid duplicates)
   - Log daemon PID in session notes
   - Graceful handling if daemon fails to start

2. **Integrate with finish_task_pr.sh** (45 minutes)
   - Add `--wait-for-ci` flag to `finish_task_pr.sh`
   - After PR creation, notify daemon to monitor this PR
   - Optional: Block until PR merges (for synchronous workflow)
   - Terminal notification when PR auto-merges

3. **Dashboard View** (45 minutes)
   - Enhance `ci_monitor_daemon.sh status` to show all monitored PRs
   - Show CI status for each PR (pending/running/passed/failed)
   - Estimated merge time (based on typical CI duration)
   - Color-coded status output (green=passing, yellow=running, red=failed)

**Files Modified:**
- `scripts/agent_setup.sh` (add daemon start)
- `scripts/finish_task_pr.sh` (add `--wait-for-ci` flag)
- `scripts/ci_monitor_daemon.sh` (enhance status command)

**Expected Performance Impact:**
- **User Experience:** Developers never need to manually check CI status
- **Time Savings:** 0-2 minutes per PR (if not waiting, no blocking)
- **Workflow Improvement:** Notifications keep developers informed without context-switching

**Test Cases:**
- Daemon auto-starts on session setup
- Daemon doesn't duplicate if already running
- `finish_task_pr.sh --wait-for-ci` blocks until merge
- Status command shows accurate PR states
- Terminal notifications work correctly

---

### Optimization #6: Pre-commit Hook Optimization (3-4 hours)
**Status:** 📋 PLANNED
**Priority:** HIGH
**Dependencies:** None

**Problem Analysis:**
Current pre-commit hooks run ALL checks on EVERY commit:
- `check-yaml` runs even if no YAML files changed
- `check-json` runs even if no JSON files changed
- `black` runs on all Python files (even unchanged)
- `ruff` runs on all Python files (even unchanged)
- **Total overhead:** 1-2 seconds per commit (adds up over time)

**Implementation:**

#### Part A: Conditional Execution (1.5 hours)
Modify `.pre-commit-config.yaml` to run hooks only on relevant files:

```yaml
# OLD: Run black on all files
- repo: https://github.com/psf/black
  rev: 23.12.1
  hooks:
    - id: black
      # No conditions - runs on all commits

# NEW: Run black only if Python files changed
- repo: https://github.com/psf/black
  rev: 23.12.1
  hooks:
    - id: black
      files: \.py$  # Only .py files
      # Pre-commit automatically skips if no matching files
```

**Hooks to optimize:**
- `check-yaml` → only if `*.yml` or `*.yaml` changed
- `check-json` → only if `*.json` changed
- `black` → only if `*.py` changed (already done, verify)
- `ruff` → only if `*.py` changed (already done, verify)
- `check-added-large-files` → always run (critical)
- `trailing-whitespace` → always run (critical for Step 2.5)
- `end-of-file-fixer` → always run (critical)
- `mixed-line-ending` → always run (critical)

**Implementation Steps:**
1. Audit `.pre-commit-config.yaml` - identify hooks without file filters
2. Add `files:` patterns to appropriate hooks
3. Test with commits touching different file types
4. Measure performance improvement (expect 30-50% faster for non-Python commits)

#### Part B: Parallel Hook Execution (1.5-2 hours)
Enable parallel execution in `.pre-commit-config.yaml`:

```yaml
# At top of .pre-commit-config.yaml
default_stages: [commit]
default_language_version:
  python: python3.9
fail_fast: false  # Don't stop on first failure
parallel: true    # NEW: Run hooks in parallel
```

**Challenges:**
- Some hooks may have side effects (writing to same file)
- Need to test for race conditions
- May need to exclude certain hooks from parallelization

**Safe Hooks for Parallelization:**
- `check-yaml` (read-only)
- `check-json` (read-only)
- `check-added-large-files` (read-only)
- `black` (safe - atomic writes)
- `ruff` (safe - atomic writes)

**Unsafe Hooks (keep sequential):**
- `trailing-whitespace` (modifies files - may conflict)
- `end-of-file-fixer` (modifies files - may conflict)
- `mixed-line-ending` (modifies files - may conflict)

**Implementation Steps:**
1. Add `parallel: true` to config
2. Test with multiple file changes
3. Watch for race conditions or corrupted files
4. If issues, exclude problematic hooks from parallelization
5. Measure performance improvement (expect 20-40% faster on multi-file commits)

**Files Modified:**
- `.pre-commit-config.yaml` (add file filters, enable parallel)

**Expected Performance Impact:**
- **Conditional execution:** 30-50% faster for non-Python commits (YAML/JSON/docs only)
- **Parallel execution:** 20-40% faster for multi-file commits
- **Combined:** Up to 70% faster for commits with mixed file types

**Test Cases:**
- Commit only YAML files → `check-yaml` runs, black/ruff skip
- Commit only Python files → black/ruff run, YAML checks skip
- Commit mixed files → relevant hooks run in parallel
- Hooks don't corrupt files (race condition test)
- Pre-commit still catches all issues (no false negatives)

---

### Optimization #7: File Risk Caching (2-3 hours)
**Status:** 📋 PLANNED
**Priority:** MEDIUM
**Dependencies:** None

**Problem Analysis:**
`scripts/should_use_pr.sh` analyzes file risk on EVERY invocation:
- Parses file extensions
- Counts lines changed
- Calculates complexity score
- **Redundant:** Same file analyzed multiple times in same session

**Implementation:**

#### Part A: Risk Cache Implementation (1.5 hours)
Create `scripts/risk_cache.sh` library:

```bash
#!/bin/bash
# scripts/risk_cache.sh
# Cache file risk assessments to avoid redundant analysis

CACHE_DIR="${PROJECT_ROOT}/.git/risk_cache"
CACHE_TTL=3600  # 1 hour (adjustable)

# Initialize cache directory
init_cache() {
    mkdir -p "$CACHE_DIR"
}

# Generate cache key from file path and modification time
get_cache_key() {
    local file=$1
    local mtime=$(stat -f "%m" "$file" 2>/dev/null || echo "0")
    echo "${file}:${mtime}" | sha256sum | cut -d' ' -f1
}

# Check if cached risk assessment exists and is valid
get_cached_risk() {
    local file=$1
    local cache_key=$(get_cache_key "$file")
    local cache_file="${CACHE_DIR}/${cache_key}"

    # Check if cache file exists and is within TTL
    if [ -f "$cache_file" ]; then
        local cache_age=$(($(date +%s) - $(stat -f "%m" "$cache_file")))
        if [ "$cache_age" -lt "$CACHE_TTL" ]; then
            cat "$cache_file"
            return 0
        fi
    fi

    return 1
}

# Store risk assessment in cache
set_cached_risk() {
    local file=$1
    local risk=$2
    local cache_key=$(get_cache_key "$file")
    local cache_file="${CACHE_DIR}/${cache_key}"

    echo "$risk" > "$cache_file"
}

# Invalidate cache for specific file (on modification)
invalidate_cache() {
    local file=$1
    local cache_key=$(get_cache_key "$file")
    local cache_file="${CACHE_DIR}/${cache_key}"

    rm -f "$cache_file"
}

# Clean up old cache entries (run periodically)
cleanup_cache() {
    find "$CACHE_DIR" -type f -mtime +1 -delete  # Remove >1 day old
}
```

#### Part B: Integrate with should_use_pr.sh (1-1.5 hours)
Modify `scripts/should_use_pr.sh` to use cache:

```bash
# At start of should_use_pr.sh
source "$(dirname "$0")/risk_cache.sh"
init_cache

# In file analysis loop
for file in $files; do
    # Check cache first
    if cached_risk=$(get_cached_risk "$file"); then
        echo "DEBUG: Using cached risk for $file: $cached_risk"
        total_risk=$((total_risk + cached_risk))
        continue
    fi

    # Cache miss - calculate risk
    file_risk=$(calculate_file_risk "$file")

    # Store in cache
    set_cached_risk "$file" "$file_risk"

    total_risk=$((total_risk + file_risk))
done
```

#### Part C: Cache Invalidation (30 minutes)
Hook into git operations to invalidate cache:

```bash
# In safe_push.sh after Step 2 (commit)
# Invalidate cache for committed files
for file in $(git diff --name-only HEAD~1 HEAD); do
    invalidate_cache "$file"
done
```

**Files Modified:**
- `scripts/risk_cache.sh` (new)
- `scripts/should_use_pr.sh` (add cache usage)
- `scripts/safe_push.sh` (add cache invalidation)

**Expected Performance Impact:**
- **First analysis:** Same speed (cache miss)
- **Subsequent analyses:** 50-80% faster (cache hit)
- **Session improvement:** 30-50% faster overall (multiple `should_use_pr.sh` calls)

**Cache Invalidation Strategy:**
- **File modified:** Invalidate on commit (mtime change detected)
- **TTL expires:** 1 hour (adjustable)
- **Manual cleanup:** `cleanup_cache` runs weekly (cron or agent_setup.sh)

**Test Cases:**
- First `should_use_pr.sh` call → cache miss, analysis runs
- Second call (same file) → cache hit, instant result
- File modified → cache invalidated, fresh analysis
- Cache entry expires → automatic cleanup
- Manual `cleanup_cache` → old entries removed

---

### Optimization #8: Branch State Test Suite (3-4 hours)
**Status:** 📋 PLANNED
**Priority:** MEDIUM
**Dependencies:** None

**Rationale:**
Week 1 Optimization #4 tested merge conflicts (90% coverage). Week 2 should test ALL git operations for comprehensive reliability.

**Implementation:**

#### Test Scenarios (20 tests planned)

**Branch Operations (5 tests):**
1. **Create branch** - `git checkout -b task/TEST-001`
2. **Switch branch** - `git checkout main` then `git checkout task/TEST-001`
3. **Delete branch** - `git branch -d task/TEST-001` (merged), `git branch -D task/TEST-001` (forced)
4. **List branches** - `git branch --list`, verify all branches shown
5. **Rename branch** - `git branch -m old-name new-name`

**Worktree Operations (5 tests):**
1. **Create worktree** - `git worktree add ../worktree-test task/TEST-001`
2. **List worktrees** - `git worktree list`, verify all shown
3. **Remove worktree** - `git worktree remove ../worktree-test`
4. **Prune stale worktrees** - `git worktree prune`
5. **Worktree branch conflict** - Two worktrees try to use same branch (should fail)

**PR Workflow Operations (5 tests):**
1. **Create task branch** - `scripts/create_task_pr.sh TASK-001 "Test"`
2. **Commit on task branch** - `scripts/ai_commit.sh "test commit"`
3. **Finish task PR** - `scripts/finish_task_pr.sh TASK-001 "Test"`
4. **PR merge** - Verify PR created, CI passes, auto-merge works
5. **Branch cleanup** - Verify local/remote branches deleted after merge

**Edge Cases (5 tests):**
1. **Unfinished merge** - Detect `MERGE_HEAD`, complete merge
2. **Detached HEAD** - Recovery to named branch
3. **Uncommitted changes** - Stash, switch branch, pop stash
4. **Branch behind remote** - Pull with fast-forward, handle conflicts
5. **Remote branch deleted** - Local branch still exists, clean up

**Test Infrastructure:**
```bash
#!/bin/bash
# scripts/test_branch_operations.sh
# Comprehensive test suite for git branch and worktree operations

setup_test_env() {
    TEST_DIR=$(mktemp -d)
    cd "$TEST_DIR"

    # Create test repository
    git init test_repo
    cd test_repo
    git config user.email "test@example.com"
    git config user.name "Test User"

    # Create initial commit
    echo "Initial commit" > README.md
    git add README.md
    git commit -m "Initial commit"
}

cleanup_test_env() {
    cd /
    rm -rf "$TEST_DIR"
}

trap cleanup_test_env EXIT

# Test functions
test_1_create_branch() {
    git checkout -b task/TEST-001
    assert_equal "$(git branch --show-current)" "task/TEST-001" "Branch created"
}

test_6_create_worktree() {
    git checkout -b task/WORKTREE-001
    git worktree add ../worktree-test task/WORKTREE-001
    assert_contains "$(git worktree list)" "worktree-test" "Worktree created"
}

# ... 18 more tests ...

# Run all tests
run_tests
```

**Files Created:**
- `scripts/test_branch_operations.sh` (new, 800-1000 lines)

**Expected Coverage:**
- Branch operations: 100%
- Worktree operations: 100%
- PR workflow: 80% (some steps require GitHub API)
- Edge cases: 90%

**Test Cases:**
- All 20 tests pass
- Test duration <10 seconds
- No false positives (tests accurately reflect real behavior)
- Edge cases caught before production

---

## 📈 Expected Performance Summary

| Metric | Week 1 Baseline | Week 2 Target | Improvement |
|--------|----------------|---------------|-------------|
| Commit Time | ~5s | ~3-4s | 20-40% faster |
| CI Wait | 0s (daemon) | 0s (integrated) | Same (already optimal) |
| Pre-commit Hooks | 1-2s | 0.5-1s | 50% faster |
| should_use_pr.sh | 0.5s | 0.1-0.2s | 60-80% faster |
| Test Coverage | 15 tests (conflicts) | 35 tests (all ops) | 133% increase |

**Overall Workflow Impact:**
- Week 1: 45-60s → 5s (90% faster)
- Week 2: 5s → 3-4s (additional 20-40% speedup)
- **Total improvement:** 45-60s → 3-4s (93-95% faster!)

---

## 🔄 Implementation Order

### Phase 1: High-Impact, Low-Risk (First Session, 2-3 hours)
1. **Optimization #5A:** Auto-start CI Monitor (30 min)
2. **Optimization #6A:** Conditional pre-commit hooks (1.5 hours)
3. Test and validate changes

**Rationale:** These changes are low-risk (no breaking changes) and high-impact (immediate productivity gains). Start Week 2 with quick wins.

### Phase 2: Medium-Impact, Medium-Risk (Second Session, 3-4 hours)
1. **Optimization #7:** File risk caching (2-3 hours)
2. **Optimization #5B:** Integrate CI Monitor with finish_task_pr.sh (45 min)
3. Test and validate changes

**Rationale:** Caching adds complexity (cache invalidation), so implement after high-confidence changes. CI Monitor integration builds on Phase 1 foundation.

### Phase 3: High-Value, Higher-Risk (Third Session, 4-5 hours)
1. **Optimization #6B:** Parallel pre-commit hooks (1.5-2 hours)
2. **Optimization #8:** Branch state test suite (3-4 hours)
3. Comprehensive testing

**Rationale:** Parallel hooks have race condition risks. Test suite is time-intensive but critical for reliability. Implement last when all other optimizations are stable.

### Phase 4: Polish and Documentation (Fourth Session, 1-2 hours)
1. **Optimization #5C:** CI Monitor dashboard (45 min)
2. Update documentation (30 min)
3. Create Week 2 completion summary (30 min)

**Rationale:** Dashboard is nice-to-have, not critical. Documentation ensures knowledge transfer for future agents.

---

## 🧪 Testing Strategy

### Unit Tests (Per Optimization)
- Each optimization has specific test cases (listed above)
- Test isolation (no dependencies between tests)
- Fast execution (<10 seconds per optimization)

### Integration Tests (End-to-End)
- Full workflow test: `agent_setup.sh → ai_commit.sh → finish_task_pr.sh`
- Verify all optimizations work together
- No performance regressions (Week 1 baseline maintained)

### Regression Tests (Week 1 Coverage)
- Re-run Week 1 test suite (15 merge conflict tests)
- Verify Week 1 optimizations still work
- No breaking changes introduced

### Performance Benchmarks
- Measure commit time (target: 3-4s)
- Measure pre-commit duration (target: 0.5-1s)
- Measure should_use_pr.sh (target: 0.1-0.2s)
- Compare against Week 1 baseline

---

## 📊 Success Metrics

### Quantitative Metrics
- [ ] Commit time reduced by 20-40% (5s → 3-4s)
- [ ] Pre-commit hooks 50% faster (1-2s → 0.5-1s)
- [ ] File risk assessment 60-80% faster (0.5s → 0.1-0.2s)
- [ ] Test coverage increased by 133% (15 → 35 tests)
- [ ] All tests passing (35/35)
- [ ] CI Monitor auto-starts on session setup
- [ ] Zero manual CI status checks required

### Qualitative Metrics
- [ ] Developer experience improved (seamless workflow)
- [ ] CI monitoring fully automated (no manual intervention)
- [ ] Git operations reliable (comprehensive test coverage)
- [ ] Documentation updated (knowledge preserved)

---

## 🚨 Risk Assessment

### High-Risk Changes
1. **Parallel pre-commit hooks (Opt #6B)**
   - **Risk:** Race conditions, file corruption
   - **Mitigation:** Thorough testing, exclude unsafe hooks, rollback plan
   - **Rollback:** Revert `.pre-commit-config.yaml` to sequential execution

2. **Cache invalidation (Opt #7)**
   - **Risk:** Stale cache, incorrect risk assessments
   - **Mitigation:** Conservative TTL (1 hour), file mtime tracking, manual cleanup
   - **Rollback:** Delete `.git/risk_cache/`, disable caching

### Medium-Risk Changes
1. **CI Monitor auto-start (Opt #5A)**
   - **Risk:** Daemon fails to start, blocks session setup
   - **Mitigation:** Graceful error handling, continue if daemon fails
   - **Rollback:** Remove auto-start from `agent_setup.sh`

2. **Conditional pre-commit hooks (Opt #6A)**
   - **Risk:** Hooks skip incorrectly, miss issues
   - **Mitigation:** Test with all file types, verify no false negatives
   - **Rollback:** Remove `files:` patterns from `.pre-commit-config.yaml`

### Low-Risk Changes
1. **CI Monitor integration (Opt #5B)**
   - **Risk:** Minimal (optional flag, doesn't affect existing workflow)
   - **Mitigation:** Test both with/without `--wait-for-ci` flag

2. **Branch state tests (Opt #8)**
   - **Risk:** None (read-only tests, no production impact)
   - **Mitigation:** N/A (pure testing)

---

## 📝 Documentation Updates

### Files to Update (Post-Implementation)
- [ ] `docs/agents/sessions/2026-01/agent-8-week2-completion-summary.md` (create)
- [ ] `docs/TASKS.md` (add AGENT8-WEEK2 entry)
- [ ] `docs/SESSION_LOG.md` (add Week 2 achievements)
- [ ] `docs/planning/next-session-brief.md` (update with Week 3 planning)
- [ ] `docs/AGENT_WORKFLOW_MASTER_GUIDE.md` (add Week 2 features)
- [ ] `.github/copilot-instructions.md` (update performance metrics)

### New Documentation to Create
- [ ] `docs/git-workflow-caching.md` (cache usage guide)
- [ ] `docs/ci-monitor-integration-guide.md` (daemon usage)
- [ ] `scripts/README.md` (update with new scripts)

---

## 🎓 Learning Objectives

### For Future Agents
1. **Caching strategies:** When to cache, how to invalidate, TTL considerations
2. **Pre-commit optimization:** Conditional execution, parallelization, trade-offs
3. **Background daemon integration:** Auto-start, graceful degradation, status monitoring
4. **Comprehensive testing:** Branch operations, worktrees, PR workflows, edge cases

### For Project
1. **Performance optimization patterns:** I/O parallelization, incremental processing, intelligent caching
2. **Reliability through testing:** Comprehensive test suites prevent regressions
3. **Developer experience focus:** Automation eliminates manual tasks, reduces cognitive load

---

## 🔗 References

### Week 1 Resources
- [Week 1 Completion Summary](agent-8-week1-completion-summary.md)
- [PR #309: Parallel Git Fetch](https://github.com/Pravin-surawase/structural_engineering_lib/pull/309)
- [PR #310: Incremental Whitespace Fix](https://github.com/Pravin-surawase/structural_engineering_lib/pull/310)
- [PR #311: CI Monitor Daemon](https://github.com/Pravin-surawase/structural_engineering_lib/pull/311)
- [PR #312: Merge Conflict Test Suite](https://github.com/Pravin-surawase/structural_engineering_lib/pull/312)

### Week 2 Scripts
- `scripts/agent_setup.sh` (modify)
- `scripts/finish_task_pr.sh` (modify)
- `scripts/ci_monitor_daemon.sh` (enhance)
- `scripts/should_use_pr.sh` (add caching)
- `scripts/risk_cache.sh` (new)
- `scripts/test_branch_operations.sh` (new)
- `.pre-commit-config.yaml` (optimize)

### Documentation
- `docs/AGENT_WORKFLOW_MASTER_GUIDE.md` (comprehensive workflow guide)
- `docs/git-workflow-ai-agents.md` (git workflow documentation)
- `docs/TASKS.md` (task tracking)

---

## ⏱️ Time Estimates

| Optimization | Estimate | Confidence |
|--------------|----------|------------|
| #5: CI Monitor Integration | 2-3 hours | HIGH (builds on Week 1) |
| #6: Pre-commit Optimization | 3-4 hours | MEDIUM (testing critical) |
| #7: File Risk Caching | 2-3 hours | MEDIUM (cache invalidation complex) |
| #8: Branch State Tests | 3-4 hours | HIGH (similar to Week 1 tests) |
| **Total Week 2** | **10-14 hours** | **HIGH** |

**Comparison:**
- Week 1: 6 hours actual (as estimated)
- Week 2: 10-14 hours estimated (67% more complex)

---

## 🚀 Getting Started

### Prerequisites Check
```bash
# Verify Week 1 complete
git log --oneline -4 | grep -E "(#309|#310|#311|#312)"

# Verify CI Monitor available
./scripts/ci_monitor_daemon.sh status

# Verify test suite passing
./scripts/test_merge_conflicts.sh

# Verify clean working tree
git status -sb
```

### Start Week 2
```bash
# Create Week 2 branch (optional)
git checkout -b agent8/week2-integration

# Or work directly on main (for small incremental changes)
# Begin with Optimization #5A (CI Monitor auto-start)
```

---

**Prepared by:** Agent 8 (Main Agent)
**Planning Date:** 2026-01-09
**Implementation Start:** TBD
**Estimated Completion:** TBD

**Status:** 📋 PLANNING COMPLETE - READY TO START!
