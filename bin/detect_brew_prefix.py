"""
Detect Homebrew prefix based on OS and architecture.

Usage:
    from bin.detect_brew_prefix import get_brew_prefix, get_os, get_arch
    
    prefix = get_brew_prefix()
    os_type = get_os()
    arch = get_arch()
"""

import platform
import subprocess
from pathlib import Path


def get_os() -> str:
    """Detect operating system type.
    
    Returns:
        'macos', 'linux', or 'unknown'
    """
    system = platform.system()
    if system == "Darwin":
        return "macos"
    elif system == "Linux":
        return "linux"
    return "unknown"


def get_arch() -> str:
    """Detect system architecture.
    
    Returns:
        'arm64', 'amd64', or 'unknown'
    """
    machine = platform.machine()
    if machine in ("arm64", "aarch64"):
        return "arm64"
    elif machine in ("x86_64", "AMD64"):
        return "amd64"
    return "unknown"


def get_brew_prefix() -> str:
    """Get Homebrew prefix based on OS and architecture.
    
    Returns:
        Path to Homebrew prefix directory.
    """
    os_type = get_os()
    arch = get_arch()
    
    if os_type == "macos":
        if arch == "arm64":
            # Apple Silicon (M1, M2, etc.)
            return "/opt/homebrew"
        elif arch == "amd64":
            # Intel Macs
            return "/usr/local"
        else:
            # Fallback
            try:
                result = subprocess.run(
                    ["brew", "--prefix"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            return "/usr/local"
    
    elif os_type == "linux":
        # Linux Homebrew: usually /home/linuxbrew/.linuxbrew regardless of arch
        try:
            result = subprocess.run(
                ["brew", "--prefix"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return "/home/linuxbrew/.linuxbrew"
    
    else:
        # Fallback for unknown OS
        try:
            result = subprocess.run(
                ["brew", "--prefix"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return "/usr/local"


if __name__ == "__main__":
    print(f"Detected OS: {get_os()}")
    print(f"Detected architecture: {get_arch()}")
    print(f"Homebrew prefix: {get_brew_prefix()}")
