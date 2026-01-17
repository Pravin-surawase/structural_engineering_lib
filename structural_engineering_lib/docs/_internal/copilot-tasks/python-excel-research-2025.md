# Python-Excel Integration Research (2025)

**Date:** 2026-01-01
**Purpose:** Research best Python-Excel UDF solution before committing to xlwings

---

## Options Researched

| Solution | Type | Pricing | Performance | Maturity |
|----------|------|---------|-------------|----------|
| **xlSlim** | Commercial | £75/year ($91) | Fast (~ PyXLL) | New (2020s) |
| **PyXLL** | Commercial | $299/year | Fastest (300-1000x vs xlwings) | Mature (since 2010) |
| **xlwings** | Open-source + PRO | Free / $1490/year | Slower | Popular (2014+) |
| **Anaconda Code** | Microsoft AppSource | Unknown | Unknown | New (2024+) |
| **ExcelPython** | Open-source | Free | Unknown | Less active |

---

## Detailed Comparison

### 1. xlSlim (NEW DISCOVERY - Best Value!)

**Website:** https://www.xlslim.com/

**Pricing:** £74.99/year ($91 USD) per user
- ✅ **14-day free trial**
- ✅ Cheapest commercial option
- ✅ Includes pandas and numpy in premium

**Performance:**
- Claims to be "as fast as PyXLL"
- No confirmed benchmarks, but user reports suggest good performance

**Ease of Use:**
- ⭐ **BIGGEST ADVANTAGE:** No code changes needed
- No decorators required (unlike xlwings @xw.func)
- If you have modern Python code, it works directly
- Far simpler than competitors

**Features:**
- ✅ UDFs (User-Defined Functions)
- ✅ Excel add-in (not workbook-specific)
- ✅ Pandas/numpy support
- ✅ Python notebooks in Excel
- ✅ Good documentation and YouTube tutorials

**Deployment:**
- True Excel add-in (like PyXLL)
- Not tied to specific workbook
- Clean distribution

**Limitations:**
- Relatively new (less battle-tested)
- Smaller community vs xlwings

**Verdict:** 🏆 **Best price/performance ratio**

---

### 2. PyXLL (Enterprise-Grade)

**Website:** https://www.pyxll.com/

**Pricing:** $299/user/year
- More expensive than xlSlim, cheaper than xlwings PRO
- Free trial available

**Performance:**
- ⭐ **Fastest by far** (300-1000x faster than xlwings in benchmarks)
- Uses C++ core with embedded Python runtime
- Multi-threading and lazy evaluation
- Highly optimized for UDFs

**Architecture:**
- True Excel add-in (C++ with embedded Python)
- Uses Excel C API for core features
- Python runs inside Excel process (not external)

**Features:**
- ✅ UDFs (best performance)
- ✅ Real-time data (RTD) functions
- ✅ Custom ribbon UI
- ✅ Custom task panes
- ✅ Menu functions
- ✅ Excel object model access

**Enterprise:**
- ✅ Most mature (since 2010, v5 now)
- ✅ Professional support
- ✅ Used by financial institutions
- ✅ Proven at scale

**Deployment:**
- Add-in accessible from any workbook
- Clean enterprise distribution
- Network installation support

**Verdict:** 🥈 **Best for enterprise/performance-critical**

---

### 3. xlwings (Popular Open-Source)

**Website:** https://www.xlwings.org/

**Pricing:**
- **Free:** Open-source version (basic features)
- **PRO:** $1490/year (most expensive!)

**Performance:**
- ⚠️ **Slowest option** (300-1000x slower than PyXLL for UDFs)
- Recent issues: Python 3.14 caused 3-minute delays (was 10 seconds)
- Better for automation than UDFs

**Architecture:**
- COM/AppleScript wrapper (Excel runs externally)
- Auto-generates VBA code that calls Python process
- Workbook-specific by default

**Features:**
- ✅ UDFs (slow but functional)
- ✅ Excel automation (strong suit)
- ✅ Free version available
- ✅ Cross-platform (Windows + Mac)
- ✅ Server version (web-based)

**Community:**
- ✅ Most popular (largest community)
- ✅ Extensive documentation
- ✅ Many examples and tutorials
- ✅ Active GitHub

**Limitations:**
- ❌ UDFs are slow (external Python process)
- ❌ Workbook-specific deployment
- ❌ VBA code generation adds complexity
- ❌ Recent performance issues (Python 3.14)
- ❌ PRO version very expensive ($1490 vs $299 vs $91)

**Verdict:** 🥉 **Best for learning/non-commercial (free version)**

---

### 4. Anaconda Code / Toolbox

**Website:** Microsoft AppSource

**Pricing:** Unknown (likely subscription)

**Status:** Very new (2024-2025)

**Features:**
- Python UDFs in Excel
- Microsoft AppSource distribution
- Anaconda ecosystem integration

**Limitations:**
- Too new to evaluate
- Unknown pricing
- Limited documentation
- Unknown performance

**Verdict:** ⏳ **Too early to recommend**

---

### 5. ExcelPython

**Website:** https://github.com/ericremoreynolds/excelpython

**Pricing:** Free and open-source

**Status:** Less actively maintained

**Verdict:** ⏸️ **Not recommended** (use xlwings free instead)

---

## Performance Benchmarks (from PyXLL)

| Operation | PyXLL | xlwings | Ratio |
|-----------|-------|---------|-------|
| Simple UDF | 0.001s | 0.3s | 300x faster |
| Complex UDF | 0.01s | 10s | 1000x faster |
| Array function | 0.1s | 30s | 300x faster |

**Source:** [PyXLL Performance Comparison](https://www.pyxll.com/blog/performance-comparison/)

**Note:** xlSlim claims comparable performance to PyXLL but no independent benchmarks available.

---

## Use Case Analysis: Structural Engineering UDFs

### Requirements:
- ✅ Fast calculations (beams, flexure, shear)
- ✅ Reuse existing Python code
- ✅ Distribute to users (add-in, not workbook-specific)
- ✅ Professional appearance
- ✅ Cost-effective
- ⚠️ Real-time data: Not needed
- ⚠️ Web/cloud: Not needed now (maybe future)

### Scoring:

| Criteria | xlSlim | PyXLL | xlwings Free | xlwings PRO |
|----------|--------|-------|--------------|-------------|
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Pricing** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Deployment** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **Maturity** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Community** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Total** | **25/30** | **27/30** | **20/30** | **21/30** |

---

## Recommendation

### 🏆 Winner: xlSlim

**Reasons:**
1. **Best value:** $91/year vs $299 (PyXLL) vs $1490 (xlwings PRO)
2. **Easiest to use:** No code changes needed (no decorators)
3. **Good performance:** Claims comparable to PyXLL
4. **True add-in:** Not workbook-specific (clean distribution)
5. **14-day free trial:** Test before committing
6. **Your existing code works:** No @xw.func decorators needed

**Ideal for:**
- ✅ Solo developer / small team
- ✅ Budget-conscious
- ✅ Want simplicity
- ✅ Existing Python codebase

---

### 🥈 Runner-up: PyXLL

**When to choose:**
- Need proven enterprise-grade performance
- Calculations are extremely performance-critical
- Need real-time data (RTD) features
- Want professional support
- Budget allows $299/year

**Ideal for:**
- ✅ Large teams
- ✅ Financial/engineering firms
- ✅ Performance-critical applications
- ✅ Need professional support

---

### 🥉 Runner-up: xlwings (Free)

**When to choose:**
- Budget is absolutely $0
- Learning Python-Excel integration
- Automation (not UDFs) is primary use case
- Don't mind slower UDFs

**Ideal for:**
- ✅ Personal projects
- ✅ Non-commercial use
- ✅ Learning
- ✅ Excel automation (not calculations)

---

## Migration Path Comparison

### xlSlim Migration:
```python
# Your existing code (NO CHANGES NEEDED!)
def calculate_mu_lim(b, d, fck, fy):
    # ... existing code ...
    return mu_lim_knm
```

Excel usage:
```excel
=calculate_mu_lim(300, 450, 25, 500)
```

**Time to migrate:** ~1 hour (install add-in, register module)

---

### PyXLL Migration:
```python
from pyxll import xl_func

@xl_func  # ← Only change needed
def calculate_mu_lim(b, d, fck, fy):
    # ... existing code ...
    return mu_lim_knm
```

Excel usage:
```excel
=calculate_mu_lim(300, 450, 25, 500)
```

**Time to migrate:** ~2 hours (add decorators, configure)

---

### xlwings Migration:
```python
import xlwings as xw

@xw.func  # ← Decorator needed
@xw.arg('b', doc='Beam width')  # ← Extra decorators
@xw.arg('d', doc='Effective depth')
# ... etc for all args
def calculate_mu_lim(b, d, fck, fy):
    # ... existing code ...
    return mu_lim_knm
```

Excel usage:
```excel
=calculate_mu_lim(300, 450, 25, 500)
```

**Time to migrate:** ~4 hours (decorators, types.py fix, VBA generation)
**Blocker:** types.py naming conflict (must fix first)

---

## Cost Comparison (5 Years)

| Solution | Year 1 | Year 5 | 5-Year Total |
|----------|--------|--------|--------------|
| **xlSlim** | $91 | $91 | $455 |
| **PyXLL** | $299 | $299 | $1,495 |
| **xlwings PRO** | $1,490 | $1,490 | $7,450 |
| **xlwings Free** | $0 | $0 | $0 |

**Savings (xlSlim vs xlwings PRO):** $6,995 over 5 years!

---

## Final Verdict

### Recommended: xlSlim

**Why:**
1. **10x cheaper than xlwings PRO** ($91 vs $1490)
2. **3x cheaper than PyXLL** ($91 vs $299)
3. **Easiest to use** (no code changes)
4. **Fast enough** for structural calculations
5. **Clean deployment** (true add-in)
6. **Free trial** (test now, commit later)

### Action Plan:

1. **Try xlSlim** (14-day free trial)
   - Download from https://www.xlslim.com/
   - Register your existing Python modules
   - Test with beam calculations
   - If works → purchase ($91/year)

2. **If xlSlim doesn't work:**
   - Try **PyXLL** (if need more performance) - $299/year
   - Try **xlwings free** (if budget is $0) - need to fix types.py

3. **Avoid xlwings PRO** unless:
   - You need server/web features
   - Company already invested in xlwings ecosystem

---

## Sources

1. [The Best Python Libraries for Excel in 2025](https://sheetflash.com/blog/the-best-python-libraries-for-excel-in-2024)
2. [xlwings Official Site](https://www.xlwings.org/)
3. [PyXLL vs xlwings Comparison](https://support.pyxll.com/hc/en-gb/articles/360042910613-What-is-the-difference-between-PyXLL-and-xlwings)
4. [PyXLL Performance Comparison](https://www.pyxll.com/blog/performance-comparison/)
5. [xlSlim Official Site](https://www.xlslim.com/en-us)
6. [xlwings Performance Issues](https://github.com/xlwings/xlwings/issues/2650)
7. [PyXLL Features](https://www.pyxll.com/features.html)
8. [xlSlim vs PyXLL Performance](https://www.xlslim.com/en-us/blogs/news/pyxll)

---

## Next Steps

**If you choose xlSlim (recommended):**
1. Download 14-day trial: https://www.xlslim.com/
2. Test with your existing `flexure.py`, `shear.py` modules
3. No code changes needed (huge win!)
4. If works → purchase ($91/year)
5. Distribute as Excel add-in to users

**If you choose PyXLL:**
1. Download trial: https://www.pyxll.com/
2. Add `@xl_func` decorators to functions
3. Test performance
4. Purchase ($299/year)

**If you choose xlwings free:**
1. Fix types.py naming conflict (15 min)
2. Add @xw.func decorators
3. Use free forever (but slower)

---

**My recommendation: Start with xlSlim trial TODAY. It solves all your problems at the lowest cost.**
