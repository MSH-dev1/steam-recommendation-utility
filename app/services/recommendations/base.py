"""Recommender core boundary.

This is the stable interface from principle #2. The whole project calls
recommendations ONLY through get_recommendations(user). Whatever is inside -
stub (step 1), content-based (step 5), LLM on top (step 7) - is none of the
rest of the project's business. The signature does not change.
"""

from abc import ABC, abstractmethod

from app.schemas.recommendation import Recommendation


class RecommenderBase(ABC):
    @abstractmethod
    def get_recommendations(self, user_id: int) -> list[Recommendation]:
        """Return recommendations for a user.

        At step 1 user_id is a placeholder (the User model doesn't exist yet,
        it arrives at step 2). Once User exists, the signature can be extended
        here, in one place, rather than across the whole project.
        """
        ...
