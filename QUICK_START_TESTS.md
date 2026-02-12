# Quick Start: Running Tests

## Local Setup (One-time)

```bash
# Install dependencies
pipenv sync --dev

# Initialize Homebrew template (one-time, ~3 sec)
bash testenv/setup_brew_template.sh
```

## Running Tests

### Quick test (all platforms, serial)
```bash
pipenv run test
```
*Runs:* Pytest unit tests on your current Homebrew  
*Time:* ~2-5 sec

### Fast parallel execution (recommended)
```bash
pipenv run test-fast
```
*Runs:* Pytest unit tests in parallel (auto-detects CPU cores)  
*Time:* ~1-3 sec  
*Requirements:* pytest-xdist installed

### Specific test
```bash
pipenv run pytest tests/test_brew_offload_pytest.py::TestArgumentParsing::test_parse_brew_passthrough -v
```

### Tests with markers
```bash
# Unit tests only (all platforms)
pipenv run pytest tests/test_brew_offload_pytest.py -m "not requires_docker" -v

# Docker tests only (Linux CI)
pipenv run pytest tests/test_brew_offload_pytest.py -m requires_docker -v
```

## What Gets Tested?

### Unit Tests (TestArgumentParsing, TestBrewExecution)
- ✅ Run on **macOS** and **Linux**
- ✅ Use **native system Homebrew** (no isolation)
- ✅ ~0.5 seconds total
- ✅ Safe for parallel execution

### Wrapper Tests (TestWrappedBrew)
- ✅ Test the `etc/brew-wrap` script
- ✅ Source it and verify no errors
- ✅ ~0.1 seconds

### Integration Tests (TestOffloadIntegration)
- ⚙️ Require Docker
- ⚙️ **Skipped on macOS** (auto-skip via @requires_docker marker)
- ⚙️ Run on Linux CI
- ⚙️ ~3-5 seconds

---

## Test Environment Isolation

Each test gets its own **temporary Homebrew directory** via the `temp_brew_env` fixture:

```python
def test_something(temp_brew_env):
    # temp_brew_env["brew_prefix"] = /tmp/brew_offload_test_xyz/homebrew
    # temp_brew_env["cellar"] = /tmp/brew_offload_test_xyz/homebrew/Cellar
    # temp_brew_env["env"] = Dict with HOMEBREW_* vars set
    
    # Your test runs here with isolated Homebrew
    pass
    
    # Cleanup: /tmp/... auto-deleted (no manual cleanup needed!)
```

**Benefits:**
- No test pollution (each test clean slate)
- Safe for parallel execution
- Easy to understand test state

---

## Troubleshooting

### "pytest: command not found"
```bash
pipenv sync --dev  # Install dev dependencies
pipenv run pytest ...
```

### Tests hang or timeout
```bash
# Run with shorter timeout
pipenv run pytest --timeout=10 tests/
```

### Import errors in tests
```bash
# Verify PYTHONPATH
cd /workspaces/homebrew-offload
pipenv run pytest tests/test_brew_offload_pytest.py -v
```

### Docker tests error on Linux
```bash
# Ensure Docker is running
docker ps

# Then try again
pipenv run pytest tests/test_brew_offload_pytest.py -m requires_docker
```

---

## Platform-Specific Notes

### macOS
- Homebrew prefix varies: `/opt/homebrew` (Apple Silicon) or `/usr/local` (Intel)
- Detected automatically; no manual setup needed
- Docker tests automatically skipped (no Docker on macOS runners)
- Test time: ~3-5 sec

### Linux
- Linuxbrew prefix: `/home/linuxbrew/.linuxbrew`
- Docker tests run if available
- Test time: ~5-8 sec total

---

## For CI/GitHub Actions

See [CI_ARCHITECTURE.md](CI_ARCHITECTURE.md) for:
- Full workflow details
- Caching strategy
- Performance breakdown
- Parallel execution setup

TL;DR: CI uses `pytest -n auto` (parallel) + template caching = ~10-20 sec total runtime.

---

## Next Steps

1. **Try it locally:**
   ```bash
   pipenv sync --dev
   bash testenv/setup_brew_template.sh
   pipenv run test
   ```

2. **Verify on your platform:**
   ```bash
   pipenv run pytest tests/test_brew_offload_pytest.py -v
   ```

3. **Run in parallel (if pytest-xdist installed):**
   ```bash
   pipenv run test-fast
   ```

4. **Push to GitHub:** CI will auto-run on both macOS and Linux!
