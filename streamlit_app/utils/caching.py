"""
Caching utilities for Streamlit app performance optimization.

This module provides smart caching strategies for expensive operations:
- Design calculations
- Visualization generation
- Database queries
- Theme/config objects

Key Features:
- Function-level caching with @st.cache_data
- Resource caching with @st.cache_resource
- TTL-based cache expiration
- Input hashing for cache keys
- Cache warming on startup

Usage:
    from streamlit_app.utils.caching import cached_design_beam, get_cached_theme

    result = cached_design_beam(span=5000, width=300, depth=500, ...)
    theme = get_cached_theme()
"""

import hashlib
import json
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple

import streamlit as st

# Cache TTL settings (in seconds)
TTL_DESIGN_RESULTS = 3600  # 1 hour - design calculations
TTL_VISUALIZATIONS = 1800  # 30 minutes - plots/charts
TTL_DATABASE = 7200  # 2 hours - material/code tables
TTL_SHORT = 300  # 5 minutes - frequently changing data


class SmartCache:
    """
    Simple in-memory cache with TTL and statistics tracking.

    Features:
    - Time-to-live (TTL) expiration
    - Memory usage tracking
    - Hit/miss statistics
    - Size limits

    Example:
        >>> cache = SmartCache(max_size_mb=50, ttl_seconds=300)
        >>> cache.set("key1", result)
        >>> value = cache.get("key1")
        >>> stats = cache.get_stats()
    """

    def __init__(self, max_size_mb: int = 50, ttl_seconds: int = 300):
        """
        Initialize cache.

        Args:
            max_size_mb: Maximum cache size in megabytes
            ttl_seconds: Time-to-live for cache entries in seconds
        """
        self.max_size_mb = max_size_mb
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[Any, float]] = {}  # key: (value, timestamp)
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            # Check if expired
            if time.time() - timestamp < self.ttl_seconds:
                self._hits += 1
                return value
            else:
                # Expired, remove it
                del self._cache[key]

        self._misses += 1
        return None

    def set(self, key: str, value: Any) -> None:
        """Set value in cache with current timestamp."""
        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

        return {
            "size": len(self._cache),
            "hit_rate": hit_rate,
            "hits": self._hits,
            "misses": self._misses,
            "memory_mb": len(self._cache) * 0.1,  # Rough estimate
        }


def hash_inputs(*args, **kwargs) -> str:
    """
    Create stable hash from function inputs for cache key.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        str: SHA256 hash of inputs

    Example:
        >>> hash_inputs(5000, 300, fck=25)
        'a3f7...'
    """
    # Convert to JSON-serializable dict
    data = {
        "args": args,
        "kwargs": kwargs
    }

    # Create stable JSON string
    json_str = json.dumps(data, sort_keys=True, default=str)

    # Hash it
    return hashlib.sha256(json_str.encode()).hexdigest()[:16]


@st.cache_data(ttl=TTL_DESIGN_RESULTS, show_spinner="Calculating design...")
def cached_design_beam(
    span_mm: float,
    width_mm: float,
    depth_mm: float,
    fck: float,
    fy: float,
    cover_mm: float,
    load_udl_kn_m: float,
    load_ll_kn_m: Optional[float] = None,
    exposure: str = "moderate",
    bar_dia: int = 16,
) -> Dict[str, Any]:
    """
    Cache beam design results for 1 hour.

    Args:
        span_mm: Beam span in mm
        width_mm: Section width in mm
        depth_mm: Section depth in mm
        fck: Concrete grade (N/mm²)
        fy: Steel grade (N/mm²)
        cover_mm: Clear cover in mm
        load_udl_kn_m: Dead load UDL (kN/m)
        load_ll_kn_m: Live load UDL (kN/m), optional
        exposure: Exposure condition
        bar_dia: Main bar diameter (mm)

    Returns:
        dict: Design results with keys:
            - ast_required: Steel area required (mm²)
            - spacing: Stirrup spacing (mm)
            - status: Overall status
            - flexure_result: Flexure design details
            - shear_result: Shear design details

    Example:
        >>> result = cached_design_beam(5000, 300, 500, 25, 415, 40, 10.5)
        >>> result['ast_required']
        682.4
    """
    from streamlit_app.utils.api_wrapper import design_beam

    return design_beam(
        span_mm=span_mm,
        width_mm=width_mm,
        depth_mm=depth_mm,
        fck=fck,
        fy=fy,
        cover_mm=cover_mm,
        load_udl_kn_m=load_udl_kn_m,
        load_ll_kn_m=load_ll_kn_m,
        exposure=exposure,
        bar_dia=bar_dia,
    )


@st.cache_data(ttl=TTL_VISUALIZATIONS, show_spinner="Generating chart...")
def cached_beam_diagram(
    span_mm: float,
    width_mm: float,
    depth_mm: float,
    ast_provided: float,
    xu: Optional[float] = None,
    show_strain: bool = True,
) -> Any:
    """
    Cache beam diagram generation for 30 minutes.

    Args:
        span_mm: Beam span
        width_mm: Section width
        depth_mm: Section depth
        ast_provided: Provided steel area
        xu: Neutral axis depth (optional)
        show_strain: Show strain diagram

    Returns:
        plotly.graph_objects.Figure: Cached figure
    """
    from streamlit_app.components.visualizations import create_beam_diagram

    return create_beam_diagram(
        span_mm=span_mm,
        width_mm=width_mm,
        depth_mm=depth_mm,
        ast_provided=ast_provided,
        xu=xu,
        show_strain=show_strain,
    )


@st.cache_data(ttl=TTL_VISUALIZATIONS, show_spinner=False)
def cached_plotly_chart(
    chart_type: str,
    data: Dict[str, Any],
    layout: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Cache generic Plotly chart generation.

    Args:
        chart_type: Type of chart ('bar', 'line', 'scatter', etc.)
        data: Chart data dictionary
        layout: Optional layout configuration

    Returns:
        plotly.graph_objects.Figure: Cached figure
    """
    import plotly.graph_objects as go

    # Create figure based on type
    if chart_type == "bar":
        fig = go.Figure(data=[go.Bar(**data)])
    elif chart_type == "line":
        fig = go.Figure(data=[go.Scatter(**data)])
    elif chart_type == "scatter":
        fig = go.Figure(data=[go.Scatter(mode='markers', **data)])
    else:
        raise ValueError(f"Unknown chart type: {chart_type}")

    # Apply layout if provided
    if layout:
        fig.update_layout(**layout)

    return fig


@st.cache_resource
def get_cached_theme() -> Dict[str, Any]:
    """Cache Plotly theme object (singleton).

    This caches the theme configuration as a resource that persists
    across reruns and is shared by all users.

    Returns:
        dict: Plotly theme configuration

    Example:
        >>> theme = get_cached_theme()
        >>> fig.update_layout(**theme)
    """
    from streamlit_app.utils.plotly_theme import get_plotly_theme

    return get_plotly_theme()


@st.cache_resource
def get_design_system_tokens() -> Any:
    """Cache design system tokens (singleton).

    Returns:
        module: Design system tokens module
    """
    from streamlit_app.utils import design_system

    return design_system


@st.cache_data(ttl=TTL_DATABASE)
def cached_material_database() -> Dict[str, Any]:
    """
    Cache material properties database.

    Returns:
        dict: Material properties by grade
            - concrete: {M20: {...}, M25: {...}, ...}
            - steel: {Fe415: {...}, Fe500: {...}, ...}
    """
    return {
        "concrete": {
            "M20": {"fck": 20, "ec": 22360},
            "M25": {"fck": 25, "ec": 25000},
            "M30": {"fck": 30, "ec": 27386},
            "M35": {"fck": 35, "ec": 29580},
            "M40": {"fck": 40, "ec": 31623},
        },
        "steel": {
            "Fe415": {"fy": 415, "es": 200000},
            "Fe500": {"fy": 500, "es": 200000},
            "Fe550": {"fy": 550, "es": 200000},
        }
    }


@st.cache_data(ttl=TTL_DATABASE)
def cached_code_tables() -> Dict[str, Any]:
    """
    Cache IS 456 code tables.

    Returns:
        dict: Code tables by table number
    """
    return {
        "table_16": {  # Min cover for exposure
            "mild": 20,
            "moderate": 30,
            "severe": 45,
            "very_severe": 50,
            "extreme": 75,
        },
        "table_19": {  # Design shear strength
            # Grade: {pt: tau_c}
            "M20": {0.15: 0.28, 0.25: 0.35, 0.50: 0.48},
            "M25": {0.15: 0.29, 0.25: 0.36, 0.50: 0.49},
        }
    }


def cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics.

    Returns:
        dict: Cache stats with keys:
            - cache_hit_rate: Percentage of cache hits
            - cache_size: Total cached objects
            - cache_memory: Estimated memory usage (MB)

    Note:
        This is a placeholder - Streamlit doesn't expose cache metrics yet.
    """
    return {
        "cache_hit_rate": "N/A (Streamlit doesn't expose this)",
        "cache_size": "N/A",
        "cache_memory": "N/A",
        "note": "Use st.cache_data.clear() to clear all caches"
    }


def clear_all_caches() -> None:
    """Clear all Streamlit caches.

    Use this when:
    - Switching projects
    - After library updates
    - When memory usage is high
    - For testing/debugging

    Example:
        >>> clear_all_caches()
        >>> st.success("All caches cleared!")
    """
    st.cache_data.clear()
    st.cache_resource.clear()


def warm_caches() -> None:
    """Pre-load common data into caches on app startup.

    This reduces first-load latency by caching frequently used data.
    Call this in the main app initialization.

    Example:
        >>> if 'caches_warmed' not in st.session_state:
        >>>     warm_caches()
        >>>     st.session_state.caches_warmed = True
    """
    # Pre-load material database
    cached_material_database()

    # Pre-load code tables
    cached_code_tables()

    # Pre-load theme
    get_cached_theme()

    # Pre-load design tokens
    get_design_system_tokens()


# Performance decorator for custom caching logic
def timed_cache(ttl: int = 300) -> Callable[[Callable], Callable]:
    """Decorator for custom caching with timing.

    Args:
        ttl: Time to live in seconds

    Returns:
        Callable: Decorated function with caching

    Example:
        >>> @timed_cache(ttl=600)
        >>> def expensive_function(x):
        >>>     return x ** 2
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Use st.cache_data with specified TTL
            cached_func = st.cache_data(ttl=ttl)(func)
            return cached_func(*args, **kwargs)
        return wrapper
    return decorator


# Example usage in docstring
if __name__ == "__main__":
    # This won't run in Streamlit, just for documentation
    print("Caching utilities loaded")
    print(f"Design results TTL: {TTL_DESIGN_RESULTS}s")
    print(f"Visualizations TTL: {TTL_VISUALIZATIONS}s")
    print(f"Database TTL: {TTL_DATABASE}s")
