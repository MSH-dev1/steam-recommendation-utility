"""Temporary route to verify library sync. Replaced by a real page in step 6."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.game import Game
from app.models.user import User
from app.models.user_game import UserGame
from app.services.library_sync import sync_user_library
from app.services.metadata_sync import enrich_games
from app.services.rawg_client import RawgClient
from app.services.steam_client import SteamClient

router = APIRouter(prefix="/library", tags=["library"])


@router.get("/me")
def get_my_library(
    force: bool = False,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    if user is None:
        raise HTTPException(status_code=401, detail="Not logged in")

    settings = get_settings()
    client = SteamClient(settings.steam_api_key)
    sync_result = sync_user_library(db, user, client, force=force)

    rows = (
        db.query(UserGame, Game)
        .join(Game, UserGame.game_id == Game.id)
        .filter(UserGame.user_id == user.id)
        .order_by(UserGame.playtime_forever.desc())
        .all()
    )
    games = [
        {"appid": game.appid, "name": game.name, "playtime_forever": user_game.playtime_forever}
        for user_game, game in rows
    ]

    return {
        "profile": {
            "steam_id": user.steam_id,
            "personaname": user.personaname,
            "avatar_url": user.avatar_url,
        },
        "games": games,
        "sync": {**sync_result, "last_synced_at": user.last_synced_at},
    }


@router.post("/enrich")
def enrich_library(
    limit: int = 20,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    if user is None:
        raise HTTPException(status_code=401, detail="Not logged in")

    settings = get_settings()
    client = RawgClient(settings.rawg_api_key)
    return enrich_games(db, client, limit=limit)
