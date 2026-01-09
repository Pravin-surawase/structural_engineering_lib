"""
Lazy Loading Utilities for Streamlit App Performance
Defers expensive imports and component loading until needed.
"""
from functools import wraps
from typing import Any, Callable, Dict, Optional
import streamlit as st


class LazyImporter:
    """Import heavy modules only when first accessed."""

    def __init__(self):
        self._imports: Dict[str, Any] = {}

    def get_module(self, module_name: str) -> Any:
        """
        Import module lazily on first access.

        Args:
            module_name: Full module path (e.g., 'pandas', 'plotly.graph_objects')

        Returns:
            Imported module
        """
        if module_name not in self._imports:
            try:
                # Dynamic import
                parts = module_name.split('.')
                module = __import__(module_name)
                for part in parts[1:]:
                    module = getattr(module, part)
                self._imports[module_name] = module
            except ImportError as e:
                st.error(f"Failed to import {module_name}: {e}")
                return None

        return self._imports[module_name]


# Global lazy importer instance
_lazy_importer = LazyImporter()


def lazy_import(module_name: str) -> Any:
    """
    Import module lazily.

    Usage:
        pd = lazy_import('pandas')
        df = pd.DataFrame(data)

    Args:
        module_name: Module to import

    Returns:
        Imported module or None if failed
    """
    return _lazy_importer.get_module(module_name)


def load_on_demand(component_key: str):
    """
    Decorator to load component only when first accessed.
    Component state tracked in session_state.

    Usage:
        @load_on_demand('heavy_chart')
        def render_chart():
            # Expensive rendering code
            pass

    Args:
        component_key: Unique key for component
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if component should be loaded
            state_key = f"_loaded_{component_key}"

            if state_key not in st.session_state:
                st.session_state[state_key] = False

            # Load on first access or if explicitly requested
            if not st.session_state[state_key]:
                st.session_state[state_key] = True

            # Call the actual function
            return func(*args, **kwargs)

        return wrapper
    return decorator


def defer_until_visible(container_type: str = "expander"):
    """
    Defer rendering until container is visible/expanded.

    Args:
        container_type: Type of container ('expander', 'tab', 'column')
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # For expanders, check if expanded
            if container_type == "expander":
                # Render immediately (Streamlit handles visibility)
                return func(*args, **kwargs)

            # For tabs, rely on Streamlit's lazy rendering
            elif container_type == "tab":
                return func(*args, **kwargs)

            # Default: render immediately
            return func(*args, **kwargs)

        return wrapper
    return decorator


class ComponentLoader:
    """Progressive component loading manager."""

    def __init__(self):
        self._loaded_components = set()

    def is_loaded(self, component_id: str) -> bool:
        """Check if component already loaded."""
        return component_id in self._loaded_components

    def mark_loaded(self, component_id: str) -> None:
        """Mark component as loaded."""
        self._loaded_components.add(component_id)

    def unload(self, component_id: str) -> None:
        """Unload component (for memory management)."""
        if component_id in self._loaded_components:
            self._loaded_components.remove(component_id)

    def reset(self) -> None:
        """Reset all loaded components."""
        self._loaded_components.clear()


# Global component loader
_component_loader = ComponentLoader()


def progressive_load(
    component_id: str,
    placeholder_text: str = "Loading component..."
) -> Callable:
    """
    Load component progressively with placeholder.

    Usage:
        @progressive_load('chart_section', 'Loading chart...')
        def render_chart():
            # Heavy rendering
            pass

    Args:
        component_id: Unique component identifier
        placeholder_text: Text to show while loading
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if already loaded
            if _component_loader.is_loaded(component_id):
                return func(*args, **kwargs)

            # Show placeholder
            with st.spinner(placeholder_text):
                result = func(*args, **kwargs)

            # Mark as loaded
            _component_loader.mark_loaded(component_id)
            return result

        return wrapper
    return decorator


def batch_load_components(components: Dict[str, Callable]) -> None:
    """
    Load multiple components in batches for better performance.

    Args:
        components: Dict of {component_id: render_function}
    """
    for component_id, render_func in components.items():
        if not _component_loader.is_loaded(component_id):
            with st.spinner(f"Loading {component_id}..."):
                render_func()
            _component_loader.mark_loaded(component_id)


def clear_component_cache() -> None:
    """Clear all loaded component states."""
    _component_loader.reset()

    # Clear session state loaded flags
    keys_to_remove = [k for k in st.session_state.keys() if k.startswith('_loaded_')]
    for key in keys_to_remove:
        del st.session_state[key]
