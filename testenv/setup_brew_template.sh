#!/bin/bash
set -euo pipefail

# Setup script for brew_template directory structure
# This runs once per CI workflow or locally on first test
# Creates the minimal Homebrew directory structure needed for testing

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
. "$SCRIPT_DIR/.env.test"

BREW_TEMPLATE_DIR="$BREW_TEMPLATE_DIR"
PATH="$PATH"
HOMEBREW_REPO="$HOMEBREW_REPO"
TEST_TARGET_FORMULAE=("${TEST_TARGET_FORMULAE[@]}")

echo "Setting up Homebrew template at: $BREW_TEMPLATE_DIR"

if ! (mkdir "$BREW_TEMPLATE_DIR" && mkdir "$BREW_TEMPLATE_DIR/brew"); then
    echo "Error: Could not create directory $BREW_TEMPLATE_DIR/brew" 2>&1
    echo "Please clean up $BREW_TEMPLATE_DIR and try again." 2>&1
    exit 1
fi

git clone --filter=blob:none "$HOMEBREW_REPO" "$BREW_TEMPLATE_DIR/brew"

eval "$(brew shellenv)"
test "$(which brew)" = "$BREW_TEMPLATE_DIR/brew/bin/brew"
brew --version

for formula in "${TEST_TARGET_FORMULAE[@]}"; do
    echo "Installing formula $formula into brew template..."
    brew install "$formula"
    $formula --version
done

echo "Homebrew template setup complete."
