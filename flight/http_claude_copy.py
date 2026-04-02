import json
from datetime import datetime
from typing import Any, Optional

# ==== Dealing with Memory ======

_STORE = {}
_SEQ = 0


def _now() -> str:
    return datetime.now()


# ======== response helpers =========


# Q? : how can you insert a string as a param and its also got idea issues?
def send_json(h: "BookmarkHandler", status: int, payload: Any) -> None:
    """
    Serialise payload to JSON and write a complete HTTP response.
    "h" being handler instance -> with inheritited fucntions
    """
    body = json.dumps(payload).encode()
    h.send_response(status)
    h.send_header("Content-type", "application/json")
    h.send_header("Content-Length", str(len(body)))
    h.end_headers()  # seperating header from body
    h.wfile.write(body)


def send_empty(h: "BookmarkHandler", status: int) -> None:
    """
    for 204 No-Content (no body, content length = 0)
    """
    h.send_response(status)
    h.send_header("Content-lenght", "0")
    h.end_headers()


def send_error(h: "BookmarkHandler", status: int, message: str) -> None:
    send_json("BookmarkHandler", status, {"error": message, "status": status})


def read_json(h: "BookmarkHandler") -> Optional[Any]:
    """
    Reading the request body of a h.rfile

    h.rfile is a file-like object wrapping the incoming TCP stream.
    Content-lwngth defines how many bytes -> must stop after
    """
    try:
        length = int(h.headers.get("Content-length"), 0)

    # Dealing with type or null errors
    except ValueError:
        return None
    if length <= 0:
        return None

    raw = h.rfile.read(length)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


# ======= defining the request handler class ========
"""
This class is ins
"""


class BookmarkHandler:
    pass
