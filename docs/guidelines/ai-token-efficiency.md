---
owner: Main Agent
status: active
last_updated: 2026-08-07
doc_type: guideline
---

# AI Token-Efficiency Policy

This is the canonical low-token operating policy for AI-assisted work in this
repository. It controls avoidable context and agent fan-out without weakening
engineering, test, or Git safety gates.

## Defaults

1. Keep one parent task active for this project. Finish, pause, or stop it
   before starting a separate parent task.
2. Use GPT-5.6 Terra at medium reasoning for normal implementation, testing,
   documentation, and review.
3. Use Luna, when the active client exposes it, for simple searches, status
   checks, extraction, formatting, and small mechanical edits.
4. Use Sol only after user approval for genuinely difficult architecture,
   conflicting safety constraints, structural-math risk, or a final high-risk
   review.
5. Keep Fast mode off. Enable it only when the user explicitly chooses speed
   over credit efficiency for a time-sensitive task.

Project-local defaults live in [`.codex/config.toml`](../../.codex/config.toml).
An explicit model choice by the user still takes precedence.

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

- Read folder `index.json` or `index.md` before individual files.
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

1. Inspect only affected files and existing patterns.
2. Implement one bounded issue.
3. Run the narrowest relevant test or lint command while iterating.
4. Add one or two independent reviews only when risk justifies them.
5. Run `./run.sh check --quick` before committing.
6. Run the full project or release gate once at closeout. Repeat only the failed
   portion unless the fix can affect other categories.

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

## Reusable Task Preamble

```text
Work in low-token mode.

Use one parent task. Default to Terra at medium reasoning and keep Fast mode
off. Do not use Sol without asking me first. Default to no subagents; use no
more than two only for independent, bounded work. Give them a concise task
packet and no full conversation history. Inspect only affected indexes and
files. Use targeted tests while developing and run the full gate once at
closeout. Close subagents immediately, report the result, and stop.
```

## Official References

- [Codex models](https://learn.chatgpt.com/docs/models)
- [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Codex Speed and Fast mode](https://learn.chatgpt.com/docs/agent-configuration/speed)
- [Codex pricing and usage](https://learn.chatgpt.com/docs/pricing)
- [Codex slash commands](https://learn.chatgpt.com/docs/reference/slash-commands)
- [Codex project configuration](https://learn.chatgpt.com/docs/config-file/config-basic)

