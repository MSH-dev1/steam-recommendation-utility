"""Many-to-many link between games and genres."""

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class GameGenre(Base):
    """A single (game, genre) association."""

    __tablename__ = "game_genres"
    __table_args__ = (UniqueConstraint("appid", "genre_id", name="uq_game_genres_appid_genre"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    appid: Mapped[int] = mapped_column(ForeignKey("games.appid"), nullable=False, index=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"), nullable=False, index=True)
