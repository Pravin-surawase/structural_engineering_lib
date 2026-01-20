# AI Assistant Workspace Integration — Research & Planning

**Type:** Research
**Audience:** Developers
**Status:** Draft
**Importance:** High
**Created:** 2026-01-20
**Last Updated:** 2026-01-20
**Related Tasks:** Session 58

---

## Executive Summary

This document researches how to make the AI Assistant deeply integrated with the StructEng Streamlit workspace, giving it:
1. **Context awareness** - Understanding of the structural engineering library functions
2. **Tool use** - Ability to call library functions and analyze results
3. **Workspace control** - Ability to manipulate the UI, show visualizations, run designs

---

## Table of Contents

1. [Current State Analysis](#1-current-state-analysis)
2. [Research Findings](#2-research-findings)
3. [Architecture Options](#3-architecture-options)
4. [Implementation Plan](#4-implementation-plan)
5. [Context Document Design](#5-context-document-design)
6. [Risks & Mitigations](#6-risks--mitigations)
7. [Decision Matrix](#7-decision-matrix)
8. [Recommended Approach](#8-recommended-approach)
9. [Next Steps](#9-next-steps)

---

## 1. Current State Analysis

### 1.1 What Works Now

**AI Chat (Pages 10 & 11):**
- ✅ Chat interface with streaming responses
- ✅ OpenAI/OpenRouter API integration (fixed in Session 58)
- ✅ Basic command recognition ("load sample", "design all", etc.)
- ✅ Local fallback mode (SmartDesigner)
- ✅ Session state for conversation history

**Workspace Integration:**
- ✅ Hardcoded command handlers in `get_ai_response()`
- ✅ Can trigger state changes (WELCOME → IMPORT → DESIGN → VIEW_3D)
- ✅ Beam selection via regex matching

### 1.2 What's Missing

**Context Awareness:**
- ❌ AI doesn't know our library functions or their signatures
- ❌ AI doesn't understand IS 456 code specifics
- ❌ AI can't see the current workspace state (beams loaded, results)
- ❌ AI has no memory of what the user designed previously

**Tool Use / Function Calling:**
- ❌ AI cannot call `design_beam_is456()` or other API functions
- ❌ AI cannot generate Python code that runs against the library
- ❌ No structured output for design parameters

**Workspace Control:**
- ❌ Limited to 6-7 hardcoded commands
- ❌ Cannot dynamically create visualizations
- ❌ Cannot export results or generate reports

### 1.3 Key Files

| File | Purpose |
|------|---------|
| [pages/11_⚡_ai_assistant_v2.py](../../streamlit_app/pages/11_⚡_ai_assistant_v2.py) | Main AI page (v2) |
| [pages/10_🤖_ai_assistant.py](../../streamlit_app/pages/10_🤖_ai_assistant.py) | Legacy AI page (v1) |
| [components/ai_workspace.py](../../streamlit_app/components/ai_workspace.py) | Dynamic workspace component |
| [structural_lib/api.py](../../Python/structural_lib/api.py) | Public API (50+ functions) |
| [structural_lib/insights.py](../../Python/structural_lib/insights.py) | SmartDesigner for local analysis |

---

## 2. Research Findings

### 2.1 OpenAI Function Calling (Tools)

**Source:** [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)

**How it works:**
```
1. Define tools (JSON schema of functions)
2. Send request with tools + user message
3. Model returns tool_calls if it wants to use tools
4. Execute function locally with model's arguments
5. Send function results back to model
6. Model generates final response
```

**Example function definition:**
```python
tools = [
    {
        "type": "function",
        "name": "design_beam",
        "description": "Design an RC beam per IS 456:2000. Returns required steel area, shear capacity, and pass/fail status.",
        "parameters": {
            "type": "object",
            "properties": {
                "b_mm": {"type": "number", "description": "Beam width in mm"},
                "D_mm": {"type": "number", "description": "Overall depth in mm"},
                "span_mm": {"type": "number", "description": "Beam span in mm"},
                "mu_knm": {"type": "number", "description": "Factored moment in kN·m"},
                "vu_kn": {"type": "number", "description": "Factored shear in kN"},
                "fck_nmm2": {"type": "number", "description": "Concrete grade (default 25)"},
                "fy_nmm2": {"type": "number", "description": "Steel grade (default 500)"},
            },
            "required": ["b_mm", "D_mm", "span_mm", "mu_knm", "vu_kn"],
            "additionalProperties": False
        },
        "strict": True
    }
]
```

**Key learnings:**
- Keep functions < 20 for best accuracy
- Use clear descriptions with units
- Enable `strict: true` for reliable argument parsing
- Function names should be obvious (principle of least surprise)

### 2.2 System Prompt / Context Injection

**Source:** [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)

**Best practices:**
1. **Identity section:** Who the assistant is
2. **Instructions section:** Rules and guidelines
3. **Examples section:** Few-shot demonstrations
4. **Context section:** Dynamic data (workspace state, loaded beams)

**Prompt caching:**
- Static content at start of prompt → cached (lower cost)
- Dynamic content at end → recalculated each request

**Markdown + XML formatting:**
```markdown
# Identity
You are StructEng AI...

# Instructions
* Always use IS 456:2000 for RC design
* Show calculations with IS clause references

# Available Tools
<tool name="design_beam">
Design an RC beam. Parameters: b_mm, D_mm, span_mm, mu_knm, vu_kn...
</tool>

# Current Workspace State
<workspace>
  <beams_loaded>10</beams_loaded>
  <selected_beam>B1_Ground</selected_beam>
  <state>DESIGN</state>
</workspace>
```

### 2.3 OpenRouter Models & Pricing

**Source:** [OpenRouter Models](https://openrouter.ai/models)

**Verified available models (Jan 2026):**

| Model | Context | Input $/M | Output $/M | Best For |
|-------|---------|-----------|------------|----------|
| `openai/gpt-4o-mini` | 128K | $0.15 | $0.60 | Fast, cheap, good |
| `openai/gpt-4o` | 128K | $2.50 | $10.00 | Complex reasoning |
| `openai/gpt-4-turbo` | 128K | $10.00 | $30.00 | Legacy best |
| `anthropic/claude-3.5-sonnet` | 200K | $3.00 | $15.00 | Code, analysis |
| `anthropic/claude-3-haiku` | 200K | $0.25 | $1.25 | Fast, cheap |
| `google/gemini-2.5-pro-preview` | 1M+ | Varies | Varies | Huge context |

**⚠️ IMPORTANT:** Model names change! Always verify via API before hardcoding.

**OpenRouter API key format:** `sk-or-v1-...`
**OpenRouter base URL:** `https://openrouter.ai/api/v1`

### 2.4 Streamlit Chat Patterns

**Source:** [Streamlit Chat Tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)

**Key patterns:**
```python
# Session state for history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input handling
if prompt := st.chat_input("Ask about beam design..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get response (with streaming)
    with st.chat_message("assistant"):
        response = st.write_stream(
            client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=st.session_state.messages,
                stream=True
            )
        )
    st.session_state.messages.append({"role": "assistant", "content": response})
```

---

## 3. Architecture Options

### Option A: Enhanced System Prompt Only

**Approach:**
- Create a comprehensive system prompt with all library documentation
- Inject current workspace state into prompt
- No function calling - AI generates natural language responses only

**Pros:**
- Simplest to implement
- Works with any model
- No API changes needed

**Cons:**
- AI cannot directly execute functions
- Limited to predefined commands
- Cannot handle complex multi-step workflows

**Effort:** 1-2 days

### Option B: Function Calling with OpenAI Tools API

**Approach:**
- Define 10-15 core functions as OpenAI tools
- AI can call `design_beam()`, `show_3d()`, `export_report()`, etc.
- Execute functions locally, return results to AI

**Pros:**
- AI can perform real calculations
- Structured, reliable function arguments
- Scales to complex workflows

**Cons:**
- Requires OpenAI-compatible API (works with OpenRouter)
- More complex error handling
- ~2-3x token usage (tool schemas + results)

**Effort:** 3-5 days

### Option C: Hybrid (Recommended)

**Approach:**
1. **Enhanced system prompt** with library documentation
2. **Lightweight tools** for workspace actions (5-8 functions)
3. **Context injection** for current state

**Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│                    AI ASSISTANT V3                          │
├─────────────────────────────────────────────────────────────┤
│  SYSTEM PROMPT (Cached)                                     │
│  ├── Identity & Guidelines                                  │
│  ├── IS 456 Overview                                        │
│  └── Library API Reference                                  │
├─────────────────────────────────────────────────────────────┤
│  DYNAMIC CONTEXT (Per-request)                              │
│  ├── Workspace State (beams, results, selected)             │
│  ├── Recent Actions                                         │
│  └── User Preferences                                       │
├─────────────────────────────────────────────────────────────┤
│  TOOLS (Function Calling)                                   │
│  ├── design_beam          - Run IS 456 design               │
│  ├── design_all_beams     - Batch design                    │
│  ├── select_beam          - Select for detail view          │
│  ├── show_visualization   - Trigger 3D/2D view              │
│  ├── get_beam_details     - Get detailed results            │
│  ├── suggest_optimization - Get cost/design suggestions     │
│  └── export_results       - Export to CSV/JSON              │
└─────────────────────────────────────────────────────────────┘
```

**Pros:**
- Best of both worlds
- AI understands context AND can take actions
- Efficient token usage (cached static content)

**Cons:**
- Medium complexity
- Requires careful prompt engineering

**Effort:** 4-6 days

---

## 4. Implementation Plan

### Phase 1: Context Document (Day 1)

Create `ai_context.md` with:
- Library overview and philosophy
- API function reference (signatures, examples)
- IS 456 quick reference
- Common workflows

### Phase 2: Enhanced System Prompt (Day 2)

1. Refactor `SYSTEM_PROMPT` into sections
2. Add library function documentation
3. Add dynamic context injection
4. Test with various queries

### Phase 3: Function Calling Tools (Days 3-4)

1. Define tool schemas for 7 core functions
2. Implement tool execution handlers
3. Add streaming support for tool results
4. Handle errors gracefully

### Phase 4: Workspace Integration (Days 5-6)

1. Expose workspace state to AI
2. Allow AI to trigger state transitions
3. Add result visualization hooks
4. Test end-to-end workflows

### Phase 5: Testing & Refinement (Day 7)

1. Test with real ETABS data
2. Optimize prompt for cost/quality
3. Document patterns for future extensions

---

## 5. Context Document Design

### 5.1 File Location

```
streamlit_app/
├── ai/
│   ├── __init__.py
│   ├── context.py          # Dynamic context generation
│   ├── tools.py            # Tool definitions & handlers
│   ├── prompts/
│   │   ├── system.md       # Static system prompt
│   │   ├── is456_ref.md    # IS 456 quick reference
│   │   └── api_ref.md      # Library API reference
│   └── README.md
```

### 5.2 System Prompt Structure

```markdown
# StructEng AI — System Instructions

## Identity
You are StructEng AI, an expert structural engineering assistant...

## Capabilities
You can:
1. Design RC beams per IS 456:2000
2. Analyze and optimize designs for cost
3. Generate 3D visualizations
4. Import data from ETABS, SAFE, CSV

## Guidelines
1. Always cite IS 456 clauses
2. Include units in all values
3. Explain reasoning, not just results
4. Offer follow-up suggestions

## Tools Available
You have access to the following tools:

### design_beam
Design a single beam per IS 456:2000.
Parameters:
- b_mm (required): Beam width in mm
- D_mm (required): Overall depth in mm
...

### design_all_beams
Design all beams in the current workspace.
No parameters required.
...

## Response Format
Start with a brief answer, then provide details.
Use tables for numerical results.
Always offer next steps.
```

### 5.3 API Reference Section

```markdown
## Library API Reference

### design_beam_is456()
Design/check a single IS 456 beam case.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| units | str | Yes | Must be "IS456" |
| mu_knm | float | Yes | Factored moment (kN·m) |
| vu_kn | float | Yes | Factored shear (kN) |
| b_mm | float | Yes | Width (mm) |
| D_mm | float | Yes | Overall depth (mm) |
| d_mm | float | Yes | Effective depth (mm) |
| fck_nmm2 | float | Yes | Concrete grade (N/mm²) |
| fy_nmm2 | float | Yes | Steel grade (N/mm²) |

**Returns:** ComplianceCaseResult with:
- is_ok: bool - Overall pass/fail
- flexure.ast_required: float - Required tension steel (mm²)
- flexure.mu_capacity: float - Moment capacity (kN·m)
- shear.is_ok: bool - Shear check status
- shear.sv_required: float - Required stirrup spacing (mm)

**Example:**
```python
result = design_beam_is456(
    units="IS456",
    mu_knm=150,
    vu_kn=80,
    b_mm=300,
    D_mm=500,
    d_mm=450,
    fck_nmm2=25,
    fy_nmm2=500
)
print(f"Ast = {result.flexure.ast_required:.0f} mm²")
# Ast = 1045 mm²
```

### design_and_detail_beam_is456()
Combined design + detailing in one call.
...
```

### 5.4 Dynamic Context Template

```python
def generate_dynamic_context() -> str:
    """Generate current workspace context for AI."""
    ctx_parts = ["<workspace>"]

    # Beams loaded
    beams_df = st.session_state.get("ws_beams_df")
    if beams_df is not None:
        ctx_parts.append(f"  <beams_loaded>{len(beams_df)}</beams_loaded>")
        ctx_parts.append(f"  <beam_ids>{beams_df['beam_id'].tolist()[:10]}</beam_ids>")

    # Current state
    state = st.session_state.get("ws_state", "WELCOME")
    ctx_parts.append(f"  <state>{state}</state>")

    # Selected beam
    selected = st.session_state.get("ws_selected_beam")
    if selected:
        ctx_parts.append(f"  <selected_beam>{selected}</selected_beam>")
        # Include design results for selected beam
        results_df = st.session_state.get("ws_design_results")
        if results_df is not None:
            beam_row = results_df[results_df["beam_id"] == selected]
            if not beam_row.empty:
                row = beam_row.iloc[0]
                ctx_parts.append(f"  <selected_beam_result>")
                ctx_parts.append(f"    <is_safe>{row.get('is_safe', False)}</is_safe>")
                ctx_parts.append(f"    <ast_required>{row.get('ast_required', 0):.0f}</ast_required>")
                ctx_parts.append(f"    <utilization>{row.get('utilization', 0):.1%}</utilization>")
                ctx_parts.append(f"  </selected_beam_result>")

    # Design summary
    results_df = st.session_state.get("ws_design_results")
    if results_df is not None:
        passed = len(results_df[results_df["is_safe"] == True])
        failed = len(results_df) - passed
        ctx_parts.append(f"  <design_summary>")
        ctx_parts.append(f"    <total>{len(results_df)}</total>")
        ctx_parts.append(f"    <passed>{passed}</passed>")
        ctx_parts.append(f"    <failed>{failed}</failed>")
        ctx_parts.append(f"  </design_summary>")

    ctx_parts.append("</workspace>")
    return "\n".join(ctx_parts)
```

---

## 6. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Model hallucinating function calls | Medium | High | Use `strict: true`, validate inputs |
| High token costs | Medium | Medium | Cache system prompt, limit history |
| API rate limits | Low | Medium | Implement exponential backoff |
| Model unavailable | Low | High | Fallback to local SmartDesigner |
| Wrong IS 456 interpretation | Medium | High | Validate all results, add disclaimers |
| Context window overflow | Low | Medium | Summarize old messages, limit beams shown |

---

## 7. Decision Matrix

| Criterion | Weight | Option A | Option B | Option C |
|-----------|--------|----------|----------|----------|
| Implementation effort | 20% | 5 | 2 | 3 |
| User experience | 30% | 2 | 4 | 5 |
| Extensibility | 20% | 2 | 5 | 4 |
| Cost efficiency | 15% | 5 | 2 | 4 |
| Reliability | 15% | 4 | 3 | 4 |
| **Weighted Score** | 100% | **3.15** | **3.35** | **4.05** |

**Winner: Option C (Hybrid)**

---

## 8. Recommended Approach

### 8.1 Implementation Summary

1. **Create context document** (`ai/prompts/system.md`)
   - 500-800 tokens of static context
   - Library function reference
   - IS 456 quick reference

2. **Define 7 tools:**
   - `design_beam` - Single beam design
   - `design_all` - Batch design
   - `select_beam` - Select for detail
   - `show_view` - Trigger visualization
   - `get_details` - Get beam details
   - `suggest_optimization` - Get suggestions
   - `export` - Export results

3. **Add dynamic context:**
   - Current workspace state
   - Loaded beams summary
   - Selected beam details

4. **Implement tool handlers:**
   - Execute structural_lib functions
   - Format results for AI
   - Update workspace state

### 8.2 Immediate Next Steps

1. **Create `streamlit_app/ai/` directory**
2. **Write `prompts/system.md`** with library documentation
3. **Implement `tools.py`** with tool schemas
4. **Refactor `get_ai_response()`** to use new architecture

### 8.3 Model Selection

**Recommended default:** `openai/gpt-4o-mini`
- Good at function calling
- Low cost ($0.15/$0.60 per M tokens)
- 128K context (more than enough)
- Fast responses (~1-2 seconds)

**For complex analysis:** `openai/gpt-4o` or `anthropic/claude-3.5-sonnet`

### 8.4 Token Budget Estimate

| Component | Tokens | Per Request |
|-----------|--------|-------------|
| System prompt | 600 | Cached |
| API reference | 400 | Cached |
| Dynamic context | 200 | Fresh |
| User message | 50 | Fresh |
| Tool schemas | 300 | Cached |
| **Total input** | ~1550 | ~250 fresh |
| Response | ~300 | - |

**Estimated cost per query:** ~$0.0003 (with caching)

---

## 9. Next Steps

### ✅ Completed (This Session)

- [x] Research OpenAI function calling
- [x] Research OpenRouter models
- [x] Document current state
- [x] Create this research document
- [x] Create `streamlit_app/ai/` directory structure
- [x] Write `prompts/system.md` with library reference
- [x] Implement tool definitions in `tools.py`
- [x] Create `handlers.py` with tool execution logic
- [x] Refactor AI assistant to use new architecture
- [x] Add action-oriented system prompt (no clarifying questions)
- [x] Implement 10 tools: design_beam, design_all, get_beam_details, select_beam, show_visualization, filter_3d_view, get_critical_beams, start_optimization, suggest_optimization, export_results

### Next Session

- [ ] Test with actual user queries (filter floor, list critical beams, optimize)
- [ ] Fine-tune system prompt based on test results
- [ ] Add more workspace actions (export screenshots, rebar schedule)
- [ ] Optimize token usage with context trimming

- [ ] Add code generation capabilities
- [ ] Implement multi-step reasoning chains
- [ ] Add persistent memory (cross-session)
- [ ] Support for custom IS 456 interpretations
- [ ] Voice input/output integration

---

## References

1. [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
2. [OpenAI Prompt Engineering](https://platform.openai.com/docs/guides/prompt-engineering)
3. [OpenRouter Documentation](https://openrouter.ai/docs)
4. [Streamlit LLM Tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)
5. [IS 456:2000](https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf)

---

*Document created during Session 58 - AI Assistant Workspace Integration Research*
