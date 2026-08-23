---
owner: Agent Governance
status: active
last_updated: 2026-08-23
doc_type: reference
---

# Agent Instruction Composition

Agent platforms load repository instructions differently. There is no single
universal precedence ladder shared by Claude Code, GitHub Copilot, VS Code, and
Codex. This repository therefore separates canonical policy from platform
loading and validates the result semantically.

## Ownership Model

| Surface | Owner | Contract |
|---|---|---|
| `AGENTS.md` | Cross-agent repository policy | Canonical safety, architecture, Git, session, and execution rules |
| `CLAUDE.md` | Claude Code entry | Imports `AGENTS.md`; adds loading guidance only |
| `.github/copilot-instructions.md` | Copilot global entry | Concise standalone baseline compatible with `AGENTS.md` |
| `.github/copilot/instructions.md` | Compatibility path | Pointer only; no executable workflow |
| `.github/instructions/*.instructions.md` | Maintained path rules | Narrow file-specific additions |
| `.claude/rules/*.md` | Claude path projections | Exact body match with the maintained GitHub path rule |
| `.github/agents/*.agent.md` | Role prompts | Role-specific scope; may not weaken cross-agent safety |
| `agents/agent_registry.json` | Role authority | Names, permissions, skills, and routing metadata |
| `.github/skills/*/SKILL.md` | Workflow authority | Exact procedure for a named skill |
| `.github/prompts/*.prompt.md` | Invocation templates | Task templates, not independent policy |
| `scripts/control-plane.json` | Command authority | Operations, commands, aliases, and permissions |

More specific or role-focused guidance may narrow the work. It may not weaken
authorization, protected-source, Git-preservation, release, professional-
approval, or destructive-action boundaries. If two loaded instructions would
materially change the outcome, preserve the stricter safety boundary and stop
before mutation until the conflict is resolved.

## Platform Loading

- Codex discovers `AGENTS.md` from the repository hierarchy; a nearer nested
  `AGENTS.md` or `AGENTS.override.md` can add narrower directory guidance.
- Claude Code loads `CLAUDE.md`, its imports, and matching `.claude/rules/`.
- Copilot support for `AGENTS.md` varies by surface, so the concise global
  Copilot file must remain safe when loaded alone.
- VS Code agent, skill, and prompt files add role or task context; their
  executable commands still come from the repository control plane.

## Validation

Run both checks after changing any instruction surface:

```bash
./scripts/python_runtime.sh scripts/check_instruction_drift.py
./scripts/python_runtime.sh scripts/config_precedence.py audit
```

The first check requires exact scoped-rule body parity and audits the semantic
contract. The second reports the composed files for a path and rejects known
unsafe or contradictory ownership patterns. Approximate textual similarity is
not sufficient evidence of consistent behavior.

## Adding Guidance

1. Update an existing canonical owner when possible.
2. Put cross-agent policy in `AGENTS.md`.
3. Put a path-specific rule in `.github/instructions/` and update its exact
   `.claude/rules/` projection in the same patch.
4. Put role metadata in the registry and role behavior in one agent file.
5. Put repeatable procedures in a skill and task wording in a prompt.
6. Add commands only through `scripts/control-plane.json` and refresh its
   deterministic compatibility projection.
7. Run the two validators above and the affected governance tests.
