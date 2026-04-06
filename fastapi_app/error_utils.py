"""Error sanitization utilities for API responses.

Prevents CWE-209 (Information Exposure Through Error Message) by:
- Logging full exception details server-side for debugging
- Returning generic messages to API consumers
- Preserving ValueError/TypeError messages (user input issues) unless they contain paths
- Including a request_id for correlating client errors with server logs
"""

import logging
import math
import uuid

logger = logging.getLogger(__name__)


def sanitize_float(v: float) -> float:
    """Replace non-finite floats for JSON safety (RFC 8259)."""
    if math.isfinite(v):
        return v
    if math.isnan(v):
        return 0.0
    return 9999.0 if v > 0 else -9999.0


def sanitize_error(e: Exception, context: str = "operation") -> str:
    """Return a safe error message for API responses.

    - Logs the full exception server-side with exc_info for debugging
    - Returns a generic message to the client with a reference ID
    - Preserves ValueError/TypeError messages (user input issues are safe to expose)
      unless they contain file paths or tracebacks

    Args:
        e: The caught exception.
        context: A short description of the operation (e.g., "beam design").

    Returns:
        A sanitized error message string safe for API consumers.
    """
    request_id = uuid.uuid4().hex[:8]
    logger.error("Error in %s [%s]: %s", context, request_id, e, exc_info=True)

    if isinstance(e, (ValueError, TypeError)):
        msg = str(e)
        # Strip messages containing internal paths or tracebacks
        if "/" in msg or "\\" in msg or "Traceback" in msg:
            return f"Invalid input for {context}. Reference: {request_id}"
        return msg

    return f"Internal error during {context}. Reference: {request_id}"
