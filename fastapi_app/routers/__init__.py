"""
FastAPI Routers Package.

Exports all router modules for mounting in main.py.
"""

from fastapi_app.routers import (
    analysis,
    catalog,
    column,
    combined_footing,
    deep_beam,
    design,
    design_v2,
    detailing,
    export,
    flat_slab,
    footing,
    geometry,
    health,
    imports,
    insights,
    library_core,
    optimization,
    rebar,
    staircase,
    strap_footing,
    streaming,
    wall,
    websocket,
    workflows,
)

__all__ = [
    "analysis",
    "catalog",
    "column",
    "combined_footing",
    "deep_beam",
    "design",
    "design_v2",
    "detailing",
    "export",
    "flat_slab",
    "footing",
    "geometry",
    "health",
    "imports",
    "insights",
    "library_core",
    "optimization",
    "rebar",
    "staircase",
    "strap_footing",
    "streaming",
    "wall",
    "websocket",
    "workflows",
]
