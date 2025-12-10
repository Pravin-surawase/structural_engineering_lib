# IS 456 RC Beam Design Library — API Reference

**Document Version:** 0.1 (stub)  
**Last Updated:** December 10, 2025  
**Scope:** Public APIs for VBA and Python implementations (signatures, inputs/outputs, units, status codes).

---

## 1. Conventions
- Units: `Mu` in kN·m, `Vu` in kN, lengths in mm, stresses in N/mm², areas in mm².
- Inputs validated at API boundary; functions use absolute values for moments/shears (UI handles sign).
- Return values: VBA uses UDTs for main APIs; Python uses dataclasses. Simple helpers return scalars.

---

## 2. Flexure API

### 2.1 VBA
```vba
Public Function IS456_FlexureDesign( _
    Mu_kNm As Double, _
    b_mm As Double, _
    d_mm As Double, _
    D_mm As Double, _
    fck As Double, _
    fy As Double _
) As FlexureResult
```
- **Purpose:** Singly reinforced rectangular beam design per IS 456 Cl. 38.1.
- **Inputs:** Mu (kN·m, factored), b (mm), d (effective mm), D (overall mm), fck (N/mm²), fy (N/mm²).
- **Returns:** `FlexureResult` (see Section 6). `DesignStatus` = `OK` or `DOUBLY_REQUIRED`/`ERROR`.

### 2.2 Python
```python
def flexure_design(
    mu_knm: float,
    b_mm: float,
    d_mm: float,
    D_mm: float,
    fck: float,
    fy: float,
) -> FlexureResult:
    ...
```
- Same behavior, units, and status semantics as VBA.

---

## 3. Shear API

### 3.1 VBA
```vba
Public Function IS456_ShearDesign( _
    Vu_kN As Double, _
    b_mm As Double, _
    d_mm As Double, _
    fck As Double, _
    fy_stirrup As Double, _
    Ast_provided_mm2 As Double, _
    Optional stirrup_dia_mm As Double = 8, _
    Optional stirrup_legs As Long = 2 _
) As ShearResult
```
- **Purpose:** Shear design with vertical stirrups per IS 456 Cl. 40 and Tables 19/20.
- **Returns:** `ShearResult` (see Section 6). `DesignStatus` = `SECTION_INADEQUATE`, `MIN_SHEAR_ONLY`, or `OK`.

### 3.2 Python
```python
def shear_design(
    vu_kn: float,
    b_mm: float,
    d_mm: float,
    fck: float,
    fy_stirrup: float,
    ast_provided_mm2: float,
    stirrup_dia_mm: float = 8.0,
    stirrup_legs: int = 2,
) -> ShearResult:
    ...
```
- Same behavior, units, and status semantics as VBA.

---

## 4. Helper Functions (VBA/Python parity)
- `d_effective(D_mm, cover_mm, dia_main_mm, dia_stirrup_mm) -> d_mm`
- `pt_from_Ast(Ast_mm2, b_mm, d_mm) -> pt_percent`
- `Ast_min_IS456(b_mm, d_mm, fy) -> mm2` (Cl. 26.5.1.1)
- `Ast_max_IS456(b_mm, D_mm) -> mm2` (Cl. 26.5.1.2)
- `tau_v(Vu_kN, b_mm, d_mm) -> N/mm2`
- `tau_c_IS456(fck, pt_percent) -> N/mm2` (Table 19, clamped 0.15–3.0%)
- `tau_cmax_IS456(fck) -> N/mm2` (Table 20)
- `StirrupSpacing_IS456(Vus_kN, dia_stirrup_mm, legs, fy, d_mm, sv_max_mm) -> mm`

---

## 5. Table Lookup Data
- Table 19 (τc vs. pt% and fck) stored once and interpolated linearly in pt; clamp pt% to [0.15, 3.0].
- Table 20 (τc,max vs. fck) stored as constants, no interpolation between grades.
- Neutral axis ratios (Annex G.1.1): Fe250=0.53, Fe415=0.48, Fe500=0.46.

---

## 6. Result Types

### 6.1 FlexureResult
- `Ast_required` (mm²), `Ast_min` (mm²), `Ast_max` (mm²)
- `xu` (mm), `xu_max` (mm), `Mu_lim` (kN·m)
- `IsDoublyReinforced` (bool), `DesignStatus` (string), `ErrorMessage` (string)

### 6.2 ShearResult
- `tau_v` (N/mm²), `tau_c` (N/mm²), `tau_cmax` (N/mm²)
- `Vus_required` (kN), `sv_provided` (mm), `sv_max` (mm)
- `DesignStatus` (string), `ErrorMessage` (string)

---

## 7. Status and Error Codes
- `DesignStatus` (flexure): `OK`, `DOUBLY_REQUIRED`, `ERROR`
- `DesignStatus` (shear): `OK`, `MIN_SHEAR_ONLY`, `SECTION_INADEQUATE`, `ERROR`
- `IS456_ErrorCode` enum (VBA): `ERR_NONE`, `ERR_NEGATIVE_DIMENSION`, `ERR_ZERO_DIMENSION`, `ERR_INVALID_CONCRETE_GRADE`, `ERR_INVALID_STEEL_GRADE`, `ERR_MOMENT_EXCEEDS_LIMIT`, `ERR_SHEAR_EXCEEDS_MAX`, `ERR_INVALID_REINFORCEMENT_RATIO`, `ERR_COVER_EXCEEDS_DEPTH`, `ERR_NEGATIVE_MOMENT`, `ERR_CALCULATION_FAILED`

---

## 8. Examples (to be expanded with code)
- Flexure: design of 300×500 beam, Mu=150 kN·m, M25/Fe415 → expected Ast ≈ 1050 mm².
- Shear: same beam with Vu=150 kN, pt=1.0% → τv vs. τc lookup and stirrup spacing.

---

## 9. Notes and Assumptions
- Moments/shears provided as factored design values.
- Library uses absolute values for design; caller handles sign conventions.
- Single layer of tension steel assumed for effective depth calculation; adjust when compression steel added in future versions.

---

**End of API Reference (stub)**
