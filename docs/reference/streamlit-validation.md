# Streamlit Code Validation Reference

> **For AI Agents:** This guide explains the automated validation system for Streamlit code.

**Last Updated:** 2026-01-09
**Status:** ✅ Production Ready (Phase 1B Complete)

---

## 🎯 Overview

The Streamlit validation system consists of two layers:
1. **AST Scanner** - Static analysis for runtime error detection
2. **Pylint** - Code quality and style checks

Both run automatically on every commit (pre-commit hooks) and in CI for every PR.

---

## 🔍 AST Scanner

**Tool:** `scripts/check_streamlit_issues.py`

### Usage

```bash
# Scan all Streamlit pages
.venv/bin/python scripts/check_streamlit_issues.py --all-pages

# Scan single file
.venv/bin/python scripts/check_streamlit_issues.py streamlit_app/pages/01_🏗️_beam_design.py

# Get help
.venv/bin/python scripts/check_streamlit_issues.py --help
```

### What It Detects

| Issue Type | Severity | Example | Detection |
|------------|----------|---------|-----------|
| **NameError** | CRITICAL | Using undefined variable `foo` | Tracks all defined names in scope |
| **ZeroDivisionError** | CRITICAL | `x / y` without validation | Checks for zero-validation patterns |
| **AttributeError** | HIGH | `st.session_state.foo` without check | Tracks session state keys |
| **KeyError** | HIGH | `dict['key']` without `.get()` | Detects unsafe dict access |
| **ImportError** | CRITICAL | Using `pandas` without import | Tracks all imports |

### Intelligence Features (Zero False Positives)

The scanner understands Python's zero-validation patterns:

#### 1. Ternary Expressions
```python
# Scanner recognizes this is safe
result = x / y if y > 0 else 0
```

#### 2. If-Statement Blocks
```python
# Scanner tracks validated variables
if denominator > 0:
    result = numerator / denominator
```

#### 3. Compound Conditions
```python
# Scanner extracts both validated variables
if fy > 0 and fck > 0:
    rho = (0.5 * fck / fy) * (...)
```

#### 4. Complex Expressions
```python
# Scanner handles nested expressions
sv_req = (0.87 * fy * Asv * d) / (Vus * 1000) if Vus > 0 else float("inf")
```

#### 5. Dict/Subscript Access
```python
# Scanner traces through dict access
limit = 0.85 * b * d / steel["fy"] if steel.get("fy", 0) > 0 else 0
```

### Output Example

```
📊 SUMMARY
================================================================================
Files scanned: 4
Files with issues: 3
Total issues: 123
  - Errors: 0
  - Critical: 0
  - High: 123
  - Medium: 0

⚠️  Issues found. Review and fix before merging.
```

**Current State (2026-01-09):**
- ✅ 0 Critical issues (all false positives eliminated)
- ⚠️ 123 High issues (legitimate session state patterns - not blocking)

---

## 🎨 Pylint Check

**Config:** `.pylintrc-streamlit`

### Usage

```bash
# Check all Streamlit code
.venv/bin/python -m pylint --rcfile=.pylintrc-streamlit streamlit_app/

# Check single file
.venv/bin/python -m pylint --rcfile=.pylintrc-streamlit streamlit_app/pages/01_🏗️_beam_design.py
```

### What It Checks

- Code style (PEP 8)
- Unused imports
- Unused variables
- Function complexity
- Docstring presence
- Type hints

---

## 🔄 Integration Points

### Pre-Commit Hooks

Both checks run automatically when you commit:

```bash
# These hooks run on commit:
# 1. check-streamlit-issues (AST scanner)
# 2. pylint-streamlit (Pylint)

# If CRITICAL issues found, commit is blocked
# If HIGH issues found, commit proceeds with warnings
```

**Config:** `.pre-commit-config.yaml`

### CI Workflow

Both checks run in GitHub Actions:

**Workflow:** `.github/workflows/streamlit-validation.yml`

**Jobs:**
- `ast-scanner` - Runs AST scanner
- `pylint-check` - Runs Pylint
- `combined-check` - Combines results

**Result:** PR cannot merge if CRITICAL issues exist

---

## 📝 When to Run

### Manual Checks (Before Committing)

```bash
# Editing Streamlit pages
1. Make changes to streamlit_app/pages/*.py
2. Run scanner: .venv/bin/python scripts/check_streamlit_issues.py <file>
3. Fix any CRITICAL issues
4. Commit: ./scripts/ai_commit.sh "feat: ..."
   # Pre-commit hooks run automatically
```

### Automatic Checks

- **Pre-commit:** Runs on every `./scripts/ai_commit.sh`
- **CI:** Runs on every PR
- **No manual intervention needed** (unless issues found)

---

## 🐛 Interpreting Results

### CRITICAL Issues (Blocking)

**What:** Runtime errors that will crash the app
**Action:** MUST fix before committing
**Examples:**
- Using undefined variables
- Division without zero checks
- Missing imports

### HIGH Issues (Warnings)

**What:** Potential issues that may cause errors
**Action:** Review and fix if appropriate
**Examples:**
- Session state access without `.get()`
- Dict access without default
- Function imports inside loops

### Medium Issues (Info)

**What:** Style or minor improvements
**Action:** Optional to fix
**Examples:**
- Missing type hints
- Docstring formatting

---

## 🎯 Best Practices

### 1. Run Scanner Locally

```bash
# Before committing Streamlit changes
.venv/bin/python scripts/check_streamlit_issues.py --all-pages
```

### 2. Fix Critical Issues First

Address CRITICAL issues immediately. They indicate code that will crash at runtime.

### 3. Understand HIGH Warnings

HIGH issues often indicate valid patterns (like session state access). Review context before fixing.

### 4. Use Validation Patterns

The scanner recognizes these safe patterns:

```python
# ✅ Ternary with validation
result = x / y if y > 0 else 0

# ✅ If-block with validation
if y > 0:
    result = x / y

# ✅ Compound validation
if x > 0 and y > 0:
    result = x / y

# ❌ Unsafe (will trigger warning)
result = x / y
```

---

## 🔧 Configuration

### AST Scanner

**File:** `scripts/check_streamlit_issues.py`

**Key Classes:**
- `StreamlitCodeScanner` - Main visitor
- `_extract_var_name()` - Variable name extraction
- `_is_zero_check()` - Zero validation detection
- `_get_validated_vars()` - Compound condition handling
- `_is_in_safe_ternary()` - Ternary expression checking

**Customization:**
- Modify severity levels in `issues.append()` calls
- Add new checks by implementing `visit_*` methods
- Adjust patterns in `_is_zero_check()` logic

### Pylint

**File:** `.pylintrc-streamlit`

**Key Settings:**
```ini
[MESSAGES CONTROL]
disable=C0111,C0103,R0913,R0914,W0603

[DESIGN]
max-args=10
max-locals=20
```

---

## 📊 Current Stats (2026-01-09)

### Scanner Results

| Metric | Value |
|--------|-------|
| **Files Scanned** | 4 |
| **Total Issues** | 123 |
| **Critical Issues** | 0 ✅ |
| **High Issues** | 123 |
| **False Positives** | 0 ✅ |

### Phase History

| Phase | Date | Achievement |
|-------|------|-------------|
| **Phase 1A** | 2026-01-03 | Scanner created, CI integration |
| **Phase 1B (Days 1-3)** | 2026-01-04-06 | 39 bugs fixed (22 real + 17 false positives) |
| **Phase 1B (Days 4-7)** | 2026-01-07-09 | Zero false positives achieved |

---

## 🚀 Future Enhancements

### Planned (Phase 2)

- [ ] Session state flow analysis
- [ ] Streamlit API usage validation
- [ ] Performance anti-pattern detection
- [ ] Accessibility checks

### Ideas

- Integration with mypy for type checking
- Custom Streamlit-specific rules
- Auto-fix suggestions
- IDE integration (VS Code extension)

---

## 📚 Related Documentation

- [Git Workflow](../contributing/git-workflow-ai-agents.md) - Commit workflow with pre-commit hooks
- [Testing Strategy](../contributing/testing-strategy.md) - Overall testing approach
- [Agent Bootstrap](../getting-started/agent-bootstrap.md) - Getting started guide
- [AI Context Pack](../getting-started/ai-context-pack.md) - Quick reference

---

## 🆘 Troubleshooting

### Scanner Shows False Positives

**Issue:** Scanner warns about safe code
**Solution:** Check if pattern is recognized. Report to team if not.

### Pre-Commit Hook Fails

**Issue:** Commit blocked by scanner
**Solution:** Run manually to see details:
```bash
.venv/bin/python scripts/check_streamlit_issues.py --all-pages
```

### CI Fails But Local Passes

**Issue:** Different results locally vs CI
**Solution:** Ensure you're on latest main:
```bash
./scripts/recover_git_state.sh
.venv/bin/python scripts/check_streamlit_issues.py --all-pages
```

### Too Many Warnings

**Issue:** 100+ HIGH warnings
**Solution:** HIGH warnings are often legitimate patterns. Focus on CRITICAL first.

---

## 📞 Support

**Questions?** Check:
1. This documentation
2. [TASKS.md](../TASKS.md) for known issues
3. [SESSION_LOG.md](../SESSION_LOG.md) for recent changes
4. `.github/copilot-instructions.md` for general rules

**Bug in scanner?** Report with:
- File and line number
- Code snippet
- Why it's a false positive
- Expected behavior

---

*Last updated: 2026-01-09*
