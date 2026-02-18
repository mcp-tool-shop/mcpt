<p align="center"><img src="logo.png" alt="mcpt logo" width="200"></p>

# mcpt

> Part of [MCP Tool Shop](https://mcptoolshop.com)

**CLI for discovering, installing, and running MCP Tool Shop tools.**

[![PyPI version](https://img.shields.io/pypi/v/mcp-select)](https://pypi.org/project/mcp-select/)
[![npm version](https://img.shields.io/npm/v/@mcptoolshop/mcpt)](https://www.npmjs.com/package/@mcptoolshop/mcpt)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## At a Glance

- **Official client** for the [mcp-tool-registry](https://github.com/mcp-tool-shop-org/mcp-tool-registry) -- the canonical source of truth for MCP Tool Shop tools
- **Workspace management** via `mcp.yaml` -- declare, pin, and share tool sets across projects
- **Trust tiers** (trusted / verified / neutral / experimental) and **risk auras** that surface capability-level danger at a glance
- **Safe-by-default execution** -- tools run in stub mode unless explicitly promoted, with capability grants enforced before real execution
- **Registry pinning** for reproducibility -- lock the registry ref *and* individual tool refs so builds are deterministic
- **Rich TUI** with `--plain` and `NO_COLOR` support for accessible, CI-friendly output

## Installation

### Python (recommended)

```bash
pip install mcp-select
```

> **Why `mcp-select`?** The official Anthropic `mcp` package exists on PyPI for the
> Model Context Protocol SDK. We use `mcp-select` as the package name to avoid
> conflicts. The CLI command is always `mcpt`.

### npm wrapper

```bash
npx @mcptoolshop/mcpt          # one-shot
npm install -g @mcptoolshop/mcpt  # global install
```

The npm package auto-installs the Python `mcp-select` package via a postinstall hook. Python 3.10+ is required.

## Getting Started

```bash
mcpt list --refresh        # Fetch the registry and browse available tools
mcpt init                  # Create mcp.yaml in the current directory
mcpt add file-compass      # Add a tool to your workspace
mcpt install file-compass  # Install the tool via pip
mcpt run file-compass      # Run in stub mode (safe by default)
```

## Commands

| Command | Description |
|---------|-------------|
| `mcpt list` | List all available tools in the registry |
| `mcpt info <tool-id>` | Show detailed information about a tool |
| `mcpt search <query>` | Search for tools with ranked results |
| `mcpt init` | Initialize a workspace (`mcp.yaml`) |
| `mcpt add <tool-id>` | Add a tool to the workspace |
| `mcpt remove <tool-id>` | Remove a tool from the workspace |
| `mcpt install <tool-id>` | Install a tool via git into a virtual environment |
| `mcpt run <tool-id>` | Run a tool (stub by default, `--mode restricted` for real execution) |
| `mcpt grant <tool-id> <cap>` | Grant a capability to a tool |
| `mcpt revoke <tool-id> <cap>` | Revoke a capability from a tool |
| `mcpt check <tool-id>` | Pre-flight check before execution |
| `mcpt doctor` | Check CLI configuration and registry connectivity |
| `mcpt icons` | Show the visual-language cheat sheet (trust tiers, risk markers, badges) |
| `mcpt bundles` | List available tool bundles |
| `mcpt featured` | Browse featured tools and curated collections |
| `mcpt facets` | Show registry facets and statistics |
| `mcpt registry` | Show detailed registry status and provenance |

Most commands accept `--json` for machine-readable output and `--plain` for color-free rendering.

## Configuration

mcpt uses `mcp.yaml` for workspace configuration:

```yaml
schema_version: "0.1"
name: "my-mcp-workspace"

registry:
  source: "https://github.com/mcp-tool-shop-org/mcp-tool-registry"
  ref: "v0.3.0"

tools:
  - file-compass
  - id: tool-compass
    ref: v1.0.0
    grants:
      - network

run:
  safe_by_default: true

ui:
  sigil: unicode   # unicode | ascii | off
  badges: on       # on | off
```

### Pinning

When you set `registry.ref: v0.3.0` in `mcp.yaml`, you pin the **registry metadata** -- which version of the tool list you read. This is separate from tool-level refs:

- **Registry ref** -- which snapshot of the tool catalog you use
- **Tool ref** -- pin individual tools with `mcpt add tool-id --ref v1.0.0`

Both matter for reproducibility. Pin the registry for consistent tool discovery; pin tools for consistent behavior.

## Ecosystem

mcpt is the official client for the **[mcp-tool-registry](https://github.com/mcp-tool-shop-org/mcp-tool-registry)**.

- **[Public Explorer](https://mcp-tool-shop-org.github.io/mcp-tool-registry/)** -- Browse available tools on the web
- **[Registry Contract](https://github.com/mcp-tool-shop-org/mcp-tool-registry/blob/main/docs/contract.md)** -- Stability and metadata guarantees
- **[Submit a Tool](https://github.com/mcp-tool-shop-org/mcp-tool-registry/issues/new/choose)** -- Contribute to the ecosystem

## Docs

| Document | Description |
|----------|-------------|
| [HANDBOOK.md](HANDBOOK.md) | Deep-dive guide: architecture, workspace model, trust & safety, CI patterns, FAQ |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute to mcpt |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community standards |
| [CHANGELOG.md](CHANGELOG.md) | Release history |

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

[MIT](LICENSE)
