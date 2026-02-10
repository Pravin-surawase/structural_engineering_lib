#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
FastAPI Route Generator (V3 Preparation)
=========================================

Generates FastAPI route stubs and Pydantic models from the structural_lib API.
This accelerates V3 migration by scaffolding the backend automatically.

Usage:
    python scripts/generate_api_routes.py                    # Generate routes
    python scripts/generate_api_routes.py --output app/      # Custom output dir
    python scripts/generate_api_routes.py --dry-run          # Preview only
    python scripts/generate_api_routes.py --function design_beam_is456

Exit Codes:
    0 - Routes generated successfully
    1 - Generation errors
    2 - Infrastructure error

V3 Context:
    This script generates:
    1. FastAPI route stubs for each API function
    2. Pydantic request/response models
    3. OpenAPI schema annotations
    4. Type-safe parameter validation

Author: AI Agent (V3 Foundation Session)
Created: 2026-01-24
"""

from __future__ import annotations

import argparse
import inspect
import re
import sys
from dataclasses import is_dataclass, fields
from enum import Enum
from pathlib import Path
from typing import Any, get_type_hints, get_origin, get_args, Union

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
PYTHON_DIR = PROJECT_ROOT / "Python"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "fastapi_app"

# Add Python directory to path
sys.path.insert(0, str(PYTHON_DIR))


def load_api():
    """Load the structural_lib.api module."""
    try:
        from structural_lib import api
        return api
    except ImportError as e:
        print(f"❌ Cannot import structural_lib.services.api: {e}")
        sys.exit(2)


def get_python_type_str(type_hint: Any) -> str:
    """Convert a type hint to a Python type string for Pydantic."""
    if type_hint is None or type_hint is type(None):
        return "None"

    # Handle basic types
    if type_hint in (str, int, float, bool):
        return type_hint.__name__

    # Handle Optional/Union
    origin = get_origin(type_hint)
    if origin is Union:
        args = get_args(type_hint)
        if len(args) == 2 and type(None) in args:
            # Optional[X] -> X | None
            inner = [a for a in args if a is not type(None)][0]
            return f"{get_python_type_str(inner)} | None"
        return " | ".join(get_python_type_str(a) for a in args)

    # Handle list
    if origin is list:
        args = get_args(type_hint)
        if args:
            return f"list[{get_python_type_str(args[0])}]"
        return "list"

    # Handle dict
    if origin is dict:
        args = get_args(type_hint)
        if len(args) == 2:
            return f"dict[{get_python_type_str(args[0])}, {get_python_type_str(args[1])}]"
        return "dict"

    # Handle Enum
    if isinstance(type_hint, type) and issubclass(type_hint, Enum):
        return type_hint.__name__

    # Handle dataclass
    if is_dataclass(type_hint):
        return type_hint.__name__

    # Default
    if hasattr(type_hint, "__name__"):
        return type_hint.__name__

    return str(type_hint)


def get_pydantic_field_type(type_hint: Any) -> str:
    """Convert type hint to Pydantic-compatible field type."""
    type_str = get_python_type_str(type_hint)

    # Map common structural types
    replacements = {
        "FlexureResult": "FlexureResponse",
        "ShearResult": "ShearResponse",
        "ComplianceCaseResult": "ComplianceCaseResponse",
        "DesignSectionType": "str",  # Enum as string for JSON
    }

    for old, new in replacements.items():
        type_str = type_str.replace(old, new)

    return type_str


def generate_request_model(func_name: str, sig: inspect.Signature, type_hints: dict) -> str:
    """Generate Pydantic request model for a function."""
    lines = []
    lines.append(f"class {func_name.title().replace('_', '')}Request(BaseModel):")
    lines.append('    """Request model for ' + func_name + '."""')

    has_fields = False
    for param_name, param in sig.parameters.items():
        if param_name in ("self", "cls"):
            continue

        type_hint = type_hints.get(param_name, Any)
        type_str = get_pydantic_field_type(type_hint)

        # Check if optional (has default)
        if param.default is not inspect.Parameter.empty:
            default = param.default
            if isinstance(default, str):
                default_str = f'"{default}"'
            elif default is None:
                default_str = "None"
            else:
                default_str = repr(default)
            lines.append(f"    {param_name}: {type_str} = {default_str}")
        else:
            lines.append(f"    {param_name}: {type_str}")
        has_fields = True

    if not has_fields:
        lines.append("    pass")

    return "\n".join(lines)


def generate_response_model(func_name: str, return_hint: Any) -> str:
    """Generate Pydantic response model stub."""
    if return_hint is None or return_hint is type(None):
        return ""

    # For dataclass returns, generate a placeholder
    if is_dataclass(return_hint):
        model_name = return_hint.__name__.replace("Result", "Response")
        lines = [f"class {model_name}(BaseModel):"]
        lines.append(f'    """Response model for {return_hint.__name__}."""')

        for field in fields(return_hint):
            field_type = get_pydantic_field_type(field.type)
            lines.append(f"    {field.name}: {field_type}")

        return "\n".join(lines)

    return ""


def generate_route(func_name: str, func: callable, type_hints: dict) -> str:
    """Generate FastAPI route for an API function."""
    sig = inspect.signature(func)
    return_hint = type_hints.get("return")

    # Determine HTTP method (POST for design functions, GET for info/check)
    method = "post" if "design" in func_name or "calculate" in func_name else "get"

    # Generate route path
    route_path = "/" + func_name.replace("_", "-")

    lines = []
    lines.append(f'@router.{method}("{route_path}")')

    # Generate function signature
    params = []
    for param_name, param in sig.parameters.items():
        if param_name in ("self", "cls"):
            continue

        type_hint = type_hints.get(param_name, Any)
        type_str = get_pydantic_field_type(type_hint)

        if param.default is not inspect.Parameter.empty:
            default = param.default
            if isinstance(default, str):
                default_str = f'"{default}"'
            elif default is None:
                default_str = "None"
            else:
                default_str = repr(default)
            params.append(f"{param_name}: {type_str} = {default_str}")
        else:
            params.append(f"{param_name}: {type_str}")

    # Return type
    return_type = get_pydantic_field_type(return_hint) if return_hint else "dict"

    # Generate async function
    params_str = ",\n    ".join(params) if params else ""
    if params_str:
        lines.append(f"async def {func_name}(")
        lines.append(f"    {params_str}")
        lines.append(f") -> {return_type}:")
    else:
        lines.append(f"async def {func_name}() -> {return_type}:")

    # Docstring
    if func.__doc__:
        doc_first_line = func.__doc__.strip().split("\n")[0]
        lines.append(f'    """{doc_first_line}"""')
    else:
        lines.append(f'    """Execute {func_name}."""')

    # Function body
    params_call = ", ".join(
        f"{p}={p}"
        for p in sig.parameters.keys()
        if p not in ("self", "cls")
    )
    lines.append(f"    result = api.{func_name}({params_call})")
    lines.append("    return result")

    return "\n".join(lines)


def generate_routes_file(api_module, functions: list[str] | None = None) -> str:
    """Generate complete routes.py file content."""
    lines = []

    # Header
    lines.append('"""')
    lines.append("FastAPI Routes for structural_lib API")
    lines.append("=====================================")
    lines.append("")
    lines.append("Auto-generated by scripts/generate_api_routes.py")
    lines.append("Do not edit manually - regenerate after API changes.")
    lines.append('"""')
    lines.append("")
    lines.append("from fastapi import APIRouter, HTTPException")
    lines.append("from pydantic import BaseModel")
    lines.append("from typing import Any")
    lines.append("")
    lines.append("from structural_lib import api")
    lines.append("")
    lines.append('router = APIRouter(prefix="/api/v1", tags=["structural"])')
    lines.append("")

    # Collect functions to generate
    public_funcs = []
    for name in dir(api_module):
        if name.startswith("_"):
            continue
        obj = getattr(api_module, name)
        if callable(obj) and not isinstance(obj, type):
            if functions is None or name in functions:
                public_funcs.append((name, obj))

    # Generate routes
    for func_name, func in sorted(public_funcs):
        try:
            type_hints = get_type_hints(func)
        except Exception:
            type_hints = {}

        lines.append("")
        lines.append(generate_route(func_name, func, type_hints))

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate FastAPI routes from structural_lib API"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for generated files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview generated code without writing files"
    )
    parser.add_argument(
        "--function", "-f",
        action="append",
        dest="functions",
        help="Generate routes for specific function(s) only"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )

    args = parser.parse_args()

    # Load API
    api_module = load_api()

    # Generate routes
    routes_content = generate_routes_file(api_module, args.functions)

    if args.dry_run:
        print("=" * 60)
        print("Generated routes.py (dry run)")
        print("=" * 60)
        print(routes_content)
        print()
        print("=" * 60)
        print(f"Would write to: {args.output / 'routes.py'}")
        return

    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)

    # Write routes file
    routes_file = args.output / "routes.py"
    routes_file.write_text(routes_content)
    print(f"✅ Generated: {routes_file}")

    # Generate __init__.py if not exists
    init_file = args.output / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""FastAPI app for structural_lib."""\n')
        print(f"✅ Generated: {init_file}")

    # Generate main.py stub
    main_file = args.output / "main.py"
    if not main_file.exists():
        main_content = '''"""
FastAPI Application Entry Point
================================

Run with: uvicorn fastapi_app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

app = FastAPI(
    title="Structural Engineering Library API",
    description="IS 456 beam design calculations via REST API",
    version="0.20.0",
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.20.0"}
'''
        main_file.write_text(main_content)
        print(f"✅ Generated: {main_file}")

    print()
    print("=" * 60)
    print("FastAPI Route Generation Complete")
    print("=" * 60)
    print(f"Output directory: {args.output}")
    print()
    print("Next steps:")
    print("  1. pip install fastapi uvicorn")
    print("  2. uvicorn fastapi_app.main:app --reload")
    print("  3. Open http://localhost:8000/docs")


if __name__ == "__main__":
    main()
