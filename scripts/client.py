import httpx

BASEURL = "http://localhost:8000"


class Client:
    def __init__(self, base_url: str = BASEURL):
        self._http = httpx.Client(base_url=base_url)
        self._token = None

    def __repr__(self):
        status = "authenticated" if self._token else "not authenticated"
        return f"<Client {status} base={self._http.base_url}>"

    def list_all_bookmarks(self):
        return self._http.get("/bookmarks/").json()

    def specific_bookmark(self, index: int):
        return self._http.get(f"/bookmarks/{index}").json()

    def create_bookmark(self, title: str, author: str, page: int):
        json_post = {"title": title, "author": author, "page": page}
        return self._http.post(url="/bookmarks/", json=json_post)

    def update_bookmark(self, book_id: int, title: str, author: str, page: int):
        json_post = {"title": title, "author": author, "page": page}
        return self._http.put(url=f"/bookmarks/{book_id}", json=json_post)
