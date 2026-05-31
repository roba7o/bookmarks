import httpx

BASEURL = "http://localhost:8000"


class Client:
    def __init__(self, base_url: str = BASEURL):
        self._http = httpx.Client(base_url=base_url)
        self._token = None

    def __repr__(self):
        status = "authenticated" if self._token else "not authenticated"
        return f"<Client {status} base={self._http.base_url}>"


if __name__ == "__main__":
    c = Client()
    print(c)
