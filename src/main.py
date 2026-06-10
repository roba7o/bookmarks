from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from pydantic import ValidationError
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.routing import Route

from routes.auth import AuthLogin, AuthMe, AuthRegister
from routes.bookmarks import (
    BookMarkItem,
    BookMarkList,
)
from src import middleware
from src.schemas import metadata
from src.settings import DB_NAME, DB_PASSWORD, DB_USER, logger

from . import exception_handlers


@asynccontextmanager
async def lifespan(app) -> AsyncGenerator:
    password = DB_PASSWORD
    user = DB_USER
    db_name = DB_NAME

    app.state.engine = create_async_engine(
        f"postgresql+asyncpg://{user}:{password}@localhost:5432/{db_name}", echo=False
    )

    logger.info(f"Engine booted for db:'{db_name}' via lifespan")

    async with app.state.engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    yield
    await app.state.engine.dispose()


app = Starlette(
    debug=True,
    lifespan=lifespan,
    routes=[
        Route("/bookmarks", endpoint=BookMarkList),
        Route("/bookmarks/{book_index:int}", endpoint=BookMarkItem),
        Route("/auth/register", endpoint=AuthRegister),
        Route("/auth/login", endpoint=AuthLogin),
        Route("/auth/me", endpoint=AuthMe),
    ],
    exception_handlers={
        ValidationError: exception_handlers.invalid_payload_handler,
        HTTPException: exception_handlers.http_exception,
        IntegrityError: exception_handlers.db_integrity_handler,
        DatabaseError: exception_handlers.db_database_gen_handler,
        Exception: exception_handlers.unhandled,
    },
    middleware=[Middleware(middleware.AuthenticationMiddleware)],
)
