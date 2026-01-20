# AI Module for StructEng App

This module provides context-aware AI assistant capabilities.

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Module exports |
| `context.py` | Dynamic context generation for AI prompts |
| `tools.py` | Function calling tool definitions |
| `prompts/system.md` | Static system prompt with library documentation |

## Usage

```python
from streamlit_app.ai import (
    build_messages,
    get_tools,
    load_system_prompt,
    generate_workspace_context
)

# Build messages for API call
messages = build_messages(
    user_message="Design beam B1 with 150 kN·m moment",
    history=st.session_state.messages,
    include_workspace=True
)

# Get tool definitions for function calling
tools = get_tools()

# Make API call
response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)
```

## Architecture

```
ai/
├── __init__.py          # Module exports
├── context.py           # Dynamic context generation
├── tools.py             # Tool schemas for function calling
├── prompts/
│   ├── system.md        # Main system prompt
│   ├── is456_ref.md     # IS 456 quick reference (future)
│   └── api_ref.md       # Library API reference (future)
└── README.md            # This file
```

## Tool Definitions

The following tools are defined for function calling:

1. **design_beam** - Design a single RC beam
2. **design_all_beams** - Batch design all loaded beams
3. **get_beam_details** - Get detailed results for a beam
4. **select_beam** - Select beam for visualization
5. **show_visualization** - Trigger 3D/dashboard views
6. **suggest_optimization** - Get optimization suggestions
7. **export_results** - Export to CSV/JSON/Excel

## Context Injection

The `generate_workspace_context()` function creates XML-formatted context:

```xml
<workspace>
  <beams_loaded>10</beams_loaded>
  <beam_ids>['B1_Ground', 'B2_Ground', ...]</beam_ids>
  <state>DESIGN</state>
  <selected_beam>B1_Ground</selected_beam>
  <selected_beam_details>
    <is_safe>True</is_safe>
    <ast_required>785</ast_required>
    <ast_provided>829</ast_provided>
    <moment_utilization>69.5%</moment_utilization>
  </selected_beam_details>
  <design_summary>
    <total>10</total>
    <passed>8</passed>
    <failed>2</failed>
    <failed_beams>['B3_First', 'B7_Ground']</failed_beams>
  </design_summary>
</workspace>
```

## Integration

To integrate with the AI assistant page:

1. Import the module functions
2. Replace hardcoded system prompt with `load_system_prompt()`
3. Use `build_messages()` to construct API requests
4. Pass `get_tools()` to enable function calling
5. Implement tool handlers for each function

See [ai-assistant-workspace-integration.md](../../docs/research/ai-assistant-workspace-integration.md) for full implementation plan.
