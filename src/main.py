import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from sqlalchemy import (
    Column,
    DateTime,
    Identity,
    Integer,
    MetaData,
    Table,
    Text,
    delete,
    insert,
    select,
    text,
    update,
)
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.routing import Route

import handlers

load_dotenv()

"""
TODO LIST

1) Alter these to alembic migrations once app is stable with necessary tables.
   Minimum tables being: bookmarks & users

2) Change the parameter names and modularise each REST function. Namings of anything
    related to bookmarks is terrible atm

3)
"""


# pydantic type strictening
class BookMarkCreate(BaseModel):
    title: str
    author: str
    page: int


# Table instantiation - postgressqlalchemy
metadata = MetaData()

bookmarks = Table(
    "bookmarks",
    metadata,
    Column("bm_seq", Integer, Identity(always=True), primary_key=True),
    Column("title", Text, unique=True),
    Column("author", Text),
    Column("page", Integer),
    Column(
        "created_at",
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    ),
)


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
    yield
    await app.state.engine.dispose()


class BookMarkItem(HTTPEndpoint):
    async def get(self, request):
        async with request.app.state.engine.connect() as conn:
            book_index = request.path_params["book_index"]

            bookmark_result = await conn.execute(
                select(bookmarks).where(bookmarks.c.bm_seq == book_index)
            )
            bookmark_item = bookmark_result.mappings().fetchone()
            if bookmark_item is None:
                raise HTTPException(404)

            response_dict = {
                "title": bookmark_item["title"],
                "author": bookmark_item["author"],
                "page": bookmark_item["page"],
                "created_at": str(bookmark_item["created_at"]),
            }

            return JSONResponse(response_dict)

    async def put(self, request):
        async with request.app.state.engine.connect() as conn:
            post_bookmark = await request.json()
            book_index = request.path_params["book_index"]
            new_bookmark_pyd = BookMarkCreate(**post_bookmark)

            put_result = await conn.execute(
                update(bookmarks)
                .where(bookmarks.c.bm_seq == book_index)
                .values(
                    title=new_bookmark_pyd.title,
                    author=new_bookmark_pyd.author,
                    page=new_bookmark_pyd.page,
                )
                .returning(bookmarks)
            )

            putted_item = put_result.mappings().fetchone()
            if putted_item is None:
                raise HTTPException(404)

            await conn.commit()

            response_dict = {
                "bm_seq": book_index,
                "title": putted_item["title"],
                "author": putted_item["author"],
                "page": putted_item["page"],
                "created_at": str(putted_item["created_at"]),
            }

            return JSONResponse(response_dict)

    async def delete(self, request):
        async with request.app.state.engine.connect() as conn:
            book_index = request.path_params["book_index"]

            deleted_result = await conn.execute(
                delete(bookmarks)
                .where(bookmarks.c.bm_seq == book_index)
                .returning(bookmarks)
            )

            deleted_item = deleted_result.mappings().fetchone()

            if deleted_item is None:
                raise HTTPException(404)

            await conn.commit()

            response_dict = {
                "bm_seq": book_index,
                "title": deleted_item["title"],
                "author": deleted_item["author"],
                "page": deleted_item["page"],
                "created_at": str(deleted_item["created_at"]),
            }
            return JSONResponse(response_dict)


class BookMarkList(HTTPEndpoint):
    async def get(self, request):
        async with request.app.state.engine.connect() as conn:
            # 404 if there is none?
            bookmark_items = await conn.execute(select(bookmarks)).fetchall()

            full_response = [
                {
                    "bm_seq": n["bm_seq"],
                    "title": n["title"],
                    "author": n["author"],
                    "page": n["page"],
                    "created_at": str(n["created_at"]),
                }
                for n in bookmark_items
            ]

            return JSONResponse(full_response)

    async def post(self, request):
        new_bookmark = await request.json()

        async with request.app.state.engine.connect() as conn:
            new_bookmark_pyd = BookMarkCreate(**new_bookmark)

            post_result = await conn.execute(
                insert(bookmarks)
                .values(
                    title=new_bookmark_pyd.title,
                    author=new_bookmark_pyd.author,
                    page=new_bookmark_pyd.page,
                )
                .returning(bookmarks)
            )

            posted_item = post_result.mappings().fetchone()

            await conn.commit()
            response_dict = {
                "bm_seq": posted_item["bm_seq"],
                "title": posted_item["title"],
                "author": posted_item["author"],
                "page": posted_item["page"],
                "created_at": str(posted_item["created_at"]),
            }

            return JSONResponse(response_dict)


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
