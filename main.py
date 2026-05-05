import os

import asyncpg
from dotenv import load_dotenv
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
                "date_cre": str(bookmark_item["created_at"]),
            }

            return JSONResponse(response_dict)

        finally:
            await conn.close()


app = Starlette(
    debug=True,
    routes=[
        Route("/bookmarks/{book_index:int}", endpoint=BookMarkItem),
    ],
)
