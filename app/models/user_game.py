"""Ownership link between a user and a game, with playtime."""

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class UserGame(Base):
    """A game a user owns, with how many minutes they've played it."""

    __tablename__ = "user_games"
    __table_args__ = (UniqueConstraint("user_id", "game_id", name="uq_user_games_user_game"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False, index=True)
    playtime_forever: Mapped[int] = mapped_column(default=0, nullable=False)
