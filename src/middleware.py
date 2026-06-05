from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.auth import decode_token


class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # tryin for get now
        if request.method in ["OPTIONS"]:
            return await call_next(request)

        if "auth" in request.url.path:
            return await call_next(request)

        bearer_data = request.headers.get("Authorization")
        token = bearer_data.replace("Bearer ", "") if bearer_data else None

        if not token:
            return JSONResponse(
                content="Missing auth token mate",
                status_code=401,
            )

        if not decode_token(token):
            return JSONResponse(
                content="INVALID auth token mate",
                status_code=401,
            )

        return await call_next(request)
