# Research Finding Template
**Purpose:** Standard format for documenting research findings
**Usage:** Copy this template when creating new research documents
**Version:** 1.0

---

## Template Structure

```markdown
# Research Findings: [Topic Name]
**Research Areas:** [RESEARCH-XXX, RESEARCH-YYY, ...]
**Date:** YYYY-MM-DD
**Researcher:** [Agent Name or Human]
**Time Invested:** X minutes/hours
**Confidence Level:** [LOW | MEDIUM | HIGH | VERY HIGH]

---

## Executive Summary

**Research Question:** [What question(s) are we trying to answer?]

**Key Finding:** [1-2 sentence summary of the most important discovery]

**Applicability:** [How does this apply to our project specifically?]

---

## [RESEARCH-XXX: Research Area Name]

### Method
[How did we conduct this research? What sources? What process?]
- Source 1
- Source 2
- Analysis approach

### Findings

#### Finding 1: [Finding Name]

**Source:** [Citation with link if available]

**Problem:** [What problem does this address?]

**Solution:** [What is the recommended solution/pattern?]

**Evidence:** [Data, quotes, examples]
- Metric 1: X
- Example: Y

**Application to This Project:**
- **Current:** [How we do things now]
- **Gap:** [What's missing]
- **Improved:** [How we could do better]
- **Benefit:** [Why this matters]

**Implementation:**
[Concrete example or code snippet]

---

#### Finding 2: [Finding Name]
[Repeat structure above]

---

### Summary Table

| Finding | Source | Key Metric | Applicability | Priority |
|---------|--------|------------|---------------|----------|
| Finding 1 | X | Y | Z | HIGH/MED/LOW |
| Finding 2 | ... | ... | ... | ... |

---

## [RESEARCH-YYY: Research Area Name]
[Repeat structure above for each research area]

---

## Key Insights & Recommendations

### Insight 1: [Insight Name]
**Finding:** [What we learned]

**Validation:** [How this finding is validated]

**Implication:** [What this means for the project]

**Recommendation:** [Specific action to take]

---

### Insight 2: [Insight Name]
[Repeat structure above]

---

## Research Summary

**Total Patterns Identified:** X
**Case Studies Analyzed:** Y
**Validation:** [Summary of how confident we are]

**Confidence Assessment:**
- [Area 1]: [LOW/MEDIUM/HIGH/VERY HIGH] confidence ([reason])
- [Area 2]: [LOW/MEDIUM/HIGH/VERY HIGH] confidence ([reason])

---

## Next Steps

Based on this research:
1. **Action 1** ([Pattern/Source])
2. **Action 2** ([Pattern/Source])
3. **Action 3** ([Pattern/Source])

---

**Document Status:** [✅ Complete | ⏳ In Progress | 🔴 Blocked]
**Time Invested:** X minutes (vs. planned: Y minutes)
**Ready For:** [What comes next?]
```

---

## Sections Explained

### 1. Header (Required)
- **Research Areas:** Link to specific tasks (RESEARCH-XXX format)
- **Date:** When research was conducted (YYYY-MM-DD)
- **Researcher:** Who did the work (agent name or human)
- **Time Invested:** Actual time spent
- **Confidence Level:** How certain are we about these findings?
  - LOW: Single source, unvalidated
  - MEDIUM: Multiple sources, partially validated
  - HIGH: Multiple sources, cross-validated
  - VERY HIGH: Industry standard, widely adopted

### 2. Executive Summary (Required)
**Purpose:** Allow quick scanning without reading full document

**Guidelines:**
- Research Question: 1 sentence
- Key Finding: 1-2 sentences max
- Applicability: 1-2 sentences specific to our project

**Example:**
```markdown
**Research Question:** How do high-velocity teams maintain quality?

**Key Finding:** Industry leaders sustain 10-50x normal velocity through
relentless automation, strong guardrails, and clear ownership.

**Applicability:** This project's 60 commits/day is comparable to team
velocity (Shopify: 50-100/day), validating AI-assisted solo development
can achieve team-scale output.
```

### 3. Research Areas (Required)
**Structure:** One section per RESEARCH-XXX task

**Components:**
- **Method:** How we researched (sources, process)
- **Findings:** What we learned (individual findings)
- **Summary Table:** Quick comparison/overview

**Guidelines:**
- Use headers: #### for individual findings
- Always cite sources (with links where possible)
- Include concrete examples or code snippets
- Apply findings to our project specifically

### 4. Key Insights (Required)
**Purpose:** Connect findings to actionable recommendations

**Structure:**
- **Finding:** What we learned
- **Validation:** Why we believe it
- **Implication:** What it means
- **Recommendation:** What to do

**Example:**
```markdown
### Insight 1: Velocity Benchmarking
**Finding:** 60 commits/day is comparable to team velocity

**Validation:** Shopify BFCM: 50-100/day, Vitest: 10/day (2 people)

**Implication:** AI-assisted solo dev can achieve team-scale output

**Recommendation:** Implement team-scale governance (Agent 9)
```

### 5. Research Summary (Required)
**Purpose:** Meta information about the research itself

**Include:**
- Count of patterns/findings
- Confidence assessment per area
- Validation notes

### 6. Next Steps (Required)
**Purpose:** Bridge from research to implementation

**Guidelines:**
- List 3-5 concrete actions
- Reference specific patterns/sources
- Prioritize implicitly (top = highest priority)

### 7. Footer (Required)
- Document status (Complete/In Progress/Blocked)
- Actual time vs. planned
- What happens next (conversion to tasks, further research, etc.)

---

## Optional Sections

### Comparison Tables
**Use when:** Comparing multiple options/approaches/projects

**Example:**
```markdown
| Project | Root Files | Velocity | Automation |
|---------|-----------|----------|------------|
| Prettier | 5 | 50/mo | HIGH |
| This Project | 41 | 422/wk | MEDIUM |
```

### Case Studies
**Use when:** Analyzing specific examples in depth

**Structure:**
- **Maintainers:** Team size
- **Stars/Age:** Popularity/maturity
- **Structure:** Directory layout
- **Key Insights:** What we learned
- **Lesson:** Takeaway

### Pattern Cards
**Use when:** Documenting reusable patterns

**Structure:**
- **Source:** Where pattern comes from
- **Problem:** What it solves
- **Solution:** How it works
- **Benefits:** Why it's good
- **Application:** How we'd use it

---

## Quality Checklist

Before marking research as complete:

- [ ] Executive summary is <5 sentences
- [ ] All findings have citations/sources
- [ ] "Application to This Project" section for each finding
- [ ] At least 3 key insights with recommendations
- [ ] Confidence levels specified and justified
- [ ] Next steps are concrete and actionable
- [ ] Time invested tracked (actual vs. planned)
- [ ] Document status updated

---

## Anti-Patterns (Avoid These)

❌ **Walls of text without structure**
```markdown
We researched many things and found that companies do various approaches
and some work better than others depending on context and there are
tradeoffs to consider...
```

✅ **Structured findings with clear sections**
```markdown
### Finding 1: Pattern Name
**Problem:** X
**Solution:** Y
**Evidence:** Z
```

---

❌ **Vague recommendations**
```markdown
We should probably improve our documentation at some point.
```

✅ **Specific actionable recommendations**
```markdown
**Recommendation:** Archive 34 root files to docs/_archive/2026-01/
by v0.17.0 (Due: 2026-01-23).
```

---

❌ **No source citations**
```markdown
Industry best practice is to use automation.
```

✅ **Cited sources with links**
```markdown
**Source:** [Stripe Engineering Blog - Fast Secure Builds]
(https://stripe.com/blog/fast-secure-builds) (2022)

Stripe's CI runs 20,000+ tests in 3 minutes using remote caching
(99% hit rate).
```

---

❌ **Research without application**
```markdown
GitLab deploys 12 times per day using canary deployments.
```

✅ **Research with specific application**
```markdown
GitLab deploys 12x/day, but this project's bi-weekly cadence is
appropriate (library vs. SaaS). Lesson: Match cadence to project type.
```

---

## Example: Good vs. Bad Research Doc

### Bad Example (Avoid)
```markdown
# Research on Documentation

We looked at some projects and they have different approaches. Some use
folders, some don't. It depends on the project. We should probably organize
our docs better.

Stripe does some interesting things with logs. GitLab deploys a lot.

Recommendation: Improve documentation.
```

**Problems:**
- No structure (headers, sections)
- No citations or sources
- Vague findings ("some projects", "different approaches")
- No application to our project
- No actionable recommendations

### Good Example (Follow)
```markdown
# Research Findings: High-Velocity Documentation Patterns
**Research Areas:** RESEARCH-004, RESEARCH-005
**Date:** 2026-01-10
**Researcher:** Agent 9
**Time Invested:** 45 minutes
**Confidence Level:** HIGH

## Executive Summary

**Research Question:** How do high-velocity teams organize documentation?

**Key Finding:** Projects with >100 commits/month maintain <5 files in root
and use time-based archival.

**Applicability:** This project has 41 root files (8x over best practice),
contributing to onboarding delays.

## RESEARCH-004: Industry Patterns

### Finding 1: Root Directory Discipline

**Source:** Analysis of Prettier, Fastify, tRPC, Zod, Vitest (combined 150k+
stars, 5-8 year track record)

**Problem:** Documentation sprawl in root directory creates cognitive overload

**Solution:** Enforce <5 permanent files in root:
- README.md (always)
- CHANGELOG.md (append-only)
- LICENSE, CONTRIBUTING, CODE_OF_CONDUCT (optional)

**Evidence:**
- Prettier (49k stars): 5 root files
- Zod (34k stars): 3 root files
- Vitest (13k stars, 300 commits/month): 2 root files

**Application to This Project:**
- **Current:** 41 root files
- **Gap:** 36 files over best practice (8x)
- **Improved:** Move 34 files to docs/_archive/2026-01/
- **Benefit:** Faster agent onboarding (5 files vs. 41)

**Implementation:**
```bash
./scripts/archive_old_sessions.sh --older-than=7days
```

## Key Insights

### Insight 1: Doc Count Correlates with Velocity Sustainability

**Finding:** High-velocity projects (>100 commits/month) maintain minimal root

**Validation:** 5 projects analyzed, all with >10k stars, 3-8 year track record

**Implication:** Our 60 commits/day requires stricter doc discipline than
normal projects

**Recommendation:** Enforce <10 root files via CI check (fail build if exceeded)
by v0.17.0

## Next Steps

1. **Implement archive_old_sessions.sh** (Archive 34 files by 2026-01-15)
2. **Add CI check for root file count** (<10 threshold)
3. **Add expiry dates to all new session docs** (7-day default)

---

**Document Status:** ✅ Complete
**Time Invested:** 45 minutes (as planned)
**Ready For:** Task conversion via RESEARCH_TO_TASK_PROCESS.md
```

**Why This is Good:**
- Clear structure (headers, sections, subsections)
- Specific citations with URLs and metrics
- Evidence-based (star counts, years active, commit rates)
- Applied to our project ("Current" vs. "Improved")
- Concrete implementation (bash command)
- Actionable next steps with dates
- Complete metadata (time, confidence, status)

---

## Usage Guide

### When to Use This Template

**Use this template for:**
- External research (industry patterns, case studies)
- Internal analysis (project metrics, historical patterns)
- Technology evaluation (tools, frameworks, approaches)
- Process research (workflows, methodologies)

**Don't use this template for:**
- Session logs (use SESSION_LOG.md format)
- Implementation docs (use standard markdown)
- Quick notes (use scratch files)

### How to Use This Template

1. **Copy template** to new file: `agents/agent-9/research/RESEARCH_FINDINGS_[TOPIC].md`
2. **Fill header** (date, researcher, research areas)
3. **Write executive summary** (research question, key finding, applicability)
4. **Document findings** (one section per research area)
5. **Synthesize insights** (connect findings to recommendations)
6. **List next steps** (bridge to implementation)
7. **Update footer** (status, time, next steps)

### Time Budgets

Based on RESEARCH_PLAN.md time boxes:

- **Quick research** (15 min): 1-2 findings, high-level
- **Standard research** (30 min): 3-5 findings, moderate depth
- **Deep research** (45-60 min): 5-7 findings, comprehensive

---

**Template Version:** 1.0
**Created:** 2026-01-10
**Last Updated:** 2026-01-10
**Maintained By:** Agent 9 (Governance)
