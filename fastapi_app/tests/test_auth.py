"""
Tests for Authentication and Rate Limiting.

Tests JWT token creation/validation and rate limiting behaviors.
"""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from jose import jwt

from fastapi_app.auth import (
    ALGORITHM,
    SECRET_KEY,
    RateLimiter,
    create_access_token,
    decode_token,
    TokenData,
)

# =============================================================================
# JWT Token Tests
# =============================================================================


class TestCreateAccessToken:
    """Tests for create_access_token function."""

    def test_create_token_with_user_data(self):
        """Token should contain user data."""
        token = create_access_token(
            data={"sub": "user123", "email": "test@example.com"}
        )

        # Decode without verification to check payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert payload["sub"] == "user123"
        assert payload["email"] == "test@example.com"
        assert "exp" in payload

    def test_create_token_with_scopes(self):
        """Token should support scopes."""
        token = create_access_token(
            data={"sub": "user123", "scopes": ["design", "analyze"]}
        )

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["scopes"] == ["design", "analyze"]

    def test_create_token_with_custom_expiry(self):
        """Token should respect custom expiry time."""
        token = create_access_token(
            data={"sub": "user123"},
            expires_delta=timedelta(hours=1),
        )

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload

    def test_create_token_default_expiry(self):
        """Token should use default expiry if not specified."""
        token = create_access_token(data={"sub": "user123"})

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload


class TestDecodeToken:
    """Tests for decode_token function."""

    def test_decode_valid_token(self):
        """Should decode valid token."""
        token = create_access_token(
            data={
                "sub": "user123",
                "email": "test@example.com",
                "scopes": ["design"],
            }
        )

        result = decode_token(token)

        assert isinstance(result, TokenData)
        assert result.user_id == "user123"
        assert result.email == "test@example.com"
        assert result.scopes == ["design"]

    def test_decode_expired_token(self):
        """Should reject expired token."""
        # Create already-expired token
        token = create_access_token(
            data={"sub": "user123"},
            expires_delta=timedelta(seconds=-10),
        )

        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)

        assert exc_info.value.status_code == 401
        assert "Invalid token" in exc_info.value.detail

    def test_decode_invalid_token(self):
        """Should reject invalid token."""
        with pytest.raises(HTTPException) as exc_info:
            decode_token("not-a-valid-token")

        assert exc_info.value.status_code == 401

    def test_decode_tampered_token(self):
        """Should reject tampered token."""
        token = create_access_token(data={"sub": "user123"})
        # Tamper with the token
        tampered = token[:-5] + "xxxxx"

        with pytest.raises(HTTPException) as exc_info:
            decode_token(tampered)

        assert exc_info.value.status_code == 401


# =============================================================================
# Rate Limiter Tests
# =============================================================================


class TestRateLimiter:
    """Tests for RateLimiter class."""

    def test_allows_requests_under_limit(self):
        """Should allow requests under the limit."""
        limiter = RateLimiter(requests_per_window=5, window_seconds=60)
        request = MagicMock()
        request.headers.get.return_value = None
        request.client.host = "127.0.0.1"

        # First 5 requests should be allowed
        for i in range(5):
            allowed, headers = limiter.is_allowed(request)
            assert allowed, f"Request {i+1} should be allowed"
            assert headers["X-RateLimit-Limit"] == "5"
            assert int(headers["X-RateLimit-Remaining"]) == 5 - i - 1

    def test_blocks_requests_over_limit(self):
        """Should block requests over the limit."""
        limiter = RateLimiter(requests_per_window=3, window_seconds=60)
        request = MagicMock()
        request.headers.get.return_value = None
        request.client.host = "127.0.0.1"

        # Use up the limit
        for _ in range(3):
            limiter.is_allowed(request)

        # Fourth request should be blocked
        allowed, headers = limiter.is_allowed(request)
        assert not allowed
        assert "X-RateLimit-Reset" in headers

    def test_uses_forwarded_for_header(self):
        """Should use X-Forwarded-For for client identification."""
        limiter = RateLimiter(requests_per_window=2, window_seconds=60)

        # Request from proxy
        request1 = MagicMock()
        request1.headers.get.return_value = "192.168.1.1, 10.0.0.1"

        # Different client via proxy
        request2 = MagicMock()
        request2.headers.get.return_value = "192.168.1.2"

        # Each client gets their own limit
        limiter.is_allowed(request1)
        limiter.is_allowed(request1)
        allowed1, _ = limiter.is_allowed(request1)  # Should be blocked
        allowed2, _ = limiter.is_allowed(request2)  # Should be allowed

        assert not allowed1
        assert allowed2

    def test_separate_limits_per_client(self):
        """Different clients should have separate rate limits."""
        limiter = RateLimiter(requests_per_window=2, window_seconds=60)

        client1 = MagicMock()
        client1.headers.get.return_value = None
        client1.client.host = "192.168.1.1"

        client2 = MagicMock()
        client2.headers.get.return_value = None
        client2.client.host = "192.168.1.2"

        # Client 1 uses their limit
        limiter.is_allowed(client1)
        limiter.is_allowed(client1)
        allowed1, _ = limiter.is_allowed(client1)

        # Client 2 should still have theirs
        allowed2, _ = limiter.is_allowed(client2)

        assert not allowed1
        assert allowed2


# =============================================================================
# Integration Tests (require FastAPI test client)
# =============================================================================


def test_auth_module_imports():
    """Auth module should import all required components."""
    from fastapi_app.auth import (
        create_access_token,
        decode_token,
        get_current_user,
        require_auth,
        verify_ws_token,
        check_rate_limit,
    )

    assert callable(create_access_token)
    assert callable(decode_token)
    assert callable(get_current_user)
    assert callable(require_auth)
    assert callable(verify_ws_token)
    assert callable(check_rate_limit)


def test_create_dev_token():
    """Dev token helper should create valid token."""
    from fastapi_app.auth import create_dev_token

    token = create_dev_token(user_id="test-user", email="test@test.com")

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "test-user"
    assert payload["email"] == "test@test.com"
    assert "design" in payload["scopes"]
