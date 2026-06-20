"""Populate the games catalog with popular titles from RAWG.

These games act as recommendation candidates (step 5c-2): titles a user
doesn't already own. Catalog-only rows have no Steam appid.
"""

import time

from sqlalchemy.orm import Session

from app.models.game import Game
from app.schemas.rawg import RawgGame
from app.services.game_metadata import get_or_create_genre
from app.services.rawg_client import RawgAPIError, RawgClient

MAX_PAGES_PER_RUN = 50


def populate_catalog(
    db: Session,
    rawg_client: RawgClient,
    target_count: int = 500,
    throttle_seconds: float = 0.5,
) -> dict[str, object]:
    """Fetch popular RAWG games until the catalog has target_count rows.

    Idempotent: games already known by rawg_id are matched and skipped
    (their genres are refreshed), not duplicated.
    """
    added = 0
    already_existed = 0
    page = 1

    catalog_size = db.query(Game).count()

    while catalog_size < target_count and page <= MAX_PAGES_PER_RUN:
        try:
            rawg_games = rawg_client.list_popular_games(page)
        except RawgAPIError:
            break

        if not rawg_games:
            break

        for rawg_game in rawg_games:
            if catalog_size >= target_count:
                break

            created = _upsert_catalog_game(db, rawg_game)
            db.commit()

            if created:
                added += 1
                catalog_size += 1
            else:
                already_existed += 1

        page += 1
        if catalog_size < target_count:
            time.sleep(throttle_seconds)

    return {"added": added, "already_existed": already_existed, "catalog_size": catalog_size}


def _upsert_catalog_game(db: Session, rawg_game: RawgGame) -> bool:
    """Create a catalog row for this RAWG game, or refresh genres if it exists.

    Returns True if a new row was created, False if it already existed.
    """
    game = db.query(Game).filter(Game.rawg_id == rawg_game.rawg_id).first()
    genres = [get_or_create_genre(db, name) for name in rawg_game.genres]

    if game is not None:
        game.genres = genres
        return False

    game = Game(
        appid=None,
        name=rawg_game.name,
        rawg_id=rawg_game.rawg_id,
        genres=genres,
    )
    db.add(game)
    db.flush()
    return True
