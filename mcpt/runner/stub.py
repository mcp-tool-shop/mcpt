"""Stub runner for MCP tools - safe by default."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def generate_run_plan(tool: dict[str, Any], args: list[str] | None = None) -> dict[str, Any]:
    """Generate an execution plan for a tool without actually running it."""
    install = tool.get("install", {})

    plan = {
        "tool_id": tool.get("id"),
        "tool_name": tool.get("name"),
        "action": "run",
        "install": {
            "type": install.get("type"),
            "url": install.get("url"),
            "ref": install.get("default_ref"),
        },
        "args": args or [],
        "safe_run": tool.get("defaults", {}).get("safe_run", True),
    }

    return plan


def stub_run(tool_id: str, plan: dict[str, Any]) -> None:
    """Print execution plan without running (stub mode)."""
    console.print()
    console.print(
        Panel(
            f"[bold yellow]STUB MODE[/bold yellow] - Would run tool: [bold cyan]{tool_id}[/bold cyan]",
            title="Execution Plan",
            border_style="yellow",
        )
    )

    table = Table(show_header=False, box=None)
    table.add_column("Key", style="dim")
    table.add_column("Value")

    table.add_row("Tool ID", plan.get("tool_id", ""))
    table.add_row("Tool Name", plan.get("tool_name", ""))
    table.add_row("Install Type", plan.get("install", {}).get("type", ""))
    table.add_row("Git URL", plan.get("install", {}).get("url", ""))
    table.add_row("Git Ref", plan.get("install", {}).get("ref", ""))
    table.add_row("Arguments", " ".join(plan.get("args", [])) or "(none)")
    table.add_row("Safe Run", str(plan.get("safe_run", True)))

    console.print(table)
    console.print()
    console.print("[dim]Use --real to actually execute the tool.[/dim]")
