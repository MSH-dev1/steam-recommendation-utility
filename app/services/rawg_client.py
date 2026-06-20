"""Wrapper around the RAWG Video Games Database API. Callers never see raw JSON.

Kept as a small class with two methods so a caching/rate-limiting layer can later
wrap or replace it without changing any calling code.

Note: RAWG's terms require attributing RAWG as the data source wherever this data
is displayed. That attribution is added to the frontend in step 6, not here.
"""

import httpx

from app.schemas.rawg import RawgGame

RAWG_API_BASE_URL = "https://api.rawg.io/api"
TAGS_LIMIT = 20


class RawgAPIError(Exception):
    """Raised when the RAWG API returns an unexpected (non-404) response."""


class RawgClient:
    """Thin wrapper around the subset of the RAWG API this app needs."""

    def __init__(self, api_key: str, client: httpx.Client | None = None) -> None:
        self._api_key = api_key
        self._client = client or httpx.Client()

    def search_game(self, name: str) -> RawgGame | None:
        """Find the best-matching RAWG game for a name. None if no match.

        The search endpoint doesn't return full tag data, so once we have a
        candidate's id we fetch full details via get_game_by_id.
        """
        url = f"{RAWG_API_BASE_URL}/games"
        params = {"key": self._api_key, "search": name, "page_size": "1"}
        data = self._get_json(url, params)

        results = data.get("results", [])
        if not results:
            return None

        return self.get_game_by_id(results[0]["id"])

    def list_popular_games(self, page: int, page_size: int = 40) -> list[RawgGame]:
        """Fetch a page of popular games, ordered by how many users added them.

        The list endpoint includes genres but not full tag data, so results
        here have an empty tags list. Full tag enrichment happens later via
        get_game_by_id, reusing the existing enrichment mechanism.
        """
        url = f"{RAWG_API_BASE_URL}/games"
        params = {
            "key": self._api_key,
            "ordering": "-added",
            "page": str(page),
            "page_size": str(page_size),
        }
        data = self._get_json(url, params)

        return [
            RawgGame(
                rawg_id=item["id"],
                name=item["name"],
                slug=item["slug"],
                genres=[genre["name"] for genre in item.get("genres", [])],
                tags=[],
                released=item.get("released"),
                rating=item.get("rating"),
            )
            for item in data.get("results", [])
        ]

    def get_game_by_id(self, rawg_id: int) -> RawgGame | None:
        """Fetch full details (including genres/tags) for a known RAWG id."""
        url = f"{RAWG_API_BASE_URL}/games/{rawg_id}"
        params = {"key": self._api_key}

        try:
            response = self._client.get(url, params=params)
        except httpx.HTTPError as exc:
            raise RawgAPIError(f"Request to RAWG API failed: {exc}") from exc

        if response.status_code == 404:
            return None
        if response.status_code != 200:
            raise RawgAPIError(f"RAWG API returned status {response.status_code} for {url}")

        try:
            game = response.json()
        except ValueError as exc:
            raise RawgAPIError(f"RAWG API returned invalid JSON for {url}") from exc

        genres = [genre["name"] for genre in game.get("genres", [])]
        tags = [tag["name"] for tag in game.get("tags", [])][:TAGS_LIMIT]

        return RawgGame(
            rawg_id=game["id"],
            name=game["name"],
            slug=game["slug"],
            genres=genres,
            tags=tags,
            released=game.get("released"),
            rating=game.get("rating"),
        )

    def _get_json(self, url: str, params: dict[str, str]) -> dict:
        try:
            response = self._client.get(url, params=params)
        except httpx.HTTPError as exc:
            raise RawgAPIError(f"Request to RAWG API failed: {exc}") from exc

        if response.status_code != 200:
            raise RawgAPIError(f"RAWG API returned status {response.status_code} for {url}")

        try:
            return response.json()
        except ValueError as exc:
            raise RawgAPIError(f"RAWG API returned invalid JSON for {url}") from exc
