# Bookmarks API

A learning project: building a CRUD REST API from the ground up, working
through each layer of the stack instead of starting at a higher abstraction.

Roadmap and notes live in `docs/` — that directory is gitignored, so it only
exists on the machine it was written on.

## Stack (current)

- **Server:** Starlette + Uvicorn
- **Database:** PostgreSQL 14 (in Docker)
- **Driver / ORM:** asyncpg + SQLAlchemy Core (async)
- **Validation:** Pydantic
- **Auth:** PyJWT (HS256) + bcrypt, enforced by ASGI middleware
- **Packaging:** uv (`pyproject.toml` + `uv.lock`)
- **Infra (local):** Docker Compose — `app` and `db` services, named volume for
  Postgres persistence

## Setup

### Everything in Docker

```bash
# 1. Copy the env template and fill in values
cp .env.example .env

# 2. Build and start Postgres + the API
docker compose up -d --build
```

The API listens on `localhost:8000`. Postgres listens on `localhost:5432`.

`.env` is excluded by [.dockerignore](.dockerignore), so the app container gets
its config from the `environment:` block in
[docker-compose.yml](docker-compose.yml), which interpolates `.env` at compose
time. `DATABASE_URL` is built there and points at the `db` service hostname.

### Running the API on the host

Useful for `--reload`. Postgres still runs in Docker.

```bash
docker compose up -d db
uv sync
uv run uvicorn src.bookmarks.main:app --reload
```

This path reads `DATABASE_URL` from `.env` via `load_dotenv()`, so `.env` needs
a host-facing URL:

```
DATABASE_URL=postgresql+asyncpg://<DB_USER>:<DB_PASSWORD>@localhost:5432/<DB_NAME>
```

### Run modes (`RUN_MODE`)

The app **requires** `RUN_MODE` (`DEV` or `LOAD`), read in
[settings.py](src/bookmarks/settings.py):

| `RUN_MODE` | debug | log level | use for |
|---|---|---|---|
| `DEV`  | on  | `INFO`    | everyday development |
| `LOAD` | off | `WARNING` | load testing — quiet logs, no traceback leaked in responses |

Keep `RUN_MODE=DEV` in `.env` as the default (so normal commands need no prefix),
and override only when load testing:

```bash
# everyday — DEV comes from .env, no prefix needed
uv run uvicorn src.bookmarks.main:app
uv run ipython -i scripts/reload.py

# load test — put the APP into LOAD mode
RUN_MODE=LOAD uv run uvicorn src.bookmarks.main:app
```

**Locust does not take `RUN_MODE`.** It's a *separate process* that only fires
HTTP at the app — it never imports `settings`, so `RUN_MODE` means nothing to it.
The mode changes how the **app** behaves, so it goes on the `uvicorn` command.
Run Locust plainly against the app:

```bash
uv run locust -f locust_load/test_locust_from_docs.py
```

### Tables

The lifespan in [src/main.py](src/main.py) runs `metadata.create_all` on every
boot. It creates missing tables and leaves existing ones alone — it does not
drop or migrate. To change a column you currently have to wipe the volume:

```bash
docker compose down -v
docker compose up -d --build
```

### REPL client

[scripts/client.py](scripts/client.py) is a thin httpx wrapper that holds the
JWT for you, so you can drive the API without assembling curl headers by hand.

```bash
uv run ipython -i scripts/reload.py
```

```python
c.create_user("me@example.com", "hunter2000")
c.login_user("me@example.com", "hunter2000")   # stores the token on the client
c.create_bookmark("Damascus Station", "David McCloskey", 10)
c.list_all_bookmarks()
```

## Endpoints

Every route except `/auth/register` and `/auth/login` requires an
`Authorization: Bearer <token>` header. [src/middleware.py](src/middleware.py)
decodes it and puts the user id on `request.state.user_id`; the bookmark
queries filter on that, so a user only ever sees their own rows.

### Auth

| Method | Path | What it does | Status codes |
|---|---|---|---|
| `POST` | `/auth/register` | Create a user, return a token | 200, 409, 422 |
| `POST` | `/auth/login` | Exchange email + password for a token | 200, 401, 422 |
| `GET` | `/auth/me` | Return the caller's id and email | 200, 401, 404 |

### Bookmarks

| Method | Path | What it does | Status codes |
|---|---|---|---|
| `GET` | `/bookmarks` | List the caller's bookmarks | 200, 401 |
| `POST` | `/bookmarks` | Create a bookmark | 200, 401, 409, 422 |
| `GET` | `/bookmarks/{bm_seq}` | Get one bookmark | 200, 401, 404 |
| `PUT` | `/bookmarks/{bm_seq}` | Update a bookmark | 200, 401, 404, 409, 422 |
| `DELETE` | `/bookmarks/{bm_seq}` | Delete a bookmark | 200, 401, 404 |

Paths are registered without a trailing slash.

### Errors

Handlers are wired up in [src/main.py](src/main.py) and defined in
[src/exception_handlers.py](src/exception_handlers.py). They return
`{"detail": ..., "code": ...}`:

- **404** — resource doesn't exist, or belongs to another user
- **409** — unique-constraint violation
- **422** — payload failed Pydantic validation
- **500** — anything unexpected (logged server-side with traceback)

**401** is the exception: it's returned directly by the middleware, before the
handler chain, and its body is a bare JSON string rather than an object.

## Environment variables

| Variable | Purpose |
|---|---|
| `DB_USER` | Postgres user — used by compose to init the `db` container |
| `DB_PASSWORD` | Postgres password |
| `DB_NAME` | Database name |
| `DATABASE_URL` | Full async SQLAlchemy URL the app connects with |
| `JWT_SECRET` | HMAC signing key for tokens |
| `JWT_ALGORITHM` | Signing algorithm (`HS256`) |

`JWT_SECRET` and `JWT_ALGORITHM` are read with `os.environ[...]` in
[src/settings.py](src/settings.py), so the app fails at import if they're
missing rather than starting up unsigned.

## Project layout

```
bookmarks/
├── README.md
├── Dockerfile                    ← uv-based image for the app service
├── docker-compose.yml            ← app + db
├── .dockerignore
├── pyproject.toml
├── uv.lock
├── .env.example
├── SQL/                          ← hand-written DDL from phase 1 (see below)
│   ├── 01-CREATE_TABLE.sql
│   └── 02-GEN_SAMPLE_DATA.sql
├── scripts/
│   ├── client.py                 ← httpx REPL client, holds the JWT
│   ├── reload.py                 ← ipython entrypoint
│   └── seed.py                   ← loads 02-GEN_SAMPLE_DATA.sql
├── docs/                         ← learning notes + plans (gitignored)
└── src/
    ├── main.py                   ← Starlette app, lifespan, route + handler wiring
    ├── settings.py               ← env loading + logging config
    ├── schemas.py                ← SQLAlchemy tables + Pydantic models
    ├── auth.py                   ← issue/decode JWTs
    ├── middleware.py             ← bearer-token authentication
    ├── exception_handlers.py     ← global exception handlers
    └── routes/
        ├── auth.py               ← register / login / me
        └── bookmarks.py          ← bookmark CRUD
```

## Known rough edges

Tracked here rather than fixed, because working through them is the point.

- **`SQL/` and `scripts/seed.py` are stale.** `01-CREATE_TABLE.sql` predates the
  `users` table and has no `user_id` column, and the sample-data insert doesn't
  supply one — so seeding fails against the schema the app now creates.
  `scripts/seed.py` also imports `psycopg2`, which isn't in `pyproject.toml`.
- **`bookmarks.title` is globally unique.** The comment in
  [src/schemas.py](src/schemas.py) says bookmarks only need to be unique per
  user, but the constraint isn't scoped to `user_id` — so two users can't save
  the same title. Wants a composite unique constraint.
- **No healthcheck on `db`.** The `app` service uses `depends_on`, which waits
  for the container to start, not for Postgres to accept connections. First boot
  after `down -v` can race.
- **No migrations.** `create_all` can't alter an existing table.
- **No tests.**

## Status

Phase 3 (JWT auth) built: registration, login, `/auth/me`, bearer-token
middleware, and per-user scoping on every bookmark query. The app is
containerised and dependency management has moved to uv.
