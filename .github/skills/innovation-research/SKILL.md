---
name: innovation-research
description: "Run a structured innovation research cycle — discover gaps, propose novel capabilities, prototype and validate breakthrough ideas for structural engineering."
argument-hint: "Domain: 'sustainability' | 'generative-design' | 'ml-estimator' | 'failure-analysis' | 'knowledge-graph' | 'cross-code' | 'digital-twin' | 'construction-intel'"
---

# Skill: Innovation Research

Run a structured innovation research cycle to discover, validate, and prototype new capabilities for the structural engineering library.

## When to Use

- Starting a research session on a new innovation domain
- Evaluating feasibility of a proposed innovation
- Prototyping a new capability
- Reviewing the innovation backlog
- Surveying what competitors and open-source tools offer

## Pre-Flight Checks

```bash
# 1. Check existing research docs
ls docs/research/

# 2. Check library coverage gaps
.venv/bin/python scripts/parity_dashboard.py

# 3. Check existing insights/AI features
ls Python/structural_lib/insights/
grep "^def " Python/structural_lib/insights/*.py 2>/dev/null

# 4. Check current API surface
grep "^def " Python/structural_lib/services/api.py | head -20

# 5. Check innovation backlog in TASKS
grep -i "innovation\|research\|novel\|prototype" docs/TASKS.md
```

## Step-by-Step Cycle

### Step 1: Scan — Survey the Landscape

Review the Innovation Domains table in `.github/agents/innovator.agent.md`.
Check what exists in our codebase and what competitors offer.

```bash
# What do we already have?
ls Python/structural_lib/codes/is456/    # Implemented IS 456 modules
ls Python/structural_lib/insights/       # Existing smart features
ls Python/structural_lib/services/       # Service layer

# Use web search for competitor analysis (innovator has web access)
```

### Step 2: Identify — Find the Gap

Pick the highest-impact innovation domain that's still in "🆕 Research" status.
Consider:
- Engineering value (does this solve a real problem?)
- Uniqueness (does any other tool do this well?)
- Feasibility (can we build it with our stack?)

### Step 3: Research — Deep Dive

Use web search to find:
- Academic papers on the topic
- Open-source implementations (OpenSees, SAP2000 API, etc.)
- Industry standards and databases
- Benchmark data for validation

Document findings as you go — research without docs is lost.

### Step 4: Propose — Write Innovation Document

Create `docs/research/innovation-<domain>.md` using the Innovation Proposal Template from `innovator.agent.md`.

**Required sections:**
- Problem Statement
- Current State (what exists)
- Proposed Approach
- Data Requirements
- Implementation Sketch
- Validation Plan
- Impact Assessment

**Score feasibility** using the 7-criterion framework (must be ≥40/70 to proceed):

| Criterion | Score (1-10) |
|-----------|-------------|
| Engineering Value | ? |
| Uniqueness | ? |
| Feasibility | ? |
| Data Availability | ? |
| User Demand | ? |
| Code Integration | ? |
| Safety | ? |
| **Total** | **?/70** |

### Step 5: Prototype — Build Proof of Concept

Create prototype in `Python/structural_lib/research/` (create directory if needed).
File naming: `research_<domain>.py`

Delegate implementation to specialist agents:
- @structural-math — math prototypes, core types
- @api-developer — API endpoints
- @frontend — UI/visualizations
- @tester — validation tests, benchmarks

### Step 6: Validate — Engineering Validation

Hand off to:
- @structural-engineer — correctness and IS 456 compliance check
- @library-expert — professional standards review
- @security — safety and security implications

Run benchmarks against known results where applicable.

## Output

A complete innovation cycle produces:
- Innovation proposal in `docs/research/` (with feasibility score)
- Prototype code in `Python/structural_lib/research/` (if feasible)
- Validation results documented
- Delegation plan for production implementation
- TASKS.md updated with any new innovation tasks
- next-session-brief.md updated with research continuity

## Example Usage

```
# Research sustainability scoring domain
1. Check existing: ls Python/structural_lib/insights/
2. Web search: ICE database, embodied carbon calculation methods
3. Write proposal: docs/research/innovation-sustainability-scoring.md
4. Score feasibility: Engineering Value=9, Uniqueness=8, ...
5. Prototype: Python/structural_lib/research/research_sustainability.py
6. Validate: delegate to @structural-engineer
```

## Related Skills

- `/api-discovery` — check existing API before proposing new features
- `/is456-verification` — validate IS 456 compliance of prototypes
- `/new-structural-element` — if innovation requires a new element type
- `/architecture-check` — verify prototype fits 4-layer architecture