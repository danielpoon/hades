#!/usr/bin/env python3.12
"""
Test case: Verify Postgres container can be brought up
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Tuple


def run_command(cmd: list[str]) -> Tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def get_compose_command() -> str:
    """Detect which docker compose command is available."""
    # Try docker compose (newer)
    code, _, _ = run_command(["docker", "compose", "version"])
    if code == 0:
        return "docker compose"
    
    # Try docker-compose (legacy)
    code, _, _ = run_command(["docker-compose", "version"])
    if code == 0:
        return "docker-compose"
    
    return None


def test_container_up() -> Tuple[bool, str]:
    """Test if Postgres container can be brought up."""
    script_dir = Path(__file__).parent.parent.parent
    compose_file = script_dir / "docker-compose.yml"
    
    if not compose_file.exists():
        return False, f"docker-compose.yml not found at {compose_file}"
    
    compose_cmd = get_compose_command()
    if not compose_cmd:
        return False, "Docker Compose not available"
    
    # Stop container first to ensure clean state
    cmd = compose_cmd.split() + ["-f", str(compose_file), "stop", "db"]
    run_command(cmd)
    time.sleep(2)
    
    # Start container
    cmd = compose_cmd.split() + ["-f", str(compose_file), "up", "-d", "db"]
    code, stdout, stderr = run_command(cmd)
    
    if code != 0:
        return False, f"Failed to start container: {stderr}"
    
    # Wait a bit for container to be ready
    time.sleep(3)
    
    # Check if container is running
    cmd = compose_cmd.split() + ["-f", str(compose_file), "ps", "--status", "running", "db"]
    code, stdout, stderr = run_command(cmd)
    
    if code != 0 or "db" not in stdout:
        return False, "Container started but not running"
    
    return True, "Container successfully brought up and is running"


if __name__ == "__main__":
    success, message = test_container_up()
    print(f"{'PASS' if success else 'FAIL'}: {message}")
    sys.exit(0 if success else 1)

