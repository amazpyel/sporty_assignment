import requests


class BaseApiClient:
    """Thin requests.Session wrapper: base URL + x-user-id header on every call."""

    def __init__(self, base_url: str, user_id: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"x-user-id": user_id, "Content-Type": "application/json"})

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.session.get(f"{self.base_url}{path}", **kwargs)

    def post(self, path: str, json: dict | None = None, **kwargs) -> requests.Response:
        return self.session.post(f"{self.base_url}{path}", json=json, **kwargs)
