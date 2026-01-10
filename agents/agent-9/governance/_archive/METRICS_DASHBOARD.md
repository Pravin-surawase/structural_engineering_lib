# Governance Metrics Dashboard

> **Auto-generated** by `scripts/generate_dashboard.sh` (TASK-285)
> **Last updated:**
2026-01-10 16:00:50

> **Purpose:** Track project health metrics, velocity trends, and governance compliance
> **Research:** Based on [METRICS_BASELINE.md](../../research/METRICS_BASELINE.md)

---

## 🎯 Current Snapshot

### Latest Metrics (2026-01-10)

| Category | Metric | Value | Target | Status |
|----------|--------|-------|--------|--------|
| **Velocity** | Commits/day (7d avg) | 62.5 | 50-75 | ✅ |
| | Total commits | 826 | - | ℹ️ |
| **WIP** | Active PRs | 1 | ≤2 | ✅ |
| | Worktrees | 1 | ≤2 | ✅ |
| | Active tasks | 2 | ≤2 | ✅ |
| **Documentation** | Root files | 10 | <10 | ❌ |
| | Archived files | 63 | - | ℹ️ |
| **Quality** | Test coverage | 86% | >85% | ✅ |
| | Ruff errors | 0 | 0 | ✅ |
| | Mypy errors | 0 | 0 | ✅ |
| **Alerts** | Active alerts | 1 | 0 | ⚠️ |

### 🚨 Active Alerts

- ⚠️ Root doc creation rate HIGH: 36 in 7 days (threshold: 6)

---

## 📈 Trends (Last 30 Days)

### Velocity Trends

| Date | Commits/day | Commits (7d) | Total | Trend |
|------|-------------|--------------|-------|-------|
| 2026-01-10 | 62.5 | 438 | 826 | - |

### Documentation Trends

| Date | Root Files | Total Docs | Archived | Status |
|------|------------|------------|----------|--------|
| 2026-01-10 | 10 | 402 | 63 | ✅ |

### Quality Trends

| Date | Coverage | Ruff Errors | Mypy Errors | Status |
|------|----------|-------------|-------------|--------|
| 2026-01-10 | 86% | 0 | 0 | ✅ |

---

## 📊 Analysis

### Velocity
- **Target:** 50-75 commits/day (sustainable pace)
- **Research:** 60 commits/day = team-scale velocity (Shopify: 50-100/day)
- **Alert threshold:** >100 commits/day (burnout risk)

### Documentation
- **Target:** <10 root files (industry standard: Prettier 5, Vitest 2, tRPC 2)
- **Archival:** Automated via `scripts/archive_old_sessions.sh`
- **CI enforcement:** `scripts/check_root_file_count.sh`

### Quality
- **Coverage target:** >85% (current industry standard)
- **Zero tolerance:** Ruff and Mypy errors
- **Tests:** Run `pytest` before pushing

### Leading Indicators
Six metrics with alert thresholds:
1. Root doc creation rate: >2/day for 3+ days
2. Crisis docs: >3 in 7 days
3. Handoff docs: >2 overlapping
4. Completion docs: >5
5. Velocity spike: >100 commits/day
6. PR age: >3 days

---

## 🔗 Related Documentation

- [Metrics Baseline](../../research/METRICS_BASELINE.md) - Initial research
- [Research Findings](../../research/RESEARCH_FINDINGS_EXTERNAL.md) - Industry patterns
- [Implementation Roadmap](../../AGENT_9_IMPLEMENTATION_ROADMAP.md) - Complete plan
- [Governance Session Script](../../scripts/governance_session.sh) - 80/20 rule automation

---

**Automation:** Run `./scripts/generate_dashboard.sh` to update this dashboard
**Frequency:** Daily (automated in governance sessions)
**Version:** 1.0.0 (TASK-285)
