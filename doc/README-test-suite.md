# Test Suite Documentation

Automated test suite for verifying Python environment setup, Postgres container management, and database connectivity.

## Overview

The test suite consists of independent test cases that verify:

- Python version compatibility (3.12)
- Postgres container lifecycle (start/stop)
- Database connection functionality

All tests are located in the `test_cases/` subdirectory and can be run individually or together via the main test runner.

## Prerequisites

Before running the tests, ensure:

1. **Python 3.12** is installed (via Homebrew: `brew install python@3.12`)
2. **Docker** and **Docker Compose** are installed and running
3. **Dependencies** are installed:
   
   ```bash
   # From project root
   source .venv/bin/activate  # or create venv first
   pip install -r requirements.txt
   ```
4. **`.env` file** exists in the project root with Postgres credentials:
   
   ```
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_USER=*****
   POSTGRES_PASSWORD="****"  # Note: quoted if starts with special chars
   POSTGRES_DB=****_db
   ```

## Test Cases

### 1. `test_python_version.py`

**Purpose:** Verifies that Python 3.12 is installed and being used.

**What it tests:**

- Checks `sys.version_info` for major version 3 and minor version 12
- Validates the Python interpreter version matches requirements

**Expected output:**

```
PASS: Python version is correct: 3.12.x
```

**Run individually:**

```bash
python3.12 test/test_cases/test_python_version.py
```

---

### 2. `test_container_up.py`

**Purpose:** Verifies that the Postgres container can be successfully started.

**What it tests:**

- Detects available Docker Compose command (`docker compose` or `docker-compose`)
- Stops any existing container to ensure clean state
- Starts the Postgres container using `docker-compose.yml`
- Verifies the container is running after startup
- Waits for container to be ready (3 seconds)

**Expected output:**

```
PASS: Container successfully brought up and is running
```

**Run individually:**

```bash
python3.12 test/test_cases/test_container_up.py
```

**Note:** This test will stop the container first to ensure a clean test state.

---

### 3. `test_container_down.py`

**Purpose:** Verifies that the Postgres container can be successfully stopped.

**What it tests:**

- Ensures container is running first (starts it if needed)
- Stops the container using Docker Compose
- Verifies the container is no longer in running state

**Expected output:**

```
PASS: Container successfully brought down
```

**Run individually:**

```bash
python3.12 test/test_cases/test_container_down.py
```

---

### 4. `test_database_connection.py`

**Purpose:** Verifies that a database connection can be established and queries executed.

**What it tests:**

- Ensures Postgres container is running (starts it if needed)
- Loads environment variables from `.env` file
- Parses password correctly (handles special characters like "@" prefix)
- Establishes async connection using `asyncpg`
- Executes a test query (`SELECT 1`)
- Validates connection and query execution

**Expected output:**

```
PASS: Successfully connected to *****@localhost:5432/****_db
```

**Run individually:**

```bash
python3.12 test/test_cases/test_database_connection.py
```

**Special handling:**

- Automatically loads `.env` file if present
- Strips quotes from password values (handles `POSTGRES_PASSWORD="@****"`)
- Ensures container is running before attempting connection
- Waits 5 seconds after starting container for it to be ready

---

## Running Tests

### Run All Tests

Execute the main test runner to run all test cases:

```bash
# From project root
python3.12 test/exec-tests.py

# Or using venv Python
.venv/bin/python test/exec-tests.py
```

**Expected output:**

```
======================================================================
Running Test Suite
======================================================================

Found 4 test case(s):
  - test_container_down.py
  - test_container_up.py
  - test_database_connection.py
  - test_python_version.py

Running: test_python_version.py...
  [PASS] Python version is correct: 3.12.0

Running: test_container_up.py...
  [PASS] Container successfully brought up and is running

Running: test_container_down.py...
  [PASS] Container successfully brought down

Running: test_database_connection.py...
  [PASS] Successfully connected to *****@localhost:5432/****_db

======================================================================
Test Summary
======================================================================
  ✓ test_python_version: Python version is correct: 3.12.0
  ✓ test_container_up: Container successfully brought up and is running
  ✓ test_container_down: Container successfully brought down
  ✓ test_database_connection: Successfully connected to *****@localhost:5432/****_db

Total: 4 | Passed: 4 | Failed: 0
======================================================================
```

### Run Individual Tests

Each test case can be run independently:

```bash
# Test Python version
python3.12 test/test_cases/test_python_version.py

# Test container startup
python3.12 test/test_cases/test_container_up.py

# Test container shutdown
python3.12 test/test_cases/test_container_down.py

# Test database connection
python3.12 test/test_cases/test_database_connection.py
```

Each test will output:

- `PASS: <message>` on success (exit code 0)
- `FAIL: <message>` on failure (exit code 1)

## Test Execution Order

When running all tests via `exec-tests.py`, tests are executed in alphabetical order:

1. `test_container_down.py`
2. `test_container_up.py`
3. `test_database_connection.py`
4. `test_python_version.py`

**Note:** The order doesn't matter as each test is independent and manages container state as needed.

## Test Architecture

### Test Structure

Each test case follows a consistent pattern:

```python
def test_<feature>() -> Tuple[bool, str]:
    """
    Test description.

    Returns:
        Tuple[bool, str]: (success, message)
    """
    # Test implementation
    return success, message

if __name__ == "__main__":
    success, message = test_<feature>()
    print(f"{'PASS' if success else 'FAIL'}: {message}")
    sys.exit(0 if success else 1)
```

### Test Runner

The `exec-tests.py` script:

- Discovers all test files in `test_cases/` directory (files starting with `test_` and ending with `.py`)
- Dynamically imports and executes each test module
- Collects results and displays a summary
- Returns exit code 0 if all tests pass, 1 if any fail

## Troubleshooting

### "Python 3.12 is not installed"

**Error:**

```
FAIL: Python version is 3.11, expected 3.12
```

**Solution:**

```bash
brew install python@3.12
```

### "Docker Compose not available"

**Error:**

```
FAIL: Docker Compose not available
```

**Solution:**

- Install Docker Desktop (includes Docker Compose)

- Or install Docker Compose separately:
  
  ```bash
  # macOS
  brew install docker-compose
  
  # Linux
  sudo apt-get install docker-compose
  ```

### "Connection failed: password authentication failed"

**Error:**

```
FAIL: Database connection failed: password authentication failed for user "*****"
```

**Solutions:**

1. Verify `.env` file exists and has correct credentials
2. Ensure password is quoted if it starts with special characters:
   
   ```
   POSTGRES_PASSWORD="@****"
   ```
3. Rebuild container to apply new credentials:
   
   ```bash
   ./start.sh rebuild
   ```

### "Container started but not running"

**Error:**

```
FAIL: Container started but not running
```

**Solutions:**

1. Check Docker logs:
   
   ```bash
   docker compose logs db
   ```
2. Verify port 5432 is not already in use
3. Check Docker daemon is running:
   
   ```bash
   docker ps
   ```

### "ModuleNotFoundError: No module named 'asyncpg'"

**Error:**

```
ModuleNotFoundError: No module named 'asyncpg'
```

**Solution:**

```bash
# Install dependencies
pip install -r requirements.txt

# Or using venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Test Timeout

If tests timeout, it may be due to:

- Slow Docker startup
- Network issues
- System resource constraints

Increase timeout values in test files if needed, or ensure Docker has adequate resources.

## Integration with CI/CD

The test suite can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Test Suite
  run: |
    python3.12 test/exec-tests.py
```

Exit codes:

- `0`: All tests passed
- `1`: One or more tests failed

## File Structure

```
test/
├── README-test-suite.md          # This file
├── exec-tests.py                 # Main test runner
└── test_cases/
    ├── test_python_version.py    # Python version test
    ├── test_container_up.py     # Container startup test
    ├── test_container_down.py   # Container shutdown test
    └── test_database_connection.py  # Database connection test
```

## Best Practices

1. **Run tests before committing changes** to ensure everything works
2. **Run tests after environment changes** (Python version, Docker setup, etc.)
3. **Use individual tests** for debugging specific issues
4. **Check test output** for detailed error messages
5. **Ensure container is in expected state** before running tests (some tests modify container state)

## Additional Notes

- Tests are designed to be **idempotent** - they can be run multiple times safely
- Container state tests (`test_container_up`, `test_container_down`) will modify container state
- Database connection test automatically ensures container is running
- All tests use the same `.env` file and Docker Compose configuration as the main application
- Password parsing handles special characters (like "@") correctly by stripping quotes from `.env` values
