# MCPT CLI

CLI for discovering and running MCP Tool Shop tools.

> **Why "mcpt"?** The official Anthropic `mcp` package exists on PyPI for the
> Model Context Protocol SDK. We use `mcpt` (MCP Tools) to avoid conflicts.
> The command is `mcpt`, but workspace configs remain `mcp.yaml` for ecosystem
> compatibility.

## How MCP Tool Shop Fits Together

- **Registry** ([mcp-tool-registry](https://github.com/mcp-tool-shop-org/mcp-tool-registry)) → what tools exist
- **CLI** → how you consume them (this repo)
- **Examples** ([mcp-examples](https://github.com/mcp-tool-shop-org/mcp-examples)) → how you learn the model
- **Tags** (v0.1.0, v0.2.0) → stability, reproducibility
- **main** → development only; may change without notice; builds may break
- **Tools default to least privilege** → no network, no writes, no side effects
- **Capability is always explicit and opt-in** → you decide when to enable

## Installation

### Via Homebrew (macOS/Linux) - Recommended

```bash
brew tap mcp-tool-shop-org/mcp-tools
brew install mcpt
```

### Via Local Development

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
