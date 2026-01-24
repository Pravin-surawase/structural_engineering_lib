"""
Authentication and Authorization Module.

Provides JWT-based authentication for WebSocket and REST endpoints.
Includes rate limiting middleware for abuse prevention.

Week 3 Implementation - V3 Migration

Usage:
    # Decode and validate JWT token
    user = await get_current_user(token)

    # Protect WebSocket
    @router.websocket("/ws/design/{session}")
    async def ws_endpoint(websocket: WebSocket, token: str = Query(...)):
        user = await verify_ws_token(token)
        ...

    # Rate limiting is applied via middleware in main.py
"""

from __future__ import annotations

import os
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException, Query, Request, WebSocket, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

# =============================================================================
# Configuration
# =============================================================================

# JWT settings (use environment variables in production)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Rate limiting settings
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))  # requests per window
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # window in seconds


# =============================================================================
# Models
# =============================================================================


class TokenData(BaseModel):
    """JWT token payload data."""
    user_id: str | None = None
    email: str | None = None
    scopes: list[str] = []
    exp: datetime | None = None


class User(BaseModel):
    """Authenticated user model."""
    id: str
    email: str
    is_active: bool = True
    scopes: list[str] = []


# =============================================================================
# JWT Token Functions
# =============================================================================


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data (user_id, email, scopes)
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> TokenData:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        TokenData with user info

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(
            user_id=payload.get("sub"),
            email=payload.get("email"),
            scopes=payload.get("scopes", []),
            exp=datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.utc),
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# =============================================================================
# Authentication Dependencies
# =============================================================================


security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> User | None:
    """
    Get current authenticated user from JWT token.

    Returns None if no token provided (allows public access).
    Raises HTTPException if token is invalid.
    """
    if not credentials:
        return None

    token_data = decode_token(credentials.credentials)

    if not token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return User(
        id=token_data.user_id,
        email=token_data.email or "",
        scopes=token_data.scopes,
    )


async def require_auth(
    user: User | None = Depends(get_current_user),
) -> User:
    """
    Require authentication - raises if not authenticated.

    Use this for protected endpoints.
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# =============================================================================
# WebSocket Authentication
# =============================================================================


async def verify_ws_token(
    websocket: WebSocket,
    token: str | None = Query(None),
) -> User | None:
    """
    Verify JWT token for WebSocket connections.

    Token can be passed as query parameter: ws://host/ws/design/123?token=xxx

    Returns None if no token (allows public access).
    Closes WebSocket with 4001 if token is invalid.
    """
    if not token:
        return None

    try:
        token_data = decode_token(token)
        if not token_data.user_id:
            await websocket.close(code=4001, reason="Invalid token payload")
            return None

        return User(
            id=token_data.user_id,
            email=token_data.email or "",
            scopes=token_data.scopes,
        )
    except HTTPException:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return None


# =============================================================================
# Rate Limiting
# =============================================================================


class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window.

    In production, use Redis for distributed rate limiting.
    """

    def __init__(
        self,
        requests_per_window: int = RATE_LIMIT_REQUESTS,
        window_seconds: int = RATE_LIMIT_WINDOW_SECONDS,
    ):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    def _get_client_key(self, request: Request) -> str:
        """Get unique key for rate limiting (IP-based)."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _cleanup_old_requests(self, key: str) -> None:
        """Remove requests outside the sliding window."""
        now = time.time()
        cutoff = now - self.window_seconds
        self.requests[key] = [t for t in self.requests[key] if t > cutoff]

    def is_allowed(self, request: Request) -> tuple[bool, dict[str, Any]]:
        """
        Check if request is allowed under rate limit.

        Returns:
            (allowed: bool, headers: dict with rate limit info)
        """
        key = self._get_client_key(request)
        self._cleanup_old_requests(key)

        current_count = len(self.requests[key])
        remaining = max(0, self.requests_per_window - current_count)

        headers = {
            "X-RateLimit-Limit": str(self.requests_per_window),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Window": str(self.window_seconds),
        }

        if current_count >= self.requests_per_window:
            # Calculate reset time
            oldest = min(self.requests[key]) if self.requests[key] else time.time()
            reset_at = oldest + self.window_seconds
            headers["X-RateLimit-Reset"] = str(int(reset_at))
            return False, headers

        # Allow request
        self.requests[key].append(time.time())
        headers["X-RateLimit-Remaining"] = str(remaining - 1)
        return True, headers


# Global rate limiter instance
rate_limiter = RateLimiter()


async def check_rate_limit(request: Request) -> None:
    """
    Dependency to check rate limit.

    Add to endpoints that need rate limiting:
        @router.get("/endpoint")
        async def endpoint(rate_limit: None = Depends(check_rate_limit)):
            ...
    """
    allowed, headers = rate_limiter.is_allowed(request)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please slow down.",
            headers=headers,
        )


# =============================================================================
# Development Helpers
# =============================================================================


def create_dev_token(user_id: str = "dev-user", email: str = "dev@example.com") -> str:
    """
    Create a development token for testing.

    DO NOT use in production!
    """
    return create_access_token(
        data={
            "sub": user_id,
            "email": email,
            "scopes": ["design", "analyze", "batch"],
        },
        expires_delta=timedelta(hours=24),
    )


if __name__ == "__main__":
    # Generate a dev token for testing
    token = create_dev_token()
    print("Development Token (24h expiry):")
    print(token)
    print()
    print("Use in WebSocket: ws://localhost:8000/ws/design/test?token=" + token)
    print("Use in REST: Authorization: Bearer " + token)
