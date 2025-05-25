# app/api/statsapi.py
import httpx

class StatsAPI:
    def __init__(self, base_url: str = "https://statsapi.mlb.com/api"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=10.0)

    def fetch(self, endpoint: str, params: dict = None) -> dict:
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            print(f"[StatsAPI] Request error: {e}")
            return {}
        except httpx.HTTPStatusError as e:
            print(f"[StatsAPI] HTTP error: {e}")
            return {}

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()