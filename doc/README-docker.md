## Docker Quickstart

### Prereqs
- Docker and Docker Compose installed.
- Homebrew installed with `python@3.12` (`brew install python@3.12`).
- `.env` configured (Postgres host/port/user/password/db).

### Manage Postgres
- Start (installs Python dependancies, creates venv if needed): `./start.sh start`
- Status: `./start.sh status`
- Stop: `./start.sh stop`
- Rebuild (down + remove volumes/images, then recreate): `./start.sh rebuild`
- Help: `./start.sh help`

### Clean All Containers/Images (manual)
```bash
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker container prune -f
docker rmi $(docker images -q)  # optional; removes all images
```

### Notes
- Data persists in the `db_data` volume defined in `docker-compose.yml`.
- If port `5432` is busy, set `POSTGRES_PORT` in `.env` to a free port (e.g., `5433`) and rerun `./start.sh start`.

