# Migration Task Plan Walkthrough
**Date:** 2026-01-10
**Status:** Tailored for execution
**Owner:** Agent 9 (Governance)

---

## 📋 Validation Scripts Status

### ✅ All Required Scripts Present

| Script | Status | Purpose |
|--------|--------|---------|
| check_links.py | ✅ Exists | Broken link detection |
| check_docs_index.py | ✅ Exists | Index structure validation |
| check_docs_index_links.py | ✅ Exists | Index link validity |
| validate_folder_structure.py | ✅ Exists | Folder compliance |
| check_root_file_count.sh | ✅ Exists | Root file sprawl |
| collect_metrics.sh | ✅ Exists | Metrics collection |
| generate_dashboard.sh | ✅ Exists | Dashboard generation |
| generate_all_indexes.sh | ✅ Exists | Index generation |
| check_not_main.sh | ✅ Exists | Branch validation |
| validate_git_state.sh | ✅ Exists | Git state check |

**Result:** No missing prerequisites! ✅

---

## 🎯 Tailored Execution Plan

### Timeline Summary
- **Total time:** 15-20 hours over 2 weeks
- **Phases:** 6 phases (A0-A6)
- **Approach:** Small batches with validation after each
- **Risk level:** Low (junior-safe with stop conditions)

### Week 1: Prep + Structure (A0-A2)
- **Jan 10 (Today):** Phase A0 (Prep + Baseline) - 2-4h
- **Jan 11-12:** Phase A1 (Critical Structure) - 4-6h
- **Jan 13-14:** Phase A2 (High-Value Doc Moves) - 3-5h

### Week 2: Cleanup + Validation (A3-A6)
- **Jan 15:** Phase A3 (Dated Files) - 1-2h
- **Jan 16-17:** Phase A4 (Naming Cleanup) - 2-3h
- **Jan 18:** Phase A5 (Link + Script Integrity) - 2-3h
- **Jan 19:** Phase A6 (Final Validation) - 1-2h

---

## 📊 Phase A0: Prep + Baseline (READY TO EXECUTE)

### Prerequisites Check

**Decision Gate:**
- ✅ Option A selected (formally recorded in session work)
- ⚠️ Need to update DECISION-SUMMARY.md with formal decision
- ✅ Freeze window: No open PRs on docs/ (verified)
- ✅ Git state: Clean (main branch, no uncommitted changes)

**Required Scripts:**
- ✅ All validation scripts present
- ✅ All support scripts present
- ✅ No missing dependencies

### TASK-A0.1: Freeze Window + Baseline Snapshot

**Estimated time:** 2-4 hours

#### Step 1: Confirm Safe Git State (15 min)
```bash
# 1. Verify not on main (migration should use branch)
./scripts/check_not_main.sh

# NOTE: We're on main! Need to create migration branch first
git checkout -b migration/option-a-execution

# 2. Check for unfinished merges
./scripts/check_unfinished_merge.sh

# 3. Comprehensive git state validation
./scripts/validate_git_state.sh
```

**Expected outcome:** Clean git state, no blocking issues

#### Step 2: Create Backup Tag (5 min)
```bash
git tag backup-pre-migration-2026-01-10
git push origin backup-pre-migration-2026-01-10
```

**Expected outcome:** Tag created and pushed for rollback safety

#### Step 3: Run Baseline Metrics (30 min)
```bash
# Collect metrics
./scripts/collect_metrics.sh

# Generate dashboard
./scripts/generate_dashboard.sh
```

**Expected outcome:**
- Metrics captured in `metrics/`
- Dashboard updated in `agents/agent-9/governance/METRICS_DASHBOARD.md`

**Metrics to capture:**
- Root file count: ____ (current baseline)
- Validation errors: ____ (from validate_folder_structure.py)
- Broken link count: ____ (from check_links.py)
- Docs index link errors: ____ (from check_docs_index_links.py)

#### Step 4: Generate Initial Indexes (45 min)
```bash
# Generate all indexes for navigation study
chmod +x scripts/generate_all_indexes.sh
./scripts/generate_all_indexes.sh
```

**Expected outcome:**
- `index.json` and `index.md` in key folders
- Navigation data ready for hierarchical approach testing

#### Step 5: Run Validation Bundle (30 min)
```bash
# 1. Root file count
./scripts/check_root_file_count.sh

# 2. Folder structure
python scripts/validate_folder_structure.py

# 3. Link checks
.venv/bin/python scripts/check_links.py

# 4. Docs index structure
./scripts/check_docs_index.py

# 5. Docs index links
./scripts/check_docs_index_links.py
```

**Expected outcome:** Baseline validation results (issues logged if any)

#### Step 6: Log Results in MIGRATION-STATUS.md (15 min)

Update `agents/agent-9/governance/MIGRATION-STATUS.md`:

```markdown
## Metrics Snapshot (Phase A0 - 2026-01-10)

- Root file count: [FILL]
- Validation errors: [FILL]
- Broken link count: [FILL]
- Docs index link errors: [FILL]

## Readiness Checklist (Phase A0)

- [x] Baseline metrics captured
- [x] Dashboard updated
- [x] Indexes generated
- [x] Root file count check complete
- [x] Folder structure validation complete
- [x] Link checks complete
```

---

## 🚨 Stop Conditions (When to Pause)

### Red Flags (Must Fix Before Proceeding)
1. **Git state unclean:** Uncommitted changes, unfinished merges
2. **Critical script missing:** Any validation script not found
3. **Backup tag creation fails:** Can't create safety rollback point
4. **Validation bundle fails catastrophically:** >50 critical errors

### Yellow Flags (Document but Can Proceed)
1. **Minor link issues:** <10 broken links (document in MIGRATION-STATUS)
2. **Known validation errors:** Already tracked in Phase 1 work
3. **Index generation warnings:** Non-critical folder index issues

---

## 🎯 Phase A0 Success Criteria

After completing Phase A0, you should have:

✅ **Backup safety net:**
- Git tag created: `backup-pre-migration-2026-01-10`
- Tag pushed to remote

✅ **Baseline metrics captured:**
- All metrics recorded in MIGRATION-STATUS.md
- Dashboard generated and up-to-date
- Comparison baseline established

✅ **Indexes generated:**
- All key folders have index.json + index.md
- Navigation study ready for hierarchical testing

✅ **Validation baseline:**
- All validation scripts run successfully
- Issues logged in MIGRATION-STATUS.md
- No blocking errors

✅ **Documentation updated:**
- MIGRATION-STATUS.md has Phase A0 results
- DECISION-SUMMARY.md updated with Option A confirmation
- Next steps clear (Phase A1 ready to start)

---

## 📝 Issue Capture Example (If Issues Found)

```markdown
### Issue: Broken links in legacy docs
- Phase: A0
- Triggering check: ./scripts/check_links.py
- Impact: 8 broken links found (5 in docs/planning/, 3 in docs/research/)
- Root cause: Old session docs reference moved files
- Fix applied: Noted for Phase A3 archival (will be resolved when files archived)
- Follow-up: Re-run check_links.py after Phase A3
```

---

## 🔮 Next Phase Preview: A1 (Critical Structure)

**After Phase A0 completes:**
1. Review Phase A0 results
2. Address any critical issues
3. Update MIGRATION-STATUS.md
4. Proceed to Phase A1: Critical Structure (4-6 hours)

**Phase A1 Focus:**
- Ensure all required folders exist
- Verify READMEs in place
- Regenerate indexes after confirmation
- Run validation bundle

---

## ⚡ Quick Decision: Ready for Phase A0?

**Checklist:**
- ✅ All validation scripts exist
- ✅ Git state clean (will create branch)
- ✅ No open PRs on docs/
- ✅ Governance docs committed
- ⚠️ Need to create migration branch (not on main)
- ⚠️ Need to update DECISION-SUMMARY.md

**Recommendation:**
1. Create migration branch: `git checkout -b migration/option-a-execution`
2. Update DECISION-SUMMARY.md with Option A confirmation
3. Execute Phase A0 steps sequentially
4. Log all results in MIGRATION-STATUS.md

**Time estimate:** 2-4 hours for complete Phase A0 execution

---

**Status:** Ready to execute Phase A0
**Confidence:** High (90%)
**Blocking issues:** None (minor setup needed)
