"""Contracts returned by the RAWG API wrapper (app.services.rawg_client)."""

from pydantic import BaseModel


class RawgGame(BaseModel):
    rawg_id: int
    name: str
    slug: str
    genres: list[str]
    tags: list[str]
    released: str | None
    rating: float | None
