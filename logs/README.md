# logs/

This folder is for **local, machine-specific runtime logs** (debug output, ad-hoc run logs, temporary traces).

- Logs are **not** part of the library’s source of truth and should not be committed.
- Git ignores everything under `logs/` except this README.
- `model_usage.jsonl` stores local, repository-observable model/agent
  checkpoints. It never estimates billing tokens or cost; optional dashboard
  values are copied manually with `./run.sh session usage`.
- `agent_costs.jsonl` is a legacy calendar-day Git-activity proxy despite its
  historical name. Do not use it as a token or billing report.

If we ever decide to version specific diagnostic artifacts, put them in `docs/_references/` (or add a dedicated, explicitly versioned folder) rather than committing raw runtime logs.
