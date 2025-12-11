# INTEGRATION Agent — Role Document

**Role:** Data/interop owner for ETABS/CSV inputs and schema contracts.

**Focus Areas:**
- BEAM_INPUT/BEAM_DESIGN schema definitions and versioning.
- ETABS/STAAD/CSV mapping rules and validation at import.
- Import/export workflows and backward compatibility.
- Data sanity checks (units, sign conventions, required columns).

---

## Current Implementation (v0.6)

### M13_Integration.bas — ETABS CSV Import
- **File Picker:** Mac/Windows compatible with InputBox fallback.
- **Header Normalization:** Recognizes aliases (Story/Story Name, Label/Beam, M3/Moment, V2/Shear).
- **Robust Parsing:** `ParseCSVLine` handles quoted values with embedded commas.
- **Grouping:** Dictionary-based grouping by `Story|Label` key.
- **Bucket Aggregation:** Start (0-20%), Mid (20-80%), End (80-100%) zones.
- **Sign Preservation:** Negative moments (hogging) preserved for correct steel placement.
- **Fallback:** Built-in sample data (B1-B3) if no file selected.

### Sample Data Generator
- `Generate_Sample_ETABS_CSV`: Creates test CSV for validation.
- Output: Story, Label, Station, M3, V2, Output Case columns.

---

## When to Use This Role
- Adding or changing input/output table columns.
- Designing ETABS/CSV import/export features or macros.
- Validating third-party data formats before they hit the app layer.

---

## Output Expectations
1. **Schema spec:** columns, types, units, required/optional, defaults.
2. **Mapping rules:** how external fields map into BEAM_INPUT; handling missing/extra columns.
3. **Validation:** preflight checks and failure messages.
4. **Compatibility:** notes on versioning and how to avoid breaking old sheets/CSVs.

---

## Example Prompt
```
Act as INTEGRATION agent. Define the ETABS CSV -> BEAM_INPUT mapping, including required headers, units, and validation rules.
```
