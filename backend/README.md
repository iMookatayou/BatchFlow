# BatchFlow Backend

Backend service for BatchFlow (FastAPI + SQLAlchemy + Alembic + MySQL).
This repo is packaged so a new engineer can migrate, seed, and run integration tests quickly.

---

## Requirements

- Python **3.11+** recommended (project targets `>=3.11`)
- MySQL **8+**
- macOS / Linux shell (Windows should work via WSL)

---

## Project Structure (high level)

- `app/` — application code (API, services, jobs)
- `alembic/` — migrations
- `scripts/` — local/dev scripts (`seed_db.py`, `test.sh`, etc.)
- `tests/` — integration tests

---

## Setup (Local)

### 1) Create virtualenv + install dependencies

```bash
python3.11 -m venv .venv
source .venv/bin/activate

pip install -U pip
pip install -e ".[dev]"

## 🐳 Local Development with Docker

### Requirements
- Docker
- Docker Compose

### Start backend + database
```bash
docker compose up --build
