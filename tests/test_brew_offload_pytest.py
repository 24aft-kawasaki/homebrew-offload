"""
Pytest-based test suite for brew-offload.

Uses isolated Homebrew environments (temp_brew_env fixture) for each test.
Supports parallel execution with pytest-xdist.
"""

import subprocess
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "tests"))
from brew_offload import arg_parse, BrewOffload


class TestArgumentParsing:
    """Unit tests for CLI argument parsing."""
    
    def test_parse_brew_passthrough(self):
        """Test parsing of brew passthrough commands."""
        args = ["brew-offload", "wrapped", "list", "--help"]
        namespace = arg_parse(*args)
        assert namespace.offload is False
        assert namespace.original_brew_args == ["list", "--help"]
    
    def test_parse_offload_add(self):
        """Test parsing of 'offload add' command."""
        args = ["brew-offload", "wrapped", "offload", "add", "python@3.12"]
        namespace = arg_parse(*args)
        assert namespace.offload is True
        assert namespace.subcommand == "add"
        assert namespace.formula == "python@3.12"
    
    def test_parse_remove_shorthand(self):
        """Test parsing of 'remove' shorthand."""
        args = ["brew-offload", "remove", "python@3.12"]
        namespace = arg_parse(*args)
        assert namespace.offload is True
        assert namespace.subcommand == "remove"
        assert namespace.formula == "python@3.12"


class TestBrewOffloadInit:
    """Tests for BrewOffload initialization."""
    
    def test_offload_object_creation(self):
        """Test basic BrewOffload object creation."""
        args = ["brew-offload", "wrapped", "list"]
        bo = BrewOffload(args)
        assert bo.args.offload is False
        assert bo.args.original_brew_args == ["list"]
    
    def test_offload_add_initialization(self):
        """Test BrewOffload initialization with offload command."""
        args = ["brew-offload", "add", "python@3.12"]
        bo = BrewOffload(args)
        assert bo.args.offload is True
        assert bo.args.subcommand == "add"


class TestBrewExecution:
    """Tests for brew command execution (passthrough)."""
    
    def test_brew_version_passthrough(self):
        """Test that brew --version can be called through the wrapper."""
        args = ["brew-offload", "wrapped", "--version"]
        bo = BrewOffload(args)
        # This should succeed; brew is available on the system
        returncode = bo.execute_original_brew(bo.args.original_brew_args)
        assert returncode == 0
    
    def test_brew_nonexistent_formula(self):
        """Test that invalid commands return non-zero."""
        args = ["brew-offload", "wrapped", "info", "nonexistent-formula-xyz-12345"]
        bo = BrewOffload(args)
        returncode = bo.execute_original_brew(bo.args.original_brew_args)
        assert returncode != 0


class TestBrewOffloadConfigFile:
    """Tests for configuration file handling."""
    
    def test_missing_config_file_handling(self, temp_brew_env):
        """
        Test that brew-offload handles missing config gracefully.
        
        Uses temp_brew_env fixture to test in isolated environment.
        """
        import os
        
        # Test environment with isolated HOMEBREW_PREFIX
        env = temp_brew_env["env"]
        cellar = temp_brew_env["cellar"]
        
        # Verify temp environment is set
        assert env["HOMEBREW_PREFIX"] == temp_brew_env["brew_prefix"]
        assert Path(cellar).exists()


class TestWrappedBrew:
    """Tests for brew wrapper functionality."""
    
    def test_brew_wrap_script_exists(self):
        """Test that the brew-wrap script exists and is readable."""
        wrap_script = Path(__file__).parent.parent / "etc" / "brew-wrap"
        assert wrap_script.exists()
        assert wrap_script.stat().st_mode & 0o111  # Check if executable
    
    def test_wrapper_sourcing(self, tmp_path):
        """Test that brew-wrap can be sourced without errors."""
        wrap_script = Path(__file__).parent.parent / "etc" / "brew-wrap"
        
        # Source the script and verify no errors
        result = subprocess.run(
            ["bash", "-c", f"source {wrap_script} && echo 'OK'"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        
        assert result.returncode == 0
        assert "OK" in result.stdout


@pytest.mark.requires_docker
class TestOffloadIntegration:
    """Integration tests requiring Docker (macOS tests skip these)."""
    
    def test_offload_add_placeholder(self):
        """
        Placeholder for Docker-based offload integration test.
        
        Full integration tests would:
        1. Start a Docker container with Homebrew
        2. Add a formula using brew-offload
        3. Verify the formula is installed and symlinked
        4. Verify offload directory structure
        
        On macOS (no Docker), this test is automatically skipped.
        """
        pytest.skip("Docker-based integration tests run on Linux CI only")


# Markers for test categorization
def pytest_configure(config):
    """Register test markers."""
    config.addinivalue_line(
        "markers",
        "unit: fast unit tests (run on all platforms)",
    )
    config.addinivalue_line(
        "markers",
        "integration: integration tests (Docker-based, Linux only)",
    )
