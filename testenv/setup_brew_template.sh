#!/bin/bash
set -euo pipefail

# Setup script for brew_template directory structure
# This runs once per CI workflow or locally on first test
# Creates the minimal Homebrew directory structure needed for testing

BREW_TEMPLATE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/brew_template"

echo "Setting up Homebrew template at: $BREW_TEMPLATE_DIR"

# Create directory structure
mkdir -p "$BREW_TEMPLATE_DIR"/{Cellar,opt,bin,etc,var/{cache,log,run}}

# Create minimal .homebrew directory structure (Homebrew metadata)
mkdir -p "$BREW_TEMPLATE_DIR/.homebrew"

# Create a stub brew executable (so tests can detect Homebrew)
# Real tests won't use this; they exercise the actual system brew through brew-offload
cat > "$BREW_TEMPLATE_DIR/bin/brew_stub" << 'EOF'
#!/bin/bash
# Stub file; actual tests use system brew
echo "Stub brew - this should not be called in tests"
exit 1
EOF
chmod +x "$BREW_TEMPLATE_DIR/bin/brew_stub"

# Create config structure
mkdir -p "$BREW_TEMPLATE_DIR/etc/brew-offload"

# Optional: add a minimal config file template
cat > "$BREW_TEMPLATE_DIR/etc/brew-offload/config.json.template" << 'EOF'
{
  "offload_cellar": "$HOME/.offload"
}
EOF

echo "✓ Brew template created successfully at: $BREW_TEMPLATE_DIR"
du -sh "$BREW_TEMPLATE_DIR" || true
