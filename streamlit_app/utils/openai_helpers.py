# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""OpenAI client helper utilities.

Provides shared OpenAI client initialization for AI-powered pages.
Supports both OpenAI and OpenRouter API endpoints.

Created: 2026-01-24 (Session 70 - UI Duplication Fix)
"""

from __future__ import annotations

from typing import Any

import streamlit as st

# Try to import OpenAI
try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None  # type: ignore


def get_openai_client() -> "OpenAI | None":
    """Get OpenAI client if API key is available.

    Supports both OpenAI and OpenRouter API keys:
    - OpenAI: sk-...
    - OpenRouter: sk-or-v1-...

    Returns:
        OpenAI client instance or None if unavailable

    Example:
        >>> client = get_openai_client()
        >>> if client:
        ...     response = client.chat.completions.create(...)
    """
    if not OPENAI_AVAILABLE:
        return None

    api_key = st.secrets.get("OPENAI_API_KEY", None)
    if not api_key:
        return None

    # OpenRouter uses different base URL
    if api_key.startswith("sk-or-"):
        return OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    return OpenAI(api_key=api_key)


def get_openai_config() -> dict[str, Any]:
    """Get OpenAI configuration from secrets.

    Returns:
        Dict with model, temperature, and max_tokens settings
    """
    # Default model - gpt-4o-mini is fast, cost-efficient
    model = "gpt-4o-mini"
    temperature = 0.7
    max_tokens = 2000

    if "openai" in st.secrets:
        openai_config = st.secrets["openai"]
        model = openai_config.get("model", model)
        temperature = openai_config.get("temperature", temperature)
        max_tokens = openai_config.get("max_tokens", max_tokens)

    return {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }


def is_openai_available() -> bool:
    """Check if OpenAI is available and configured.

    Returns:
        True if OpenAI library is installed and API key is configured
    """
    if not OPENAI_AVAILABLE:
        return False
    return bool(st.secrets.get("OPENAI_API_KEY", None))
