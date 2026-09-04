---
owner: Main Agent
status: active
last_updated: 2026-09-01
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

Start one exact task with the smallest timed orientation pack:

```bash
./run.sh session begin --task-id <task> --agent <role>
```

Then:

- Treat the compact brief and environment result as the default orientation;
  do not reopen files or rerun Git queries that they already answered.
- Read the bounded recurrence controls shown by `session begin`. Each task's
  newest session entry references stable `RR-NNN` rows in
  `docs/verification/rework-recurrence-index.json`; counts, observed-time basis,
  and short solutions live once in that index, while deep evidence stays in the
  session log or linked postmortem. Subagent findings are deduplicated by the
  parent into that one entry.
- Use `./run.sh context show <area>` only for a concrete unresolved routing
  question, then targeted
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
5. Enter `CONTENT_FROZEN`, run `./run.sh format --write` once, and then run the
   affected focused tests, benchmarks, and architecture/import checks together
   as one consolidated selection. The formatter owns only changed Python,
   FastAPI, and C# paths and fails if bytes change outside that set.
6. Add one or two independent reviews only when risk justifies them. After the
   final candidate commit and independent acceptance, run
   `./run.sh check --candidate-integrity` exactly once; its consolidated manual
   all-files owner is read-only. A failure invalidates the candidate; record
   `INTEGRITY_REJECTED` to use the one repair path or enter `REPLAN` after the
   repair candidate. Preserve separately named raw artifact identities.
   Ordinary commits run only conflict, large-file, and live Git-operation
   safety guards; comprehensive assurance belongs to the PR.
7. If verification exposes an outcome-changing defect, repair its root cause,
   rerun the failed or affected narrow evidence, and repeat the consolidated
   gate once for the new frozen candidate.
8. Treat a multi-unit milestone branch as the publication and validation unit.
   Complete its sequential internal task IDs with only their affected focused
   tests and any required independent benchmark; do not run broad local gates,
   hosted CI, or create a PR for every internal unit. Once all intended units
   are integrated, run their union of focused evidence, then push once for one
   PR/hosted cycle.
   Installed-application evidence, mutation authority, and externally acquired
   artifacts remain separate milestone boundaries.
9. After all intended milestone branches are integrated, run the broad Python suite and
   `./run.sh check` (currently 32 checks) once at the cumulative closeout.
   Repeat only a failed portion unless the fix can affect other categories.
10. Run either broad gate before cumulative closeout only when an
   outcome-changing failure or repository-wide surface makes it necessary.
Required hosted checks are never deferred or bypassed for a publishable
milestone candidate; they are intentionally not invoked for unpublished
internal checkpoints on the same branch.

`check` JSON retains `duration` as the sum of child-check seconds for
compatibility; it is not elapsed time when checks run in parallel. Use `timings`
for non-overlapping planning, exact-input preparation, checks-wall and
postflight seconds plus their wall total. Console output reports the same
breakdown; output/usage-recording overhead is outside that gate interval.
Fingerprint preparation uses at most four independent exact-byte readers,
preserves deterministic sorted identities and never substitutes mtime/stat
metadata for bytes. Actual fresh cold-disk improvement must be measured on the
next worktree; a warm run or controlled-delay benchmark is not that proof.

Content-addressed reuse is evidence reuse, not a weakened gate. A receipt is
accepted only for the same check command, declared domains, current input bytes,
Python/platform/dependency identity, and verification contract. Failed or
malformed evidence is never stored or reused. Use `./run.sh check --no-reuse`
when a genuinely fresh execution is required; changing the input invalidates the
receipt automatically, so calendar-based cache resets are unnecessary.

Changed-path routing follows maintained callers and outcome owners, not a
headline folder category. Shared helper directories must be decomposed into
explicit helper-level impact rules when their callers differ. A genuinely
unknown or unclassified path remains fail-closed and selects every domain.

For work requiring independent acceptance, use these stricter efficiency
controls:

- one writer owns all mutable, shared, and generated surfaces;
- freeze acceptance rows, maintained callers, and context scope before editing;
- use focused gates during iteration; after content freezes, validate live
  context once and rerun the affected focused checks;
- only then commit an immutable local candidate for a read-only independent
  audit and return one consolidated blocker list after the full audit matrix;
- run no hosted CI before `PASS <head> <tree>` from that local audit;
- after PASS, run the full gate at cumulative milestone closeout (earlier only
  for repository-wide risk), then push once for one hosted validation cycle;
- allow the initial candidate plus one consolidated repair candidate; a second
  rejection requires contract/design re-planning; and
- if the audited head changes, invalidate the PASS rather than spending another
  hosted run on unaudited work.

For a release, freeze the prepared code candidate before its one exact-head
Weekly run. After review, one bounded publication packet may change only
`CITATION.cff`, `CHANGELOG.md`, the append-only release ledger, and the
authorization evidence while retaining the reviewed Python tree. Run the narrow
publication-surface and target-authorization checks on that packet; do not rerun
Weekly verification for those metadata-only changes. The TestPyPI rehearsal and
tag-triggered production workflow remain distinct publication gates.

The ignored Git-common ledger persists the executable sequence
`INTAKE → BOUNDED_UNITS → CONTENT_FROZEN → FORMATTED → FOCUSED_VERIFIED →
PREPARED → CANDIDATE → AUDIT_ACCEPTED → INTEGRITY_VERIFIED → FINAL_CLOSED →
PUSHED → HOSTED_PASSED → MERGED`. One rejection enters `REPAIR` and permits one
`REPAIRED_CANDIDATE`; a second enters `REPLAN` and blocks until an acceptance
file changes. An accepted candidate's integrity failure uses that same repair
allowance and is recorded separately from an audit rejection. Transitions,
timed commands, candidate heads, audit failures,
repair batches, focused retries, full-gate runs, the single hosted run, and total
elapsed time are machine-derived rather than caller-entered. Closeout derives
the seven non-overlapping phase intervals from transition timestamps, binds the
PR/merge commit, and proves accepted-candidate/merged-tree equality. It also
reports rework and network ratios. The read-only `session end` command does not
consume the start checkpoint or write a timing event; the pre-push guard records
its one successful `FINAL_CLOSED` transition.
Record closeout after exact post-merge verification and before starting the
next task; inspect an unexpected open task with `session usage --active --json`.

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
- Start through `session begin`, optionally record milestones roughly every
  2–3 hours, and record closeout after exact post-merge verification. The shared
  Git-common JSONL ledger projects retained legacy per-worktree records for
  history and records model, reasoning, derived elapsed time, automatic step
  durations, parent/subagent counts, optional manually copied dashboard values,
  verification, and Git state. It deliberately leaves token and billing fields
  empty because the repository cannot measure them.

If a historical task start is genuinely abandoned or replaced and its phase
timings cannot be reconstructed, do not fabricate a closeout. Record an exact
`superseded` checkpoint with a reason; it closes only the named active task and
records no elapsed-time, efficiency, candidate, PR, or integration claim.

```bash
./run.sh session begin --task-id TASK-XXX --agent governance --task "bounded scope"
./run.sh session delivery --to BOUNDED_UNITS --acceptance-path docs/task-contract.md
./run.sh session delivery --to CONTENT_FROZEN
./run.sh format --write
./run.sh session delivery --to FORMATTED
./run.sh session delivery --to FOCUSED_VERIFIED --evidence "targeted tests pass"
./run.sh session delivery --to PREPARED --evidence "owned docs and projections complete"
# Commit the candidate, record CANDIDATE, obtain independent audit acceptance,
# run candidate integrity once, push, record hosted PASS, then merge.
./run.sh session usage --checkpoint milestone --elapsed-min 120 \
  --verification "targeted tests pass" --notes "no subagents"
./run.sh session usage --active --json
./run.sh session usage --checkpoint superseded --task-id STALE-TASK \
  --notes "Exact successor task owns current work; no timing claim"
./run.sh session usage --checkpoint closeout --task-id TASK-XXX \
  --verification "delivery state MERGED; required hosted checks pass"
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
then run one consolidated focused selection after content freezes. Let the
batched PR own comprehensive candidate assurance; run the full local gate only
at a named cumulative or release boundary. Close subagents and stop
when done.
```

## Official References

- [Codex models](https://learn.chatgpt.com/docs/models)
- [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Codex Speed and Fast mode](https://learn.chatgpt.com/docs/agent-configuration/speed)
- [Codex pricing and usage](https://developers.openai.com/codex/pricing/)
- [Codex slash commands](https://learn.chatgpt.com/docs/reference/slash-commands)
- [Codex project configuration](https://learn.chatgpt.com/docs/config-file/config-basic)
