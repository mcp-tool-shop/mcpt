# MCPT CLI

CLI for discovering and running MCP Tool Shop tools.

> **Why "mcpt"?** The official Anthropic `mcp` package exists on PyPI for the
> Model Context Protocol SDK. We use `mcpt` (MCP Tools) to avoid conflicts.
> The command is `mcpt`, but workspace configs remain `mcp.yaml` for ecosystem
> compatibility.

## Installation

```bash
pip install -e .
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
  source: "https://github.com/mcp-tool-shop/mcp-tool-registry"
  ref: "main"

tools:
  - file-compass
  - id: tool-compass
    ref: v1.0.0

run:
  safe_by_default: true
```

## Development

```bash
pip install -e ".[dev]"
pytest
```
