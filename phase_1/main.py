import json
from json import JSONDecodeError

from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route

"""
From the docs but not a decorator approach
"""

bookmark_dict = {
    1: {"book": "Designing Data Intensive Applications", "Page": 88},
    2: {"book": "Fluent Python", "Page": 444},
    3: {"book": "Version Control with Git", "Page": "144"},
}

_SEQ = 4


async def homepage(request):
    basic_200_body = (
        "Welcome to the api! You are at the root page. \n"
        "These are the following books stored on memory: \n"
        f"{json.dumps(bookmark_dict, indent=2)}"
    )
    return PlainTextResponse(basic_200_body)


class BookMarkItem(HTTPEndpoint):
    async def get(self, request):
        try:
            book_index = request.path_params["book_index"]
            return JSONResponse(bookmark_dict[book_index])
        except KeyError:
            raise HTTPException(404)

    async def delete(self, request):
        try:
            book_index = request.path_params["book_index"]
            deleted = str(bookmark_dict[book_index])
            bookmark_dict.pop(book_index)
            return PlainTextResponse(f"Removed: {deleted}")
        except KeyError:
            raise HTTPException(404)

    async def patch(self, request):
        try:
            book_index = request.path_params["book_index"]
            new_bookmark = await request.json()
            bookmark_dict[book_index] = new_bookmark
            return JSONResponse(bookmark_dict[book_index])
        except JSONDecodeError:
            raise HTTPException(400)
        except KeyError:
            raise HTTPException(404)


class BookMarkCollection(HTTPEndpoint):
    async def post(self, request):
        """
        New entries!!
        """
        try:
            new_bookmark = await request.json()
            global _SEQ
            _SEQ += 1
            bookmark_dict[_SEQ] = new_bookmark
            return PlainTextResponse(
                f"Created new bookmark at index: {_SEQ}, {bookmark_dict[_SEQ]}"
            )
        except ValueError:
            raise HTTPException(400)

    async def get(self, request):
        return JSONResponse(bookmark_dict)


app = Starlette(
    debug=True,
    routes=[
        Route("/", endpoint=homepage),
        Route("/bookmarks/", endpoint=BookMarkCollection),
        Route("/bookmarks/{book_index:int}", endpoint=BookMarkItem),
    ],
)
