import os

import asyncpg
from dotenv import load_dotenv
from pydantic import BaseModel
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.routing import Route

load_dotenv()

"""
From the docs but not a decorator approach

jsut run main -> its not working

TODO: but the standard pattern is a connection pool (asyncpg.create_pool())
created once at app startup and shared across requests.
Starlette has lifespan hooks for this
"""


class BookMarkCreate(BaseModel):
    title: str
    author: str
    page: int


class BookMarkPost(BookMarkCreate):
    bm_seq: int


class BookMarkItem(HTTPEndpoint):
    async def get(self, request):
        conn = await asyncpg.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            host="127.0.0.1",
            port=5432,
        )
        try:
            book_index = request.path_params["book_index"]

            bookmark_item = await conn.fetchrow(
                "SELECT * FROM public.bookmarks WHERE bm_seq = $1", book_index
            )
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

        finally:
            await conn.close()

    async def put(self, request):
        conn = await asyncpg.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            host="127.0.0.1",
            port=5432,
        )
        try:
            post_bookmark = await request.json()
            book_index = request.path_params["book_index"]

            # print for debugging
            new_bookmark_pyd = BookMarkCreate(**post_bookmark)

            update_string = f"""
                UPDATE BOOKMARKS SET
                    title = '{new_bookmark_pyd.title}',
                    author = '{new_bookmark_pyd.author}',
                    page = '{new_bookmark_pyd.page}'
                WHERE
                    (bm_seq = {book_index})
                RETURNING *;
                """

            row = await conn.fetchrow(update_string)

            print(f"index {book_index} returned row: {row}")

            if row is None:
                raise HTTPException(404)

            return JSONResponse(f"Index:{book_index}' has been updated!")

        finally:
            await conn.close()


class BookMarkList(HTTPEndpoint):
    async def get(self, request):
        # todo: anyway to create a fucntion that handles the connection and it closing
        conn = await asyncpg.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            host="127.0.0.1",
            port=5432,
        )
        try:
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

        finally:
            await conn.close()

    async def post(self, request):
        conn = await asyncpg.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            host="127.0.0.1",
            port=5432,
        )
        new_bookmark = await request.json()

        # printing for now as i need to test the the suitability
        print(new_bookmark)

        # attempting pydantic
        try:
            new_bookmark_pyd = BookMarkCreate(**new_bookmark)

            insert_string = f"""
                INSERT INTO BOOKMARKS (TITLE, AUTHOR, PAGE) VALUES
                ('{new_bookmark_pyd.title}',
                '{new_bookmark_pyd.author}',
                '{new_bookmark_pyd.page}')
            """

            print(f"insert string is {insert_string}")

            await conn.execute(insert_string)

            # print(new_bookmark_pyd)
            return JSONResponse(f"'{str(new_bookmark_pyd)}' has been added!")

        finally:
            await conn.close()


app = Starlette(
    debug=True,
    routes=[
        Route("/bookmarks/", endpoint=BookMarkList),
        Route("/bookmarks/{book_index:int}", endpoint=BookMarkItem),
    ],
)
