"""Registry client with GitHub fetch and local caching."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from platformdirs import user_cache_dir

# Update this to your actual org/repo when deploying
DEFAULT_REGISTRY_SOURCE = "https://github.com/mcp-tool-shop/mcp-tool-registry"
DEFAULT_REF = "main"


def github_raw_registry_url(source: str, ref: str) -> str:
    """Convert GitHub repo URL to raw registry.json URL."""
    parts = source.rstrip("/").split("/")
    org, repo = parts[-2], parts[-1]
    return f"https://raw.githubusercontent.com/{org}/{repo}/{ref}/registry.json"


@dataclass(frozen=True)
class RegistryConfig:
    """Configuration for registry source."""

    source: str = DEFAULT_REGISTRY_SOURCE
    ref: str = DEFAULT_REF


def registry_cache_path(cfg: RegistryConfig) -> Path:
    """Get the cache path for the registry."""
    base = Path(user_cache_dir("mcp", "mcp-tool-shop"))
    return base / "registry" / cfg.ref / "registry.json"


def load_cached_registry(cfg: RegistryConfig) -> dict[str, Any] | None:
    """Load registry from local cache if available."""
    p = registry_cache_path(cfg)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def save_cached_registry(cfg: RegistryConfig, data: dict[str, Any]) -> None:
    """Save registry to local cache."""
    p = registry_cache_path(cfg)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def load_local_registry(path: Path) -> dict[str, Any]:
    """Load registry from a local file."""
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_registry(cfg: RegistryConfig) -> dict[str, Any]:
    """Fetch registry from GitHub or local file."""
    # Support local file paths
    source_path = Path(cfg.source)
    if source_path.exists() and source_path.is_file():
        return load_local_registry(source_path)

    url = github_raw_registry_url(cfg.source, cfg.ref)
    r = httpx.get(url, timeout=20.0)
    r.raise_for_status()
    return r.json()


def get_registry(
    cfg: RegistryConfig | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    """Get registry, using cache if available unless force_refresh is True."""
    if cfg is None:
        cfg = RegistryConfig()

    if not force_refresh:
        cached = load_cached_registry(cfg)
        if cached is not None:
            return cached

    data = fetch_registry(cfg)
    save_cached_registry(cfg, data)
    return data


def get_tool(tool_id: str, cfg: RegistryConfig | None = None) -> dict[str, Any] | None:
    """Get a specific tool by ID."""
    registry = get_registry(cfg)
    for tool in registry.get("tools", []):
        if tool.get("id") == tool_id:
            return tool
    return None


def search_tools(
    query: str,
    cfg: RegistryConfig | None = None,
) -> list[dict[str, Any]]:
    """Search tools by name, description, or tags."""
    registry = get_registry(cfg)
    query_lower = query.lower()
    results = []

    for tool in registry.get("tools", []):
        # Search in id, name, description, and tags
        if query_lower in tool.get("id", "").lower():
            results.append(tool)
        elif query_lower in tool.get("name", "").lower():
            results.append(tool)
        elif query_lower in tool.get("description", "").lower():
            results.append(tool)
        elif any(query_lower in tag.lower() for tag in tool.get("tags", [])):
            results.append(tool)

    return results


@dataclass
class RegistryStatus:
    """Status information about the registry."""

    source: str
    ref: str
    cache_path: Path
    cache_exists: bool
    cache_mtime: datetime | None
    tool_count: int
    provenance: str  # "cache", "remote", "local_file", "not_loaded"


def get_registry_status(cfg: RegistryConfig | None = None) -> RegistryStatus:
    """Get status information about the registry without fetching."""
    if cfg is None:
        cfg = RegistryConfig()

    cache_path = registry_cache_path(cfg)
    cache_exists = cache_path.exists()
    cache_mtime = None
    tool_count = 0
    provenance = "not_loaded"

    if cache_exists:
        cache_mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        try:
            data = json.loads(cache_path.read_text(encoding="utf-8"))
            tool_count = len(data.get("tools", []))
            provenance = "cache"
        except Exception:
            pass

    # Check if source is a local file
    source_path = Path(cfg.source)
    if source_path.exists() and source_path.is_file():
        provenance = "local_file"

    return RegistryStatus(
        source=cfg.source,
        ref=cfg.ref,
        cache_path=cache_path,
        cache_exists=cache_exists,
        cache_mtime=cache_mtime,
        tool_count=tool_count,
        provenance=provenance,
    )
