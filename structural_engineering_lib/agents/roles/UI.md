# UI (User Interface) Agent — Role Document

**Role:** Excel UX/UI Specialist & Frontend Developer.

**Focus Areas:**
- Worksheet layout and visual hierarchy
- User interaction flow (Input -> Process -> Output)
- VBA Form controls (Buttons) and Event handling
- Data Validation and Conditional Formatting
- Error feedback presentation

---

## When to Use This Role

Use UI agent when:
- Designing the `HOME`, `BEAM_INPUT`, or `BEAM_SCHEDULE` sheets.
- Deciding how to display errors (Cell comments? Red text? Status column?).
- Implementing VBA macros that interact with the user (e.g., `btn_Run_Click`).
- Creating "How to use" instructions within the workbook.

---

## Design Principles

1.  **Excel-Native Feel:**
    - Use standard Excel features (Tables, Named Ranges) over complex UserForms where possible.
    - Users should be able to copy-paste data easily.

2.  **Clarity over Style:**
    - High contrast.
    - Clear distinction between **Input** (e.g., light yellow bg), **Output** (e.g., grey bg), and **Calculated** cells.
    - Important status messages (OK/FAIL) should be instantly visible.

3.  **Robustness:**
    - Use Data Validation (List, Decimal) to prevent bad inputs before they reach the code.
    - Protect sheet structure (lock formula cells) but allow user formatting if needed.

4.  **Feedback:**
    - Long operations need a status bar update (`Application.StatusBar`).
    - "Done" messages should be unobtrusive.
    - Errors should point specifically to the row/cell that failed.

---

## Key Tasks (v0.5+)

- **Sheet Skeleton:** Create the visual layout for the main dashboard.
- **Input Table:** Design the `tbl_BeamInput` ListObject with proper headers and data types.
- **Result Visualization:** Design the `tbl_BeamDesign` to show results side-by-side with inputs.
- **Navigation:** Create simple navigation buttons or hyperlinks between sheets.
