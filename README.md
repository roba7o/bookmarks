# Bookmarks API

A learning project: building a CRUD REST API from the ground up,
working through each layer of the stack instead of starting at a higher
abstraction. See [docs/first_plan.md](docs/first_plan.md) for the full roadmap.

## Stack (current)

- **Server:** Starlette + Uvicorn
- **Database:** PostgreSQL 14 (in Docker)
- **Driver / ORM:** asyncpg + SQLAlchemy Core (async)
- **Validation:** Pydantic
- **Infra (local):** Docker Compose with a named volume for persistence

## Setup

```bash
# 1. Clone and enter the repo
cd bookmarks

# 2. Copy the env template and fill in values
cp .env.example .env

# 3. Start Postgres
docker compose up -d

# 4. Create a virtualenv and install deps
python -m venv venv
source venv/bin/activate
pip install -e .

# 5. Run the API
uvicorn src.main:app --reload
```

The API listens on `localhost:8000`. Postgres listens on `localhost:5432`.

### Seeding sample data

The lifespan can optionally run [SQL/02-GEN_SAMPLE_DATA.sql](SQL/02-GEN_SAMPLE_DATA.sql)
on startup. Gated by an env var:

```bash
SEED_DATA=true uvicorn src.main:app --reload
```

### Resetting the database

The lifespan currently drops and recreates tables on every boot
(see [src/main.py](src/main.py)). To also wipe the Postgres volume entirely:

```bash
docker compose down -v
docker compose up -d
```

## Endpoints

| Method | Path | What it does | Status codes |
|---|---|---|---|
| `GET` | `/bookmarks/` | List all bookmarks | 200 |
| `POST` | `/bookmarks/` | Create a bookmark | 200, 409, 422 |
| `GET` | `/bookmarks/{id}` | Get one bookmark | 200, 404 |
| `PUT` | `/bookmarks/{id}` | Update a bookmark | 200, 404, 409, 422 |
| `DELETE` | `/bookmarks/{id}` | Delete a bookmark | 200, 404 |

Error responses are JSON:

- **404** — resource doesn't exist
- **409** — unique-constraint violation (e.g., duplicate title)
- **422** — payload failed Pydantic validation
- **500** — anything unexpected (logged server-side with traceback)

See [docs/exceptions.md](docs/exceptions.md) for the full handler model.

## Environment variables

| Variable | Purpose |
|---|---|
| `DB_USER` | Postgres user (used by docker-compose and the app) |
| `DB_PASSWORD` | Postgres password |
| `DB_NAME` | Database name |
| `SEED_DATA` | Set to `"true"` to load sample data on startup |

## Project layout

```
bookmarks/
├── README.md
├── docker-compose.yml
├── pyproject.toml
├── .env.example
├── SQL/
│   ├── 01-CREATE_TABLE.sql
│   └── 02-GEN_SAMPLE_DATA.sql
├── docs/                       ← learning notes + plans
│   ├── first_plan.md           ← phase-by-phase roadmap
│   ├── phase2_polish.md        ← current-phase tidy-up plan
│   └── exceptions.md           ← Starlette exception model reference
└── src/
    ├── __init__.py
    ├── main.py                 ← Starlette app + lifespan + wiring
    ├── endpoints.py            ← Table + Pydantic schema + route classes
    └── handlers.py             ← global exception handlers
```

## Status

Phase 2 (PostgreSQL + SQLAlchemy) complete. Phase 3 (JWT auth) next.
