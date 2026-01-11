# Contributing

Guides for developers and maintainers of the structural engineering library.

**Files:** 16 | **Updated:** 2026-01-11

---

## 🚀 Quick Start

| I want to... | Do this |
|--------------|---------|
| **Fix a bug** | Read [Development Guide](development-guide.md) → Fix → `pytest` → PR |
| **Add a feature** | Read [API Design](../guidelines/api-design-guidelines.md) → Implement → Test → PR |
| **Set up AI agent** | Read [Git Workflow for AI Agents](git-workflow-ai-agents.md) ⚠️ **CRITICAL** |
| **Understand tests** | Read [Testing Strategy](testing-strategy.md) |

---

## ⚠️ AI Agents: MUST READ

| Guide | Purpose |
|-------|---------|
| [**Git Workflow for AI Agents**](git-workflow-ai-agents.md) | **Avoid git race conditions** |
| [Background Agent Guide](background-agent-guide.md) | Parallel work with 1-2 background agents |
| [Agent Collaboration Framework](agent-collaboration-framework.md) | Multi-agent coordination |
| [Agent Onboarding Message](agent-onboarding-message.md) | New agent onboarding |

---

## 📋 Development Guides

| Guide | Audience |
|-------|----------|
| [Development Guide](development-guide.md) | Coding standards, PR workflow |
| [Naming Conventions](naming-conventions.md) | File, module, branch naming |
| [Learning Paths](learning-paths.md) | Reading paths by task complexity |
| [Solo Maintainer Operating System](solo-maintainer-operating-system.md) | Solo maintainer workflow |

---

## 🧪 Testing & Quality

| Guide | Purpose |
|-------|---------|
| [Testing Strategy](testing-strategy.md) | Test structure, coverage goals |
| [VBA Testing Guide](vba-testing-guide.md) | Running VBA test suites |
| [Docstring Style Guide](docstring-style-guide.md) | Docstring conventions |

---

## 📦 VBA & Excel

| Guide | Purpose |
|-------|---------|
| [VBA Guide](vba-guide.md) | VBA module conventions |
| [Excel Add-in Guide](excel-addin-guide.md) | Packaging the .xlam |

---

## 📝 Templates

| Template | Use Case |
|----------|----------|
| [Doc Template](doc-template.md) | New documentation file |
| [Changelog Deprecation Template](changelog-deprecation-template.md) | Changelog entries |
| [End of Session Workflow](end-of-session-workflow.md) | Session wrap-up checklist |

---

## ✅ Before Contributing

```bash
# 1. Read coding standards
cat docs/contributing/development-guide.md

# 2. Run tests locally
cd Python && pytest

# 3. Format code
python -m black .

# 4. Commit using safe workflow
./scripts/ai_commit.sh "feat: your feature description"
```

---

## 🏗️ Layer Architecture (Must Follow)

| Layer | Modules | Rules |
|-------|---------|-------|
| **Core** | flexure, shear, detailing, etc. | Pure functions, no I/O |
| **Application** | api, job_runner, bbs | Orchestrates core |
| **UI/I-O** | excel_integration, dxf_export, job_cli | External data |

---

## 📚 Related Documentation

| Document | Purpose |
|----------|---------|
| [Guidelines](../guidelines/README.md) | Development standards |
| [Architecture](../architecture/README.md) | System design decisions |
| [Agent Onboarding](../agents/guides/agent-onboarding.md) | Complete agent setup |

---

**Parent:** [docs/README.md](../README.md)
