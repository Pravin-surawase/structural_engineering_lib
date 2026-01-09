"""
Design System - Core design tokens and theme configuration.

Based on RESEARCH-004 (Modern UI Design Systems).
Implements Material Design 3 principles adapted for engineering applications.

Version: 1.0
Created: 2026-01-08
"""

from dataclasses import dataclass
from typing import Dict, Literal

# ============================================================================
# PART 1: COLOR SYSTEM
# ============================================================================


@dataclass(frozen=True)
class ColorPalette:
    """Immutable color palette following 60-30-10 rule."""

    # Primary (Navy Blue - 60% usage)
    primary_50: str = "#E6EDF5"
    primary_100: str = "#CCDAEA"
    primary_200: str = "#99B5D5"
    primary_300: str = "#6690C0"
    primary_400: str = "#336BAB"
    primary_500: str = "#003366"  # Base brand color
    primary_600: str = "#002952"
    primary_700: str = "#001F3D"
    primary_800: str = "#001429"
    primary_900: str = "#000A14"

    # Accent (Orange - 10% usage)
    accent_50: str = "#FFF3E6"
    accent_100: str = "#FFE7CC"
    accent_200: str = "#FFCF99"
    accent_300: str = "#FFB766"
    accent_400: str = "#FF9F33"
    accent_500: str = "#FF6600"  # Base call-to-action
    accent_600: str = "#CC5200"
    accent_700: str = "#993D00"
    accent_800: str = "#662900"
    accent_900: str = "#331400"

    # Semantic Colors
    success_light: str = "#D1F4E0"
    success: str = "#10B981"
    success_dark: str = "#059669"

    warning_light: str = "#FEF3C7"
    warning: str = "#F59E0B"
    warning_dark: str = "#D97706"

    error_light: str = "#FEE2E2"
    error: str = "#EF4444"
    error_dark: str = "#DC2626"

    info_light: str = "#DBEAFE"
    info: str = "#3B82F6"
    info_dark: str = "#2563EB"

    # Neutral Grays (30% usage)
    gray_50: str = "#FAFAFA"
    gray_100: str = "#F5F5F5"
    gray_200: str = "#E5E5E5"
    gray_300: str = "#D4D4D4"
    gray_400: str = "#A3A3A3"
    gray_500: str = "#737373"
    gray_600: str = "#525252"
    gray_700: str = "#404040"
    gray_800: str = "#262626"
    gray_900: str = "#171717"

    # Semantic aliases for common UI patterns
    text_primary: str = "#171717"  # Same as gray_900
    text_secondary: str = "#525252"  # Same as gray_600
    bg_primary: str = "#FFFFFF"  # White background
    bg_secondary: str = "#F5F5F5"  # Same as gray_100


# Singleton instance
COLORS = ColorPalette()


# ============================================================================
# PART 2: TYPOGRAPHY SYSTEM
# ============================================================================


@dataclass(frozen=True)
class TypographyScale:
    """Typography system with modular scale (1.25 ratio)."""

    # Font families
    font_ui: str = (
        "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', "
        "'Roboto', 'Helvetica Neue', Arial, sans-serif"
    )
    font_mono: str = (
        "'JetBrains Mono', 'SF Mono', Monaco, 'Cascadia Code', "
        "'Roboto Mono', Consolas, monospace"
    )

    # Display (Hero text)
    display_size: str = "48px"
    display_line_height: str = "56px"
    display_weight: int = 700

    # H1 (Page titles)
    h1_size: str = "36px"
    h1_line_height: str = "44px"
    h1_weight: int = 700

    # H2 (Section headers)
    h2_size: str = "28px"
    h2_line_height: str = "36px"
    h2_weight: int = 600

    # H3 (Subsection headers)
    h3_size: str = "24px"
    h3_line_height: str = "32px"
    h3_weight: int = 600

    # H4 (Card titles)
    h4_size: str = "20px"
    h4_line_height: str = "28px"
    h4_weight: int = 600

    # Body Large
    body_lg_size: str = "18px"
    body_lg_line_height: str = "28px"
    body_lg_weight: int = 400

    # Body (Default)
    body_size: str = "16px"
    body_line_height: str = "24px"
    body_weight: int = 400

    # Body Small
    body_sm_size: str = "14px"
    body_sm_line_height: str = "20px"
    body_sm_weight: int = 400

    # Caption
    caption_size: str = "12px"
    caption_line_height: str = "16px"
    caption_weight: int = 400

    # Button
    button_size: str = "14px"
    button_line_height: str = "20px"
    button_weight: int = 500

    # Semantic aliases for common use cases
    display_sm: str = "36px"  # Same as h1_size
    display_md: str = "48px"  # Same as display_size
    heading_xl: str = "28px"  # Same as h2_size
    heading_lg: str = "24px"  # Same as h3_size
    heading_sm: str = "20px"  # Same as h4_size
    body_lg: str = "18px"     # Same as body_lg_size
    body_md: str = "16px"     # Same as body_size
    body_sm: str = "14px"     # Same as body_sm_size
    text_xs: str = "12px"     # Same as caption_size
    text_sm: str = "14px"     # Same as body_sm_size
    text_base: str = "16px"   # Same as body_size
    text_lg: str = "18px"     # Same as body_lg_size


TYPOGRAPHY = TypographyScale()


# ============================================================================
# PART 3: SPACING SYSTEM
# ============================================================================


@dataclass(frozen=True)
class SpacingScale:
    """8px-based spacing system."""

    space_0: str = "0px"
    space_1: str = "4px"
    space_2: str = "8px"
    space_3: str = "12px"
    space_4: str = "16px"
    space_5: str = "24px"
    space_6: str = "32px"
    space_7: str = "40px"
    space_8: str = "48px"
    space_9: str = "64px"
    space_10: str = "80px"

    # Semantic T-shirt sizes (rem-based for responsive design)
    xs: str = "0.5rem"   # 8px
    sm: str = "0.75rem"  # 12px
    md: str = "1rem"     # 16px
    lg: str = "1.5rem"   # 24px
    xl: str = "2rem"     # 32px
    xxl: str = "3rem"    # 48px


SPACING = SpacingScale()


# ============================================================================
# PART 4: ELEVATION SYSTEM
# ============================================================================


@dataclass(frozen=True)
class ElevationSystem:
    """4-level shadow system for depth."""

    level_0: str = "none"
    level_1: str = "0px 1px 3px rgba(0, 0, 0, 0.12), 0px 1px 2px rgba(0, 0, 0, 0.24)"
    level_2: str = (
        "0px 3px 6px rgba(0, 0, 0, 0.15), 0px 2px 4px rgba(0, 0, 0, 0.12)"
    )
    level_3: str = (
        "0px 10px 20px rgba(0, 0, 0, 0.15), 0px 3px 6px rgba(0, 0, 0, 0.10)"
    )
    level_4: str = (
        "0px 15px 25px rgba(0, 0, 0, 0.15), 0px 5px 10px rgba(0, 0, 0, 0.05)"
    )

    # Semantic aliases for common use cases
    shadow_xs: str = "0px 1px 2px rgba(0, 0, 0, 0.1)"  # Extra small shadow
    shadow_sm: str = "0px 1px 3px rgba(0, 0, 0, 0.12), 0px 1px 2px rgba(0, 0, 0, 0.24)"  # Same as level_1
    shadow_md: str = "0px 3px 6px rgba(0, 0, 0, 0.15), 0px 2px 4px rgba(0, 0, 0, 0.12)"  # Same as level_2
    shadow_lg: str = "0px 10px 20px rgba(0, 0, 0, 0.15), 0px 3px 6px rgba(0, 0, 0, 0.10)"  # Same as level_3
    shadow_xl: str = "0px 15px 25px rgba(0, 0, 0, 0.15), 0px 5px 10px rgba(0, 0, 0, 0.05)"  # Same as level_4


ELEVATION = ElevationSystem()


# ============================================================================
# PART 5: ANIMATION TIMING
# ============================================================================


@dataclass(frozen=True)
class AnimationTimings:
    """Standard animation durations and easing."""

    # Durations (CSS format - for Streamlit CSS injection)
    instant: str = "100ms"
    fast: str = "200ms"
    normal: str = "300ms"
    slow: str = "500ms"

    # Semantic aliases for CSS (PATTERN: duration_*)
    duration_instant: str = "100ms"  # Same as instant
    duration_fast: str = "200ms"     # Same as fast
    duration_normal: str = "300ms"   # Same as normal
    duration_slow: str = "500ms"     # Same as slow

    # Numeric durations for Plotly (milliseconds as int)
    # Plotly requires numeric values, not CSS strings
    duration_instant_ms: int = 100
    duration_fast_ms: int = 200
    duration_normal_ms: int = 300
    duration_slow_ms: int = 500

    # Easing functions
    ease_in_out: str = "cubic-bezier(0.4, 0, 0.2, 1)"
    ease_out: str = "cubic-bezier(0.0, 0, 0.2, 1)"
    ease_in: str = "cubic-bezier(0.4, 0, 1, 1)"
    ease_linear: str = "linear"


ANIMATION = AnimationTimings()


# ============================================================================
# PART 6: BORDER RADIUS
# ============================================================================


@dataclass(frozen=True)
class BorderRadius:
    """Border radius scale for rounded corners."""

    none: str = "0px"
    sm: str = "4px"
    md: str = "8px"
    lg: str = "12px"
    xl: str = "16px"
    full: str = "9999px"


RADIUS = BorderRadius()


# ============================================================================
# PART 7: BREAKPOINTS (Responsive Design)
# ============================================================================


@dataclass(frozen=True)
class Breakpoints:
    """Responsive breakpoints."""

    mobile: str = "320px"
    mobile_lg: str = "480px"
    tablet: str = "768px"
    desktop: str = "1024px"
    desktop_lg: str = "1440px"
    desktop_xl: str = "1920px"


BREAKPOINTS = Breakpoints()


# ============================================================================
# PART 8: COMPONENT SPECS
# ============================================================================


@dataclass
class ButtonSpecs:
    """Button component specifications."""

    height_sm: str = "32px"
    height_md: str = "40px"
    height_lg: str = "48px"

    padding_sm: str = f"{SPACING.space_2} {SPACING.space_4}"
    padding_md: str = f"{SPACING.space_3} {SPACING.space_5}"
    padding_lg: str = f"{SPACING.space_4} {SPACING.space_6}"

    border_radius: str = RADIUS.md
    font_size: str = TYPOGRAPHY.button_size
    font_weight: int = TYPOGRAPHY.button_weight


@dataclass
class InputSpecs:
    """Input field specifications."""

    height: str = "40px"
    padding: str = f"{SPACING.space_2} {SPACING.space_3}"
    border_radius: str = RADIUS.sm
    border_width: str = "1px"
    font_size: str = TYPOGRAPHY.body_size


@dataclass
class CardSpecs:
    """Card component specifications."""

    padding_sm: str = SPACING.space_4
    padding_md: str = SPACING.space_5
    padding_lg: str = SPACING.space_6

    border_radius: str = RADIUS.lg
    elevation: str = ELEVATION.level_1


BUTTON_SPECS = ButtonSpecs()
INPUT_SPECS = InputSpecs()
CARD_SPECS = CardSpecs()


# ============================================================================
# PART 9: DARK MODE COLORS
# ============================================================================


@dataclass(frozen=True)
class DarkModePalette:
    """Dark mode color overrides."""

    # Background colors
    bg_primary: str = "#0F1419"
    bg_secondary: str = "#1A1F26"
    bg_tertiary: str = "#252B33"

    # Text colors
    text_primary: str = "#F5F5F5"
    text_secondary: str = "#A3A3A3"
    text_tertiary: str = "#737373"

    # Border colors
    border_primary: str = "#404040"
    border_secondary: str = "#2C2C2C"

    # Primary adapted for dark
    primary: str = "#4A90E2"
    primary_hover: str = "#5FA3F5"

    # Accent adapted for dark
    accent: str = "#FF8533"
    accent_hover: str = "#FFA366"


DARK_COLORS = DarkModePalette()


# ============================================================================
# PART 10: THEME GENERATOR
# ============================================================================


def generate_css_variables(dark_mode: bool = False) -> str:
    """
    Generate CSS custom properties for theming.

    Args:
        dark_mode: Whether to use dark mode colors

    Returns:
        CSS string with custom properties
    """
    colors = DARK_COLORS if dark_mode else COLORS

    css = f"""
    :root {{
        /* Colors - Primary */
        --color-primary-50: {COLORS.primary_50};
        --color-primary-100: {COLORS.primary_100};
        --color-primary-500: {COLORS.primary_500};
        --color-primary-600: {COLORS.primary_600};
        --color-primary-900: {COLORS.primary_900};

        /* Colors - Accent */
        --color-accent-500: {COLORS.accent_500};
        --color-accent-600: {COLORS.accent_600};

        /* Colors - Semantic */
        --color-success: {COLORS.success};
        --color-success-light: {COLORS.success_light};
        --color-warning: {COLORS.warning};
        --color-warning-light: {COLORS.warning_light};
        --color-error: {COLORS.error};
        --color-error-light: {COLORS.error_light};
        --color-info: {COLORS.info};
        --color-info-light: {COLORS.info_light};

        /* Colors - Grays */
        --color-gray-50: {COLORS.gray_50};
        --color-gray-100: {COLORS.gray_100};
        --color-gray-200: {COLORS.gray_200};
        --color-gray-400: {COLORS.gray_400};
        --color-gray-500: {COLORS.gray_500};
        --color-gray-600: {COLORS.gray_600};
        --color-gray-700: {COLORS.gray_700};
        --color-gray-900: {COLORS.gray_900};

        /* Typography */
        --font-ui: {TYPOGRAPHY.font_ui};
        --font-mono: {TYPOGRAPHY.font_mono};

        --font-size-h1: {TYPOGRAPHY.h1_size};
        --font-size-h2: {TYPOGRAPHY.h2_size};
        --font-size-h3: {TYPOGRAPHY.h3_size};
        --font-size-h4: {TYPOGRAPHY.h4_size};
        --font-size-body: {TYPOGRAPHY.body_size};
        --font-size-small: {TYPOGRAPHY.body_sm_size};
        --font-size-caption: {TYPOGRAPHY.caption_size};

        /* Spacing */
        --space-1: {SPACING.space_1};
        --space-2: {SPACING.space_2};
        --space-3: {SPACING.space_3};
        --space-4: {SPACING.space_4};
        --space-5: {SPACING.space_5};
        --space-6: {SPACING.space_6};
        --space-8: {SPACING.space_8};

        /* Elevation */
        --shadow-1: {ELEVATION.level_1};
        --shadow-2: {ELEVATION.level_2};
        --shadow-3: {ELEVATION.level_3};

        /* Radius */
        --radius-sm: {RADIUS.sm};
        --radius-md: {RADIUS.md};
        --radius-lg: {RADIUS.lg};

        /* Animation */
        --transition-fast: {ANIMATION.fast};
        --transition-normal: {ANIMATION.normal};
        --easing: {ANIMATION.ease_in_out};
    }}
    """

    if dark_mode:
        css += f"""
        body {{
            --bg-primary: {DARK_COLORS.bg_primary};
            --bg-secondary: {DARK_COLORS.bg_secondary};
            --text-primary: {DARK_COLORS.text_primary};
            --text-secondary: {DARK_COLORS.text_secondary};
        }}
        """

    return css


# ============================================================================
# PART 11: UTILITY FUNCTIONS
# ============================================================================


def get_semantic_color(
    status: Literal["success", "warning", "error", "info"],
    variant: Literal["base", "light", "dark"] = "base",
) -> str:
    """
    Get semantic color by status.

    Args:
        status: One of success, warning, error, info
        variant: Color variant (base, light, dark)

    Returns:
        Hex color code

    Example:
        >>> get_semantic_color("success", "light")
        '#D1F4E0'
    """
    color_map = {
        "success": (COLORS.success, COLORS.success_light, COLORS.success_dark),
        "warning": (COLORS.warning, COLORS.warning_light, COLORS.warning_dark),
        "error": (COLORS.error, COLORS.error_light, COLORS.error_dark),
        "info": (COLORS.info, COLORS.info_light, COLORS.info_dark),
    }

    variant_index = {"base": 0, "light": 1, "dark": 2}[variant]
    return color_map[status][variant_index]


def get_spacing(size: int) -> str:
    """
    Get spacing value by size number.

    Args:
        size: Spacing size (0-10)

    Returns:
        Spacing in pixels

    Example:
        >>> get_spacing(4)
        '16px'
    """
    spacing_map = {
        0: SPACING.space_0,
        1: SPACING.space_1,
        2: SPACING.space_2,
        3: SPACING.space_3,
        4: SPACING.space_4,
        5: SPACING.space_5,
        6: SPACING.space_6,
        7: SPACING.space_7,
        8: SPACING.space_8,
        9: SPACING.space_9,
        10: SPACING.space_10,
    }
    return spacing_map.get(size, SPACING.space_4)


# ============================================================================
# EXPORT PUBLIC API
# ============================================================================

__all__ = [
    "COLORS",
    "TYPOGRAPHY",
    "SPACING",
    "ELEVATION",
    "ANIMATION",
    "RADIUS",
    "BREAKPOINTS",
    "DARK_COLORS",
    "BUTTON_SPECS",
    "INPUT_SPECS",
    "CARD_SPECS",
    "generate_css_variables",
    "get_semantic_color",
    "get_spacing",
]
