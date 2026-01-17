"""Design code registry for multi-code support.

Enables runtime selection of design codes and plugin architecture.

Usage:
    from structural_lib.core import CodeRegistry

    # Get available codes
    codes = CodeRegistry.list_codes()

    # Get a specific code
    is456 = CodeRegistry.get("IS456")
    result = is456.flexure.required_steel_area(...)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from structural_lib.core.base import DesignCode


class CodeRegistry:
    """Registry for design code implementations.

    Design codes register themselves here on import.
    Applications can query available codes and instantiate them.
    """

    _codes: dict[str, type[DesignCode]] = {}
    _instances: dict[str, DesignCode] = {}

    @classmethod
    def register(cls, code_id: str, code_class: type[DesignCode]) -> None:
        """Register a design code implementation.

        Args:
            code_id: Unique identifier (e.g., "IS456", "ACI318")
            code_class: Class implementing DesignCode
        """
        cls._codes[code_id] = code_class

    @classmethod
    def get(cls, code_id: str) -> DesignCode:
        """Get an instance of a design code.

        Args:
            code_id: Code identifier

        Returns:
            DesignCode instance (cached)

        Raises:
            KeyError: If code_id not registered
        """
        if code_id not in cls._instances:
            if code_id not in cls._codes:
                available = ", ".join(cls._codes.keys()) or "none"
                raise KeyError(
                    f"Design code '{code_id}' not found. "
                    f"Available codes: {available}"
                )
            cls._instances[code_id] = cls._codes[code_id]()
        return cls._instances[code_id]

    @classmethod
    def list_codes(cls) -> list[str]:
        """List all registered code IDs."""
        return list(cls._codes.keys())

    @classmethod
    def is_registered(cls, code_id: str) -> bool:
        """Check if a code is registered."""
        return code_id in cls._codes

    @classmethod
    def clear(cls) -> None:
        """Clear registry (for testing)."""
        cls._codes.clear()
        cls._instances.clear()


def register_code(code_id: str) -> Callable[[type[DesignCode]], type[DesignCode]]:
    """Decorator to register a design code class.

    Usage:
        @register_code("IS456")
        class IS456Code(DesignCode):
            ...
    """

    def decorator(cls: type[DesignCode]) -> type[DesignCode]:
        CodeRegistry.register(code_id, cls)
        return cls

    return decorator
