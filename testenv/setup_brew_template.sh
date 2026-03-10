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

git clone --filter=blob:none "$HOMEBREW_REPO" "$BREW_TEMPLATE_DIR/brew" 2>&1

echo $PATH
which brew

brew shellenv

eval "echo hoge"

eval "$(brew shellenv)"
test "$(which brew)" = "$BREW_TEMPLATE_DIR/brew/bin/brew"
brew --version

if brew search brew-offload 2>/dev/null ; then
    echo "brew-offload already exists in Homebrew core." 2>&1
    exit 1
fi

for formula in "${TEST_TARGET_FORMULAE[@]}"; do
    echo "Installing formula $formula into brew template..."
    brew install "$formula"
    $formula --version
done

function install_brew-offload() {
    echo "Installing brew-offload into brew template..."
    which brew
    local TEST_VERSION=0.0.1
    tar czvf /tmp/homebrew-offload-$TEST_VERSION.tar.gz -C $SCRIPT_DIR/../../ homebrew-offload
    local SHA=$(sha256sum /tmp/homebrew-offload-$TEST_VERSION.tar.gz) && SHA=${SHA%% *}
    echo SHA256: $SHA
    sed -i "s|sha256 \".*\"|sha256 \"$SHA\"|" "$SCRIPT_DIR/../brew-offload.rb"
    brew tap-new user/repo
    # create formula to populate tap metadata (URL, version)
    # Use EDITOR=true to skip interactive editor invocation
    EDITOR=true brew create file:///tmp/homebrew-offload-$TEST_VERSION.tar.gz --tap=user/repo --set-name=brew-offload --set-version=$TEST_VERSION
    local TAP=$(brew --repository user/repo)
    # copy workspace into tap, but keep the created formula's metadata
    # instead of wiping everything, just overwrite the root contents and
    # then reapply the sha256 patch to the formula file that will actually
    # be installed.
    cp -R $SCRIPT_DIR/../* $TAP
    sed -i "s|sha256 \".*\"|sha256 \"$SHA\"|" "$TAP/Formula/brew-offload.rb"
    chmod +t "$(brew --repository)"/Library/Homebrew/vendor/bundle/ruby/*/gems
    # brew audit --strict brew-offload # This command is very slow and optional.
    brew install --verbose --formula --debug $TAP/brew-offload.rb
}

install_brew-offload

echo "Homebrew template setup complete."
