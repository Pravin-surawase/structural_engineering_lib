# CLI + AI Discoverability Plan

Goal: Make CLI usage and command inventory easy for humans and AI to find without bloating `README.md`.

Scope
- CLI help text for `python -m structural_lib` and subcommands.
- Canonical CLI reference in `docs/cookbook/cli-reference.md`.
- AI discovery metadata via `llms.txt` at repo root.
- Light cross-links from docs index.

Non-goals
- No new CLI commands or flags.
- No behavior or schema changes.
- No VBA changes.

Principles
- Single source of truth for full CLI command list: `docs/cookbook/cli-reference.md`.
- README stays short; only links to canonical docs.
- AI-friendly summary is separate (`llms.txt`).
- Examples are copy-paste runnable and match actual CLI behavior.

Deliverables
- `llms.txt` with summary, install, import, CLI list, and links.
- Polished CLI help output (clear required args, examples, actionable errors).
- CLI reference updated to match current schema and outputs.
- Doc index links pointing to CLI reference (and `llms.txt` if desired).

Acceptance Criteria
- `python -m structural_lib --help` and each subcommand help text is clear and example-rich.
- `docs/cookbook/cli-reference.md` matches current CLI inputs/outputs.
- `llms.txt` is present and accurate.
- README remains concise (no full CLI dump).

Phases
0) Inventory
   - Confirm current CLI subcommands and outputs.
   - Identify doc locations referencing CLI.
1) AI summary
   - Add `llms.txt` with minimal, accurate content.
2) CLI help pass
   - Tighten argparse help text and add examples per subcommand.
3) CLI reference sync
   - Align `docs/cookbook/cli-reference.md` with current schema and outputs.
4) Cross-links
   - Ensure docs index and README link to the CLI reference (and optionally `llms.txt`).

Open Questions
- Should `llms.txt` be linked from README or only from docs index?
- Do we want a machine-readable CLI spec (e.g., `--help-json`) in a future pass?

Status
- 2025-12-27: Drafted plan; tasks added to board.
- 2025-12-27: Completed deliverables (CLI help pass, CLI reference sync, llms.txt, cross-links).
