# Contributing

Guides for developers and maintainers.

**Updated:** 2026-01-11

## Contents

| Guide | Audience |
|-------|----------|
| [**Git Workflow for AI Agents**](git-workflow-ai-agents.md) ⚠️ | **AI agents: MUST READ to avoid git race conditions** |
| [Background Agent Guide](background-agent-guide.md) | Parallel work with 1-2 background agents |
| [Agent Collaboration Framework](agent-collaboration-framework.md) | Multi-agent coordination |
| [Agent Onboarding Message](agent-onboarding-message.md) | New agent onboarding |
| [Naming Conventions](naming-conventions.md) | File, module, and branch naming standards |
| [Development Guide](development-guide.md) | Coding standards, PR workflow |
| [Learning Paths](learning-paths.md) | Quick reading paths by task complexity |
| [Solo Maintainer Operating System](solo-maintainer-operating-system.md) | Solo maintainer workflow, release gates |
| [Testing Strategy](testing-strategy.md) | Test structure, coverage goals |
| [VBA Guide](vba-guide.md) | VBA module conventions |
| [VBA Testing Guide](vba-testing-guide.md) | Running VBA test suites |
| [Excel Add-in Guide](excel-addin-guide.md) | Packaging the .xlam |
| [Docstring Style Guide](docstring-style-guide.md) | Docstring conventions |
| [Doc Template](doc-template.md) | Documentation template |
| [Changelog Deprecation Template](changelog-deprecation-template.md) | Changelog entry format |
| [End of Session Workflow](end-of-session-workflow.md) | Session wrap-up checklist |

## Before contributing

1. Read [Development Guide](development-guide.md) for coding standards
2. Run tests locally: `cd Python && pytest`
3. Format code: `python -m black .`

## Layer architecture (must follow)

| Layer | Modules | Rules |
|-------|---------|-------|
| Core | flexure, shear, detailing, etc. | Pure functions, no I/O |
| Application | api, job_runner, bbs | Orchestrates core |
| UI/I-O | excel_integration, dxf_export, job_cli | External data |
