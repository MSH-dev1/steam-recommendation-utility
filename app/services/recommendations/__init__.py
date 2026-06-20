"""Recommender factory.

The single place where the project decides WHICH implementation is active.
Steps 5 and 7 change only this line (or the config-based selection logic) -
the rest of the code keeps calling get_recommender().get_recommendations().
"""

from app.services.recommendations.base import RecommenderBase
from app.services.recommendations.content_based import ContentBasedRecommender


def get_recommender() -> RecommenderBase:
    return ContentBasedRecommender()
