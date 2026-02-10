#!/usr/bin/env python3
"""Generate enhanced index.json + index.md for ANY folder type.

Extends generate_folder_index.py to handle:
- Python packages (.py files with class/function extraction)
- React/TypeScript (.ts/.tsx with export detection)
- Config files (.json, .yaml, .toml)
- Mixed folders (docs + code)

Creates AI-agent-optimized index files that enable quick context loading.

Usage:
    python scripts/generate_enhanced_index.py <folder_path>
    python scripts/generate_enhanced_index.py Python/structural_lib/ --recursive
    python scripts/generate_enhanced_index.py react_app/src/ --recursive --depth 2
    python scripts/generate_enhanced_index.py --all  # Generate for all key folders

Options:
    --recursive   Recurse into subfolders
    --depth N     Max recursion depth (default: 3)
    --json-only   Generate only index.json
    --md-only     Generate only index.md
    --all         Generate indexes for all key project folders
    --dry-run     Show what would be generated
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Folders to skip
SKIP_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    ".venv",
    ".git",
    ".turbo",
    "dist",
    "build",
    ".vite",
    ".next",
    "coverage",
    "htmlcov",
    ".tox",
    "egg-info",
    "structural_lib_is456.egg-info",
}

# Key project folders that should have indexes
KEY_FOLDERS = [
    "Python/structural_lib",
    "Python/structural_lib/core",
    "Python/structural_lib/codes",
    "Python/structural_lib/codes/is456",
    "Python/structural_lib/insights",
    "Python/structural_lib/reports",
    "Python/structural_lib/visualization",
    "Python/tests",
    "Python/examples",
    "fastapi_app",
    "fastapi_app/models",
    "fastapi_app/routers",
    "fastapi_app/tests",
    "fastapi_app/examples",
    "react_app/src",
    "react_app/src/components",
    "react_app/src/hooks",
    "react_app/src/store",
    "react_app/src/types",
    "react_app/src/utils",
    "scripts",
    "docs",
    "docs/getting-started",
    "docs/reference",
    "docs/architecture",
    "docs/planning",
    "docs/agents",
    "docs/agents/guides",
    "docs/guides",
    "docs/contributing",
    "agents",
    "agents/roles",
]


# ─── Python Analysis ────────────────────────────────────────────


def analyze_python_file(file_path: Path) -> dict[str, Any]:
    """Extract metadata from a Python file."""
    info: dict[str, Any] = {
        "name": file_path.name,
        "type": "python",
    }

    try:
        content = file_path.read_text(encoding="utf-8")
        info["size_lines"] = len(content.split("\n"))
        info["last_updated"] = datetime.fromtimestamp(
            file_path.stat().st_mtime
        ).strftime("%Y-%m-%d")
    except (OSError, UnicodeDecodeError):
        return info

    # Extract docstring
    try:
        tree = ast.parse(content)
        docstring = ast.get_docstring(tree)
        if docstring:
            # First line only
            info["description"] = docstring.split("\n")[0].strip()[:200]
    except SyntaxError:
        info["description"] = "(syntax error)"
        return info

    # Extract public API
    classes = []
    functions = []
    constants = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            doc = ast.get_docstring(node)
            cls_info = {"name": node.name}
            if doc:
                cls_info["description"] = doc.split("\n")[0].strip()[:100]
            # Count methods
            methods = [
                n.name
                for n in ast.iter_child_nodes(node)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                and not n.name.startswith("_")
            ]
            if methods:
                cls_info["public_methods"] = methods[:10]
            classes.append(cls_info)

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            doc = ast.get_docstring(node)
            fn_info = {"name": node.name}
            if doc:
                fn_info["description"] = doc.split("\n")[0].strip()[:100]
            # Extract parameter names
            params = [
                arg.arg
                for arg in node.args.args
                if arg.arg != "self" and arg.arg != "cls"
            ]
            if params:
                fn_info["params"] = params[:8]
            functions.append(fn_info)

        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    constants.append(target.id)

    if classes:
        info["classes"] = classes[:15]
    if functions:
        info["functions"] = functions[:20]
    if constants:
        info["constants"] = constants[:10]

    # Detect if it's a re-export stub
    if info.get("size_lines", 0) < 40:
        if "warnings.warn" in content and "deprecated" in content.lower():
            info["is_compat_stub"] = True

    return info


# ─── TypeScript/React Analysis ──────────────────────────────────


def analyze_ts_file(file_path: Path) -> dict[str, Any]:
    """Extract metadata from a TypeScript/React file."""
    info: dict[str, Any] = {
        "name": file_path.name,
        "type": "typescript" if file_path.suffix == ".ts" else "react-component",
    }

    try:
        content = file_path.read_text(encoding="utf-8")
        info["size_lines"] = len(content.split("\n"))
        info["last_updated"] = datetime.fromtimestamp(
            file_path.stat().st_mtime
        ).strftime("%Y-%m-%d")
    except (OSError, UnicodeDecodeError):
        return info

    # Extract exports
    exports = []

    # export function X, export const X, export default
    for match in re.finditer(
        r"export\s+(?:default\s+)?(?:function|const|class|interface|type|enum)\s+(\w+)",
        content,
    ):
        exports.append(match.group(1))

    # export { X, Y }
    for match in re.finditer(r"export\s*\{([^}]+)\}", content):
        for name in match.group(1).split(","):
            name = name.strip().split(" as ")[0].strip()
            if name:
                exports.append(name)

    if exports:
        info["exports"] = exports[:15]

    # Detect hooks
    if file_path.name.startswith("use"):
        info["type"] = "react-hook"

    # Detect component props
    props_match = re.search(r"(?:interface|type)\s+(\w+Props)\s*[{=]", content)
    if props_match:
        info["props_type"] = props_match.group(1)

    # Extract JSDoc description
    jsdoc_match = re.search(r"/\*\*\s*\n\s*\*\s*(.+?)(?:\n|\*/)", content)
    if jsdoc_match:
        info["description"] = jsdoc_match.group(1).strip()[:200]

    return info


# ─── Markdown Analysis ──────────────────────────────────────────


def analyze_md_file(file_path: Path) -> dict[str, Any]:
    """Extract metadata from a Markdown file."""
    info: dict[str, Any] = {
        "name": file_path.name,
        "type": "documentation",
    }

    try:
        content = file_path.read_text(encoding="utf-8")
        info["size_lines"] = len(content.split("\n"))
        info["last_updated"] = datetime.fromtimestamp(
            file_path.stat().st_mtime
        ).strftime("%Y-%m-%d")
    except (OSError, UnicodeDecodeError):
        return info

    # Extract title
    for line in content.split("\n")[:5]:
        if line.startswith("# "):
            info["title"] = line[2:].strip()
            break

    # Extract description (first paragraph after title)
    lines = content.split("\n")
    found_title = False
    desc_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            found_title = True
            continue
        if found_title and stripped and not stripped.startswith(("#", "---", "===", "**")):
            desc_lines.append(stripped)
            if len(desc_lines) >= 2:
                break

    if desc_lines:
        desc = " ".join(desc_lines)
        # Strip markdown formatting
        desc = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", desc)
        desc = desc.replace("`", "")
        info["description"] = desc[:200]

    return info


# ─── Config File Analysis ───────────────────────────────────────


def analyze_config_file(file_path: Path) -> dict[str, Any]:
    """Extract metadata from config files."""
    info: dict[str, Any] = {
        "name": file_path.name,
        "type": "config",
        "last_updated": datetime.fromtimestamp(
            file_path.stat().st_mtime
        ).strftime("%Y-%m-%d"),
    }

    ext = file_path.suffix
    if ext == ".json":
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                info["top_level_keys"] = list(data.keys())[:10]
                if "name" in data:
                    info["description"] = f"Package: {data['name']}"
                elif "description" in data:
                    info["description"] = str(data["description"])[:200]
        except (json.JSONDecodeError, OSError):
            pass
    elif ext in (".yaml", ".yml", ".toml"):
        info["description"] = f"{ext.upper()} configuration file"

    return info


# ─── Generic File Analyzer ──────────────────────────────────────


def analyze_file(file_path: Path) -> dict[str, Any] | None:
    """Analyze any file and return metadata."""
    ext = file_path.suffix

    if ext == ".py":
        return analyze_python_file(file_path)
    elif ext in (".ts", ".tsx"):
        return analyze_ts_file(file_path)
    elif ext in (".js", ".jsx"):
        return analyze_ts_file(file_path)  # Similar enough
    elif ext == ".md":
        return analyze_md_file(file_path)
    elif ext in (".json", ".yaml", ".yml", ".toml"):
        return analyze_config_file(file_path)
    elif ext in (".sh", ".bash"):
        return analyze_shell_file(file_path)
    elif ext in (".css", ".scss"):
        return {
            "name": file_path.name,
            "type": "stylesheet",
            "size_lines": len(file_path.read_text(encoding="utf-8").split("\n")),
            "last_updated": datetime.fromtimestamp(
                file_path.stat().st_mtime
            ).strftime("%Y-%m-%d"),
        }
    else:
        return None


def analyze_shell_file(file_path: Path) -> dict[str, Any]:
    """Extract metadata from shell scripts."""
    info: dict[str, Any] = {
        "name": file_path.name,
        "type": "shell-script",
    }

    try:
        content = file_path.read_text(encoding="utf-8")
        info["size_lines"] = len(content.split("\n"))
        info["last_updated"] = datetime.fromtimestamp(
            file_path.stat().st_mtime
        ).strftime("%Y-%m-%d")

        # Extract description from comments
        for line in content.split("\n")[:10]:
            line = line.strip()
            if line.startswith("#") and not line.startswith("#!"):
                desc = line.lstrip("# ").strip()
                if desc and len(desc) > 10:
                    info["description"] = desc[:200]
                    break
    except (OSError, UnicodeDecodeError):
        pass

    return info


# ─── Folder Scanner ─────────────────────────────────────────────


def scan_folder_enhanced(folder_path: Path) -> dict[str, Any]:
    """Scan folder and generate enhanced index data."""
    folder_rel = str(folder_path.relative_to(PROJECT_ROOT))

    # Categorize files
    all_files = sorted(
        f
        for f in folder_path.iterdir()
        if f.is_file()
        and f.name not in ("index.json", "index.md")
        and not f.name.startswith(".")
    )

    # Get subfolders
    subfolders = sorted(
        d
        for d in folder_path.iterdir()
        if d.is_dir()
        and not d.name.startswith((".", "_"))
        and d.name not in SKIP_DIRS
    )

    # Read README for folder description
    readme_path = folder_path / "README.md"
    folder_description = ""
    if readme_path.exists():
        try:
            content = readme_path.read_text(encoding="utf-8")
            for line in content.split("\n")[:10]:
                if line.startswith("# "):
                    continue
                stripped = line.strip()
                if stripped and not stripped.startswith(("#", "---", "**")):
                    folder_description = stripped[:200]
                    break
        except (OSError, UnicodeDecodeError):
            pass

    # Detect folder type
    exts = {f.suffix for f in all_files}
    if ".py" in exts:
        folder_type = "python-package"
    elif ".ts" in exts or ".tsx" in exts:
        folder_type = "react-source"
    elif ".md" in exts and len(exts.difference({".md", ".json"})) == 0:
        folder_type = "documentation"
    elif ".sh" in exts:
        folder_type = "scripts"
    else:
        folder_type = "mixed"

    # Build index
    index: dict[str, Any] = {
        "folder": folder_rel,
        "type": folder_type,
        "description": folder_description,
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "file_count": len(all_files),
        "files": [],
        "subfolders": [],
    }

    # Analyze files
    for f in all_files:
        file_info = analyze_file(f)
        if file_info:
            index["files"].append(file_info)

    # Analyze subfolders
    for d in subfolders:
        sub_info: dict[str, Any] = {
            "name": d.name,
            "path": f"{d.name}/",
        }

        # Count files in subfolder
        sub_files = list(d.rglob("*"))
        sub_files = [
            f
            for f in sub_files
            if f.is_file() and not any(skip in f.parts for skip in SKIP_DIRS)
        ]
        sub_info["file_count"] = len(sub_files)

        # Check for README/description
        sub_readme = d / "README.md"
        if sub_readme.exists():
            try:
                content = sub_readme.read_text(encoding="utf-8")
                for line in content.split("\n")[:10]:
                    if line.startswith("# "):
                        continue
                    stripped = line.strip()
                    if stripped and not stripped.startswith(("#", "---", "**")):
                        sub_info["description"] = stripped[:150]
                        break
            except (OSError, UnicodeDecodeError):
                pass

        # Check for __init__.py (Python package)
        if (d / "__init__.py").exists():
            sub_info["is_package"] = True

        index["subfolders"].append(sub_info)

    # Add Python-specific metadata
    if folder_type == "python-package":
        init_file = folder_path / "__init__.py"
        if init_file.exists():
            index["has_init"] = True
            try:
                content = init_file.read_text(encoding="utf-8")
                # Find __all__ using AST for accuracy
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Assign):
                            for target in node.targets:
                                if isinstance(target, ast.Name) and target.id == "__all__":
                                    if isinstance(node.value, (ast.List, ast.Tuple)):
                                        exports = [
                                            elt.value
                                            for elt in node.value.elts
                                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                                        ]
                                        index["public_api"] = exports[:20]
                except SyntaxError:
                    pass
            except (OSError, UnicodeDecodeError):
                pass

    return index


# ─── Output Generators ──────────────────────────────────────────


def generate_json(index: dict, output_path: Path) -> None:
    """Generate index.json."""
    json_path = output_path / "index.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"  ✅ {json_path.relative_to(PROJECT_ROOT)}")


def generate_markdown(index: dict, output_path: Path) -> None:
    """Generate index.md."""
    folder_name = Path(index["folder"]).name or "Root"
    title = folder_name.replace("-", " ").replace("_", " ").title()

    lines = [
        f"# {title}",
        "",
    ]

    if index["description"]:
        lines.extend([index["description"], ""])

    type_label = index.get("type", "mixed").replace("-", " ").title()
    lines.extend([
        f"**Type:** {type_label}  ",
        f"**Last Updated:** {index['last_updated']}  ",
        f"**Files:** {index['file_count']}",
        "",
    ])

    # Public API summary (for Python packages)
    if "public_api" in index:
        lines.extend(["## Public API", ""])
        for api in index["public_api"]:
            lines.append(f"- `{api}`")
        lines.append("")

    # Files by type
    file_types: dict[str, list] = {}
    for f in index["files"]:
        ft = f.get("type", "other")
        file_types.setdefault(ft, []).append(f)

    for ft, files in sorted(file_types.items()):
        section_title = ft.replace("-", " ").replace("_", " ").title()
        lines.extend([f"## {section_title} Files", ""])

        if ft == "python":
            lines.extend([
                "| File | Description | Classes | Functions | Lines |",
                "|------|-------------|---------|-----------|-------|",
            ])
            for f in files:
                desc = f.get("description", "")[:60]
                n_cls = len(f.get("classes", []))
                n_fn = len(f.get("functions", []))
                n_lines = f.get("size_lines", "?")
                stub = " *(stub)*" if f.get("is_compat_stub") else ""
                lines.append(
                    f"| [{f['name']}]({f['name']}) | {desc}{stub} | {n_cls} | {n_fn} | {n_lines} |"
                )
        elif ft in ("react-component", "typescript", "react-hook"):
            lines.extend([
                "| File | Exports | Lines |",
                "|------|---------|-------|",
            ])
            for f in files:
                exports = ", ".join(f.get("exports", [])[:5])
                if len(f.get("exports", [])) > 5:
                    exports += f" (+{len(f['exports']) - 5})"
                n_lines = f.get("size_lines", "?")
                lines.append(
                    f"| [{f['name']}]({f['name']}) | {exports} | {n_lines} |"
                )
        elif ft == "documentation":
            lines.extend([
                "| File | Title | Description | Lines |",
                "|------|-------|-------------|-------|",
            ])
            for f in files:
                title = f.get("title", "")[:40]
                desc = f.get("description", "")[:60]
                n_lines = f.get("size_lines", "?")
                lines.append(
                    f"| [{f['name']}]({f['name']}) | {title} | {desc} | {n_lines} |"
                )
        else:
            for f in files:
                desc = f.get("description", "")
                suffix = f" — {desc}" if desc else ""
                lines.append(f"- [{f['name']}]({f['name']}){suffix}")

        lines.append("")

    # Subfolders
    if index["subfolders"]:
        lines.extend(["## Subfolders", ""])
        lines.extend([
            "| Folder | Files | Description |",
            "|--------|-------|-------------|",
        ])
        for sf in index["subfolders"]:
            desc = sf.get("description", "")[:80]
            pkg = " 📦" if sf.get("is_package") else ""
            lines.append(
                f"| [{sf['name']}/]({sf['path']}){pkg} | {sf.get('file_count', '?')} | {desc} |"
            )
        lines.append("")

    md_path = output_path / "index.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  ✅ {md_path.relative_to(PROJECT_ROOT)}")


# ─── Main ───────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Generate enhanced folder indexes for AI agents"
    )
    parser.add_argument(
        "folder", nargs="?", help="Folder to index (or use --all)"
    )
    parser.add_argument(
        "--all", action="store_true", help="Generate indexes for all key folders"
    )
    parser.add_argument(
        "--recursive", action="store_true", help="Recurse into subfolders"
    )
    parser.add_argument(
        "--depth", type=int, default=3, help="Max recursion depth (default: 3)"
    )
    parser.add_argument(
        "--json-only", action="store_true", help="Generate only index.json"
    )
    parser.add_argument(
        "--md-only", action="store_true", help="Generate only index.md"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be generated"
    )
    args = parser.parse_args()

    if args.json_only and args.md_only:
        print("❌ Choose only one of --json-only or --md-only")
        sys.exit(1)

    # Determine which folders to process
    folders: list[Path] = []

    if args.all:
        for rel_path in KEY_FOLDERS:
            folder = PROJECT_ROOT / rel_path
            if folder.exists() and folder.is_dir():
                folders.append(folder)
            else:
                print(f"  ⏭️  Skipping (not found): {rel_path}")
    elif args.folder:
        folder = Path(args.folder)
        if not folder.is_absolute():
            folder = PROJECT_ROOT / folder
        folder = folder.resolve()

        if not folder.exists():
            print(f"❌ Folder not found: {folder}")
            sys.exit(1)

        folders.append(folder)

        if args.recursive:
            def collect_subfolders(parent: Path, depth: int):
                if depth <= 0:
                    return
                for d in sorted(parent.iterdir()):
                    if (
                        d.is_dir()
                        and not d.name.startswith((".", "_"))
                        and d.name not in SKIP_DIRS
                    ):
                        folders.append(d)
                        collect_subfolders(d, depth - 1)

            collect_subfolders(folder, args.depth)
    else:
        parser.print_help()
        sys.exit(1)

    print("=" * 60)
    print("📂 Enhanced Folder Index Generator")
    print("=" * 60)
    print(f"Folders to process: {len(folders)}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    generated = 0
    for folder in folders:
        rel = folder.relative_to(PROJECT_ROOT)
        print(f"📁 {rel}/")

        if args.dry_run:
            print(f"  Would generate: {rel}/index.json + {rel}/index.md")
            generated += 1
            continue

        try:
            index = scan_folder_enhanced(folder)

            if not args.md_only:
                generate_json(index, folder)
            if not args.json_only:
                generate_markdown(index, folder)

            generated += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")

    print()
    print("=" * 60)
    print(f"✨ Generated indexes for {generated}/{len(folders)} folder(s)")
    print("=" * 60)


if __name__ == "__main__":
    main()
