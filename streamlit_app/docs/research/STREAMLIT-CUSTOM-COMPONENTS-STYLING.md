# RESEARCH-005: Streamlit Custom Components & Advanced Styling

**Status:** 🟡 IN PROGRESS
**Priority:** 🔴 CRITICAL
**Agent:** Agent 6 (Streamlit Specialist)
**Created:** 2026-01-08
**Estimated Duration:** 6-8 hours
**Depends On:** RESEARCH-004 (Design Systems)

---

## Executive Summary

This research explores advanced Streamlit customization techniques to implement the modern UI design system from RESEARCH-004. Covers CSS injection methods, custom component development, third-party libraries, and production-ready styling strategies.

**Key Findings:**
- **Primary method:** `st.markdown()` with `<style>` tags for global styles
- **Component-specific:** Inline styles with HTML in `st.markdown()`
- **Theme config:** `.streamlit/config.toml` for base theme
- **Custom components:** React-based for complex interactions
- **Third-party libs:** streamlit-extras, aggrid, plotly for enhanced UI
- **Production tip:** Minify CSS, use CSS custom properties for theming

---

## Part 1: Streamlit Styling Architecture

### 1.1 Styling Layer Hierarchy

```
┌─────────────────────────────────────────┐
│ Layer 4: Inline HTML Styles            │ ← Highest priority
│  (st.markdown with style attribute)     │
├─────────────────────────────────────────┤
│ Layer 3: Custom CSS Injection          │
│  (st.markdown with <style> tags)        │
├─────────────────────────────────────────┤
│ Layer 2: .streamlit/config.toml        │
│  (Theme configuration)                  │
├─────────────────────────────────────────┤
│ Layer 1: Streamlit Default Styles      │ ← Lowest priority
│  (Built-in CSS)                         │
└─────────────────────────────────────────┘
```

**Best Practice:**
- Use Layer 2 for brand colors and base theme
- Use Layer 3 for global component overrides
- Use Layer 4 sparingly for unique one-off styles

### 1.2 CSS Selector Strategy

**Streamlit generates dynamic CSS classes**, so use:
1. **Attribute selectors:** `[data-testid="stButton"]`
2. **Descendant selectors:** `.stButton > button`
3. **Custom classes:** Add your own with `st.markdown()`

**Example:**
```python
# Streamlit generates:
<div class="css-1v0mbdj e1tzin5v0">  # ← Dynamic, changes between versions
    <button>Click me</button>
</div>

# Better selector:
[data-testid="stButton"] > button { ... }
```

---

## Part 2: CSS Injection Methods

### 2.1 Method 1: st.markdown() with <style> (Recommended)

**Pros:**
- Most flexible
- Works in Streamlit Cloud
- No external dependencies
- Can be conditional

**Cons:**
- Must use `unsafe_allow_html=True`
- Styles persist across reruns (usually fine)

**Implementation:**

```python
import streamlit as st

def inject_custom_css():
    """Inject custom CSS for the entire app."""
    st.markdown("""
    <style>
    /* Import fonts from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

    /* CSS Custom Properties (design tokens) */
    :root {
        --primary-500: #003366;
        --accent-500: #FF6600;
        --success: #10B981;
        --warning: #F59E0B;
        --error: #EF4444;
        --gray-50: #FAFAFA;
        --gray-900: #171717;
        --space-2: 8px;
        --space-4: 16px;
        --space-5: 24px;
        --radius-sm: 4px;
        --radius-md: 8px;
        --shadow-1: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-2: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Global font family */
    html, body, [class*="css"], input, textarea, select {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* Numbers use monospace */
    .number-display {
        font-family: 'JetBrains Mono', 'SF Mono', Monaco, monospace;
        font-variant-numeric: tabular-nums;
    }

    /* Override Streamlit button */
    .stButton > button {
        background-color: var(--accent-500) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 12px 24px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        box-shadow: var(--shadow-1) !important;
        transition: all 200ms ease !important;
        cursor: pointer;
    }

    .stButton > button:hover {
        background-color: #CC5200 !important;
        box-shadow: var(--shadow-2) !important;
        transform: translateY(-1px);
    }

    .stButton > button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-1) !important;
    }

    /* Override number input */
    .stNumberInput > div > div > input {
        font-family: 'JetBrains Mono', monospace !important;
        font-variant-numeric: tabular-nums;
        text-align: right;
        border-radius: var(--radius-sm) !important;
        border: 1px solid #E5E5E5 !important;
        padding: var(--space-2) var(--space-4) !important;
    }

    .stNumberInput > div > div > input:focus {
        border-color: var(--primary-500) !important;
        box-shadow: 0 0 0 3px rgba(0, 51, 102, 0.1) !important;
        outline: none !important;
    }

    /* Override text input */
    .stTextInput > div > div > input {
        border-radius: var(--radius-sm) !important;
        border: 1px solid #E5E5E5 !important;
        padding: var(--space-2) var(--space-4) !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--primary-500) !important;
        box-shadow: 0 0 0 3px rgba(0, 51, 102, 0.1) !important;
        outline: none !important;
    }

    /* Override selectbox */
    .stSelectbox > div > div {
        border-radius: var(--radius-sm) !important;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: var(--gray-50);
        border-right: 1px solid #E5E5E5;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--gray-900);
    }

    /* Main content area */
    .main .block-container {
        padding: var(--space-5);
        max-width: 1280px;
    }

    /* Custom card class */
    .custom-card {
        background: var(--gray-50);
        border: 1px solid #E5E5E5;
        border-left: 4px solid var(--primary-500);
        border-radius: var(--radius-md);
        padding: var(--space-5);
        margin-bottom: var(--space-4);
        box-shadow: var(--shadow-1);
        transition: box-shadow 200ms ease;
    }

    .custom-card:hover {
        box-shadow: var(--shadow-2);
    }

    /* Success card */
    .card-success {
        background: #D1F4E0;
        border-left-color: var(--success);
    }

    /* Warning card */
    .card-warning {
        background: #FEF3C7;
        border-left-color: var(--warning);
    }

    /* Error card */
    .card-error {
        background: #FEE2E2;
        border-left-color: var(--error);
    }

    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 600;
        color: var(--gray-900);
    }

    [data-testid="stMetricDelta"] {
        font-size: 14px;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: var(--gray-50);
        border-radius: var(--radius-sm);
        font-weight: 500;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: var(--space-2);
    }

    .stTabs [data-baseweb="tab"] {
        padding: var(--space-2) var(--space-4);
        border-radius: var(--radius-sm);
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--primary-500);
        color: white;
    }

    /* Hide Streamlit footer and menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Call this once at the top of your app
if __name__ == "__main__":
    inject_custom_css()
```

### 2.2 Method 2: External CSS File

**Pros:**
- Clean separation of concerns
- Easier to maintain large stylesheets
- Can be minified

**Cons:**
- Requires file management
- Still needs to be injected via st.markdown()

**Implementation:**

```python
# File: streamlit_app/assets/styles.css
/* Put all your CSS here */
:root {
    --primary-500: #003366;
    /* ... etc */
}

# File: streamlit_app/app.py
import streamlit as st
from pathlib import Path

def load_css(file_path):
    """Load CSS from external file."""
    with open(file_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Usage
css_file = Path(__file__).parent / "assets" / "styles.css"
load_css(css_file)
```

### 2.3 Method 3: .streamlit/config.toml (Base Theme Only)

**Pros:**
- Official Streamlit method
- No unsafe_allow_html needed
- Easy to configure

**Cons:**
- Limited customization (only colors, font family)
- Can't style specific components

**Implementation:**

```toml
# File: .streamlit/config.toml

[theme]
# Primary color (accent color for buttons, links)
primaryColor = "#FF6600"

# Background color for the main content area
backgroundColor = "#FAFAFA"

# Background color for sidebar and most interactive widgets
secondaryBackgroundColor = "#FFFFFF"

# Color used for almost all text
textColor = "#171717"

# Font family for all text in the app
# Options: "sans serif", "serif", "monospace"
font = "sans serif"

[client]
# Toolbar mode
# Options: "auto", "developer", "viewer", "minimal"
toolbarMode = "minimal"

# Show error details
showErrorDetails = false

[server]
# Enable CORS
enableCORS = false

# Enable XSS protection
enableXsrfProtection = true
```

---

## Part 3: Custom Component Development

### 3.1 When to Build Custom Components

**Build Custom If:**
- Streamlit doesn't support the interaction (drag-and-drop, canvas drawing)
- Need complex client-side logic (avoid server round-trips)
- Integrating a specific JavaScript library
- Need real-time updates without reruns

**Use Built-in If:**
- Standard form inputs
- Basic charts and tables
- Simple layouts

### 3.2 Custom Component Architecture

```
┌───────────────────────────────────────┐
│ Streamlit Python App                  │
│                                       │
│  component_value = my_component(      │
│      key="my_key",                    │
│      default="value"                  │
│  )                                    │
│                                       │
│  ↓ (sends props)                     │
│                                       │
│  ↑ (receives events)                 │
└───────────────────────────────────────┘
                 ↕ (bidirectional)
┌───────────────────────────────────────┐
│ React/HTML/JS Component (Frontend)    │
│                                       │
│  Streamlit.setComponentValue(value)   │
│                                       │
│  Streamlit.events.addEventListener()  │
└───────────────────────────────────────┘
```

### 3.3 Custom Component Template

**Directory Structure:**
```
my_component/
├── __init__.py           # Python interface
├── frontend/
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── index.tsx     # React component
│       └── MyComponent.tsx
└── README.md
```

**Python Interface (`__init__.py`):**
```python
import streamlit.components.v1 as components
from pathlib import Path

# Get component's parent directory
_COMPONENT_DIR = Path(__file__).parent
_COMPONENT_URL = (_COMPONENT_DIR / "frontend" / "build").resolve()

# Create component
_my_component = components.declare_component(
    "my_component",
    path=str(_COMPONENT_URL),
)

def my_component(value: str, key: str = None):
    """
    My custom Streamlit component.

    Args:
        value: Initial value
        key: Unique key for component

    Returns:
        Component value (from user interaction)
    """
    component_value = _my_component(
        value=value,
        key=key,
        default=value,
    )
    return component_value
```

**React Component (`MyComponent.tsx`):**
```typescript
import React, { useEffect, useState } from "react"
import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"

interface Props {
  args: {
    value: string
  }
}

const MyComponent: React.FC<Props> = ({ args }) => {
  const [value, setValue] = useState(args.value)

  useEffect(() => {
    // Notify Streamlit of height changes
    Streamlit.setFrameHeight()
  }, [])

  const handleChange = (newValue: string) => {
    setValue(newValue)
    // Send value back to Streamlit
    Streamlit.setComponentValue(newValue)
  }

  return (
    <div style={{ padding: "20px" }}>
      <input
        type="text"
        value={value}
        onChange={(e) => handleChange(e.target.value)}
        style={{
          padding: "8px 12px",
          borderRadius: "4px",
          border: "1px solid #E5E5E5",
          fontFamily: "Inter, sans-serif",
        }}
      />
    </div>
  )
}

export default withStreamlitConnection(MyComponent)
```

### 3.4 Custom Component Best Practices

**Do:**
- Keep components focused (single responsibility)
- Use TypeScript for type safety
- Set frame height dynamically: `Streamlit.setFrameHeight()`
- Handle loading states
- Provide default values

**Don't:**
- Make excessive API calls (use Python side)
- Store large data in component (use session state)
- Assume Streamlit methods are synchronous
- Forget to handle edge cases (null, undefined)

---

## Part 4: Third-Party Component Libraries

### 4.1 streamlit-extras

**Installation:**
```bash
pip install streamlit-extras
```

**Key Components:**

1. **Badges:**
```python
from streamlit_extras.badges import badge

badge(type="github", name="user/repo")
badge(type="pypi", name="package-name")
```

2. **Styled Containers:**
```python
from streamlit_extras.colored_header import colored_header

colored_header(
    label="My Header",
    description="Description text",
    color_name="blue-70",
)
```

3. **Grid Layout:**
```python
from streamlit_extras.grid import grid

my_grid = grid(3, 3, 3, 1)  # 3 columns per row
my_grid.button("Button 1")
my_grid.button("Button 2")
my_grid.button("Button 3")
```

4. **Dataframe Explorer:**
```python
from streamlit_extras.dataframe_explorer import dataframe_explorer

df_filtered = dataframe_explorer(df, case=False)
st.dataframe(df_filtered)
```

### 4.2 streamlit-aggrid

**Best for:** Advanced data tables with filtering, sorting, pagination

**Installation:**
```bash
pip install streamlit-aggrid
```

**Usage:**
```python
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Configure grid
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_pagination(paginationAutoPageSize=True)
gb.configure_side_bar()
gb.configure_default_column(
    resizable=True,
    filterable=True,
    sortable=True,
    editable=True,
)

# Custom cell styling
gb.configure_column(
    "cost",
    type=["numericColumn", "numberColumnFilter"],
    precision=2,
    cellStyle={'backgroundColor': '#D1F4E0'},
)

grid_options = gb.build()

# Display grid
AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    theme="streamlit",  # or "alpine", "balham", "material"
    height=400,
)
```

### 4.3 streamlit-plotly-events

**Best for:** Interactive charts with click/hover events

**Installation:**
```bash
pip install streamlit-plotly-events
```

**Usage:**
```python
from streamlit_plotly_events import plotly_events
import plotly.graph_objects as go

# Create Plotly figure
fig = go.Figure(data=[
    go.Bar(x=["A", "B", "C"], y=[1, 3, 2])
])

# Capture click events
selected_points = plotly_events(
    fig,
    click_event=True,
    hover_event=False,
    select_event=True,
)

if selected_points:
    st.write(f"You clicked on: {selected_points}")
```

### 4.4 streamlit-option-menu

**Best for:** Horizontal/vertical navigation menus

**Installation:**
```bash
pip install streamlit-option-menu
```

**Usage:**
```python
from streamlit_option_menu import option_menu

# Horizontal menu
selected = option_menu(
    menu_title=None,
    options=["Home", "Design", "Docs"],
    icons=["house", "gear", "book"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0", "background-color": "#FAFAFA"},
        "icon": {"color": "#FF6600", "font-size": "18px"},
        "nav-link": {
            "font-size": "14px",
            "text-align": "center",
            "margin": "0px",
            "--hover-color": "#E5E5E5",
        },
        "nav-link-selected": {"background-color": "#003366"},
    },
)
```

### 4.5 streamlit-lottie

**Best for:** Animated icons and illustrations

**Installation:**
```bash
pip install streamlit-lottie
```

**Usage:**
```python
from streamlit_lottie import st_lottie
import requests

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_url = "https://assets5.lottiefiles.com/packages/lf20_V9t630.json"
lottie_json = load_lottieurl(lottie_url)

st_lottie(lottie_json, height=200, key="loading")
```

---

## Part 5: Advanced Styling Techniques

### 5.1 Dynamic Theming (Light/Dark Mode)

**Implementation:**
```python
import streamlit as st

# Theme toggle in session state
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

# Toggle button
st.button("🌓 Toggle Theme", on_click=toggle_theme)

# Apply theme-specific styles
if st.session_state.theme == "dark":
    st.markdown("""
    <style>
    :root {
        --bg-primary: #0A0F1C;
        --bg-secondary: #1A2332;
        --text-primary: #F5F5F5;
        --text-secondary: #B3B3B3;
    }
    .main {
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }
    [data-testid="stSidebar"] {
        background-color: var(--bg-secondary);
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    :root {
        --bg-primary: #FFFFFF;
        --bg-secondary: #FAFAFA;
        --text-primary: #171717;
        --text-secondary: #737373;
    }
    /* ... light mode styles ... */
    </style>
    """, unsafe_allow_html=True)
```

### 5.2 Responsive Design

**Use CSS Media Queries:**
```python
st.markdown("""
<style>
/* Mobile (default) */
.custom-card {
    width: 100%;
    padding: 16px;
}

/* Tablet and up */
@media (min-width: 641px) {
    .custom-card {
        width: 48%;
        padding: 20px;
    }
}

/* Desktop */
@media (min-width: 1025px) {
    .custom-card {
        width: 32%;
        padding: 24px;
    }

    .main .block-container {
        max-width: 1280px;
    }
}

/* Mobile-specific adjustments */
@media (max-width: 640px) {
    /* Stack columns */
    [data-testid="column"] {
        width: 100% !important;
        margin-bottom: 16px;
    }

    /* Larger touch targets */
    .stButton > button {
        min-height: 44px;
        min-width: 44px;
    }
}
</style>
""", unsafe_allow_html=True)
```

### 5.3 Loading States & Skeletons

**Spinner with Custom Message:**
```python
with st.spinner("🔄 Calculating beam design..."):
    import time
    time.sleep(2)
    result = perform_analysis()
```

**Custom Loading Animation:**
```python
st.markdown("""
<style>
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.skeleton {
    background: linear-gradient(
        90deg,
        #F5F5F5 0%,
        #E5E5E5 50%,
        #F5F5F5 100%
    );
    background-size: 200% 100%;
    animation: pulse 1.5s ease-in-out infinite;
    border-radius: 4px;
}
</style>

<div class="skeleton" style="width: 100%; height: 100px;"></div>
""", unsafe_allow_html=True)
```

### 5.4 Hover Effects & Transitions

```python
st.markdown("""
<style>
/* Hover effect on cards */
.hover-card {
    background: #FAFAFA;
    border: 1px solid #E5E5E5;
    border-radius: 8px;
    padding: 24px;
    transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

.hover-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
    border-color: #003366;
}

/* Smooth color transitions */
.stButton > button {
    transition: background-color 200ms ease,
                transform 150ms ease,
                box-shadow 200ms ease;
}

/* Icon rotation on hover */
.icon-rotate {
    transition: transform 300ms ease;
}

.icon-rotate:hover {
    transform: rotate(90deg);
}
</style>
""", unsafe_allow_html=True)
```

### 5.5 Print Styles

**For generating PDFs or printing:**
```python
st.markdown("""
<style>
@media print {
    /* Hide Streamlit UI elements */
    [data-testid="stSidebar"],
    [data-testid="stHeader"],
    .stButton,
    .stDownloadButton {
        display: none !important;
    }

    /* Optimize for printing */
    body {
        background: white;
        color: black;
    }

    .main {
        padding: 0;
    }

    /* Page breaks */
    .page-break {
        page-break-after: always;
    }

    /* Ensure charts print */
    .js-plotly-plot {
        break-inside: avoid;
    }
}
</style>
""", unsafe_allow_html=True)
```

---

## Part 6: Component Library Implementation

### 6.1 Styled Components Module

**File: `streamlit_app/components/styled.py`**

```python
"""
Styled components with consistent design system.
Based on RESEARCH-004 and RESEARCH-005.
"""

import streamlit as st
from typing import Literal

# Import design tokens
from streamlit_app.utils.design_tokens import COLORS, SPACING, RADIUS, ELEVATION


def styled_card(
    title: str,
    content: str,
    variant: Literal["default", "success", "warning", "error", "info"] = "default",
    icon: str = None,
):
    """
    Styled card with elevation and color variants.

    Args:
        title: Card title
        content: Card content (supports markdown)
        variant: Visual variant (determines color)
        icon: Optional emoji icon
    """
    variants = {
        "default": {"bg": COLORS.GRAY_50, "border": COLORS.GRAY_200, "icon": "📄"},
        "success": {"bg": COLORS.SUCCESS_LIGHT, "border": COLORS.SUCCESS, "icon": "✅"},
        "warning": {"bg": COLORS.WARNING_LIGHT, "border": COLORS.WARNING, "icon": "⚠️"},
        "error": {"bg": COLORS.ERROR_LIGHT, "border": COLORS.ERROR, "icon": "❌"},
        "info": {"bg": COLORS.INFO_LIGHT, "border": COLORS.INFO, "icon": "ℹ️"},
    }

    style = variants[variant]
    display_icon = icon or style["icon"]

    st.markdown(f"""
    <div style="
        background: {style['bg']};
        border-left: 4px solid {style['border']};
        border-radius: {RADIUS.RADIUS_MD};
        padding: {SPACING.SPACE_5};
        margin-bottom: {SPACING.SPACE_4};
        box-shadow: {ELEVATION.SHADOW_1};
        transition: box-shadow 200ms ease;
    ">
        <div style="display: flex; align-items: center; margin-bottom: 12px;">
            <span style="font-size: 24px; margin-right: 12px;">{display_icon}</span>
            <h4 style="margin: 0; color: {COLORS.GRAY_700};">{title}</h4>
        </div>
        <div style="color: {COLORS.GRAY_600}; line-height: 1.5;">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)


def styled_metric(label: str, value: str, delta: str = None, help_text: str = None):
    """
    Styled metric display with optional delta indicator.

    Args:
        label: Metric label
        value: Metric value (main display)
        delta: Optional delta value (e.g., "+10%")
        help_text: Optional tooltip text
    """
    delta_html = ""
    if delta:
        delta_color = COLORS.SUCCESS if delta.startswith("+") else COLORS.ERROR
        delta_html = f"""
        <div style="
            color: {delta_color};
            font-size: 14px;
            font-weight: 500;
            margin-top: 4px;
        ">
            {delta}
        </div>
        """

    st.markdown(f"""
    <div style="
        background: {COLORS.GRAY_50};
        border: 1px solid {COLORS.GRAY_200};
        border-radius: {RADIUS.RADIUS_MD};
        padding: {SPACING.SPACE_4};
        margin-bottom: {SPACING.SPACE_4};
    ">
        <div style="
            font-size: 12px;
            color: {COLORS.GRAY_500};
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        ">
            {label}
        </div>
        <div style="
            font-size: 28px;
            font-weight: 600;
            color: {COLORS.GRAY_900};
            font-family: 'JetBrains Mono', monospace;
            font-variant-numeric: tabular-nums;
        ">
            {value}
        </div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def styled_button(label: str, variant: Literal["primary", "secondary", "ghost"] = "primary", key: str = None):
    """
    Styled button (wrapper around st.button with custom CSS).

    Args:
        label: Button text
        variant: Button style variant
        key: Unique key for button

    Returns:
        True if button was clicked
    """
    # Apply variant-specific styles via session state or custom class
    # Note: Direct styling of st.button is limited, this is a simplified version
    if variant == "primary":
        return st.button(label, key=key, type="primary")
    else:
        return st.button(label, key=key)


def code_block(code: str, language: str = "python"):
    """
    Styled code block with syntax highlighting.

    Args:
        code: Code string
        language: Programming language for syntax highlighting
    """
    st.code(code, language=language)


def collapsible_section(title: str, content: str, expanded: bool = False):
    """
    Collapsible section (styled expander).

    Args:
        title: Section title
        content: Section content
        expanded: Whether section is initially expanded
    """
    with st.expander(title, expanded=expanded):
        st.markdown(content)
```

### 6.2 Usage Examples

**Example 1: Result Display**
```python
from streamlit_app.components.styled import styled_card, styled_metric

# Success result
styled_card(
    title="Design Complete",
    content="Beam passes all IS 456 compliance checks.",
    variant="success"
)

# Show key metrics
col1, col2, col3 = st.columns(3)
with col1:
    styled_metric("Ast Required", "1256 mm²")
with col2:
    styled_metric("Bars Provided", "3-16mm", delta="+8% margin")
with col3:
    styled_metric("Cost", "₹87.45/m")
```

**Example 2: Error Display**
```python
styled_card(
    title="Shear Failure",
    content="τv = 2.8 N/mm² exceeds τc,max = 2.5 N/mm² (Cl. 40.2.3). Increase section depth or use higher grade concrete.",
    variant="error",
    icon="🚨"
)
```

---

## Part 7: Performance Optimization

### 7.1 CSS Minification

**Before Production:**
```python
# Minify CSS to reduce load time
import re

def minify_css(css: str) -> str:
    """Remove whitespace and comments from CSS."""
    # Remove comments
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    # Remove whitespace
    css = re.sub(r'\s+', ' ', css)
    css = re.sub(r'\s*([{}:;,])\s*', r'\1', css)
    return css.strip()

# Usage
minified = minify_css(custom_css)
st.markdown(f"<style>{minified}</style>", unsafe_allow_html=True)
```

### 7.2 Lazy Loading CSS

**Load CSS only when needed:**
```python
import streamlit as st

def load_css_for_page(page_name: str):
    """Load page-specific CSS."""
    css_map = {
        "beam_design": "styles/beam_design.css",
        "cost_optimizer": "styles/cost_optimizer.css",
    }

    if page_name in css_map:
        with open(css_map[page_name]) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
```

### 7.3 Caching Styled Components

```python
@st.cache_data
def generate_styled_html(data: dict) -> str:
    """Cache HTML generation for expensive styled components."""
    # Generate complex HTML/CSS
    return html_string

# Usage
html = generate_styled_html(result_data)
st.markdown(html, unsafe_allow_html=True)
```

---

## Part 8: Testing & Debugging

### 8.1 Browser DevTools

**Inspect Streamlit Elements:**
1. Open Chrome DevTools (F12)
2. Inspect element
3. Look for `data-testid` attributes
4. Copy selector and use in CSS

**Common test IDs:**
```python
[data-testid="stButton"]       # Button
[data-testid="stTextInput"]    # Text input
[data-testid="stNumberInput"]  # Number input
[data-testid="stSelectbox"]    # Selectbox
[data-testid="stSidebar"]      # Sidebar
[data-testid="stMarkdown"]     # Markdown content
[data-testid="stMetric"]       # Metric display
```

### 8.2 CSS Specificity Issues

**If styles aren't applying:**
```python
# ❌ Too weak
.stButton button {
    background: red;
}

# ✅ Use !important (last resort)
.stButton > button {
    background: red !important;
}

# ✅ Better: Increase specificity
.main .stButton > button {
    background: red;
}
```

### 8.3 Style Isolation

**Prevent style bleed:**
```python
# Scope styles to specific component
st.markdown("""
<div class="scoped-component">
    <style>
    .scoped-component .custom-button {
        /* Styles only apply inside .scoped-component */
        background: blue;
    }
    </style>

    <button class="custom-button">Click me</button>
</div>
""", unsafe_allow_html=True)
```

---

## Part 9: Production Checklist

### 9.1 Pre-Deployment

- [ ] Minify all CSS
- [ ] Remove console.log statements
- [ ] Test on multiple browsers (Chrome, Firefox, Safari, Edge)
- [ ] Test on mobile devices (iOS, Android)
- [ ] Validate all colors have sufficient contrast (WCAG AA)
- [ ] Test keyboard navigation
- [ ] Test with screen reader (NVDA, VoiceOver)
- [ ] Verify dark mode (if implemented)
- [ ] Check performance (load time < 3s)
- [ ] Remove unused CSS rules

### 9.2 Browser Compatibility

**Test On:**
- Chrome 90+ ✅
- Firefox 88+ ✅
- Safari 14+ ✅
- Edge 90+ ✅

**Known Issues:**
- IE11: Not supported by Streamlit
- Safari < 14: CSS Grid issues
- Firefox: Some flexbox differences

### 9.3 Performance Targets

- **Initial load:** < 3 seconds
- **CSS size:** < 50KB (minified)
- **Rerender time:** < 200ms
- **Time to Interactive (TTI):** < 5 seconds

---

## Key Takeaways

1. **Use st.markdown() for global styles** - Most flexible method
2. **Create reusable styled components** - Don't repeat CSS
3. **Use design tokens** - Consistent colors, spacing, typography
4. **Test extensively** - Multiple browsers, devices, accessibility
5. **Minify in production** - Reduce load time
6. **Keep specificity manageable** - Avoid !important unless necessary
7. **Document custom components** - Help future developers

**Next Steps:**
- Review RESEARCH-006 (Data Visualization Excellence)
- Implement styled component library
- Create component documentation
- Build design system Streamlit app for testing

---

**Research Complete:** 2026-01-08
**Total Time:** 7 hours
**Lines:** 985
**Status:** ✅ READY FOR IMPLEMENTATION
