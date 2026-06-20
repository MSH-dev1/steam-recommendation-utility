"""Shared FastAPI dependencies that don't belong to a single route module."""

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.i18n import resolve_language
from app.db.session import get_db
from app.models.user import User


def get_language(request: Request) -> str:
    """Resolve the active language for this request (cookie, then browser, then default)."""
    return resolve_language(request)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    """Resolve the logged-in user from the session, or None if not logged in."""
    user_id = request.session.get("user_id")
    if user_id is None:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        request.session.pop("user_id", None)
        return None

    return user
