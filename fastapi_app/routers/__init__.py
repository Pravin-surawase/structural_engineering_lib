"""
FastAPI Routers Package.

Exports all router modules for mounting in main.py.
"""

from fastapi_app.routers import (
    analysis,
    catalog,
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
    workflows,
)

__all__ = [
    "analysis",
    "catalog",
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
    "workflows",
]
