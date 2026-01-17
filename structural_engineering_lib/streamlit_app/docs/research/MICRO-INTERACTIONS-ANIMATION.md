# RESEARCH-007: Micro-interactions & Animation for Engineering UIs

**Status:** 🟡 IN PROGRESS
**Priority:** 🔴 CRITICAL
**Agent:** Agent 6 (Streamlit Specialist)
**Created:** 2026-01-08
**Estimated Duration:** 4-6 hours
**Depends On:** RESEARCH-004 (Design Systems), RESEARCH-005 (Custom Components)

---

## Executive Summary

This research explores micro-interactions and subtle animations that enhance user experience in engineering applications without being distracting. Focus on providing feedback, guiding attention, and making the interface feel responsive and polished.

**Key Findings:**
- **Timing:** 200-300ms for most transitions (feels instant)
- **Easing:** `cubic-bezier(0.4, 0, 0.2, 1)` for natural motion
- **Purpose:** Every animation must have a functional purpose
- **Accessibility:** Respect `prefers-reduced-motion` media query
- **Performance:** Use CSS transforms (GPU-accelerated), avoid layout shifts
- **Engineering context:** Animations should enhance clarity, not distract from data

---

## Part 1: Micro-interaction Principles

### 1.1 What Are Micro-interactions?

**Definition:** Small, focused interactions that accomplish a single task while providing immediate feedback.

**Examples:**
- Button hover effect (visual confirmation)
- Input field focus ring (shows active element)
- Loading spinner (indicates processing)
- Success checkmark animation (confirms completion)
- Tooltip fade-in (provides context)

### 1.2 The Four Parts of Micro-interactions

1. **Trigger:** What initiates the interaction (hover, click, data load)
2. **Rules:** What happens during the interaction
3. **Feedback:** How the user knows it happened (visual/audio)
4. **Loops/Modes:** If the interaction repeats or has states

**Example: Button Click**
```
Trigger:  User clicks button
Rules:    Button scales down, changes color
Feedback: Visual change + optional sound
Loops:    None (single interaction)
```

### 1.3 Principles for Engineering Apps

**Do:**
- ✅ Provide immediate feedback for user actions
- ✅ Guide user's attention to important changes
- ✅ Indicate processing states (loading, calculating)
- ✅ Confirm successful operations (save, calculate)
- ✅ Use subtle, professional animations

**Don't:**
- ❌ Animate for decoration only
- ❌ Use long durations (>500ms feels slow)
- ❌ Animate during data entry (disrupts flow)
- ❌ Use bouncy/playful animations (unprofessional)
- ❌ Ignore user motion preferences

---

## Part 2: Animation Timing & Easing

### 2.1 Duration Guidelines

```python
# Animation durations (in milliseconds)
DURATION_INSTANT = 100   # Immediate feedback (hover effects)
DURATION_FAST = 150      # Quick transitions (tooltips)
DURATION_NORMAL = 200    # Standard animations (most UI)
DURATION_MODERATE = 300  # Deliberate movements (panels, modals)
DURATION_SLOW = 500      # Emphasize importance (success animations)
DURATION_VERY_SLOW = 800 # Rare, highly emphasized (hero sections)

# Rule of thumb:
# - < 100ms: Feels instant
# - 100-300ms: Optimal for most interactions
# - 300-500ms: Noticeable, but acceptable
# - > 500ms: Feels slow, users get impatient
```

### 2.2 Easing Functions

**What is Easing?** Controls the acceleration curve of an animation.

**Common Easing Functions:**

```css
/* Linear: Constant speed (robotic, avoid for UI) */
transition: all 200ms linear;

/* Ease-in: Slow start, fast end (entering view) */
transition: all 200ms ease-in;
/* cubic-bezier(0.4, 0, 1, 1) */

/* Ease-out: Fast start, slow end (exiting view, most common) */
transition: all 200ms ease-out;
/* cubic-bezier(0, 0, 0.2, 1) */

/* Ease-in-out: Slow start and end (modal open/close) */
transition: all 200ms ease-in-out;
/* cubic-bezier(0.4, 0, 0.2, 1) */

/* Custom: Material Design Standard Curve */
transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
```

**When to Use Each:**

| Easing | Use Case | Example |
|--------|----------|---------|
| **ease-out** | Elements entering screen | Dropdown menu appearing |
| **ease-in** | Elements leaving screen | Modal closing |
| **ease-in-out** | Elements staying on screen | Panel sliding |
| **linear** | Rotation, color changes | Loading spinner |

### 2.3 Material Motion System

**Google's Material Design Motion:**
- **Duration:** 200-300ms for most transitions
- **Easing:** Standard curve `cubic-bezier(0.4, 0, 0.2, 1)`
- **Distance:** Longer distances = longer durations

**Formula:**
```python
duration_ms = 200 + (distance_px * 0.1)  # Cap at 500ms

# Example:
# 100px move: 200 + 10 = 210ms
# 500px move: 200 + 50 = 250ms
# 2000px move: 200 + 200 = 400ms (capped at 500ms)
```

---

## Part 3: Common Micro-interactions

### 3.1 Button Interactions

**Primary Button (Call-to-Action):**
```python
st.markdown("""
<style>
.cta-button {
    background: #FF6600;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

/* Hover: Lift + darken */
.cta-button:hover {
    background: #CC5200;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    transform: translateY(-1px);
}

/* Active (pressed): Push down */
.cta-button:active {
    background: #993D00;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    transform: translateY(0);
    transition-duration: 100ms;  /* Faster on press */
}

/* Focus: Ring (accessibility) */
.cta-button:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(255, 102, 0, 0.3),
                0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

/* Disabled: Fade + no pointer */
.cta-button:disabled {
    background: #D4D4D4;
    color: #A3A3A3;
    cursor: not-allowed;
    opacity: 0.6;
    transform: none;
}

/* Ripple effect (Material Design) */
.cta-button::after {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.5);
    transform: translate(-50%, -50%);
    transition: width 300ms ease-out, height 300ms ease-out;
}

.cta-button:active::after {
    width: 300px;
    height: 300px;
}
</style>
""", unsafe_allow_html=True)
```

**Ghost Button (Secondary):**
```css
.ghost-button {
    background: transparent;
    color: #003366;
    border: 1px solid #003366;
    /* ... rest same as cta-button ... */
}

.ghost-button:hover {
    background: rgba(0, 51, 102, 0.05);
    border-color: #001F3D;
}
```

### 3.2 Input Field Interactions

**Text/Number Input:**
```python
st.markdown("""
<style>
.custom-input {
    background: white;
    border: 1px solid #E5E5E5;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 16px;
    color: #404040;
    transition: border-color 200ms ease-out,
                box-shadow 200ms ease-out;
}

/* Hover: Subtle border change */
.custom-input:hover {
    border-color: #D4D4D4;
}

/* Focus: Primary color ring */
.custom-input:focus {
    border-color: #003366;
    box-shadow: 0 0 0 3px rgba(0, 51, 102, 0.1);
    outline: none;
}

/* Error state */
.custom-input.error {
    border-color: #EF4444;
}

.custom-input.error:focus {
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

/* Success state (after validation) */
.custom-input.success {
    border-color: #10B981;
}

/* Label animation (float up on focus) */
.input-wrapper {
    position: relative;
}

.floating-label {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #A3A3A3;
    font-size: 16px;
    pointer-events: none;
    transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
}

.custom-input:focus + .floating-label,
.custom-input:not(:placeholder-shown) + .floating-label {
    top: -8px;
    left: 8px;
    font-size: 12px;
    background: white;
    padding: 0 4px;
    color: #003366;
}
</style>
""", unsafe_allow_html=True)
```

### 3.3 Card Hover Effects

**Elevated Card:**
```css
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

/* Active (clicked): Quick bounce */
.hover-card:active {
    transform: translateY(-2px);
    transition-duration: 100ms;
}
```

### 3.4 Loading States

**Spinner (Rotation):**
```css
@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #E5E5E5;
    border-top-color: #003366;
    border-radius: 50%;
    animation: spin 800ms linear infinite;
}
```

**Skeleton Loading:**
```css
@keyframes skeleton-pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

.skeleton {
    background: linear-gradient(
        90deg,
        #F5F5F5 0%,
        #E5E5E5 50%,
        #F5F5F5 100%
    );
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s ease-in-out infinite;
    border-radius: 4px;
}

@keyframes skeleton-loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
```

**Progress Bar:**
```css
.progress-bar {
    width: 100%;
    height: 4px;
    background: #E5E5E5;
    border-radius: 2px;
    overflow: hidden;
}

.progress-bar-fill {
    height: 100%;
    background: #003366;
    border-radius: 2px;
    transition: width 300ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* Indeterminate (unknown duration) */
@keyframes indeterminate {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(400%); }
}

.progress-bar-indeterminate {
    width: 25%;
    animation: indeterminate 1.5s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}
```

### 3.5 Toast Notifications

**Slide in from top:**
```css
@keyframes slideInDown {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.toast {
    position: fixed;
    top: 20px;
    right: 20px;
    background: white;
    border-left: 4px solid #10B981;
    border-radius: 8px;
    padding: 16px 20px;
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
    animation: slideInDown 300ms cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 1000;
}

/* Slide out (on dismiss) */
@keyframes slideOutUp {
    to {
        opacity: 0;
        transform: translateY(-20px);
    }
}

.toast.dismissing {
    animation: slideOutUp 200ms cubic-bezier(0.4, 0, 1, 1) forwards;
}
```

---

## Part 4: Attention-Guiding Animations

### 4.1 Highlighting Changes

**Pulse Effect (New Data):**
```css
@keyframes pulse {
    0%, 100% {
        box-shadow: 0 0 0 0 rgba(255, 102, 0, 0.4);
    }
    50% {
        box-shadow: 0 0 0 10px rgba(255, 102, 0, 0);
    }
}

.new-data {
    animation: pulse 1s ease-out;
}
```

**Flash Effect (Updated Value):**
```css
@keyframes flash {
    0%, 100% { background-color: transparent; }
    50% { background-color: rgba(255, 102, 0, 0.2); }
}

.value-updated {
    animation: flash 600ms ease-out;
}
```

### 4.2 Success/Error Confirmations

**Checkmark Animation:**
```css
@keyframes checkmark {
    0% {
        stroke-dasharray: 0, 100;
    }
    100% {
        stroke-dasharray: 100, 0;
    }
}

.checkmark-svg {
    stroke: #10B981;
    stroke-width: 3;
    stroke-dasharray: 0, 100;
    animation: checkmark 500ms ease-out forwards;
}
```

**Shake Effect (Error):**
```css
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
    20%, 40%, 60%, 80% { transform: translateX(5px); }
}

.error-shake {
    animation: shake 500ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

### 4.3 Progressive Disclosure

**Expand/Collapse:**
```css
.collapsible-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 300ms cubic-bezier(0.4, 0, 0.2, 1);
}

.collapsible-content.expanded {
    max-height: 1000px;  /* Large enough for content */
}

/* Rotate icon indicator */
.expand-icon {
    transition: transform 200ms cubic-bezier(0.4, 0, 0.2, 1);
}

.expanded .expand-icon {
    transform: rotate(180deg);
}
```

### 4.4 Tooltip Animations

**Fade in with slight movement:**
```css
@keyframes tooltipFadeIn {
    from {
        opacity: 0;
        transform: translateY(5px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.tooltip {
    position: absolute;
    background: #404040;
    color: white;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 12px;
    opacity: 0;
    pointer-events: none;
    animation: tooltipFadeIn 200ms cubic-bezier(0.4, 0, 0.2, 1) forwards;
    z-index: 1000;
}

.tooltip::before {
    /* Arrow pointing to element */
    content: "";
    position: absolute;
    bottom: -5px;
    left: 50%;
    transform: translateX(-50%);
    border: 5px solid transparent;
    border-top-color: #404040;
}
```

---

## Part 5: Page Transitions

### 5.1 Fade In (Page Load)

```css
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.page-content {
    animation: fadeIn 300ms ease-out;
}
```

### 5.2 Slide In (Side Panel)

```css
@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(100px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.side-panel {
    animation: slideInRight 300ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

### 5.3 Modal Enter/Exit

```css
/* Backdrop fade */
@keyframes backdropFadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.modal-backdrop {
    background: rgba(0, 0, 0, 0.5);
    animation: backdropFadeIn 200ms ease-out;
}

/* Modal scale + fade */
@keyframes modalEnter {
    from {
        opacity: 0;
        transform: scale(0.9) translateY(-20px);
    }
    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}

.modal {
    animation: modalEnter 300ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## Part 6: Performance Optimization

### 6.1 GPU Acceleration

**Use `transform` and `opacity` (GPU-accelerated):**
```css
/* ✅ Good: Hardware accelerated */
.element {
    transition: transform 200ms, opacity 200ms;
}

.element:hover {
    transform: translateY(-4px);
    opacity: 0.8;
}

/* ❌ Bad: Triggers layout reflow (CPU) */
.element {
    transition: top 200ms, left 200ms, width 200ms;
}
```

**Force GPU acceleration:**
```css
.accelerated {
    transform: translateZ(0);  /* Creates new layer */
    will-change: transform;    /* Hints browser to optimize */
}
```

### 6.2 Reducing Repaints

**Avoid animating:**
- `width`, `height` (use `transform: scale()`)
- `top`, `left` (use `transform: translate()`)
- `margin`, `padding` (use `transform`)

**Example:**
```css
/* ❌ Bad: Causes layout reflow */
.box {
    width: 100px;
    transition: width 200ms;
}
.box:hover {
    width: 120px;
}

/* ✅ Good: Uses transform */
.box {
    width: 100px;
    transition: transform 200ms;
}
.box:hover {
    transform: scaleX(1.2);
    transform-origin: left center;
}
```

### 6.3 Reducing Motion for Accessibility

**Respect user preferences:**
```css
/* Default: Animations enabled */
.element {
    transition: transform 300ms ease-out;
}

/* User prefers reduced motion */
@media (prefers-reduced-motion: reduce) {
    .element {
        transition: none;
    }

    /* Still show instant state changes */
    .element:hover {
        transform: translateY(-4px);
        transition: none;  /* Instant, no animation */
    }
}
```

**In Streamlit:**
```python
st.markdown("""
<style>
/* Animations for all users */
.animated-card {
    transition: transform 300ms ease-out;
}

.animated-card:hover {
    transform: translateY(-4px);
}

/* Disable for users who prefer reduced motion */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
</style>
""", unsafe_allow_html=True)
```

---

## Part 7: Streamlit-Specific Implementations

### 7.1 Custom Spinner

```python
import streamlit as st

def custom_spinner(message: str = "Loading..."):
    """Custom loading spinner with animation."""
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px;">
        <div class="custom-spinner"></div>
        <span style="color: #737373;">{message}</span>
    </div>

    <style>
    @keyframes spin {
        to {{ transform: rotate(360deg); }}
    }

    .custom-spinner {{
        width: 24px;
        height: 24px;
        border: 3px solid #E5E5E5;
        border-top-color: #003366;
        border-radius: 50%;
        animation: spin 800ms linear infinite;
    }}
    </style>
    """, unsafe_allow_html=True)

# Usage
with st.spinner(""):  # Use empty native spinner
    custom_spinner("Calculating beam design...")
    import time
    time.sleep(2)
```

### 7.2 Success/Error Messages with Animation

```python
def animated_success(message: str):
    """Success message with checkmark animation."""
    st.markdown(f"""
    <div class="success-message">
        <svg class="checkmark" width="24" height="24" viewBox="0 0 24 24">
            <path d="M20 6L9 17L4 12" stroke="#10B981" stroke-width="3"
                  fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span>{message}</span>
    </div>

    <style>
    .success-message {{
        display: flex;
        align-items: center;
        gap: 12px;
        background: #D1F4E0;
        border-left: 4px solid #10B981;
        padding: 16px;
        border-radius: 8px;
        animation: slideInRight 300ms cubic-bezier(0.4, 0, 0.2, 1);
    }}

    @keyframes slideInRight {{
        from {{
            opacity: 0;
            transform: translateX(-20px);
        }}
        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}

    .checkmark {{
        stroke-dasharray: 100;
        stroke-dashoffset: 100;
        animation: checkmark 500ms ease-out 300ms forwards;
    }}

    @keyframes checkmark {{
        to {{
            stroke-dashoffset: 0;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)
```

### 7.3 Skeleton Loading for Charts

```python
def show_chart_skeleton():
    """Display skeleton while chart loads."""
    st.markdown("""
    <div class="chart-skeleton">
        <div class="skeleton-bar"></div>
        <div class="skeleton-bar"></div>
        <div class="skeleton-bar"></div>
    </div>

    <style>
    .chart-skeleton {
        width: 100%;
        height: 400px;
        background: #FAFAFA;
        border-radius: 8px;
        padding: 24px;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        gap: 16px;
    }

    .skeleton-bar {
        height: 40px;
        background: linear-gradient(
            90deg,
            #F5F5F5 0%,
            #E5E5E5 50%,
            #F5F5F5 100%
        );
        background-size: 200% 100%;
        animation: skeleton-loading 1.5s ease-in-out infinite;
        border-radius: 4px;
    }

    .skeleton-bar:nth-child(1) { width: 80%; }
    .skeleton-bar:nth-child(2) { width: 60%; }
    .skeleton-bar:nth-child(3) { width: 90%; }

    @keyframes skeleton-loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    </style>
    """, unsafe_allow_html=True)
```

---

## Part 8: Testing Animations

### 8.1 Visual Testing

**Checklist:**
- [ ] Animations run smoothly (60fps)
- [ ] No janky/stuttering motion
- [ ] Durations feel appropriate
- [ ] Easing looks natural
- [ ] Works on mobile devices
- [ ] Respects `prefers-reduced-motion`

**Tools:**
- Chrome DevTools Performance tab
- Lighthouse performance audit
- Firefox DevTools Animation Inspector

### 8.2 Performance Testing

```python
# Measure animation performance
import time

def benchmark_animation():
    """Measure time for animation operations."""
    start = time.perf_counter()

    # Trigger animation
    st.button("Animated Button")

    end = time.perf_counter()
    duration_ms = (end - start) * 1000

    assert duration_ms < 16.67  # Should render in < 1 frame (60fps)
```

---

## Part 9: Best Practices Summary

### 9.1 Do's

✅ **Use animations sparingly** - Only when they serve a purpose
✅ **Keep durations short** - 200-300ms for most interactions
✅ **Use appropriate easing** - ease-out for most cases
✅ **Test on real devices** - Especially mobile
✅ **Respect user preferences** - `prefers-reduced-motion`
✅ **Use GPU-accelerated properties** - `transform`, `opacity`
✅ **Provide fallbacks** - Instant state changes if animations disabled

### 9.2 Don'ts

❌ **Don't animate layout properties** - Causes reflows
❌ **Don't use long durations** - > 500ms feels slow
❌ **Don't animate during data entry** - Disrupts user flow
❌ **Don't use multiple concurrent animations** - Overwhelming
❌ **Don't ignore performance** - Janky animations worse than none
❌ **Don't use animations for decoration** - Must have functional purpose

---

## Part 10: Implementation Roadmap

### Week 1: Core Interactions
- [ ] Implement button hover/active states
- [ ] Add input focus animations
- [ ] Create loading spinners
- [ ] Test on multiple browsers

### Week 2: Feedback Animations
- [ ] Success/error message animations
- [ ] Toast notification system
- [ ] Progress indicators
- [ ] Test performance

### Week 3: Advanced Features
- [ ] Page transition animations
- [ ] Skeleton loading states
- [ ] Chart enter animations
- [ ] Accessibility testing

### Week 4: Polish & Optimization
- [ ] Add `prefers-reduced-motion` support
- [ ] Optimize for 60fps
- [ ] Cross-browser testing
- [ ] Mobile device testing

---

## Key Takeaways

1. **Purpose over decoration** - Every animation must have a functional reason
2. **Fast transitions** - 200-300ms feels instant and responsive
3. **Use GPU acceleration** - `transform` and `opacity` only
4. **Respect accessibility** - Honor `prefers-reduced-motion`
5. **Test thoroughly** - Multiple devices, browsers, performance
6. **Professional restraint** - Subtle animations for engineering apps

**Next Steps:**
- Review RESEARCH-008 (Competitive Analysis)
- Implement animation utilities library
- Create animation documentation
- Build interactive examples

---

**Research Complete:** 2026-01-08
**Total Time:** 5 hours
**Lines:** 850
**Status:** ✅ READY FOR IMPLEMENTATION
