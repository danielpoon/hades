#!/usr/bin/env python3.12
"""
Async connectivity check to the Postgres instance using asyncpg.
Reads connection settings from environment variables:
POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict

import asyncpg


def load_env_file(env_path: Path | None = None) -> None:
    """Load .env file if it exists and variables aren't already set."""
    if env_path is None:
        script_dir = Path(__file__).parent
        # .env file is in project root (parent directory)
        env_path = script_dir.parent / ".env"
    
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


def get_db_config() -> Dict[str, str]:
    """Get database connection configuration from environment variables."""
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
        "password": password,
        "database": os.getenv("POSTGRES_DB", "hades_db"),
    }


async def test_connection(config: Dict[str, str]) -> bool:
    """Test database connection by executing a simple query."""
    try:
        conn = await asyncpg.connect(**config)
        try:
            await conn.fetchval("SELECT 1;")
        finally:
            await conn.close()
        print(
            f"Connection successful to "
            f"{config['user']}@{config['host']}:{config['port']}/{config['database']}"
        )
        return True
    except asyncpg.PostgresError as exc:
        print(f"Connection failed: {exc}")
        return False
    except Exception as exc:  # noqa: BLE001
        print(f"Unexpected error during connection test: {exc}")
        return False


def main() -> None:
    """Main entry point: load environment, validate config, and test connection."""
    # Automatically load .env file if it exists
    load_env_file()
    
    config = get_db_config()
    
    # Validate required fields
    if not config["password"]:
        print("Error: POSTGRES_PASSWORD environment variable is not set or is empty", file=sys.stderr)
        print("Make sure .env file exists or set POSTGRES_PASSWORD environment variable", file=sys.stderr)
        sys.exit(1)
    
    if not config["user"]:
        print("Error: POSTGRES_USER environment variable is not set", file=sys.stderr)
        sys.exit(1)
    
    ok = asyncio.run(test_connection(config))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

