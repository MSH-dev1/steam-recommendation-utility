"""Temporary route to verify the Steam API wrapper. Replaced by a real page in step 6."""

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.models.user import User
from app.services.steam_client import SteamClient

router = APIRouter(prefix="/library", tags=["library"])


@router.get("/me")
def get_my_library(user: User | None = Depends(get_current_user)) -> dict[str, object]:
    if user is None:
        raise HTTPException(status_code=401, detail="Not logged in")

    settings = get_settings()
    client = SteamClient(settings.steam_api_key)

    profile = client.get_player_summary(user.steam_id)
    games = client.get_owned_games(user.steam_id)
    games.sort(key=lambda game: game.playtime_forever, reverse=True)

    return {"profile": profile, "games": games}
