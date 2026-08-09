---
name: agent-evolution
description: "Observe agent performance on a scheduled cadence, score exact collected sessions, and apply a reviewed evolution by ID only after enough evidence and explicit approval."
---

# Agent Evolution

This is an experimental governance process, not a mandatory session-end step. Normal coding sessions may log concrete feedback, but they do not run or apply evolution automatically.

## Read-Only Status and Reviews

```bash
./run.sh evolve --status
./run.sh evolve --review weekly
./run.sh evolve --review monthly
```

Periodic reviews are report-only unless `--fix` is explicitly supplied. Do not use `--fix` during burn-in or merely because status says a review is due.

## Collect and Score One Exact Session

Choose a stable session ID and agent name:

```bash
.venv/bin/python scripts/agent_session_collector.py --session-id <session-id>
.venv/bin/python scripts/agent_scorer.py --session <session-id> --agent <agent> --auto-only
.venv/bin/python scripts/agent_drift_detector.py --session <session-id> --agent <agent>
.venv/bin/python scripts/agent_compliance_checker.py --session <session-id> --agent <agent>
```

Drift and compliance checks are read-only. Add `--write` to the drift command
only when a persisted report is an intentional output of the review.

Do not use nonexistent bulk flags. Manual scores require the scorer's explicit dimension flags and evidence; do not invent values to complete a record.

## Proposal Gate

Instruction proposals require at least 15 collected session records. Before that threshold, observe and collect only. When the threshold is met and an evolution review is requested:

```bash
.venv/bin/python scripts/agent_trends.py --weekly --alert
.venv/bin/python scripts/agent_evolve_instructions.py --propose
.venv/bin/python scripts/agent_evolve_instructions.py --list
```

Trend analysis is read-only by default; add `--write` only for an intentional
managed trend artifact.

Review each proposal against the underlying sessions. Correlation or a single bad run is not a root cause.

## Apply or Roll Back

Preview one exact proposal ID:

```bash
.venv/bin/python scripts/agent_evolve_instructions.py --apply <evolution-id> --dry-run
```

Actual `--apply <evolution-id>` changes agent instructions and requires explicit user approval. `--rollback <evolution-id>` also requires explicit approval and the evolution ID from the log; an agent name is not a valid rollback target.

After an approved change, run the narrow instruction/registry validations and inspect the diff before committing. Never combine an evolution edit with unrelated product work.

## Decision Record

Record the session IDs, repeated behavior, root cause, exact instruction changed, expected measurable effect, preview result, approval, and rollback ID. Without that chain, leave the proposal unapplied.
