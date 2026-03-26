# V3 Automation Foundation Research

**Type:** Research
**Audience:** Developers
**Status:** Draft
**Importance:** Critical
**Created:** 2026-01-24
**Last Updated:** 2026-01-24
**Related Tasks:** V3 Foundation, TASK-V3-FOUNDATION

---

## Executive Summary

This research analyzes the automation script ecosystem to prepare for the React + FastAPI V3 migration. Key findings:

1. **51% documentation gap**: 73 of 143 scripts lack documentation in automation-catalog.md
2. **V3-critical scripts exist but undocumented**: API validation, migration, and testing scripts
3. **New automation needed**: FastAPI validation, React build integration, API parity testing
4. **Scripts README outdated**: Shows 128 scripts, actual count is 143

---

## 1. Current Automation Landscape

### 1.1 Script Statistics

| Metric | Count |
|--------|-------|
| **Total scripts** | 143 |
| **Python scripts (.py)** | 75 |
| **Shell scripts (.sh)** | 68 |
| **Documented in automation-catalog.md** | 70 |
| **Undocumented scripts** | 73 (51%) |
| **Tier 0 (critical daily use)** | 5 |
| **Categories in index.json** | 14 |

### 1.2 Script Coverage by Category

| Category | Total | Documented | Gap |
|----------|-------|------------|-----|
| Git Workflow | 17 | 14 | 3 |
| Session Management | 12 | 8 | 4 |
| Code Validation | 18 | 10 | 8 |
| Documentation | 16 | 8 | 8 |
| File Operations | 10 | 4 | 6 |
| Project Structure | 12 | 5 | 7 |
| API Validation | 7 | 2 | 5 |
| Testing | 16 | 10 | 6 |
| Release | 6 | 4 | 2 |
| CI/CD | 8 | 5 | 3 |
| Code Migration | 5 | 1 | 4 |
| Streamlit Dev | 5 | 3 | 2 |
| VBA | 4 | 2 | 2 |
| Governance | 7 | 4 | 3 |

---

## 2. Undocumented Scripts Analysis

### 2.1 V3-Critical Scripts (High Priority)

These scripts are essential for V3 migration but lack documentation:

| Script | Purpose | V3 Relevance |
|--------|---------|--------------|
| `generate_api_manifest.py` | Generate API manifest JSON | **Critical** - Documents API for FastAPI wrapper |
| `check_api_signatures.py` | Validate API contracts | **Critical** - Ensures API stability for migration |
| `validate_migration.py` | Validate module migrations | **Critical** - Module migration validation |
| `pre_migration_check.py` | Pre-migration validation | **Critical** - Safety checks before migration |
| `create_reexport_stub.py` | Create re-export stubs | **High** - Maintain backward compatibility |
| `update_is456_init.py` | Update IS456 exports | **High** - API organization |
| `validate_stub_exports.py` | Validate stub modules | **High** - Export path validation |
| `migrate_module.py` | Module migration helper | **High** - Automates migration steps |

### 2.2 Quality Assurance Scripts (Medium-High Priority)

| Script | Purpose | V3 Relevance |
|--------|---------|--------------|
| `check_circular_imports.py` | Detect import cycles | **High** - Clean architecture |
| `check_type_annotations.py` | Validate type hints | **High** - FastAPI needs types |
| `check_fragment_violations.py` | Streamlit fragment API | **Medium** - Current UI only |
| `check_streamlit_imports.py` | Streamlit imports | **Medium** - Current UI only |
| `check_performance_issues.py` | Performance detection | **Medium** - General utility |
| `audit_input_validation.py` | Input validation audit | **High** - API robustness |
| `profile_streamlit_page.py` | Page profiling | **Low** - Streamlit-specific |

### 2.3 Documentation Scripts (Medium Priority)

| Script | Purpose | V3 Relevance |
|--------|---------|--------------|
| `create_doc.py` | Create docs with metadata | **Medium** - General utility |
| `check_doc_similarity.py` | Prevent duplicates | **Medium** - Doc quality |
| `check_doc_metadata.py` | Validate doc headers | **Medium** - Doc quality |
| `check_doc_frontmatter.py` | Frontmatter format | **Medium** - Doc quality |
| `check_duplicate_docs.py` | Find duplicate docs | **Medium** - Doc quality |
| `find_orphan_files.py` | Find unreferenced files | **Medium** - Cleanup |
| `fix_broken_links.py` | Auto-fix links | **Medium** - Doc maintenance |
| `consolidate_docs.py` | Merge similar docs | **Medium** - Doc quality |
| `enhance_readme.py` | Enhance README content | **Low** - One-time use |
| `analyze_doc_redundancy.py` | Find doc redundancy | **Low** - Analysis only |

### 2.4 Infrastructure Scripts (Medium Priority)

| Script | Purpose | V3 Relevance |
|--------|---------|--------------|
| `agent_start.sh` | Unified session start | **High** - Daily use |
| `git_ops.sh` | Git state router | **High** - Daily use |
| `git_automation_health.sh` | Git system health | **Medium** - Diagnostics |
| `collect_diagnostics.py` | Bundle debug context | **Medium** - Troubleshooting |
| `find_automation.py` | Script discovery | **High** - Agent onboarding |
| `check_scripts_index.py` | Index validation | **Medium** - Maintenance |
| `launch_streamlit.sh` | Start Streamlit | **Low** - Streamlit-specific |

### 2.5 Governance Scripts (Lower Priority)

| Script | Purpose | V3 Relevance |
|--------|---------|--------------|
| `governance_health_score.py` | Governance metrics | **Low** - Metrics only |
| `predict_velocity.py` | Velocity prediction | **Low** - Metrics only |
| `analyze_release_cadence.py` | Release analysis | **Low** - Analysis only |
| `check_governance_compliance.py` | Compliance check | **Low** - Governance |
| `weekly_governance_check.sh` | Weekly audit | **Low** - Scheduling |

### 2.6 Testing & VBA Scripts (Lower Priority)

| Script | Purpose | V3 Relevance |
|--------|---------|--------------|
| `test_import_3d_pipeline.py` | 3D pipeline test | **Medium** - Integration testing |
| `test_setup.py` | Installation test | **Medium** - CI validation |
| `test_vba_adapter.py` | VBA adapter test | **Low** - VBA-specific |
| `run_vba_smoke_tests.py` | VBA smoke tests | **Low** - VBA-specific |
| `vba_validator.py` | VBA syntax check | **Low** - VBA-specific |

---

## 3. V3-Specific Automation Gaps

### 3.1 FastAPI Integration (New Scripts Needed)

| Proposed Script | Purpose | Priority |
|-----------------|---------|----------|
| `validate_fastapi_schema.py` | Validate OpenAPI schema | **Critical** |
| `check_api_response_types.py` | Validate response models | **Critical** |
| `generate_fastapi_wrapper.py` | Auto-generate FastAPI routes | **High** |
| `test_api_parity.py` | Test library ↔ API parity | **Critical** |
| `benchmark_api_latency.py` | Performance benchmarking | **High** |

### 3.2 React Integration (New Scripts Needed)

| Proposed Script | Purpose | Priority |
|-----------------|---------|----------|
| `validate_react_build.sh` | React build validation | **High** |
| `check_r3f_components.py` | R3F component validation | **Medium** |
| `migrate_plotly_to_r3f.py` | Migrate visualizations | **Medium** |
| `generate_ts_types.py` | Generate TypeScript types from Python | **High** |

### 3.3 Migration Automation (Enhance Existing)

| Script | Enhancement Needed |
|--------|-------------------|
| `validate_migration.py` | Add React/FastAPI migration checks |
| `pre_migration_check.py` | Add V3 prerequisite validation |
| `migrate_module.py` | Support cross-stack migrations |

---

## 4. Documentation Gaps to Fix

### 4.1 automation-catalog.md Updates Needed

The following sections need to be added:

1. **API Validation** (new section)
   - `generate_api_manifest.py`
   - `check_api_signatures.py`
   - `check_api_doc_signatures.py`
   - `validate_stub_exports.py`
   - `create_reexport_stub.py`
   - `update_is456_init.py`

2. **Code Migration** (new section)
   - `migrate_module.py`
   - `pre_migration_check.py`
   - `validate_migration.py`
   - `add_future_annotations.py`

3. **Agent Utilities** (expand existing)
   - `agent_start.sh` (tier 0)
   - `find_automation.py`
   - `collect_diagnostics.py`
   - `agent_mistakes_report.sh`

4. **Documentation Quality** (expand existing)
   - `create_doc.py`
   - `check_doc_similarity.py`
   - `check_doc_metadata.py`
   - `check_duplicate_docs.py`
   - `find_orphan_files.py`
   - `fix_broken_links.py`
   - `consolidate_docs.py`

### 4.2 scripts/index.json Updates

1. Update total_scripts: 128 → 143
2. Add missing scripts to appropriate categories
3. Add V3-specific category for new migration scripts

### 4.3 scripts/README.md Updates

1. Update total count: 128 → 143
2. Add V3 migration section
3. Add API validation section

---

## 5. Implementation Plan

### Phase 1: Document Critical V3 Scripts (This Session)

**Priority 1 - API/Migration Scripts:**
1. Add documentation for API validation scripts
2. Add documentation for migration scripts
3. Update automation-catalog.md with new sections

**Deliverables:**
- [ ] Update automation-catalog.md (+8 scripts)
- [ ] Update scripts/index.json (fix count, add missing)
- [ ] Update scripts/README.md

### Phase 2: Create V3 Automation Scripts (Future Session)

**New scripts to create:**
1. `validate_fastapi_schema.py` - OpenAPI validation
2. `test_api_parity.py` - Library ↔ FastAPI parity testing
3. `generate_ts_types.py` - TypeScript type generation
4. `benchmark_api_latency.py` - API performance benchmarks

### Phase 3: Enhance Existing Scripts (Future)

1. Extend `validate_migration.py` for V3
2. Add V3 checks to `pre_migration_check.py`
3. Update `generate_api_manifest.py` for FastAPI schema

---

## 6. V3 Automation Checklist

Pre-migration checklist for V3:

### Library Readiness
- [ ] All P0 APIs implemented (modify_beam, validate_beam, etc.)
- [ ] API manifest generated and validated
- [ ] Type annotations complete (check_type_annotations.py passes)
- [ ] No circular imports (check_circular_imports.py passes)
- [ ] All API signatures stable (check_api_signatures.py passes)

### Documentation Readiness
- [ ] API reference complete for all public functions
- [ ] automation-catalog.md updated (100% coverage)
- [ ] scripts/index.json accurate (143 scripts)
- [ ] V3 architecture document finalized

### Infrastructure Readiness
- [ ] FastAPI validation scripts created
- [ ] API parity testing framework ready
- [ ] TypeScript type generation working
- [ ] CI pipeline ready for dual-stack testing

---

## 7. Recommendations

### Immediate Actions (This Session)

1. **Update automation-catalog.md** with 10-15 critical undocumented scripts
2. **Fix scripts/index.json** count discrepancy (128 → 143)
3. **Update automation-map.json** with V3-relevant tasks
4. **Create V3 automation tasks** in TASKS.md

### Short-term Actions (Next 2 Sessions)

1. Create `validate_fastapi_schema.py` script
2. Create `test_api_parity.py` script
3. Enhance `generate_api_manifest.py` for FastAPI
4. Document remaining 60+ undocumented scripts

### Long-term Actions (V3 Phase)

1. Create full React build integration
2. Implement TypeScript type generation
3. Build dual-stack CI pipeline
4. Create V3 migration validation suite

---

## References

- [V3 Architecture](ai-workspace-expansion-v3.md)
- [Current automation-catalog.md](../reference/automation-catalog.md)
- [scripts/index.json](../../scripts/index.json)
- [automation-map.json](../../scripts/automation-map.json)
