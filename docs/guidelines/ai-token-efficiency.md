---
owner: Main Agent
status: active
last_updated: 2026-08-23
doc_type: guide
---

# AI Token-Efficiency Policy

This is the canonical low-token operating policy for AI-assisted work in this
repository. It controls avoidable context and agent fan-out without weakening
engineering, test, or Git safety gates.

## Defaults

1. Keep one parent task active for this project. Finish, pause, or stop it
   before starting a separate parent task.
2. An explicit model and reasoning selection by the user controls. When the
   user explicitly delegates model choice for a task, the main orchestrator may
   choose suitable available parent and subagent profiles in proportion to task
   risk. Project defaults remain advisory in either case.
3. Luna is unavailable in the active runtime. Do not probe or attempt it. Use
   Terra Low for clear repeatable work and Terra Medium/High in proportion to
   implementation and risk.
4. Sol profiles require explicit user selection, case-specific approval, or
   delegated model-choice authority. Escalate only when the task risk or a
   concrete quality gap justifies it.
5. Spark is available as a bounded, preview, text-only lane for explicit, outcome-
   bounded documentation, automation, API/schema, and runnable-example work. It is
   not the baseline for engineering/math/release decisions, and preview billing
   remains explicitly unpriced in-project.
6. Keep Fast mode off. Enable it only when the user explicitly chooses speed
   over credit efficiency for a time-sensitive task.

## Model and Reasoning Matrix

The verified token rate card retains Luna as the accounting reference: Terra is
10x and Sol is 25x for the same input/cached-input/output token mix. This does
not make Luna an available routing option. Reasoning effort changes how many
tokens a task may consume, but OpenAI does not publish a fixed
Low/Medium/High/Extra High multiplier. Use the lowest available Terra profile
that reliably completes the work.

| Profile | Default use | Escalate when |
|---|---|---|
| Terra Low | Small code fixes with an obvious pattern | Targeted verification does not explain a failure |
| Terra Medium | Normal implementation and maintenance | Architecture, safety, or multiple systems interact |
| Terra High | Cross-layer debugging, architecture, security, release, IS 456 | A concrete unresolved quality gap justifies Sol |
| Terra Extra High | Rare, critical but bounded work | Sol may materially improve a high-value decision |
| Spark Low | Small, explicit bounded packets with deterministic checks and clear stop conditions | Task intent is ambiguous, impacts safety boundaries, or is not output-verifiable |
| Sol High | Explicitly selected important, complicated, or high-stakes execution | Obtain case-specific user approval |
| Sol Medium/Extra High | Exceptional Sol profiles | Obtain case-specific user approval |

Max is a quality-first single-agent mode. Ultra may create subagents. Both are
outside the routine project profiles and require case-specific approval. Fast mode
uses 2.5x the standard credits for currently documented GPT-5.6/5.5 models.

## Task-Aware Picker

Use the deterministic picker before selecting a model for a new bounded task:

```bash
./run.sh model --table
./run.sh model "fix the known FastAPI validation error"
./run.sh model "verify the release calculation" --risk critical
./run.sh model "plan the next architecture milestone" --important
./run.sh model "start and delegate the maintenance task" --orchestrator
```

The policy is stored in [`agents/model_policy.json`](../../agents/model_policy.json).
The picker is optional and advisory. Run it only when the user asks for a
recommendation, has not selected a model, or has delegated model choice. It
does not override an explicit user selection. Sol recommendations remain
approval-gated unless the user has delegated model choice for the current task.
Apply a parent-model recommendation with `/model` when the user chooses it or
the active client permits the delegated orchestrator to do so. Use a fresh task
when changing to a genuinely different issue.

## Orchestrator Contract

The user-selected orchestrator owns decomposition and acceptance, not just routing.
Before handing work to Terra, it provides a compact task packet with:

- one objective and explicit non-goals;
- exact files/paths and existing patterns to reuse;
- constraints, architecture/units/Git rules, and likely pitfalls;
- measurable acceptance criteria and the narrow test commands;
- expected return format: findings or changes, evidence, unresolved risks, and
  files touched.

The orchestrator keeps disjoint workstreams, avoids overlapping writes, and
does not pass full conversation history. After each handoff it reviews the diff
or findings, checks the requested evidence, tests integration assumptions, and
either accepts the result or returns a precise correction packet. It never
equates a subagent's confident report with verified completion.

Project-local efficiency defaults live in
[`.codex/config.toml`](../../.codex/config.toml). Parent `model` and
`model_reasoning_effort` are deliberately unset so an explicit user selection
or delegated orchestrator choice remains in control.

## Delegation Budget

- Default to no subagents for routine work.
- Use at most two concurrent subagents, and only for independent, bounded
  workstreams where parallelism materially improves quality or elapsed time.
- Prefer read-heavy delegation: focused exploration, log analysis, tests, or
  independent review. Avoid parallel writes to overlapping files.
- Give every subagent a compact task packet: objective, exact files or paths,
  constraints, precise question, expected output, and relevant commands.
- Do not fork the full conversation. In runtimes that expose history controls,
  use no inherited turns (`fork_turns="none"`) or the smallest useful recent
  slice.
- Ask for distilled findings with file references, not raw logs or a transcript.
- Close completed subagents immediately. Do not keep idle reviewers alive.

The named handoff chains in project documentation describe quality roles, not
mandatory agent processes. The parent agent normally performs the specialist,
test, documentation, and operations passes itself. Separate agents are reserved
for the bounded exceptions above.

## Context Budget

Start with the smallest orientation pack:

```bash
./run.sh session brief --agent <role>
sed -n '1,80p' docs/TASKS.md
git status --short --branch
```

Then:

- Use `./run.sh context show <area>` for authoritative routing, then targeted
  `rg`; request a bounded live inventory with
  `./run.sh context summary <area-or-folder>` only when useful.
- Search with `rg` and read only the matching sections.
- Load the full bootstrap, a full agent file, or large logs only when the task
  actually depends on them.
- Keep tool output bounded; return tails, summaries, or counts instead of full
  logs where possible.
- Use `/compact` when the same task must continue after substantial context
  growth. Start a fresh task with a concise handoff for a genuinely new issue.
- State each instruction once. Avoid repeating architecture, Git, and style
  rules already provided by `AGENTS.md`.

## Verification Ladder

The default cadence is implementation first, then one batched verification
sequence for the agreed bounded packet. A diagnostic check during implementation
is an exception used to guide or debug the change, not a ritual after each edit.

1. Inspect only affected files and existing patterns.
2. Complete the bounded implementation, its tests, documentation, evidence,
   and other intended versioned writes.
3. While implementing, run only the narrowest reproducer, test, lint, or
   diagnostic needed to answer a current question or repair a failure. Do not
   rerun quick, full, or unchanged suites after each edit.
4. Freeze the packet content and validate the live repository-context manifest;
   generic committed folder indexes require no refresh.
5. Run the affected focused tests, benchmarks, and architecture/import checks
   together as one consolidated selection.
6. Add one or two independent reviews only when risk justifies them, then run
   `./run.sh check --quick` once before committing and allow normal hooks to run.
   The hook calls the same quick orchestrator, so exact PASS receipts are reused
   instead of rerunning unchanged checks; Git-state checks always execute fresh.
7. If verification exposes an outcome-changing defect, repair its root cause,
   rerun the failed or affected narrow evidence, and repeat the consolidated
   gate once for the new frozen candidate.
8. For a multi-packet milestone, keep each completed packet to focused tests,
   independent benchmarks, architecture/import checks, the quick gate, normal
   commit hooks, and all required hosted PR checks.
9. After all intended packets are integrated, run the broad Python suite and
   `./run.sh check` (currently 31 checks) once at the cumulative closeout.
   Repeat only a failed portion unless the fix can affect other categories.
10. Run either broad gate before cumulative closeout only when an
   outcome-changing failure or repository-wide surface makes it necessary.
Required hosted checks are never deferred or bypassed.

Content-addressed reuse is evidence reuse, not a weakened gate. A receipt is
accepted only for the same check command, declared domains, current input bytes,
Python/platform/dependency identity, and verification contract. Failed or
malformed evidence is never stored or reused. Use `./run.sh check --no-reuse`
when a genuinely fresh execution is required; changing the input invalidates the
receipt automatically, so calendar-based cache resets are unnecessary.

For work requiring independent acceptance, use these stricter efficiency
controls:

- one writer owns all mutable, shared, and generated surfaces;
- freeze acceptance rows, maintained callers, and context scope before editing;
- use focused gates during iteration; after content freezes, validate live
  context once, rerun focused checks, and run the sole quick gate;
- only then commit an immutable local candidate for a read-only independent
  audit and return one consolidated blocker list after the full audit matrix;
- run no hosted CI before `PASS <head> <tree>` from that local audit;
- after PASS, run one full gate at closeout, then push once for one hosted run;
- allow the initial candidate plus one consolidated repair candidate; a second
  rejection requires contract/design re-planning; and
- if the audited head changes, invalidate the PASS rather than spending another
  hosted run on unaudited work.

Use non-overlapping timing labels: `contract/intake`, `writer implementation +
focused verification`, `independent local audit`, `writer rework`, `final local
closeout`, `hosted/network wait`, and `merge + post-merge verification`. Report
their sum as `total wall time`; do not count idle or network time in another
interval. At closeout report `candidate_heads`, `audit_rejections`,
`repair_batches`, `focused_gate_retries`, `full_gate_runs`,
`hosted_validation_runs`, `rework_minutes`, and `network_wait_minutes`.

Safety-critical structural calculations still require independent reference
validation. Token efficiency never replaces practicing-engineer review or the
IS 456 quality gate.

## Monitoring

- Use `/status` in Codex to inspect current context usage and rate limits.
- Use **Settings → Usage** for account/workspace usage and credits.
- `/usage daily` and `/usage weekly` are not current documented Codex desktop
  commands and must not be included in project prompts.
- Run `./run.sh efficiency check` to validate repository-side controls. This
  checks configuration and context proxies; it cannot read OpenAI billing.
- Run `./run.sh efficiency prompt` to print a reusable task preamble.
- Run `./run.sh model --table` to compare profiles, or pass a task description
  to receive a deterministic recommendation and explicit escalation trigger.
- Record start, milestone (roughly every 2–3 hours), and closeout checkpoints
  with `./run.sh session usage`. The local JSONL ledger records model,
  reasoning, elapsed time, parent/subagent counts, optional manually copied
  dashboard values, verification, and Git state. It deliberately leaves token
  and billing fields empty because the repository cannot measure them.

```bash
./run.sh session usage --checkpoint start --task-id TASK-XXX --task "bounded scope"
./run.sh session usage --checkpoint milestone --elapsed-min 120 \
  --verification "targeted tests pass" --notes "no subagents"
./run.sh session usage --checkpoint closeout --elapsed-min 210 \
  --verification "quick gate 9/9"
./run.sh session usage --summary --hours 24
```

The Claude model labels in `.github/agents/*.agent.md` and
`agents/agent_registry.json` are VS Code Copilot configuration. They are not
Codex routing inputs; Codex Terra/Sol choices live only in
`agents/model_policy.json` and project `.codex/config.toml`.

## Reusable Task Preamble

```text
Work in low-token mode.

Honor an explicit parent model and reasoning selection by the user. If the user
delegates model choice, select available parent and subagent profiles in
proportion to task risk. Repository defaults remain advisory. Keep Fast mode
off. Luna is unavailable; use Terra-low subagents for clear repetitive work
without probing Luna. Use Sol only after
explicit selection, case-specific approval, or delegated model-choice
authority. Default to no
subagents; use no more than two only for independent,
bounded work. Give each a concise packet with objective, exact files, non-goals,
pitfalls, acceptance criteria, tests, and return format—never full conversation
history. Verify every result before accepting it. Complete the bounded
implementation first; use a narrow diagnostic during editing only when needed,
then run one consolidated focused selection and one quick gate after content
freezes. Run the full gate once at cumulative closeout. Close subagents and stop
when done.
```

## Official References

- [Codex models](https://learn.chatgpt.com/docs/models)
- [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Codex Speed and Fast mode](https://learn.chatgpt.com/docs/agent-configuration/speed)
- [Codex pricing and usage](https://developers.openai.com/codex/pricing/)
- [Codex slash commands](https://learn.chatgpt.com/docs/reference/slash-commands)
- [Codex project configuration](https://learn.chatgpt.com/docs/config-file/config-basic)
