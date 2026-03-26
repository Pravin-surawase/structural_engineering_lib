# Research: Enterprise Folder Structure for Multi-Code Structural Library

**Date:** 2026-01-10
**Author:** AI Agent (Phase C.3)
**Purpose:** Research enterprise-level folder structure patterns for a structural engineering library supporting multiple design codes (IS 456, ACI 318, Eurocode 2)

---

## Part 1: Current Structure Analysis

### 1.1 Current Top-Level Structure

```
structural_engineering_lib/
├── Python/                 # Core Python library
│   ├── structural_lib/     # Main package (IS 456 specific)
│   ├── tests/              # Test suite
│   └── examples/           # Usage examples
├── VBA/                    # Excel VBA modules
│   ├── Modules/            # VBA source files
│   ├── Tests/              # VBA tests
│   └── Examples/           # VBA examples
├── Excel/                  # Excel workbooks
├── streamlit_app/          # Web UI
├── docs/                   # Documentation (389 files)
├── scripts/                # Automation (85 scripts)
├── agents/                 # AI agent specs
└── tests/                  # Additional tests
```

### 1.2 Strengths

| Strength | Evidence |
|----------|----------|
| ✅ Clear separation | Python, VBA, Excel, docs in separate folders |
| ✅ Comprehensive docs | 389 markdown files with semantic indexes |
| ✅ Strong automation | 85 scripts for CI, validation, maintenance |
| ✅ Test organization | Unit, integration, performance, property tests |
| ✅ Agent specs | Dedicated folder for AI agent guidelines |

### 1.3 Weaknesses

| Weakness | Impact | Priority |
|----------|--------|----------|
| ❌ IS 456 hardcoded | Can't add ACI/Eurocode easily | 🔴 High |
| ❌ Flat module structure | All 30+ modules in one folder | 🟠 Medium |
| ❌ No code-specific namespacing | `flexure.py` only handles IS 456 | 🔴 High |
| ❌ No shared abstractions | No base classes for code-agnostic logic | 🔴 High |
| ❌ No plugin architecture | Can't add codes without modifying core | 🟠 Medium |
| ❌ No JSON metadata index | Manual doc navigation | 🟡 Low |

### 1.4 Current Python Module Categories

**Core Calculations (Code-Specific):**
- `flexure.py` - Flexural design (IS 456 Cl. 38.1)
- `shear.py` - Shear design (IS 456 Cl. 40)
- `detailing.py` - Reinforcement detailing (IS 456)
- `serviceability.py` - Deflection/cracking (IS 456)
- `ductile.py` - Seismic detailing (IS 13920)
- `compliance.py` - Code compliance checks

**Utilities (Code-Agnostic):**
- `materials.py` - Material properties
- `tables.py` - Lookup tables
- `utilities.py` - Helper functions
- `constants.py` - Physical constants
- `types.py` - Type definitions

**Integration (Code-Agnostic):**
- `api.py` - Public API
- `bbs.py` - Bar bending schedule
- `dxf_export.py` - CAD export
- `report.py` - Report generation
- `excel_bridge.py` - Excel integration

---

## Part 2: Enterprise Patterns Research

### 2.1 Multi-Code Library Patterns

**Pattern 1: Namespace by Code (Recommended)**

```
structural_lib/
├── core/                    # Code-agnostic base
│   ├── __init__.py
│   ├── base.py              # Abstract base classes
│   ├── materials.py         # Universal material models
│   ├── geometry.py          # Cross-section geometry
│   └── units.py             # Unit conversion
├── codes/                   # Code-specific implementations
│   ├── __init__.py
│   ├── is456/               # Indian Standard
│   │   ├── __init__.py
│   │   ├── flexure.py
│   │   ├── shear.py
│   │   ├── detailing.py
│   │   └── tables.py
│   ├── aci318/              # ACI 318 (future)
│   │   ├── __init__.py
│   │   ├── flexure.py
│   │   └── ...
│   └── ec2/                 # Eurocode 2 (future)
│       ├── __init__.py
│       └── ...
├── integration/             # Code-agnostic integration
│   ├── api.py
│   ├── bbs.py
│   └── dxf_export.py
└── utils/                   # Shared utilities
    ├── validation.py
    └── errors.py
```

**Benefits:**
- Clear separation of code-specific logic
- Easy to add new codes (just add folder)
- Shared logic in `core/`
- Backward compatible imports via `__init__.py`

**Pattern 2: Plugin Architecture**

```python
# structural_lib/registry.py
class CodeRegistry:
    _codes: dict[str, "DesignCode"] = {}

    @classmethod
    def register(cls, code_id: str, code_class: type):
        cls._codes[code_id] = code_class

    @classmethod
    def get(cls, code_id: str) -> "DesignCode":
        return cls._codes[code_id]()

# Usage
from structural_lib.codes.is456 import IS456Code
CodeRegistry.register("IS456", IS456Code)

# Later
code = CodeRegistry.get("IS456")
result = code.design_flexure(beam)
```

**Benefits:**
- Runtime code selection
- Third-party code plugins possible
- Clean dependency injection

### 2.2 JSON Metadata Index Pattern

**Purpose:** Machine-readable index of all documentation for AI agents.

**Schema:**

```json
{
  "version": "1.0.0",
  "generated": "2026-01-10T00:00:00Z",
  "docs": {
    "docs/reference/api.md": {
      "title": "API Reference",
      "type": "reference",
      "complexity": "advanced",
      "owner": "Main Agent",
      "tags": ["api", "python", "contracts"],
      "sections": ["flexure", "shear", "detailing"],
      "last_updated": "2026-01-10"
    }
  },
  "navigation": {
    "by_role": {
      "ai_agent": ["docs/agents/agent-onboarding.md"],
      "python_dev": ["docs/getting-started/python-quickstart.md"],
      "excel_user": ["docs/getting-started/excel-tutorial.md"]
    },
    "by_topic": {
      "api": ["docs/reference/api.md"],
      "testing": ["docs/contributing/testing-strategy.md"]
    }
  }
}
```

**Benefits:**
- AI agents can query programmatically
- Faster navigation (no parsing markdown)
- Enables semantic search
- Auto-generated from front-matter

### 2.3 Folder Expansion Patterns

**When Adding ACI 318:**

```
# Step 1: Create code folder
mkdir -p Python/structural_lib/codes/aci318

# Step 2: Abstract shared logic
# Move pure math to core/, keep code refs in codes/is456/

# Step 3: Implement ACI equivalents
# Python/structural_lib/codes/aci318/flexure.py
# - Same interface as is456/flexure.py
# - Different formulas, tables, coefficients

# Step 4: Registry integration
# Auto-discover codes from folder structure
```

**Versioning for Codes:**

```
codes/
├── is456/
│   ├── __init__.py        # Current: IS 456:2000
│   └── is456_2000/        # Explicit version
├── aci318/
│   ├── aci318_19/         # ACI 318-19
│   └── aci318_25/         # ACI 318-25 (when released)
```

---

## Part 3: Recommendations

### 3.1 Short-Term (This Session)

| Task | Effort | Impact |
|------|--------|--------|
| Create `codes/is456/` folder structure | 2h | Foundation for multi-code |
| Move IS 456-specific modules | 2h | Clean separation |
| Create `core/` with base classes | 1h | Abstraction layer |
| Generate `docs-index.json` | 1h | AI agent efficiency |

### 3.2 Medium-Term (v0.17-v0.18)

| Task | Effort | Impact |
|------|--------|--------|
| Implement code registry | 4h | Plugin architecture |
| Add abstract base classes | 4h | Interface contracts |
| Create code scaffold generator | 2h | Easy new code setup |
| JSON index auto-generator | 2h | Docs freshness |

### 3.3 Long-Term (v1.0+)

| Task | Effort | Impact |
|------|--------|--------|
| ACI 318-19 implementation | 40h | US market |
| Eurocode 2 implementation | 40h | EU market |
| Code comparison module | 8h | Educational value |
| Multi-code report generation | 8h | Professional feature |

---

## Part 4: Proposed Enterprise Structure

```
structural_engineering_lib/
├── src/                           # Source code (new location)
│   ├── structural_lib/            # Main package
│   │   ├── __init__.py
│   │   ├── core/                  # Code-agnostic core
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # Abstract classes
│   │   │   ├── materials.py       # Universal materials
│   │   │   ├── geometry.py        # Cross-sections
│   │   │   ├── units.py           # Unit handling
│   │   │   └── registry.py        # Code registration
│   │   ├── codes/                 # Code implementations
│   │   │   ├── __init__.py
│   │   │   ├── is456/             # Indian Standard
│   │   │   ├── aci318/            # American (future)
│   │   │   └── ec2/               # European (future)
│   │   ├── integration/           # Output/export
│   │   │   ├── api.py
│   │   │   ├── bbs.py
│   │   │   ├── dxf_export.py
│   │   │   └── report.py
│   │   └── utils/                 # Shared utilities
│   │       ├── errors.py
│   │       ├── validation.py
│   │       └── types.py
│   └── structural_lib_vba/        # VBA package (future)
├── tests/                         # All tests
│   ├── unit/
│   ├── integration/
│   └── codes/                     # Code-specific tests
│       ├── is456/
│       └── aci318/
├── docs/                          # Documentation
│   ├── docs-index.json            # Machine-readable index
│   ├── codes/                     # Code-specific docs
│   │   ├── is456/
│   │   └── aci318/
│   └── ...
├── examples/                      # Usage examples
│   ├── is456/
│   └── aci318/
├── apps/                          # Applications
│   ├── streamlit/
│   └── cli/
├── scripts/                       # Automation
├── agents/                        # AI agent specs
└── vba/                           # VBA source
    ├── modules/
    └── tests/
```

**Key Changes from Current:**
1. `Python/` → `src/` (standard Python packaging)
2. `structural_lib/` split into `core/`, `codes/`, `integration/`, `utils/`
3. Tests moved to top-level `tests/`
4. Streamlit moved to `apps/streamlit/`
5. VBA renamed to lowercase `vba/`
6. Added `docs-index.json` for machine-readable navigation

---

## Part 5: Implementation Priority

### Phase 1: Foundation (This Session)
1. ✅ Create docs-index.json generator
2. ✅ Create core/ folder structure
3. ✅ Create codes/is456/ folder
4. ⏳ Add backward-compatible imports

### Phase 2: Migration (Next Session)
1. Move IS 456 modules to codes/is456/
2. Create abstract base classes
3. Update all imports

### Phase 3: Expansion (Future)
1. Add code registry
2. Scaffold ACI 318
3. Multi-code API

---

**Research Status:** Complete
**Next Step:** Review findings and create actionable tasks
