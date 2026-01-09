# IMPL-007: Apply Performance Optimizations to Pages

**Task ID:** IMPL-007
**Priority:** 🟠 HIGH
**Status:** ⏳ IN PROGRESS
**Estimated:** 3-4 hours
**Prerequisite:** ✅ IMPL-006 complete (all 4 optimization phases done)
**Date Started:** 2026-01-09

---

## Objective

Integrate all IMPL-006 performance optimizations into `01_beam_design.py` to demonstrate:
- 40% faster initial load via lazy loading
- 30-50% memory reduction via caching
- Smooth interactions via render optimization
- Professional user experience

---

## Implementation Plan

### Phase 1: Caching Integration (45 min)

**File:** `streamlit_app/pages/01_beam_design.py`

**Changes:**
1. Import `SmartCache` from `utils.caching`
2. Wrap design calculations with `@SmartCache.memoize()`
3. Wrap visualization generation with caching
4. Add cache stats display (debug mode)

**Expected Impact:**
- Repeated calculations instant (cached)
- Parameter sweep operations 10x faster

### Phase 2: Session State Optimization (45 min)

**Changes:**
1. Import `SessionStateManager` from `utils.session_manager`
2. Replace manual `st.session_state` with manager
3. Add batch updates for geometry inputs
4. Implement undo/redo for design iterations

**Expected Impact:**
- Cleaner state management
- Reduced re-renders on input changes

### Phase 3: Lazy Loading (30 min)

**Changes:**
1. Import `LazyLoader` from `utils.lazy_loader`
2. Defer heavy imports (plotly, pandas) until needed
3. Lazy-load help text, tooltips
4. Progressive loading for tabs

**Expected Impact:**
- Initial page load 40% faster
- Smoother tab switching

### Phase 4: Render Optimization (45 min)

**Changes:**
1. Import `RenderOptimizer` from `utils.render_optimizer`
2. Batch metric updates in summary cards
3. Debounce slider inputs (geometry changes)
4. Throttle real-time preview updates

**Expected Impact:**
- Smooth interactions (no lag)
- Reduced Streamlit reruns

### Phase 5: Data Loading (30 min)

**Changes:**
1. Import `DataLoader` from `utils.data_loader`
2. Use async loading for material properties
3. Batch load design tables (IS 456 data)
4. Add loading states for long operations

**Expected Impact:**
- Professional loading UX
- No blocking operations

---

## Success Criteria

- [ ] All 4 optimization utilities integrated
- [ ] Page loads in <1s (down from ~1.5s)
- [ ] Input changes responsive (<100ms)
- [ ] Cache hit rate >80% after 5 designs
- [ ] No regressions in functionality
- [ ] All existing tests pass

---

## Testing Strategy

**Manual Testing:**
1. Cold start (clear cache) → measure load time
2. Design iteration (change inputs) → check responsiveness
3. Tab switching → verify lazy loading
4. Parameter sweep (5 designs) → check cache effectiveness

**Automated Testing:**
- Rerun `pytest streamlit_app/tests/test_impl_005_integration.py`
- Verify no new failures introduced

---

## Rollback Plan

If performance degrades or bugs introduced:
```bash
git checkout main -- streamlit_app/pages/01_beam_design.py
git commit -m "revert: rollback IMPL-007 integration"
```

All optimization utilities are modular - page can work without them.

---

## Next Steps After IMPL-007

With optimizations proven on beam_design page:

1. **IMPL-008:** Apply to remaining pages (02-04)
2. **IMPL-009:** Add performance monitoring dashboard
3. **IMPL-010:** Optimize mobile/tablet experience
