"""Content-based recommender: IDF-weighted genre/tag similarity, weighted by playtime."""

import math

from sqlalchemy.orm import Session, selectinload

from app.db.session import SessionLocal
from app.models.game import Game
from app.models.user_game import UserGame
from app.schemas.recommendation import Recommendation
from app.services.recommendations.base import RecommenderBase
from app.services.recommendations.math_utils import (
    build_profile,
    compute_idf,
    cosine_similarity,
    top_contributing_features,
)

MIN_PLAYTIME_MINUTES = 30
TOP_N = 20

# Steam storefront/platform metadata, not properties of the game itself.
# Excluded outright rather than left to IDF, for cleaner `reason` text.
STOP_FEATURES = {
    "Steam Achievements",
    "Steam Cloud",
    "Steam Trading Cards",
    "steam-trading-cards",
    "Full controller support",
    "Captions available",
}


class ContentBasedRecommender(RecommenderBase):
    def get_recommendations(self, user_id: int, top_n: int = TOP_N) -> list[Recommendation]:
        db = SessionLocal()
        try:
            all_games = _load_all_games(db)
            idf = compute_idf([_game_features(game) for game in all_games])

            owned_playtime = _load_owned_playtime(db, user_id)
            owned_games = [game for game in all_games if game.id in owned_playtime]

            profile = build_profile(
                [
                    _weighted_features(game, owned_playtime[game.id], idf)
                    for game in owned_games
                ]
            )

            if not profile:
                return []

            owned_game_ids = set(owned_playtime.keys())
            candidates = [game for game in all_games if game.id not in owned_game_ids]

            scored = []
            for game in candidates:
                candidate_vector = _idf_weighted_vector(_game_features(game), idf)
                similarity = cosine_similarity(profile, candidate_vector)
                scored.append((similarity, game, candidate_vector))

            scored.sort(key=lambda item: item[0], reverse=True)

            return [
                Recommendation(
                    appid=game.appid,
                    name=game.name,
                    reason=_build_reason(profile, candidate_vector),
                )
                for _, game, candidate_vector in scored[:top_n]
            ]
        finally:
            db.close()


def _load_all_games(db: Session) -> list[Game]:
    """Load the whole catalog once - reused for IDF, the profile, and candidates."""
    return db.query(Game).options(selectinload(Game.genres), selectinload(Game.tags)).all()


def _load_owned_playtime(db: Session, user_id: int) -> dict[int, int]:
    rows = (
        db.query(UserGame.game_id, UserGame.playtime_forever)
        .filter(UserGame.user_id == user_id, UserGame.playtime_forever >= MIN_PLAYTIME_MINUTES)
        .all()
    )
    return dict(rows)


def _game_features(game: Game) -> set[str]:
    features = {genre.name for genre in game.genres} | {tag.name for tag in game.tags}
    return features - STOP_FEATURES


def _idf_weighted_vector(features: set[str], idf: dict[str, float]) -> dict[str, float]:
    return {feature: idf.get(feature, 0.0) for feature in features}


def _weighted_features(
    game: Game, playtime_forever: int, idf: dict[str, float]
) -> dict[str, float]:
    playtime_weight = math.log(1 + playtime_forever)
    return {
        feature: playtime_weight * idf.get(feature, 0.0) for feature in _game_features(game)
    }


def _build_reason(profile: dict[str, float], candidate_vector: dict[str, float]) -> str:
    top_features = top_contributing_features(profile, candidate_vector)
    if not top_features:
        return "Picked from the catalog"
    return f"Matches your interest in: {', '.join(top_features)}"
