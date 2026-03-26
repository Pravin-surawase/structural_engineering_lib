# AI Agent Effectiveness Research: Current State & Improvements

**Type:** Research
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-01-23
**Last Updated:** 2026-01-23
**Related Tasks:** TASK-AGENT-EFFICIENCY

---

## Executive Summary

This project uses AI agents for **100% of code development and maintenance**. We have strong infrastructure, but agent effectiveness is still bottlenecked by knowledge freshness, context limits, and documentation sprawl.

**Current strengths (real, working):**
- **Unified onboarding:** `./scripts/agent_start.sh` + `scripts/start_session.py`
- **Automation catalog:** 143 scripts tracked in `scripts/index.json` (updated 2026-01-21)
- **Duplication controls:** `docs/docs-canonical.json`, `scripts/check_doc_similarity.py`, `scripts/check_duplicate_docs.py`
- **Enforcement:** Git hooks + pre-commit checks block manual git and enforce metadata

**Persistent issues (observed in this repo):**
- **Knowledge cutoff / tool drift** → agents suggest outdated models/libs/commands
- **Context limits** → partial reading and missed rules
- **Document duplication + naming drift** → multiple files for one topic
- **Automation underuse** → manual work despite existing scripts
- **Session clutter** → new docs created each session, hard to find the canonical source

**Goal:** make the system *practical* for real agents: shorter context, clearer canonical docs, stronger duplication gates, and mandatory verification for volatile info.

---

## Table of Contents

1. [Current Infrastructure Inventory](#1-current-infrastructure-inventory)
2. [Problem Analysis (Repo Reality)](#2-problem-analysis-repo-reality)
3. [External Best Practices & Research](#3-external-best-practices--research)
4. [Gap Analysis](#4-gap-analysis)
5. [Proposed Improvements (Practical)](#5-proposed-improvements-practical)
6. [Implementation Roadmap](#6-implementation-roadmap)
7. [Success Metrics](#7-success-metrics)
8. [Appendix: Evidence & References](#8-appendix-evidence--references)

---

## 1. Current Infrastructure Inventory

### 1.1 Onboarding System (Working Today)

**Primary entrypoint:** `docs/getting-started/agent-bootstrap.md`

**Mandatory flow:**
1. `./scripts/agent_start.sh --quick`
2. Read: `agent-essentials.md → ai-context-pack.md → TASKS.md`
3. Follow `.github/copilot-instructions.md` rules

### 1.2 Core Onboarding Docs (Active)

| Document | Purpose | Priority |
|----------|---------|----------|
| `docs/getting-started/agent-bootstrap.md` | First 30 seconds | P0 |
| `docs/getting-started/agent-essentials.md` | 50-line critical rules | P0 |
| `docs/getting-started/ai-context-pack.md` | Project summary, golden rules | P1 |
| `.github/copilot-instructions.md` | All rules, mandatory | P1 |
| `docs/agents/guides/agent-quick-reference.md` | Emergency cheat sheet | P2 |
| `docs/agents/guides/agent-workflow-master-guide.md` | Complete workflows | P1 |
| `docs/reference/known-pitfalls.md` | Engineering mistakes | P2 |
| `docs/contributing/session-issues.md` | Recurring friction + fixes | P2 |

**Reality:** These docs total **7,000+ lines** and exceed a typical agent context window. The system *must* be selective and task-specific.

### 1.3 Automation (143 Scripts)

**Catalog:** `scripts/index.json` and `scripts/automation-map.json`

**Discovery:** `scripts/find_automation.py "task"`

**Key automation areas:**
- Git workflow (commit/PR automation)
- Validation + scanners
- Documentation tooling (metadata, duplication checks)
- Safe file operations
- Session management

### 1.4 Enforcement & Guardrails

| Mechanism | Purpose | Effect |
|----------|---------|--------|
| Git hooks | Block manual git | Prevents conflicts + policy violations |
| Pre-commit checks | Metadata/formatting | Enforces documentation hygiene |
| Automation maps | Discovery | Helps agents find scripts quickly |

---

## 2. Problem Analysis (Repo Reality)

### 2.1 Knowledge Cutoff & Tool Drift

**Observed:** Agents propose outdated models, commands, or APIs. Example: invalid model names and deprecated CLI flags have appeared in session work.

**Root cause:** Agents cannot know which info is stale unless explicitly forced to verify.

**Impact:** Rework, broken builds, incorrect docs.

**Required fix:** Explicit *verify-online* workflow for volatile info (models, versions, APIs, commands).

### 2.2 Context Window Limits → Partial Reading

**Observed:** Agents skip mid-file rules and miss critical details (especially in long docs).

**Root cause:** Long docs + token limits → agents read only headers/summary.

**Impact:** Repeated mistakes, duplicated implementations.

**Required fix:** Shorter rule tiers + task-specific context packs.

### 2.3 Document Duplication & Naming Drift

**Observed:** Multiple documents for the same topic (e.g., bootstrap, git workflow, AI guides). Agents create new docs instead of updating canonical ones.

**Root cause:** No hard gate at doc creation time; naming conventions are informal.

**Impact:** Search fatigue, contradictory guidance, higher onboarding time.

**Required fix:** Pre-creation similarity checks + enforced naming conventions.

### 2.4 Automation Underuse

**Observed:** Agents do manual work even when scripts exist (link fixing, file moves, git operations, doc checks).

**Root cause:** Discovery friction (catalog too long, not in context).

**Impact:** Higher error rate, slower delivery.

**Required fix:** “Before You Do It Manually” checklist + automation prompts inside onboarding.

### 2.5 Session Document Clutter

**Observed:** Session-specific docs accumulate and are hard to find; multiple “final” files exist.

**Root cause:** No lifecycle enforcement at document creation time.

**Impact:** Navigation friction, duplication, stale docs.

**Required fix:** Lifecycle metadata + automated archiving rules.

### 2.6 Past Errors and Mistakes (From Repo Logs)

**Recurring issues captured in `docs/contributing/session-issues.md`:**
- Doc stamps introducing whitespace → pre-commit failures
- `gh pr checks --watch` timeouts → use async polling scripts
- Manual git attempts blocked by hooks

**Engineering pitfalls captured in `docs/reference/known-pitfalls.md`:**
- Unit conversion errors (kN vs N, kN·m vs N·mm)
- CI scope mismatch (local checks too narrow)
- Cross-language parity drift (Python vs VBA)

**Learning:** Even strong automation needs explicit reminders in onboarding and daily workflow.

---

## 3. External Best Practices & Research

### 3.1 Rules Files for Always-On Guidance

- **Cursor**: rules stored in `.cursor/rules` (or legacy `.cursorrules`), with guidance to keep them short and focused.
- **Windsurf**: rules live in `.windsurf/rules`, with explicit rule types and size limits.

**Takeaway:** Always-on, *short* rules reduce context load and errors.

### 3.2 Model Context Protocol (MCP)

- MCP standardizes how tools and resources are provided to agents.
- Emphasizes structured context injection instead of dumping long docs.

**Takeaway:** Prefer structured resources + tool interfaces over long “read everything” docs.

### 3.3 Long-Context Degradation ("Lost in the Middle")

- Research shows long-context models perform worse when relevant info is buried mid-context.

**Takeaway:** Put critical rules at the top, or surface them with targeted retrieval.

### 3.4 Retrieval-Augmented Generation (RAG)

- RAG combines retrieval with generation to improve factual accuracy on knowledge-intensive tasks.

**Takeaway:** Internal doc retrieval (semantic search) is better than loading entire docs.

### 3.5 Official Model Catalogs & Deprecations

- OpenAI and Anthropic publish official model lists and deprecation timelines.

**Takeaway:** Agents must verify model names and versions *online* before use.

---

## 4. Gap Analysis

| Area | Current State | Gap |
|------|---------------|-----|
| Freshness | Manual reminders | No mandatory online verification step |
| Naming | Informal conventions | No enforced naming checks |
| Duplication | Similarity scripts exist | Not enforced at doc creation time |
| Context | Tiered docs exist | No task-context selection automation |
| Automation | Catalog exists | Not surfaced in day-to-day workflow |
| Lifecycle | Archive scripts exist | No consistent triggers or metadata |

---

## 5. Proposed Improvements (Practical)

### 5.1 Freshness & Verification

**Add a visible rule in onboarding + copilot instructions:**
- “If info is likely to change (models, versions, commands), verify online.”

**Add lightweight markers for volatile sections:**
```
<!-- VERIFY_ONLINE: model names -->
```

### 5.2 Naming Conventions + Enforcement

- Publish a short naming standard for docs.
- Add a validation check in doc metadata tooling.

### 5.3 Duplication Gate at Doc Creation

- Extend `create_doc.py` to run `check_doc_similarity.py` before creating new docs.
- Require explicit `--allow-duplicate` override.

### 5.4 Automation-First Prompts

Add a “Before You Do It Manually” table to onboarding docs and copilot instructions.

### 5.5 Lifecycle Enforcement

- Tag session docs with lifecycle metadata.
- Use `archive_old_sessions.sh` monthly (or automate in CI).

---

## 6. Implementation Roadmap

### Phase 1 (This session)
- Update research doc with repo reality + external references
- Add doc naming conventions doc + index entries
- Wire naming checks into doc metadata validation
- Add duplication warnings to `create_doc.py`
- Reinforce automation + online verification in onboarding docs

### Phase 2 (Next 1–2 sessions)
- Add lightweight task-context routing (`task → docs/scripts`)
- Add lifecycle metadata defaults for session docs
- Tighten automation prompts in start_session output

### Phase 3 (Ongoing)
- Monthly dedup + archive run
- Track automation usage
- Review onboarding time and context issues

---

## 7. Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Duplicate docs created/month | 5–10 | <1 | `check_duplicate_docs.py` |
| Automation usage | ~30% | >80% | commit + script logs |
| Onboarding time | ~10 min | <5 min | agent self-report |
| Context errors (missed rules) | frequent | rare | session reviews |
| Doc discovery time | variable | <1 min | time-on-task tests |

---

## 8. Appendix: Evidence & References

### Internal Evidence (Repo)
- `docs/contributing/session-issues.md` — recurring mistakes and fixes
- `docs/reference/known-pitfalls.md` — engineering pitfalls
- `docs/docs-canonical.json` — canonical registry
- `scripts/check_doc_similarity.py` — duplication detection
- `scripts/check_duplicate_docs.py` — content overlap detection
- `scripts/automation-map.json` — task → script mapping
- `scripts/find_automation.py` — automation discovery

### External References (Best Practices)
- Cursor rules system (`.cursor/rules`): https://docs.cursor.com/context/rules
- Windsurf rules system (`.windsurf/rules`): https://docs.windsurf.com/windsurf/cascade/memories
- Anthropic MCP overview: https://docs.anthropic.com/en/docs/mcp
- "Lost in the Middle" long-context research (TACL 2024): https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00638/119630/Lost-in-the-Middle-How-Language-Models-Use-Long
- RAG (retrieval-augmented generation) paper (NeurIPS 2020): https://proceedings.neurips.cc/paper_files/paper/2020/file/6b493230205f780e1bc26945df7481e5-Paper.pdf
- OpenAI model catalog: https://platform.openai.com/docs/models
- OpenAI deprecations: https://platform.openai.com/docs/deprecations/overview
- Anthropic model overview: https://docs.anthropic.com/en/docs/models-overview

---

## 9. Next Steps (Actionable)

1. Implement Phase 1 items (doc naming + duplicate gate + onboarding updates).
2. Add tasks to `docs/TASKS.md` once changes are scoped.
3. Run a short onboarding drill: new agent → measure time to productivity.
4. Review outcomes in the next session log.
