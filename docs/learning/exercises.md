# Exercises (Hands-On, Beginner Friendly)

These exercises are small and safe. They build confidence without heavy math.

## Exercise 1: Run a single beam
- Use the one-liner in docs/getting-started/python-quickstart.md
- Confirm you see Ast required and Status OK

## Exercise 2: Run the CLI on a tiny CSV
1) Create a CSV with one beam (see beginners-guide.md)
2) Run:
   python -m structural_lib design beams.csv -o results.json
3) Open results.json and find:
   - flexure.ast_required
   - shear.spacing

## Exercise 3: Add serviceability Level A
Run:
python -m structural_lib design beams.csv -o results.json --deflection
Check results.json:
- deflection_status should be ok or fail

## Exercise 4: Generate a BBS
Run:
python -m structural_lib bbs results.json -o schedule.csv
Open schedule.csv and verify:
- total_weight_kg is not zero

## Exercise 5: Generate a DXF
Run:
python -m structural_lib dxf results.json -o drawings.dxf --title-block --title "Beam Sheet"
Open the DXF in any viewer.

## Exercise 6: Batch run without ETABS
Run:
python Python/examples/full_pipeline_synthetic.py --count 50 --output-dir ./output/demo_50
Review outputs:
- results.json, schedule.csv, drawings.dxf

## Exercise 7: Read one test
Open Python/tests/test_critical_is456.py
Pick one test and explain:
- input
- expected value
- why it matters

## Exercise 8: Tiny code change (safe)
- Change a title string in CLI help
- Run: python -m structural_lib --help
- Confirm it matches
