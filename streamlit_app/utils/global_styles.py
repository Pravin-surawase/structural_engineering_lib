"""
Global Styles - Custom CSS for Streamlit app styling.

Based on RESEARCH-005 (Streamlit Custom Components & Styling).
Transforms default Streamlit UI with professional design system.

Version: 1.0
Created: 2026-01-08
"""

from .design_system import (
    COLORS,
    TYPOGRAPHY,
    SPACING,
    ELEVATION,
    RADIUS,
    ANIMATION,
    generate_css_variables,
)


# ============================================================================
# GLOBAL CSS (Part 1: Base Styles)
# ============================================================================

GLOBAL_CSS_PART1 = f"""
/* ==================== CSS VARIABLES ==================== */
{generate_css_variables(dark_mode=False)}

/* ==================== BASE RESETS ==================== */
* {{
    box-sizing: border-box;
}}

html, body {{
    font-family: {TYPOGRAPHY.font_ui};
    font-size: {TYPOGRAPHY.body_size};
    line-height: {TYPOGRAPHY.body_line_height};
    color: {COLORS.gray_900};
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

/* ==================== STREAMLIT SPECIFIC ==================== */

/* Hide default Streamlit elements */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}

/* Page container */
.main .block-container {{
    padding-top: {SPACING.space_6};
    padding-bottom: {SPACING.space_8};
    max-width: 1400px;
}}

/* Sidebar styling */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {COLORS.primary_500} 0%, {COLORS.primary_700} 100%);
    padding: {SPACING.space_5};
}}

[data-testid="stSidebar"] * {{
    color: white !important;
}}

[data-testid="stSidebar"] .stMarkdown {{
    color: white;
}}

/* Sidebar headings */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
    color: white !important;
    font-weight: 600;
}}

/* ==================== TYPOGRAPHY ==================== */

h1 {{
    font-size: {TYPOGRAPHY.h1_size};
    line-height: {TYPOGRAPHY.h1_line_height};
    font-weight: {TYPOGRAPHY.h1_weight};
    color: {COLORS.gray_900};
    margin-bottom: {SPACING.space_5};
    letter-spacing: -0.02em;
}}

h2 {{
    font-size: {TYPOGRAPHY.h2_size};
    line-height: {TYPOGRAPHY.h2_line_height};
    font-weight: {TYPOGRAPHY.h2_weight};
    color: {COLORS.gray_900};
    margin-top: {SPACING.space_6};
    margin-bottom: {SPACING.space_4};
    letter-spacing: -0.01em;
}}

h3 {{
    font-size: {TYPOGRAPHY.h3_size};
    line-height: {TYPOGRAPHY.h3_line_height};
    font-weight: {TYPOGRAPHY.h3_weight};
    color: {COLORS.gray_800};
    margin-top: {SPACING.space_5};
    margin-bottom: {SPACING.space_3};
}}

h4 {{
    font-size: {TYPOGRAPHY.h4_size};
    line-height: {TYPOGRAPHY.h4_line_height};
    font-weight: {TYPOGRAPHY.h4_weight};
    color: {COLORS.gray_800};
    margin-bottom: {SPACING.space_3};
}}

p {{
    margin-bottom: {SPACING.space_4};
    color: {COLORS.gray_700};
}}

code {{
    font-family: {TYPOGRAPHY.font_mono};
    background: {COLORS.gray_100};
    padding: {SPACING.space_1} {SPACING.space_2};
    border-radius: {RADIUS.sm};
    font-size: 0.9em;
    color: {COLORS.primary_600};
}}

pre {{
    font-family: {TYPOGRAPHY.font_mono};
    background: {COLORS.gray_100};
    padding: {SPACING.space_4};
    border-radius: {RADIUS.md};
    overflow-x: auto;
    border-left: 4px solid {COLORS.primary_500};
}}
"""


# ============================================================================
# GLOBAL CSS (Part 2: Input & Form Elements)
# ============================================================================

GLOBAL_CSS_PART2 = f"""
/* ==================== BUTTONS ==================== */

/* Primary button (Streamlit default) */
.stButton > button {{
    background: {COLORS.primary_500};
    color: white;
    border: none;
    border-radius: {RADIUS.md};
    padding: {SPACING.space_3} {SPACING.space_5};
    font-size: {TYPOGRAPHY.button_size};
    font-weight: {TYPOGRAPHY.button_weight};
    font-family: {TYPOGRAPHY.font_ui};
    cursor: pointer;
    transition: all {ANIMATION.fast} {ANIMATION.ease_in_out};
    box-shadow: {ELEVATION.level_1};
    height: 40px;
    min-width: 120px;
}}

.stButton > button:hover {{
    background: {COLORS.primary_600};
    box-shadow: {ELEVATION.level_2};
    transform: translateY(-1px);
}}

.stButton > button:active {{
    transform: translateY(0);
    box-shadow: {ELEVATION.level_1};
}}

.stButton > button:focus {{
    outline: 2px solid {COLORS.accent_500};
    outline-offset: 2px;
}}

/* Download button */
.stDownloadButton > button {{
    background: {COLORS.accent_500};
    color: white;
}}

.stDownloadButton > button:hover {{
    background: {COLORS.accent_600};
}}

/* ==================== INPUT FIELDS ==================== */

/* Text input */
.stTextInput > div > div > input {{
    font-family: {TYPOGRAPHY.font_ui};
    font-size: {TYPOGRAPHY.body_size};
    color: {COLORS.gray_900};
    background: white;
    border: 1px solid {COLORS.gray_300};
    border-radius: {RADIUS.sm};
    padding: {SPACING.space_2} {SPACING.space_3};
    transition: all {ANIMATION.fast} {ANIMATION.ease_in_out};
    height: 40px;
}}

.stTextInput > div > div > input:hover {{
    border-color: {COLORS.gray_400};
}}

.stTextInput > div > div > input:focus {{
    border-color: {COLORS.primary_500};
    box-shadow: 0 0 0 3px {COLORS.primary_100};
    outline: none;
}}

/* Number input */
.stNumberInput > div > div > input {{
    font-family: {TYPOGRAPHY.font_mono};
    font-size: {TYPOGRAPHY.body_size};
    color: {COLORS.gray_900};
    background: white;
    border: 1px solid {COLORS.gray_300};
    border-radius: {RADIUS.sm};
    padding: {SPACING.space_2} {SPACING.space_3};
    transition: all {ANIMATION.fast} {ANIMATION.ease_in_out};
    height: 40px;
}}

.stNumberInput > div > div > input:focus {{
    border-color: {COLORS.primary_500};
    box-shadow: 0 0 0 3px {COLORS.primary_100};
    outline: none;
}}

/* Select box */
.stSelectbox > div > div {{
    background: white;
    border: 1px solid {COLORS.gray_300};
    border-radius: {RADIUS.sm};
    transition: all {ANIMATION.fast} {ANIMATION.ease_in_out};
}}

.stSelectbox > div > div:hover {{
    border-color: {COLORS.gray_400};
}}

.stSelectbox > div > div > div {{
    font-family: {TYPOGRAPHY.font_ui};
    color: {COLORS.gray_900};
    padding: {SPACING.space_2} {SPACING.space_3};
}}

/* Slider */
.stSlider > div > div > div {{
    background: {COLORS.gray_200};
}}

.stSlider > div > div > div > div {{
    background: {COLORS.primary_500};
}}

.stSlider > div > div > div > div > div {{
    background: {COLORS.primary_500};
    border: 2px solid white;
    box-shadow: {ELEVATION.level_2};
}}

/* Checkbox */
.stCheckbox > label {{
    font-family: {TYPOGRAPHY.font_ui};
    color: {COLORS.gray_700};
    cursor: pointer;
}}

.stCheckbox > label > div {{
    background: white;
    border: 2px solid {COLORS.gray_300};
    border-radius: {RADIUS.sm};
    transition: all {ANIMATION.fast} {ANIMATION.ease_in_out};
}}

.stCheckbox > label > div[data-checked="true"] {{
    background: {COLORS.primary_500};
    border-color: {COLORS.primary_500};
}}

/* Radio button */
.stRadio > label {{
    font-family: {TYPOGRAPHY.font_ui};
    color: {COLORS.gray_700};
}}

.stRadio > div {{
    gap: {SPACING.space_2};
}}

.stRadio > div > label {{
    padding: {SPACING.space_2} {SPACING.space_3};
    border-radius: {RADIUS.md};
    transition: all {ANIMATION.fast} {ANIMATION.ease_in_out};
}}

.stRadio > div > label:hover {{
    background: {COLORS.gray_100};
}}

/* Input labels */
.stTextInput > label,
.stNumberInput > label,
.stSelectbox > label,
.stSlider > label {{
    font-family: {TYPOGRAPHY.font_ui};
    font-size: {TYPOGRAPHY.body_sm_size};
    font-weight: 500;
    color: {COLORS.gray_700};
    margin-bottom: {SPACING.space_2};
}}
"""


# ============================================================================
# GLOBAL CSS (Part 3: Layout & Components)
# ============================================================================

GLOBAL_CSS_PART3 = f"""
/* ==================== TABS ==================== */

.stTabs [data-baseweb="tab-list"] {{
    gap: {SPACING.space_2};
    background: {COLORS.gray_100};
    padding: {SPACING.space_2};
    border-radius: {RADIUS.lg};
}}

.stTabs [data-baseweb="tab"] {{
    font-family: {TYPOGRAPHY.font_ui};
    font-size: {TYPOGRAPHY.body_size};
    font-weight: 500;
    color: {COLORS.gray_600};
    background: transparent;
    border: none;
    border-radius: {RADIUS.md};
    padding: {SPACING.space_3} {SPACING.space_5};
    transition: all {ANIMATION.fast} {ANIMATION.ease_in_out};
}}

.stTabs [data-baseweb="tab"]:hover {{
    background: {COLORS.gray_200};
    color: {COLORS.gray_900};
}}

.stTabs [aria-selected="true"] {{
    background: white !important;
    color: {COLORS.primary_600} !important;
    box-shadow: {ELEVATION.level_1};
}}

/* ==================== EXPANDER ==================== */

.streamlit-expanderHeader {{
    font-family: {TYPOGRAPHY.font_ui};
    font-size: {TYPOGRAPHY.body_size};
    font-weight: 600;
    color: {COLORS.gray_900};
    background: {COLORS.gray_100};
    border-radius: {RADIUS.md};
    padding: {SPACING.space_3} {SPACING.space_4};
    transition: all {ANIMATION.fast} {ANIMATION.ease_in_out};
}}

.streamlit-expanderHeader:hover {{
    background: {COLORS.gray_200};
}}

.streamlit-expanderContent {{
    border: 1px solid {COLORS.gray_200};
    border-top: none;
    border-radius: 0 0 {RADIUS.md} {RADIUS.md};
    padding: {SPACING.space_4};
}}

/* ==================== COLUMNS ==================== */

[data-testid="column"] {{
    background: white;
    border-radius: {RADIUS.lg};
    padding: {SPACING.space_4};
    box-shadow: {ELEVATION.level_1};
}}

/* ==================== METRICS (st.metric) ==================== */

[data-testid="stMetric"] {{
    background: white;
    border-radius: {RADIUS.lg};
    padding: {SPACING.space_4};
    box-shadow: {ELEVATION.level_1};
}}

[data-testid="stMetricLabel"] {{
    font-family: {TYPOGRAPHY.font_ui};
    font-size: {TYPOGRAPHY.body_sm_size};
    font-weight: 500;
    color: {COLORS.gray_600};
}}

[data-testid="stMetricValue"] {{
    font-family: {TYPOGRAPHY.font_mono};
    font-size: {TYPOGRAPHY.h2_size};
    font-weight: 700;
    color: {COLORS.gray_900};
}}

[data-testid="stMetricDelta"] {{
    font-size: {TYPOGRAPHY.body_sm_size};
}}

/* ==================== DATAFRAME / TABLE ==================== */

.stDataFrame {{
    border-radius: {RADIUS.lg};
    overflow: hidden;
    box-shadow: {ELEVATION.level_1};
}}

.stDataFrame table {{
    font-family: {TYPOGRAPHY.font_mono};
    font-size: {TYPOGRAPHY.body_sm_size};
}}

.stDataFrame thead tr th {{
    background: {COLORS.primary_500};
    color: white;
    font-weight: 600;
    padding: {SPACING.space_3};
}}

.stDataFrame tbody tr:nth-child(even) {{
    background: {COLORS.gray_50};
}}

.stDataFrame tbody tr:hover {{
    background: {COLORS.primary_50};
}}

/* ==================== ALERTS ==================== */

.stSuccess {{
    background: {COLORS.success_light};
    border-left: 4px solid {COLORS.success};
    color: {COLORS.gray_900};
    border-radius: {RADIUS.md};
    padding: {SPACING.space_4};
}}

.stWarning {{
    background: {COLORS.warning_light};
    border-left: 4px solid {COLORS.warning};
    color: {COLORS.gray_900};
    border-radius: {RADIUS.md};
    padding: {SPACING.space_4};
}}

.stError {{
    background: {COLORS.error_light};
    border-left: 4px solid {COLORS.error};
    color: {COLORS.gray_900};
    border-radius: {RADIUS.md};
    padding: {SPACING.space_4};
}}

.stInfo {{
    background: {COLORS.info_light};
    border-left: 4px solid {COLORS.info};
    color: {COLORS.gray_900};
    border-radius: {RADIUS.md};
    padding: {SPACING.space_4};
}}

/* ==================== SPINNER ==================== */

.stSpinner > div {{
    border-color: {COLORS.primary_500} !important;
    border-right-color: transparent !important;
}}
"""


# ============================================================================
# GLOBAL CSS (Part 4: Responsive & Utilities)
# ============================================================================

GLOBAL_CSS_PART4 = f"""
/* ==================== PLOTLY CHARTS ==================== */

.js-plotly-plot {{
    border-radius: {RADIUS.lg};
    box-shadow: {ELEVATION.level_1};
    background: white;
    padding: {SPACING.space_2};
}}

/* ==================== LOADING STATE ==================== */

@keyframes shimmer {{
    0% {{
        background-position: -1000px 0;
    }}
    100% {{
        background-position: 1000px 0;
    }}
}}

.skeleton {{
    background: linear-gradient(
        90deg,
        {COLORS.gray_200} 0%,
        {COLORS.gray_300} 50%,
        {COLORS.gray_200} 100%
    );
    background-size: 1000px 100%;
    animation: shimmer 2s infinite linear;
    border-radius: {RADIUS.md};
}}

/* ==================== RESPONSIVE DESIGN ==================== */

@media (max-width: 768px) {{
    .main .block-container {{
        padding-top: {SPACING.space_4};
        padding-left: {SPACING.space_3};
        padding-right: {SPACING.space_3};
    }}

    h1 {{
        font-size: {TYPOGRAPHY.h2_size};
    }}

    h2 {{
        font-size: {TYPOGRAPHY.h3_size};
    }}

    [data-testid="stSidebar"] {{
        padding: {SPACING.space_3};
    }}
}}

/* ==================== ACCESSIBILITY ==================== */

/* Focus visible for keyboard navigation */
*:focus-visible {{
    outline: 2px solid {COLORS.accent_500};
    outline-offset: 2px;
}}

/* Respect reduced motion preferences */
@media (prefers-reduced-motion: reduce) {{
    * {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }}
}}

/* High contrast mode support */
@media (prefers-contrast: high) {{
    button, input, select {{
        border-width: 2px;
    }}
}}

/* ==================== PRINT STYLES ==================== */

@media print {{
    [data-testid="stSidebar"] {{
        display: none;
    }}

    .stButton {{
        display: none;
    }}

    body {{
        background: white;
    }}

    * {{
        box-shadow: none !important;
    }}
}}

/* ==================== UTILITY CLASSES ==================== */

.text-center {{
    text-align: center;
}}

.text-right {{
    text-align: right;
}}

.font-mono {{
    font-family: {TYPOGRAPHY.font_mono};
}}

.text-primary {{
    color: {COLORS.primary_500};
}}

.text-success {{
    color: {COLORS.success};
}}

.text-warning {{
    color: {COLORS.warning};
}}

.text-error {{
    color: {COLORS.error};
}}

.mb-2 {{
    margin-bottom: {SPACING.space_2};
}}

.mb-4 {{
    margin-bottom: {SPACING.space_4};
}}

.mb-6 {{
    margin-bottom: {SPACING.space_6};
}}

/* ==================== CUSTOM SCROLLBAR ==================== */

::-webkit-scrollbar {{
    width: 10px;
    height: 10px;
}}

::-webkit-scrollbar-track {{
    background: {COLORS.gray_100};
    border-radius: {RADIUS.full};
}}

::-webkit-scrollbar-thumb {{
    background: {COLORS.gray_400};
    border-radius: {RADIUS.full};
}}

::-webkit-scrollbar-thumb:hover {{
    background: {COLORS.gray_500};
}}
"""


# ============================================================================
# COMBINE ALL CSS PARTS
# ============================================================================

def get_global_css(dark_mode: bool = False) -> str:
    """
    Get complete global CSS for the app.

    Args:
        dark_mode: Use dark mode styles

    Returns:
        Complete CSS string
    """
    # For now, return light mode only
    # Dark mode to be fully implemented in UI-004
    return GLOBAL_CSS_PART1 + GLOBAL_CSS_PART2 + GLOBAL_CSS_PART3 + GLOBAL_CSS_PART4


# ============================================================================
# EXPORT PUBLIC API
# ============================================================================

__all__ = ["get_global_css"]
