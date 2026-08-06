import bcrypt
from sqlalchemy import (
    insert,
    select,
)
from starlette.concurrency import run_in_threadpool
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from bookmarks.schemas import LoginRequest, UserCreate, user_table
from bookmarks.settings import logger
from bookmarks.token import issue_token


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

            # checking password -> now concurrent
            if await run_in_threadpool(
                bcrypt.checkpw,
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


class AuthMe(HTTPEndpoint):
    async def get(self, request):
        # Grabbing the user_id which i can then just use as select clause

        user_id_from_state = request.state.user_id
        logger.info(f"Grabbing user_id for AuthMe: {user_id_from_state}")

        async with request.app.state.engine.connect() as conn:
            user_search_result = await conn.execute(
                select(user_table).where(
                    user_table.c.user_id == user_id_from_state,
                )
            )

            user_result_item = user_search_result.mappings().fetchone()

            if user_search_result is None:
                logger.info(
                    "user id cant be found in AuthMe.. something has went wrong"
                )
                raise HTTPException(404)

            response_dict = {
                "user_id": str(user_result_item["user_id"]),
                "email": user_result_item["email"],
            }

            return JSONResponse(response_dict)
