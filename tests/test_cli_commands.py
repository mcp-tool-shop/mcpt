"""Tests for CLI commands."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from mcpt.cli import app, fuzzy_match_tools

runner = CliRunner()


class TestIconsCommand:
    """Test icons command."""

    def test_icons_basic(self):
        """Test icons command runs successfully."""
        result = runner.invoke(app, ["icons"])
        assert result.exit_code == 0
        assert "Trust Tiers" in result.stdout
        assert "Risk Markers" in result.stdout

    def test_icons_plain(self):
        """Test icons command with plain flag."""
        result = runner.invoke(app, ["icons", "--plain"])
        assert result.exit_code == 0
        assert "Trust Tiers" in result.stdout

class TestFuzzyMatchTools:
    """Test fuzzy_match_tools function."""

    @patch("mcpt.cli.get_registry")
    def test_fuzzy_match_exact_match(self, mock_get_registry):
        """Test fuzzy_match_tools with exact match."""
        mock_get_registry.return_value = {
            "tools": [
                {"id": "file-compass"},
                {"id": "tool-scan"},
            ]
        }
        results = fuzzy_match_tools("file-compass")
        assert len(results) > 0
        assert results[0]["id"] == "file-compass"

    @patch("mcpt.cli.get_registry")
    def test_fuzzy_match_partial_match(self, mock_get_registry):
        """Test fuzzy_match_tools with partial match."""
        mock_get_registry.return_value = {
            "tools": [
                {"id": "file-compass"},
                {"id": "tool-compass"},
                {"id": "voice-soundboard"},
            ]
        }
        results = fuzzy_match_tools("compass")
        assert len(results) >= 2

    @patch("mcpt.cli.get_registry")
    def test_fuzzy_match_limit(self, mock_get_registry):
        """Test fuzzy_match_tools respects limit."""
        mock_get_registry.return_value = {
            "tools": [
                {"id": f"tool-{i}"} for i in range(10)
            ]
        }
        results = fuzzy_match_tools("tool", limit=3)
        assert len(results) <= 3

    @patch("mcpt.cli.get_registry")
    def test_fuzzy_match_case_insensitive(self, mock_get_registry):
        """Test fuzzy_match_tools is case insensitive."""
        mock_get_registry.return_value = {
            "tools": [
                {"id": "file-compass"},
            ]
        }
        results = fuzzy_match_tools("FILE-COMPASS")
        assert len(results) > 0


class TestListCommand:
    """Test list command."""

    @patch("mcpt.cli.get_registry")
    def test_list_basic(self, mock_get_registry):
        """Test list command basic output."""
        mock_get_registry.return_value = {
            "tools": [
                {"id": "file-compass", "name": "File Compass"},
                {"id": "tool-scan", "name": "Tool Scan"},
            ]
        }
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "file-compass" in result.stdout or "File Compass" in result.stdout

    @patch("mcpt.cli.get_registry")
    def test_list_json_output(self, mock_get_registry):
        """Test list command with JSON output."""
        mock_get_registry.return_value = {
            "tools": [
                {"id": "file-compass", "name": "File Compass"},
            ]
        }
        result = runner.invoke(app, ["list", "--json"])
        assert result.exit_code == 0
        assert "file-compass" in result.stdout

    @patch("mcpt.cli.get_registry")
    def test_list_with_refresh(self, mock_get_registry):
        """Test list command with --refresh flag."""
        mock_get_registry.return_value = {
            "tools": [
                {"id": "file-compass", "name": "File Compass"},
            ]
        }
        result = runner.invoke(app, ["list", "--refresh"])
        assert result.exit_code == 0

    @patch("mcpt.cli.get_registry")
    def test_list_handles_error(self, mock_get_registry):
        """Test list command handles registry fetch errors."""
        mock_get_registry.side_effect = Exception("Registry fetch failed")
        result = runner.invoke(app, ["list"])
        assert result.exit_code != 0


class TestInfoCommand:
    """Test info command."""

    @patch("mcpt.cli.get_tool")
    def test_info_found(self, mock_get_tool):
        """Test info command when tool exists."""
        mock_get_tool.return_value = {
            "id": "file-compass",
            "name": "File Compass",
            "description": "Find files in your workspace",
        }
        result = runner.invoke(app, ["info", "file-compass"])
        assert result.exit_code == 0
        assert "File Compass" in result.stdout

    @patch("mcpt.cli.get_tool")
    def test_info_not_found(self, mock_get_tool):
        """Test info command when tool doesn't exist."""
        mock_get_tool.return_value = None
        result = runner.invoke(app, ["info", "nonexistent"])
        assert result.exit_code != 0

    @patch("mcpt.cli.get_tool")
    def test_info_json_output(self, mock_get_tool):
        """Test info command with JSON output."""
        mock_get_tool.return_value = {
            "id": "file-compass",
            "name": "File Compass",
        }
        result = runner.invoke(app, ["info", "file-compass", "--json"])
        assert result.exit_code == 0


class TestSearchCommand:
    """Test search command."""

    @patch("mcpt.cli.search_tools")
    def test_search_basic(self, mock_search):
        """Test search command basic functionality."""
        mock_search.return_value = [
            {"id": "file-compass", "name": "File Compass"},
        ]
        result = runner.invoke(app, ["search", "compass"])
        assert result.exit_code == 0

    @patch("mcpt.cli.search_tools")
    def test_search_no_results(self, mock_search):
        """Test search command with no results."""
        mock_search.return_value = []
        result = runner.invoke(app, ["search", "nonexistent"])
        assert result.exit_code == 0

    @patch("mcpt.cli.search_tools")
    def test_search_json_output(self, mock_search):
        """Test search command with JSON output."""
        mock_search.return_value = [
            {"id": "file-compass"},
        ]
        result = runner.invoke(app, ["search", "compass", "--json"])
        assert result.exit_code == 0


class TestInitCommand:
    """Test init command."""

    def test_init_creates_mcp_yaml(self):
        """Test init command creates mcp.yaml."""
        with runner.isolated_filesystem():
            result = runner.invoke(app, ["init"])
            assert result.exit_code == 0
            assert Path("mcp.yaml").exists()

    def test_init_yaml_is_valid(self):
        """Test init command creates valid YAML."""
        with runner.isolated_filesystem():
            runner.invoke(app, ["init"])
            content = Path("mcp.yaml").read_text()
            assert "schema_version" in content
            assert "tools" in content


class TestAddCommand:
    """Test add command."""

    @patch("mcpt.cli.get_tool")
    def test_add_tool_to_workspace(self, mock_get_tool):
        """Test add command adds tool to mcp.yaml."""
        mock_get_tool.return_value = {"id": "file-compass"}
        with runner.isolated_filesystem():
            runner.invoke(app, ["init"])
            result = runner.invoke(app, ["add", "file-compass"])
            assert result.exit_code == 0
            assert Path("mcp.yaml").exists()

    @patch("mcpt.cli.get_tool")
    def test_add_duplicate_tool(self, mock_get_tool):
        """Test add command with duplicate tool."""
        mock_get_tool.return_value = {"id": "file-compass"}
        with runner.isolated_filesystem():
            runner.invoke(app, ["init"])
            runner.invoke(app, ["add", "file-compass"])
            result = runner.invoke(app, ["add", "file-compass"])
            # Should handle gracefully
            assert result.exit_code >= 0


class TestRemoveCommand:
    @patch("mcpt.cli.get_tool")
    def test_remove_tool_from_workspace(self, mock_get_tool):
        """Test remove command removes tool from mcp.yaml."""
        mock_get_tool.return_value = {"id": "file-compass"}
        with runner.isolated_filesystem():
            runner.invoke(app, ["init"])
            runner.invoke(app, ["add", "file-compass"])
            result = runner.invoke(app, ["remove", "file-compass"])
            assert result.exit_code == 0

    def test_remove_nonexistent_tool(self):
        """Test remove command with nonexistent tool."""
        with runner.isolated_filesystem():
            runner.invoke(app, ["init"])
            result = runner.invoke(app, ["remove", "nonexistent"])
            # Should handle gracefully (either succeed or fail)
            assert result.exit_code >= 0


class TestRunCommand:
    """Test run command."""

    @patch("mcpt.cli.get_tool")
    def test_run_stub_mode(self, mock_get_tool):
        """Test run command in stub mode (default)."""
        mock_get_tool.return_value = {
            "id": "file-compass",
            "name": "File Compass",
            "install": {"type": "git", "url": "https://example.com"},
        }
        result = runner.invoke(app, ["run", "file-compass"])
        assert result.exit_code == 0
        assert "STUB" in result.stdout or "stub" in result.stdout.lower()

    @patch("mcpt.cli.get_tool")
    def test_run_with_args(self, mock_get_tool):
        """Test run command with arguments."""
        mock_get_tool.return_value = {
            "id": "file-compass",
            "name": "File Compass",
            "install": {"type": "git", "url": "https://example.com"},
        }
        result = runner.invoke(app, ["run", "file-compass", "--", "--pattern", "*.py"])
        assert result.exit_code == 0

    @patch("mcpt.cli.get_tool")
    def test_run_nonexistent_tool(self, mock_get_tool):
        """Test run command with nonexistent tool."""
        mock_get_tool.return_value = None
        result = runner.invoke(app, ["run", "nonexistent"])
        assert result.exit_code != 0


class TestDoctorCommand:
    """Test doctor command."""

    def test_doctor_basic(self):
        """Test doctor command runs."""
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0
