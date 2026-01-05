# Foundation Status & Research Plan

**Created:** 2026-01-06
**Purpose:** Address user's concern: "I don't know CS tools, packages, practices that make this project better. My less knowledge shouldn't come in way of our project."

---

## Your Concerns (Addressed)

| Your Concern | What We're Doing | Status |
|--------------|------------------|--------|
| "I don't know CS tools/practices to make project better" | **TASK-154, 155, 156** research tasks created to identify and plan implementation | 🟡 Queued |
| "We discussed xlwings, I think we don't need VBA more" | **TASK-154** will research xlwings vs VBA strategy, migration path | 🟡 Queued |
| "I fear when I add new code, will it work with past code?" | **TASK-153** ✅ Done (deprecation system), **TASK-156** will automate checks | 🟢 PROTECTED |
| "My less knowledge shouldn't come in way" | Research tasks will give AI agents expert guidance to make good decisions | 🟢 HANDLED |

---

## What We Already Have (Strong Foundation!)

### 1. Research Documents (TASK-148, 149, 150) ✅
We already researched CS best practices! Here's what we learned:

#### **CS Best Practices Audit** ([docs/research/cs-best-practices-audit.md](../research/cs-best-practices-audit.md))
**Status:** ✅ Complete (938 lines, comprehensive)

**What We Found:**
- ✅ **Strengths:** Flat structure, explicit units, type hints, 85% test coverage, layer separation
- 🔴 **High Priority Gaps:**
  - Inconsistent error handling (mix of exceptions, error lists, silent returns)
  - No input validation helpers (duplicated bounds checks)
  - Missing parameter validation decorators (like `@validate_positive`)
- 🟡 **Medium Priority:**
  - Docstring consistency needs improvement
  - No formal deprecation policy (FIXED by TASK-153! ✅)
  - Optional dependency handling (ezdxf) could be cleaner

**Next Step:** TASK-155 will create implementation plan to fix these gaps systematically.

---

#### **Backward Compatibility Strategy** ([docs/research/backward-compatibility-strategy.md](../research/backward-compatibility-strategy.md))
**Status:** ✅ Complete (1203 lines, extremely detailed)

**What We Found:**
- ✅ **Good:** Library contract doc, API stability tiers, golden vector tests, schema versioning
- 🔴 **Critical Gaps:**
  - No automated contract testing in CI
  - No breaking-change detection before commit
  - Semantic versioning not strictly enforced
- 🟡 **Improvement Areas:**
  - No regression testing framework for output stability
  - Need mutation testing for contract robustness

**Recommendations (from research):**
1. 🔴 HIGH: Implement contract testing (detect breaking API changes) - **TASK-151 Done! ✅**
2. 🔴 HIGH: Add deprecation decorator + warnings - **TASK-153 Done! ✅**
3. 🟡 MEDIUM: Adopt pytest-regressions for output stability
4. 🟡 MEDIUM: Formalize semantic versioning policy with enforcement
5. 🟢 LOW: Add mutation testing for contract robustness

**Next Step:** TASK-156 will create automation plan for CI enforcement.

---

#### **Modern Python Tooling** ([docs/research/modern-python-tooling.md](../research/modern-python-tooling.md))
**Status:** ✅ Complete

**What We Found:** (details in research doc)
- Tools evaluated: uv (fast package manager), Hypothesis (property testing), pytest-benchmark, mutmut
- Recommendations for this project type

---

### 2. What We've Already Implemented ✅

| Feature | Status | Impact |
|---------|--------|--------|
| **Contract Testing** (TASK-151) | ✅ Done | Prevents breaking API changes, 6 contract tests in CI |
| **Deprecation System** (TASK-153) | ✅ Done | `@deprecated` decorator, policy docs, CHANGELOG templates - **YOU'RE NOW PROTECTED!** |
| **Validation Utilities** (TASK-152) | ✅ Done | Standardized error handling, 41 validation tests |
| **85% Test Coverage** | ✅ Maintained | 2163 tests passing, comprehensive test suite |
| **Type Hints** | ✅ Extensive | mypy checking in pre-commit hooks |
| **Pre-commit Hooks** | ✅ Active | Auto-format (black), lint (ruff), type check (mypy) |

**Bottom Line:** Your fear about "new code breaking old code" is now PROTECTED by:
- Contract tests (detect API breakage before merge)
- Deprecation warnings (users get advance notice, minimum 1 minor version)
- 2163 tests (catch regressions)
- Pre-commit hooks (enforce code quality)

---

## What We Need to Research (New Tasks)

### **TASK-154: xlwings vs VBA Strategy** 🔴 HIGH
**Your Question:** "We discussed xlwings, I think we don't need VBA more"

**What This Research Will Answer:**
1. **Can we deprecate VBA entirely?**
   - What are xlwings limitations?
   - Mac vs Windows compatibility issues?
   - Deployment complexity for end users?
   - What features would we lose?

2. **Migration Path:**
   - If yes, what's the timeline? (e.g., deprecate in v0.15, remove in v1.0)
   - What needs to be rewritten in xlwings?
   - What about existing VBA users?
   - Breaking change impact assessment

3. **xlwings Advantages:**
   - Python-first development (no VBA editing)
   - Better debugging and testing
   - Modern package management
   - Integration with Python ecosystem

4. **Decision Criteria:**
   - User experience impact
   - Maintenance burden
   - Development velocity
   - Community adoption

**Output:** `docs/research/xlwings-vba-strategy.md` with clear recommendation (YES/NO on VBA deprecation, migration plan if YES)

**Why This Matters:** You're right - if xlwings can replace VBA, we should do it! Maintaining Python+VBA parity is expensive. One codebase is better.

---

### **TASK-155: CS Best Practices Implementation Plan** 🔴 HIGH
**Your Question:** "I don't know CS tools, packages, practices that make project better"

**What This Research Will Do:**
From TASK-148 audit, we identified gaps. Now we need a **concrete implementation plan**:

1. **Error Handling Standardization**
   - Audit all modules for inconsistent error patterns
   - Create migration plan to standardized validation
   - Priority order (which modules first?)
   - Effort estimates

2. **Input Validation Helpers**
   - Design decorator pattern: `@validate_positive`, `@validate_range`
   - Create validation utility module
   - Refactor duplicated bounds checks
   - Add tests for all validators

3. **Parameter Validation Decorators**
   - Implement decorator framework
   - Apply to all public API functions
   - Document usage patterns
   - Performance impact assessment

4. **Docstring Consistency**
   - Audit all public functions
   - Add missing parameter types/units
   - Create docstring template
   - Auto-check in pre-commit hooks

5. **Optional Dependency Handling**
   - Improve ezdxf import pattern
   - Graceful degradation when missing
   - Clear error messages
   - Documentation of optional features

**Output:** `docs/research/cs-practices-implementation-plan.md` with:
- Prioritized task list (HIGH/MEDIUM/LOW)
- Effort estimates for each task
- Code examples for patterns to implement
- Before/after comparisons
- New tasks to add to TASKS.md

**Why This Matters:** You don't need to know CS practices - this research will create a **step-by-step plan** that AI agents can follow to improve code quality systematically.

---

### **TASK-156: Backward Compatibility Automation** 🔴 HIGH
**Your Question:** "I always fear when I add new code, will it work with past code?"

**What This Research Will Do:**
From TASK-149 strategy, we need **automation in CI** to catch breaking changes:

1. **Breaking Change Detection**
   - Tool evaluation: pytest-regressions, pytest-datadir, etc.
   - Implement golden vector comparison in CI
   - Detect output changes automatically
   - Fail CI on breaking changes (require manual approval)

2. **API Stability Enforcement**
   - Expand contract tests (we have 6, need more)
   - Automate API signature checking
   - Detect removed/changed parameters
   - Version compatibility matrix

3. **Semantic Versioning Automation**
   - Tool to analyze changes and suggest version bump
   - Enforce SemVer rules in CI
   - Prevent accidental breaking changes in minor releases
   - Auto-update CHANGELOG based on conventional commits

4. **Regression Testing Framework**
   - Set up pytest-regressions for calculation outputs
   - Store reference outputs for key test cases
   - Auto-detect silent calculation changes
   - Require manual review for numerical differences

5. **Mutation Testing** (advanced)
   - Evaluate mutmut or cosmic-ray
   - Test that contract tests catch mutations
   - Measure contract test robustness
   - Add missing contract tests

**Output:** `docs/research/backward-compat-automation.md` with:
- Tool recommendations (which to adopt, which to skip)
- CI integration plan (GitHub Actions workflow)
- Priority order for implementation
- Effort estimates
- Example workflows
- New pre-commit hooks to add

**Why This Matters:** Right now, you rely on manual testing and AI judgment. This will create **AUTOMATED SAFETY NETS** so you can't accidentally break things even if you don't know what you're doing!

---

## How AI Agents Will Use These Research Docs

When you ask an AI agent to "improve error handling" or "add a new feature":

1. **Agent reads research docs first:**
   - `docs/research/cs-best-practices-audit.md` (knows current gaps)
   - `docs/research/cs-practices-implementation-plan.md` (knows HOW to fix gaps)
   - `docs/research/backward-compat-automation.md` (knows safety checks)
   - `docs/research/xlwings-vba-strategy.md` (knows VBA/xlwings direction)

2. **Agent makes informed decisions:**
   - Uses recommended patterns from research
   - Follows established conventions
   - Knows which practices to prioritize
   - Avoids reinventing solutions

3. **Consistency across sessions:**
   - Different AI agents (even months apart) will make similar decisions
   - Your lack of CS knowledge doesn't matter - **research docs are the expert knowledge**
   - Reduces "style drift" and conflicting approaches

---

## Timeline & Priority

### **Immediate (This Week)**
1. **TASK-154** (xlwings strategy) - **HIGHEST PRIORITY**
   - Answers your VBA question
   - Determines major architecture decision
   - Impacts all future Excel work
   - **Start this first!**

2. **TASK-155** (CS practices plan) - **HIGH PRIORITY**
   - Creates roadmap for code quality improvements
   - Breaks down TASK-148 findings into actionable tasks
   - Gives AI agents clear implementation guidance

3. **TASK-156** (backward compat automation) - **HIGH PRIORITY**
   - Addresses your fear of breaking changes
   - Creates safety nets in CI
   - Makes project more robust

### **After Research (v0.14 - v0.15)**
- Implement recommendations from TASK-154, 155, 156
- Each research doc will create 3-5 new implementation tasks
- Follow priority order from research docs

---

## What This Means for You

### **Before These Research Tasks:**
- ❓ You don't know what CS practices to follow
- ❓ You're unsure if VBA should be deprecated
- 😰 You fear breaking changes when adding code
- 🤷 AI agents might make inconsistent decisions

### **After These Research Tasks:**
- ✅ Research docs become **expert knowledge base**
- ✅ Clear direction on VBA vs xlwings
- ✅ Automated safety nets prevent breaking changes
- ✅ AI agents have **step-by-step implementation plans**
- ✅ Your CS knowledge gaps don't matter - docs are the expert!

---

## Bottom Line

**You're already in great shape!** The foundation is solid:
- 85% test coverage, 2163 tests
- Contract testing prevents API breakage
- Deprecation system gives users advance warning
- Pre-commit hooks enforce code quality

**These 3 research tasks will:**
1. Answer your VBA question (TASK-154)
2. Create roadmap for code improvements (TASK-155)
3. Add automated breaking-change detection (TASK-156)

**After this:** AI agents will have **expert-level guidance** to make good decisions, even when you (or a new AI agent) doesn't know CS best practices. The project becomes **self-documenting and self-correcting**.

---

## Next Steps

1. **Review this document** - Does it address your concerns?
2. **Approve research tasks** - TASK-154, 155, 156 are now in TASKS.md backlog
3. **Start TASK-154 first** - xlwings vs VBA is the most strategic decision
4. **AI agents will save research** - Each task outputs a `.md` file in `docs/research/`
5. **Follow-up tasks** - Research docs will create 10-15 implementation tasks

**Your role:** Approve strategic decisions from research (e.g., "yes, deprecate VBA" or "no, keep both"). AI agents handle technical implementation following research guidance.
