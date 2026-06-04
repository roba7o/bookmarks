import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from pydantic import ValidationError
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.routing import Route

from src import handlers
from src.endpoints import AuthLogin, AuthRegister, BookMarkItem, BookMarkList, metadata

load_dotenv()

# configuring logging globally.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app) -> AsyncGenerator:
    password = os.getenv("DB_PASSWORD")
    user = os.getenv("DB_USER")
    db_name = os.getenv("DB_NAME")

    app.state.engine = create_async_engine(
        f"postgresql+asyncpg://{user}:{password}@localhost:5432/{db_name}", echo=False
    )

    async with app.state.engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    yield
    await app.state.engine.dispose()


app = Starlette(
    debug=True,
    lifespan=lifespan,
    routes=[
        Route("/bookmarks/", endpoint=BookMarkList),
        Route("/bookmarks/{book_index:int}", endpoint=BookMarkItem),
        Route("/auth/register", endpoint=AuthRegister),
        Route("/auth/login", endpoint=AuthLogin),
    ],
    exception_handlers={
        ValidationError: handlers.invalid_payload_handler,
        HTTPException: handlers.http_exception,
        IntegrityError: handlers.db_integrity_handler,
        DatabaseError: handlers.db_database_gen_handler,
        Exception: handlers.unhandled,
    },
)
