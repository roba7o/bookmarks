import json

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
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


app = Starlette(
    debug=True,
    routes=[
        Route("/", homepage),
    ],
)
