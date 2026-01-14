"""
Rendering Optimization Utilities
Batch rendering, fragment management, and render cycle optimization.
"""
from typing import Any, Callable, Dict, List, Optional
import streamlit as st
from functools import wraps
import time


class RenderBatcher:
    """Batch multiple render operations for better performance."""

    def __init__(self):
        self._batches: Dict[str, List[Callable]] = {}

    def add_to_batch(self, batch_id: str, render_func: Callable) -> None:
        """Add render function to a batch.

        Args:
            batch_id: Batch identifier
            render_func: Function to call during render
        """
        if batch_id not in self._batches:
            self._batches[batch_id] = []

        self._batches[batch_id].append(render_func)

    def render_batch(self, batch_id: str) -> None:
        """Render all functions in a batch.

        Args:
            batch_id: Batch to render
        """
        if batch_id not in self._batches:
            return

        batch = self._batches[batch_id]

        # Render all at once
        for render_func in batch:
            render_func()

        # Clear batch after rendering
        self._batches[batch_id] = []

    def clear_batch(self, batch_id: str) -> None:
        """Clear a batch without rendering."""
        if batch_id in self._batches:
            self._batches[batch_id] = []

    def clear_all(self) -> None:
        """Clear all batches."""
        self._batches.clear()


# Global render batcher
_render_batcher = RenderBatcher()


def batch_render(batch_id: str) -> Callable[[Callable], Callable]:
    """Decorator to add function to render batch.

    Usage:
        @batch_render('metrics_section')
        def render_metric1():
            st.metric("Value", 100)

    Args:
        batch_id: Batch identifier

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> None:
            # Add to batch instead of immediate render
            _render_batcher.add_to_batch(batch_id, lambda: func(*args, **kwargs))

        return wrapper
    return decorator


def flush_render_batch(batch_id: str) -> None:
    """Flush (render) a specific batch.

    Args:
        batch_id: Batch to render
    """
    _render_batcher.render_batch(batch_id)


class FragmentManager:
    """Manage Streamlit fragments for partial rerenders."""

    @staticmethod
    def create_isolated_fragment(func: Callable, run_every: Optional[float] = None) -> Callable:
        """Create isolated fragment that doesn't trigger full rerun.

        Args:
            func: Function to wrap in fragment
            run_every: Optional auto-rerun interval in seconds

        Returns:
            Wrapped fragment function
        """
        # Note: st.fragment introduced in Streamlit 1.30+
        # For older versions, this is a no-op wrapper
        try:
            if run_every:
                return st.fragment(func, run_every=run_every)
            else:
                return st.fragment(func)
        except AttributeError:
            # Streamlit version doesn't support fragments
            return func

    @staticmethod
    def update_fragment_state(fragment_key: str, value: Any) -> None:
        """Update state for a specific fragment.

        Args:
            fragment_key: Fragment identifier
            value: New value
        """
        state_key = f"_fragment_{fragment_key}"
        st.session_state[state_key] = value

    @staticmethod
    def get_fragment_state(fragment_key: str, default: Any = None) -> Any:
        """
        Get state for a specific fragment.

        Args:
            fragment_key: Fragment identifier
            default: Default value if not found

        Returns:
            Fragment state value
        """
        state_key = f"_fragment_{fragment_key}"
        return st.session_state.get(state_key, default)


def optimize_render_cycle(func: Callable) -> Callable:
    """Decorator to optimize render cycle by skipping unnecessary rerenders.

    Usage:
        @optimize_render_cycle
        def render_expensive_component():
            # Expensive rendering code
            pass

    Args:
        func: Function to optimize

    Returns:
        Optimized function
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Optional[Any]:
        # Create state key for this function
        func_key = f"_render_hash_{func.__name__}"

        # Compute hash of arguments
        arg_hash = hash((args, tuple(sorted(kwargs.items()))))

        # Check if we've rendered with same args before
        if func_key in st.session_state:
            if st.session_state[func_key] == arg_hash:
                # Same args, skip rerender
                return None

        # Different args or first render
        result = func(*args, **kwargs)
        st.session_state[func_key] = arg_hash

        return result

    return wrapper


def debounce_render(delay_ms: int = 300) -> Callable[[Callable], Callable]:
    """Debounce rendering to avoid excessive rerenders.

    Args:
        delay_ms: Delay in milliseconds

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[Any]:
            # Get last render time
            time_key = f"_debounce_{func.__name__}"

            if time_key in st.session_state:
                elapsed = (time.time() - st.session_state[time_key]) * 1000

                if elapsed < delay_ms:
                    # Too soon, skip render
                    return None

            # Enough time passed, render
            result = func(*args, **kwargs)
            st.session_state[time_key] = time.time()

            return result

        return wrapper
    return decorator


class ConditionalRenderer:
    """Render components conditionally to save resources."""

    @staticmethod
    def render_if_visible(container_name: str, render_func: Callable) -> None:
        """Render only if container is visible/expanded.

        Args:
            container_name: Name of container
            render_func: Function to call if visible
        """
        # Check visibility state
        visibility_key = f"_visible_{container_name}"

        if st.session_state.get(visibility_key, True):
            render_func()

    @staticmethod
    def render_if_changed(watch_keys: List[str], render_func: Callable) -> None:
        """Render only if watched state keys changed.

        Args:
            watch_keys: List of state keys to watch
            render_func: Function to call if any key changed
        """
        # Create hash of watched values
        watched_values = tuple(st.session_state.get(k) for k in watch_keys)
        watch_hash = hash(watched_values)

        hash_key = f"_watch_hash_{render_func.__name__}"

        # Check if changed
        if hash_key not in st.session_state or st.session_state[hash_key] != watch_hash:
            render_func()
            st.session_state[hash_key] = watch_hash

    @staticmethod
    def lazy_render(threshold_px: int = 800) -> Callable[[Callable], Callable]:
        """Lazy render components below the fold.

        Args:
            threshold_px: Pixel threshold for lazy loading

        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                # In Streamlit, we can't directly detect scroll position
                # So this is a simplified version that just renders
                # In a real implementation, this would use JS
                return func(*args, **kwargs)

            return wrapper
        return decorator


def render_with_profiling(func: Callable) -> Callable:
    """Decorator to profile render time.

    Usage:
        @render_with_profiling
        def render_chart():
            # Expensive rendering
            pass

    Args:
        func: Function to profile

    Returns:
        Wrapped function that logs timing
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = (time.time() - start_time) * 1000

        # Store timing metrics
        metrics_key = '_render_metrics'
        if metrics_key not in st.session_state:
            st.session_state[metrics_key] = {}

        st.session_state[metrics_key][func.__name__] = {
            'last_render_ms': elapsed,
            'timestamp': time.time()
        }

        # Log if slow
        if elapsed > 100:  # > 100ms
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Slow render: {func.__name__} took {elapsed:.1f}ms")

        return result

    return wrapper


def get_render_metrics() -> Dict[str, Any]:
    """Get render performance metrics.

    Returns:
        Dictionary of metrics by function name
    """
    metrics_key = '_render_metrics'
    return st.session_state.get(metrics_key, {})


def clear_render_cache() -> None:
    """Clear all render optimization caches."""
    keys_to_remove = [
        k for k in st.session_state.keys()
        if k.startswith('_render_') or k.startswith('_debounce_') or k.startswith('_watch_')
    ]

    for key in keys_to_remove:
        del st.session_state[key]

    _render_batcher.clear_all()


# Export utilities
__all__ = [
    'RenderBatcher',
    'batch_render',
    'flush_render_batch',
    'FragmentManager',
    'optimize_render_cycle',
    'debounce_render',
    'ConditionalRenderer',
    'render_with_profiling',
    'get_render_metrics',
    'clear_render_cache',
]
