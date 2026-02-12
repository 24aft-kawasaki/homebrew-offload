# CI Architecture: Homebrew Template-Based Testing

## Overview

This document describes the pytest-based test infrastructure for `brew-offload`, optimized for:
- ✅ Both macOS and Linux
- ✅ No Docker (native Homebrew testing)
- ✅ Parallel execution safety
- ✅ Sub-20 second test runtime

---

## Directory Structure

```
testenv/
├── brew_template/               # Cached prebuilt template (~50KB)
│   ├── Cellar/                  # Empty; test-writable
│   ├── opt/
│   ├── bin/
│   ├── etc/
│   ├── var/
│   └── .homebrew/
├── conftest.py                  # Pytest fixtures
├── setup_brew_template.sh       # Template initializer (runs once per CI cache)
└── Dockerfile                   # Optional: for isolated template builds

tests/
├── test_brew_offload_pytest.py # Pytest-based test suite
├── conftest.py                 # Auto-loaded by pytest
└── __init__.py

pytest.ini                       # Pytest configuration
.github/workflows/
├── ci-pytest.yml               # Main CI workflow (this design)
└── update-formula.yml          # Existing release workflow
```

---

## Test Environment Lifecycle

### Per-Test Isolation (temp_brew_env fixture)

```
1. Test starts
   ├─ Random temp directory created (e.g., /tmp/brew_offload_test_xyz/)
   ├─ brew_template/ → copied to /tmp/brew_offload_test_xyz/homebrew/
   │  (Fast: ~50-100ms for small template)
   ├─ Environment variables set:
   │  ├ HOMEBREW_PREFIX=/tmp/brew_offload_test_xyz/homebrew
   │  ├ HOMEBREW_CELLAR=/tmp/brew_offload_test_xyz/homebrew/Cellar
   │  ├ HOMEBREW_REPOSITORY=/tmp/brew_offload_test_xyz/homebrew/.homebrew
   │  ├ PATH prepended with temp bin/ and brew-offload bin/
   │  └ Others (CACHE, LOGS, TEMP)
   │
   └─ Test runs with isolated environment

2. Test completes
   └─ Everything (/tmp/brew_offload_test_xyz/) auto-deleted
      (No cleanup code needed; managed by tempfile context manager)
```

### Parallel Execution Safety

- Each test gets a **unique temp directory**
- No shared state (no conflicts with pytest-xdist)
- Safe for running N tests simultaneously

---

## CI Acceleration Strategy

### 1. **Caching (3–5 seconds saved)**

**GitHub Actions cache:**
```yaml
- uses: actions/cache@v4
  with:
    path: testenv/brew_template
    key: brew-template-v1-${{ runner.os }}-${{ hashFiles('testenv/setup_brew_template.sh') }}
```

**Effect:**
- On cache hit: template already on runner (~5ms restore)
- On cache miss (new runner, script changed): rebuild in ~3 seconds
- Across ~100 jobs/month: saves ~300 seconds total

### 2. **Parallel Test Execution (pytest-xdist)**

```bash
pipenv run pytest -n auto tests/test_brew_offload_pytest.py
```

**Effect:**
- Automatic detection of available CPU cores
- GitHub Actions runners typically have 2–4 cores
- 8 unit tests × 2 cores = ~4 seconds per CPU
- **Total: ~2 seconds for all unit tests**

### 3. **Minimal Template**

Template size: ~50KB (not 50MB)
```
testenv/brew_template/
├── Cellar/              # Empty
├── opt/                 # Empty
├── bin/                 # Stub files only
├── etc/
│   └── brew-offload/    # Config structure
└── var/
```

**Copy cost:** ~50–100ms per test × 8 tests = 0.5 seconds total

### 4. **Fixture Reuse**

- `brew_template_ready`: session-scoped (once per test run)
- `temp_brew_env`: function-scoped (per test, fast copy + cleanup)
- `reset_environment`: autouse (no boilerplate in tests)

---

## Platform Differences & Handling

### macOS vs. Linux

| Aspect | macOS | Linux |
|--------|-------|-------|
| **Homebrew prefix** | `/opt/homebrew` or `/usr/local` | Manual via `get_homebrew_prefix()` |
| **Xcode CLT** | Pre-installed on GH runners | N/A |
| **Docker support** | Limited; skipped on macOS | Full support; used for integration tests |
| **Template cache** | Cached separately (different key) | Cached separately |
| **Test runtime** | ~5–10 sec (no Docker tests) | ~15–20 sec (includes Docker tests) |

### How Tests Adapt

1. **Dynamic prefix detection** (in conftest.py):
   ```python
   HOMEBREW_PREFIX=$(brew --prefix)  # Handles both /opt and /usr/local
   ```

2. **Docker auto-skip** (in conftest.py):
   ```python
   @pytest.mark.requires_docker
   def test_offload_function():
       ...  # Automatically skipped if docker not available
   ```

3. **Separate cache keys**:
   ```yaml
   key: brew-template-${{ env.CACHE_VERSION }}-${{ runner.os }}-...
   ```
   Ensures macOS and Linux templates don't collide.

---

## Runtime Breakdown (Target: 10–20 seconds)

### macOS (test-macos job)
```
Setup & Python:           ~3 sec
  ├── Checkout            1 sec
  ├── Set up Python       1 sec
  ├── Verify Homebrew      1 sec

Cache restore:            ~1 sec
  └── Template cache hit/restore

Install dependencies:     ~3 sec
  ├── pip install         1 sec
  ├── pipenv sync         2 sec

Test execution:           ~5 sec
  ├── Setup template      0.1 sec
  ├── Parallel tests (4 cores):  ~2 sec
  └── Teardown            0.1 sec

Total per matrix entry:   ~12 seconds
× 2 Python versions:      ~24 seconds total
 (but runners run in parallel, so ~12 sec wall-clock)
```

### Linux (test-linux job, similar breakout)

**Includes legacy Docker tests:**
```
... (same as above) ...
+ Docker tests:          ~5 sec
  ├── Docker setup       1 sec
  ├── Integration tests  3 sec
  └── Cleanup            1 sec

Total per matrix entry:   ~17 seconds
```

---

## Implementation Checklist

- [x] `testenv/conftest.py` – pytest fixtures + environment setup
- [x] `testenv/setup_brew_template.sh` – template initializer
- [x] `tests/test_brew_offload_pytest.py` – pytest test suite
- [x] `pytest.ini` – pytest configuration
- [x] `Pipfile` – pytest dependencies
- [x] `.github/workflows/ci-pytest.yml` – CI workflow with caching
- [ ] Update `.github/workflows/update-formula.yml` to use `ci-pytest.yml` (if needed)
- [ ] Document in README.md

---

## Usage

### Local Testing

```bash
# Install dependencies
pipenv sync --dev

# Run all tests (serial)
pipenv run test

# Run tests in parallel (auto-detect cores)
pipenv run pytest -n auto tests/test_brew_offload_pytest.py

# Run specific test
pipenv run pytest tests/test_brew_offload_pytest.py::TestArgumentParsing::test_parse_brew_passthrough -v

# Run unit tests only (macOS/Linux)
pipenv run pytest -m "not requires_docker" tests/test_brew_offload_pytest.py

# Run tests with timeout (e.g., 30 sec)
pipenv run pytest --timeout=30 tests/test_brew_offload_pytest.py
```

### CI Workflow

```bash
# Runs automatically on push/PR to main or temp
# Parallel cross-platform tests:
# - macOS-latest × Python 3.9, 3.13
# - ubuntu-latest × Python 3.9, 3.13
```

---

## Performance Tuning

### If tests are still too slow (>20 sec):

1. **Reduce template size:** Remove unused subdirectories
2. **Skip integration tests on fast runners:** Add `--skip-integration` flag
3. **Further parallelize:** Use `pytest-xdist` with `-n 8` (explicit core count)
4. **Lazy import:** Defer heavy imports inside test functions

### If tests are flaky (random failures):

1. **Check temp cleanup:** Ensure `TemporaryDirectory` context manager is working
2. **Verify PATH precedence:** Confirm `brew-offload/bin` comes first in test ENV
3. **Investigate race conditions:** Add `-v -s` flags to see detailed output
4. **Increase timeout:** Default is 30 sec; adjust in pytest.ini if needed

---

## Next Steps

1. Commit these changes:
   ```bash
   git add -A
   git commit -m "CI: Add pytest-based test infrastructure with Homebrew template caching"
   ```

2. Test locally:
   ```bash
   pipenv sync --dev
   pipenv run test-fast
   ```

3. Push to PR and verify CI passes on both platforms

4. Once stable, update `update-formula.yml` to use the new `ci-pytest.yml` if needed

---

## References

- [Pytest docs](https://docs.pytest.org/)
- [pytest-xdist for parallelization](https://pytest-xdist.readthedocs.io/)
- [GitHub Actions cache](https://docs.github.com/en/actions/using-workflows/caching-dependencies-and-build-artifacts)
- [tempfile module](https://docs.python.org/3/library/tempfile.html)
