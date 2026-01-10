# Project Hygiene & Professional Standards - Research Specifications

**Purpose:** Detailed specifications for TASK-165 through TASK-170 research tasks
**Date:** 2026-01-06
**Context:** Post-v0.14.0 foundation hardening, preparing for v1.0 professional release

---

## TASK-165: Project Hygiene & File Organization

**Goal:** Audit project for obsolete, duplicate, or poorly organized files. Create cleanup plan.

### What to Audit:

#### 1. Duplicate Files
- [ ] Search for duplicate filenames across directories
- [ ] Check for backup files (.bak, .old, ~, etc.)
- [ ] Identify redundant documentation (same content in multiple places)
- [ ] Find duplicate code across modules

#### 2. Obsolete Content
- [ ] **Archive Candidates:**
  - Old session logs (keep recent 3-5, archive rest)
  - Completed research that's been implemented
  - Old planning documents superseded by current docs
  - Historical migration guides no longer needed
  - Deprecated examples
- [ ] **Removal Candidates:**
  - Dead code (unreachable, commented out)
  - Unused imports
  - Empty placeholder files
  - Test fixtures for removed features

#### 3. Inconsistent Naming
- [ ] File naming conventions (snake_case vs kebab-case vs camelCase)
- [ ] Directory naming patterns
- [ ] Module names vs import names
- [ ] Test file naming (`test_*.py` vs `*_test.py`)

#### 4. Broken Links
- [ ] Cross-references between docs
- [ ] Links to moved/renamed files
- [ ] External links (dead URLs)
- [ ] Relative path issues

#### 5. Directory Structure
- [ ] Is `docs/` well-organized?
- [ ] Should `docs/_internal/` content be public?
- [ ] Is `docs/_archive/` being used consistently?
- [ ] Are examples in the right place?
- [ ] Should tests be reorganized?

### Expected Output:

**File:** `docs/research/project-hygiene-audit.md`

**Contents:**
1. **Executive Summary** - Top 5 issues found
2. **Duplicate Files Report** - List with recommendations (merge/remove/keep)
3. **Obsolete Content Report** - Archive vs remove decisions
4. **Naming Inconsistencies** - Patterns found, proposed standards
5. **Broken Links Report** - All broken links with fix suggestions
6. **Directory Structure Proposal** - Current vs proposed structure
7. **Action Plan** - Prioritized cleanup tasks with effort estimates
8. **File Organization Standards** - Rules for future files

---

## TASK-166: Nomenclature Standardization

**Goal:** Create consistent naming standards across Python, VBA, and documentation.

### What to Audit:

#### 1. Python Code Naming
- [ ] **Functions:**
  - Inconsistent verb usage (calculate vs compute vs get)
  - Abbreviations (mu vs moment, ast vs steel_area)
  - Underscores vs no underscores
- [ ] **Variables:**
  - Units in names (b_mm vs b, fck_nmm2 vs fck)
  - Temporary vars (tmp, temp, x, result)
  - Magic numbers
- [ ] **Classes:**
  - Result vs Output vs Report suffixes
  - Dataclass naming patterns
- [ ] **Modules:**
  - Singular vs plural (detailing vs details)
  - Abbreviations (bbs vs bar_bending_schedule)

#### 2. VBA Code Naming
- [ ] Function names (PascalCase vs camelCase)
- [ ] Variable names (Hungarian notation usage)
- [ ] Module names (M01_ prefix consistency)
- [ ] Python/VBA naming alignment

#### 3. Documentation Terms
- [ ] Technical terms (flexure vs bending, shear vs punching)
- [ ] IS 456 clause references format
- [ ] Abbreviations usage (Mu vs M_u vs mu)
- [ ] Capitalization (Beam Design vs beam design)

#### 4. Abbreviations Inventory
- [ ] Create complete list of abbreviations used
- [ ] Check for inconsistent usage
- [ ] Document full forms
- [ ] Identify ambiguous abbreviations

### Expected Output:

**File:** `docs/research/nomenclature-standards.md`

**Contents:**
1. **Executive Summary** - Key inconsistencies found
2. **Python Naming Audit** - Current patterns, issues, recommendations
3. **VBA Naming Audit** - Current patterns, issues, recommendations
4. **Documentation Terms Audit** - Inconsistencies, preferred terms
5. **Abbreviations Glossary** - Complete list with definitions
6. **Proposed Standards:**
   - Function naming rules
   - Variable naming rules
   - Module/file naming rules
   - Documentation style guide
7. **Migration Plan** - How to standardize existing code
8. **Examples** - Before/after comparisons

---

## TASK-167: Professional Repository Standards

**Goal:** Audit repo against open-source best practices. Add missing professional touches.

### What to Audit:

#### 1. License & Copyright
- [ ] **License Headers:**
  - Check all Python files for license headers
  - Check all VBA files for license headers
  - Verify correct copyright year (2024-2026?)
  - Consistent header format
- [ ] **LICENSE File:**
  - MIT license complete and correct
  - Copyright holder correct
  - Year current

#### 2. Community Health Files
- [ ] **CODE_OF_CONDUCT.md** - Does it exist? Is it standard (Contributor Covenant)?
- [ ] **SECURITY.md** - Security policy, vulnerability reporting
- [ ] **CONTRIBUTING.md** - Complete? References to all tools/processes?
- [ ] **CITATION.cff** - For academic citations
- [ ] **AUTHORS.md** or **CONTRIBUTORS.md** - Credit all contributors

#### 3. GitHub Templates
- [ ] **Issue Templates:**
  - Bug report template
  - Feature request template
  - Question template
- [ ] **PR Template:**
  - Checklist for PRs
  - Testing requirements
  - Documentation requirements
- [ ] **PULL_REQUEST_TEMPLATE.md**

#### 4. Repository Metadata
- [ ] **Badges:**
  - CI status
  - Test coverage
  - PyPI version
  - License
  - Python version
  - Code style (black)
  - Downloads
- [ ] **Topics/Tags** on GitHub
- [ ] **Description** accurate
- [ ] **Website link** set
- [ ] **Social preview image**

#### 5. Funding & Sponsorship
- [ ] **FUNDING.yml** - GitHub sponsors, Open Collective, etc.
- [ ] **Sponsor acknowledgments**

#### 6. Legal & Compliance
- [ ] **Third-party licenses** documented
- [ ] **Dependencies** license-compatible
- [ ] **Export restrictions** (if applicable)

### Expected Output:

**File:** `docs/research/professional-repo-standards.md`

**Contents:**
1. **Executive Summary** - Missing elements, priority fixes
2. **License & Copyright Audit** - Files missing headers, recommendations
3. **Community Health Assessment** - What exists, what's missing
4. **GitHub Configuration Audit** - Templates, badges, metadata
5. **Compliance Check** - Legal/licensing issues
6. **Implementation Plan:**
   - High priority (required for v1.0)
   - Medium priority (nice to have)
   - Low priority (future enhancement)
7. **Templates & Examples** - Actual files to add
8. **Checklist** - v1.0 professional repo readiness

---

## TASK-168: Documentation Quality & Completeness

**Goal:** Audit all documentation for quality, accuracy, and completeness.

### What to Audit:

#### 1. Outdated Information
- [ ] Version references (0.12.0 when current is 0.14.0)
- [ ] Deprecated API examples
- [ ] Old feature descriptions
- [ ] Obsolete installation instructions
- [ ] Historical "coming soon" that's now done

#### 2. Broken Cross-References
- [ ] Internal links to moved files
- [ ] Relative path issues
- [ ] Section anchors that don't exist
- [ ] Code references to renamed functions

#### 3. Missing Examples
- [ ] APIs without usage examples
- [ ] Complex features without tutorials
- [ ] Error handling examples missing
- [ ] CLI commands without examples

#### 4. Inconsistent Formatting
- [ ] Heading levels (# vs ## vs ###)
- [ ] Code block languages (```python vs ```py vs ```)
- [ ] Lists (- vs * vs 1.)
- [ ] Tables (formatting consistency)
- [ ] Admonitions (> **Note:** vs **Note** vs NOTE)

#### 5. Clarity Issues
- [ ] Jargon without explanation
- [ ] Assumptions about reader knowledge
- [ ] Steps missing context
- [ ] Ambiguous instructions

#### 6. Redundant Content
- [ ] Same information in multiple places
- [ ] Duplicate getting started guides
- [ ] Overlapping READMEs

#### 7. Organization Issues
- [ ] Logical flow problems
- [ ] Topics in wrong sections
- [ ] Index/ToC completeness
- [ ] Navigation difficulties

### Expected Output:

**File:** `docs/research/documentation-quality-audit.md`

**Contents:**
1. **Executive Summary** - Quality score, top issues
2. **Completeness Report:**
   - Coverage matrix (what's documented vs what exists)
   - Missing API docs
   - Missing examples
3. **Accuracy Report:**
   - Outdated content list
   - Version reference errors
   - Broken links inventory
4. **Quality Report:**
   - Formatting inconsistencies
   - Clarity issues
   - Redundancy problems
5. **Organization Assessment:**
   - Current structure review
   - Proposed improvements
6. **Improvement Roadmap:**
   - Quick wins (1-2 hrs)
   - Medium effort (1-2 days)
   - Major rewrites (3-5 days)
7. **Documentation Standards** - Style guide for future docs

---

## TASK-169: Code Style Consistency

**Goal:** Audit code for style inconsistencies and create cleanup plan.

### What to Audit:

#### 1. Formatting Inconsistencies
- [ ] **Black Coverage:**
  - Files not formatted with black
  - Manual formatting overrides
  - Line length violations (>88)
- [ ] **Import Ordering:**
  - Inconsistent import organization
  - Relative vs absolute imports
  - Unused imports
- [ ] **Whitespace:**
  - Trailing whitespace
  - Inconsistent blank lines
  - Mixed tabs/spaces (should never happen)

#### 2. Docstrings
- [ ] **Missing Docstrings:**
  - Public functions without docs
  - Classes without docs
  - Modules without docs
- [ ] **Inconsistent Format:**
  - NumPy style vs Google style vs reStructuredText
  - Parameter documentation format
  - Return value documentation
  - Example placement

#### 3. Comments
- [ ] **Outdated Comments:**
  - References to removed code
  - Old TODOs completed
  - Incorrect algorithm descriptions
- [ ] **Comment Quality:**
  - Obvious comments (# increment i)
  - Missing comments (complex logic without explanation)
  - Commented-out code blocks

#### 4. TODO/FIXME Markers
- [ ] Inventory all TODO/FIXME/HACK/XXX markers
- [ ] Which are still relevant?
- [ ] Which should be GitHub issues?
- [ ] Which are obsolete?

#### 5. Dead Code
- [ ] Unreachable code
- [ ] Unused functions
- [ ] Unused classes
- [ ] Unused variables

#### 6. Magic Numbers
- [ ] Constants that should be named
- [ ] IS 456 values without clause references
- [ ] Unexplained thresholds

#### 7. Code Duplication
- [ ] Repeated logic that should be functions
- [ ] Copy-pasted sections
- [ ] Similar functions that could be unified

### Expected Output:

**File:** `docs/research/code-style-consistency.md`

**Contents:**
1. **Executive Summary** - Overall style health
2. **Black/Ruff Report:**
   - Coverage percentage
   - Files to format
   - Rule violations
3. **Docstring Audit:**
   - Missing docstrings count
   - Format inconsistencies
   - Quality issues
4. **Comment Audit:**
   - TODO/FIXME inventory
   - Outdated comments
   - Quality issues
5. **Dead Code Report:**
   - Unreachable code
   - Unused definitions
   - Removal candidates
6. **Magic Numbers Inventory:**
   - All magic numbers found
   - Proposed constant names
7. **Code Duplication Report:**
   - Duplicated logic
   - Refactoring opportunities
8. **Cleanup Plan:**
   - Automated fixes (black, ruff --fix)
   - Semi-automated (docstring templates)
   - Manual work (refactoring, TODO resolution)

---

## TASK-170: Test Organization & Coverage Gaps

**Goal:** Audit test suite for organization, completeness, and quality.

### What to Audit:

#### 1. Test File Organization
- [ ] **Naming Consistency:**
  - All files follow `test_*.py` pattern?
  - Names match modules tested?
- [ ] **Directory Structure:**
  - Tests organized by module?
  - Integration tests separate?
  - Fixtures in right place?
- [ ] **Test Discovery:**
  - All tests discoverable by pytest?
  - Any orphaned test files?

#### 2. Test Categories
- [ ] **Unit Tests:**
  - Coverage per module
  - Missing unit tests
- [ ] **Integration Tests:**
  - API integration
  - CLI integration
  - File I/O integration
- [ ] **Property Tests:**
  - Good candidates for Hypothesis
  - Mathematical property tests
- [ ] **Regression Tests:**
  - Golden fixtures
  - Bug regression tests
- [ ] **Performance Tests:**
  - Benchmark suite exists?
  - Performance regression tracking?

#### 3. Coverage Gaps
- [ ] **Modules < 80% coverage:**
  - Which modules?
  - Which branches missed?
  - Why untested?
- [ ] **Edge Cases:**
  - Boundary conditions
  - Error paths
  - Invalid inputs
- [ ] **IS 456 Compliance:**
  - All tables tested?
  - All clauses covered?

#### 4. Test Quality
- [ ] **Assertions:**
  - Weak assertions (assert True)
  - Missing assertions
  - Assertion messages
- [ ] **Test Independence:**
  - Tests depending on each other
  - Shared mutable state
- [ ] **Test Speed:**
  - Slow tests (>1s)
  - Can they be faster?

#### 5. Fixtures & Helpers
- [ ] **Fixture Organization:**
  - conftest.py usage
  - Fixture duplication
  - Fixture documentation
- [ ] **Test Helpers:**
  - Repeated setup code
  - Missing test utilities

### Expected Output:

**File:** `docs/research/test-organization-audit.md`

**Contents:**
1. **Executive Summary** - Test health score
2. **Organization Assessment:**
   - Current structure
   - Proposed improvements
3. **Category Coverage:**
   - Unit: X%
   - Integration: X%
   - Property: X%
   - Performance: X%
4. **Coverage Gaps Report:**
   - Modules needing tests
   - Edge cases missed
   - Critical paths untested
5. **Quality Issues:**
   - Weak tests
   - Slow tests
   - Brittle tests
6. **Improvement Plan:**
   - Quick wins (add missing tests)
   - Medium effort (refactor tests)
   - Major work (property test suite, benchmarks)
7. **Testing Standards** - Guidelines for new tests

---

## General Instructions for All Research Tasks

### Research Methodology:
1. **Audit Phase:** Use automated tools where possible (grep, find, scripts)
2. **Analysis Phase:** Categorize findings, identify patterns
3. **Recommendation Phase:** Propose concrete solutions with examples
4. **Planning Phase:** Prioritize, estimate effort, create actionable tasks

### Document Structure:
Each research document should follow this template:
```markdown
# [Task Title]

**Task:** TASK-XXX
**Date:** 2026-01-06
**Status:** ✅ Complete
**Scope:** [Brief description]

---

## Executive Summary
[3-5 sentences: What was found, severity, recommended action]

## Methodology
[How the audit was conducted]

## Findings
[Detailed findings with examples]

## Recommendations
[Specific recommendations with code examples where applicable]

## Action Plan
[Prioritized implementation tasks]

## References
[Tools used, standards referenced]
```

### Deliverables:
- Research document in `docs/research/`
- Scripts used for auditing (if any) in `scripts/`
- Example files (if applicable)
- Update TASKS.md with implementation tasks

### Success Criteria:
- ✅ Comprehensive audit (nothing major missed)
- ✅ Actionable recommendations (clear next steps)
- ✅ Prioritized (know what to do first)
- ✅ Effort-estimated (can plan sprints)
- ✅ Examples included (show don't tell)

---

**End of Research Specifications**
