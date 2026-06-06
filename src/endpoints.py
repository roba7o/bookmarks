import uuid

import bcrypt
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    ForeignKey,
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

from auth import issue_token
from src.settings import logger

# Table instantiation - postgressqlalchemy
metadata = MetaData()

bookmarks_table = Table(
    "bookmarks",
    metadata,
    Column("bm_seq", Integer, Identity(always=True), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False),
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
    Column("email", Text, unique=True, nullable=False),
    Column(
        "user_id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    ),
    Column("hashed_pw", Text, nullable=False),
    Column(
        "created_at",
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    ),
)


# Pydantic Schemas


class BookMarkCreate(BaseModel):
    title: str
    author: str
    page: int


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=20)
    # we type check the raw password not the hash!
    # todo: type check against common passwords like a csv
    # make it a SecretStr so i cant print it


class LoginRequest(BaseModel):
    email: str
    password: str
    # do i add token here?


class BookMarkItem(HTTPEndpoint):
    async def get(self, request):
        # Grabbing the user_id that the middleware has assigned

        user_id_from_state = request.state.user_id
        book_index = request.path_params["book_index"]

        logger.info(
            f"Request data - user_id:'{user_id_from_state}', book_index:'{book_index}'"
        )

        async with request.app.state.engine.connect() as conn:
            bookmark_result = await conn.execute(
                select(bookmarks_table)
                .where(bookmarks_table.c.bm_seq == book_index)
                .where(bookmarks_table.c.user_id == user_id_from_state)
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

            # password -> bytes -> gen salt -> hash it all
            password_bytes = new_user.password.encode("utf-8")
            salt = bcrypt.gensalt()
            hashed_w_salt = bcrypt.hashpw(password=password_bytes, salt=salt)

            new_user_result = await conn.execute(
                insert(user_table)
                .values(email=new_user.email, hashed_pw=hashed_w_salt.decode("utf-8"))
                .returning(user_table)
            )

            result = new_user_result.mappings().fetchone()

            await conn.commit()

            # generate token
            user_id = str(result["user_id"])
            token = issue_token(user_id)

            # eventually i will not return the password! i will return the JWT token
            return JSONResponse({"status": "ok", "user_id": user_id, "token": token})


class AuthLogin(HTTPEndpoint):
    async def post(self, request):
        post_user_login_creds = await request.json()
        async with request.app.state.engine.connect() as conn:
            login_user_creds_request = LoginRequest(**post_user_login_creds)

            # select where email = login_user_creds.email is there
            # if none -> invalid, if true -> verify login password
            login_user_exec = await conn.execute(
                select(user_table).where(
                    user_table.c.email == login_user_creds_request.email
                )
            )

            login_user_result = login_user_exec.mappings().fetchone()

            if login_user_result is None:
                raise HTTPException(401)

            # checking password
            if bcrypt.checkpw(
                password=login_user_creds_request.password.encode("utf-8"),
                hashed_password=login_user_result["hashed_pw"].encode("utf-8"),
            ):
                # Generate Token
                user_id = str(login_user_result["user_id"])
                token = issue_token(user_id)

                return JSONResponse(
                    {
                        "status": "password checks out!",
                        "user_id": str(login_user_result["user_id"]),
                        "token": token,
                    }
                )
            else:
                raise HTTPException(401)
