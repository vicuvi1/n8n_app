"""Parse n8n workflow JSON into visual flow representations."""

from __future__ import annotations

import re
from typing import Any


def _node_sort_key(node: dict[str, Any]) -> tuple[float, float]:
    pos = node.get("position") or [0, 0]
    return (float(pos[0]) if len(pos) > 0 else 0, float(pos[1]) if len(pos) > 1 else 0)


def _short_type(node_type: str) -> str:
    if not node_type:
        return "node"
    return node_type.split(".")[-1].replace("Trigger", " ▶")


def _escape_mermaid(text: str) -> str:
    return re.sub(r'["\[\]{}()|<>#]', " ", str(text)).strip()[:40]


def build_linear_flow_text(workflow: dict[str, Any]) -> str:
    """Left-to-right node chain based on canvas position."""
    nodes = sorted(workflow.get("nodes", []), key=_node_sort_key)
    if not nodes:
        return "No nodes in workflow"
    return "  →  ".join(n.get("name", "Unnamed") for n in nodes)


def build_connection_edges(workflow: dict[str, Any]) -> list[tuple[str, str]]:
    """Extract (source, target) pairs from n8n connections object."""
    edges: list[tuple[str, str]] = []
    connections = workflow.get("connections") or {}

    for source_name, outputs in connections.items():
        if not isinstance(outputs, dict):
            continue
        for _output_key, chains in outputs.items():
            if not isinstance(chains, list):
                continue
            for chain in chains:
                if not isinstance(chain, list):
                    continue
                for link in chain:
                    if isinstance(link, dict) and link.get("node"):
                        edges.append((source_name, link["node"]))

    return edges


def build_mermaid_diagram(workflow: dict[str, Any]) -> str:
    """Build a Mermaid flowchart LR diagram from workflow nodes and connections."""
    nodes = workflow.get("nodes", [])
    if not nodes:
        return "graph LR\n  empty[No nodes]"

    name_to_id: dict[str, str] = {}
    lines = ["graph LR"]

    for index, node in enumerate(sorted(nodes, key=_node_sort_key)):
        name = node.get("name", f"Node {index}")
        node_id = f"N{index}"
        name_to_id[name] = node_id
        label = _escape_mermaid(name)
        short = _escape_mermaid(_short_type(node.get("type", "")))
        lines.append(f'  {node_id}["{label}<br/><small>{short}</small>"]')

    edges = build_connection_edges(workflow)
    seen_edges: set[tuple[str, str]] = set()

    for source, target in edges:
        if source in name_to_id and target in name_to_id:
            edge = (source, target)
            if edge not in seen_edges:
                seen_edges.add(edge)
                lines.append(f"  {name_to_id[source]} --> {name_to_id[target]}")

    # Fallback: chain by position if no connections defined
    if not seen_edges and len(nodes) > 1:
        ordered = [n.get("name", "") for n in sorted(nodes, key=_node_sort_key)]
        for i in range(len(ordered) - 1):
            a, b = ordered[i], ordered[i + 1]
            if a in name_to_id and b in name_to_id:
                lines.append(f"  {name_to_id[a]} -.-> {name_to_id[b]}")

    return "\n".join(lines)


def get_node_summary(workflow: dict[str, Any]) -> list[dict[str, str]]:
    """Return a list of node summaries for UI cards."""
    summaries = []
    for node in sorted(workflow.get("nodes", []), key=_node_sort_key):
        summaries.append(
            {
                "name": node.get("name", "Unnamed"),
                "type": _short_type(node.get("type", "")),
            }
        )
    return summaries
