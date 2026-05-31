import httpx

BASEURL = "http://localhost:8000"

"""
request helper so i see status codes
"""


class Client:
    def _request(self, method: str, path: str, **kwargs):
        r = self._http.request(method, path, **kwargs)
        r.raise_for_status()
        return r.json()

    def __init__(self, base_url: str = BASEURL):
        self._http = httpx.Client(base_url=base_url)
        self._token = None

    def __repr__(self):
        status = "authenticated" if self._token else "not authenticated"
        return f"<Client {status} base={self._http.base_url}>"

    def list_all_bookmarks(self):
        return self._request("GET", "/bookmarks/")

    def specific_bookmark(self, index: int):
        return self._request("GET", f"/bookmarks/{index}")

    def create_bookmark(self, title: str, author: str, page: int):
        json_post = {"title": title, "author": author, "page": page}
        return self._request("POST", "/bookmarks/", json=json_post)

    def update_bookmark(self, book_id: int, title: str, author: str, page: int):
        json_post = {"title": title, "author": author, "page": page}
        return self._request("PUT", f"/bookmarks/{book_id}", json=json_post)

    def delete_bookmark(self, book_id: int):
        return self._request("DELETE", f"/bookmarks/{book_id}")
