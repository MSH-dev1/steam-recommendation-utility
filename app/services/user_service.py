"""User lookup/creation, independent of how the steam_id was obtained."""

from sqlalchemy.orm import Session

from app.models.user import User


def get_or_create_user(db: Session, steam_id: str) -> User:
    """Find a user by steam_id, creating one if it doesn't exist yet."""
    user = db.query(User).filter(User.steam_id == steam_id).first()
    if user is not None:
        return user

    user = User(steam_id=steam_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
