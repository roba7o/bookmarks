import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from bookmarks.auth import decode_token
from bookmarks.settings import logger


class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        Auth middleware = a gate with an ALLOWLIST of public paths:

        OPTIONS                     → let through  (CORS preflight, no creds)
        /auth/register, /auth/login → let through  (bootstrap — how you GET a token)
        everything else             → require a valid Bearer token, else 401

        """

        if request.method in ["OPTIONS"]:
            return await call_next(request)

        if request.url.path in ["/auth/register", "/auth/login"]:
            return await call_next(request)

        logger.info("Grabbing bearer data from header")
        bearer_data = request.headers.get("Authorization")
        token = bearer_data.replace("Bearer ", "") if bearer_data else None

        # will remove but just for testing
        logger.info(f"Bearer token is {str(token)[:6] + '******'}")

        if not token:
            return JSONResponse(
                content="Missing auth token mate",
                status_code=401,
            )
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                content="EXPIRED token token mate",
                status_code=401,
            )
        except jwt.InvalidTokenError:
            return JSONResponse(
                content="INVALID auth token mate",
                status_code=401,
            )

        # printing payload for now
        logger.info(f"payload is {payload}")
        request.state.user_id = payload["sub"]

        return await call_next(request)
