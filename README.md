<div align="center">
  <img src="logo.jpg" alt="MCP Tool Registry" width="500" />
</div>

# MCPT CLI

CLI for discovering and running MCP Tool Shop tools.

> **Why "mcpt"?** The official Anthropic `mcp` package exists on PyPI for the
> Model Context Protocol SDK. We use `mcpt` (MCP Tools) to avoid conflicts.
> The command is `mcpt`, but workspace configs remain `mcp.yaml` for ecosystem
> compatibility.

## Ecosystem & Backing Registry

`mcpt` is the official client for the **[mcp-tool-registry](https://github.com/mcp-tool-shop-org/mcp-tool-registry)**, the source of truth for the ecosystem.

- **[Public Explorer](https://mcp-tool-shop-org.github.io/mcp-tool-registry/)**: Browse available tools on the web.
- **[Registry Contract](https://github.com/mcp-tool-shop-org/mcp-tool-registry/blob/main/docs/contract.md)**: Understanding stability and metadata guarantees.
- **[Submit a Tool](https://github.com/mcp-tool-shop-org/mcp-tool-registry/issues/new/choose)**: Contribute to the ecosystem.

## Core Philosophy

- **Canonical Files**: We trust the `registry.index.json` artifact as the single source of truth.
- **Rules-Generated Bundles**: Trust tiers are derived from objective rules (Core, Ops, Agents, Evaluation), not manual curation.
- **Least Privilege**: Tools default to zero capability; access is always **opt-in**.

## Registry Compatibility

`mcpt` follows the MCP Tool Registry **v1.x** contract.

- **Supported Artifacts**: `registry.index.json` (v1 schema)
- **Pinning**: Use `mcpt init --registry-ref <git-tag>` to pin to a stable registry version (e.g., `v1.0.0`).

## Installation

```bash
pip install -e .
```

## Getting Started

```bash
mcpt list --refresh        # Fetch registry and see available tools
mcpt init                  # Create mcp.yaml in current directory
mcpt add file-compass      # Add a tool to your workspace
mcpt install file-compass  # Install via pip
mcpt run file-compass      # Stub run (safe by default)
```

## Usage

### List available tools

```bash
mcpt list
mcpt list --json
mcpt list --refresh  # Force refresh from remote
```

### Get tool info

```bash
mcpt info <tool-id>
mcpt info file-compass --json
```

### Search for tools

```bash
mcpt search filesystem
mcpt search agents --json
```

### Initialize a workspace

```bash
mcpt init              # Create mcp.yaml in current directory
mcpt init ./my-project # Create in specific directory
mcpt init --force      # Overwrite existing
```

### Add/remove tools from workspace

```bash
mcpt add file-compass
mcpt add tool-compass --ref v1.0.0
mcpt remove file-compass
```

### Install tools

```bash
mcpt install file-compass
mcpt install tool-compass --ref main
mcpt install dev-brain --venv ./venv
```

### Run tools

```bash
mcpt run file-compass           # Stub mode (shows plan)
mcpt run file-compass --real    # Actually execute
mcpt run file-compass -- --help # Pass args to tool
```

### Check configuration

```bash
mcpt doctor
```

## Configuration

MCPT uses `mcp.yaml` for workspace configuration:

```yaml
schema_version: "0.1"
name: "my-mcp-workspace"

registry:
  source: "https://github.com/mcp-tool-shop-org/mcp-tool-registry"
  ref: "v0.1.0"

tools:
  - file-compass
  - id: tool-compass
    ref: v1.0.0

run:
  safe_by_default: true
```

## What Does Pinning Mean?

When you set `registry.ref: v0.1.0` in `mcp.yaml`, you're pinning the **registry metadata**, not tool code.

- **Registry ref** → which version of the tool list you read
- **Tool ref** → pin individual tools with `mcpt add tool-id --ref v1.0.0`

Both matter for reproducibility. Pin the registry for consistent tool discovery, pin tools for consistent behavior.

## Development

```bash
pip install -e ".[dev]"
pytest
```
