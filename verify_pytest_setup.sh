#!/bin/bash
# Verification script: Ensure all components are ready for testing

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ERRORS=0

echo "🔍 Verifying pytest infrastructure..."
echo

# 1. Check file existence
echo "1️⃣  Checking file structure..."
files=(
    "testenv/conftest.py"
    "testenv/setup_brew_template.sh"
    "tests/test_brew_offload_pytest.py"
    ".github/workflows/ci-pytest.yml"
    "pytest.ini"
    "Pipfile"
    "CI_ARCHITECTURE.md"
    "QUICK_START_TESTS.md"
    "IMPLEMENTATION_SUMMARY.md"
)

for file in "${files[@]}"; do
    if [ -f "$REPO_ROOT/$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ✗ $file (MISSING)"
        ERRORS=$((ERRORS + 1))
    fi
done
echo

# 2. Check script permissions
echo "2️⃣  Checking script permissions..."
if [ -x "$REPO_ROOT/testenv/setup_brew_template.sh" ]; then
    echo "   ✓ setup_brew_template.sh is executable"
else
    echo "   ✗ setup_brew_template.sh is NOT executable"
    ERRORS=$((ERRORS + 1))
fi
echo

# 3. Check Python syntax
echo "3️⃣  Checking Python syntax..."
python3 -m py_compile "$REPO_ROOT/testenv/conftest.py" > /dev/null 2>&1 && \
    echo "   ✓ testenv/conftest.py" || \
    { echo "   ✗ testenv/conftest.py (syntax error)"; ERRORS=$((ERRORS + 1)); }

python3 -m py_compile "$REPO_ROOT/tests/test_brew_offload_pytest.py" > /dev/null 2>&1 && \
    echo "   ✓ tests/test_brew_offload_pytest.py" || \
    { echo "   ✗ tests/test_brew_offload_pytest.py (syntax error)"; ERRORS=$((ERRORS + 1)); }
echo

# 4. Check Pipfile
echo "4️⃣  Checking Pipfile dependencies..."
if grep -q "pytest" "$REPO_ROOT/Pipfile"; then
    echo "   ✓ pytest listed"
else
    echo "   ✗ pytest NOT in Pipfile"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "pytest-xdist" "$REPO_ROOT/Pipfile"; then
    echo "   ✓ pytest-xdist listed"
else
    echo "   ✗ pytest-xdist NOT in Pipfile"
    ERRORS=$((ERRORS + 1))
fi
echo

# 5. Check CI workflow
echo "5️⃣  Checking CI workflow..."
if grep -q "pytest -n auto" "$REPO_ROOT/.github/workflows/ci-pytest.yml"; then
    echo "   ✓ Parallel execution configured"
else
    echo "   ✗ Parallel execution NOT configured"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "actions/cache" "$REPO_ROOT/.github/workflows/ci-pytest.yml"; then
    echo "   ✓ Caching configured"
else
    echo "   ✗ Caching NOT configured"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "macos-latest" "$REPO_ROOT/.github/workflows/ci-pytest.yml"; then
    echo "   ✓ macOS job configured"
else
    echo "   ✗ macOS job NOT configured"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "ubuntu-latest" "$REPO_ROOT/.github/workflows/ci-pytest.yml"; then
    echo "   ✓ Linux job configured"
else
    echo "   ✗ Linux job NOT configured"
    ERRORS=$((ERRORS + 1))
fi
echo

# 6. Summary
echo "────────────────────────────────────────"
if [ $ERRORS -eq 0 ]; then
    echo "✅  All checks passed! Infrastructure is ready."
    echo
    echo "Next steps:"
    echo "  1. pipenv sync --dev"
    echo "  2. bash testenv/setup_brew_template.sh"
    echo "  3. pipenv run test"
    exit 0
else
    echo "❌  $ERRORS check(s) failed. Please review above."
    exit 1
fi
