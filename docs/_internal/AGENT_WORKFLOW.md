# Agent Workflow System — Master Governance

**Status:** Active  
**Owner:** PM Agent  
**Purpose:** Define clear workflows, duties, and handoff protocols for multi-agent collaboration.

---

## 1. Core Philosophy

### 1.1 The Agent Mindset
- **Agents are specialists.** Each agent has a focused domain of expertise.
- **Agents don't assume.** When unsure, ask or escalate to PM.
- **Agents document.** Every decision, finding, or deliverable is recorded.
- **Agents handoff cleanly.** Provide complete context for the next agent.
- **Agents verify.** Check work from previous agents before proceeding.

### 1.2 The Human's Role
- **Final authority** on scope, priorities, and acceptance.
- **Provides requirements** (via CLIENT proxy or directly).
- **Reviews and approves** key decisions.
- **Can override** any agent recommendation.

---

## 2. Agent Roster & Responsibilities

| Agent | Domain | Primary Duties | Outputs |
|-------|--------|----------------|---------|
| **PM** | Governance | Scope, priorities, releases, conflicts | TASKS.md, RELEASES.md |
| **CLIENT** | Requirements | User stories, acceptance criteria | Requirements spec |
| **RESEARCHER** | Standards | IS Codes, algorithms, constraints | Research docs |
| **UI** | Interface | Sheet layouts, UX flows, forms | Mockups, specs |
| **DEV** | Implementation | Code, architecture, refactoring | .bas/.py files |
| **INTEGRATION** | Data | Schema, mapping, validation | Data specs |
| **TESTER** | Quality | Test cases, edge cases, validation | Test results |
| **DOCS** | Documentation | API refs, guides, changelog | .md files |
| **DEVOPS** | Delivery | Git, builds, releases, CI | Tags, releases |
| **SUPPORT** | Operations | Troubleshooting, known issues | TROUBLESHOOTING.md |

---

## 3. Standard Workflows

### 3.1 Feature Development Workflow
```
┌─────────────────────────────────────────────────────────────────┐
│                    FEATURE DEVELOPMENT FLOW                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. INTAKE          2. RESEARCH        3. DESIGN                │
│  ┌────────┐        ┌────────┐         ┌────────┐                │
│  │ CLIENT │───────▶│RESEARCH│────────▶│  PM    │                │
│  │        │        │        │         │  +UI   │                │
│  │Require-│        │IS Codes│         │  +DEV  │                │
│  │ments   │        │Algos   │         │Scope   │                │
│  └────────┘        └────────┘         │Design  │                │
│                                       └───┬────┘                │
│                                           │                      │
│  ┌────────────────────────────────────────▼─────────────────┐   │
│  │                                                           │   │
│  │  4. IMPLEMENTATION (Parallel)                            │   │
│  │  ┌─────────┐  ┌───────────┐  ┌──────────┐                │   │
│  │  │   DEV   │  │INTEGRATION│  │  TESTER  │                │   │
│  │  │Code M15 │  │Data Schema│  │Test Cases│                │   │
│  │  │Code M16 │  │           │  │          │                │   │
│  │  └────┬────┘  └─────┬─────┘  └────┬─────┘                │   │
│  │       │             │             │                       │   │
│  │       └─────────────┴─────────────┘                       │   │
│  │                     │                                     │   │
│  └─────────────────────┼─────────────────────────────────────┘   │
│                        ▼                                         │
│  5. VALIDATION       6. DOCS           7. RELEASE               │
│  ┌────────┐         ┌────────┐        ┌────────┐                │
│  │ TESTER │────────▶│ DOCS   │───────▶│DEVOPS  │                │
│  │Execute │         │API Ref │        │Merge   │                │
│  │Report  │         │Changelog        │Tag     │                │
│  └────────┘         └────────┘        │Release │                │
│                                       └────────┘                │
│                                            │                     │
│                                            ▼                     │
│                                       ┌────────┐                │
│                                       │   PM   │                │
│                                       │Ledger  │                │
│                                       │Update  │                │
│                                       └────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Bug Fix Workflow
```
PM (Triage) → TESTER (Reproduce) → RESEARCHER (Root Cause) 
    → DEV (Fix) → TESTER (Verify) → DEVOPS (Ship) → DOCS (Update)
```

### 3.3 Documentation Update Workflow
```
DOCS (Draft) → DEV (Technical Review) → PM (Approve) → DEVOPS (Commit)
```

---

## 4. Agent Handoff Protocol

### 4.1 Handoff Checklist
Every agent handoff MUST include:

| Item | Description |
|------|-------------|
| **Summary** | What was done in 2-3 sentences |
| **Deliverables** | List of files created/modified |
| **Decisions Made** | Key choices and rationale |
| **Open Questions** | Unresolved items for next agent |
| **Next Agent** | Who should receive this handoff |
| **Action Required** | Specific task for next agent |

### 4.2 Handoff Format
```markdown
## Handoff: [FROM_AGENT] → [TO_AGENT]
**Task:** TASK-XXX  
**Date:** YYYY-MM-DD

### Summary
[2-3 sentence summary of completed work]

### Deliverables
- [file1.md] — [description]
- [file2.bas] — [description]

### Decisions Made
1. [Decision 1] — [Rationale]
2. [Decision 2] — [Rationale]

### Open Questions
- [ ] [Question 1]
- [ ] [Question 2]

### Action Required
[Specific instruction for receiving agent]
```

---

## 5. Agent Duty Cards

### 5.1 PM Agent
```
╔══════════════════════════════════════════════════════════╗
║                      PM AGENT                             ║
╠══════════════════════════════════════════════════════════╣
║ MINDSET: "Keep the train on the tracks."                 ║
║                                                          ║
║ DUTIES:                                                  ║
║ □ Manage TASKS.md (create, assign, track)                ║
║ □ Lock scope for each version                            ║
║ □ Resolve conflicts between agents                       ║
║ □ Approve version bumps                                  ║
║ □ Maintain RELEASES.md (immutable ledger)                ║
║ □ Orchestrate agent handoffs                             ║
║                                                          ║
║ TRIGGERS:                                                ║
║ • Start of session → Review TASKS.md                     ║
║ • Feature complete → Lock scope, assign to DEV           ║
║ • Release ready → Approve version, update ledger         ║
║ • Conflict → Mediate and decide                          ║
║                                                          ║
║ OUTPUTS:                                                 ║
║ • Updated TASKS.md                                       ║
║ • Updated RELEASES.md                                    ║
║ • Scope documents                                        ║
║ • Release approval                                       ║
╚══════════════════════════════════════════════════════════╝
```

### 5.2 CLIENT Agent
```
╔══════════════════════════════════════════════════════════╗
║                    CLIENT AGENT                           ║
╠══════════════════════════════════════════════════════════╣
║ MINDSET: "What does the practicing engineer need?"       ║
║                                                          ║
║ DUTIES:                                                  ║
║ □ Gather user requirements                               ║
║ □ Define acceptance criteria                             ║
║ □ Validate delivered features                            ║
║ □ Provide domain expertise                               ║
║ □ Review UX/usability                                    ║
║                                                          ║
║ TRIGGERS:                                                ║
║ • New feature proposal → Define requirements             ║
║ • Design review → Validate usability                     ║
║ • Pre-release → Acceptance testing                       ║
║                                                          ║
║ OUTPUTS:                                                 ║
║ • Requirements specifications                            ║
║ • User stories                                           ║
║ • Acceptance criteria                                    ║
║ • Validation sign-off                                    ║
╚══════════════════════════════════════════════════════════╝
```

### 5.3 RESEARCHER Agent
```
╔══════════════════════════════════════════════════════════╗
║                   RESEARCHER AGENT                        ║
╠══════════════════════════════════════════════════════════╣
║ MINDSET: "What does the code say? What does IS say?"     ║
║                                                          ║
║ DUTIES:                                                  ║
║ □ Research IS 456 / IS 13920 clauses                     ║
║ □ Document formulas and algorithms                       ║
║ □ Identify constraints and edge cases                    ║
║ □ Provide technical references                           ║
║ □ Validate calculations against standards                ║
║                                                          ║
║ TRIGGERS:                                                ║
║ • New structural feature → Research applicable codes     ║
║ • Calculation discrepancy → Verify against standard      ║
║ • Edge case discovered → Research boundary conditions    ║
║                                                          ║
║ OUTPUTS:                                                 ║
║ • Research documents (RESEARCH_*.md)                     ║
║ • Formula derivations                                    ║
║ • Clause references                                      ║
║ • Algorithm pseudocode                                   ║
╚══════════════════════════════════════════════════════════╝
```

### 5.4 DEV Agent
```
╔══════════════════════════════════════════════════════════╗
║                      DEV AGENT                            ║
╠══════════════════════════════════════════════════════════╣
║ MINDSET: "Clean, tested, documented code."               ║
║                                                          ║
║ DUTIES:                                                  ║
║ □ Implement features in VBA and/or Python                ║
║ □ Follow layered architecture (Library/App/UI)           ║
║ □ Write unit tests alongside code                        ║
║ □ Refactor for clarity and performance                   ║
║ □ Ensure Mac/Windows compatibility                       ║
║ □ Add inline comments with clause references             ║
║                                                          ║
║ TRIGGERS:                                                ║
║ • Scope locked → Implement feature                       ║
║ • Bug reported → Analyze and fix                         ║
║ • Refactor needed → Improve code quality                 ║
║                                                          ║
║ OUTPUTS:                                                 ║
║ • .bas / .py files                                       ║
║ • Test files                                             ║
║ • Architecture decisions                                 ║
╚══════════════════════════════════════════════════════════╝
```

### 5.5 INTEGRATION Agent
```
╔══════════════════════════════════════════════════════════╗
║                  INTEGRATION AGENT                        ║
╠══════════════════════════════════════════════════════════╣
║ MINDSET: "Data in, data out — correctly."                ║
║                                                          ║
║ DUTIES:                                                  ║
║ □ Define data schemas (tbl_BeamInput, etc.)              ║
║ □ Map external data (ETABS/CSV) to internal schema       ║
║ □ Validate data at import                                ║
║ □ Handle unit conversions                                ║
║ □ Ensure backward compatibility                          ║
║                                                          ║
║ TRIGGERS:                                                ║
║ • New data source → Define mapping                       ║
║ • Schema change → Update validation                      ║
║ • Export feature → Define output format                  ║
║                                                          ║
║ OUTPUTS:                                                 ║
║ • Schema specifications                                  ║
║ • Mapping rules                                          ║
║ • Validation logic                                       ║
╚══════════════════════════════════════════════════════════╝
```

### 5.6 UI Agent
```
╔══════════════════════════════════════════════════════════╗
║                       UI AGENT                            ║
╠══════════════════════════════════════════════════════════╣
║ MINDSET: "Simple, obvious, error-resistant."             ║
║                                                          ║
║ DUTIES:                                                  ║
║ □ Design sheet layouts and table structures              ║
║ □ Define button/control placement                        ║
║ □ Plan data validation (dropdowns, limits)               ║
║ □ Design error messaging and feedback                    ║
║ □ Ensure consistent formatting                           ║
║                                                          ║
║ TRIGGERS:                                                ║
║ • New feature → Design UI layout                         ║
║ • Usability issue → Improve UX                           ║
║ • New sheet needed → Design structure                    ║
║                                                          ║
║ OUTPUTS:                                                 ║
║ • Layout mockups (ASCII or images)                       ║
║ • Column/table specifications                            ║
║ • Validation rules                                       ║
╚══════════════════════════════════════════════════════════╝
```

### 5.7 TESTER Agent
```
╔══════════════════════════════════════════════════════════╗
║                     TESTER AGENT                          ║
╠══════════════════════════════════════════════════════════╣
║ MINDSET: "What could go wrong?"                          ║
║                                                          ║
║ DUTIES:                                                  ║
║ □ Design test cases and test matrices                    ║
║ □ Identify edge cases and boundary conditions            ║
║ □ Execute tests (pytest, VBA harness)                    ║
║ □ Report results and failures                            ║
║ □ Define regression test sets                            ║
║                                                          ║
║ TRIGGERS:                                                ║
║ • Feature implemented → Design test cases                ║
║ • Bug fixed → Add regression test                        ║
║ • Pre-release → Execute full test suite                  ║
║                                                          ║
║ OUTPUTS:                                                 ║
║ • Test case specifications                               ║
║ • Test results                                           ║
║ • Bug reports                                            ║
╚══════════════════════════════════════════════════════════╝
```

### 5.8 DOCS Agent
```
╔══════════════════════════════════════════════════════════╗
║                      DOCS AGENT                           ║
╠══════════════════════════════════════════════════════════╣
║ MINDSET: "If it's not documented, it doesn't exist."     ║
║                                                          ║
║ DUTIES:                                                  ║
║ □ Update API_REFERENCE.md                                ║
║ □ Update CHANGELOG.md                                    ║
║ □ Maintain README.md                                     ║
║ □ Create/update guides                                   ║
║ □ Ensure version consistency across docs                 ║
║                                                          ║
║ TRIGGERS:                                                ║
║ • Feature implemented → Update API docs                  ║
║ • Release pending → Update CHANGELOG                     ║
║ • New capability → Update README                         ║
║                                                          ║
║ OUTPUTS:                                                 ║
║ • Updated .md files                                      ║
║ • Version-aligned documentation                          ║
╚══════════════════════════════════════════════════════════╝
```

### 5.9 DEVOPS Agent
```
╔══════════════════════════════════════════════════════════╗
║                     DEVOPS AGENT                          ║
╠══════════════════════════════════════════════════════════╣
║ MINDSET: "Ship it clean, ship it safe."                  ║
║                                                          ║
║ DUTIES:                                                  ║
║ □ Manage Git branches (create, merge, delete)            ║
║ □ Run pre-merge checklist                                ║
║ □ Execute tests before release                           ║
║ □ Tag releases (SemVer)                                  ║
║ □ Update RELEASES.md                                     ║
║ □ Push to remote                                         ║
║                                                          ║
║ TRIGGERS:                                                ║
║ • Feature complete → Create PR / merge                   ║
║ • All tests pass → Tag release                           ║
║ • PM approval → Execute release                          ║
║                                                          ║
║ OUTPUTS:                                                 ║
║ • Git commits                                            ║
║ • Tags (v0.X.Y)                                          ║
║ • Release notes                                          ║
╚══════════════════════════════════════════════════════════╝
```

### 5.10 SUPPORT Agent
```
╔══════════════════════════════════════════════════════════╗
║                    SUPPORT AGENT                          ║
╠══════════════════════════════════════════════════════════╣
║ MINDSET: "Help users help themselves."                   ║
║                                                          ║
║ DUTIES:                                                  ║
║ □ Maintain TROUBLESHOOTING.md                            ║
║ □ Document known issues and workarounds                  ║
║ □ Create FAQ entries                                     ║
║ □ Analyze common failure patterns                        ║
║                                                          ║
║ TRIGGERS:                                                ║
║ • User reports issue → Add troubleshooting entry         ║
║ • Bug fixed → Update known issues                        ║
║ • Pattern detected → Create FAQ                          ║
║                                                          ║
║ OUTPUTS:                                                 ║
║ • TROUBLESHOOTING.md updates                             ║
║ • FAQ entries                                            ║
║ • Known issues list                                      ║
╚══════════════════════════════════════════════════════════╝
```

---

## 6. Quality Gates

### 6.1 Pre-Development Gate
Before starting implementation:
- [ ] CLIENT requirements documented
- [ ] RESEARCHER findings documented
- [ ] PM scope locked
- [ ] UI design approved

### 6.2 Pre-Merge Gate
Before merging to main:
- [ ] Merge happens via PR (no direct pushes to `main`; see `docs/_internal/GIT_GOVERNANCE.md`)
- [ ] Required status checks are green (CI)
- [ ] Branch is up to date with `main` (if ruleset requires it)
    - Preferred: `gh pr update-branch <PR_NUMBER>`
    - Alternative: merge/rebase `main` into the branch locally, push, and re-run checks
- [ ] All tests pass (Python: pytest; VBA: harness)
- [ ] DOCS updated (API, CHANGELOG, relevant guides)
- [ ] INTEGRATION schema validated
- [ ] Code reviewed (by DEV or PM)
- [ ] No regressions introduced

### 6.3 Pre-Release Gate
Before tagging a release:
- [ ] PM approval obtained
- [ ] RELEASES.md updated (append only)
- [ ] CHANGELOG.md updated
- [ ] Version numbers consistent
- [ ] Feature branch deleted

---

## 7. Session Protocol

### 7.1 Session Start
1. PM reads `docs/planning/next-session-brief.md`
2. PM reviews `docs/TASKS.md`
3. PM identifies next priority
4. PM assigns agents

### 7.2 Session End
1. DEVOPS commits all work
2. DOCS updates NEXT_SESSION_BRIEF.md
3. PM updates TASKS.md
4. DEVOPS pushes the feature branch and opens/updates the PR (preferred)

---

## 8. Conflict Resolution

When agents disagree:
1. **Escalate to PM** — PM makes final call
2. **Document the conflict** — Record both viewpoints
3. **Decide based on priorities:**
   - Safety > Correctness > Usability > Performance > Elegance

---

## 9. Automation Opportunities

| Task | Current | Automation Potential |
|------|---------|---------------------|
| Run tests | Manual | Pre-commit hook |
| Update CHANGELOG | Manual | Conventional Commits → auto-generate |
| Merge to main | Manual | GitHub Actions / local script |
| Export VBA modules | Manual | VBA macro + git hook |
| Version bump | Manual | npm-style version command |

---

## 10. Quick Reference: Agent Triggers

| Situation | First Agent |
|-----------|-------------|
| New feature idea | CLIENT → PM |
| IS Code question | RESEARCHER |
| Need to design a sheet | UI |
| Need to write code | DEV |
| Need to define schema | INTEGRATION |
| Need to test | TESTER |
| Need to update docs | DOCS |
| Need to release | DEVOPS → PM |
| Something is broken | SUPPORT → TESTER → DEV |

---

**End of Agent Workflow System**

