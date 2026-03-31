"""
FastAPI Routers Package.

Exports all router modules for mounting in main.py.
"""

from fastapi_app.routers import (
    analysis,
    column,
    design,
    detailing,
    geometry,
    health,
    imports,
    insights,
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
    "insights",
    "optimization",
    "rebar",
    "streaming",
    "websocket",
]
