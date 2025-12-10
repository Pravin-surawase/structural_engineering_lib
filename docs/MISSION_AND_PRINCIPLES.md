# StructEng Automation – Mission, Vision & Principles

## 1. Why this project exists

Structural engineering today, especially in everyday practice (beams, slabs, columns, walls), has a few recurring problems:
*   Critical calculations are scattered across messy Excel sheets, half-remembered macros, and “that one file” on someone’s desktop.
*   Tools are either:
    *   Too primitive (random Excel from a WhatsApp group), or
    *   Too heavy/expensive (complex plugins and software stacks meant for very large firms).
*   There’s rarely a clear, transparent link from:
    *   ETABS model → design → schedule → drawings → final checking.
*   Juniors often press buttons without understanding, seniors don’t have time to teach properly, and reviews are rushed.

This project exists to change that.

We want to build tools that:
*   Automate boring, error-prone work.
*   Expose assumptions and calculations instead of hiding them.
*   Help engineers think more clearly, not replace them.

---

## 2. Our mission

To build an open, transparent, and reusable structural design core that makes everyday RC design (starting with beams) more robust, auditable, and easy to automate – especially for Indian and similar code environments.

Concretely, our mission includes:

1.  **Engineering robustness first**
    *   Calculations must be correct, traceable, and code-consistent.
    *   If there’s a conflict between “fancy tech” and “clear, correct engineering”, engineering wins.

2.  **Library over spaghetti**
    *   Structural logic should live in a clean, reusable library, not buried across thousands of cells and macros.
    *   We start in VBA for Excel, but plan for a future Python library with the same logic.

3.  **Excel as the first-class UI**
    *   Most civil/structural engineers already live in Excel.
    *   Our first tools should feel natural there: sheets, buttons, schedules, simple workflows.

4.  **AI as explainer & assistant, not black-box designer**
    *   AI will help explain, document, and sanity-check designs.
    *   It will NOT silently decide reinforcement without clear formulas behind it.

5.  **Open and shareable**
    *   Wherever possible, formulas, assumptions, and code should be shareable and open (within reasonable licensing).
    *   We want others to understand, critique, and build on our work.

---

## 3. Vision (5–10 years)

If we’re successful, this is what the world looks like:

*   There is a widely-known “structural core library” (starting with IS 456 beams, later walls, columns, slabs, other codes) that:
    *   has a clear API,
    *   is open-source or semi-open,
    *   is trusted for everyday RC design tasks.

*   A typical workflow in a small or mid-size office:
    1.  Model in ETABS.
    2.  Export to a known format (or direct API).
    3.  Run through our design engine:
        *   beams/columns/walls are designed,
        *   schedules are generated,
        *   checks and failures are clearly listed.
    4.  AI assistants generate:
        *   explanation of key design decisions,
        *   checklists for review,
        *   suggestions where the model/design looks suspicious.

*   Young engineers learn by using these tools:
    *   They can click on any beam and see:
        *   what formula was used,
        *   what code clause applies,
        *   which assumption controlled the design.

*   Senior engineers use it as:
    *   a second pair of eyes,
    *   a way to impose standards and reduce chaos,
    *   a way to onboard new people faster.

And for us personally:
*   We have an ecosystem of tools and libraries with our fingerprints on them.
*   Even if any product “fails” commercially, the library, knowledge, and patterns remain useful – for us and others.

---

## 4. Product philosophy

### 4.1 “Small, sharp tools” over “giant platforms”

We are not trying to build an all-in-one monolithic software from day one.

We prefer:
*   Small, well-defined components:
    *   beam engine,
    *   wall engine,
    *   schedule generator,
    *   ETABS importer.
*   Each component:
    *   does one job clearly,
    *   has a well-defined input/output,
    *   can be tested and used in isolation.

Our first tool is Beam Engine IS 456 – Excel Edition. It should feel like:
*   a solid, reliable screwdriver,
*   not some 400-feature multi-tool nobody trusts.

### 4.2 Transparency beats magic

We avoid:
*   “Click here and trust us.”
*   Hidden tables, magic constants, silent overrides.

We prefer:
*   “Click here, and you can see exactly how and why we arrived at this design.”
*   Clear logs, intermediate outputs, references to code clauses, visible formula derivations.

If someone asks “Where did this Ast value come from?” they should be able to see:
*   input Mu, b, d, fck, fy,
*   internal assumptions,
*   formula used,
*   code reference.

### 4.3 Respect for existing workflows

We don’t force people to abandon ETABS, Excel, CAD.
We:
*   integrate with them, not fight them,
*   start with copy-paste/CSV → later API integrations.

Our tools should slot into existing workflows:
*   ETABS → Excel → CAD,
*   not demand a full ecosystem replacement.

---

## 5. Technical philosophy

### 5.1 Deterministic core

Core design logic must be:
*   deterministic (same inputs → same outputs),
*   versioned (we know what changed and when),
*   easy to test (we can write test cases, compare with textbook/handbook examples).

This core lives in:
*   VBA structural library first,
*   later mirrored in Python (and potentially other environments).

### 5.2 Separation of concerns

We strictly separate:
*   Domain logic (IS 456 equations, engineering checks)
*   Application logic (looping over beams, deciding status flags, mapping to schedules)
*   UI / I/O (Excel sheets, ETABS imports, messages, formatting)

We do not mix:
*   sheet formatting inside engineering formulas, or
*   file parsing inside structural calculations.

This makes it possible to:
*   reuse the core in different UIs,
*   test logic without needing Excel open,
*   port to Python without rewriting concepts.

### 5.3 Minimal dependencies, maximum clarity

We avoid unnecessary complexity:
*   No fancy frameworks,
*   No overkill infra (Kubernetes etc.),
*   No magical Excel add-in architectures before we need them.

But we embrace:
*   Git for version control,
*   clear folder structures,
*   basic CI/testing (especially when Python layer comes in),
*   code comments that actually help.

---

## 6. User personas (who we’re building for)

### 6.1 Primary user (now): practicing structural engineer
*   Works in a small/mid office or as an individual consultant.
*   Uses ETABS + Excel + AutoCAD.
*   Pain points:
    *   repetitive, manual calc work,
    *   error-prone data transfer,
    *   low visibility of where designs are weak/critical.

What they want:
*   A reliable Excel tool that:
    *   reads their beam data (manual or ETABS-derived),
    *   designs beams per IS 456,
    *   outputs schedules ready for CAD,
    *   doesn’t feel like a black box.

### 6.2 Secondary user: senior engineer / checker
*   Reviews designs from juniors.
*   Needs confidence, not hand-waving.
*   Wants:
    *   quick indication of where beams are overstressed,
    *   ability to drill into one beam and see detailed calc steps.

### 6.3 Future user: developer / tool-builder
*   Might want to integrate the library into their own tools.
*   They care about:
    *   clean API,
    *   clear functions,
    *   license that permits usage,
    *   good test cases.

We build with all three in mind.

---

## 7. Non-goals and boundaries (what we are not doing right now)

To keep focus, we explicitly do NOT aim for:
*   Full building code coverage (all clauses of all Indian codes) in v0.
*   Auto-drawing or Revit/CAD plugins in early phases.
*   “One click complete design of entire building” at the start.
*   A web platform with user logins, subscriptions, dashboards – until core tools are solid.
*   Replacing engineering judgment with AI decisions.

We can grow into some of these over time, but they are not early priorities.

---

## 8. How we measure success (beyond money)

For this project, early success looks like:

1.  **Technical quality**
    *   A clear structural library (VBA) with well-defined functions.
    *   A beam workbook that runs reliably on real projects.
    *   Tests that compare our outputs with validated examples.

2.  **User reality**
    *   At least a handful of engineers using the tool on real jobs.
    *   Feedback that it:
        *   saves time,
        *   catches errors,
        *   is understandable.

3.  **Reusability & trajectory**
    *   A repo that:
        *   others can read and understand,
        *   can be ported to Python,
        *   can host future modules (walls, columns, etc.).
    *   Early signs that this can grow into a broader structural automation suite.

Revenue can come later if it makes sense, but our main metrics for now are:
*   robustness,
*   adoption (even if small),
*   and how much it raises the standard of everyday structural practice.

---

## 9. How AI tools (like VS Code AI) should support this mission

When an AI works on this project, it should:
*   Be grounded in this mission:
    *   correctness over clever hacks,
    *   structure over chaos,
    *   clarity over “smart but opaque” solutions.
*   Always ask:
    *   “Is this logic in the right layer?” (lib vs app vs UI)
    *   “Are the units and assumptions clear?”
    *   “Would a structural engineer, reading this, trust it?”
*   Help with:
    *   designing and refining the library functions,
    *   keeping code and file structure clean,
    *   proposing tests and edge cases,
    *   generating documentation, explanations, and change summaries.
*   Avoid:
    *   overcomplicating infrastructure,
    *   mixing engineering logic with UI-specific details,
    *   inventing features that are not aligned with the current phase.
