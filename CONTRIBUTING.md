# Contributing to MCPT

MCPT is the command-line interface for discovering and running MCP Tool Shop tools. Contributions are welcome!

## Development Setup

```bash
git clone https://github.com/mcp-tool-shop-org/mcpt.git
cd mcpt
pip install -e ".[dev]"
pytest
```

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Check existing [issues](https://github.com/mcp-tool-shop-org/mcpt/issues)
2. If not found, create a new issue with:
   - Clear description of the problem or feature
   - Steps to reproduce (for bugs)
   - Expected vs. actual behavior
   - Your environment (Python version, OS)

### Contributing Code

1. **Fork the repository** and create a branch from `main`
2. **Make your changes**
   - Follow existing code style
   - Use type hints with Typer conventions
   - Add tests for new functionality
3. **Test your changes**
   ```bash
   pytest
   ```
4. **Commit your changes**
   - Use clear, descriptive commit messages
   - Reference issue numbers when applicable
5. **Submit a pull request**
   - Describe what your PR does and why
   - Link to related issues

## Project Structure

```
mcpt/
├── mcpt/
│   ├── cli.py          # Main CLI app with Typer commands
│   ├── config.py       # mcp.yaml parsing and validation
│   ├── registry.py     # Registry fetching and caching
│   ├── commands/       # Command implementations
│   └── utils.py        # Shared utilities
├── tests/              # Test suite
└── pyproject.toml      # Project metadata
```

## Adding New Commands

Use Typer's command pattern:

```python
@app.command()
def my_command(
    arg: str = typer.Argument(..., help="Description"),
    option: bool = typer.Option(False, "--flag", help="Enable something")
):
    """Command description shown in help."""
    # Implementation
```

## Testing

- Write tests for new functionality
- Use fixtures for common test data
- Test both success and error paths
- Run tests before submitting PR: `pytest`

## Registry Integration

When adding features that interact with the registry:

- Cache registry data in platformdirs-appropriate locations
- Handle network failures gracefully
- Validate schema versions
- Support both tagged and development registry refs

## Configuration (`mcp.yaml`)

When modifying config handling:

- Maintain backward compatibility with schema version
- Validate all config fields
- Provide clear error messages for invalid configs
- Support both minimal and full config formats

## CLI Design Principles

- **Safe by default**: Operations that modify state require explicit flags
- **Clear feedback**: Use Rich for formatted output
- **Composable**: Commands should work well in scripts
- **JSON output**: Support `--json` for machine-readable output
- **Help text**: Every command and option needs clear help text

## Documentation

When adding features:

- Update README.md with usage examples
- Add inline help text to commands
- Update this CONTRIBUTING.md if changing dev workflow

## Release Process

(For maintainers)

1. Update version in `pyproject.toml`
2. Create git tag: `git tag v0.x.x`
3. Push tag: `git push origin v0.x.x`
4. GitHub Actions will publish to PyPI

## Code Style

- Use type hints
- Follow PEP 8
- Use Rich for terminal output
- Use Typer for CLI structure
- Keep functions small and focused
- Add docstrings for complex logic

## Questions?

Open an issue or start a discussion in the [MCP Tool Shop](https://github.com/mcp-tool-shop) organization.
