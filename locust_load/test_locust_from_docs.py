import os
import time

from dotenv import load_dotenv
from locust import HttpUser, between, task

load_dotenv()

BASEURL = "http://localhost:8000"

token_email = os.getenv("TEST_DB_EMAIL")
token_pass = os.getenv("TEST_DB_PW")


class BookmarkAuthUser(HttpUser):
    wait_time = between(1, 2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.token_expiry = 0

    def get_token(self):
        """
        Obtaining token either fresh if none exists or expired

        not sure how to see if a tokens expired with our salted hash

        should i just login everytime?

        """

        # not doing token check as i will log in everytime
        json_post = {"email": token_email, "password": token_pass}
        response = self.client.post(f"{BASEURL}/auth/login", json=json_post)

        if response.status_code == 200:
            data = response.json()
            self.token = data["token"]

            # we know that the token expires after 1 hour
            self.token_expiry = time.time() + 3600
            return self.token
        else:
            raise Exception(f"Login failed: {response.status_code}")

    def on_start(self):
        self.get_token()

    @task
    def authenticated_request(self):
        """Make a reqest with jwt token"""
        token = self.get_token()  # in case its been an hour since on_start()

        headers = {"Authorization": f"Bearer {token}"}

        with self.client.get(
            f"{BASEURL}/bookmarks", headers=headers, catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                # Token expired, force refresh
                self.token = None
                response.failure("Token expired")
            else:
                response.failure(f"Status: {response.status_code}")
