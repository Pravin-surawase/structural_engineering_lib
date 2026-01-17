# Quick Start — Run Your First Beam Design (5 Minutes)

This is the **fastest way to run real code** without setup headaches.

---

## Option 1: In the Terminal (Recommended First Time)

### Step 1: Activate the Python environment
```bash
cd /Users/Pravin/Library/Mobile\ Documents/com~apple~CloudDocs/pravin/projects/project_21_dec_25/structural_engineering_lib
source .venv/bin/activate
```

You should see:
```
(.venv) Pravin@Mac structural_engineering_lib %
```

### Step 2: Run a simple design
```bash
cd Python
python3 -c "
from structural_lib.codes.is456 import flexure

# Design a beam
result = flexure.design_singly_reinforced(
    b=300,           # width 300mm
    d=450,           # effective depth 450mm
    d_total=500,     # total depth 500mm
    mu_knm=150,      # load 150 kN·m
    fck=25,          # concrete grade 25
    fy=500           # steel grade 500
)

# Print results
print(f'✅ Steel required: {result.ast_required:.0f} mm²')
print(f'   Min allowed: {result.ast_min:.0f} mm²')
print(f'   Max allowed: {result.ast_max:.0f} mm²')
print(f'   Status: {\"SAFE\" if result.is_safe else \"UNSAFE\"}')"
```

**Expected output:**
```
✅ Steel required: 942 mm²
   Min allowed: 280 mm²
   Max allowed: 2250 mm²
   Status: SAFE
```

---

## Option 2: Create a Python Script

### Step 1: Create a file
```bash
cd Python
cat > my_first_beam.py << 'EOF'
#!/usr/bin/env python3
"""My first beam design."""

from structural_lib.codes.is456 import flexure, shear
from structural_lib import detailing

# Beam properties
b = 300           # width (mm)
d = 450           # effective depth (mm)
D = 500           # total depth (mm)
fck = 25          # concrete strength (N/mm²)
fy = 500          # steel strength (N/mm²)
mu_knm = 150      # load moment (kN·m)
vu_kn = 80        # shear force (kN)
cover = 40        # concrete cover (mm)

print("=" * 50)
print("BEAM DESIGN — First Example")
print("=" * 50)

# Step 1: Flexure design
print("\n1️⃣  FLEXURE DESIGN")
print(f"   Beam: {b}mm wide × {d}mm deep")
print(f"   Load: {mu_knm} kN·m")

flex_result = flexure.design_singly_reinforced(
    b=b, d=d, d_total=D, mu_knm=mu_knm, fck=fck, fy=fy
)

if flex_result.is_safe:
    print(f"   ✅ SAFE")
    print(f"   Steel required: {flex_result.ast_required:.0f} mm²")
else:
    print(f"   ❌ UNSAFE: {flex_result.error_message}")
    exit(1)

# Step 2: Shear design
print("\n2️⃣  SHEAR DESIGN")
print(f"   Shear force: {vu_kn} kN")

pt = (flex_result.ast_required / (b * d)) * 100

shear_result = shear.design_shear(
    vu_kn=vu_kn, b=b, d=d, fck=fck, fy=fy, asv=101, pt=pt
)

if shear_result.is_safe:
    print(f"   ✅ SAFE")
    print(f"   Stirrup spacing: {shear_result.spacing:.0f}mm")
else:
    print(f"   ❌ UNSAFE")
    exit(1)

# Step 3: Detailing
print("\n3️⃣  DETAILING")
bars = detailing.decide_bar_arrangement(
    ast_required=flex_result.ast_required, fy=fy
)
print(f"   Use: {bars}")

# Step 4: Development length
print("\n4️⃣  DEVELOPMENT LENGTH")
ld = detailing.calculate_development_length(
    bar_diameter=20, fck=fck, fy=fy, bond_type="Good"
)
print(f"   Bar extension: {ld:.0f}mm")

print("\n" + "=" * 50)
print("✅✅✅ ALL CHECKS PASSED ✅✅✅")
print("=" * 50)
EOF
```

### Step 2: Run it
```bash
python3 my_first_beam.py
```

**Expected output:**
```
==================================================
BEAM DESIGN — First Example
==================================================

1️⃣  FLEXURE DESIGN
   Beam: 300mm wide × 450mm deep
   Load: 150 kN·m
   ✅ SAFE
   Steel required: 942 mm²

2️⃣  SHEAR DESIGN
   Shear force: 80 kN
   ✅ SAFE
   Stirrup spacing: 150mm

3️⃣  DETAILING
   Use: [{'size': 20, 'count': 3}]

4️⃣  DEVELOPMENT LENGTH
   Bar extension: 650mm

==================================================
✅✅✅ ALL CHECKS PASSED ✅✅✅
==================================================
```

---

## Option 3: Using the CLI (Batch Design)

### Step 1: Create a CSV file with beam data
```bash
cat > input.csv << 'EOF'
BeamID,b,D,span,cover,fck,fy,Mu,Vu
B1,300,500,6000,40,25,500,100,60
B2,350,550,7000,40,25,500,150,80
B3,400,600,8000,40,30,500,200,100
EOF
```

### Step 2: Run the design CLI
```bash
python3 -m structural_lib design input.csv -o results.json
```

### Step 3: See the results
```bash
cat results.json | python3 -m json.tool | head -50
```

**You'll get JSON with all results for all beams!**

---

## Understanding the Output

```python
result.ast_required  # Area of steel needed (mm²)
result.ast_min       # Minimum by code (mm²)
result.ast_max       # Maximum by code (mm²)
result.is_safe       # True = beam is safe, False = failed
result.error_message # Why it failed (if it did)
```

**Real example output:**
```
ast_required = 942 mm²     ← This is what you use
ast_min = 280 mm²          ← Can't use less than this
ast_max = 2250 mm²         ← Can't use more than this
is_safe = True             ← Design worked!
error_message = None       ← No errors
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **"ModuleNotFoundError: No module named 'structural_lib'"** | Make sure you're in `Python/` directory and venv is activated |
| **Results seem too large** | Check you used mm for dimensions, not meters |
| **Script says "UNSAFE"** | Increase beam depth (d) or use `design_doubly_reinforced()` |
| **It's running slow** | Normal for first time, Python compiles. Second run is fast |

---

## Next Step

Read `FUNCTION-GUIDE.md` in this same folder. It explains every function in plain English.

---

**Congratulations! You've run your first beam design! 🎉**

Created: 2026-01-13
For: Quick start, no reading
