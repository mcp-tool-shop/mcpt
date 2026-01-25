"""Workspace configuration for MCP."""

from .config import (
    default_yaml,
    write_default,
    read_config,
    write_config,
    add_tool,
    remove_tool,
    MCP_YAML_FILENAME,
)

__all__ = [
    "default_yaml",
    "write_default",
    "read_config",
    "write_config",
    "add_tool",
    "remove_tool",
    "MCP_YAML_FILENAME",
]
