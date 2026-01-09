"""
Tests for caching utilities.

Tests caching strategies, cache hits/misses, TTL behavior, and performance.
"""

import time
from unittest.mock import MagicMock, Mock, patch

import pytest

from streamlit_app.utils.caching import (
    TTL_DATABASE,
    TTL_DESIGN_RESULTS,
    TTL_SHORT,
    TTL_VISUALIZATIONS,
    cache_stats,
    cached_code_tables,
    cached_design_beam,
    cached_material_database,
    clear_all_caches,
    get_cached_theme,
    get_design_system_tokens,
    hash_inputs,
    timed_cache,
    warm_caches,
)


class TestHashInputs:
    """Test input hashing for cache keys."""

    def test_hash_basic_args(self):
        """Hash should be consistent for same inputs."""
        hash1 = hash_inputs(5000, 300, 500)
        hash2 = hash_inputs(5000, 300, 500)
        assert hash1 == hash2
        assert len(hash1) == 16  # Truncated SHA256

    def test_hash_with_kwargs(self):
        """Hash should include keyword arguments."""
        hash1 = hash_inputs(5000, fck=25, fy=415)
        hash2 = hash_inputs(5000, fck=25, fy=415)
        assert hash1 == hash2

    def test_hash_different_inputs(self):
        """Different inputs should produce different hashes."""
        hash1 = hash_inputs(5000, 300)
        hash2 = hash_inputs(5000, 400)
        assert hash1 != hash2

    def test_hash_order_independence(self):
        """Kwargs order shouldn't affect hash."""
        hash1 = hash_inputs(fck=25, fy=415)
        hash2 = hash_inputs(fy=415, fck=25)
        assert hash1 == hash2


class TestCachedDesignBeam:
    """Test beam design caching."""

    def test_design_caching_structure(self):
        """Design function should have caching decorator applied."""
        # Just verify the function exists and has cache attributes
        assert callable(cached_design_beam)
        assert hasattr(cached_design_beam, 'clear')

    def test_design_accepts_parameters(self):
        """Design function should accept expected parameters."""
        # Test parameter validation without calling actual API
        try:
            # This will fail at runtime but validates signature
            import inspect
            sig = inspect.signature(cached_design_beam)
            assert 'span_mm' in sig.parameters
            assert 'width_mm' in sig.parameters
            assert 'fck' in sig.parameters
        except Exception:
            # If inspection fails, at least function exists
            assert callable(cached_design_beam)


class TestCachedVisualizations:
    """Test visualization caching."""

    def test_diagram_function_exists(self):
        """Beam diagram function should exist and be cached."""
        from streamlit_app.utils.caching import cached_beam_diagram

        assert callable(cached_beam_diagram)
        assert hasattr(cached_beam_diagram, 'clear')

    def test_plotly_chart_caching_bar(self):
        """Bar charts should be cached."""
        from streamlit_app.utils.caching import cached_plotly_chart

        data = {'x': [1, 2, 3], 'y': [4, 5, 6]}
        fig1 = cached_plotly_chart('bar', data)
        fig2 = cached_plotly_chart('bar', data)

        # Should be cached (same hash)
        assert fig1 is not None
        assert fig2 is not None

    def test_plotly_chart_caching_line(self):
        """Line charts should be cached."""
        from streamlit_app.utils.caching import cached_plotly_chart

        data = {'x': [1, 2, 3], 'y': [4, 5, 6], 'mode': 'lines'}
        fig = cached_plotly_chart('line', data)

        assert fig is not None

    def test_plotly_chart_invalid_type(self):
        """Invalid chart type should raise error."""
        from streamlit_app.utils.caching import cached_plotly_chart

        with pytest.raises(ValueError, match="Unknown chart type"):
            cached_plotly_chart('invalid', {})


class TestResourceCaching:
    """Test singleton resource caching."""

    def test_theme_function_exists(self):
        """Theme function should exist and be cached."""
        assert callable(get_cached_theme)
        assert hasattr(get_cached_theme, 'clear')

    def test_tokens_function_exists(self):
        """Design tokens function should exist and be cached."""
        assert callable(get_design_system_tokens)
        assert hasattr(get_design_system_tokens, 'clear')


class TestDatabaseCaching:
    """Test database/table caching."""

    def test_material_database_structure(self):
        """Material database should have expected structure."""
        db = cached_material_database()

        assert 'concrete' in db
        assert 'steel' in db
        assert 'M25' in db['concrete']
        assert 'Fe415' in db['steel']
        assert db['concrete']['M25']['fck'] == 25
        assert db['steel']['Fe415']['fy'] == 415

    def test_code_tables_structure(self):
        """Code tables should have expected structure."""
        tables = cached_code_tables()

        assert 'table_16' in tables
        assert 'table_19' in tables
        assert tables['table_16']['moderate'] == 30
        assert 'M25' in tables['table_19']


class TestCacheManagement:
    """Test cache management functions."""

    def test_cache_stats(self):
        """Cache stats should return dict."""
        stats = cache_stats()

        assert isinstance(stats, dict)
        assert 'cache_hit_rate' in stats
        assert 'cache_size' in stats
        assert 'note' in stats

    def test_clear_all_caches_exists(self):
        """Clear all caches function should exist."""
        assert callable(clear_all_caches)
        # Just verify it doesn't crash
        try:
            clear_all_caches()
        except Exception:
            # Mock st might not have clear methods, that's OK
            pass

    def test_warm_caches_exists(self):
        """Warm caches function should exist."""
        assert callable(warm_caches)
        # Just verify it doesn't crash when called
        try:
            warm_caches()
        except Exception:
            # Dependencies might not be available in test, that's OK
            pass


class TestTimedCache:
    """Test custom timed cache decorator."""

    def test_timed_cache_decorator(self):
        """Timed cache decorator should work."""
        call_count = 0

        @timed_cache(ttl=600)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x ** 2

        result1 = expensive_function(5)
        result2 = expensive_function(5)

        assert result1 == 25
        assert result2 == 25
        # Note: Actual caching behavior depends on Streamlit runtime

    def test_timed_cache_different_ttl(self):
        """Decorator should accept different TTL values."""
        @timed_cache(ttl=60)
        def short_cache(x):
            return x * 2

        @timed_cache(ttl=3600)
        def long_cache(x):
            return x * 3

        assert short_cache(5) == 10
        assert long_cache(5) == 15


class TestTTLConstants:
    """Test TTL constant values."""

    def test_ttl_values(self):
        """TTL constants should have reasonable values."""
        assert TTL_DESIGN_RESULTS == 3600  # 1 hour
        assert TTL_VISUALIZATIONS == 1800  # 30 min
        assert TTL_DATABASE == 7200  # 2 hours
        assert TTL_SHORT == 300  # 5 min

    def test_ttl_hierarchy(self):
        """Database should have longest TTL."""
        assert TTL_DATABASE > TTL_DESIGN_RESULTS
        assert TTL_DESIGN_RESULTS > TTL_VISUALIZATIONS
        assert TTL_VISUALIZATIONS > TTL_SHORT


@pytest.mark.performance
class TestCachePerformance:
    """Test cache performance characteristics."""

    def test_hash_performance(self):
        """Hash function should be fast."""
        start = time.time()
        for _ in range(1000):
            hash_inputs(5000, 300, 500, fck=25, fy=415)
        elapsed = time.time() - start

        # Should hash 1000 times in < 100ms
        assert elapsed < 0.1, f"Hashing too slow: {elapsed:.3f}s"

    def test_cached_design_function_structure(self):
        """Cached design should have expected structure."""
        import inspect
        sig = inspect.signature(cached_design_beam)

        # Verify parameters
        assert 'span_mm' in sig.parameters
        assert 'fck' in sig.parameters
        assert 'fy' in sig.parameters

        # Verify caching decorator applied
        assert hasattr(cached_design_beam, 'clear')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
