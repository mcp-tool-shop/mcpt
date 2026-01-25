"""Workspace configuration (mcp.yaml) management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from mcpt.registry.client import DEFAULT_REGISTRY_SOURCE, DEFAULT_REF

MCP_YAML_FILENAME = "mcp.yaml"


def default_yaml(registry_source: str, registry_ref: str) -> str:
    """Generate default mcp.yaml content."""
    return (
        'schema_version: "0.1"\n'
        'name: "my-mcp-workspace"\n\n'
        "registry:\n"
        f'  source: "{registry_source}"\n'
        f'  ref: "{registry_ref}"\n\n'
        "tools: []\n\n"
        "run:\n"
        "  safe_by_default: true\n"
    )


def write_default(
    path: Path,
    registry_source: str = DEFAULT_REGISTRY_SOURCE,
    registry_ref: str = DEFAULT_REF,
) -> None:
    """Write default mcp.yaml to path."""
    path.write_text(default_yaml(registry_source, registry_ref), encoding="utf-8")


def read_config(path: Path) -> dict[str, Any]:
    """Read mcp.yaml configuration."""
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def write_config(path: Path, config: dict[str, Any]) -> None:
    """Write configuration to mcp.yaml."""
    path.write_text(
        yaml.dump(config, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def add_tool(path: Path, tool_id: str, ref: str | None = None) -> bool:
    """Add a tool to the workspace configuration.

    Returns True if the tool was added, False if it already exists.
    """
    config = read_config(path)
    tools = config.get("tools", [])

    # Check if tool already exists
    for tool in tools:
        if isinstance(tool, str) and tool == tool_id:
            return False
        if isinstance(tool, dict) and tool.get("id") == tool_id:
            return False

    # Add the tool
    if ref:
        tools.append({"id": tool_id, "ref": ref})
    else:
        tools.append(tool_id)

    config["tools"] = tools
    write_config(path, config)
    return True


def remove_tool(path: Path, tool_id: str) -> bool:
    """Remove a tool from the workspace configuration.

    Returns True if the tool was removed, False if it wasn't found.
    """
    config = read_config(path)
    tools = config.get("tools", [])
    original_len = len(tools)

    # Filter out the tool
    new_tools = []
    for tool in tools:
        if isinstance(tool, str) and tool == tool_id:
            continue
        if isinstance(tool, dict) and tool.get("id") == tool_id:
            continue
        new_tools.append(tool)

    if len(new_tools) == original_len:
        return False

    config["tools"] = new_tools
    write_config(path, config)
    return True
