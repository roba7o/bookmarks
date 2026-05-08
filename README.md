# Bookmarks API

A learning project: building crud REST API from the ground up,
attempting each layer of the stack instead of starting at higher abstracted level.

## Stack (current)

- **Server:** Starlette + Uvicorn
- **Database:** PostgreSQL 14 in Docker
- **Driver:** asyncpg (raw SQL, no ORM yet)
- **Validation:** Pydantic
- **Infra (local):** Docker Compose with named volume for persistence

## Running it

```bash
# 1. Start Postgres (auto-loads schema + sample data on fresh volume)
docker compose up -d

# 2. Activate venv and install deps
source venv/bin/activate
pip install -r phase_2/requirements.txt

# 3. Run the API
uvicorn main:app --reload
```

The API is on `localhost:8000`, Postgres is on `localhost:5432`.

### Fresh-data workflow

`phase_2/01-CREATE_TABLE.sql` and
`phase_2/02-GEN_SAMPLE_DATA.sql` for sample data.

```bash
docker compose down -v
docker compose up -d
```

## Endpoints

| Method | Path | What it does |
|---|---|---|
| `GET` | `/bookmarks/` | List all bookmarks |
| `POST` | `/bookmarks/` | Create a bookmark |
| `GET` | `/bookmarks/{id}` | Get one bookmark |
| `PUT` | `/bookmarks/{id}` | Update a bookmark |
| `DELETE` | `/bookmarks/{id}` | Delete a bookmark |

## Project layout

```
bookmarks/
├── docker-compose.yml
├── .env
├── main.py
│   ├── 01-CREATE_TABLE.sql
│   ├── 02-GEN_SAMPLE_DATA.sql
│   └── requirements.txt
```
