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
    optimization,
)

__all__ = [
    "analysis",
    "design",
    "detailing",
    "geometry",
    "health",
    "optimization",
]
