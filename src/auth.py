import datetime as dt
import os

import jwt
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGO = os.environ["JWT_ALGORITHM"]
JWT_TTL = dt.timedelta(hours=1)


def issue_token(user_id: int):
    # I would like to use the user_id and not the email as its more secure?
    now = dt.datetime.now(dt.timezone.utc)
    payload = {"sub": user_id, "iat": now, "exp": now + JWT_TTL}
    return jwt.encode(payload=payload, key=JWT_SECRET, algorithm=JWT_ALGO)
