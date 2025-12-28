# Guides (Simple and Practical)

These are short guides to help you work confidently.

## How to read any function (3 steps)
1) Read the arguments. What are the units and types?
2) Scan the calculations. Look for formulas and lookups.
3) Read the return type. What fields are returned?

## How to debug a wrong result
1) Check units first (mm, kN, kN-m, N/mm^2).
2) Print the intermediate values (Mu_lim, tau_v, xu).
3) Compare with the formulas in docs/reference/is456-formulas.md.

## How to add a feature safely
1) Add the code in the correct module (flexure, shear, serviceability, etc.).
2) Add or update a test.
3) Update docs/reference/api.md.
4) Run ./scripts/ci_local.sh.

## How to trust your outputs
- Use the verification examples in docs/verification/examples.md.
- Use parity vectors for VBA and Python.
- Keep outputs deterministic (same input -> same output).

## How to use AI safely
- Ask AI for explanations, not for unchecked math.
- Always verify formulas against IS 456.
- Treat AI code as a draft, not a final answer.
