"""
Pytest configuration and fixtures for brew-offload tests.

Provides isolated Homebrew environments per test case using a prebuilt template.
Supports parallel execution (pytest-xdist) with no cross-test conflicts.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Generator

import pytest


# Project root and template path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
TEMPLATE_PATH = Path(__file__).parent / "brew_template"
TESTS_PATH = PROJECT_ROOT / "tests"


def get_homebrew_prefix() -> str:
    """Detect system Homebrew prefix for template generation only."""
    try:
        result = subprocess.run(
            ["brew", "--prefix"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "/home/linuxbrew/.linuxbrew"  # Fallback for Linux


@pytest.fixture(scope="session")
def brew_template_ready() -> bool:
    """
    Session-level fixture: ensure template exists.
    
    In CI: template is pre-cached.
    Locally: creates minimal template on first test run.
    """
    if not TEMPLATE_PATH.exists():
        # Create minimal template structure
        TEMPLATE_PATH.mkdir(parents=True, exist_ok=True)
        for subdir in ["Cellar", "opt", "bin", "etc", "var/cache", "var/log"]:
            (TEMPLATE_PATH / subdir).mkdir(parents=True, exist_ok=True)
        print(f"\n✓ Created minimal brew template at {TEMPLATE_PATH}")
    return True


@pytest.fixture
def temp_brew_env(brew_template_ready) -> Generator[dict, None, None]:
    """
    Per-test fixture: provides isolated Homebrew environment.
    
    Yields:
        dict with keys:
            - brew_prefix: Path to temporary Homebrew prefix
            - cellar: Path to temporary Cellar
            - env: Dict of environment variables to use in test
    
    Cleanup:
        Automatically removes temporary directory after test.
    """
    # Create unique temp directory for this test
    with tempfile.TemporaryDirectory(prefix="brew_offload_test_") as tmpdir:
        tmpdir_path = Path(tmpdir)
        brew_prefix = tmpdir_path / "homebrew"
        
        # Copy template → temporary location (fast, typically <100ms)
        shutil.copytree(TEMPLATE_PATH, brew_prefix)
        
        cellar = brew_prefix / "Cellar"
        opt = brew_prefix / "opt"
        
        # Create minimal bin structure for brew script
        bin_dir = brew_prefix / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare environment variables for clean test isolation
        test_env = os.environ.copy()
        test_env.update({
            "HOMEBREW_PREFIX": str(brew_prefix),
            "HOMEBREW_CELLAR": str(cellar),
            "HOMEBREW_REPOSITORY": str(brew_prefix / ".homebrew"),
            "HOMEBREW_CACHE": str(brew_prefix / "var/cache/Homebrew"),
            "HOMEBREW_LOGS": str(brew_prefix / "var/log"),
            "HOMEBREW_TEMP": str(tmpdir_path / "tmp"),
            # Prepend test bin and brew-offload bin to PATH
            "PATH": ":".join([
                str(PROJECT_ROOT / "bin"),
                str(bin_dir),
                test_env.get("PATH", ""),
            ]),
        })
        
        yield {
            "brew_prefix": str(brew_prefix),
            "cellar": str(cellar),
            "opt": str(opt),
            "tmpdir": str(tmpdir_path),
            "env": test_env,
        }
        
        # Cleanup: temp directory is automatically deleted by TemporaryDirectory context


@pytest.fixture
def brew_offload_module():
    """Fixture to import brew_offload module with correct PATH."""
    sys_path_backup = __import__("sys").path.copy()
    sys = __import__("sys")
    
    # Add project root to path for imports
    sys.path.insert(0, str(PROJECT_ROOT))
    
    from tests import brew_offload as module
    
    yield module
    
    # Restore sys.path
    sys.path = sys_path_backup


@pytest.fixture(autouse=True)
def reset_environment():
    """
    Autouse fixture: ensure test environment doesn't leak into global state.
    
    Stores and restores key environment variables.
    """
    env_backup = {
        "PATH": os.environ.get("PATH", ""),
        "HOMEBREW_PREFIX": os.environ.get("HOMEBREW_PREFIX"),
        "HOMEBREW_CELLAR": os.environ.get("HOMEBREW_CELLAR"),
        "HOMEBREW_REPOSITORY": os.environ.get("HOMEBREW_REPOSITORY"),
    }
    
    yield
    
    # Restore after test
    os.environ["PATH"] = env_backup["PATH"]
    for var in ["HOMEBREW_PREFIX", "HOMEBREW_CELLAR", "HOMEBREW_REPOSITORY"]:
        if env_backup[var] is not None:
            os.environ[var] = env_backup[var]
        elif var in os.environ:
            del os.environ[var]


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "requires_docker: mark test as requiring Docker (skipped on macOS)",
    )


def pytest_collection_modifyitems(config, items):
    """
    Auto-skip tests requiring Docker if Docker is unavailable.
    
    Docker tests only run on Linux in CI; automatic skip on macOS.
    """
    try:
        subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            timeout=2,
            check=True,
        )
        docker_available = True
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        docker_available = False
    
    if not docker_available:
        skip_docker = pytest.mark.skip(reason="Docker not available")
        for item in items:
            if "requires_docker" in item.keywords:
                item.add_marker(skip_docker)
