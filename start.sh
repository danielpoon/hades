#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: start.sh [start|stop|status|rebuild|help]

  start    Start Postgres (only if not already running)
  stop     Stop Postgres (only if running)
  status   Show whether Postgres is up or down
  rebuild  Remove containers/images/volumes and recreate Postgres
  help     Show this help
EOF
  exit "${1:-0}"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.yml"
VENV_DIR="${SCRIPT_DIR}/.venv"
[[ -f "${COMPOSE_FILE}" ]] || { echo "docker-compose.yml not found at ${COMPOSE_FILE}" >&2; exit 1; }

compose() {
  if docker compose version >/dev/null 2>&1; then
    docker compose -f "${COMPOSE_FILE}" "$@"
    return
  fi
  if docker-compose version >/dev/null 2>&1; then
    docker-compose -f "${COMPOSE_FILE}" "$@"
    return
  fi
  echo "Docker Compose is not available. Install docker and docker compose." >&2
  exit 1
}

SERVICE=db

wait_for_key() {
  # ANSI color codes: \033[33m = yellow, \033[0m = reset
  read -n 1 -s -r -p $'\033[33mPress any key to continue...\033[0m'
  echo ""
}

require_python312() {
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew is not installed. Install Homebrew, then run: brew install python@3.12" >&2
    exit 1
  fi
  if ! command -v python3.12 >/dev/null 2>&1; then
    echo "Python 3.12 is not installed. Install with: brew install python@3.12" >&2
    exit 1
  fi
  echo "Python 3.12 detected at $(command -v python3.12)"
  echo "Execute python scripts with % python3.12 <scriptname>"
  echo "Uninstall in future if required: brew uninstall --force python@3.12"
}

require_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is not installed. Install Docker Desktop from https://www.docker.com/products/docker-desktop" >&2
    exit 1
  fi
  
  # Check if Docker daemon is running
  if ! docker info >/dev/null 2>&1; then
    echo "Docker daemon is not running. Please start Docker Desktop." >&2
    exit 1
  fi
  
  # Check for Docker Compose (newer or legacy)
  if ! docker compose version >/dev/null 2>&1 && ! docker-compose version >/dev/null 2>&1; then
    echo "Docker Compose is not available. Install Docker Desktop (includes Docker Compose) or install docker-compose separately." >&2
    exit 1
  fi
  
  # Detect which compose command is available
  if docker compose version >/dev/null 2>&1; then
    echo "Docker and Docker Compose detected (using 'docker compose')"
  else
    echo "Docker and Docker Compose detected (using 'docker-compose')"
  fi
}

ensure_venv() {
  if [[ -x "${VENV_DIR}/bin/python" ]]; then
    echo "Virtual environment found at ${VENV_DIR}"
    return
  fi
  echo "Virtual environment not found. Creating one with python3.12 at ${VENV_DIR}"
  python3.12 -m venv "${VENV_DIR}"
  echo "Virtual environment created successfully"
}

install_requirements() {
  local req_file="${SCRIPT_DIR}/requirements.txt"
  if [[ ! -f "${req_file}" ]]; then
    echo "requirements.txt not found at ${req_file}; skipping dependency install." >&2
    return
  fi
  
  # Ensure venv exists and is valid
  if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
    echo "Error: Virtual environment not found at ${VENV_DIR}. Run ensure_venv first." >&2
    return 1
  fi
  
  local venv_python="${VENV_DIR}/bin/python"
  local venv_pip="${VENV_DIR}/bin/pip"
  
  # ANSI color codes: \033[2;90m = faint light grey, \033[0m = reset
  local grey_start="\033[2;90m"
  local grey_end="\033[0m"
  
  echo -e "${grey_start}Installing/updating dependencies using venv Python: ${venv_python}${grey_end}"
  
  # Color all pip output in grey by wrapping each line
  "${venv_python}" -m pip install --upgrade pip 2>&1 | while IFS= read -r line; do
    echo -e "${grey_start}${line}${grey_end}"
  done
  
  "${venv_pip}" install -r "${req_file}" 2>&1 | while IFS= read -r line; do
    echo -e "${grey_start}${line}${grey_end}"
  done
}

is_running() {
  compose ps --status running "${SERVICE}" | grep -q "${SERVICE}"
}

wait_for_health() {
  # Wait for container healthcheck to report healthy
  local cid status
  cid="$(compose ps -q "${SERVICE}")"
  if [[ -z "${cid}" ]]; then
    echo "Container ID not found for service ${SERVICE}" >&2
    return 1
  fi

  local attempts=15
  local delay=2
  for ((i = 1; i <= attempts; i++)); do
    status="$(docker inspect -f '{{.State.Health.Status}}' "${cid}" 2>/dev/null || true)"
    if [[ "${status}" == "healthy" ]]; then
      return 0
    fi
    if [[ "${status}" == "unhealthy" ]]; then
      echo "Container healthcheck reports unhealthy." >&2
      return 1
    fi
    sleep "${delay}"
  done

  echo "Container did not become healthy after $((attempts * delay))s." >&2
  return 1
}

start_service() {
  require_docker
  wait_for_key
  
  require_python312
  wait_for_key
  
  ensure_venv
  echo "Virtual environment is ready and will be used for all Python operations."
  wait_for_key
  
  install_requirements
  wait_for_key

  if is_running; then
    echo "Postgres is already running."
  else
    compose up -d "${SERVICE}"
  fi

  # Wait for health before connection test
  echo "Waiting for Postgres container health..."
  if ! wait_for_health; then
    echo "Container is not healthy; skipping connection test." >&2
    return
  fi
  
  # Test connection if container is running
  if is_running; then
    local env_file="${SCRIPT_DIR}/.env"
    local host="localhost"
    local port="5432"
    local user="postgres"
    local db="postgres"
    
    if [[ -f "${env_file}" ]]; then
      # Source .env to get variables (handle variable expansion)
      set +u
      # shellcheck source=/dev/null
      source "${env_file}"
      set -u
      host="${POSTGRES_HOST:-${host}}"
      port="${POSTGRES_PORT:-${port}}"
      user="${POSTGRES_USER:-${user}}"
      db="${POSTGRES_DB:-${db}}"
    fi
    
    local test_script="${SCRIPT_DIR}/postgres/postgres-conn-test.py"
    if [[ -f "${test_script}" ]]; then
      echo ""
      echo "Testing connection..."
      
      local python_cmd
      if [[ -x "${VENV_DIR}/bin/python" ]]; then
        python_cmd="${VENV_DIR}/bin/python"
      elif command -v python3.12 >/dev/null 2>&1; then
        python_cmd="python3.12"
      else
        echo "  Skipping connection test: Python 3.12 not found" >&2
        return
      fi
      
      # Export env vars for the test script
      export POSTGRES_HOST="${host}"
      export POSTGRES_PORT="${port}"
      export POSTGRES_USER="${user}"
      export POSTGRES_DB="${db}"
      if [[ -n "${POSTGRES_PASSWORD:-}" ]]; then
        export POSTGRES_PASSWORD="${POSTGRES_PASSWORD}"
      fi
      
      if "${python_cmd}" "${test_script}" 2>/dev/null; then
        echo "  Connection test: ✓ Success"
      else
        echo "  Connection test: ✗ Failed"
      fi
    fi
  fi
}

stop_service() {
  if ! is_running; then
    echo "Postgres is already stopped."
    return
  fi
  compose stop "${SERVICE}"
}

show_status() {
  local env_file="${SCRIPT_DIR}/.env"
  local host="localhost"
  local port="5432"
  local user="postgres"
  local db="postgres"
  local password_set="No"

  if [[ -f "${env_file}" ]]; then
    # Source .env to get variables (handle variable expansion)
    set +u
    # shellcheck source=/dev/null
    source "${env_file}"
    set -u
    host="${POSTGRES_HOST:-${host}}"
    port="${POSTGRES_PORT:-${port}}"
    user="${POSTGRES_USER:-${user}}"
    db="${POSTGRES_DB:-${db}}"
    if [[ -n "${POSTGRES_PASSWORD:-}" ]]; then
      password_set="Yes (hidden)"
    fi
  fi

  if is_running; then
    echo "Postgres status: up"
  else
    echo "Postgres status: down"
  fi
  echo ""
  echo "Connection parameters:"
  echo "  Host:     ${host}"
  echo "  Port:     ${port}"
  echo "  User:     ${user}"
  echo "  Database: ${db}"
  echo "  Password: ${password_set}"
  echo ""
  compose ps "${SERVICE}"
  
  # Test connection if container is running
  if is_running; then
    local test_script="${SCRIPT_DIR}/postgres/postgres-conn-test.py"
    if [[ -f "${test_script}" ]]; then
      echo ""
      local python_cmd
      if [[ -x "${VENV_DIR}/bin/python" ]]; then
        python_cmd="${VENV_DIR}/bin/python"
        echo "Virtual environment found at ${VENV_DIR}"
        wait_for_key
      elif command -v python3.12 >/dev/null 2>&1; then
        python_cmd="python3.12"
        echo "Using system Python 3.12 (venv not found)"
        wait_for_key
      else
        echo "  Skipping connection test: Python 3.12 not found" >&2
        return
      fi
      
      echo "Testing connection..."
      
      # Export env vars for the test script
      export POSTGRES_HOST="${host}"
      export POSTGRES_PORT="${port}"
      export POSTGRES_USER="${user}"
      export POSTGRES_DB="${db}"
      if [[ -n "${POSTGRES_PASSWORD:-}" ]]; then
        export POSTGRES_PASSWORD="${POSTGRES_PASSWORD}"
      fi
      
      if "${python_cmd}" "${test_script}" 2>/dev/null; then
        echo "  Connection test: ✓ Success"
      else
        echo "  Connection test: ✗ Failed"
      fi
    fi
  fi
}

rebuild_service() {
  require_docker
  wait_for_key
  
  require_python312
  wait_for_key
  
  ensure_venv
  echo "Virtual environment is ready and will be used for all Python operations."
  wait_for_key
  
  install_requirements
  wait_for_key

  echo "This will stop the service and remove containers/images for Postgres (data volume preserved)."
  read -r -p "Type YES to continue: " confirm
  if [[ "${confirm}" != "YES" ]]; then
    echo "Rebuild aborted."
    return
  fi

  # Preserve the named volume; omit --volumes to keep data
  compose down --rmi all || true
  compose pull "${SERVICE}"
  compose up -d --force-recreate "${SERVICE}"
}

[[ $# -gt 0 ]] || usage 1

case "$1" in
  start) start_service ;;
  stop) stop_service ;;
  status) show_status ;;
  rebuild) rebuild_service ;;
  help|--help|-h) usage 0 ;;
  *) echo "Unknown option: $1" >&2; usage 1 ;;
esac

