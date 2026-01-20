# AI Workspace Expansion — Research & Architecture (V2)

**Type:** Research
**Audience:** Developers
**Status:** Draft
**Importance:** Critical
**Created:** 2026-01-20
**Last Updated:** 2026-01-20
**Related Tasks:** Session 58, AI Workspace Enhancement

---

## Executive Summary

This research document explores how to dramatically expand the AI assistant's workspace capabilities, transforming it from a command executor to a powerful design partner. Key expansions include:

1. **Optimization Workspace** - Interactive table for beam-by-beam optimization with savings tracking
2. **Direct Library Access** - AI can call structural_lib functions directly
3. **Multi-Beam Batch Operations** - Floor-wise and building-wide optimizations
4. **Live Cost Tracking** - Real-time savings calculations
5. **Design History & Comparison** - Track changes and compare alternatives

Based on the user's feedback showing excellent AI performance, we should maximize its workspace access.

---

## Table of Contents

1. [Current State Assessment](#1-current-state-assessment)
2. [User Feedback Analysis](#2-user-feedback-analysis)
3. [Proposed Expansions](#3-proposed-expansions)
4. [Optimization Workspace Design](#4-optimization-workspace-design)
5. [Library Function Integration](#5-library-function-integration)
6. [New Tools Architecture](#6-new-tools-architecture)
7. [Implementation Roadmap](#7-implementation-roadmap)
8. [UI/UX Considerations](#8-uiux-considerations)
9. [Risks & Mitigations](#9-risks--mitigations)
10. [Next Steps](#10-next-steps)

---

## 1. Current State Assessment

### 1.1 What's Working Well (From User Demo)

Based on the conversation shown, the AI demonstrates strong capabilities:

| Capability | Example | Status |
|------------|---------|--------|
| Rebar display | "show rebar of beam b11_2" | ✅ Detailed response |
| Beam selection | "open beam b11_2 in workspace" | ✅ Works |
| Design all | "design all beams" | ✅ 153 beams designed |
| Floor filtering | "filter story 2" | ✅ Shows 28 beams |
| Critical identification | Lists top 6 by utilization | ✅ Excellent |
| Rebar arrangement | "arrange in 2 layers" | ✅ Works |
| Help system | Clear command listing | ✅ Good UX |

### 1.2 Current Tools (10 Total)

```python
CURRENT_TOOLS = [
    "design_beam",           # Single beam design
    "design_all_beams",      # Batch design
    "get_beam_details",      # Get beam info
    "select_beam",           # Select for viz
    "show_visualization",    # Trigger views
    "filter_3d_view",        # Filter by floor
    "get_critical_beams",    # List critical
    "start_optimization",    # Run optimization
    "suggest_optimization",  # Get suggestions
    "export_results",        # Export data
]
```

### 1.3 What's Limited

From the conversation, the AI shows knowledge but limited workspace control:

| Limitation | User Impact | Solution |
|------------|------------|----------|
| Optimization is single-beam | User can't batch optimize floor | Add `optimize_floor` tool |
| No savings tracking | User doesn't see cumulative savings | Add optimization history |
| No "what-if" comparisons | Can't compare alternatives | Add comparison workspace |
| No direct library calls | AI generates text, not actual calcs | Expose library functions |
| No editable table | User can't modify multiple beams | Add optimization table UI |
| No undo/revert | Changes are permanent | Add design history |

---

## 2. User Feedback Analysis

### 2.1 Key Insights from User

> "our ai llm model is really good, it can work a lot, so do give him workspace to work"

**Interpretation:** The LLM is capable but we're artificially limiting it. Expand its workspace.

> "we are limiting its capabilities as our workspace is limited"

**Interpretation:** The bottleneck is UI/tools, not AI capability.

> "like a table where llm can optimize beams, each beam, or floor wise, show changes, savings"

**Interpretation:** User wants:
- Interactive optimization table
- Beam-by-beam OR floor-by-floor modes
- Change tracking
- Cost/savings visualization

> "users need to work with ai chat, so think about it"

**Interpretation:** The AI should be the primary interface for complex operations.

> "even llm can use our lib functions which will increase its efficiency"

**Interpretation:** Expose structural_lib API to the AI directly.

### 2.2 Target User Workflow

Based on the demo conversation, ideal workflow:

```
User: "optimize all beams on floor 2"
AI: [Uses optimize_floor tool]
    → Shows table: 28 beams | Current: ₹4.2L | Optimized: ₹3.6L | Savings: 14%
    → Lists top 3 changes: b2_07 reduced depth, b2_12 reduced steel
    → Asks: "Apply all changes? Or review individual beams?"

User: "apply but skip b2_07, I need the extra depth there"
AI: [Uses apply_optimization tool with exclusions]
    → Applied 27 changes, skipped b2_07
    → Total savings: ₹58,000 (13.8%)
```

---

## 3. Proposed Expansions

### 3.1 Expansion Categories

| Category | New Tools | Impact |
|----------|-----------|--------|
| **Batch Optimization** | optimize_floor, optimize_building | High |
| **Cost Tracking** | get_project_cost, compare_designs | High |
| **Design History** | save_design_state, restore_state, list_history | Medium |
| **Direct Library** | call_api_function, run_calculation | High |
| **Rebar Editing** | modify_rebar_layout, arrange_bars | Medium |
| **Export/Reports** | generate_report, schedule_export | Medium |
| **What-If Analysis** | create_variant, compare_variants | High |

### 3.2 Priority Matrix

```
                   HIGH VALUE
                       │
     ┌─────────────────┼─────────────────┐
     │                 │                 │
     │  optimize_floor │ call_api_func   │
     │  compare_designs│ optimization_   │
     │                 │   workspace     │
LOW  ├─────────────────┼─────────────────┤ HIGH
EFFORT│ list_history   │ create_variant  │ EFFORT
     │ modify_rebar   │ multi_floor_opt │
     │                 │                 │
     └─────────────────┼─────────────────┘
                       │
                   LOW VALUE
```

**Immediate priorities (Phase 1):**
1. `optimize_floor` - Batch optimize beams on a floor
2. `get_project_summary` - Cost/status overview
3. `optimization_workspace` - Show interactive table
4. `compare_designs` - Before/after comparison

---

## 4. Optimization Workspace Design

### 4.1 Concept: Interactive Optimization Table

The AI should be able to display and manipulate an optimization table:

```
┌──────────────────────────────────────────────────────────────────────────┐
│ 🔧 Optimization Workspace - Floor 2                                      │
├──────────────────────────────────────────────────────────────────────────┤
│ ✓ Select  │ Beam ID │ Section │ Util% │ Steel │ Cost   │ Opt Steel │ Δ   │
├───────────┼─────────┼─────────┼───────┼───────┼────────┼───────────┼─────┤
│ ☑         │ b2_07   │ 300×600 │ 92%   │ 1240  │ ₹8,420 │ 1180      │ -5% │
│ ☑         │ b2_12   │ 300×550 │ 88%   │ 1050  │ ₹7,150 │ 980       │ -7% │
│ ☐         │ b2_03   │ 250×500 │ 85%   │ 890   │ ₹5,940 │ 890       │ 0%  │
│ ☑         │ b2_19   │ 300×600 │ 80%   │ 1180  │ ₹8,020 │ 1050      │-11% │
├───────────┴─────────┴─────────┴───────┴───────┴────────┴───────────┴─────┤
│ Selected: 3 beams   │ Current Total: ₹23,590 │ Optimized: ₹21,730 (-8%) │
└──────────────────────────────────────────────────────────────────────────┘
│ [Apply Selected] [Apply All] [Reset] [Export Changes]                    │
└──────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Session State for Optimization

```python
# New session state keys
st.session_state.optimization_workspace = {
    "active": True,
    "floor": "Floor 2",
    "beams": [
        {
            "beam_id": "b2_07",
            "selected": True,
            "current": {"ast": 1240, "cost": 8420, "section": "300x600"},
            "optimized": {"ast": 1180, "cost": 8020, "section": "300x600"},
            "delta": {"ast_pct": -5, "cost_pct": -5},
            "changes": ["Reduced bar diameter from Ø20 to Ø16"],
        },
        # ... more beams
    ],
    "totals": {
        "current_cost": 45000,
        "optimized_cost": 41000,
        "savings_pct": 8.9,
    },
    "history": [
        {"timestamp": "2026-01-20 14:30", "action": "Applied optimization to b2_07"},
    ],
}
```

### 4.3 Tool: `show_optimization_workspace`

```python
{
    "type": "function",
    "function": {
        "name": "show_optimization_workspace",
        "description": "Display interactive optimization table for a floor or the entire building. Users can select beams, view savings, and apply changes.",
        "parameters": {
            "type": "object",
            "properties": {
                "scope": {
                    "type": "string",
                    "enum": ["floor", "building", "selected"],
                    "description": "Scope of optimization (default: floor)"
                },
                "floor": {
                    "type": "string",
                    "description": "Floor/story to show (for floor scope)"
                },
                "target": {
                    "type": "string",
                    "enum": ["cost", "weight", "constructability"],
                    "description": "Optimization target (default: cost)"
                },
                "utilization_limit": {
                    "type": "number",
                    "description": "Maximum utilization % after optimization (default: 90)"
                }
            },
            "required": [],
            "additionalProperties": false
        },
        "strict": true
    }
}
```

### 4.4 Tool: `apply_optimization`

```python
{
    "type": "function",
    "function": {
        "name": "apply_optimization",
        "description": "Apply optimization changes to selected beams. Can apply all, selected only, or exclude specific beams.",
        "parameters": {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["all", "selected", "exclude"],
                    "description": "Apply mode"
                },
                "beam_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Beam IDs to apply/exclude based on mode"
                },
                "confirm": {
                    "type": "boolean",
                    "description": "Must be true to actually apply changes"
                }
            },
            "required": ["mode", "confirm"],
            "additionalProperties": false
        },
        "strict": true
    }
}
```

---

## 5. Library Function Integration

### 5.1 The Opportunity

The structural_lib API has 50+ functions that the AI cannot currently use:

```python
# Currently unavailable to AI (but should be):
design_beam_is456()           # Core design function
design_and_detail_beam_is456()  # Combined design + detailing
optimize_beam_cost()          # Cost optimization
suggest_beam_design_improvements()  # AI suggestions
smart_analyze_design()        # Full analysis dashboard
compute_bmd_sfd()             # Load diagrams
design_torsion()              # Torsion design
```

### 5.2 Approach: Generic API Caller

Instead of creating a tool for each function, create a **generic library caller**:

```python
{
    "type": "function",
    "function": {
        "name": "call_structural_lib",
        "description": "Call any function from structural_lib API. Use for calculations, optimizations, and analysis. Available functions: design_beam_is456, optimize_beam_cost, smart_analyze_design, compute_bmd_sfd, design_torsion, compute_detailing, compute_bbs, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "function_name": {
                    "type": "string",
                    "description": "Name of the API function to call"
                },
                "arguments": {
                    "type": "object",
                    "description": "Arguments for the function (see API reference)"
                }
            },
            "required": ["function_name", "arguments"],
            "additionalProperties": false
        },
        "strict": true
    }
}
```

### 5.3 Handler Implementation

```python
def _handle_call_structural_lib(args: dict) -> str:
    """Call structural_lib API functions directly."""
    from structural_lib import api

    func_name = args.get("function_name", "")
    func_args = args.get("arguments", {})

    # Whitelist of allowed functions
    ALLOWED_FUNCTIONS = [
        "design_beam_is456",
        "design_and_detail_beam_is456",
        "optimize_beam_cost",
        "suggest_beam_design_improvements",
        "smart_analyze_design",
        "compute_bmd_sfd",
        "design_torsion",
        "compute_detailing",
        "compute_bbs",
        "check_beam_ductility",
        "check_deflection_span_depth",
        "check_crack_width",
    ]

    if func_name not in ALLOWED_FUNCTIONS:
        return json.dumps({
            "error": f"Function '{func_name}' not allowed",
            "allowed": ALLOWED_FUNCTIONS,
        })

    # Get function and call it
    func = getattr(api, func_name, None)
    if func is None:
        return json.dumps({"error": f"Function '{func_name}' not found"})

    try:
        result = func(**func_args)

        # Convert result to JSON-serializable format
        if hasattr(result, "to_dict"):
            return json.dumps(result.to_dict())
        elif hasattr(result, "__dict__"):
            return json.dumps({k: v for k, v in result.__dict__.items() if not k.startswith("_")})
        else:
            return json.dumps({"result": str(result)})

    except Exception as e:
        return json.dumps({"error": str(e)})
```

### 5.4 System Prompt Enhancement

Add API reference to the system prompt:

```markdown
## Library API Reference

You can call structural_lib functions using the `call_structural_lib` tool.

### design_beam_is456()
Design a beam per IS 456. Required args: units="IS456", mu_knm, vu_kn, b_mm, D_mm, d_mm, fck_nmm2, fy_nmm2

### optimize_beam_cost()
Find cheapest design. Args: units="IS456", span_mm, mu_knm, vu_kn
Returns: optimal_design, savings_percent, alternatives

### smart_analyze_design()
Full analysis dashboard. Args: units="IS456", span_mm, mu_knm, vu_kn, b_mm, D_mm, d_mm, fck_nmm2, fy_nmm2
Returns: cost analysis, suggestions, sensitivity, constructability

### compute_bmd_sfd()
Generate bending moment and shear force diagrams.
Args: span_mm, loads (list of LoadDefinition)
```

---

## 6. New Tools Architecture

### 6.1 Proposed Tool Expansion (Phase 1 - 8 New Tools)

| Tool | Purpose | Priority |
|------|---------|----------|
| `show_optimization_workspace` | Display interactive optimization table | P0 |
| `apply_optimization` | Apply changes from workspace | P0 |
| `get_project_summary` | Overall cost/status/savings | P0 |
| `call_structural_lib` | Generic API caller | P0 |
| `compare_designs` | Compare current vs optimized | P1 |
| `modify_beam_design` | Change beam properties | P1 |
| `save_design_state` | Save current state | P1 |
| `undo_last_change` | Revert last modification | P1 |

### 6.2 Tool: `get_project_summary`

```python
{
    "type": "function",
    "function": {
        "name": "get_project_summary",
        "description": "Get comprehensive project summary including beam count, design status, costs, and optimization potential.",
        "parameters": {
            "type": "object",
            "properties": {
                "include_costs": {
                    "type": "boolean",
                    "description": "Include cost estimates (default: true)"
                },
                "include_optimization": {
                    "type": "boolean",
                    "description": "Include optimization potential (default: true)"
                }
            },
            "required": [],
            "additionalProperties": false
        },
        "strict": true
    }
}
```

### 6.3 Tool: `modify_beam_design`

```python
{
    "type": "function",
    "function": {
        "name": "modify_beam_design",
        "description": "Modify a beam's design parameters and re-run analysis. Use for 'change beam b1 depth to 600mm' requests.",
        "parameters": {
            "type": "object",
            "properties": {
                "beam_id": {
                    "type": "string",
                    "description": "Beam to modify"
                },
                "changes": {
                    "type": "object",
                    "properties": {
                        "b_mm": {"type": "number"},
                        "D_mm": {"type": "number"},
                        "fck": {"type": "number"},
                        "fy": {"type": "number"},
                        "bottom_bars": {"type": "string", "description": "e.g., '4Ø16' or '3Ø20+2Ø16'"},
                        "top_bars": {"type": "string"},
                        "stirrup_spacing": {"type": "number"}
                    }
                },
                "redesign": {
                    "type": "boolean",
                    "description": "Re-run design after changes (default: true)"
                }
            },
            "required": ["beam_id", "changes"],
            "additionalProperties": false
        },
        "strict": true
    }
}
```

---

## 7. Implementation Roadmap

### 7.1 Phase 1: Optimization Workspace (2-3 days)

| Task | Description | Effort |
|------|-------------|--------|
| 1.1 | Create `optimization_workspace.py` component | 4h |
| 1.2 | Implement `show_optimization_workspace` tool | 2h |
| 1.3 | Implement `apply_optimization` tool | 2h |
| 1.4 | Add session state management | 2h |
| 1.5 | Integrate with AI page 11 | 2h |
| 1.6 | Test and refine | 2h |

### 7.2 Phase 2: Library Integration (2-3 days)

| Task | Description | Effort |
|------|-------------|--------|
| 2.1 | Implement `call_structural_lib` tool | 3h |
| 2.2 | Add result serialization helpers | 2h |
| 2.3 | Enhance system prompt with API reference | 2h |
| 2.4 | Add function whitelisting | 1h |
| 2.5 | Test with complex queries | 2h |

### 7.3 Phase 3: Project Overview (1-2 days)

| Task | Description | Effort |
|------|-------------|--------|
| 3.1 | Implement `get_project_summary` tool | 2h |
| 3.2 | Add cost calculation for all beams | 2h |
| 3.3 | Implement `compare_designs` tool | 2h |
| 3.4 | Add design history tracking | 2h |

### 7.4 Phase 4: Advanced Features (2-3 days)

| Task | Description | Effort |
|------|-------------|--------|
| 4.1 | Implement `modify_beam_design` tool | 3h |
| 4.2 | Add undo/redo functionality | 2h |
| 4.3 | Implement batch floor optimization | 3h |
| 4.4 | Add export for optimization results | 2h |

---

## 8. UI/UX Considerations

### 8.1 Workspace Layout (AI Chat + Interactive)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ⚡ AI Assistant V2                                              [🔧] [📊] │
├───────────────────────────────────┬─────────────────────────────────────┤
│                                   │                                     │
│    💬 Chat Panel                  │      🔧 Workspace Panel             │
│                                   │                                     │
│  User: optimize all floor 2      │   ┌─────────────────────────────┐   │
│                                   │   │ Optimization Workspace      │   │
│  AI: Running optimization...      │   │ Floor 2 | 28 beams          │   │
│       ✅ Found savings of 14%     │   ├─────────────────────────────┤   │
│       See table on right →        │   │ ☑ b2_07 │ 92% │ -5% steel  │   │
│                                   │   │ ☑ b2_12 │ 88% │ -7% steel  │   │
│  User: skip b2_07                 │   │ ☐ b2_03 │ 85% │ 0% change  │   │
│                                   │   │ ☑ b2_19 │ 80% │ -11% steel │   │
│  AI: Unchecked b2_07. Updated    │   ├─────────────────────────────┤   │
│       savings: ₹48,000 (12%)     │   │ Total: ₹23,590 → ₹20,890   │   │
│                                   │   │ [Apply] [Reset] [Export]    │   │
├───────────────────────────────────┤   └─────────────────────────────┘   │
│ Ask about optimization...     ⏎  │                                     │
└───────────────────────────────────┴─────────────────────────────────────┘
```

### 8.2 AI-Driven Table Interaction

The AI should be able to:
1. **Select/deselect beams** in the table via chat
2. **Sort/filter** the table ("show only beams > 80% utilization")
3. **Apply changes** ("apply all except b2_07")
4. **Export** selected beams or changes

### 8.3 Visual Feedback

When AI makes changes, show:
- ✅ Green highlight for applied optimizations
- ⚠️ Yellow for pending changes
- 📊 Running totals of savings
- 📈 Before/after comparison charts

---

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| AI makes incorrect API calls | Medium | High | Whitelist allowed functions, validate inputs |
| Optimization breaks design | Low | High | Always re-check compliance after optimization |
| Too many API calls → slow | Medium | Medium | Cache results, batch operations |
| UI complexity overwhelms users | Medium | Medium | Progressive disclosure, sensible defaults |
| Undo not working correctly | Medium | High | Implement robust state snapshots |
| Cost calculations inaccurate | Medium | Medium | Use actual library costing, show disclaimers |

---

## 10. Next Steps

### Immediate (This Session)
- [x] Complete this research document
- [ ] Create detailed tool specifications for Phase 1
- [ ] Design session state structure for optimization workspace
- [ ] Update system prompt with new capabilities

### Phase 1 Sprint (Next 2-3 days)
- [ ] Implement optimization workspace component
- [ ] Add `show_optimization_workspace` tool
- [ ] Add `apply_optimization` tool
- [ ] Test with real beam data

### Phase 2 Sprint (Following week)
- [ ] Implement `call_structural_lib` generic API tool
- [ ] Add serialization for all result types
- [ ] Enhance system prompt with complete API reference
- [ ] Test complex multi-step workflows

---

## Appendix A: Example Conversations

### A.1 Batch Optimization

```
User: "optimize floor 2 for cost"

AI: I'm optimizing all 28 beams on Floor 2 for minimum cost while maintaining structural safety.

[Shows optimization workspace table]

Results:
• 28 beams analyzed
• Current cost: ₹2,34,500
• Optimized cost: ₹2,01,800
• Savings: ₹32,700 (14%)

Top 3 changes:
1. b2_07: Reduce bar diameter Ø20 → Ø16 (saves ₹4,200)
2. b2_12: Reduce section depth 600 → 550mm (saves ₹3,800)
3. b2_19: Widen stirrup spacing 150 → 175mm (saves ₹2,100)

All 28 beams still pass IS 456 checks after optimization.

Say "apply all" to accept, or "skip b2_07" to exclude specific beams.
```

### A.2 Direct Library Call

```
User: "run smart analysis on beam b1 with span 5m, moment 150kNm, shear 80kN"

AI: [Uses call_structural_lib tool]

Smart Analysis Results for B1:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📐 Design Status: ✅ SAFE
   • Flexure utilization: 72%
   • Shear utilization: 45%
   • Min steel: ✅ Met

💰 Cost Analysis:
   • Current cost: ₹8,450 per meter
   • Optimal cost: ₹7,200 per meter
   • Potential savings: 15%

💡 Suggestions (4 found):
   • [HIGH] Reduce section depth 500 → 450mm
   • [MEDIUM] Use Fe415 instead of Fe500
   • [LOW] Variable stirrup spacing

Would you like me to apply the optimal design?
```

### A.3 Comparison Mode

```
User: "compare current design vs optimized for floor 1"

AI: [Uses compare_designs tool]

Floor 1 Design Comparison:
━━━━━━━━━━━━━━━━━━━━━━━━━

| Metric           | Current   | Optimized | Change   |
|------------------|-----------|-----------|----------|
| Total steel      | 4,520 kg  | 3,940 kg  | -13%     |
| Concrete volume  | 18.5 m³   | 17.2 m³   | -7%      |
| Est. cost        | ₹4,85,000 | ₹4,22,000 | -13%     |
| Avg utilization  | 65%       | 78%       | +13 pts  |
| Beams changed    | —         | 22/32     | —        |

All optimized beams maintain safety factor ≥ 1.10.

Changes summary:
• 8 beams: reduced section depth
• 12 beams: reduced steel area
• 2 beams: changed bar configuration

Ready to apply? Say "apply optimized" or "review changes".
```

---

## Appendix B: Session State Schema

```python
# Complete session state for expanded AI workspace

st.session_state.ai_workspace = {
    # Current design state
    "beams_df": pd.DataFrame(),  # All beams
    "design_results": pd.DataFrame(),  # Design results
    "selected_beam": None,  # Currently selected beam ID

    # Optimization workspace
    "optimization": {
        "active": False,
        "scope": "floor",  # floor | building | selected
        "floor_filter": None,
        "beams": [],  # List of OptimizationBeam objects
        "totals": {
            "current_cost": 0,
            "optimized_cost": 0,
            "savings_pct": 0,
        },
        "pending_changes": [],  # Changes not yet applied
        "applied_changes": [],  # Changes already applied
    },

    # Design history (for undo)
    "history": [
        {
            "timestamp": "2026-01-20T14:30:00",
            "action": "design_all",
            "description": "Designed 153 beams",
            "snapshot": {...},  # Full state snapshot
        }
    ],
    "history_index": 0,  # Current position in history

    # Comparison mode
    "comparison": {
        "active": False,
        "baseline": {...},  # Baseline design state
        "variant": {...},  # Variant being compared
    },

    # API call results cache
    "api_cache": {},

    # Export pending
    "export": {
        "format": None,
        "data": None,
        "filename": None,
    },
}
```

---

*Document created during Session 58 - AI Workspace Expansion Research V2*
