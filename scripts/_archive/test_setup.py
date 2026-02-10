#!/usr/bin/env python3
"""Quick test of structural_lib installation"""

from structural_lib import flexure

res = flexure.design_singly_reinforced(
    b=300, d=450, d_total=500, mu_knm=150, fck=25, fy=500
)
status = "OK" if res.is_safe else res.error_message
print(f"Ast required: {res.ast_required:.0f} mm^2 | Status: {status}")
print("✓ Setup successful! Library is working correctly.")
