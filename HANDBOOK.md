# mcpt Handbook

A deep-dive guide to mcpt -- the official CLI for discovering, installing, and running MCP Tool Shop tools.

---

## Table of Contents

1. [What is mcpt?](#what-is-mcpt)
2. [Architecture](#architecture)
3. [Workspace Model](#workspace-model)
4. [Registry Integration](#registry-integration)
5. [Tool Lifecycle](#tool-lifecycle)
6. [Trust & Safety Model](#trust--safety-model)
7. [Visual Language](#visual-language)
8. [Bundle System](#bundle-system)
9. [Command Reference](#command-reference)
10. [CI & Automation](#ci--automation)
11. [The npm Wrapper](#the-npm-wrapper)
12. [Troubleshooting & FAQ](#troubleshooting--faq)

---

## What is mcpt?

mcpt is the official package manager and runner for the [MCP Tool Shop](https://mcptoolshop.com) ecosystem. It is the client-side counterpart to the [mcp-tool-registry](https://github.com/mcp-tool-shop-org/mcp-tool-registry), which serves as the canonical catalog of available tools.

mcpt handles the full tool lifecycle: discovery, workspace declaration, installation, capability gating, and execution. It is designed to be safe by default -- tools cannot perform dangerous operations unless you explicitly grant them the required capabilities.

### Package naming

The Python package is published as `mcp-select` on PyPI. This avoids a namespace collision with Anthropic's official `mcp` package (the Model Context Protocol SDK). The CLI command is always `mcpt`, and workspace configuration files use `mcp.yaml` for ecosystem compatibility.

---

## Architecture

```
mcpt CLI (Typer + Rich)
  |
  |-- registry/          # Registry client: fetch, cache, search, bundles, featured
  |     |-- client.py    # HTTP fetch, local cache, graceful degradation
  |     +-- featured.py  # Featured tools and curated collections
  |
  |-- workspace/          # Workspace config management
  |     +-- config.py    # mcp.yaml read/write, grants, lock records, run stats
  |
  |-- runner/             # Tool execution engine
  |     +-- stub.py      # Stub runner (dry-run execution plans)
  |
  |-- ui/                 # Rendering and visual language
  |     |-- trust.py     # Trust tier definitions and precedence
  |     |-- risk.py      # Risk scoring and tiering
  |     |-- caps.py      # Capability badge definitions
  |     |-- sigil.py     # Deterministic sigil generation (SHA-256 based)
  |     |-- render.py    # Table and header rendering
  |     |-- legend.py    # Visual cheat sheet (mcpt icons)
  |     |-- featured.py  # Featured view rendering
  |     +-- style.py     # Style utilities
  |
  +-- cli.py              # Typer application and command definitions
```

### Data flow

1. **Registry fetch** -- mcpt downloads `registry.json` and supplementary artifacts (`registry.index.json`, `capabilities.json`, `featured.json`, `registry.report.json`) from the mcp-tool-registry GitHub repository. Artifacts are cached locally under `~/.cache/mcp/` (platform-appropriate via `platformdirs`).
2. **Workspace management** -- `mcp.yaml` declares which tools belong to a project, their pinned refs, and their granted capabilities. `mcp.lock.yaml` records installed versions and timestamps. `mcp.state.json` tracks run statistics.
3. **Tool install** -- `mcpt install` runs `pip install git+<url>@<ref>` into the current environment or a specified virtualenv, then writes a lock record.
4. **Tool run** -- `mcpt run` defaults to stub mode (prints an execution plan without side effects). Promoting to `--mode restricted` or `--mode real` requires all declared capabilities to be granted first.

---

## Workspace Model

A workspace is a directory containing an `mcp.yaml` file. This file declares everything mcpt needs to know about the tools used in that project.

### Schema

```yaml
schema_version: "0.1"
name: "my-mcp-workspace"

registry:
  source: "https://github.com/mcp-tool-shop-org/mcp-tool-registry"
  ref: "v0.3.0"

tools:
  # Simple form: just the tool ID (uses registry defaults)
  - file-compass

  # Extended form: pin a ref and grant capabilities
  - id: tool-compass
    ref: v1.0.0
    grants:
      - network
      - filesystem_read

run:
  safe_by_default: true

ui:
  sigil: unicode   # unicode | ascii | off
  badges: on       # on | off
```

### Key sections

**registry** -- Where to fetch the tool catalog from, and which version to use. The `ref` field pins the registry to a specific Git tag or commit, ensuring deterministic tool discovery.

**tools** -- A list of tools in this workspace. Each entry can be a plain string (tool ID) or an object with `id`, `ref` (pinned Git ref), and `grants` (list of capabilities this tool is allowed to use).

**run** -- Execution defaults. When `safe_by_default` is `true` (the default), `mcpt run` uses stub mode unless you explicitly opt in to real execution.

**ui** -- Visual preferences. The `sigil` field controls whether tool identity glyphs use Unicode characters, ASCII fallbacks, or are disabled entirely. The `badges` field toggles capability risk badges in list/search output.

### Lock file

`mcp.lock.yaml` is generated by `mcpt install` and records the exact source, ref, and install timestamp for each tool:

```yaml
tools:
  file-compass:
    source: "git+https://github.com/mcp-tool-shop-org/file-compass"
    ref: v1.2.0
    installed_at: "2026-02-15T10:30:00+00:00"
    install_type: git
```

### State file

`mcp.state.json` tracks runtime statistics per tool (successful runs, failed runs, last run timestamp). It is managed automatically and does not need manual editing.

---

## Registry Integration

### How fetching works

mcpt constructs a raw GitHub URL from the `registry.source` and `registry.ref` values in `mcp.yaml` (or from built-in defaults). On first use or when `--refresh` is passed, it fetches `registry.json` and caches it locally.

In addition to the main registry file, mcpt fetches supplementary artifacts on a best-effort basis:

| Artifact | Purpose |
|----------|---------|
| `registry.index.json` | Bundle membership, indexed lookups |
| `capabilities.json` | Capability definitions and risk metadata |
| `featured.json` | Curated collections and featured tool lists |
| `registry.report.json` | Aggregate statistics and facets |
| `registry.llms.txt` | LLM-friendly tool descriptions |

### Cache location

Artifacts are cached under the platform-appropriate user cache directory:

- **Linux/macOS**: `~/.cache/mcp/registry/<ref>/`
- **Windows**: `C:\Users\<user>\AppData\Local\mcp\mcp-tool-shop\Cache\registry\<ref>\`

### Graceful degradation

If a network fetch fails and a cached copy exists, mcpt silently falls back to the cached data. If no cache exists and the network is unavailable, mcpt raises a clear error with remediation steps.

### Pinning explained

There are two independent levels of pinning:

1. **Registry ref** (`registry.ref` in `mcp.yaml`) -- Controls which snapshot of the tool catalog you see. Pinning to a tagged release (e.g., `v0.3.0`) means tool discovery is deterministic across environments.

2. **Tool ref** (`ref` per tool entry, or `mcpt add <id> --ref <tag>`) -- Controls which version of the tool's source code gets installed. Pinning a tool ref means `mcpt install` always checks out the same commit.

Both levels should be pinned for fully reproducible workflows. Use `mcpt init --registry-ref <tag>` to set the registry ref at workspace creation time.

---

## Tool Lifecycle

The lifecycle of a tool in mcpt follows five stages:

### 1. Discovery

```bash
mcpt list --refresh        # Browse the full catalog
mcpt search filesystem     # Search by keyword (ranked)
mcpt info file-compass     # Deep-dive into a single tool
mcpt featured              # Browse curated collections
```

The `search` command scores results by ID match, name match, tag match, and description substring, then sorts by relevance. Use `--explain` to see match scores and reasons.

### 2. Add

```bash
mcpt add file-compass               # Add with default ref
mcpt add tool-compass --ref v1.0.0  # Add with a pinned ref
```

Adding a tool writes it into `mcp.yaml`. If the tool requires capabilities, mcpt prints a warning and tells you how to grant them later. If the tool is deprecated, mcpt prompts for confirmation.

### 3. Install

```bash
mcpt install file-compass             # Install into current env
mcpt install file-compass --ref main  # Override ref
mcpt install file-compass --venv ./venv  # Install into a virtualenv
```

Installation runs `pip install git+<url>@<ref>` and writes a lock record to `mcp.lock.yaml`.

### 4. Grant capabilities

```bash
mcpt grant file-compass network          # Allow network access
mcpt grant file-compass filesystem_read  # Allow filesystem reads
mcpt revoke file-compass network         # Revoke a grant
```

Grants are stored in `mcp.yaml` under each tool entry. A tool cannot execute in restricted/real mode until all of its declared capabilities are granted.

### 5. Run

```bash
mcpt run file-compass                # Stub mode (prints plan, no side effects)
mcpt run file-compass --mode restricted  # Real execution with sandboxing
mcpt run file-compass --dry-run      # Print plan without executing (any mode)
mcpt run file-compass -- --help      # Pass arguments through to the tool
```

Stub mode is the default. It generates and displays an execution plan without performing any operations. Promoting to `restricted` or `real` mode requires:

- All declared capabilities must be granted in `mcp.yaml`
- The tool must have a lock record (i.e., be installed)

Use `mcpt check <tool-id>` to verify all pre-flight conditions before running.

---

## Trust & Safety Model

mcpt surfaces tool trustworthiness and risk at every interaction point. This is not security theater -- it is a layered system designed to prevent accidental execution of dangerous operations.

### Trust tiers

Every tool is assigned a trust tier based on a precedence chain:

| Tier | Criteria | Visual |
|------|----------|--------|
| **Trusted** | Core bundle, stable maturity, or production-grade | Gold, shield icon |
| **Verified** | Ops bundle or validated partner tool | Green, checkmark |
| **Neutral** | Standard community tool (default) | White, dot |
| **Experimental** | Alpha maturity, evaluation bundle, or dev-stage | Purple/dim, flask icon |
| **Deprecated** | Explicitly deprecated in registry | Red/dim, strikethrough |

The precedence is: deprecated > maturity field > bundle membership > default (neutral).

### Risk scoring

Each capability declared by a tool carries a risk level:

| Level | Weight | Examples |
|-------|--------|----------|
| None | 0 | (no capabilities) |
| Low | 1 | clipboard, model_context, sampling |
| Medium | 2 | filesystem_read, http, env, screenshot |
| High | 4 | network, filesystem_write, filesystem, browser |
| Critical | 8 | exec, subprocess, shell |

The aggregate risk score for a tool is the sum of the weighted risk levels of all its capabilities. This score maps to a risk tier:

| Score range | Tier |
|------------|------|
| 0 | Low |
| 1-4 | Medium |
| 5-9 | High |
| 10+ | Extreme |

### Capability badges

In list and search output, each tool can display compact badges like `NET`, `EXEC!`, `READ`, or `WRITE`. These are color-coded by risk level:

- Blue: Low risk
- Yellow: Medium risk
- Red: High risk
- Red reverse: Critical risk (requires explicit grant)

### Safe-by-default execution

The `run.safe_by_default: true` setting (on by default) ensures that `mcpt run` always starts in stub mode. Stub mode prints the execution plan without performing any operations. To execute for real, you must:

1. Grant all required capabilities via `mcpt grant`
2. Explicitly pass `--mode restricted` or `--mode real`

This two-gate model prevents accidental execution of tools with dangerous capabilities.

---

## Visual Language

mcpt uses a consistent visual language across all output to convey trust, risk, and tool identity at a glance. Run `mcpt icons` to see the full cheat sheet.

### Sigils

Every tool gets a deterministic sigil -- a (glyph, color) pair derived from a SHA-256 hash of the tool ID. Sigils provide instant visual recognition of tools across different contexts (list, search, info).

Sigil rendering modes (configured via `ui.sigil` in `mcp.yaml`):

- `unicode` (default): Uses Unicode geometric shapes
- `ascii`: ASCII-safe fallback characters
- `off`: No sigils displayed

### Risk markers (aura)

Risk level is conveyed through visual markers next to tool names:

| Marker | Meaning |
|--------|---------|
| (none) | Low risk -- benign operations |
| `*` | Medium risk -- read-only system access |
| `^` | High risk -- file editing, uncontrolled network |
| `!!` | Extreme risk -- code execution, shell access |

### Accessibility

mcpt respects the `NO_COLOR` environment variable and the `--plain` flag for accessible, pipe-friendly output. When stdout is not a TTY, mcpt automatically falls back to plain mode unless `--force-rich` is passed.

---

## Bundle System

Bundles are rule-generated groupings of tools maintained by the registry. They are not curated manually -- membership is determined by objective criteria (tags, capabilities, maturity).

### Available bundles

| Bundle | Description |
|--------|-------------|
| `core` | Foundational tools with the highest trust level |
| `ops` | Operational and infrastructure tools |
| `agents` | Agent-oriented tools and frameworks |
| `evaluation` | Testing, benchmarking, and evaluation tools |

### Using bundles

```bash
mcpt bundles                    # List all bundles with tool counts
mcpt list --bundle core         # Filter the tool list by bundle
mcpt search agents --bundle ops # Combine search with bundle filter
```

Bundles also feed into the trust tier system: tools in the `core` bundle automatically receive the "trusted" tier, `ops` tools get "verified", and `evaluation` tools get "experimental".

---

## Command Reference

This section provides deeper flag-level detail than the README summary.

### mcpt list

```
mcpt list [OPTIONS]
```

| Flag | Description |
|------|-------------|
| `--json` | Output as JSON array |
| `--refresh` | Force-fetch from remote registry |
| `--bundle <name>` | Filter by bundle (core, ops, agents, evaluation) |
| `--tag <name>` | Filter by tag |
| `--collection <slug>` | Filter by curated collection |
| `--featured` | Show featured tools only |
| `--include-deprecated` | Include deprecated tools in output |
| `--plain` | Disable color and glyphs |
| `--no-badges` | Hide capability risk badges |
| `--force-rich` | Force rich output even when piped |

### mcpt search

```
mcpt search <query> [OPTIONS]
```

| Flag | Description |
|------|-------------|
| `--bundle <name>` | Filter results by bundle |
| `--tag <name>` | Filter results by tag |
| `--collection <slug>` | Filter results by collection |
| `--featured` | Search within featured tools only |
| `--explain` | Show match reasons and relevance scores |
| `--json` | Output as JSON |
| `--plain` | Disable color and glyphs |
| `--no-badges` | Hide capability risk badges |
| `--force-rich` | Force rich output even when piped |

### mcpt info

```
mcpt info <tool-id> [OPTIONS]
```

| Flag | Description |
|------|-------------|
| `--json` | Output as JSON |

Displays: description, bundles, risk score, capabilities with grant status, install command, repository URL, install type, Git URL, default ref, tags, and safe-run flag.

### mcpt init

```
mcpt init [PATH] [OPTIONS]
```

| Flag | Description |
|------|-------------|
| `--force`, `-f` | Overwrite existing `mcp.yaml` |
| `--registry-ref <ref>` | Set the registry Git ref (default: `v0.3.0`) |

### mcpt add

```
mcpt add <tool-id> [OPTIONS]
```

| Flag | Description |
|------|-------------|
| `--ref <ref>` | Pin the tool to a specific Git ref |
| `--path`, `-p` | Path to `mcp.yaml` (default: current directory) |
| `--allow-deprecated` | Skip the deprecation confirmation prompt |

Validates that the tool exists in the registry. Shows fuzzy-match suggestions if the ID is not found. Warns about required capabilities.

### mcpt remove

```
mcpt remove <tool-id> [OPTIONS]
```

| Flag | Description |
|------|-------------|
| `--path`, `-p` | Path to `mcp.yaml` |

### mcpt install

```
mcpt install <tool-id> [OPTIONS]
```

| Flag | Description |
|------|-------------|
| `--ref <ref>` | Override the Git ref for this install |
| `--venv <path>` | Install into a specific virtualenv |
| `--allow-deprecated` | Skip the deprecation confirmation prompt |

### mcpt run

```
mcpt run <tool-id> [ARGS...] [OPTIONS]
```

| Flag | Description |
|------|-------------|
| `--mode <mode>` | Execution mode: `stub` (default), `restricted`, `real` |
| `--real` | (Deprecated) Alias for `--mode restricted` |
| `--dry-run` | Print execution plan without running |

Arguments after `--` are passed through to the tool.

### mcpt grant / revoke

```
mcpt grant <tool-id> <capability>
mcpt revoke <tool-id> <capability>
```

| Flag | Description |
|------|-------------|
| `--path`, `-p` | Path to `mcp.yaml` |

### mcpt check

```
mcpt check <tool-id> [OPTIONS]
```

| Flag | Description |
|------|-------------|
| `--json` | Output as JSON |

Pre-flight check that verifies: registry metadata, workspace config, tool added, tool installed, risk profile, and capability grants. Exits with code 0 if ready, code 1 if any check fails.

### mcpt doctor

```
mcpt doctor
```

No options. Reports Python version, registry status and provenance, remote connectivity, workspace health, and actionable next steps.

### mcpt icons

```
mcpt icons [OPTIONS]
```

| Flag | Description |
|------|-------------|
| `--plain` | Print in plain text mode |

Displays the full visual-language cheat sheet: trust tiers, risk markers, capability badges, and example tool renderings.

### mcpt bundles

```
mcpt bundles [OPTIONS]
```

| Flag | Description |
|------|-------------|
| `--json` | Output as JSON |

### mcpt featured

```
mcpt featured [OPTIONS]
```

| Flag | Description |
|------|-------------|
| `--collection`, `-c` | Show a specific collection |
| `--list`, `--list-collections` | List available collections |
| `--json` | Output as JSON |
| `--plain` | Disable color and glyphs |
| `--refresh` | Force-refresh the registry |
| `--force-rich` | Force rich output even when piped |

### mcpt facets

```
mcpt facets [OPTIONS]
```

| Flag | Description |
|------|-------------|
| `--json` | Output as JSON |

### mcpt registry

```
mcpt registry [OPTIONS]
```

| Flag | Description |
|------|-------------|
| `--json` | Output as JSON |

Shows: source URL, ref, tool count, last fetch time, and artifact availability.

---

## CI & Automation

mcpt is designed to work in CI pipelines. Key patterns:

### Machine-readable output

Every listing and search command accepts `--json` for structured output that can be piped into `jq`, Python scripts, or other tools:

```bash
mcpt list --json | jq '.[].id'
mcpt search agents --json | jq '.[] | select(._score > 50)'
mcpt info file-compass --json | jq '.capabilities'
mcpt check file-compass --json
```

### Plain mode in CI

mcpt auto-detects non-TTY environments and disables color. You can also force plain mode:

```bash
mcpt list --plain
# or
export NO_COLOR=1
mcpt list
```

### Reproducible workspace setup

Pin both registry and tool refs in `mcp.yaml`, then use the standard install flow:

```bash
# In CI
pip install mcp-select
mcpt list --refresh           # Populate cache
mcpt install file-compass     # Installs the pinned ref
mcpt check file-compass --json  # Verify pre-flight
```

### Pre-flight in CI

Use `mcpt check <tool-id> --json` in CI to verify that a tool is properly configured before attempting execution. The exit code is 0 for ready, 1 for any failure.

```yaml
# Example GitHub Actions step
- name: Verify tool readiness
  run: mcpt check file-compass --json
```

---

## The npm Wrapper

The `@mcptoolshop/mcpt` npm package is a thin wrapper that makes mcpt accessible to Node.js workflows.

### How it works

1. `npm install @mcptoolshop/mcpt` triggers a postinstall script
2. The postinstall script runs `pip install mcp-select` to install the Python package
3. A bin shim (`mcpt`) forwards all CLI invocations to the Python `mcpt` command

### Requirements

- Node.js 18+
- Python 3.10+
- pip (bundled with standard Python installations)

### When to use pip vs npm

Use `pip install mcp-select` when:
- You are working in a Python-first environment
- You want direct control over the Python installation
- You are already managing a virtualenv

Use `npm install @mcptoolshop/mcpt` (or `npx`) when:
- You want mcpt declared in `package.json` alongside other Node dependencies
- You are in a Node-first environment and do not want to manage pip manually
- You need a quick one-shot run via `npx @mcptoolshop/mcpt <command>`

---

## Troubleshooting & FAQ

### "Tool not found" errors

**Cause**: The local registry cache may be stale or missing.

**Fix**: Run `mcpt list --refresh` to fetch the latest registry data. If the tool was recently added to the registry, the cache may not include it yet.

### "Execution Blocked" when running a tool

**Cause**: The tool requires capabilities that have not been granted.

**Fix**: Run `mcpt check <tool-id>` to see which capabilities are missing, then grant them with `mcpt grant <tool-id> <capability>`.

### "No mcp.yaml found"

**Cause**: You are running a workspace command outside of an initialized workspace.

**Fix**: Run `mcpt init` to create `mcp.yaml` in the current directory.

### Registry fetch fails (network error)

**Cause**: Network connectivity issues or the GitHub raw content URL is unreachable.

**Fix**: If you have a cached registry, mcpt will fall back to it automatically. Run `mcpt doctor` to check connectivity and cache status.

### "Unsupported install type"

**Cause**: The tool uses an install method other than `git` (which is currently the only supported type).

**Fix**: Check `mcpt info <tool-id>` to see the install type. If it is not `git`, the tool may require manual installation.

### Why is the PyPI package called `mcp-select`?

The `mcp` name on PyPI is taken by Anthropic's official Model Context Protocol SDK package. To avoid conflicts, mcpt publishes under the name `mcp-select`. The CLI command remains `mcpt` regardless of how you install it.

### How do I update mcpt?

```bash
# Python
pip install --upgrade mcp-select

# npm
npm update @mcptoolshop/mcpt
```

### Can I use mcpt without a workspace?

Yes. Commands like `mcpt list`, `mcpt search`, `mcpt info`, `mcpt doctor`, and `mcpt icons` work without a workspace. Workspace-dependent commands (`add`, `remove`, `install`, `run`, `grant`, `revoke`, `check`) require `mcp.yaml`.

### How do I contribute a tool to the registry?

Visit the [Submit a Tool](https://github.com/mcp-tool-shop-org/mcp-tool-registry/issues/new/choose) page on the mcp-tool-registry repository.

---

*This handbook covers mcpt v1.1.0. For the latest changes, see [CHANGELOG.md](CHANGELOG.md).*
