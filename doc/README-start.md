# start.sh - Postgres Docker Management Script

A comprehensive bash script for managing the Postgres database container with automatic Python environment setup and dependency management.

## Overview

`start.sh` provides a unified interface for managing the Postgres Docker container, ensuring Python 3.12 is available, maintaining a virtual environment, and installing required dependencies automatically.

## Prerequisites

- **Docker** and **Docker Compose** (or `docker-compose`)
- **Homebrew** (for Python installation check)
- **Python 3.12** (installed via Homebrew: `brew install python@3.12`)

## Usage

```bash
./start.sh [command]
```

## Commands

### `start`

Starts the Postgres container and sets up the Python environment.

**What it does:**
1. Verifies Python 3.12 is installed (exits if not found)
2. Creates or verifies the virtual environment (`.venv`) exists
3. Installs/updates Python dependencies from `requirements.txt`
4. Starts the Postgres container (only if not already running)

**Interactive prompts:**
- Press any key after Python version verification
- Press any key after virtual environment setup
- Press any key after dependency installation

**Example:**
```bash
./start.sh start
```

### `stop`

Stops the running Postgres container.

**What it does:**
- Checks if container is running
- Stops the container if running
- Shows message if already stopped

**Example:**
```bash
./start.sh stop
```

### `status`

Shows comprehensive status information about the Postgres container.

**What it displays:**
- Container status (up/down)
- Connection parameters from `.env`:
  - Host
  - Port
  - User
  - Database
  - Password status (hidden)
- Container details from Docker Compose
- Connection test (if container is running)

**Interactive prompts:**
- Press any key after virtual environment verification (before connection test)

**Example:**
```bash
./start.sh status
```

**Output example:**
```
Postgres status: up

Connection parameters:
  Host:     localhost
  Port:     5432
  User:     *****
  Database: ****_db
  Password: Yes (hidden)

NAME             IMAGE         COMMAND                  SERVICE   STATUS
****-postgres    postgres:18   "docker-entrypoint.s…"   db        Up 5 minutes

Virtual environment found at .venv
Press any key to continue...
Testing connection...
  Connection test: ✓ Success
```

### `rebuild`

Completely rebuilds the Postgres container and environment (data volume preserved).

**What it does:**
1. Verifies Python 3.12 is installed
2. Creates or verifies the virtual environment
3. Installs/updates Python dependencies
4. Prompts for confirmation (requires typing "YES")
5. Stops and removes existing containers and images (keeps the data volume)
6. Pulls the latest Postgres image
7. Creates a fresh container (reuses existing data volume)

**Interactive prompts:**
- Press any key after Python version verification
- Press any key after virtual environment setup
- Press any key after dependency installation
- Type "YES" to confirm rebuild

**Data persistence:** The named volume is preserved; database data is kept. To fully wipe data, manually remove the volume: `docker compose down --volumes` (or use `docker volume rm hades-db_data`).

**Example:**
```bash
./start.sh rebuild
```

### `help`

Displays usage information and available commands.

**Example:**
```bash
./start.sh help
# or
./start.sh --help
# or
./start.sh -h
```

## Features

### Automatic Python Environment Management

- **Python 3.12 Check**: Verifies Python 3.12 is installed via Homebrew
- **Virtual Environment**: Automatically creates `.venv` if it doesn't exist
- **Dependency Installation**: Installs packages from `requirements.txt` into the venv
- **Venv Usage**: All Python operations use the virtual environment

### Docker Compose Compatibility

- Supports both `docker compose` (newer) and `docker-compose` (legacy)
- Automatically detects which version is available
- Uses the appropriate command format

### Connection Testing

- Automatically tests database connectivity when checking status
- Uses `postgres/postgres-conn-test.py` script
- Shows success (✓) or failure (✗) indicators

### Environment Variable Management

- Reads configuration from `.env` file
- Displays connection parameters (password hidden)
- Exports variables for Python scripts

## File Structure

The script expects the following files in the project root:

- `docker-compose.yml` - Docker Compose configuration
- `.env` - Environment variables (database credentials, etc.)
- `requirements.txt` - Python dependencies
- `postgres/postgres-conn-test.py` - Connection test script (optional, for status command)

## Virtual Environment

The script creates and manages a virtual environment at `.venv/` in the project root:

- Created automatically if missing
- Uses Python 3.12
- All dependencies installed here
- Used for all Python operations

**To remove the venv:**
```bash
rm -rf .venv
```

The venv will be automatically recreated on the next `start` or `rebuild` command.

## Error Handling

The script includes error handling for:

- Missing Docker/Docker Compose
- Missing Python 3.12
- Missing Homebrew
- Missing `docker-compose.yml`
- Missing `requirements.txt` (skips installation, continues)
- Missing virtual environment (creates it)
- Container already running/stopped (graceful messages)

## Security Notes

- Passwords are never displayed in output
- Connection test uses environment variables securely
- Rebuild requires explicit "YES" confirmation to prevent accidental data loss

## Troubleshooting

### "Python 3.12 is not installed"
Install it via Homebrew:
```bash
brew install python@3.12
```

### "Docker Compose is not available"
Install Docker Desktop or Docker Compose:
- macOS: Install Docker Desktop
- Linux: `sudo apt-get install docker-compose` or use Docker Compose plugin

### "Connection test: ✗ Failed"
- Verify container is running: `./start.sh status`
- Check `.env` file has correct credentials
- Ensure password doesn't have special characters that need quoting
- Try rebuilding: `./start.sh rebuild`

### Port already in use
- Check if another Postgres instance is running on port 5432
- Change `POSTGRES_PORT` in `.env` to a different port
- Stop conflicting services

## Examples

### First-time setup
```bash
# Start everything (creates venv, installs deps, starts container)
./start.sh start
```

### Check if everything is working
```bash
./start.sh status
```

### Stop the database
```bash
./start.sh stop
```

### Complete reset (removes all data)
```bash
./start.sh rebuild
# Type YES when prompted
```

