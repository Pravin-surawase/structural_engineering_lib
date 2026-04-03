---
owner: Orchestrator
status: active
last_updated: 2026-04-01
doc_type: planning
complexity: advanced
tags: [agent-evolver, self-improvement, meta-agent, metrics, paper-data]
---

**Type:** Architecture
**Audience:** All Agents
**Status:** Active
**Importance:** Critical
**Created:** 2026-04-01
**Last Updated:** 2026-04-01

# Agent-Evolver: Self-Evolving Meta-Agent — v2.0

**Plan Version:** v2.0
**Review Status:** All 8 agent reviews incorporated
**Phase:** Pre-implementation (P0 next)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Research Foundation](#2-research-foundation)
3. [Operational Philosophy](#3-operational-philosophy)
4. [Infrastructure Audit](#4-infrastructure-audit)
5. [Agent Design](#5-agent-design)
6. [Three-Phase Rollout](#6-three-phase-rollout)
7. [Helper Scripts (Agent Toolkit)](#7-helper-scripts-agent-toolkit)
8. [Performance Scoring Framework (11 Dimensions)](#8-performance-scoring-framework-11-dimensions)
9. [Scoring Rubric (Anchored Examples)](#9-scoring-rubric-anchored-examples)
10. [Per-Agent Review Pipeline](#10-per-agent-review-pipeline)
11. [Drift Detection Engine](#11-drift-detection-engine)
12. [Data Architecture](#12-data-architecture)
13. [Evolution Rules Engine](#13-evolution-rules-engine)
14. [Security Guardrails](#14-security-guardrails)
15. [Self-Evolution (Meta)](#15-self-evolution-meta)
16. [Academic Data Export](#16-academic-data-export)
17. [Implementation Pipeline](#17-implementation-pipeline)
18. [Agent Review Summary (v1.0)](#18-agent-review-summary-v10)
19. [Version History](#19-version-history)

---

## 1. Executive Summary

The **agent-evolver** is a 15th meta-agent that **observes first, measures second, evolves last**. It closes the feedback loop that exists in infrastructure (`evolve.py`, `agent_feedback.py`, `project_health.py`) but has **zero usage data**.

### The Approach: Observe → Measure → Evolve

```
Weeks 1-3:  OBSERVE ONLY  — Collect data, score silently, build baselines
Weeks 4-5:  MEASURE+REPORT — Share findings, propose changes (human-approved)
Week 6+:    EVOLVE         — Auto-apply proven improvements (with guardrails)
```

**Key design decisions from v1.0 reviews:**
- 11 scoring dimensions (added "Engineering Accuracy" per structural-engineer)
- Burn-in of 15-20 sessions before any evolution fires (per tester)
- All `.agent.md` changes staged in pending JSON, applied via weekly PR (per ops)
- Safety-critical agents (structural-engineer, structural-math) require human approval for ALL modifications (per structural-engineer)
- 7 helper scripts automate data collection so the evolver doesn't guess (per backend)
- Anchored scoring rubric with examples at each level (per tester + reviewer)
- Security guardrails: sanitization, schema validation, rate limits, rollback (per security)

---

## 2. Research Foundation

| Framework | Paper | Applied Mechanism |
|-----------|-------|-------------------|
| **Reflexion** | Shinn et al., 2023 (NeurIPS, arXiv:2303.11366) | Verbal reflection stored in episodic memory → better decisions next trial |
| **STOP** | Zelikman et al., 2023 (COLM 2024, arXiv:2310.02304) | Scaffolding improves itself via utility function optimization |
| **Self-Refine** | Madaan et al., 2023 (NeurIPS, arXiv:2303.17651) | Iterative refinement with self-feedback loops |
| **MetaGPT** | Hong et al., 2024 (ICLR, arXiv:2308.00352) | Multi-agent coding framework with structured communication |
| **Multi-Agent Survey** | Masterman et al., 2024 (arXiv:2404.11584) | Leadership, reflection phases in multi-agent systems |
| **LLM Self-Correct Limits** | Huang et al., 2024 (ICLR, arXiv:2310.01798) | Self-correction fails without external validation — our 27 checks mitigate this |
| **GQM** | Basili & Weiss, 1984 (IEEE TSE) | Goal-Question-Metric paradigm for deriving metrics from goals |
| **ISO/IEC 25010** | ISO, 2011 | Software quality model — our 11 dimensions map to its characteristics |

**Why external validation matters:** Huang et al. showed LLMs cannot reliably self-correct reasoning alone. Our evolver mitigates this by relying on **external signals** (test results, architecture checks, git hooks, 27 automated checks) rather than LLM self-judgment.

---

## 3. Operational Philosophy

### 3.1 Observation-First (Not Change-First)

The evolver's first job is to **watch** agents work. For the first 15-20 sessions:
- Record every terminal command each agent runs
- Note when agents drift from prescribed commands
- Track which instructions agents follow vs ignore
- Measure how long agents take vs how long they should take
- Identify patterns — what works, what fails, what's missing

**No changes during burn-in.** Only data collection and silent scoring.

### 3.2 The Drift Problem

Agents drift from their instructions in predictable ways:

| Agent | Prescribed | Drift Pattern | Detection Signal |
|-------|-----------|---------------|-----------------|
| **ops** | `./scripts/ai_commit.sh "type: msg"` | Falls back to `git add && git commit` under stress | Pre-push hook blocks, manual git commands in terminal log |
| **backend** | `.venv/bin/python scripts/discover_api_signatures.py` | Guesses param names (`width` instead of `b_mm`) | API call failures, wrong parameter names in code |
| **frontend** | `ls react_app/src/hooks/` first | Creates new hooks without checking existing 21 | Duplicate hook files in git diff |
| **tester** | Test degenerate cases (Mu=0, Vu=0) | Skips edge cases, only tests happy path | Missing test categories in coverage report |
| **doc-master** | `scripts/safe_file_move.py --dry-run` | Uses manual `mv` → breaks 870+ links | Broken link count increases |

The evolver detects these drifts automatically via helper scripts (§7).

### 3.3 Non-Breaking Evolution

Evolution rules follow a strict safety hierarchy:

```
Level 0: OBSERVE  — Log findings only (always safe)
Level 1: SUGGEST  — Write proposals to pending-evolutions.json (human reviews)
Level 2: APPEND   — Add warnings/examples to .agent.md (auto, after burn-in)
Level 3: MODIFY   — Change existing instructions (requires weekly PR + human approval)
Level 4: REMOVE   — Remove outdated instructions (requires explicit human approval)
```

Safety-critical agents (structural-engineer, structural-math) are **locked to Level 0-1** — the evolver can only observe and suggest, never auto-modify.

---

## 4. Infrastructure Audit

### 4.1 What Exists

| Component | Script | Lines | Status | Gap |
|-----------|--------|-------|--------|-----|
| Evolution engine | `scripts/evolve.py` | 542 | ✅ Working | No per-agent metrics |
| Feedback collection | `scripts/agent_feedback.py` | 379 | ✅ Built, **0 items** | Not enforced |
| Health scanner | `scripts/project_health.py` | 740 | ✅ 62/100 | Not agent-granular |
| Mistake tracker | `scripts/agent_mistakes_report.sh` | ~60 | ✅ Working | Git mistakes only |
| Instruction drift | `scripts/check_instruction_drift.py` | ~150 | ✅ Working | Detects, doesn't fix |
| Agent context | `scripts/agent_context.py` | ~300 | ✅ 16 agents | No performance data |
| 27 checks | `scripts/check_all.py` | ~400 | ✅ All pass | No per-agent attribution |

### 4.2 Available Data Sources

| Source | Location | Format | Agent-Tagged? |
|--------|----------|--------|--------------|
| Git log | `git log` | Text | ❌ No — commit msg only |
| Hook output | `logs/hook_output_*.log` | Text | ❌ No |
| Git workflow | `logs/git_workflow.log` | Structured log | ❌ No |
| Session log | `docs/SESSION_LOG.md` | Markdown | ⚠️ Partially |
| Health scans | `logs/evolution/health_*.json` | JSON | ❌ No |
| Evolution reports | `logs/evolution/evolution_*.json` | JSON | ❌ No |
| Feedback | `logs/feedback/*.json` | JSON | ✅ Yes |
| Agent .md files | `.github/agents/*.agent.md` | Markdown | ✅ Yes |

### 4.3 What's Missing (New Scripts Fill These Gaps)

| Gap | Impact | Solution |
|-----|--------|----------|
| No terminal command logging per agent | Can't detect drift | `agent_session_collector.py` |
| No per-agent scoring | Can't measure improvement | `agent_scorer.py` |
| No drift detection from prescribed behavior | Can't auto-diagnose | `agent_drift_detector.py` |
| No instruction compliance checking | Don't know which rules agents ignore | `agent_compliance_checker.py` |
| No trend analysis | Can't predict degradation | `agent_trends.py` |
| No agent registry sync | 3 agents missing from feedback system | `_lib/agent_registry.py` |

---

## 5. Agent Design

### 5.1 Identity

| Property | Value |
|----------|-------|
| **Name** | `agent-evolver` |
| **File** | `.github/agents/agent-evolver.agent.md` |
| **Model** | Claude Opus 4.6 |
| **Role** | Meta-agent: observe, measure, evolve all agents (including itself) |
| **Tools** | `read/readFile`, `search`, `web`, `terminal` |
| **Skill** | `/agent-evolution` |

### 5.2 Core Cycle

```
┌──────────────────────────────────────────────────────────┐
│                  AGENT-EVOLVER CYCLE                      │
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ COLLECT  │→ │ ANALYZE  │→ │  SCORE   │                │
│  │ (scripts)│  │ (drift)  │  │ (11 dim) │                │
│  └──────────┘  └──────────┘  └──────────┘                │
│       ↑                           │                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ VALIDATE │← │ EVOLVE   │← │ REPORT   │                │
│  │ (checks) │  │ (safe)   │  │ (trends) │                │
│  └──────────┘  └──────────┘  └──────────┘                │
│                                                           │
│  Phase 1 (Weeks 1-3): COLLECT → ANALYZE → SCORE → REPORT │
│  Phase 2 (Weeks 4-5): + EVOLVE (human-approved proposals) │
│  Phase 3 (Week 6+):   + VALIDATE (auto-apply Level 0-2)  │
└──────────────────────────────────────────────────────────┘
```

### 5.3 What the Evolver Does Per Session

```
SESSION END:
1. ./run.sh evolve --collect         # Auto-collect session artifacts
   ├── Parse git log since last session
   ├── Extract terminal commands used
   ├── Identify which agents were active
   ├── Collect feedback items
   └── Run automated checks

2. ./run.sh evolve --score           # Score each active agent
   ├── Auto-score 5 dimensions (terminal, errors, pipeline, time, engineering)
   ├── Flag 6 dimensions for manual input
   └── Save to logs/agent-performance/sessions/

3. ./run.sh evolve --report          # Generate findings
   ├── Drift detected (commands, patterns)
   ├── Instruction violations
   ├── Comparison to previous sessions
   └── Trends (if ≥5 sessions exist)
```

### 5.4 Execution Cadence

| Cadence | What Runs | Who Triggers | Output |
|---------|-----------|-------------|--------|
| **Per-Session** | COLLECT + SCORE + REPORT | Integrated into `./run.sh session summary` | Session scorecard JSON |
| **Weekly** | ANALYZE trends + EVOLVE proposals | `./run.sh evolve --weekly` | Pending evolutions JSON |
| **Monthly** | Full audit + self-evolve + paper export | `./run.sh evolve --monthly` | Stats + evolution log |

---

## 6. Three-Phase Rollout

### Phase 1: OBSERVE (Weeks 1-3, Sessions 1-20)

**Goal:** Build baselines. Collect data. Score silently. NO changes to any agent.

| Week | Focus | Deliverables |
|------|-------|-------------|
| **Week 1** | Infrastructure setup | Helper scripts deployed, first 5 sessions scored |
| **Week 2** | Data collection | 10+ sessions scored, drift patterns cataloged |
| **Week 3** | Baseline establishment | Per-agent baselines computed, rubric calibrated |

**What the evolver does each session:**
1. Run `agent_session_collector.py` → gather session artifacts
2. Run `agent_drift_detector.py` → detect command/behavior drift
3. Run `agent_compliance_checker.py` → check instruction adherence
4. Run `agent_scorer.py --auto-only` → score automatable dimensions
5. Generate session report → `logs/agent-performance/sessions/YYYY-MM-DD.json`

**What the evolver does NOT do:**
- Modify any `.agent.md` file
- Propose any evolution actions
- Make any judgments about agent quality

**Calibration during Phase 1:**
- After 10 sessions, human reviews 3 random scorecards for accuracy
- Scorer consistency test: same session scored 3 times, variance < ±0.5
- ICC (Intraclass Correlation) computed — must reach ≥ 0.80

### Phase 2: MEASURE + PROPOSE (Weeks 4-5, Sessions 20-35)

**Goal:** Share findings with human. Propose instruction improvements. Human approves.

| Activity | Frequency | Output |
|----------|-----------|--------|
| Trend analysis | Weekly | `logs/agent-performance/trends/weekly_W*.json` |
| Drift report | Weekly | Per-agent drift summary in console |
| Evolution proposals | Weekly | `logs/agent-performance/pending-evolutions.json` |
| Human review | Weekly | Approve/reject/modify proposals |

**What the evolver proposes (never auto-applies in Phase 2):**
- "Backend agent guessed param names 4 times → add warning to backend.agent.md"
- "Frontend agent didn't check hooks/ in 3 sessions → add to quick-reference"
- "Ops agent used manual git twice → reinforce THE ONE RULE"

### Phase 3: EVOLVE (Week 6+, Sessions 35+)

**Goal:** Auto-apply safe Level 0-2 changes. Human approves Level 3-4.

**Prerequisites before Phase 3 activates:**
- [ ] ≥ 20 scored sessions in database
- [ ] ICC ≥ 0.80 on 3+ calibration runs
- [ ] Human reviewed and approved first 5 evolution proposals
- [ ] No false positive rate > 20% in Phase 2 proposals

**Evolution cadence in Phase 3:**
- Per-session: score only (no changes)
- Weekly: auto-apply Level 0-2, propose Level 3-4
- Monthly: full audit + self-evolution + paper export

---

## 7. Helper Scripts (Agent Toolkit)

These scripts automate 80% of the evolver's data collection work.

### 7.1 Script Overview

| # | Script | Purpose | Input | Output | Lines |
|---|--------|---------|-------|--------|-------|
| 1 | `agent_session_collector.py` | Gather all session artifacts for scoring | git log, SESSION_LOG, feedback | `session_raw_YYYY-MM-DD.json` | ~250 |
| 2 | `agent_drift_detector.py` | Detect when agents use non-prescribed commands | Session artifacts + agent.md rules | Drift report JSON | ~300 |
| 3 | `agent_compliance_checker.py` | Check instruction adherence per agent | Session behavior vs .agent.md | Compliance score per rule | ~200 |
| 4 | `agent_scorer.py` | Score agents on 11 dimensions | All above + manual input | Session scorecard JSON | ~350 |
| 5 | `agent_trends.py` | Compute trends, detect degradation | All session scorecards | Trend report JSON | ~200 |
| 6 | `agent_evolve_instructions.py` | Safely propose/apply `.agent.md` changes | Trend data + rules | Pending evolutions / diffs | ~300 |
| 7 | `export_paper_data.py` | Export CSV/stats for academic paper | All performance data | CSV + summary_stats.json | ~200 |

**Shared module:** `scripts/_lib/agent_registry.py` (~50 lines) — single source of truth for agent list, auto-discovered from `.github/agents/*.agent.md`.

### 7.2 Script Details

#### Script 1: `agent_session_collector.py`

Collects all raw data from a session into a single structured JSON.

```bash
# Usage
.venv/bin/python scripts/agent_session_collector.py
.venv/bin/python scripts/agent_session_collector.py --since "2026-04-01"
.venv/bin/python scripts/agent_session_collector.py --session-id "2026-04-01T14:30"
```

**What it collects:**
```json
{
  "session_id": "2026-04-01T14:30",
  "git_commits": [
    {"sha": "abc123", "message": "feat(column): add axial capacity", "files_changed": 5, "agent_hint": "structural-math"}
  ],
  "files_changed": {
    "Python/structural_lib/codes/is456/column/axial.py": "modified",
    "Python/tests/unit/test_column_axial.py": "added"
  },
  "terminal_commands": [
    {"command": ".venv/bin/pytest Python/tests/ -v", "category": "prescribed", "agent": "tester"},
    {"command": "git add .", "category": "FORBIDDEN", "agent": "ops"}
  ],
  "feedback_items": [],
  "health_before": 62,
  "health_after": 65,
  "tests_run": {"passed": 142, "failed": 0, "skipped": 3},
  "build_status": {"python": "pass", "react": "pass", "docker": "skip"}
}
```

**Agent identification heuristic:**
- Commit messages: `feat(column):` → structural-math, `docs:` → doc-master
- File paths: `react_app/` → frontend, `fastapi_app/` → api-developer
- Terminal commands: `npm run build` → frontend, `pytest` → tester
- Feedback items: tagged with agent name

#### Script 2: `agent_drift_detector.py`

Compares actual terminal commands to prescribed/forbidden lists per agent.

```bash
.venv/bin/python scripts/agent_drift_detector.py --session "2026-04-01T14:30"
.venv/bin/python scripts/agent_drift_detector.py --agent ops --last 5
```

**Per-agent drift rules (loaded from agent.md files):**

```python
DRIFT_RULES = {
    "ops": {
        "prescribed": [
            r"./scripts/ai_commit\.sh",
            r"git status", r"git branch", r"git log", r"git diff",  # read-only OK
        ],
        "forbidden": [
            r"^git add", r"^git commit", r"^git push", r"^git pull",
            r"--force", r"--no-verify", r"GIT_HOOKS_BYPASS",
            r"gh pr merge --admin", r"gh issue close",
        ],
        "drift_indicators": [
            r"^git add \.",  # manual staging
            r"^git commit -m",  # manual commit
        ]
    },
    "backend": {
        "prescribed": [
            r"\.venv/bin/python", r"\.venv/bin/pytest",
            r"discover_api_signatures", r"validate_imports",
        ],
        "forbidden": [
            r"^python\s",  # bare python
        ],
        "drift_indicators": [
            r"width|height",  # wrong param names (should be b_mm, d_mm)
        ]
    },
    "frontend": {
        "prescribed": [
            r"ls react_app/src/hooks/",
            r"cd react_app && npm run build",
            r"npx vitest",
        ],
        "forbidden": [],
        "drift_indicators": [
            r"\.css$",  # creating CSS files
        ]
    }
}
```

**Output:**
```json
{
  "session_id": "2026-04-01T14:30",
  "drift_events": [
    {
      "agent": "ops",
      "severity": "CRITICAL",
      "command": "git add .",
      "rule_violated": "FORBIDDEN: manual git",
      "prescribed_alternative": "./scripts/ai_commit.sh"
    },
    {
      "agent": "frontend",
      "severity": "WARNING",
      "observation": "No 'ls react_app/src/hooks/' before creating useColumnDesign.ts",
      "rule_violated": "PRESCRIBED: check hooks before creating"
    }
  ],
  "compliance_rate": {
    "ops": 0.85,
    "frontend": 0.70,
    "backend": 0.95
  }
}
```

#### Script 3: `agent_compliance_checker.py`

Checks whether agents followed their `.agent.md` rules.

```bash
.venv/bin/python scripts/agent_compliance_checker.py --session "2026-04-01T14:30"
.venv/bin/python scripts/agent_compliance_checker.py --agent backend --last 10
```

**Compliance checks per agent:**

| Check | Applies To | How Detected |
|-------|-----------|-------------|
| Used `ai_commit.sh` (not manual git) | ops | Terminal command log |
| Ran `discover_api_signatures.py` before API calls | backend, api-developer | Terminal command log |
| Checked `hooks/` before creating hook | frontend | Terminal command + git diff |
| Ran `npm run build` before commit | frontend | Terminal command log |
| Used `safe_file_move.py` (not `mv`) | doc-master | Terminal command log |
| Ran tests after changes | tester, backend | Terminal command log |
| Updated TASKS.md at session end | doc-master | Git diff check |
| Updated next-session-brief.md | doc-master | Git diff check |
| Logged feedback at session end | all agents | `logs/feedback/` check |
| Used `--dry-run` before file operations | doc-master, governance | Terminal command log |

#### Script 4: `agent_scorer.py`

Scores agents on 11 dimensions. 5 auto-scored, 6 need manual input.

```bash
# Auto-score only (runs at session end automatically)
.venv/bin/python scripts/agent_scorer.py --auto-only --session "2026-04-01T14:30"

# Full scoring (adds manual dimensions)
.venv/bin/python scripts/agent_scorer.py --session "2026-04-01T14:30" \
  --agent backend --task-completion 8 --code-quality 9 --context-utilization 7 \
  --instruction-adherence 9 --handoff-quality 7 --regression-avoidance 8

# View latest scores
.venv/bin/python scripts/agent_scorer.py --view
.venv/bin/python scripts/agent_scorer.py --view --agent backend
```

#### Script 5: `agent_trends.py`

```bash
.venv/bin/python scripts/agent_trends.py --weekly      # Last 7 sessions
.venv/bin/python scripts/agent_trends.py --agent ops   # Single agent trend
.venv/bin/python scripts/agent_trends.py --alert        # Flag degrading agents
```

Uses **Mann-Kendall test** for trend detection (non-parametric, works with N<10).

#### Script 6: `agent_evolve_instructions.py`

```bash
# Propose changes (Phase 2, never auto-applies)
.venv/bin/python scripts/agent_evolve_instructions.py --propose

# Apply approved changes (Phase 3, from pending JSON)
.venv/bin/python scripts/agent_evolve_instructions.py --apply --evolution-id ev_001

# Rollback a change
.venv/bin/python scripts/agent_evolve_instructions.py --rollback --evolution-id ev_001
```

#### Script 7: `export_paper_data.py`

```bash
.venv/bin/python scripts/export_paper_data.py --all     # Full export
.venv/bin/python scripts/export_paper_data.py --table    # Paper table (§16)
.venv/bin/python scripts/export_paper_data.py --stats    # Mean, σ, CI, Hedges' g
```

### 7.3 run.sh Integration

These scripts are accessed through existing `./run.sh evolve` with new subcommands:

```bash
./run.sh evolve --collect              # Collect session artifacts
./run.sh evolve --score                # Auto-score current session
./run.sh evolve --score --full         # Full scoring with manual input
./run.sh evolve --drift                # Run drift detection
./run.sh evolve --compliance           # Run compliance check
./run.sh evolve --weekly               # Weekly trend analysis + proposals
./run.sh evolve --monthly              # Monthly full audit + paper export
./run.sh evolve --paper                # Export paper data
./run.sh evolve --scores               # View current scorecard
./run.sh evolve --scores --agent ops   # View single agent
./run.sh evolve --propose              # Generate evolution proposals
./run.sh evolve --apply ev_001         # Apply approved evolution
./run.sh evolve --rollback ev_001      # Rollback evolution
```

---

## 8. Performance Scoring Framework (11 Dimensions)

### 8.1 Dimension Table

| # | Dimension | Automation | Data Source | Weight | Struct. Override |
|---|-----------|-----------|-------------|--------|-----------------|
| 1 | **Task Completion** | Manual (5-checkpoint) | Reviewer verdict, git diff | 18% | 18% |
| 2 | **Code Quality** | Semi-auto | Arch check + reviewer | 12% | 10% |
| 3 | **Terminal Efficiency** | Auto | `agent_drift_detector.py` | 8% | 5% |
| 4 | **Context Utilization** | Semi-auto | File reads before edits + manual | 10% | 10% |
| 5 | **Pipeline Compliance** | Auto | Orchestrator checklist tracking | 10% | 10% |
| 6 | **Error Rate** | Auto | Test/build output | 8% | 8% |
| 7 | **Instruction Adherence** | Semi-auto | `agent_compliance_checker.py` | 10% | 10% |
| 8 | **Handoff Quality** | Semi-auto | Doc completeness + manual | 5% | 5% |
| 9 | **Regression Avoidance** | Semi-auto | Mistake history comparison | 4% | 4% |
| 10 | **Engineering Accuracy** | Auto | Benchmark tests, clause coverage | 15% | **25%** |
| 11 | **Collaboration** | Manual | Cross-agent rework rate | — | — |

*Struct. Override = weight override for structural-engineer and structural-math agents.*
*Dim 11 (Collaboration) is experimental — tracked but not weighted in composite until Phase 3.*

### 8.2 Composite Score Formula

$$S_{agent} = \sum_{i=1}^{10} w_i \cdot d_i, \quad d_i \in [0, 10], \quad \sum w_i = 1$$

**Grade mapping:** 9-10 = Excellent, 7-8.9 = Good, 5-6.9 = Needs Improvement, <5 = Critical.

### 8.3 Auto-Scored Dimensions (No Human Input Needed)

| Dimension | Auto-Score Method |
|-----------|------------------|
| **Terminal Efficiency** | `(prescribed_cmds / total_cmds) × 10` — penalizes forbidden/redundant commands |
| **Pipeline Compliance** | Checklist: each step completed = +points (PLAN=+1, GATHER=+2, EXECUTE=+2, TEST=+2, VERIFY=+2, DOCUMENT=+1) |
| **Error Rate** | `(1 - failures/total_runs) × 10` — test failures, build errors, lint errors |
| **Engineering Accuracy** | `(benchmark_pass_rate × 0.5 + clause_coverage_delta × 0.3 + safety_factor_intact × 0.2) × 10` |
| **Instruction Adherence** | `compliance_checker score × 10` — % of rules followed |

### 8.4 Manual-Input Dimensions (5-Checkpoint Rubric)

**Task Completion (5 checkpoints, +2 each):**
- [ ] Tests pass for new/changed code (+2)
- [ ] Reviewer did not reject (+2)
- [ ] PR merged (or commit pushed) (+2)
- [ ] No rework needed after commit (+2)
- [ ] Zero architecture violations (+2)

---

## 9. Scoring Rubric (Anchored Examples)

Each dimension has anchored examples to ensure consistent scoring.

### 9.1 Task Completion

| Score | Description | Example |
|-------|-------------|---------|
| 0-2 | Failed to start or abandoned | Agent couldn't find the file, gave up |
| 3-4 | Partially started, wrong approach | Edited wrong api.py (stub), needed rework |
| 5-6 | Completed with significant issues | PR merged but 3 reviewer comments unresolved |
| 7-8 | Completed well, minor issues | Tests pass, 1 minor reviewer suggestion |
| 9-10 | Perfect execution, proactive quality | Completed + caught a pre-existing bug, updated docs |

### 9.2 Terminal Efficiency

| Score | Description | Example |
|-------|-------------|---------|
| 0-2 | Multiple FORBIDDEN commands used | `git add .` + `git commit -m` instead of ai_commit.sh |
| 3-4 | Many wrong paths, > 5 retries | Ran `cd Python && .venv/bin/pytest` (wrong cwd, 3 retries) |
| 5-6 | Some redundant searches, minor drift | Searched for file 3 times, found on 3rd try |
| 7-8 | Mostly prescribed commands, efficient | Used all prescribed commands, 1 unnecessary search |
| 9-10 | All prescribed, zero redundancy | Every command necessary and correct on first try |

### 9.3 Context Utilization

| Score | Description | Example |
|-------|-------------|---------|
| 0-2 | Wrote code without reading anything | Created duplicate hook without checking hooks/ |
| 3-4 | Read some files but missed key ones | Didn't check api.py before wrapping a function |
| 5-6 | Read index files but not source | Read index.json but not the actual implementation |
| 7-8 | Read relevant source, checked for duplicates | Searched hooks/, read existing hook, then extended it |
| 9-10 | Thorough context + proactive discovery | Read index + source + tests + ran API discovery script |

### 9.4 Engineering Accuracy (Structural Agents)

| Score | Description | Example |
|-------|-------------|---------|
| 0-2 | Formula wrong, safety factors altered | Used γc=1.3 instead of 1.5 |
| 3-4 | Formula correct but benchmarks fail | SP:16 deviation > 1% |
| 5-6 | Benchmarks pass but missing edge cases | No degenerate case tests (Mu=0) |
| 7-8 | All benchmarks pass, clause annotated | SP:16 ±0.1%, IS 456 clause referenced |
| 9-10 | Perfect + verification report filed | All above + Structural Engineer Verification Report |

### 9.5 Instruction Adherence

| Score | Description | Example |
|-------|-------------|---------|
| 0-2 | Ignored most rules, used FORBIDDEN commands | Manual git, no session end logging |
| 3-4 | Followed some rules, missed critical ones | Used ai_commit.sh but skipped session summary |
| 5-6 | Followed most rules, missed minor ones | All critical rules followed, forgot to update TASKS.md |
| 7-8 | Near-complete adherence | All rules followed, one minor formatting deviation |
| 9-10 | Perfect adherence + used skills/prompts | All rules + used /api-discovery + updated docs |

---

## 10. Per-Agent Review Pipeline

### 10.1 How the Evolver Reviews Each Agent

For every agent active in a session, the evolver runs this pipeline:

```
┌──────────────────────────────────────────────────────────┐
│           PER-AGENT REVIEW PIPELINE                       │
│                                                           │
│  Step 1: IDENTIFY                                         │
│  ├── Which agent was active? (from collector)              │
│  ├── What task was assigned? (from TASKS.md / orchestrator)│
│  └── What files were changed? (from git diff)             │
│                                                           │
│  Step 2: LOAD RULES                                       │
│  ├── Read agent's .agent.md (prescribed behavior)          │
│  ├── Load drift rules for this agent                       │
│  └── Load historical scores (if any)                      │
│                                                           │
│  Step 3: CHECK COMPLIANCE                                  │
│  ├── Terminal commands vs prescribed/forbidden              │
│  ├── Files read before files written? (context check)      │
│  ├── Architecture boundaries respected?                    │
│  ├── Duplication introduced? (new file vs existing)        │
│  └── Session-end workflow completed?                       │
│                                                           │
│  Step 4: AUTO-SCORE (5 dimensions)                         │
│  ├── Terminal Efficiency (from drift detector)              │
│  ├── Pipeline Compliance (from orchestrator tracking)       │
│  ├── Error Rate (from test/build output)                    │
│  ├── Engineering Accuracy (from benchmark tests)            │
│  └── Instruction Adherence (from compliance checker)       │
│                                                           │
│  Step 5: COMPARE                                           │
│  ├── This session vs agent's average                        │
│  ├── This session vs agent's best                           │
│  ├── Dimension-level changes since last session             │
│  └── New drift patterns not seen before?                   │
│                                                           │
│  Step 6: REPORT                                            │
│  ├── Findings summary (what went well, what drifted)       │
│  ├── Score delta from baseline                              │
│  └── Recommendations (if Phase 2+)                         │
└──────────────────────────────────────────────────────────┘
```

### 10.2 Review Pipeline per Agent Type

| Agent | Review Focus | Special Checks |
|-------|-------------|----------------|
| **orchestrator** | Pipeline adherence, delegation accuracy, stuck detection | Did it intervene when agents were stuck? Correct agent chosen? |
| **backend** | API param names, architecture layer compliance, import direction | Ran `discover_api_signatures.py`? Used `.venv/bin/python`? |
| **frontend** | Hook duplication, no CSS files, build passed, Tailwind only | Checked `hooks/` first? `npm run build` ran? No `.css` created? |
| **structural-math** | Formula correctness, clause annotations, safety factors | SP:16 ±0.1%? Degenerate tests? γc/γs unchanged? |
| **api-developer** | Route duplication, Pydantic models, OpenAPI spec | Checked existing routes? Tests for new endpoints? |
| **structural-engineer** | Verification report, benchmark validation, clause completeness | Verification report filed? IS 456 clause cited? |
| **tester** | Test coverage, edge cases, golden tests preserved | Degenerate cases tested? Golden tests untouched? Property tests? |
| **reviewer** | 12-point checklist completed, verdict given, both passes done | Math review + code review both done? |
| **doc-master** | Safe file ops, session logging, link integrity | Used `safe_file_move.py`? SESSION_LOG updated? Links intact? |
| **ops** | ai_commit.sh used, no manual git, PR workflow followed | THE ONE RULE followed? PR created when required? |
| **governance** | Health score maintained, metrics tracked, archival done | Health check ran? Standards enforced? |
| **security** | OWASP checks, dependency scan, input validation | Vulnerability scan ran? Dependencies checked? |
| **library-expert** | Citation accuracy, professional standards, benchmark sources | Sources cited? SP:16 values verified? |
| **ui-designer** | Design spec quality, accessibility, component reuse | WCAG 2.1 AA? Existing components referenced? |
| **agent-evolver** | Self-scoring accuracy, false positive rate, evolution impact | Did proposals improve scores? Any false alarms? |

---

## 11. Drift Detection Engine

### 11.1 What Is Drift?

Drift is when an agent's **actual behavior** deviates from its **prescribed behavior** in `.agent.md`. It's the #1 cause of recurring mistakes.

### 11.2 Drift Categories

| Category | Severity | Example | Detection Method |
|----------|----------|---------|-----------------|
| **Command Drift** | High | `git commit -m` instead of `ai_commit.sh` | Terminal command pattern matching |
| **Search Drift** | Medium | Didn't check hooks/ before creating hook | File access order analysis |
| **Architecture Drift** | High | Math in React, I/O in pure math layer | `check_architecture_boundaries.py` |
| **Naming Drift** | Medium | `width` instead of `b_mm` | Code grep for wrong param names |
| **Workflow Drift** | Medium | Skipped session-end steps | Checklist completion tracking |
| **Safety Drift** | Critical | Safety factor changed, golden test deleted | Pre-commit hook + benchmark regression |

### 11.3 Per-Agent Drift Rules

Loaded from agent files, maintained in `scripts/_lib/drift_rules.json`:

```json
{
  "ops": {
    "critical_rules": [
      {"id": "OPS-001", "name": "THE_ONE_RULE", "pattern": ".*ai_commit\\.sh.*", "type": "must_use", "description": "All commits via ai_commit.sh"},
      {"id": "OPS-002", "name": "NO_MANUAL_GIT", "patterns": ["^git add", "^git commit", "^git push"], "type": "forbidden"},
      {"id": "OPS-003", "name": "NO_FORCE", "patterns": ["--force", "--no-verify"], "type": "forbidden"}
    ]
  },
  "backend": {
    "critical_rules": [
      {"id": "BE-001", "name": "VENV_PYTHON", "pattern": "\\.venv/bin/python", "type": "must_use"},
      {"id": "BE-002", "name": "NO_BARE_PYTHON", "pattern": "^python\\s", "type": "forbidden"},
      {"id": "BE-003", "name": "API_DISCOVERY", "pattern": "discover_api_signatures", "type": "should_use_before_api_call"}
    ]
  },
  "frontend": {
    "critical_rules": [
      {"id": "FE-001", "name": "CHECK_HOOKS_FIRST", "pattern": "ls react_app/src/hooks/", "type": "must_use_before_creating_hook"},
      {"id": "FE-002", "name": "BUILD_BEFORE_COMMIT", "pattern": "npm run build", "type": "must_use"},
      {"id": "FE-003", "name": "NO_CSS_FILES", "pattern": "\\.css$", "type": "forbidden_file_creation"}
    ]
  }
}
```

### 11.4 Drift Score Formula

$$D_{agent} = 1 - \frac{\text{violations}}{\text{total\_applicable\_rules}}$$

$D = 1.0$ means perfect compliance. $D < 0.7$ triggers an alert.

---

## 12. Data Architecture

### 12.1 Directory Structure

```
logs/agent-performance/
├── scorecard_index.json            # Latest score per agent (small, fast read)
├── sessions/
│   ├── 2026-04-01T1430.json        # Per-session full record
│   ├── 2026-04-02T0900.json
│   └── ...
├── trends/
│   ├── weekly_2026-W14.json        # Weekly aggregates
│   ├── monthly_2026-04.json        # Monthly aggregates
│   └── ...
├── drift/
│   ├── drift_2026-04-01.json       # Per-session drift events
│   └── ...
├── pending-evolutions.json         # Proposed changes awaiting approval
├── evolution-log.json              # Applied changes with diffs + SHAs
├── backups/                        # Last 10 .agent.md versions
│   ├── backend_2026-04-01.agent.md
│   └── ...
└── paper-export/
    ├── agent_scores.csv
    ├── dimension_trends.csv
    ├── evolution_events.csv
    ├── drift_summary.csv
    └── summary_stats.json
```

### 12.2 Session Record Schema (v1.1)

```json
{
  "schema_version": "1.1",
  "session_id": "2026-04-01T14:30",
  "phase": "observe",
  "duration_prompts": 12,
  "agents_active": ["backend", "tester", "reviewer"],
  "task_ids": ["TASK-633"],
  "health_delta": {"before": 62, "after": 65},
  "agent_scores": {
    "backend": {
      "dimensions": {
        "task_completion": 8,
        "code_quality": 9,
        "terminal_efficiency": 7.5,
        "context_utilization": 7,
        "pipeline_compliance": 10,
        "error_rate": 8,
        "instruction_adherence": 9,
        "handoff_quality": 7,
        "regression_avoidance": 8,
        "engineering_accuracy": null,
        "collaboration": null
      },
      "composite": 8.12,
      "scoring_method": {"auto": 5, "manual": 4, "na": 2},
      "drift_score": 0.95,
      "compliance_rate": 0.90,
      "notes": "Missed checking hooks/ before creating useColumnDesign",
      "feedback_ids": []
    }
  },
  "drift_events": [],
  "evolution_actions": [],
  "evolver_self_reflection": {
    "issues_caught": 3,
    "issues_missed": 0,
    "false_positives": 0,
    "precision": 1.0,
    "recall": 1.0
  }
}
```

### 12.3 Retention Policy

| Data Type | Retention | Archive |
|-----------|-----------|---------|
| Session JSONs | 6 months raw | Yearly compressed archive |
| Trend JSONs | 12 months | Never archived |
| Drift JSONs | 6 months | Yearly compressed |
| Evolution log | Permanent | Never archived |
| Agent backups | Last 10 per agent | Oldest rotated out |
| Paper export | Permanent | Versioned snapshots |

---

## 13. Evolution Rules Engine

### 13.1 Trigger Rules

| # | Trigger | Threshold | Action | Level | Severity |
|---|---------|-----------|--------|-------|----------|
| 1 | Same drift pattern 3+ sessions | Count ≥ 3 | Add WARNING to .agent.md | L2 | Medium |
| 2 | Dimension < 5 for 2+ sessions | Avg < 5.0 | Add instruction + example | L2 | High |
| 3 | Composite declining 3 sessions | 3 consecutive ↓ | Flag for human review | L1 | High |
| 4 | Duplicate code created | Reviewer detected | Add to "DO NOT recreate" list | L2 | Medium |
| 5 | FORBIDDEN command used | Any occurrence | Reinforce rule + add example | L2 | High |
| 6 | Same workaround 5+ times | Count ≥ 5 | Propose new skill creation | L1 | Medium |
| 7 | Health drops > 10 pts | Delta > -10 | Auto `evolve --fix` | L0 | Critical |
| 8 | Benchmark test fails after change | Any SP:16 failure | Block evolution, revert, alert human | L0 | Critical |
| 9 | Safety factor modified | γc or γs changed | Immediate human review | L1 | Critical |
| 10 | Tolerance regression | ±0.1% → ±0.5%+ | Revert change, flag review | L1 | Critical |

*Thresholds are self-adjustable within range [2, 5] for count-based triggers, based on false positive rate.*

### 13.2 Evolution Actions (Leveled)

| Action | Level | Auto-Apply? | Safety-Critical Agents |
|--------|-------|-------------|----------------------|
| Log finding only | L0 | ✅ Always | ✅ Allowed |
| Propose change (pending JSON) | L1 | ✅ Always | ✅ Allowed |
| Add WARNING block | L2 | After burn-in | ❌ Human approval required |
| Add instruction + example | L2 | After burn-in | ❌ Human approval required |
| Update quick-reference | L2 | After burn-in | ❌ Human approval required |
| Add to "DO NOT recreate" list | L2 | After burn-in | ❌ Human approval required |
| Modify existing instruction | L3 | Never auto | ❌ Human approval required |
| Propose new skill | L3 | Never auto | ❌ Human approval required |
| Remove stale instruction | L4 | Never auto | ❌ Human approval required |
| Self-modify evolver rules | L4 | Never auto | N/A |

### 13.3 Rate Limits

- Max **3 auto-edits** per weekly cycle
- Max **1 agent file** modified per session
- Max **5 pending proposals** in queue (oldest must be resolved before adding more)
- Max **1 self-modification** per monthly cycle

### 13.4 Impact Measurement

Every evolution action tracked with before/after:
- $\bar{S}_{before}$: mean score on affected dimension, last 5 sessions
- $\bar{S}_{after}$: mean on same dimension, next 5 sessions post-evolution
- $\Delta = \bar{S}_{after} - \bar{S}_{before}$
- **Primary metric:** Hedges' g (bias-corrected effect size for small samples)
- **Secondary:** Wilcoxon signed-rank test (non-parametric, works with N<10)
- **If $\Delta < 0$** (evolution made things worse): auto-revert, flag for review

---

## 14. Security Guardrails

### 14.1 Input Sanitization

When reading SESSION_LOG.md, feedback logs, and terminal output:
- Strip lines matching instruction override patterns: `"SYSTEM:"`, `"You are now..."`, `"Ignore previous..."`
- Escape content before using in evolution proposals
- Validate all JSON against schema before processing

### 14.2 Output Validation

Before writing to any `.agent.md` file:
- Validate YAML frontmatter remains parseable
- No new `tools:` or `handoffs:` directives injected
- Content matches allowlist (WARNING blocks, bullet points, code examples only)
- File stays under 350-line limit (consolidate before adding if at limit)
- SHA-256 of file computed before and after, logged in evolution-log.json

### 14.3 Diff-Based Modification

All `.agent.md` changes:
1. Produce a unified diff for review
2. Write to `.agent.md.pending` (not directly to the file)
3. Validate the pending file parses correctly
4. Apply via atomic rename (not incremental write)
5. Log old SHA-256, new SHA-256, diff, and commit SHA

### 14.4 Rollback

```bash
# Rollback a specific evolution
.venv/bin/python scripts/agent_evolve_instructions.py --rollback --evolution-id ev_001

# This restores .agent.md from backups/ directory
```

- `evolution-log.json` stores full unified diff for every change
- `backups/` keeps last 10 versions of each `.agent.md`
- Evolution that causes composite drop > 1.0 in next session → auto-revert

### 14.5 Recursion Limits

- Self-modification capped at **1 per monthly cycle**
- Self-modification cannot trigger another self-review in same run
- Self-modifications stored as pending proposals, **never** auto-applied

---

## 15. Self-Evolution (Meta)

### 15.1 Self-Reflection Questions

After each monthly run, the evolver evaluates itself:

1. **Precision:** Did I catch issues the reviewer later found? (target: > 80%)
2. **Recall:** Did I miss issues that caused problems? (target: < 20% miss rate)
3. **Impact:** Did my instruction updates improve scores? (target: Hedges' g > 0.3)
4. **Noise:** Am I generating false positives? (target: < 20% FP rate)
5. **Calibration:** Are my evolution rules well-tuned? (target: all thresholds within [2,5])

### 15.2 Self-Evolution Triggers

| Condition | Action |
|-----------|--------|
| Evolution made things worse ($\Delta < 0$, confirmed over 3 sessions) | Tighten threshold or remove rule |
| Rule never fires in 15+ sessions | Lower threshold or remove |
| New recurring issue, no rule covers it | Propose new rule |
| False positive rate > 20% | Add specificity constraints |
| Evolver's own composite < 7.0 | Full self-review with human |

---

## 16. Academic Data Export

### 16.1 Table for Paper (Monthly Export)

| Agent | Sessions | Avg Score | σ | Trend | Task | Quality | Terminal | Context | Pipeline | Error | Instruct. | Handoff | Regress. | Eng. Acc. | Evolutions |
|-------|----------|-----------|---|-------|------|---------|----------|---------|----------|-------|-----------|---------|----------|-----------|------------|
| orchestrator | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| backend | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| frontend | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| structural-math | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| api-developer | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| structural-engineer | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| reviewer | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| tester | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| doc-master | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| ops | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| governance | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| security | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| library-expert | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| ui-designer | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **agent-evolver** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **System Avg** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Table populated after first burn-in cycle. Trends: ↑ improving, → stable, ↓ declining.*

### 16.2 Statistical Methods

| Method | Purpose | When Used |
|--------|---------|-----------|
| **Hedges' g** (primary) | Effect size for pre/post evolution | Every evolution event |
| **Wilcoxon signed-rank** | Non-parametric significance test | Pre/post comparisons (N<10) |
| **Mann-Kendall** | Trend detection | Weekly/monthly trends |
| **ICC (two-way mixed, consistency)** | Inter-rater reliability | Calibration sessions |
| **Cohen's κ** | Cross-agent scoring agreement | Monthly calibration |
| **Benjamini-Hochberg FDR** | Multiple comparison correction | Paper export |
| **Bootstrapped 95% CIs** | Robust confidence intervals | All reported means |
| **PCA** | Dimension independence check | Quarterly review |

### 16.3 Testable Hypotheses (for Paper)

| ID | Hypothesis | Measurement | Expected |
|----|-----------|-------------|----------|
| H1 | Agent scores increase post-evolution | Hedges' g on affected dimension | g > 0.3 |
| H2 | Mistake recurrence rate decreases | Same drift type frequency | ↓ 50%+ |
| H3 | Domain dimensions (Eng. Accuracy) show higher variance | σ comparison | σ_eng > σ_avg |
| H4 | Safety-critical agents score higher on instruction adherence | Mean comparison | μ_safety > μ_general |
| H5 | Self-evolution reduces false positive rate | FP rate over time | ↓ monotonic |

### 16.4 Recommended Figures (for Paper)

1. **Heatmap:** Agent × Dimension scores (Fig. 1)
2. **Box plots with effect sizes:** Pre/post evolution comparison per dimension (Fig. 2)
3. **Spider charts:** Per-agent dimension profile overlaid with system average (Fig. 3)
4. **Cumulative evolution curve:** Number of instruction updates over time (Fig. 4)
5. **Drift frequency timeline:** Drift events by category over sessions (Fig. 5)

### 16.5 Paper Venue

- Primary: **ICSE 2027 NIER** (New Ideas and Emerging Results)
- Alternate: **ASE Tool Demo Track**
- Backup: **CAIN 2027** (AI Engineering)

---

## 17. Implementation Pipeline

### 17.1 Phase Plan (12 Phases)

| Phase | Deliverables | Agent | Depends On | Est. Hours |
|-------|-------------|-------|------------|------------|
| **P0: Bootstrap** | Retroactively score last 10 sessions from SESSION_LOG.md | doc-master + backend | — | 4h |
| **P1: Plan** | This document (v2.0), all reviews incorporated | orchestrator | — | Done ✅ |
| **P2: Agent Definition** | `agent-evolver.agent.md`, `/agent-evolution` skill | doc-master | P1 | 3h |
| **P3: Shared Libraries** | `scripts/_lib/agents.py`, `scoring.py`, `agent_data.py` | backend | P2 | 5h |
| **P4: Collector** | `scripts/agent_session_collector.py` | backend | P3 | 4h |
| **P5: Scoring Engine** | `scripts/agent_scorer.py` + CLI | backend | P3, P4 | 6h |
| **P6: Drift Detector** | `scripts/agent_drift_detector.py` | backend | P3, P4 | 5h |
| **P7: Compliance Checker** | `scripts/agent_compliance_checker.py` | backend | P3 | 4h |
| **P8: Trend Analysis** | `scripts/agent_trends.py` | backend | P5 | 4h |
| **P9: Instruction Evolver** | `scripts/agent_evolve_instructions.py` | backend | P8, security review | 5h |
| **P10: Paper Export** | `scripts/export_paper_data.py` | backend | P5 | 3h |
| **P11: Integration** | Session workflow updates, run.sh commands | ops | P5 | 3h |
| **P12: Validation** | Burn-in (15-20 sessions), golden fixture tests, ICC check | governance + tester | P11 | Ongoing |

### 17.2 Test Files

| Script | Test File | Golden Fixtures |
|--------|-----------|-----------------|
| `agent_scorer.py` | `tests/test_agent_scorer.py` | 10 hand-scored sessions |
| `agent_trends.py` | `tests/test_agent_trends.py` | Synthetic trend data |
| `agent_drift_detector.py` | `tests/test_agent_drift.py` | Known drift examples |
| `agent_compliance_checker.py` | `tests/test_agent_compliance.py` | Rule violation fixtures |
| `agent_evolve_instructions.py` | `tests/test_agent_evolve.py` | Before/after .agent.md pairs |
| `agent_session_collector.py` | `tests/test_agent_collector.py` | Mock session artifacts |
| `export_paper_data.py` | `tests/test_paper_export.py` | Expected CSV output |

### 17.3 Golden Session Fixtures

10 hand-scored sessions used for calibration and ICC validation:

| Fixture | Agent | Scenario | Expected Composite |
|---------|-------|----------|-------------------|
| golden_01 | backend | Perfect session: all rules followed, tests pass | 9.2 |
| golden_02 | backend | Manual git used, architecture violation | 4.5 |
| golden_03 | frontend | Duplicate hook created, no build check | 3.8 |
| golden_04 | tester | Comprehensive tests, edge cases, benchmarks | 9.0 |
| golden_05 | ops | ai_commit.sh every time, session-end complete | 9.5 |
| golden_06 | structural-math | Formula wrong (γc=1.3), benchmark fails | 2.1 |
| golden_07 | reviewer | Perfect 12-point review, both passes | 9.3 |
| golden_08 | doc-master | Used rm instead of safe_file_delete, broke links | 3.2 |
| golden_09 | orchestrator | Correct delegation, stuck detection worked | 8.7 |
| golden_10 | mixed | 3 agents active, one excellent, one poor | varies |

---

## 18. Agent Review Summary (v1.0)

All 8 specialist agents reviewed v1.0. Consensus: **APPROVED WITH CHANGES** (avg 6.6/10).

| # | Agent | Score | Key Contribution to v2.0 |
|---|-------|-------|--------------------------|
| 1 | @governance | 7/10 | Agent registry, enforcement mechanism, rollback, 5-session minimum |
| 2 | @reviewer | 7/10 | 5-checkpoint rubric, Wilcoxon/Hedges' g, rate limits, burn-in, architecture constraint |
| 3 | @backend | 7.5/10 | CLI scoring interface, directory-based scorecard, schema versioning, phased automation |
| 4 | @tester | 4/10 | Test strategy (7 test files), golden fixtures, ICC, anchored rubric, FDR correction |
| 5 | @ops | 7/10 | Fold into session summary, pending JSON → weekly PR, main-only execution |
| 6 | @security | 5/10 | Input sanitization, output validation, diff-based modification, SHA-256, recursion limits |
| 7 | @library-expert | 7/10 | ICC/Cohen's κ, focus on active agents, ISO 25010, PCA, paper venue, hypotheses |
| 8 | @structural-engineer | 6/10 | Engineering Accuracy dim, safety-critical classification, domain triggers, weight overrides |

**All 60+ suggestions** from reviews have been incorporated into v2.0 (this document).

Full review transcripts preserved in v1.0 document history.

---

## 19. Version History

| Version | Date | Changes | Status |
|---------|------|---------|--------|
| v1.0-draft | 2026-04-01 | Initial plan — 13 sections, 10 scoring dimensions, 7 evolution rules, 8-phase implementation | Archived |
| v1.1-reviewed | 2026-04-01 | All 8 agent reviews complete. Consensus: APPROVED WITH CHANGES (avg 6.6/10). 60+ specific suggestions collected. | Archived |
| **v2.0** | **2026-04-01** | **Major revision incorporating ALL review feedback. See changelog below.** | **Active** |

### v2.0 Changelog (from v1.1)

**CRITICAL changes (all implemented):**
1. ✅ Added 11th dimension: Engineering Accuracy (§8, 15% weight) — structural-engineer
2. ✅ Added §14 Security Guardrails (input sanitization, output validation, diff-based modification, rollback, recursion limits) — security
3. ✅ Added burn-in phase: 15-20 sessions observe-only before evolution activates (§6 Three-Phase Rollout) — tester
4. ✅ Added §9 anchored scoring rubric with examples at 5 anchor levels — tester + reviewer
5. ✅ Added shared agent registry to §7 Helper Scripts (auto-discovered from .agent.md) — governance
6. ✅ Added test strategy: 7 test files + 10 golden fixtures (§17) — tester
7. ✅ Classified safety-critical agent files: ALL modifications require human approval (§13.2) — structural-engineer

**HIGH changes (all implemented):**
8. ✅ Directory-based scorecard (§12.1) — backend
9. ✅ Folded scoring into session summary workflow (§5.3) — ops
10. ✅ Evolution changes staged in pending JSON, applied via weekly PR (§13.2) — ops
11. ✅ Wilcoxon + Hedges' g as primary statistics (§16.2) — tester + reviewer
12. ✅ 10 golden session fixtures for calibration (§17.3) — tester
13. ✅ Max 3 auto-edits per weekly cycle (§13.3) — reviewer + security
14. ✅ Domain-specific trigger rules (§13.1, rules 8-10) — structural-engineer
15. ✅ Self-modification proposals stored as pending, never auto-applied (§14.5) — reviewer

**MEDIUM changes (all implemented):**
16. ✅ Renamed dim #9 from "Self-Improvement" to "Regression Avoidance" (§8.1) — library-expert
17. ✅ Added Phase P0 bootstrap from historical data (§17.1) — reviewer
18. ✅ Added citations: Self-Refine, MetaGPT, LLMs Cannot Self-Correct (§2) — library-expert
19. ✅ Per-agent weight overrides for structural agents (§8.1) — structural-engineer
20. ✅ Retention policy: 6-month raw + yearly archive (§12.3) — governance
21. ✅ SHA-256 file integrity + diff-based evolution (§14.2, §14.3) — security

**NEW sections in v2.0 (not in v1.0):**
- §3 Operational Philosophy — observation-first, the drift problem, non-breaking evolution
- §6 Three-Phase Rollout — burn-in, measure+propose, full evolution
- §7 Helper Scripts — 7 scripts with full descriptions, run.sh integration
- §9 Scoring Rubric — anchored examples for 5 dimensions at 5 levels
- §10 Per-Agent Review Pipeline — step-by-step pipeline + per-agent review table
- §11 Drift Detection Engine — categories, per-agent rules JSON, drift score formula
- §14 Security Guardrails — 5 subsections covering full security posture
- §15 Self-Evolution (Meta) — self-reflection + self-evolution triggers
- §18 Agent Review Summary — condensed review results

---

*This document is the single source of truth for the agent-evolver plan.*
*Status: Active (v2.0) — Implementation begins at Phase P0 (Bootstrap).*
*All 60+ review suggestions from 8 specialist agents have been incorporated.*