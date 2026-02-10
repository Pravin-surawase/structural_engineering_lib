# Agent 6 Comprehensive Onboarding Guide

**Type:** Guide
**Audience:** Agent 6 (Streamlit UI Specialist)
**Status:** Production Ready
**Importance:** Critical
**Version:** 1.0.0
**Created:** 2026-01-11
**Last Updated:** 2026-01-11
**Related Tasks:** v0.17.5 Code Quality Enhancement
**Archive Condition:** Never - living document, update rather than archive

---

## 🎯 Mission Statement

**You are Agent 6, the Streamlit UI Specialist.**

Your mission: Build and maintain production-ready Streamlit dashboards for the IS 456 structural engineering library. You own all code in `streamlit_app/` (~20,000 lines).

---

## 🚀 Quick Start (60 Seconds)

```bash
# 1. Start your session
./scripts/agent_start.sh --quick

# 2. Check your current tasks
cat docs/TASKS.md | grep -A 20 "v0.17.5"

# 3. Validate the app
.venv/bin/python scripts/check_streamlit.py --all-pages

# 4. Run tests
cd streamlit_app && pytest tests/ -v

# 5. Start app locally (optional)
cd streamlit_app && streamlit run app.py
```

---

## 📂 Your Codebase

### Directory Structure

```
streamlit_app/                # ~20,000 lines total
├── app.py                    # Main entry point
├── pages/                    # 12 pages (~6,000 lines)
│   ├── 01_🏗️_beam_design.py    # Main beam design (851 lines)
│   ├── 02_💰_cost_optimizer.py  # Cost optimization (596 lines)
│   ├── 03_✅_compliance.py      # IS 456 compliance (455 lines)
│   ├── 04_📚_documentation.py   # Docs viewer (462 lines)
│   ├── 05_📋_bbs_generator.py   # Bar bending schedule (481 lines)
│   ├── 06_📐_dxf_export.py      # CAD export (582 lines)
│   ├── 07_📄_report_generator.py # PDF reports (317 lines)
│   ├── 08_📊_batch_design.py    # Batch processing (332 lines)
│   ├── 09_🔬_advanced_analysis.py # Advanced calcs (582 lines)
│   ├── 10_📚_learning_center.py # Education (565 lines)
│   ├── 11_🎬_demo_showcase.py   # Demos (551 lines)
│   └── 12_📖_clause_traceability.py # Clause refs (316 lines)
├── components/              # 6 reusable components (~2,600 lines)
│   ├── inputs.py            # Form inputs (393 lines)
│   ├── results.py           # Result displays (392 lines)
│   ├── visualizations.py    # Charts/graphs (931 lines)
│   ├── preview.py           # Live preview (499 lines)
│   └── polish.py            # UI polish (398 lines)
├── utils/                   # 26 utilities (~11,300 lines)
│   ├── design_system.py     # Core tokens (586 lines)
│   ├── layout.py            # Page layouts (753 lines)
│   ├── error_handler.py     # Error handling (925 lines)
│   ├── api_wrapper.py       # Library integration (713 lines)
│   ├── session_manager.py   # State persistence (692 lines)
│   └── ... (21 more utilities)
└── tests/                   # Test suite
    └── ... (600+ tests)
```

### File Size Guide

| Category | Lines | Quality Priority |
|----------|-------|------------------|
| Pages | 6,090 | HIGH - User-facing |
| Components | 2,645 | CRITICAL - Reused |
| Utils | 11,312 | HIGH - Core logic |

---

## ⚠️ CRITICAL: Guard Rails (Read These!)

### Rule 1: NEVER Use Manual Git Commands

```bash
# ❌ FORBIDDEN: manual add/commit/push workflows

# ✅ ALWAYS USE
./scripts/ai_commit.sh "message"
```

### Rule 2: Run Scanner Before Every Commit

```bash
# REQUIRED: Run this before committing any Streamlit changes
.venv/bin/python scripts/check_streamlit.py --all-pages

# Scanner catches:
# - NameError (undefined variables)
# - ZeroDivisionError (unprotected division)
# - KeyError (dict access without .get())
# - AttributeError (session state issues)
# - IndexError (list access without bounds check)
```

### Rule 3: Follow Coding Standards

**Full guide:** [agent-coding-standards.md](../../contributing/agent-coding-standards.md)

**Quick Reference:**

```python
# ❌ WRONG: Bare dict access
value = data["key"]

# ✅ CORRECT: Safe dict access
value = data.get("key", default_value)

# ❌ WRONG: Bare list access
first = items[0]

# ✅ CORRECT: Bounds-checked list access
first = items[0] if len(items) > 0 else None

# ❌ WRONG: Unprotected division
result = a / b

# ✅ CORRECT: Zero-safe division
result = a / b if b != 0 else 0

# ❌ WRONG: Bare session state access
value = st.session_state["key"]

# ✅ CORRECT: Safe session state access
value = st.session_state.get("key", default)
```

### Rule 4: Run Tests Before Commit

```bash
# Run all Streamlit tests
cd streamlit_app && pytest tests/ -v

# Run specific test file
cd streamlit_app && pytest tests/test_beam_design.py -v

# Run with coverage
cd streamlit_app && pytest tests/ --cov=. --cov-report=html
```

---

## 🔧 Development Workflow

### Standard Task Workflow

```
1. Start Session
   ./scripts/agent_start.sh --quick

2. Pick Task from TASKS.md
   Review v0.17.5 Code Quality Enhancement section

3. Implement Changes
   - Follow coding standards
   - Add/update tests
   - Update documentation

4. Validate Changes
   .venv/bin/python scripts/check_streamlit.py <file>
   cd streamlit_app && pytest tests/ -v

5. Commit Changes
   ./scripts/ai_commit.sh "feat(streamlit): description"

6. End Session
   .venv/bin/python scripts/session.py end
```

### PR Workflow (For Substantial Changes)

```bash
# 1. Check if PR needed
./scripts/should_use_pr.sh --explain

# 2. If PR required:
./scripts/create_task_pr.sh TASK-XXX "description"

# 3. Make changes and commit
./scripts/ai_commit.sh "feat: implement feature"

# 4. Submit PR
./scripts/finish_task_pr.sh TASK-XXX "description"

# 5. Wait for CI
gh pr checks <PR_NUMBER> --watch

# 6. Merge when green
gh pr merge <PR_NUMBER> --squash --delete-branch
```

---

## 🔍 Quality Tools

### 1. AST Scanner (`check_streamlit.py`)

The scanner uses AST analysis to detect runtime errors before they happen.

```bash
# Scan all pages
.venv/bin/python scripts/check_streamlit.py --all-pages

# Scan specific file
.venv/bin/python scripts/check_streamlit.py streamlit_app/pages/01_🏗️_beam_design.py

# What it detects:
# - CRITICAL: NameError, ZeroDivisionError, ImportError
# - HIGH: KeyError, AttributeError, IndexError
# - MEDIUM: Best practice violations

# Scanner intelligence (zero false positives for division):
# Recognizes patterns like: x / y if y != 0 else 0
# Recognizes: if y > 0: result = x / y
# Recognizes: compound conditions, ternary, try/except
```

### 2. Pylint (`.pylintrc-streamlit`)

```bash
# Run pylint on Streamlit code
.venv/bin/python -m pylint --rcfile=.pylintrc-streamlit streamlit_app/

# Focus on specific page
.venv/bin/python -m pylint --rcfile=.pylintrc-streamlit streamlit_app/pages/01_🏗️_beam_design.py
```

### 3. Pre-commit Hooks (Automatic)

When you commit using `ai_commit.sh`, these run automatically:
- Black (formatting)
- Ruff (linting)
- AST scanner (if Streamlit files changed)
- Pylint (if Streamlit files changed)

---

## 📚 Design System

### Color Tokens (from `utils/design_system.py`)

```python
from utils.design_system import COLORS

# Primary (Navy Blue - 60% usage)
COLORS.primary_500  # #003366

# Accent (Orange - 10% usage)
COLORS.accent_500   # #FF6600

# Semantic
COLORS.success      # #10B981
COLORS.warning      # #F59E0B
COLORS.error        # #EF4444
COLORS.info         # #3B82F6
```

### Typography

```python
from utils.design_system import TYPOGRAPHY

# Font family
TYPOGRAPHY.font_family  # "Inter, system-ui, sans-serif"
TYPOGRAPHY.mono_family  # "JetBrains Mono, Fira Code, monospace"

# Sizes
TYPOGRAPHY.h1     # 36px
TYPOGRAPHY.h2     # 28px
TYPOGRAPHY.body   # 16px
```

### Spacing

```python
from utils.design_system import SPACING

SPACING.xs    # 4px
SPACING.sm    # 8px
SPACING.md    # 16px
SPACING.lg    # 24px
SPACING.xl    # 32px
```

---

## 🏗️ Common Patterns

### Page Template

```python
"""
Page Title - Brief description.

Author: Agent 6
Created: 2026-01-XX
"""
from __future__ import annotations

import streamlit as st
from utils.layout import setup_page, create_header
from utils.error_handler import safe_design_call
from utils.session_manager import SessionManager

# Initialize
setup_page("Page Title", "🎯")
SessionManager.initialize()

# Header
create_header("Page Title", "Brief description of functionality")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    # Input section
    st.subheader("Inputs")
    # ... input widgets ...

with col2:
    # Preview section
    st.subheader("Preview")
    # ... preview content ...

# Calculate button
if st.button("Calculate", type="primary"):
    result, errors = safe_design_call(api_function, **inputs)
    if errors:
        for error in errors:
            error.display()
    else:
        # Display results
        pass
```

### Safe API Call Pattern

```python
from utils.api_wrapper import cached_design_beam
from utils.error_handler import safe_design_call, DesignError

# Wrap API calls for error handling
result, errors = safe_design_call(
    cached_design_beam,
    b=width,
    d=depth,
    Mu=moment,
    fck=concrete_grade,
    fy=steel_grade
)

if errors:
    for error in errors:
        error.display()
else:
    st.success(f"Required steel: {result['ast_required']:.0f} mm²")
```

### Session State Pattern

```python
from utils.session_manager import SessionManager

# Initialize at page start
SessionManager.initialize()

# Save a design session
SessionManager.save_session(
    inputs={"b": 300, "d": 450, "Mu": 100},
    results=result,
    name="B1-Ground Floor"
)

# Load from history
session = SessionManager.load_session(session_id)
if session:
    st.session_state.update(session.inputs)
```

---

## 📋 Current Tasks (v0.17.5)

Reference: `docs/TASKS.md` > v0.17.5 section

### Phase A: Quick Wins
- TASK-401: Fix IndexError false positives
- TASK-422: ✅ Document PR auto-merge
- TASK-431: ✅ Fix finish_task_pr.sh

### Phase B: Scanner Enhancement
- TASK-402: Add type annotation checker
- TASK-403: Add widget return type validation
- TASK-404: Add circular import detection
- TASK-405: Add performance issue detection

### Phase C: Streamlit Automation
- TASK-411: Create streamlit_preflight.sh
- TASK-412: Create generate_streamlit_page.py
- TASK-413: Create validate_session_state.py
- TASK-414: Create performance profiler

### Phase D: Documentation
- TASK-421: ✅ Create agent-coding-standards.md
- TASK-423: Update copilot-instructions

---

## 🔗 Quick Links

### Essential Reading
1. [agent-coding-standards.md](../../contributing/agent-coding-standards.md) - Coding rules
2. [copilot-instructions.md](../../../.github/copilot-instructions.md) - All project rules
3. [agent-workflow-master-guide.md](agent-workflow-master-guide.md) - Git workflow

### Streamlit Docs
1. [streamlit-maintenance-guide.md](../../contributing/streamlit-maintenance-guide.md)
2. [streamlit-comprehensive-prevention-system.md](../../contributing/streamlit-comprehensive-prevention-system.md)
3. [streamlit-issues-catalog.md](../../contributing/streamlit-issues-catalog.md)

### Research
1. [streamlit-code-quality-research.md](../../research/streamlit-code-quality-research.md)

---

## 🆘 Troubleshooting

### Scanner Shows False Positive

If the scanner flags something you believe is safe:

1. Check if it's a known gap (IndexError on `split()` etc.)
2. Add explicit check anyway (consistency > minimal code)
3. If truly false positive, add a comment:
   ```python
   # Scanner note: split() always returns at least 1 element
   parts = x.split('.')
   first = parts[0] if len(parts) > 0 else x
   ```

### Tests Failing

```bash
# Get detailed failure info
cd streamlit_app && pytest tests/test_failing.py -v --tb=long

# Check if it's a mock issue
grep -r "MockStreamlit" streamlit_app/tests/conftest.py
```

### Import Errors

```bash
# Check circular imports
.venv/bin/python -c "import streamlit_app.utils.design_system"

# If circular, use lazy imports:
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from utils.design_system import COLORS
```

### App Won't Start

```bash
# Check for syntax errors
.venv/bin/python -m py_compile streamlit_app/app.py

# Check imports
.venv/bin/python -c "import streamlit_app.app"
```

---

## 📊 Quality Metrics

### Current State
- **Test count:** 600+ tests
- **Scanner accuracy:** 100% for division, 85-90% for dict/list
- **Code coverage:** ~80%

### Targets (v0.17.5)
- Scanner false positive rate: <2%
- New agent onboarding issues: 0 first-day errors
- Page creation time: <5 min with template

---

## 🏆 Success Criteria

You're doing well when:
- ✅ Scanner shows 0 CRITICAL issues before commit
- ✅ All tests pass before commit
- ✅ Pre-commit hooks pass on first try
- ✅ PRs pass CI on first attempt
- ✅ No runtime errors reported in production

---

**Remember:** When in doubt, ask! Better to clarify than to break things.

**Emergency:** Run `./scripts/recover_git_state.sh` if git is broken.
