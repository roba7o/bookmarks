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
from src.exception_handlers import (
    db_database_gen_handler,
    db_integrity_handler,
    http_exception,
    invalid_payload_handler,
    unhandled,
)
from src.middleware import AuthenticationMiddleware
from src.schemas import metadata
from src.settings import DATABASE_URL, DB_NAME, logger


@asynccontextmanager
async def lifespan(app) -> AsyncGenerator:
    app.state.engine = create_async_engine(f"{DATABASE_URL}", echo=False)

    logger.info(f"Engine booted for db:'{DB_NAME}' via lifespan")

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
        ValidationError: invalid_payload_handler,
        HTTPException: http_exception,
        IntegrityError: db_integrity_handler,
        DatabaseError: db_database_gen_handler,
        Exception: unhandled,
    },
    middleware=[Middleware(AuthenticationMiddleware)],
)
