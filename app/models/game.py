"""Game model. Genres/tags (from IGDB) are added in a later step."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Game(Base):
    """A Steam game, identified by its Steam appid."""

    __tablename__ = "games"

    appid: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
