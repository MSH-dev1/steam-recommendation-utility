"""Wrapper around the Steam Web API. Callers never see raw Steam JSON or httpx.

Kept as a small class with two methods so a caching layer (e.g. Redis) can later
wrap or replace it without changing any calling code.
"""

import httpx

from app.schemas.steam import OwnedGame, PlayerSummary

STEAM_API_BASE_URL = "https://api.steampowered.com"


class SteamAPIError(Exception):
    """Raised when the Steam Web API returns an unexpected response."""


class SteamClient:
    """Thin wrapper around the subset of the Steam Web API this app needs."""

    def __init__(self, api_key: str, client: httpx.Client | None = None) -> None:
        self._api_key = api_key
        self._client = client or httpx.Client()

    def get_owned_games(self, steam_id: str) -> list[OwnedGame]:
        """Fetch a user's game library with playtime. Empty if private/no games."""
        url = f"{STEAM_API_BASE_URL}/IPlayerService/GetOwnedGames/v1/"
        params = {
            "key": self._api_key,
            "steamid": steam_id,
            "include_appinfo": "true",
            "include_played_free_games": "true",
        }
        data = self._get_json(url, params)

        games = data.get("response", {}).get("games", [])
        return [
            OwnedGame(
                appid=game["appid"],
                name=game.get("name", ""),
                playtime_forever=game.get("playtime_forever", 0),
            )
            for game in games
        ]

    def get_player_summary(self, steam_id: str) -> PlayerSummary | None:
        """Fetch a user's public profile info, or None if not found."""
        url = f"{STEAM_API_BASE_URL}/ISteamUser/GetPlayerSummaries/v2/"
        params = {"key": self._api_key, "steamids": steam_id}
        data = self._get_json(url, params)

        players = data.get("response", {}).get("players", [])
        if not players:
            return None

        player = players[0]
        return PlayerSummary(
            steam_id=player["steamid"],
            personaname=player.get("personaname", ""),
            avatar_url=player.get("avatarfull", ""),
            profile_url=player.get("profileurl", ""),
        )

    def _get_json(self, url: str, params: dict[str, str]) -> dict:
        try:
            response = self._client.get(url, params=params)
        except httpx.HTTPError as exc:
            raise SteamAPIError(f"Request to Steam API failed: {exc}") from exc

        if response.status_code != 200:
            raise SteamAPIError(
                f"Steam API returned status {response.status_code} for {url}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise SteamAPIError(f"Steam API returned invalid JSON for {url}") from exc
