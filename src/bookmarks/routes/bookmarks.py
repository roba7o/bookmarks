from sqlalchemy import (
    delete,
    insert,
    select,
    update,
)
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from bookmarks.schemas import BookMarkCreate, bookmarks_table
from bookmarks.settings import logger


class BookMarkItem(HTTPEndpoint):
    async def get(self, request):
        # Grabbing the user_id that the middleware has assigned

        user_id_from_state = request.state.user_id
        logger.info(f"user_id is grabbed from state? {user_id_from_state}")
        book_index = request.path_params["book_index"]

        logger.info(
            f"Request data - user_id:'{user_id_from_state}', book_index:'{book_index}'"
        )

        async with request.app.state.engine.connect() as conn:
            bookmark_result = await conn.execute(
                select(bookmarks_table).where(
                    bookmarks_table.c.bm_seq == book_index,
                    bookmarks_table.c.user_id == user_id_from_state,
                )
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
        # grabbing the user_id from the request so a bookmark is created with a user

        user_id_from_state = request.state.user_id
        logger.info(f"user_id is grabbed from state? {user_id_from_state}")

        async with request.app.state.engine.connect() as conn:
            post_bookmark = await request.json()
            book_index = request.path_params["book_index"]
            new_bookmark_pyd = BookMarkCreate(**post_bookmark)

            put_result = await conn.execute(
                update(bookmarks_table)
                .where(
                    bookmarks_table.c.bm_seq == book_index,
                    bookmarks_table.c.user_id == user_id_from_state,
                )
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
        user_id_from_state = request.state.user_id
        logger.info(f"user_id is grabbed from state? {user_id_from_state}")
        async with request.app.state.engine.connect() as conn:
            book_index = request.path_params["book_index"]

            deleted_result = await conn.execute(
                delete(bookmarks_table)
                .where(
                    bookmarks_table.c.bm_seq == book_index,
                    bookmarks_table.c.user_id == user_id_from_state,
                )
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
        user_id_from_state = request.state.user_id
        logger.info(f"user_id is grabbed from state? {user_id_from_state}")
        async with request.app.state.engine.connect() as conn:
            bookmark_items = await conn.execute(
                select(bookmarks_table).where(
                    bookmarks_table.c.user_id == user_id_from_state
                )
            )

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
        # grabbing the user_id from the request so a bookmark is created with a user

        user_id_from_state = request.state.user_id
        logger.info(f"user_id is grabbed from state? {user_id_from_state}")

        async with request.app.state.engine.connect() as conn:
            new_bookmark_pyd = BookMarkCreate(**new_bookmark)

            post_result = await conn.execute(
                insert(bookmarks_table)
                .values(
                    title=new_bookmark_pyd.title,
                    author=new_bookmark_pyd.author,
                    page=new_bookmark_pyd.page,
                    user_id=user_id_from_state,
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
