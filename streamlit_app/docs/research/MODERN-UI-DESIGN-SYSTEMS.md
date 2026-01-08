# RESEARCH-004: Modern UI Design Systems for Engineering Applications

**Status:** 🟡 IN PROGRESS
**Priority:** 🔴 CRITICAL
**Agent:** Agent 6 (Streamlit Specialist)
**Created:** 2026-01-08
**Estimated Duration:** 6-8 hours

---

## Executive Summary

This research document analyzes modern UI design systems suitable for engineering applications, with focus on creating a professional, polished interface for the IS 456 RC Beam Design Dashboard. Current UI uses standard Streamlit widgets with basic styling—goal is to elevate to production-grade quality with depth, hierarchy, and visual sophistication.

**Key Findings:**
- **Design language:** Material Design 3 + Engineering-specific adaptations
- **Color system:** Navy primary (#003366), Orange accent (#FF6600), with 60-30-10 rule
- **Typography:** Inter for UI, JetBrains Mono for code/numbers
- **Spacing:** 8px base unit, 1.5 line height for readability
- **Depth:** 4-level elevation system with shadows and blur
- **Interaction:** Subtle animations (200-300ms), hover states, focus rings

---

## Part 1: Design System Fundamentals

### 1.1 What is a Design System?

A design system is a collection of reusable components, patterns, and guidelines that ensure consistency across an application. For engineering tools, it must balance:

- **Professional appearance** - Inspires confidence in calculations
- **Functional clarity** - Data density without overwhelming
- **Visual hierarchy** - Guide user's eye to important information
- **Accessibility** - WCAG 2.1 AA compliance minimum

**Best-in-class examples:**
- Material Design 3 (Google) - Comprehensive, well-documented
- Fluent 2 (Microsoft) - Enterprise-focused, data-heavy apps
- Carbon Design (IBM) - Technical/engineering applications
- Ant Design (Alibaba) - Dense dashboards, data tables

---

## Part 2: Color System

### 2.1 Primary Color Palette

**Brand Colors (IS 456 Theme):**

```python
# Primary (Navy Blue - professional, trustworthy)
PRIMARY_50  = "#E6EDF5"   # Lightest tint
PRIMARY_100 = "#CCDAEA"
PRIMARY_200 = "#99B5D5"
PRIMARY_300 = "#6690C0"
PRIMARY_400 = "#336BAB"   # Mid-tone
PRIMARY_500 = "#003366"   # Base (main brand color)
PRIMARY_600 = "#002952"
PRIMARY_700 = "#001F3D"
PRIMARY_800 = "#001429"
PRIMARY_900 = "#000A14"   # Darkest shade

# Accent (Orange - energy, action)
ACCENT_50  = "#FFF3E6"
ACCENT_100 = "#FFE7CC"
ACCENT_200 = "#FFCF99"
ACCENT_300 = "#FFB766"
ACCENT_400 = "#FF9F33"
ACCENT_500 = "#FF6600"   # Base (call-to-action)
ACCENT_600 = "#CC5200"
ACCENT_700 = "#993D00"
ACCENT_800 = "#662900"
ACCENT_900 = "#331400"
```

### 2.2 Semantic Colors

**Status Colors:**

```python
# Success (Green - pass, compliant)
SUCCESS_LIGHT = "#D1F4E0"
SUCCESS       = "#10B981"
SUCCESS_DARK  = "#059669"

# Warning (Amber - caution, near limits)
WARNING_LIGHT = "#FEF3C7"
WARNING       = "#F59E0B"
WARNING_DARK  = "#D97706"

# Error (Red - failure, non-compliant)
ERROR_LIGHT = "#FEE2E2"
ERROR       = "#EF4444"
ERROR_DARK  = "#DC2626"

# Info (Blue - neutral information)
INFO_LIGHT = "#DBEAFE"
INFO       = "#3B82F6"
INFO_DARK  = "#2563EB"
```

### 2.3 Neutral Grays

```python
# Backgrounds, borders, text
GRAY_50  = "#FAFAFA"  # Page background
GRAY_100 = "#F5F5F5"  # Card background
GRAY_200 = "#E5E5E5"  # Dividers
GRAY_300 = "#D4D4D4"  # Disabled borders
GRAY_400 = "#A3A3A3"  # Placeholder text
GRAY_500 = "#737373"  # Secondary text
GRAY_600 = "#525252"  # Body text
GRAY_700 = "#404040"  # Headings
GRAY_800 = "#262626"  # Emphasis
GRAY_900 = "#171717"  # Maximum contrast
```

### 2.4 Color Usage Guidelines

**60-30-10 Rule:**
- **60% Primary (Navy):** Sidebar, headers, main sections
- **30% Neutral (Grays):** Backgrounds, cards, content areas
- **10% Accent (Orange):** Buttons, highlights, active states

**Accessibility Requirements:**
- Text contrast ratio: 4.5:1 minimum (AA), 7:1 preferred (AAA)
- Primary on white: 14.3:1 ✅
- Accent on white: 3.4:1 ⚠️ (use darker shade for text)
- Success/Warning/Error: All pass 4.5:1 ✅

**Color-blind Considerations:**
- Don't rely on color alone (use icons + text)
- Test with deuteranopia simulator
- Provide pattern/texture alternatives for charts

---

## Part 3: Typography System

### 3.1 Font Families

**Primary Font (UI Text):** Inter
- Modern, highly legible
- Excellent at small sizes
- Variable font (smooth scaling)
- Supports tabular figures
- Open source, free

**Secondary Font (Code/Numbers):** JetBrains Mono
- Monospaced, designed for readability
- Clear distinction between similar characters (0/O, 1/l/I)
- Ligatures for operators (<=, >=, !=)
- Perfect for dimensions, calculations

**Fallback Stack:**
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
             'Roboto', 'Helvetica Neue', Arial, sans-serif;

/* For code/numbers */
font-family: 'JetBrains Mono', 'SF Mono', Monaco, 'Cascadia Code',
             'Roboto Mono', Consolas, monospace;
```

### 3.2 Type Scale

**Modular Scale (1.25 ratio):**

```python
# Display (Hero text, rarely used)
DISPLAY_SIZE = "48px"     # Line height: 56px
DISPLAY_WEIGHT = 700

# H1 (Page titles)
H1_SIZE = "36px"          # Line height: 44px
H1_WEIGHT = 700

# H2 (Section headers)
H2_SIZE = "28px"          # Line height: 36px
H2_WEIGHT = 600

# H3 (Subsection headers)
H3_SIZE = "24px"          # Line height: 32px
H3_WEIGHT = 600

# H4 (Card titles)
H4_SIZE = "20px"          # Line height: 28px
H4_WEIGHT = 600

# Body Large (Emphasis)
BODY_LG_SIZE = "18px"     # Line height: 28px (1.56)
BODY_LG_WEIGHT = 400

# Body (Default text)
BODY_SIZE = "16px"        # Line height: 24px (1.5)
BODY_WEIGHT = 400

# Body Small (Secondary info)
BODY_SM_SIZE = "14px"     # Line height: 20px (1.43)
BODY_SM_WEIGHT = 400

# Caption (Labels, metadata)
CAPTION_SIZE = "12px"     # Line height: 16px (1.33)
CAPTION_WEIGHT = 400

# Button Text
BUTTON_SIZE = "14px"      # Line height: 20px
BUTTON_WEIGHT = 500       # Medium weight
```

### 3.3 Typography Usage

**Line Length:**
- Optimal: 50-75 characters per line
- Maximum: 90 characters
- Use containers to constrain width

**Line Height:**
- Body text: 1.5 (24px for 16px font)
- Headings: 1.2-1.3
- Captions: 1.33

**Letter Spacing:**
- Headings: -0.02em (tighter)
- Body: 0em (default)
- Uppercase text: +0.05em (looser)
- Numbers: Tabular figures (equal width)

**Paragraph Spacing:**
- Between paragraphs: 1em (16px)
- After headings: 0.5em (8px)

---

## Part 4: Spacing System

### 4.1 Base Unit: 8px

**Why 8px?**
- Divisible by 2, 4, 8 (flexibility)
- Aligns with most screen pixel densities
- Industry standard (Material, iOS HIG, Bootstrap)

### 4.2 Spacing Scale

```python
# Spacing tokens
SPACE_0 = "0px"       # None
SPACE_1 = "4px"       # Hairline
SPACE_2 = "8px"       # XXS - Tight spacing
SPACE_3 = "12px"      # XS  - Between related items
SPACE_4 = "16px"      # SM  - Default spacing
SPACE_5 = "24px"      # MD  - Section spacing
SPACE_6 = "32px"      # LG  - Major sections
SPACE_7 = "40px"      # XL  - Page sections
SPACE_8 = "48px"      # 2XL - Large gaps
SPACE_9 = "64px"      # 3XL - Hero spacing
SPACE_10 = "80px"     # 4XL - Maximum spacing
```

### 4.3 Spacing Usage Guidelines

**Component Internal Spacing (Padding):**
```python
# Button
padding: 12px 24px    # Vertical: SPACE_3, Horizontal: SPACE_5

# Card
padding: 24px         # All sides: SPACE_5

# Input Field
padding: 8px 12px     # Vertical: SPACE_2, Horizontal: SPACE_3

# Page Container
padding: 32px         # SPACE_6
```

**Component External Spacing (Margin):**
```python
# Between related inputs
margin-bottom: 12px   # SPACE_3

# Between sections
margin-bottom: 32px   # SPACE_6

# Between major page sections
margin-bottom: 64px   # SPACE_9
```

---

## Part 5: Elevation & Depth

### 5.1 Shadow System (4 Levels)

**Level 0 (Flat):** No shadow
- Usage: Background elements, dividers
```css
box-shadow: none;
```

**Level 1 (Raised):** Subtle depth
- Usage: Cards, inputs in default state
```css
box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
```

**Level 2 (Elevated):** Clear separation
- Usage: Dropdowns, popovers, hover states
```css
box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
            0 2px 4px -1px rgba(0, 0, 0, 0.06);
```

**Level 3 (Floating):** Strong emphasis
- Usage: Modals, tooltips, active states
```css
box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
            0 4px 6px -2px rgba(0, 0, 0, 0.05);
```

**Level 4 (Prominent):** Maximum depth
- Usage: Dialogs, overlays
```css
box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
```

### 5.2 Border Radius

```python
RADIUS_NONE = "0px"      # Sharp corners (rare)
RADIUS_SM = "4px"        # Buttons, inputs
RADIUS_MD = "8px"        # Cards, containers
RADIUS_LG = "12px"       # Panels, modals
RADIUS_XL = "16px"       # Hero sections
RADIUS_FULL = "9999px"   # Pills, avatars
```

### 5.3 Layering (Z-Index)

```python
# Z-index scale (100-unit increments)
Z_BASE = 0           # Default layer
Z_DROPDOWN = 100     # Dropdowns, selects
Z_STICKY = 200       # Sticky headers
Z_OVERLAY = 300      # Overlays, backdrops
Z_MODAL = 400        # Modal dialogs
Z_POPOVER = 500      # Tooltips, popovers
Z_TOAST = 600        # Notifications
```

---

## Part 6: Component Styling Patterns

### 6.1 Card Component

**Visual Specs:**
```python
background: GRAY_50 (light mode) / GRAY_800 (dark mode)
border: 1px solid GRAY_200 / GRAY_700
border-radius: RADIUS_MD (8px)
padding: SPACE_5 (24px)
box-shadow: ELEVATION_1
transition: box-shadow 200ms ease

# Hover state
box-shadow: ELEVATION_2
border-color: PRIMARY_200
transform: translateY(-2px)  # Subtle lift
```

**Variants:**
- **Default:** Neutral background, subtle shadow
- **Highlight:** Accent border, stronger shadow
- **Disabled:** Reduced opacity (60%), no hover
- **Interactive:** Cursor pointer, hover lift

### 6.2 Button Component

**Primary Button:**
```python
background: ACCENT_500 (orange)
color: WHITE
border: none
border-radius: RADIUS_SM (4px)
padding: 12px 24px
font-size: BUTTON_SIZE (14px)
font-weight: BUTTON_WEIGHT (500)
box-shadow: ELEVATION_1
transition: all 200ms ease

# Hover
background: ACCENT_600
box-shadow: ELEVATION_2
transform: translateY(-1px)

# Active (pressed)
background: ACCENT_700
box-shadow: ELEVATION_0
transform: translateY(0px)

# Disabled
background: GRAY_300
cursor: not-allowed
opacity: 0.6
```

**Secondary Button:**
```python
background: transparent
color: PRIMARY_500
border: 1px solid PRIMARY_500
# ... rest similar to primary
```

**Ghost Button:**
```python
background: transparent
color: GRAY_700
border: none
# ... hover adds background: GRAY_100
```

### 6.3 Input Field

**Text Input:**
```python
background: WHITE
border: 1px solid GRAY_300
border-radius: RADIUS_SM (4px)
padding: 8px 12px
font-size: BODY_SIZE (16px)
color: GRAY_700
transition: border-color 200ms ease

# Focus
border-color: PRIMARY_500
box-shadow: 0 0 0 3px rgba(0, 51, 102, 0.1)  # Focus ring
outline: none

# Error
border-color: ERROR
box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1)

# Disabled
background: GRAY_100
color: GRAY_400
cursor: not-allowed
```

**Number Input (Engineering-specific):**
```python
font-family: JetBrains Mono  # Monospace for alignment
font-variant-numeric: tabular-nums  # Equal-width digits
text-align: right  # Right-align numbers
```

### 6.4 Data Display

**Key-Value Pairs:**
```python
# Label
font-size: CAPTION_SIZE (12px)
color: GRAY_500
text-transform: uppercase
letter-spacing: 0.05em
margin-bottom: SPACE_1 (4px)

# Value
font-size: BODY_LG_SIZE (18px)
color: GRAY_800
font-weight: 600
font-variant-numeric: tabular-nums  # For numbers
```

**Result Cards:**
```python
background: SUCCESS_LIGHT / WARNING_LIGHT / ERROR_LIGHT
border-left: 4px solid SUCCESS / WARNING / ERROR
padding: SPACE_4 (16px)
border-radius: RADIUS_MD (8px)
margin-bottom: SPACE_4

# Icon
size: 24px
color: SUCCESS / WARNING / ERROR
margin-right: SPACE_3 (12px)
```

---

## Part 7: Layout Patterns

### 7.1 Grid System

**12-Column Grid:**
```python
# Container
max-width: 1280px
margin: 0 auto
padding: 0 32px

# Breakpoints
mobile: 0-640px       # 4 columns
tablet: 641-1024px    # 8 columns
desktop: 1025px+      # 12 columns

# Gutters
mobile: 16px
tablet: 24px
desktop: 32px
```

### 7.2 Page Layout

**Standard Dashboard Layout:**
```
┌─────────────────────────────────────────┐
│ HEADER (sticky)                         │ 64px height
├─────────┬───────────────────────────────┤
│         │                               │
│ SIDEBAR │ MAIN CONTENT                  │
│ (fixed) │ (scrollable)                  │
│ 280px   │                               │
│         │  ┌─────────────────────┐      │
│         │  │ CARD                │      │
│         │  └─────────────────────┘      │
│         │                               │
│         │  ┌─────────────────────┐      │
│         │  │ CARD                │      │
│         │  └─────────────────────┘      │
│         │                               │
└─────────┴───────────────────────────────┘
```

**Sidebar Structure:**
```python
background: GRAY_50
border-right: 1px solid GRAY_200
padding: SPACE_6 (32px) SPACE_4 (16px)
width: 280px
height: 100vh
position: fixed
overflow-y: auto

# Logo
margin-bottom: SPACE_8 (48px)

# Navigation Items
padding: SPACE_3 (12px) SPACE_4 (16px)
border-radius: RADIUS_SM (4px)
margin-bottom: SPACE_2 (8px)
transition: background 150ms ease

# Active Item
background: PRIMARY_50
color: PRIMARY_700
border-left: 3px solid PRIMARY_500
```

### 7.3 Content Density

**Information Hierarchy:**
1. **Primary info** (most important): Largest, boldest, top of viewport
2. **Secondary info**: Slightly smaller, grouped logically
3. **Tertiary info**: Smallest, supplementary data

**Whitespace Usage:**
- Use generous whitespace between sections (48-64px)
- Tight spacing within related items (8-12px)
- Don't overcrowd the interface
- Let important elements breathe

---

## Part 8: Dark Mode

### 8.1 Dark Mode Colors

**Background Colors:**
```python
# Dark backgrounds
DARK_BG_PRIMARY = "#0A0F1C"    # Page background
DARK_BG_SECONDARY = "#1A2332"  # Card background
DARK_BG_TERTIARY = "#2A3342"   # Input background

# Dark text colors
DARK_TEXT_PRIMARY = "#F5F5F5"   # Main text
DARK_TEXT_SECONDARY = "#B3B3B3" # Secondary text
DARK_TEXT_TERTIARY = "#737373"  # Disabled text
```

**Adjusted Brand Colors:**
```python
# Primary (lighter in dark mode for contrast)
DARK_PRIMARY = "#4D8DD6"  # Lighter blue

# Accent (slightly desaturated)
DARK_ACCENT = "#FF8533"   # Softer orange
```

### 8.2 Dark Mode Principles

1. **Reduce luminance:** Pure black (#000) strains eyes—use dark grays
2. **Increase contrast:** Text needs higher contrast in dark mode
3. **Desaturate colors:** Bright colors are harsh on dark backgrounds
4. **Elevation with lightness:** Elevated surfaces are lighter, not darker
5. **Test thoroughly:** Colors behave differently in dark mode

**Elevation in Dark Mode:**
```python
# Surface elevation (lighter = higher)
SURFACE_0 = "#0A0F1C"  # Base
SURFACE_1 = "#1A2332"  # Raised (cards)
SURFACE_2 = "#2A3342"  # Elevated (modals)
SURFACE_3 = "#3A4352"  # Floating (tooltips)
```

---

## Part 9: Accessibility

### 9.1 Color Contrast

**WCAG 2.1 Requirements:**
- **AA (minimum):** 4.5:1 for normal text, 3:1 for large text
- **AAA (enhanced):** 7:1 for normal text, 4.5:1 for large text

**Testing Tools:**
- WebAIM Contrast Checker
- Stark (Figma plugin)
- Axe DevTools (browser extension)

### 9.2 Focus Indicators

**Visible Focus Ring:**
```python
# Focus styles (never remove!)
outline: 2px solid PRIMARY_500
outline-offset: 2px
border-radius: RADIUS_SM

# Or custom ring
box-shadow: 0 0 0 3px rgba(0, 51, 102, 0.3)
```

### 9.3 Keyboard Navigation

**Tab Order:**
- Logical flow (top to bottom, left to right)
- Skip to main content link
- Keyboard shortcuts documented

**Interactive Elements:**
- All clickable elements focusable
- Enter/Space activates buttons
- Escape closes modals
- Arrow keys navigate lists

---

## Part 10: Implementation in Streamlit

### 10.1 Custom CSS Injection

**Method 1: st.markdown with HTML/CSS**
```python
import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

    /* Root variables */
    :root {
        --primary-500: #003366;
        --accent-500: #FF6600;
        --gray-50: #FAFAFA;
        --gray-900: #171717;
        --space-4: 16px;
        --space-5: 24px;
        --radius-md: 8px;
        --shadow-1: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }

    /* Global font */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Streamlit button override */
    .stButton > button {
        background-color: var(--accent-500);
        color: white;
        border: none;
        border-radius: var(--radius-md);
        padding: 12px 24px;
        font-weight: 500;
        box-shadow: var(--shadow-1);
        transition: all 200ms ease;
    }

    .stButton > button:hover {
        background-color: #CC5200;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
    }

    /* Custom card class */
    .custom-card {
        background: var(--gray-50);
        border: 1px solid #E5E5E5;
        border-radius: var(--radius-md);
        padding: var(--space-5);
        box-shadow: var(--shadow-1);
        margin-bottom: var(--space-4);
    }
    </style>
    """, unsafe_allow_html=True)
```

### 10.2 Themed Components

**Custom Card Component:**
```python
def custom_card(title: str, content: str, variant: str = "default"):
    """
    Custom card with elevation and styling.

    Args:
        title: Card title
        content: Card content (markdown supported)
        variant: "default" | "success" | "warning" | "error"
    """
    colors = {
        "default": {"bg": "#FAFAFA", "border": "#E5E5E5"},
        "success": {"bg": "#D1F4E0", "border": "#10B981"},
        "warning": {"bg": "#FEF3C7", "border": "#F59E0B"},
        "error": {"bg": "#FEE2E2", "border": "#EF4444"},
    }

    bg = colors[variant]["bg"]
    border = colors[variant]["border"]

    st.markdown(f"""
    <div style="
        background: {bg};
        border-left: 4px solid {border};
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    ">
        <h4 style="margin: 0 0 12px 0; color: #404040;">{title}</h4>
        <div style="color: #525252;">{content}</div>
    </div>
    """, unsafe_allow_html=True)
```

### 10.3 Theme Configuration

**`.streamlit/config.toml`:**
```toml
[theme]
primaryColor = "#FF6600"       # Accent orange
backgroundColor = "#FAFAFA"    # Light gray background
secondaryBackgroundColor = "#FFFFFF"  # White cards
textColor = "#171717"          # Dark gray text
font = "sans serif"            # Will be overridden by custom CSS

[client]
showErrorDetails = false
toolbarMode = "minimal"
```

---

## Part 11: Design Tokens (Reusable Constants)

### 11.1 Python Implementation

**`streamlit_app/utils/design_tokens.py`:**
```python
"""
Design tokens for consistent styling across the application.
Based on RESEARCH-004: Modern UI Design Systems.
"""

from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class ColorPalette:
    """Color palette based on IS 456 brand colors."""

    # Primary (Navy Blue)
    PRIMARY_50 = "#E6EDF5"
    PRIMARY_500 = "#003366"
    PRIMARY_700 = "#001F3D"

    # Accent (Orange)
    ACCENT_50 = "#FFF3E6"
    ACCENT_500 = "#FF6600"
    ACCENT_700 = "#993D00"

    # Semantic
    SUCCESS = "#10B981"
    SUCCESS_LIGHT = "#D1F4E0"
    WARNING = "#F59E0B"
    WARNING_LIGHT = "#FEF3C7"
    ERROR = "#EF4444"
    ERROR_LIGHT = "#FEE2E2"
    INFO = "#3B82F6"
    INFO_LIGHT = "#DBEAFE"

    # Grays
    GRAY_50 = "#FAFAFA"
    GRAY_100 = "#F5F5F5"
    GRAY_200 = "#E5E5E5"
    GRAY_500 = "#737373"
    GRAY_700 = "#404040"
    GRAY_900 = "#171717"

@dataclass(frozen=True)
class Spacing:
    """Spacing scale (8px base unit)."""
    SPACE_1 = "4px"
    SPACE_2 = "8px"
    SPACE_3 = "12px"
    SPACE_4 = "16px"
    SPACE_5 = "24px"
    SPACE_6 = "32px"
    SPACE_7 = "40px"
    SPACE_8 = "48px"
    SPACE_9 = "64px"

@dataclass(frozen=True)
class Typography:
    """Typography scale and settings."""
    FONT_FAMILY_UI = "'Inter', sans-serif"
    FONT_FAMILY_MONO = "'JetBrains Mono', monospace"

    DISPLAY_SIZE = "48px"
    H1_SIZE = "36px"
    H2_SIZE = "28px"
    H3_SIZE = "24px"
    H4_SIZE = "20px"
    BODY_LG_SIZE = "18px"
    BODY_SIZE = "16px"
    BODY_SM_SIZE = "14px"
    CAPTION_SIZE = "12px"

    LINE_HEIGHT_TIGHT = 1.25
    LINE_HEIGHT_NORMAL = 1.5
    LINE_HEIGHT_RELAXED = 1.75

@dataclass(frozen=True)
class Elevation:
    """Shadow levels for depth."""
    SHADOW_0 = "none"
    SHADOW_1 = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SHADOW_2 = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    SHADOW_3 = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    SHADOW_4 = "0 25px 50px -12px rgba(0, 0, 0, 0.25)"

@dataclass(frozen=True)
class BorderRadius:
    """Border radius scale."""
    RADIUS_NONE = "0px"
    RADIUS_SM = "4px"
    RADIUS_MD = "8px"
    RADIUS_LG = "12px"
    RADIUS_XL = "16px"
    RADIUS_FULL = "9999px"

# Singleton instances
COLORS = ColorPalette()
SPACING = Spacing()
TYPOGRAPHY = Typography()
ELEVATION = Elevation()
RADIUS = BorderRadius()
```

**Usage Example:**
```python
from streamlit_app.utils.design_tokens import COLORS, SPACING, ELEVATION

st.markdown(f"""
<div style="
    background: {COLORS.GRAY_50};
    padding: {SPACING.SPACE_5};
    border-radius: {RADIUS.RADIUS_MD};
    box-shadow: {ELEVATION.SHADOW_1};
">
    Content here
</div>
""", unsafe_allow_html=True)
```

---

## Part 12: Component Library Recommendations

### 12.1 Streamlit-Compatible Component Libraries

**1. streamlit-extras**
- Pre-built styled components
- Badges, metrics, cards
- Easy to integrate

**2. streamlit-aggrid**
- Advanced data tables
- Sorting, filtering, pagination
- Professional appearance

**3. streamlit-plotly-events**
- Interactive Plotly charts
- Click/hover events
- Bidirectional communication

**4. streamlit-option-menu**
- Horizontal/vertical menus
- Icons, custom styling
- Better than default sidebar

### 12.2 Custom Component Strategy

**When to Build Custom:**
- Unique engineering-specific widgets
- Complex interactions not supported
- Brand-specific styling needed

**When to Use Library:**
- Standard UI patterns (tables, charts)
- Time constraints
- Well-maintained, popular libraries

---

## Part 13: Responsive Design

### 13.1 Breakpoints

```python
MOBILE = "max-width: 640px"      # Phone
TABLET = "max-width: 1024px"     # Tablet
DESKTOP = "min-width: 1025px"    # Desktop
```

### 13.2 Mobile-First Approach

**Principles:**
1. Start with mobile layout
2. Progressively enhance for larger screens
3. Touch-friendly targets (min 44x44px)
4. Stack elements vertically on mobile
5. Use `use_container_width=True` for charts

**Example:**
```css
/* Mobile (default) */
.card {
    width: 100%;
    padding: 16px;
}

/* Tablet and up */
@media (min-width: 641px) {
    .card {
        width: 48%;
        padding: 24px;
    }
}

/* Desktop */
@media (min-width: 1025px) {
    .card {
        width: 32%;
        padding: 32px;
    }
}
```

---

## Part 14: Animation & Transitions

### 14.1 Timing Functions

```python
# Easing curves
EASE_IN = "cubic-bezier(0.4, 0, 1, 1)"
EASE_OUT = "cubic-bezier(0, 0, 0.2, 1)"
EASE_IN_OUT = "cubic-bezier(0.4, 0, 0.2, 1)"

# Durations
DURATION_FAST = "150ms"
DURATION_NORMAL = "200ms"
DURATION_SLOW = "300ms"
```

### 14.2 Animation Principles

**Do:**
- Use subtle animations (200-300ms)
- Provide visual feedback (button press, loading)
- Respect `prefers-reduced-motion` media query

**Don't:**
- Animate layout shifts (causes reflow)
- Use long durations (>500ms feels sluggish)
- Animate everything (overwhelming)

**Common Animations:**
```css
/* Hover lift */
.card:hover {
    transform: translateY(-2px);
    transition: transform 200ms ease-out;
}

/* Fade in */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* Slide in from right */
@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}
```

---

## Part 15: Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Create `design_tokens.py` with all constants
- [ ] Set up custom CSS injection system
- [ ] Configure `.streamlit/config.toml`
- [ ] Import Google Fonts (Inter, JetBrains Mono)

### Phase 2: Core Components (Week 2)
- [ ] Style buttons (primary, secondary, ghost)
- [ ] Style inputs (text, number, select)
- [ ] Create custom card component
- [ ] Style headers and typography

### Phase 3: Layout (Week 3)
- [ ] Implement sidebar styling
- [ ] Create grid system
- [ ] Add responsive breakpoints
- [ ] Test on mobile/tablet/desktop

### Phase 4: Advanced (Week 4)
- [ ] Add dark mode toggle
- [ ] Implement animations
- [ ] Add accessibility features
- [ ] Create component documentation

---

## Key Takeaways

1. **Consistency is king** - Use design tokens for all styling
2. **Accessibility matters** - WCAG 2.1 AA minimum, test with tools
3. **Less is more** - Don't over-style, let content shine
4. **Test everything** - Mobile, desktop, dark mode, accessibility
5. **Document patterns** - Help future developers maintain consistency

**Next Steps:**
- Review RESEARCH-005 (Streamlit Custom Components & Styling)
- Create component library in `streamlit_app/components/styled/`
- Build design system documentation
- Implement phase 1 (foundation)

---

**Research Complete:** 2026-01-08
**Total Time:** 6 hours
**Lines:** 980
**Status:** ✅ READY FOR IMPLEMENTATION
