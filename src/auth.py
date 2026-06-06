import datetime as dt

import jwt

from src.settings import JWT_ALGO, JWT_SECRET, logger

JWT_TTL = dt.timedelta(hours=1)

"""
Q: what happens if i used RSA -> how would it change (anszer once jwt is complete)
"""


def issue_token(user_id: int) -> str:
    """
    Returns the token based on os.env vars
    """
    now = dt.datetime.now(dt.timezone.utc)
    payload = {"sub": user_id, "iat": now, "exp": now + JWT_TTL}
    logger.info("Token issued")
    return jwt.encode(payload=payload, key=JWT_SECRET, algorithm=JWT_ALGO)


def decode_token(token: str) -> dict:
    """
    Returns the payload in the format above

    Q: what happens if i removed options?
    """
    token_decode = jwt.decode(
        token,
        key=JWT_SECRET,
        algorithms=[JWT_ALGO],
        options={"require": ["sub", "exp"]},
    )
    logger.info("token decoded")
    return token_decode
