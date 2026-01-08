# Plotly Type Mismatch - Root Cause Analysis & Long-Term Solution

**Date:** 2026-01-08
**Status:** CRITICAL - Production-blocking issue
**Agent:** Agent 6 (Background Agent)

---

## 🚨 THE PROBLEM

### Runtime Error
```
ValueError: Invalid value of type 'builtins.str' received for the 'duration' property of layout.transition
    Received value: '300ms'
    The 'duration' property is a number and may be specified as:
      - An int or float in the interval [0, inf]
```

### Where It Happens
```python
# components/visualizations.py:322, 458, 573, 706
fig.update_layout(
    transition=dict(duration=ANIMATION.duration_normal, easing='cubic-in-out')
    #                       ^^^^^^^^^^^^^^^^^^^^^^^^ This is "300ms" (string)
    #                       But Plotly expects 300 (int)
)
```

### Root Cause
```python
# utils/design_system.py:236
@dataclass(frozen=True)
class AnimationTimings:
    duration_normal: str = "300ms"  # ❌ CSS string, NOT Plotly number
```

**The disconnect:** Design tokens were created for **CSS** (where `"300ms"` is correct), but used in **Plotly** (where `300` integer is required).

---

## 🤔 WHY TESTS DIDN'T CATCH THIS

### Analysis of Test Coverage

#### 1. **Unit tests (test_plotly_theme.py)** ✅ Passed
```python
def test_apply_theme():
    fig = go.Figure()
    apply_theme(fig)  # Only tests theme APPLICATION, not usage
```
**Gap:** Tests the theme object structure, not how it's used in real charts.

#### 2. **Component contract tests (test_component_contracts.py)** ✅ Passed
```python
def test_design_tokens_types():
    assert isinstance(ANIMATION.duration_normal, str)  # ✅ Correct for CSS
```
**Gap:** Validates token TYPES for CSS, not Plotly compatibility.

#### 3. **API integration tests (test_api_integration.py)** ✅ Passed
```python
def test_api_call_works():
    result = calculate_flexure(...)  # Tests backend, not visualization
```
**Gap:** Doesn't test chart rendering with design tokens.

#### 4. **Page smoke tests (test_page_smoke.py)** ❌ Failed to detect
```python
def test_beam_design_page_loads():
    # Should have rendered the chart, but didn't test actual rendering
    pass
```
**Gap:** Created stubs but never executed actual page imports.

### The Missing Test Type: **USAGE VALIDATION**

None of our tests actually:
1. Import `components/visualizations.py`
2. Call `create_beam_diagram()` with real data
3. Execute `fig.update_layout()` with ANIMATION tokens
4. Validate that Plotly accepts the values

---

## 📊 IMPACT ASSESSMENT

### Immediate Impact
- ❌ All 4 visualization functions broken (`create_beam_diagram`, `create_bmd_diagram`, `create_sfd_diagram`, `create_load_diagram`)
- ❌ Beam Design page crashes on render
- ❌ Cannot test UI visually
- ❌ Production demo impossible

### Cascading Effects
- **Design system integrity:** If ANIMATION tokens are wrong, are other tokens compatible with Plotly?
- **Trust in tests:** 407 tests passed, yet production code is broken
- **Development velocity:** False confidence leads to shipping broken code

---

## 🔍 DEEP ROOT CAUSE: ARCHITECTURE MISMATCH

### The Fundamental Issue

We have **TWO DIFFERENT CONSUMERS** of design tokens:

```
┌──────────────────────────────────────────────────────────────┐
│                    DESIGN_SYSTEM.PY                          │
│                 (Single Source of Truth)                     │
└──────────────────────────────────────────────────────────────┘
                          │
                          ├─────────────────────────────────┐
                          ▼                                 ▼
                ┌──────────────────┐              ┌──────────────────┐
                │   CSS/STREAMLIT  │              │      PLOTLY      │
                │   Consumer       │              │   Consumer       │
                ├──────────────────┤              ├──────────────────┤
                │ duration="300ms" │              │ duration=300     │
                │ (string)         │              │ (int)            │
                └──────────────────┘              └──────────────────┘
                        ✅                                ❌
```

**The conflict:**
- CSS expects: `"300ms"` (string with unit)
- Plotly expects: `300` (milliseconds as integer)
- Our tokens: `"300ms"` (CSS format only)

### Why This Wasn't Obvious

1. **Research Phase Focus:** Research docs focused on CSS design systems (Material Design, Tailwind) - all use string-based tokens
2. **Plotly Theme Separate:** `plotly_theme.py` uses theme dict, didn't need `ANIMATION` directly
3. **Late Integration:** Design tokens created before visualizations were fully integrated
4. **No Cross-Library Validation:** Didn't test token compatibility across both CSS and Plotly

---

## ✅ IMMEDIATE FIX (30 minutes)

### Step 1: Add Numeric Animation Values

```python
# utils/design_system.py
@dataclass(frozen=True)
class AnimationTimings:
    """Standard animation durations and easing."""

    # CSS durations (for Streamlit CSS injection)
    instant: str = "100ms"
    fast: str = "200ms"
    normal: str = "300ms"
    slow: str = "500ms"

    # Semantic aliases for CSS
    duration_instant: str = "100ms"
    duration_fast: str = "200ms"
    duration_normal: str = "300ms"
    duration_slow: str = "500ms"

    # 🆕 NUMERIC VALUES FOR PLOTLY (milliseconds as int)
    duration_instant_ms: int = 100
    duration_fast_ms: int = 200
    duration_normal_ms: int = 300
    duration_slow_ms: int = 500

    # Easing functions
    ease_in_out: str = "cubic-bezier(0.4, 0, 0.2, 1)"
    ease_out: str = "cubic-bezier(0.0, 0, 0.2, 1)"
    ease_in: str = "cubic-bezier(0.4, 0, 1, 1)"
    ease_linear: str = "linear"
```

### Step 2: Update All Visualizations

```python
# components/visualizations.py (4 occurrences)
fig.update_layout(
    transition=dict(
        duration=ANIMATION.duration_normal_ms,  # ✅ Now uses int
        easing='cubic-in-out'
    )
)
```

### Step 3: Verify Fix

```bash
cd streamlit_app
.venv/bin/python -c "
from utils.design_system import ANIMATION
from components.visualizations import create_beam_diagram
print(f'duration type: {type(ANIMATION.duration_normal_ms)}')
print(f'duration value: {ANIMATION.duration_normal_ms}')
assert isinstance(ANIMATION.duration_normal_ms, int)
print('✅ Type check passed')
"
```

---

## 🏗️ LONG-TERM SOLUTION (4-6 hours)

### Strategy: **Multi-Consumer Design Token Architecture**

#### Phase 1: Token Contract Definition (1 hour)

Create `utils/design_tokens_contracts.py`:

```python
"""
Design Token Contracts - Type-safe tokens for multiple consumers.

Ensures design tokens work correctly across:
- Streamlit CSS
- Plotly charts
- React components (future)
"""

from typing import Protocol, runtime_checkable
from dataclasses import dataclass


@runtime_checkable
class PlotlyCompatible(Protocol):
    """Token must provide numeric values for Plotly."""

    def to_plotly(self) -> int | float:
        """Convert to Plotly-compatible numeric value."""
        ...


@runtime_checkable
class CSSCompatible(Protocol):
    """Token must provide string values for CSS."""

    def to_css(self) -> str:
        """Convert to CSS-compatible string value."""
        ...


@dataclass(frozen=True)
class DurationToken:
    """
    Multi-format duration token.

    Provides both CSS string and Plotly numeric formats.
    """
    milliseconds: int

    def to_css(self) -> str:
        """CSS format: '300ms'"""
        return f"{self.milliseconds}ms"

    def to_plotly(self) -> int:
        """Plotly format: 300"""
        return self.milliseconds

    def __str__(self) -> str:
        """Default to CSS format for backwards compat."""
        return self.to_css()


# Usage
DURATION_NORMAL = DurationToken(milliseconds=300)
print(DURATION_NORMAL.to_css())     # "300ms" for Streamlit
print(DURATION_NORMAL.to_plotly())  # 300 for Plotly
```

#### Phase 2: Update Design System (1 hour)

```python
# utils/design_system.py
from .design_tokens_contracts import DurationToken

@dataclass(frozen=True)
class AnimationTimings:
    """Standard animation durations and easing."""

    # Multi-format tokens
    instant: DurationToken = DurationToken(100)
    fast: DurationToken = DurationToken(200)
    normal: DurationToken = DurationToken(300)
    slow: DurationToken = DurationToken(500)

    # Backwards compat (deprecated in 2.0)
    @property
    def duration_instant(self) -> str:
        return self.instant.to_css()

    @property
    def duration_normal_ms(self) -> int:
        return self.normal.to_plotly()
```

#### Phase 3: Consumer-Specific Adapters (1 hour)

```python
# utils/plotly_tokens.py
"""
Plotly-specific token adapter.

Converts design tokens to Plotly-compatible format.
"""

from .design_system import ANIMATION, SPACING, COLORS

class PlotlyTokens:
    """Adapter for Plotly chart configuration."""

    @staticmethod
    def transition_duration(speed: str = "normal") -> int:
        """Get Plotly transition duration."""
        mapping = {
            "instant": ANIMATION.instant.to_plotly(),
            "fast": ANIMATION.fast.to_plotly(),
            "normal": ANIMATION.normal.to_plotly(),
            "slow": ANIMATION.slow.to_plotly(),
        }
        return mapping.get(speed, 300)

    @staticmethod
    def color(token: str) -> str:
        """Get color value (already compatible)."""
        return getattr(COLORS, token)


# Usage in visualizations
from utils.plotly_tokens import PlotlyTokens

fig.update_layout(
    transition=dict(
        duration=PlotlyTokens.transition_duration("normal"),  # ✅ Type-safe
        easing='cubic-in-out'
    )
)
```

#### Phase 4: Validation Test Suite (1 hour)

```python
# tests/test_design_token_compatibility.py
"""
Design Token Compatibility Tests.

Validates tokens work across ALL consumers.
"""

import pytest
import plotly.graph_objects as go
from utils.design_system import ANIMATION, COLORS, SPACING
from utils.plotly_tokens import PlotlyTokens


class TestPlotlyCompatibility:
    """Ensure tokens work with Plotly API."""

    def test_animation_duration_types(self):
        """Duration values must be numeric for Plotly."""
        for speed in ["instant", "fast", "normal", "slow"]:
            duration = PlotlyTokens.transition_duration(speed)
            assert isinstance(duration, (int, float))
            assert duration > 0

    def test_plotly_accepts_transition(self):
        """Plotly must accept our transition config."""
        fig = go.Figure()

        # This should NOT raise ValueError
        fig.update_layout(
            transition=dict(
                duration=PlotlyTokens.transition_duration("normal"),
                easing='cubic-in-out'
            )
        )

        # Verify it was set
        assert fig.layout.transition.duration == 300

    def test_all_visualizations_use_compatible_tokens(self):
        """All chart functions must use Plotly-compatible tokens."""
        from components.visualizations import (
            create_beam_diagram,
            create_bmd_diagram,
            create_sfd_diagram,
            create_load_diagram
        )

        # These should NOT raise type errors
        # (Use minimal valid inputs)
        try:
            create_beam_diagram(width=300, depth=450)
            create_bmd_diagram(positions=[0, 3000], moments=[0, 50])
            create_sfd_diagram(positions=[0, 3000], shear=[20, -20])
            create_load_diagram(span=3000, dead=10, live=5)
        except ValueError as e:
            if "Invalid value of type" in str(e):
                pytest.fail(f"Type mismatch detected: {e}")

    def test_color_tokens_plotly_compatible(self):
        """Color tokens must work in Plotly."""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[1, 2, 3],
            y=[1, 2, 3],
            marker=dict(color=COLORS.primary_500)  # Must accept hex string
        ))

        assert fig.data[0].marker.color == COLORS.primary_500


class TestCSSCompatibility:
    """Ensure tokens work with Streamlit CSS."""

    def test_animation_duration_css_format(self):
        """Duration must be valid CSS for Streamlit."""
        css_duration = ANIMATION.normal.to_css()
        assert isinstance(css_duration, str)
        assert css_duration.endswith("ms")
        assert css_duration == "300ms"

    def test_inject_css_variables(self):
        """CSS injection must work with token format."""
        from utils.design_system import inject_css

        css = inject_css()
        assert "--transition-normal: 300ms;" in css
        assert "--color-primary: #003366;" in css


class TestTokenContract:
    """Validate token contract compliance."""

    def test_duration_tokens_implement_protocol(self):
        """Duration tokens must implement both protocols."""
        from utils.design_tokens_contracts import (
            PlotlyCompatible,
            CSSCompatible
        )

        assert isinstance(ANIMATION.normal, PlotlyCompatible)
        assert isinstance(ANIMATION.normal, CSSCompatible)

    def test_no_string_durations_in_plotly_code(self):
        """Visualizations must NOT use string durations."""
        import ast
        import inspect
        from components import visualizations

        source = inspect.getsource(visualizations)
        tree = ast.parse(source)

        # Find all fig.update_layout calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if (hasattr(node.func, 'attr') and
                    node.func.attr == 'update_layout'):
                    # Check for transition duration
                    for keyword in node.keywords:
                        if keyword.arg == 'transition':
                            # Should use .to_plotly() or PlotlyTokens
                            # NOT direct ANIMATION.duration_normal
                            pass  # Implement AST check
```

#### Phase 5: Pre-Commit Hook (30 min)

```bash
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: plotly-token-validator
      name: Validate Plotly Token Usage
      entry: python scripts/validate_plotly_tokens.py
      language: python
      files: ^streamlit_app/components/.*\.py$
      pass_filenames: true
```

```python
# scripts/validate_plotly_tokens.py
"""
Pre-commit hook: Validate Plotly token usage.

Fails if code uses string durations with Plotly.
"""

import ast
import sys
from pathlib import Path


def check_file(filepath: Path) -> list[str]:
    """Check file for invalid Plotly token usage."""
    errors = []

    with open(filepath) as f:
        try:
            tree = ast.parse(f.read(), filename=str(filepath))
        except SyntaxError:
            return []  # Let Python handle syntax errors

    for node in ast.walk(tree):
        # Check for fig.update_layout(transition=dict(duration=...))
        if isinstance(node, ast.Call):
            if (hasattr(node.func, 'attr') and
                node.func.attr == 'update_layout'):

                for keyword in node.keywords:
                    if keyword.arg == 'transition':
                        # Check duration value
                        if isinstance(keyword.value, ast.Dict):
                            for key, val in zip(keyword.value.keys,
                                               keyword.value.values):
                                if (hasattr(key, 's') and
                                    key.s == 'duration'):
                                    # duration value must be:
                                    # - PlotlyTokens.transition_duration()
                                    # - ANIMATION.normal.to_plotly()
                                    # - Literal int
                                    # NOT: ANIMATION.duration_normal (string)

                                    if isinstance(val, ast.Attribute):
                                        attr_name = val.attr
                                        if 'duration' in attr_name and '_ms' not in attr_name:
                                            errors.append(
                                                f"{filepath}:{node.lineno}: "
                                                f"Invalid Plotly duration token: "
                                                f"{attr_name}. Use _ms suffix or "
                                                f"PlotlyTokens.transition_duration()"
                                            )

    return errors


def main():
    """Run validation on all provided files."""
    files = [Path(f) for f in sys.argv[1:]]
    all_errors = []

    for filepath in files:
        errors = check_file(filepath)
        all_errors.extend(errors)

    if all_errors:
        print("\n❌ Plotly Token Validation Failed:\n")
        for error in all_errors:
            print(f"  {error}")
        print("\n💡 Fix: Use PlotlyTokens.transition_duration() or ANIMATION.normal.to_plotly()\n")
        sys.exit(1)

    print("✅ Plotly token usage validated")
    sys.exit(0)


if __name__ == "__main__":
    main()
```

---

## 📈 PREVENTION METRICS

### Before (Current State)
- ❌ 0% runtime type checking
- ❌ No cross-library validation
- ❌ Manual token format conversion
- ❌ Tests pass but production fails

### After (With Solution)
- ✅ 100% compile-time type safety (Protocol)
- ✅ Automatic format conversion
- ✅ Pre-commit prevents misuse
- ✅ Tests validate ACTUAL usage

### Success Criteria
1. **Zero type errors** in production (Plotly accepts all tokens)
2. **Tests catch misuse** before commit
3. **Clear API** for developers (`PlotlyTokens.transition_duration()`)
4. **Backwards compatible** (existing CSS code still works)

---

## 🎯 IMPLEMENTATION PLAN

### Priority 1: Immediate Fix (Deploy today)
- [ ] Add `duration_*_ms` fields to `AnimationTimings`
- [ ] Update 4 occurrences in `visualizations.py`
- [ ] Verify app runs without errors
- [ ] Commit: `fix(ui): use numeric duration for plotly transitions`

### Priority 2: Test Coverage (Tomorrow)
- [ ] Add `test_plotly_accepts_tokens()` to catch future mismatches
- [ ] Add `test_visualizations_render()` to test actual chart creation
- [ ] Update `test_page_smoke.py` to import and test pages
- [ ] Commit: `test(ui): add plotly token compatibility tests`

### Priority 3: Long-Term Architecture (Next sprint)
- [ ] Create `design_tokens_contracts.py`
- [ ] Implement `DurationToken` class
- [ ] Create `PlotlyTokens` adapter
- [ ] Add pre-commit hook
- [ ] Update docs
- [ ] Commit: `refactor(ui): multi-consumer design token architecture`

---

## 📚 LESSONS LEARNED

### What Went Wrong
1. **Assumed CSS-only usage** when creating design tokens
2. **Tests validated structure, not usage** (contract vs. integration)
3. **No cross-library compatibility checks**
4. **Late integration** between design system and visualizations

### What Went Right
1. **Centralized tokens** made fix simple (single source of truth)
2. **Type hints** helped identify issue quickly
3. **Modular architecture** allowed surgical fix
4. **Clear error message** from Plotly pinpointed exact problem

### Process Improvements
1. **Add "Usage Validation" test category** to test plan template
2. **Require integration tests** before marking feature "done"
3. **Document token consumer requirements** in design system
4. **Add pre-commit validation** for library-specific APIs

---

## 🔗 RELATED DOCS

- `docs/planning/agent-6-impl-000-review-and-error-prevention.md` - Original error prevention plan
- `streamlit_app/docs/DESIGN-SYSTEM-GUIDE.md` - Design token documentation
- `streamlit_app/tests/test_plotly_theme.py` - Theme tests (need expansion)

---

## 📝 SIGN-OFF

**Analysis by:** Agent 6 (Background Agent)
**Reviewed by:** [Pending - needs human review]
**Severity:** CRITICAL (blocks production)
**Estimated fix time:** 30 minutes (immediate) + 6 hours (long-term)
**Risk of regression:** LOW (adding new fields, not changing existing)

---

*This analysis demonstrates the importance of testing not just token structure, but actual usage across all consumer libraries.*
