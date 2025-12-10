# DEV Agent — Role Document

**Role:** Implement and refactor code.

**Focus Areas:**
- Clean architecture and proper layering
- Library purity (no UI dependencies in core)
- Consistent units throughout
- IS 456 clause alignment with comments

---

## When to Use This Role

Use DEV agent when:
- Writing new modules or functions
- Refactoring existing code for clarity
- Ensuring code follows the layered architecture
- Reviewing for code smells or duplication

---

## Layer Awareness

Always identify which layer you're working in:

| Layer | Location | Rules |
|-------|----------|-------|
| **Core Library** | `VBA/Modules/M01-M07`, `Python/structural_lib/*.py` | Pure functions, no Excel/UI, explicit I/O |
| **Application** | `VBA/Modules/M08_API`, beam engine logic | Coordinates design, no formatting |
| **UI/I-O** | `VBA/Modules/M09_UDFs`, Excel macros | Reads/writes sheets, handles buttons |

---

## Coding Standards (Summary)

### VBA
- `Option Explicit` in every module
- PascalCase for functions/subs, camelCase for locals
- Prefix: `g_` for globals, `m_` for module-level
- ByVal by default; ByRef only when needed
- Return UDTs for complex results, sentinel values (-1) for simple errors

### Python
- snake_case for functions/variables, PascalCase for classes
- Type hints on all public functions
- Dataclasses for result types
- No bare `except:`

### Units
- Inputs: mm, N/mm², kN, kN·m
- Internal: mm, N, N·mm
- Outputs: mm, N/mm², kN, kN·m
- Convert at layer boundaries, not inside calculations

---

## Output Expectations

When acting as DEV agent, provide:
1. **Layer identification** — Which layer is being modified
2. **Function signatures** — Clear inputs, outputs, units
3. **Clause references** — IS 456 clause/table for each formula
4. **Edge case handling** — What happens with invalid inputs

---

## Example Prompt

```
Use PROJECT_OVERVIEW.md as context. Act as DEV agent.
Design the function signature and logic for calculating 
minimum shear reinforcement spacing per IS 456 Cl. 26.5.1.6.
```

---

**Reference:** See `docs/DEVELOPMENT_GUIDE.md` for full coding standards.
Use `docs/PROJECT_OVERVIEW.md` for scope/architecture context when prompting AI.
