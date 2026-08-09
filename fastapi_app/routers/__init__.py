"""
FastAPI Routers Package.

Exports all router modules for mounting in main.py.
"""

from fastapi_app.routers import (
    analysis,
    column,
    design,
    detailing,
    export,
    geometry,
    health,
    imports,
    insights,
    library_core,
    optimization,
    rebar,
    streaming,
    websocket,
)

__all__ = [
    "analysis",
    "column",
    "design",
    "detailing",
    "export",
    "geometry",
    "health",
    "imports",
    "insights",
    "library_core",
    "optimization",
    "rebar",
    "streaming",
    "websocket",
]
