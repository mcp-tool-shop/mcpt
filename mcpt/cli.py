"""MCPT CLI - CLI for discovering and running MCP Tool Shop tools."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Annotated, List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mcpt import __version__
from mcpt.registry import RegistryConfig, get_registry, get_registry_status, get_tool, search_tools
from mcpt.workspace import (
    MCP_YAML_FILENAME,
    add_tool as workspace_add_tool,
    read_config,
    remove_tool as workspace_remove_tool,
    write_default,
)
from mcpt.runner import generate_run_plan, stub_run

app = typer.Typer(
    help="CLI for discovering and running MCP Tool Shop tools.",
    no_args_is_help=True,
)


def fuzzy_match_tools(query: str, limit: int = 5) -> list[dict]:
    """Find tools with similar names using simple fuzzy matching."""
    from difflib import SequenceMatcher

    registry = get_registry()
    tools = registry.get("tools", [])
    query_lower = query.lower()

    scored = []
    for tool in tools:
        tool_id = tool.get("id", "")
        # Score based on: substring match, sequence similarity, starts-with
        score = 0
        if query_lower in tool_id.lower():
            score += 0.5
        if tool_id.lower().startswith(query_lower):
            score += 0.3
        score += SequenceMatcher(None, query_lower, tool_id.lower()).ratio() * 0.5
        if score > 0.2:
            scored.append((score, tool))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scored[:limit]]


console = Console()


# ============================================================================
# Global options
# ============================================================================


def version_callback(value: bool) -> None:
    if value:
        console.print(f"mcpt {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = False,
) -> None:
    """MCPT CLI - Discover and run MCP Tool Shop tools."""
    pass


# ============================================================================
# Registry commands
# ============================================================================


@app.command("list")
def list_tools(
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
    refresh: Annotated[bool, typer.Option("--refresh", help="Force refresh from remote")] = False,
) -> None:
    """List all available tools in the registry."""
    try:
        registry = get_registry(force_refresh=refresh)
    except Exception as e:
        console.print(f"[red]Error fetching registry:[/red] {e}")
        raise typer.Exit(1)

    tools = registry.get("tools", [])

    if json_output:
        console.print(json.dumps(tools, indent=2))
        return

    if not tools:
        console.print("[dim]No tools found in registry.[/dim]")
        return

    table = Table(title="MCP Tools")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Description")
    table.add_column("Tags", style="dim")

    for tool in tools:
        table.add_row(
            tool.get("id", ""),
            tool.get("name", ""),
            tool.get("description", "")[:60] + "..." if len(tool.get("description", "")) > 60 else tool.get("description", ""),
            ", ".join(tool.get("tags", [])),
        )

    console.print(table)


@app.command()
def info(
    tool_id: Annotated[str, typer.Argument(help="Tool ID to get info for")],
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show detailed information about a tool."""
    tool = get_tool(tool_id)

    if tool is None:
        console.print(f"[red]Tool not found:[/red] {tool_id}")
        console.print("[dim]Stale registry? Try: mcpt list --refresh[/dim]")
        raise typer.Exit(1)

    if json_output:
        console.print(json.dumps(tool, indent=2))
        return

    console.print()
    console.print(Panel(f"[bold cyan]{tool.get('name', '')}[/bold cyan]", subtitle=tool.get("id", "")))

    table = Table(show_header=False, box=None)
    table.add_column("Key", style="dim", width=15)
    table.add_column("Value")

    table.add_row("Description", tool.get("description", ""))
    table.add_row("Repository", tool.get("repo", ""))
    table.add_row("Install Type", tool.get("install", {}).get("type", ""))
    table.add_row("Git URL", tool.get("install", {}).get("url", ""))
    table.add_row("Default Ref", tool.get("install", {}).get("default_ref", ""))
    table.add_row("Tags", ", ".join(tool.get("tags", [])))
    table.add_row("Safe Run", str(tool.get("defaults", {}).get("safe_run", True)))

    console.print(table)
    console.print()


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search query")],
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Search for tools by name, description, or tags."""
    results = search_tools(query)

    if json_output:
        console.print(json.dumps(results, indent=2))
        return

    if not results:
        console.print(f"[dim]No tools found matching:[/dim] {query}")
        console.print("[dim]Stale registry? Try: mcpt list --refresh[/dim]")
        return

    table = Table(title=f"Search Results: {query}")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Description")
    table.add_column("Tags", style="dim")

    for tool in results:
        table.add_row(
            tool.get("id", ""),
            tool.get("name", ""),
            tool.get("description", "")[:50] + "..." if len(tool.get("description", "")) > 50 else tool.get("description", ""),
            ", ".join(tool.get("tags", [])),
        )

    console.print(table)


# ============================================================================
# Workspace commands
# ============================================================================


@app.command()
def init(
    path: Annotated[
        Optional[Path],
        typer.Argument(help="Directory to initialize (default: current directory)"),
    ] = None,
    force: Annotated[bool, typer.Option("--force", "-f", help="Overwrite existing mcp.yaml")] = False,
    registry_ref: Annotated[
        Optional[str],
        typer.Option("--registry-ref", help="Registry git ref (default: v0.1.0)"),
    ] = None,
) -> None:
    """Initialize a new MCP workspace with mcp.yaml."""
    from mcpt.registry.client import DEFAULT_REF

    if path is None:
        path = Path.cwd()

    config_path = path / MCP_YAML_FILENAME

    if config_path.exists() and not force:
        console.print(f"[yellow]{MCP_YAML_FILENAME} already exists.[/yellow] Use --force to overwrite.")
        raise typer.Exit(1)

    path.mkdir(parents=True, exist_ok=True)
    write_default(config_path, registry_ref=registry_ref or DEFAULT_REF)
    console.print(f"[green]Created[/green] {config_path}")


@app.command()
def add(
    tool_id: Annotated[str, typer.Argument(help="Tool ID to add")],
    ref: Annotated[Optional[str], typer.Option("--ref", help="Git ref to use")] = None,
    path: Annotated[
        Optional[Path],
        typer.Option("--path", "-p", help="Path to mcp.yaml"),
    ] = None,
) -> None:
    """Add a tool to the workspace configuration."""
    if path is None:
        path = Path.cwd() / MCP_YAML_FILENAME

    if not path.exists():
        console.print(f"[red]{MCP_YAML_FILENAME} not found.[/red] Run 'mcpt init' first.")
        raise typer.Exit(1)

    # Verify tool exists in registry
    tool = get_tool(tool_id)
    if tool is None:
        console.print(f"[red]Tool not found in registry:[/red] {tool_id}")
        # Show fuzzy matches
        similar = fuzzy_match_tools(tool_id)
        if similar:
            console.print("[dim]Did you mean:[/dim]")
            for t in similar:
                console.print(f"  [cyan]{t.get('id')}[/cyan] - {t.get('name', '')}")
        console.print("[dim]Stale registry? Try: mcpt list --refresh[/dim]")
        raise typer.Exit(1)

    if workspace_add_tool(path, tool_id, ref):
        console.print(f"[green]Added[/green] {tool_id} to {path}")
        # Show capability hints if tool has side effects
        defaults = tool.get("defaults", {})
        if not defaults.get("safe_run", True):
            console.print("[dim]Note: This tool has side effects. Check its documentation for capability env vars.[/dim]")
    else:
        console.print(f"[yellow]{tool_id} already in workspace.[/yellow]")


@app.command()
def remove(
    tool_id: Annotated[str, typer.Argument(help="Tool ID to remove")],
    path: Annotated[
        Optional[Path],
        typer.Option("--path", "-p", help="Path to mcp.yaml"),
    ] = None,
) -> None:
    """Remove a tool from the workspace configuration."""
    if path is None:
        path = Path.cwd() / MCP_YAML_FILENAME

    if not path.exists():
        console.print(f"[red]{MCP_YAML_FILENAME} not found.[/red]")
        raise typer.Exit(1)

    if workspace_remove_tool(path, tool_id):
        console.print(f"[green]Removed[/green] {tool_id} from {path}")
    else:
        console.print(f"[yellow]{tool_id} not found in workspace.[/yellow]")


# ============================================================================
# Install command
# ============================================================================


@app.command()
def install(
    tool_id: Annotated[str, typer.Argument(help="Tool ID to install")],
    ref: Annotated[Optional[str], typer.Option("--ref", help="Git ref to install")] = None,
    venv: Annotated[
        Optional[Path],
        typer.Option("--venv", help="Virtual environment to install into"),
    ] = None,
) -> None:
    """Install a tool via git into a virtual environment."""
    tool = get_tool(tool_id)

    if tool is None:
        console.print(f"[red]Tool not found:[/red] {tool_id}")
        raise typer.Exit(1)

    install_info = tool.get("install", {})
    if install_info.get("type") != "git":
        console.print(f"[red]Unsupported install type:[/red] {install_info.get('type')}")
        raise typer.Exit(1)

    git_url = install_info.get("url", "")
    git_ref = ref or install_info.get("default_ref", "main")

    # Determine pip executable
    if venv:
        pip_path = venv / "Scripts" / "pip.exe" if sys.platform == "win32" else venv / "bin" / "pip"
        if not pip_path.exists():
            console.print(f"[red]pip not found in venv:[/red] {pip_path}")
            raise typer.Exit(1)
        pip_cmd = str(pip_path)
    else:
        pip_cmd = "pip"

    # Install via pip git+url@ref
    install_url = f"git+{git_url}@{git_ref}"
    console.print(f"[dim]Installing {tool_id} from {install_url}...[/dim]")

    try:
        result = subprocess.run(
            [pip_cmd, "install", install_url],
            capture_output=True,
            text=True,
            check=True,
        )
        console.print(f"[green]Installed[/green] {tool_id}")
        if result.stdout:
            console.print(result.stdout)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Installation failed:[/red]")
        if e.stderr:
            console.print(e.stderr)
        raise typer.Exit(1)


# ============================================================================
# Run command
# ============================================================================


@app.command()
def run(
    tool_id: Annotated[str, typer.Argument(help="Tool ID to run")],
    args: Annotated[Optional[List[str]], typer.Argument(help="Arguments to pass to the tool")] = None,
    real: Annotated[bool, typer.Option("--real", help="Actually execute (not stub)")] = False,
) -> None:
    """Run a tool (stub by default, use --real to execute)."""
    tool = get_tool(tool_id)

    if tool is None:
        console.print(f"[red]Tool not found:[/red] {tool_id}")
        raise typer.Exit(1)

    plan = generate_run_plan(tool, args)

    if not real:
        stub_run(tool_id, plan)
        return

    # Real execution - for now, just show what would happen
    console.print(f"[bold green]Executing[/bold green] {tool_id}...")
    console.print("[yellow]Real execution not yet implemented.[/yellow]")
    console.print("[dim]Tool would be executed with the following plan:[/dim]")
    console.print(json.dumps(plan, indent=2))


# ============================================================================
# Utility commands
# ============================================================================


@app.command()
def doctor() -> None:
    """Check MCPT CLI configuration and connectivity."""
    console.print("[bold]MCPT Doctor[/bold]")
    console.print()

    # Check Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    console.print(f"[dim]Python:[/dim] {py_version}")

    # Registry provenance
    console.print()
    console.print("[bold]Registry Status[/bold]")
    status = get_registry_status()
    console.print(f"  [dim]Source:[/dim] {status.source}")
    console.print(f"  [dim]Ref:[/dim] {status.ref}")
    if status.ref == "main":
        console.print("  [yellow]Tip:[/yellow] Pin to a tagged release (e.g., v0.1.0) for reproducibility.")
    console.print(f"  [dim]Cache:[/dim] {status.cache_path}")

    if status.cache_exists:
        mtime_str = status.cache_mtime.strftime("%Y-%m-%d %H:%M:%S") if status.cache_mtime else "unknown"
        console.print(f"  [dim]Last fetched:[/dim] {mtime_str}")
        console.print(f"  [dim]Cached tools:[/dim] {status.tool_count}")

        # Provenance indicator
        if status.provenance == "cache":
            console.print(f"  [yellow]Provenance:[/yellow] Loaded from cache (use --refresh to update)")
        elif status.provenance == "local_file":
            console.print(f"  [yellow]Provenance:[/yellow] Local file (not from remote)")
    else:
        console.print(f"  [dim]Cache:[/dim] not found")

    # Check remote connectivity
    console.print()
    console.print("[dim]Checking remote connectivity...[/dim]")
    try:
        registry = get_registry(force_refresh=True)
        tool_count = len(registry.get("tools", []))
        console.print(f"[green]Remote OK[/green] - {tool_count} tools fetched")
    except Exception as e:
        console.print(f"[red]Remote error:[/red] {e}")
        if status.cache_exists:
            console.print(f"[yellow]Using cached registry ({status.tool_count} tools)[/yellow]")

    # Check for mcp.yaml in current directory
    console.print()
    config_path = Path.cwd() / MCP_YAML_FILENAME
    workspace_exists = config_path.exists()
    workspace_tools = 0
    workspace_ref = None

    if workspace_exists:
        try:
            config = read_config(config_path)
            workspace_tools = len(config.get("tools", []))
            workspace_ref = config.get("registry", {}).get("ref")
            console.print(f"[green]Workspace OK[/green] - {workspace_tools} tools configured")
        except Exception as e:
            console.print(f"[yellow]Workspace config error:[/yellow] {e}")
    else:
        console.print(f"[dim]No {MCP_YAML_FILENAME} in current directory[/dim]")

    # Next steps (max 3 bullets based on current state)
    console.print()
    console.print("[bold]Next Steps[/bold]")
    next_steps = []

    if not workspace_exists:
        next_steps.append("Run [cyan]mcpt init[/cyan] to create a workspace")
    elif workspace_tools == 0:
        next_steps.append("Run [cyan]mcpt add <tool-id>[/cyan] to add a tool")

    if workspace_ref == "main":
        next_steps.append("Edit mcp.yaml to pin [cyan]ref: v0.1.0[/cyan] for reproducibility")

    if not status.cache_exists:
        next_steps.append("Run [cyan]mcpt list --refresh[/cyan] to fetch the registry")

    if not next_steps:
        next_steps.append("[green]All good![/green] Run [cyan]mcpt list[/cyan] to explore tools")

    for step in next_steps[:3]:
        console.print(f"  • {step}")

    console.print()
    console.print("[green]Doctor complete.[/green]")


if __name__ == "__main__":
    app()
