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

        try:
            return JSONResponse("Jsut a test")
        finally:
            await conn.close()


app = Starlette(
    debug=True,
    routes=[
        Route("/bookmarks/", endpoint=BookMarkList),
        Route("/bookmarks/{book_index:int}", endpoint=BookMarkItem),
    ],
)
