"""Tests for runner functionality."""

from unittest.mock import patch, MagicMock

import pytest
from rich.console import Console

from mcpt.runner import generate_run_plan, stub_run


class TestGenerateRunPlan:
    """Test generate_run_plan function."""

    def test_generate_run_plan_basic(self):
        """Test generate_run_plan with basic tool."""
        tool = {
            "id": "file-compass",
            "name": "File Compass",
            "install": {"type": "git", "url": "https://github.com/mcp-tool-shop-org/file-compass.git"},
        }
        plan = generate_run_plan(tool)
        
        assert plan["tool_id"] == "file-compass"
        assert plan["tool_name"] == "File Compass"
        assert plan["install"]["type"] == "git"
        assert plan["action"] == "run"

    def test_generate_run_plan_with_args(self):
        """Test generate_run_plan with arguments."""
        tool = {
            "id": "file-compass",
            "name": "File Compass",
            "install": {"type": "git", "url": "https://github.com/mcp-tool-shop-org/file-compass.git"},
        }
        args = ["--pattern", "*.py", "--limit", "10"]
        plan = generate_run_plan(tool, args)
        
        assert plan["args"] == args

    def test_generate_run_plan_with_default_ref(self):
        """Test generate_run_plan includes default_ref."""
        tool = {
            "id": "file-compass",
            "name": "File Compass",
            "install": {
                "type": "git",
                "url": "https://github.com/mcp-tool-shop-org/file-compass.git",
                "default_ref": "v1.0.0",
            },
        }
        plan = generate_run_plan(tool)
        
        assert plan["install"]["ref"] == "v1.0.0"

    def test_generate_run_plan_safe_run_default(self):
        """Test generate_run_plan defaults safe_run to True."""
        tool = {
            "id": "file-compass",
            "name": "File Compass",
            "install": {"type": "git", "url": "https://github.com/mcp-tool-shop-org/file-compass.git"},
        }
        plan = generate_run_plan(tool)
        
        assert plan["safe_run"] is True

    def test_generate_run_plan_safe_run_from_defaults(self):
        """Test generate_run_plan reads safe_run from tool defaults."""
        tool = {
            "id": "file-compass",
            "name": "File Compass",
            "install": {"type": "git", "url": "https://github.com/mcp-tool-shop-org/file-compass.git"},
            "defaults": {"safe_run": False},
        }
        plan = generate_run_plan(tool)
        
        assert plan["safe_run"] is False

    def test_generate_run_plan_no_args(self):
        """Test generate_run_plan with no arguments."""
        tool = {
            "id": "file-compass",
            "name": "File Compass",
            "install": {"type": "git", "url": "https://github.com/mcp-tool-shop-org/file-compass.git"},
        }
        plan = generate_run_plan(tool)
        
        assert plan["args"] == []

    def test_generate_run_plan_missing_install(self):
        """Test generate_run_plan handles missing install info."""
        tool = {
            "id": "file-compass",
            "name": "File Compass",
        }
        plan = generate_run_plan(tool)
        
        assert plan["tool_id"] == "file-compass"
        assert plan["install"]["type"] is None


class TestStubRun:
    """Test stub_run function."""

    @patch("mcpt.runner.stub.console.print")
    def test_stub_run_prints_output(self, mock_print):
        """Test stub_run prints execution plan."""
        plan = {
            "tool_id": "file-compass",
            "tool_name": "File Compass",
            "install": {"type": "git", "url": "https://github.com/mcp-tool-shop-org/file-compass.git", "ref": "main"},
            "args": [],
            "safe_run": True,
        }
        
        stub_run("file-compass", plan)
        
        # Check that print was called
        assert mock_print.call_count > 0

    @patch("mcpt.runner.stub.console.print")
    def test_stub_run_mentions_stub_mode(self, mock_print):
        """Test stub_run mentions it's in stub mode."""
        plan = {
            "tool_id": "file-compass",
            "tool_name": "File Compass",
            "install": {"type": "git", "url": "https://example.com", "ref": "main"},
            "args": [],
            "safe_run": True,
        }
        
        stub_run("file-compass", plan)
        
        # Verify stub mode is mentioned (in Panel or table output)
        calls = [str(call) for call in mock_print.call_args_list]
        all_output = " ".join(calls)
        assert "STUB" in all_output or "stub" in all_output

    @patch("mcpt.runner.stub.console.print")
    def test_stub_run_with_args(self, mock_print):
        """Test stub_run displays arguments."""
        plan = {
            "tool_id": "file-compass",
            "tool_name": "File Compass",
            "install": {"type": "git", "url": "https://example.com", "ref": "main"},
            "args": ["--pattern", "*.py"],
            "safe_run": True,
        }
        
        stub_run("file-compass", plan)
        
        assert mock_print.call_count > 0

    @patch("mcpt.runner.stub.console.print")
    def test_stub_run_shows_tool_info(self, mock_print):
        """Test stub_run shows tool information."""
        tool_id = "file-compass"
        plan = {
            "tool_id": tool_id,
            "tool_name": "File Compass",
            "install": {"type": "git", "url": "https://example.com", "ref": "main"},
            "args": [],
            "safe_run": True,
        }
        
        stub_run(tool_id, plan)
        
        # Should have called print multiple times
        assert mock_print.call_count >= 2

    @patch("mcpt.runner.stub.console.print")
    def test_stub_run_with_different_tool_ids(self, mock_print):
        """Test stub_run works with different tool IDs."""
        tools = ["file-compass", "tool-scan", "voice-soundboard"]
        
        for tool_id in tools:
            mock_print.reset_mock()
            plan = {
                "tool_id": tool_id,
                "tool_name": tool_id.title(),
                "install": {"type": "git", "url": "https://example.com", "ref": "main"},
                "args": [],
                "safe_run": True,
            }
            stub_run(tool_id, plan)
            assert mock_print.call_count > 0
