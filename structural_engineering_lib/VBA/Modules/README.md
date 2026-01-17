# Modules - VBA Core Calculation Modules

> **Purpose:** Core IS 456 calculation modules for Excel VBA
> **Last Updated:** 2026-01-10

## Module Overview

| File | Purpose | Python Equivalent |
|------|---------|-------------------|
| `M01_Constants.bas` | Physical and code constants | `constants.py` |
| `M02_Materials.bas` | Material property calculations | `materials.py` |
| `M03_Flexure.bas` | Flexural design (Mu, Ast) | `flexure.py` |
| `M04_Shear.bas` | Shear design (Vu, stirrups) | `shear.py` |
| `M05_Detailing.bas` | Rebar spacing, cover rules | `detailing.py` |
| `M06_Tables.bas` | IS 456 table lookups | `tables.py` |
| `M07_Serviceability.bas` | Deflection, cracking | `serviceability.py` |
| `M08_API.bas` | Public interface functions | `api.py` |
| `M09_UDFs.bas` | Excel User Defined Functions | N/A (Excel only) |

## Guidelines

1. **Clause references** - Every calculation must cite IS 456 clause
2. **Mac compatibility** - Follow CDbl() wrapping rules (see parent README)
3. **No I/O in M01-M07** - Keep core modules pure calculation
4. **Type declarations** - Use explicit `As Long`, `As Double`, etc.

## For AI Agents

- Match function signatures with Python equivalents
- When adding new calculations, add to BOTH VBA and Python
- Test tolerance: ±0.1% for areas, ±1mm for dimensions
