"""Temporary recommendations route - proves the boundary works over HTTP.

At step 6 this is replaced by proper pages (Jinja2 + HTMX). For now it just
calls the stub so the Recommendation contract can be seen live.
"""

from fastapi import APIRouter

from app.schemas.recommendation import Recommendation
from app.services.recommendations import get_recommender

router = APIRouter(tags=["recommendations"])


@router.get("/recommendations")
def recommendations(user_id: int = 0) -> list[Recommendation]:
    return get_recommender().get_recommendations(user_id)
