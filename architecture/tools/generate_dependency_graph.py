from __future__ import annotations

import ast
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = ROOT / "Python" / "structural_lib"
OUTPUT_PATH = ROOT / "docs" / "architecture" / "dependencies.png"

EXCLUDE_FILES = {"__init__.py", "__main__.py"}


def resolve_relative(
    current: str, level: int, module: str | None, name: str | None
) -> str:
    parts = current.split(".")
    if level:
        parts = parts[:-level]
    if module:
        parts.extend(module.split("."))
    if name:
        parts.append(name)
    return ".".join(parts)


def build_graph() -> nx.DiGraph:
    module_files = [
        path for path in SOURCE_ROOT.rglob("*.py") if path.name not in EXCLUDE_FILES
    ]

    module_names = {}
    for path in module_files:
        rel = path.relative_to(SOURCE_ROOT).with_suffix("")
        module = ".".join(("structural_lib",) + rel.parts)
        module_names[path] = module

    modules = set(module_names.values())
    edges: set[tuple[str, str]] = set()

    for path, current in module_names.items():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    target = alias.name
                    if target in modules:
                        edges.add((current, target))
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    base = node.module
                    if base in modules:
                        edges.add((current, base))
                    for alias in node.names:
                        candidate = f"{base}.{alias.name}"
                        if candidate in modules:
                            edges.add((current, candidate))
                    continue

                base = resolve_relative(current, node.level, node.module, None)
                if base in modules:
                    edges.add((current, base))
                for alias in node.names:
                    candidate = resolve_relative(
                        current, node.level, node.module, alias.name
                    )
                    if candidate in modules:
                        edges.add((current, candidate))

    graph = nx.DiGraph()
    for module in sorted(modules):
        graph.add_node(module)
    for source, target in sorted(edges):
        if source in modules and target in modules:
            graph.add_edge(source, target)

    return graph


def draw_graph(graph: nx.DiGraph) -> None:
    labels = {m: m.replace("structural_lib.", "") for m in graph.nodes}
    node_colors = [
        "#7aa6c2" if m.startswith("structural_lib.insights.") else "#c9d6df"
        for m in graph.nodes
    ]

    plt.figure(figsize=(12, 9))
    pos = nx.spring_layout(graph, k=0.9, seed=42)

    nx.draw_networkx_edges(
        graph,
        pos,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=10,
        edge_color="#8a8f95",
        width=0.8,
    )

    nx.draw_networkx_nodes(
        graph,
        pos,
        node_color=node_colors,
        node_size=900,
        linewidths=0.8,
        edgecolors="#4b5563",
    )

    nx.draw_networkx_labels(
        graph,
        pos,
        labels=labels,
        font_size=7,
        font_color="#1f2933",
    )

    plt.axis("off")
    plt.tight_layout()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUTPUT_PATH, dpi=160)


def main() -> None:
    graph = build_graph()
    draw_graph(graph)


if __name__ == "__main__":
    main()
