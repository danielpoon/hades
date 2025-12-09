#!/usr/bin/env python3.12
"""
Test case: Verify database connection works
"""

import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Tuple

import asyncpg


def load_env_file(env_path: Path | None = None) -> None:
    """Load .env file if it exists and variables aren't already set."""
    if env_path is None:
        script_dir = Path(__file__).parent.parent.parent
        env_path = script_dir / ".env"
    
    if not env_path.exists():
        return
    
    # Only set variables that aren't already in environment
    with env_path.open() as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            # Parse KEY=VALUE or KEY="VALUE"
            if "=" not in line:
                continue
            
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            
            # Remove quotes if present
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]
            
            # Only set if not already in environment
            if key and key not in os.environ:
                os.environ[key] = value


def get_db_config() -> Dict[str, str | int]:
    """Get database configuration from environment variables."""
    password = os.getenv("POSTGRES_PASSWORD", "")
    # Strip quotes if present (from .env file quoting)
    if password.startswith('"') and password.endswith('"'):
        password = password[1:-1]
    elif password.startswith("'") and password.endswith("'"):
        password = password[1:-1]
    
    return {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "user": os.getenv("POSTGRES_USER", "hades"),
        "password": password,  # Keep as string to handle "@" prefix correctly
        "database": os.getenv("POSTGRES_DB", "hades_db"),
    }


async def test_connection(config: Dict[str, str | int]) -> Tuple[bool, str]:
    """Test database connection by executing a simple query."""
    try:
        conn = await asyncpg.connect(**config)
        try:
            result = await conn.fetchval("SELECT 1;")
            if result == 1:
                return True, f"Successfully connected to {config['user']}@{config['host']}:{config['port']}/{config['database']}"
            return False, "Connection succeeded but query returned unexpected result"
        finally:
            await conn.close()
    except asyncpg.PostgresError as exc:
        return False, f"Database connection failed: {exc}"
    except Exception as exc:
        return False, f"Unexpected error during connection test: {exc}"


def ensure_container_running() -> Tuple[bool, str]:
    """Ensure Postgres container is running."""
    script_dir = Path(__file__).parent.parent.parent
    compose_file = script_dir / "docker-compose.yml"
    
    if not compose_file.exists():
        return False, f"docker-compose.yml not found at {compose_file}"
    
    # Detect compose command
    compose_cmd = None
    for cmd in ["docker compose", "docker-compose"]:
        try:
            subprocess.run(
                cmd.split() + ["version"],
                capture_output=True,
                check=True,
                timeout=5
            )
            compose_cmd = cmd
            break
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    if not compose_cmd:
        return False, "Docker Compose not available"
    
    # Check if container is running
    try:
        result = subprocess.run(
            compose_cmd.split() + ["-f", str(compose_file), "ps", "--status", "running", "db"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "db" in result.stdout:
            return True, "Container is already running"
        
        # Start container
        result = subprocess.run(
            compose_cmd.split() + ["-f", str(compose_file), "up", "-d", "db"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            return False, f"Failed to start container: {result.stderr}"
        
        # Wait for container to be ready
        time.sleep(5)
        return True, "Container started successfully"
        
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, f"Error ensuring container is running: {e}"


def test_database_connection() -> Tuple[bool, str]:
    """Test if database connection works by ensuring container is running and connecting."""
    # Ensure container is running
    container_ok, container_msg = ensure_container_running()
    if not container_ok:
        return False, f"Cannot test connection: {container_msg}"
    
    # Load .env file
    load_env_file()
    
    config = get_db_config()
    
    # Validate required fields
    if not config["password"]:
        return False, "POSTGRES_PASSWORD environment variable is not set or is empty"
    
    if not config["user"]:
        return False, "POSTGRES_USER environment variable is not set"
    
    # Run async test
    success, message = asyncio.run(test_connection(config))
    return success, message


if __name__ == "__main__":
    success, message = test_database_connection()
    print(f"{'PASS' if success else 'FAIL'}: {message}")
    sys.exit(0 if success else 1)

