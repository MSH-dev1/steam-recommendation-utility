"""Enrich games with RAWG genres/tags, with TTL-based selection and throttling."""

import time
from datetime import datetime, timedelta, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.game import Game
from app.schemas.rawg import RawgGame
from app.services.game_metadata import get_or_create_genre, get_or_create_tag
from app.services.rawg_client import RawgAPIError, RawgClient


def enrich_games(
    db: Session,
    rawg_client: RawgClient,
    limit: int = 20,
    ttl_days: int = 30,
    throttle_seconds: float = 0.5,
) -> dict[str, object]:
    """Fetch RAWG metadata for a batch of games that need it.

    Selects games whose metadata is missing or stale and that haven't already
    failed to match in RAWG, processes up to `limit` of them, and pauses
    between requests to respect RAWG's rate limits.
    """
    candidates = _select_candidates(db, limit, ttl_days)

    matched = 0
    not_matched = 0
    processed = 0

    for index, game in enumerate(candidates):
        try:
            rawg_game = (
                rawg_client.get_game_by_id(game.rawg_id)
                if game.rawg_id is not None
                else rawg_client.search_game(game.name)
            )
        except RawgAPIError:
            # Transient failure: stop here, don't mark this game as a non-match.
            break

        if rawg_game is None:
            game.rawg_match_failed = True
            game.metadata_synced_at = datetime.now(timezone.utc)
            not_matched += 1
        else:
            _apply_metadata(db, game, rawg_game)
            matched += 1

        db.commit()
        processed += 1

        if index < len(candidates) - 1:
            time.sleep(throttle_seconds)

    remaining = _count_candidates(db, ttl_days) > 0

    return {
        "processed": processed,
        "matched": matched,
        "not_matched": not_matched,
        "remaining": remaining,
    }


def _select_candidates(db: Session, limit: int, ttl_days: int) -> list[Game]:
    stale_before = datetime.now(timezone.utc) - timedelta(days=ttl_days)
    return (
        db.query(Game)
        .filter(Game.rawg_match_failed.is_(False))
        .filter(or_(Game.metadata_synced_at.is_(None), Game.metadata_synced_at < stale_before))
        .limit(limit)
        .all()
    )


def _count_candidates(db: Session, ttl_days: int) -> int:
    stale_before = datetime.now(timezone.utc) - timedelta(days=ttl_days)
    return (
        db.query(Game)
        .filter(Game.rawg_match_failed.is_(False))
        .filter(or_(Game.metadata_synced_at.is_(None), Game.metadata_synced_at < stale_before))
        .count()
    )


def _apply_metadata(db: Session, game: Game, rawg_game: RawgGame) -> None:
    """Upsert genres/tags and link them to the game, then update sync state."""
    game.genres = [get_or_create_genre(db, name) for name in rawg_game.genres]
    game.tags = [get_or_create_tag(db, name) for name in rawg_game.tags]
    game.rawg_id = rawg_game.rawg_id
    game.metadata_synced_at = datetime.now(timezone.utc)
