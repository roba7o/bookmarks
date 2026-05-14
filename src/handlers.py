import logging

from pydantic import ValidationError
from sqlalchemy.exc import DatabaseError, IntegrityError
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

"""
REGISTER THE SPECIFIC ERROR FIRST!! -> cant do by route call
"""


async def invalid_payload_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        {
            "detail": "validation failed",
            "code": "validation_error",
            "errors": exc.errors(),
        },
        status_code=422,
    )


async def db_integrity_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        {
            "detail": "Conflict existing data",
            "code": "conflict",
            "errors": exc.orig,
        },
        status_code=409,
    )


async def db_database_gen_handler(request: Request, exc: DatabaseError):
    return JSONResponse(
        {
            "detail": "Conflict existing data",
            "code": "conflict",
            "errors": exc.orig,
        },
        status_code=409,
    )


async def http_exception(request: Request, exc: HTTPException):
    return JSONResponse(
        {"detail": exc.detail, "code": exc.status_code},
        status_code=exc.status_code,
    )


async def unhandled(request: Request, exc: HTTPException):
    logger.exception("unhandled error")
    return JSONResponse(
        {"detail": "Internal server error"},
        status_code=500,
    )
