"""Many-to-many link between games and genres."""

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class GameGenre(Base):
    """A single (game, genre) association."""

    __tablename__ = "game_genres"
    __table_args__ = (UniqueConstraint("game_id", "genre_id", name="uq_game_genres_game_genre"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False, index=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"), nullable=False, index=True)
