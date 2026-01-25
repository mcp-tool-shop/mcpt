"""Smoke tests for MCPT CLI."""

from typer.testing import CliRunner

from mcpt.cli import app

runner = CliRunner()


def test_version():
    """Test version command."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "mcpt" in result.stdout
    assert "0.1.0" in result.stdout


def test_help():
    """Test help output."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout
    assert "info" in result.stdout
    assert "search" in result.stdout
    assert "init" in result.stdout
    assert "add" in result.stdout
    assert "remove" in result.stdout
    assert "install" in result.stdout
    assert "run" in result.stdout
    assert "doctor" in result.stdout


def test_list_help():
    """Test list command help."""
    result = runner.invoke(app, ["list", "--help"])
    assert result.exit_code == 0
    assert "--json" in result.stdout
    assert "--refresh" in result.stdout


def test_info_help():
    """Test info command help."""
    result = runner.invoke(app, ["info", "--help"])
    assert result.exit_code == 0
    assert "TOOL_ID" in result.stdout


def test_search_help():
    """Test search command help."""
    result = runner.invoke(app, ["search", "--help"])
    assert result.exit_code == 0
    assert "QUERY" in result.stdout


def test_init_help():
    """Test init command help."""
    result = runner.invoke(app, ["init", "--help"])
    assert result.exit_code == 0
    assert "--force" in result.stdout


def test_run_help():
    """Test run command help."""
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    assert "--real" in result.stdout
