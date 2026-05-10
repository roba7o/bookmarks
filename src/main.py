import os
from contextlib import asynccontextmanager

# from typing import DateTime, Integer, Text
from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy import (
    Column,
    DateTime,
    Identity,
    Integer,
    MetaData,
    Table,
    Text,
    select,
    text,
)
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.routing import Route

load_dotenv()

"""
Declaring models for SQLAlchemy

"""

DATABASE_URL = "sqlite:///database.db"


# class BookMarkORM(DeclarativeBase):
#     __tablename__ = "bookmark"
#     bm_seq = Column(Integer, Identity(always=True, primary_key=True))
#     title = Column(Text, unique=True)
#     author = Column(Text)
#     page = Column(Integer)
#     created_at = Column(DateTime)

#     def __repr__(self) -> str:
#         return f"Book(id={self.bm_seq}, author={self.author}, title={self.title})"


class BookMarkCreate(BaseModel):
    title: str
    author: str
    page: int


metadata = MetaData()

bookmarks = Table(
    "bookmarks",
    metadata,
    Column("bm_seq", Integer, Identity(always=True)),
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
async def lifespan(app) -> None:
    password = os.getenv("DB_PASSWORD")
    user = os.getenv("DB_USER")
    db_name = os.getenv("DB_NAME")

    app.state.engine = create_async_engine(
        f"postgresql+asyncpg://{user}:{password}@localhost:5432/{db_name}", echo=True
    )
    async with app.state.engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)  # delete once stable
        await conn.run_sync(metadata.create_all)
    yield
    await app.state.engine.dispose()


class BookMarkItem(HTTPEndpoint):
    async def get(self, request):
        async with request.app.state.engine.connect() as conn:
            book_index = request.path_params["book_index"]

            # bookmark_item = await conn.fetchrow(
            #     "SELECT * FROM public.bookmarks WHERE bm_seq = $1", book_index
            # )

            bookmark_item = await conn.execute(
                select(bookmarks).where(bookmarks.c.bm_seq == book_index)
            ).fetch()

            print(
                f"bookmark_item is type: {type(bookmark_item)} \
                and is value: {bookmark_item}"
            )

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

            # print for debugging
            new_bookmark_pyd = BookMarkCreate(**post_bookmark)

            row = await conn.fetchrow(
                """
                    UPDATE BOOKMARKS SET
                    title = $1,
                    author = $2,
                    page = $3
                WHERE
                    bm_seq = $4
                RETURNING
                    *;
                """,
                new_bookmark_pyd.title,
                new_bookmark_pyd.author,
                new_bookmark_pyd.page,
                book_index,
            )

            print(f"index {book_index} returned row: {row}")

            if row is None:
                raise HTTPException(404)

            return JSONResponse(f"Index:{book_index}' has been updated!")

    async def delete(self, request):
        async with request.app.state.engine.connect() as conn:
            book_index = request.path_params["book_index"]

            deleted_row = await conn.fetchrow(
                """
                DELETE FROM public.bookmarks
                WHERE bm_seq = $1
                RETURNING *;
                """,
                book_index,
            )
            print(f"index {book_index} deleted row: {deleted_row}")

            if deleted_row is None:
                raise HTTPException(404)

            return JSONResponse(f"Index:{book_index}' has been deleted!")


class BookMarkList(HTTPEndpoint):
    async def get(self, request):
        async with request.app.state.engine.connect() as conn:
            bookmark_items = await conn.fetch("SELECT * FROM public.bookmarks;")

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
            row = await conn.fetchrow(
                """
                INSERT INTO BOOKMARKS (TITLE, AUTHOR, PAGE)
                VALUES($1, $2, $3)
                RETURNING *;
                """,
                new_bookmark_pyd.title,
                new_bookmark_pyd.author,
                new_bookmark_pyd.page,
            )

            if row is None:
                raise HTTPException(404)

            return JSONResponse(f"'{str(new_bookmark_pyd)}' has been added!")


app = Starlette(
    debug=True,
    lifespan=lifespan,
    routes=[
        Route("/bookmarks/", endpoint=BookMarkList),
        Route("/bookmarks/{book_index:int}", endpoint=BookMarkItem),
    ],
)
