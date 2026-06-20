"""Recommendations route - proves the boundary works over HTTP.

At step 6 this is replaced by proper pages (Jinja2 + HTMX). For now it just
calls get_recommender() for the logged-in user.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.recommendation import Recommendation
from app.services.recommendations import get_recommender

router = APIRouter(tags=["recommendations"])


@router.get("/recommendations")
def recommendations(user: User | None = Depends(get_current_user)) -> list[Recommendation]:
    if user is None:
        raise HTTPException(status_code=401, detail="Not logged in")

    return get_recommender().get_recommendations(user.id)
