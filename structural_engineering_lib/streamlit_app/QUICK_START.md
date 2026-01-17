# Quick Start: Using Error Handler & Session Manager

## 🚀 5-Minute Integration Guide

### Step 1: Import in Your Page

```python
# At top of your page file (e.g., pages/01_🏗️_beam_design.py)
from utils.error_handler import (
    validate_beam_inputs,
    display_error_message,
    display_success_message
)
from utils.session_manager import (
    SessionStateManager,
    BeamInputs,
    DesignResult
)
```

### Step 2: Initialize Session State

```python
# At the very start of your page (before any st. calls)
SessionStateManager.initialize()
```

### Step 3: Load Persisted Inputs

```python
# Get last used values (or defaults if first time)
current_inputs = SessionStateManager.get_current_inputs()

# Use as default values in your input widgets
span_mm = st.sidebar.number_input(
    "Span (mm)",
    min_value=1000,
    max_value=15000,
    value=int(current_inputs.span_mm),  # Persisted value!
    step=100
)

b_mm = st.sidebar.number_input(
    "Width (mm)",
    min_value=150,
    max_value=1000,
    value=int(current_inputs.b_mm),     # Persisted value!
    step=50
)

# ... repeat for all input fields ...
```

### Step 4: Validate Before Computing

```python
if st.sidebar.button("🔍 Analyze Design", type="primary"):
    # Validate all inputs
    errors = validate_beam_inputs(
        span_mm=span_mm,
        b_mm=b_mm,
        d_mm=d_mm,
        D_mm=D_mm,
        fck_mpa=fck_mpa,
        fy_mpa=fy_mpa,
        mu_knm=mu_knm,
        vu_kn=vu_kn
    )

    if errors:
        # Show errors and stop
        st.error(f"⛔ Found {len(errors)} validation error(s)")
        for error in errors:
            display_error_message(error)
        st.stop()  # Don't proceed!

    # All inputs valid
    display_success_message("✅ All inputs valid!")

    # Continue to step 5...
```

### Step 5: Check Cache Before Computing

```python
    # Create inputs object
    inputs = BeamInputs(
        span_mm=span_mm,
        b_mm=b_mm,
        d_mm=d_mm,
        D_mm=D_mm,
        fck_mpa=fck_mpa,
        fy_mpa=fy_mpa,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        cover_mm=cover_mm
    )

    # Check if we already computed this
    cached_result = SessionStateManager.get_cached_design(inputs)

    if cached_result:
        # Use cached result (instant!)
        st.info("⚡ Using cached result (instant)")
        result = cached_result
    else:
        # Compute design (may take 1-2 seconds)
        with st.spinner("Analyzing beam design..."):
            # YOUR EXISTING DESIGN CODE HERE
            result_dict = smart_analyze_design(
                span_mm=span_mm,
                b_mm=b_mm,
                # ... pass all parameters ...
            )

            # Convert to DesignResult object
            result = DesignResult(
                inputs=inputs,
                ast_mm2=result_dict['ast_mm2'],
                ast_provided_mm2=result_dict['ast_provided_mm2'],
                num_bars=result_dict['num_bars'],
                bar_diameter_mm=result_dict['bar_diameter_mm'],
                stirrup_diameter_mm=result_dict['stirrup_diameter_mm'],
                stirrup_spacing_mm=result_dict['stirrup_spacing_mm'],
                utilization_pct=result_dict['utilization_pct'],
                status=result_dict['status'],  # "PASS" or "FAIL"
                compliance_checks=result_dict['compliance_checks'],
                cost_per_meter=result_dict.get('cost_per_meter', 0)
            )

            # Cache for next time
            SessionStateManager.cache_design(inputs, result)

    # Continue to step 6...
```

### Step 6: Save to Session & History

```python
    # Save current inputs (for persistence across pages)
    SessionStateManager.set_current_inputs(inputs)

    # Save current result
    SessionStateManager.set_current_result(result)

    # Add to history (for "recent designs" feature)
    SessionStateManager.add_to_history(inputs, result)

    # Now display results...
```

### Step 7: Display Results

```python
    # YOUR EXISTING RESULT DISPLAY CODE
    if result.status == "PASS":
        st.success("✅ Design Successful!")

        # Display result tabs, visualizations, etc.
        tab1, tab2, tab3 = st.tabs(["Summary", "Visualization", "Compliance"])

        with tab1:
            st.write(f"**Main Steel:** {result.num_bars}-{result.bar_diameter_mm}mm bars")
            st.write(f"**Provided Area:** {result.ast_provided_mm2:.0f} mm²")
            st.write(f"**Utilization:** {result.utilization_pct:.1f}%")
            # ... more summary ...

        with tab2:
            # Show beam diagram
            fig = create_beam_diagram(result)
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            # Show compliance checks
            for check, passed in result.compliance_checks.items():
                icon = "✅" if passed else "❌"
                st.write(f"{icon} {check}")
    else:
        st.error("❌ Design Failed")
        st.write("Review errors and adjust parameters")
```

---

## 📚 Optional: Show History

Add this anywhere on your page to show recent designs:

```python
# Sidebar: Recent Designs
with st.sidebar:
    st.divider()
    st.subheader("📜 Recent Designs")

    history = SessionStateManager.get_history()
    if history:
        for i, past_result in enumerate(history[-5:], 1):  # Last 5
            with st.expander(f"Design {i}: {past_result.inputs.span_mm:.0f}mm"):
                st.write(f"Span: {past_result.inputs.span_mm:.0f} mm")
                st.write(f"Steel: {past_result.num_bars}-{past_result.bar_diameter_mm}mm")
                st.write(f"Util: {past_result.utilization_pct:.1f}%")
                st.write(f"Cost: ₹{past_result.cost_per_meter:.2f}/m")
    else:
        st.info("No designs yet")
```

---

## 🎯 That's It!

You now have:
- ✅ Input validation with user-friendly errors
- ✅ State persistence across pages
- ✅ Smart caching for instant results
- ✅ Design history tracking
- ✅ All in < 50 lines of code!

---

## 🐛 Troubleshooting

### "NameError: name 'SessionStateManager' is not defined"

**Solution:** Add import at top of file:
```python
from utils.session_manager import SessionStateManager, BeamInputs, DesignResult
```

### "ModuleNotFoundError: No module named 'utils'"

**Solution:** Make sure you're running from the `streamlit_app/` directory:
```bash
cd streamlit_app
streamlit run app.py
```

### "You can now view your Streamlit app in your browser"

This is normal startup output and includes your local and network URLs.
If you see a Watchdog performance tip, you can optionally install it:
```bash
xcode-select --install
pip install watchdog
```

### "AttributeError: 'dict' object has no attribute..."

**Solution:** Initialize session state first:
```python
SessionStateManager.initialize()
```

### Validation errors not showing

**Solution:** Make sure you're calling `display_error_message()`:
```python
for error in errors:
    display_error_message(error)  # Not just st.error()!
```

---

## 📖 More Examples

See complete examples in:
- `docs/STREAMLIT-IMPL-009-010-COMPLETE.md` - Full integration examples
- `docs/AGENT-6-HANDOFF-FINAL.md` - Usage patterns
- `tests/test_error_handler.py` - All validation scenarios
- `tests/test_session_manager.py` - All state operations

---

**Questions?** Check the documentation files or ask the MAIN agent!

**Happy Coding! 🚀**
