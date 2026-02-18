<p align="center"><img src="logo.jpg" alt="mcpt logo" width="200"></p>

# @mcptoolshop/mcpt

> Part of [MCP Tool Shop](https://mcptoolshop.com)

**npm wrapper for mcpt -- CLI for discovering, installing, and running MCP Tool Shop tools.**

[![npm version](https://img.shields.io/npm/v/@mcptoolshop/mcpt)](https://www.npmjs.com/package/@mcptoolshop/mcpt)
[![PyPI version](https://img.shields.io/pypi/v/mcp-select)](https://pypi.org/project/mcp-select/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/mcp-tool-shop-org/mcpt/blob/main/LICENSE)

---

## What is this?

This is an **npm convenience wrapper** around [mcpt](https://github.com/mcp-tool-shop-org/mcpt), the official CLI for the MCP Tool Shop ecosystem. It lets you use mcpt from any Node.js project without manually installing Python dependencies.

On `npm install`, a postinstall hook automatically installs the `mcp-select` Python package (which provides the `mcpt` command). After installation, you can use `mcpt` directly or via `npx`.

## Quick Start

```bash
# One-shot (no install required)
npx @mcptoolshop/mcpt list

# Browse and search
npx @mcptoolshop/mcpt search filesystem
npx @mcptoolshop/mcpt info file-compass

# Initialize a workspace
npx @mcptoolshop/mcpt init
npx @mcptoolshop/mcpt add file-compass
npx @mcptoolshop/mcpt install file-compass

# Global install
npm install -g @mcptoolshop/mcpt
mcpt list --refresh
mcpt doctor
```

## How it works

1. `npm install` triggers the postinstall script
2. The postinstall script runs `pip install mcp-select` to install the Python CLI
3. The `mcpt` binary shim forwards all arguments to the Python `mcpt` command

No manual Python setup is needed -- as long as Python 3.10+ is on your PATH, everything works automatically.

## When to use pip vs npm

| Scenario | Recommendation |
|----------|---------------|
| Python-first workflow | `pip install mcp-select` |
| Node.js project, want mcpt in `package.json` | `npm install @mcptoolshop/mcpt` |
| Quick one-off usage | `npx @mcptoolshop/mcpt <command>` |
| CI pipeline (Python available) | `pip install mcp-select` |
| CI pipeline (Node available, no Python setup) | `npx @mcptoolshop/mcpt` |

## Requirements

- **Node.js** 18+
- **Python** 3.10+
- **pip** (bundled with Python)

## Full Documentation

For the complete command reference, workspace model, trust & safety system, and CI patterns, see the main repository:

**[github.com/mcp-tool-shop-org/mcpt](https://github.com/mcp-tool-shop-org/mcpt)**

## License

[MIT](https://github.com/mcp-tool-shop-org/mcpt/blob/main/LICENSE)
