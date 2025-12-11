# Production Readiness Roadmap

> **Current Status:** v0.7.0 — Strength design complete, serviceability checks missing.
> 
> **Production Readiness:** ~70%

---

## 🎯 Critical Path to Production

### Phase 1: Serviceability (Required for Real Projects)

| Task | Priority | Effort | IS 456 Reference |
|------|----------|--------|------------------|
| **Deflection Check** | 🔴 Critical | 2-3 sessions | Cl. 23.2, Annex C |
| **Crack Width Check** | 🔴 Critical | 1-2 sessions | Annex F |

**Why these are mandatory:**
- IS 456 Cl. 23.2: *"Final deflection shall not exceed span/250"*
- Annex F: Crack width limits (0.3mm moderate, 0.2mm severe exposure)
- A beam can pass strength design but fail serviceability in practice

#### Deflection Check Scope
```
1. Simplified Method (Cl. 23.2.1) - Span/depth ratios
   - Basic values: Cantilever=7, Simply supported=20, Continuous=26
   - Modification factors for tension steel, compression steel, flanged beams
   
2. Detailed Method (Annex C) - Optional
   - Short-term deflection from Ieff
   - Long-term deflection (shrinkage + creep)
```

#### Crack Width Scope
```
1. Annex F formula: wcr = 3 * acr * εm / (1 + 2(acr - cmin)/(h - x))
2. Exposure class input (mild/moderate/severe/very severe)
3. Limiting values per Table 3.2
```

---

### Phase 2: Enhanced Output (Recommended)

| Task | Priority | Effort | Value |
|------|----------|--------|-------|
| **Bar Bending Schedule (BBS)** | 🟡 Medium | 2 sessions | Contractor handoff |
| **PDF Report Generation** | 🟡 Medium | 1-2 sessions | Client deliverables |
| **DXF Section Cuts** | 🟢 Low | 1 session | Complete drawings |

#### BBS Output Format
```
| Bar Mark | Type | Dia | No. | Length | Shape | Total Wt |
|----------|------|-----|-----|--------|-------|----------|
| A        | Main | 16  | 4   | 4200   | ST    | 26.4 kg  |
| B        | Main | 12  | 2   | 3850   | ST    | 8.6 kg   |
| C        | Stirrup | 8 | 45  | 1120  | R1    | 15.8 kg  |
```

---

### Phase 3: Code Quality (Polish)

| Task | Priority | Effort |
|------|----------|--------|
| **Enhanced docstrings** | 🟢 Low | 1 session |
| **`__all__` exports** | 🟢 Low | 30 min |
| **VBA automated tests** | 🟢 Low | 2 sessions |
| **Type checking (mypy)** | 🟢 Low | 1 session |
| **Code coverage report** | 🟢 Low | 30 min |

---

## ✅ Already Complete

| Feature | Status | Tests |
|---------|--------|-------|
| Singly reinforced flexure | ✅ | ✅ |
| Doubly reinforced flexure | ✅ | ✅ |
| Flanged beam flexure (T/L) | ✅ | ✅ |
| Shear design (Table 19/20) | ✅ | ✅ |
| IS 13920 ductile detailing | ✅ | ✅ |
| Reinforcement detailing (Ld, lap, spacing) | ✅ | ✅ |
| DXF export (Python + VBA) | ✅ | ✅ |
| ETABS CSV integration | ✅ | ✅ |
| Beam schedule generation | ✅ | ✅ |
| Beginner documentation | ✅ | — |
| Python packaging (PyPI ready) | ✅ | — |
| Excel workbook | ✅ | — |

---

## 🚀 Recommended Implementation Order

```
Week 1-2: Deflection Check
├── Implement span/depth ratio method (simplified)
├── Add modification factors (MF1, MF2, MF3)
├── Add tests with known examples
└── Update Python + VBA

Week 3: Crack Width Check  
├── Implement Annex F formula
├── Add exposure class enum
├── Add tests
└── Update Python + VBA

Week 4: Integration
├── Add deflection/crack to design workflow
├── Update beam schedule with serviceability status
├── Update documentation
└── Release v0.8.0
```

---

## 📊 Production Readiness Checklist

### Strength Design ✅
- [x] Flexure — Singly reinforced
- [x] Flexure — Doubly reinforced  
- [x] Flexure — Flanged (T/L)
- [x] Shear — Stirrup design
- [x] Ductile — IS 13920 compliance
- [x] Detailing — Ld, lap lengths, spacing

### Serviceability Design ❌
- [ ] Deflection — Span/depth method
- [ ] Deflection — Detailed calculation (optional)
- [ ] Crack width — Annex F

### Output & Reporting
- [x] DXF drawings — Longitudinal + section
- [x] Beam schedule — Tabular format
- [ ] BBS — Bar bending schedule
- [ ] PDF report — Design summary

### Integration
- [x] ETABS CSV import
- [x] Excel workbook UI
- [ ] ETABS API (future)
- [ ] SAFE integration (future)

### Quality Assurance
- [x] Python tests (67 passing)
- [ ] VBA automated tests
- [x] Type hints
- [x] py.typed marker
- [ ] mypy clean
- [ ] 80%+ code coverage

---

## 🎯 Minimum Viable Production (MVP)

To use this library for **actual project submissions**, you need:

1. ✅ Strength design (DONE)
2. ❌ **Deflection check** (MISSING — implement span/depth method)
3. ❌ **Crack width check** (MISSING — implement Annex F)

**Without serviceability checks:**
- ✅ Safe for preliminary design
- ✅ Safe for quantity estimation
- ⚠️ NOT safe for final submission (must verify manually)

**With serviceability checks:**
- ✅ Fully production-ready
- ✅ Can replace manual calculations
- ✅ Suitable for professional practice

---

## Version Targets

| Version | Focus | Status |
|---------|-------|--------|
| v0.7.0 | Detailing + DXF | ✅ Current |
| **v0.8.0** | **Deflection + Crack Width** | 🎯 Next |
| v0.9.0 | BBS + PDF Reports | Planned |
| v1.0.0 | Production Release | Goal |

---

*Last updated: December 2025*
