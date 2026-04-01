---
owner: Orchestrator
status: draft
last_updated: 2026-04-01
doc_type: planning
complexity: advanced
tags: [agent-evolver, self-improvement, meta-agent, metrics, paper-data]
---

**Type:** Architecture
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-04-01
**Last Updated:** 2026-04-01

# Agent-Evolver: Self-Evolving Meta-Agent — Planning Document

**Plan Version:** v1.0-draft
**Review Status:** Pending agent reviews

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Research Foundation](#2-research-foundation)
3. [Existing Infrastructure Audit](#3-existing-infrastructure-audit)
4. [Agent Design](#4-agent-design)
5. [Performance Scoring Framework](#5-performance-scoring-framework)
6. [Data Architecture](#6-data-architecture)
7. [Evolution Rules Engine](#7-evolution-rules-engine)
8. [Self-Evolution (Meta)](#8-self-evolution-meta)
9. [Implementation Pipeline](#9-implementation-pipeline)
10. [Academic Data Export](#10-academic-data-export)
11. [Integration Points](#11-integration-points)
12. [Agent Reviews](#12-agent-reviews)
13. [Version History](#13-version-history)

---

## 1. Executive Summary

The **agent-evolver** is a 15th meta-agent that monitors, scores, and improves all 14 existing agents (and itself). It closes the feedback loop that currently exists in infrastructure (`evolve.py`, `agent_feedback.py`, `project_health.py`) but has **zero usage data** — 0 feedback items logged, no per-agent scoring, no trend analysis.

**Problem:** Agents repeat mistakes across sessions. No quantitative tracking of agent performance. Evolution infrastructure built but not activated. No data for a paper on self-evolving multi-agent systems.

**Solution:** A dedicated meta-agent that runs at session-end (mandatory), weekly (deep), and monthly (paper-grade), collecting structured performance data on each agent across 10 dimensions, detecting degradation patterns, auto-evolving instructions, and exporting academic-quality datasets.

**Academic Value:** Produces time-series data of agent performance, evolution events, and their impact — suitable for a paper on "Self-Evolving Multi-Agent Systems for Domain-Specific Software Engineering."

---

## 2. Research Foundation

| Framework | Paper | Key Idea Applied |
|-----------|-------|-----------------|
| **Reflexion** | Shinn et al., 2023 (arXiv:2303.11366) | Verbal reinforcement — agents reflect on failures in episodic memory buffer, not weight updates |
| **STOP** | Zelikman et al., 2023 (arXiv:2310.02304) | Recursive self-improvement — scaffolding program improves itself via utility function |
| **Multi-Agent Survey** | Masterman et al., 2024 (arXiv:2404.11584) | Leadership, communication styles, reflection phases in multi-agent architectures |
| **LLM Agents** | Weng, 2023 (Lil'Log) | Planning + Memory + Tool Use pillars; Reflexion loop design |

**Key insight from Reflexion:** Self-improvement through *verbal reflection* stored in episodic memory (not model fine-tuning) achieves 91% HumanEval vs 80% baseline. Our approach: store agent performance reflections in `logs/agent-performance/` as the episodic memory buffer.

**Key insight from STOP:** A scaffolding program that improves itself outperforms the seed improver. Our approach: agent-evolver can modify its own evolution rules when they prove ineffective (the meta part).

---

## 3. Existing Infrastructure Audit

| Component | Script | Status | Gap |
|-----------|--------|--------|-----|
| Evolution engine | `scripts/evolve.py` (542 lines) | ✅ Built | No per-agent metrics |
| Feedback collection | `scripts/agent_feedback.py` (379 lines) | ✅ Built, **0 items** | Agents don't call it |
| Health scanner | `scripts/project_health.py` (740 lines) | ✅ Built (62/100) | Not agent-granular |
| Mistake tracker | `scripts/agent_mistakes_report.sh` | ✅ Built | Only git/hook mistakes |
| Instruction drift | `scripts/check_instruction_drift.py` | ✅ Built | Detects but doesn't fix |
| Agent context | `scripts/agent_context.py` | ✅ 14 agents | No performance history |
| 27 checks | `scripts/check_all.py` | ✅ All working | No per-agent attribution |
| Feedback storage | `logs/feedback/` | **Empty** | Framework ready, zero data |
| Evolution logs | `logs/evolution/` | 2 reports | No trend analysis |

**Bottom line:** Infrastructure exists but the feedback loop is open. Agent-evolver closes it.

---

## 4. Agent Design

### 4.1 Identity

| Property | Value |
|----------|-------|
| **Name** | `agent-evolver` |
| **File** | `.github/agents/agent-evolver.agent.md` |
| **Model** | Claude Opus 4.6 |
| **Role** | Self-evolving meta-agent — monitors, scores, and improves all agents (including itself) |
| **Tools** | `read/readFile`, `search`, `web`, `terminal` |
| **Trigger** | Session-end (mandatory), weekly (deep review), monthly (full audit + paper export) |

### 4.2 Core Cycle (6 Pillars)

```
┌─────────────────────────────────────────────────────────┐
│                   AGENT-EVOLVER CYCLE                    │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ OBSERVE  │→ │ MEASURE  │→ │ REFLECT  │               │
│  └──────────┘  └──────────┘  └──────────┘               │
│       ↑                           │                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ VALIDATE │← │ EVOLVE   │← │ DIAGNOSE │               │
│  └──────────┘  └──────────┘  └──────────┘               │
│                                                          │
│  Theory: Reflexion (verbal RL) + STOP (recursive)        │
└─────────────────────────────────────────────────────────┘
```

| Pillar | What It Does | Data Source |
|--------|-------------|-------------|
| **OBSERVE** | Collect session data — what each agent did, commands run, errors, files changed | `git log`, `SESSION_LOG.md`, `logs/feedback/`, terminal output |
| **MEASURE** | Score each agent on 10 dimensions (§5), compute composites | `logs/agent-performance/` |
| **REFLECT** | Identify patterns — recurring mistakes, inefficiencies, instruction gaps | Feedback analysis, mistake report, health scan |
| **DIAGNOSE** | Root-cause: WHY did the agent fail? Instruction gap? Tool limitation? Context loss? | Cross-reference with `.agent.md` content |
| **EVOLVE** | Update `.agent.md` instructions, add warnings, propose new skills | Targeted edits to agent files |
| **VALIDATE** | Verify evolution didn't break anything — instruction drift, architecture boundaries | `check_instruction_drift.py`, `check_all.py` |

### 4.3 Execution Cadence

| Cadence | Scope | Actions | Est. Duration |
|---------|-------|---------|---------------|
| **Per-Session** (mandatory) | Current session | Log metrics for each active agent, append to scorecard | ~2 min |
| **Weekly** (every 5 sessions) | Last 5-7 sessions | Aggregate scores, detect trends, flag degraded agents, propose evolution | ~10 min |
| **Monthly** | All historical data | Full statistical analysis, paper-grade tables, update all instructions, self-evolve | ~30 min |

---

## 5. Performance Scoring Framework (10 Dimensions)

Each agent scored 0–10 per dimension per session. Produces a per-agent, per-session, per-dimension matrix.

| # | Dimension | Measures | Data Source | Weight |
|---|-----------|----------|-------------|--------|
| 1 | **Task Completion** | Did the agent complete its task? (0=failed, 5=partial, 10=done) | Git diff, reviewer verdict | 20% |
| 2 | **Code Quality** | Architecture compliance, no duplication, proper patterns | Reviewer checklist, arch boundary check | 15% |
| 3 | **Terminal Efficiency** | Commands run vs needed; redundant searches, wrong paths | Terminal log analysis | 10% |
| 4 | **Context Utilization** | Read existing code before writing? Checked hooks/routes/API? | Session log, search patterns | 10% |
| 5 | **Pipeline Compliance** | Followed mandatory 8/9-step pipeline? | Orchestrator tracking | 10% |
| 6 | **Error Rate** | Build failures, test failures, lint errors introduced | Build/test output | 10% |
| 7 | **Instruction Adherence** | Followed `.agent.md` rules? Used right tools, avoided FORBIDDEN? | Feedback log, reviewer notes | 10% |
| 8 | **Handoff Quality** | Clear summary for next agent? Updated TASKS/WORKLOG? | Doc completeness | 5% |
| 9 | **Time Efficiency** | Prompt count vs expected for task complexity | Message count | 5% |
| 10 | **Self-Improvement** | Avoided previously-documented mistakes? | Mistake history comparison | 5% |

**Composite Score Formula:**

$$S_{agent} = \sum_{i=1}^{10} w_i \cdot d_i$$

where $w_i$ is the weight for dimension $i$ and $d_i \in [0, 10]$ is the score.

**Normalization:** Composite $\in [0, 10]$. Grade mapping: 9-10 = Excellent, 7-8.9 = Good, 5-6.9 = Needs Improvement, <5 = Critical.

---

## 6. Data Architecture

### 6.1 Directory Structure

```
logs/agent-performance/
├── scorecard.json              # Master scorecard (all agents, all sessions)
├── sessions/
│   ├── 2026-04-01_session.json # Per-session metrics
│   └── ...
├── trends/
│   ├── weekly_2026-W14.json    # Weekly aggregates
│   ├── monthly_2026-04.json    # Monthly aggregates
│   └── ...
├── evolution-log.json          # What was changed in agent.md files and why
└── paper-export/
    ├── agent_scores.csv        # CSV: agent × session × 10 dimensions
    ├── dimension_trends.csv    # Time-series per dimension per agent
    ├── evolution_events.csv    # When/what evolved, impact measurement
    └── summary_stats.json      # Means, σ, CI, p-values, effect sizes
```

### 6.2 Session Record Schema

```json
{
  "session_id": "2026-04-01T14:30",
  "session_duration_prompts": 12,
  "agents_active": ["backend", "tester", "reviewer"],
  "task_ids": ["TASK-633"],
  "health_score_before": 62,
  "health_score_after": 65,
  "agent_scores": {
    "backend": {
      "task_completion": 8,
      "code_quality": 9,
      "terminal_efficiency": 6,
      "context_utilization": 7,
      "pipeline_compliance": 10,
      "error_rate": 8,
      "instruction_adherence": 9,
      "handoff_quality": 7,
      "time_efficiency": 6,
      "self_improvement": 8,
      "composite": 8.05,
      "notes": "Missed checking hooks/ before creating useColumnDesign"
    }
  },
  "evolution_actions": [],
  "evolver_self_reflection": {
    "issues_caught": 3,
    "issues_missed": 0,
    "false_positives": 0,
    "rule_effectiveness": "all rules within threshold"
  }
}
```

---

## 7. Evolution Rules Engine

### 7.1 Trigger Rules

| Trigger | Threshold | Action | Severity |
|---------|-----------|--------|----------|
| Same mistake 3+ times | Pattern count ≥ 3 | Add WARNING to `.agent.md` | Medium |
| Dimension score < 5 for 2 sessions | Avg < 5.0 on any dim | Add specific instruction + example | High |
| Composite trending down | 3 consecutive declining | Flag for human review | High |
| Agent duplicates existing code | Detected by reviewer | Add to "DO NOT recreate" list | Medium |
| Terminal command > 5 retries | Failed cmd count ≥ 5 | Add to quick-reference section | Low |
| Same workaround 5+ times | Pattern count ≥ 5 | Propose new skill creation | Medium |
| Health score drops > 10 pts | Delta > -10 | Automatic `evolve --fix` | Critical |

### 7.2 Evolution Actions

| Action Type | What Changes | Requires Human Approval |
|-------------|-------------|------------------------|
| `add_warning` | Add WARNING block to `.agent.md` | No |
| `add_instruction` | Add specific instruction with example | No |
| `update_quick_ref` | Add command to quick-reference | No |
| `add_do_not_recreate` | Add to existing "DO NOT" list | No |
| `propose_skill` | Draft new skill SKILL.md | Yes |
| `modify_pipeline` | Change pipeline steps or thresholds | Yes |
| `self_modify` | Change evolver's own rules | Yes (auto-flagged) |

### 7.3 Impact Measurement

Every evolution action includes a before/after measurement:
- **Before:** Avg score on affected dimension over last 3 sessions
- **After:** Score on same dimension next 3 sessions post-evolution
- **Impact:** $\Delta = \bar{S}_{after} - \bar{S}_{before}$
- **Significance:** Paired t-test, $p < 0.05$ required to declare improvement

---

## 8. Self-Evolution (Meta)

The agent-evolver applies its own framework to itself (STOP-inspired recursion):

### 8.1 Self-Reflection Questions (after each run)

1. Did I catch all issues the reviewer later found? (precision)
2. Did I miss issues that caused problems later? (recall)
3. Were my instruction updates helpful? (impact — score delta)
4. Am I generating too many false positives? (noise level)
5. Are my evolution rules too aggressive or too conservative?

### 8.2 Self-Evolution Triggers

| Condition | Self-Action |
|-----------|------------|
| A rule fires but makes things worse (negative $\Delta$) | Tighten threshold or remove rule |
| A rule never fires in 10+ sessions | Lower threshold or remove |
| Gap exists (recurring issue, no rule covers it) | Create new rule |
| False positive rate > 20% | Add specificity constraints |
| Evolver's own composite < 7.0 | Full self-review with human |

---

## 9. Implementation Pipeline

### 9.1 Phase Plan

| Phase | Deliverables | Agent | Depends On |
|-------|-------------|-------|------------|
| **P1: Plan** | This document, agent reviews | orchestrator | — |
| **P2: Agent Definition** | `agent-evolver.agent.md`, `/agent-evolution` skill | doc-master | P1 approved |
| **P3: Scoring Engine** | `scripts/agent_scorer.py` | backend | P2 |
| **P4: Trend Analysis** | `scripts/agent_trends.py` | backend | P3 |
| **P5: Instruction Evolver** | `scripts/agent_evolve_instructions.py` | backend | P4 |
| **P6: Paper Export** | `scripts/export_paper_data.py` | backend | P3 |
| **P7: Integration** | Session workflow updates | ops | P3 |
| **P8: Validation** | First monthly run, data quality check | governance + tester | P7 |

### 9.2 New Files

| File | Purpose | Est. Lines |
|------|---------|-----------|
| `.github/agents/agent-evolver.agent.md` | Agent definition | ~200 |
| `.github/skills/agent-evolution/SKILL.md` | Skill definition | ~80 |
| `scripts/agent_scorer.py` | Per-session scoring engine | ~300 |
| `scripts/agent_trends.py` | Trend detection + aggregation | ~200 |
| `scripts/agent_evolve_instructions.py` | Auto-update `.agent.md` | ~250 |
| `scripts/export_paper_data.py` | Academic CSV + stats export | ~200 |
| `logs/agent-performance/scorecard.json` | Master scorecard (init empty) | ~10 |

---

## 10. Academic Data Export

### 10.1 Table for Paper (Monthly Export)

| Agent | Sessions | Avg Score | σ | Trend | Task | Quality | Terminal | Context | Pipeline | Error | Instruct. | Handoff | Time | Self-Imp. | Evolutions |
|-------|----------|-----------|---|-------|------|---------|----------|---------|----------|-------|-----------|---------|------|-----------|------------|
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

*Table populated after first session cycle. Trends: ↑ improving, → stable, ↓ declining.*

### 10.2 Statistical Metrics for Paper

| Metric Category | Specific Metrics | Export Format |
|----------------|-----------------|--------------|
| **Efficiency** | Prompts/task, commands/task, redundant searches | Time-series CSV |
| **Quality** | Test pass rate, arch violations, code duplicates | Per-session counts |
| **Learning** | Score improvement post-evolution, mistake recurrence | Before/after pairs |
| **Autonomy** | Tasks without human intervention, self-fixes | Percentages |
| **Coverage** | IS 456 clause coverage, test %, API coverage | Monotonic growth |
| **Meta** | Evolution events, instruction updates, new skills | Cumulative counts |
| **Reliability** | Build success rate, CI pass rate, commit rate | Percentages |
| **Collaboration** | Handoff quality, cross-agent rework rate | Per-handoff score |

### 10.3 Statistical Rigor

- **Central tendency:** Mean, median per dimension per agent
- **Dispersion:** Standard deviation, IQR
- **Confidence:** 95% confidence intervals
- **Significance:** Paired t-tests for pre/post evolution comparisons
- **Effect size:** Cohen's d for meaningful improvement detection
- **Trend:** Linear regression slope per dimension over time

---

## 11. Integration Points

### 11.1 Updated Session End Workflow

```
Session End (UPDATED):
1. ./run.sh commit (uncommitted work)          ← EXISTING
2. ./run.sh feedback log --agent <name>        ← EXISTING (must enforce)
3. ./run.sh session summary                    ← EXISTING
4. agent-evolver --session                     ← NEW (score active agents)
5. Update next-session-brief.md                ← EXISTING
6. ./run.sh commit "docs: session end"         ← EXISTING
```

### 11.2 Cadence Integration

```
Weekly:
  ./run.sh evolve --review weekly              ← EXISTING
  agent-evolver --weekly                       ← NEW (trend analysis)

Monthly:
  agent-evolver --monthly                      ← NEW (full stats + self-evolve)
  agent-evolver --paper                        ← NEW (CSV export for paper)
```

### 11.3 Orchestrator Integration

Update orchestrator.agent.md to include agent-evolver in the decision tree and handoff chain:

```
| Agent performance / evolution | → agent-evolver |
```

### 11.4 All Agent Updates

Every agent's `.agent.md` gets a new section:

```markdown
## Performance Tracking
This agent is scored by @agent-evolver on 10 dimensions after each session.
Current avg score: [auto-updated]
Recent evolution events: [auto-updated]
See logs/agent-performance/scorecard.json for full history.
```

---

## 12. Agent Reviews

### Review Summary

| # | Agent | Focus | Verdict | Score | Key Concern |
|---|-------|-------|---------|-------|-------------|
| 1 | @governance | Evolution framework, metrics, automation | APPROVED WITH CHANGES | 7/10 | Enforcement gap — same failure mode as current unused feedback system |
| 2 | @reviewer | Quality gates, scoring rigor, pipeline | APPROVED WITH CHANGES | 7/10 | Scoring subjectivity — 4 of 10 dimensions lack operational definitions |
| 3 | @backend | Script design, schemas, implementation | APPROVED WITH CHANGES | 7.5/10 | No scoring input mechanism defined; single scorecard.json won't scale |
| 4 | @tester | Measurement validity, test strategy | APPROVED WITH CHANGES | 4/10 | No tests for evolver scripts; paired t-test underpowered at N=3 |
| 5 | @ops | Session workflow, git implications | APPROVED WITH CHANGES | 7/10 | Don't add new session-end step — fold into existing summary command |
| 6 | @security | Data integrity, safe modification | APPROVED WITH CHANGES | 5/10 | Prompt injection via session data; unsanitized writes to .agent.md |
| 7 | @library-expert | Academic rigor, paper strategy | APPROVED WITH CHANGES | 7/10 | No inter-rater reliability; weight justification missing; need N≥34 |
| 8 | @structural-engineer | Domain relevance, IS 456 | APPROVED WITH CHANGES | 6/10 | No "Engineering Accuracy" dimension; safety-critical agents need special rules |

**Consensus Verdict:** APPROVED WITH CHANGES (8/8 agents)
**Average Score:** 6.6/10 (range: 4–7.5)
**All agents agree** the plan addresses a real gap and the architecture is sound.
**Key risk identified by ALL:** The enforcement gap — feedback logging has 0 usage despite being built.

### 12.1 Governance Review
**Status:** ✅ Complete | **Verdict:** APPROVED WITH CHANGES | **Score:** 7/10

**Strengths:** Correctly identifies open feedback loop; 10-dimension framework is well-structured; cadence maps onto governance cadence.

**Critical Concerns:**
- `VALID_AGENTS` in `agent_feedback.py` is missing 3 agents (structural-math, security, library-expert). Must synchronize before building scorer.
- Zero enforcement mechanism for per-session scoring. Existing feedback mandate has 0% compliance.
- Statistical power insufficient — most agents appear in ≤2-3 sessions/month.

**Accepted Suggestions:**
1. Create shared agent registry (`scripts/_lib/agents.py`) auto-discovered from `.github/agents/*.agent.md`
2. Enforce scoring via git hook / session summary integration
3. Minimum 5 scored sessions before any evolution action fires
4. Add rollback mechanism using evolution-log.json diffs
5. Require dry-run for all auto-modifications (3 consecutive sessions confirm pattern before apply)
6. Drop Time Efficiency (dim #9) initially, redistribute weight
7. Add test suite for `agent_scorer.py` (~100 lines)
8. Define "sporadically active" agent handling (carry forward last score)
9. Integration with governance weekly report template
10. Log rotation policy: 6-month raw, yearly archive

### 12.2 Reviewer Review
**Status:** ✅ Complete | **Verdict:** APPROVED WITH CHANGES | **Score:** 7/10

**Strengths:** Excellent research grounding; infrastructure audit is accurate; data architecture well-designed; self-evolution guardrails include human approval.

**Critical Concerns:**
- Dimensions 1, 4, 8, 9 are subjective — need operational definitions with binary checkpoints
- Paired t-test with N=3 has ~6% power — use Wilcoxon signed-rank or make Cohen's d primary
- Self-modification "auto-flagged" approval is theatrical — require HUMAN approval in next session

**Accepted Suggestions:**
1. Replace 0/5/10 scale with 5-checkpoint rubric for Task Completion
2. Wilcoxon signed-rank as primary test, Cohen's d as primary metric, t-test secondary
3. Rate limit: max 3 auto-edits per weekly cycle
4. Self-modification stored as pending proposals, never auto-applied
5. Add Phase P0: retroactively score last 10 sessions for baseline bootstrap
6. State architecture constraint: evolver NEVER modifies structural_lib, fastapi_app, or react_app
7. Make "3+ times" threshold self-adjustable in range [2, 5]
8. Add instruction size guard: 300-line cap per `.agent.md`

### 12.3 Backend Review
**Status:** ✅ Complete | **Verdict:** APPROVED WITH CHANGES | **Score:** 7.5/10

**Strengths:** Leverages existing infrastructure; scripts are well-scoped; reuse opportunities identified.

**Critical Concerns:**
- No scoring input mechanism (CLI? JSON template? Interactive?)
- Single `scorecard.json` won't scale — need directory-based approach
- Terminal commands not logged per-agent (new infrastructure needed)

**Accepted Suggestions:**
1. CLI scoring interface: `python scripts/agent_scorer.py --session <id> --agent backend ...`
2. Directory-based scorecard: `scorecard_index.json` + `sessions/*.json` + `trends/*.json`
3. Add `schema_version`, `feedback_ids`, `auto_metrics` to JSON schema
4. Phased automation: manual first → auto 4 dims → semi-auto 3 more
5. Create `scripts/_lib/scoring.py` + `agent_data.py` as reusable modules
6. Effort estimate: ~30-37 hours total across 4+1 scripts

### 12.4 Tester Review
**Status:** ✅ Complete | **Verdict:** APPROVED WITH CHANGES | **Score:** 4/10 (lowest)

**Strengths:** Right instinct on impact measurement; phased implementation reduces risk.

**Critical Concerns:**
- NO test strategy for evolver scripts themselves (ironic for a measurement tool)
- Paired t-test at N=3 has ~10% power — useless for detecting real improvements
- No calibration/burn-in phase — evolution enabled from session 1 is premature
- Gaming/Goodhart's Law risk unaddressed

**Accepted Suggestions:**
1. Test files for all 4 new scripts (test_agent_scorer.py, test_agent_trends.py, etc.)
2. 10 "golden session" fixtures hand-scored by human engineer
3. Burn-in: First 15-20 sessions = OBSERVE-MEASURE-REFLECT only, no evolution
4. Scorer consistency test: ICC ≥ 0.80 required before evolution activates
5. Use Hedges' g instead of Cohen's d (unbiased for small samples)
6. Apply Benjamini-Hochberg FDR correction for multiple comparisons in paper
7. Mann-Kendall test for trend detection instead of linear regression on N<10
8. Bootstrapped 95% CIs (10,000 resamples) instead of parametric
9. Anchored scoring rubric with examples at levels 1-2, 3-4, 5-6, 7-8, 9-10
10. Anchor recalibration: monthly re-score 3 random past sessions

### 12.5 Ops Review
**Status:** ✅ Complete | **Verdict:** APPROVED WITH CHANGES | **Score:** 7/10

**Strengths:** logs/agent-performance/ already gitignored; session integration is minimally invasive; run.sh already has evolve/feedback commands.

**Critical Concerns:**
- Adding separate session-end step creates friction — fold into `./run.sh session summary`
- `.agent.md` modifications are production files requiring PR — stage in pending JSON, apply via weekly PR
- Merge conflict risk when evolver modifies `.agent.md` while another agent edits it on a branch

**Accepted Suggestions:**
1. Fold scoring into `./run.sh session summary` (step 3) — no new step
2. Evolution changes staged in `pending-evolutions.json`, applied weekly via task branch + PR
3. Evolver runs on main only, never on task branches
4. Scoring at session-end, instruction changes ONLY at weekly/monthly cadence
5. Paper data to `docs/research/paper-data/` if tracking needed for reproducibility
6. New run.sh commands: `--session`, `--weekly`, `--monthly`, `--paper`, `--scores`
7. Max 100 sessions per scorecard file, monthly rotation

### 12.6 Security Review
**Status:** ✅ Complete | **Verdict:** APPROVED WITH CHANGES | **Score:** 5/10

**Critical Concerns:**
- [CRITICAL] Prompt injection via session data — evolver reads SESSION_LOG, feedback, terminal output that could contain adversarial content manipulating instruction generation
- [CRITICAL] Unsanitized writes to `.agent.md` — no content validation, schema enforcement, or character sanitization
- [HIGH] No JSON schema validation on scorecard.json — score tampering could trigger/suppress evolution rules

**Accepted Suggestions:**
1. Add §7.4 "Security Guardrails" section
2. Content sanitization: validate markdown, YAML parseable, no tool/handoff injection
3. JSON Schema validation for all data files — reject schema violations
4. Input boundary markers: strip instruction override patterns from session data
5. Max 3 agent files modified per evolution cycle
6. Recursion depth limit: 1 self-modification per monthly cycle max
7. SHA-256 file integrity for .agent.md before/after modification
8. Diff-based evolution (produce unified diff, apply via patch, never overwrite)
9. Rollback command: `./run.sh evolve --rollback <evolution_id>`
10. Backup directory: last 10 .agent.md versions before modification

### 12.7 Library Expert Review
**Status:** ✅ Complete | **Verdict:** APPROVED WITH CHANGES | **Score:** 7/10

**Strengths:** Real gap identified; Reflexion/STOP correctly mapped; paper-grade data architecture; fills existing paper's §10.4 Limitation 5.

**Critical Concerns:**
- No inter-rater reliability protocol — LLM judging LLM with no calibration
- N≈34 per agent needed for medium effect; focus on 4-5 most active agents
- Weight justification missing — cite ISO/IEC 25010 or GQM paradigm

**Accepted Suggestions:**
1. Calibration: 2+ agents independently score same session, compute Cohen's κ
2. Focus statistical claims on 4-5 most active agents (backend, tester, reviewer, frontend, doc-master)
3. Cite ISO/IEC 25010, GQM, Self-Refine (Madaan et al.), LLMs Cannot Self-Correct (Huang et al.), MetaGPT (Hong et al.)
4. Rename dim #10 from "Self-Improvement" to "Regression Avoidance"
5. Report correlation matrix and consider PCA for dimension independence
6. Paper venue: ICSE 2027 NIER or ASE Tool track
7. Testable hypotheses: (H1) scores increase post-evolution, (H2) mistake recurrence decreases, (H3) domain dimensions show higher variance
8. Recommended figures: heatmap, box plots with effect sizes, spider charts, cumulative evolution curve

### 12.8 Structural Engineer Review
**Status:** ✅ Complete | **Verdict:** APPROVED WITH CHANGES | **Score:** 6/10

**Critical Concerns:**
- [CRITICAL] No "Engineering Accuracy" scoring dimension — library's core purpose (IS 456 compliance) is invisible to the evolver
- [CRITICAL] Auto-modification of structural-engineer and structural-math agent files could alter safety factors, tolerances
- [HIGH] No domain-specific trigger rules for benchmark failures, tolerance regressions

**Accepted Suggestions:**
1. Add 11th dimension: "Engineering Accuracy" (15% weight) measuring benchmark pass rate, clause coverage, safety factor integrity
2. Classify structural-engineer.agent.md and structural-math.agent.md as "safety-critical" — ALL modifications require human approval
3. Domain-specific triggers: benchmark test failure → block evolution; tolerance regression → revert; safety factor modified → immediate human review
4. Per-agent weight overrides for structural agents: Engineering Accuracy 25%, Terminal Efficiency 5%, Time Efficiency 0%
5. Run structural regression tests after every evolution of structural agents
6. Track function-quality-pipeline gate execution in scoring
7. Evolver consumes but does NOT own IS 456 clause coverage data

---

## 13. Version History

| Version | Date | Changes | Status |
|---------|------|---------|--------|
| v1.0-draft | 2026-04-01 | Initial plan — 13 sections, 10 scoring dimensions, 7 evolution rules, 8-phase implementation | Draft |
| v1.1-reviewed | 2026-04-01 | All 8 agent reviews complete. Consensus: APPROVED WITH CHANGES (avg 6.6/10). 60+ specific suggestions collected. | Reviewed |
| v2.0 | *Pending* | Incorporate critical review feedback: add Engineering Accuracy dim, security guardrails, burn-in phase, test strategy, rubric anchoring, directory-based scorecard, safety-critical agent classification | *Planned* |

### Review-Driven Changes for v2.0

**CRITICAL (must address before implementation):**
1. Add 11th dimension: "Engineering Accuracy" (§5) — structural-engineer review
2. Add §7.4 "Security Guardrails" — security review
3. Add burn-in phase: 15-20 sessions observe-only before evolution activates — tester review
4. Add anchored scoring rubric with examples — tester + reviewer reviews
5. Synchronize VALID_AGENTS across all scripts — governance review
6. Add test strategy for evolver scripts — tester review (4 test files)
7. Classify safety-critical agent files — structural-engineer review

**HIGH (strongly recommended):**
8. Directory-based scorecard, not single JSON — backend review
9. Fold scoring into `./run.sh session summary` — ops review
10. Stage evolution changes in pending JSON, apply via weekly PR — ops review
11. Wilcoxon + Hedges' g as primary statistics — tester + reviewer reviews
12. 10 golden session fixtures for calibration — tester review
13. Max 3 auto-edits per weekly cycle — reviewer + security reviews
14. Domain-specific trigger rules for IS 456 — structural-engineer review
15. Self-modification proposals stored as pending, never auto-applied — reviewer review

**MEDIUM (recommended):**
16. Rename dim #10 to "Regression Avoidance" — library-expert review
17. Add Phase P0 (bootstrap from historical data) — reviewer review
18. Cite additional papers: Self-Refine, MetaGPT, LLMs Cannot Self-Correct — library-expert review
19. Per-agent weight overrides for structural agents — structural-engineer review
20. Log rotation: 6-month raw + yearly archive — governance review
21. SHA-256 file integrity + diff-based evolution — security review

---

*This document is the single source of truth for the agent-evolver plan. All reviews, updates, and version changes go here.*
*Next step: Orchestrator incorporates critical feedback → v2.0 → Implementation begins at Phase P0.*

*This document is the single source of truth for the agent-evolver plan. All reviews, updates, and version changes go here.*