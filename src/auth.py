import datetime as dt
import os

import jwt
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGO = os.environ["JWT_ALGORITHM"]
JWT_TTL = dt.timedelta(hours=1)

"""
Q: what happens if i used RSA -> how would it change (anszer once jwt is complete)
"""


def issue_token(user_id: int) -> str:
    """
    Returns the token based on os.env vars
    """
    # I would like to use the user_id and not the email as its more secure?
    now = dt.datetime.now(dt.timezone.utc)
    payload = {"sub": user_id, "iat": now, "exp": now + JWT_TTL}
    return jwt.encode(payload=payload, key=JWT_SECRET, algorithm=JWT_ALGO)


def decode_token(token: str) -> dict:
    """
    Returns the payload in the format above

    Q: what happens if i removed options?
    """
    return jwt.decode(
        token,
        key=JWT_SECRET,
        algorithms=[JWT_ALGO],
        options={"require": ["sub", "exp"]},
    )
