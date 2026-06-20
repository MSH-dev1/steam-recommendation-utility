"""Contracts returned by the Steam API wrapper (app.services.steam_client)."""

from pydantic import BaseModel


class OwnedGame(BaseModel):
    appid: int
    name: str
    playtime_forever: int


class PlayerSummary(BaseModel):
    steam_id: str
    personaname: str
    avatar_url: str
    profile_url: str
