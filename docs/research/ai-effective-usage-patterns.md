# Effective AI Usage Patterns for Structural Engineering

**Type:** Research
**Audience:** Developers
**Status:** Draft
**Importance:** High
**Created:** 2026-01-20
**Last Updated:** 2026-01-20
**Related Tasks:** TASK-AI-CHAT

---

## Overview

This document captures research and best practices for effective AI integration in the StructEng AI Assistant. It covers model selection, prompt engineering, and usage patterns specific to structural engineering applications.

---

## 1. Model Selection (January 2026)

### Available Models

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| **gpt-5-mini** | ⚡ Fast | $0.25/1M tokens | **RECOMMENDED** - Quick design assistance |
| gpt-5 | Medium | $1.75/1M tokens | Complex reasoning, code generation |
| gpt-5.2 | Medium | ~$2/1M tokens | Agentic tasks, multi-step workflows |
| gpt-4.1 | Fast | $0.50/1M tokens | Non-reasoning, simple queries |
| gpt-4o-mini | Fast | $0.15/1M tokens | Legacy support, budget-conscious |

### Configuration in `secrets.toml`

```toml
[openai]
model = "gpt-5-mini"
temperature = 0.7
max_tokens = 2000
```

### Temperature Guidelines

| Use Case | Temperature | Reasoning |
|----------|-------------|-----------|
| Design calculations | 0.3-0.5 | Deterministic, consistent results |
| Explanations & advice | 0.7 | Balanced creativity |
| Brainstorming | 0.9 | More varied suggestions |

---

## 2. System Prompt Engineering

### Current System Prompt Structure

```python
SYSTEM_PROMPT = """
You are StructEng AI, an expert structural engineering assistant specializing in
IS 456 reinforced concrete design.

## Your Capabilities:
- Design RC beams for moment and shear (IS 456:2000)
- Optimize designs for cost, safety, or constructability
- Explain code clauses in simple terms
- Provide practical engineering advice

## Guidelines:
1. Be practical - Engineers want actionable advice
2. Be specific - Always include numbers
3. Show your work - Explain reasoning
4. Follow IS 456 - All designs must comply

## Important:
- Never fabricate structural calculations
- If uncertain, say so
- Always prioritize safety over economy
"""
```

### Best Practices for Engineering AI

1. **Be domain-specific**: Reference IS 456:2000 explicitly
2. **Enforce safety**: System prompt emphasizes safety over economy
3. **Require numbers**: Engineers need quantitative answers
4. **Acknowledge limits**: Explicitly state uncertainty handling

---

## 3. Function Calling Integration

### Tool Definitions (7 Tools)

1. **design_beam** - Create new beam design
2. **optimize_cost** - Cost optimization analysis
3. **get_suggestions** - Design improvement suggestions
4. **analyze_design** - Comprehensive SmartDesigner analysis
5. **compare_options** - Compare design alternatives
6. **explain_code_clause** - IS 456 clause explanations
7. **show_3d_view** - Switch to 3D visualization

### Local Fallback (SmartDesigner)

When OpenAI API is unavailable, we use SmartDesigner for:
- Cost analysis and optimization
- Design scoring (safety, cost, constructability)
- Quick wins and suggestions
- Constructability assessment

This provides AI-like intelligence without API dependency.

---

## 4. Usage Patterns

### Pattern 1: Design-First Workflow

```
User: "Design a beam for 150 kN·m"
  ↓
Parse parameters from natural language
  ↓
Call structural_api.design_beam_is456()
  ↓
Format response with design summary
  ↓
Offer follow-up actions (optimize, analyze, 3D)
```

### Pattern 2: Iterative Refinement

```
User: "Design a beam"
  ↓ Create initial design
User: "Optimize cost"
  ↓ Run SmartDesigner analysis
User: "Show 3D"
  ↓ Switch workspace tab to 3D view
User: "Make it deeper"
  ↓ Update parameters, redesign
```

### Pattern 3: Batch Processing

```
User: Uploads CSV with 100 beams
  ↓
Parse columns (b, D, Mu, Vu)
  ↓
Batch design all beams
  ↓
Show summary: "85 SAFE, 15 UNSAFE"
  ↓
User can analyze individual beams via chat
```

---

## 5. Response Formatting

### Engineering Response Template

```markdown
I've designed a beam for your requirements:

**Design Summary:**
- Section: **300×500mm**
- Steel Area Required: **557 mm²**
- Utilization: **49.3%**
- Status: ✅ **SAFE**

The design uses M25 concrete and Fe500 steel.

Would you like me to:
1. 💰 Optimize for cost?
2. 📊 Show detailed analysis?
3. 🎨 View in 3D?
```

### Key Principles

1. **Start with answer** - Engineers want results first
2. **Use metrics** - Numbers, percentages, status
3. **Visual formatting** - Bold key values, emoji status
4. **Offer next steps** - Don't dead-end the conversation

---

## 6. Error Handling

### Graceful Degradation

```python
try:
    # Try OpenAI API
    response = client.chat.completions.create(...)
except Exception as e:
    # Fall back to local SmartDesigner
    return simulate_ai_response(user_message)
```

### User-Friendly Error Messages

```python
# Bad: Technical error
"Analysis failed: NoneType has no attribute 'cost'"

# Good: Actionable message
"Analysis failed: Try redesigning the beam first."
```

---

## 7. Future Enhancements

### V1.1 Roadmap

1. **Multi-turn context** - Remember conversation history better
2. **Code clause lookup** - Indexed IS 456 knowledge base
3. **Drawing integration** - Generate detailing sketches
4. **Comparative analysis** - "Compare 3 design options"

### V2.0 Vision

1. **Multi-code support** - ACI 318, EC2
2. **Agentic workflows** - Multi-step design optimization
3. **Learning from feedback** - Improve suggestions over time

---

## References

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [SmartDesigner Implementation](../../Python/structural_lib/insights/smart_designer.py)
- [AI Chat Architecture](ai-chat-architecture-v2.md)
- [secrets.toml.example](../../streamlit_app/.streamlit/secrets.toml.example)
