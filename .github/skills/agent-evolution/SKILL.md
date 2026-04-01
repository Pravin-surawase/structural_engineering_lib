---
name: agent-evolution
description: "Run self-evolution cycle — score agents, detect drift, propose instruction improvements. Use at session end, weekly cadence, or monthly deep review."
---

# Agent Evolution Skill

Run the self-evolving agent improvement cycle — from data collection through scoring, drift detection, and instruction evolution.

## When to Use

- **Session end:** Quick status check and data collection
- **Weekly review:** Full scoring + drift detection + trend analysis
- **Monthly audit:** Complete audit with paper export and evolution proposals

## Quick Status Check (Session End)

```bash
./run.sh evolve --status
./run.sh feedback log --agent <name>
```

## Weekly Evolution Cycle

Run these 5 steps in order:

1. **Collect session data:**
   ```bash
   .venv/bin/python scripts/agent_session_collector.py
   ```

2. **Score agents:**
   ```bash
   .venv/bin/python scripts/agent_scorer.py --all
   ```

3. **Detect drift:**
   ```bash
   .venv/bin/python scripts/agent_drift_detector.py
   ```

4. **Check compliance:**
   ```bash
   .venv/bin/python scripts/agent_compliance_checker.py
   ```

5. **Analyze trends:**
   ```bash
   .venv/bin/python scripts/agent_trends.py --weekly
   ```

Or one command: `./run.sh evolve --review weekly`

## Monthly Deep Review

Additional steps beyond the weekly cycle:

1. **Run weekly cycle first** (steps 1-5 above)

2. **Export paper data:**
   ```bash
   .venv/bin/python scripts/export_paper_data.py
   ```

3. **Propose evolutions:**
   ```bash
   .venv/bin/python scripts/agent_evolve_instructions.py --propose
   ```

4. **Review proposals:**
   ```bash
   .venv/bin/python scripts/agent_evolve_instructions.py --list
   ```

5. **Apply approved:**
   ```bash
   .venv/bin/python scripts/agent_evolve_instructions.py --apply --confirm
   ```

Or: `./run.sh evolve --review monthly`

## Rollback

Emergency rollback procedure:

```bash
.venv/bin/python scripts/agent_evolve_instructions.py --rollback <agent-name>
```

## Key Data Files

| File | Purpose |
|------|---------|
| `logs/agent-performance/scorecard_index.json` | Latest scores per agent |
| `logs/agent-performance/evolution-log.json` | Applied evolution history |
| `logs/agent-performance/pending-evolutions.json` | Proposed changes |
| `logs/agent-performance/sessions/*.json` | Raw session data |
| `logs/agent-performance/trends/*.json` | Trend analyses |
| `logs/agent-performance/backups/*.bak` | Agent file backups |

## Safety Rules

- Level 2+ changes on safety-critical agents are **BLOCKED**
- Maximum 3 auto-edits per week
- Always verify with `--dry-run` or `--propose` before `--apply`
- Backups are created automatically; rollback with `--rollback`

## Burn-in Period

The system requires **15-20 sessions** of data collection before evolution proposals become meaningful. During burn-in, focus on **OBSERVE** and **MEASURE** only — do not **EVOLVE**.