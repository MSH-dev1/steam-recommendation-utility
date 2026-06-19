"""Stub recommender. Gets its real implementation at step 5 (content-based)."""

from app.schemas.recommendation import Recommendation
from app.services.recommendations.base import RecommenderBase

_FAKE_GAMES = [
    Recommendation(appid=620, name="Portal 2", reason="stub: everyone likes Portal 2"),
    Recommendation(appid=400, name="Portal", reason="stub: start with the first one"),
    Recommendation(
        appid=292030, name="The Witcher 3", reason="stub: lots of hours among similar users"
    ),
]


class StubRecommender(RecommenderBase):
    def get_recommendations(self, user_id: int) -> list[Recommendation]:
        return list(_FAKE_GAMES)
