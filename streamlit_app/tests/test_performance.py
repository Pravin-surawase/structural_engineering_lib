"""
Tests for performance optimization utilities.
"""

import time
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from streamlit_app.utils.performance import (
    batch_render,
    calculate_image_hash,
    clear_all_cache,
    clear_old_cache,
    get_cache_size,
    get_render_stats,
    lazy_load,
    measure_render_time,
    memoize_with_ttl,
    optimize_image,
    should_lazy_load,
    show_performance_stats,
)


# =============================================================================
# LAZY LOADING TESTS
# =============================================================================


class TestLazyLoading:
    """Test lazy loading functionality."""

    def test_lazy_load_decorator(self, mock_streamlit):
        """Test lazy load decorator wraps function."""

        @lazy_load
        def test_component():
            return "rendered"

        result = test_component()
        assert result == "rendered"
        assert test_component.__name__ == "test_component"

    def test_should_lazy_load_no_data(self, mock_streamlit):
        """Test should_lazy_load returns False when no perf data."""
        result = should_lazy_load("test_component")
        assert result is False

    def test_should_lazy_load_below_threshold(self, mock_streamlit):
        """Test should_lazy_load returns False below threshold."""
        mock_streamlit.session_state["perf_test_component"] = 50
        result = should_lazy_load("test_component", threshold_ms=100)
        assert result is False

    def test_should_lazy_load_above_threshold(self, mock_streamlit):
        """Test should_lazy_load returns True above threshold."""
        mock_streamlit.session_state["perf_test_component"] = 150
        result = should_lazy_load("test_component", threshold_ms=100)
        assert result is True


# =============================================================================
# IMAGE OPTIMIZATION TESTS
# =============================================================================


class TestImageOptimization:
    """Test image optimization functionality."""

    def test_calculate_image_hash(self):
        """Test image hash calculation."""
        data = b"test image data"
        hash1 = calculate_image_hash(data)
        hash2 = calculate_image_hash(data)

        assert hash1 == hash2
        assert len(hash1) == 16  # Truncated to 16 chars
        assert isinstance(hash1, str)

    def test_calculate_image_hash_different_data(self):
        """Test different data produces different hashes."""
        hash1 = calculate_image_hash(b"data1")
        hash2 = calculate_image_hash(b"data2")
        assert hash1 != hash2

    def test_optimize_image_returns_bytes(self):
        """Test image optimization returns bytes regardless of PIL availability."""
        original = b"test image data"
        result = optimize_image(original, max_width=1200, quality=85)

        # Should return original bytes when PIL fails or isn't available
        assert isinstance(result, bytes)
        assert result == original  # Returns original on error

    def test_optimize_image_handles_invalid_data(self):
        """Test image optimization handles invalid image data gracefully."""
        # Invalid image data - should return original bytes on error
        original = b"not a real image"
        result = optimize_image(original, max_width=5000, quality=85)

        # Should return original bytes when image can't be processed
        assert isinstance(result, bytes)
        assert result == original


# =============================================================================
# MEMOIZATION TESTS
# =============================================================================


class TestMemoization:
    """Test memoization and caching."""

    def test_memoize_with_ttl_caches_result(self, mock_streamlit):
        """Test memoization caches function results."""
        call_count = 0

        @memoize_with_ttl(ttl_seconds=60)
        def expensive_fn(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call
        result1 = expensive_fn(5)
        assert result1 == 10
        assert call_count == 1

        # Second call (should use cache)
        result2 = expensive_fn(5)
        assert result2 == 10
        assert call_count == 1  # Not called again

    def test_memoize_with_ttl_expires(self, mock_streamlit):
        """Test memoization cache expires after TTL."""
        call_count = 0

        @memoize_with_ttl(ttl_seconds=0.1)
        def expensive_fn(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call
        expensive_fn(5)
        assert call_count == 1

        # Wait for TTL to expire
        time.sleep(0.2)

        # Second call (cache expired, should call again)
        expensive_fn(5)
        assert call_count == 2

    def test_clear_old_cache(self, mock_streamlit):
        """Test clearing old cache entries."""
        # Create cache with old timestamp
        old_time = time.time() - (25 * 3600)  # 25 hours ago
        mock_streamlit.session_state["memo_test"] = {
            "key1": ("value1", old_time),
            "key2": ("value2", time.time()),
        }

        cleared = clear_old_cache(max_age_hours=24)
        assert cleared == 1  # Only old entry cleared

        cache = mock_streamlit.session_state["memo_test"]
        assert "key1" not in cache
        assert "key2" in cache

    def test_get_cache_size(self, mock_streamlit):
        """Test getting cache size."""
        mock_streamlit.session_state["memo_fn1"] = {"a": 1, "b": 2}
        mock_streamlit.session_state["memo_fn2"] = {"c": 3}
        mock_streamlit.session_state["other_key"] = "ignored"

        size = get_cache_size()
        assert size == 3  # 2 + 1

    def test_clear_all_cache(self, mock_streamlit):
        """Test clearing all caches."""
        mock_streamlit.session_state["memo_fn1"] = {"a": 1, "b": 2}
        mock_streamlit.session_state["memo_fn2"] = {"c": 3}

        cleared = clear_all_cache()
        assert cleared == 3

        assert mock_streamlit.session_state["memo_fn1"] == {}
        assert mock_streamlit.session_state["memo_fn2"] == {}


# =============================================================================
# RENDER BATCHING TESTS
# =============================================================================


class TestRenderBatching:
    """Test render batching functionality."""

    def test_batch_render_small_list(self, mock_streamlit):
        """Test batch render with small list (no progress bar)."""
        items = [1, 2, 3]
        rendered = []

        def render_fn(item):
            rendered.append(item)

        batch_render(items, render_fn, batch_size=10, show_progress=False)
        assert rendered == [1, 2, 3]

    def test_batch_render_large_list(self, mock_streamlit):
        """Test batch render with large list (shows progress)."""
        items = list(range(25))
        rendered = []

        def render_fn(item):
            rendered.append(item)

        # Mock progress and empty to return MagicMock objects
        mock_streamlit.progress = MagicMock(return_value=MagicMock())
        mock_streamlit.empty = MagicMock(return_value=MagicMock())

        batch_render(items, render_fn, batch_size=10, show_progress=True)
        assert len(rendered) == 25
        assert rendered == list(range(25))

        # Verify progress was called
        assert mock_streamlit.progress.called

    def test_batch_render_empty_list(self, mock_streamlit):
        """Test batch render with empty list."""
        rendered = []

        def render_fn(item):
            rendered.append(item)

        batch_render([], render_fn, batch_size=10)
        assert rendered == []


# =============================================================================
# PERFORMANCE MONITORING TESTS
# =============================================================================


class TestPerformanceMonitoring:
    """Test performance monitoring functionality."""

    def test_measure_render_time(self, mock_streamlit):
        """Test measuring component render time."""
        with measure_render_time("test_component"):
            time.sleep(0.01)  # Simulate work

        render_time = mock_streamlit.session_state["perf_test_component"]
        assert render_time >= 10  # At least 10ms

    def test_get_render_stats_exists(self, mock_streamlit):
        """Test getting render stats when data exists."""
        mock_streamlit.session_state["perf_test"] = 123.45
        stats = get_render_stats("test")
        assert stats == 123.45

    def test_get_render_stats_not_exists(self, mock_streamlit):
        """Test getting render stats when data doesn't exist."""
        stats = get_render_stats("nonexistent")
        assert stats is None

    def test_show_performance_stats_no_data(self, mock_streamlit):
        """Test showing performance stats with no data."""
        # Mock methods to track calls
        mock_streamlit.info = MagicMock()
        mock_streamlit.subheader = MagicMock()
        mock_streamlit.write = MagicMock()

        show_performance_stats()

        # Should call st.info when no data
        assert mock_streamlit.info.called

    def test_show_performance_stats_with_data(self, mock_streamlit):
        """Test showing performance stats with data."""
        # Mock methods to track calls
        mock_streamlit.info = MagicMock()
        mock_streamlit.subheader = MagicMock()
        mock_streamlit.write = MagicMock()

        mock_streamlit.session_state["perf_fast"] = 50
        mock_streamlit.session_state["perf_medium"] = 250
        mock_streamlit.session_state["perf_slow"] = 600

        show_performance_stats()

        # Should call st.subheader and st.write
        assert mock_streamlit.subheader.called
        assert mock_streamlit.write.call_count >= 3
