"""Sync a user's Steam library into the database, with TTL-based throttling."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.game import Game
from app.models.user import User
from app.models.user_game import UserGame
from app.schemas.steam import OwnedGame
from app.services.steam_client import SteamClient


def sync_user_library(
    db: Session,
    user: User,
    steam_client: SteamClient,
    ttl_hours: int = 24,
    force: bool = False,
) -> dict[str, object]:
    """Refresh a user's owned games and profile from Steam, unless TTL hasn't expired.

    On any failure while talking to Steam or writing to the database, the
    transaction is rolled back so the DB is never left half-updated.
    """
    if not force and not _is_stale(user.last_synced_at, ttl_hours):
        games_count = db.query(UserGame).filter(UserGame.user_id == user.id).count()
        return {"synced": False, "reason": "ttl_not_expired", "games_count": games_count}

    try:
        owned_games = steam_client.get_owned_games(user.steam_id)
        profile = steam_client.get_player_summary(user.steam_id)

        _upsert_games(db, owned_games)
        _upsert_user_games(db, user.id, owned_games)

        if profile is not None:
            user.personaname = profile.personaname
            user.avatar_url = profile.avatar_url

        user.last_synced_at = datetime.now(timezone.utc)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {"synced": True, "reason": "synced", "games_count": len(owned_games)}


def _is_stale(last_synced_at: datetime | None, ttl_hours: int) -> bool:
    if last_synced_at is None:
        return True
    return datetime.now(timezone.utc) - last_synced_at >= timedelta(hours=ttl_hours)


def _upsert_games(db: Session, owned_games: list[OwnedGame]) -> None:
    """Create or update the games table for the given owned games, in bulk."""
    if not owned_games:
        return

    appids = [game.appid for game in owned_games]
    existing_games = {game.appid: game for game in db.query(Game).filter(Game.appid.in_(appids))}

    for owned_game in owned_games:
        existing = existing_games.get(owned_game.appid)
        if existing is None:
            db.add(Game(appid=owned_game.appid, name=owned_game.name))
        elif existing.name != owned_game.name:
            existing.name = owned_game.name


def _upsert_user_games(db: Session, user_id: int, owned_games: list[OwnedGame]) -> None:
    """Create or update user_games rows for the given owned games, in bulk."""
    existing_rows = {
        row.appid: row
        for row in db.query(UserGame).filter(UserGame.user_id == user_id)
    }

    for owned_game in owned_games:
        existing = existing_rows.get(owned_game.appid)
        if existing is None:
            db.add(
                UserGame(
                    user_id=user_id,
                    appid=owned_game.appid,
                    playtime_forever=owned_game.playtime_forever,
                )
            )
        elif existing.playtime_forever != owned_game.playtime_forever:
            existing.playtime_forever = owned_game.playtime_forever
