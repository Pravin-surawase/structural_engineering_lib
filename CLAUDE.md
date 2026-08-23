# CLAUDE.md — Claude Code Entry

@AGENTS.md

`AGENTS.md` is the canonical cross-agent contract for this repository. Read and
follow it before acting. Claude-specific files only describe how that contract
is loaded; they do not restate or override it.

## Claude Code Composition

- Claude Code loads this file and the imported root `AGENTS.md`.
- Path-scoped rules under `.claude/rules/` apply when their globs match.
- The bodies of `.claude/rules/*.md` are exact projections of the corresponding
  `.github/instructions/*.instructions.md` bodies. Change the maintained
  `.github/instructions/` source and its Claude projection in the same patch.
- Use `/context` when you need to confirm which Claude instruction files are
  loaded. Do not infer effective instructions from filenames alone.
- If two instructions appear inconsistent, preserve the stricter safety,
  authorization, source, Git, and release boundary and stop before mutation if
  the outcome would materially differ.

## Canonical Start and Validation

Start one bounded task with:

```bash
./run.sh session begin --task-id <task> --agent <role>
```

After any instruction change, run:

```bash
./scripts/python_runtime.sh scripts/check_instruction_drift.py
./scripts/python_runtime.sh scripts/config_precedence.py audit
```

Do not add project architecture, command catalogs, role lists, or duplicated
Git/session rules here. Update their canonical owners named in `AGENTS.md`.
