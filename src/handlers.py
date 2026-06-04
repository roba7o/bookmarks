import logging

from pydantic import ValidationError
from sqlalchemy.exc import DatabaseError, IntegrityError
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


async def invalid_payload_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        {"detail": "validation failed", "code": "validation_error"},
        status_code=422,
    )


async def db_integrity_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        {
            "detail": "Conflict existing data",
            "code": "conflict",
        },
        status_code=409,
    )


async def db_database_gen_handler(request: Request, exc: DatabaseError):
    return JSONResponse(
        {
            "detail": "Database error",
            "code": "db_error",
        },
        status_code=500,
    )


async def http_exception(request: Request, exc: HTTPException):
    return JSONResponse(
        {"detail": exc.detail, "code": "HTTP Error"},
        status_code=exc.status_code,
    )


async def unhandled(request: Request, exc: Exception):
    logger.exception("unhandled error")
    return JSONResponse(
        {"detail": "Internal server error"},
        status_code=500,
    )
