# Extension Guide: Adding Features Without Modifying Core

**Type:** Guide
**Audience:** Developers
**Status:** Production Ready
**Importance:** High
**Created:** 2026-01-15
**Last Updated:** 2026-01-15

---

## Overview

This guide shows you how to **extend the library** with custom features **without modifying core code**. This ensures:

- ✅ Your extensions survive library updates
- ✅ No merge conflicts when upgrading
- ✅ Clean separation between core and custom logic
- ✅ Easy to maintain and test

---

## Extension Patterns

### Pattern 1: Wrapper Functions

**Add custom logic around core functions:**

```python
# custom_validators.py
from structural_lib.api import design_beam_is456
from structural_lib.data_types import DesignError

def design_beam_with_seismic_rules(span_mm, mu_knm, vu_kn, **kwargs):
    """
    Design beam with additional seismic requirements per IS 1893.

    Adds checks for:
    - Minimum steel ratio (1.2% for ductility)
    - Stirrup spacing (max 100mm in plastic hinge zones)
    - Minimum stirrup diameter (10mm for confinement)
    """

    # 1. Call core design function
    result = design_beam_is456(
        span_mm=span_mm,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        **kwargs
    )

    # 2. Add custom validation
    if result.ok:
        errors = []

        # Check 1: Steel ratio for ductility
        steel_ratio = result.ast_required_start / (result.b * result.d)
        if steel_ratio < 0.012:
            errors.append(DesignError(
                error_message=f"Seismic: Steel ratio {steel_ratio:.3f} < 1.2% (IS 1893 requirement)",
                field_name="ast",
                severity="ERROR"
            ))

        # Check 2: Stirrup spacing for confinement
        if result.stirrups_start.spacing > 100:
            errors.append(DesignError(
                error_message=f"Seismic: Stirrup spacing {result.stirrups_start.spacing}mm > 100mm (ductile detailing)",
                field_name="stirrups",
                severity="ERROR"
            ))

        # Check 3: Stirrup diameter
        if result.stirrups_start.diameter < 10:
            errors.append(DesignError(
                error_message=f"Seismic: Stirrup diameter {result.stirrups_start.diameter}mm < 10mm min",
                field_name="stirrups",
                severity="ERROR"
            ))

        # Update result if failures found
        if errors:
            result.ok = False
            result.errors.extend(errors)

    return result
```

**Usage:**
```python
result = design_beam_with_seismic_rules(
    span_mm=5000,
    mu_knm=120,
    vu_kn=80,
    b_mm=300,
    D_mm=500,
    fck_nmm2=25.0,
    fy_nmm2=500.0,
)

# Now includes seismic checks automatically
if result.ok:
    print("✓ Passes IS 456 + IS 1893")
else:
    print("Seismic violations found")
```

---

### Pattern 2: Custom Design Codes

**Implement alternative design codes (ACI, Eurocode, etc.):**

```python
# aci318_module.py
"""ACI 318 (US code) beam design implementation."""

from structural_lib.data_types import BeamDesignResult, BarArrangement, StirrupArrangement

def design_beam_aci318(width_in, depth_in, mu_kipft, vu_kip,
                       fc_psi=4000, fy_ksi=60, cover_in=1.5):
    """
    Design reinforced concrete beam per ACI 318-19.

    Args:
        width_in: Beam width (inches)
        depth_in: Beam total depth (inches)
        mu_kipft: Factored moment (kip-ft)
        vu_kip: Factored shear (kip)
        fc_psi: Concrete strength (psi)
        fy_ksi: Steel yield strength (ksi)
        cover_in: Clear cover (inches)

    Returns:
        BeamDesignResult (uses same structure as IS 456)
    """

    # Convert units
    mu_inkip = mu_kipft * 12  # kip-ft to in-kip
    d_in = depth_in - cover_in - 0.5  # Effective depth

    # Calculate required steel (ACI equations)
    # Rn = Mu / (φ * b * d²) where φ = 0.9
    phi = 0.9
    Rn = mu_inkip / (phi * width_in * d_in**2)  # psi

    # ρ = (0.85fc/fy)[1 - √(1 - 2Rn/(0.85fc))]
    rho = (0.85 * fc_psi / (fy_ksi * 1000)) * \
          (1 - (1 - 2*Rn/(0.85*fc_psi))**0.5)

    As_required = rho * width_in * d_in  # in²

    # Select bars (US bar sizes)
    bar_database = {
        "#4": 0.20, "#5": 0.31, "#6": 0.44,
        "#7": 0.60, "#8": 0.79, "#9": 1.00,
    }

    for bar_size, bar_area in bar_database.items():
        count = int(As_required / bar_area) + 1
        if count <= 6:  # Max 6 bars single layer
            break

    # Check shear (simplified)
    Vc = 2 * (fc_psi**0.5) * width_in * d_in / 1000  # kip
    shear_ok = (vu_kip / phi) <= Vc

    # Select stirrups if needed
    if shear_ok:
        stirrups = StirrupArrangement(
            diameter=10,  # #3 stirrups (~10mm)
            legs=2,
            spacing=min(d_in * 25.4 / 2, 600),  # mm (ACI max spacing)
            zone_length=1000,
        )
    else:
        # Design stirrups (simplified)
        stirrups = StirrupArrangement(
            diameter=10,
            legs=2,
            spacing=min(d_in * 25.4 / 4, 300),  # Tighter spacing
            zone_length=1000,
        )

    # Return result (convert to mm for consistency with library)
    return BeamDesignResult(
        ok=True,
        beam_id="ACI_DESIGN",
        story="ACI 318",
        span=width_in * 25.4,  # Convert to mm
        b=width_in * 25.4,
        D=depth_in * 25.4,
        d=d_in * 25.4,
        cover=cover_in * 25.4,
        ast_required_start=As_required * 645.16,  # in² to mm²
        bars_bottom_start=BarArrangement(
            count=count,
            diameter=int(bar_size[1:]) * 3.175,  # US # to mm (approx)
            area_provided=count * bar_area * 645.16,
            spacing=100,
            layers=1
        ),
        stirrups_start=stirrups,
        # ... additional fields as needed
    )

# Usage - same as IS 456!
result = design_beam_aci318(
    width_in=12,
    depth_in=20,
    mu_kipft=150,
    vu_kip=40,
)

print(f"ACI Design: {result.bars_bottom_start.count} bars")
```

**Benefits:**
- Reuses library data structures
- Same interface as IS 456 design
- Can use library utilities (DXF export, BBS, reports)

---

### Pattern 3: Custom Output Formats

**Add new export formats without touching core:**

```python
# excel_exporter.py
"""Export beam design to Excel with custom formatting."""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from structural_lib.api import design_beam_is456

def export_to_excel(design_result, output_path, company_name=""):
    """
    Export beam design to formatted Excel file.

    Args:
        design_result: BeamDesignResult from design_beam_is456()
        output_path: Path to save .xlsx file
        company_name: Optional company name for header

    Returns:
        Path to generated Excel file
    """

    wb = Workbook()
    ws = wb.active
    ws.title = "Beam Design"

    # Header
    ws["A1"] = company_name if company_name else "Beam Design Report"
    ws["A1"].font = Font(size=14, bold=True)
    ws["A1"].fill = PatternFill(start_color="4472C4", fill_type="solid")
    ws["A1"].font = Font(size=14, bold=True, color="FFFFFF")
    ws.merge_cells("A1:D1")

    # Input parameters
    row = 3
    ws[f"A{row}"] = "INPUT PARAMETERS"
    ws[f"A{row}"].font = Font(bold=True)
    row += 1

    inputs = [
        ("Beam ID", design_result.beam_id),
        ("Story", design_result.story),
        ("Span (mm)", design_result.span),
        ("Width (mm)", design_result.b),
        ("Depth (mm)", design_result.D),
        ("Cover (mm)", design_result.cover),
    ]

    for label, value in inputs:
        ws[f"A{row}"] = label
        ws[f"B{row}"] = value
        row += 1

    # Design results
    row += 2
    ws[f"A{row}"] = "DESIGN RESULTS"
    ws[f"A{row}"].font = Font(bold=True)
    row += 1

    if design_result.ok:
        ws[f"A{row}"] = "Status"
        ws[f"B{row}"] = "✓ OK"
        ws[f"B{row}"].font = Font(color="00B050")
        row += 1

        # Reinforcement
        ws[f"A{row}"] = "Bottom Steel (Start)"
        ws[f"B{row}"] = design_result.bars_bottom_start.callout()
        row += 1

        ws[f"A{row}"] = "Top Steel (Start)"
        ws[f"B{row}"] = design_result.bars_top_start.callout()
        row += 1

        ws[f"A{row}"] = "Stirrups (Start)"
        ws[f"B{row}"] = design_result.stirrups_start.callout()
        row += 1
    else:
        ws[f"A{row}"] = "Status"
        ws[f"B{row}"] = "✗ FAILED"
        ws[f"B{row}"].font = Font(color="FF0000")
        row += 1

        # Errors
        for error in design_result.errors:
            ws[f"A{row}"] = "Error"
            ws[f"B{row}"] = error.error_message
            row += 1

    # Auto-size columns
    for col in ["A", "B", "C", "D"]:
        ws.column_dimensions[col].width = 25

    wb.save(output_path)
    return output_path

# Usage
result = design_beam_is456(...)
export_to_excel(result, "beam_design.xlsx", "My Company")
```

---

### Pattern 4: Plugin Architecture

**Create reusable plugins:**

```python
# plugin_base.py
"""Base class for beam design plugins."""

from abc import ABC, abstractmethod

class BeamDesignPlugin(ABC):
    """Base class for all beam design plugins."""

    def __init__(self, name):
        self.name = name
        self.enabled = True

    @abstractmethod
    def validate(self, result):
        """Validate design result. Return list of errors."""
        pass

    @abstractmethod
    def enhance(self, result):
        """Enhance design result. Return modified result."""
        pass

# seismic_plugin.py
class SeismicPlugin(BeamDesignPlugin):
    """Plugin for seismic design checks."""

    def __init__(self):
        super().__init__("Seismic Checker")

    def validate(self, result):
        """Add seismic validation rules."""
        errors = []

        if result.ok:
            # Check 1: Steel ratio
            steel_ratio = result.ast_required_start / (result.b * result.d)
            if steel_ratio < 0.012:
                errors.append("Seismic: Steel ratio < 1.2%")

            # Check 2: Stirrup spacing
            if result.stirrups_start.spacing > 100:
                errors.append("Seismic: Stirrup spacing > 100mm")

        return errors

    def enhance(self, result):
        """No enhancements needed for seismic."""
        return result

# cost_plugin.py
class CostEstimationPlugin(BeamDesignPlugin):
    """Plugin for cost estimation."""

    def __init__(self, price_concrete=6000, price_steel=70):
        super().__init__("Cost Estimator")
        self.price_concrete = price_concrete  # INR per m³
        self.price_steel = price_steel  # INR per kg

    def validate(self, result):
        """No validation for cost."""
        return []

    def enhance(self, result):
        """Add cost estimate to result."""
        if result.ok:
            # Calculate concrete volume
            concrete_vol = result.b * result.D * result.span / 1e9  # mm³ to m³
            concrete_cost = concrete_vol * self.price_concrete

            # Calculate steel weight (approx 7850 kg/m³)
            steel_area = result.ast_required_start  # mm²
            steel_vol = steel_area * result.span / 1e9  # mm³ to m³
            steel_weight = steel_vol * 7850  # kg
            steel_cost = steel_weight * self.price_steel

            # Add to result (extend result object)
            result.estimated_cost = concrete_cost + steel_cost
            result.cost_breakdown = {
                "concrete": concrete_cost,
                "steel": steel_cost,
            }

        return result

# plugin_manager.py
class PluginManager:
    """Manage and apply plugins to design results."""

    def __init__(self):
        self.plugins = []

    def register(self, plugin):
        """Register a plugin."""
        self.plugins.append(plugin)
        print(f"Registered plugin: {plugin.name}")

    def apply(self, result):
        """Apply all plugins to design result."""
        all_errors = []

        for plugin in self.plugins:
            if not plugin.enabled:
                continue

            # Validate
            errors = plugin.validate(result)
            all_errors.extend(errors)

            # Enhance
            result = plugin.enhance(result)

        # Update result with plugin errors
        if all_errors:
            result.ok = False
            result.errors.extend([
                DesignError(error_message=e) for e in all_errors
            ])

        return result

# Usage
from structural_lib.api import design_beam_is456

# Create plugin manager
manager = PluginManager()
manager.register(SeismicPlugin())
manager.register(CostEstimationPlugin(price_concrete=6500, price_steel=75))

# Design beam
result = design_beam_is456(...)

# Apply plugins
result = manager.apply(result)

# Now result has seismic checks + cost estimate
if result.ok:
    print(f"Cost: ₹{result.estimated_cost:.0f}")
    print(f"Breakdown: Concrete ₹{result.cost_breakdown['concrete']:.0f}, Steel ₹{result.cost_breakdown['steel']:.0f}")
```

---

## Best Practices

### 1. Don't Modify Core Files

**❌ DON'T:**
```python
# Modifying Python/structural_lib/flexure.py
def design_singly_reinforced(...):
    # Adding seismic checks HERE
    if seismic_zone > 3:
        ...  # Will break on library updates!
```

**✅ DO:**
```python
# Create my_extensions/seismic.py
from structural_lib.flexure import design_singly_reinforced

def design_with_seismic(...):
    result = design_singly_reinforced(...)
    # Add custom logic here
    return result
```

### 2. Reuse Library Data Structures

**✅ DO:**
```python
from structural_lib.data_types import BeamDesignResult, BarArrangement

def my_custom_function(...):
    # Return same structures library uses
    return BeamDesignResult(...)
```

**Why?**
- Compatible with library utilities (DXF export, BBS, reports)
- Type-safe with IDE autocomplete
- Easy to test and validate

### 3. Test Your Extensions

```python
# test_my_extensions.py
import pytest
from my_extensions.seismic import design_with_seismic

def test_seismic_check_passes():
    """Test seismic design for adequate steel."""
    result = design_with_seismic(
        span_mm=5000,
        mu_knm=120,
        vu_kn=80,
        b_mm=300,
        D_mm=500,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
    )

    assert result.ok, "Design should pass seismic checks"

def test_seismic_check_fails():
    """Test seismic rejection for low steel."""
    result = design_with_seismic(
        span_mm=8000,  # Long span
        mu_knm=50,     # Low moment
        vu_kn=40,
        b_mm=300,
        D_mm=400,
        fck_nmm2=20.0,
        fy_nmm2=500.0,
    )

    assert not result.ok, "Should fail seismic checks"
    assert any("Seismic" in e.error_message for e in result.errors)
```

---

## Common Extension Scenarios

### Scenario 1: Add Regional Pricing

```python
# regional_pricing.py
from structural_lib.api import optimize_beam_cost

REGIONAL_PRICES = {
    "Mumbai": {
        "concrete_m3": 6500,
        "steel_kg": 75,
        "formwork_m2": 450,
    },
    "Delhi": {
        "concrete_m3": 6000,
        "steel_kg": 70,
        "formwork_m2": 400,
    },
    "Bangalore": {
        "concrete_m3": 6200,
        "steel_kg": 72,
        "formwork_m2": 420,
    },
}

def optimize_regional(span_mm, mu_knm, vu_kn, region="Mumbai"):
    """Optimize with regional pricing."""
    prices = REGIONAL_PRICES[region]

    return optimize_beam_cost(
        span_mm=span_mm,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        price_concrete_per_m3=prices["concrete_m3"],
        price_steel_per_kg=prices["steel_kg"],
        price_formwork_per_m2=prices["formwork_m2"],
    )
```

### Scenario 2: Add Company-Specific Rules

```python
# company_rules.py
from structural_lib.api import design_beam_is456

class CompanyDesignRules:
    """Company-specific design preferences."""

    # Preferred bar sizes (mm)
    PREFERRED_BARS = [12, 16, 20, 25]

    # Maximum span/depth ratio
    MAX_SPAN_DEPTH_RATIO = 20

    @classmethod
    def design_beam(cls, **kwargs):
        """Design with company rules."""
        result = design_beam_is456(**kwargs)

        if result.ok:
            # Check span/depth ratio
            ratio = kwargs["span_mm"] / kwargs["D_mm"]
            if ratio > cls.MAX_SPAN_DEPTH_RATIO:
                result.ok = False
                result.errors.append(DesignError(
                    error_message=f"Company rule: Span/depth ratio {ratio:.1f} > {cls.MAX_SPAN_DEPTH_RATIO}"
                ))

            # Check bar sizes
            bar_dia = result.bars_bottom_start.diameter
            if bar_dia not in cls.PREFERRED_BARS:
                # Find nearest preferred size
                nearest = min(cls.PREFERRED_BARS, key=lambda x: abs(x - bar_dia))
                result.warnings = result.warnings or []
                result.warnings.append(
                    f"Consider using T{nearest} instead of T{bar_dia} (company preference)"
                )

        return result
```

---

## Next Steps

1. **Explore Examples** → [Integration Examples](integration-examples.md)
2. **Check API** → [API Reference](../reference/api.md)
3. **Build Extension** → Use patterns from this guide
4. **Test Extension** → Write unit tests
5. **Share with Community** → Open GitHub issue to feature your work!

---

**Questions?** [Open an issue](https://github.com/Pravin-surawase/structural_engineering_lib/issues)
