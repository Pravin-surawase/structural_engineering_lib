# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2025-12-11
### Added (VBA)
- **Flanged Beam Design (T/L Beams)**:
  - `Calculate_Mu_Lim_Flanged`: Calculates limiting moment for T-sections.
  - `Design_Flanged_Beam`: Handles Neutral Axis in Flange, Web (Singly), and Web (Doubly).
  - `Test_Flanged.bas`: Comprehensive unit tests for all three cases.

## [0.2.1] - 2025-12-11
### Fixed (Mac VBA Compatibility)
- **Stack Corruption:** Fixed `Runtime Error 6: Overflow` caused by passing inline boolean expressions to subroutines.
- **Integer Overflow:** Wrapped all dimension multiplications in `CDbl()` within library modules.
- **UDT Stability:** Removed nested UDT returns in `Design_Doubly_Reinforced` to prevent stack corruption.
- **Test Harness:** Refactored `Test_Structural.bas` to use the "Safe Assertion Pattern" and deferred `Debug.Print`.

## [0.2.0] - 2025-12-11
### Added
- **Doubly Reinforced Beam Design**:
  - `design_doubly_reinforced`: Logic to handle `Mu > Mu_lim` by adding compression steel.
  - `get_steel_stress`: Non-linear stress-strain curve implementation for Fe415/Fe500 (IS 456 Figure 23).
  - Updated `FlexureResult` to include `asc_required`.

## [0.1.0] - 2025-12-10
### Added
- **Core Flexure Module**:
  - Singly reinforced rectangular beam design (`design_singly_reinforced`).
  - Limiting moment calculation (`calculate_mu_lim`).
  - Steel area calculation (`calculate_ast_required`).
- **Shear Module**:
  - Shear capacity calculation (`calculate_shear_capacity`).
  - Stirrup design (`design_shear_reinforcement`).
  - Table 19 (Tc) and Table 20 (Tc_max) lookups.
- **Infrastructure**:
  - Dual implementation in Python and VBA.
  - Unit tests for Python (`pytest`).
  - Documentation structure (`API_REFERENCE.md`, `TASKS.md`).
  - Excel add-in guide (`EXCEL_ADDIN_GUIDE.md`).

---

Format: Keep a section per release with Added/Changed/Fixed as needed. Tag releases as `vX.Y.Z`.
