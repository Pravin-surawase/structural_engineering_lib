---
description: "Run a structured innovation research cycle — discover gaps, propose novel capabilities, prototype and validate"
mode: "innovator"
---

# Innovation Research Cycle

## Context

You are running a research and innovation cycle for structural_engineering_lib.
This is NOT about implementing existing features — it's about discovering what NO tool currently does well and building it.

## Steps

### Step 1: Scan

Read existing research:
```bash
ls docs/research/
```

Check coverage gaps:
```bash
.venv/bin/python scripts/parity_dashboard.py
```

Review innovation domains in `.github/agents/innovator.agent.md`.

Check what insights already exist:
```bash
ls Python/structural_lib/insights/
```

### Step 2: Choose Domain

Pick the highest-impact innovation domain from the Innovation Domains table.
Prioritize by: Engineering Value × Uniqueness × Feasibility.
Score feasibility BEFORE proceeding (must be ≥40/70).

### Step 3: Research

Use web search to find papers, open-source tools, industry databases.
Document findings — research without documentation is lost.

Key research targets:
- Academic papers (structural optimization, sustainability, ML in engineering)
- Open-source tools (OpenSees, SAP2000, ETABS APIs)
- Industry databases (ICE embodied carbon, EPD data)
- Code comparison resources (IS 456 vs ACI 318 vs EC2)

### Step 4: Propose

Write a formal innovation proposal in `docs/research/innovation-{{innovation_domain}}.md`.
Use the Innovation Proposal Template from `innovator.agent.md`.
Must include: Problem Statement, Proposed Approach, Validation Plan, Impact Assessment.
Must score ≥40/70 on feasibility.

### Step 5: Prototype

Create proof-of-concept code in `Python/structural_lib/research/`.
Delegate to specialist agents for implementation:
- @structural-math for math prototypes
- @api-developer for API endpoints
- @frontend for visualizations
- @tester for benchmarks and tests

### Step 6: Validate

Engineering validation:
- @structural-engineer for correctness verification
- @library-expert for professional standards compliance
- @security for safety implications review

Run benchmarks against known results where applicable.

## Completion Criteria

- [ ] Innovation domain selected and justified
- [ ] Feasibility scored ≥40/70
- [ ] Innovation proposal written in `docs/research/`
- [ ] At least one prototype created or delegated
- [ ] Validation plan defined with specific delegations
- [ ] TASKS.md updated with innovation items
- [ ] next-session-brief.md updated with research continuity