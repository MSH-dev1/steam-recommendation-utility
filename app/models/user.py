"""User model. Authentication is via Steam OpenID — no password is stored."""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class User(Base):
    """A Steam account that has logged into the app."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    steam_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    personaname: Mapped[str | None] = mapped_column(String, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
