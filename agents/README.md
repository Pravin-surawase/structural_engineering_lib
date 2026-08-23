# Agent Infrastructure Compatibility Guide

This file is a human-facing pointer, not an executable workflow or routing
authority. Older links may still arrive here, so it remains intentionally
small.

Use these maintained owners:

- `../AGENTS.md` — canonical cross-agent repository contract.
- `agent_registry.json` — role, permission, skill, keyword, and routing truth.
- `../.github/agents/*.agent.md` — platform role prompts.
- `../.github/skills/skill_tiers.json` and `../.github/skills/*/SKILL.md` —
  workflow catalog and procedures.
- `../.github/prompts/*.prompt.md` — invocation templates.
- `../scripts/control-plane.json` — operation, command, alias, and permission
  truth.

For bounded live context, run `./run.sh session brief --agent <role>` or
`./run.sh context show agents`. Start actual work once with
`./run.sh session begin --task-id <task> --agent <role>`.

Do not add role-chain catalogs, copied agent inventories, cleanup instructions, or
command catalogs here. Their maintained owners are listed above.
