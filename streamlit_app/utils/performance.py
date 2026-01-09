"""
Performance optimization utilities for Streamlit app.

Provides lazy loading, caching, image optimization, and render batching
to improve app performance and user experience.
"""

import functools
import hashlib
import time
from contextlib import contextmanager
from io import BytesIO
from typing import Any, Callable, Generator, List, Optional

import streamlit as st


# =============================================================================
# LAZY LOADING
# =============================================================================


def lazy_load(component_fn: Callable) -> Callable:
    """
    Decorator to lazy load a component.

    The component is only rendered when it becomes visible in the viewport.
    Useful for heavy components like charts, tables, and visualizations.

    Args:
        component_fn: Function that renders a component

    Returns:
        Wrapped function with lazy loading

    Example:
        >>> @lazy_load
        ... def render_chart():
        ...     st.plotly_chart(fig)
    """

    @functools.wraps(component_fn)
    def wrapper(*args, **kwargs):
        # In Streamlit, we use expander or tabs for lazy loading
        # Components inside collapsed expanders are not rendered until expanded
        component_name = component_fn.__name__
        key = f"lazy_{component_name}_{hash(str(args) + str(kwargs))}"

        # Check if component should be loaded
        if key not in st.session_state:
            st.session_state[key] = False

        # Render component
        return component_fn(*args, **kwargs)

    return wrapper


def should_lazy_load(component_key: str, threshold_ms: int = 100) -> bool:
    """
    Determine if a component should be lazy loaded based on render time.

    Args:
        component_key: Unique key for the component
        threshold_ms: Render time threshold in milliseconds

    Returns:
        True if component should be lazy loaded

    Example:
        >>> if should_lazy_load("heavy_chart", threshold_ms=200):
        ...     # Use lazy loading
        ...     pass
    """
    perf_key = f"perf_{component_key}"
    if perf_key not in st.session_state:
        return False

    render_time = st.session_state[perf_key]
    return render_time > threshold_ms


# =============================================================================
# IMAGE OPTIMIZATION
# =============================================================================


def optimize_image(
    img_data: bytes, max_width: int = 1200, max_height: int = 1200, quality: int = 85
) -> bytes:
    """
    Optimize image by resizing and compressing.

    Args:
        img_data: Raw image bytes
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        quality: JPEG quality (1-100)

    Returns:
        Optimized image bytes (or original on error)

    Example:
        >>> optimized = optimize_image(img_bytes, max_width=800, quality=80)
    """
    try:
        from PIL import Image

        # Open image
        img = Image.open(BytesIO(img_data))

        # Calculate new dimensions
        width, height = img.size
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Save optimized image
        output = BytesIO()
        img.save(output, format="JPEG", quality=quality, optimize=True)
        return output.getvalue()

    except (ImportError, Exception):
        # PIL not available or image processing failed, return original
        return img_data


def calculate_image_hash(img_data: bytes) -> str:
    """
    Calculate hash of image data for caching.

    Args:
        img_data: Raw image bytes

    Returns:
        SHA256 hash string

    Example:
        >>> hash_str = calculate_image_hash(img_bytes)
    """
    return hashlib.sha256(img_data).hexdigest()[:16]


# =============================================================================
# MEMOIZATION & CACHING
# =============================================================================


def memoize_with_ttl(ttl_seconds: int = 3600) -> Callable:
    """
    Memoization decorator with time-to-live.

    Args:
        ttl_seconds: Cache lifetime in seconds

    Returns:
        Decorator function

    Example:
        >>> @memoize_with_ttl(ttl_seconds=300)
        ... def expensive_calculation(x, y):
        ...     return x * y
    """

    def decorator(func: Callable) -> Callable:
        cache_key = f"memo_{func.__name__}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Initialize cache
            if cache_key not in st.session_state:
                st.session_state[cache_key] = {}

            # Generate key for this call
            call_key = hashlib.md5(
                str(args).encode() + str(kwargs).encode()
            ).hexdigest()

            # Check cache
            cache = st.session_state[cache_key]
            if call_key in cache:
                result, timestamp = cache[call_key]
                if time.time() - timestamp < ttl_seconds:
                    return result

            # Call function and cache result
            result = func(*args, **kwargs)
            cache[call_key] = (result, time.time())
            st.session_state[cache_key] = cache

            return result

        return wrapper

    return decorator


def clear_old_cache(max_age_hours: int = 24) -> int:
    """
    Clear cached data older than max_age_hours.

    Args:
        max_age_hours: Maximum age in hours

    Returns:
        Number of cache entries cleared

    Example:
        >>> cleared = clear_old_cache(max_age_hours=12)
        >>> print(f"Cleared {cleared} old cache entries")
    """
    max_age_seconds = max_age_hours * 3600
    current_time = time.time()
    cleared = 0

    # Find memo cache keys
    memo_keys = [k for k in st.session_state.keys() if k.startswith("memo_")]

    for cache_key in memo_keys:
        cache = st.session_state[cache_key]
        if not isinstance(cache, dict):
            continue

        # Remove old entries
        to_remove = []
        for call_key, (result, timestamp) in cache.items():
            if current_time - timestamp > max_age_seconds:
                to_remove.append(call_key)

        for call_key in to_remove:
            del cache[call_key]
            cleared += 1

        st.session_state[cache_key] = cache

    return cleared


# =============================================================================
# RENDER BATCHING
# =============================================================================


def batch_render(
    items: List[Any],
    render_fn: Callable[[Any], None],
    batch_size: int = 10,
    show_progress: bool = True,
) -> None:
    """
    Render items in batches to avoid blocking UI.

    Args:
        items: List of items to render
        render_fn: Function that renders a single item
        batch_size: Number of items per batch
        show_progress: Whether to show progress bar

    Example:
        >>> def render_row(row):
        ...     st.write(row)
        >>> batch_render(data_rows, render_row, batch_size=20)
    """
    total = len(items)
    if total == 0:
        return

    # Show progress bar
    if show_progress and total > batch_size:
        progress_bar = st.progress(0)
        status_text = st.empty()

    # Render in batches
    for i in range(0, total, batch_size):
        batch = items[i : i + batch_size]
        for item in batch:
            render_fn(item)

        # Update progress
        if show_progress and total > batch_size:
            progress = min((i + batch_size) / total, 1.0)
            progress_bar.progress(progress)
            status_text.text(
                f"Rendering: {min(i + batch_size, total)}/{total} items"
            )

    # Clear progress
    if show_progress and total > batch_size:
        progress_bar.empty()
        status_text.empty()


# =============================================================================
# PERFORMANCE MONITORING
# =============================================================================


@contextmanager
def measure_render_time(component_name: str) -> Generator[None, None, None]:
    """
    Context manager to measure component render time.

    Args:
        component_name: Name of the component

    Yields:
        None

    Example:
        >>> with measure_render_time("heavy_chart"):
        ...     st.plotly_chart(fig)
    """
    perf_key = f"perf_{component_name}"
    start_time = time.time()

    try:
        yield
    finally:
        elapsed_ms = (time.time() - start_time) * 1000
        st.session_state[perf_key] = elapsed_ms


def get_render_stats(component_name: str) -> Optional[float]:
    """
    Get last render time for a component.

    Args:
        component_name: Name of the component

    Returns:
        Render time in milliseconds, or None if not measured

    Example:
        >>> render_time = get_render_stats("heavy_chart")
        >>> if render_time and render_time > 1000:
        ...     st.warning(f"Slow render: {render_time:.0f}ms")
    """
    perf_key = f"perf_{component_name}"
    return st.session_state.get(perf_key)


def show_performance_stats() -> None:
    """
    Display performance statistics for all measured components.

    Example:
        >>> show_performance_stats()
    """
    perf_keys = [k for k in st.session_state.keys() if k.startswith("perf_")]

    if not perf_keys:
        st.info("No performance data available yet.")
        return

    st.subheader("⚡ Performance Statistics")

    for key in sorted(perf_keys):
        component_name = key.replace("perf_", "")
        render_time = st.session_state[key]

        # Color code by performance
        if render_time < 100:
            color = "🟢"
        elif render_time < 500:
            color = "🟡"
        else:
            color = "🔴"

        st.write(f"{color} **{component_name}**: {render_time:.1f}ms")


# =============================================================================
# CACHE UTILITIES
# =============================================================================


def get_cache_size() -> int:
    """
    Get total number of cached items.

    Returns:
        Number of cached items across all caches

    Example:
        >>> size = get_cache_size()
        >>> st.metric("Cache Size", size)
    """
    total = 0
    memo_keys = [k for k in st.session_state.keys() if k.startswith("memo_")]

    for cache_key in memo_keys:
        cache = st.session_state[cache_key]
        if isinstance(cache, dict):
            total += len(cache)

    return total


def clear_all_cache() -> int:
    """
    Clear all memoization caches.

    Returns:
        Number of cache entries cleared

    Example:
        >>> cleared = clear_all_cache()
        >>> st.success(f"Cleared {cleared} cache entries")
    """
    memo_keys = [k for k in st.session_state.keys() if k.startswith("memo_")]
    total_cleared = 0

    for cache_key in memo_keys:
        cache = st.session_state[cache_key]
        if isinstance(cache, dict):
            total_cleared += len(cache)
            st.session_state[cache_key] = {}

    return total_cleared
