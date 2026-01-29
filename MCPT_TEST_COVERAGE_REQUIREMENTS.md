# MCPT Test Coverage Requirements

**Goal**: Achieve 100% test coverage across all modules

**Current Status**:
- Source modules: 8 files (cli.py, registry/client.py, workspace/config.py, runner/stub.py + __init__ files)
- Test files: 6 files (test_cli_commands.py, test_registry.py, test_workspace.py, test_runner.py, test_comprehensive.py, test_smoke.py)
- **Estimated coverage**: ~60-70% (many edge cases, error paths, and integration scenarios missing)

---

## Module: `mcpt/cli.py` (480 lines)

### Currently Tested
- ✅ Basic list/info/search commands
- ✅ Init command creates mcp.yaml
- ✅ Add/remove tool operations
- ✅ Run command in stub mode
- ✅ Doctor command runs

### Missing Tests (Priority: HIGH)

#### 1. Fuzzy Matching Edge Cases
**Lines**: 33-58 (`fuzzy_match_tools`)

```python
def test_fuzzy_match_empty_registry():
    """Test fuzzy_match_tools with empty registry."""
    # When: registry has no tools
    # Then: should return empty list without error

def test_fuzzy_match_no_matches():
    """Test fuzzy_match_tools when no tools match."""
    # When: query doesn't match any tool
    # Then: should return empty list

def test_fuzzy_match_scoring_accuracy():
    """Test fuzzy_match_tools ranks results correctly."""
    # Given: tools with varying similarity to query
    # Then: results should be sorted by relevance score
```

#### 2. List Command Error Handling
**Lines**: 88-106

```python
def test_list_handles_network_timeout():
    """Test list command when registry fetch times out."""
    # Mock httpx timeout exception
    # Verify graceful error message

def test_list_handles_corrupted_cache():
    """Test list with corrupted cache and network failure."""
    # Mock corrupted cache + network error
    # Verify appropriate error message

def test_list_empty_registry():
    """Test list when registry has no tools."""
    # Verify "No tools found" message displayed
```

#### 3. Info Command Edge Cases
**Lines**: 108-152

```python
def test_info_with_minimal_tool_metadata():
    """Test info when tool has minimal metadata."""
    # Tool with only id and name, no description/tags
    # Verify displays without errors

def test_info_with_long_description():
    """Test info with very long description text."""
    # Verify formatting handles long text gracefully
```

#### 4. Search Command Variations
**Lines**: 154-192

```python
def test_search_by_tag():
    """Test search finds tools by tag."""
    # Search for tag that matches multiple tools

def test_search_by_description():
    """Test search finds tools by description content."""
    # Query appears in description but not name

def test_search_case_insensitive():
    """Test search is case insensitive."""
    # Mixed case queries match tools

def test_search_special_characters():
    """Test search handles special characters."""
    # Query with regex special chars doesn't crash
```

#### 5. Init Command Edge Cases
**Lines**: 199-225

```python
def test_init_in_nested_directory():
    """Test init creates parent directories if needed."""
    # Path with non-existent parents
    # Verify directories created

def test_init_with_custom_registry_ref():
    """Test init with custom --registry-ref."""
    # Verify custom ref appears in mcp.yaml

def test_init_force_overwrites_existing():
    """Test --force flag overwrites existing mcp.yaml."""
    # Existing config gets replaced
```

#### 6. Add Command Error Paths
**Lines**: 227-264

```python
def test_add_without_init():
    """Test add command when mcp.yaml doesn't exist."""
    # Should show helpful error: "Run mcpt init first"

def test_add_with_fuzzy_suggestions():
    """Test add shows suggestions for typo'd tool name."""
    # Typo in tool name triggers fuzzy match suggestions

def test_add_tool_with_custom_ref():
    """Test add tool with --ref flag."""
    # Tool added with specific git ref in config

def test_add_shows_capability_warning():
    """Test add warns about tools with side effects."""
    # Tool with safe_run=false shows warning
```

#### 7. Remove Command Edge Cases
**Lines**: 266-291

```python
def test_remove_without_workspace():
    """Test remove when no mcp.yaml exists."""
    # Verify clear error message

def test_remove_case_sensitivity():
    """Test remove handles case correctly."""
    # Tool added as "File-Compass", removed as "file-compass"
```

#### 8. Install Command Scenarios
**Lines**: 298-344

```python
def test_install_unsupported_type():
    """Test install with non-git install type."""
    # Tool has install.type = "npm"
    # Should error with clear message

def test_install_network_failure():
    """Test install when git clone fails."""
    # Mock subprocess failure
    # Verify error handling

def test_install_with_venv():
    """Test install into specific venv."""
    # Use --venv flag
    # Verify correct pip executable used

def test_install_venv_not_found():
    """Test install when --venv path doesn't exist."""
    # Verify error message about missing venv

def test_install_with_default_ref():
    """Test install uses default_ref when --ref not specified."""
    # Verify git URL includes default_ref

def test_install_pip_failure():
    """Test install when pip install fails."""
    # Mock CalledProcessError
    # Verify stderr displayed to user
```

#### 9. Run Command Expansions
**Lines**: 351-377

```python
def test_run_with_multiple_args():
    """Test run command with multiple arguments."""
    # Pass multiple args to tool
    # Verify all appear in plan

def test_run_real_mode_placeholder():
    """Test run with --real flag (not yet implemented)."""
    # Should show "not yet implemented" message

def test_run_tool_with_safe_run_false():
    """Test run displays appropriate warnings for unsafe tools."""
    # Tool has safe_run=false
    # Should warn about potential side effects
```

#### 10. Doctor Command Completeness
**Lines**: 384-480

```python
def test_doctor_with_stale_cache():
    """Test doctor shows cache age warning."""
    # Cache older than 30 days
    # Should suggest --refresh

def test_doctor_with_workspace():
    """Test doctor detects workspace configuration."""
    # mcp.yaml exists in current directory
    # Shows workspace stats

def test_doctor_no_workspace_guidance():
    """Test doctor suggests creating workspace."""
    # No mcp.yaml present
    # Next steps include "mcpt init"

def test_doctor_with_main_ref_warning():
    """Test doctor warns about unpinned main ref."""
    # Registry ref is "main"
    # Should warn about lack of reproducibility

def test_doctor_network_offline():
    """Test doctor when network is unavailable."""
    # Network check fails
    # Should show cache usage message

def test_doctor_cache_not_found():
    """Test doctor when cache doesn't exist."""
    # No cached registry
    # Should suggest running list --refresh

def test_doctor_workspace_parse_error():
    """Test doctor handles corrupted mcp.yaml."""
    # Invalid YAML in workspace config
    # Should show parse error with helpful message
```

---

## Module: `mcpt/registry/client.py` (200 lines)

### Currently Tested
- ✅ RegistryConfig initialization
- ✅ get_registry returns dict
- ✅ get_tool finds/doesn't find tools
- ✅ search_tools basic functionality
- ✅ Cache loading/saving attempts

### Missing Tests (Priority: CRITICAL)

#### 1. GitHub URL Conversion
**Lines**: 19-23 (`github_raw_registry_url`)

```python
def test_github_raw_registry_url_standard():
    """Test converting GitHub repo URL to raw file URL."""
    # Input: https://github.com/org/repo
    # Output: https://raw.githubusercontent.com/org/repo/{ref}/registry.json

def test_github_raw_registry_url_trailing_slash():
    """Test URL conversion handles trailing slash."""
    # Input: https://github.com/org/repo/
    # Should strip trailing slash

def test_github_raw_registry_url_custom_ref():
    """Test URL conversion with custom git ref."""
    # Different refs produce different URLs
```

#### 2. Cache Path Generation
**Lines**: 31-34 (`registry_cache_path`)

```python
def test_registry_cache_path_per_ref():
    """Test cache path includes git ref for isolation."""
    # Different refs get different cache paths

def test_registry_cache_path_platform_dirs():
    """Test cache uses proper platform directories."""
    # Uses platformdirs user_cache_dir
```

#### 3. Cache Corruption Handling
**Lines**: 36-57 (`load_cached_registry`)

```python
def test_load_cached_registry_corrupted_json():
    """Test corrupted cache file is deleted (self-healing)."""
    # Write invalid JSON to cache
    # Should delete file and return None

def test_load_cached_registry_invalid_structure():
    """Test cache with valid JSON but wrong structure."""
    # JSON missing "tools" key
    # Should delete and return None

def test_load_cached_registry_permission_error():
    """Test cache deletion fails gracefully."""
    # Permission denied on cache file
    # Should return None without crashing
```

#### 4. Local File Support
**Lines**: 71-75 (`load_local_registry`)

```python
def test_load_local_registry_absolute_path():
    """Test loading registry from local file path."""
    # Write registry.json locally
    # Should load without network call

def test_load_local_registry_invalid_json():
    """Test local file with invalid JSON."""
    # Should raise JSONDecodeError

def test_load_local_registry_not_found():
    """Test local file path that doesn't exist."""
    # Should raise FileNotFoundError
```

#### 5. Network Fetch
**Lines**: 77-88 (`fetch_registry`)

```python
def test_fetch_registry_http_timeout():
    """Test fetch handles timeout."""
    # Mock httpx timeout
    # Should raise appropriate exception

def test_fetch_registry_404():
    """Test fetch when registry.json not found."""
    # HTTP 404 response
    # Should raise HTTPStatusError

def test_fetch_registry_invalid_response():
    """Test fetch when response isn't valid JSON."""
    # Server returns non-JSON
    # Should raise JSONDecodeError

def test_fetch_registry_redirects():
    """Test fetch follows redirects."""
    # Mock HTTP redirects
    # Should follow and fetch final URL
```

#### 6. Error Handling & Graceful Degradation
**Lines**: 90-123 (`get_registry`)

```python
def test_get_registry_network_failure_with_cache():
    """Test graceful degradation to cache on network failure."""
    # Network fails but cache exists
    # Should return cached data without error

def test_get_registry_network_failure_no_cache():
    """Test error when network fails and no cache."""
    # No network, no cache
    # Should raise RegistryFetchError with helpful message

def test_get_registry_force_refresh_bypasses_cache():
    """Test force_refresh ignores cache."""
    # Cache exists but force_refresh=True
    # Should fetch from network

def test_get_registry_force_refresh_updates_cache():
    """Test force_refresh saves new data to cache."""
    # After force_refresh, cache should be updated

def test_get_registry_uses_cache_by_default():
    """Test cache is used when available without force_refresh."""
    # Cache exists
    # Should not make network call
```

#### 7. Tool Search Edge Cases
**Lines**: 131-161 (`search_tools`)

```python
def test_search_tools_empty_query():
    """Test search with empty string."""
    # Should return empty list or all tools (document behavior)

def test_search_tools_unicode():
    """Test search handles unicode characters."""
    # Query with emoji or non-ASCII
    # Should not crash

def test_search_tools_matches_all_fields():
    """Test search checks id, name, description, and tags."""
    # Query appears in different fields for different tools
    # All should be returned
```

#### 8. Registry Status
**Lines**: 176-199 (`get_registry_status`)

```python
def test_get_registry_status_no_cache():
    """Test status when cache doesn't exist."""
    # cache_exists = False
    # provenance = "not_loaded"

def test_get_registry_status_local_file_provenance():
    """Test status detects local file source."""
    # source is local file path
    # provenance = "local_file"

def test_get_registry_status_cache_mtime():
    """Test status includes cache modification time."""
    # Cache exists
    # cache_mtime should be valid datetime

def test_get_registry_status_corrupted_cache():
    """Test status handles corrupted cache gracefully."""
    # Cache file is invalid JSON
    # Should not crash, tool_count = 0
```

---

## Module: `mcpt/workspace/config.py` (100 lines)

### Currently Tested
- ✅ default_yaml generates valid structure
- ✅ write_default creates file
- ✅ read_config returns dict
- ✅ write_config saves changes
- ✅ add_tool/remove_tool basic operations

### Missing Tests (Priority: MEDIUM)

#### 1. YAML Generation Edge Cases
**Lines**: 17-26 (`default_yaml`)

```python
def test_default_yaml_special_characters_in_source():
    """Test default_yaml with URL containing special characters."""
    # Registry URL with query params or anchors
    # Should escape properly in YAML

def test_default_yaml_long_source_url():
    """Test default_yaml with very long source URL."""
    # Extremely long URL
    # Should not break YAML formatting
```

#### 2. Configuration Reading Errors
**Lines**: 37-40 (`read_config`)

```python
def test_read_config_invalid_yaml():
    """Test read_config with invalid YAML syntax."""
    # Malformed YAML file
    # Should raise appropriate exception

def test_read_config_empty_file():
    """Test read_config with empty file."""
    # File exists but is empty
    # Should handle gracefully

def test_read_config_wrong_encoding():
    """Test read_config with different file encoding."""
    # File with non-UTF-8 encoding
    # Should handle or error clearly
```

#### 3. Configuration Writing Edge Cases
**Lines**: 43-49 (`write_config`)

```python
def test_write_config_preserves_comments():
    """Test write_config handling of YAML comments."""
    # User added comments to mcp.yaml
    # Document whether comments are preserved

def test_write_config_permission_denied():
    """Test write_config when file is read-only."""
    # Read-only mcp.yaml
    # Should raise PermissionError

def test_write_config_disk_full():
    """Test write_config when disk is full."""
    # Mock OSError for disk full
    # Should raise with clear message
```

#### 4. Add Tool Edge Cases
**Lines**: 52-78 (`add_tool`)

```python
def test_add_tool_mixed_format_duplication():
    """Test adding tool when it exists in different format."""
    # Tool exists as string, trying to add as dict with ref
    # Should detect as duplicate

def test_add_tool_case_insensitive_duplicate():
    """Test add_tool is case-sensitive for tool IDs."""
    # Document: "File-Compass" vs "file-compass" are different

def test_add_tool_empty_ref():
    """Test add_tool with ref="" (empty string)."""
    # Should add as dict with empty ref or as string?

def test_add_tool_special_characters_in_id():
    """Test add_tool with tool ID containing special chars."""
    # Tool ID with @, #, etc.
    # Should handle gracefully
```

#### 5. Remove Tool Edge Cases
**Lines**: 81-100 (`remove_tool`)

```python
def test_remove_tool_from_mixed_format_list():
    """Test remove_tool when list has both strings and dicts."""
    # Some tools as strings, others as {id, ref} dicts
    # Should remove correct one

def test_remove_tool_multiple_occurrences():
    """Test remove_tool when tool appears multiple times."""
    # Duplicate entries (shouldn't happen but test anyway)
    # Should remove all occurrences

def test_remove_tool_empty_tools_list():
    """Test remove_tool when tools list becomes empty."""
    # Remove last tool
    # tools: [] should remain in config
```

---

## Module: `mcpt/runner/stub.py` (60 lines)

### Currently Tested
- ❌ No dedicated runner tests exist yet

### Missing Tests (Priority: HIGH)

#### 1. Plan Generation
**Lines**: 15-32 (`generate_run_plan`)

```python
def test_generate_run_plan_minimal_tool():
    """Test plan generation with minimal tool metadata."""
    # Tool with only required fields
    # Should generate valid plan

def test_generate_run_plan_with_args():
    """Test plan includes arguments."""
    # Args passed to function
    # Should appear in plan["args"]

def test_generate_run_plan_safe_run_default():
    """Test plan defaults safe_run to True."""
    # Tool without defaults.safe_run
    # Plan should have safe_run=True

def test_generate_run_plan_safe_run_false():
    """Test plan respects safe_run=false."""
    # Tool with defaults.safe_run=false
    # Plan should reflect this

def test_generate_run_plan_missing_install_info():
    """Test plan generation when install info is incomplete."""
    # Tool missing install.url or install.ref
    # Should not crash
```

#### 2. Stub Execution Display
**Lines**: 35-60 (`stub_run`)

```python
def test_stub_run_displays_plan():
    """Test stub_run prints execution plan."""
    # Capture console output
    # Verify plan details shown

def test_stub_run_shows_stub_warning():
    """Test stub_run displays STUB MODE banner."""
    # Output should contain "STUB" or "stub" indication

def test_stub_run_shows_real_flag_hint():
    """Test stub_run mentions --real flag."""
    # Should guide user: "Use --real to execute"

def test_stub_run_handles_empty_args():
    """Test stub_run when plan has no arguments."""
    # args=[]
    # Should show "(none)" for arguments

def test_stub_run_handles_long_git_url():
    """Test stub_run formats long URLs gracefully."""
    # Very long git URL
    # Should not break table formatting
```

---

## Integration & End-to-End Tests

### Missing Tests (Priority: CRITICAL)

```python
# test_integration_workflows.py

def test_full_workflow_init_add_install():
    """Test complete workflow: init -> add -> install."""
    # 1. mcpt init
    # 2. mcpt add file-compass
    # 3. mcpt install file-compass
    # All should work together seamlessly

def test_workflow_search_info_add():
    """Test user journey: search -> info -> add."""
    # 1. Search for tool
    # 2. Get info on specific tool
    # 3. Add it to workspace

def test_concurrent_registry_access():
    """Test multiple mcpt commands accessing registry simultaneously."""
    # Multiple processes reading registry
    # Should not cause cache corruption

def test_workspace_migration_v0_to_v1():
    """Test handling of workspace schema version changes."""
    # Old schema_version config
    # Should handle or migrate

def test_offline_mode_workflow():
    """Test all commands work offline after initial fetch."""
    # 1. mcpt list --refresh (with network)
    # 2. Disconnect network
    # 3. All commands use cache

def test_registry_ref_pinning():
    """Test pinning to specific registry ref."""
    # Workspace uses ref=v0.1.0
    # Should use that exact ref, not latest

def test_tool_version_pinning():
    """Test adding tool with specific git ref."""
    # mcpt add file-compass --ref=v1.0.0
    # Workspace should record pinned version
```

---

## Error Scenarios & Edge Cases

### Missing Tests (Priority: HIGH)

```python
# test_error_scenarios.py

def test_corrupted_mcp_yaml():
    """Test commands handle corrupted workspace config."""
    # Invalid YAML syntax in mcp.yaml
    # Should show clear error, not crash

def test_network_interruption_during_fetch():
    """Test partial download of registry."""
    # Network drops mid-fetch
    # Should not leave corrupted cache

def test_invalid_registry_json_schema():
    """Test registry with unexpected schema."""
    # Registry missing "tools" key
    # Or tools have wrong structure

def test_permission_denied_cache_directory():
    """Test when cache directory is not writable."""
    # No write permission to cache dir
    # Should show helpful error

def test_disk_full_during_cache_write():
    """Test behavior when disk fills during operation."""
    # Mock OSError during cache save
    # Should not crash

def test_unicode_in_tool_names():
    """Test handling of non-ASCII characters."""
    # Tool names with emoji or unicode
    # Should display and work correctly

def test_extremely_large_registry():
    """Test performance with 1000+ tools."""
    # Registry with many tools
    # Search and list should remain fast

def test_circular_registry_reference():
    """Test registry source that redirects to itself."""
    # Infinite redirect loop
    # Should timeout gracefully

def test_malicious_tool_id():
    """Test tool IDs with path traversal attempts."""
    # Tool ID like "../../../etc/passwd"
    # Should not allow directory traversal

def test_command_line_injection():
    """Test CLI doesn't execute injected commands."""
    # Tool IDs or args with shell metacharacters
    # Should be safely escaped
```

---

## Performance & Load Tests

### Missing Tests (Priority: LOW)

```python
# test_performance.py

def test_list_command_response_time():
    """Test list command completes within 100ms (cached)."""
    # Measure execution time
    # Should be fast with cache

def test_search_large_registry_performance():
    """Test search performance with 10,000 tools."""
    # Large registry
    # Search should complete in <200ms

def test_cache_write_performance():
    """Test cache write doesn't block CLI."""
    # Cache write should be fast

def test_memory_usage_with_large_registry():
    """Test memory footprint remains reasonable."""
    # Load large registry
    # Monitor memory usage
```

---

## Test Coverage Summary

### Total Tests Needed: ~120 tests

**By Priority:**
- 🔴 **CRITICAL**: 25 tests (Error handling, graceful degradation, security)
- 🟠 **HIGH**: 45 tests (Core functionality, edge cases)
- 🟡 **MEDIUM**: 30 tests (Configuration variations, error messages)
- 🟢 **LOW**: 20 tests (Performance, large-scale scenarios)

**By Module:**
- `cli.py`: ~50 tests (largest module, user-facing)
- `registry/client.py`: ~35 tests (network, caching, critical infrastructure)
- `workspace/config.py`: ~20 tests (file I/O, YAML handling)
- `runner/stub.py`: ~10 tests (small module)
- Integration: ~10 tests (end-to-end workflows)

---

## Implementation Order Recommendation

1. **Week 1**: Registry critical tests (network, caching, graceful degradation) - 20 tests
2. **Week 2**: CLI error handling & security (injection, path traversal) - 20 tests
3. **Week 3**: Workspace & runner comprehensive coverage - 30 tests
4. **Week 4**: Integration tests & remaining edge cases - 30 tests
5. **Week 5**: Performance tests & polish - 20 tests

---

## Notes for Your Coders

- All test files should use `pytest` framework
- Use `typer.testing.CliRunner()` for CLI command tests
- Use `tmp_path` fixture for file operations (auto-cleanup)
- Mock `httpx` for network tests: `@patch("mcpt.registry.client.httpx.get")`
- Use `monkeypatch` for environment variable tests
- Aim for descriptive test names that explain the scenario
- Include docstrings explaining what's being tested and why
- Group related tests in classes (already established pattern)
- Test both success paths AND failure paths for every function
- Remember: **test the behavior, not the implementation**
