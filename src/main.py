import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from pydantic import ValidationError
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.routing import Route

from src import handlers
from src.endpoints import BookMarkItem, BookMarkList, metadata

load_dotenv()

"""
TODO LIST

1) Alter these to alembic migrations once app is stable with necessary tables.
   Minimum tables being: bookmarks & users
"""


@asynccontextmanager
async def lifespan(app) -> AsyncGenerator:
    password = os.getenv("DB_PASSWORD")
    user = os.getenv("DB_USER")
    db_name = os.getenv("DB_NAME")

    app.state.engine = create_async_engine(
        f"postgresql+asyncpg://{user}:{password}@localhost:5432/{db_name}", echo=True
    )

    async with app.state.engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

        # test data flagging
        if os.getenv("SEED_DATA") == "true":
            await conn.execute(text(open("SQL/02-GEN_SAMPLE_DATA.sql").read()))

    yield
    await app.state.engine.dispose()


app = Starlette(
    debug=True,
    lifespan=lifespan,
    routes=[
        Route("/bookmarks/", endpoint=BookMarkList),
        Route("/bookmarks/{book_index:int}", endpoint=BookMarkItem),
    ],
    exception_handlers={
        ValidationError: handlers.invalid_payload_handler,
        HTTPException: handlers.http_exception,
        IntegrityError: handlers.db_integrity_handler,
        DatabaseError: handlers.db_database_gen_handler,
        Exception: handlers.unhandled,
    },
)
