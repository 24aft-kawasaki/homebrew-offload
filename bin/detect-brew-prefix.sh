#!/usr/bin/env bash
# Detect and export the Homebrew prefix based on OS and architecture
# Usage: source bin/detect-brew-prefix.sh
#        echo $BREW_PREFIX

set -e

detect_os() {
  case "$(uname -s)" in
    Darwin)
      echo "macos"
      ;;
    Linux)
      echo "linux"
      ;;
    *)
      echo "unknown"
      ;;
  esac
}

detect_arch() {
  case "$(uname -m)" in
    arm64 | aarch64)
      echo "arm64"
      ;;
    x86_64 | amd64)
      echo "amd64"
      ;;
    *)
      echo "unknown"
      ;;
  esac
}

# Detect OS and architecture
OS=$(detect_os)
ARCH=$(detect_arch)

# Determine Homebrew prefix based on OS and architecture
case "${OS}" in
  macos)
    case "${ARCH}" in
      arm64)
        # Apple Silicon (M1, M2, etc.)
        BREW_PREFIX="/opt/homebrew"
        ;;
      amd64)
        # Intel Macs
        BREW_PREFIX="/usr/local"
        ;;
      *)
        # Fallback: try to get brew --prefix
        BREW_PREFIX="$(brew --prefix 2>/dev/null || echo '/usr/local')"
        ;;
    esac
    ;;
  linux)
    # Linux Homebrew
    case "${ARCH}" in
      arm64)
        BREW_PREFIX="/home/linuxbrew/.linuxbrew"
        ;;
      amd64)
        BREW_PREFIX="/home/linuxbrew/.linuxbrew"
        ;;
      *)
        BREW_PREFIX="$(brew --prefix 2>/dev/null || echo '/home/linuxbrew/.linuxbrew')"
        ;;
    esac
    ;;
  *)
    # Fallback
    BREW_PREFIX="$(brew --prefix 2>/dev/null || echo '/usr/local')"
    ;;
esac

# Export for use in subshells
export BREW_PREFIX
export DETECTED_OS="${OS}"
export DETECTED_ARCH="${ARCH}"

# Output info
if [[ "${1}" != "--quiet" ]]; then
  echo "Detected OS: ${DETECTED_OS} (${DETECTED_ARCH})"
  echo "Homebrew prefix: ${BREW_PREFIX}"
fi
