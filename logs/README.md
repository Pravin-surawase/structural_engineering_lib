# logs/

This folder is for **local, machine-specific runtime logs** (debug output, ad-hoc run logs, temporary traces).

- Logs are **not** part of the library’s source of truth and should not be committed.
- Git ignores everything under `logs/` except this README.

If we ever decide to version specific diagnostic artifacts, put them in `docs/_references/` (or add a dedicated, explicitly versioned folder) rather than committing raw runtime logs.
