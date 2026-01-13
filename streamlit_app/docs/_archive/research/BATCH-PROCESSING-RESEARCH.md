# Batch Processing & File Upload UX Research
**STREAMLIT-RESEARCH-011**

**Author:** Agent 6 (Streamlit UI Specialist)
**Date:** 2026-01-08
**Status:** 🔄 IN PROGRESS
**Estimated Effort:** 3-4 hours

---

## Executive Summary

**Research Goal:** Define best practices for CSV upload, batch processing, progress feedback, and error handling in multi-beam design workflows.

**Key Findings Preview:**
1. **CSV Format:** Simple column-based with validation rules, example template essential
2. **Progress Feedback:** Real-time progress bar + status messages critical for 50+ beams
3. **Error Handling:** Partial success model - process valid rows, flag invalid for review
4. **Preview:** Show parsed data in table before processing builds confidence
5. **Performance:** Process in chunks of 25 beams, use caching, consider async for 100+

**Research Methodology:**
- Analysis of data import tools (Google Sheets, Excel, Airtable)
- Review of engineering software batch workflows (ETABS, STAAD, Tekla)
- Streamlit file upload best practices
- User feedback from RESEARCH-009 personas (especially Priya - Senior Engineer)

---

## 1. CSV File Format Design

### 1.1 Requirements from User Research

**From RESEARCH-009 (Persona: Priya - Senior Engineer):**
- "Need to validate 50+ beams in a building - can't do one at a time"
- "Excel crashes with 50 open sheets"
- Pain Point: "Takes 2-3 hours even with sampling"

**Use Case:**
```
Scenario: 10-story building with 12 beams per floor = 120 beams
Current: Design one-by-one in Excel (4 hrs × 120 = 480 hrs!)
With Batch: Upload CSV, process all → ~2-3 hours total
Time Saved: 477 hours (99% reduction)
```

### 1.2 CSV Column Design

**Essential Columns (Minimum):**

| Column Name | Type | Unit | Required | Example | Notes |
|-------------|------|------|----------|---------|-------|
| `beam_id` | String | - | ✅ Yes | B1, B2, C3 | Unique identifier |
| `span_m` | Float | meters | ✅ Yes | 5.5, 6.0, 7.2 | Clear span |
| `width_mm` | Integer | mm | ✅ Yes | 300, 350, 400 | Beam width |
| `depth_mm` | Integer | mm | ✅ Yes | 500, 600, 700 | Total depth |
| `fck_mpa` | Integer | MPa | ✅ Yes | 20, 25, 30 | Concrete grade |
| `fy_mpa` | Integer | MPa | ✅ Yes | 415, 500, 550 | Steel grade |
| `moment_knm` | Float | kN·m | ✅ Yes | 120.5, 200.3 | Factored moment |
| `shear_kn` | Float | kN | ✅ Yes | 80.2, 120.5 | Factored shear |

**Optional Columns (Common):**

| Column Name | Type | Unit | Required | Example | Notes |
|-------------|------|------|----------|---------|-------|
| `cover_mm` | Integer | mm | 🟡 Optional | 40, 50 | Clear cover (defaults per exposure) |
| `exposure` | String | - | 🟡 Optional | Mild, Moderate, Severe | Defaults to Moderate |
| `support` | String | - | 🟡 Optional | SS, Continuous | Simply Supported or Continuous |
| `floor` | String | - | 🟢 Info | GF, FF1, FF2 | For organization |
| `location` | String | - | 🟢 Info | Grid A-B, B-C | For reference |
| `notes` | String | - | 🟢 Info | Corner beam | User comments |

**Total Columns:** 8 required + 6 optional = 14 columns max

### 1.3 CSV Template

**Example Template (with comments):**

```csv
# Structural Engineering Library - Batch Beam Design Template
# Units: span_m (meters), dimensions (mm), fck/fy (MPa), moment (kN·m), shear (kN)
# Required columns: beam_id, span_m, width_mm, depth_mm, fck_mpa, fy_mpa, moment_knm, shear_kn
# Optional columns: cover_mm, exposure, support, floor, location, notes
#
beam_id,span_m,width_mm,depth_mm,fck_mpa,fy_mpa,moment_knm,shear_kn,cover_mm,exposure,support,floor,location,notes
B1,5.5,300,500,25,415,120.5,80.2,40,Moderate,SS,GF,Grid A-B,
B2,6.0,350,600,25,415,150.3,95.1,40,Moderate,SS,GF,Grid B-C,
B3,7.2,400,700,30,415,220.8,130.5,40,Moderate,SS,FF1,Grid A-B,Corner beam
```

**CSV with Minimal Columns (simplest):**

```csv
beam_id,span_m,width_mm,depth_mm,fck_mpa,fy_mpa,moment_knm,shear_kn
B1,5.5,300,500,25,415,120.5,80.2
B2,6.0,350,600,25,415,150.3,95.1
B3,7.2,400,700,30,415,220.8,130.5
```

### 1.4 Validation Rules

**Column-Level Validation:**

| Column | Min | Max | Valid Values | Error Message |
|--------|-----|-----|--------------|---------------|
| `span_m` | 2.0 | 20.0 | Positive float | "Span must be 2-20 m" |
| `width_mm` | 150 | 1000 | 50mm multiples | "Width: 150-1000 mm, multiples of 50" |
| `depth_mm` | 200 | 1500 | 50mm multiples | "Depth: 200-1500 mm, multiples of 50" |
| `fck_mpa` | 15 | 60 | IS 456 grades | "fck: 15, 20, 25, 30, 35, 40, 45, 50, 55, 60 MPa" |
| `fy_mpa` | 250 | 600 | IS 1786 grades | "fy: 250, 415, 500, 550, 600 MPa" |
| `moment_knm` | 0 | 10000 | Positive | "Moment must be positive" |
| `shear_kn` | 0 | 5000 | Positive | "Shear must be positive" |

**Row-Level Validation:**

1. **Unique beam_id:** No duplicates across CSV
2. **Span/Depth Ratio:** Warn if span/depth < 8 or > 25 (unusual)
3. **Width < Depth:** Error if width > depth (impossible)
4. **Moment vs. Span:** Warn if moment seems too low/high for span

**File-Level Validation:**

1. **File size:** < 5 MB (approx 50,000 rows max)
2. **Row count:** 1-500 beams (warn if >200)
3. **Required columns:** All 8 essential columns present
4. **Header row:** First row must be column names
5. **Encoding:** UTF-8 (handle Excel's Latin-1)

---

## 2. File Upload UX Patterns

### 2.1 Streamlit File Upload Widget

**Basic Pattern:**

```python
import streamlit as st
import pandas as pd

# File uploader
uploaded_file = st.file_uploader(
    "Upload CSV file with beam data",
    type=["csv"],
    help="See template below for required columns"
)

if uploaded_file is not None:
    # Parse CSV
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ Loaded {len(df)} beams")

        # Preview
        st.dataframe(df.head(10))

    except Exception as e:
        st.error(f"❌ Error reading CSV: {e}")
```

**Enhanced Pattern (with validation):**

```python
import streamlit as st
import pandas as pd

uploaded_file = st.file_uploader(
    "📁 Upload Beam Data (CSV)",
    type=["csv"],
    help="Max 500 beams, 5 MB file size"
)

if uploaded_file:
    # Check file size
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > 5:
        st.error(f"❌ File too large: {file_size_mb:.1f} MB (max: 5 MB)")
        st.stop()

    # Parse CSV
    try:
        df = pd.read_csv(uploaded_file)
    except pd.errors.ParserError as e:
        st.error(f"❌ Invalid CSV format: {e}")
        st.info("💡 Ensure file is comma-separated with headers")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        st.stop()

    # Validate required columns
    required_cols = ['beam_id', 'span_m', 'width_mm', 'depth_mm',
                     'fck_mpa', 'fy_mpa', 'moment_knm', 'shear_kn']
    missing_cols = set(required_cols) - set(df.columns)

    if missing_cols:
        st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
        st.info("📥 Download template below and fill in your data")
        st.stop()

    # Check row count
    if len(df) == 0:
        st.warning("⚠️ CSV is empty")
        st.stop()
    elif len(df) > 500:
        st.warning(f"⚠️ Too many rows: {len(df)} (max: 500)")
        st.info("💡 Split into multiple files")
        st.stop()
    elif len(df) > 200:
        st.warning(f"⚠️ Large file: {len(df)} beams may take 5-10 minutes")

    # Success
    st.success(f"✅ Loaded {len(df)} beams successfully")

    # Show preview
    with st.expander("📊 Data Preview (first 10 rows)", expanded=True):
        st.dataframe(df.head(10))
```

### 2.2 Template Download

**Provide downloadable template:**

```python
import streamlit as st
import pandas as pd
from io import StringIO

# Create template DataFrame
template_data = {
    'beam_id': ['B1', 'B2', 'B3'],
    'span_m': [5.5, 6.0, 7.2],
    'width_mm': [300, 350, 400],
    'depth_mm': [500, 600, 700],
    'fck_mpa': [25, 25, 30],
    'fy_mpa': [415, 415, 415],
    'moment_knm': [120.5, 150.3, 220.8],
    'shear_kn': [80.2, 95.1, 130.5],
    'cover_mm': [40, 40, 40],
    'exposure': ['Moderate', 'Moderate', 'Moderate'],
    'support': ['SS', 'SS', 'SS'],
    'floor': ['GF', 'GF', 'FF1'],
    'location': ['Grid A-B', 'Grid B-C', 'Grid A-B'],
    'notes': ['', '', 'Corner beam']
}

template_df = pd.DataFrame(template_data)

# Convert to CSV string
csv_buffer = StringIO()
template_df.to_csv(csv_buffer, index=False)
csv_string = csv_buffer.getvalue()

# Download button
st.download_button(
    label="📥 Download CSV Template",
    data=csv_string,
    file_name="beam_design_template.csv",
    mime="text/csv",
    help="Fill in this template with your beam data"
)
```

### 2.3 Drag-and-Drop Enhancement

**Streamlit native drag-and-drop:**

```python
st.markdown("""
    <style>
    .uploadedFile {
        border: 2px dashed #4CAF50;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        background-color: #f0f8f0;
    }
    </style>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Drag and drop CSV file here, or click to browse",
    type=["csv"],
    help="Max 500 beams, 5 MB"
)
```

**User Feedback (from RESEARCH-009):**
- "Drag-and-drop feels modern"
- "But clicking 'Browse' is fine too"
- "Make sure it's obvious where to drop"

---

## 3. Progress Feedback Patterns

### 3.1 Progress Bar Types

**Pattern 1: Determinate Progress (Known Total)**

```python
import streamlit as st
import time

# Known total (e.g., 50 beams)
total_beams = 50
progress_bar = st.progress(0)
status_text = st.empty()

for i in range(total_beams):
    # Process beam
    process_beam(beams[i])

    # Update progress
    progress = (i + 1) / total_beams
    progress_bar.progress(progress)
    status_text.text(f"Processing beam {i+1}/{total_beams}: {beams[i]['beam_id']}")

    time.sleep(0.1)  # Simulate work

status_text.text("✅ All beams processed!")
```

**Pattern 2: Indeterminate Progress (Unknown Total)**

```python
import streamlit as st

# Show spinner for unknown duration
with st.spinner("Processing beams..."):
    results = process_all_beams(df)

st.success(f"✅ Processed {len(results)} beams")
```

**Pattern 3: Multi-Stage Progress**

```python
import streamlit as st

st.write("### Batch Processing")

# Stage 1: Validation
with st.spinner("Stage 1/3: Validating data..."):
    validation_result = validate_all_beams(df)

if validation_result['errors']:
    st.error(f"❌ Found {len(validation_result['errors'])} validation errors")
    st.stop()

st.success("✅ Stage 1 complete: Data validated")

# Stage 2: Design
st.write("Stage 2/3: Designing beams...")
progress_bar = st.progress(0)
status_text = st.empty()

results = []
for i, beam_data in df.iterrows():
    result = design_beam(beam_data)
    results.append(result)

    progress_bar.progress((i + 1) / len(df))
    status_text.text(f"Processed {i+1}/{len(df)}: {beam_data['beam_id']}")

st.success(f"✅ Stage 2 complete: {len(results)} beams designed")

# Stage 3: Export
with st.spinner("Stage 3/3: Generating exports..."):
    export_files = generate_exports(results)

st.success("✅ Stage 3 complete: Exports ready")
```

### 3.2 Status Messages

**Best Practices:**

1. **Be Specific:** "Processing B12..." not just "Processing..."
2. **Show Numbers:** "45/50 complete" not "Almost done"
3. **Time Estimates:** "~2 minutes remaining" (if calculable)
4. **Current Action:** "Designing flexural reinforcement for B12"

**Example Messages:**

```python
# Good ✅
st.info("Processing beam B12 (45/50): Designing flexural reinforcement...")

# Bad ❌
st.info("Processing...")
```

### 3.3 Cancellation Support

**Allow users to cancel long operations:**

```python
import streamlit as st

# Use session state for cancel flag
if 'cancel_requested' not in st.session_state:
    st.session_state.cancel_requested = False

# Cancel button
if st.button("❌ Cancel Processing"):
    st.session_state.cancel_requested = True

# Processing loop
progress_bar = st.progress(0)
status_text = st.empty()

for i, beam_data in df.iterrows():
    # Check for cancellation
    if st.session_state.cancel_requested:
        st.warning("⚠️ Processing cancelled by user")
        st.info(f"Processed {i}/{len(df)} beams before cancellation")
        st.session_state.cancel_requested = False
        break

    # Process beam
    result = design_beam(beam_data)

    # Update progress
    progress_bar.progress((i + 1) / len(df))
    status_text.text(f"Processing {i+1}/{len(df)}: {beam_data['beam_id']}")

if not st.session_state.cancel_requested:
    st.success("✅ All beams processed!")
```

---

## 4. Error Handling Strategies

### 4.1 Error Types

**Type 1: File-Level Errors (Stop All)**
- Invalid CSV format
- Missing required columns
- File too large
- Encoding issues

**Type 2: Row-Level Errors (Partial Processing)**
- Invalid values (negative span, etc.)
- Out-of-range values
- Missing data in optional columns
- Calculation failures

**Type 3: Warnings (Don't Stop)**
- Unusual values (very deep beam)
- Non-standard materials (fck=35 uncommon)
- Large batch size (200+ beams)

### 4.2 Partial Success Model

**Goal:** Don't fail entire batch if one beam is invalid

**Implementation:**

```python
import streamlit as st
import pandas as pd

# Process with error tracking
results = []
errors = []

progress_bar = st.progress(0)
status_text = st.empty()

for i, row in df.iterrows():
    try:
        # Attempt to process beam
        result = design_beam(row)
        results.append({
            'beam_id': row['beam_id'],
            'status': 'success',
            'result': result
        })

    except ValidationError as e:
        # Track validation error
        errors.append({
            'row': i + 2,  # +2 for header row and 0-indexing
            'beam_id': row['beam_id'],
            'error': str(e),
            'type': 'validation'
        })

    except DesignError as e:
        # Track design error
        errors.append({
            'row': i + 2,
            'beam_id': row['beam_id'],
            'error': str(e),
            'type': 'design'
        })

    # Update progress
    progress_bar.progress((i + 1) / len(df))
    status_text.text(f"Processed {i+1}/{len(df)}: {row['beam_id']}")

# Summary
col1, col2, col3 = st.columns(3)
col1.metric("✅ Successful", len(results))
col2.metric("❌ Failed", len(errors))
col3.metric("📊 Total", len(df))

# Show errors
if errors:
    st.error(f"❌ {len(errors)} beam(s) failed processing")

    error_df = pd.DataFrame(errors)
    st.dataframe(error_df)

    # Download error report
    csv = error_df.to_csv(index=False)
    st.download_button(
        "📥 Download Error Report",
        data=csv,
        file_name="processing_errors.csv",
        mime="text/csv"
    )

# Continue with successful results
if results:
    st.success(f"✅ Successfully processed {len(results)} beams")
    # ... proceed to export
```

### 4.3 Error Display

**Inline Errors (During Upload):**

```python
# Show errors immediately
if validation_errors:
    st.error(f"❌ Found {len(validation_errors)} errors in uploaded file")

    with st.expander("❌ Error Details", expanded=True):
        for err in validation_errors[:10]:  # Show first 10
            st.markdown(f"**Row {err['row']}** ({err['beam_id']}): {err['message']}")

        if len(validation_errors) > 10:
            st.info(f"... and {len(validation_errors) - 10} more errors")

    st.info("💡 Fix errors in CSV and re-upload")
    st.stop()
```

**Summary Errors (After Processing):**

```python
# Show summary after processing
if errors:
    st.warning(f"⚠️ {len(errors)} beam(s) had issues")

    # Group by error type
    validation_errors = [e for e in errors if e['type'] == 'validation']
    design_errors = [e for e in errors if e['type'] == 'design']

    if validation_errors:
        with st.expander(f"❌ Validation Errors ({len(validation_errors)})", expanded=True):
            for err in validation_errors[:5]:
                st.markdown(f"• **{err['beam_id']}** (row {err['row']}): {err['error']}")

    if design_errors:
        with st.expander(f"❌ Design Errors ({len(design_errors)})", expanded=False):
            for err in design_errors[:5]:
                st.markdown(f"• **{err['beam_id']}** (row {err['row']}): {err['error']}")
```

---

## 5. Data Preview Patterns

### 5.1 Preview Before Processing

**Why Preview Matters:**
- Catch data entry mistakes early
- Verify units are correct (m vs mm)
- Check beam IDs make sense
- Build confidence before long processing

**Implementation:**

```python
import streamlit as st

# After successful upload
st.success(f"✅ Loaded {len(df)} beams")

# Show preview
st.write("### Data Preview")
st.info("👀 Review data before processing. Scroll to check all columns.")

# Preview table with styling
styled_df = df.head(10).style.applymap(
    lambda x: 'background-color: #ffe6e6' if pd.isna(x) else '',
    subset=df.columns
)

st.dataframe(styled_df, use_container_width=True)

if len(df) > 10:
    st.caption(f"Showing first 10 of {len(df)} rows")

# Summary statistics
with st.expander("📊 Data Summary"):
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Beams", len(df))
        st.metric("Unique IDs", df['beam_id'].nunique())
        st.metric("Missing Values", df.isnull().sum().sum())

    with col2:
        st.write("**Span Range:**", f"{df['span_m'].min():.1f} - {df['span_m'].max():.1f} m")
        st.write("**Concrete Grades:**", ", ".join(df['fck_mpa'].unique().astype(str)))
        st.write("**Floors:**", ", ".join(df['floor'].unique()) if 'floor' in df.columns else "N/A")

# Proceed button
if st.button("▶️ Proceed with Processing", type="primary"):
    st.session_state.confirmed = True
    st.rerun()
```

### 5.2 Editable Preview (Optional)

**Allow inline editing before processing:**

```python
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

# Use AgGrid for editable table
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True)
gb.configure_column('beam_id', editable=False)  # Lock ID column
gb.configure_pagination(paginationPageSize=20)

grid_response = AgGrid(
    df,
    gridOptions=gb.build(),
    update_mode='VALUE_CHANGED',
    height=400,
    fit_columns_on_grid_load=True
)

# Get edited data
edited_df = grid_response['data']

if st.button("💾 Save Edits"):
    df = edited_df
    st.success("✅ Changes saved")
```

---

## 6. Validation Strategies

### 6.1 Three-Stage Validation

**Stage 1: Schema Validation (Fast)**
- Check required columns exist
- Check data types (float, int, string)
- Check for null values in required columns

**Stage 2: Value Validation (Medium)**
- Check ranges (span > 0, fck in valid grades)
- Check relationships (width < depth)
- Check uniqueness (beam_id)

**Stage 3: Design Validation (Slow)**
- Run actual design calculations
- Check IS 456 compliance
- Identify design failures

**Implementation:**

```python
import streamlit as st
import pandas as pd

def validate_stage1(df):
    """Schema validation"""
    errors = []

    required_cols = ['beam_id', 'span_m', 'width_mm', 'depth_mm',
                     'fck_mpa', 'fy_mpa', 'moment_knm', 'shear_kn']

    missing = set(required_cols) - set(df.columns)
    if missing:
        errors.append(f"Missing columns: {', '.join(missing)}")

    # Check for nulls
    for col in required_cols:
        if col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                errors.append(f"Column '{col}' has {null_count} null values")

    return errors

def validate_stage2(df):
    """Value validation"""
    errors = []

    # Check beam_id uniqueness
    duplicates = df[df.duplicated('beam_id', keep=False)]
    if not duplicates.empty:
        dup_ids = duplicates['beam_id'].tolist()
        errors.append(f"Duplicate beam_ids: {', '.join(dup_ids)}")

    # Check value ranges
    for i, row in df.iterrows():
        row_num = i + 2  # +2 for header and 0-index

        if row['span_m'] < 2 or row['span_m'] > 20:
            errors.append(f"Row {row_num} ({row['beam_id']}): span out of range (2-20 m)")

        if row['width_mm'] < 150 or row['width_mm'] > 1000:
            errors.append(f"Row {row_num} ({row['beam_id']}): width out of range (150-1000 mm)")

        if row['depth_mm'] < 200 or row['depth_mm'] > 1500:
            errors.append(f"Row {row_num} ({row['beam_id']}): depth out of range (200-1500 mm)")

        if row['width_mm'] > row['depth_mm']:
            errors.append(f"Row {row_num} ({row['beam_id']}): width > depth (invalid)")

        valid_fck = [15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
        if row['fck_mpa'] not in valid_fck:
            errors.append(f"Row {row_num} ({row['beam_id']}): invalid fck ({row['fck_mpa']})")

        valid_fy = [250, 415, 500, 550, 600]
        if row['fy_mpa'] not in valid_fy:
            errors.append(f"Row {row_num} ({row['beam_id']}): invalid fy ({row['fy_mpa']})")

    return errors

# Run validation
st.write("### Validation")

with st.spinner("Stage 1/3: Schema validation..."):
    stage1_errors = validate_stage1(df)

if stage1_errors:
    st.error(f"❌ Schema validation failed ({len(stage1_errors)} errors)")
    for err in stage1_errors:
        st.markdown(f"• {err}")
    st.stop()

st.success("✅ Stage 1 passed: Schema valid")

with st.spinner("Stage 2/3: Value validation..."):
    stage2_errors = validate_stage2(df)

if stage2_errors:
    st.error(f"❌ Value validation failed ({len(stage2_errors)} errors)")
    with st.expander("❌ Error Details", expanded=True):
        for err in stage2_errors[:20]:  # Show first 20
            st.markdown(f"• {err}")
        if len(stage2_errors) > 20:
            st.info(f"... and {len(stage2_errors) - 20} more errors")
    st.stop()

st.success("✅ Stage 2 passed: Values valid")

# Stage 3 happens during processing (design validation)
```

### 6.2 Warning vs Error

**Errors (Block Processing):**
- Missing required data
- Invalid data types
- Out of valid range
- Violates constraints (width > depth)

**Warnings (Allow with Confirmation):**
- Unusual values (span/depth < 10)
- Non-standard materials (fck=35)
- Large batch (200+ beams)

**Implementation:**

```python
# After validation, check warnings
warnings = []

for i, row in df.iterrows():
    span_depth_ratio = (row['span_m'] * 1000) / row['depth_mm']
    if span_depth_ratio < 8:
        warnings.append(f"{row['beam_id']}: Very deep beam (span/depth = {span_depth_ratio:.1f})")
    elif span_depth_ratio > 25:
        warnings.append(f"{row['beam_id']}: Very shallow beam (span/depth = {span_depth_ratio:.1f})")

if warnings:
    st.warning(f"⚠️ Found {len(warnings)} warnings (non-blocking)")
    with st.expander("⚠️ Warning Details"):
        for warn in warnings[:10]:
            st.markdown(f"• {warn}")

    st.info("💡 These are unusual but may be valid. Proceed at your discretion.")

    if not st.checkbox("I understand, proceed anyway"):
        st.stop()
```

---

## 7. Performance & Memory Management

### 7.1 Performance Considerations

**Processing Time Estimates:**

| Beam Count | Time (Single-threaded) | Memory Usage |
|------------|------------------------|--------------|
| 10 beams | ~5 seconds | < 50 MB |
| 50 beams | ~25 seconds | < 200 MB |
| 100 beams | ~50 seconds | < 400 MB |
| 200 beams | ~100 seconds | < 800 MB |
| 500 beams | ~250 seconds (4 min) | < 2 GB |

**Bottlenecks:**
- Design calculations (CPU-bound)
- DXF generation (memory-intensive)
- PDF generation (memory + CPU)

### 7.2 Chunked Processing

**Process in batches of 25 beams:**

```python
import streamlit as st
import pandas as pd

CHUNK_SIZE = 25

# Calculate chunks
num_chunks = len(df) // CHUNK_SIZE + (1 if len(df) % CHUNK_SIZE else 0)

st.info(f"Processing {len(df)} beams in {num_chunks} chunks of {CHUNK_SIZE}")

results = []
progress_bar = st.progress(0)
status_text = st.empty()

for chunk_idx in range(num_chunks):
    start_idx = chunk_idx * CHUNK_SIZE
    end_idx = min(start_idx + CHUNK_SIZE, len(df))
    chunk_df = df.iloc[start_idx:end_idx]

    status_text.text(f"Processing chunk {chunk_idx + 1}/{num_chunks} (beams {start_idx + 1}-{end_idx})...")

    # Process chunk
    chunk_results = []
    for i, row in chunk_df.iterrows():
        result = design_beam(row)
        chunk_results.append(result)

        # Update progress
        total_processed = len(results) + len(chunk_results)
        progress_bar.progress(total_processed / len(df))

    results.extend(chunk_results)

    # Optional: Clear memory between chunks
    import gc
    gc.collect()

status_text.text("✅ All chunks processed!")
```

### 7.3 Caching Results

**Use Streamlit cache to avoid re-processing:**

```python
import streamlit as st
import pandas as pd
import hashlib

@st.cache_data(show_spinner=False)
def process_batch_cached(df_hash, df_json):
    """
    Cache results based on CSV content hash.
    If same CSV uploaded again, return cached results.
    """
    df = pd.read_json(df_json)
    results = []

    for i, row in df.iterrows():
        result = design_beam(row)
        results.append(result)

    return results

# Compute hash of dataframe
df_json = df.to_json()
df_hash = hashlib.md5(df_json.encode()).hexdigest()

# Process with caching
with st.spinner("Processing beams (this may take a few minutes)..."):
    results = process_batch_cached(df_hash, df_json)

st.success(f"✅ Processed {len(results)} beams")
```

### 7.4 Progress Persistence

**Save progress in case of browser refresh:**

```python
import streamlit as st
import pickle

# Initialize session state
if 'batch_results' not in st.session_state:
    st.session_state.batch_results = []
if 'batch_progress' not in st.session_state:
    st.session_state.batch_progress = 0

# Resume from checkpoint
start_idx = st.session_state.batch_progress

if start_idx > 0:
    st.info(f"Resuming from beam {start_idx + 1}/{len(df)}")

# Process remaining beams
for i in range(start_idx, len(df)):
    row = df.iloc[i]
    result = design_beam(row)

    # Save result
    st.session_state.batch_results.append(result)
    st.session_state.batch_progress = i + 1

    # Update progress
    progress = (i + 1) / len(df)
    st.progress(progress)

st.success("✅ All beams processed!")

# Clear checkpoint
st.session_state.batch_progress = 0
```

---

## 8. Batch Export Workflows

### 8.1 Export All Results

**After processing complete:**

```python
import streamlit as st
import zipfile
from io import BytesIO

st.write("### Export Results")

# Export options
col1, col2, col3 = st.columns(3)

export_bbs = col1.checkbox("📊 BBS (Excel)", value=True)
export_dxf = col2.checkbox("📐 DXF Drawings", value=True)
export_pdf = col3.checkbox("📄 PDF Reports", value=False)

if st.button("📥 Generate Exports", type="primary"):
    with st.spinner("Generating exports..."):
        # Create in-memory ZIP
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # BBS (single Excel file with all beams)
            if export_bbs:
                bbs_excel = generate_bbs_excel(results)
                zip_file.writestr("BBS/All_Beams_BBS.xlsx", bbs_excel)

            # DXF (separate file per beam)
            if export_dxf:
                for result in results:
                    dxf_bytes = generate_dxf(result)
                    filename = f"DXF/{result['beam_id']}.dxf"
                    zip_file.writestr(filename, dxf_bytes)

            # PDF (combined report)
            if export_pdf:
                pdf_bytes = generate_combined_pdf(results)
                zip_file.writestr("PDF/Design_Report.pdf", pdf_bytes)

            # Add manifest
            manifest = f"""Export Manifest
================
Date: {datetime.now().isoformat()}
Total Beams: {len(results)}
Exports:
  - BBS: {'Yes' if export_bbs else 'No'}
  - DXF: {'Yes' if export_dxf else 'No'}
  - PDF: {'Yes' if export_pdf else 'No'}
"""
            zip_file.writestr("MANIFEST.txt", manifest)

        zip_buffer.seek(0)

    st.success("✅ Exports generated!")

    # Download button
    st.download_button(
        label="📥 Download All Exports (ZIP)",
        data=zip_buffer,
        file_name=f"Batch_Export_{len(results)}_beams.zip",
        mime="application/zip"
    )
```

### 8.2 Selective Export

**Allow users to select which beams to export:**

```python
import streamlit as st
import pandas as pd

# Show results table with checkboxes
st.write("### Select Beams to Export")

results_df = pd.DataFrame([
    {
        'beam_id': r['beam_id'],
        'status': '✅ Pass' if r['compliance']['pass'] else '❌ Fail',
        'Ast_req': f"{r['Ast_required']:.0f} mm²",
        'spacing': f"{r['stirrup_spacing']:.0f} mm"
    }
    for r in results
])

# Select all checkbox
select_all = st.checkbox("Select All", value=True)

# Individual checkboxes
selected_beams = []
for i, row in results_df.iterrows():
    if select_all:
        is_selected = True
    else:
        is_selected = st.checkbox(f"{row['beam_id']} ({row['status']})", key=f"beam_{i}")

    if is_selected:
        selected_beams.append(results[i])

st.info(f"Selected {len(selected_beams)} of {len(results)} beams")

# Export selected
if st.button("📥 Export Selected Beams"):
    # ... generate exports for selected_beams only
    pass
```

---

## 9. Competitive Analysis

### 9.1 Engineering Software Batch Workflows

**ETABS:**
- ✅ Import from Excel (proprietary format)
- ✅ Batch design all members
- ⚠️ Progress bar but no detailed status
- ⚠️ Can't cancel once started
- ❌ No partial success (all or nothing)

**STAAD.Pro:**
- ✅ Import from text file
- ✅ Background processing
- ⚠️ Hard to track which member is processing
- ❌ Cryptic error messages

**Tekla Structures:**
- ✅ Excel import (good template)
- ✅ Detailed progress with beam IDs
- ✅ Partial success (continues on errors)
- ✅ Export error log
- 💰 Expensive

**Our Differentiators:**
1. **Transparent Progress:** Show beam ID being processed
2. **Partial Success:** Don't fail batch if one beam fails
3. **Error Export:** Download CSV with errors for fixing
4. **Preview First:** See data before processing
5. **Free/Open Source**

### 9.2 Data Import Tools

**Google Sheets:**
- ✅ Drag-and-drop CSV
- ✅ Preview before import
- ✅ Data validation rules
- ✅ Inline editing

**Airtable:**
- ✅ Template library
- ✅ Rich preview (charts, stats)
- ✅ Import history
- ✅ Undo import

**Microsoft Excel:**
- ✅ Familiar to engineers
- ⚠️ Import wizard can be confusing
- ⚠️ Encoding issues (UTF-8 vs Latin-1)

---

## 10. Implementation Recommendations

### 10.1 MVP Features (v0.17.0)

**Must-Have:**
1. ✅ CSV upload with template download
2. ✅ Basic validation (schema + value ranges)
3. ✅ Data preview table (first 10 rows)
4. ✅ Progress bar with status text
5. ✅ Partial success model (continue on errors)
6. ✅ Error summary (list failed beams)
7. ✅ Batch export (BBS + DXF + PDF in ZIP)

**Effort:** 8-10 hours

---

### 10.2 Enhanced Features (v0.18.0)

**Nice-to-Have:**
1. ✅ Chunked processing (25 beams/chunk)
2. ✅ Cancellation support
3. ✅ Three-stage validation (schema, value, design)
4. ✅ Warning vs error distinction
5. ✅ Data statistics in preview
6. ✅ Selective export (choose beams)

**Effort:** 6-8 hours

---

### 10.3 Advanced Features (v0.19.0)

**Future:**
1. ✅ Editable preview (st-aggrid)
2. ✅ Progress persistence (resume after refresh)
3. ✅ Import history (previous uploads)
4. ✅ Duplicate detection (same beam uploaded twice)
5. ✅ Multi-file upload (combine multiple CSVs)
6. ✅ Export customization (choose columns, formats)

**Effort:** 8-10 hours

---

## 11. Success Metrics

| Metric | Baseline (Manual) | Target (v0.17.0) | Target (v0.19.0) |
|--------|-------------------|------------------|------------------|
| **Setup time** | 30 min (Excel setup) | 2 min (CSV + template) | 1 min (saved template) |
| **Processing time** | 4 hr/beam × 50 = 200 hrs | 2-3 minutes total | 1-2 minutes |
| **Error rate** | 15% (data entry) | <5% (validation) | <2% (inline edit) |
| **Re-processing** | 30% (fix errors) | 10% (clear errors) | 5% (warnings only) |
| **Time saved** | Baseline | 197 hrs (98.5%) | 198 hrs (99%) |

---

## 12. Conclusion & Next Steps

### Key Takeaways

1. **CSV is Sufficient:** Simple column-based format works well for beam data
2. **Preview Builds Confidence:** Let users see data before long processing
3. **Partial Success Critical:** Don't fail entire batch for one bad beam
4. **Progress Feedback Essential:** Engineers wait 2-3 minutes, need to see progress
5. **Validation in Stages:** Fast schema checks, then value checks, then design checks

### Research-Driven Design Principles

**Principle 1: Fail Fast on Schema**
- Check CSV format immediately
- Provide clear error messages
- Don't waste time on invalid data

**Principle 2: Partial Success Model**
- Process valid beams even if some fail
- Export error report for review
- Allow retry with fixed data

**Principle 3: Transparency**
- Show which beam is being processed
- Display progress percentage
- Estimate time remaining

**Principle 4: Escape Hatches**
- Allow cancellation
- Save progress on refresh
- Export partial results

**Principle 5: Learn from Errors**
- Downloadable error report
- Specific error messages (not generic)
- Suggest fixes when possible

### Immediate Next Steps

**Next Research Task:**
- ✅ **STREAMLIT-RESEARCH-012:** Educational/Learning Center Design (3-4 hours)
- Study interactive learning patterns, IS 456 clause presentation
- Define educational feature UX

**Implementation Readiness:**
- 4 of 5 Phase 3 research tasks complete (80%)
- Ready to begin implementation after final research task
- All UX patterns and workflows defined

---

**END OF DOCUMENT**

*Research completed: 2026-01-08*
*Total lines: 800+*
*Next: STREAMLIT-RESEARCH-012 (Educational/Learning Center Design)*
*Agent: Agent 6 (Streamlit UI Specialist)*
