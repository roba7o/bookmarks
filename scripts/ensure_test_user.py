"""
Make sure the Locust test account (TEST_DB_EMAIL / TEST_DB_PW) exists.

usage: uv run python scripts/ensure_test_user.py     (server must be running)
"""

import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()

BASEURL = "http://localhost:8000"
creds = {"email": os.environ["TEST_DB_EMAIL"], "password": os.environ["TEST_DB_PW"]}

# 200 = created, 409 = email already registered
register = httpx.post(f"{BASEURL}/auth/register", json=creds)
if register.status_code not in (200, 409):
    sys.exit(f"register failed: {register.status_code} {register.text}")

login = httpx.post(f"{BASEURL}/auth/login", json=creds)
if login.status_code != 200:
    sys.exit(f"login failed: {login.status_code} (registered with another password?)")

print("test user created" if register.status_code == 200 else "test user exists")
