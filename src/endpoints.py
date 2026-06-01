import logging

from pydantic import BaseModel
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
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


# Table instantiation - postgressqlalchemy
metadata = MetaData()

bookmarks_table = Table(
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

user_table = Table(
    "users",
    metadata,
    Column("username", Text, unique=True),
    Column("user_id", Integer, Identity(always=True), primary_key=True),
    Column("hashed_pw", Text),
)


# pydantic type strictening
class BookMarkCreate(BaseModel):
    title: str
    author: str
    page: int


class UserCreate(BaseModel):
    username: str
    password: str  # we type check the raw password not the hash!
    # todo: type check against common passwords like a csv...
    # make it a SecretStr so i cant print it


class BookMarkItem(HTTPEndpoint):
    async def get(self, request):
        async with request.app.state.engine.connect() as conn:
            book_index = request.path_params["book_index"]

            bookmark_result = await conn.execute(
                select(bookmarks_table).where(bookmarks_table.c.bm_seq == book_index)
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
                update(bookmarks_table)
                .where(bookmarks_table.c.bm_seq == book_index)
                .values(
                    title=new_bookmark_pyd.title,
                    author=new_bookmark_pyd.author,
                    page=new_bookmark_pyd.page,
                )
                .returning(bookmarks_table)
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
                delete(bookmarks_table)
                .where(bookmarks_table.c.bm_seq == book_index)
                .returning(bookmarks_table)
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
            bookmark_items = await conn.execute(select(bookmarks_table))

            full_response = [
                {
                    "bm_seq": n["bm_seq"],
                    "title": n["title"],
                    "author": n["author"],
                    "page": n["page"],
                    "created_at": str(n["created_at"]),
                }
                for n in bookmark_items.mappings().fetchall()
            ]

            return JSONResponse(full_response)

    async def post(self, request):
        new_bookmark = await request.json()

        async with request.app.state.engine.connect() as conn:
            new_bookmark_pyd = BookMarkCreate(**new_bookmark)

            post_result = await conn.execute(
                insert(bookmarks_table)
                .values(
                    title=new_bookmark_pyd.title,
                    author=new_bookmark_pyd.author,
                    page=new_bookmark_pyd.page,
                )
                .returning(bookmarks_table)
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


class AuthRegister(HTTPEndpoint):
    async def post(self, request):
        post_user_reg_creds = await request.json()

        async with request.app.state.engine.connect() as conn:
            new_user = UserCreate(**post_user_reg_creds)

            new_user_result = await conn.execute(
                insert(user_table)
                .values(username=new_user.username, hashed_pw=new_user.password)
                .returning(user_table)
            )

            posted_password = new_user_result.mappings().fetchone()

            await conn.commit()
            response_dict = {
                "username": posted_password["username"],
                "password": posted_password["hashed_pw"],
            }

            return JSONResponse(response_dict)

            # need to add screening so that identical usernames cant be added?
            # or is this ok due to postgres constraint


class AuthLogin(HTTPEndpoint):
    """ """

    pass
