---
owner: Main Agent
status: active
last_updated: 2026-08-23
doc_type: spec
complexity: intermediate
tags: [maintenance, agents, instructions, control-plane, token-efficiency]
---

# MAINT-0134 Agent Instruction Consolidation Plan

## Decision

MAINT-0134 consolidates the repository's prose control plane before INDIA-3-G0
continues. It repairs confirmed instruction conflicts and makes platform
composition explicit without deleting agents, skills, prompts, branches,
worktrees, historical evidence, or compatibility files.

The implementation baseline is merged `origin/main` commit
`40aa5864194a7296caea13def1ccf82f44aca917`. The isolated implementation lane
is `codex/maint-0134-agent-instructions`, and its worktree-bound runtime must
report `source_bound=true` before verification.

## Confirmed root causes

1. Claude, Copilot, and agent-specific entry files copied common policy instead
   of composing one repository contract. Later repairs changed only some copies.
2. `check_instruction_drift.py` compares four file pairs by approximate text
   similarity. It does not validate commands, platform entry files, prompts,
   agent definitions, legacy routing, or safety semantics.
3. `config_precedence.py` documents one invented global precedence order even
   though Codex, Claude, and Copilot discover and combine instructions
   differently.
4. `agent_brief.sh` passes newline-separated closed task IDs through an `awk -v`
   argument. The system `awk` parses those embedded newlines as source text,
   emits `newline in string`, and falsely reports no active tasks.
5. The live agents context routes readers first to `agents/README.md`, even
   though that document labels itself legacy and still contains age-based
   archival and worktree-cleaning instructions.

## Platform contract

| Surface | Owned responsibility |
|---|---|
| `AGENTS.md` | Cross-agent safety, architecture, Git, session, verification, and repository invariants |
| `CLAUDE.md` | Import `AGENTS.md`, then add only Claude-specific discovery/context guidance |
| `.github/copilot-instructions.md` | Concise Copilot repository baseline for Copilot surfaces that do not load `AGENTS.md` |
| `.github/instructions/` | Maintained path-scoped implementation rules |
| `.claude/rules/` | Claude projections with bodies matching the maintained path-scoped rules |
| `agents/agent_registry.json` | Machine-readable role, permission, and skill assignments |
| `.github/agents/` | Copilot role deltas and handoff UI, never repository-global policy ownership |
| `.github/skills/` | Reusable multi-step workflows |
| `.github/prompts/` | Task invocation templates, never independent safety or command authority |
| `scripts/control-plane.json` | Executable commands, permissions, aliases, and compatibility projection source |

`AGENTS.md` safety and authorization rules may be narrowed only by a more
restrictive platform or path rule. No agent, prompt, skill, or platform delta
may weaken them. Machine-enforced permissions and repository hooks remain
enforcement authorities; prose does not override them.

## Implementation packets

### Packet A — authority and entry paths

- Replace the duplicated `CLAUDE.md` body with `@AGENTS.md` plus a small
  Claude-specific delta.
- Reduce `.github/copilot-instructions.md` to a two-page-scale baseline that
  states only Copilot-specific discovery plus the minimum repository invariants
  needed on Copilot surfaces that do not load `AGENTS.md`.
- Turn `.github/copilot/instructions.md` and `agents/README.md` into pointer-only
  compatibility surfaces with no executable workflow of their own.
- Remove enumerated agent/skill/prompt catalogs from `AGENTS.md`; route discovery
  to the registry, tier catalog, and live folders instead.
- Correct `docs/architecture/config-precedence.md` to document platform
  composition rather than a universal override hierarchy.

### Packet B — semantic convergence

- Replace every active instruction reference to direct `.venv/bin/python` or
  `.venv/bin/pytest` execution with `./scripts/python_runtime.sh`.
- Make `./run.sh session begin --task-id <task> --agent <role>` the single task
  start contract in entry files, the session prompt, and active agent guidance.
- Remove final generated-index refresh language from active instructions.
- Remove age-based archival, generic branch/worktree cleaning, and non-Codex
  commit handoffs from active agent guidance.
- Mirror maintained file-scoped instruction bodies into `.claude/rules/` while
  retaining platform-specific frontmatter.
- Repair `agent_brief.sh` so multiple externally closed task IDs cannot corrupt
  active-task parsing, and update its role commands to the repository launcher.

### Packet C — executable validation

- Upgrade `check_instruction_drift.py` from approximate similarity reporting to
  an exact projection check plus cross-surface semantic contract audit.
- Update `config_precedence.py` to describe platform composition and remove the
  false claim that agent-specific prose overrides repository safety.
- Add focused regression tests for Claude import composition, worktree-safe
  commands, session-start convergence, legacy-route retirement, governance
  handoffs, file-rule parity, and multiline closed-task handling.
- Update control-registry descriptions without adding a second operation or
  weakening the existing quick/full gates.

## Non-goals

- No INDIA-3 engineering interpretation, formula, source, benchmark, or release
  work.
- No agent, skill, prompt, branch, worktree, document, or compatibility-file
  deletion.
- No permission expansion, model change, Fast-mode change, GitHub settings
  change, or release action.
- No mass rewrite of specialist role content whose commands and authority are
  already correct.
- No replacement of repository hooks or machine permission enforcement with
  prose checks.

## Acceptance criteria

1. `CLAUDE.md` imports `AGENTS.md`, stays below 200 lines, and contains no copied
   repository-global workflow.
2. `AGENTS.md`, `CLAUDE.md`, and the Copilot orchestrator entry stay below the
   repository's 24,000-byte active-instruction warning threshold.
3. The active instruction surface contains zero direct `.venv/bin/python` or
   `.venv/bin/pytest` commands.
4. All task-start surfaces use `session begin`; compatibility-only references
   to `session brief` or `session start` are explicitly labelled and are not
   presented as the task-start workflow.
5. Claude and Copilot file-scoped rule bodies are exact normalized matches.
6. `./run.sh context show agents` no longer routes readers to legacy executable
   guidance.
7. The governance agent contains no commit handoff, age-based archival, or
   generic branch/worktree-cleaning instruction.
8. A live agent brief emits no `awk` error and truthfully lists the active task
   even when the shared ledger contains multiple closed task IDs.
9. Focused instruction, session, control-plane, context, and token-efficiency
   checks pass; the frozen candidate then passes `./run.sh check --quick` once.
10. The final diff contains no INDIA-3 source or engineering-behavior change and
    no unrelated worktree mutation.

## Verification plan

After all intended content freezes, run one consolidated sequence:

```bash
./scripts/python_runtime.sh -m pytest \
  Python/tests/test_agent_governance_automation.py \
  Python/tests/test_session_automation.py \
  Python/tests/test_token_efficiency.py -q
./scripts/python_runtime.sh scripts/check_instruction_drift.py
./scripts/python_runtime.sh scripts/config_precedence.py audit
./run.sh control validate
./run.sh context validate
./run.sh efficiency check
./run.sh check --quick
./run.sh check
```

If an outcome-changing repair modifies the frozen candidate, rerun only the
affected focused evidence and then the consolidated quick gate once.

## Source basis

- OpenAI Codex documents repository instruction discovery through `AGENTS.md`
  and directory-local overrides:
  <https://developers.openai.com/codex/guides/agents-md>.
- Anthropic documents importing `AGENTS.md` from `CLAUDE.md`, recommends concise
  project instructions, and warns that conflicting instructions may be chosen
  arbitrarily:
  <https://code.claude.com/docs/en/memory>.
- GitHub documents that Copilot instruction-file support varies by feature;
  `.github/copilot-instructions.md` remains the repository-wide surface while
  `AGENTS.md` support is not universal:
  <https://docs.github.com/en/copilot/reference/custom-instructions-support>.

## Result

The candidate is implementation-complete:

- `AGENTS.md` is 22,705 bytes, `CLAUDE.md` is 38 lines/1,449 bytes, the global
  Copilot entry is 3,583 bytes, and the Copilot orchestrator is 17,943 bytes.
- The maintained instruction surface contains zero direct checkout-specific
  Python or pytest commands.
- All four GitHub/Claude scoped-rule bodies are exact normalized matches.
- The semantic instruction and composition audits report no conflicts.
- The multiline closed-task reproducer lists the live task with no `awk`
  parse error.
- Control validation reports 115 active operations and 101/101 registered
  top-level scripts with a current deterministic compatibility projection.

The frozen evidence is
`docs/verification/maint-0134-instruction-consolidation-evidence.json`. Hosted
integration facts remain external to this immutable candidate.
