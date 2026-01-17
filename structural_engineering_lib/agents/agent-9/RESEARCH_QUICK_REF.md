# Agent 9 Research Plan - Quick Reference Card
**⚡ Print/Pin This | 1-Page Essentials**

---

## 🎯 Mission
Research evidence-based governance for sustainable AI-assisted development (3-5 hours, 5-10 actionable tasks)

---

## 📋 14 Research Tasks (Checklist)

### Area 1: Structure & Archive (45 min) 🔴 CRITICAL
- [ ] **RESEARCH-001** - Historical patterns (SESSION_LOG analysis) — 15 min
- [ ] **RESEARCH-002** - File structure assessment (categorize 67 docs) — 15 min
- [ ] **RESEARCH-003** - Archive strategy (time/category/hybrid) — 15 min

### Area 2: External Patterns (45 min) 🔴 HIGH
- [ ] **RESEARCH-004** - High-velocity AI development (Shopify/Stripe/GitLab) — 20 min
- [ ] **RESEARCH-005** - Solo dev compact structures (GitHub analysis) — 15 min
- [ ] **RESEARCH-006** - AI context optimization (format guidelines) — 10 min

### Area 3: Constraints (30 min) 🔴 HIGH
- [ ] **RESEARCH-007** - Governance risk assessment (red lines) — 15 min
- [ ] **RESEARCH-008** - Time budget allocation (80/20 rule) — 10 min
- [ ] **RESEARCH-009** - Decision authority matrix (autonomous/escalate) — 5 min

### Area 4: Metrics (30 min) 🟡 MEDIUM
- [ ] **RESEARCH-010** - Baseline collection (commits/docs/WIP) — 15 min
- [ ] **RESEARCH-011** - Leading indicators (early warnings) — 10 min
- [ ] **RESEARCH-012** - Success targets (SMART goals) — 5 min

### Area 5: Meta (20 min) 🟢 LOW
- [ ] **RESEARCH-013** - Research template (standardize findings) — 10 min
- [ ] **RESEARCH-014** - Finding→Task process (conversion flow) — 10 min

---

## ⏱️ Time Budgets

| Session Type | Duration | Focus |
|--------------|----------|-------|
| **Phase 1** | 2-3 hours | Areas 1, 3, 4 (internal + baselines) |
| **Phase 2** | 1.5-2 hours | Area 2 + meta + roadmap |
| **Quick Win** | 45 min | Top 3 pain points only |

---

## 🚦 Success Criteria

### ✅ Research Complete When:
1. Can answer: "Why 122 commits/day?" (root cause)
2. Can answer: "What archive strategy?" (decision)
3. Can answer: "How much governance?" (limits)
4. Have 5-10 tasks for TASKS.md (actionable)
5. Have baseline metrics (measurable)
6. Time invested <5 hours (efficient)

### 🚩 Abort/Pivot If:
- No insights after 3 hours → ship partial findings
- Stuck >1.5 hours on one task → change approach
- External sources contradictory → focus internal
- >6 hours without deliverables → stop, escalate

---

## 🎁 Deliverables

```
agents/agent-9/research/
├── RESEARCH_FINDINGS_STRUCTURE.md    (Area 1)
├── RESEARCH_FINDINGS_EXTERNAL.md     (Area 2)
├── AGENT_9_CONSTRAINTS.md            (Area 3)
├── METRICS_BASELINE.md               (Area 4)
├── RESEARCH_FINDING_TEMPLATE.md      (Area 5)
├── RESEARCH_TO_TASK_PROCESS.md       (Area 5)
└── AGENT_9_IMPLEMENTATION_ROADMAP.md (Final)
```

---

## 🔑 Key Questions to Answer

1. **Root cause:** What's creating doc sprawl?
2. **Benchmark:** Is 122 commits/day normal?
3. **Strategy:** Time-based or category archive?
4. **Boundaries:** What can Agent 9 change autonomously?
5. **Investment:** How much time for governance?
6. **Measurement:** What metrics matter most?
7. **Format:** What context works for AI agents?
8. **Scale:** Will this work from v0.16 → v1.0?

---

## 🛠️ Quick Start Commands

### Collect Baselines (5 min)
```bash
# Velocity
git log --since="7 days ago" --oneline | wc -l

# Sprawl
find . -name "*.md" -maxdepth 1 | wc -l

# WIP
gh pr list --state open | wc -l
git worktree list | wc -l
```

### Analyze Patterns (10 min)
```bash
# Recent activity
grep "2026-01" docs/SESSION_LOG.md > tmp/recent.txt

# File categories
ls -la . | grep ".md$" | awk '{print $9}' | sort
```

### External Research (30 min)
```bash
# Search targets:
# - "AI agent software development workflow"
# - "high velocity development practices"
# - "solo developer project organization"
# - "GitHub Copilot context best practices"

# Sources: Shopify/Stripe/GitLab/Simon Willison blogs
```

---

## 🎭 Agent 9 Authority

### ✅ CAN (Autonomous)
- Archive docs >7 days old
- Create governance scripts
- Collect metrics, generate reports
- Update agent specs/templates
- Run cleanup/maintenance

### ❌ CANNOT (Escalate)
- Delete canonical docs
- Change release schedule
- Modify code/tests/CI
- Make breaking changes
- Block feature work

---

## 📊 Target Metrics

| Metric | Current | Target | Reduction |
|--------|---------|--------|-----------|
| Commits/day | 122 | 50-75 | 40-60% |
| Active docs | 67+ | <10 | 85% |
| WIP compliance | 0% | 100% | New |
| Archive org | 0% | 100% | New |

---

## 🎯 Prioritized Research Order

**If time-limited, do in this order:**

1. **RESEARCH-002** (15m) → Know what to archive NOW
2. **RESEARCH-003** (15m) → Choose archive strategy
3. **RESEARCH-010** (15m) → Capture baseline metrics
4. **RESEARCH-007** (15m) → Define Agent 9 red lines
5. **RESEARCH-001** (15m) → Understand root causes

**Total: 75 min for critical insights**

Then decide: continue or implement quick wins?

---

## 🚀 3 Execution Modes

### Mode A: Full Plan (3-5 hours, 2 sessions)
Complete all 14 tasks → comprehensive findings → full roadmap

### Mode B: Critical Only (1.5 hours, 1 session)
Do Areas 1, 3, 4 → ship partial → iterate later

### Mode C: Validation (30 min)
Test one hypothesis → document decision → ship

**Recommended:** Start with Mode B, expand to Mode A if valuable

---

## 🔗 Related Documents

- [RESEARCH_PLAN.md](RESEARCH_PLAN.md) - Full specification (810 lines)
- [RESEARCH_PLAN_SUMMARY.md](_archive/RESEARCH_PLAN_SUMMARY.md) - Executive summary (394 lines)
- [agents/agent-9/README.md](README.md) - Agent 9 spec
- [agents/agent-9/WORKFLOWS.md](WORKFLOWS.md) - Operational procedures
- [agents/agent-9/KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md) - Research foundations

---

## 🎓 Anti-Patterns to Avoid

- ❌ Analysis paralysis (researching forever)
- ❌ Perfect over good (ship partial findings)
- ❌ External cargo-culting (internal-first)
- ❌ Documentation for docs sake (action-oriented)
- ❌ Solving non-existent problems (focus pain points)

---

## ✅ Quality Gates

Before marking complete:
- [ ] All critical research tasks attempted (Areas 1-3)
- [ ] 3+ findings per critical area (evidence-based)
- [ ] 5-10 actionable tasks identified (ready for TASKS.md)
- [ ] Baseline metrics documented (measurable)
- [ ] Agent 9 constraints defined (clear boundaries)
- [ ] Time investment <5 hours (efficient)
- [ ] Templates created (reusable)

---

## 📞 When to Escalate

Escalate to human if:
1. **Conflict** with other agent's work
2. **Uncertainty** about authority boundaries
3. **High impact** (10+ files or multiple systems)
4. **Policy change** (modify core principles)
5. **Blocked** >24 hours on decision

**Process:** Document in `ESCALATIONS.md`, add to TASKS.md with "🔴 HUMAN REVIEW"

---

## 💡 Pro Tips

1. **Start internal** - Mine SESSION_LOG before external research
2. **Ship partial** - Don't wait for perfection
3. **Use templates** - Standardize findings format
4. **Time-box strictly** - Set timer for each task
5. **Focus pain** - Address current problems, not hypothetical
6. **Measure first** - Baseline before optimization
7. **Automate early** - Script decisions ASAP

---

**📍 Current Status:** Plan ready, awaiting execution

**🎯 Next Action:** Review plan → Execute Phase 1 (2-3 hours) → Ship findings

**📁 Location:** [agents/agent-9/RESEARCH_PLAN.md](RESEARCH_PLAN.md)

---

**Version:** 1.0.0 | **Created:** 2026-01-10 | **Status:** ✅ Ready
