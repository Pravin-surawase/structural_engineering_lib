**Type:** Architecture
**Audience:** All Agents
**Status:** Approved
**Importance:** Critical
**Created:** 2026-03-28
**Last Updated:** 2026-03-28

# Self-Evolving System Architecture

## Problem

As the project evolves, **information entropy increases**:

| Issue | Impact | Example |
|-------|--------|---------|
| Docs reference stale counts | Agents get wrong context | "38 endpoints" when actual is 42 |
| Agent instructions drift from code | Wrong commands, missing hooks | `.agent.md` says `useExport` but hook was renamed |
| Scripts reference removed patterns | Runtime errors | Script checks for file that moved |
| No feedback loop | Same mistakes repeat | Agent wastes 15min finding hook every session |
| Manual maintenance | 10+ hours rework | Manually updating 20 files after a refactor |
| Static context in limited windows | Wasted tokens on stale info | 500 tokens of outdated instructions |
| No review cadence | Drift accumulates silently | Doc untouched for 6 months |
| No cross-agent learning | Knowledge silos | Backend agent discovers pattern, frontend never learns |

## Solution: 3-Layer Self-Evolving System

```
┌─────────────────────────────────────────────────────────┐
│                    EVOLVE ENGINE                         │
│  ./run.sh evolve [--dry-run|--fix|--report]             │
│  Orchestrates everything. Runs periodically or on-demand│
├────────────────────┬────────────────────────────────────┤
│  PROJECT HEALTH    │  AGENT FEEDBACK                    │
│  Unified scanner   │  Session-end collection            │
│  Auto-fix engine   │  Pattern analysis                  │
│  Health scoring    │  Cross-agent learning              │
├────────────────────┴────────────────────────────────────┤
│              EXISTING INFRASTRUCTURE                     │
│  20 check scripts │ sync_numbers │ CI/CD │ git hooks    │
└─────────────────────────────────────────────────────────┘
```

### Layer 1: `project_health.py` — Unified Health Scanner

**Purpose**: Single command to assess entire project health.

```bash
./run.sh health                    # Full scan, report issues
./run.sh health --fix              # Auto-fix everything fixable
./run.sh health --score            # Just the health score (0-100)
./run.sh health --category docs    # Scan specific category
./run.sh health --json             # Machine-readable output
```

**Categories scanned**:

| Category | What's Checked | Auto-Fixable |
|----------|---------------|--------------|
| **docs** | Freshness (age), broken links, stale numbers, missing metadata, orphan files | Links, numbers, metadata |
| **code** | Architecture violations, circular imports, broken imports | — |
| **agents** | Instruction drift, reference validity, stale examples, context efficiency | Agent instruction refs |
| **infra** | CI config, Docker, script validity, hook installation | — |
| **feedback** | Unresolved items, recurring issues, avg resolution time | — |

**Health Score**: Weighted composite (0-100):
- Docs: 30% (most frequent drift)
- Code: 25% (high impact)
- Agents: 20% (agent effectiveness)
- Infra: 15% (stability)
- Feedback: 10% (continuous improvement)

### Layer 2: `agent_feedback.py` — Feedback Collection

**Purpose**: Agents log issues they encounter; patterns emerge over time.

```bash
# Log feedback at session end
./run.sh feedback log --agent backend \
  --stale-doc "api.md had wrong param name for design_beam" \
  --missing "No docs on batch_design endpoint" \
  --time-wasted "15min searching for geometry hook location"

# Analyze patterns
./run.sh feedback summary           # Recent trends
./run.sh feedback pending           # Unresolved items
./run.sh feedback resolve <id>      # Mark resolved
```

**Feedback categories**:
- `stale-doc` — Doc had wrong/outdated info
- `missing` — Info that should exist but doesn't
- `wrong-instruction` — Agent instruction was incorrect
- `time-wasted` — Significant time lost due to information gap
- `fix-applied` — What the agent fixed (for learning)
- `suggestion` — Improvement idea

**Storage**: `logs/feedback/YYYY-MM-DD_<agent>_<session>.json`

### Layer 3: `evolve.py` — Self-Evolution Engine

**Purpose**: Periodically evolve the project based on health data + feedback.

```bash
./run.sh evolve                     # Full evolution cycle
./run.sh evolve --dry-run           # Preview changes
./run.sh evolve --report            # Generate evolution report only
./run.sh evolve --review weekly     # Quick weekly review
./run.sh evolve --review monthly    # Comprehensive monthly review
```

**Evolution cycle**:
1. Run `project_health.py --fix` (auto-fix fixable issues)
2. Process pending feedback → update docs/instructions
3. Regenerate stale indexes
4. Archive docs older than 90 days in `_active/`
5. Generate evolution report
6. Auto-commit fixes via `ai_commit.sh`
7. Create TODO items for manual fixes in `TASKS.md`

## Dynamic vs Static Context

### What should be STATIC (in `.agent.md`, instructions):
- Architecture rules (4-layer boundary)
- Git workflow rules (always use `ai_commit.sh`)
- Naming conventions (`b_mm` not `width`)
- Import direction rules
- PR enforcement

### What should be DYNAMIC (loaded at runtime via `agent_context.py`):
- File counts (tests, scripts, hooks, endpoints)
- Recent commits and active branches
- Current task priorities
- File lists and paths
- Live route/function enumerations

### Principle: **Never hardcode a number in a static instruction file.**

If a number appears in `.agent.md` or `copilot-instructions.md`, it WILL go stale.
Use `agent_context.py` dynamic sections instead.

## Integration Points

### Session Start
```
agent_context.py → loads dynamic context
  ↓ also runs
project_health.py --score → shows health score
agent_feedback.py pending --brief → shows unresolved feedback
```

### Session End
```
agent_feedback.py log → agent records issues found
project_health.py --quick → quick health check
session.py end → normal session logging
```

### Periodic (CI/Cron)
```
Weekly:  evolve.py --review weekly   (quick: numbers, links, feedback)
Monthly: evolve.py --review monthly  (full: all categories + archive)
```

### Post-Commit (existing)
```
sync_numbers.py → warns of number drift (non-blocking)
collect_metrics.sh → logs velocity metrics
```

## Review Schedule

| Frequency | What | How | Auto-Fix |
|-----------|------|-----|----------|
| Every commit | Number drift | `sync_numbers.py` (post-commit hook) | Warns only |
| Every session end | Agent feedback | `agent_feedback.py log` | N/A |
| Weekly | Links, numbers, feedback trends | `evolve.py --review weekly` | Yes |
| Monthly | Full health, archive old docs, instruction drift | `evolve.py --review monthly` | Partial |
| Quarterly | Deep review, agent effectiveness, context optimization | Manual review triggered by report | No |

## Measuring Success

Track these metrics in `logs/evolution/`:
- **Health score trend**: Should stay above 80 or improve
- **Feedback volume**: Decreasing = system is learning
- **Auto-fix rate**: Higher = less manual work
- **Recurring issues**: Should go to zero as fixes stick
- **Time-to-resolution**: Feedback → fix time should decrease
