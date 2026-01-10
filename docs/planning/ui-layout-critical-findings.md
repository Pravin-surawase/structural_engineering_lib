# UI Layout Implementation - Critical Findings & Resolutions
**Date:** 2026-01-08
**Status:** ✅ ALL BLOCKERS RESOLVED - READY FOR IMPLEMENTATION

---

## Executive Summary

Pre-implementation review identified **5 critical issues** in the original plan that would cause failures. All issues addressed with explicit migration paths and updated code examples.

### Current System Status (Verified 2026-01-08)
```
✅ 651 Streamlit tests passing
✅ 36 token-specific tests passing
✅ Dual-token system working correctly
✅ No runtime errors in production
✅ All visualizations use correct tokens
```

### Key Decision: Preserve Current System
**The existing dual-token system works correctly. We are NOT replacing it.**

Current tokens that work:
- `ANIMATION.fast` → `"200ms"` (for CSS)
- `ANIMATION.duration_fast_ms` → `200` (for Plotly)

Future Duration class (OPTIONAL - for migration):
- `Duration(200).to_css()` → `"200ms"`
- `Duration(200).to_plotly()` → `200`
- `str(Duration(200))` → `"200ms"` (backwards compatible via `__str__`)

---

## Related Documents
- **Step-by-Step Guide:** [UI-IMPLEMENTATION-AGENT-GUIDE.md](UI-IMPLEMENTATION-AGENT-GUIDE.md)
- **Original Plan:** [UI-LAYOUT-FINAL-DECISION.md](UI-LAYOUT-FINAL-DECISION.md)
- **Research:** [ui-layout-best-practices.md](../research/ui-layout-best-practices.md)
- **Data Model:** [data-model-compatibility-checklist.md](data-model-compatibility-checklist.md)

---

## Alignment Update (2026-01-08)

This plan now aligns with the **Option 5 baseline + Power View toggle** decision and the
visual-first direction (professional, interactive, and clearly “smart tech” at first glance).

### Visual Experience Requirements (Non-negotiable)
- **Option 5 default:** Sidebar inputs + results tabs (inputs always visible).
- **Power View toggle:** Option 6 three-panel layout enabled on wide screens only.
- **Professional visuals:** No default Plotly styling; all charts use design tokens.
- **Engineering context:** Units, limits, and clause references visible by default.
- **Interactive feel:** Live preview, hover details, click-to-edit hooks.
- **3D readiness:** 3D view is optional, performance-gated, and backed by 2D.
- Compatibility checklist: `docs/planning/data-model-compatibility-checklist.md`

### Innovative UI Signature (First-Glance Cues)
These elements make the UI read as professional + smart tech in the first 3 seconds.

**1) Engineering Credibility Banner**
- Title line: "IS 456 Beam Design" + version + active code clause badge.
- Status chip: "SAFE / REVIEW / FAIL" with explicit utilization percent.
- One-line context: units (mm, kN, kN·m) shown on the header.

**2) Smart Insight Capsule**
- Compact card that surfaces the top 1-2 risks or optimizations.
- Must include "why" and "what to change" (not just warnings).
- Example: "Shear near limit (Vu/Vc = 0.96). Try 8mm @ 150."

**3) Traceability Ribbon**
- Inline clause references with hover detail (e.g., "Cl. 26.5.1.1").
- A "View Calculation Steps" link that expands a small audit trail.

**4) Professional Visual Tone**
- Subtle grid, muted palette, monospace numeric labels.
- Units and limit lines are always visible (no hidden context).
- No bright default colors; use IS 456 tokens only.

**5) Interactive Preview Hooks**
- Slider + live preview (instant feedback).
- Click-to-edit marker on the diagram (shows editable nodes).
- Power View toggle appears only on wide screens.

### Visual Roadmap (2D → 2.5D → 3D)
1. **Phase A (2D, Week 1-2):** Cross-section, BMD/SFD, detailing diagrams with
   units, limits, and clause tags.
2. **Phase B (2.5D, Week 2-3):** Extruded section + rebar cage in pseudo-3D,
   hoverable callouts, and comparison sliders.
3. **Phase C (3D, Week 3+):** Full 3D toggle (Plotly 3D or equivalent),
   gated by screen width and device performance.

---

## Critical Findings

### 🔴 HIGH: Token String Coercion Breaking Change

**Problem:**
```python
# Current code (EVERYWHERE):
st.markdown(f"""
<style>
    .element {{
        transition: all {ANIMATION.fast};  # Expects string "200ms"
    }}
</style>
""")

# Proposed DurationToken:
fast: Duration = Duration(200)  # Object, not string!
# Would fail: TypeError: unsupported format string
```

**Impact:** Breaks ALL existing CSS template usage (50+ occurrences)

**Root Cause:** Plan proposed token objects without string coercion path

**Resolution:** Make tokens string-coercible with `__str__()` method

```python
@dataclass(frozen=True)
class Duration:
    """Duration token with automatic CSS string coercion."""

    milliseconds: int

    def to_css(self) -> str:
        """Explicit CSS format."""
        return f"{self.milliseconds}ms"

    def to_plotly(self) -> int:
        """Explicit Plotly format."""
        return self.milliseconds

    def to_seconds(self) -> float:
        """Explicit seconds format."""
        return self.milliseconds / 1000.0

    def __str__(self) -> str:
        """
        Implicit string coercion for backwards compatibility.

        CRITICAL: Enables existing CSS templates to work without changes:
        - f"{ANIMATION.fast}" → "200ms"
        - Gradual migration to explicit .to_css() calls
        """
        return self.to_css()

    def __repr__(self) -> str:
        """Debug representation."""
        return f"Duration({self.milliseconds}ms)"
```

**Migration Strategy:**

**Phase 1 (Backwards Compatible):**
```python
# Old code CONTINUES to work:
st.markdown(f"<style>.el {{ transition: {ANIMATION.fast}; }}</style>")
# → "transition: 200ms;"  ✅ Works via __str__()

# New code can be explicit:
fig.update_layout(transition=dict(duration=ANIMATION.fast.to_plotly()))
# → duration: 200  ✅ Type-safe
```

**Phase 2 (Gradual Explicit Migration - Optional):**
```python
# Update CSS templates incrementally:
st.markdown(f"<style>.el {{ transition: {ANIMATION.fast.to_css()}; }}</style>")
# → More explicit, but not required
```

**Phase 3 (Deprecation - Future):**
```python
# Mark __str__() as deprecated (v2.0.0):
def __str__(self) -> str:
    warnings.warn(
        "Implicit string coercion deprecated. Use .to_css() explicitly.",
        DeprecationWarning
    )
    return self.to_css()
```

**Decision:** ✅ **Use `__str__()` for backwards compatibility**

---

### 🟡 MEDIUM: Missing @runtime_checkable Decorator

**Problem:**
```python
class DurationToken(Protocol):
    def to_css(self) -> str: ...
    def to_plotly(self) -> int: ...

# Test code:
def test_token_validation():
    token = Duration(300)
    assert isinstance(token, DurationToken)  # ❌ TypeError!
```

**Impact:** All Protocol validation tests fail at runtime

**Root Cause:** Protocols are structural typing only (static analysis)

**Resolution:** Add `@runtime_checkable` decorator

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class DurationToken(Protocol):
    """
    Protocol for duration tokens.

    @runtime_checkable enables isinstance() checks at runtime.
    Without it, Protocol is static-only (mypy/pyright).
    """

    def to_css(self) -> str:
        """Format for CSS (e.g., "300ms")."""
        ...

    def to_plotly(self) -> int:
        """Format for Plotly (e.g., 300)."""
        ...

    def to_seconds(self) -> float:
        """Format as seconds (e.g., 0.3)."""
        ...


# Now tests work:
def test_duration_is_duration_token():
    token = Duration(300)
    assert isinstance(token, DurationToken)  # ✅ Works!

def test_invalid_token_rejected():
    invalid = "300ms"  # Plain string
    assert not isinstance(invalid, DurationToken)  # ✅ Correctly rejected
```

**Decision:** ✅ **All Protocols must use `@runtime_checkable`**

---

### 🟡 MEDIUM: Test Function Signature Mismatch

**Problem:**
```python
# Proposed test:
fig = create_beam_diagram(width=300, depth=450)  # ❌ Wrong signature!

# Actual function (visualizations.py line 91):
def create_beam_diagram(
    b_mm: float,
    D_mm: float,
    d_mm: float,
    rebar_positions: List[Tuple[float, float]],
    xu: float,
    bar_dia: int,
    spacing: Optional[int] = None
) -> go.Figure:
```

**Impact:** All proposed integration tests fail immediately

**Root Cause:** Plan used simplified examples without checking actual signatures

**Resolution:** Match actual function signatures in tests

```python
# CORRECT test example:
def test_beam_diagram_uses_plotly_tokens():
    """Verify beam diagram uses Plotly-compatible animation tokens."""
    from components.visualizations import create_beam_diagram

    # Use actual function signature
    fig = create_beam_diagram(
        b_mm=300.0,
        D_mm=500.0,
        d_mm=450.0,
        rebar_positions=[(50, 450), (150, 450), (250, 450)],  # 3 bars
        xu=150.0,
        bar_dia=20,
        spacing=None
    )

    # Verify uses integer duration (Plotly-compatible)
    assert isinstance(fig.layout.transition.duration, int)
    assert fig.layout.transition.duration == ANIMATION.duration_normal_ms

    # Verify figure is valid
    assert len(fig.data) > 0 or len(fig.layout.shapes) > 0


def test_create_beam_preview_diagram():
    """Test simplified preview diagram (NEW function, correct signature)."""
    from components.preview import create_beam_preview_diagram

    # This is the NEW function we're creating (simpler signature)
    fig = create_beam_preview_diagram(
        span_mm=5000.0,
        b_mm=300.0,
        D_mm=500.0,
        support_condition="Simply Supported"
    )

    # Verify Plotly token usage
    assert fig.layout.transition.duration == ANIMATION.duration_normal_ms
```

**Decision:** ✅ **Always verify actual signatures before writing tests**

---

### 🟢 LOW: Silent Fallback Hides Typos

**Problem:**
```python
class PlotlyTokens:
    @staticmethod
    def transition_duration(speed: str = "normal") -> int:
        durations = {
            "instant": 100,
            "fast": 200,
            "normal": 300,
            "slow": 500
        }
        return durations.get(speed, 300)  # ❌ Silent fallback!

# Usage:
duration = PlotlyTokens.transition_duration("normmal")  # Typo!
# → Returns 300 (default)
# → Bug hidden, no error raised
```

**Impact:** Typos silently ignored, weakens type-safety goal

**Root Cause:** dict.get() with default fallback

**Resolution Option 1:** Use Literal type (strict, preferred)

```python
from typing import Literal

class PlotlyTokens:
    @staticmethod
    def transition_duration(
        speed: Literal["instant", "fast", "normal", "slow"] = "normal"
    ) -> int:
        """
        Get Plotly transition duration.

        Args:
            speed: Animation speed (mypy enforces valid values)

        Returns:
            Duration in milliseconds
        """
        durations = {
            "instant": 100,
            "fast": 200,
            "normal": 300,
            "slow": 500
        }
        # No fallback - mypy catches typos at static analysis
        return durations[speed]

# Usage:
duration = PlotlyTokens.transition_duration("normmal")
# → mypy error: Argument 1 has incompatible type "Literal['normmal']"
# → Caught before runtime! ✅
```

**Resolution Option 2:** Raise on invalid (runtime safety)

```python
class PlotlyTokens:
    @staticmethod
    def transition_duration(speed: str = "normal") -> int:
        """
        Get Plotly transition duration.

        Args:
            speed: Animation speed ("instant", "fast", "normal", "slow")

        Returns:
            Duration in milliseconds

        Raises:
            ValueError: If speed is not recognized
        """
        durations = {
            "instant": 100,
            "fast": 200,
            "normal": 300,
            "slow": 500
        }

        if speed not in durations:
            valid = ", ".join(durations.keys())
            raise ValueError(
                f"Invalid speed: {speed!r}. "
                f"Valid options: {valid}"
            )

        return durations[speed]

# Usage:
duration = PlotlyTokens.transition_duration("normmal")
# → ValueError: Invalid speed: 'normmal'. Valid options: instant, fast, normal, slow
# → Caught at runtime! ✅
```

**Decision:** ✅ **Use Literal type (Option 1) for static safety + runtime ValueError**

```python
def transition_duration(
    speed: Literal["instant", "fast", "normal", "slow"] = "normal"
) -> int:
    durations = {
        "instant": 100,
        "fast": 200,
        "normal": 300,
        "slow": 500
    }

    # Belt-and-suspenders: Literal catches at static, ValueError at runtime
    if speed not in durations:
        raise ValueError(f"Invalid speed: {speed!r}")

    return durations[speed]
```

---

### 🟢 LOW: Incomplete Pre-Commit Validation

**Problem:**
```python
# Current pre-commit script only checks:
fig.update_layout(transition=dict(duration=ANIMATION.duration_normal))

# But misses:
fig.layout.transition.duration = ANIMATION.duration_normal  # Direct assignment
go.Layout(transition=dict(duration=ANIMATION.duration_normal))  # Constructor
frames[0].layout.transition.duration = ANIMATION.duration_normal  # Frames
```

**Impact:** Partial validation coverage, some type mismatches slip through

**Root Cause:** AST walker only looks for `update_layout` method calls

**Resolution:** Expand AST patterns

```python
def check_file(filepath: Path) -> list[str]:
    """Check file for improper Plotly token usage."""
    with open(filepath) as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return []

    errors = []

    for node in ast.walk(tree):
        # Pattern 1: fig.update_layout(transition=dict(duration=...))
        if isinstance(node, ast.Call):
            if hasattr(node.func, 'attr') and node.func.attr == 'update_layout':
                errors.extend(_check_transition_duration(node, filepath))

        # Pattern 2: fig.layout.transition.duration = ...
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if _is_transition_duration_attr(target):
                    if _uses_wrong_token(node.value):
                        errors.append(
                            f"{filepath}:{node.lineno}: "
                            f"Direct assignment to transition.duration must use _ms token"
                        )

        # Pattern 3: go.Layout(transition=dict(duration=...))
        if isinstance(node, ast.Call):
            if _is_plotly_layout_constructor(node):
                errors.extend(_check_transition_duration(node, filepath))

        # Pattern 4: Frame transitions
        if isinstance(node, ast.Call):
            if _is_frame_constructor(node):
                errors.extend(_check_transition_duration(node, filepath))

    return errors

def _is_transition_duration_attr(node: ast.AST) -> bool:
    """Check if node is fig.layout.transition.duration."""
    if not isinstance(node, ast.Attribute):
        return False
    if node.attr != 'duration':
        return False
    if not isinstance(node.value, ast.Attribute):
        return False
    if node.value.attr != 'transition':
        return False
    return True

def _uses_wrong_token(node: ast.AST) -> bool:
    """Check if node uses string token where integer expected."""
    if isinstance(node, ast.Attribute):
        attr_name = node.attr
        # duration_normal (string) is wrong, duration_normal_ms (int) is correct
        return 'duration' in attr_name and '_ms' not in attr_name
    return False

def _is_plotly_layout_constructor(node: ast.Call) -> bool:
    """Check if node is go.Layout(...)."""
    if not isinstance(node.func, ast.Attribute):
        return False
    return node.func.attr == 'Layout'

def _is_frame_constructor(node: ast.Call) -> bool:
    """Check if node is go.Frame(...)."""
    if not isinstance(node.func, ast.Attribute):
        return False
    return node.func.attr == 'Frame'
```

**Decision:** ✅ **Expand validation to cover all Plotly transition patterns**

---

## Open Questions - Resolved

### Question 1: String Coercion vs Explicit Migration?

**Question:**
> Do you want DurationToken to be string‑coercible (`__str__` → CSS) to avoid a large refactor in CSS templates and tests, or do you prefer an explicit `.to_css()` migration across all call sites?

**Answer:** ✅ **String-coercible with gradual migration path**

**Rationale:**
1. **Backwards compatibility is critical** - 50+ CSS usage sites
2. **Gradual migration is safer** - no big-bang refactor
3. **Explicit is optional** - teams can migrate at their pace
4. **Deprecation path is clear** - can remove `__str__()` in v2.0.0

**Implementation:**
- ✅ Add `__str__()` method to all token classes
- ✅ Make it return `.to_css()` for now
- ✅ Add deprecation warning in future major version
- ✅ Document both patterns in usage guide

**Example:**
```python
# Both work:
st.markdown(f"<style>.el {{ transition: {ANIMATION.fast}; }}</style>")  # Implicit
st.markdown(f"<style>.el {{ transition: {ANIMATION.fast.to_css()}; }}</style>")  # Explicit

# New code should prefer explicit:
fig.update_layout(transition=dict(duration=ANIMATION.fast.to_plotly()))  # Clear intent
```

---

### Question 2: Expand Adapter Pattern Now or Later?

**Question:**
> Should the adapter pattern be expanded beyond durations (e.g., spacing, typography, color) for future DXF/PDF consumers now, or staged later?

**Answer:** ✅ **Expand NOW for Duration + Color, stage Spacing/Typography for later**

**Rationale:**
1. **Duration + Color are needed immediately** - Plotly uses both
2. **Spacing/Typography can wait** - DXF/PDF export is Phase 3+ (weeks away)
3. **Establish pattern now** - easier to replicate later
4. **Cost is low** - 2 hours to do Duration + Color properly

**Implementation Plan:**

**Phase 1 (This Week - Duration + Color):**
```python
@runtime_checkable
class DurationToken(Protocol):
    def to_css(self) -> str: ...
    def to_plotly(self) -> int: ...
    def to_seconds(self) -> float: ...

@runtime_checkable
class ColorToken(Protocol):
    def to_css(self) -> str: ...
    def to_plotly(self) -> str: ...
    def to_rgb(self) -> tuple[int, int, int]: ...
    def to_rgba(self, alpha: float = 1.0) -> str: ...

# Implementations:
class Duration: ...  # Full implementation
class Color: ...     # Full implementation
```

**Phase 2 (Next Sprint - Spacing + Typography):**
```python
@runtime_checkable
class SpacingToken(Protocol):
    def to_css(self) -> str: ...
    def to_pixels(self) -> int: ...
    def to_rem(self) -> float: ...
    def to_dxf_units(self) -> float: ...  # For AutoCAD

@runtime_checkable
class TypographyToken(Protocol):
    def to_css(self) -> str: ...
    def to_points(self) -> float: ...
    def to_dxf_height(self) -> float: ...  # For AutoCAD text
```

**Why Duration + Color Together:**
- Plotly charts use BOTH (colors for traces, duration for transitions)
- Pattern is proven by doing 2 implementations
- Tests validate Protocol system works
- Future tokens just copy the pattern

---

## Updated Implementation Timeline

### Week 1 (Current): Token Architecture Foundation

**Day 1-2: Duration + Color Tokens (4 hours)**
- [ ] Create `design_tokens_contracts.py`
- [ ] Implement `Duration` class with `__str__()`
- [ ] Implement `Color` class with `__str__()`
- [ ] Add `@runtime_checkable` to protocols
- [ ] Write unit tests (20 tests)
- [ ] Update existing ANIMATION + COLORS to use new classes

**Day 3: Pre-Commit Validation (2 hours)**
- [ ] Expand `check_plotly_tokens.py` to cover all patterns
- [ ] Add tests for pre-commit script
- [ ] Integrate with `.pre-commit-config.yaml`
- [ ] Verify catches all type mismatches

**Day 4-5: UI Layout Implementation (6 hours)**
- [ ] Implement Option 5 layout (sidebar + results tabs)
- [ ] Add Power View toggle stub (Option 6) for wide screens
- [ ] Use new token classes in preview components
- [ ] Test both implicit and explicit token usage
- [ ] Document token usage patterns

### Week 2: Expand + Polish

**Day 1-2: Spacing + Typography (Future)**
- Staged for later when DXF/PDF export begins

---

## Updated Code Examples

### Duration Token (Complete)

```python
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

@runtime_checkable
class DurationToken(Protocol):
    """Protocol for duration tokens supporting multiple consumers."""

    def to_css(self) -> str:
        """Format for CSS (e.g., "300ms")."""
        ...

    def to_plotly(self) -> int:
        """Format for Plotly (e.g., 300)."""
        ...

    def to_seconds(self) -> float:
        """Format as seconds (e.g., 0.3)."""
        ...


@dataclass(frozen=True)
class Duration:
    """
    Duration token with multi-format support.

    Examples:
        >>> normal = Duration(300)
        >>> str(normal)  # Implicit CSS
        "300ms"
        >>> normal.to_css()  # Explicit CSS
        "300ms"
        >>> normal.to_plotly()  # Plotly integer
        300
        >>> normal.to_seconds()  # Seconds float
        0.3
    """

    milliseconds: int

    def to_css(self) -> str:
        """CSS format: "300ms"."""
        return f"{self.milliseconds}ms"

    def to_plotly(self) -> int:
        """Plotly format: 300."""
        return self.milliseconds

    def to_seconds(self) -> float:
        """Seconds format: 0.3."""
        return self.milliseconds / 1000.0

    def __str__(self) -> str:
        """
        Implicit string coercion for backwards compatibility.

        Enables existing code to work without changes:
            f"transition: {ANIMATION.fast}"  → "transition: 200ms"

        Future: May deprecate in favor of explicit .to_css()
        """
        return self.to_css()

    def __repr__(self) -> str:
        """Debug representation."""
        return f"Duration({self.milliseconds}ms)"


# Usage in AnimationTimings:
@dataclass(frozen=True)
class AnimationTimings:
    """Animation timing tokens with automatic format conversion."""

    # Token objects (single source of truth)
    instant: Duration = Duration(100)
    fast: Duration = Duration(200)
    normal: Duration = Duration(300)
    slow: Duration = Duration(500)

    # Semantic aliases (return token objects)
    @property
    def duration_instant(self) -> Duration:
        """Alias for instant (backwards compat)."""
        return self.instant

    @property
    def duration_fast(self) -> Duration:
        """Alias for fast (backwards compat)."""
        return self.fast

    @property
    def duration_normal(self) -> Duration:
        """Alias for normal (backwards compat)."""
        return self.normal

    @property
    def duration_slow(self) -> Duration:
        """Alias for slow (backwards compat)."""
        return self.slow

    # OLD _ms tokens (keep for backwards compat, mark deprecated)
    @property
    def duration_instant_ms(self) -> int:
        """DEPRECATED: Use instant.to_plotly() instead."""
        return self.instant.to_plotly()

    @property
    def duration_fast_ms(self) -> int:
        """DEPRECATED: Use fast.to_plotly() instead."""
        return self.fast.to_plotly()

    @property
    def duration_normal_ms(self) -> int:
        """DEPRECATED: Use normal.to_plotly() instead."""
        return self.normal.to_plotly()

    @property
    def duration_slow_ms(self) -> int:
        """DEPRECATED: Use slow.to_plotly() instead."""
        return self.slow.to_plotly()
```

### Color Token (Complete)

```python
@runtime_checkable
class ColorToken(Protocol):
    """Protocol for color tokens supporting multiple consumers."""

    def to_css(self) -> str:
        """Format for CSS (e.g., "#003366")."""
        ...

    def to_plotly(self) -> str:
        """Format for Plotly (e.g., "#003366")."""
        ...

    def to_rgb(self) -> tuple[int, int, int]:
        """Format as RGB tuple (e.g., (0, 51, 102))."""
        ...

    def to_rgba(self, alpha: float = 1.0) -> str:
        """Format as RGBA (e.g., "rgba(0,51,102,1.0)")."""
        ...


@dataclass(frozen=True)
class Color:
    """
    Color token with multi-format support.

    Examples:
        >>> primary = Color("#003366")
        >>> str(primary)  # Implicit CSS
        "#003366"
        >>> primary.to_css()  # Explicit CSS
        "#003366"
        >>> primary.to_plotly()  # Plotly string
        "#003366"
        >>> primary.to_rgb()  # RGB tuple
        (0, 51, 102)
        >>> primary.to_rgba(0.5)  # RGBA string
        "rgba(0,51,102,0.5)"
    """

    hex_value: str

    def __post_init__(self):
        """Validate hex color format."""
        if not self.hex_value.startswith('#'):
            raise ValueError(f"Hex color must start with #: {self.hex_value}")
        if len(self.hex_value) != 7:
            raise ValueError(f"Hex color must be 7 chars (#RRGGBB): {self.hex_value}")

    def to_css(self) -> str:
        """CSS format: "#003366"."""
        return self.hex_value

    def to_plotly(self) -> str:
        """Plotly format: "#003366" (same as CSS)."""
        return self.hex_value

    def to_rgb(self) -> tuple[int, int, int]:
        """RGB tuple: (0, 51, 102)."""
        hex_clean = self.hex_value.lstrip('#')
        return tuple(int(hex_clean[i:i+2], 16) for i in (0, 2, 4))

    def to_rgba(self, alpha: float = 1.0) -> str:
        """RGBA string: "rgba(0,51,102,1.0)"."""
        r, g, b = self.to_rgb()
        return f"rgba({r},{g},{b},{alpha})"

    def __str__(self) -> str:
        """Implicit string coercion for backwards compatibility."""
        return self.to_css()

    def __repr__(self) -> str:
        """Debug representation."""
        return f"Color({self.hex_value})"


# Usage in ColorPalette:
@dataclass(frozen=True)
class ColorPalette:
    """Color palette with automatic format conversion."""

    # Primary colors (token objects)
    primary_500: Color = Color("#003366")
    primary_600: Color = Color("#002952")

    # Accent colors
    accent_500: Color = Color("#FF6600")
    accent_600: Color = Color("#CC5200")

    # Semantic colors
    success: Color = Color("#10B981")
    warning: Color = Color("#F59E0B")
    error: Color = Color("#EF4444")
    info: Color = Color("#3B82F6")
```

### PlotlyTokens with Literal (Complete)

```python
from typing import Literal

class PlotlyTokens:
    """Convenience adapters for Plotly-specific token operations."""

    @staticmethod
    def transition_duration(
        speed: Literal["instant", "fast", "normal", "slow"] = "normal"
    ) -> int:
        """
        Get Plotly transition duration.

        Args:
            speed: Animation speed (mypy enforces valid values)

        Returns:
            Duration in milliseconds

        Raises:
            ValueError: If speed is invalid (runtime safety)

        Examples:
            >>> PlotlyTokens.transition_duration("fast")
            200
            >>> PlotlyTokens.transition_duration("normmal")  # Typo
            mypy error: Argument 1 has incompatible type
        """
        durations = {
            "instant": 100,
            "fast": 200,
            "normal": 300,
            "slow": 500
        }

        # Belt-and-suspenders: Literal for static, ValueError for runtime
        if speed not in durations:
            valid = ", ".join(durations.keys())
            raise ValueError(
                f"Invalid speed: {speed!r}. Valid options: {valid}"
            )

        return durations[speed]

    @staticmethod
    def transition(
        duration: Duration,
        easing: str = 'cubic-in-out'
    ) -> dict:
        """
        Create Plotly transition dict from duration token.

        Args:
            duration: Duration token
            easing: CSS easing function

        Returns:
            Plotly transition dict

        Examples:
            >>> PlotlyTokens.transition(ANIMATION.fast)
            {'duration': 200, 'easing': 'cubic-in-out'}
        """
        return {
            'duration': duration.to_plotly(),
            'easing': easing
        }
```

### Updated Pre-Commit Script (Complete)

```python
#!/usr/bin/env python3
"""
Validate Plotly token usage in Streamlit components.

Checks all patterns:
- fig.update_layout(transition=dict(duration=...))
- fig.layout.transition.duration = ...
- go.Layout(transition=dict(duration=...))
- go.Frame(transition=dict(duration=...))

Ensures tokens use .to_plotly() or _ms suffix for integer values.
"""
import ast
import sys
from pathlib import Path
from typing import List

def check_file(filepath: Path) -> List[str]:
    """Check file for improper Plotly token usage."""
    with open(filepath) as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return []

    errors = []

    for node in ast.walk(tree):
        # Pattern 1: Method calls (update_layout, etc.)
        if isinstance(node, ast.Call):
            if hasattr(node.func, 'attr'):
                if node.func.attr in ('update_layout', 'Layout', 'Frame'):
                    errors.extend(_check_transition_keyword(node, filepath))

        # Pattern 2: Direct attribute assignment
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if _is_transition_duration_attr(target):
                    if _uses_wrong_token(node.value):
                        errors.append(
                            f"{filepath}:{node.lineno}: "
                            f"Direct assignment to transition.duration must use "
                            f".to_plotly() or _ms token"
                        )

    return errors


def _check_transition_keyword(node: ast.Call, filepath: Path) -> List[str]:
    """Check transition keyword argument in call."""
    errors = []

    for keyword in node.keywords:
        if keyword.arg == 'transition':
            if isinstance(keyword.value, ast.Dict):
                for key, val in zip(keyword.value.keys, keyword.value.values):
                    if (hasattr(key, 's') and key.s == 'duration') or \
                       (hasattr(key, 'value') and key.value == 'duration'):
                        if _uses_wrong_token(val):
                            errors.append(
                                f"{filepath}:{node.lineno}: "
                                f"Plotly duration must use .to_plotly() or _ms token. "
                                f"Found: {ast.unparse(val)}"
                            )

    return errors


def _is_transition_duration_attr(node: ast.AST) -> bool:
    """Check if node is *.transition.duration attribute."""
    if not isinstance(node, ast.Attribute):
        return False
    if node.attr != 'duration':
        return False
    if isinstance(node.value, ast.Attribute):
        if node.value.attr == 'transition':
            return True
    return False


def _uses_wrong_token(node: ast.AST) -> bool:
    """
    Check if node uses string token where integer expected.

    Wrong: ANIMATION.duration_normal (string)
    Right: ANIMATION.duration_normal_ms (int)
    Right: ANIMATION.normal.to_plotly() (int)
    """
    if isinstance(node, ast.Attribute):
        attr_name = node.attr
        # Has "duration" but not "_ms" or "to_plotly" → likely string
        if 'duration' in attr_name:
            if '_ms' not in attr_name and 'to_plotly' not in attr_name:
                return True
    return False


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
        print("\n💡 Fix: Use .to_plotly() or _ms suffix for Plotly tokens\n")
        print("Examples:")
        print("  ✅ ANIMATION.normal.to_plotly()")
        print("  ✅ ANIMATION.duration_normal_ms")
        print("  ❌ ANIMATION.duration_normal (string, breaks Plotly)")
        print()
        sys.exit(1)

    print("✅ Plotly token usage validated")
    sys.exit(0)


if __name__ == "__main__":
    main()
```

---

## Updated Success Criteria

### Phase 1 (Token Architecture) - DEFERRED (Optional)

**Status:** Current dual-token system works. Future Duration/Color classes are optional.

If implementing Duration class, these must pass:
- [ ] `Duration` class with `__str__()` implemented
- [ ] `Color` class with `__str__()` implemented
- [ ] All Protocols have `@runtime_checkable`
- [ ] 20+ unit tests passing
- [ ] Backwards compatibility verified (existing CSS works)
- [ ] Existing tests like `assert ANIMATION.fast == "200ms"` still pass

**Note:** If Duration class is added, these tests need updates:
```python
# test_design_system_integration.py:154-157 will need:
# OLD: assert ANIMATION.fast == "200ms"
# NEW: assert str(ANIMATION.fast) == "200ms"

# test_design_system_integration.py:280 will need:
# OLD: assert ANIMATION.fast.endswith("ms")
# NEW: assert str(ANIMATION.fast).endswith("ms")
```

### Phase 2 (UI Layout) - PRIORITY - Complete When:

- [ ] Two-column layout working (col_input, col_preview)
- [ ] Real-time preview component created (`components/preview.py`)
- [ ] All 651 existing tests pass
- [ ] New preview tests pass (30+ tests)
- [ ] No regression in existing functionality
- [ ] Manual testing confirms layout renders correctly

### Test Verification Commands

```bash
# Run all tests
cd streamlit_app && ../.venv/bin/python -m pytest tests/ -v --tb=short

# Run token-specific tests
../.venv/bin/python -m pytest tests/test_design_token_contracts.py tests/test_plotly_token_usage.py -v

# Run preview tests (after creating)
../.venv/bin/python -m pytest tests/test_preview.py -v

# Check import works
../.venv/bin/python -c "from components.preview import render_real_time_preview; print('OK')"
```

---

## Summary of Changes from Original Plan

| Issue | Original Plan | Updated Plan |
|-------|---------------|--------------|
| **String coercion** | No `__str__()` → breaks CSS | ✅ Add `__str__()` for backwards compat |
| **Protocol runtime** | Plain Protocol → isinstance fails | ✅ Add `@runtime_checkable` decorator |
| **Test signatures** | Wrong function args → tests fail | ✅ Match actual function signatures |
| **Silent fallback** | dict.get(default) → hides typos | ✅ Use Literal + ValueError |
| **Pre-commit coverage** | Only update_layout → partial | ✅ Check all Plotly patterns |
| **Token scope** | Expand all now? | ✅ Duration + Color now, rest later |
| **Layout alignment** | Two-column baseline | ✅ Option 5 baseline + Power View |

---

## Sign-Off

**Findings reviewed by:** Main Agent
**Resolutions approved by:** TBD
**Status:** ✅ **READY FOR IMPLEMENTATION** (with fixes)

**All blockers resolved. Safe to proceed.**

---

*This document ensures the implementation plan accounts for real-world usage patterns and prevents the issues that would have caused failures.*
