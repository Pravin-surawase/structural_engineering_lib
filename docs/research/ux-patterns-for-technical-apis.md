# User Experience Patterns for Technical APIs

**Status:** Draft
**Task:** TASK-201
**Date:** 2026-01-07
**Author:** AI Researcher

## 1. Executive Summary

This research focuses on the "Developer Experience" (DX) of using `structural_engineering_lib`. Just as a graphical UI needs to be intuitive, a library's Public API must be intuitive. The goal is to maximize **"Time to First Success"** and minimize **"Cognitive Load"**.

**Core Philosophy:** The library should be a *force multiplier* for the engineer, not a puzzle to be solved. We aim for the **"Pit of Success"**—designing the API such that falling into the correct usage is inevitable.

---

## 2. Cognitive Load Management

Cognitive load is the amount of mental effort required to use the library. High load leads to bugs and frustration.

### 2.1 The "Rule of Seven" (Information Chunking)
*   **Principle:** Users can only hold ~7 items in short-term memory.
*   **Application:** Functions with >5 parameters require looking up documentation.
*   **Solution:**
    *   **Parameter Grouping:** Use Data Classes/Pydantic models for configuration `(span, load, width, depth, DesignConfig)`.
    *   **Progressive Disclosure:** Hide advanced options behind `**kwargs` or optional arguments with sensible defaults.
    *   **Consistency:** If `width` is the 2nd argument in `design_beam`, it MUST be the 2nd in `check_shear`.

### 2.2 Naming as Interface
*   **Verb-Noun-Adjective Pattern:** `verbs` (methods) and `nouns` (classes) must be distinct.
    *   *Good:* `beam.calculate_deflection()`
    *   *Bad:* `beam.deflection()` (Is it a property? A calculation?)
*   **Suffixes for Units:** Ambiguity is the enemy.
    *   *Risky:* `length` (meters? mm? inches?)
    *   *Safe:* `length_mm` or `Length` type.
    *   *Professional:* Type hints `length: Millimeters`.

### 2.3 "One Way to Do It" vs Flexibility
*   Python's Zen: "There should be one-- and preferably only one --obvious way to do it."
*   **Anti-Pattern:** Supporting `beam.design()`, `design(beam)`, and `beam.run_design()` simultaneously without deprecation.
*   **Strategy:** Define a single "Canonical Path" for every major task.

---

## 3. Discoverability & The "Pit of Success"

### 3.1 IDE-Driven Development
Modern development relies on Autocomplete (Intellisense/LSP).
*   **Type Hints are Documentation:** They are not just for linting; they trigger IDE tooltips.
*   **Docstring Previews:** The first line of the docstring is critical; it shows in the autocomplete popup.
*   **Namespace Organization:** Flat namespaces (`import structural_lib`) are hard to explore. Hierarchical namespaces (`structural_lib.concrete.beams`) guide discovery.

### 3.2 The "Pit of Success" Design
*   **Definition:** The default path is the correct path. It's harder to use the API wrongly than rightly.
*   **Application:**
    *   **Required vs Optional:** Mandatory mechanics (span, load) must be required arguments. Toggles (logging, optimizations) must be optional.
    *   **Safe Defaults:** Default to the most conservative engineering assumption (e.g., standard exposure, standard fire rating) rather than `None`.
    *   **Guardrails:** Fail fast if inputs are physically impossible (negative depth, zero span) *before* doing complex math.

---

## 4. Error Experience (Error UX)

Errors are part of the user interface. A stack trace is a "UI failure".

### 4.1 Errors as Guides
*   **Bad Error:** `IndexError: list index out of range` (Implementation leak)
*   **Better Error:** `ValueError: Beam checks failed` (Domain context)
*   **Best Error:** `ComplianceError: Beam failed deflection check. Span/Depth ratio (22.5) > Allowable (20.0). Increase depth or add compression reinforcement.` (Actionable advice)

### 4.2 Hierarchy and Catchability
*   Users must be able to catch high-level errors without catching `Exception`.
*   **Recommended Hierarchy:**
    *   `StructuralError` (Base)
        *   `InputError` (User input invalid)
        *   `CalculationError` (Math failed/non-convergence)
        *   `ComplianceError` (Valid math, but design code violation)

---

## 5. Specific Pain Point Analysis (Review of Current State)

Based on the library's current state, we identify these friction points:

### 5.1 The "Tuple Mystery"
*   **Current:** `calculate_ast(...)` returns `(1250.5, 4, 16)`.
*   **Friction:** User must remember: `index 0 = area`, `index 1 = count`, `index 2 = diameter`.
*   **Fix:** Return `ReinforcementResult(area=1250.5, count=4, diameter=16)`.

### 5.2 The "Magic Constant" Problem
*   **Current:** Hardcoded `25000` (Concrete E modulus) inside functions.
*   **Friction:** User assumes standard concrete, but high-strength concrete requires different E.
*   **Fix:** Explicit config object or `materials.py` constants that can be overridden.

### 5.3 Inconsistent Units
*   Current functions mostly assume `mm` and `N`, but some might take `m` or `kN-m`.
*   **Fix:** **Strict Unit Standard**: All internal math in `N` and `mm`. All inputs documented or typed clearly.

---

## 6. UX Recommendations for `structural_engineering_lib`

1.  **Adopt Typed Result Objects:** Eliminate tuple returns immediately for public APIs.
2.  **Enforce Keyword-Only Arguments:** For any function with >3 parameters, forces readability: `design_beam(3000, 10, width=230, depth=450)` vs `design_beam(3000, 10, 230, 450)`.
3.  **Actionable Error Messages:** Errors must answer: "What happened?", "Why?", and "How do I fix it?".
4.  **Examples in Docstrings:** Every public function must have a runnable `Examples:` section.
5.  **"Smart" Entry Points:** Create a `Job` object that validates the entire problem setup before running, rather than failing 50% through a batch run.
6.  **Progress Feedback:** For long-running optimizations, provide hooks for progress bars or logging, don't just `print()`.

---
