# Guidelines Index

**Type:** Index
**Audience:** All Agents
**Status:** Production Ready
**Importance:** High
**Created:** 2025-01-01
**Last Updated:** 2026-08-10

---

Development standards and best practices for the structural engineering library.

**Files:** 17 | **Updated:** 2026-08-10

---

## 🎯 Quick Reference

| Need To... | Read This |
|------------|-----------|
| Design a new API function | [api-design-guidelines.md](api-design-guidelines.md) |
| Handle errors properly | [error-handling-standard.md](error-handling-standard.md) |
| Return results from functions | [result-object-standard.md](result-object-standard.md) |
| Move/delete files safely | [file-operations-safety-guide.md](file-operations-safety-guide.md) |
| Migrate a module | [migration-workflow-guide.md](migration-workflow-guide.md) |
| Run independent tasks in parallel | [parallel-task-policy.md](parallel-task-policy.md) |

---

## 📐 API Standards

| File | Description | Key Takeaway |
|------|-------------|--------------|
| [api-design-guidelines.md](api-design-guidelines.md) | API design principles | Explicit units, no defaults |
| [api-evolution-standard.md](api-evolution-standard.md) | API versioning & evolution | SemVer + deprecation rules |
| [function-signature-standard.md](function-signature-standard.md) | Function signature conventions | mm, N/mm², kN units |
| [result-object-standard.md](result-object-standard.md) | Result object patterns | NamedTuple with status |
| [error-handling-standard.md](error-handling-standard.md) | Error handling guidelines | DesignError + Severity levels |

---

## 📝 Documentation Standards

| File | Description | Key Takeaway |
|------|-------------|--------------|
| [documentation-standard.md](documentation-standard.md) | Documentation requirements | Every public function documented |
| [doc-naming-conventions.md](doc-naming-conventions.md) | Document naming rules | One topic, one canonical doc |
| [blog-writing-guide.md](blog-writing-guide.md) | Blog writing style guide | Practical, example-first |

---

## 🔄 Migration & Cleanup

| File | Description | When To Use |
|------|-------------|-------------|
| [migration-workflow-guide.md](migration-workflow-guide.md) | Module migration workflow | Moving modules to new locations |
| [migration-preflight-checklist.md](migration-preflight-checklist.md) | Pre-migration checklist | Before any migration |
| [file-operations-safety-guide.md](file-operations-safety-guide.md) | Safe file operations | Moving, deleting any files |
| [folder-cleanup-workflow.md](folder-cleanup-workflow.md) | Folder cleanup process | Reorganizing documentation |

## Parallel Work

| File | Description | Key Takeaway |
|------|-------------|--------------|
| [parallel-task-policy.md](parallel-task-policy.md) | Codex task/worktree isolation and integration | One task, one worktree, one branch, disjoint paths |

---

## 📚 Related Documentation

| Document | Purpose |
|----------|---------|
| [Contributing](../contributing/README.md) | Developer onboarding |
| [Architecture](../architecture/README.md) | System design decisions |
| [Reference](../reference/README.md) | API & standards reference |

---

**Parent:** [docs/README.md](../README.md)
