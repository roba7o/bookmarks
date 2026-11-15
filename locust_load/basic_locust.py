import os

import requests
from dotenv import load_dotenv
from locust import HttpUser, between, events, task

load_dotenv()

BASEURL = "http://localhost:8000"
CREDS = {"email": os.getenv("TEST_DB_EMAIL"), "password": os.getenv("TEST_DB_PW")}

# task mix: LOGIN_WEIGHT logins (bcrypt) for every 3 bookmark reads
LOGIN_WEIGHT = int(os.getenv("LOGIN_WEIGHT", "1"))
BOOKMARKS_WEIGHT = 3

shared_token = None


@events.test_start.add_listener
def login_once(environment, **kwargs):
    """One login before users spawn -> no bcrypt burst at startup"""
    global shared_token
    response = requests.post(f"{BASEURL}/auth/login", json=CREDS)
    response.raise_for_status()
    shared_token = response.json()["token"]


class BookmarkAuthUser(HttpUser):
    wait_time = between(1, 2)
    host = BASEURL

    @task(LOGIN_WEIGHT)
    def login(self):
        """Repeated login -> keeps bcrypt under load"""
        self.client.post("/auth/login", json=CREDS)

    @task(BOOKMARKS_WEIGHT)
    def bookmarks(self):
        """Cheap request with the shared jwt token"""
        headers = {"Authorization": f"Bearer {shared_token}"}
        self.client.get("/bookmarks", headers=headers)
