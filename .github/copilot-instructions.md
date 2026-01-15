# Copilot Instructions — structural_engineering_lib

> **FOR AI AGENTS:** This file guides GitHub Copilot/VS Code AI agents.
> Read this FIRST before any work. Following these rules prevents 99% of errors.

---

## 🚀 Quick Start (30 Seconds to Productivity)

```bash
# 1. Start session (ONE COMMAND replaces 4 legacy commands)
./scripts/agent_start.sh --quick

# 2. Work on code, then commit
./scripts/ai_commit.sh "feat: your description"

# 3. End session
.venv/bin/python scripts/end_session.py
```

**Essential Resources (Read in Order):**
1. [copilot-instructions.md](/.github/copilot-instructions.md) ← **YOU ARE HERE**
2. [agent-workflow-master-guide.md](docs/agents/guides/agent-workflow-master-guide.md) - Complete workflow
3. [agent-quick-reference.md](docs/agents/guides/agent-quick-reference.md) - Command cheat sheet
4. [TASKS.md](docs/TASKS.md) - Current work items
5. [git-automation/README.md](docs/git-automation/README.md) - Git workflow hub

---

## ⚠️ THE ONE RULE (Git Workflow)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ NEVER use manual git commands!              ┃
┃ ALWAYS: ./scripts/ai_commit.sh "message"    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

**Why?**
- Manual git causes merge conflicts (wastes 10-30 minutes per incident)
- Pre-commit hooks modify files → manual workflow fails
- We have 103 automation scripts built specifically to prevent git issues

**Results:** 90-95% faster commits, 97.5% fewer errors, 100% conflict elimination

**🔒 Git Enforcement:**
- Hooks block manual `git commit`/`git push` (installed by `agent_start.sh`)
- Confused? Run: `./scripts/git_ops.sh --status` (analyzes state, gives recommendation)
- Health check: `./scripts/git_automation_health.sh`

---

## � What This Project Is

**IS 456 RC Beam Design Library** - Python + VBA parity for structural engineering calculations.

**Architecture (3-layer):**
1. **Core:** Pure calculations (`Python/structural_lib/codes/is456/`) - NO I/O, explicit units (mm, N/mm², kN, kN·m)
2. **Application:** Orchestration (`api.py`, `job_runner.py`) - coordinates core, NO formatting
3. **UI/I-O:** External interfaces (`streamlit_app/`, `excel_integration.py`, `dxf_export.py`)

**Critical:** Never mix layers. Core modules CANNOT import from app/UI layers.

**Key Files:**
- `Python/structural_lib/codes/is456/flexure.py` - Moment design (Mu, Ast calculations)
- `Python/structural_lib/codes/is456/shear.py` - Shear design (Vu, stirrup spacing)
- `Python/structural_lib/codes/is456/detailing.py` - Rebar layout, development lengths
- `Python/structural_lib/api.py` - Main entry point for external users
- `streamlit_app/pages/01_beam_design.py` - Primary UI (4 core pages visible, 8 hidden with `_` prefix)

---

## 🎯 Essential Rules (Scanner-Enforced)

### Code Safety (Streamlit & Python)

❌ **FORBIDDEN (causes runtime crashes):**
```python
value = data['key']              # KeyError
first = items[0]                 # IndexError
result = a / b                   # ZeroDivisionError
value = st.session_state.key     # AttributeError
```

✅ **REQUIRED patterns:**
```python
value = data.get('key', default)
first = items[0] if len(items) > 0 else None
result = a / b if b != 0 else 0
value = st.session_state.get('key', default)
```

**Validation:** Run `.venv/bin/python scripts/check_streamlit_issues.py <file>` before commit.

### Streamlit-Specific Rules (CRITICAL)

**Fragment API restrictions** (discovered Session 30):
```python
# ❌ FORBIDDEN in @st.fragment functions:
@st.fragment
def my_fragment():
    st.sidebar.button("Click")  # StreamlitAPIException!
    st.tabs(["A", "B"])         # Not allowed

# ✅ CORRECT patterns:
@st.fragment
def my_fragment():
    st.button("Click")          # OK - regular widgets

# Or wrap fragment in sidebar context:
with st.sidebar:
    my_fragment()  # Now can use sidebar widgets inside
```

**Validation:**
- AST scanner: `.venv/bin/python scripts/check_fragment_violations.py --all-pages`
- Runtime: `.venv/bin/python -m pytest streamlit_app/tests/test_app.py` (AppTest framework)
- Both run in pre-commit hooks + CI automatically

### Import Rules

❌ **NEVER:**
```python
def my_function():
    import pandas as pd  # Import inside function
```

✅ **ALWAYS:**
```python
import pandas as pd  # At module level (top of file)

def my_function():
    df = pd.DataFrame(data)
```

---

## 🧪 Testing Requirements

**Before committing ANY code:**

```bash
# Python code changes:
cd Python && .venv/bin/python -m pytest tests/ -v

# Streamlit changes:
.venv/bin/python scripts/check_streamlit_issues.py --all-pages
.venv/bin/python scripts/check_fragment_violations.py --all-pages

# Formatting (auto-fix):
cd Python && .venv/bin/python -m black .
.venv/bin/python -m ruff check --fix .
```

**Test patterns:**
- **Unit tests:** `Python/tests/unit/test_<module>.py` - test single functions
- **Integration:** `Python/tests/integration/test_<feature>.py` - test workflows
- **Property-based:** Use `hypothesis` for edge cases (see `test_flexure_properties.py`)
- **Coverage gate:** CI requires 85% branch coverage minimum

**Writing tests:**
```python
def test_calculate_ast_required_nominal_case():
    """Test steel calculation for nominal beam."""
    result = calculate_ast_required(
        moment=100,  # kN·m
        width=300,   # mm
        depth=450,   # mm
        fck=25.0,    # N/mm²
        fy=500.0,    # N/mm²
    )
    assert result.ast_required > 0
    assert result.ast_min <= result.ast_required <= result.ast_max
```

---

## 🔄 Commit Strategy (PR vs Direct)

**Use automation to decide:**
```bash
./scripts/should_use_pr.sh --explain
```

**Quick reference:**
| Change Type | Strategy | Command |
|-------------|----------|---------|
| Production code (`Python/structural_lib/`) | **PR required** | `./scripts/create_task_pr.sh TASK-XXX "desc"` |
| VBA code (`VBA/`, `Excel/`) | **PR required** | Same as above |
| CI workflows (`.github/workflows/`) | **PR required** | Same as above |
| Dependencies (`pyproject.toml`) | **PR required** | Same as above |
| Docs (<150 lines) | Direct commit OK | `./scripts/ai_commit.sh "docs: fix typo"` |
| Tests (<50 lines) | Direct commit OK | `./scripts/ai_commit.sh "test: add case"` |
| Scripts (<50 lines) | Direct commit OK | `./scripts/ai_commit.sh "chore: update script"` |

**PR Workflow:**
```bash
# 1. Create PR branch
./scripts/create_task_pr.sh TASK-XXX "Fix benchmark signatures"

# 2. Make changes + commit
./scripts/ai_commit.sh "fix: update function calls"

# 3. Finish PR (auto-submits to GitHub)
./scripts/finish_task_pr.sh TASK-XXX "description" --async

# 4. Monitor CI
./scripts/pr_async_merge.sh status
```

**Session docs:** Update `SESSION_LOG.md` + `next-session-brief.md` in the same PR, log PR number (not merge hash).

---

## 🔧 Layer Architecture (NEVER Violate)

| Layer | Python | Rules |
|-------|--------|-------|
| **Core** | `Python/structural_lib/codes/is456/*.py` | Pure functions, no I/O, explicit units |
| **Application** | `api.py`, `job_runner.py` | Orchestrates core, NO formatting |
| **UI/I-O** | `streamlit_app/`, `excel_integration.py` | External interfaces only |

**Units:** mm, N/mm², kN, kN·m (explicit everywhere)

---

## ⚠️ Common Mistakes (AVOID)

| Mistake | Correct Approach |
|---------|------------------|
| Using manual git commands | **ALWAYS** `./scripts/ai_commit.sh "message"` |
| Mixing layers (Core imports UI) | Keep strict layer separation |
| Manual file operations (`rm`, `mv`) | Use `scripts/safe_file_move.py` |
| Using `git commit --amend` after push | **NEVER!** Create new commit instead |
| Not running tests before commit | Run tests + scanner locally first |

---

## 📚 Quick Resources

**Essential Commands:**
```bash
./scripts/agent_start.sh --quick     # Start session
./scripts/ai_commit.sh "message"     # Commit
./scripts/should_use_pr.sh --explain # Check if PR needed
.venv/bin/python scripts/end_session.py  # End session
```

**Key Docs:**
- [TASKS.md](docs/TASKS.md) - Current work
- [agent-workflow-master-guide.md](docs/agents/guides/agent-workflow-master-guide.md) - Complete guide
- [git-automation/README.md](docs/git-automation/README.md) - Git automation

---

**Remember:** When in doubt:
1. `./scripts/git_ops.sh --status` for state analysis
2. `./scripts/should_use_pr.sh --explain` for decisions
3. Read the workflow guides for details
