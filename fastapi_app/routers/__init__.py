"""
FastAPI Routers Package.

Exports all router modules for mounting in main.py.
"""

from fastapi_app.routers import (
    analysis,
    design,
    detailing,
    geometry,
    health,
    imports,
    optimization,
    rebar,
    streaming,
    websocket,
)

__all__ = [
    "analysis",
    "design",
    "detailing",
    "geometry",
    "health",
    "imports",
    "optimization",
    "rebar",
    "streaming",
    "websocket",
]
